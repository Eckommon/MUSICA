"""PROD-E2E-R1A: user-selected WAV bytes -> immutable resource -> explicit audio Accept.

These are first-party localhost HTTP and Studio authority tests. Static JS presence
is NOT a real-Chromium interaction test; that remains a separate promotion gate.
"""
from __future__ import annotations

import hashlib
import io
import json
import threading
import wave
from contextlib import contextmanager
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from musica.audio_assets import list_audio_assets, read_audio_asset
from musica.audio_edit import audio_material_sha256, blueprint_sha256
from musica.studio import StudioService
from musica.studio_audio import StudioAudioSurface
from musica.studio_http_r3 import MAX_WAV_IMPORT_BYTES, create_local_server


def _wav() -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"".join(
            int(3500 if index % 2 == 0 else -3500).to_bytes(2, "little", signed=True)
            for index in range(800)
        ))
    return buf.getvalue()


@contextmanager
def _studio(tmp_path):
    service = StudioService(tmp_path / "workspace")
    initial = service.create_project_session(
        project_slug="first-song", session_id="user-song",
        user_text="Create a dark electronic 12-second song",
        provider_mode="fixture", duration_seconds=12,
        use_case="song", style_profile="dark_electronic", seed=191,
    )
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    host, port = server.server_address[:2]
    try:
        yield service, initial, f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _post_wav(base: str, data: bytes, *, session: str = "user-song",
              content_type: str = "audio/wav", length: int | None = None):
    headers = {"Content-Type": content_type, "Accept": "application/json"}
    if length is not None:
        headers["Content-Length"] = str(length)
    request = Request(
        base + f"/v0/sessions/{session}/audio/import-wav",
        data=data, method="POST", headers=headers
    )
    with urlopen(request, timeout=10) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def _candidate(parent: dict, cid: str, operations: list[dict]) -> dict:
    return {
        "candidate_version": "0", "candidate_id": cid,
        "authority_target": "blueprint_audio_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
            "audio_material_sha256": audio_material_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "r1a-browser"},
        "reason": "Explicit browser operator arrangement edit",
        "operations": operations, "preview_only": True,
    }


def test_r1a_import_is_idempotent_content_addressed_resource_not_accept(tmp_path):
    with _studio(tmp_path) as (service, initial, base):
        project = service._get_session("user-song").project
        head = initial["session"]["head_revision_id"]
        original_events = len(project._audit_events())
        wav = _wav()
        status, response = _post_wav(base, wav)
        assert status == 200 and response["ok"] is True
        info = response["data"]
        asset = info["asset"]
        assert info["classification"] == "IMMUTABLE_AUDIO_ASSET_NOT_ACCEPTED_CLIP"
        assert info["accepted_revision_unchanged"] is True
        assert info["requires_separate_clip_preview_and_explicit_accept"] is True
        assert asset["object_sha256"] == hashlib.sha256(wav).hexdigest()
        assert asset["size_bytes"] == len(wav)
        assert asset["format"]["duration_seconds"] == 0.1
        assert project.head_revision_id() == head
        assert service._get_session("user-song").pending is None
        assert list_audio_assets(project) == [asset]
        assert len(project._audit_events()) == original_events + 1
        status2, duplicate = _post_wav(base, wav)
        assert status2 == 200 and duplicate["data"]["asset"] == asset
        assert len(project._audit_events()) == original_events + 1
        assert project.head_revision_id() == head
        assert project.verify_integrity()["status"] == "PASS"


def test_r1a_browser_asset_import_then_separate_explicit_track_and_clip_accept(tmp_path):
    with _studio(tmp_path) as (service, initial, base):
        project = service._get_session("user-song").project
        root = project.read_revision(initial["session"]["head_revision_id"])
        asset = _post_wav(base, _wav())[1]["data"]["asset"]
        surface = StudioAudioSurface(service)

        track = _candidate(root, "R1A-TRACK", [
            {"operation_id": "R1A-ADD-T", "op": "ADD_TRACK",
             "track_id": "AT-R1A", "order": 0, "name": "My imported WAV"}
        ])
        preview = surface.preview_audio_edit(
            "user-song", candidate=track, candidate_kind="arrangement"
        )
        assert preview["preview_installed"] is True
        assert preview["session"]["head_revision_id"] == root["project"]["revision_id"]
        assert preview["audio_view"]["preview"]["audition"]["available"] is False
        assert preview["session"]["pending_preview"] is not None
        accepted_track = surface.accept_audio_preview("user-song")
        accepted_track_id = accepted_track["revision_record"]["revision_id"]
        assert accepted_track_id != root["project"]["revision_id"]

        parent = project.read_revision(accepted_track_id)
        clip = _candidate(parent, "R1A-CLIP", [
            {"operation_id": "R1A-ADD-C", "op": "ADD_CLIP",
             "target": {"track_id": "AT-R1A"},
             "clip": {"clip_id": "AC-R1A", "asset_id": asset["asset_id"],
                      "timeline_start_seconds": 0.0, "source_in_seconds": 0.0,
                      "source_out_seconds": 0.1, "gain_db": 0.0}}
        ])
        preview_clip = surface.preview_audio_edit(
            "user-song", candidate=clip, candidate_kind="arrangement"
        )
        assert preview_clip["preview_installed"] is True
        assert preview_clip["audio_view"]["preview"]["audition"]["available"] is True
        assert project.head_revision_id() == accepted_track_id
        accepted_clip = surface.accept_audio_preview("user-song")
        new_head = accepted_clip["revision_record"]["revision_id"]
        assert new_head != accepted_track_id
        assert accepted_clip["audio_view"]["preview"] is None
        with urlopen(base + "/v0/sessions/user-song/audio/accepted.wav", timeout=10) as response:
            raw = response.read()
            assert response.status == 200
        assert raw.startswith(b"RIFF") and raw[8:12] == b"WAVE"
        assert len(raw) > 44
        report = service.export_project("user-song")
        assert report["sha256"]
        assert project.head_revision_id() == new_head
        reopened_service = StudioService(tmp_path / "workspace")
        reopened = reopened_service.open_project_session(
            project_slug="first-song", session_id="reopened-user-song"
        )
        reopened_project = reopened_service._get_session("reopened-user-song").project
        assert reopened["session"]["head_revision_id"] == new_head
        assert read_audio_asset(reopened_project, asset["asset_id"]) == asset
        assert reopened_project.verify_integrity()["status"] == "PASS"


def test_r1a_invalid_file_and_unknown_session_fail_closed(tmp_path):
    with _studio(tmp_path) as (service, initial, base):
        project = service._get_session("user-song").project
        head = project.head_revision_id()
        for data, kwargs, expected in [
            (b"A" * 60, {}, 400),
            (_wav(), {"content_type": "application/json"}, 400),
            (_wav(), {"session": "missing-session"}, 404),
            (_wav(), {"length": MAX_WAV_IMPORT_BYTES + 1}, 400),
        ]:
            try:
                _post_wav(base, data, **kwargs)
                raise AssertionError("invalid import unexpectedly succeeded")
            except HTTPError as exc:
                assert exc.code == expected
                assert json.loads(exc.read().decode("utf-8"))["ok"] is False
        assert project.head_revision_id() == head
        assert list_audio_assets(project) == []


def test_r1a_import_conflicts_with_pending_noncanonical_preview(tmp_path):
    with _studio(tmp_path) as (service, initial, base):
        project = service._get_session("user-song").project
        before = project.head_revision_id()
        parent = project.read_revision(before)
        candidate = _candidate(parent, "R1A-PENDING", [
            {"operation_id": "R1A-T", "op": "ADD_TRACK",
             "track_id": "AT-PENDING", "order": 0, "name": "Pending"}
        ])
        surface = StudioAudioSurface(service)
        assert surface.preview_audio_edit(
            "user-song", candidate=candidate, candidate_kind="arrangement"
        )["preview_installed"]
        try:
            _post_wav(base, _wav())
            raise AssertionError("resource import during a pending Preview was allowed")
        except HTTPError as exc:
            assert exc.code == 409
        assert project.head_revision_id() == before
        assert list_audio_assets(project) == []
        surface.discard_audio_preview("user-song")
        assert project.head_revision_id() == before


def test_r1a_native_browser_assets_expose_real_import_control(tmp_path):
    with _studio(tmp_path) as (service, initial, base):
        with urlopen(base + "/assets/app.js", timeout=10) as response:
            js = response.read().decode("utf-8")
        for piece in ("r3WavFile", "r3ImportWav", "importWav", "/audio/import-wav",
                      "requires_separate_clip_preview_and_explicit_accept"):
            assert piece in js
        assert "/assets/app.js" not in js.split("MUSICA_NATIVE_AUDIO")[0] or "Import" in js
