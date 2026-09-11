from __future__ import annotations

import copy
import json
import struct
import wave
from pathlib import Path

import pytest

from musica.audio_qa import analyze_wav
from musica.compiler import compile_blueprint
from musica.contracts import validate_contract
from musica.evidence import canonical_json_bytes
from musica.renderer import (
    REFERENCE_RENDERER_ID,
    RendererError,
    build_renderer_request,
    music_ir_sha256,
    reference_renderer_capability,
    render_with_registry,
    verify_result_artifacts,
)

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"


def _ir() -> tuple[dict, float]:
    blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return compile_blueprint(blueprint), float(blueprint["project"]["duration_seconds"])


def _request(ir: dict, duration: float, **overrides):
    values = {
        "request_id": "m5-r1-test",
        "renderer_id": REFERENCE_RENDERER_ID,
        "outputs": ["midi", "wav"],
        "duration_seconds": duration,
        "sample_rate": 22050,
        "channels": 1,
        "sample_width_bytes": 2,
    }
    values.update(overrides)
    return build_renderer_request(ir, **values)


def _write_pcm16(path: Path, samples: list[int], *, sample_rate: int = 8000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def test_reference_renderer_contract_is_exact_bound_and_reproducible(tmp_path: Path) -> None:
    ir, duration = _ir()
    before = canonical_json_bytes(ir)
    request = _request(ir, duration)
    capability = reference_renderer_capability()

    validate_contract(request, "renderer-request-v0.schema.json")
    validate_contract(capability, "renderer-capability-v0.schema.json")
    assert request["music_ir_sha256"] == music_ir_sha256(ir)

    result_a = render_with_registry(request, ir, tmp_path / "a")
    result_b = render_with_registry(request, ir, tmp_path / "b")

    validate_contract(result_a, "renderer-result-v0.schema.json")
    validate_contract(result_b, "renderer-result-v0.schema.json")
    assert canonical_json_bytes(ir) == before
    assert result_a["music_ir_sha256"] == request["music_ir_sha256"]
    assert result_a["status"] == "SUCCESS"
    assert result_a["audio_quality"]["status"] in {"PASS", "WARN"}
    # One render may carry the adapter claim but cannot self-verify reproducibility.
    assert result_a["reproducibility"] == {"claim": "byte_exact", "verified": False}

    hashes_a = {item["role"]: item["sha256"] for item in result_a["artifacts"]}
    hashes_b = {item["role"]: item["sha256"] for item in result_b["artifacts"]}
    assert hashes_a == hashes_b
    assert set(hashes_a) == {"midi", "wav"}
    verify_result_artifacts(result_a, tmp_path / "a")
    verify_result_artifacts(result_b, tmp_path / "b")

    qa_files = list((tmp_path / "a").rglob("audio-quality.json"))
    assert len(qa_files) == 1
    qa = json.loads(qa_files[0].read_text(encoding="utf-8"))
    validate_contract(qa, "audio-quality-report-v0.schema.json")
    assert qa["container"]["valid"] is True
    assert qa["container"]["sample_rate"] == 22050
    assert qa["container"]["channels"] == 1
    assert qa["container"]["sample_width_bytes"] == 2
    assert qa["signal"]["non_zero_sample_count"] > 0
    assert qa["signal"]["clipping_sample_count"] == 0
    assert qa["duration"]["within_tolerance"] is True
    assert qa["loudness"] == {"integrated_lufs": None, "measurement_status": "UNKNOWN"}


def test_renderer_rejects_music_ir_hash_mismatch(tmp_path: Path) -> None:
    ir, duration = _ir()
    request = _request(ir, duration)
    request["music_ir_sha256"] = "0" * 64
    with pytest.raises(RendererError, match="Music IR hash"):
        render_with_registry(request, ir, tmp_path)


def test_renderer_rejects_unknown_renderer(tmp_path: Path) -> None:
    ir, duration = _ir()
    request = _request(ir, duration, renderer_id="unknown-renderer")
    with pytest.raises(RendererError, match="unknown renderer"):
        render_with_registry(request, ir, tmp_path)


def test_renderer_rejects_capability_mismatch(tmp_path: Path) -> None:
    ir, duration = _ir()
    request = _request(ir, duration, sample_rate=32000)
    with pytest.raises(RendererError, match="capability mismatch"):
        render_with_registry(request, ir, tmp_path)


def test_renderer_artifact_tamper_is_detected(tmp_path: Path) -> None:
    ir, duration = _ir()
    request = _request(ir, duration, outputs=["midi"])
    result = render_with_registry(request, ir, tmp_path)
    artifact = result["artifacts"][0]
    path = tmp_path / artifact["path"]
    path.write_bytes(path.read_bytes() + b"tamper")
    with pytest.raises(RendererError, match="size mismatch|hash mismatch"):
        verify_result_artifacts(result, tmp_path)


def test_renderer_result_path_traversal_is_rejected(tmp_path: Path) -> None:
    ir, duration = _ir()
    request = _request(ir, duration, outputs=["midi"])
    result = render_with_registry(request, ir, tmp_path)
    tampered = copy.deepcopy(result)
    tampered["artifacts"][0]["path"] = "../escape.mid"
    with pytest.raises(RendererError, match="workspace traversal"):
        verify_result_artifacts(tampered, tmp_path)


def test_audio_quality_rejects_corrupt_silent_clipped_and_bad_duration(tmp_path: Path) -> None:
    corrupt = tmp_path / "corrupt.wav"
    corrupt.write_bytes(b"not a wav container")
    corrupt_report = analyze_wav(corrupt, target_seconds=1.0)
    assert corrupt_report["status"] == "FAIL"
    assert corrupt_report["container"]["valid"] is False

    silent = tmp_path / "silent.wav"
    _write_pcm16(silent, [0] * 8000)
    silent_report = analyze_wav(silent, target_seconds=1.0)
    assert silent_report["status"] == "FAIL"
    assert silent_report["signal"]["non_zero_sample_count"] == 0

    clipped = tmp_path / "clipped.wav"
    _write_pcm16(clipped, [32767] * 8000)
    clipped_report = analyze_wav(clipped, target_seconds=1.0)
    assert clipped_report["status"] == "FAIL"
    assert clipped_report["signal"]["clipping_sample_count"] == 8000

    short = tmp_path / "short.wav"
    _write_pcm16(short, [1000, -1000] * 4000)
    short_report = analyze_wav(short, target_seconds=2.0)
    assert short_report["status"] == "FAIL"
    assert short_report["duration"]["within_tolerance"] is False
