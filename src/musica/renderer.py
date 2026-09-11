"""Renderer-neutral adapter boundary for MUSICA M5-R1.

MUSICA M5-R1용 renderer-neutral adapter 경계.

The renderer receives validated Music IR plus an exact-hash-bound request and may only
emit artifacts/evidence below a caller-provided workspace. It never receives project
mutation authority.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Protocol

from .audio_qa import analyze_wav
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes, sha256_file, write_canonical_json
from .render import DEFAULT_SAMPLE_RATE, RENDERER_VERSION, render_midi, render_wav

REFERENCE_RENDERER_ID = "musica-reference-local"
REFERENCE_ADAPTER_VERSION = "0.1.0"


class RendererError(ContractError):
    """Raised when the renderer boundary or result violates M5-R1 policy."""


class RendererAdapter(Protocol):
    def capability(self) -> dict[str, Any]:
        """Return a validated RendererCapability v0 object."""

    def render(
        self,
        request: dict[str, Any],
        music_ir: dict[str, Any],
        workspace: str | Path,
    ) -> dict[str, Any]:
        """Render exact-hash-bound Music IR and return RendererResult v0."""


def music_ir_sha256(music_ir: dict[str, Any]) -> str:
    validate_contract(music_ir, "music-ir-v0.schema.json")
    return hashlib.sha256(canonical_json_bytes(music_ir)).hexdigest()


def build_renderer_request(
    music_ir: dict[str, Any],
    *,
    request_id: str,
    outputs: list[str] | None = None,
    renderer_id: str = REFERENCE_RENDERER_ID,
    seed: int | None = None,
    duration_seconds: float,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    channels: int = 1,
    sample_width_bytes: int = 2,
    quality_preferences: list[str] | None = None,
) -> dict[str, Any]:
    request = {
        "request_version": "0",
        "request_id": request_id,
        "music_ir_sha256": music_ir_sha256(music_ir),
        "renderer_id": renderer_id,
        "outputs": list(outputs or ["midi", "wav"]),
        "seed": seed,
        "audio": {
            "sample_rate": int(sample_rate),
            "channels": int(channels),
            "sample_width_bytes": int(sample_width_bytes),
            "duration_seconds": float(duration_seconds),
        },
        "hints": {"quality_preferences": list(quality_preferences or [])},
    }
    validate_contract(request, "renderer-request-v0.schema.json")
    return request


def reference_renderer_capability() -> dict[str, Any]:
    capability = {
        "capability_version": "0",
        "renderer_id": REFERENCE_RENDERER_ID,
        "renderer_version": f"adapter-{REFERENCE_ADAPTER_VERSION}/core-{RENDERER_VERSION}",
        "classification": "deterministic",
        "supported_inputs": ["music-ir-v0"],
        "supported_outputs": ["midi", "wav"],
        "audio": {
            "sample_rates": [22050, 44100, 48000],
            "channels": [1],
            "sample_width_bytes": [2],
        },
        "requirements": {
            "external_binary": False,
            "plugin_host": False,
            "network": False,
        },
        "reproducibility": "byte_exact",
    }
    validate_contract(capability, "renderer-capability-v0.schema.json")
    return capability


def _safe_output_root(workspace: str | Path, request_id: str) -> tuple[Path, Path]:
    root = Path(workspace).resolve()
    root.mkdir(parents=True, exist_ok=True)
    token = hashlib.sha256(request_id.encode("utf-8")).hexdigest()[:20]
    output = (root / "renderer" / token).resolve()
    if output != root and root not in output.parents:
        raise RendererError("renderer output escaped workspace")
    output.mkdir(parents=True, exist_ok=True)
    return root, output


def _relative_verified(path: Path, workspace: Path) -> str:
    resolved = path.resolve()
    if resolved != workspace and workspace not in resolved.parents:
        raise RendererError(f"renderer artifact escaped workspace: {resolved}")
    return resolved.relative_to(workspace).as_posix()


def _artifact(role: str, path: Path, workspace: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size <= 0:
        raise RendererError(f"renderer did not produce non-empty {role} artifact")
    return {
        "role": role,
        "path": _relative_verified(path, workspace),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def _validate_request_against_capability(
    request: dict[str, Any], capability: dict[str, Any]
) -> None:
    validate_contract(request, "renderer-request-v0.schema.json")
    validate_contract(capability, "renderer-capability-v0.schema.json")
    if capability["classification"] == "stochastic" and capability["reproducibility"] == "byte_exact":
        raise RendererError("stochastic renderer cannot claim byte_exact reproducibility")
    if request["renderer_id"] != capability["renderer_id"]:
        raise RendererError("renderer request id does not match selected adapter")
    unsupported = set(request["outputs"]) - set(capability["supported_outputs"])
    if unsupported:
        raise RendererError(f"renderer output not declared by capability: {sorted(unsupported)}")
    if "wav" in request["outputs"]:
        audio = request["audio"]
        for key, capability_key in (
            ("sample_rate", "sample_rates"),
            ("channels", "channels"),
            ("sample_width_bytes", "sample_width_bytes"),
        ):
            if audio[key] not in capability["audio"][capability_key]:
                raise RendererError(f"renderer capability mismatch for audio.{key}: {audio[key]}")


class ReferenceRendererAdapter:
    """Bounded adapter around the existing deterministic MUSICA MIDI/WAV renderer."""

    def capability(self) -> dict[str, Any]:
        return reference_renderer_capability()

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

        workspace_root, output_root = _safe_output_root(workspace, request["request_id"])
        artifacts: list[dict[str, Any]] = []
        qa_report: dict[str, Any] | None = None

        for role in request["outputs"]:
            if role == "midi":
                path = render_midi(music_ir, output_root / "render.mid")
                artifacts.append(_artifact("midi", path, workspace_root))
            elif role == "wav":
                audio = request["audio"]
                path = render_wav(
                    music_ir,
                    output_root / "render.wav",
                    duration_seconds=float(audio["duration_seconds"]),
                    sample_rate=int(audio["sample_rate"]),
                )
                qa_report = analyze_wav(path, target_seconds=float(audio["duration_seconds"]))
                if qa_report["container"]["channels"] != audio["channels"]:
                    raise RendererError("rendered WAV channel count violates RendererRequest")
                if qa_report["container"]["sample_width_bytes"] != audio["sample_width_bytes"]:
                    raise RendererError("rendered WAV sample width violates RendererRequest")
                if qa_report["status"] == "FAIL":
                    raise RendererError("required AudioQualityReport checks failed")
                artifacts.append(_artifact("wav", path, workspace_root))
                write_canonical_json(output_root / "audio-quality.json", qa_report)
            else:
                raise RendererError(f"unsupported renderer output: {role}")

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
        }
        validate_contract(result, "renderer-result-v0.schema.json")
        verify_result_artifacts(result, workspace_root)
        return result


_RENDERERS: dict[str, RendererAdapter] = {
    REFERENCE_RENDERER_ID: ReferenceRendererAdapter(),
}


def get_renderer(renderer_id: str) -> RendererAdapter:
    try:
        return _RENDERERS[renderer_id]
    except KeyError as exc:
        raise RendererError(f"unknown renderer: {renderer_id}") from exc


def render_with_registry(
    request: dict[str, Any],
    music_ir: dict[str, Any],
    workspace: str | Path,
) -> dict[str, Any]:
    validate_contract(request, "renderer-request-v0.schema.json")
    return get_renderer(request["renderer_id"]).render(request, music_ir, workspace)


def verify_result_artifacts(result: dict[str, Any], workspace: str | Path) -> None:
    """Fail closed if a validated result no longer matches its artifact bytes."""

    validate_contract(result, "renderer-result-v0.schema.json")
    root = Path(workspace).resolve()
    for artifact in result["artifacts"]:
        path = (root / artifact["path"]).resolve()
        if path != root and root not in path.parents:
            raise RendererError("renderer result contains workspace traversal")
        if not path.is_file():
            raise RendererError(f"renderer artifact missing: {artifact['path']}")
        if path.stat().st_size != artifact["size_bytes"]:
            raise RendererError(f"renderer artifact size mismatch: {artifact['path']}")
        if sha256_file(path) != artifact["sha256"]:
            raise RendererError(f"renderer artifact hash mismatch: {artifact['path']}")
