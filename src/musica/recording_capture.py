"""REC-R0 deterministic simulated input capture substrate.

Capture plans, runtime lifecycle, block traces and captured PCM are derived and
non-canonical. This module intentionally does not import captured bytes into the
Project asset store and does not create accepted audio track/clip state.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Iterable

from .automation_edit import automation_material_sha256, blueprint_sha256
from .audio_edit import audio_material_sha256
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256

ENGINE_ID = "musica-recording-simulated-capture-v0"
BACKEND_ID = "musica-simulated-input-v0"
SOURCE_GENERATOR_ID = "musica-deterministic-input-pattern-v0"

SIMULATED_INPUT_CAPABILITY: dict[str, Any] = {
    "capability_version": "0",
    "backend_id": BACKEND_ID,
    "classification": "simulated_test_input_backend",
    "deterministic": True,
    "supported_sample_rates_hz": [8000, 44100, 48000],
    "supported_input_channels": [1, 2],
    "supported_block_sizes_frames": [64, 128, 256, 512, 1024],
    "sample_format": "pcm16_little_endian",
    "latency_metadata": {
        "available": True,
        "nominal_input_latency_frames": 0,
    },
    "host_native_input_claimed": False,
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def simulated_input_capability() -> dict[str, Any]:
    value = {
        key: (
            dict(item)
            if isinstance(item, dict)
            else list(item)
            if isinstance(item, list)
            else item
        )
        for key, item in SIMULATED_INPUT_CAPABILITY.items()
    }
    validate_contract(value, "recording-input-capability-v0.schema.json")
    return value


def simulated_input_capability_sha256() -> str:
    return _sha256(canonical_json_bytes(simulated_input_capability()))


def _validate_config(
    *,
    sample_rate_hz: int,
    input_channels: int,
    block_size_frames: int,
    capture_frames: int,
) -> None:
    capability = simulated_input_capability()
    if sample_rate_hz not in capability["supported_sample_rates_hz"]:
        raise ContractError(f"simulated input backend unsupported sample rate: {sample_rate_hz}")
    if input_channels not in capability["supported_input_channels"]:
        raise ContractError(f"simulated input backend unsupported input channels: {input_channels}")
    if block_size_frames not in capability["supported_block_sizes_frames"]:
        raise ContractError(f"simulated input backend unsupported block size: {block_size_frames}")
    if not isinstance(capture_frames, int) or capture_frames <= 0 or capture_frames > 10_000_000:
        raise ContractError("recording capture_frames must be an integer in [1, 10000000]")


def build_recording_capture_plan(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    input_channels: int = 1,
    block_size_frames: int = 256,
    capture_frames: int,
) -> dict[str, Any]:
    """Bind one exact accepted revision to a deterministic non-canonical capture plan."""

    _validate_config(
        sample_rate_hz=sample_rate_hz,
        input_channels=input_channels,
        block_size_frames=block_size_frames,
        capture_frames=capture_frames,
    )
    blueprint = project.read_revision(revision_id)
    if str(blueprint["project"]["revision_id"]) != str(revision_id):
        raise ContractError("recording capture revision binding mismatch")
    routing = routing_material_from_blueprint(blueprint)
    assert routing is not None
    capability = simulated_input_capability()

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
        },
        "input": {
            "backend_id": BACKEND_ID,
            "classification": "simulated_test_input_backend",
            "capability_sha256": _sha256(canonical_json_bytes(capability)),
            "nominal_input_latency_frames": int(
                capability["latency_metadata"]["nominal_input_latency_frames"]
            ),
            "source_generator_id": SOURCE_GENERATOR_ID,
        },
        "sample_rate_hz": int(sample_rate_hz),
        "input_channels": int(input_channels),
        "block_size_frames": int(block_size_frames),
        "capture_frames": int(capture_frames),
        "policy": {
            "source_rate_policy": "exact_match_required_no_resampling",
            "sample_format": "pcm16_little_endian",
            "cursor_authority": "exact_zero_based_capture_frame",
            "scheduler": "sequential_fixed_blocks",
            "final_block": "partial_block_without_padding",
            "runtime_state_is_canonical": False,
            "captured_payload_is_canonical": False,
        },
    }
    plan = dict(plan_base)
    plan["recording_capture_plan_sha256"] = _sha256(canonical_json_bytes(plan_base))
    validate_recording_capture_plan(plan)
    return plan


def validate_recording_capture_plan(plan: dict[str, Any]) -> None:
    validate_contract(plan, "recording-capture-plan-v0.schema.json")
    base = dict(plan)
    claimed = str(base.pop("recording_capture_plan_sha256"))
    actual = _sha256(canonical_json_bytes(base))
    if claimed != actual:
        raise ContractError("recording capture plan SHA-256 mismatch")
    capability = simulated_input_capability()
    if str(plan["input"]["capability_sha256"]) != _sha256(canonical_json_bytes(capability)):
        raise ContractError("recording capture plan input capability SHA-256 mismatch")


def _sample_value(frame: int, channel: int) -> int:
    """Stable full-range-ish deterministic PCM16 pattern without floating point."""

    unsigned = (int(frame) * 31 + int(channel) * 997 + 12345) % 65536
    return unsigned - 32768


def deterministic_input_payload(
    *,
    start_frame: int,
    frame_count: int,
    input_channels: int,
) -> bytes:
    if start_frame < 0 or frame_count < 0:
        raise ContractError("deterministic input frame range cannot be negative")
    if input_channels not in (1, 2):
        raise ContractError("deterministic input supports one or two channels")
    payload = bytearray()
    for frame in range(start_frame, start_frame + frame_count):
        for channel in range(input_channels):
            payload.extend(
                int(_sample_value(frame, channel)).to_bytes(
                    2, "little", signed=True
                )
            )
    return bytes(payload)


class SimulatedInputBackend:
    """Strict deterministic capture lifecycle for REC-R0."""

    def __init__(
        self,
        *,
        sample_rate_hz: int,
        input_channels: int,
        block_size_frames: int,
        capture_frames: int,
    ) -> None:
        _validate_config(
            sample_rate_hz=sample_rate_hz,
            input_channels=input_channels,
            block_size_frames=block_size_frames,
            capture_frames=capture_frames,
        )
        self.sample_rate_hz = int(sample_rate_hz)
        self.input_channels = int(input_channels)
        self.block_size_frames = int(block_size_frames)
        self.capture_frames = int(capture_frames)
        self.state = "CLOSED"
        self.lifecycle = ["CLOSED"]
        self.payload = bytearray()
        self.blocks_captured = 0
        self.frames_captured = 0
        self.error_count = 0
        self.short_fill_count = 0
        self.late_count = 0

    def _transition(self, expected: str, target: str) -> None:
        if self.state != expected:
            raise ContractError(
                f"simulated input backend illegal lifecycle transition: {self.state} -> {target}"
            )
        self.state = target
        self.lifecycle.append(target)

    def open(self) -> None:
        self._transition("CLOSED", "OPEN")

    def ready(self) -> None:
        self._transition("OPEN", "READY")

    def start(self) -> None:
        self._transition("READY", "CAPTURING")

    def capture_block(
        self,
        *,
        start_frame: int,
        requested_frame_count: int,
        force_error: bool = False,
        force_short_fill: bool = False,
        force_late: bool = False,
    ) -> tuple[bytes, int, str]:
        if self.state != "CAPTURING":
            raise ContractError("simulated input capture requires CAPTURING state")
        if requested_frame_count <= 0 or requested_frame_count > self.block_size_frames:
            raise ContractError("simulated input invalid requested frame count")
        if start_frame < 0 or start_frame + requested_frame_count > self.capture_frames:
            raise ContractError("simulated input requested frame range outside capture plan")
        if force_error and force_short_fill:
            raise ContractError("simulated input ERROR and SHORT_FILL cannot overlap")

        if force_error:
            self.error_count += 1
            return b"", 0, "ERROR"

        captured = requested_frame_count
        status = "OK"
        if force_short_fill:
            captured = max(0, requested_frame_count // 2)
            self.short_fill_count += 1
            status = "SHORT_FILL"
        if force_late:
            self.late_count += 1
            if status == "OK":
                status = "LATE"

        payload = deterministic_input_payload(
            start_frame=start_frame,
            frame_count=captured,
            input_channels=self.input_channels,
        )
        self.payload.extend(payload)
        self.blocks_captured += 1
        self.frames_captured += captured
        return payload, captured, status

    def stop(self) -> None:
        self._transition("CAPTURING", "STOPPED")

    def finalize(self) -> None:
        self._transition("STOPPED", "FINALIZED")

    def close(self) -> None:
        self._transition("FINALIZED", "CLOSED")


@dataclass(frozen=True)
class SimulatedCaptureRun:
    plan: dict[str, Any]
    block_trace: tuple[dict[str, Any], ...]
    captured_payload: bytes
    report: dict[str, Any]


def run_recording_capture_simulation(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    input_channels: int = 1,
    block_size_frames: int = 256,
    capture_frames: int,
    force_error_block_indices: Iterable[int] = (),
    force_short_fill_block_indices: Iterable[int] = (),
    force_late_block_indices: Iterable[int] = (),
) -> SimulatedCaptureRun:
    """Capture deterministic PCM without creating accepted project media."""

    plan = build_recording_capture_plan(
        project,
        revision_id,
        sample_rate_hz=sample_rate_hz,
        input_channels=input_channels,
        block_size_frames=block_size_frames,
        capture_frames=capture_frames,
    )
    head_before = project.head_revision_id("main")

    total_blocks = (capture_frames + block_size_frames - 1) // block_size_frames
    errors = {int(v) for v in force_error_block_indices}
    shorts = {int(v) for v in force_short_fill_block_indices}
    lates = {int(v) for v in force_late_block_indices}
    for name, values in (("ERROR", errors), ("SHORT_FILL", shorts), ("LATE", lates)):
        if any(v < 0 or v >= total_blocks for v in values):
            raise ContractError(f"recording forced {name} block index outside capture trace")
    if errors & shorts:
        raise ContractError("recording ERROR and SHORT_FILL injection cannot overlap")

    backend = SimulatedInputBackend(
        sample_rate_hz=sample_rate_hz,
        input_channels=input_channels,
        block_size_frames=block_size_frames,
        capture_frames=capture_frames,
    )
    backend.open()
    backend.ready()
    backend.start()

    trace: list[dict[str, Any]] = []
    cursor = 0
    block_index = 0
    blocks_requested = 0
    frames_requested = 0
    while cursor < capture_frames:
        requested = min(block_size_frames, capture_frames - cursor)
        blocks_requested += 1
        frames_requested += requested
        payload, captured, status = backend.capture_block(
            start_frame=cursor,
            requested_frame_count=requested,
            force_error=block_index in errors,
            force_short_fill=block_index in shorts,
            force_late=block_index in lates,
        )
        trace.append(
            {
                "block_index": block_index,
                "start_frame": cursor,
                "end_frame_exclusive": cursor + requested,
                "requested_frame_count": requested,
                "captured_frame_count": captured,
                "status": status,
                "late": block_index in lates,
                "payload_sha256": _sha256(payload),
                "payload_size_bytes": len(payload),
            }
        )
        cursor += requested
        block_index += 1

    backend.stop()
    backend.finalize()
    backend.close()

    if project.head_revision_id("main") != head_before:
        raise ContractError("recording capture simulation mutated accepted Project HEAD")

    captured_payload = bytes(backend.payload)
    dropout_equivalent_count = (
        backend.error_count + backend.short_fill_count + backend.late_count
    )
    report_base: dict[str, Any] = {
        "report_version": "0",
        "classification": "derived_noncanonical",
        "source": {
            "revision_id": str(revision_id),
            "recording_capture_plan_sha256": str(
                plan["recording_capture_plan_sha256"]
            ),
        },
        "lifecycle": list(backend.lifecycle),
        "metrics": {
            "blocks_requested": blocks_requested,
            "blocks_captured": backend.blocks_captured,
            "frames_requested": frames_requested,
            "frames_captured": backend.frames_captured,
            "final_capture_cursor": capture_frames,
            "error_count": backend.error_count,
            "short_fill_count": backend.short_fill_count,
            "late_count": backend.late_count,
            "dropout_equivalent_count": dropout_equivalent_count,
        },
        "payload": {
            "format": "pcm16_little_endian",
            "channels": input_channels,
            "sample_rate_hz": sample_rate_hz,
            "payload_sha256": _sha256(captured_payload),
            "payload_size_bytes": len(captured_payload),
            "captured_frames": backend.frames_captured,
        },
        "accepted_head_unchanged": True,
        "runtime_state_is_canonical": False,
        "captured_payload_is_canonical": False,
    }
    report = dict(report_base)
    report["recording_capture_run_report_sha256"] = _sha256(
        canonical_json_bytes(report_base)
    )
    validate_recording_capture_report(report)

    return SimulatedCaptureRun(
        plan=plan,
        block_trace=tuple(trace),
        captured_payload=captured_payload,
        report=report,
    )


def validate_recording_capture_report(report: dict[str, Any]) -> None:
    validate_contract(report, "recording-capture-run-report-v0.schema.json")
    base = dict(report)
    claimed = str(base.pop("recording_capture_run_report_sha256"))
    actual = _sha256(canonical_json_bytes(base))
    if claimed != actual:
        raise ContractError("recording capture report SHA-256 mismatch")
