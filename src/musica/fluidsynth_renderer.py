"""Bounded FluidSynth adapter for MUSICA M5-R2.

MUSICA M5-R2용 제한된 FluidSynth adapter.

The adapter treats FluidSynth and SoundFont content as external renderer infrastructure.
It consumes exact-hash-bound Music IR lowered to MIDI and never receives project mutation
authority.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any

from .audio_qa import analyze_wav
from .contracts import validate_contract
from .evidence import sha256_file, write_canonical_json
from .render import render_midi
from .renderer import (
    RendererError,
    _artifact,
    _safe_output_root,
    _validate_request_against_capability,
    build_renderer_request,
    music_ir_sha256,
    verify_result_artifacts,
)

FLUIDSYNTH_RENDERER_ID = "musica-fluidsynth-local"
FLUIDSYNTH_ADAPTER_VERSION = "0.1.0"
FLUIDSYNTH_TARGET_VERSION = "2.6.0"
DEFAULT_RENDER_TIMEOUT_SECONDS = 120.0

_VERSION_RE = re.compile(r"\b(\d+\.\d+\.\d+)\b")


def _resolve_executable(value: str | Path) -> Path:
    raw = str(value)
    candidate = Path(raw).expanduser()
    if candidate.is_absolute() or candidate.parent != Path("."):
        resolved = candidate.resolve()
        if not resolved.is_file():
            raise RendererError(f"FluidSynth executable not found: {raw}")
        return resolved
    found = shutil.which(raw)
    if not found:
        raise RendererError(f"FluidSynth executable not found on PATH: {raw}")
    resolved = Path(found).resolve()
    if not resolved.is_file():
        raise RendererError(f"FluidSynth executable is not a file: {resolved}")
    return resolved


def discover_fluidsynth(
    executable: str | Path,
    *,
    expected_version: str = FLUIDSYNTH_TARGET_VERSION,
) -> dict[str, Any]:
    """Resolve one FluidSynth binary and prove its exact runtime version."""

    resolved = _resolve_executable(executable)
    try:
        completed = subprocess.run(
            [str(resolved), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10.0,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RendererError(f"FluidSynth version probe failed: {exc}") from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()[-512:]
        raise RendererError(f"FluidSynth version probe returned {completed.returncode}: {detail}")
    combined = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    match = _VERSION_RE.search(combined)
    if not match:
        raise RendererError("FluidSynth version probe did not expose a semantic version")
    version = match.group(1)
    if expected_version and version != expected_version:
        raise RendererError(
            f"FluidSynth version mismatch: expected {expected_version}, discovered {version}"
        )
    return {
        "name": "FluidSynth",
        "version": version,
        "executable": resolved,
        "executable_sha256": sha256_file(resolved),
    }


def _resolve_soundfont(path: str | Path) -> dict[str, Any]:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file() or resolved.stat().st_size <= 0:
        raise RendererError(f"SoundFont not found or empty: {resolved}")
    return {
        "path": resolved,
        "sha256": sha256_file(resolved),
        "size_bytes": resolved.stat().st_size,
    }


def _normalize_wav_duration(
    raw_path: Path,
    final_path: Path,
    *,
    target_seconds: float,
) -> dict[str, Any]:
    """Deterministically trim renderer tail to the explicit MUSICA duration contract.

    The raw engine output is not a canonical RendererResult artifact. Its hash and
    duration are recorded in provenance. Underruns fail closed; MUSICA never pads or
    invents audio that FluidSynth did not render.
    """

    try:
        with wave.open(str(raw_path), "rb") as source:
            channels = int(source.getnchannels())
            sample_width = int(source.getsampwidth())
            sample_rate = int(source.getframerate())
            frame_count = int(source.getnframes())
            compression = source.getcomptype()
            compression_name = source.getcompname()
            if compression != "NONE":
                raise RendererError("FluidSynth raw WAV must be uncompressed PCM")
            target_frames = int(round(float(target_seconds) * sample_rate))
            if target_frames <= 0:
                raise RendererError("FluidSynth target duration produced no frames")
            if frame_count < target_frames:
                raise RendererError(
                    "FluidSynth raw WAV is shorter than requested duration: "
                    f"raw_frames={frame_count}, target_frames={target_frames}"
                )
            frames = source.readframes(target_frames)
    except (wave.Error, EOFError) as exc:
        raise RendererError(f"FluidSynth raw WAV could not be normalized: {exc}") from exc

    final_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(final_path), "wb") as target:
        target.setnchannels(channels)
        target.setsampwidth(sample_width)
        target.setframerate(sample_rate)
        target.setcomptype(compression, compression_name)
        target.writeframes(frames)

    return {
        "policy": "trim_tail_to_requested_duration_v0",
        "raw_sha256": sha256_file(raw_path),
        "raw_size_bytes": raw_path.stat().st_size,
        "raw_frame_count": frame_count,
        "raw_duration_seconds": frame_count / sample_rate,
        "target_frame_count": target_frames,
        "target_duration_seconds": float(target_seconds),
        "trimmed_frame_count": frame_count - target_frames,
        "normalization_applied": frame_count != target_frames,
        "padding_applied": False,
    }


def build_fluidsynth_request(
    music_ir: dict[str, Any],
    *,
    request_id: str,
    soundfont_id: str,
    soundfont_sha256: str,
    duration_seconds: float,
    outputs: list[str] | None = None,
    seed: int | None = None,
    sample_rate: int = 48000,
    sample_width_bytes: int = 2,
    quality_preferences: list[str] | None = None,
) -> dict[str, Any]:
    """Build an exact Music-IR + SoundFont-hash-bound R2 request."""

    return build_renderer_request(
        music_ir,
        request_id=request_id,
        outputs=outputs or ["midi", "wav"],
        renderer_id=FLUIDSYNTH_RENDERER_ID,
        seed=seed,
        duration_seconds=duration_seconds,
        sample_rate=sample_rate,
        channels=2,
        sample_width_bytes=sample_width_bytes,
        quality_preferences=quality_preferences,
        resources=[
            {
                "role": "soundfont",
                "resource_id": soundfont_id,
                "sha256": soundfont_sha256,
            }
        ],
    )


class FluidSynthRendererAdapter:
    """External-process adapter that keeps FluidSynth below the M5-R1 authority boundary."""

    def __init__(
        self,
        *,
        executable: str | Path,
        soundfont_path: str | Path,
        soundfont_id: str,
        expected_version: str = FLUIDSYNTH_TARGET_VERSION,
        render_timeout_seconds: float = DEFAULT_RENDER_TIMEOUT_SECONDS,
    ) -> None:
        if not soundfont_id:
            raise RendererError("SoundFont resource id must be non-empty")
        if render_timeout_seconds <= 0:
            raise RendererError("FluidSynth render timeout must be positive")
        self._runtime = discover_fluidsynth(executable, expected_version=expected_version)
        self._soundfont = _resolve_soundfont(soundfont_path)
        self._soundfont_id = soundfont_id
        self._timeout = float(render_timeout_seconds)

    @classmethod
    def from_environment(cls) -> "FluidSynthRendererAdapter":
        soundfont = os.environ.get("MUSICA_FLUIDSYNTH_SOUNDFONT")
        if not soundfont:
            raise RendererError("MUSICA_FLUIDSYNTH_SOUNDFONT is required for FluidSynth renderer")
        return cls(
            executable=os.environ.get("MUSICA_FLUIDSYNTH_BIN", "fluidsynth"),
            soundfont_path=soundfont,
            soundfont_id=os.environ.get("MUSICA_FLUIDSYNTH_SOUNDFONT_ID", "external-soundfont"),
            expected_version=os.environ.get(
                "MUSICA_FLUIDSYNTH_EXPECTED_VERSION", FLUIDSYNTH_TARGET_VERSION
            ),
        )

    def capability(self) -> dict[str, Any]:
        capability = {
            "capability_version": "0",
            "renderer_id": FLUIDSYNTH_RENDERER_ID,
            "renderer_version": (
                f"adapter-{FLUIDSYNTH_ADAPTER_VERSION}/fluidsynth-{self._runtime['version']}"
            ),
            "classification": "deterministic",
            "supported_inputs": ["music-ir-v0"],
            "supported_outputs": ["midi", "wav"],
            "audio": {
                "sample_rates": [48000],
                "channels": [2],
                "sample_width_bytes": [2],
            },
            "requirements": {
                "external_binary": True,
                "plugin_host": False,
                "network": False,
            },
            "reproducibility": "stable_parameters",
        }
        validate_contract(capability, "renderer-capability-v0.schema.json")
        return capability

    def _soundfont_resource(self, request: dict[str, Any]) -> dict[str, Any]:
        resources = request.get("resources", [])
        soundfonts = [item for item in resources if item.get("role") == "soundfont"]
        if len(soundfonts) != 1:
            raise RendererError("FluidSynth request must bind exactly one SoundFont resource")
        resource = soundfonts[0]
        if resource["resource_id"] != self._soundfont_id:
            raise RendererError("FluidSynth SoundFont resource id does not match configured content")
        if resource["sha256"] != self._soundfont["sha256"]:
            raise RendererError("FluidSynth SoundFont hash mismatch")
        return resource

    def _render_wav(self, midi_path: Path, wav_path: Path, sample_rate: int) -> None:
        command = [
            str(self._runtime["executable"]),
            "-n",
            "-i",
            "-q",
            "-F",
            str(wav_path),
            "-T",
            "wav",
            "-O",
            "s16",
            "-r",
            str(sample_rate),
            str(self._soundfont["path"]),
            str(midi_path),
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RendererError("FluidSynth render timed out") from exc
        except OSError as exc:
            raise RendererError(f"FluidSynth render process failed: {exc}") from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()[-1024:]
            raise RendererError(f"FluidSynth render returned {completed.returncode}: {detail}")

    def render(
        self,
        request: dict[str, Any],
        music_ir: dict[str, Any],
        workspace: str | Path,
    ) -> dict[str, Any]:
        validate_contract(music_ir, "music-ir-v0.schema.json")
        capability = self.capability()
        _validate_request_against_capability(request, capability)

        exact_hash = music_ir_sha256(music_ir)
        if request["music_ir_sha256"] != exact_hash:
            raise RendererError("RendererRequest Music IR hash does not match supplied Music IR")
        resource = self._soundfont_resource(request)

        workspace_root, output_root = _safe_output_root(workspace, request["request_id"])
        midi_path = render_midi(music_ir, output_root / "render.mid")
        artifacts: list[dict[str, Any]] = []
        if "midi" in request["outputs"]:
            artifacts.append(_artifact("midi", midi_path, workspace_root))

        qa_report: dict[str, Any] | None = None
        duration_normalization: dict[str, Any] | None = None
        if "wav" in request["outputs"]:
            audio = request["audio"]
            raw_wav_path = output_root / "render.engine.wav"
            wav_path = output_root / "render.wav"
            self._render_wav(midi_path, raw_wav_path, int(audio["sample_rate"]))
            duration_normalization = _normalize_wav_duration(
                raw_wav_path,
                wav_path,
                target_seconds=float(audio["duration_seconds"]),
            )
            qa_report = analyze_wav(wav_path, target_seconds=float(audio["duration_seconds"]))
            write_canonical_json(output_root / "audio-quality.json", qa_report)
            if qa_report["container"]["sample_rate"] != audio["sample_rate"]:
                raise RendererError("FluidSynth WAV sample rate violates RendererRequest")
            if qa_report["container"]["channels"] != audio["channels"]:
                raise RendererError("FluidSynth WAV channel count violates RendererRequest")
            if qa_report["container"]["sample_width_bytes"] != audio["sample_width_bytes"]:
                raise RendererError("FluidSynth WAV sample width violates RendererRequest")
            if qa_report["status"] == "FAIL":
                raise RendererError(
                    "required AudioQualityReport checks failed after duration normalization: "
                    f"container={qa_report['container']}; "
                    f"signal={qa_report['signal']}; "
                    f"duration={qa_report['duration']}"
                )
            try:
                raw_wav_path.unlink()
            except OSError as exc:
                raise RendererError("FluidSynth raw WAV cleanup failed") from exc
            artifacts.append(_artifact("wav", wav_path, workspace_root))

        provenance = {
            "provenance_version": "0",
            "renderer_id": FLUIDSYNTH_RENDERER_ID,
            "adapter_version": FLUIDSYNTH_ADAPTER_VERSION,
            "engine": {
                "name": self._runtime["name"],
                "version": self._runtime["version"],
                "executable_sha256": self._runtime["executable_sha256"],
            },
            "resources": [
                {
                    "role": "soundfont",
                    "resource_id": resource["resource_id"],
                    "sha256": self._soundfont["sha256"],
                    "size_bytes": self._soundfont["size_bytes"],
                }
            ],
            "render_settings": {
                "sample_rate": request["audio"]["sample_rate"],
                "channels": request["audio"]["channels"],
                "sample_width_bytes": request["audio"]["sample_width_bytes"],
                "audio_file_type": "wav",
                "audio_file_format": "s16",
                "network_required": False,
                "duration_normalization": duration_normalization,
            },
            "project_authority": False,
        }
        provenance_path = output_root / "renderer-provenance.json"
        write_canonical_json(provenance_path, provenance)

        qa_path = output_root / "audio-quality.json"
        result = {
            "result_version": "0",
            "request_id": request["request_id"],
            "music_ir_sha256": exact_hash,
            "renderer": {
                "renderer_id": capability["renderer_id"],
                "renderer_version": capability["renderer_version"],
            },
            "status": "SUCCESS",
            "artifacts": artifacts,
            "warnings": [] if qa_report is None or qa_report["status"] == "PASS" else ["audio QA returned WARN"],
            "reproducibility": {
                "claim": capability["reproducibility"],
                "verified": False,
            },
            "audio_quality": {
                "status": qa_report["status"] if qa_report is not None else "NOT_REQUESTED",
                "report_sha256": sha256_file(qa_path) if qa_report is not None else None,
            },
            "provenance": {
                "manifest_path": provenance_path.relative_to(workspace_root).as_posix(),
                "manifest_sha256": sha256_file(provenance_path),
            },
        }
        validate_contract(result, "renderer-result-v0.schema.json")
        verify_result_artifacts(result, workspace_root)
        return result
