"""Objective PCM WAV quality baseline for MUSICA M5-R1.

MUSICA M5-R1용 객관적 PCM WAV 품질 기준선.

This module measures container/signal sanity only. It does not claim perceptual or
mastering quality and intentionally leaves integrated loudness UNKNOWN in R1.
"""

from __future__ import annotations

import struct
import wave
from pathlib import Path
from typing import Any, Iterable

from .contracts import validate_contract
from .evidence import sha256_file

DC_WARN_THRESHOLD = 0.05
MIN_DURATION_TOLERANCE_SECONDS = 0.05
DURATION_TOLERANCE_RATIO = 0.005


def _pcm_samples(raw: bytes, sample_width: int) -> Iterable[int]:
    if sample_width == 1:
        for value in raw:
            yield value - 128
        return
    if sample_width == 2:
        count = len(raw) // 2
        yield from struct.unpack(f"<{count}h", raw[: count * 2])
        return
    if sample_width == 3:
        usable = len(raw) - (len(raw) % 3)
        for offset in range(0, usable, 3):
            value = int.from_bytes(raw[offset : offset + 3], "little", signed=False)
            if value & 0x800000:
                value -= 1 << 24
            yield value
        return
    if sample_width == 4:
        count = len(raw) // 4
        yield from struct.unpack(f"<{count}i", raw[: count * 4])
        return
    raise ValueError(f"unsupported PCM sample width: {sample_width}")


def _invalid_report(path: Path, target_seconds: float, tolerance_seconds: float) -> dict[str, Any]:
    report = {
        "report_version": "0",
        "report_id": f"qa-{sha256_file(path)[:16]}",
        "artifact_sha256": sha256_file(path),
        "artifact_size_bytes": path.stat().st_size,
        "status": "FAIL",
        "container": {
            "valid": False,
            "format": "wav",
            "sample_rate": None,
            "channels": None,
            "sample_width_bytes": None,
            "bit_depth": None,
            "frame_count": None,
        },
        "signal": {
            "non_zero_sample_count": None,
            "peak_normalized": None,
            "clipping_sample_count": None,
            "dc_offset_normalized": None,
        },
        "duration": {
            "actual_seconds": None,
            "target_seconds": target_seconds,
            "tolerance_seconds": tolerance_seconds,
            "within_tolerance": None,
        },
        "loudness": {"integrated_lufs": None, "measurement_status": "UNKNOWN"},
    }
    validate_contract(report, "audio-quality-report-v0.schema.json")
    return report


def analyze_wav(
    path: str | Path,
    *,
    target_seconds: float,
    tolerance_seconds: float | None = None,
) -> dict[str, Any]:
    """Measure reproducible WAV validity/signal metrics and return AudioQualityReport v0."""

    target = Path(path)
    if not target.is_file():
        raise FileNotFoundError(target)
    if target_seconds <= 0:
        raise ValueError("target_seconds must be positive")

    tolerance = (
        float(tolerance_seconds)
        if tolerance_seconds is not None
        else max(MIN_DURATION_TOLERANCE_SECONDS, float(target_seconds) * DURATION_TOLERANCE_RATIO)
    )
    if tolerance < 0:
        raise ValueError("tolerance_seconds cannot be negative")

    try:
        with wave.open(str(target), "rb") as handle:
            if handle.getcomptype() != "NONE":
                return _invalid_report(target, float(target_seconds), tolerance)
            channels = int(handle.getnchannels())
            sample_width = int(handle.getsampwidth())
            sample_rate = int(handle.getframerate())
            frame_count = int(handle.getnframes())
            raw = handle.readframes(frame_count)
    except (wave.Error, EOFError):
        return _invalid_report(target, float(target_seconds), tolerance)

    try:
        samples = list(_pcm_samples(raw, sample_width))
    except ValueError:
        return _invalid_report(target, float(target_seconds), tolerance)

    bits = sample_width * 8
    positive_full_scale = float((1 << (bits - 1)) - 1)
    negative_full_scale = -(1 << (bits - 1))
    non_zero = sum(1 for value in samples if value != 0)
    peak_integer = max((abs(value) for value in samples), default=0)
    peak_normalized = float(peak_integer) / positive_full_scale if positive_full_scale else 0.0
    clipping = sum(
        1 for value in samples if value >= int(positive_full_scale) or value <= negative_full_scale
    )
    dc_offset = (
        (sum(samples) / len(samples)) / positive_full_scale
        if samples and positive_full_scale
        else 0.0
    )
    actual_seconds = frame_count / sample_rate if sample_rate else 0.0
    duration_ok = abs(actual_seconds - float(target_seconds)) <= tolerance

    if non_zero == 0 or clipping > 0 or not duration_ok:
        status = "FAIL"
    elif abs(dc_offset) > DC_WARN_THRESHOLD:
        status = "WARN"
    else:
        status = "PASS"

    report = {
        "report_version": "0",
        "report_id": f"qa-{sha256_file(target)[:16]}",
        "artifact_sha256": sha256_file(target),
        "artifact_size_bytes": target.stat().st_size,
        "status": status,
        "container": {
            "valid": True,
            "format": "wav",
            "sample_rate": sample_rate,
            "channels": channels,
            "sample_width_bytes": sample_width,
            "bit_depth": bits,
            "frame_count": frame_count,
        },
        "signal": {
            "non_zero_sample_count": non_zero,
            "peak_normalized": round(peak_normalized, 9),
            "clipping_sample_count": clipping,
            "dc_offset_normalized": round(dc_offset, 9),
        },
        "duration": {
            "actual_seconds": round(actual_seconds, 9),
            "target_seconds": float(target_seconds),
            "tolerance_seconds": tolerance,
            "within_tolerance": duration_ok,
        },
        "loudness": {"integrated_lufs": None, "measurement_status": "UNKNOWN"},
    }
    validate_contract(report, "audio-quality-report-v0.schema.json")
    return report
