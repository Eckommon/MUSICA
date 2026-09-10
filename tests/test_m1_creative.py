from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from musica.compiler import compile_blueprint
from musica.contracts import ContractError, validate_contract, validate_revision
from musica.creative import compose_blueprint, plan_intent
from musica.m1_demo import run_suite
from musica.render import midi_bytes, wav_bytes
from musica.semantic import M1_SEMANTIC_AXES, apply_semantic_control

ROOT = Path(__file__).resolve().parents[1]
INTENT_DIR = ROOT / "examples" / "intents"
INTENT_PATHS = [
    INTENT_DIR / "dark-electronic-12s.json",
    INTENT_DIR / "warm-ambient-12s.json",
    INTENT_DIR / "kinetic-minimal-12s.json",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def track(ir: dict, track_id: str) -> dict:
    return next(item for item in ir["tracks"] if item["track_id"] == track_id)


def final_scope(blueprint: dict) -> str:
    section = blueprint["form"]["sections"][-1]
    return f"time:{float(section['start']):g}-{float(section['end']):g}"


def semantic_control(axis: str, blueprint: dict) -> dict:
    return {
        "control_id": f"TEST-{axis.upper()}",
        "name": axis,
        "operation": "set",
        "value": 0.90,
        "scope": final_scope(blueprint),
        "confidence": 1.0,
        "source": "user_control",
        "phrase": f"Set final section {axis} to 0.90.",
        "interpretation_notes": [],
        "protected_targets": [
            "/musical_context/tempo/bpm",
            "/materials/melody/main_motif_id",
            "/materials/rhythm/drum_pattern_id",
        ],
    }


def test_music_intent_contract_and_composer_are_deterministic():
    intent = load(INTENT_PATHS[0])
    validate_contract(intent, "music-intent-v0.schema.json")

    plan_a = plan_intent(intent)
    plan_b = plan_intent(copy.deepcopy(intent))
    blueprint_a = compose_blueprint(intent)
    blueprint_b = compose_blueprint(copy.deepcopy(intent))

    assert plan_a == plan_b
    assert blueprint_a == blueprint_b
    assert midi_bytes(compile_blueprint(blueprint_a)) == midi_bytes(compile_blueprint(blueprint_b))


def test_seed_changes_generated_material_without_changing_contract_shape():
    intent_a = load(INTENT_PATHS[0])
    intent_b = copy.deepcopy(intent_a)
    intent_b["seed"] += 1

    blueprint_a = compose_blueprint(intent_a)
    blueprint_b = compose_blueprint(intent_b)

    assert blueprint_a["materials"]["melody"]["main_motif_id"] != blueprint_b["materials"]["melody"]["main_motif_id"]
    assert blueprint_a["materials"]["melody"]["motif_notes"] != blueprint_b["materials"]["melody"]["motif_notes"]
    assert set(blueprint_a) == set(blueprint_b)


def test_three_profiles_are_materially_distinct_and_render_distinct_midi():
    blueprints = [compose_blueprint(load(path)) for path in INTENT_PATHS]
    tempos = {bp["musical_context"]["tempo"]["bpm"] for bp in blueprints}
    characters = {tuple(bp["materials"]["sound_design"]["character"]) for bp in blueprints}
    programs = {
        (
            bp["materials"]["sound_design"]["motif_program"],
            bp["materials"]["sound_design"]["bass_program"],
        )
        for bp in blueprints
    }
    midi_hashes = {sha256_bytes(midi_bytes(compile_blueprint(bp))) for bp in blueprints}

    assert len(tempos) == 3
    assert len(characters) == 3
    assert len(programs) == 3
    assert len(midi_hashes) == 3


@pytest.mark.parametrize("axis", M1_SEMANTIC_AXES)
def test_all_six_semantic_axes_are_lock_aware_and_change_executable_output(axis: str):
    parent = compose_blueprint(load(INTENT_PATHS[0]))
    control = semantic_control(axis, parent)
    candidate, diff = apply_semantic_control(parent, control, revision_id=f"rev-{axis}")

    assert not [conflict for conflict in validate_revision(parent, candidate) if conflict.status == "BLOCKED"]
    assert candidate["musical_context"]["tempo"]["bpm"] == parent["musical_context"]["tempo"]["bpm"]
    assert candidate["materials"]["melody"]["main_motif_id"] == parent["materials"]["melody"]["main_motif_id"]
    assert candidate["materials"]["rhythm"]["drum_pattern_id"] == parent["materials"]["rhythm"]["drum_pattern_id"]
    assert diff
    assert candidate["provenance"]["selected_mechanisms"]

    parent_ir = compile_blueprint(parent)
    candidate_ir = compile_blueprint(candidate)
    parent_midi = midi_bytes(parent_ir)
    candidate_midi = midi_bytes(candidate_ir)
    parent_wav = wav_bytes(parent_ir, duration_seconds=12.0, sample_rate=8000)
    candidate_wav = wav_bytes(candidate_ir, duration_seconds=12.0, sample_rate=8000)

    assert parent_midi != candidate_midi, axis
    assert parent_wav != candidate_wav, axis


def test_tension_edit_preserves_motif_and_drums_while_changing_support_activity():
    parent = compose_blueprint(load(INTENT_PATHS[0]))
    candidate, _ = apply_semantic_control(parent, semantic_control("tension", parent))
    ir1 = compile_blueprint(parent)
    ir2 = compile_blueprint(candidate)

    assert track(ir1, "T-MOTIF")["events"] == track(ir2, "T-MOTIF")["events"]
    assert track(ir1, "T-DRUMS")["events"] == track(ir2, "T-DRUMS")["events"]
    assert len(track(ir2, "T-BASS")["events"]) > len(track(ir1, "T-BASS")["events"])


def test_future_semantic_vocabulary_fails_closed_until_implemented():
    parent = compose_blueprint(load(INTENT_PATHS[0]))
    control = semantic_control("energy", parent)
    control["name"] = "roughness"
    with pytest.raises(ContractError, match="supports only energy, tension, density, motion, brightness, warmth"):
        apply_semantic_control(parent, control)


def test_m1_evidence_suite_is_reproducible_and_profile_outputs_are_distinct(tmp_path: Path):
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    manifest_a = run_suite(INTENT_PATHS, out_a)
    manifest_b = run_suite(INTENT_PATHS, out_b)

    assert manifest_a == manifest_b
    assert manifest_a["creative_contract"]["semantic_axes"] == list(M1_SEMANTIC_AXES)
    assert len(manifest_a["cases"]) == 3
    assert len(manifest_a["semantic_probes"]) == 6

    base_midis = {
        record["sha256"]
        for record in manifest_a["artifacts"]
        if record["path"].startswith("cases/") and record["path"].endswith("preview.mid")
    }
    base_wavs = {
        record["sha256"]
        for record in manifest_a["artifacts"]
        if record["path"].startswith("cases/") and record["path"].endswith("preview.wav")
    }
    semantic_midis = {
        record["sha256"]
        for record in manifest_a["artifacts"]
        if record["path"].startswith("semantic-probes/") and record["path"].endswith("preview.mid")
    }

    assert len(base_midis) == 3
    assert len(base_wavs) == 3
    assert len(semantic_midis) == 6
    assert (out_a / "manifest.json").exists()
