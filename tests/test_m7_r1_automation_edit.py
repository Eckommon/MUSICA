from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from musica.automation_contracts import (
    automation_material_from_blueprint,
    empty_automation_material,
)
from musica.automation_edit import (
    accept_automation_edit_preview,
    automation_material_sha256,
    blueprint_sha256,
    build_automation_edit_preview,
)
from musica.contracts import ContractError, clone_for_revision, validate_contract, validate_revision
from musica.evidence import canonical_json_bytes
from musica.project import create_project

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def automation_material() -> dict:
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
                    {
                        "point_id": "AP-GAIN-001",
                        "beat": 0.0,
                        "value": -6.0,
                        "interpolation": "linear",
                    },
                    {
                        "point_id": "AP-GAIN-002",
                        "beat": 8.0,
                        "value": -3.0,
                        "interpolation": "hold",
                    },
                ],
            }
        ],
    }


def exact_value_lock() -> dict:
    return {
        "lock_version": "0",
        "lock_id": "L-AUTO-GAIN-VALUE",
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
        "reason": "Protect accepted opening gain.",
    }


def presence_lock() -> dict:
    return {
        "lock_version": "0",
        "lock_id": "L-AUTO-GAIN-PRESENCE",
        "strength": "HARD",
        "selector": {
            "lane_id": "A-GAIN",
            "point_id": "AP-GAIN-001",
            "property": "point",
        },
        "mode": "presence",
        "inheriting": True,
        "reason": "Opening gain anchor must remain present.",
    }


def automation_blueprint(*, lock: str | None = None) -> dict:
    blueprint = _load(BLUEPRINT_PATH)
    blueprint["materials"]["automation"] = automation_material()
    if lock == "exact":
        blueprint["materials"]["automation_locks"] = [exact_value_lock()]
    elif lock == "presence":
        blueprint["materials"]["automation_locks"] = [presence_lock()]
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def candidate(parent: dict, operations: list[dict], *, candidate_id: str = "AEC-M7-R1-001") -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_automation_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
            "automation_material_sha256": automation_material_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "m7-r1-test"},
        "reason": "M7-R1 automation edit test.",
        "operations": operations,
        "preview_only": True,
    }


def point_target(point_id: str = "AP-GAIN-001", lane_id: str = "A-GAIN") -> dict:
    return {"lane_id": lane_id, "point_id": point_id}


def lane_target(lane_id: str = "A-GAIN") -> dict:
    return {"lane_id": lane_id}


def point_by_id(blueprint: dict, point_id: str) -> dict:
    lane = blueprint["materials"]["automation"]["lanes"][0]
    return next(point for point in lane["points"] if point["point_id"] == point_id)


def test_legacy_blueprint_remains_valid_without_fabricated_automation() -> None:
    legacy = _load(BLUEPRINT_PATH)
    original = copy.deepcopy(legacy)
    validate_contract(legacy, "music-blueprint-v0.schema.json")
    assert legacy == original
    assert "automation" not in legacy["materials"]
    assert automation_material_from_blueprint(legacy) == empty_automation_material()
    assert automation_material_sha256(legacy) == automation_material_sha256(copy.deepcopy(legacy))


def test_blueprint_optional_automation_validates_and_is_canonical() -> None:
    blueprint = automation_blueprint()
    material = blueprint["materials"]["automation"]
    assert [lane["lane_id"] for lane in material["lanes"]] == ["A-GAIN"]
    assert [point["point_id"] for point in material["lanes"][0]["points"]] == [
        "AP-GAIN-001",
        "AP-GAIN-002",
    ]


def test_blueprint_automation_rejects_unknown_part_and_out_of_duration_point() -> None:
    unknown = automation_blueprint()
    lane = unknown["materials"]["automation"]["lanes"][0]
    lane["target"]["scope"] = "part"
    lane["target"]["owner_id"] = "P-NOT-THERE"
    with pytest.raises(ContractError, match="unknown part_id"):
        validate_contract(unknown, "music-blueprint-v0.schema.json")

    outside = automation_blueprint()
    outside["materials"]["automation"]["lanes"][0]["points"][1]["beat"] = 1000.0
    with pytest.raises(ContractError, match="exceeds project duration"):
        validate_contract(outside, "music-blueprint-v0.schema.json")


@pytest.mark.parametrize(
    "operation,point_id,field,value",
    [
        (
            {
                "operation_id": "OP-INSERT",
                "op": "INSERT_POINT",
                "target": lane_target(),
                "point": {
                    "point_id": "AP-GAIN-003",
                    "beat": 4.0,
                    "value": -4.0,
                    "interpolation": "linear",
                },
            },
            "AP-GAIN-003",
            "value",
            -4.0,
        ),
        (
            {"operation_id": "OP-DELETE", "op": "DELETE_POINT", "target": point_target()},
            "AP-GAIN-001",
            "deleted",
            True,
        ),
        (
            {"operation_id": "OP-MOVE", "op": "MOVE_POINT", "target": point_target(), "beat": 2.0},
            "AP-GAIN-001",
            "beat",
            2.0,
        ),
        (
            {"operation_id": "OP-VALUE", "op": "SET_VALUE", "target": point_target(), "value": -5.0},
            "AP-GAIN-001",
            "value",
            -5.0,
        ),
        (
            {
                "operation_id": "OP-INTERP",
                "op": "SET_INTERPOLATION",
                "target": point_target(),
                "interpolation": "hold",
            },
            "AP-GAIN-001",
            "interpolation",
            "hold",
        ),
    ],
)
def test_all_five_r0_primitives_build_ready_preview(
    operation: dict, point_id: str, field: str, value: object
) -> None:
    parent = automation_blueprint()
    preview = build_automation_edit_preview(parent, candidate(parent, [operation]))
    assert preview.ready is True
    assert preview.blueprint is not None
    assert preview.authority_result["project_mutation_authorized"] is False
    assert preview.authority_result["music_ir_mutation_authorized"] is False
    if field == "deleted":
        ids = [
            point["point_id"]
            for point in preview.blueprint["materials"]["automation"]["lanes"][0]["points"]
        ]
        assert point_id not in ids
    else:
        assert point_by_id(preview.blueprint, point_id)[field] == value
    assert preview.changed_lane_ids == ["A-GAIN"]
    assert point_id in preview.changed_point_ids


@pytest.mark.parametrize(
    "source_field",
    ["project_id", "revision_id", "blueprint_sha256", "automation_material_sha256"],
)
def test_stale_source_binding_fails_closed(source_field: str) -> None:
    parent = automation_blueprint()
    edit = candidate(
        parent,
        [{"operation_id": "OP-VALUE", "op": "SET_VALUE", "target": point_target(), "value": -5.0}],
    )
    edit["source"][source_field] = (
        "0" * 64 if source_field.endswith("sha256") else "stale"
    )
    preview = build_automation_edit_preview(parent, edit)
    assert preview.ready is False
    assert preview.blueprint is None
    assert preview.authority_result["conflicts"][0]["code"] == "STALE_SOURCE"


def test_unknown_lane_and_point_fail_closed() -> None:
    parent = automation_blueprint()
    unknown_lane = candidate(
        parent,
        [{"operation_id": "OP-LANE", "op": "SET_VALUE", "target": point_target(lane_id="A-NOPE"), "value": -5.0}],
    )
    preview = build_automation_edit_preview(parent, unknown_lane)
    assert preview.authority_result["conflicts"][0]["code"] == "UNKNOWN_LANE"

    unknown_point = candidate(
        parent,
        [{"operation_id": "OP-POINT", "op": "SET_VALUE", "target": point_target("AP-NOPE"), "value": -5.0}],
    )
    preview = build_automation_edit_preview(parent, unknown_point)
    assert preview.authority_result["conflicts"][0]["code"] == "UNKNOWN_POINT"


def test_duplicate_id_occupied_beat_and_out_of_range_fail_closed() -> None:
    parent = automation_blueprint()
    duplicate = candidate(
        parent,
        [
            {
                "operation_id": "OP-DUP-ID",
                "op": "INSERT_POINT",
                "target": lane_target(),
                "point": {
                    "point_id": "AP-GAIN-001",
                    "beat": 4.0,
                    "value": -4.0,
                    "interpolation": "linear",
                },
            }
        ],
    )
    assert build_automation_edit_preview(parent, duplicate).authority_result["conflicts"][0]["code"] == "UNREPRESENTABLE_EDIT"

    occupied = candidate(
        parent,
        [{"operation_id": "OP-BEAT", "op": "MOVE_POINT", "target": point_target(), "beat": 8.0}],
    )
    assert build_automation_edit_preview(parent, occupied).authority_result["conflicts"][0]["code"] == "INVALID_TIME"

    out_of_range = candidate(
        parent,
        [{"operation_id": "OP-RANGE", "op": "SET_VALUE", "target": point_target(), "value": 7.0}],
    )
    assert build_automation_edit_preview(parent, out_of_range).authority_result["conflicts"][0]["code"] == "INVALID_VALUE"


def test_unsupported_interpolation_is_schema_rejected() -> None:
    parent = automation_blueprint()
    edit = candidate(
        parent,
        [
            {
                "operation_id": "OP-BEZIER",
                "op": "SET_INTERPOLATION",
                "target": point_target(),
                "interpolation": "bezier",
            }
        ],
    )
    with pytest.raises(ContractError, match="schema validation failed"):
        build_automation_edit_preview(parent, edit)


def test_hard_exact_value_lock_blocks_with_typed_conflict() -> None:
    parent = automation_blueprint(lock="exact")
    edit = candidate(
        parent,
        [{"operation_id": "OP-LOCK", "op": "SET_VALUE", "target": point_target(), "value": -5.0}],
    )
    preview = build_automation_edit_preview(parent, edit)
    assert preview.ready is False
    conflict = preview.authority_result["conflicts"][0]
    assert conflict["code"] == "HARD_LOCK_VIOLATION"
    assert conflict["rule_id"] == "L-AUTO-GAIN-VALUE"


def test_hard_presence_lock_blocks_delete_with_typed_conflict() -> None:
    parent = automation_blueprint(lock="presence")
    edit = candidate(
        parent,
        [{"operation_id": "OP-DELETE", "op": "DELETE_POINT", "target": point_target()}],
    )
    preview = build_automation_edit_preview(parent, edit)
    assert preview.ready is False
    conflict = preview.authority_result["conflicts"][0]
    assert conflict["code"] == "HARD_LOCK_VIOLATION"
    assert conflict["rule_id"] == "L-AUTO-GAIN-PRESENCE"


def test_validate_revision_and_direct_m2_commit_cannot_bypass_hard_automation_lock(tmp_path: Path) -> None:
    parent = automation_blueprint(lock="exact")
    direct = clone_for_revision(parent, "rev-direct-auto-lock-bypass")
    point_by_id(direct, "AP-GAIN-001")["value"] = -5.0
    conflicts = validate_revision(parent, direct)
    assert any(item.rule_type == "automation_lock" and item.status == "BLOCKED" for item in conflicts)

    project = create_project(tmp_path / "auto-locked.musica", parent)
    with pytest.raises(ContractError, match="revision commit blocked"):
        project.commit_revision(direct)
    assert project.head_revision_id() == parent["project"]["revision_id"]


def test_preview_is_side_effect_free_and_explicit_accept_advances_once(tmp_path: Path) -> None:
    parent = automation_blueprint()
    project = create_project(tmp_path / "automation-edit.musica", parent)
    root_id = project.head_revision_id()
    edit = candidate(
        parent,
        [{"operation_id": "OP-ACCEPT", "op": "SET_VALUE", "target": point_target(), "value": -5.0}],
    )
    preview = build_automation_edit_preview(parent, edit)
    assert preview.ready is True
    assert project.head_revision_id() == root_id
    assert project.read_revision(root_id) == parent

    record = accept_automation_edit_preview(project, preview)
    assert preview.blueprint is not None
    assert record["revision_id"] == preview.blueprint["project"]["revision_id"]
    assert project.head_revision_id() == record["revision_id"]
    accepted = project.read_revision(record["revision_id"])
    assert point_by_id(accepted, "AP-GAIN-001")["value"] == -5.0

    with pytest.raises(ContractError, match="already exists"):
        accept_automation_edit_preview(project, preview)


def test_legacy_empty_material_source_binding_cannot_fabricate_lane() -> None:
    parent = _load(BLUEPRINT_PATH)
    edit = candidate(
        parent,
        [{"operation_id": "OP-NO-LANE", "op": "SET_VALUE", "target": point_target(), "value": -5.0}],
    )
    preview = build_automation_edit_preview(parent, edit)
    assert preview.ready is False
    assert preview.blueprint is None
    assert preview.authority_result["conflicts"][0]["code"] == "UNKNOWN_LANE"
    assert "automation" not in parent["materials"]


def test_material_hash_is_deterministic_and_not_array_identity() -> None:
    parent = automation_blueprint()
    first = automation_material_sha256(parent)
    second = automation_material_sha256(copy.deepcopy(parent))
    assert first == second
    assert len(first) == 64
    assert canonical_json_bytes(parent["materials"]["automation"]) == canonical_json_bytes(
        copy.deepcopy(parent["materials"]["automation"])
    )
