"""Generate deterministic M7-R3 automation-lowering evidence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .automation_edit import automation_material_sha256, blueprint_sha256
from .automation_lowering import lower_automation_execution, validate_automation_execution
from .compiler import compile_blueprint
from .contracts import ContractError, validate_contract
from .evidence import artifact_record, canonical_json_bytes, write_canonical_json

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _explicit_blueprint() -> dict[str, Any]:
    blueprint = _load(BLUEPRINT_PATH)
    material = _load(AUTOMATION_PATH)
    cutoff = next(lane for lane in material["lanes"] if lane["lane_id"] == "B-SYNTH-CUTOFF")
    cutoff["section_id"] = "S01"
    gain = next(lane for lane in material["lanes"] if lane["lane_id"] == "A-MIX-GAIN")
    gain["points"].append(
        {
            "point_id": "P-GAIN-003",
            "beat": 12.0,
            "value": 0.75,
            "interpolation": "linear",
        }
    )
    blueprint["materials"]["automation"] = material
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _sha(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def run_evidence(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    explicit = _explicit_blueprint()
    legacy = _load(BLUEPRINT_PATH)
    validate_contract(legacy, "music-blueprint-v0.schema.json")

    explicit_source_before = canonical_json_bytes(explicit)
    legacy_source_before = canonical_json_bytes(legacy)
    compiler_before = compile_blueprint(copy.deepcopy(explicit))

    execution_a = lower_automation_execution(explicit)
    execution_b = lower_automation_execution(explicit)
    legacy_execution = lower_automation_execution(legacy)
    compiler_after = compile_blueprint(copy.deepcopy(explicit))

    explicit_unchanged = canonical_json_bytes(explicit) == explicit_source_before
    legacy_unchanged = canonical_json_bytes(legacy) == legacy_source_before
    execution_bytes_equal = canonical_json_bytes(execution_a) == canonical_json_bytes(execution_b)
    compiler_bytes_equal = canonical_json_bytes(compiler_before) == canonical_json_bytes(compiler_after)

    gain = next(lane for lane in execution_a["lanes"] if lane["lane_id"] == "A-MIX-GAIN")
    interpolation_proof = {
        "lane_id": gain["lane_id"],
        "parameter_id": gain["parameter_id"],
        "point_ids": [point["point_id"] for point in gain["points"]],
        "ticks": [point["tick"] for point in gain["points"]],
        "segments": gain["segments"],
        "linear_preserved": gain["segments"][0]["interpolation"] == "linear",
        "hold_preserved": gain["segments"][1]["interpolation"] == "hold",
    }

    tampered = copy.deepcopy(execution_a)
    tampered["lanes"][0]["backend_mapping"]["midi_cc"] = 11
    backend_address_rejected = False
    backend_rejection_reason = ""
    try:
        validate_automation_execution(tampered)
    except ContractError as exc:
        backend_address_rejected = True
        backend_rejection_reason = str(exc)

    authority_proof = {
        "classification": execution_a["classification"],
        "authority": execution_a["authority"],
        "all_backend_mappings_unmapped": all(
            lane["backend_mapping"] == {"status": "UNMAPPED"} for lane in execution_a["lanes"]
        ),
        "backend_address_injection_rejected": backend_address_rejected,
        "backend_address_rejection_reason": backend_rejection_reason,
        "source_blueprint_unchanged": explicit_unchanged,
        "legacy_blueprint_unchanged": legacy_unchanged,
    }

    compiler_regression = {
        "before_sha256": _sha(compiler_before),
        "after_sha256": _sha(compiler_after),
        "byte_identical": compiler_bytes_equal,
        "existing_control_controllers": sorted(
            {
                int(event["controller"])
                for track in compiler_after["tracks"]
                for event in track["events"]
                if event["type"] == "control"
            }
        ),
        "canonical_automation_injected_into_music_ir": False,
    }

    determinism = {
        "execution_a_sha256": _sha(execution_a),
        "execution_b_sha256": _sha(execution_b),
        "byte_identical": execution_bytes_equal,
        "policy_id": execution_a["lowering"]["policy_id"],
        "ppq": execution_a["lowering"]["ppq"],
        "tick_rounding": execution_a["lowering"]["tick_rounding"],
    }

    source_hashes = {
        "project_id": explicit["project"]["project_id"],
        "revision_id": explicit["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(explicit),
        "automation_material_sha256": automation_material_sha256(explicit),
        "execution_source": execution_a["source"],
        "exact_match": (
            execution_a["source"]["blueprint_sha256"] == blueprint_sha256(explicit)
            and execution_a["source"]["automation_material_sha256"]
            == automation_material_sha256(explicit)
        ),
    }

    proof = {
        "proof_version": "0",
        "explicit_source_bound_exactly": source_hashes["exact_match"],
        "explicit_automation_present": execution_a["source"]["explicit_automation_present"],
        "legacy_explicit_automation_present": legacy_execution["source"]["explicit_automation_present"],
        "legacy_lanes_empty": legacy_execution["lanes"] == [],
        "stable_lane_order": [lane["lane_id"] for lane in execution_a["lanes"]]
        == sorted(lane["lane_id"] for lane in execution_a["lanes"]),
        "stable_point_provenance_preserved": interpolation_proof["point_ids"]
        == ["P-GAIN-001", "P-GAIN-002", "P-GAIN-003"],
        "linear_semantics_preserved": interpolation_proof["linear_preserved"],
        "hold_semantics_preserved": interpolation_proof["hold_preserved"],
        "deterministic_tick_policy_recorded": execution_a["lowering"]["tick_rounding"]
        == "decimal_nearest_half_up_nonnegative",
        "execution_byte_deterministic": execution_bytes_equal,
        "backend_mapping_unmapped": authority_proof["all_backend_mappings_unmapped"],
        "backend_address_injection_rejected": backend_address_rejected,
        "derived_is_noncanonical": execution_a["authority"]["canonical"] is False,
        "project_mutation_authorized": execution_a["authority"]["project_mutation_authorized"],
        "blueprint_mutation_authorized": execution_a["authority"]["blueprint_mutation_authorized"],
        "reverse_promotion_authorized": execution_a["authority"]["reverse_promotion_authorized"],
        "renderer_mapping_authorized": execution_a["authority"]["renderer_mapping_authorized"],
        "audible_automation_validated": execution_a["authority"]["audible_automation_validated"],
        "source_blueprint_unchanged": explicit_unchanged,
        "legacy_blueprint_unchanged": legacy_unchanged,
        "existing_music_ir_compiler_byte_identical": compiler_bytes_equal,
        "canonical_automation_injected_into_existing_music_ir": False,
    }

    required_true = [
        "explicit_source_bound_exactly",
        "explicit_automation_present",
        "legacy_lanes_empty",
        "stable_lane_order",
        "stable_point_provenance_preserved",
        "linear_semantics_preserved",
        "hold_semantics_preserved",
        "deterministic_tick_policy_recorded",
        "execution_byte_deterministic",
        "backend_mapping_unmapped",
        "backend_address_injection_rejected",
        "derived_is_noncanonical",
        "source_blueprint_unchanged",
        "legacy_blueprint_unchanged",
        "existing_music_ir_compiler_byte_identical",
    ]
    if not all(bool(proof[key]) for key in required_true):
        raise RuntimeError("M7-R3 positive proof failed")
    required_false = [
        "legacy_explicit_automation_present",
        "project_mutation_authorized",
        "blueprint_mutation_authorized",
        "reverse_promotion_authorized",
        "renderer_mapping_authorized",
        "audible_automation_validated",
        "canonical_automation_injected_into_existing_music_ir",
    ]
    if any(bool(proof[key]) for key in required_false):
        raise RuntimeError("M7-R3 authority/non-claim boundary failed")

    tracked = [
        write_canonical_json(root / "source-hashes.json", source_hashes),
        write_canonical_json(root / "source-automation-material.json", explicit["materials"]["automation"]),
        write_canonical_json(root / "execution-a.json", execution_a),
        write_canonical_json(root / "execution-b.json", execution_b),
        write_canonical_json(root / "legacy-empty-execution.json", legacy_execution),
        write_canonical_json(root / "hold-linear-proof.json", interpolation_proof),
        write_canonical_json(root / "determinism.json", determinism),
        write_canonical_json(root / "authority-boundary-proof.json", authority_proof),
        write_canonical_json(root / "compiler-regression.json", compiler_regression),
        write_canonical_json(root / "proof.json", proof),
    ]
    manifest = {
        "manifest_version": "0",
        "evidence_class": "DETERMINISTIC_AUTOMATION_LOWERING_EVIDENCE",
        "evidence_scope": "M7-R3-Automation-Execution-v0",
        "source_blueprint_sha256": blueprint_sha256(explicit),
        "source_automation_material_sha256": automation_material_sha256(explicit),
        "execution_sha256": _sha(execution_a),
        "proof": proof,
        "claim_boundary": [
            "accepted canonical automation to backend-independent derived execution package",
            "stable lane/parameter/point source provenance",
            "deterministic quarter-note-beat to PPQ tick policy",
            "explicit hold/linear outgoing-segment semantics",
            "backend mapping remains UNMAPPED",
            "legacy no-automation produces explicit empty derived execution",
            "no project or Blueprint mutation authority",
            "no reverse promotion authority",
            "not Music IR MIDI-CC automation mapping",
            "not audible automation rendering evidence",
            "not plug-in/device/DAW automation mapping",
        ],
        "artifacts": [artifact_record(path, root) for path in sorted(tracked, key=lambda item: item.name)],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M7-R3 automation lowering evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_evidence(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
