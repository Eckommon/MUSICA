"""G3B-0: staged 16–64 MiB WAV import and adversarial session/offset/hash tests."""
from __future__ import annotations

import hashlib
import io
import http.client
import socket
from urllib.parse import urlsplit
import json
import struct
import threading
import wave
from contextlib import contextmanager
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from musica.audio_assets import list_audio_assets
from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server
from musica.studio_wav_staging import MAX_STAGED_WAV_BYTES, STAGED_CHUNK_BYTES


@contextmanager
def _studio(tmp_path):
    service = StudioService(tmp_path / "workspace")
    initial = service.create_project_session(
        project_slug="long-user-take", session_id="long-wav-owner",
        user_text="Import long user-selected WAV safely", provider_mode="fixture",
        duration_seconds=180, use_case="song", style_profile="dark_electronic", seed=72
    )
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": .01}, daemon=True
    )
    thread.start()
    host, port = server.server_address[:2]
    try:
        yield service, initial, f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _post(base, suffix, body, headers=None, *, session="long-wav-owner"):
    request = Request(
        f"{base}/v0/sessions/{session}/audio/stage{suffix}",
        data=body, method="POST",
        headers={"Accept": "application/json", **(headers or {})}
    )
    with urlopen(request, timeout=35) as response:
        return json.loads(response.read().decode())["data"]


def _json(base, suffix, body=None, *, session="long-wav-owner"):
    return _post(base, suffix, json.dumps(body or {}).encode(), {
        "Content-Type": "application/json"
    }, session=session)


def _chunk(base, upload_id, offset, data, *, digest=None, session="long-wav-owner"):
    return _post(base, f"/{upload_id}/chunk", data, {
        "Content-Type": "application/octet-stream",
        "X-MUSICA-Chunk-Offset": str(offset),
        "X-MUSICA-Chunk-SHA256": digest or hashlib.sha256(data).hexdigest()
    }, session=session)


def _big_wav(*, min_size=16 * 1024 * 1024 + 4096):
    # Stereo PCM16 at 48kHz, deliberately larger than the old direct cap.
    frames = (min_size + 3) // 4
    samples = (b"\x2a\x00\x00\x00" * frames)
    out = io.BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(48000)
        wav.writeframes(samples)
    return out.getvalue()


def test_g3b0_large_real_wav_is_immutable_resource_and_does_not_accept(tmp_path):
    with _studio(tmp_path) as (service, initial, base):
        project = service._get_session("long-wav-owner").project
        head = project.head_revision_id()
        audit = len(project._audit_events())
        data = _big_wav()
        assert 16 * 1024 * 1024 < len(data) < MAX_STAGED_WAV_BYTES
        digest = hashlib.sha256(data).hexdigest()
        started = _json(base, "/start", {"size_bytes": len(data), "sha256": digest})
        assert started["accepted_revision_id"] == head
        assert started["next_offset"] == 0
        assert started["max_chunk_bytes"] == STAGED_CHUNK_BYTES
        assert started["classification"] == "TEMPORARY_WAV_NOT_ACCEPTED_ASSET_OR_CLIP"
        token = started["upload_id"]
        assert "/" not in token and len(token) == 32
        # No accepted resource / clip / audit event until all verified chunks finalize.
        assert list_audio_assets(project) == []
        assert project.head_revision_id() == head
        for offset in range(0, len(data), STAGED_CHUNK_BYTES):
            part = data[offset:offset + STAGED_CHUNK_BYTES]
            receipt = _chunk(base, token, offset, part)
            assert receipt["next_offset"] == offset + len(part)
            assert receipt["accepted_revision_unchanged"]
        assert list_audio_assets(project) == []
        committed = _json(base, f"/{token}/finish")
        assert committed["classification"] == "IMMUTABLE_AUDIO_ASSET_NOT_ACCEPTED_CLIP"
        assert committed["accepted_revision_id"] == head
        assert committed["staged_upload_sha256"] == digest
        descriptor = committed["asset"]
        assert descriptor["asset_id"] == "sha256:" + digest
        assert descriptor["size_bytes"] == len(data)
        assert descriptor["format"]["sample_rate_hz"] == 48000
        assert descriptor["format"]["channels"] == 2
        assert list_audio_assets(project) == [descriptor]
        assert len(project._audit_events()) == audit + 1
        assert project.head_revision_id() == head
        assert not list((service.workspace / ".wav-staging-g3b0").glob("*.part"))
        assert project.verify_integrity()["status"] == "PASS"


def test_g3b0_wrong_offset_and_digest_fail_closed_and_clean_temp(tmp_path):
    with _studio(tmp_path) as (service, _, base):
        project = service._get_session("long-wav-owner").project
        head, audit = project.head_revision_id(), len(project._audit_events())
        data = b"RIFF" + b"\x00" * 128
        digest = hashlib.sha256(data).hexdigest()
        start = _json(base, "/start", {"size_bytes": len(data), "sha256": digest})
        with pytest.raises(HTTPError) as exc:
            _chunk(base, start["upload_id"], 1, data[:55])
        assert exc.value.code == 400
        resumed = _json(base, "/start", {"size_bytes": len(data), "sha256": digest})
        # The first invalid sequence was deleted and cannot be reused.
        with pytest.raises(HTTPError) as old:
            _chunk(base, start["upload_id"], 0, data[:55])
        assert old.value.code == 400
        assert _json(base, f"/{resumed['upload_id']}/cancel")["cancelled"]
        assert not list((service.workspace / ".wav-staging-g3b0").glob("*.part"))
        assert list_audio_assets(project) == []
        assert project.head_revision_id() == head
        assert len(project._audit_events()) == audit


def test_g3b0_hash_mismatch_and_cancel_cannot_create_asset(tmp_path):
    with _studio(tmp_path) as (service, _, base):
        project = service._get_session("long-wav-owner").project
        head = project.head_revision_id()
        data = b"RIFF" + b"\x00" * 128
        init = _json(base, "/start", {
            "size_bytes": len(data), "sha256": "0" * 64
        })
        token = init["upload_id"]
        _chunk(base, token, 0, data)
        with pytest.raises(HTTPError) as exc:
            _json(base, f"/{token}/finish")
        assert exc.value.code == 400
        assert not list((service.workspace / ".wav-staging-g3b0").glob("*.part"))
        init = _json(base, "/start", {
            "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()
        })
        token = init["upload_id"]
        with pytest.raises(HTTPError) as exc:
            _chunk(base, token, 0, data[:24], digest="f" * 64)
        assert exc.value.code == 400
        assert not list((service.workspace / ".wav-staging-g3b0").glob("*.part"))
        init = _json(base, "/start", {
            "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()
        })
        assert _json(base, f"/{init['upload_id']}/cancel")["cancelled"]
        assert not list((service.workspace / ".wav-staging-g3b0").glob("*.part"))
        assert list_audio_assets(project) == []
        assert project.head_revision_id() == head


def test_g3b0_cross_session_oversize_conflict_and_direct_route_unchanged(tmp_path):
    with _studio(tmp_path) as (service, _, base):
        data = b"RIFF" + b"\x00" * 128
        with pytest.raises(HTTPError) as ex:
            _json(base, "/start", {"size_bytes": MAX_STAGED_WAV_BYTES + 1, "sha256": "0" * 64})
        assert ex.value.code == 400
        init = _json(base, "/start", {
            "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()
        })
        with pytest.raises(HTTPError) as ex:
            _json(base, "/start", {"size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        assert ex.value.code == 409
        with pytest.raises(HTTPError) as ex:
            _chunk(base, init["upload_id"], 0, data, session="different-session")
        assert ex.value.code in {400, 404}
        # No user path is part of the REST request or server staging path.
        with pytest.raises(HTTPError) as ex:
            _chunk(base, "../../objects", 0, data)
        assert ex.value.code in {400, 404}
        assert _json(base, f"/{init['upload_id']}/cancel")["cancelled"]
        assert not list((service.workspace / ".wav-staging-g3b0").glob("*.part"))


def test_g3b0_truncated_chunk_disconnect_cleans_staged_partial(tmp_path):
    """No orphan after a client half-closes before its Content-Length is sent."""
    with _studio(tmp_path) as (service, _, base):
        payload = b"RIFF" + b"\\x00" * 128
        start = _json(base, "/start", {
            "size_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()
        })
        uri = urlsplit(base)
        conn = http.client.HTTPConnection(uri.hostname, uri.port, timeout=10)
        try:
            path = (f"/v0/sessions/long-wav-owner/audio/stage/"
                    f"{start['upload_id']}/chunk")
            conn.putrequest("POST", path)
            conn.putheader("Content-Type", "application/octet-stream")
            conn.putheader("Content-Length", "100")
            conn.putheader("X-MUSICA-Chunk-Offset", "0")
            conn.putheader("X-MUSICA-Chunk-SHA256", hashlib.sha256(b"x" * 100).hexdigest())
            conn.endheaders()
            conn.send(b"x" * 10)
            conn.sock.shutdown(socket.SHUT_WR)
            response = conn.getresponse()
            assert response.status == 400
            response.read()
        finally:
            conn.close()
        assert not list((service.workspace / ".wav-staging-g3b0").glob("*.part"))
        session = service._get_session("long-wav-owner")
        assert list_audio_assets(session.project) == []
        assert session.pending is None
