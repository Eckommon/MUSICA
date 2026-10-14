"""K2 Studio bus host truthful accepted view and explicit offline media."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from threading import Thread
from urllib.request import urlopen
from urllib.error import HTTPError

import pytest

from musica.bus_host_runtime import render_accepted_simulated_bus_host
from musica.studio import StudioService
from musica.studio_bus_plugins import StudioBusHostSurface
from musica.studio_http import create_local_server
from musica.studio import StudioServiceError
from test_plug_r2b_k1_accepted_bridge import _accepted_two_buses
from test_plug_r2b_k1b_accepted_bus_host import _accept, _instance, _material


def _service(tmp_path: Path) -> tuple[StudioService, str, object, str]:
    project, rid = _accepted_two_buses(tmp_path)
    service = StudioService(tmp_path)
    sid = "studio-bus-host-k2"
    opened = service.open_project_session(project_slug="song", session_id=sid)
    assert opened["session"]["head_revision_id"] == rid
    return service, sid, project, rid


def _pair():
    return _material([
        _instance(latency=3),
        _instance("BUS-002", instance_id="BPI-002", latency=9),
    ])


def test_studio_reports_only_accepted_host_and_does_not_mutate(tmp_path: Path):
    service, sid, project, rid = _service(tmp_path)
    surface = StudioBusHostSurface(service)
    empty = surface.bus_plugins_view(sid)
    assert empty["revision_id"] == rid
    assert empty["instances"] == []
    assert empty["accepted_state_is_canonical"] is True
    assert empty["pending_preview_is_not_included"] is True
    assert empty["capabilities"]["realtime_pdc"] is False
    assert empty["capabilities"]["native_vst3_clap_au_host"] is False
    assert empty["capabilities"]["default_studio_media_overridden"] is False
    assert empty["offline_audition"]["available"] is True
    before_head = project.head_revision_id("main")

    accepted = _accept(project, project.read_revision(rid), _pair(), "K2-STUDIO")
    rid = accepted["project"]["revision_id"]
    view = surface.bus_plugins_view(sid)
    assert view["revision_id"] == rid
    assert len(view["instances"]) == 2
    assert view["instances"][0]["algorithmic_latency_frames"] == 3
    assert view["offline_audition"]["available"] is True
    assert view["offline_audition"]["mode"] == "accepted_two_bus_simulated_reference_pdc"
    expected = render_accepted_simulated_bus_host(project, rid, sample_rate_hz=8000)
    raw = surface.accepted_offline_wav(sid)
    assert raw == expected.wav_bytes
    assert view["offline_audition"]["wav_sha256"] == hashlib.sha256(raw).hexdigest()
    assert view["offline_audition"]["processing_plan_sha256"] == expected.plan["bus_host_processing_plan_sha256"]
    assert project.head_revision_id("main") == rid
    assert before_head != rid
    assert view == surface.bus_plugins_view(sid)


def test_unsupported_project_is_inspectable_but_not_falsely_audible(tmp_path: Path):
    service = StudioService(tmp_path)
    created = service.create_project_session(
        project_slug="ordinary", user_text="A simple gentle melody",
        session_id="studio-ordinary", provider_mode="fixture",
    )
    sid = "studio-ordinary"
    assert created["session"]["head_revision_id"]
    surface = StudioBusHostSurface(service)
    view = surface.bus_plugins_view(sid)
    assert view["instances"] == []
    assert view["offline_audition"]["available"] is False
    assert view["offline_audition"]["unavailable_reason"]
    with pytest.raises(StudioServiceError):
        surface.accepted_offline_wav(sid)


def test_studio_http_accepted_wav_opt_in_and_errors(tmp_path: Path):
    service, sid, project, rid = _service(tmp_path)
    accepted = _accept(project, project.read_revision(rid), _pair(), "K2-HTTP")
    actual_rid = accepted["project"]["revision_id"]
    server = create_local_server(service, host="127.0.0.1", port=0)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}/v0/sessions/{sid}/bus-plugins"
        with urlopen(base, timeout=20) as response:
            payload = json.loads(response.read())
            assert response.status == 200
        assert payload["operation"] == "accepted_bus_plugins_view"
        assert payload["data"]["revision_id"] == actual_rid
        assert payload["data"]["offline_audition"]["available"] is True
        with urlopen(base + "/media/accepted.wav", timeout=20) as response:
            media = response.read()
            assert response.headers["Content-Type"] == "audio/wav"
        expected = render_accepted_simulated_bus_host(project, actual_rid, sample_rate_hz=8000)
        assert media == expected.wav_bytes
        assert project.head_revision_id("main") == actual_rid
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=10)


def test_http_not_found_when_session_unknown(tmp_path: Path):
    service = StudioService(tmp_path)
    server = create_local_server(service, host="127.0.0.1", port=0)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}/v0/sessions/not-a-session/bus-plugins"
        with pytest.raises(HTTPError) as exc:
            urlopen(base, timeout=10)
        assert exc.value.code == 404
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=10)
