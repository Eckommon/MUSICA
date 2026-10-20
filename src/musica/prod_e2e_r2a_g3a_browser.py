"""R2A-G3A: real-browser standard-resolution two-track/bus/gain lane proof.

Exercises the G1 → G2B → G2C trusted user-operated flow at exact 44.1/48 kHz;
no actual device, resampling, arbitrary-length upload or real plugin claim.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import struct
import time
import wave
from pathlib import Path

from .evidence import write_canonical_json
from .prod_e2e_r1b_g2c_browser import run_suite as seed_g2c


def run_suite(destination: str | Path, *, sample_rate_hz: int) -> dict:
    if sample_rate_hz not in {44100, 48000}:
        raise ValueError("G3A must prove one explicit standard source rate, 44100 or 48000")
    out = Path(destination)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    start_monotonic = time.perf_counter()
    seed = out / "integrated-g2c"
    g2c = seed_g2c(seed, sample_rate_hz=sample_rate_hz)

    g1 = json.loads((seed / "seed-g2b" / "seed-g1" / "proof.json").read_text(encoding="utf-8"))
    g2b = json.loads((seed / "seed-g2b" / "proof.json").read_text(encoding="utf-8"))
    assert g1["output_sample_rate_hz"] == g2b["sample_rate_hz"] == g2c["sample_rate_hz"] == sample_rate_hz
    assert g1["accepted_tracks"] == g1["accepted_clips"] == 2
    assert g2b["two_bus_plus_master_manual_preview_and_accept"]
    assert g2c["explicit_accept"] and g2c["rendered_sound_changed"]

    accepted = (seed / "gain-automated.wav").read_bytes()
    reopened = (seed / "gain-reopened.wav").read_bytes()
    assert accepted == reopened, "reopened standard-rate WAV differs"
    with wave.open(io.BytesIO(accepted), "rb") as stream:
        assert stream.getnchannels() == 2 and stream.getsampwidth() == 2
        assert stream.getframerate() == sample_rate_hz
        assert stream.getnframes() == 12 * sample_rate_hz
        samples = struct.unpack(
            "<" + "h" * (stream.getnframes() * 2),
            stream.readframes(stream.getnframes()),
        )
    left = samples[::2]
    right = samples[1::2]
    source_frames = 2 * sample_rate_hz
    assert all(left[i] or right[i] for i in range(source_frames)), "missing source frames"
    assert all(x == 0 for x in left[source_frames:]), "unexpected left tail"
    assert all(x == 0 for x in right[source_frames:]), "unexpected right tail"
    left_peaks = [
        max(abs(x) for x in left[start:start + 100])
        for start in (0, sample_rate_hz // 2, sample_rate_hz,
                      sample_rate_hz * 3 // 2, sample_rate_hz * 19 // 10)
    ]
    right_peaks = [
        max(abs(x) for x in right[start:start + 100])
        for start in (0, sample_rate_hz // 2, sample_rate_hz,
                      sample_rate_hz * 3 // 2, sample_rate_hz * 19 // 10)
    ]
    assert all(left_peaks[i] > left_peaks[i+1] for i in range(4)), left_peaks
    assert right_peaks == [6200] * 5, right_peaks
    peak = max(abs(v) for v in samples)
    clipped = sum(abs(v) >= 32767 for v in samples)
    assert peak == 6200 and clipped == 0
    sha = hashlib.sha256(accepted).hexdigest()
    assert sha == g2c["accepted_wav_sha256"]
    (out / "standard-accepted.wav").write_bytes(accepted)
    (out / "standard-reopened.wav").write_bytes(reopened)

    proof = {
        "milestone": "PROD-E2E-R2A-G3A",
        "real_automated_chromium_g1_g2b_g2c": True,
        "user_file_picker_two_distinct_wavs": True,
        "sample_rate_hz": sample_rate_hz,
        "output_frames": 12 * sample_rate_hz,
        "duration_seconds": 12,
        "channels": 2,
        "sample_width_bytes": 2,
        "source_frames_each": source_frames,
        "accepted_track_and_clip_count": 2,
        "accepted_bus_count": 2,
        "accepted_native_gain_lane_count": 1,
        "manual_preview_accept_enforced": True,
        "left_gain_peaks": left_peaks,
        "unaffected_right_peaks": right_peaks,
        "absolute_pcm_peak": peak,
        "clipped_scalar_samples": clipped,
        "accepted_wav_sha256": sha,
        "reopened_wav_byte_exact": True,
        "source_resampling_performed": False,
        "automated_browser_e2e_elapsed_seconds": round(time.perf_counter() - start_monotonic, 3),
        "mixed_rate_import_proven": False,
        "real_audio_device_proven": False,
        "real_plugin_binary_proven": False,
        "three_minute_song_proven": False,
        "human_usability_study": False,
    }
    write_canonical_json(out / "proof.json", proof)
    return proof


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_suite(args.out, sample_rate_hz=args.rate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
