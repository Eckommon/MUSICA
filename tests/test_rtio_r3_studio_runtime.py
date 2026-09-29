from __future__ import annotations

from pathlib import Path

import pytest

from musica.realtime_engine import build_realtime_execution_plan
from musica.routing_edit import accept_routing_edit_preview, build_routing_edit_preview
from musica.studio import StudioService, StudioServiceError
from musica.studio_realtime import StudioRealtimeSurface

from test_mram_r1_routing_authority_mixer import _routing_candidate
from test_rtio_r0_realtime_simulated_backend import _fixture


def _service_fixture(tmp_path: Path):
    project, accepted = _fixture(tmp_path)
    service = StudioService(tmp_path)
    opened = service.open_project_session(
        project_slug="song",
        session_id="studio-rtio-r3",
    )
    assert opened["session"]["head_revision_id"] == accepted["project"]["revision_id"]
    return project, accepted, service, StudioRealtimeSurface(service)


def test_studio_realtime_view_binds_exact_accepted_source_and_is_noncanonical(
    tmp_path: Path,
) -> None:
    project, accepted, service, surface = _service_fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    head_before = project.head_revision_id("main")
    expected = build_realtime_execution_plan(
        project,
        revision_id,
        sample_rate_hz=8000,
        output_channels=2,
        block_size_frames=256,
    )

    view = surface.open_runtime(
        "studio-rtio-r3",
        sample_rate_hz=8000,
        output_channels=2,
        block_size_frames=256,
    )
    assert view["revision_id"] == revision_id
    assert (
        view["realtime_execution_plan_sha256"]
        == expected["realtime_execution_plan_sha256"]
    )
    assert view["source"] == {
        key: expected["source"][key]
        for key in (
            "blueprint_sha256",
            "audio_material_sha256",
            "routing_material_sha256",
            "automation_material_sha256",
            "routed_mix_plan_sha256",
            "routed_wav_sha256",
        )
    }
    assert view["transport"]["state"] == "STOPPED"
    assert view["transport"]["playhead_frame"] == 0
    assert view["transport"]["callback_index"] is None
    assert view["latency"]["nominal_source"] == "simulated_backend_capability"
    assert view["latency"]["host_observed_latency_available"] is False
    assert view["latency"]["wall_clock_guarantee_claimed"] is False
    assert view["authority"] == {
        "accepted_project_state_is_canonical": True,
        "runtime_state_is_canonical": False,
        "browser_state_is_canonical": False,
        "project_mutation_authorized": False,
        "runtime_commands_mutate_project": False,
        "position_authority": "exact_frame_cursor_not_wall_clock",
    }
    assert project.head_revision_id("main") == head_before
    assert service.inspect_session("studio-rtio-r3")["head_revision_id"] == head_before


def test_runtime_play_step_stop_seek_commands_delegate_to_rtio_r2_without_project_mutation(
    tmp_path: Path,
) -> None:
    project, accepted, _service, surface = _service_fixture(tmp_path)
    head_before = accepted["project"]["revision_id"]
    opened = surface.open_runtime("studio-rtio-r3", sample_rate_hz=8000)
    runtime_id = opened["runtime_id"]

    playing = surface.play("studio-rtio-r3", runtime_id)["runtime"]
    assert playing["transport"]["state"] == "PLAYING"
    assert playing["transport"]["callback_index"] == 0

    stepped = surface.callback("studio-rtio-r3", runtime_id)["runtime"]
    assert stepped["transport"]["playhead_frame"] == 256
    assert stepped["transport"]["callback_index"] == 1
    assert stepped["metrics"]["callbacks_requested"] == 1
    assert stepped["metrics"]["frames_requested"] == 256
    assert stepped["metrics"]["frames_delivered"] == 256

    stopped = surface.stop("studio-rtio-r3", runtime_id)["runtime"]
    assert stopped["transport"]["state"] == "STOPPED"
    assert stopped["transport"]["playhead_frame"] == 256
    assert stopped["transport"]["callback_index"] is None

    sought = surface.seek(
        "studio-rtio-r3", runtime_id, target_frame=48000
    )["runtime"]
    assert sought["transport"]["playhead_frame"] == 48000
    assert sought["metrics"]["seek_count"] == 1
    assert sought["metrics"]["transport_discontinuity_count"] == 1

    surface.play("studio-rtio-r3", runtime_id)
    after_seek = surface.callback("studio-rtio-r3", runtime_id)["runtime"]
    assert after_seek["transport"]["playhead_frame"] == 48256
    assert after_seek["transport"]["callback_index"] == 1
    surface.stop("studio-rtio-r3", runtime_id)

    closed = surface.close_runtime("studio-rtio-r3", runtime_id)
    assert closed["transport_report"]["metrics"]["final_state"] == "STOPPED"
    assert closed["transport_report"]["metrics"]["final_playhead_frame"] == 48256
    assert closed["accepted_head_unchanged"] is True
    assert closed["runtime_state_is_canonical"] is False
    assert project.head_revision_id("main") == head_before


def test_unknown_runtime_and_accepted_head_advance_fail_closed(tmp_path: Path) -> None:
    project, accepted, _service, surface = _service_fixture(tmp_path)
    with pytest.raises(StudioServiceError, match="unknown realtime runtime"):
        surface.runtime_view("studio-rtio-r3", "rtio-missing")

    opened = surface.open_runtime("studio-rtio-r3", sample_rate_hz=8000)
    runtime_id = opened["runtime_id"]

    candidate = _routing_candidate(
        accepted,
        "RTIO-R3-ADVANCE",
        [
            {
                "operation_id": "RTIO-R3-SEND",
                "op": "SET_SEND_GAIN",
                "send_id": "SEND-001",
                "gain_db": -2.0,
            }
        ],
    )
    preview = build_routing_edit_preview(project, accepted, candidate)
    assert preview.ready
    accept_routing_edit_preview(project, preview)

    with pytest.raises(StudioServiceError, match="accepted Project HEAD changed"):
        surface.runtime_view("studio-rtio-r3", runtime_id)


def test_fresh_service_restart_rebuilds_same_plan_and_does_not_persist_playhead(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    service1 = StudioService(tmp_path)
    service1.open_project_session(
        project_slug="song", session_id="studio-rtio-r3"
    )
    surface1 = StudioRealtimeSurface(service1)
    before = surface1.open_runtime("studio-rtio-r3", sample_rate_hz=8000)
    runtime_id_before = before["runtime_id"]
    surface1.play("studio-rtio-r3", runtime_id_before)
    surface1.callback("studio-rtio-r3", runtime_id_before)
    surface1.stop("studio-rtio-r3", runtime_id_before)
    close_before = surface1.close_runtime("studio-rtio-r3", runtime_id_before)
    service1.close_session("studio-rtio-r3")

    service2 = StudioService(tmp_path)
    opened2 = service2.open_project_session(
        project_slug="song", session_id="studio-rtio-r3"
    )
    surface2 = StudioRealtimeSurface(service2)
    after = surface2.open_runtime("studio-rtio-r3", sample_rate_hz=8000)

    assert opened2["session"]["head_revision_id"] == revision_id
    assert after["runtime_id"] == runtime_id_before
    assert (
        after["realtime_execution_plan_sha256"]
        == before["realtime_execution_plan_sha256"]
    )
    assert after["source"] == before["source"]
    assert after["transport"]["state"] == "STOPPED"
    assert after["transport"]["playhead_frame"] == 0
    assert after["metrics"]["callbacks_requested"] == 0
    assert close_before["transport_report"]["metrics"]["final_playhead_frame"] == 256
    assert service2.inspect_session("studio-rtio-r3")["head_revision_id"] == revision_id
    assert project.head_revision_id("main") == revision_id
