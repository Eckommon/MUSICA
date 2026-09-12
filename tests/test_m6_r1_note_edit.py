from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from musica.compiler import PPQ, compile_blueprint
from musica.contracts import ContractError, clone_for_revision, validate_contract, validate_revision
from musica.note_edit import (
    accept_note_edit_preview,
    blueprint_sha256,
    build_note_edit_preview,
)
from musica.project import create_project

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
MATERIAL_PATH = ROOT / "examples" / "note-material" / "valid" / "dark-electronic-explicit-timeline-v0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def exact_blueprint(*, locked: bool = False) -> dict:
    blueprint = _load(BLUEPRINT_PATH)
    blueprint["materials"]["melody"]["exact_timeline"] = _load(MATERIAL_PATH)
    if locked:
        blueprint["materials"]["melody"]["exact_note_locks"] = [
            {
                "lock_version": "0",
                "lock_id": "L-M6-N1-PITCH",
                "strength": "HARD",
                "selector": {
                    "part_id": "P-SYNTH",
                    "note_id": "N-MOTIF-001",
                    "property": "pitch",
                },
                "mode": "exact",
                "inheriting": True,
                "value": 62,
                "reason": "Protect the accepted anchor pitch.",
            }
        ]
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def candidate(parent: dict, operations: list[dict], *, candidate_id: str = "NEC-M6-R1-001") -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_exact_note_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "m6-r1-test"},
        "reason": "M6-R1 exact-note edit test.",
        "operations": operations,
        "preview_only": True,
    }


def target(note_id: str = "N-MOTIF-001", part_id: str = "P-SYNTH") -> dict:
    return {"note_id": note_id, "part_id": part_id}


def motif_note_events(blueprint: dict) -> list[dict]:
    ir = compile_blueprint(blueprint)
    track = next(track for track in ir["tracks"] if track["track_id"] == "T-MOTIF")
    return [event for event in track["events"] if event["type"] == "note"]


def test_legacy_motif_path_remains_valid_and_deterministic() -> None:
    legacy = _load(BLUEPRINT_PATH)
    validate_contract(legacy, "music-blueprint-v0.schema.json")
    assert compile_blueprint(legacy) == compile_blueprint(copy.deepcopy(legacy))
    assert "exact_timeline" not in legacy["materials"]["melody"]
    assert compile_blueprint(legacy)["compile_provenance"]["lowering_policy"].startswith("explicit motif/drums")


def test_exact_timeline_blueprint_validates() -> None:
    blueprint = exact_blueprint()
    timeline = blueprint["materials"]["melody"]["exact_timeline"]
    assert [note["note_id"] for note in timeline["notes"]] == [
        "N-MOTIF-001",
        "N-MOTIF-002",
        "N-MOTIF-003",
    ]


def test_exact_timeline_duplicate_note_id_fails_closed() -> None:
    blueprint = exact_blueprint()
    duplicate = copy.deepcopy(blueprint["materials"]["melody"]["exact_timeline"]["notes"][0])
    duplicate["start_beat"] = 3.75
    blueprint["materials"]["melody"]["exact_timeline"]["notes"].append(duplicate)
    with pytest.raises(ContractError, match="exact note_id must be unique"):
        validate_contract(blueprint, "music-blueprint-v0.schema.json")


def test_exact_timeline_canonical_order_is_required() -> None:
    blueprint = exact_blueprint()
    notes = blueprint["materials"]["melody"]["exact_timeline"]["notes"]
    notes[0], notes[1] = notes[1], notes[0]
    with pytest.raises(ContractError, match="canonical order"):
        validate_contract(blueprint, "music-blueprint-v0.schema.json")


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("part_id", "P-UNKNOWN", "unknown part_id"),
        ("section_id", "S-UNKNOWN", "unknown section_id"),
    ],
)
def test_exact_timeline_unknown_ownership_fails_closed(field: str, value: str, match: str) -> None:
    blueprint = exact_blueprint()
    blueprint["materials"]["melody"]["exact_timeline"]["notes"][0][field] = value
    with pytest.raises(ContractError, match=match):
        validate_contract(blueprint, "music-blueprint-v0.schema.json")


def test_exact_timeline_r1_is_explicitly_bounded_to_motif_lead_part() -> None:
    blueprint = exact_blueprint()
    note = blueprint["materials"]["melody"]["exact_timeline"]["notes"][0]
    note["part_id"] = "P-BASS"
    with pytest.raises(ContractError, match="supports only motif/lead part"):
        validate_contract(blueprint, "music-blueprint-v0.schema.json")


def test_exact_timeline_requires_fixed_tempo_and_section_consistency() -> None:
    adaptive = exact_blueprint()
    adaptive["musical_context"]["tempo"]["policy"] = "adaptive"
    with pytest.raises(ContractError, match="requires fixed tempo"):
        validate_contract(adaptive, "music-blueprint-v0.schema.json")

    outside = exact_blueprint()
    outside["materials"]["melody"]["exact_timeline"]["notes"][0]["start_beat"] = 12.0
    outside["materials"]["melody"]["exact_timeline"]["notes"].sort(
        key=lambda item: (item["start_beat"], item["part_id"], item["pitch"], item["note_id"])
    )
    with pytest.raises(ContractError, match="outside declared section"):
        validate_contract(outside, "music-blueprint-v0.schema.json")


def test_exact_timeline_lowers_pitch_time_duration_velocity_faithfully() -> None:
    blueprint = exact_blueprint()
    events = motif_note_events(blueprint)
    assert events == [
        {"type": "note", "tick": 0, "duration": round(0.75 * PPQ), "note": 62, "velocity": 82},
        {"type": "note", "tick": PPQ, "duration": round(0.75 * PPQ), "note": 65, "velocity": 76},
        {"type": "note", "tick": 2 * PPQ, "duration": round(1.5 * PPQ), "note": 69, "velocity": 80},
    ]
    assert compile_blueprint(blueprint)["compile_provenance"]["lowering_policy"].startswith(
        "explicit exact-note timeline"
    )


def test_semantic_energy_changes_do_not_rewrite_exact_note_properties() -> None:
    low = exact_blueprint()
    high = copy.deepcopy(low)
    low["semantics"]["global"]["energy"] = 0.0
    high["semantics"]["global"]["energy"] = 1.0
    for section in low["form"]["sections"]:
        section["semantic_targets"]["energy"] = 0.0
    for section in high["form"]["sections"]:
        section["semantic_targets"]["energy"] = 1.0
    assert motif_note_events(low) == motif_note_events(high)


@pytest.mark.parametrize(
    "operation,expected",
    [
        (
            {"operation_id": "OP-MOVE", "op": "MOVE", "target": target(), "start_beat": 0.25},
            ("N-MOTIF-001", "start_beat", 0.25),
        ),
        (
            {"operation_id": "OP-RESIZE", "op": "RESIZE", "target": target(), "duration_beats": 0.5},
            ("N-MOTIF-001", "duration_beats", 0.5),
        ),
        (
            {"operation_id": "OP-REPITCH", "op": "REPITCH", "target": target(), "pitch": 64},
            ("N-MOTIF-001", "pitch", 64),
        ),
        (
            {"operation_id": "OP-VEL", "op": "SET_VELOCITY", "target": target(), "velocity": 90},
            ("N-MOTIF-001", "velocity", 90),
        ),
    ],
)
def test_stable_id_update_operations_build_ready_preview(operation: dict, expected: tuple[str, str, object]) -> None:
    parent = exact_blueprint()
    preview = build_note_edit_preview(parent, candidate(parent, [operation]))
    assert preview.ready is True
    assert preview.blueprint is not None
    note_id, field, value = expected
    note = next(
        note
        for note in preview.blueprint["materials"]["melody"]["exact_timeline"]["notes"]
        if note["note_id"] == note_id
    )
    assert note[field] == value
    assert preview.changed_note_ids == [note_id]


def test_insert_and_delete_are_stable_id_operations() -> None:
    parent = exact_blueprint()
    inserted = {
        "note_id": "N-MOTIF-004",
        "part_id": "P-SYNTH",
        "section_id": "S01",
        "start_beat": 4.0,
        "duration_beats": 0.5,
        "pitch": 67,
        "velocity": 74,
    }
    insert_preview = build_note_edit_preview(
        parent,
        candidate(parent, [{"operation_id": "OP-INSERT", "op": "INSERT", "note": inserted}]),
    )
    assert insert_preview.ready is True
    assert insert_preview.blueprint is not None
    assert any(note["note_id"] == "N-MOTIF-004" for note in insert_preview.blueprint["materials"]["melody"]["exact_timeline"]["notes"])
    assert insert_preview.stable_note_diff[0]["op"] == "insert"

    delete_preview = build_note_edit_preview(
        parent,
        candidate(parent, [{"operation_id": "OP-DELETE", "op": "DELETE", "target": target()}]),
    )
    assert delete_preview.ready is True
    assert delete_preview.blueprint is not None
    assert not any(note["note_id"] == "N-MOTIF-001" for note in delete_preview.blueprint["materials"]["melody"]["exact_timeline"]["notes"])
    assert delete_preview.stable_note_diff[0]["op"] == "delete"


@pytest.mark.parametrize("source_field", ["project_id", "revision_id", "blueprint_sha256"])
def test_stale_source_binding_blocks_without_preview(source_field: str) -> None:
    parent = exact_blueprint()
    edit = candidate(
        parent,
        [{"operation_id": "OP-REPITCH", "op": "REPITCH", "target": target(), "pitch": 64}],
    )
    edit["source"][source_field] = "0" * 64 if source_field == "blueprint_sha256" else "stale"
    preview = build_note_edit_preview(parent, edit)
    assert preview.ready is False
    assert preview.blueprint is None
    assert preview.authority_result["conflicts"][0]["code"] == "STALE_SOURCE"


def test_duplicate_operation_ids_fail_closed() -> None:
    parent = exact_blueprint()
    edit = candidate(
        parent,
        [
            {"operation_id": "OP-DUP", "op": "REPITCH", "target": target(), "pitch": 64},
            {"operation_id": "OP-DUP", "op": "SET_VELOCITY", "target": target(), "velocity": 90},
        ],
    )
    preview = build_note_edit_preview(parent, edit)
    assert preview.ready is False
    assert preview.authority_result["conflicts"][0]["code"] == "UNREPRESENTABLE_EDIT"


@pytest.mark.parametrize(
    "part_id,note_id,code",
    [
        ("P-SYNTH", "N-NOT-THERE", "UNKNOWN_NOTE"),
        ("P-BASS", "N-MOTIF-001", "PART_MISMATCH"),
    ],
)
def test_missing_or_wrong_part_target_fails_closed(part_id: str, note_id: str, code: str) -> None:
    parent = exact_blueprint()
    edit = candidate(
        parent,
        [
            {
                "operation_id": "OP-TARGET",
                "op": "REPITCH",
                "target": target(note_id=note_id, part_id=part_id),
                "pitch": 64,
            }
        ],
    )
    preview = build_note_edit_preview(parent, edit)
    assert preview.ready is False
    assert preview.authority_result["conflicts"][0]["code"] == code


def test_invalid_inserted_note_is_structured_block_not_project_mutation() -> None:
    parent = exact_blueprint()
    bad_note = {
        "note_id": "N-BAD-SECTION",
        "part_id": "P-SYNTH",
        "section_id": "S-UNKNOWN",
        "start_beat": 4.0,
        "duration_beats": 0.5,
        "pitch": 67,
        "velocity": 74,
    }
    preview = build_note_edit_preview(
        parent,
        candidate(parent, [{"operation_id": "OP-INSERT-BAD", "op": "INSERT", "note": bad_note}]),
    )
    assert preview.ready is False
    assert preview.authority_result["conflicts"][0]["code"] == "INVALID_NOTE"


def test_stable_id_hard_note_lock_blocks_preview_and_revision() -> None:
    parent = exact_blueprint(locked=True)
    edit = candidate(
        parent,
        [{"operation_id": "OP-LOCKED", "op": "REPITCH", "target": target(), "pitch": 64}],
    )
    preview = build_note_edit_preview(parent, edit)
    assert preview.ready is False
    conflict = preview.authority_result["conflicts"][0]
    assert conflict["code"] == "HARD_LOCK_VIOLATION"
    assert conflict["rule_id"] == "L-M6-N1-PITCH"

    direct = clone_for_revision(parent, "rev-direct-lock-violation")
    direct["materials"]["melody"]["exact_timeline"]["notes"][0]["pitch"] = 64
    conflicts = validate_revision(parent, direct)
    assert any(item.rule_type == "note_lock" and item.status == "BLOCKED" for item in conflicts)


def test_direct_m2_commit_cannot_bypass_stable_note_lock(tmp_path: Path) -> None:
    parent = exact_blueprint(locked=True)
    project = create_project(tmp_path / "locked.musica", parent)
    direct = clone_for_revision(parent, "rev-direct-lock-bypass")
    direct["materials"]["melody"]["exact_timeline"]["notes"][0]["pitch"] = 64
    with pytest.raises(ContractError, match="revision commit blocked"):
        project.commit_revision(direct)
    assert project.head_revision_id() == parent["project"]["revision_id"]


def test_preview_is_side_effect_free_and_accept_advances_exactly_once(tmp_path: Path) -> None:
    parent = exact_blueprint()
    project = create_project(tmp_path / "edit.musica", parent)
    root_id = project.head_revision_id()
    edit = candidate(
        parent,
        [{"operation_id": "OP-ACCEPT", "op": "REPITCH", "target": target(), "pitch": 64}],
    )

    preview = build_note_edit_preview(parent, edit)
    assert preview.ready is True
    assert project.head_revision_id() == root_id
    assert preview.blueprint is not None
    assert compile_blueprint(preview.blueprint) == compile_blueprint(copy.deepcopy(preview.blueprint))

    record = accept_note_edit_preview(project, preview)
    assert project.head_revision_id() == preview.blueprint["project"]["revision_id"]
    assert record["parent_revision_id"] == root_id
    assert project.verify_integrity()["revision_count"] == 2

    with pytest.raises(ContractError, match="immutable"):
        accept_note_edit_preview(project, preview)


def test_preview_diff_and_hash_are_deterministic_across_repeat_execution() -> None:
    parent = exact_blueprint()
    edit = candidate(
        parent,
        [
            {"operation_id": "OP-MOVE", "op": "MOVE", "target": target(), "start_beat": 0.25},
            {"operation_id": "OP-REPITCH", "op": "REPITCH", "target": target(), "pitch": 64},
        ],
    )
    first = build_note_edit_preview(parent, edit)
    second = build_note_edit_preview(copy.deepcopy(parent), copy.deepcopy(edit))
    assert first.ready is True
    assert first.as_dict() == second.as_dict()
    assert first.blueprint == second.blueprint
    assert first.candidate_blueprint_sha256 == blueprint_sha256(first.blueprint)
