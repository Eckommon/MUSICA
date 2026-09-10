from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from musica.compiler import compile_blueprint
from musica.contracts import ContractError, clone_for_revision, validate_revision
from musica.evidence import sha256_file
from musica.m0_demo import run_demo
from musica.render import midi_bytes, wav_bytes
from musica.semantic import apply_semantic_control

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples/blueprints/valid/dark-electronic-20s-r1.json"
CONTROL_PATH = ROOT / "examples/semantic-controls/urgent-final-section.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def track(ir: dict, track_id: str) -> dict:
    return next(item for item in ir["tracks"] if item["track_id"] == track_id)


def test_semantic_edit_preserves_protected_targets_and_emits_explainable_diff():
    parent = load(BLUEPRINT_PATH)
    control = load(CONTROL_PATH)
    candidate, diff = apply_semantic_control(parent, control)

    protected = [
        "/musical_context/tempo/bpm",
        "/materials/melody/main_motif_id",
        "/materials/rhythm/drum_pattern_id",
    ]
    for pointer, before, after in [
        (protected[0], parent["musical_context"]["tempo"]["bpm"], candidate["musical_context"]["tempo"]["bpm"]),
        (protected[1], parent["materials"]["melody"]["main_motif_id"], candidate["materials"]["melody"]["main_motif_id"]),
        (protected[2], parent["materials"]["rhythm"]["drum_pattern_id"], candidate["materials"]["rhythm"]["drum_pattern_id"]),
    ]:
        assert before == after, pointer

    changed_paths = {item["path"] for item in diff}
    assert not (set(protected) & changed_paths)
    assert any("section_overrides/0/values/tension" in path for path in changed_paths)
    assert candidate["provenance"]["selected_mechanisms"]
    assert any("L-TEMPO" in item for item in candidate["provenance"]["rejected_mechanisms"])


def test_semantic_runtime_does_not_pretend_unimplemented_axes_exist():
    parent = load(BLUEPRINT_PATH)
    control = load(CONTROL_PATH)
    control["name"] = "warmth"
    with pytest.raises(ContractError, match="implements only 'tension'"):
        apply_semantic_control(parent, control)


def test_prohibited_tempo_mutation_is_blocked_by_hard_lock():
    parent = load(BLUEPRINT_PATH)
    candidate = clone_for_revision(parent, "rev-illegal")
    candidate["musical_context"]["tempo"]["bpm"] = 118
    conflicts = validate_revision(parent, candidate)
    assert any(conflict.rule_id == "L-TEMPO" and conflict.status == "BLOCKED" for conflict in conflicts)


def test_compiler_preserves_motif_and_drums_while_semantic_edit_changes_bass_activity():
    parent = load(BLUEPRINT_PATH)
    control = load(CONTROL_PATH)
    candidate, _ = apply_semantic_control(parent, control)

    ir1 = compile_blueprint(parent)
    ir2 = compile_blueprint(candidate)

    assert track(ir1, "T-MOTIF")["events"] == track(ir2, "T-MOTIF")["events"]
    assert track(ir1, "T-DRUMS")["events"] == track(ir2, "T-DRUMS")["events"]
    assert len(track(ir2, "T-BASS")["events"]) > len(track(ir1, "T-BASS")["events"])
    assert ir1["tempo_events"] == ir2["tempo_events"]


def test_midi_and_wav_serialization_are_deterministic_and_structurally_valid():
    parent = load(BLUEPRINT_PATH)
    candidate, _ = apply_semantic_control(parent, load(CONTROL_PATH))
    ir = compile_blueprint(candidate)

    midi_a = midi_bytes(ir)
    midi_b = midi_bytes(copy.deepcopy(ir))
    assert midi_a == midi_b
    assert midi_a[:4] == b"MThd"

    wav_a = wav_bytes(ir, duration_seconds=2.0, sample_rate=8000)
    wav_b = wav_bytes(copy.deepcopy(ir), duration_seconds=2.0, sample_rate=8000)
    assert wav_a == wav_b
    assert wav_a[:4] == b"RIFF"
    assert wav_a[8:12] == b"WAVE"
    assert len(wav_a) > 44


def test_full_evidence_bundle_hashes_are_reproducible(tmp_path: Path):
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    manifest_a = run_demo(BLUEPRINT_PATH, CONTROL_PATH, out_a)
    manifest_b = run_demo(BLUEPRINT_PATH, CONTROL_PATH, out_b)

    assert manifest_a == manifest_b
    records = {record["path"]: record for record in manifest_a["artifacts"]}
    for relative, record in records.items():
        assert sha256_file(out_a / relative) == record["sha256"]
        assert sha256_file(out_b / relative) == record["sha256"]

    assert records["preview-r1.mid"]["sha256"] != records["preview-r2.mid"]["sha256"]
    assert records["preview-r1.wav"]["sha256"] != records["preview-r2.wav"]["sha256"]
    assert (out_a / "manifest.json").exists()
