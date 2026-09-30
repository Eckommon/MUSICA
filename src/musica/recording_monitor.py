"""REC-R2 deterministic runtime-only input monitoring.

Monitoring taps the exact payload returned by REC-R0 SimulatedInputBackend after
capture has already recorded that payload. The monitor sink therefore cannot alter
captured PCM or accepted Project authority. v0 deliberately supports only exact
stereo/no-resampling/unity monitoring because the validated simulated output backend
is stereo-only.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Iterable

from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .realtime_engine import (
    SimulatedOutputBackend,
    simulated_backend_capability,
    simulated_backend_capability_sha256,
)
from .recording_capture import (
    BACKEND_ID as INPUT_BACKEND_ID,
    SimulatedCaptureRun,
    SimulatedInputBackend,
    build_recording_capture_plan,
    simulated_input_capability_sha256,
    validate_recording_capture_report,
)

ENGINE_ID = "musica-recording-monitor-v0"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_recording_monitor_plan(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    input_channels: int,
    block_size_frames: int,
    capture_frames: int,
    monitor_enabled: bool,
) -> dict[str, Any]:
    """Bind one REC-R0 capture plan to a deterministic runtime-only monitor plan."""

    capture_plan = build_recording_capture_plan(
        project,
        revision_id,
        sample_rate_hz=sample_rate_hz,
        input_channels=input_channels,
        block_size_frames=block_size_frames,
        capture_frames=capture_frames,
    )
    output_capability = simulated_backend_capability()
    if int(input_channels) != 2:
        raise ContractError(
            "REC-R2 monitoring v0 requires stereo input because the validated simulated output backend is stereo-only"
        )
    if int(sample_rate_hz) not in output_capability["supported_sample_rates_hz"]:
        raise ContractError("REC-R2 monitoring output backend sample rate mismatch")
    if int(block_size_frames) not in output_capability["supported_block_sizes_frames"]:
        raise ContractError("REC-R2 monitoring output backend block size mismatch")

    source = capture_plan["source"]
    plan_base: dict[str, Any] = {
        "plan_version": "0",
        "engine_id": ENGINE_ID,
        "classification": "derived_noncanonical",
        "source": {
            "project_id": str(source["project_id"]),
            "revision_id": str(source["revision_id"]),
            "blueprint_sha256": str(source["blueprint_sha256"]),
            "audio_material_sha256": str(source["audio_material_sha256"]),
            "routing_material_sha256": str(source["routing_material_sha256"]),
            "automation_material_sha256": str(source["automation_material_sha256"]),
            "recording_capture_plan_sha256": str(
                capture_plan["recording_capture_plan_sha256"]
            ),
        },
        "input": {
            "backend_id": INPUT_BACKEND_ID,
            "capability_sha256": simulated_input_capability_sha256(),
        },
        "output": {
            "backend_id": str(output_capability["backend_id"]),
            "capability_sha256": simulated_backend_capability_sha256(),
            "classification": str(output_capability["classification"]),
        },
        "sample_rate_hz": int(sample_rate_hz),
        "channels": int(input_channels),
        "block_size_frames": int(block_size_frames),
        "capture_frames": int(capture_frames),
        "monitor_enabled": bool(monitor_enabled),
        "policy": {
            "tap": "direct_input_post_capture_copy",
            "sample_format": "pcm16_little_endian",
            "rate_policy": "exact_match_required_no_resampling",
            "channel_policy": "exact_stereo_only",
            "monitor_gain": "unity_only_v0",
            "monitor_state_is_canonical": False,
            "monitor_output_is_canonical": False,
        },
    }
    plan = dict(plan_base)
    plan["recording_monitor_plan_sha256"] = _sha(canonical_json_bytes(plan_base))
    validate_recording_monitor_plan(plan)
    return plan


def validate_recording_monitor_plan(plan: dict[str, Any]) -> None:
    validate_contract(plan, "recording-monitor-plan-v0.schema.json")
    base = dict(plan)
    claimed = str(base.pop("recording_monitor_plan_sha256"))
    if claimed != _sha(canonical_json_bytes(base)):
        raise ContractError("recording monitor plan SHA-256 mismatch")
    if str(plan["input"]["capability_sha256"]) != simulated_input_capability_sha256():
        raise ContractError("recording monitor input capability SHA-256 mismatch")
    if str(plan["output"]["capability_sha256"]) != simulated_backend_capability_sha256():
        raise ContractError("recording monitor output capability SHA-256 mismatch")


@dataclass(frozen=True)
class SimulatedMonitorRun:
    monitoring_plan: dict[str, Any]
    capture_run: SimulatedCaptureRun
    monitor_trace: tuple[dict[str, Any], ...]
    monitor_sink_payload: bytes
    report: dict[str, Any]


def run_recording_monitor_simulation(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    input_channels: int = 2,
    block_size_frames: int = 256,
    capture_frames: int,
    monitor_enabled: bool = True,
    force_error_block_indices: Iterable[int] = (),
    force_short_fill_block_indices: Iterable[int] = (),
    force_late_block_indices: Iterable[int] = (),
    force_monitor_xrun_block_indices: Iterable[int] = (),
) -> SimulatedMonitorRun:
    """Run one deterministic capture with an optional runtime-only direct monitor tap."""

    monitor_plan = build_recording_monitor_plan(
        project,
        revision_id,
        sample_rate_hz=sample_rate_hz,
        input_channels=input_channels,
        block_size_frames=block_size_frames,
        capture_frames=capture_frames,
        monitor_enabled=monitor_enabled,
    )
    capture_plan = build_recording_capture_plan(
        project,
        revision_id,
        sample_rate_hz=sample_rate_hz,
        input_channels=input_channels,
        block_size_frames=block_size_frames,
        capture_frames=capture_frames,
    )
    if (
        capture_plan["recording_capture_plan_sha256"]
        != monitor_plan["source"]["recording_capture_plan_sha256"]
    ):
        raise ContractError("REC-R2 monitor/capture plan binding mismatch")

    head_before = project.head_revision_id("main")
    total_blocks = (capture_frames + block_size_frames - 1) // block_size_frames
    errors = {int(v) for v in force_error_block_indices}
    shorts = {int(v) for v in force_short_fill_block_indices}
    lates = {int(v) for v in force_late_block_indices}
    monitor_xruns = {int(v) for v in force_monitor_xrun_block_indices}
    for name, values in (
        ("ERROR", errors),
        ("SHORT_FILL", shorts),
        ("LATE", lates),
        ("MONITOR_XRUN", monitor_xruns),
    ):
        if any(v < 0 or v >= total_blocks for v in values):
            raise ContractError(f"REC-R2 forced {name} block index outside capture trace")
    if errors & shorts:
        raise ContractError("REC-R2 ERROR and SHORT_FILL injection cannot overlap")
    if monitor_xruns and not monitor_enabled:
        raise ContractError("REC-R2 monitor xrun injection requires monitoring enabled")

    input_backend = SimulatedInputBackend(
        sample_rate_hz=sample_rate_hz,
        input_channels=input_channels,
        block_size_frames=block_size_frames,
        capture_frames=capture_frames,
    )
    output_backend = (
        SimulatedOutputBackend(
            sample_rate_hz=sample_rate_hz,
            output_channels=2,
            block_size_frames=block_size_frames,
        )
        if monitor_enabled
        else None
    )

    input_backend.open()
    input_backend.ready()
    input_backend.start()
    if output_backend is not None:
        output_backend.open()
        output_backend.start()

    capture_trace: list[dict[str, Any]] = []
    monitor_trace: list[dict[str, Any]] = []
    cursor = 0
    block_index = 0
    blocks_requested = 0
    frames_requested = 0
    monitor_blocks_requested = 0
    monitor_input_error_drops = 0
    monitor_input_short_fills = 0
    monitor_input_lates = 0

    while cursor < capture_frames:
        requested = min(block_size_frames, capture_frames - cursor)
        blocks_requested += 1
        frames_requested += requested
        payload, captured, status = input_backend.capture_block(
            start_frame=cursor,
            requested_frame_count=requested,
            force_error=block_index in errors,
            force_short_fill=block_index in shorts,
            force_late=block_index in lates,
        )
        capture_trace.append(
            {
                "block_index": block_index,
                "start_frame": cursor,
                "end_frame_exclusive": cursor + requested,
                "requested_frame_count": requested,
                "captured_frame_count": captured,
                "status": status,
                "late": block_index in lates,
                "payload_sha256": _sha(payload),
                "payload_size_bytes": len(payload),
            }
        )

        if output_backend is not None:
            monitor_blocks_requested += 1
            if status == "ERROR" or captured == 0:
                monitor_input_error_drops += 1
                monitor_status = "INPUT_ERROR_DROPPED"
            else:
                if status == "SHORT_FILL":
                    monitor_input_short_fills += 1
                if block_index in lates:
                    monitor_input_lates += 1
                force_xrun = block_index in monitor_xruns
                output_backend.write_block(
                    payload,
                    frame_count=captured,
                    force_xrun=force_xrun,
                )
                monitor_status = (
                    "OUTPUT_XRUN_DROPPED"
                    if force_xrun
                    else "SHORT_FILL_FORWARDED"
                    if status == "SHORT_FILL"
                    else "LATE_FORWARDED"
                    if status == "LATE"
                    else "OK"
                )
            monitor_trace.append(
                {
                    "block_index": block_index,
                    "source_start_frame": cursor,
                    "requested_frame_count": requested,
                    "captured_frame_count": captured,
                    "status": monitor_status,
                    "source_payload_sha256": _sha(payload),
                }
            )

        cursor += requested
        block_index += 1

    input_backend.stop()
    input_backend.finalize()
    input_backend.close()
    if output_backend is not None:
        output_backend.stop()
        output_backend.close()

    if project.head_revision_id("main") != head_before:
        raise ContractError("REC-R2 monitoring mutated accepted Project HEAD")

    captured_payload = bytes(input_backend.payload)
    capture_dropout_count = (
        input_backend.error_count
        + input_backend.short_fill_count
        + input_backend.late_count
    )
    capture_report_base: dict[str, Any] = {
        "report_version": "0",
        "classification": "derived_noncanonical",
        "source": {
            "revision_id": str(revision_id),
            "recording_capture_plan_sha256": str(
                capture_plan["recording_capture_plan_sha256"]
            ),
        },
        "lifecycle": list(input_backend.lifecycle),
        "metrics": {
            "blocks_requested": blocks_requested,
            "blocks_captured": input_backend.blocks_captured,
            "frames_requested": frames_requested,
            "frames_captured": input_backend.frames_captured,
            "final_capture_cursor": capture_frames,
            "error_count": input_backend.error_count,
            "short_fill_count": input_backend.short_fill_count,
            "late_count": input_backend.late_count,
            "dropout_equivalent_count": capture_dropout_count,
        },
        "payload": {
            "format": "pcm16_little_endian",
            "channels": input_channels,
            "sample_rate_hz": sample_rate_hz,
            "payload_sha256": _sha(captured_payload),
            "payload_size_bytes": len(captured_payload),
            "captured_frames": input_backend.frames_captured,
        },
        "accepted_head_unchanged": True,
        "runtime_state_is_canonical": False,
        "captured_payload_is_canonical": False,
    }
    capture_report = dict(capture_report_base)
    capture_report["recording_capture_run_report_sha256"] = _sha(
        canonical_json_bytes(capture_report_base)
    )
    validate_recording_capture_report(capture_report)
    capture_run = SimulatedCaptureRun(
        plan=capture_plan,
        block_trace=tuple(capture_trace),
        captured_payload=captured_payload,
        report=capture_report,
    )

    monitor_payload = (
        bytes(output_backend.payload) if output_backend is not None else b""
    )
    report_base: dict[str, Any] = {
        "report_version": "0",
        "classification": "derived_noncanonical",
        "source": {
            "revision_id": str(revision_id),
            "recording_monitor_plan_sha256": str(
                monitor_plan["recording_monitor_plan_sha256"]
            ),
        },
        "capture": {
            "recording_capture_run_report_sha256": str(
                capture_report["recording_capture_run_report_sha256"]
            ),
            "payload_sha256": str(capture_report["payload"]["payload_sha256"]),
            "payload_size_bytes": int(capture_report["payload"]["payload_size_bytes"]),
            "captured_frames": int(capture_report["payload"]["captured_frames"]),
            "error_count": int(capture_report["metrics"]["error_count"]),
            "short_fill_count": int(capture_report["metrics"]["short_fill_count"]),
            "late_count": int(capture_report["metrics"]["late_count"]),
            "dropout_equivalent_count": int(
                capture_report["metrics"]["dropout_equivalent_count"]
            ),
        },
        "monitor": {
            "enabled": bool(monitor_enabled),
            "blocks_requested": monitor_blocks_requested,
            "blocks_written": (
                int(output_backend.blocks_written) if output_backend is not None else 0
            ),
            "frames_written": (
                int(output_backend.frames_written) if output_backend is not None else 0
            ),
            "input_error_drop_count": monitor_input_error_drops,
            "input_short_fill_count": monitor_input_short_fills,
            "input_late_count": monitor_input_lates,
            "output_xrun_count": (
                int(output_backend.xrun_count) if output_backend is not None else 0
            ),
            "payload_sha256": _sha(monitor_payload),
            "payload_size_bytes": len(monitor_payload),
        },
        "accepted_head_unchanged": True,
        "monitor_state_is_canonical": False,
        "monitor_output_is_canonical": False,
    }
    report = dict(report_base)
    report["recording_monitor_run_report_sha256"] = _sha(
        canonical_json_bytes(report_base)
    )
    validate_recording_monitor_report(report)

    return SimulatedMonitorRun(
        monitoring_plan=monitor_plan,
        capture_run=capture_run,
        monitor_trace=tuple(monitor_trace),
        monitor_sink_payload=monitor_payload,
        report=report,
    )


def validate_recording_monitor_report(report: dict[str, Any]) -> None:
    validate_contract(report, "recording-monitor-run-report-v0.schema.json")
    base = dict(report)
    claimed = str(base.pop("recording_monitor_run_report_sha256"))
    if claimed != _sha(canonical_json_bytes(base)):
        raise ContractError("recording monitor run report SHA-256 mismatch")
