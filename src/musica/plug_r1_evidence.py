"""Generate deterministic PLUG-R1 accepted plugin authority evidence."""

from __future__ import annotations

import copy
import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from .audio_edit import audio_material_sha256, blueprint_sha256
from .automation_edit import automation_material_sha256
from .contracts import ContractError
from .evidence import canonical_json_bytes
from .plug_r0_evidence import _fixture, _material as _r0_material
from .plugin_edit import accept_plugin_edit_preview, build_plugin_edit_preview
from .plugin_reference import (
    accepted_plugin_material_from_blueprint,
    accepted_plugin_material_sha256,
    build_accepted_plugin_processing_plan,
    empty_accepted_plugin_material,
    render_accepted_plugins,
)
from .project import MusicaProject
from .routed_mixer import render_routed_mix
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256

ROOT = Path(__file__).resolve().parents[2]

CONTRACT_PATHS = [
    ROOT / "schemas" / "accepted-plugin-material-v0.schema.json",
    ROOT / "schemas" / "plugin-edit-candidate-v0.schema.json",
    ROOT / "schemas" / "plugin-authority-result-v0.schema.json",
    ROOT / "schemas" / "music-blueprint-v0.schema.json",
    ROOT / "src" / "musica" / "plugin_reference.py",
    ROOT / "src" / "musica" / "plugin_edit.py",
    ROOT / "src" / "musica" / "project.py",
    ROOT / "src" / "musica" / "contracts.py",
    ROOT / "src" / "musica" / "plug_r1_evidence.py",
    ROOT / "tests" / "test_plug_r1_accepted_plugin_authority.py",
    ROOT / ".github" / "workflows" / "plug-r1-accepted-plugin-authority-evidence.yml",
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
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(routing),
        "automation_material_sha256": automation_material_sha256(parent),
        "plugin_material_sha256": accepted_plugin_material_sha256(parent),
    }


def _candidate(
    parent: dict[str, Any],
    candidate_id: str,
    operations: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_plugin_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "plug-r1-evidence"},
        "reason": candidate_id,
        "operations": operations,
        "preview_only": True,
    }


def _add_op(*, gain_db: float = -6.0, delay_frames: int = 4) -> dict[str, Any]:
    proposal = _r0_material(gain_db=gain_db, delay_frames=delay_frames)
    return {
        "operation_id": "ADD-PI-001",
        "op": "ADD_INSTANCE",
        "descriptor": copy.deepcopy(proposal["descriptors"][0]),
        "instance": copy.deepcopy(proposal["instances"][0]),
    }


def generate_plug_r1_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-plug-r1-") as temp_value:
        temp = Path(temp_value)
        project, routed = _fixture(temp)
        routed_revision_id = str(routed["project"]["revision_id"])
        source_head = project.head_revision_id("main")
        baseline = render_routed_mix(
            project, routed_revision_id, mix_sample_rate_hz=8000
        )

        add_candidate = _candidate(
            routed, "PLUG-R1-ADD", [_add_op(gain_db=-6.0, delay_frames=4)]
        )
        add_preview = build_plugin_edit_preview(project, routed, add_candidate)
        if not add_preview.ready or add_preview.blueprint is None:
            raise RuntimeError("PLUG-R1 add Preview blocked")
        preview_head_unchanged = project.head_revision_id("main") == source_head
        generic_commit_blocked = _blocked(
            lambda: project.commit_revision(add_preview.blueprint)
        )
        add_record = accept_plugin_edit_preview(project, add_preview)
        accepted_a = project.read_revision(add_record["revision_id"])
        revision_a = str(accepted_a["project"]["revision_id"])
        same_preview_second_accept_blocked = _blocked(
            lambda: accept_plugin_edit_preview(project, add_preview)
        )

        material_a = accepted_plugin_material_from_blueprint(accepted_a)
        plan_a1 = build_accepted_plugin_processing_plan(
            project, revision_a, sample_rate_hz=8000
        )
        plan_a2 = build_accepted_plugin_processing_plan(
            project, revision_a, sample_rate_hz=8000
        )
        render_a1 = render_accepted_plugins(
            project, revision_a, sample_rate_hz=8000
        )
        render_a2 = render_accepted_plugins(
            project, revision_a, sample_rate_hz=8000
        )

        state_candidate = _candidate(
            accepted_a,
            "PLUG-R1-STATE",
            [
                {
                    "operation_id": "STATE-PI-001",
                    "op": "SET_STATE",
                    "instance_id": "PI-001",
                    "state": {"gain_db": -12.0, "delay_frames": 4},
                }
            ],
        )
        state_preview = build_plugin_edit_preview(project, accepted_a, state_candidate)
        if not state_preview.ready:
            raise RuntimeError("PLUG-R1 controlled state Preview blocked")

        stale_preview = build_plugin_edit_preview(
            project,
            accepted_a,
            _candidate(
                accepted_a,
                "PLUG-R1-STALE",
                [
                    {
                        "operation_id": "STALE-BYPASS",
                        "op": "SET_BYPASS",
                        "instance_id": "PI-001",
                        "bypass": True,
                    }
                ],
            ),
        )
        if not stale_preview.ready:
            raise RuntimeError("PLUG-R1 stale fixture Preview blocked")

        forged = copy.deepcopy(accepted_a)
        forged["project"]["title"] = str(forged["project"]["title"]) + " forged"
        forged_preview = build_plugin_edit_preview(
            project,
            forged,
            _candidate(
                forged,
                "PLUG-R1-FORGED",
                [
                    {
                        "operation_id": "FORGED-BYPASS",
                        "op": "SET_BYPASS",
                        "instance_id": "PI-001",
                        "bypass": True,
                    }
                ],
            ),
        )

        state_record = accept_plugin_edit_preview(project, state_preview)
        accepted_b = project.read_revision(state_record["revision_id"])
        revision_b = str(accepted_b["project"]["revision_id"])
        material_b = accepted_plugin_material_from_blueprint(accepted_b)
        plan_b = build_accepted_plugin_processing_plan(
            project, revision_b, sample_rate_hz=8000
        )
        render_b = render_accepted_plugins(
            project, revision_b, sample_rate_hz=8000
        )
        stale_after_head_advance_blocked = _blocked(
            lambda: accept_plugin_edit_preview(project, stale_preview)
        )

        head_before_error = project.head_revision_id("main")
        material_before_error = accepted_plugin_material_sha256(accepted_b)
        forced_processor_error_blocked = _blocked(
            lambda: render_accepted_plugins(
                project,
                revision_b,
                sample_rate_hz=8000,
                force_error_instance_ids={"PI-001"},
            )
        )
        forced_error_head_unchanged = project.head_revision_id("main") == head_before_error
        forced_error_material_unchanged = (
            accepted_plugin_material_sha256(project.read_revision(revision_b))
            == material_before_error
        )

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_blueprint = reopened.read_revision(revision_b)
        reopened_plan = build_accepted_plugin_processing_plan(
            reopened, revision_b, sample_rate_hz=8000
        )
        reopened_render = render_accepted_plugins(
            reopened, revision_b, sample_rate_hz=8000
        )

        bypass_preview = build_plugin_edit_preview(
            project,
            accepted_b,
            _candidate(
                accepted_b,
                "PLUG-R1-BYPASS",
                [
                    {
                        "operation_id": "BYPASS-PI-001",
                        "op": "SET_BYPASS",
                        "instance_id": "PI-001",
                        "bypass": True,
                    }
                ],
            ),
        )
        if not bypass_preview.ready:
            raise RuntimeError("PLUG-R1 bypass Preview blocked")
        bypass_record = accept_plugin_edit_preview(project, bypass_preview)
        accepted_bypass = project.read_revision(bypass_record["revision_id"])
        bypass_render = render_accepted_plugins(
            project,
            accepted_bypass["project"]["revision_id"],
            sample_rate_hz=8000,
        )
        bypass_baseline = render_routed_mix(
            project,
            accepted_bypass["project"]["revision_id"],
            mix_sample_rate_hz=8000,
        )

        remove_preview = build_plugin_edit_preview(
            project,
            accepted_bypass,
            _candidate(
                accepted_bypass,
                "PLUG-R1-REMOVE",
                [
                    {
                        "operation_id": "REMOVE-PI-001",
                        "op": "REMOVE_INSTANCE",
                        "instance_id": "PI-001",
                    }
                ],
            ),
        )
        if not remove_preview.ready:
            raise RuntimeError("PLUG-R1 remove Preview blocked")
        remove_record = accept_plugin_edit_preview(project, remove_preview)
        accepted_removed = project.read_revision(remove_record["revision_id"])
        removed_material = accepted_plugin_material_from_blueprint(accepted_removed)
        removed_render = render_accepted_plugins(
            project,
            accepted_removed["project"]["revision_id"],
            sample_rate_hz=8000,
        )
        removed_baseline = render_routed_mix(
            project,
            accepted_removed["project"]["revision_id"],
            mix_sample_rate_hz=8000,
        )

        missing_preview = build_plugin_edit_preview(
            project,
            accepted_removed,
            _candidate(
                accepted_removed,
                "PLUG-R1-MISSING",
                [
                    {
                        "operation_id": "MISSING-STATE",
                        "op": "SET_STATE",
                        "instance_id": "PI-MISSING",
                        "state": {"gain_db": -1.0, "delay_frames": 1},
                    }
                ],
            ),
        )

        _write_json(out / "accepted-plugin-a.json", material_a)
        _write_json(out / "accepted-plugin-b.json", material_b)
        _write_json(out / "accepted-plugin-bypass.json", accepted_plugin_material_from_blueprint(accepted_bypass))
        _write_json(out / "accepted-plugin-removed.json", removed_material)
        _write_json(out / "plugin-plan-a.json", plan_a1)
        _write_json(out / "plugin-plan-b.json", plan_b)
        _write_json(out / "plugin-plan-bypass.json", bypass_render.plan)
        _write_json(out / "plugin-plan-removed.json", removed_render.plan)
        (out / "baseline-routed.wav").write_bytes(baseline.wav_bytes)
        (out / "plugin-a.wav").write_bytes(render_a1.wav_bytes)
        (out / "plugin-b.wav").write_bytes(render_b.wav_bytes)
        (out / "plugin-bypass.wav").write_bytes(bypass_render.wav_bytes)
        (out / "plugin-removed.wav").write_bytes(removed_render.wav_bytes)

        proof = {
            "milestone": "PLUG-R1",
            "validation_class": "TRUSTED_ACCEPTED_PLUGIN_PREVIEW_ACCEPT_AND_DETERMINISTIC_OFFLINE_EXECUTION",
            "source_head_before_preview": source_head,
            "preview_ready": add_preview.ready,
            "preview_head_unchanged": preview_head_unchanged,
            "generic_commit_plugin_bypass_blocked": generic_commit_blocked,
            "accept_advanced_exactly_once": add_record["parent_revision_id"] == source_head,
            "same_preview_second_accept_blocked": same_preview_second_accept_blocked,
            "accepted_plugin_material_sha256_a": accepted_plugin_material_sha256(accepted_a),
            "accepted_plugin_material_sha256_b": accepted_plugin_material_sha256(accepted_b),
            "plan_repeat_exact": plan_a1 == plan_a2,
            "render_repeat_exact": render_a1.wav_bytes == render_a2.wav_bytes,
            "active_plugin_changes_routed_output": render_a1.wav_sha256 != baseline.wav_sha256,
            "controlled_state_change_changes_plan": (
                plan_a1["plugin_processing_plan_sha256"]
                != plan_b["plugin_processing_plan_sha256"]
            ),
            "controlled_state_change_changes_output": render_a1.wav_sha256 != render_b.wav_sha256,
            "controlled_state_change_reduces_peak": render_b.peak_pre_clip < render_a1.peak_pre_clip,
            "stale_preview_after_head_advance_blocked": stale_after_head_advance_blocked,
            "forged_same_revision_parent_blocked": (
                not forged_preview.ready
                and forged_preview.authority_result["conflicts"][0]["code"] == "STALE_SOURCE"
            ),
            "missing_instance_target_blocked": (
                not missing_preview.ready
                and missing_preview.authority_result["conflicts"][0]["code"] == "INVALID_TARGET"
            ),
            "forced_processor_error_blocked": forced_processor_error_blocked,
            "forced_processor_error_head_unchanged": forced_error_head_unchanged,
            "forced_processor_error_plugin_material_unchanged": forced_error_material_unchanged,
            "bypass_is_byte_exact_routed_baseline": bypass_render.wav_bytes == bypass_baseline.wav_bytes,
            "bypass_effective_latency_zero": bypass_render.plan["total_effective_latency_frames"] == 0,
            "remove_returns_empty_accepted_material": removed_material == empty_accepted_plugin_material(),
            "remove_output_is_byte_exact_routed_baseline": removed_render.wav_bytes == removed_baseline.wav_bytes,
            "reopen_plugin_material_exact": accepted_plugin_material_from_blueprint(reopened_blueprint) == material_b,
            "reopen_plan_exact": reopened_plan == plan_b,
            "reopen_wav_exact": reopened_render.wav_bytes == render_b.wav_bytes,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
            "plugin_runtime_is_canonical": False,
            "processed_audio_is_canonical": False,
            "real_plugin_binary_hosting_claimed": False,
            "arbitrary_graph_latency_compensation_claimed": False,
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
        "milestone": "PLUG-R1",
        "artifact_name": "musica-plug-r1-accepted-plugin-authority-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_PLUG_R1_EVIDENCE_OUT",
        "artifacts/plug-r1-accepted-plugin-authority-evidence",
    )
    generate_plug_r1_evidence(destination)
