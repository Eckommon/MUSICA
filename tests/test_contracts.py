from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from musica.contracts import ContractError, clone_for_revision, validate_contract, validate_revision

ROOT = Path(__file__).resolve().parents[1]
VALID_BLUEPRINT = ROOT / "examples/blueprints/valid/dark-electronic-20s-r1.json"
INVALID_BLUEPRINT = ROOT / "examples/blueprints/invalid/semantic-out-of-range.json"
SEMANTIC_CONTROL = ROOT / "examples/semantic-controls/urgent-final-section.json"
SCHEMA_DIR = ROOT / "schemas"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_from(parent: dict, revision_id: str = "rev-002") -> dict:
    candidate = clone_for_revision(parent, revision_id)
    candidate["provenance"]["actor"] = "deterministic_transform"
    candidate["provenance"]["change_reason"] = "M0 contract test candidate revision."
    candidate["provenance"]["source_revision"] = parent["project"]["revision_id"]
    return candidate


def test_all_json_schemas_are_valid_draft_2020_12():
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        Draft202012Validator.check_schema(load(path))


def test_canonical_blueprint_validates():
    validate_contract(load(VALID_BLUEPRINT), "music-blueprint-v0.schema.json")


def test_invalid_semantic_value_fails_closed():
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_contract(load(INVALID_BLUEPRINT), "music-blueprint-v0.schema.json")


def test_semantic_control_uses_bounded_vocabulary():
    control = load(SEMANTIC_CONTROL)
    validate_contract(control, "semantic-control-v0.schema.json")
    control["name"] = "cinematic_magic"
    with pytest.raises(ContractError):
        validate_contract(control, "semantic-control-v0.schema.json")


def test_lock_constraint_standalone_contract():
    lock = {
        "kind": "lock",
        "lock_id": "L1",
        "strength": "HARD",
        "target": "/musical_context/tempo/bpm",
        "mode": "exact",
        "inheriting": True,
        "value": 112,
        "tolerance": 0,
        "reason": "test",
    }
    validate_contract(lock, "lock-constraint-v0.schema.json")


def test_valid_revision_preserves_hard_locks():
    parent = load(VALID_BLUEPRINT)
    candidate = candidate_from(parent)
    candidate["semantics"]["section_overrides"][0]["values"]["tension"] = 0.82
    candidate["semantics"]["section_overrides"][0]["values"]["motion"] = 0.78
    candidate["materials"]["harmony"]["tension_strategy"] = "denser_suspensions_in_final_section"
    conflicts = validate_revision(parent, candidate)
    assert conflicts == []


def test_hard_value_lock_blocks_tempo_mutation():
    parent = load(VALID_BLUEPRINT)
    candidate = candidate_from(parent)
    candidate["musical_context"]["tempo"]["bpm"] = 118
    conflicts = validate_revision(parent, candidate)
    assert any(c.rule_id == "L-TEMPO" and c.status == "BLOCKED" for c in conflicts)


def test_hard_identity_lock_blocks_motif_identity_mutation():
    parent = load(VALID_BLUEPRINT)
    candidate = candidate_from(parent)
    candidate["materials"]["melody"]["main_motif_id"] = "motif-B"
    conflicts = validate_revision(parent, candidate)
    assert any(c.rule_id == "L-MELODY-IDENTITY" and c.status == "BLOCKED" for c in conflicts)


def test_inherited_hard_lock_cannot_be_silently_removed():
    parent = load(VALID_BLUEPRINT)
    candidate = candidate_from(parent)
    candidate["locks"] = [lock for lock in candidate["locks"] if lock["lock_id"] != "L-MELODY-IDENTITY"]
    for section in candidate["form"]["sections"]:
        section["locks"] = [lock_id for lock_id in section["locks"] if lock_id != "L-MELODY-IDENTITY"]
    conflicts = validate_revision(parent, candidate)
    assert any(c.rule_id == "L-MELODY-IDENTITY" and c.status == "BLOCKED" for c in conflicts)


def test_hard_constraint_blocks_out_of_range_candidate():
    parent = load(VALID_BLUEPRINT)
    parent["locks"] = [lock for lock in parent["locks"] if lock["lock_id"] != "L-TEMPO"]
    candidate = candidate_from(parent)
    candidate["musical_context"]["tempo"]["bpm"] = 125
    conflicts = validate_revision(parent, candidate)
    assert any(c.rule_id == "C-TEMPO-RANGE" and c.status == "BLOCKED" for c in conflicts)


def test_sections_must_be_ordered_and_non_overlapping():
    blueprint = load(VALID_BLUEPRINT)
    blueprint["form"]["sections"][1]["start"] = 5.0
    with pytest.raises(ContractError, match="overlaps or is out of order"):
        validate_contract(blueprint, "music-blueprint-v0.schema.json")


def test_blueprint_and_music_ir_are_distinct_contracts():
    blueprint = load(VALID_BLUEPRINT)
    polluted = copy.deepcopy(blueprint)
    polluted["tracks"] = []
    with pytest.raises(ContractError):
        validate_contract(polluted, "music-blueprint-v0.schema.json")

    ir = {
        "ir_version": "0",
        "source_blueprint_revision": "rev-001",
        "timing": {"ppq": 480},
        "tempo_events": [{"tick": 0, "bpm": 112}],
        "tracks": [
            {
                "track_id": "T1",
                "part_id": "P-SYNTH",
                "channel": 0,
                "program": 81,
                "events": [{"type": "note", "tick": 0, "duration": 480, "note": 62, "velocity": 80}],
            }
        ],
        "compile_provenance": {
            "compiler_id": "musica-m0",
            "compiler_version": "0.0.1",
            "lowering_policy": "explicit-test-lowering",
            "approximations": [],
        },
    }
    validate_contract(ir, "music-ir-v0.schema.json")
    ir["intent"] = {"summary": "must not belong in IR"}
    with pytest.raises(ContractError):
        validate_contract(ir, "music-ir-v0.schema.json")
