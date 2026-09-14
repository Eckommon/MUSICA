"""Generate deterministic M7-R0 automation contract/design evidence."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Callable

from .automation_contracts import validate_automation_lock, validate_automation_material
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
VALID = ROOT / "examples" / "automation" / "valid"
INVALID = ROOT / "examples" / "automation" / "invalid"

CONTRACT_PATHS = [
    ROOT / "docs" / "M7_AUTOMATION_AUTHORITY.md",
    ROOT / "docs" / "M7_ACCEPTANCE.md",
    ROOT / "docs" / "M7_R0_DECISIONS.md",
    ROOT / "docs" / "M7_R0_SCOPE.md",
    ROOT / "docs" / "M7_R0_TRACEABILITY.md",
    ROOT / "evidence" / "M7_R0_PRECHECK.md",
    SCHEMA_DIR / "automation-material-v0.schema.json",
    SCHEMA_DIR / "automation-edit-candidate-v0.schema.json",
    SCHEMA_DIR / "automation-authority-result-v0.schema.json",
    SCHEMA_DIR / "automation-lock-v0.schema.json",
    ROOT / "src" / "musica" / "automation_contracts.py",
    ROOT / "src" / "musica" / "m7_r0_evidence.py",
    ROOT / "tests" / "test_m7_r0_automation_contracts.py",
    ROOT / ".github" / "workflows" / "m7-r0-automation-contract-evidence.yml",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _blocked(fn: Callable[[], None]) -> bool:
    try:
        fn()
    except ContractError:
        return True
    return False


def generate_m7_r0_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    material = _load(VALID / "automation-material-v0.json")
    candidate = _load(VALID / "automation-edit-candidate-v0.json")
    lock = _load(VALID / "automation-lock-v0.json")
    ready = _load(VALID / "automation-authority-ready-v0.json")
    blocked = _load(VALID / "automation-authority-blocked-v0.json")

    validate_automation_material(material)
    validate_contract(candidate, "automation-edit-candidate-v0.schema.json")
    validate_automation_lock(lock, material)
    validate_contract(ready, "automation-authority-result-v0.schema.json")
    validate_contract(blocked, "automation-authority-result-v0.schema.json")

    bad_track = copy.deepcopy(material)
    bad_track["lanes"][1]["target"]["scope"] = "track"

    bad_value = copy.deepcopy(material)
    bad_value["lanes"][0]["points"][0]["value"] = 1.5

    bad_ready = copy.deepcopy(ready)
    bad_ready["project_mutation_authorized"] = True

    material_schema = _load(SCHEMA_DIR / "automation-material-v0.schema.json")
    candidate_schema = _load(SCHEMA_DIR / "automation-edit-candidate-v0.schema.json")

    scope_enum = material_schema["$defs"]["target"]["properties"]["scope"]["enum"]
    operation_variants = candidate_schema["$defs"]["operation"]["oneOf"]
    operations = sorted(
        variant["properties"]["op"]["const"] for variant in operation_variants
    )

    proof = {
        "milestone": "M7-R0",
        "validation_class": "CONTRACT_DESIGN_ONLY",
        "automation_material_valid": True,
        "edit_candidate_valid": True,
        "automation_lock_valid": True,
        "ready_authority_result_valid": True,
        "blocked_authority_result_valid": True,
        "canonical_scope_enum": scope_enum,
        "derived_track_scope_excluded": "track" not in scope_enum,
        "primitive_operations": operations,
        "primitive_vocabulary_exact": operations
        == sorted([
            "INSERT_POINT",
            "DELETE_POINT",
            "MOVE_POINT",
            "SET_VALUE",
            "SET_INTERPOLATION",
        ]),
        "candidate_preview_only": candidate["preview_only"] is True,
        "ready_project_mutation_authorized": ready["project_mutation_authorized"],
        "ready_music_ir_mutation_authorized": ready["music_ir_mutation_authorized"],
        "track_scope_fails_closed": _blocked(lambda: validate_automation_material(bad_track)),
        "out_of_range_value_fails_closed": _blocked(
            lambda: validate_automation_material(bad_value)
        ),
        "duplicate_beat_fixture_fails_closed": _blocked(
            lambda: validate_automation_material(
                _load(INVALID / "duplicate-beat-material-v0.json")
            )
        ),
        "point_operation_without_point_id_fails_closed": _blocked(
            lambda: validate_contract(
                _load(INVALID / "missing-point-target-candidate-v0.json"),
                "automation-edit-candidate-v0.schema.json",
            )
        ),
        "direct_project_mutation_authority_fails_closed": _blocked(
            lambda: validate_contract(bad_ready, "automation-authority-result-v0.schema.json")
        ),
        "runtime_automation_editing_claimed": False,
        "blueprint_storage_integration_claimed": False,
        "audible_automation_rendering_claimed": False,
        "external_daw_automation_reconciliation_claimed": False,
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
    for path in sorted((ROOT / "examples" / "automation").rglob("*.json")):
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
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json"):
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
        "milestone": "M7-R0",
        "artifact_name": "musica-m7-r0-automation-contract-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    import os

    destination = os.environ.get(
        "MUSICA_M7_R0_EVIDENCE_OUT", "artifacts/m7-r0-automation-contract-evidence"
    )
    generate_m7_r0_evidence(destination)
