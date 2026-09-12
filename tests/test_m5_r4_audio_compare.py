from __future__ import annotations

import copy
import hashlib
import wave
from pathlib import Path

import numpy as np
import pytest

from musica.audio_compare import (
    AudioComparisonError,
    build_audio_comparison,
    common_frequency_ceiling,
    comparison_sha256,
)
from musica.audio_qa import analyze_wav
from musica.evidence import canonical_json_bytes, sha256_file, write_canonical_json


def _write_mono(path: Path, sample_rate: int, seconds: float = 1.0) -> Path:
    frames = int(round(sample_rate * seconds))
    t = np.arange(frames, dtype=np.float64) / sample_rate
    signal = 0.2 * np.sin(2.0 * np.pi * 440.0 * t)
    pcm = np.clip(np.round(signal * 32767.0), -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm.tobytes())
    return path


def _write_stereo(path: Path, sample_rate: int, seconds: float = 1.0) -> Path:
    frames = int(round(sample_rate * seconds))
    t = np.arange(frames, dtype=np.float64) / sample_rate
    left = 0.18 * np.sin(2.0 * np.pi * 440.0 * t)
    right = 0.16 * np.sin(2.0 * np.pi * 660.0 * t)
    stacked = np.column_stack([left, right])
    pcm = np.clip(np.round(stacked * 32767.0), -32768, 32767).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm.tobytes())
    return path


def _canonical_hash(value: dict) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _side(
    *,
    renderer_id: str,
    wav: Path,
    qa: dict,
    qa_path: Path,
    music_ir_hash: str,
    sample_rate: int,
    channels: int,
    external: bool,
) -> dict:
    return {
        "renderer_id": renderer_id,
        "renderer_version": "fixture-0",
        "bound_music_ir_sha256": music_ir_hash,
        "runtime": {
            "kind": "external_process" if external else "in_process",
            "name": "fixture-runtime",
            "version": "0",
            "executable_sha256": "1" * 64 if external else None,
            "os": "fixture-os",
            "architecture": "fixture-arch",
        },
        "content": (
            [{"content_id": "fixture-content", "version": "0", "sha256": "2" * 64}]
            if external
            else []
        ),
        "config_sha256": "3" * 64,
        "raw_artifact": {
            "role": "wav",
            "sha256": sha256_file(wav),
            "size_bytes": wav.stat().st_size,
            "sample_rate": sample_rate,
            "channels": channels,
            "bit_depth": 16,
            "duration_seconds": 1.0,
        },
        "audio_quality_report": {
            "report_id": qa["report_id"],
            "report_sha256": sha256_file(qa_path),
            "status": qa["status"],
        },
        "renderer_normalizations": [],
    }


def _fixture(tmp_path: Path):
    wav_a = _write_mono(tmp_path / "a.wav", 22050)
    wav_b = _write_stereo(tmp_path / "b.wav", 48000)
    qa_a = analyze_wav(wav_a, target_seconds=1.0)
    qa_b = analyze_wav(wav_b, target_seconds=1.0)
    qa_a_path = write_canonical_json(tmp_path / "qa-a.json", qa_a)
    qa_b_path = write_canonical_json(tmp_path / "qa-b.json", qa_b)
    ir_hash = "a" * 64
    source = {
        "project_id": "fixture-project",
        "blueprint_revision_id": "fixture-rev",
        "blueprint_sha256": "b" * 64,
        "music_ir_sha256": ir_hash,
        "target_duration_seconds": 1.0,
    }
    side_a = _side(
        renderer_id="musica-reference-local",
        wav=wav_a,
        qa=qa_a,
        qa_path=qa_a_path,
        music_ir_hash=ir_hash,
        sample_rate=22050,
        channels=1,
        external=False,
    )
    side_b = _side(
        renderer_id="musica-fluidsynth-local",
        wav=wav_b,
        qa=qa_b,
        qa_path=qa_b_path,
        music_ir_hash=ir_hash,
        sample_rate=48000,
        channels=2,
        external=True,
    )
    return source, side_a, side_b, wav_a, wav_b, qa_a, qa_b


def _compare(tmp_path: Path):
    source, side_a, side_b, wav_a, wav_b, qa_a, qa_b = _fixture(tmp_path)
    result = build_audio_comparison(
        comparison_id="CMP-TEST",
        source_binding=source,
        source_binding_a=source,
        source_binding_b=source,
        renderer_a=side_a,
        renderer_b=side_b,
        wav_a=wav_a,
        wav_b=wav_b,
        qa_a=qa_a,
        qa_b=qa_b,
    )
    return result, source, side_a, side_b, wav_a, wav_b, qa_a, qa_b


def test_controlled_pair_is_comparable_objective_only(tmp_path: Path):
    result, *_ = _compare(tmp_path)
    assert result["comparability"] == {"status": "COMPARABLE", "reasons": []}
    assert result["verdict"] == "COMPARABLE_OBJECTIVE_ONLY"
    assert result["claim_boundary"] == {
        "human_subject_evidence": "NOT_VALIDATED",
        "perceptual_superiority": "UNKNOWN",
        "human_preference_claim_allowed": False,
    }
    assert result["analysis_policy"]["frequency_ceiling_hz"] == 9922.5
    assert result["analysis_policy"]["comparison_resampling"] == "NONE"
    assert result["analysis_policy"]["comparison_gain_matching"] == "NONE"


def test_native_format_differences_are_visible_confounds(tmp_path: Path):
    result, *_ = _compare(tmp_path)
    codes = {item["code"] for item in result["confounds"]}
    assert "CHANNEL_LAYOUT_DIFFERENCE" in codes
    assert "SAMPLE_RATE_DIFFERENCE" in codes
    assert result["objective_metrics_a"]["stereo_correlation"]["status"] == "NOT_APPLICABLE"
    assert result["objective_metrics_b"]["stereo_correlation"]["status"] == "MEASURED"


def test_objective_metrics_are_not_preference_verdicts(tmp_path: Path):
    result, *_ = _compare(tmp_path)
    serialized = canonical_json_bytes(result).decode("utf-8").upper()
    assert "RENDERER_B_BETTER" not in serialized
    assert "SUPERIOR" not in serialized
    assert all(item["status"] in {"MEASURED", "NOT_APPLICABLE", "UNKNOWN"} for item in result["paired_deltas"])


def test_source_music_ir_mismatch_fails_closed_to_not_comparable(tmp_path: Path):
    _, source, side_a, side_b, wav_a, wav_b, qa_a, qa_b = _compare(tmp_path)
    source_b = copy.deepcopy(source)
    source_b["music_ir_sha256"] = "f" * 64
    result = build_audio_comparison(
        comparison_id="CMP-NEG-SOURCE",
        source_binding=source,
        source_binding_a=source,
        source_binding_b=source_b,
        renderer_a=side_a,
        renderer_b=side_b,
        wav_a=wav_a,
        wav_b=wav_b,
        qa_a=qa_a,
        qa_b=qa_b,
    )
    assert result["comparability"]["status"] == "NOT_COMPARABLE"
    assert "source_hash_match" in result["comparability"]["reasons"]


def test_blueprint_binding_mismatch_fails_closed(tmp_path: Path):
    _, source, side_a, side_b, wav_a, wav_b, qa_a, qa_b = _compare(tmp_path)
    source_b = copy.deepcopy(source)
    source_b["blueprint_revision_id"] = "other-revision"
    result = build_audio_comparison(
        comparison_id="CMP-NEG-BLUEPRINT",
        source_binding=source,
        source_binding_a=source,
        source_binding_b=source_b,
        renderer_a=side_a,
        renderer_b=side_b,
        wav_a=wav_a,
        wav_b=wav_b,
        qa_a=qa_a,
        qa_b=qa_b,
    )
    assert result["comparability"]["status"] == "NOT_COMPARABLE"
    assert "blueprint_binding_match" in result["comparability"]["reasons"]


def test_failed_qa_fails_closed(tmp_path: Path):
    _, source, side_a, side_b, wav_a, wav_b, qa_a, qa_b = _compare(tmp_path)
    failed = copy.deepcopy(qa_b)
    failed["status"] = "FAIL"
    side_b = copy.deepcopy(side_b)
    side_b["audio_quality_report"]["status"] = "FAIL"
    side_b["audio_quality_report"]["report_sha256"] = _canonical_hash(failed)
    result = build_audio_comparison(
        comparison_id="CMP-NEG-QA",
        source_binding=source,
        source_binding_a=source,
        source_binding_b=source,
        renderer_a=side_a,
        renderer_b=side_b,
        wav_a=wav_a,
        wav_b=wav_b,
        qa_a=qa_a,
        qa_b=failed,
    )
    assert result["comparability"]["status"] == "NOT_COMPARABLE"
    assert "qa_acceptable" in result["comparability"]["reasons"]


def test_missing_fluidsynth_content_provenance_fails_closed(tmp_path: Path):
    _, source, side_a, side_b, wav_a, wav_b, qa_a, qa_b = _compare(tmp_path)
    side_b = copy.deepcopy(side_b)
    side_b["content"] = []
    result = build_audio_comparison(
        comparison_id="CMP-NEG-PROVENANCE",
        source_binding=source,
        source_binding_a=source,
        source_binding_b=source,
        renderer_a=side_a,
        renderer_b=side_b,
        wav_a=wav_a,
        wav_b=wav_b,
        qa_a=qa_a,
        qa_b=qa_b,
    )
    assert result["comparability"]["status"] == "NOT_COMPARABLE"
    assert "provenance_complete" in result["comparability"]["reasons"]


def test_artifact_tamper_is_not_comparable(tmp_path: Path):
    _, source, side_a, side_b, wav_a, wav_b, qa_a, qa_b = _compare(tmp_path)
    side_b = copy.deepcopy(side_b)
    side_b["raw_artifact"]["sha256"] = "9" * 64
    result = build_audio_comparison(
        comparison_id="CMP-NEG-TAMPER",
        source_binding=source,
        source_binding_a=source,
        source_binding_b=source,
        renderer_a=side_a,
        renderer_b=side_b,
        wav_a=wav_a,
        wav_b=wav_b,
        qa_a=qa_a,
        qa_b=qa_b,
    )
    assert result["comparability"]["status"] == "NOT_COMPARABLE"
    assert "provenance_complete" in result["comparability"]["reasons"]


def test_identical_inputs_produce_identical_comparison_hash(tmp_path: Path):
    first, source, side_a, side_b, wav_a, wav_b, qa_a, qa_b = _compare(tmp_path)
    second = build_audio_comparison(
        comparison_id="CMP-TEST",
        source_binding=source,
        source_binding_a=source,
        source_binding_b=source,
        renderer_a=side_a,
        renderer_b=side_b,
        wav_a=wav_a,
        wav_b=wav_b,
        qa_a=qa_a,
        qa_b=qa_b,
    )
    assert first == second
    assert comparison_sha256(first) == comparison_sha256(second)


def test_common_frequency_ceiling_requires_v0_high_band_support():
    assert common_frequency_ceiling(22050, 48000) == 9922.5
    with pytest.raises(AudioComparisonError, match="high band"):
        common_frequency_ceiling(8000, 48000)
