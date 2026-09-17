from __future__ import annotations

import io
import json
import threading
import urllib.request
import wave
from pathlib import Path

import pytest

from musica.audio_assets import import_audio_asset
from musica.audio_edit import (
    accept_audio_edit_preview,
    audio_material_sha256,
    blueprint_sha256,
    build_audio_edit_preview,
)
from musica.creative import compose_blueprint
from musica.studio import StudioService, StudioServiceError
from musica.studio_audio import StudioAudioSurface
from musica.studio_http_r3 import create_local_server
from musica.project import create_project

ROOT = Path(__file__).resolve().parents[1]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def _blueprint() -> dict:
    return compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))


def _wav_bytes(*, sample_rate: int = 8000, frames: int = 800) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        payload = b"".join(int(12000 if index % 2 == 0 else -12000).to_bytes(2, "little", signed=True) for index in range(frames))
        writer.writeframes(payload)
    return stream.getvalue()


def _source(parent: dict) -> dict:
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
    }


def _candidate(parent: dict, candidate_id: str, operations: list[dict], *, actor: str = "r3-test") -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_audio_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": actor},
        "reason": f"ATCM-R3 candidate {candidate_id}",
        "operations": operations,
        "preview_only": True,
    }


def _workspace(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    root = _blueprint()
    project = create_project(workspace / "native.musica", root)
    wav = tmp_path / "source.wav"
    wav.write_bytes(_wav_bytes())
    asset = import_audio_asset(project, wav)
    arrange = _candidate(root, "R3-SETUP", [
        {"operation_id":"R3-SETUP-T","op":"ADD_TRACK","track_id":"AT-R3","order":0,"name":"Native"},
        {"operation_id":"R3-SETUP-C","op":"ADD_CLIP","target":{"track_id":"AT-R3"},"clip":{"clip_id":"AC-R3","asset_id":asset["asset_id"],"timeline_start_seconds":0.0,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
    ])
    preview = build_audio_edit_preview(project, root, arrange)
    assert preview.ready
    record = accept_audio_edit_preview(project, preview)
    accepted = project.read_revision(record["revision_id"])
    service = StudioService(workspace)
    opened = service.open_project_session(project_slug="native", session_id="studio-r3")
    assert opened["session"]["head_revision_id"] == accepted["project"]["revision_id"]
    return workspace, service, StudioAudioSurface(service), accepted, asset


def test_r3_projects_accepted_audio_and_preview_without_advancing_head(tmp_path: Path) -> None:
    _, service, surface, accepted, _ = _workspace(tmp_path)
    source_head = service._get_session("studio-r3").project.head_revision_id()
    view = surface.audio_view("studio-r3")
    assert view["revision_id"] == source_head
    assert view["accepted_state_is_canonical"] is True
    assert view["browser_state_is_canonical"] is False
    assert view["accepted_audition"]["available"] is True
    assert view["tracks"][0]["track_id"] == "AT-R3"

    candidate = _candidate(accepted, "R3-MOVE", [
        {"operation_id":"R3-MOVE-OP","op":"MOVE_CLIP","target":{"track_id":"AT-R3","clip_id":"AC-R3"},"timeline_start_seconds":0.2}
    ])
    result = surface.preview_audio_edit("studio-r3", candidate=candidate, candidate_kind="arrangement")
    assert result["preview_installed"] is True
    assert service._get_session("studio-r3").project.head_revision_id() == source_head
    assert result["audio_view"]["preview"]["audition"]["available"] is True
    assert result["audio_view"]["preview"]["tracks"][0]["clips"][0]["timeline_start_seconds"] == 0.2

    # Generic Studio acceptance is intentionally not authorized for native-audio changes.
    with pytest.raises(StudioServiceError):
        service.accept_preview("studio-r3")
    assert service._get_session("studio-r3").project.head_revision_id() == source_head

    discarded = surface.discard_audio_preview("studio-r3")
    assert discarded["head_revision_id"] == source_head
    assert discarded["audio_view"]["preview"] is None


def test_r3_mixer_preview_uses_trusted_audio_accept_and_advances_once(tmp_path: Path) -> None:
    _, service, surface, accepted, _ = _workspace(tmp_path)
    source_head = accepted["project"]["revision_id"]
    before_wav = surface.audio_view("studio-r3")["accepted_audition"]["wav_sha256"]
    candidate = _candidate(accepted, "R3-MIX", [
        {"operation_id":"R3-MIX-OP","op":"SET_TRACK_MIXER","target":{"track_id":"AT-R3"},"mixer":{"gain_db":-6.0,"pan":0.5,"mute":False,"solo":True}}
    ])
    preview = surface.preview_audio_edit("studio-r3", candidate=candidate, candidate_kind="mixer")
    assert preview["preview_installed"] is True
    assert preview["audio_view"]["preview"]["candidate_kind"] == "mixer"
    assert service._get_session("studio-r3").project.head_revision_id() == source_head

    accepted_result = surface.accept_audio_preview("studio-r3")
    new_head = accepted_result["revision_record"]["revision_id"]
    assert new_head != source_head
    assert service._get_session("studio-r3").project.head_revision_id() == new_head
    view = accepted_result["audio_view"]
    assert view["preview"] is None
    assert view["tracks"][0]["mixer"] == {"gain_db":-6.0,"pan":0.5,"mute":False,"solo":True}
    assert view["accepted_audition"]["wav_sha256"] != before_wav


def test_r3_stale_pending_preview_fails_closed_after_head_change(tmp_path: Path) -> None:
    _, service, surface, accepted, _ = _workspace(tmp_path)
    stale_candidate = _candidate(accepted, "R3-STALE", [
        {"operation_id":"R3-STALE-MIX","op":"SET_TRACK_MIXER","target":{"track_id":"AT-R3"},"mixer":{"gain_db":-2.0,"pan":0.0,"mute":False,"solo":False}}
    ])
    result = surface.preview_audio_edit("studio-r3", candidate=stale_candidate, candidate_kind="mixer")
    assert result["preview_installed"] is True

    project = service._get_session("studio-r3").project
    concurrent = _candidate(accepted, "R3-CONCURRENT", [
        {"operation_id":"R3-CONCURRENT-GAIN","op":"SET_CLIP_GAIN","target":{"track_id":"AT-R3","clip_id":"AC-R3"},"gain_db":-1.0}
    ])
    concurrent_preview = build_audio_edit_preview(project, accepted, concurrent)
    assert concurrent_preview.ready
    accept_audio_edit_preview(project, concurrent_preview)
    with pytest.raises(StudioServiceError, match="stale|HEAD changed"):
        surface.accept_audio_preview("studio-r3")


def test_r3_http_adds_same_origin_native_audio_surface(tmp_path: Path) -> None:
    _, service, _, _, _ = _workspace(tmp_path)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval":0.01}, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        with urllib.request.urlopen(base + "/assets/app.js", timeout=10) as response:
            javascript = response.read().decode("utf-8")
        assert "MUSICA_NATIVE_AUDIO" in javascript
        with urllib.request.urlopen(base + "/v0/sessions/studio-r3/audio", timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["ok"] is True
        assert payload["data"]["accepted_state_is_canonical"] is True
        with urllib.request.urlopen(base + "/v0/sessions/studio-r3/audio/accepted.wav", timeout=10) as response:
            wav = response.read()
        assert wav[:4] == b"RIFF" and wav[8:12] == b"WAVE"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
