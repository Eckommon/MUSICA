from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from musica.automation_edit import automation_material_sha256, blueprint_sha256
from musica.automation_lowering import (
    AUTOMATION_EXECUTION_PPQ,
    beat_to_tick,
    lower_automation_execution,
    validate_automation_execution,
)
from musica.compiler import compile_blueprint
from musica.contracts import ContractError, validate_contract
from musica.evidence import canonical_json_bytes

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _blueprint(*, automation: bool = True, third_point: bool = True) -> dict:
    blueprint = _load(BLUEPRINT_PATH)
    if automation:
        material = _load(AUTOMATION_PATH)
        cutoff = next(lane for lane in material["lanes"] if lane["lane_id"] == "B-SYNTH-CUTOFF")
        cutoff["section_id"] = "S01"
        if third_point:
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


def test_legacy_lowering_is_explicit_empty_and_does_not_reverse_infer() -> None:
    blueprint = _blueprint(automation=False)
    before = canonical_json_bytes(blueprint)

    execution = lower_automation_execution(blueprint)

    assert execution["classification"] == "derived_noncanonical"
    assert execution["source"]["explicit_automation_present"] is False
    assert execution["source"]["blueprint_sha256"] == blueprint_sha256(blueprint)
    assert execution["source"]["automation_material_sha256"] == automation_material_sha256(blueprint)
    assert execution["lanes"] == []
    assert execution["unsupported"] == []
    assert execution["authority"] == {
        "canonical": False,
        "project_mutation_authorized": False,
        "blueprint_mutation_authorized": False,
        "reverse_promotion_authorized": False,
        "renderer_mapping_authorized": False,
        "audible_automation_validated": False,
    }
    assert canonical_json_bytes(blueprint) == before


def test_explicit_automation_lowers_with_exact_source_binding_and_unmapped_backend() -> None:
    blueprint = _blueprint()
    execution = lower_automation_execution(blueprint)

    assert execution["source"] == {
        "project_id": blueprint["project"]["project_id"],
        "revision_id": blueprint["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(blueprint),
        "automation_material_sha256": automation_material_sha256(blueprint),
        "explicit_automation_present": True,
    }
    assert execution["lowering"]["ppq"] == AUTOMATION_EXECUTION_PPQ
    assert [lane["lane_id"] for lane in execution["lanes"]] == ["A-MIX-GAIN", "B-SYNTH-CUTOFF"]
    assert all(lane["derivation_status"] == "DERIVED_GENERIC" for lane in execution["lanes"])
    assert all(lane["backend_mapping"] == {"status": "UNMAPPED"} for lane in execution["lanes"])

    gain = execution["lanes"][0]
    assert gain["parameter_id"] == "mix.gain"
    assert gain["scope"] == "project"
    assert gain["owner_id"] is None
    assert gain["unit"] == "normalized"
    assert [point["point_id"] for point in gain["points"]] == [
        "P-GAIN-001",
        "P-GAIN-002",
        "P-GAIN-003",
    ]
    assert [point["tick"] for point in gain["points"]] == [0, 3840, 5760]


def test_hold_and_linear_segments_preserve_start_point_semantics() -> None:
    execution = lower_automation_execution(_blueprint())
    gain = execution["lanes"][0]

    assert gain["segments"] == [
        {
            "start_point_id": "P-GAIN-001",
            "end_point_id": "P-GAIN-002",
            "start_tick": 0,
            "end_tick": 3840,
            "start_value": 0.65,
            "end_value": 0.82,
            "interpolation": "linear",
        },
        {
            "start_point_id": "P-GAIN-002",
            "end_point_id": "P-GAIN-003",
            "start_tick": 3840,
            "end_tick": 5760,
            "start_value": 0.82,
            "end_value": 0.75,
            "interpolation": "hold",
        },
    ]


def test_beat_to_tick_uses_explicit_decimal_half_up_policy() -> None:
    assert beat_to_tick(0) == 0
    assert beat_to_tick(1) == 480
    assert beat_to_tick("0.001041666666666666666666666667") == 1
    assert beat_to_tick("0.003125") == 2  # 1.5 ticks -> 2, not bankers rounding.
    with pytest.raises(ContractError, match="cannot be negative"):
        beat_to_tick(-0.1)


def test_distinct_beats_that_quantize_to_same_tick_fail_closed() -> None:
    blueprint = _blueprint(third_point=False)
    gain = blueprint["materials"]["automation"]["lanes"][0]
    gain["points"].insert(
        1,
        {
            "point_id": "P-GAIN-SUBTICK",
            "beat": 0.0001,
            "value": 0.7,
            "interpolation": "hold",
        },
    )
    validate_contract(blueprint, "music-blueprint-v0.schema.json")

    with pytest.raises(ContractError, match="collapse"):
        lower_automation_execution(blueprint)


def test_lowering_is_byte_deterministic_and_input_is_not_mutated() -> None:
    blueprint = _blueprint()
    source_before = canonical_json_bytes(blueprint)

    first = lower_automation_execution(blueprint)
    second = lower_automation_execution(blueprint)

    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert canonical_json_bytes(blueprint) == source_before


def test_reordered_canonical_points_are_rejected_not_silently_normalized() -> None:
    blueprint = _blueprint()
    gain = blueprint["materials"]["automation"]["lanes"][0]
    gain["points"] = list(reversed(gain["points"]))

    with pytest.raises(ContractError, match="canonical order"):
        lower_automation_execution(blueprint)


def test_invalid_blueprint_ownership_fails_before_lowering() -> None:
    blueprint = _blueprint()
    cutoff = blueprint["materials"]["automation"]["lanes"][1]
    cutoff["section_id"] = "S-DOES-NOT-EXIST"

    with pytest.raises(ContractError, match="unknown section_id"):
        lower_automation_execution(blueprint)


def test_execution_schema_forbids_backend_address_authority() -> None:
    execution = lower_automation_execution(_blueprint())
    execution["lanes"][0]["backend_mapping"]["midi_cc"] = 11

    with pytest.raises(ContractError, match="Additional properties"):
        validate_automation_execution(execution)


def test_execution_cross_fields_fail_closed_on_segment_tamper() -> None:
    execution = lower_automation_execution(_blueprint())
    execution["lanes"][0]["segments"][0]["interpolation"] = "hold"

    with pytest.raises(ContractError, match="does not match source points"):
        validate_automation_execution(execution)


def test_lowering_does_not_change_existing_music_ir_compiler_output() -> None:
    blueprint = _blueprint()
    ir_before = compile_blueprint(copy.deepcopy(blueprint))
    source_before = canonical_json_bytes(blueprint)

    lower_automation_execution(blueprint)
    ir_after = compile_blueprint(copy.deepcopy(blueprint))

    assert canonical_json_bytes(ir_before) == canonical_json_bytes(ir_after)
    assert canonical_json_bytes(blueprint) == source_before
    # R3 does not inject canonical automation into the existing MIDI-like control path.
    assert all(
        event.get("controller") in {11, 71, 74}
        for track in ir_after["tracks"]
        for event in track["events"]
        if event["type"] == "control"
    )
