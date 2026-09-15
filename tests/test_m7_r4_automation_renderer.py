from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest

from musica.automation_lowering import lower_automation_execution
from musica.automation_renderer import (
    automation_wav_bytes,
    build_automation_render_plan,
    gain_at_tick,
    validate_automation_render_plan,
)
from musica.compiler import compile_blueprint
from musica.contracts import ContractError, validate_contract
from musica.evidence import canonical_json_bytes
from musica.render import midi_bytes, wav_bytes

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _explicit_blueprint() -> dict:
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


def _stack() -> tuple[dict, dict, dict]:
    blueprint = _explicit_blueprint()
    music_ir = compile_blueprint(copy.deepcopy(blueprint))
    execution = lower_automation_execution(copy.deepcopy(blueprint))
    return blueprint, music_ir, execution


def test_r4_plan_maps_only_project_normalized_mix_gain() -> None:
    _, music_ir, execution = _stack()
    plan = build_automation_render_plan(music_ir, execution)

    assert plan["classification"] == "derived_noncanonical"
    assert plan["renderer"]["renderer_id"] == "musica-reference-local"
    assert plan["mapping"]["policy_id"] == "reference-renderer-mix-gain-v0"
    assert len(plan["mapped_lanes"]) == 1
    mapped = plan["mapped_lanes"][0]
    assert mapped["lane_id"] == "A-MIX-GAIN"
    assert mapped["parameter_id"] == "mix.gain"
    assert mapped["scope"] == "project"
    assert mapped["unit"] == "normalized"
    assert mapped["mapping_id"] == "reference.mix_gain.normalized"

    assert [item["lane_id"] for item in plan["unmapped_lanes"]] == ["B-SYNTH-CUTOFF"]
    assert plan["unmapped_lanes"][0]["code"] == "UNSUPPORTED_PARAMETER"
    assert plan["authority"]["canonical"] is False
    assert plan["authority"]["midi_cc_semantics_authorized"] is False
    assert plan["authority"]["reverse_promotion_authorized"] is False
    assert plan["authority"]["renderer_application_authorized"] is True


def test_r4_gain_envelope_preserves_linear_hold_and_boundaries() -> None:
    _, music_ir, execution = _stack()
    plan = build_automation_render_plan(music_ir, execution)

    assert gain_at_tick(plan, 0) == Decimal("0.65")
    assert gain_at_tick(plan, 1920) == Decimal("0.735")
    assert gain_at_tick(plan, 3840) == Decimal("0.82")
    assert gain_at_tick(plan, 5000) == Decimal("0.82")
    assert gain_at_tick(plan, 5760) == Decimal("0.75")
    assert gain_at_tick(plan, 999999) == Decimal("0.75")
    with pytest.raises(ContractError, match="cannot be negative"):
        gain_at_tick(plan, -1)


def test_r4_scope_and_unit_are_not_guessed_into_mapping() -> None:
    blueprint = _explicit_blueprint()
    gain = next(lane for lane in blueprint["materials"]["automation"]["lanes"] if lane["lane_id"] == "A-MIX-GAIN")
    gain["target"]["scope"] = "part"
    gain["target"]["owner_id"] = blueprint["roles"]["instruments_or_parts"][0]["part_id"]
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    ir = compile_blueprint(copy.deepcopy(blueprint))
    execution = lower_automation_execution(copy.deepcopy(blueprint))
    plan = build_automation_render_plan(ir, execution)
    gain_unmapped = next(item for item in plan["unmapped_lanes"] if item["lane_id"] == "A-MIX-GAIN")
    assert gain_unmapped["code"] == "UNSUPPORTED_SCOPE"
    assert plan["mapped_lanes"] == []

    blueprint = _explicit_blueprint()
    gain = next(lane for lane in blueprint["materials"]["automation"]["lanes"] if lane["lane_id"] == "A-MIX-GAIN")
    gain["target"]["unit"] = "decibel"
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    ir = compile_blueprint(copy.deepcopy(blueprint))
    execution = lower_automation_execution(copy.deepcopy(blueprint))
    plan = build_automation_render_plan(ir, execution)
    gain_unmapped = next(item for item in plan["unmapped_lanes"] if item["lane_id"] == "A-MIX-GAIN")
    assert gain_unmapped["code"] == "UNSUPPORTED_UNIT"
    assert plan["mapped_lanes"] == []


def test_r4_cross_source_and_tamper_checks_fail_closed() -> None:
    _, music_ir, execution = _stack()

    wrong_revision = copy.deepcopy(music_ir)
    wrong_revision["source_blueprint_revision"] = "rev-other"
    with pytest.raises(ContractError, match="source revision"):
        build_automation_render_plan(wrong_revision, execution)

    wrong_ppq = copy.deepcopy(music_ir)
    wrong_ppq["timing"]["ppq"] = 960
    with pytest.raises(ContractError, match="PPQ"):
        build_automation_render_plan(wrong_ppq, execution)

    tampered_execution = copy.deepcopy(execution)
    tampered_execution["lanes"][0]["points"][0]["value"] = 0.91
    with pytest.raises(ContractError):
        build_automation_render_plan(music_ir, tampered_execution)

    plan = build_automation_render_plan(music_ir, execution)
    tampered_plan = copy.deepcopy(plan)
    tampered_plan["source"]["music_ir_sha256"] = "0" * 64
    with pytest.raises(ContractError, match="does not exactly match"):
        validate_automation_render_plan(tampered_plan, music_ir, execution)


def test_r4_audio_is_deterministic_different_and_non_mutating() -> None:
    _, music_ir, execution = _stack()
    music_ir_before = canonical_json_bytes(music_ir)
    execution_before = canonical_json_bytes(execution)
    midi_before = midi_bytes(music_ir)
    baseline = wav_bytes(music_ir, duration_seconds=2.0)

    automated_a = automation_wav_bytes(music_ir, execution, duration_seconds=2.0)
    automated_b = automation_wav_bytes(music_ir, execution, duration_seconds=2.0)

    assert automated_a == automated_b
    assert automated_a != baseline
    assert canonical_json_bytes(music_ir) == music_ir_before
    assert canonical_json_bytes(execution) == execution_before
    assert midi_bytes(music_ir) == midi_before
    assert wav_bytes(music_ir, duration_seconds=2.0) == baseline


def test_r4_legacy_no_automation_is_baseline_equivalent() -> None:
    blueprint = _load(BLUEPRINT_PATH)
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    music_ir = compile_blueprint(copy.deepcopy(blueprint))
    execution = lower_automation_execution(copy.deepcopy(blueprint))
    plan = build_automation_render_plan(music_ir, execution)

    assert execution["source"]["explicit_automation_present"] is False
    assert plan["mapped_lanes"] == []
    assert plan["unmapped_lanes"] == []
    baseline = wav_bytes(music_ir, duration_seconds=2.0)
    assert automation_wav_bytes(music_ir, execution, duration_seconds=2.0) == baseline
