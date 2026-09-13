from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from musica.automation_contracts import validate_automation_lock, validate_automation_material
from musica.contracts import ContractError, validate_contract

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "examples" / "automation" / "valid"
INVALID = ROOT / "examples" / "automation" / "invalid"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def material() -> dict:
    return load(VALID / "automation-material-v0.json")


def candidate() -> dict:
    return load(VALID / "automation-edit-candidate-v0.json")


def lock() -> dict:
    return load(VALID / "automation-lock-v0.json")


def test_valid_m7_r0_fixtures_validate():
    validate_automation_material(material())
    validate_contract(candidate(), "automation-edit-candidate-v0.schema.json")
    validate_automation_lock(lock(), material())
    validate_contract(
        load(VALID / "automation-authority-ready-v0.json"),
        "automation-authority-result-v0.schema.json",
    )
    validate_contract(
        load(VALID / "automation-authority-blocked-v0.json"),
        "automation-authority-result-v0.schema.json",
    )


def test_invalid_fixture_duplicate_beat_fails_cross_field_contract():
    with pytest.raises(ContractError, match="point beats must be unique"):
        validate_automation_material(load(INVALID / "duplicate-beat-material-v0.json"))


def test_invalid_fixture_point_operation_without_point_id_fails_schema():
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_contract(
            load(INVALID / "missing-point-target-candidate-v0.json"),
            "automation-edit-candidate-v0.schema.json",
        )


def test_track_scope_is_not_canonical_in_m7_r0():
    value = material()
    value["lanes"][1]["target"]["scope"] = "track"
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_automation_material(value)


def test_project_scope_requires_null_owner():
    value = material()
    value["lanes"][0]["target"]["owner_id"] = "T-DERIVED"
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_automation_material(value)


def test_parameter_namespace_and_interpolation_are_bounded():
    bad_parameter = material()
    bad_parameter["lanes"][0]["target"]["parameter_id"] = "VST#17"
    with pytest.raises(ContractError):
        validate_automation_material(bad_parameter)

    bad_curve = material()
    bad_curve["lanes"][0]["points"][0]["interpolation"] = "bezier"
    with pytest.raises(ContractError):
        validate_automation_material(bad_curve)


def test_lane_ids_and_global_point_ids_must_be_unique():
    duplicate_lane = material()
    duplicate_lane["lanes"][1]["lane_id"] = duplicate_lane["lanes"][0]["lane_id"]
    with pytest.raises(ContractError, match="lane_id must be unique"):
        validate_automation_material(duplicate_lane)

    duplicate_point = material()
    duplicate_point["lanes"][1]["points"][0]["point_id"] = "P-GAIN-001"
    with pytest.raises(ContractError, match="point_id across material must be unique"):
        validate_automation_material(duplicate_point)


def test_lane_target_signatures_must_be_unique():
    value = material()
    duplicate = copy.deepcopy(value["lanes"][0])
    duplicate["lane_id"] = "A2-MIX-GAIN"
    duplicate["points"][0]["point_id"] = "P-GAIN-X01"
    duplicate["points"][1]["point_id"] = "P-GAIN-X02"
    value["lanes"].insert(1, duplicate)
    with pytest.raises(ContractError, match="target signatures must be unique"):
        validate_automation_material(value)


def test_lanes_and_points_require_canonical_order():
    lanes = material()
    lanes["lanes"] = list(reversed(lanes["lanes"]))
    with pytest.raises(ContractError, match="canonical order by lane_id"):
        validate_automation_material(lanes)

    points = material()
    points["lanes"][0]["points"] = list(reversed(points["lanes"][0]["points"]))
    with pytest.raises(ContractError, match="canonical order \(beat, point_id\)"):
        validate_automation_material(points)


def test_lane_bounds_and_point_values_fail_closed():
    inverted = material()
    inverted["lanes"][0]["target"]["minimum"] = 1.0
    inverted["lanes"][0]["target"]["maximum"] = 1.0
    with pytest.raises(ContractError, match="minimum must be less than maximum"):
        validate_automation_material(inverted)

    out_of_range = material()
    out_of_range["lanes"][0]["points"][0]["value"] = 1.2
    with pytest.raises(ContractError, match="outside lane range"):
        validate_automation_material(out_of_range)


def test_all_five_m7_r0_primitive_operation_shapes_are_typed():
    base = candidate()
    operations = [
        {
            "operation_id": "OP-INSERT",
            "op": "INSERT_POINT",
            "target": {"lane_id": "A-MIX-GAIN"},
            "point": {
                "point_id": "P-GAIN-003",
                "beat": 12.0,
                "value": 0.7,
                "interpolation": "hold",
            },
        },
        {
            "operation_id": "OP-DELETE",
            "op": "DELETE_POINT",
            "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-002"},
        },
        {
            "operation_id": "OP-MOVE",
            "op": "MOVE_POINT",
            "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-002"},
            "beat": 9.0,
        },
        {
            "operation_id": "OP-VALUE",
            "op": "SET_VALUE",
            "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-002"},
            "value": 0.75,
        },
        {
            "operation_id": "OP-INTERPOLATION",
            "op": "SET_INTERPOLATION",
            "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-002"},
            "interpolation": "linear",
        },
    ]
    for operation in operations:
        value = copy.deepcopy(base)
        value["operations"] = [operation]
        validate_contract(value, "automation-edit-candidate-v0.schema.json")


def test_candidate_is_always_noncanonical_and_source_bound():
    value = candidate()
    value["preview_only"] = False
    with pytest.raises(ContractError):
        validate_contract(value, "automation-edit-candidate-v0.schema.json")

    value = candidate()
    value["source"]["blueprint_sha256"] = "not-a-hash"
    with pytest.raises(ContractError):
        validate_contract(value, "automation-edit-candidate-v0.schema.json")


def test_automation_lock_mode_payloads_are_disjoint():
    value = lock()
    value["minimum"] = 700.0
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_automation_lock(value, material())

    value = lock()
    value["mode"] = "range"
    value.pop("value")
    value["minimum"] = 900.0
    value["maximum"] = 700.0
    with pytest.raises(ContractError, match="minimum exceeds maximum"):
        validate_automation_lock(value, material())


def test_automation_lock_references_are_stable_and_fail_closed():
    unknown_lane = lock()
    unknown_lane["selector"]["lane_id"] = "NO-SUCH-LANE"
    with pytest.raises(ContractError, match="unknown lane_id"):
        validate_automation_lock(unknown_lane, material())

    unknown_point = lock()
    unknown_point["selector"]["point_id"] = "NO-SUCH-POINT"
    with pytest.raises(ContractError, match="unknown point_id"):
        validate_automation_lock(unknown_point, material())

    mismatched_parameter = lock()
    mismatched_parameter["selector"]["parameter_id"] = "mix.gain"
    with pytest.raises(ContractError, match="parameter_id does not match"):
        validate_automation_lock(mismatched_parameter, material())


def test_presence_lock_is_reserved_for_lane_or_point_identity():
    value = lock()
    value["mode"] = "presence"
    value.pop("value")
    with pytest.raises(ContractError, match="presence lock supports only lane or point"):
        validate_automation_lock(value, material())


def test_authority_result_state_machine_is_fail_closed():
    ready = load(VALID / "automation-authority-ready-v0.json")
    ready["conflicts"] = [
        {
            "conflict_id": "C-BAD",
            "code": "STALE_SOURCE",
            "reason": "contradictory READY fixture",
        }
    ]
    with pytest.raises(ContractError):
        validate_contract(ready, "automation-authority-result-v0.schema.json")

    blocked = load(VALID / "automation-authority-blocked-v0.json")
    blocked["preview_generation_allowed"] = True
    with pytest.raises(ContractError):
        validate_contract(blocked, "automation-authority-result-v0.schema.json")


def test_authority_result_never_authorizes_direct_mutation():
    ready = load(VALID / "automation-authority-ready-v0.json")
    ready["project_mutation_authorized"] = True
    with pytest.raises(ContractError):
        validate_contract(ready, "automation-authority-result-v0.schema.json")

    ready = load(VALID / "automation-authority-ready-v0.json")
    ready["music_ir_mutation_authorized"] = True
    with pytest.raises(ContractError):
        validate_contract(ready, "automation-authority-result-v0.schema.json")
