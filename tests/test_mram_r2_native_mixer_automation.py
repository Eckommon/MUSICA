from __future__ import annotations

import copy
from pathlib import Path

import pytest

from musica.automation_edit import (
    accept_automation_edit_preview,
    automation_material_sha256,
    blueprint_sha256,
    build_automation_edit_preview,
)
from musica.automation_lowering import lower_automation_execution
from musica.audio_edit import audio_material_sha256
from musica.contracts import ContractError
from musica.native_mixer_automation import build_native_mixer_automation_plan
from musica.project import MusicaProject
from musica.routed_mixer import render_routed_mix
from musica.routing_contracts import (
    routing_material_from_blueprint,
    routing_material_sha256,
)
from test_mram_r1_routing_authority_mixer import _accept_audio, _accept_routing


def _source(parent: dict) -> dict:
    routing = routing_material_from_blueprint(parent)
    assert routing is not None
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "automation_material_sha256": automation_material_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(routing),
    }


def _lane(
    lane_id: str,
    *,
    scope: str,
    owner_id: str,
    parameter_id: str,
    points: list[tuple[str, float, float, str]],
) -> dict:
    if parameter_id == "mixer.gain_db":
        unit, minimum, maximum = "decibel", -60.0, 12.0
    elif parameter_id == "mixer.pan":
        unit, minimum, maximum = "normalized", -1.0, 1.0
    else:
        unit, minimum, maximum = "normalized", -1.0, 1.0
    return {
        "lane_id": lane_id,
        "target": {
            "parameter_id": parameter_id,
            "scope": scope,
            "owner_id": owner_id,
            "unit": unit,
            "minimum": minimum,
            "maximum": maximum,
        },
        "section_id": None,
        "points": [
            {
                "point_id": point_id,
                "beat": beat,
                "value": value,
                "interpolation": interpolation,
            }
            for point_id, beat, value, interpolation in points
        ],
    }


def _candidate(parent: dict, candidate_id: str, lanes: list[dict]) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_automation_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "mram-r2-test"},
        "reason": candidate_id,
        "operations": [
            {
                "operation_id": f"{candidate_id}-OP-{index:02d}",
                "op": "ADD_LANE",
                "lane": lane,
            }
            for index, lane in enumerate(lanes, start=1)
        ],
        "preview_only": True,
    }


def _accept_native(project, parent: dict, candidate_id: str, lanes: list[dict]) -> dict:
    preview = build_automation_edit_preview(
        parent,
        _candidate(parent, candidate_id, lanes),
        project=project,
    )
    assert preview.ready and preview.blueprint is not None
    assert project.head_revision_id("main") == parent["project"]["revision_id"]

    with pytest.raises(
        ContractError,
        match="native mixer automation changes require trusted automation",
    ):
        project.commit_revision(preview.blueprint)

    record = accept_automation_edit_preview(project, preview)
    assert record["parent_revision_id"] == parent["project"]["revision_id"]
    with pytest.raises(ContractError, match="stale|HEAD changed"):
        accept_automation_edit_preview(project, preview)
    return project.read_revision(record["revision_id"])


def test_track_gain_preview_accept_changes_routed_output_and_is_deterministic(
    tmp_path: Path,
) -> None:
    project, routed = _accept_routing(tmp_path)
    before = render_routed_mix(
        project, routed["project"]["revision_id"], mix_sample_rate_hz=8000
    )
    lane = _lane(
        "AUTO-AT001-GAIN",
        scope="audio_track",
        owner_id="AT-001",
        parameter_id="mixer.gain_db",
        points=[
            ("P-AT-G-0", 0.0, -6.0, "hold"),
            ("P-AT-G-1", 1.0, -6.0, "linear"),
        ],
    )
    accepted = _accept_native(project, routed, "R2-TRACK-GAIN", [lane])
    revision_id = accepted["project"]["revision_id"]

    lowering_a = build_native_mixer_automation_plan(
        project, revision_id, mix_sample_rate_hz=8000
    )
    lowering_b = build_native_mixer_automation_plan(
        project, revision_id, mix_sample_rate_hz=8000
    )
    assert lowering_a == lowering_b
    assert lowering_a["lanes"][0]["target_kind"] == "audio_track"
    assert lowering_a["lanes"][0]["target_id"] == "AT-001"
    assert lowering_a["lanes"][0]["parameter_id"] == "mixer.gain_db"

    after_a = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    after_b = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    assert after_a.plan == after_b.plan
    assert after_a.wav_bytes == after_b.wav_bytes
    assert after_a.wav_sha256 != before.wav_sha256
    assert after_a.peak_pre_clip < before.peak_pre_clip
    assert (
        after_a.plan["source"]["native_mixer_automation_plan_sha256"]
        == lowering_a["native_mixer_automation_plan_sha256"]
    )


def test_all_four_native_target_identities_lower_and_change_stereo_output(
    tmp_path: Path,
) -> None:
    project, routed = _accept_routing(tmp_path)
    lanes = [
        _lane(
            "AUTO-AT001-GAIN",
            scope="audio_track",
            owner_id="AT-001",
            parameter_id="mixer.gain_db",
            points=[("P1", 0.0, -3.0, "linear"), ("P2", 1.0, -6.0, "hold")],
        ),
        _lane(
            "AUTO-AT001-PAN",
            scope="audio_track",
            owner_id="AT-001",
            parameter_id="mixer.pan",
            points=[("P3", 0.0, -0.5, "linear"), ("P4", 1.0, 0.5, "hold")],
        ),
        _lane(
            "AUTO-BUS001-GAIN",
            scope="routing_node",
            owner_id="BUS-001",
            parameter_id="mixer.gain_db",
            points=[("P5", 0.0, 0.0, "linear"), ("P6", 1.0, -9.0, "hold")],
        ),
        _lane(
            "AUTO-BUS001-PAN",
            scope="routing_node",
            owner_id="BUS-001",
            parameter_id="mixer.pan",
            points=[("P7", 0.0, 0.75, "hold"), ("P8", 1.0, 0.75, "linear")],
        ),
    ]
    accepted = _accept_native(project, routed, "R2-FOUR-TARGETS", lanes)
    revision_id = accepted["project"]["revision_id"]
    lowering = build_native_mixer_automation_plan(
        project, revision_id, mix_sample_rate_hz=8000
    )
    identities = {
        (lane["target_kind"], lane["target_id"], lane["parameter_id"])
        for lane in lowering["lanes"]
    }
    assert identities == {
        ("audio_track", "AT-001", "mixer.gain_db"),
        ("audio_track", "AT-001", "mixer.pan"),
        ("routing_node", "BUS-001", "mixer.gain_db"),
        ("routing_node", "BUS-001", "mixer.pan"),
    }

    generic = lower_automation_execution(accepted)
    assert {
        (lane["scope"], lane["owner_id"], lane["parameter_id"])
        for lane in generic["lanes"]
    } == identities
    assert all(lane["backend_mapping"] == {"status": "UNMAPPED"} for lane in generic["lanes"])

    rendered = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    assert "native_mixer_automation" in rendered.plan
    assert rendered.plan["native_mixer_automation"]["lanes"] == lowering["lanes"]


def test_native_target_validation_and_stale_preview_fail_closed(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)

    missing_track = _lane(
        "AUTO-MISSING",
        scope="audio_track",
        owner_id="AT-MISSING",
        parameter_id="mixer.gain_db",
        points=[("PM1", 0.0, 0.0, "hold")],
    )
    blocked = build_automation_edit_preview(
        routed,
        _candidate(routed, "R2-MISSING", [missing_track]),
        project=project,
    )
    assert not blocked.ready
    assert "unknown audio track_id" in blocked.authority_result["conflicts"][0]["reason"]

    wrong_unit = _lane(
        "AUTO-WRONG-UNIT",
        scope="routing_node",
        owner_id="BUS-001",
        parameter_id="mixer.pan",
        points=[("PU1", 0.0, 0.0, "hold")],
    )
    wrong_unit["target"]["unit"] = "decibel"
    blocked_unit = build_automation_edit_preview(
        routed,
        _candidate(routed, "R2-WRONG-UNIT", [wrong_unit]),
        project=project,
    )
    assert not blocked_unit.ready
    assert "requires unit normalized" in blocked_unit.authority_result["conflicts"][0]["reason"]

    first_lane = _lane(
        "AUTO-FIRST",
        scope="audio_track",
        owner_id="AT-001",
        parameter_id="mixer.gain_db",
        points=[("PS1", 0.0, -1.0, "hold")],
    )
    stale_candidate = _candidate(routed, "R2-STALE", [
        _lane(
            "AUTO-STALE",
            scope="routing_node",
            owner_id="BUS-001",
            parameter_id="mixer.pan",
            points=[("PS2", 0.0, 0.1, "hold")],
        )
    ])
    _accept_native(project, routed, "R2-ADVANCE", [first_lane])
    stale = build_automation_edit_preview(routed, stale_candidate, project=project)
    assert not stale.ready
    assert stale.authority_result["conflicts"][0]["code"] == "STALE_SOURCE"
    assert "HEAD" in stale.authority_result["conflicts"][0]["reason"]


def test_native_automation_reopen_preserves_lowering_plan_and_wav(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    lane = _lane(
        "AUTO-BUS-PAN",
        scope="routing_node",
        owner_id="BUS-001",
        parameter_id="mixer.pan",
        points=[
            ("PR1", 0.0, -1.0, "linear"),
            ("PR2", 1.0, 1.0, "hold"),
        ],
    )
    accepted = _accept_native(project, routed, "R2-REOPEN", [lane])
    revision_id = accepted["project"]["revision_id"]
    lowering_before = build_native_mixer_automation_plan(
        project, revision_id, mix_sample_rate_hz=8000
    )
    render_before = render_routed_mix(
        project, revision_id, mix_sample_rate_hz=8000
    )

    archive = project.export_to(tmp_path / "mram-r2.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    lowering_after = build_native_mixer_automation_plan(
        reopened, revision_id, mix_sample_rate_hz=8000
    )
    render_after = render_routed_mix(
        reopened, revision_id, mix_sample_rate_hz=8000
    )
    assert lowering_after == lowering_before
    assert render_after.plan == render_before.plan
    assert render_after.wav_bytes == render_before.wav_bytes
    assert reopened.verify_integrity()["status"] == "PASS"


def test_native_preview_requires_persisted_source_and_routed_execution_context(
    tmp_path: Path,
) -> None:
    project, audio_only = _accept_audio(tmp_path / "audio-only")
    lane = _lane(
        "AUTO-AUDIO-ONLY",
        scope="audio_track",
        owner_id="AT-001",
        parameter_id="mixer.gain_db",
        points=[("PAO1", 0.0, -3.0, "hold")],
    )
    audio_only_preview = build_automation_edit_preview(
        audio_only,
        _candidate(audio_only, "R2-AUDIO-ONLY", [lane]),
        project=project,
    )
    assert not audio_only_preview.ready
    assert "requires accepted non-empty routing" in (
        audio_only_preview.authority_result["conflicts"][0]["reason"]
    )

    routed_project, routed = _accept_routing(tmp_path / "routed")
    forged = copy.deepcopy(routed)
    forged["project"]["title"] = str(forged["project"]["title"]) + " forged"
    forged_candidate = _candidate(
        forged,
        "R2-FORGED-SOURCE",
        [
            _lane(
                "AUTO-FORGED",
                scope="audio_track",
                owner_id="AT-001",
                parameter_id="mixer.pan",
                points=[("PF1", 0.0, 0.25, "hold")],
            )
        ],
    )
    forged_preview = build_automation_edit_preview(
        forged,
        forged_candidate,
        project=routed_project,
    )
    assert not forged_preview.ready
    assert forged_preview.authority_result["conflicts"][0]["code"] == "STALE_SOURCE"
    assert "persisted source Blueprint hash mismatch" in (
        forged_preview.authority_result["conflicts"][0]["reason"]
    )
