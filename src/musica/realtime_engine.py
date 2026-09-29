"""RTIO-R0 deterministic realtime execution plan and simulated output backend.

This layer intentionally does not claim wall-clock realtime or host-native devices.
It binds one accepted routed/automated revision to a deterministic fixed-block
simulation. Runtime state, sink bytes and metrics are derived/non-canonical.
"""

from __future__ import annotations

import hashlib
import io
import wave
from dataclasses import dataclass
from typing import Any, Iterable

from .automation_edit import automation_material_sha256, blueprint_sha256
from .audio_edit import audio_material_sha256
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .routed_mixer import render_routed_mix
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256

ENGINE_ID = "musica-realtime-simulated-engine-v0"
BACKEND_ID = "musica-simulated-output-v0"

SIMULATED_BACKEND_CAPABILITY: dict[str, Any] = {
    "capability_version": "0",
    "backend_id": BACKEND_ID,
    "classification": "simulated_test_backend",
    "deterministic": True,
    "supported_sample_rates_hz": [8000, 44100, 48000],
    "supported_output_channels": [2],
    "supported_block_sizes_frames": [64, 128, 256, 512, 1024],
    "latency_metadata": {
        "available": True,
        "nominal_output_latency_frames": 0,
    },
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def simulated_backend_capability() -> dict[str, Any]:
    value = {
        key: (
            dict(item) if isinstance(item, dict)
            else list(item) if isinstance(item, list)
            else item
        )
        for key, item in SIMULATED_BACKEND_CAPABILITY.items()
    }
    validate_contract(value, "realtime-backend-capability-v0.schema.json")
    return value


def simulated_backend_capability_sha256() -> str:
    return _sha256(canonical_json_bytes(simulated_backend_capability()))


def _validate_config(*, sample_rate_hz: int, output_channels: int, block_size_frames: int) -> None:
    capability = simulated_backend_capability()
    if sample_rate_hz not in capability["supported_sample_rates_hz"]:
        raise ContractError(f"simulated realtime backend unsupported sample rate: {sample_rate_hz}")
    if output_channels not in capability["supported_output_channels"]:
        raise ContractError(f"simulated realtime backend unsupported output channels: {output_channels}")
    if block_size_frames not in capability["supported_block_sizes_frames"]:
        raise ContractError(f"simulated realtime backend unsupported block size: {block_size_frames}")


def _pcm_payload_from_routed_wav(wav_bytes: bytes, *, sample_rate_hz: int) -> tuple[bytes, int]:
    try:
        with wave.open(io.BytesIO(wav_bytes), "rb") as reader:
            if reader.getcomptype() != "NONE":
                raise ContractError("RTIO-R0 requires uncompressed routed WAV")
            if int(reader.getnchannels()) != 2:
                raise ContractError("RTIO-R0 requires stereo routed WAV")
            if int(reader.getsampwidth()) != 2:
                raise ContractError("RTIO-R0 requires PCM16 routed WAV")
            if int(reader.getframerate()) != int(sample_rate_hz):
                raise ContractError("RTIO-R0 routed WAV sample rate changed")
            frame_count = int(reader.getnframes())
            payload = reader.readframes(frame_count)
    except (wave.Error, EOFError) as exc:
        raise ContractError("RTIO-R0 cannot decode routed WAV") from exc
    if len(payload) != frame_count * 4:
        raise ContractError("RTIO-R0 routed PCM payload length mismatch")
    return payload, frame_count


def build_realtime_execution_plan(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    output_channels: int = 2,
    block_size_frames: int = 256,
) -> dict[str, Any]:
    """Bind exact accepted state to one deterministic simulated-realtime plan."""

    _validate_config(
        sample_rate_hz=sample_rate_hz,
        output_channels=output_channels,
        block_size_frames=block_size_frames,
    )
    blueprint = project.read_revision(revision_id)
    if str(blueprint["project"]["revision_id"]) != str(revision_id):
        raise ContractError("realtime execution revision binding mismatch")

    routed = render_routed_mix(
        project,
        revision_id,
        mix_sample_rate_hz=sample_rate_hz,
    )
    _payload, frame_count = _pcm_payload_from_routed_wav(
        routed.wav_bytes,
        sample_rate_hz=sample_rate_hz,
    )
    routing = routing_material_from_blueprint(blueprint)
    assert routing is not None
    capability = simulated_backend_capability()

    plan_base: dict[str, Any] = {
        "plan_version": "0",
        "engine_id": ENGINE_ID,
        "classification": "derived_noncanonical",
        "source": {
            "project_id": str(blueprint["project"]["project_id"]),
            "revision_id": str(revision_id),
            "blueprint_sha256": blueprint_sha256(blueprint),
            "audio_material_sha256": audio_material_sha256(blueprint),
            "routing_material_sha256": routing_material_sha256(routing),
            "automation_material_sha256": automation_material_sha256(blueprint),
            "routed_mix_plan_sha256": str(routed.plan["routed_mix_plan_sha256"]),
            "routed_wav_sha256": routed.wav_sha256,
        },
        "backend": {
            "backend_id": BACKEND_ID,
            "classification": "simulated_test_backend",
            "capability_sha256": _sha256(canonical_json_bytes(capability)),
            "nominal_output_latency_frames": int(
                capability["latency_metadata"]["nominal_output_latency_frames"]
            ),
        },
        "sample_rate_hz": int(sample_rate_hz),
        "output_channels": int(output_channels),
        "block_size_frames": int(block_size_frames),
        "duration_frames": int(frame_count),
        "transport": {
            "start_frame": 0,
            "end_frame_exclusive": int(frame_count),
        },
        "policy": {
            "source_rate_policy": "exact_match_required_no_resampling",
            "source_format": "routed_wav_pcm16_stereo_little_endian",
            "scheduler": "sequential_fixed_blocks_from_zero_based_frame_cursor",
            "final_block": "partial_block_without_padding",
            "wall_clock_authority": "none_simulated",
            "runtime_state_is_canonical": False,
        },
    }
    plan = dict(plan_base)
    plan["realtime_execution_plan_sha256"] = _sha256(canonical_json_bytes(plan_base))
    validate_contract(plan, "realtime-execution-plan-v0.schema.json")
    return plan


@dataclass(frozen=True)
class SimulatedRealtimeRun:
    plan: dict[str, Any]
    block_trace: tuple[dict[str, Any], ...]
    sink_payload: bytes
    report: dict[str, Any]


class SimulatedOutputBackend:
    """Strict deterministic lifecycle and PCM16-stereo sink for RTIO-R0."""

    def __init__(self, *, sample_rate_hz: int, output_channels: int, block_size_frames: int):
        _validate_config(
            sample_rate_hz=sample_rate_hz,
            output_channels=output_channels,
            block_size_frames=block_size_frames,
        )
        self.sample_rate_hz = int(sample_rate_hz)
        self.output_channels = int(output_channels)
        self.block_size_frames = int(block_size_frames)
        self.state = "CLOSED"
        self.lifecycle = ["CLOSED"]
        self.payload = bytearray()
        self.blocks_written = 0
        self.frames_written = 0
        self.xrun_count = 0

    def _transition(self, expected: str, target: str) -> None:
        if self.state != expected:
            raise ContractError(
                f"simulated realtime backend illegal lifecycle transition: {self.state} -> {target}"
            )
        self.state = target
        self.lifecycle.append(target)

    def open(self) -> None:
        self._transition("CLOSED", "OPEN")

    def start(self) -> None:
        self._transition("OPEN", "RUNNING")

    def write_block(self, payload: bytes, *, frame_count: int, force_xrun: bool = False) -> None:
        if self.state != "RUNNING":
            raise ContractError("simulated realtime backend write requires RUNNING state")
        expected_size = int(frame_count) * self.output_channels * 2
        if frame_count <= 0 or frame_count > self.block_size_frames:
            raise ContractError("simulated realtime backend invalid block frame count")
        if len(payload) != expected_size:
            raise ContractError("simulated realtime backend block payload size mismatch")
        if force_xrun:
            self.xrun_count += 1
            return
        self.payload.extend(payload)
        self.blocks_written += 1
        self.frames_written += int(frame_count)

    def stop(self) -> None:
        self._transition("RUNNING", "STOPPED")

    def close(self) -> None:
        self._transition("STOPPED", "CLOSED")


def _block_trace(
    payload: bytes,
    *,
    duration_frames: int,
    block_size_frames: int,
) -> list[dict[str, Any]]:
    if len(payload) != int(duration_frames) * 4:
        raise ContractError("realtime block source payload length does not match stereo PCM16 frames")
    trace: list[dict[str, Any]] = []
    cursor = 0
    block_index = 0
    while cursor < duration_frames:
        frame_count = min(block_size_frames, duration_frames - cursor)
        start_byte = cursor * 4
        end_byte = (cursor + frame_count) * 4
        block = payload[start_byte:end_byte]
        trace.append(
            {
                "block_index": block_index,
                "start_frame": cursor,
                "end_frame_exclusive": cursor + frame_count,
                "frame_count": frame_count,
                "payload_sha256": _sha256(block),
                "payload_size_bytes": len(block),
            }
        )
        cursor += frame_count
        block_index += 1
    return trace


def run_realtime_simulation(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    output_channels: int = 2,
    block_size_frames: int = 256,
    force_xrun_block_indices: Iterable[int] = (),
) -> SimulatedRealtimeRun:
    """Execute exact routed PCM through deterministic fixed blocks and simulated sink."""

    plan = build_realtime_execution_plan(
        project,
        revision_id,
        sample_rate_hz=sample_rate_hz,
        output_channels=output_channels,
        block_size_frames=block_size_frames,
    )
    head_before = project.head_revision_id("main")
    routed = render_routed_mix(
        project,
        revision_id,
        mix_sample_rate_hz=sample_rate_hz,
    )
    payload, frame_count = _pcm_payload_from_routed_wav(
        routed.wav_bytes,
        sample_rate_hz=sample_rate_hz,
    )
    if frame_count != int(plan["duration_frames"]):
        raise ContractError("realtime source frame count changed after plan construction")
    if routed.wav_sha256 != plan["source"]["routed_wav_sha256"]:
        raise ContractError("realtime routed source WAV changed after plan construction")

    trace = _block_trace(
        payload,
        duration_frames=frame_count,
        block_size_frames=block_size_frames,
    )
    force_xruns = {int(value) for value in force_xrun_block_indices}
    if any(value < 0 or value >= len(trace) for value in force_xruns):
        raise ContractError("forced xrun block index outside execution trace")

    backend = SimulatedOutputBackend(
        sample_rate_hz=sample_rate_hz,
        output_channels=output_channels,
        block_size_frames=block_size_frames,
    )
    backend.open()
    backend.start()

    blocks_requested = 0
    frames_requested = 0
    for block in trace:
        blocks_requested += 1
        frames_requested += int(block["frame_count"])
        start_byte = int(block["start_frame"]) * 4
        end_byte = int(block["end_frame_exclusive"]) * 4
        backend.write_block(
            payload[start_byte:end_byte],
            frame_count=int(block["frame_count"]),
            force_xrun=int(block["block_index"]) in force_xruns,
        )

    backend.stop()
    backend.close()

    head_after = project.head_revision_id("main")
    if head_after != head_before:
        raise ContractError("realtime simulation mutated accepted Project HEAD")

    sink_payload = bytes(backend.payload)
    report_base: dict[str, Any] = {
        "report_version": "0",
        "classification": "derived_noncanonical",
        "source": {
            "revision_id": str(revision_id),
            "realtime_execution_plan_sha256": str(
                plan["realtime_execution_plan_sha256"]
            ),
        },
        "lifecycle": list(backend.lifecycle),
        "metrics": {
            "blocks_requested": blocks_requested,
            "blocks_written": backend.blocks_written,
            "frames_requested": frames_requested,
            "frames_written": backend.frames_written,
            "final_frame_cursor": frame_count,
            "xrun_count": backend.xrun_count,
            "nominal_output_latency_frames": int(
                plan["backend"]["nominal_output_latency_frames"]
            ),
        },
        "sink": {
            "format": "pcm16_stereo_little_endian_payload",
            "payload_sha256": _sha256(sink_payload),
            "payload_size_bytes": len(sink_payload),
            "frame_count": backend.frames_written,
        },
        "accepted_head_unchanged": True,
        "runtime_state_is_canonical": False,
    }
    report = dict(report_base)
    report["realtime_run_report_sha256"] = _sha256(canonical_json_bytes(report_base))
    validate_contract(report, "realtime-run-report-v0.schema.json")

    return SimulatedRealtimeRun(
        plan=plan,
        block_trace=tuple(trace),
        sink_payload=sink_payload,
        report=report,
    )
