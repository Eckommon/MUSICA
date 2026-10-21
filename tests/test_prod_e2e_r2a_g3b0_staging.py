"""G3B-0 fail-closed staging safety; no project acceptance or HTTP claim."""
from __future__ import annotations
import hashlib

import pytest

from musica.contracts import ContractError
from musica.staged_wav import (
    BoundedWavStaging, MAX_CHUNK_BYTES, MAX_STAGED_WAV_BYTES,
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def test_private_sequential_upload_and_cancel(tmp_path):
    staging = BoundedWavStaging(tmp_path / "private")
    wav = b"RIFF" + b"x" * (2 * MAX_CHUNK_BYTES)
    token = staging.begin(session_id="studio-A", expected_size=len(wav),
                          expected_sha256=digest(wav))
    assert staging.append(session_id="studio-A", token=token, offset=0,
                          chunk=wav[:MAX_CHUNK_BYTES],
                          chunk_sha256=digest(wav[:MAX_CHUNK_BYTES])) == MAX_CHUNK_BYTES
    with pytest.raises(ContractError, match="non-sequential"):
        staging.append(session_id="studio-A", token=token, offset=0,
                       chunk=b"a", chunk_sha256=digest(b"a"))
    with pytest.raises(ContractError, match="session mismatch"):
        staging.verified_path(session_id="studio-B", token=token)
    with pytest.raises(ContractError, match="incomplete"):
        staging.verified_path(session_id="studio-A", token=token)
    offset = MAX_CHUNK_BYTES
    while offset < len(wav):
        part = wav[offset:offset + MAX_CHUNK_BYTES]
        offset = staging.append(session_id="studio-A", token=token, offset=offset,
                                chunk=part, chunk_sha256=digest(part))
    path = staging.verified_path(session_id="studio-A", token=token)
    assert path.read_bytes() == wav
    assert str(path).startswith(str((tmp_path / "private").resolve()))
    staging.cancel(session_id="studio-A", token=token)
    assert not path.exists()
    with pytest.raises(ContractError, match="unknown"):
        staging.verified_path(session_id="studio-A", token=token)


def test_integrity_failure_does_not_append_or_accept(tmp_path):
    staging = BoundedWavStaging(tmp_path)
    original = b"RIFF" + b"A" * 40
    token = staging.begin(session_id="A", expected_size=len(original),
                          expected_sha256=digest(original))
    with pytest.raises(ContractError, match="digest mismatch"):
        staging.append(session_id="A", token=token, offset=0,
                       chunk=original, chunk_sha256=digest(b"wrong"))
    with pytest.raises(ContractError, match="size out of bounds"):
        staging.append(session_id="A", token=token, offset=0,
                       chunk=b"q" * (MAX_CHUNK_BYTES + 1),
                       chunk_sha256=digest(b"q" * (MAX_CHUNK_BYTES + 1)))
    assert staging.append(session_id="A", token=token, offset=0,
                          chunk=b"RIFF" + b"B" * 40,
                          chunk_sha256=digest(b"RIFF" + b"B" * 40)) == len(original)
    with pytest.raises(ContractError, match="complete digest mismatch"):
        staging.verified_path(session_id="A", token=token)
    staging.close()
    assert not list(tmp_path.glob("wav-*"))


@pytest.mark.parametrize("size", [0, 43, MAX_STAGED_WAV_BYTES + 1, True])
def test_declaration_limits(tmp_path, size):
    staging = BoundedWavStaging(tmp_path)
    with pytest.raises(ContractError):
        staging.begin(session_id="A", expected_size=size, expected_sha256=digest(b"RIFF"))


def test_session_identity_opaque_no_path_payload(tmp_path):
    staging = BoundedWavStaging(tmp_path)
    for identity in ("../escape", "a/b", "", "space name"):
        with pytest.raises(ContractError, match="session"):
            staging.begin(session_id=identity, expected_size=44,
                          expected_sha256=digest(b"x" * 44))
    first = staging.begin(session_id="A", expected_size=44,
                          expected_sha256=digest(b"x" * 44))
    second = staging.begin(session_id="B", expected_size=44,
                           expected_sha256=digest(b"y" * 44))
    assert first != second
    with pytest.raises(ContractError, match="too many"):
        staging.begin(session_id="C", expected_size=44,
                      expected_sha256=digest(b"z" * 44))
    staging.close()
    assert not list(tmp_path.glob("wav-*"))
