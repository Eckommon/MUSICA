"""Generate deterministic M7-R6 truthful audition inspection evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .automation_edit import automation_material_sha256, blueprint_sha256
from .contracts import validate_contract
from .evidence import artifact_record, write_canonical_json
from .project import create_project
from .studio import StudioService
from .studio_automation import StudioAutomationSurface
from .studio_automation_audition import StudioAutomationAuditionSurface

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _blueprint(*, cutoff_only: bool = False) -> dict[str, Any]:
    blueprint = _load(BLUEPRINT_PATH)
    material = _load(AUTOMATION_PATH)
    cutoff = next(lane for lane in material["lanes"] if lane["lane_id"] == "B-SYNTH-CUTOFF")
    cutoff["section_id"] = "S01"
    if cutoff_only:
        material["lanes"] = [cutoff]
    blueprint["materials"]["automation"] = material
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _candidate(parent: dict[str, Any], *, cutoff: bool = False) -> dict[str, Any]:
    operation = (
        {
            "operation_id": "OP-R6-EVIDENCE-CUTOFF",
            "op": "SET_VALUE",
            "target": {"lane_id": "B-SYNTH-CUTOFF", "point_id": "P-CUTOFF-001"},
            "value": 1200.0,
        }
        if cutoff
        else {
            "operation_id": "OP-R6-EVIDENCE-GAIN",
            "op": "SET_VALUE",
            "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-001"},
            "value": 0.71,
        }
    )
    return {
        "candidate_version": "0",
        "candidate_id": "AEC-M7-R6-EVIDENCE-CUTOFF" if cutoff else "AEC-M7-R6-EVIDENCE-001",
        "authority_target": "blueprint_automation_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
            "automation_material_sha256": automation_material_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "m7-r6-evidence"},
        "reason": "M7-R6 deterministic truthful audition inspection evidence.",
        "operations": [operation],
        "preview_only": True,
    }


def run_evidence(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    blueprint = _blueprint()
    with tempfile.TemporaryDirectory(prefix="musica-m7-r6-") as temp_value:
        workspace = Path(temp_value) / "workspace"
        workspace.mkdir()
        create_project(workspace / "r6-evidence.musica", blueprint)

        service = StudioService(workspace)
        service.open_project_session(project_slug="r6-evidence", session_id="r6-evidence-session")
        edit_surface = StudioAutomationSurface(service)
        inspect_surface = StudioAutomationAuditionSurface(service)
        project = service._get_session("r6-evidence-session").project
        root_revision = project.head_revision_id()

        historical_r2 = edit_surface.automation_view("r6-evidence-session")
        accepted_initial = inspect_surface.audition_view("r6-evidence-session")
        edit = _candidate(blueprint)

        first = edit_surface.preview_automation_edit("r6-evidence-session", candidate=edit)
        first_inspection = inspect_surface.audition_view("r6-evidence-session")
        first_pending = first_inspection["pending_audition"]
        if first_pending is None:
            raise RuntimeError("M7-R6 evidence expected pending audible Preview")
        preview_wav = service.media_bytes("r6-evidence-session", "audio")
        preview_midi = service.media_bytes("r6-evidence-session", "midi")
        (root / "preview.wav").write_bytes(preview_wav)
        (root / "preview.mid").write_bytes(preview_midi)

        service.discard_preview("r6-evidence-session")
        discarded = inspect_surface.audition_view("r6-evidence-session")

        second = edit_surface.preview_automation_edit("r6-evidence-session", candidate=edit)
        second_inspection = inspect_surface.audition_view("r6-evidence-session")
        second_pending = second_inspection["pending_audition"]
        if second_pending is None:
            raise RuntimeError("M7-R6 evidence expected repeated pending Preview")
        preview_wav_second = service.media_bytes("r6-evidence-session", "audio")
        preview_midi_second = service.media_bytes("r6-evidence-session", "midi")

        accepted_result = service.accept_preview("r6-evidence-session")
        accepted = inspect_surface.audition_view("r6-evidence-session")
        accepted_revision = project.head_revision_id()
        revision_count = len(service.revision_history("r6-evidence-session")["revisions"])

        service.close_session("r6-evidence-session")
        reopened_service = StudioService(workspace)
        reopened_service.open_project_session(project_slug="r6-evidence", session_id="r6-evidence-reopen")
        reopened = StudioAutomationAuditionSurface(reopened_service).audition_view("r6-evidence-reopen")
        reopened_audio = reopened_service.media_bytes("r6-evidence-reopen", "audio")
        reopened_midi = reopened_service.media_bytes("r6-evidence-reopen", "midi")

        cutoff_blueprint = _blueprint(cutoff_only=True)
        cutoff_blueprint["project"]["project_id"] = "PRJ-M7-R6-CUTOFF"
        cutoff_blueprint["project"]["revision_id"] = "rev-m7-r6-cutoff-r1"
        validate_contract(cutoff_blueprint, "music-blueprint-v0.schema.json")
        create_project(workspace / "r6-cutoff.musica", cutoff_blueprint)
        reopened_service.open_project_session(project_slug="r6-cutoff", session_id="r6-cutoff-session")
        cutoff_edit = StudioAutomationSurface(reopened_service)
        cutoff_inspect = StudioAutomationAuditionSurface(reopened_service)
        cutoff_accepted = cutoff_inspect.audition_view("r6-cutoff-session")
        cutoff_edit.preview_automation_edit(
            "r6-cutoff-session",
            candidate=_candidate(cutoff_blueprint, cutoff=True),
        )
        cutoff_preview = cutoff_inspect.audition_view("r6-cutoff-session")

    pending_hashes = {
        "preview_wav_sha256": _sha(preview_wav),
        "preview_midi_sha256": _sha(preview_midi),
    }
    proof = {
        "proof_version": "0",
        "historical_r2_audible_capability_remains_false": historical_r2["capabilities"]["audible_automation_validated"] is False,
        "accepted_mapping_mix_gain_only": accepted_initial["accepted_mapping"]["mapped_lane_ids"] == ["A-MIX-GAIN"],
        "accepted_mapping_preserves_cutoff_unmapped": accepted_initial["accepted_mapping"]["unmapped_lane_ids"] == ["B-SYNTH-CUTOFF"],
        "initial_media_truthfully_fallback": accepted_initial["accepted_media"]["wav"]["source"] == "fallback_render" and accepted_initial["accepted_media"]["midi"]["source"] == "fallback_render",
        "preview_noncanonical": first_pending["canonical"] is False,
        "preview_reverse_promotion_disabled": first_pending["reverse_promotion_authorized"] is False,
        "preview_project_ref_unchanged": first_pending["project_ref_unchanged"] is True and project.head_revision_id() == accepted_revision,
        "preview_hashes_match_exact_media": first_pending["preview_wav_sha256"] == _sha(preview_wav) and first_pending["preview_midi_sha256"] == _sha(preview_midi),
        "pending_keeps_accepted_media_identity": first_inspection["accepted_media"] == accepted_initial["accepted_media"],
        "discard_removes_pending_audition": discarded["pending_audition"] is None,
        "discard_preserves_root_identity": discarded["accepted_revision_id"] == root_revision and discarded["accepted_media"] == accepted_initial["accepted_media"],
        "repeat_preview_descriptor_deterministic": first["preview"] == second["preview"],
        "repeat_preview_inspection_deterministic": first_inspection == second_inspection,
        "repeat_preview_audio_byte_identical": preview_wav == preview_wav_second,
        "repeat_preview_midi_byte_identical": preview_midi == preview_midi_second,
        "accept_advanced_exactly_one_revision": revision_count == 2 and accepted_revision == second["preview"]["candidate_revision_id"],
        "accept_integrity_pass": accepted_result["project_verification"]["status"] == "PASS",
        "accepted_wav_bound_exact_preview": accepted["accepted_media"]["wav"]["source"] == "bound_artifact" and accepted["accepted_media"]["wav"]["sha256"] == _sha(preview_wav_second),
        "accepted_midi_bound_exact_preview": accepted["accepted_media"]["midi"]["source"] == "bound_artifact" and accepted["accepted_media"]["midi"]["sha256"] == _sha(preview_midi_second),
        "reopen_preserves_accepted_inspection": reopened == accepted,
        "reopen_wav_exact_identity": _sha(reopened_audio) == accepted["accepted_media"]["wav"]["sha256"],
        "reopen_midi_exact_identity": _sha(reopened_midi) == accepted["accepted_media"]["midi"]["sha256"],
        "unsupported_only_accepted_unmapped": cutoff_accepted["accepted_mapping"]["mapped_lane_ids"] == [] and cutoff_accepted["accepted_mapping"]["unmapped_lane_ids"] == ["B-SYNTH-CUTOFF"],
        "unsupported_only_preview_inaudible": cutoff_preview["pending_audition"] is not None and cutoff_preview["pending_audition"]["automation_applied"] is False and cutoff_preview["pending_audition"]["output_differs_from_baseline"] is False,
        "canonical": accepted["authority"]["canonical"],
        "browser_mutation_authorized": accepted["authority"]["browser_mutation_authorized"],
        "project_mutation_authorized": accepted["authority"]["project_mutation_authorized"],
        "reverse_promotion_authorized": accepted["authority"]["reverse_promotion_authorized"],
        "explicit_accept_required": accepted["authority"]["explicit_accept_required"],
    }

    required_true = [
        key
        for key in proof
        if key not in {
            "proof_version",
            "canonical",
            "browser_mutation_authorized",
            "project_mutation_authorized",
            "reverse_promotion_authorized",
        }
    ]
    failed_true = [key for key in required_true if proof[key] is not True]
    required_false = [
        "canonical",
        "browser_mutation_authorized",
        "project_mutation_authorized",
        "reverse_promotion_authorized",
    ]
    failed_false = [key for key in required_false if proof[key] is not False]
    if failed_true or failed_false:
        raise RuntimeError(
            f"M7-R6 deterministic evidence failed: expected true={failed_true}, false={failed_false}"
        )

    write_canonical_json(root / "historical-r2-view.json", historical_r2)
    write_canonical_json(root / "accepted-initial.json", accepted_initial)
    write_canonical_json(root / "first-preview-inspection.json", first_inspection)
    write_canonical_json(root / "discarded-inspection.json", discarded)
    write_canonical_json(root / "second-preview-inspection.json", second_inspection)
    write_canonical_json(root / "accepted-inspection.json", accepted)
    write_canonical_json(root / "reopened-inspection.json", reopened)
    write_canonical_json(root / "unsupported-only-accepted.json", cutoff_accepted)
    write_canonical_json(root / "unsupported-only-preview.json", cutoff_preview)
    write_canonical_json(root / "pending-media-hashes.json", pending_hashes)
    write_canonical_json(root / "proof.json", proof)

    evidence_files = sorted(path for path in root.iterdir() if path.is_file())
    manifest = {
        "manifest_version": "0",
        "milestone": "M7-R6",
        "evidence_class": "DETERMINISTIC_AUDITION_INSPECTION_EVIDENCE",
        "accepted_revision_id": accepted_revision,
        "accepted_wav_sha256": accepted["accepted_media"]["wav"]["sha256"],
        "accepted_midi_sha256": accepted["accepted_media"]["midi"]["sha256"],
        "records": [artifact_record(path, root) for path in evidence_files],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return {**manifest, "proof": proof}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_evidence(args.out)


if __name__ == "__main__":
    main()
