from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from musica.contracts import ContractError, validate_contract


ROOT = Path(__file__).resolve().parents[1]


def _load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_exact_note_material_example_is_schema_valid() -> None:
    material = _load("examples/note-material/valid/dark-electronic-explicit-timeline-v0.json")
    validate_contract(material, "exact-note-material-v0.schema.json")
    ids = [note["note_id"] for note in material["notes"]]
    assert len(ids) == len(set(ids))
    assert material["time_base"] == {"unit": "quarter_note_beat", "origin_beat": 0.0}


def test_note_edit_candidate_is_blueprint_bound_and_preview_only() -> None:
    candidate = _load("examples/note-edits/valid/repitch-and-move-candidate-v0.json")
    validate_contract(candidate, "note-edit-candidate-v0.schema.json")
    assert candidate["authority_target"] == "blueprint_exact_note_material"
    assert candidate["preview_only"] is True
    for operation in candidate["operations"]:
        target = operation.get("target")
        if target is not None:
            assert set(target) == {"note_id", "part_id"}


def test_direct_music_ir_authority_candidate_is_rejected() -> None:
    invalid = _load("examples/note-edits/invalid/direct-music-ir-authority-candidate.json")
    with pytest.raises(ContractError):
        validate_contract(invalid, "note-edit-candidate-v0.schema.json")


def test_candidate_cannot_claim_accepted_or_non_preview_state() -> None:
    candidate = _load("examples/note-edits/valid/repitch-and-move-candidate-v0.json")
    candidate["preview_only"] = False
    with pytest.raises(ContractError):
        validate_contract(candidate, "note-edit-candidate-v0.schema.json")


def test_note_operation_cannot_address_array_index() -> None:
    candidate = _load("examples/note-edits/valid/repitch-and-move-candidate-v0.json")
    candidate["operations"][0]["target"]["array_index"] = 1
    with pytest.raises(ContractError):
        validate_contract(candidate, "note-edit-candidate-v0.schema.json")


def test_exact_note_pitch_and_duration_are_bounded() -> None:
    material = _load("examples/note-material/valid/dark-electronic-explicit-timeline-v0.json")
    invalid_pitch = copy.deepcopy(material)
    invalid_pitch["notes"][0]["pitch"] = 128
    with pytest.raises(ContractError):
        validate_contract(invalid_pitch, "exact-note-material-v0.schema.json")

    invalid_duration = copy.deepcopy(material)
    invalid_duration["notes"][0]["duration_beats"] = 0
    with pytest.raises(ContractError):
        validate_contract(invalid_duration, "exact-note-material-v0.schema.json")


def test_ready_authority_result_has_no_mutation_authority() -> None:
    result = _load("examples/note-edits/valid/ready-for-preview-result-v0.json")
    validate_contract(result, "note-edit-authority-result-v0.schema.json")
    assert result["status"] == "READY_FOR_PREVIEW"
    assert result["conflicts"] == []
    assert result["preview_generation_allowed"] is True
    assert result["explicit_accept_required"] is True
    assert result["project_mutation_authorized"] is False
    assert result["music_ir_mutation_authorized"] is False


@pytest.mark.parametrize(
    "fixture, code",
    [
        ("examples/note-edits/valid/blocked-stale-source-result-v0.json", "STALE_SOURCE"),
        ("examples/note-edits/valid/blocked-hard-lock-result-v0.json", "HARD_LOCK_VIOLATION"),
    ],
)
def test_blocked_authority_examples_fail_closed(fixture: str, code: str) -> None:
    result = _load(fixture)
    validate_contract(result, "note-edit-authority-result-v0.schema.json")
    assert result["status"] == "BLOCKED"
    assert result["preview_generation_allowed"] is False
    assert result["project_mutation_authorized"] is False
    assert result["music_ir_mutation_authorized"] is False
    assert code in {item["code"] for item in result["conflicts"]}


def test_ready_result_cannot_hide_conflict() -> None:
    ready = _load("examples/note-edits/valid/ready-for-preview-result-v0.json")
    blocked = _load("examples/note-edits/valid/blocked-hard-lock-result-v0.json")
    ready["conflicts"] = blocked["conflicts"]
    with pytest.raises(ContractError):
        validate_contract(ready, "note-edit-authority-result-v0.schema.json")


def test_blocked_result_requires_explicit_conflict() -> None:
    blocked = _load("examples/note-edits/valid/blocked-stale-source-result-v0.json")
    blocked["conflicts"] = []
    with pytest.raises(ContractError):
        validate_contract(blocked, "note-edit-authority-result-v0.schema.json")


def test_authority_result_cannot_authorize_project_or_ir_mutation() -> None:
    result = _load("examples/note-edits/valid/ready-for-preview-result-v0.json")
    result["project_mutation_authorized"] = True
    with pytest.raises(ContractError):
        validate_contract(result, "note-edit-authority-result-v0.schema.json")

    result = _load("examples/note-edits/valid/ready-for-preview-result-v0.json")
    result["music_ir_mutation_authorized"] = True
    with pytest.raises(ContractError):
        validate_contract(result, "note-edit-authority-result-v0.schema.json")
