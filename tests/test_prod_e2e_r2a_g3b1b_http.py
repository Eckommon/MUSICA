"""G3B1B — real local HTTP session-bound upload and streamed immutable CAS."""
from __future__ import annotations

import hashlib
import http.client
import json
import socket
import threading
import wave
from contextlib import contextmanager
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import pytest

from musica.audio_assets import list_audio_assets, read_audio_asset
from musica.staged_wav import MAX_CHUNK_BYTES, MAX_STAGED_WAV_BYTES
from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server


@contextmanager
def _studio(tmp_path):
    service = StudioService(tmp_path / "workspace")
    service.create_project_session(
        project_slug="g3b1b-http", session_id="http-owner",
        user_text="Make a song", provider_mode="fixture",
        duration_seconds=12, use_case="song",
        style_profile="dark_electronic", seed=199,
    )
    service.create_project_session(
        project_slug="g3b1b-other", session_id="http-other",
        user_text="Make a different song", provider_mode="fixture",
        duration_seconds=12, use_case="song",
        style_profile="dark_electronic", seed=198,
    )
    server = create_local_server(service, host="127.0.0.1", port=0)
    worker = threading.Thread(target=server.serve_forever,
                              kwargs={"poll_interval": 0.01}, daemon=True)
    worker.start()
    try:
        host, port = server.server_address[:2]
        yield service, f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def _post(base, endpoint, data, headers=None, *, session="http-owner"):
    request = Request(
        f"{base}/v0/sessions/{session}/audio/stage{endpoint}", data=data,
        method="POST", headers={"Accept": "application/json", **(headers or {})},
    )
    with urlopen(request, timeout=40) as response:
        return json.loads(response.read())["data"]


def _json(base, endpoint, value=None, *, session="http-owner"):
    return _post(base, endpoint, json.dumps({} if value is None else value).encode(),
                 {"Content-Type": "application/json"}, session=session)


def _chunk(base, token, offset, block, *, digest=None, session="http-owner"):
    return _post(base, f"/{token}/chunk", block, {
        "Content-Type": "application/octet-stream",
        "X-MUSICA-Chunk-Offset": str(offset),
        "X-MUSICA-Chunk-SHA256": digest or hashlib.sha256(block).hexdigest(),
    }, session=session)


def _write_3min(path):
    frame = b"\x10\x04\xf0\xfb"
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(48000)
        for _ in range(1054):
            writer.writeframesraw(frame * 8192)
        writer.writeframesraw(frame * 5632)
        writer.writeframes(b"")
    assert path.stat().st_size == 34_560_044


def _sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(MAX_CHUNK_BYTES):
            h.update(block)
    return h.hexdigest()


def _assert_no_temp(service):
    assert not list((service.workspace / ".wav-staging-g3b1b").glob("wav-*"))


def test_http_three_minute_wav_to_cas_without_creative_accept(tmp_path):
    with _studio(tmp_path) as (service, base):
        project = service._get_session("http-owner").project
        original_head = project.head_revision_id()
        source = tmp_path / "three.wav"
        _write_3min(source)
        digest = _sha(source)
        begun = _json(base, "/start", {"size_bytes": source.stat().st_size, "sha256": digest})
        assert begun["accepted_revision_id"] == original_head
        assert begun["max_chunk_bytes"] == MAX_CHUNK_BYTES
        token = begun["upload_id"]
        offset = 0
        with source.open("rb") as stream:
            while block := stream.read(MAX_CHUNK_BYTES):
                response = _chunk(base, token, offset, block)
                offset += len(block)
                assert response["next_offset"] == offset
                assert response["accepted_revision_unchanged"]
        assert not list_audio_assets(project)
        response = _json(base, f"/{token}/finish")
        assert response["classification"] == "IMMUTABLE_AUDIO_ASSET_NOT_ACCEPTED_CLIP"
        assert response["requires_separate_clip_preview_and_explicit_accept"]
        assert response["accepted_revision_id"] == original_head
        descriptor = response["asset"]
        assert descriptor["size_bytes"] == 34_560_044
        assert descriptor["format"]["frame_count"] == 8_640_000
        assert descriptor["format"]["duration_seconds"] == 180
        assert descriptor["asset_id"] == "sha256:" + digest
        assert read_audio_asset(project, descriptor["asset_id"]) == descriptor
        assert project.head_revision_id() == original_head
        _assert_no_temp(service)
        assert project.verify_integrity()["status"] == "PASS"


def test_http_adversarial_upload_rejects_cross_session_offset_and_sha(tmp_path):
    with _studio(tmp_path) as (service, base):
        project = service._get_session("http-owner").project
        head = project.head_revision_id()
        before_audit = len(project._audit_events())
        raw = b"RIFF" + b"z" * 60
        sha = hashlib.sha256(raw).hexdigest()
        with pytest.raises(HTTPError) as oversized:
            _json(base, "/start", {"size_bytes": MAX_STAGED_WAV_BYTES + 1, "sha256": sha})
        assert oversized.value.code == 400
        started = _json(base, "/start", {"size_bytes": len(raw), "sha256": sha})
        token = started["upload_id"]
        with pytest.raises(HTTPError) as existing:
            _json(base, "/start", {"size_bytes": len(raw), "sha256": sha})
        assert existing.value.code == 409
        with pytest.raises(HTTPError) as foreign:
            _chunk(base, token, 0, raw, session="http-other")
        assert foreign.value.code == 400
        with pytest.raises(HTTPError) as bad_offset:
            _chunk(base, token, 1, raw)
        assert bad_offset.value.code == 400
        _assert_no_temp(service)
        started = _json(base, "/start", {"size_bytes": len(raw), "sha256": sha})
        token = started["upload_id"]
        with pytest.raises(HTTPError) as bad_digest:
            _chunk(base, token, 0, raw, digest="0" * 64)
        assert bad_digest.value.code == 400
        _assert_no_temp(service)
        started = _json(base, "/start", {"size_bytes": len(raw), "sha256": "0" * 64})
        token = started["upload_id"]
        _chunk(base, token, 0, raw)
        with pytest.raises(HTTPError) as bad_complete:
            _json(base, f"/{token}/finish")
        assert bad_complete.value.code == 400
        _assert_no_temp(service)
        assert list_audio_assets(project) == []
        assert len(project._audit_events()) == before_audit
        assert project.head_revision_id() == head


def test_http_preview_authority_cancel_and_missing_sessions(tmp_path):
    with _studio(tmp_path) as (service, base):
        session = service._get_session("http-owner")
        raw = b"RIFF" + b"z" * 60
        info = {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        session.pending = object()
        with pytest.raises(HTTPError) as pending:
            _json(base, "/start", info)
        assert pending.value.code == 409
        session.pending = None
        started = _json(base, "/start", info)
        token = started["upload_id"]
        session.pending = object()
        with pytest.raises(HTTPError) as blocked:
            _chunk(base, token, 0, raw)
        assert blocked.value.code == 409
        assert _json(base, f"/{token}/cancel")["cancelled"]
        session.pending = None
        _assert_no_temp(service)
        with pytest.raises(HTTPError) as missing:
            _json(base, "/start", info, session="never-created")
        assert missing.value.code == 404


def test_http_aborted_connection_immediately_removes_private_stage(tmp_path):
    with _studio(tmp_path) as (service, base):
        raw = b"RIFF" + b"z" * 60
        started = _json(base, "/start", {
            "size_bytes": 100, "sha256": hashlib.sha256(raw).hexdigest()
        })
        token = started["upload_id"]
        uri = urlsplit(base)
        conn = http.client.HTTPConnection(uri.hostname, uri.port, timeout=10)
        try:
            conn.putrequest("POST", f"/v0/sessions/http-owner/audio/stage/{token}/chunk")
            conn.putheader("Content-Type", "application/octet-stream")
            conn.putheader("Content-Length", "100")
            conn.putheader("X-MUSICA-Chunk-Offset", "0")
            conn.putheader("X-MUSICA-Chunk-SHA256", hashlib.sha256(b"x" * 100).hexdigest())
            conn.endheaders()
            conn.send(b"x" * 10)
            conn.sock.shutdown(socket.SHUT_WR)
            try:
                response = conn.getresponse()
                assert response.status == 400
                response.read()
            except (ConnectionResetError, http.client.RemoteDisconnected):
                pass
        finally:
            conn.close()
        _assert_no_temp(service)
        assert service._get_session("http-owner").pending is None
