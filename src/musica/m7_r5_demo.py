"""Generate deterministic M7-R5 Studio audible automation lifecycle evidence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .automation_edit import automation_material_sha256, blueprint_sha256
from .automation_lowering import lower_automation_execution
from .automation_renderer import build_automation_render_plan
from .compiler import compile_blueprint
from .contracts import validate_contract
from .evidence import artifact_record, write_canonical_json
from .project import create_project
from .studio import StudioService
from .studio_automation import StudioAutomationSurface

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _blueprint() -> dict[str, Any]:
    blueprint = _load(BLUEPRINT_PATH)
    material = _load(AUTOMATION_PATH)
    cutoff = next(lane for lane in material["lanes"] if lane["lane_id"] == "B-SYNTH-CUTOFF")
    cutoff["section_id"] = "S01"
    blueprint["materials"]["automation"] = material
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _candidate(parent: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": "AEC-M7-R5-EVIDENCE-001",
        "authority_target": "blueprint_automation_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
            "automation_material_sha256": automation_material_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "m7-r5-evidence"},
        "reason": "M7-R5 deterministic Studio audition evidence.",
        "operations": [
            {
                "operation_id": "OP-R5-EVIDENCE-GAIN",
                "op": "SET_VALUE",
                "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-001"},
                "value": 0.71,
            }
        ],
        "preview_only": True,
    }


def run_evidence(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    blueprint = _blueprint()
    with tempfile.TemporaryDirectory(prefix="musica-m7-r5-") as temp_value:
        workspace = Path(temp_value) / "workspace"
        workspace.mkdir()
        create_project(workspace / "r5-evidence.musica", blueprint)

        service = StudioService(workspace)
        service.open_project_session(
            project_slug="r5-evidence",
            session_id="r5-evidence-session",
        )
        surface = StudioAutomationSurface(service)
        project = service._get_session("r5-evidence-session").project
        accepted_head_before = project.head_revision_id()
        accepted_audio_before = service.media_bytes("r5-evidence-session", "audio")
        accepted_midi_before = service.media_bytes("r5-evidence-session", "midi")
        accepted_before = {
            "head_revision_id": accepted_head_before,
            "audio_sha256": _sha(accepted_audio_before),
            "midi_sha256": _sha(accepted_midi_before),
        }

        edit = _candidate(blueprint)
        first = surface.preview_automation_edit("r5-evidence-session", candidate=edit)
        pending_first = service._get_session("r5-evidence-session").pending
        if pending_first is None:
            raise RuntimeError("M7-R5 evidence expected a pending Preview")

        preview_wav = service.media_bytes("r5-evidence-session", "audio")
        preview_midi = service.media_bytes("r5-evidence-session", "midi")
        candidate_blueprint = copy.deepcopy(pending_first.candidate)
        music_ir = compile_blueprint(copy.deepcopy(candidate_blueprint))
        execution = lower_automation_execution(copy.deepcopy(candidate_blueprint))
        render_plan = build_automation_render_plan(music_ir, execution)
        pending_root = pending_first.wav_path.parent

        (root / "preview.wav").write_bytes(preview_wav)
        (root / "preview.mid").write_bytes(preview_midi)

        discarded = service.discard_preview("r5-evidence-session")
        accepted_audio_after_discard = service.media_bytes("r5-evidence-session", "audio")
        accepted_midi_after_discard = service.media_bytes("r5-evidence-session", "midi")
        discard_proof = {
            "discarded_preview_id": discarded["discarded_preview_id"],
            "accepted_head_unchanged": project.head_revision_id() == accepted_head_before,
            "pending_cache_removed": not pending_root.exists(),
            "accepted_audio_unchanged": accepted_audio_after_discard == accepted_audio_before,
            "accepted_midi_unchanged": accepted_midi_after_discard == accepted_midi_before,
        }

        second = surface.preview_automation_edit("r5-evidence-session", candidate=edit)
        preview_wav_second = service.media_bytes("r5-evidence-session", "audio")
        preview_midi_second = service.media_bytes("r5-evidence-session", "midi")
        preview_repeat = {
            "preview_descriptor_identical": first["preview"] == second["preview"],
            "audition_proof_identical": first["studio_audition"] == second["studio_audition"],
            "wav_byte_identical": preview_wav_second == preview_wav,
            "midi_byte_identical": preview_midi_second == preview_midi,
        }

        accepted = service.accept_preview("r5-evidence-session")
        accepted_audio = service.media_bytes("r5-evidence-session", "audio")
        accepted_midi = service.media_bytes("r5-evidence-session", "midi")
        artifact_manifest = copy.deepcopy(accepted["artifact_manifest"])
        accept_proof = {
            "accepted_preview_id": accepted["accepted_preview_id"],
            "accepted_revision_id": accepted["revision_record"]["revision_id"],
            "one_revision_advance": project.head_revision_id()
            == second["preview"]["candidate_revision_id"],
            "project_integrity_pass": accepted["project_verification"]["status"] == "PASS",
            "artifact_count": len(artifact_manifest["artifacts"]),
            "accepted_audio_equals_preview": accepted_audio == preview_wav_second,
            "accepted_midi_equals_preview": accepted_midi == preview_midi_second,
            "accepted_audio_sha256": _sha(accepted_audio),
            "accepted_midi_sha256": _sha(accepted_midi),
        }

        accepted_revision = project.head_revision_id()
        service.close_session("r5-evidence-session")
        reopened_service = StudioService(workspace)
        reopened = reopened_service.open_project_session(
            project_slug="r5-evidence",
            session_id="r5-evidence-reopen",
        )
        reopened_audio = reopened_service.media_bytes("r5-evidence-reopen", "audio")
        reopened_midi = reopened_service.media_bytes("r5-evidence-reopen", "midi")
        reopen_proof = {
            "head_revision_id": reopened["session"]["head_revision_id"],
            "head_matches_accepted": reopened["session"]["head_revision_id"] == accepted_revision,
            "integrity_status": reopened["session"]["integrity_status"],
            "audio_equals_accepted_preview": reopened_audio == preview_wav_second,
            "midi_equals_accepted_preview": reopened_midi == preview_midi_second,
            "audio_sha256": _sha(reopened_audio),
            "midi_sha256": _sha(reopened_midi),
        }

    audition = copy.deepcopy(first["studio_audition"])
    authority_proof = {
        "preview_is_noncanonical": audition["canonical"] is False,
        "reverse_promotion_authorized": audition["reverse_promotion_authorized"],
        "accepted_ref_unchanged_during_preview": audition["project_ref_unchanged"],
        "r2_view_capability_remains_false": first["automation_view"]["capabilities"]
        ["audible_automation_validated"]
        is False,
        "mapped_lane_ids": audition["mapped_lane_ids"],
        "unmapped_lane_ids": audition["unmapped_lane_ids"],
        "midi_unchanged_by_audition": _sha(preview_midi) == audition["preview_midi_sha256"],
    }

    proof = {
        "proof_version": "0",
        "preview_installed": first["preview_installed"],
        "mix_gain_mapped_only": audition["mapped_lane_ids"] == ["A-MIX-GAIN"],
        "cutoff_remains_unmapped": audition["unmapped_lane_ids"] == ["B-SYNTH-CUTOFF"],
        "audible_output_differs_from_baseline": audition["output_differs_from_baseline"],
        "preview_hash_matches_media": audition["preview_wav_sha256"] == _sha(preview_wav),
        "preview_midi_hash_matches_media": audition["preview_midi_sha256"] == _sha(preview_midi),
        "discard_preserves_accepted_head": discard_proof["accepted_head_unchanged"],
        "discard_removes_cache": discard_proof["pending_cache_removed"],
        "discard_restores_accepted_audio": discard_proof["accepted_audio_unchanged"],
        "discard_restores_accepted_midi": discard_proof["accepted_midi_unchanged"],
        "repeat_preview_deterministic": all(preview_repeat.values()),
        "accept_exact_audio_identity": accept_proof["accepted_audio_equals_preview"],
        "accept_exact_midi_identity": accept_proof["accepted_midi_equals_preview"],
        "accept_integrity_pass": accept_proof["project_integrity_pass"],
        "accept_artifact_count_two": accept_proof["artifact_count"] == 2,
        "reopen_head_matches": reopen_proof["head_matches_accepted"],
        "reopen_integrity_pass": reopen_proof["integrity_status"] == "PASS",
        "reopen_audio_identity": reopen_proof["audio_equals_accepted_preview"],
        "reopen_midi_identity": reopen_proof["midi_equals_accepted_preview"],
        "preview_noncanonical": authority_proof["preview_is_noncanonical"],
        "project_ref_unchanged": authority_proof["accepted_ref_unchanged_during_preview"],
        "r2_capability_contract_preserved": authority_proof["r2_view_capability_remains_false"],
        "canonical": audition["canonical"],
        "reverse_promotion_authorized": audition["reverse_promotion_authorized"],
    }

    required_true = [
        key
        for key in proof
        if key not in {"proof_version", "canonical", "reverse_promotion_authorized"}
    ]
    failed_true = [key for key in required_true if proof[key] is not True]
    failed_false = [
        key
        for key in ["canonical", "reverse_promotion_authorized"]
        if proof[key] is not False
    ]
    if failed_true or failed_false:
        raise RuntimeError(
            f"M7-R5 evidence proof failed: expected true={failed_true}, expected false={failed_false}"
        )

    write_canonical_json(root / "accepted-before.json", accepted_before)
    write_canonical_json(root / "candidate-blueprint.json", candidate_blueprint)
    write_canonical_json(root / "automation-execution.json", execution)
    write_canonical_json(root / "automation-render-plan.json", render_plan)
    write_canonical_json(root / "preview-descriptor.json", first["preview"])
    write_canonical_json(root / "preview-audition-proof.json", audition)
    write_canonical_json(root / "preview-repeat-proof.json", preview_repeat)
    write_canonical_json(root / "discard-proof.json", discard_proof)
    write_canonical_json(root / "accept-proof.json", accept_proof)
    write_canonical_json(root / "accepted-artifact-manifest.json", artifact_manifest)
    write_canonical_json(root / "reopen-proof.json", reopen_proof)
    write_canonical_json(root / "authority-boundary-proof.json", authority_proof)
    write_canonical_json(root / "proof.json", proof)

    evidence_files = sorted(path for path in root.iterdir() if path.is_file())
    manifest = {
        "manifest_version": "0",
        "milestone": "M7-R5",
        "candidate_revision_id": first["preview"]["candidate_revision_id"],
        "preview_wav_sha256": _sha(preview_wav),
        "preview_midi_sha256": _sha(preview_midi),
        "records": [artifact_record(path, root) for path in evidence_files],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_evidence(args.out)


if __name__ == "__main__":
    main()
