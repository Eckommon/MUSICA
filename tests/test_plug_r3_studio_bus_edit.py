"""PLUG-R3 Studio simulated bus-host edit authority and HTTP integration."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest

from musica.bus_host_edit import source_for_bus_host_candidate
from musica.bus_host_material import bus_host_material_from_blueprint
from musica.bus_host_runtime import render_accepted_simulated_bus_host
from musica.studio import StudioService, StudioServiceError
from musica.studio_bus_plugin_edit import StudioBusHostEditSurface
from musica.studio_http import create_local_server
from musica.project import MusicaProject

from test_plug_r2b_k1b_accepted_bus_host import _candidate, _instance, _material
from test_plug_r2b_k2_studio_bus_plugins import _service, _pair


def _edit(service: StudioService, sid: str, project, before: dict, material: dict, label: str = "EDIT"):
    surface = StudioBusHostEditSurface(service)
    candidate = _candidate(before, material, "STUDIO-" + label)
    head = project.head_revision_id("main")
    preview = surface.preview_edit(sid, candidate=candidate)
    assert preview["preview_installed"] is True
    assert project.head_revision_id("main") == head
    return preview


def test_view_exact_accepted_source_and_two_eligible_buses(tmp_path: Path):
    service, sid, project, rid = _service(tmp_path)
    view = StudioBusHostEditSurface(service).editor_view(sid)
    blueprint = project.read_revision(rid)
    assert view["source"] == source_for_bus_host_candidate(blueprint)
    assert view["supported_buses"] == [
        {"track_id": "AT-001", "bus_node_id": "BUS-001"},
        {"track_id": "AT-002", "bus_node_id": "BUS-002"},
    ]
    assert view["eligible_for_bounded_preview"] is True
    assert view["accepted_material"]["instances"] == []
    assert view["capabilities"]["default_studio_media_overridden"] is False
    assert view["capabilities"]["native_binary_plugin_host"] is False
    assert project.head_revision_id("main") == rid


def test_preview_wav_accept_recompute_and_no_generic_audio_rebind(tmp_path: Path):
    service, sid, project, rid = _service(tmp_path)
    surface = StudioBusHostEditSurface(service)
    parent = project.read_revision(rid)
    original_media = service.media_bytes(sid, "audio")
    preview = _edit(service, sid, project, parent, _pair(), "PAIR")
    assert preview["preview"]["kind"] == "bus_host_edit"
    assert preview["preview"]["audio_available"] is True
    assert preview["preview"]["midi_available"] is False
    assert surface.editor_view(sid)["accepted_material"]["instances"] == []
    assert surface.editor_view(sid)["preview_pending"] is True
    raw = surface.preview_wav(sid)
    assert hashlib.sha256(raw).hexdigest() == preview["detail"]["offline_preview"]["wav_sha256"]
    assert service.media_bytes(sid, "audio") == original_media
    accepted = service.accept_preview(sid)
    assert accepted["artifact_manifest"] is None
    actual = project.read_revision(accepted["revision_record"]["revision_id"])
    assert bus_host_material_from_blueprint(actual) == _pair()
    assert actual["project"]["parent_revision_id"] == rid
    assert service.inspect_session(sid)["pending_preview"] is None
    assert service.media_bytes(sid, "audio") == original_media
    rendered = render_accepted_simulated_bus_host(
        project, actual["project"]["revision_id"], sample_rate_hz=8000
    )
    assert rendered.wav_bytes == raw
    with pytest.raises(StudioServiceError):
        surface.preview_wav(sid)


def test_bypass_creative_remove_discard_and_reopen(tmp_path: Path):
    service, sid, project, rid = _service(tmp_path)
    first = project.read_revision(rid)
    surface = StudioBusHostEditSurface(service)
    _edit(service, sid, project, first, _pair(), "ADD")
    accepted = service.accept_preview(sid)
    current = project.read_revision(accepted["revision_record"]["revision_id"])

    update = _material([
        _instance(latency=3, creative=5, bypass=True),
        _instance("BUS-002", instance_id="BPI-002", latency=9),
    ])
    _edit(service, sid, project, current, update, "BYPASS")
    previous_head = project.head_revision_id("main")
    discarded = service.discard_preview(sid)
    assert discarded["head_revision_id"] == previous_head
    assert bus_host_material_from_blueprint(project.read_revision(previous_head)) == _pair()
    _edit(service, sid, project, current, update, "BYPASS2")
    saved = service.accept_preview(sid)
    bypass_rid = saved["revision_record"]["revision_id"]
    assert bus_host_material_from_blueprint(project.read_revision(bypass_rid)) == update

    _edit(service, sid, project, project.read_revision(bypass_rid), _material([]), "REMOVE")
    removed = service.accept_preview(sid)
    assert bus_host_material_from_blueprint(
        project.read_revision(removed["revision_record"]["revision_id"])
    )["instances"] == []
    archive = project.export_to(tmp_path / "plug-r3.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "plug-r3-reopen")
    assert bus_host_material_from_blueprint(reopened.read_revision(bypass_rid)) == update


def test_stale_blocked_candidate_and_corrupt_pending_fail_closed(tmp_path: Path):
    service, sid, project, rid = _service(tmp_path)
    parent = project.read_revision(rid)
    surface = StudioBusHostEditSurface(service)
    candidate = _candidate(parent, _pair(), "STUDIO-BLOCK")
    stale = copy.deepcopy(candidate)
    stale["source"]["blueprint_sha256"] = "f" * 64
    result = surface.preview_edit(sid, candidate=stale)
    assert result["preview_installed"] is False
    assert service.inspect_session(sid)["pending_preview"] is None
    with pytest.raises(StudioServiceError):
        surface.preview_wav(sid)
    _edit(service, sid, project, parent, _pair(), "CORRUPT")
    project_head = project.head_revision_id("main")
    service._get_session(sid).pending.candidate["materials"]["bus_plugins"]["instances"][0]["algorithmic_latency_frames"] = 4
    with pytest.raises(StudioServiceError, match="recomputed bus-host"):
        service.accept_preview(sid)
    assert project.head_revision_id("main") == project_head
    service.discard_preview(sid)
    _edit(service, sid, project, parent, _pair(), "WAV-TAMPER")
    service._get_session(sid).pending.wav_path.write_bytes(b"tampered")
    with pytest.raises(StudioServiceError, match="WAV was modified"):
        service.accept_preview(sid)
    assert project.head_revision_id("main") == project_head


def test_http_preview_wav_accept_and_missing_preview_404(tmp_path: Path):
    service, sid, project, rid = _service(tmp_path)
    parent = project.read_revision(rid)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    def get(path):
        with urlopen(base + path, timeout=30) as res:
            return res.status, res.read(), res.headers.get("Content-Type")
    def post(path, data):
        body = json.dumps(data).encode("utf-8")
        req = Request(base + path, data=body, headers={"Content-Type":"application/json"}, method="POST")
        with urlopen(req, timeout=30) as res:
            return json.loads(res.read())
    try:
        base = f"http://127.0.0.1:{server.server_port}/v0/sessions/{sid}"
        status,raw,_ = get("/bus-plugins/editor")
        view=json.loads(raw)["data"]
        assert status == 200
        assert view["source"] == source_for_bus_host_candidate(parent)
        result=post("/preview/bus-plugins",{"candidate":_candidate(parent,_pair(),"HTTP")})
        assert result["data"]["preview_installed"] is True
        status, preview_wav,ctype = get("/bus-plugins/media/preview.wav")
        assert status == 200 and ctype=="audio/wav"
        assert hashlib.sha256(preview_wav).hexdigest() == result["data"]["detail"]["offline_preview"]["wav_sha256"]
        assert project.head_revision_id("main") == rid
        accepted = post("/preview/accept",{})
        new_rid=accepted["data"]["revision_record"]["revision_id"]
        assert project.head_revision_id("main") == new_rid
        assert accepted["data"]["artifact_manifest"] is None
        with pytest.raises(HTTPError) as exc:
            get("/bus-plugins/media/preview.wav")
        assert exc.value.code == 404
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
