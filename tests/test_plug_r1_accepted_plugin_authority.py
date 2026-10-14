from __future__ import annotations

import copy
from pathlib import Path

import pytest

from musica.audio_edit import audio_material_sha256, blueprint_sha256
from musica.automation_edit import automation_material_sha256
from musica.contracts import ContractError
from musica.plugin_edit import (
    accept_plugin_edit_preview,
    build_plugin_edit_preview,
)
from musica.plugin_reference import (
    accepted_plugin_material_from_blueprint,
    accepted_plugin_material_sha256,
    build_accepted_plugin_processing_plan,
    empty_accepted_plugin_material,
    render_accepted_plugins,
)
from musica.project import MusicaProject
from musica.routed_mixer import render_routed_mix
from musica.routing_contracts import (
    routing_material_from_blueprint,
    routing_material_sha256,
)
from test_mram_r1_routing_authority_mixer import _accept_routing
from test_plug_r0_simulated_processor import _material as _r0_material


def _source(parent: dict) -> dict:
    routing = routing_material_from_blueprint(parent)
    assert routing is not None
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(routing),
        "automation_material_sha256": automation_material_sha256(parent),
        "plugin_material_sha256": accepted_plugin_material_sha256(parent),
    }


def _candidate(parent: dict, candidate_id: str, operations: list[dict]) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_plugin_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "plug-r1-test"},
        "reason": candidate_id,
        "operations": operations,
        "preview_only": True,
    }


def _descriptor() -> dict:
    return copy.deepcopy(_r0_material()["descriptors"][0])


def _instance(
    *,
    gain_db: float = -6.0,
    delay_frames: int = 4,
    bypass: bool = False,
    instance_id: str = "PI-001",
    owner_id: str = "MASTER-001",
    slot: int = 0,
) -> dict:
    value = copy.deepcopy(_r0_material()["instances"][0])
    value["instance_id"] = instance_id
    value["owner"]["owner_id"] = owner_id
    value["slot"] = slot
    value["bypass"] = bypass
    value["state"] = {"gain_db": gain_db, "delay_frames": delay_frames}
    return value


def _add_op(
    *,
    gain_db: float = -6.0,
    delay_frames: int = 4,
    bypass: bool = False,
    instance_id: str = "PI-001",
    owner_id: str = "MASTER-001",
    slot: int = 0,
) -> dict:
    return {
        "operation_id": f"ADD-{instance_id}",
        "op": "ADD_INSTANCE",
        "descriptor": _descriptor(),
        "instance": _instance(
            gain_db=gain_db,
            delay_frames=delay_frames,
            bypass=bypass,
            instance_id=instance_id,
            owner_id=owner_id,
            slot=slot,
        ),
    }


def _accept(project, parent: dict, candidate: dict) -> dict:
    preview = build_plugin_edit_preview(project, parent, candidate)
    assert preview.ready and preview.blueprint is not None
    head_before = project.head_revision_id("main")
    assert head_before == parent["project"]["revision_id"]
    with pytest.raises(
        ContractError,
        match="accepted plugin material changes require trusted plugin",
    ):
        project.commit_revision(preview.blueprint)
    record = accept_plugin_edit_preview(project, preview)
    assert record["parent_revision_id"] == head_before
    with pytest.raises(ContractError, match="stale|HEAD changed"):
        accept_plugin_edit_preview(project, preview)
    return project.read_revision(record["revision_id"])


def test_plugin_add_preview_accept_is_source_bound_and_executes_accepted_state(
    tmp_path: Path,
) -> None:
    project, routed = _accept_routing(tmp_path)
    assert accepted_plugin_material_from_blueprint(routed) == empty_accepted_plugin_material()
    candidate = _candidate(routed, "PLUG-R1-ADD", [_add_op()])
    preview = build_plugin_edit_preview(project, routed, candidate)
    assert preview.ready and preview.blueprint is not None
    assert project.head_revision_id("main") == routed["project"]["revision_id"]
    accepted = _accept(project, routed, candidate)

    material = accepted_plugin_material_from_blueprint(accepted)
    assert material["classification"] == "accepted_plugin_material"
    assert [item["instance_id"] for item in material["instances"]] == ["PI-001"]

    revision_id = accepted["project"]["revision_id"]
    plan_a = build_accepted_plugin_processing_plan(
        project, revision_id, sample_rate_hz=8000
    )
    plan_b = build_accepted_plugin_processing_plan(
        project, revision_id, sample_rate_hz=8000
    )
    assert plan_a == plan_b
    assert plan_a["source"]["plugin_material_sha256"] == accepted_plugin_material_sha256(
        accepted
    )

    rendered_a = render_accepted_plugins(project, revision_id, sample_rate_hz=8000)
    rendered_b = render_accepted_plugins(project, revision_id, sample_rate_hz=8000)
    baseline = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    assert rendered_a.plan == rendered_b.plan
    assert rendered_a.wav_bytes == rendered_b.wav_bytes
    assert rendered_a.wav_sha256 != baseline.wav_sha256


def test_plugin_state_bypass_and_remove_are_trusted_and_deterministic(
    tmp_path: Path,
) -> None:
    project, routed = _accept_routing(tmp_path)
    accepted = _accept(
        project,
        routed,
        _candidate(routed, "PLUG-R1-ADD", [_add_op(gain_db=-3.0, delay_frames=4)]),
    )

    state_candidate = _candidate(
        accepted,
        "PLUG-R1-STATE",
        [
            {
                "operation_id": "STATE-1",
                "op": "SET_STATE",
                "instance_id": "PI-001",
                "state": {"gain_db": -12.0, "delay_frames": 4},
            }
        ],
    )
    changed = _accept(project, accepted, state_candidate)
    render_before = render_accepted_plugins(
        project, accepted["project"]["revision_id"], sample_rate_hz=8000
    )
    render_changed = render_accepted_plugins(
        project, changed["project"]["revision_id"], sample_rate_hz=8000
    )
    assert (
        render_before.plan["plugin_processing_plan_sha256"]
        != render_changed.plan["plugin_processing_plan_sha256"]
    )
    assert render_before.wav_sha256 != render_changed.wav_sha256
    assert render_changed.peak_pre_clip < render_before.peak_pre_clip

    bypassed = _accept(
        project,
        changed,
        _candidate(
            changed,
            "PLUG-R1-BYPASS",
            [
                {
                    "operation_id": "BYPASS-1",
                    "op": "SET_BYPASS",
                    "instance_id": "PI-001",
                    "bypass": True,
                }
            ],
        ),
    )
    bypass_render = render_accepted_plugins(
        project, bypassed["project"]["revision_id"], sample_rate_hz=8000
    )
    bypass_baseline = render_routed_mix(
        project, bypassed["project"]["revision_id"], mix_sample_rate_hz=8000
    )
    assert bypass_render.plan["total_effective_latency_frames"] == 0
    assert bypass_render.wav_bytes == bypass_baseline.wav_bytes

    removed = _accept(
        project,
        bypassed,
        _candidate(
            bypassed,
            "PLUG-R1-REMOVE",
            [
                {
                    "operation_id": "REMOVE-1",
                    "op": "REMOVE_INSTANCE",
                    "instance_id": "PI-001",
                }
            ],
        ),
    )
    assert accepted_plugin_material_from_blueprint(removed) == empty_accepted_plugin_material()
    removed_render = render_accepted_plugins(
        project, removed["project"]["revision_id"], sample_rate_hz=8000
    )
    removed_baseline = render_routed_mix(
        project, removed["project"]["revision_id"], mix_sample_rate_hz=8000
    )
    assert removed_render.wav_bytes == removed_baseline.wav_bytes


def test_plugin_authority_fail_closed_matrix(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)

    wrong_owner = _candidate(
        routed,
        "PLUG-R1-WRONG-OWNER",
        [_add_op(owner_id="BUS-001")],
    )
    blocked_owner = build_plugin_edit_preview(project, routed, wrong_owner)
    assert not blocked_owner.ready
    assert "supports only exact master" in blocked_owner.authority_result["conflicts"][0]["reason"]

    first = _accept(
        project,
        routed,
        _candidate(routed, "PLUG-R1-FIRST", [_add_op()]),
    )

    missing = _candidate(
        first,
        "PLUG-R1-MISSING",
        [
            {
                "operation_id": "STATE-MISSING",
                "op": "SET_STATE",
                "instance_id": "PI-MISSING",
                "state": {"gain_db": -1.0, "delay_frames": 1},
            }
        ],
    )
    blocked_missing = build_plugin_edit_preview(project, first, missing)
    assert not blocked_missing.ready
    assert blocked_missing.authority_result["conflicts"][0]["code"] == "INVALID_TARGET"

    forged = copy.deepcopy(first)
    forged["project"]["title"] = str(forged["project"]["title"]) + " forged"
    forged_candidate = _candidate(
        forged,
        "PLUG-R1-FORGED",
        [
            {
                "operation_id": "BYPASS-FORGED",
                "op": "SET_BYPASS",
                "instance_id": "PI-001",
                "bypass": True,
            }
        ],
    )
    blocked_forged = build_plugin_edit_preview(project, forged, forged_candidate)
    assert not blocked_forged.ready
    assert blocked_forged.authority_result["conflicts"][0]["code"] == "STALE_SOURCE"
    assert "persisted source Blueprint hash mismatch" in blocked_forged.authority_result["conflicts"][0]["reason"]

    stale_candidate = _candidate(
        first,
        "PLUG-R1-STALE",
        [
            {
                "operation_id": "STATE-STALE",
                "op": "SET_STATE",
                "instance_id": "PI-001",
                "state": {"gain_db": -2.0, "delay_frames": 2},
            }
        ],
    )
    advance = _candidate(
        first,
        "PLUG-R1-ADVANCE",
        [
            {
                "operation_id": "BYPASS-ADVANCE",
                "op": "SET_BYPASS",
                "instance_id": "PI-001",
                "bypass": True,
            }
        ],
    )
    _accept(project, first, advance)
    stale = build_plugin_edit_preview(project, first, stale_candidate)
    assert not stale.ready
    assert stale.authority_result["conflicts"][0]["code"] == "STALE_SOURCE"


def test_forced_processor_error_does_not_change_accepted_plugin_state_or_head(
    tmp_path: Path,
) -> None:
    project, routed = _accept_routing(tmp_path)
    accepted = _accept(
        project,
        routed,
        _candidate(routed, "PLUG-R1-ERROR", [_add_op()]),
    )
    revision_id = accepted["project"]["revision_id"]
    head_before = project.head_revision_id("main")
    material_before = accepted_plugin_material_from_blueprint(accepted)
    with pytest.raises(ContractError, match="forced processor error"):
        render_accepted_plugins(
            project,
            revision_id,
            sample_rate_hz=8000,
            force_error_instance_ids={"PI-001"},
        )
    assert project.head_revision_id("main") == head_before
    assert accepted_plugin_material_from_blueprint(
        project.read_revision(revision_id)
    ) == material_before


def test_accepted_plugin_reopen_preserves_material_plan_and_output(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    accepted = _accept(
        project,
        routed,
        _candidate(
            routed,
            "PLUG-R1-REOPEN",
            [_add_op(gain_db=-4.5, delay_frames=7)],
        ),
    )
    revision_id = accepted["project"]["revision_id"]
    material_before = accepted_plugin_material_from_blueprint(accepted)
    plan_before = build_accepted_plugin_processing_plan(
        project, revision_id, sample_rate_hz=8000
    )
    render_before = render_accepted_plugins(
        project, revision_id, sample_rate_hz=8000
    )

    archive = project.export_to(tmp_path / "plug-r1.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    reopened_blueprint = reopened.read_revision(revision_id)
    assert accepted_plugin_material_from_blueprint(reopened_blueprint) == material_before
    assert build_accepted_plugin_processing_plan(
        reopened, revision_id, sample_rate_hz=8000
    ) == plan_before
    assert render_accepted_plugins(
        reopened, revision_id, sample_rate_hz=8000
    ).wav_bytes == render_before.wav_bytes
    assert reopened.verify_integrity()["status"] == "PASS"
