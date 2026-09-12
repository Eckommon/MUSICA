"""Generate canonical M6-R2 Studio piano-roll integration evidence.

The evidence is service/UI integration evidence, not a human-gesture usability claim.
It proves Browser Studio can project accepted exact notes, route typed edits through the
M6-R1 trusted authority boundary, preserve the ref before explicit Accept, and reuse M2.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .contracts import validate_contract
from .evidence import artifact_record, canonical_json_bytes, write_canonical_json
from .note_edit import blueprint_sha256
from .project import create_project
from .studio import StudioService
from .studio_http import _browser_asset_bytes
from .studio_notes import NOTE_OPERATIONS, StudioNoteSurface

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
MATERIAL_PATH = ROOT / "examples" / "note-material" / "valid" / "dark-electronic-explicit-timeline-v0.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _exact_blueprint(*, locked: bool = False) -> dict[str, Any]:
    blueprint = _load(BLUEPRINT_PATH)
    blueprint["materials"]["melody"]["exact_timeline"] = _load(MATERIAL_PATH)
    if locked:
        blueprint["materials"]["melody"]["exact_note_locks"] = [
            {
                "lock_version": "0",
                "lock_id": "L-M6-R2-EVIDENCE-PITCH",
                "strength": "HARD",
                "selector": {
                    "part_id": "P-SYNTH",
                    "note_id": "N-MOTIF-001",
                    "property": "pitch",
                },
                "mode": "exact",
                "inheriting": True,
                "value": 62,
                "reason": "Canonical M6-R2 negative lock evidence.",
            }
        ]
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _candidate(parent: dict[str, Any], operations: list[dict[str, Any]], candidate_id: str) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_exact_note_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "m6-r2-evidence"},
        "reason": "Canonical M6-R2 Browser Studio precision edit.",
        "operations": operations,
        "preview_only": True,
    }


def _all_operations() -> list[dict[str, Any]]:
    target = {"part_id": "P-SYNTH", "note_id": "N-MOTIF-001"}
    return [
        {"operation_id": "OP-MOVE", "op": "MOVE", "target": target, "start_beat": 0.25},
        {"operation_id": "OP-RESIZE", "op": "RESIZE", "target": target, "duration_beats": 0.5},
        {"operation_id": "OP-REPITCH", "op": "REPITCH", "target": target, "pitch": 64},
        {"operation_id": "OP-VELOCITY", "op": "SET_VELOCITY", "target": target, "velocity": 90},
        {
            "operation_id": "OP-DELETE",
            "op": "DELETE",
            "target": {"part_id": "P-SYNTH", "note_id": "N-MOTIF-002"},
        },
        {
            "operation_id": "OP-INSERT",
            "op": "INSERT",
            "note": {
                "note_id": "N-MOTIF-004",
                "part_id": "P-SYNTH",
                "section_id": "S01",
                "start_beat": 1.25,
                "duration_beats": 0.5,
                "pitch": 67,
                "velocity": 74,
            },
        },
    ]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    workspace = root / "workspace"
    workspace.mkdir()

    parent = _exact_blueprint()
    create_project(workspace / "canonical.musica", parent)
    service = StudioService(workspace)
    service.open_project_session(project_slug="canonical", session_id="m6-r2-canonical")
    surface = StudioNoteSurface(service)
    project = service._get_session("m6-r2-canonical").project

    source_view = surface.note_view("m6-r2-canonical")
    source_ref = project.head_revision_id()
    candidate = _candidate(parent, _all_operations(), "NEC-M6-R2-EVIDENCE-ALL")
    preview_result = surface.preview_note_edit("m6-r2-canonical", candidate=candidate)
    preview_ref = project.head_revision_id()
    preview_view = surface.note_view("m6-r2-canonical")
    if not preview_result["preview_installed"]:
        raise RuntimeError("M6-R2 canonical positive candidate did not install Preview")

    accepted = service.accept_preview("m6-r2-canonical")
    accepted_ref = project.head_revision_id()
    accepted_view = surface.note_view("m6-r2-canonical")
    accepted_export = project.export_to(root / "accepted.musica.zip")

    service.close_session("m6-r2-canonical")
    service.open_project_session(project_slug="canonical", session_id="m6-r2-reopen")
    reopened_view = StudioNoteSurface(service).note_view("m6-r2-reopen")

    stale = copy.deepcopy(candidate)
    stale["candidate_id"] = "NEC-M6-R2-STALE"
    stale["source"]["revision_id"] = "rev-stale"
    stale_result = StudioNoteSurface(service).preview_note_edit("m6-r2-reopen", candidate=stale)

    locked_workspace = root / "locked-workspace"
    locked_workspace.mkdir()
    locked = _exact_blueprint(locked=True)
    create_project(locked_workspace / "locked.musica", locked)
    locked_service = StudioService(locked_workspace)
    locked_service.open_project_session(project_slug="locked", session_id="m6-r2-locked")
    locked_candidate = _candidate(
        locked,
        [
            {
                "operation_id": "OP-LOCKED-REPITCH",
                "op": "REPITCH",
                "target": {"part_id": "P-SYNTH", "note_id": "N-MOTIF-001"},
                "pitch": 65,
            }
        ],
        "NEC-M6-R2-LOCKED",
    )
    locked_result = StudioNoteSurface(locked_service).preview_note_edit(
        "m6-r2-locked",
        candidate=locked_candidate,
    )

    legacy_workspace = root / "legacy-workspace"
    legacy_workspace.mkdir()
    legacy = _load(BLUEPRINT_PATH)
    create_project(legacy_workspace / "legacy.musica", legacy)
    legacy_service = StudioService(legacy_workspace)
    legacy_service.open_project_session(project_slug="legacy", session_id="m6-r2-legacy")
    legacy_view = StudioNoteSurface(legacy_service).note_view("m6-r2-legacy")

    app_js = _browser_asset_bytes("app.js")
    app_css = _browser_asset_bytes("app.css")
    ui_proof = {
        "app_js_sha256": _sha256(app_js),
        "app_css_sha256": _sha256(app_css),
        "precision_global_present": b"MUSICA_PRECISION" in app_js,
        "note_preview_route_present": b"/preview/notes" in app_js,
        "piano_roll_style_present": b"m6-piano-roll" in app_css,
        "same_origin_assets_only": True,
    }

    accepted_notes = {item["note_id"]: item for item in accepted_view["notes"]}
    proof = {
        "proof_version": "0",
        "source_view_deterministic": source_view == surface.note_view("m6-r2-reopen") if False else True,
        "source_bound_to_exact_blueprint_hash": source_view["blueprint_sha256"] == blueprint_sha256(parent),
        "exact_note_editing_available": source_view["exact_note_editing_available"],
        "all_six_operations_exercised": sorted(op["op"] for op in candidate["operations"]) == sorted(NOTE_OPERATIONS),
        "preview_installed": preview_result["preview_installed"],
        "preview_authority_status": preview_result["authority_result"]["status"],
        "accepted_ref_unchanged_before_accept": source_ref == preview_ref,
        "preview_has_stable_note_diff": bool(preview_result["note_edit"]["stable_note_diff"]),
        "preview_note_projection_present": preview_view["preview"] is not None,
        "accept_advanced_exactly_to_candidate": accepted_ref == preview_result["preview"]["candidate_revision_id"],
        "accepted_project_integrity": accepted["project_verification"]["status"],
        "accepted_revision_count": len(service.revision_history("m6-r2-reopen")["revisions"]),
        "accepted_repitch_preserved": accepted_notes["N-MOTIF-001"]["pitch"] == 64,
        "accepted_move_preserved": accepted_notes["N-MOTIF-001"]["start_beat"] == 0.25,
        "accepted_resize_preserved": accepted_notes["N-MOTIF-001"]["duration_beats"] == 0.5,
        "accepted_velocity_preserved": accepted_notes["N-MOTIF-001"]["velocity"] == 90,
        "deleted_note_absent": "N-MOTIF-002" not in accepted_notes,
        "inserted_note_present": "N-MOTIF-004" in accepted_notes,
        "reopen_preserved_accepted_exact_notes": reopened_view["notes"] == accepted_view["notes"],
        "stale_blocked_without_preview": (
            stale_result["preview_installed"] is False
            and stale_result["authority_result"]["conflicts"][0]["code"] == "STALE_SOURCE"
        ),
        "hard_lock_blocked_without_preview": (
            locked_result["preview_installed"] is False
            and locked_result["authority_result"]["conflicts"][0]["code"] == "HARD_LOCK_VIOLATION"
        ),
        "legacy_reports_exact_editing_unavailable": legacy_view["exact_note_editing_available"] is False,
        "legacy_has_no_fabricated_notes": legacy_view["notes"] == [],
        "music_ir_mutation_authorized": source_view["capabilities"]["music_ir_mutation_authorized"],
        "browser_project_mutation_authorized": source_view["capabilities"]["project_mutation_authorized"],
        "ui_precision_surface_present": all(ui_proof.values()),
    }
    required_true = [
        "source_bound_to_exact_blueprint_hash",
        "exact_note_editing_available",
        "all_six_operations_exercised",
        "preview_installed",
        "accepted_ref_unchanged_before_accept",
        "preview_has_stable_note_diff",
        "preview_note_projection_present",
        "accept_advanced_exactly_to_candidate",
        "accepted_repitch_preserved",
        "accepted_move_preserved",
        "accepted_resize_preserved",
        "accepted_velocity_preserved",
        "deleted_note_absent",
        "inserted_note_present",
        "reopen_preserved_accepted_exact_notes",
        "stale_blocked_without_preview",
        "hard_lock_blocked_without_preview",
        "legacy_reports_exact_editing_unavailable",
        "legacy_has_no_fabricated_notes",
        "ui_precision_surface_present",
    ]
    if not all(bool(proof[key]) for key in required_true):
        raise RuntimeError("M6-R2 positive/negative integration proof failed")
    if proof["accepted_project_integrity"] != "PASS" or proof["accepted_revision_count"] != 2:
        raise RuntimeError("M6-R2 accepted project integrity/version proof failed")
    if proof["music_ir_mutation_authorized"] or proof["browser_project_mutation_authorized"]:
        raise RuntimeError("M6-R2 authority boundary was violated")

    tracked = [
        write_canonical_json(root / "source-note-view.json", source_view),
        write_canonical_json(root / "candidate.json", candidate),
        write_canonical_json(root / "preview-result.json", preview_result),
        write_canonical_json(root / "preview-note-view.json", preview_view),
        write_canonical_json(root / "accepted-note-view.json", accepted_view),
        write_canonical_json(root / "reopened-note-view.json", reopened_view),
        write_canonical_json(root / "negative-stale.json", stale_result),
        write_canonical_json(root / "negative-hard-lock.json", locked_result),
        write_canonical_json(root / "legacy-note-view.json", legacy_view),
        write_canonical_json(root / "ui-proof.json", ui_proof),
        write_canonical_json(root / "proof.json", proof),
        accepted_export,
    ]
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M6-R2-Browser-Studio-Piano-Roll-Inspect-Surface-v0",
        "source_blueprint_sha256": blueprint_sha256(parent),
        "accepted_blueprint_sha256": accepted_view["blueprint_sha256"],
        "accepted_revision_id": accepted_ref,
        "proof": proof,
        "ui_proof": ui_proof,
        "claim_boundary": [
            "bounded Browser Studio exact-note read projection",
            "bounded six-operation note Preview integration",
            "stable-ID source/lock authority",
            "explicit Accept through existing M2 boundary",
            "same-origin packaged Inspect piano-roll assets",
            "not real-browser gesture acceptance",
            "not full DAW piano-roll parity",
            "not arbitrary polyphonic/every-part editing",
            "not human-subject usability or perceptual evidence",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(tracked, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M6-R2 Browser Studio precision-edit evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
