from __future__ import annotations

import json
from pathlib import Path

import pytest

from musica.compiler import compile_blueprint
from musica.contracts import validate_contract
from musica.evidence import canonical_json_bytes, sha256_file
from musica.fluidsynth_renderer import (
    FLUIDSYNTH_RENDERER_ID,
    FluidSynthRendererAdapter,
    build_fluidsynth_request,
    discover_fluidsynth,
)
from musica.renderer import RendererError, render_with_registry, verify_result_artifacts

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"


def _ir() -> tuple[dict, float]:
    blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return compile_blueprint(blueprint), float(blueprint["project"]["duration_seconds"])


def _fake_fluidsynth(
    path: Path,
    *,
    version: str = "2.6.0",
    exit_code: int = 0,
    raw_duration_seconds: float = 20.0,
) -> Path:
    script = f'''#!/usr/bin/env python3
import pathlib
import struct
import sys
import wave

VERSION = {version!r}
EXIT_CODE = {exit_code}
RAW_DURATION_SECONDS = {raw_duration_seconds!r}
if "--version" in sys.argv:
    print(f"FluidSynth runtime version {{VERSION}}")
    raise SystemExit(EXIT_CODE)
if EXIT_CODE:
    print("synthetic renderer failure", file=sys.stderr)
    raise SystemExit(EXIT_CODE)
args = sys.argv[1:]
out = pathlib.Path(args[args.index("-F") + 1])
sample_rate = int(args[args.index("-r") + 1])
if args[args.index("-T") + 1] != "wav":
    raise SystemExit(21)
if args[args.index("-O") + 1] != "s16":
    raise SystemExit(22)
out.parent.mkdir(parents=True, exist_ok=True)
remaining = int(round(sample_rate * RAW_DURATION_SECONDS))
frame = struct.pack("<hh", 1200, -1200)
with wave.open(str(out), "wb") as handle:
    handle.setnchannels(2)
    handle.setsampwidth(2)
    handle.setframerate(sample_rate)
    while remaining:
        count = min(4096, remaining)
        handle.writeframes(frame * count)
        remaining -= count
'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)
    return path


def _adapter(
    tmp_path: Path,
    *,
    version: str = "2.6.0",
    raw_duration_seconds: float = 20.0,
) -> tuple[FluidSynthRendererAdapter, Path]:
    executable = _fake_fluidsynth(
        tmp_path / "fake-fluidsynth",
        version=version,
        raw_duration_seconds=raw_duration_seconds,
    )
    soundfont = tmp_path / "FluidR3_GM.sf2"
    soundfont.write_bytes(b"synthetic-soundfont-fixture-not-real-sf2")
    return (
        FluidSynthRendererAdapter(
            executable=executable,
            soundfont_path=soundfont,
            soundfont_id="FluidR3_GM-3.1-test-fixture",
        ),
        soundfont,
    )


def test_fluidsynth_adapter_exact_bind_provenance_and_stereo_qa(tmp_path: Path) -> None:
    ir, duration = _ir()
    before = canonical_json_bytes(ir)
    adapter, soundfont = _adapter(tmp_path)
    request = build_fluidsynth_request(
        ir,
        request_id="m5-r2-unit-a",
        soundfont_id="FluidR3_GM-3.1-test-fixture",
        soundfont_sha256=sha256_file(soundfont),
        duration_seconds=duration,
    )

    validate_contract(request, "renderer-request-v0.schema.json")
    capability = adapter.capability()
    validate_contract(capability, "renderer-capability-v0.schema.json")
    assert capability["renderer_id"] == FLUIDSYNTH_RENDERER_ID
    assert capability["audio"]["sample_rates"] == [48000]
    assert capability["requirements"] == {
        "external_binary": True,
        "plugin_host": False,
        "network": False,
    }
    assert capability["reproducibility"] == "stable_parameters"

    result = adapter.render(request, ir, tmp_path / "workspace")
    validate_contract(result, "renderer-result-v0.schema.json")
    assert canonical_json_bytes(ir) == before
    assert result["status"] == "SUCCESS"
    assert result["music_ir_sha256"] == request["music_ir_sha256"]
    assert result["reproducibility"] == {"claim": "stable_parameters", "verified": False}
    assert result["audio_quality"]["status"] == "PASS"
    assert result["provenance"]["manifest_sha256"]

    qa_path = next((tmp_path / "workspace").rglob("audio-quality.json"))
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    assert qa["container"]["sample_rate"] == 48000
    assert qa["container"]["channels"] == 2
    assert qa["container"]["sample_width_bytes"] == 2
    assert qa["duration"]["actual_seconds"] == 20.0
    assert qa["signal"]["clipping_sample_count"] == 0

    provenance_path = tmp_path / "workspace" / result["provenance"]["manifest_path"]
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    assert provenance["engine"]["version"] == "2.6.0"
    assert provenance["resources"][0]["sha256"] == sha256_file(soundfont)
    assert provenance["render_settings"]["sample_rate"] == 48000
    assert provenance["render_settings"]["channels"] == 2
    assert provenance["render_settings"]["duration_normalization"]["normalization_applied"] is False
    assert provenance["project_authority"] is False
    verify_result_artifacts(result, tmp_path / "workspace")


def test_fluidsynth_trims_engine_tail_but_never_pads_underrun(tmp_path: Path) -> None:
    ir, duration = _ir()
    adapter, soundfont = _adapter(tmp_path / "tail", raw_duration_seconds=22.5)
    request = build_fluidsynth_request(
        ir,
        request_id="tail-normalization",
        soundfont_id="FluidR3_GM-3.1-test-fixture",
        soundfont_sha256=sha256_file(soundfont),
        duration_seconds=duration,
    )
    result = adapter.render(request, ir, tmp_path / "tail-workspace")
    qa_path = next((tmp_path / "tail-workspace").rglob("audio-quality.json"))
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    assert qa["duration"]["actual_seconds"] == 20.0
    provenance_path = tmp_path / "tail-workspace" / result["provenance"]["manifest_path"]
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    normalization = provenance["render_settings"]["duration_normalization"]
    assert normalization["normalization_applied"] is True
    assert normalization["padding_applied"] is False
    assert normalization["raw_duration_seconds"] == 22.5
    assert normalization["target_duration_seconds"] == 20.0
    assert normalization["trimmed_frame_count"] == 120000
    assert normalization["raw_sha256"]

    short_adapter, short_soundfont = _adapter(tmp_path / "short", raw_duration_seconds=19.0)
    short_request = build_fluidsynth_request(
        ir,
        request_id="underrun-rejected",
        soundfont_id="FluidR3_GM-3.1-test-fixture",
        soundfont_sha256=sha256_file(short_soundfont),
        duration_seconds=duration,
    )
    with pytest.raises(RendererError, match="shorter than requested duration"):
        short_adapter.render(short_request, ir, tmp_path / "short-workspace")


def test_fluidsynth_independent_runs_are_compared_outside_renderer_result(tmp_path: Path) -> None:
    ir, duration = _ir()
    adapter, soundfont = _adapter(tmp_path)
    request = build_fluidsynth_request(
        ir,
        request_id="m5-r2-repeat",
        soundfont_id="FluidR3_GM-3.1-test-fixture",
        soundfont_sha256=sha256_file(soundfont),
        duration_seconds=duration,
    )
    a = adapter.render(request, ir, tmp_path / "a")
    b = adapter.render(request, ir, tmp_path / "b")
    hashes_a = {item["role"]: item["sha256"] for item in a["artifacts"]}
    hashes_b = {item["role"]: item["sha256"] for item in b["artifacts"]}
    assert hashes_a == hashes_b
    assert a["reproducibility"]["verified"] is False
    assert b["reproducibility"]["verified"] is False


def test_fluidsynth_rejects_soundfont_hash_and_id_mismatch(tmp_path: Path) -> None:
    ir, duration = _ir()
    adapter, soundfont = _adapter(tmp_path)
    request = build_fluidsynth_request(
        ir,
        request_id="bad-resource",
        soundfont_id="FluidR3_GM-3.1-test-fixture",
        soundfont_sha256="0" * 64,
        duration_seconds=duration,
    )
    with pytest.raises(RendererError, match="SoundFont hash mismatch"):
        adapter.render(request, ir, tmp_path / "hash")

    request = build_fluidsynth_request(
        ir,
        request_id="bad-id",
        soundfont_id="wrong-content-id",
        soundfont_sha256=sha256_file(soundfont),
        duration_seconds=duration,
    )
    with pytest.raises(RendererError, match="resource id"):
        adapter.render(request, ir, tmp_path / "id")


def test_fluidsynth_rejects_missing_resource_and_capability_mismatch(tmp_path: Path) -> None:
    ir, duration = _ir()
    adapter, soundfont = _adapter(tmp_path)
    request = build_fluidsynth_request(
        ir,
        request_id="missing-resource",
        soundfont_id="FluidR3_GM-3.1-test-fixture",
        soundfont_sha256=sha256_file(soundfont),
        duration_seconds=duration,
    )
    request.pop("resources")
    with pytest.raises(RendererError, match="exactly one SoundFont"):
        adapter.render(request, ir, tmp_path / "missing")

    request = build_fluidsynth_request(
        ir,
        request_id="bad-rate",
        soundfont_id="FluidR3_GM-3.1-test-fixture",
        soundfont_sha256=sha256_file(soundfont),
        duration_seconds=duration,
        sample_rate=32000,
    )
    with pytest.raises(RendererError, match="capability mismatch"):
        adapter.render(request, ir, tmp_path / "rate")


def test_fluidsynth_runtime_version_and_missing_binary_fail_closed(tmp_path: Path) -> None:
    wrong = _fake_fluidsynth(tmp_path / "wrong-version", version="2.5.4")
    with pytest.raises(RendererError, match="version mismatch"):
        discover_fluidsynth(wrong)
    with pytest.raises(RendererError, match="not found"):
        discover_fluidsynth(tmp_path / "does-not-exist")


def test_fluidsynth_provenance_tamper_is_detected(tmp_path: Path) -> None:
    ir, duration = _ir()
    adapter, soundfont = _adapter(tmp_path)
    request = build_fluidsynth_request(
        ir,
        request_id="provenance-tamper",
        soundfont_id="FluidR3_GM-3.1-test-fixture",
        soundfont_sha256=sha256_file(soundfont),
        duration_seconds=duration,
    )
    result = adapter.render(request, ir, tmp_path / "workspace")
    provenance_path = tmp_path / "workspace" / result["provenance"]["manifest_path"]
    provenance_path.write_text("{}", encoding="utf-8")
    with pytest.raises(RendererError, match="provenance hash mismatch"):
        verify_result_artifacts(result, tmp_path / "workspace")


def test_registry_uses_environment_without_shell_or_caller_output_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ir, duration = _ir()
    executable = _fake_fluidsynth(tmp_path / "bin with spaces" / "fluidsynth")
    soundfont = tmp_path / "content with spaces" / "FluidR3_GM.sf2"
    soundfont.parent.mkdir(parents=True, exist_ok=True)
    soundfont.write_bytes(b"synthetic-soundfont-fixture-not-real-sf2")

    monkeypatch.setenv("MUSICA_FLUIDSYNTH_BIN", str(executable))
    monkeypatch.setenv("MUSICA_FLUIDSYNTH_SOUNDFONT", str(soundfont))
    monkeypatch.setenv("MUSICA_FLUIDSYNTH_SOUNDFONT_ID", "FluidR3_GM-3.1-test-fixture")
    request = build_fluidsynth_request(
        ir,
        request_id="../../escape;touch-pwned",
        soundfont_id="FluidR3_GM-3.1-test-fixture",
        soundfont_sha256=sha256_file(soundfont),
        duration_seconds=duration,
    )
    workspace = tmp_path / "workspace"
    result = render_with_registry(request, ir, workspace)
    verify_result_artifacts(result, workspace)
    assert not (tmp_path / "pwned").exists()
    for artifact in result["artifacts"]:
        assert ".." not in Path(artifact["path"]).parts
