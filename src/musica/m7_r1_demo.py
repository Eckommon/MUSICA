"""Generate canonical MUSICA M7-R1 bounded automation-runtime evidence."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

from .automation_contracts import empty_automation_material
from .automation_edit import (
    accept_automation_edit_preview,
    automation_material_sha256,
    blueprint_sha256,
    build_automation_edit_preview,
)
from .contracts import ContractError, clone_for_revision, validate_contract, validate_revision
from .evidence import artifact_record, canonical_json_bytes, write_canonical_json
from .project import create_project

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BLUEPRINT = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _material() -> dict[str, Any]:
    return {
        "material_version": "0",
        "mode": "explicit_automation",
        "time_base": {"unit": "quarter_note_beat", "origin_beat": 0.0},
        "lanes": [
            {
                "lane_id": "A-GAIN",
                "target": {
                    "parameter_id": "mix.gain",
                    "scope": "project",
                    "owner_id": None,
                    "unit": "decibel",
                    "minimum": -60.0,
                    "maximum": 6.0,
                },
                "section_id": None,
                "points": [
                    {"point_id": "AP-GAIN-001", "beat": 0.0, "value": -6.0, "interpolation": "linear"},
                    {"point_id": "AP-GAIN-002", "beat": 8.0, "value": -3.0, "interpolation": "hold"},
                ],
            }
        ],
    }


def _source(blueprint_path: str | Path) -> dict[str, Any]:
    blueprint = _load(blueprint_path)
    blueprint["materials"]["automation"] = _material()
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _candidate(parent: dict[str, Any], candidate_id: str, operations: list[dict[str, Any]]) -> dict[str, Any]:
    value = {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_automation_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
            "automation_material_sha256": automation_material_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "M7-R1-EVIDENCE"},
        "reason": "Canonical M7-R1 bounded automation runtime evidence.",
        "operations": operations,
        "preview_only": True,
    }
    validate_contract(value, "automation-edit-candidate-v0.schema.json")
    return value


def _exact_lock() -> dict[str, Any]:
    return {
        "lock_version": "0",
        "lock_id": "L-M7-R1-EVIDENCE-VALUE",
        "strength": "HARD",
        "selector": {
            "lane_id": "A-GAIN",
            "point_id": "AP-GAIN-001",
            "parameter_id": "mix.gain",
            "property": "value",
        },
        "mode": "exact",
        "inheriting": True,
        "value": -6.0,
        "reason": "Protect the accepted opening gain value.",
    }


def _presence_lock() -> dict[str, Any]:
    return {
        "lock_version": "0",
        "lock_id": "L-M7-R1-EVIDENCE-PRESENCE",
        "strength": "HARD",
        "selector": {
            "lane_id": "A-GAIN",
            "point_id": "AP-GAIN-001",
            "property": "point",
        },
        "mode": "presence",
        "inheriting": True,
        "reason": "Protect the accepted opening gain anchor.",
    }


def _locked(source: dict[str, Any], lock: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(source)
    value["materials"]["automation_locks"] = [copy.deepcopy(lock)]
    validate_contract(value, "music-blueprint-v0.schema.json")
    return value


def run_suite(out_dir: str | Path, *, blueprint_path: str | Path = DEFAULT_BLUEPRINT) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    legacy = _load(blueprint_path)
    validate_contract(legacy, "music-blueprint-v0.schema.json")
    legacy_before = canonical_json_bytes(legacy)
    legacy_empty_hash_a = automation_material_sha256(legacy)
    legacy_empty_hash_b = automation_material_sha256(copy.deepcopy(legacy))

    source = _source(blueprint_path)
    operations = [
        {
            "operation_id": "OP-M7-R1-MOVE",
            "op": "MOVE_POINT",
            "target": {"lane_id": "A-GAIN", "point_id": "AP-GAIN-001"},
            "beat": 1.0,
        },
        {
            "operation_id": "OP-M7-R1-VALUE",
            "op": "SET_VALUE",
            "target": {"lane_id": "A-GAIN", "point_id": "AP-GAIN-001"},
            "value": -5.0,
        },
        {
            "operation_id": "OP-M7-R1-INTERP",
            "op": "SET_INTERPOLATION",
            "target": {"lane_id": "A-GAIN", "point_id": "AP-GAIN-001"},
            "interpolation": "hold",
        },
        {
            "operation_id": "OP-M7-R1-DELETE",
            "op": "DELETE_POINT",
            "target": {"lane_id": "A-GAIN", "point_id": "AP-GAIN-002"},
        },
        {
            "operation_id": "OP-M7-R1-INSERT",
            "op": "INSERT_POINT",
            "target": {"lane_id": "A-GAIN"},
            "point": {
                "point_id": "AP-GAIN-003",
                "beat": 4.0,
                "value": -4.0,
                "interpolation": "linear",
            },
        },
    ]
    edit = _candidate(source, "AEC-M7-R1-EVIDENCE-001", operations)
    preview_a = build_automation_edit_preview(source, edit, revision_id="rev-m7-r1-evidence-001")
    preview_b = build_automation_edit_preview(
        copy.deepcopy(source), copy.deepcopy(edit), revision_id="rev-m7-r1-evidence-001"
    )
    if not preview_a.ready or preview_a.blueprint is None:
        raise RuntimeError("M7-R1 canonical positive preview did not become READY_FOR_PREVIEW")

    with tempfile.TemporaryDirectory(prefix="musica-m7-r1-") as temp_dir:
        project = create_project(Path(temp_dir) / "project.musica", source)
        source_revision_id = project.head_revision_id()
        ref_before_preview = project.head_revision_id()
        ref_after_preview = project.head_revision_id()
        record = accept_automation_edit_preview(project, preview_a)
        accepted_revision_id = project.head_revision_id()
        accepted = project.read_revision(accepted_revision_id)
        integrity = project.verify_integrity()

    stale = copy.deepcopy(edit)
    stale["candidate_id"] = "AEC-M7-R1-STALE"
    stale["source"]["automation_material_sha256"] = "0" * 64
    stale_result = build_automation_edit_preview(source, stale)

    exact_locked = _locked(source, _exact_lock())
    exact_edit = _candidate(
        exact_locked,
        "AEC-M7-R1-LOCK-EXACT",
        [
            {
                "operation_id": "OP-M7-R1-LOCK-EXACT",
                "op": "SET_VALUE",
                "target": {"lane_id": "A-GAIN", "point_id": "AP-GAIN-001"},
                "value": -5.0,
            }
        ],
    )
    exact_result = build_automation_edit_preview(exact_locked, exact_edit)

    presence_locked = _locked(source, _presence_lock())
    presence_edit = _candidate(
        presence_locked,
        "AEC-M7-R1-LOCK-PRESENCE",
        [
            {
                "operation_id": "OP-M7-R1-LOCK-PRESENCE",
                "op": "DELETE_POINT",
                "target": {"lane_id": "A-GAIN", "point_id": "AP-GAIN-001"},
            }
        ],
    )
    presence_result = build_automation_edit_preview(presence_locked, presence_edit)

    direct = clone_for_revision(exact_locked, "rev-m7-r1-direct-bypass")
    direct["materials"]["automation"]["lanes"][0]["points"][0]["value"] = -5.0
    direct_conflicts = validate_revision(exact_locked, direct)
    direct_blocked = any(
        item.rule_type == "automation_lock" and item.status == "BLOCKED"
        for item in direct_conflicts
    )
    with tempfile.TemporaryDirectory(prefix="musica-m7-r1-direct-") as temp_dir:
        direct_project = create_project(Path(temp_dir) / "locked.musica", exact_locked)
        direct_error = None
        try:
            direct_project.commit_revision(direct)
        except ContractError as exc:
            direct_error = str(exc)
        direct_ref_preserved = direct_project.head_revision_id() == exact_locked["project"]["revision_id"]

    legacy_out = write_canonical_json(root / "inputs" / "legacy-blueprint.json", legacy)
    empty_out = write_canonical_json(root / "inputs" / "legacy-empty-automation-material.json", empty_automation_material())
    source_out = write_canonical_json(root / "inputs" / "automation-source-blueprint.json", source)
    candidate_out = write_canonical_json(root / "contracts" / "automation-edit-candidate.json", edit)
    preview_out = write_canonical_json(root / "preview" / "preview-result.json", preview_a.as_dict())
    candidate_blueprint_out = write_canonical_json(root / "preview" / "candidate-blueprint.json", preview_a.blueprint)
    record_out = write_canonical_json(root / "accepted" / "revision-record.json", record)
    accepted_out = write_canonical_json(root / "accepted" / "blueprint.json", accepted)
    integrity_out = write_canonical_json(root / "accepted" / "project-integrity.json", integrity)
    stale_out = write_canonical_json(root / "negative" / "stale-source-result.json", stale_result.as_dict())
    exact_lock_out = write_canonical_json(root / "negative" / "hard-exact-lock-result.json", exact_result.as_dict())
    presence_lock_out = write_canonical_json(root / "negative" / "hard-presence-lock-result.json", presence_result.as_dict())
    direct_out = write_canonical_json(
        root / "negative" / "direct-m2-bypass.json",
        {
            "blocked": direct_blocked,
            "project_commit_error": direct_error,
            "project_ref_preserved": direct_ref_preserved,
            "conflicts": [item.as_dict() for item in direct_conflicts],
        },
    )

    proof = {
        "proof_version": "0",
        "legacy_blueprint_byte_unchanged": canonical_json_bytes(legacy) == legacy_before,
        "legacy_has_no_fabricated_automation": "automation" not in legacy["materials"],
        "legacy_empty_material_hash_deterministic": legacy_empty_hash_a == legacy_empty_hash_b,
        "source_blueprint_sha256": blueprint_sha256(source),
        "source_automation_material_sha256": automation_material_sha256(source),
        "positive_preview_ready": preview_a.ready,
        "positive_preview_has_no_project_authority": preview_a.authority_result["project_mutation_authorized"] is False,
        "positive_preview_has_no_music_ir_authority": preview_a.authority_result["music_ir_mutation_authorized"] is False,
        "positive_preview_deterministic": preview_a.as_dict() == preview_b.as_dict() and preview_a.blueprint == preview_b.blueprint,
        "all_five_operation_kinds_exercised": {item["op"] for item in operations}
        == {"INSERT_POINT", "DELETE_POINT", "MOVE_POINT", "SET_VALUE", "SET_INTERPOLATION"},
        "changed_lane_ids": preview_a.changed_lane_ids,
        "changed_point_ids": preview_a.changed_point_ids,
        "project_ref_unchanged_before_accept": ref_before_preview == source_revision_id == ref_after_preview,
        "explicit_accept_advanced_ref_once": accepted_revision_id == "rev-m7-r1-evidence-001"
        and record["parent_revision_id"] == source_revision_id,
        "accepted_revision_count": integrity["revision_count"],
        "accepted_project_integrity": integrity["status"],
        "accepted_matches_preview_blueprint": accepted == preview_a.blueprint,
        "stale_source_status": stale_result.authority_result["status"],
        "stale_source_code": stale_result.authority_result["conflicts"][0]["code"],
        "hard_exact_lock_status": exact_result.authority_result["status"],
        "hard_exact_lock_code": exact_result.authority_result["conflicts"][0]["code"],
        "hard_exact_lock_rule_id": exact_result.authority_result["conflicts"][0]["rule_id"],
        "hard_presence_lock_status": presence_result.authority_result["status"],
        "hard_presence_lock_code": presence_result.authority_result["conflicts"][0]["code"],
        "hard_presence_lock_rule_id": presence_result.authority_result["conflicts"][0]["rule_id"],
        "direct_m2_bypass_blocked": direct_blocked and direct_error is not None and direct_ref_preserved,
    }

    required = [
        proof["legacy_blueprint_byte_unchanged"],
        proof["legacy_has_no_fabricated_automation"],
        proof["legacy_empty_material_hash_deterministic"],
        proof["positive_preview_ready"],
        proof["positive_preview_has_no_project_authority"],
        proof["positive_preview_has_no_music_ir_authority"],
        proof["positive_preview_deterministic"],
        proof["all_five_operation_kinds_exercised"],
        proof["project_ref_unchanged_before_accept"],
        proof["explicit_accept_advanced_ref_once"],
        proof["accepted_revision_count"] == 2,
        proof["accepted_project_integrity"] == "PASS",
        proof["accepted_matches_preview_blueprint"],
        proof["stale_source_status"] == "BLOCKED",
        proof["stale_source_code"] == "STALE_SOURCE",
        proof["hard_exact_lock_status"] == "BLOCKED",
        proof["hard_exact_lock_code"] == "HARD_LOCK_VIOLATION",
        proof["hard_exact_lock_rule_id"] == "L-M7-R1-EVIDENCE-VALUE",
        proof["hard_presence_lock_status"] == "BLOCKED",
        proof["hard_presence_lock_code"] == "HARD_LOCK_VIOLATION",
        proof["hard_presence_lock_rule_id"] == "L-M7-R1-EVIDENCE-PRESENCE",
        proof["direct_m2_bypass_blocked"],
    ]
    if not all(required):
        raise RuntimeError("M7-R1 canonical evidence proof failed")

    proof_out = write_canonical_json(root / "proof.json", proof)
    tracked = [
        legacy_out,
        empty_out,
        source_out,
        candidate_out,
        preview_out,
        candidate_blueprint_out,
        record_out,
        accepted_out,
        integrity_out,
        stale_out,
        exact_lock_out,
        presence_lock_out,
        direct_out,
        proof_out,
    ]
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M7-R1-Bounded-Canonical-Automation-Runtime-v0",
        "proof": proof,
        "hash_bindings": {
            "source_blueprint_sha256": blueprint_sha256(source),
            "source_automation_material_sha256": automation_material_sha256(source),
            "candidate_blueprint_sha256": preview_a.candidate_blueprint_sha256,
            "candidate_automation_material_sha256": preview_a.candidate_automation_material_sha256,
            "accepted_blueprint_sha256": blueprint_sha256(accepted),
            "accepted_automation_material_sha256": automation_material_sha256(accepted),
        },
        "claim_boundary": [
            "backward-compatible optional canonical Blueprint automation storage",
            "deterministic legacy empty-material source binding",
            "five stable-ID automation point primitives",
            "source-bound fail-closed Preview authority",
            "HARD exact/presence automation lock enforcement",
            "direct M2 automation-lock bypass prevention",
            "explicit acceptance through existing M2 Project Engine",
            "not Browser automation-lane UI or real-browser automation E2E",
            "not automation lowering, audible rendering, plug-in mapping or hosting",
            "not DAW automation reconciliation, MIDI/OSC or arbitrary tempo-map authority",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(tracked, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M7-R1 bounded automation evidence")
    parser.add_argument("--out", required=True)
    parser.add_argument("--blueprint", default=str(DEFAULT_BLUEPRINT))
    args = parser.parse_args()
    manifest = run_suite(args.out, blueprint_path=args.blueprint)
    print(json.dumps(manifest["proof"], sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
