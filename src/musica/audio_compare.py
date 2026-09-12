"""Bounded objective paired-audio analysis for MUSICA M5-R4.

MUSICA M5-R4용 제한된 객관 쌍대 오디오 분석기입니다.

This module deliberately describes signal differences only. It does not infer human
preference, perceptual superiority, mastering quality, or musical quality.
"""

from __future__ import annotations

import hashlib
import math
import wave
from pathlib import Path
from typing import Any

import numpy as np

from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes, sha256_file

ANALYZER_ID = "musica-audio-compare"
ANALYZER_VERSION = "0.1.0"
POLICY_ID = "musica-objective-audio-comparison-v0"
POLICY_VERSION = "0"
SILENCE_THRESHOLD_DBFS = -80.0
SILENCE_THRESHOLD_AMPLITUDE = 10.0 ** (SILENCE_THRESHOLD_DBFS / 20.0)
SPECTRAL_WINDOW_MS = 50.0
SPECTRAL_OVERLAP_RATIO = 0.5
FREQUENCY_FLOOR_HZ = 20.0
MAX_COMMON_CEILING_HZ = 10000.0
NYQUIST_SAFETY_RATIO = 0.45

METRIC_UNITS = {
    "rms_dbfs": "dBFS",
    "peak_dbfs": "dBFS",
    "crest_factor_db": "dB",
    "silence_ratio": "ratio",
    "dc_offset_normalized": "normalized",
    "stereo_correlation": "correlation",
    "stereo_difference_rms_dbfs": "dBFS",
    "spectral_centroid_hz": "Hz",
    "spectral_rolloff_95_hz": "Hz",
    "band_energy_low_ratio": "ratio",
    "band_energy_mid_ratio": "ratio",
    "band_energy_high_ratio": "ratio",
}

METRIC_METHODS = {
    "rms_dbfs": "20*log10(sqrt(mean(all_channel_samples^2)))",
    "peak_dbfs": "20*log10(max(abs(all_channel_samples)))",
    "crest_factor_db": "peak_dbfs-rms_dbfs",
    "silence_ratio": "fraction_of_frames_all_channels_at_or_below_-80dBFS",
    "dc_offset_normalized": "mean(all_channel_samples)",
    "stereo_correlation": "pearson_L_R_after_channel_mean_removal",
    "stereo_difference_rms_dbfs": "20*log10(rms((L-R)/2))",
    "spectral_centroid_hz": "centroid_of_mean_Hann_window_power_in_common_band",
    "spectral_rolloff_95_hz": "frequency_below_which_95pct_common_band_power_lies",
    "band_energy_low_ratio": "20_to_250Hz_power/common_band_power",
    "band_energy_mid_ratio": "250_to_4000Hz_power/common_band_power",
    "band_energy_high_ratio": "4000Hz_to_common_ceiling_power/common_band_power",
}


class AudioComparisonError(ContractError):
    """Raised when paired comparison inputs violate the M5-R4 authority contract."""


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _dbfs(value: float) -> float | None:
    if not math.isfinite(value) or value <= 0.0:
        return None
    return 20.0 * math.log10(value)


def _round_metric(value: float | None) -> float | None:
    if value is None or not math.isfinite(value):
        return None
    return round(float(value), 9)


def _metric(name: str, value: float | None, *, status: str | None = None) -> dict[str, Any]:
    effective = status or ("MEASURED" if value is not None and math.isfinite(float(value)) else "UNKNOWN")
    if effective != "MEASURED":
        value = None
    return {
        "status": effective,
        "value": _round_metric(value),
        "unit": METRIC_UNITS[name],
        "method": METRIC_METHODS[name],
    }


def _decode_pcm(raw: bytes, sample_width: int) -> np.ndarray:
    """Decode little-endian PCM into signed float64 full-scale-normalized samples."""

    if sample_width == 1:
        values = np.frombuffer(raw, dtype=np.uint8).astype(np.int16) - 128
        scale = 128.0
    elif sample_width == 2:
        values = np.frombuffer(raw, dtype="<i2").astype(np.int32)
        scale = 32768.0
    elif sample_width == 3:
        data = np.frombuffer(raw, dtype=np.uint8)
        usable = data.size - (data.size % 3)
        data = data[:usable].reshape(-1, 3).astype(np.int32)
        values = data[:, 0] | (data[:, 1] << 8) | (data[:, 2] << 16)
        values = np.where(values & 0x800000, values - (1 << 24), values)
        scale = float(1 << 23)
    elif sample_width == 4:
        values = np.frombuffer(raw, dtype="<i4").astype(np.int64)
        scale = float(1 << 31)
    else:
        raise AudioComparisonError(f"unsupported PCM sample width: {sample_width}")
    return np.asarray(values, dtype=np.float64) / scale


def load_pcm_wav(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.is_file():
        raise AudioComparisonError(f"WAV artifact missing: {target}")
    try:
        with wave.open(str(target), "rb") as handle:
            if handle.getcomptype() != "NONE":
                raise AudioComparisonError("M5-R4 v0 requires uncompressed PCM WAV")
            channels = int(handle.getnchannels())
            sample_width = int(handle.getsampwidth())
            sample_rate = int(handle.getframerate())
            frame_count = int(handle.getnframes())
            raw = handle.readframes(frame_count)
    except (wave.Error, EOFError) as exc:
        raise AudioComparisonError(f"invalid WAV artifact: {target}") from exc
    if channels <= 0 or sample_rate <= 0 or frame_count <= 0:
        raise AudioComparisonError("WAV container has invalid channel/rate/frame count")
    decoded = _decode_pcm(raw, sample_width)
    expected = frame_count * channels
    if decoded.size != expected:
        raise AudioComparisonError(
            f"PCM sample count mismatch: decoded={decoded.size}, expected={expected}"
        )
    samples = decoded.reshape(frame_count, channels)
    return {
        "path": target,
        "samples": samples,
        "sample_rate": sample_rate,
        "channels": channels,
        "sample_width_bytes": sample_width,
        "bit_depth": sample_width * 8,
        "frame_count": frame_count,
        "duration_seconds": frame_count / sample_rate,
        "sha256": sha256_file(target),
        "size_bytes": target.stat().st_size,
    }


def common_frequency_ceiling(sample_rate_a: int, sample_rate_b: int) -> float:
    if sample_rate_a <= 0 or sample_rate_b <= 0:
        raise AudioComparisonError("sample rates must be positive")
    ceiling = min(
        MAX_COMMON_CEILING_HZ,
        NYQUIST_SAFETY_RATIO * float(min(sample_rate_a, sample_rate_b)),
    )
    if ceiling <= 4000.0:
        raise AudioComparisonError(
            f"common spectral ceiling does not support the v0 high band: {ceiling}"
        )
    return float(ceiling)


def _mean_power_spectrum(
    samples: np.ndarray,
    sample_rate: int,
    frequency_ceiling_hz: float,
) -> tuple[np.ndarray, np.ndarray]:
    if samples.ndim != 2 or samples.shape[0] <= 0:
        raise AudioComparisonError("PCM samples must be non-empty frames x channels")
    mono = np.mean(samples, axis=1, dtype=np.float64)
    window_length = max(16, int(round(sample_rate * SPECTRAL_WINDOW_MS / 1000.0)))
    hop = max(1, int(round(window_length * (1.0 - SPECTRAL_OVERLAP_RATIO))))
    if mono.size < window_length:
        raise AudioComparisonError("audio is shorter than one M5-R4 spectral window")
    window = np.hanning(window_length).astype(np.float64)
    starts = range(0, mono.size - window_length + 1, hop)
    accumulated: np.ndarray | None = None
    count = 0
    for start in starts:
        frame = mono[start : start + window_length] * window
        spectrum = np.fft.rfft(frame)
        power = np.abs(spectrum) ** 2
        accumulated = power if accumulated is None else accumulated + power
        count += 1
    if accumulated is None or count <= 0:
        raise AudioComparisonError("no spectral windows were analyzed")
    mean_power = accumulated / float(count)
    frequencies = np.fft.rfftfreq(window_length, d=1.0 / float(sample_rate))
    mask = (frequencies >= FREQUENCY_FLOOR_HZ) & (frequencies <= frequency_ceiling_hz)
    frequencies = frequencies[mask]
    mean_power = mean_power[mask]
    if frequencies.size <= 0 or float(np.sum(mean_power)) <= 0.0:
        raise AudioComparisonError("spectral common band has no measurable power")
    return frequencies, mean_power


def analyze_objective_metrics(
    wav: str | Path | dict[str, Any],
    *,
    frequency_ceiling_hz: float,
) -> dict[str, Any]:
    pcm = load_pcm_wav(wav) if not isinstance(wav, dict) else wav
    samples = np.asarray(pcm["samples"], dtype=np.float64)
    flattened = samples.reshape(-1)
    rms = float(np.sqrt(np.mean(flattened * flattened)))
    peak = float(np.max(np.abs(flattened)))
    rms_db = _dbfs(rms)
    peak_db = _dbfs(peak)
    crest = None if rms_db is None or peak_db is None else peak_db - rms_db
    silent_frames = np.all(np.abs(samples) <= SILENCE_THRESHOLD_AMPLITUDE, axis=1)
    silence_ratio = float(np.mean(silent_frames))
    dc_offset = float(np.mean(flattened))

    metrics: dict[str, Any] = {
        "rms_dbfs": _metric("rms_dbfs", rms_db),
        "peak_dbfs": _metric("peak_dbfs", peak_db),
        "crest_factor_db": _metric("crest_factor_db", crest),
        "silence_ratio": _metric("silence_ratio", silence_ratio),
        "dc_offset_normalized": _metric("dc_offset_normalized", dc_offset),
    }

    if int(pcm["channels"]) == 2:
        left = samples[:, 0]
        right = samples[:, 1]
        left_centered = left - float(np.mean(left))
        right_centered = right - float(np.mean(right))
        denom = float(
            np.sqrt(np.sum(left_centered * left_centered) * np.sum(right_centered * right_centered))
        )
        correlation = (
            float(np.sum(left_centered * right_centered) / denom) if denom > 0.0 else None
        )
        side = (left - right) / 2.0
        side_rms_db = _dbfs(float(np.sqrt(np.mean(side * side))))
        metrics["stereo_correlation"] = _metric("stereo_correlation", correlation)
        metrics["stereo_difference_rms_dbfs"] = _metric(
            "stereo_difference_rms_dbfs", side_rms_db
        )
    else:
        metrics["stereo_correlation"] = _metric(
            "stereo_correlation", None, status="NOT_APPLICABLE"
        )
        metrics["stereo_difference_rms_dbfs"] = _metric(
            "stereo_difference_rms_dbfs", None, status="NOT_APPLICABLE"
        )

    frequencies, power = _mean_power_spectrum(
        samples,
        int(pcm["sample_rate"]),
        frequency_ceiling_hz,
    )
    total_power = float(np.sum(power))
    centroid = float(np.sum(frequencies * power) / total_power)
    cumulative = np.cumsum(power)
    rolloff_index = int(np.searchsorted(cumulative, 0.95 * total_power, side="left"))
    rolloff_index = min(rolloff_index, frequencies.size - 1)
    rolloff = float(frequencies[rolloff_index])

    def band_ratio(low: float, high: float, *, include_high: bool = False) -> float:
        if include_high:
            mask = (frequencies >= low) & (frequencies <= high)
        else:
            mask = (frequencies >= low) & (frequencies < high)
        return float(np.sum(power[mask]) / total_power)

    metrics.update(
        {
            "spectral_centroid_hz": _metric("spectral_centroid_hz", centroid),
            "spectral_rolloff_95_hz": _metric("spectral_rolloff_95_hz", rolloff),
            "band_energy_low_ratio": _metric(
                "band_energy_low_ratio", band_ratio(20.0, 250.0)
            ),
            "band_energy_mid_ratio": _metric(
                "band_energy_mid_ratio", band_ratio(250.0, 4000.0)
            ),
            "band_energy_high_ratio": _metric(
                "band_energy_high_ratio",
                band_ratio(4000.0, frequency_ceiling_hz, include_high=True),
            ),
        }
    )
    return metrics


def analysis_policy(frequency_ceiling_hz: float) -> dict[str, Any]:
    return {
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "sample_domain": "full_scale_normalized_native_pcm",
        "time_domain_channel_policy": "all_channel_sample_energy",
        "spectral_channel_policy": "arithmetic_channel_mean",
        "spectral_window_ms": SPECTRAL_WINDOW_MS,
        "spectral_overlap_ratio": SPECTRAL_OVERLAP_RATIO,
        "spectral_window_function": "hann",
        "frequency_floor_hz": FREQUENCY_FLOOR_HZ,
        "frequency_ceiling_hz": round(float(frequency_ceiling_hz), 9),
        "silence_threshold_dbfs": SILENCE_THRESHOLD_DBFS,
        "comparison_resampling": "NONE",
        "comparison_gain_matching": "NONE",
        "comparison_time_stretching": "NONE",
    }


def _side_schema(side: dict[str, Any]) -> dict[str, Any]:
    keys = {
        "renderer_id",
        "renderer_version",
        "bound_music_ir_sha256",
        "runtime",
        "content",
        "config_sha256",
        "raw_artifact",
        "audio_quality_report",
        "renderer_normalizations",
    }
    return {key: side[key] for key in keys}


def _has_complete_provenance(side: dict[str, Any]) -> bool:
    runtime = side.get("runtime") or {}
    required_runtime = all(runtime.get(key) for key in ("kind", "name", "version", "os", "architecture"))
    if runtime.get("kind") == "external_process" and not runtime.get("executable_sha256"):
        required_runtime = False
    if not side.get("config_sha256") or not side.get("raw_artifact") or not side.get("audio_quality_report"):
        return False
    if side.get("renderer_id") == "musica-fluidsynth-local" and not side.get("content"):
        return False
    return bool(required_runtime)


def _artifact_matches(path: str | Path, artifact: dict[str, Any]) -> bool:
    target = Path(path)
    if not target.is_file():
        return False
    return (
        sha256_file(target) == artifact.get("sha256")
        and target.stat().st_size == artifact.get("size_bytes")
    )


def _qa_binding_matches(qa: dict[str, Any], binding: dict[str, Any]) -> bool:
    return (
        binding.get("report_id") == qa.get("report_id")
        and binding.get("report_sha256") == _canonical_sha256(qa)
        and binding.get("status") == qa.get("status")
    )


def _paired_deltas(metrics_a: dict[str, Any], metrics_b: dict[str, Any]) -> list[dict[str, Any]]:
    deltas: list[dict[str, Any]] = []
    for name in METRIC_UNITS:
        a = metrics_a[name]
        b = metrics_b[name]
        if a["status"] == "MEASURED" and b["status"] == "MEASURED":
            status = "MEASURED"
            delta = round(float(b["value"]) - float(a["value"]), 9)
        elif "NOT_APPLICABLE" in {a["status"], b["status"]}:
            status = "NOT_APPLICABLE"
            delta = None
        else:
            status = "UNKNOWN"
            delta = None
        deltas.append(
            {
                "metric": name,
                "status": status,
                "delta_b_minus_a": delta,
                "unit": METRIC_UNITS[name],
            }
        )
    return deltas


def _confounds(side_a: dict[str, Any], side_b: dict[str, Any]) -> list[dict[str, Any]]:
    artifact_a = side_a["raw_artifact"]
    artifact_b = side_b["raw_artifact"]
    confounds: list[dict[str, Any]] = []

    def add(code: str, status: str, description: str) -> None:
        confounds.append({"code": code, "status": status, "description": description})

    if artifact_a["channels"] != artifact_b["channels"]:
        add(
            "CHANNEL_LAYOUT_DIFFERENCE",
            "RECORDED",
            f"A={artifact_a['channels']} channels; B={artifact_b['channels']} channels.",
        )
    if artifact_a["sample_rate"] != artifact_b["sample_rate"]:
        add(
            "SAMPLE_RATE_DIFFERENCE",
            "RECORDED",
            f"A={artifact_a['sample_rate']} Hz; B={artifact_b['sample_rate']} Hz.",
        )
    if artifact_a["bit_depth"] != artifact_b["bit_depth"]:
        add(
            "BIT_DEPTH_DIFFERENCE",
            "RECORDED",
            f"A={artifact_a['bit_depth']} bit; B={artifact_b['bit_depth']} bit.",
        )
    if any(item.get("status") == "APPLIED" for item in side_a.get("renderer_normalizations", [])) or any(
        item.get("status") == "APPLIED" for item in side_b.get("renderer_normalizations", [])
    ):
        add(
            "RENDERER_LEVEL_DURATION_NORMALIZATION",
            "RECORDED",
            "At least one renderer applied its already-declared duration normalization policy.",
        )
    if side_a["runtime"]["os"] != side_b["runtime"]["os"]:
        add(
            "RUNTIME_OS_DIFFERENCE",
            "RECORDED",
            f"A={side_a['runtime']['os']}; B={side_b['runtime']['os']}.",
        )
    add(
        "DEFAULT_EFFECT_OR_REVERB_DIFFERENCE",
        "UNKNOWN",
        "Renderer-internal effect/reverb contribution is not independently isolated in M5-R4 v0.",
    )
    return confounds


def build_audio_comparison(
    *,
    comparison_id: str,
    source_binding: dict[str, Any],
    source_binding_a: dict[str, Any],
    source_binding_b: dict[str, Any],
    renderer_a: dict[str, Any],
    renderer_b: dict[str, Any],
    wav_a: str | Path,
    wav_b: str | Path,
    qa_a: dict[str, Any],
    qa_b: dict[str, Any],
    evidence_class: str = "EXECUTION_EVIDENCE",
) -> dict[str, Any]:
    """Build and validate one objective-only M5-R4 comparison result."""

    pcm_a = load_pcm_wav(wav_a)
    pcm_b = load_pcm_wav(wav_b)
    ceiling = common_frequency_ceiling(int(pcm_a["sample_rate"]), int(pcm_b["sample_rate"]))
    metrics_a = analyze_objective_metrics(pcm_a, frequency_ceiling_hz=ceiling)
    metrics_b = analyze_objective_metrics(pcm_b, frequency_ceiling_hz=ceiling)

    source_hash_match = all(
        candidate.get("music_ir_sha256") == source_binding.get("music_ir_sha256")
        for candidate in (source_binding_a, source_binding_b)
    ) and all(
        side.get("bound_music_ir_sha256") == source_binding.get("music_ir_sha256")
        for side in (renderer_a, renderer_b)
    )
    blueprint_binding_match = all(
        candidate.get("blueprint_revision_id") == source_binding.get("blueprint_revision_id")
        and candidate.get("blueprint_sha256") == source_binding.get("blueprint_sha256")
        for candidate in (source_binding_a, source_binding_b)
    )
    qa_acceptable = all(qa.get("status") in {"PASS", "WARN"} for qa in (qa_a, qa_b))
    qa_acceptable = qa_acceptable and _qa_binding_matches(
        qa_a, renderer_a["audio_quality_report"]
    ) and _qa_binding_matches(qa_b, renderer_b["audio_quality_report"])
    target = float(source_binding["target_duration_seconds"])
    target_duration_match = all(
        abs(float(value) - target) <= 1e-9
        for value in (
            pcm_a["duration_seconds"],
            pcm_b["duration_seconds"],
            renderer_a["raw_artifact"]["duration_seconds"],
            renderer_b["raw_artifact"]["duration_seconds"],
        )
    )
    provenance_complete = (
        _has_complete_provenance(renderer_a)
        and _has_complete_provenance(renderer_b)
        and _artifact_matches(wav_a, renderer_a["raw_artifact"])
        and _artifact_matches(wav_b, renderer_b["raw_artifact"])
    )

    technical = {
        "source_hash_match": bool(source_hash_match),
        "blueprint_binding_match": bool(blueprint_binding_match),
        "qa_acceptable": bool(qa_acceptable),
        "target_duration_match": bool(target_duration_match),
        "provenance_complete": bool(provenance_complete),
    }
    reasons = [name for name, passed in technical.items() if not passed]
    comparable = not reasons

    result = {
        "comparison_version": "0",
        "comparison_id": comparison_id,
        "evidence_class": evidence_class,
        "source_binding": dict(source_binding),
        "renderer_a": _side_schema(renderer_a),
        "renderer_b": _side_schema(renderer_b),
        "technical_validity": technical,
        "analysis_policy": analysis_policy(ceiling),
        "objective_metrics_a": metrics_a,
        "objective_metrics_b": metrics_b,
        "paired_deltas": _paired_deltas(metrics_a, metrics_b),
        "comparison_normalizations": [],
        "confounds": _confounds(renderer_a, renderer_b),
        "comparability": {
            "status": "COMPARABLE" if comparable else "NOT_COMPARABLE",
            "reasons": [] if comparable else reasons,
        },
        "claim_boundary": {
            "human_subject_evidence": "NOT_VALIDATED",
            "perceptual_superiority": "UNKNOWN",
            "human_preference_claim_allowed": False,
        },
        "verdict": "COMPARABLE_OBJECTIVE_ONLY" if comparable else "NOT_COMPARABLE",
    }
    validate_contract(result, "audio-comparison-result-v0.schema.json")
    return result


def comparison_sha256(result: dict[str, Any]) -> str:
    validate_contract(result, "audio-comparison-result-v0.schema.json")
    return _canonical_sha256(result)
