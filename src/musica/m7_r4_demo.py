"""Generate deterministic M7-R4 reference-renderer audible automation evidence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import shutil
import struct
import wave
from pathlib import Path
from typing import Any

from .audio_qa import analyze_wav
from .automation_lowering import lower_automation_execution
from .automation_renderer import (
    automation_render_plan_sha256,
    automation_wav_bytes,
    build_automation_render_plan,
    gain_at_tick,
    validate_automation_render_plan,
)
from .compiler import compile_blueprint
from .contracts import ContractError, validate_contract
from .evidence import artifact_record, canonical_json_bytes, write_canonical_json
from .render import midi_bytes, wav_bytes

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"
EVIDENCE_DURATION_SECONDS = 8.0


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _explicit_blueprint() -> dict[str, Any]:
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


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_json(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _pcm_samples(value: bytes) -> tuple[int, list[int]]:
    with wave.open(io.BytesIO(value), "rb") as handle:
        if handle.getnchannels() != 1 or handle.getsampwidth() != 2:
            raise RuntimeError("M7-R4 evidence expects mono 16-bit PCM")
        sample_rate = int(handle.getframerate())
        raw = handle.readframes(handle.getnframes())
    return sample_rate, [int(item[0]) for item in struct.iter_unpack("<h", raw)]


def _rms(values: list[int]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(float(value) * float(value) for value in values) / len(values))


def _window_metrics(
    baseline: list[int], automated: list[int], sample_rate: int, start: float, end: float
) -> dict[str, Any]:
    first = max(0, int(round(start * sample_rate)))
    last = min(len(baseline), int(round(end * sample_rate)))
    before = baseline[first:last]
    after = automated[first:last]
    before_rms = _rms(before)
    after_rms = _rms(after)
    before_abs = sum(abs(value) for value in before)
    after_abs = sum(abs(value) for value in after)
    return {
        "start_seconds": start,
        "end_seconds": end,
        "sample_count": len(before),
        "baseline_rms": round(before_rms, 9),
        "automated_rms": round(after_rms, 9),
        "rms_ratio": round(after_rms / before_rms, 9) if before_rms else None,
        "absolute_amplitude_ratio": round(after_abs / before_abs, 9) if before_abs else None,
    }


def run_evidence(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    blueprint = _explicit_blueprint()
    legacy_blueprint = _load(BLUEPRINT_PATH)
    validate_contract(legacy_blueprint, "music-blueprint-v0.schema.json")

    blueprint_before = canonical_json_bytes(blueprint)
    music_ir = compile_blueprint(copy.deepcopy(blueprint))
    execution = lower_automation_execution(copy.deepcopy(blueprint))
    music_ir_before = canonical_json_bytes(music_ir)
    execution_before = canonical_json_bytes(execution)

    plan_a = build_automation_render_plan(music_ir, execution)
    plan_b = build_automation_render_plan(music_ir, execution)
    plan_deterministic = canonical_json_bytes(plan_a) == canonical_json_bytes(plan_b)

    baseline = wav_bytes(music_ir, duration_seconds=EVIDENCE_DURATION_SECONDS)
    midi_before = midi_bytes(music_ir)
    automated_a = automation_wav_bytes(
        music_ir, execution, duration_seconds=EVIDENCE_DURATION_SECONDS
    )
    automated_b = automation_wav_bytes(
        music_ir, execution, duration_seconds=EVIDENCE_DURATION_SECONDS
    )
    baseline_after = wav_bytes(music_ir, duration_seconds=EVIDENCE_DURATION_SECONDS)
    midi_after = midi_bytes(music_ir)

    baseline_path = root / "baseline.wav"
    automated_a_path = root / "automated-a.wav"
    automated_b_path = root / "automated-b.wav"
    baseline_path.write_bytes(baseline)
    automated_a_path.write_bytes(automated_a)
    automated_b_path.write_bytes(automated_b)

    sample_rate, baseline_pcm = _pcm_samples(baseline)
    auto_rate, automated_pcm = _pcm_samples(automated_a)
    if auto_rate != sample_rate or len(automated_pcm) != len(baseline_pcm):
        raise RuntimeError("M7-R4 automated WAV container does not align with baseline")

    different_samples = sum(
        1 for before, after in zip(baseline_pcm, automated_pcm) if before != after
    )
    whole_baseline_rms = _rms(baseline_pcm)
    whole_automated_rms = _rms(automated_pcm)
    whole_baseline_peak = max((abs(value) for value in baseline_pcm), default=0)
    whole_automated_peak = max((abs(value) for value in automated_pcm), default=0)

    windows = {
        "linear": _window_metrics(baseline_pcm, automated_pcm, sample_rate, 1.0, 2.0),
        "hold": _window_metrics(baseline_pcm, automated_pcm, sample_rate, 5.0, 6.0),
        "after_last": _window_metrics(baseline_pcm, automated_pcm, sample_rate, 7.0, 7.8),
    }

    envelope_proof = {
        "policy": plan_a["mapping"],
        "mapped_lane": plan_a["mapped_lanes"][0]["lane_id"],
        "probes": [
            {"tick": 0, "gain": str(gain_at_tick(plan_a, 0))},
            {"tick": 1920, "gain": str(gain_at_tick(plan_a, 1920))},
            {"tick": 3840, "gain": str(gain_at_tick(plan_a, 3840))},
            {"tick": 5000, "gain": str(gain_at_tick(plan_a, 5000))},
            {"tick": 5760, "gain": str(gain_at_tick(plan_a, 5760))},
            {"tick": 7000, "gain": str(gain_at_tick(plan_a, 7000))},
        ],
        "linear_midpoint_exact": gain_at_tick(plan_a, 1920).as_tuple()
        == gain_at_tick(plan_b, 1920).as_tuple(),
        "hold_exact": gain_at_tick(plan_a, 5000) == gain_at_tick(plan_b, 5000),
    }

    audio_difference = {
        "duration_seconds": EVIDENCE_DURATION_SECONDS,
        "sample_rate": sample_rate,
        "baseline_sha256": _sha_bytes(baseline),
        "automated_a_sha256": _sha_bytes(automated_a),
        "automated_b_sha256": _sha_bytes(automated_b),
        "automated_byte_identical": automated_a == automated_b,
        "baseline_differs_from_automated": baseline != automated_a,
        "different_pcm_sample_count": different_samples,
        "whole_baseline_rms": round(whole_baseline_rms, 9),
        "whole_automated_rms": round(whole_automated_rms, 9),
        "whole_baseline_peak": whole_baseline_peak,
        "whole_automated_peak": whole_automated_peak,
        "windows": windows,
    }

    legacy_ir = compile_blueprint(copy.deepcopy(legacy_blueprint))
    legacy_execution = lower_automation_execution(copy.deepcopy(legacy_blueprint))
    legacy_plan = build_automation_render_plan(legacy_ir, legacy_execution)
    legacy_baseline = wav_bytes(legacy_ir, duration_seconds=2.0)
    legacy_automated = automation_wav_bytes(
        legacy_ir, legacy_execution, duration_seconds=2.0
    )
    legacy_proof = {
        "explicit_automation_present": legacy_execution["source"]["explicit_automation_present"],
        "mapped_lanes": legacy_plan["mapped_lanes"],
        "unmapped_lanes": legacy_plan["unmapped_lanes"],
        "baseline_sha256": _sha_bytes(legacy_baseline),
        "automation_sha256": _sha_bytes(legacy_automated),
        "baseline_byte_identical": legacy_baseline == legacy_automated,
    }

    tampered_plan = copy.deepcopy(plan_a)
    tampered_plan["source"]["music_ir_sha256"] = "0" * 64
    tampered_plan_rejected = False
    tampered_reason = ""
    try:
        validate_automation_render_plan(tampered_plan, music_ir, execution)
    except ContractError as exc:
        tampered_plan_rejected = True
        tampered_reason = str(exc)

    authority_proof = {
        "plan_classification": plan_a["classification"],
        "authority": plan_a["authority"],
        "mapped_parameter_ids": [lane["parameter_id"] for lane in plan_a["mapped_lanes"]],
        "unmapped_parameter_ids": [lane["parameter_id"] for lane in plan_a["unmapped_lanes"]],
        "tampered_plan_rejected": tampered_plan_rejected,
        "tampered_plan_rejection_reason": tampered_reason,
        "blueprint_unchanged": canonical_json_bytes(blueprint) == blueprint_before,
        "music_ir_unchanged": canonical_json_bytes(music_ir) == music_ir_before,
        "execution_unchanged": canonical_json_bytes(execution) == execution_before,
        "existing_wav_byte_identical": baseline == baseline_after,
        "existing_midi_byte_identical": midi_before == midi_after,
        "cc11_used_as_canonical_mix_gain": False,
    }

    qa = {
        "baseline": analyze_wav(baseline_path, target_seconds=EVIDENCE_DURATION_SECONDS),
        "automated": analyze_wav(automated_a_path, target_seconds=EVIDENCE_DURATION_SECONDS),
    }

    write_canonical_json(root / "source-blueprint.json", blueprint)
    write_canonical_json(root / "music-ir.json", music_ir)
    write_canonical_json(root / "automation-execution.json", execution)
    write_canonical_json(root / "automation-render-plan.json", plan_a)
    write_canonical_json(root / "envelope-proof.json", envelope_proof)
    write_canonical_json(root / "audio-difference-proof.json", audio_difference)
    write_canonical_json(root / "legacy-proof.json", legacy_proof)
    write_canonical_json(root / "authority-boundary-proof.json", authority_proof)
    write_canonical_json(root / "audio-quality.json", qa)

    proof = {
        "proof_version": "0",
        "plan_byte_deterministic": plan_deterministic,
        "music_ir_hash_bound": plan_a["source"]["music_ir_sha256"] == _sha_json(music_ir),
        "execution_hash_bound": plan_a["source"]["automation_execution_sha256"] == _sha_json(execution),
        "revision_cross_bound": music_ir["source_blueprint_revision"] == execution["source"]["revision_id"],
        "ppq_cross_bound": music_ir["timing"]["ppq"] == execution["lowering"]["ppq"],
        "mix_gain_mapped": [lane["parameter_id"] for lane in plan_a["mapped_lanes"]] == ["mix.gain"],
        "synth_cutoff_unmapped": "synth.cutoff" in authority_proof["unmapped_parameter_ids"],
        "linear_probe_exact": str(gain_at_tick(plan_a, 1920)) == "0.735",
        "hold_probe_exact": str(gain_at_tick(plan_a, 5000)) == "0.82",
        "after_last_probe_exact": str(gain_at_tick(plan_a, 7000)) == "0.75",
        "automated_wav_byte_deterministic": automated_a == automated_b,
        "automated_wav_differs_from_baseline": baseline != automated_a,
        "different_pcm_samples_positive": different_samples > 0,
        "whole_rms_reduced": whole_automated_rms < whole_baseline_rms,
        "whole_peak_reduced": whole_automated_peak < whole_baseline_peak,
        "linear_window_ratio_bounded": (
            windows["linear"]["rms_ratio"] is not None
            and 0.65 < windows["linear"]["rms_ratio"] < 0.82
        ),
        "hold_window_ratio_matches": (
            windows["hold"]["rms_ratio"] is not None
            and abs(windows["hold"]["rms_ratio"] - 0.82) < 0.01
        ),
        "after_last_window_ratio_matches": (
            windows["after_last"]["rms_ratio"] is not None
            and abs(windows["after_last"]["rms_ratio"] - 0.75) < 0.01
        ),
        "legacy_baseline_equivalent": legacy_proof["baseline_byte_identical"],
        "tampered_plan_rejected": tampered_plan_rejected,
        "source_objects_unchanged": (
            authority_proof["blueprint_unchanged"]
            and authority_proof["music_ir_unchanged"]
            and authority_proof["execution_unchanged"]
        ),
        "existing_wav_regression_stable": authority_proof["existing_wav_byte_identical"],
        "existing_midi_regression_stable": authority_proof["existing_midi_byte_identical"],
        "qa_pass": qa["baseline"]["status"] == "PASS" and qa["automated"]["status"] == "PASS",
        "canonical": plan_a["authority"]["canonical"],
        "project_mutation_authorized": plan_a["authority"]["project_mutation_authorized"],
        "blueprint_mutation_authorized": plan_a["authority"]["blueprint_mutation_authorized"],
        "reverse_promotion_authorized": plan_a["authority"]["reverse_promotion_authorized"],
        "midi_cc_semantics_authorized": plan_a["authority"]["midi_cc_semantics_authorized"],
        "renderer_application_authorized": plan_a["authority"]["renderer_application_authorized"],
        "cc11_used_as_canonical_mix_gain": False,
    }

    required_true = [
        "plan_byte_deterministic",
        "music_ir_hash_bound",
        "execution_hash_bound",
        "revision_cross_bound",
        "ppq_cross_bound",
        "mix_gain_mapped",
        "synth_cutoff_unmapped",
        "linear_probe_exact",
        "hold_probe_exact",
        "after_last_probe_exact",
        "automated_wav_byte_deterministic",
        "automated_wav_differs_from_baseline",
        "different_pcm_samples_positive",
        "whole_rms_reduced",
        "whole_peak_reduced",
        "linear_window_ratio_bounded",
        "hold_window_ratio_matches",
        "after_last_window_ratio_matches",
        "legacy_baseline_equivalent",
        "tampered_plan_rejected",
        "source_objects_unchanged",
        "existing_wav_regression_stable",
        "existing_midi_regression_stable",
        "qa_pass",
        "renderer_application_authorized",
    ]
    required_false = [
        "canonical",
        "project_mutation_authorized",
        "blueprint_mutation_authorized",
        "reverse_promotion_authorized",
        "midi_cc_semantics_authorized",
        "cc11_used_as_canonical_mix_gain",
    ]
    failed_true = [key for key in required_true if proof[key] is not True]
    failed_false = [key for key in required_false if proof[key] is not False]
    if failed_true or failed_false:
        raise RuntimeError(
            f"M7-R4 evidence proof failed: expected true={failed_true}, expected false={failed_false}"
        )

    write_canonical_json(root / "proof.json", proof)
    evidence_files = sorted(path for path in root.iterdir() if path.is_file())
    manifest = {
        "manifest_version": "0",
        "milestone": "M7-R4",
        "mapping_policy_id": plan_a["mapping"]["policy_id"],
        "automation_render_plan_sha256": automation_render_plan_sha256(plan_a),
        "records": [artifact_record(path, root) for path in evidence_files],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_evidence(args.out)


if __name__ == "__main__":
    main()
