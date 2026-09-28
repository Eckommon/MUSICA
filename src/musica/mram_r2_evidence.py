"""Generate deterministic MRAM-R2 native mixer automation evidence."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from .automation_contracts import automation_material_from_blueprint
from .automation_edit import (
    accept_automation_edit_preview,
    automation_material_sha256,
    blueprint_sha256,
    build_automation_edit_preview,
)
from .automation_lowering import lower_automation_execution
from .audio_assets import import_audio_asset
from .audio_edit import accept_audio_edit_preview, audio_material_sha256, build_audio_edit_preview
from .contracts import ContractError
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .mram_r1_evidence import _audio_candidate, _routing_candidate, _routing_ops, _wav_bytes
from .native_mixer_automation import build_native_mixer_automation_plan
from .project import MusicaProject, create_project
from .routed_mixer import render_routed_mix
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256
from .routing_edit import accept_routing_edit_preview, build_routing_edit_preview

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "automation-material-v0.schema.json",
    ROOT / "schemas" / "automation-edit-candidate-v0.schema.json",
    ROOT / "schemas" / "automation-execution-v0.schema.json",
    ROOT / "schemas" / "native-mixer-automation-plan-v0.schema.json",
    ROOT / "schemas" / "routed-mix-plan-v0.schema.json",
    ROOT / "src" / "musica" / "automation_contracts.py",
    ROOT / "src" / "musica" / "automation_edit.py",
    ROOT / "src" / "musica" / "automation_lowering.py",
    ROOT / "src" / "musica" / "native_mixer_automation.py",
    ROOT / "src" / "musica" / "project.py",
    ROOT / "src" / "musica" / "routed_mixer.py",
    ROOT / "src" / "musica" / "mram_r2_evidence.py",
    ROOT / "tests" / "test_mram_r2_native_mixer_automation.py",
    ROOT / ".github" / "workflows" / "mram-r2-native-mixer-automation-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _blocked(fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except ContractError:
        return True
    return False


def _source(parent: dict[str, Any]) -> dict[str, Any]:
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
) -> dict[str, Any]:
    if parameter_id == "mixer.gain_db":
        unit, minimum, maximum = "decibel", -60.0, 12.0
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


def _candidate(
    parent: dict[str, Any],
    candidate_id: str,
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_automation_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "mram-r2-evidence"},
        "reason": candidate_id,
        "operations": operations,
        "preview_only": True,
    }


def _add_lane_ops(lanes: list[dict[str, Any]], prefix: str) -> list[dict[str, Any]]:
    return [
        {
            "operation_id": f"{prefix}-{index:02d}",
            "op": "ADD_LANE",
            "lane": lane,
        }
        for index, lane in enumerate(lanes, start=1)
    ]


def generate_mram_r2_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-mram-r2-") as temp_value:
        temp = Path(temp_value)
        root = compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))
        project = create_project(temp / "source.musica", root)

        wav_a = temp / "a.wav"
        wav_b = temp / "b.wav"
        wav_a.write_bytes(_wav_bytes(16384))
        wav_b.write_bytes(_wav_bytes(8192))
        asset_a = import_audio_asset(project, wav_a)
        asset_b = import_audio_asset(project, wav_b)

        audio_preview = build_audio_edit_preview(
            project,
            root,
            _audio_candidate(
                root,
                "MRAM-R2-AUDIO",
                [
                    {"operation_id": "A-T1", "op": "ADD_TRACK", "track_id": "AT-001", "order": 0, "name": "Primary"},
                    {"operation_id": "A-T2", "op": "ADD_TRACK", "track_id": "AT-002", "order": 1, "name": "Secondary"},
                    {
                        "operation_id": "A-C1",
                        "op": "ADD_CLIP",
                        "target": {"track_id": "AT-001"},
                        "clip": {
                            "clip_id": "AC-001",
                            "asset_id": asset_a["asset_id"],
                            "timeline_start_seconds": 0.0,
                            "source_in_seconds": 0.0,
                            "source_out_seconds": 0.1,
                            "gain_db": 0.0,
                        },
                    },
                    {
                        "operation_id": "A-C2",
                        "op": "ADD_CLIP",
                        "target": {"track_id": "AT-002"},
                        "clip": {
                            "clip_id": "AC-002",
                            "asset_id": asset_b["asset_id"],
                            "timeline_start_seconds": 0.0,
                            "source_in_seconds": 0.0,
                            "source_out_seconds": 0.1,
                            "gain_db": 0.0,
                        },
                    },
                ],
            ),
        )
        if not audio_preview.ready:
            raise RuntimeError("MRAM-R2 evidence audio fixture Preview was blocked")
        audio_record = accept_audio_edit_preview(project, audio_preview)
        accepted_audio = project.read_revision(audio_record["revision_id"])

        audio_only_lane = _lane(
            "AUTO-AUDIO-ONLY",
            scope="audio_track",
            owner_id="AT-001",
            parameter_id="mixer.gain_db",
            points=[("PAO1", 0.0, -3.0, "hold")],
        )
        audio_only_native_preview = build_automation_edit_preview(
            accepted_audio,
            _candidate(
                accepted_audio,
                "MRAM-R2-AUDIO-ONLY",
                _add_lane_ops([audio_only_lane], "AO"),
            ),
            project=project,
        )

        routing_preview = build_routing_edit_preview(
            project,
            accepted_audio,
            _routing_candidate(accepted_audio, "MRAM-R2-ROUTING", _routing_ops()),
        )
        if not routing_preview.ready:
            raise RuntimeError("MRAM-R2 evidence routing fixture Preview was blocked")
        routing_record = accept_routing_edit_preview(project, routing_preview)
        routed = project.read_revision(routing_record["revision_id"])

        forged = copy.deepcopy(routed)
        forged["project"]["title"] = str(forged["project"]["title"]) + " forged"
        forged_lane = _lane(
            "AUTO-FORGED",
            scope="audio_track",
            owner_id="AT-001",
            parameter_id="mixer.pan",
            points=[("PF1", 0.0, 0.25, "hold")],
        )
        forged_source_preview = build_automation_edit_preview(
            forged,
            _candidate(
                forged,
                "MRAM-R2-FORGED-SOURCE",
                _add_lane_ops([forged_lane], "F"),
            ),
            project=project,
        )

        baseline = render_routed_mix(
            project, routed["project"]["revision_id"], mix_sample_rate_hz=8000
        )

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
        source_head = project.head_revision_id("main")
        native_preview = build_automation_edit_preview(
            routed,
            _candidate(routed, "MRAM-R2-NATIVE", _add_lane_ops(lanes, "N-ADD")),
            project=project,
        )
        if not native_preview.ready or native_preview.blueprint is None:
            raise RuntimeError("MRAM-R2 native automation Preview was blocked")
        preview_head_unchanged = project.head_revision_id("main") == source_head
        generic_commit_blocked = _blocked(
            lambda: project.commit_revision(native_preview.blueprint)
        )
        native_record = accept_automation_edit_preview(project, native_preview)
        native_revision_id = str(native_record["revision_id"])
        accepted = project.read_revision(native_revision_id)
        stale_reaccept_blocked = _blocked(
            lambda: accept_automation_edit_preview(project, native_preview)
        )

        lowering_a = build_native_mixer_automation_plan(
            project, native_revision_id, mix_sample_rate_hz=8000
        )
        lowering_b = build_native_mixer_automation_plan(
            project, native_revision_id, mix_sample_rate_hz=8000
        )
        generic_lowering = lower_automation_execution(accepted)
        render_a = render_routed_mix(
            project, native_revision_id, mix_sample_rate_hz=8000
        )
        render_b = render_routed_mix(
            project, native_revision_id, mix_sample_rate_hz=8000
        )

        stale_preview = build_automation_edit_preview(
            accepted,
            _candidate(
                accepted,
                "MRAM-R2-STALE",
                [
                    {
                        "operation_id": "STALE-VALUE",
                        "op": "SET_VALUE",
                        "target": {"lane_id": "AUTO-BUS001-PAN", "point_id": "P7"},
                        "value": -0.25,
                    }
                ],
            ),
            project=project,
        )
        if not stale_preview.ready:
            raise RuntimeError("MRAM-R2 stale-source fixture Preview was blocked")

        changed_preview = build_automation_edit_preview(
            accepted,
            _candidate(
                accepted,
                "MRAM-R2-CONTROLLED",
                [
                    {
                        "operation_id": "CONTROLLED-VALUE",
                        "op": "SET_VALUE",
                        "target": {"lane_id": "AUTO-AT001-GAIN", "point_id": "P1"},
                        "value": -12.0,
                    }
                ],
            ),
            project=project,
        )
        if not changed_preview.ready:
            raise RuntimeError("MRAM-R2 controlled edit Preview was blocked")
        changed_record = accept_automation_edit_preview(project, changed_preview)
        changed_revision_id = str(changed_record["revision_id"])
        changed = project.read_revision(changed_revision_id)
        changed_lowering = build_native_mixer_automation_plan(
            project, changed_revision_id, mix_sample_rate_hz=8000
        )
        changed_render = render_routed_mix(
            project, changed_revision_id, mix_sample_rate_hz=8000
        )
        stale_after_head_advance_blocked = _blocked(
            lambda: accept_automation_edit_preview(project, stale_preview)
        )

        missing_lane = _lane(
            "AUTO-MISSING",
            scope="audio_track",
            owner_id="AT-MISSING",
            parameter_id="mixer.gain_db",
            points=[("PM1", 0.0, 0.0, "hold")],
        )
        missing_preview = build_automation_edit_preview(
            changed,
            _candidate(changed, "MRAM-R2-MISSING", _add_lane_ops([missing_lane], "M")),
            project=project,
        )

        wrong_unit_lane = _lane(
            "AUTO-WRONG-UNIT",
            scope="routing_node",
            owner_id="MASTER-001",
            parameter_id="mixer.pan",
            points=[("PU1", 0.0, 0.0, "hold")],
        )
        wrong_unit_lane["target"]["unit"] = "decibel"
        wrong_unit_preview = build_automation_edit_preview(
            changed,
            _candidate(changed, "MRAM-R2-WRONG-UNIT", _add_lane_ops([wrong_unit_lane], "U")),
            project=project,
        )

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_blueprint = reopened.read_revision(changed_revision_id)
        reopened_lowering = build_native_mixer_automation_plan(
            reopened, changed_revision_id, mix_sample_rate_hz=8000
        )
        reopened_render = render_routed_mix(
            reopened, changed_revision_id, mix_sample_rate_hz=8000
        )

        accepted_material = automation_material_from_blueprint(accepted)
        changed_material = automation_material_from_blueprint(changed)
        assert accepted_material is not None and changed_material is not None

        _write_json(out / "accepted-automation.json", accepted_material)
        _write_json(out / "native-automation-plan.json", lowering_a)
        _write_json(out / "generic-automation-execution.json", generic_lowering)
        _write_json(out / "routed-plan.json", render_a.plan)
        (out / "routed-mix.wav").write_bytes(render_a.wav_bytes)
        _write_json(out / "changed-automation.json", changed_material)
        _write_json(out / "changed-native-automation-plan.json", changed_lowering)
        _write_json(out / "changed-routed-plan.json", changed_render.plan)
        (out / "changed-routed-mix.wav").write_bytes(changed_render.wav_bytes)

        identities = sorted(
            [
                [
                    str(lane["target_kind"]),
                    str(lane["target_id"]),
                    str(lane["parameter_id"]),
                ]
                for lane in lowering_a["lanes"]
            ]
        )
        proof = {
            "milestone": "MRAM-R2",
            "validation_class": "TRUSTED_NATIVE_MIXER_AUTOMATION_AND_DETERMINISTIC_ROUTED_EXECUTION",
            "source_head_before_preview": source_head,
            "native_preview_ready": native_preview.ready,
            "native_preview_head_unchanged": preview_head_unchanged,
            "audio_only_native_automation_blocked_without_routing": not audio_only_native_preview.ready,
            "forged_same_revision_parent_blocked_by_persisted_source_binding": not forged_source_preview.ready
            and forged_source_preview.authority_result["conflicts"][0]["code"] == "STALE_SOURCE",
            "generic_commit_native_automation_bypass_blocked": generic_commit_blocked,
            "native_accept_advanced_exactly_once": native_record["parent_revision_id"] == source_head,
            "same_preview_second_accept_blocked": stale_reaccept_blocked,
            "stable_target_identities": identities,
            "all_four_required_target_identities_present": identities
            == [
                ["audio_track", "AT-001", "mixer.gain_db"],
                ["audio_track", "AT-001", "mixer.pan"],
                ["routing_node", "BUS-001", "mixer.gain_db"],
                ["routing_node", "BUS-001", "mixer.pan"],
            ],
            "native_lowering_repeat_exact": lowering_a == lowering_b,
            "routed_plan_repeat_exact": render_a.plan == render_b.plan,
            "routed_wav_repeat_exact": render_a.wav_bytes == render_b.wav_bytes,
            "automation_changes_routed_plan": baseline.plan["routed_mix_plan_sha256"]
            != render_a.plan["routed_mix_plan_sha256"],
            "automation_changes_routed_wav": baseline.wav_sha256 != render_a.wav_sha256,
            "controlled_point_change_changes_native_plan": (
                changed_lowering["native_mixer_automation_plan_sha256"]
                != lowering_a["native_mixer_automation_plan_sha256"]
            ),
            "controlled_point_change_changes_routed_plan": (
                changed_render.plan["routed_mix_plan_sha256"]
                != render_a.plan["routed_mix_plan_sha256"]
            ),
            "controlled_point_change_changes_routed_wav": changed_render.wav_sha256
            != render_a.wav_sha256,
            "generic_lowering_keeps_backend_unmapped": all(
                lane["backend_mapping"] == {"status": "UNMAPPED"}
                for lane in generic_lowering["lanes"]
            ),
            "stale_preview_after_head_advance_blocked": stale_after_head_advance_blocked,
            "missing_target_candidate_blocked": not missing_preview.ready,
            "wrong_unit_candidate_blocked": not wrong_unit_preview.ready,
            "reopen_automation_exact": automation_material_from_blueprint(reopened_blueprint)
            == changed_material,
            "reopen_native_plan_exact": reopened_lowering == changed_lowering,
            "reopen_routed_plan_exact": reopened_render.plan == changed_render.plan,
            "reopen_routed_wav_exact": reopened_render.wav_bytes == changed_render.wav_bytes,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
            "rendered_audio_is_canonical": False,
            "native_automation_plan_is_canonical": False,
            "generic_automation_backend_mapping_authoritative": False,
            "send_automation_claimed": False,
            "mute_solo_automation_claimed": False,
            "browser_native_automation_editing_claimed": False,
            "realtime_audio_claimed": False,
            "plugin_hosting_claimed": False,
        }
        _write_json(out / "proof.json", proof)

    contract_hashes = []
    for path in CONTRACT_PATHS:
        data = path.read_bytes()
        contract_hashes.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": _sha(data),
                "size_bytes": len(data),
            }
        )
    _write_json(out / "contract-hashes.json", contract_hashes)

    records = []
    for path in sorted(
        p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json"
    ):
        data = path.read_bytes()
        records.append(
            {
                "path": path.relative_to(out).as_posix(),
                "sha256": _sha(data),
                "size_bytes": len(data),
            }
        )
    manifest = {
        "manifest_version": "0",
        "milestone": "MRAM-R2",
        "artifact_name": "musica-mram-r2-native-mixer-automation-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_MRAM_R2_EVIDENCE_OUT",
        "artifacts/mram-r2-native-mixer-automation-evidence",
    )
    generate_mram_r2_evidence(destination)
