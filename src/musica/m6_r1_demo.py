"""Generate canonical MUSICA M6-R1 exact-note edit-engine evidence.

공식 MUSICA M6-R1 exact-note 편집 엔진 근거를 생성합니다.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from .compiler import PPQ, compile_blueprint
from .contracts import validate_contract
from .evidence import artifact_record, canonical_json_bytes, write_canonical_json
from .note_edit import (
    accept_note_edit_preview,
    blueprint_sha256,
    build_note_edit_preview,
)
from .project import create_project

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BLUEPRINT = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
DEFAULT_MATERIAL = ROOT / "examples" / "note-material" / "valid" / "dark-electronic-explicit-timeline-v0.json"


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _exact_blueprint(blueprint_path: str | Path, material_path: str | Path) -> dict[str, Any]:
    blueprint = _load(blueprint_path)
    blueprint["materials"]["melody"]["exact_timeline"] = _load(material_path)
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _candidate(parent: dict[str, Any], candidate_id: str, operations: list[dict[str, Any]]) -> dict[str, Any]:
    value = {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_exact_note_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "M6-R1-EVIDENCE"},
        "reason": "Canonical M6-R1 stable-ID exact-note edit evidence.",
        "operations": operations,
        "preview_only": True,
    }
    validate_contract(value, "note-edit-candidate-v0.schema.json")
    return value


def _note_events(ir: dict[str, Any]) -> list[dict[str, Any]]:
    track = next(item for item in ir["tracks"] if item["track_id"] == "T-MOTIF")
    return [copy.deepcopy(event) for event in track["events"] if event["type"] == "note"]


def _locked_blueprint(source: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(source)
    value["materials"]["melody"]["exact_note_locks"] = [
        {
            "lock_version": "0",
            "lock_id": "L-M6-R1-EVIDENCE-PITCH",
            "strength": "HARD",
            "selector": {
                "part_id": "P-SYNTH",
                "note_id": "N-MOTIF-001",
                "property": "pitch",
            },
            "mode": "exact",
            "inheriting": True,
            "value": 62,
            "reason": "Canonical M6-R1 negative proof locks the first motif pitch.",
        }
    ]
    validate_contract(value, "music-blueprint-v0.schema.json")
    return value


def run_suite(
    out_dir: str | Path,
    *,
    blueprint_path: str | Path = DEFAULT_BLUEPRINT,
    material_path: str | Path = DEFAULT_MATERIAL,
) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    legacy = _load(blueprint_path)
    validate_contract(legacy, "music-blueprint-v0.schema.json")
    legacy_ir_a = compile_blueprint(legacy)
    legacy_ir_b = compile_blueprint(copy.deepcopy(legacy))

    source = _exact_blueprint(blueprint_path, material_path)
    source_ir = compile_blueprint(source)
    source_notes = _note_events(source_ir)
    source_material_notes = source["materials"]["melody"]["exact_timeline"]["notes"]
    expected_source_notes = [
        {
            "type": "note",
            "tick": round(float(note["start_beat"]) * PPQ),
            "duration": round(float(note["duration_beats"]) * PPQ),
            "note": int(note["pitch"]),
            "velocity": int(note["velocity"]),
        }
        for note in source_material_notes
    ]

    operations = [
        {
            "operation_id": "OP-M6-R1-MOVE",
            "op": "MOVE",
            "target": {"part_id": "P-SYNTH", "note_id": "N-MOTIF-001"},
            "start_beat": 0.25,
        },
        {
            "operation_id": "OP-M6-R1-REPITCH",
            "op": "REPITCH",
            "target": {"part_id": "P-SYNTH", "note_id": "N-MOTIF-001"},
            "pitch": 64,
        },
        {
            "operation_id": "OP-M6-R1-VELOCITY",
            "op": "SET_VELOCITY",
            "target": {"part_id": "P-SYNTH", "note_id": "N-MOTIF-001"},
            "velocity": 90,
        },
        {
            "operation_id": "OP-M6-R1-DELETE",
            "op": "DELETE",
            "target": {"part_id": "P-SYNTH", "note_id": "N-MOTIF-002"},
        },
        {
            "operation_id": "OP-M6-R1-RESIZE",
            "op": "RESIZE",
            "target": {"part_id": "P-SYNTH", "note_id": "N-MOTIF-003"},
            "duration_beats": 1.25,
        },
        {
            "operation_id": "OP-M6-R1-INSERT",
            "op": "INSERT",
            "note": {
                "note_id": "N-MOTIF-004",
                "part_id": "P-SYNTH",
                "section_id": "S01",
                "start_beat": 4.0,
                "duration_beats": 0.5,
                "pitch": 67,
                "velocity": 74,
                "articulation": "normal",
                "identity_tags": ["m6-r1-evidence"],
            },
        },
    ]
    edit = _candidate(source, "NEC-M6-R1-EVIDENCE-001", operations)
    preview_a = build_note_edit_preview(source, edit, revision_id="rev-m6-r1-evidence-001")
    preview_b = build_note_edit_preview(
        copy.deepcopy(source), copy.deepcopy(edit), revision_id="rev-m6-r1-evidence-001"
    )
    if not preview_a.ready or preview_a.blueprint is None:
        raise RuntimeError("M6-R1 canonical positive preview did not become READY_FOR_PREVIEW")

    project_root = root / "project.musica"
    project = create_project(project_root, source)
    source_revision_id = project.head_revision_id()
    ref_before_preview = project.head_revision_id()
    candidate_ir_a = compile_blueprint(preview_a.blueprint)
    candidate_ir_b = compile_blueprint(copy.deepcopy(preview_a.blueprint))
    ref_after_preview = project.head_revision_id()
    record = accept_note_edit_preview(project, preview_a)
    accepted_revision_id = project.head_revision_id()
    accepted = project.read_revision(accepted_revision_id)
    accepted_ir_a = compile_blueprint(accepted)
    accepted_ir_b = compile_blueprint(copy.deepcopy(accepted))
    integrity = project.verify_integrity()
    project_archive = project.export_to(root / "accepted-project.musica.zip")

    stale = copy.deepcopy(edit)
    stale["candidate_id"] = "NEC-M6-R1-STALE"
    stale["source"]["blueprint_sha256"] = "0" * 64
    stale_result = build_note_edit_preview(source, stale)

    locked = _locked_blueprint(source)
    locked_edit = _candidate(
        locked,
        "NEC-M6-R1-LOCKED",
        [
            {
                "operation_id": "OP-M6-R1-LOCKED-REPITCH",
                "op": "REPITCH",
                "target": {"part_id": "P-SYNTH", "note_id": "N-MOTIF-001"},
                "pitch": 66,
            }
        ],
    )
    locked_result = build_note_edit_preview(locked, locked_edit)

    legacy_out = write_canonical_json(root / "inputs" / "legacy-blueprint.json", legacy)
    legacy_ir_out = write_canonical_json(root / "inputs" / "legacy-music-ir.json", legacy_ir_a)
    source_out = write_canonical_json(root / "inputs" / "exact-source-blueprint.json", source)
    source_ir_out = write_canonical_json(root / "inputs" / "exact-source-music-ir.json", source_ir)
    candidate_out = write_canonical_json(root / "contracts" / "note-edit-candidate.json", edit)
    preview_out = write_canonical_json(root / "preview" / "preview-result.json", preview_a.as_dict())
    candidate_blueprint_out = write_canonical_json(
        root / "preview" / "candidate-blueprint.json", preview_a.blueprint
    )
    candidate_ir_out = write_canonical_json(root / "preview" / "candidate-music-ir.json", candidate_ir_a)
    record_out = write_canonical_json(root / "accepted" / "revision-record.json", record)
    accepted_out = write_canonical_json(root / "accepted" / "blueprint.json", accepted)
    accepted_ir_out = write_canonical_json(root / "accepted" / "music-ir.json", accepted_ir_a)
    integrity_out = write_canonical_json(root / "accepted" / "project-integrity.json", integrity)
    stale_out = write_canonical_json(root / "negative" / "stale-source-result.json", stale_result.as_dict())
    lock_out = write_canonical_json(root / "negative" / "hard-lock-result.json", locked_result.as_dict())

    changed = set(preview_a.changed_note_ids)
    proof = {
        "proof_version": "0",
        "legacy_motif_path_deterministic": canonical_json_bytes(legacy_ir_a) == canonical_json_bytes(legacy_ir_b),
        "legacy_motif_path_preserved": "exact_timeline" not in legacy["materials"]["melody"],
        "exact_source_blueprint_sha256": blueprint_sha256(source),
        "exact_source_notes_lower_faithfully": source_notes == expected_source_notes,
        "positive_preview_ready": preview_a.ready,
        "positive_preview_has_no_project_authority": preview_a.authority_result["project_mutation_authorized"] is False,
        "positive_preview_has_no_music_ir_authority": preview_a.authority_result["music_ir_mutation_authorized"] is False,
        "positive_preview_deterministic": preview_a.as_dict() == preview_b.as_dict() and preview_a.blueprint == preview_b.blueprint,
        "all_six_operation_kinds_exercised": {item["op"] for item in operations}
        == {"INSERT", "DELETE", "MOVE", "RESIZE", "REPITCH", "SET_VELOCITY"},
        "stable_ids_changed": sorted(changed),
        "expected_stable_ids_changed": changed == {"N-MOTIF-001", "N-MOTIF-002", "N-MOTIF-003", "N-MOTIF-004"},
        "project_ref_unchanged_before_accept": ref_before_preview == source_revision_id == ref_after_preview,
        "explicit_accept_advanced_ref_once": accepted_revision_id == "rev-m6-r1-evidence-001"
        and record["parent_revision_id"] == source_revision_id,
        "accepted_revision_count": integrity["revision_count"],
        "accepted_project_integrity": integrity["status"],
        "candidate_compile_deterministic": canonical_json_bytes(candidate_ir_a) == canonical_json_bytes(candidate_ir_b),
        "accepted_compile_deterministic": canonical_json_bytes(accepted_ir_a) == canonical_json_bytes(accepted_ir_b),
        "accepted_matches_preview_blueprint": accepted == preview_a.blueprint,
        "stale_source_status": stale_result.authority_result["status"],
        "stale_source_code": stale_result.authority_result["conflicts"][0]["code"],
        "stale_source_has_no_preview": stale_result.blueprint is None,
        "hard_lock_status": locked_result.authority_result["status"],
        "hard_lock_code": locked_result.authority_result["conflicts"][0]["code"],
        "hard_lock_rule_id": locked_result.authority_result["conflicts"][0]["rule_id"],
        "hard_lock_has_no_preview": locked_result.blueprint is None,
    }

    required = [
        proof["legacy_motif_path_deterministic"],
        proof["legacy_motif_path_preserved"],
        proof["exact_source_notes_lower_faithfully"],
        proof["positive_preview_ready"],
        proof["positive_preview_has_no_project_authority"],
        proof["positive_preview_has_no_music_ir_authority"],
        proof["positive_preview_deterministic"],
        proof["all_six_operation_kinds_exercised"],
        proof["expected_stable_ids_changed"],
        proof["project_ref_unchanged_before_accept"],
        proof["explicit_accept_advanced_ref_once"],
        proof["accepted_revision_count"] == 2,
        proof["accepted_project_integrity"] == "PASS",
        proof["candidate_compile_deterministic"],
        proof["accepted_compile_deterministic"],
        proof["accepted_matches_preview_blueprint"],
        proof["stale_source_status"] == "BLOCKED",
        proof["stale_source_code"] == "STALE_SOURCE",
        proof["stale_source_has_no_preview"],
        proof["hard_lock_status"] == "BLOCKED",
        proof["hard_lock_code"] == "HARD_LOCK_VIOLATION",
        proof["hard_lock_rule_id"] == "L-M6-R1-EVIDENCE-PITCH",
        proof["hard_lock_has_no_preview"],
    ]
    if not all(required):
        raise RuntimeError("M6-R1 canonical evidence proof failed")

    proof_out = write_canonical_json(root / "proof.json", proof)
    tracked = [
        legacy_out,
        legacy_ir_out,
        source_out,
        source_ir_out,
        candidate_out,
        preview_out,
        candidate_blueprint_out,
        candidate_ir_out,
        record_out,
        accepted_out,
        accepted_ir_out,
        integrity_out,
        stale_out,
        lock_out,
        proof_out,
        project_archive,
    ]
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M6-R1-Typed-Exact-Note-Material-Edit-Engine-v0",
        "proof": proof,
        "hash_bindings": {
            "source_blueprint_sha256": blueprint_sha256(source),
            "candidate_blueprint_sha256": preview_a.candidate_blueprint_sha256,
            "accepted_blueprint_sha256": blueprint_sha256(accepted),
        },
        "claim_boundary": [
            "typed exact-note Blueprint material validation",
            "stable-ID exact-note primitive edit engine",
            "source-bound fail-closed Preview authority",
            "stable-ID HARD exact-note lock enforcement",
            "faithful deterministic exact-note lowering",
            "explicit acceptance through existing M2 Project Engine",
            "not a piano-roll/browser exact-note editor",
            "not arbitrary DAW reverse mapping",
            "not live MIDI editing or recording",
            "not perceptual or professional audio-quality validation",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(tracked, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M6-R1 exact-note edit evidence")
    parser.add_argument("--out", required=True)
    parser.add_argument("--blueprint", default=str(DEFAULT_BLUEPRINT))
    parser.add_argument("--material", default=str(DEFAULT_MATERIAL))
    args = parser.parse_args()
    manifest = run_suite(args.out, blueprint_path=args.blueprint, material_path=args.material)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
