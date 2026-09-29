from __future__ import annotations

from pathlib import Path

from musica.automation_edit import automation_material_sha256
from musica.audio_edit import audio_material_sha256, blueprint_sha256
from musica.native_mixer_automation import build_native_mixer_automation_plan
from musica.routed_mixer import render_routed_mix
from musica.routing_contracts import routing_material_from_blueprint, routing_material_sha256
from musica.studio import StudioService
from musica.studio_automation import StudioAutomationSurface
from musica.studio_routing import StudioRoutingSurface

from test_mram_r1_routing_authority_mixer import _accept_routing
from test_mram_r2_native_mixer_automation import _accept_native, _lane


def _routing_candidate(view: dict, candidate_id: str, operations: list[dict]) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_routing_material",
        "source": {
            "project_id": view["project_id"],
            "revision_id": view["revision_id"],
            "blueprint_sha256": view["blueprint_sha256"],
            "audio_material_sha256": view["audio_material_sha256"],
            "routing_material_sha256": view["routing_material_sha256"],
        },
        "actor": {"kind": "user", "actor_id": "mram-r3-test"},
        "reason": candidate_id,
        "operations": operations,
        "preview_only": True,
    }


def _automation_candidate(view: dict, candidate_id: str, operations: list[dict]) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_automation_material",
        "source": {
            "project_id": view["project_id"],
            "revision_id": view["revision_id"],
            "blueprint_sha256": view["blueprint_sha256"],
            "automation_material_sha256": view["automation_material_sha256"],
            "audio_material_sha256": view["audio_material_sha256"],
            "routing_material_sha256": view["routing_material_sha256"],
        },
        "actor": {"kind": "user", "actor_id": "mram-r3-test"},
        "reason": candidate_id,
        "operations": operations,
        "preview_only": True,
    }


def _fixture(tmp_path: Path):
    project, routed = _accept_routing(tmp_path)
    lane = _lane(
        "AUTO-AT001-GAIN",
        scope="audio_track",
        owner_id="AT-001",
        parameter_id="mixer.gain_db",
        points=[
            ("P-R3-1", 0.0, -3.0, "linear"),
            ("P-R3-2", 1.0, -6.0, "hold"),
        ],
    )
    accepted = _accept_native(project, routed, "R3-NATIVE", [lane])
    return project, accepted


def test_studio_routing_view_binds_exact_accepted_state_and_routed_audition(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    service = StudioService(tmp_path)
    opened = service.open_project_session(
        project_slug="song",
        session_id="studio-r3-routing",
    )
    assert opened["session"]["head_revision_id"] == accepted["project"]["revision_id"]

    surface = StudioRoutingSurface(service)
    view = surface.routing_view("studio-r3-routing")
    routing = routing_material_from_blueprint(accepted)
    assert routing is not None
    assert view["blueprint_sha256"] == blueprint_sha256(accepted)
    assert view["audio_material_sha256"] == audio_material_sha256(accepted)
    assert view["routing_material_sha256"] == routing_material_sha256(routing)
    assert view["automation_material_sha256"] == automation_material_sha256(accepted)
    assert view["accepted_state_is_canonical"] is True
    assert view["browser_state_is_canonical"] is False
    assert view["accepted_audition"]["available"] is True
    assert view["accepted_audition"]["wav_sha256"] == render_routed_mix(
        project,
        accepted["project"]["revision_id"],
        mix_sample_rate_hz=8000,
    ).wav_sha256
    assert {
        (lane["target"]["scope"], lane["target"]["owner_id"], lane["target"]["parameter_id"])
        for lane in view["native_automation_lanes"]
    } == {("audio_track", "AT-001", "mixer.gain_db")}


def test_browser_routing_preview_accept_uses_trusted_authority_and_changes_exact_routed_output(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    service = StudioService(tmp_path)
    service.open_project_session(project_slug="song", session_id="studio-r3-edit")
    surface = StudioRoutingSurface(service)
    before_view = surface.routing_view("studio-r3-edit")
    before_head = service.inspect_session("studio-r3-edit")["head_revision_id"]
    before_wav = surface.audition_bytes("studio-r3-edit", source_kind="accepted")

    candidate = _routing_candidate(
        before_view,
        "R3-SEND-GAIN",
        [
            {
                "operation_id": "R3-SEND-1",
                "op": "SET_SEND_GAIN",
                "send_id": "SEND-001",
                "gain_db": -2.0,
            }
        ],
    )
    preview = surface.preview_routing_edit("studio-r3-edit", candidate=candidate)
    assert preview["preview_installed"] is True
    assert preview["authority_result"]["status"] == "READY_FOR_PREVIEW"
    assert service.inspect_session("studio-r3-edit")["head_revision_id"] == before_head
    assert preview["routing_view"]["preview"]["changed_send_ids"] == ["SEND-001"]
    preview_wav = surface.audition_bytes("studio-r3-edit", source_kind="preview")
    assert preview_wav != before_wav

    accepted_result = service.accept_preview("studio-r3-edit")
    after_head = accepted_result["revision_record"]["revision_id"]
    assert after_head != before_head
    after_view = surface.routing_view("studio-r3-edit")
    send = next(item for item in after_view["sends"] if item["send_id"] == "SEND-001")
    assert send["gain_db"] == -2.0
    assert surface.audition_bytes("studio-r3-edit", source_kind="accepted") == preview_wav
    assert service.inspect_session("studio-r3-edit")["integrity_status"] == "PASS"


def test_browser_native_automation_preview_accept_reuses_mram_r2_authority_and_routed_audition(
    tmp_path: Path,
) -> None:
    _project, accepted = _fixture(tmp_path)
    service = StudioService(tmp_path)
    service.open_project_session(project_slug="song", session_id="studio-r3-auto")
    automation = StudioAutomationSurface(service)
    view = automation.automation_view("studio-r3-auto")

    assert view["audio_material_sha256"]
    assert view["routing_material_sha256"]
    lane = next(item for item in view["lanes"] if item["lane_id"] == "AUTO-AT001-GAIN")
    assert lane["target"]["scope"] == "audio_track"

    candidate = _automation_candidate(
        view,
        "R3-AUTO-VALUE",
        [
            {
                "operation_id": "R3-AUTO-OP",
                "op": "SET_VALUE",
                "target": {"lane_id": "AUTO-AT001-GAIN", "point_id": "P-R3-1"},
                "value": -12.0,
            }
        ],
    )
    head_before = service.inspect_session("studio-r3-auto")["head_revision_id"]
    preview = automation.preview_automation_edit("studio-r3-auto", candidate=candidate)
    assert preview["preview_installed"] is True
    assert service.inspect_session("studio-r3-auto")["head_revision_id"] == head_before
    assert preview["studio_audition"]["path"] == "mram-r2-routed-native-mixer"
    assert preview["studio_audition"]["automation_applied"] is True

    accepted_result = service.accept_preview("studio-r3-auto")
    assert accepted_result["revision_record"]["parent_revision_id"] == head_before
    accepted_view = automation.automation_view("studio-r3-auto")
    accepted_lane = next(
        item for item in accepted_view["lanes"] if item["lane_id"] == "AUTO-AT001-GAIN"
    )
    point = next(item for item in accepted_lane["points"] if item["point_id"] == "P-R3-1")
    assert point["value"] == -12.0


def test_fresh_studio_restart_reopen_preserves_routing_automation_plan_and_wav(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    plan_before = build_native_mixer_automation_plan(
        project, revision_id, mix_sample_rate_hz=8000
    )
    render_before = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)

    service1 = StudioService(tmp_path)
    opened1 = service1.open_project_session(
        project_slug="song", session_id="studio-r3-before"
    )
    view1 = StudioRoutingSurface(service1).routing_view("studio-r3-before")
    service1.close_session("studio-r3-before")

    service2 = StudioService(tmp_path)
    opened2 = service2.open_project_session(
        project_slug="song", session_id="studio-r3-after"
    )
    view2 = StudioRoutingSurface(service2).routing_view("studio-r3-after")
    reopened = service2._get_session("studio-r3-after").project
    plan_after = build_native_mixer_automation_plan(
        reopened, revision_id, mix_sample_rate_hz=8000
    )
    render_after = render_routed_mix(reopened, revision_id, mix_sample_rate_hz=8000)

    assert opened1["session"]["head_revision_id"] == revision_id
    assert opened2["session"]["head_revision_id"] == revision_id
    assert view2["routing_material_sha256"] == view1["routing_material_sha256"]
    assert view2["automation_material_sha256"] == view1["automation_material_sha256"]
    assert view2["native_automation_lanes"] == view1["native_automation_lanes"]
    assert plan_after == plan_before
    assert render_after.plan == render_before.plan
    assert render_after.wav_bytes == render_before.wav_bytes
    assert service2.inspect_session("studio-r3-after")["integrity_status"] == "PASS"
