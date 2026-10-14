"""Reproducible PLUG-R2-B K0 detached causal two-path audio evidence.

This validates the *numerical reference kernel*, NOT accepted plugin placement,
algorithmic latency reporting from third-party binaries, or integrated DAW PDC.
"""
from __future__ import annotations

import copy
import hashlib
import io
import os
import shutil
import struct
import wave
from pathlib import Path
from typing import Any

from .contracts import ContractError
from .evidence import canonical_json_bytes
from .plugin_alignment_reference import (
    build_two_path_alignment_plan,
    render_two_path_alignment,
    validate_two_path_alignment_plan,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATHS = [
    ROOT / "schemas" / "plugin-two-path-alignment-reference-v0.schema.json",
    ROOT / "src" / "musica" / "plugin_alignment_reference.py",
    ROOT / "src" / "musica" / "plug_r2b_evidence.py",
    ROOT / "tests" / "test_plug_r2b_two_path_alignment_reference.py",
    ROOT / ".github" / "workflows" / "plug-r2b-two-path-reference-evidence.yml",
    ROOT / "docs" / "PLUG_R2B_REFERENCE_KERNEL.md",
]


def _sha(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value))


def _wav(channel: int, *, sample: int, frame_index: int = 4, frames: int = 128) -> bytes:
    pcm = bytearray()
    for frame in range(frames):
        sample_pair = [0, 0]
        if frame == frame_index:
            sample_pair[channel] = sample
        pcm += struct.pack("<hh", *sample_pair)
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(8000)
        writer.writeframes(bytes(pcm))
    return stream.getvalue()


def _decode(raw: bytes) -> list[tuple[int, int]]:
    with wave.open(io.BytesIO(raw)) as reader:
        assert reader.getnchannels() == 2 and reader.getsampwidth() == 2
        assert reader.getframerate() == 8000 and reader.getsampwidth() == 2
        data = reader.readframes(reader.getnframes())
    return list(struct.iter_unpack("<hh", data))


def _nonzero_on_channel(frames: list[tuple[int, int]], channel: int) -> list[int]:
    return [index for index, frame in enumerate(frames) if frame[channel] != 0]


def _paths(*, creative_delay_a: int = 0, bypass_a: bool = False) -> list[dict[str, Any]]:
    return [
        {"path_id": "PATH-A", "algorithmic_latency_frames": 3,
         "creative_delay_frames": creative_delay_a, "bypass": bypass_a},
        {"path_id": "PATH-B", "algorithmic_latency_frames": 9,
         "creative_delay_frames": 0, "bypass": False},
    ]


def generate_plug_r2b_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    inputs = {
        "PATH-A": _wav(0, sample=8000),
        "PATH-B": _wav(1, sample=-6000),
    }
    active = build_two_path_alignment_plan(
        _paths(), sample_rate_hz=8000, input_wav_by_path=inputs
    )
    repeated = build_two_path_alignment_plan(
        _paths(), sample_rate_hz=8000, input_wav_by_path=inputs
    )
    assert active == repeated
    validate_two_path_alignment_plan(active)

    dry = render_two_path_alignment(
        active, input_wav_by_path=inputs, compensate=False
    )
    wet = render_two_path_alignment(
        active, input_wav_by_path=inputs, compensate=True
    )
    wet_repeat = render_two_path_alignment(
        active, input_wav_by_path=inputs, compensate=True
    )
    assert wet.wav_bytes == wet_repeat.wav_bytes
    dry_pcm = _decode(dry.wav_bytes)
    wet_pcm = _decode(wet.wav_bytes)
    assert _nonzero_on_channel(dry_pcm, 0) == [7]
    assert _nonzero_on_channel(dry_pcm, 1) == [13]
    assert _nonzero_on_channel(wet_pcm, 0) == [13]
    assert _nonzero_on_channel(wet_pcm, 1) == [13]
    assert wet_pcm[13] == (8000, -6000)
    assert len(wet_pcm) == 128

    creative = build_two_path_alignment_plan(
        _paths(creative_delay_a=5), sample_rate_hz=8000,
        input_wav_by_path=inputs,
    )
    creative_render = render_two_path_alignment(
        creative, input_wav_by_path=inputs
    )
    creative_pcm = _decode(creative_render.wav_bytes)
    assert _nonzero_on_channel(creative_pcm, 0) == [18]
    assert _nonzero_on_channel(creative_pcm, 1) == [13]

    bypass = build_two_path_alignment_plan(
        _paths(bypass_a=True), sample_rate_hz=8000,
        input_wav_by_path=inputs,
    )
    bypass_render = render_two_path_alignment(
        bypass, input_wav_by_path=inputs
    )
    bypass_pcm = _decode(bypass_render.wav_bytes)
    assert _nonzero_on_channel(bypass_pcm, 0) == [13]
    assert _nonzero_on_channel(bypass_pcm, 1) == [13]
    assert [p["compensation_frames"] for p in bypass["paths"]] == [9, 0]

    before = copy.deepcopy(active)
    error_blocked = False
    try:
        render_two_path_alignment(
            active, input_wav_by_path=inputs,
            force_error_path_ids={"PATH-A"},
        )
    except ContractError:
        error_blocked = True
    assert error_blocked and active == before

    source_forgery_blocked = False
    forged_input = dict(inputs)
    forged_input["PATH-A"] = _wav(0, sample=7000)
    try:
        render_two_path_alignment(
            active, input_wav_by_path=forged_input,
        )
    except ContractError:
        source_forgery_blocked = True
    assert source_forgery_blocked

    for path_id, blob in inputs.items():
        (out / f"input-{path_id.lower()}.wav").write_bytes(blob)
    for name, blob in [
        ("noncompensated.wav", dry.wav_bytes),
        ("compensated.wav", wet.wav_bytes),
        ("creative-delay-preserved.wav", creative_render.wav_bytes),
        ("bypass-compensated.wav", bypass_render.wav_bytes),
    ]:
        (out / name).write_bytes(blob)
    for name, value in [
        ("plan-active.json", active),
        ("plan-creative-delay.json", creative),
        ("plan-bypass.json", bypass),
    ]:
        _write_json(out / name, value)
    _write_json(out / "proof.json", {
        "evidence_version": "0",
        "classification": "DETACHED_TWO_PATH_CAUSAL_REFERENCE_NOT_ACCEPTED_DAW_PDC",
        "sample_rate_hz": 8000,
        "duration_frames": 128,
        "uncompensated_left_impulse_frame": 7,
        "uncompensated_right_impulse_frame": 13,
        "compensated_left_impulse_frame": 13,
        "compensated_right_impulse_frame": 13,
        "aligned_compensated_stereo_sample": [8000, -6000],
        "creative_delay_left_impulse_frame": 18,
        "creative_delay_right_impulse_frame": 13,
        "bypass_compensated_left_impulse_frame": 13,
        "bypass_compensated_right_impulse_frame": 13,
        "processor_forced_error_fail_closed": True,
        "forged_wav_source_fail_closed": True,
        "repeat_plan_and_audio_byte_exact": True,
        "host_pdc_integrated": False,
        "algorithmic_latency_provenance": "simulated_explicit_reference_only",
        "accepted_blueprint_mutation_authorized": False,
    })
    files = [
        {"path": p.name, "sha256": _sha(p.read_bytes()), "bytes": p.stat().st_size}
        for p in sorted(out.iterdir()) if p.name != "manifest.json"
    ]
    sources = [
        {"path": p.relative_to(ROOT).as_posix(),
         "sha256": _sha(p.read_bytes()), "bytes": p.stat().st_size}
        for p in CONTRACT_PATHS
    ]
    manifest = {
        "manifest_version": "0",
        "classification": "PLUG_R2B_DETACHED_REFERENCE_NO_HOST_PDC_CLAIM",
        "artifacts": files,
        "contract_inventory": sources,
    }
    _write_json(out / "manifest.json", manifest)
    return manifest


def main() -> None:
    root = os.environ.get(
        "MUSICA_PLUG_R2B_EVIDENCE_OUT",
        "artifacts/plug-r2b-two-path-reference",
    )
    result = generate_plug_r2b_evidence(root)
    print(f"PLUG-R2B K0 evidence: {len(result['artifacts'])} payloads, "
          f"{len(result['contract_inventory'])} contracts")


if __name__ == "__main__":
    main()
