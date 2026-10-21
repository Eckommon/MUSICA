"""G3B1-A: actual 3-minute 48kHz stereo WAV to verified immutable CAS.

Resource-only: does not create a canonical clip, track, Preview or Accept.
"""
from __future__ import annotations

import hashlib
import wave

import pytest

from musica.audio_assets import (
    import_audio_asset_verified_path, list_audio_assets, read_audio_asset,
)
from musica.contracts import ContractError
from musica.staged_wav import BoundedWavStaging, MAX_CHUNK_BYTES
from musica.studio import StudioService


def _sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _make_three_minute_stereo_pcm16(path):
    frame = (1200).to_bytes(2, "little", signed=True) + (-1300).to_bytes(
        2, "little", signed=True
    )
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(48000)
        remaining = 180 * 48000
        while remaining:
            count = min(remaining, 8192)
            writer.writeframesraw(frame * count)
            remaining -= count
        writer.writeframes(b"")


def test_three_minute_wav_staged_and_imported_as_resource_only(tmp_path):
    workspace = tmp_path / "studio"
    service = StudioService(workspace)
    session = service.create_project_session(
        project_slug="g3b1-three-minutes", session_id="upload-A",
        user_text="Create a dark electronic 12-second song",
        provider_mode="fixture", duration_seconds=12,
        use_case="song", style_profile="dark_electronic", seed=195,
    )
    project = service._get_session("upload-A").project
    accepted_head = project.head_revision_id()
    wav_file = tmp_path / "source.wav"
    _make_three_minute_stereo_pcm16(wav_file)
    expected_sha = _sha(wav_file)
    assert wav_file.stat().st_size == 34_560_044
    staging = BoundedWavStaging(tmp_path / "private")
    token = staging.begin(session_id="upload-A",
                          expected_size=wav_file.stat().st_size,
                          expected_sha256=expected_sha)
    with wav_file.open("rb") as source:
        offset = 0
        while chunk := source.read(MAX_CHUNK_BYTES):
            offset = staging.append(
                session_id="upload-A", token=token, offset=offset,
                chunk=chunk, chunk_sha256=hashlib.sha256(chunk).hexdigest(),
            )
    assert offset == wav_file.stat().st_size
    verified = staging.verified_path(session_id="upload-A", token=token)
    descriptor = import_audio_asset_verified_path(
        project, verified, expected_sha256=expected_sha
    )
    assert project.head_revision_id() == accepted_head
    assert descriptor["asset_id"] == "sha256:" + expected_sha
    assert descriptor["format"]["sample_rate_hz"] == 48000
    assert descriptor["format"]["frame_count"] == 8_640_000
    assert descriptor["format"]["duration_seconds"] == 180
    assert len(list_audio_assets(project)) == 1
    assert read_audio_asset(project, descriptor["asset_id"]) == descriptor
    assert _sha(project._object_path(expected_sha)) == expected_sha
    assert project._object_path(expected_sha).stat().st_size == 34_560_044
    assert import_audio_asset_verified_path(
        project, verified, expected_sha256=expected_sha
    ) == descriptor
    assert project.head_revision_id() == accepted_head
    staging.cancel(session_id="upload-A", token=token)
    assert not verified.exists()
    project.verify_integrity()


def test_bad_staged_wav_never_creates_descriptor_or_head(tmp_path):
    service = StudioService(tmp_path / "workspace")
    service.create_project_session(
        project_slug="g3b1-fail", session_id="fail-A",
        user_text="Create a dark electronic 12-second song",
        provider_mode="fixture", duration_seconds=12,
        use_case="song", style_profile="dark_electronic", seed=196,
    )
    project = service._get_session("fail-A").project
    before = project.head_revision_id()
    source = tmp_path / "bad.wav"
    source.write_bytes(b"RIFF" + b"z" * 40)
    with pytest.raises(ContractError, match="RIFF/WAVE|PCM"):
        import_audio_asset_verified_path(
            project, source, expected_sha256=_sha(source)
        )
    with pytest.raises(ContractError, match="digest mismatch"):
        import_audio_asset_verified_path(
            project, source, expected_sha256="0" * 64
        )
    assert list_audio_assets(project) == []
    assert project.head_revision_id() == before
