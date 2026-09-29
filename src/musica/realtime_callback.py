"""RTIO-R1 bounded callback engine and deterministic host-adapter boundary.

This layer consumes the validated RTIO-R0 realtime execution plan and routed PCM
source. It adds explicit callback request/response transactions, deterministic
adapter lifecycle, exact frame-cursor semantics and observable callback failures.
It intentionally does not claim host-native ASIO/CoreAudio/WASAPI execution.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .realtime_engine import (
    _pcm_payload_from_routed_wav,
    build_realtime_execution_plan,
)
from .routed_mixer import render_routed_mix

ADAPTER_ID = "musica-deterministic-callback-adapter-v0"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def callback_adapter_capability() -> dict[str, Any]:
    value = {
        "capability_version": "0",
        "adapter_id": ADAPTER_ID,
        "classification": "deterministic_test_adapter",
        "deterministic": True,
        "callback_model": "registered_pull_callback",
        "supported_failure_injection": ["ERROR", "SHORT_FILL", "LATE"],
        "host_native_device_claimed": False,
    }
    validate_contract(value, "realtime-callback-adapter-capability-v0.schema.json")
    return value


def callback_adapter_capability_sha256() -> str:
    return _sha256(canonical_json_bytes(callback_adapter_capability()))


@dataclass(frozen=True)
class CallbackRun:
    plan: dict[str, Any]
    transactions: tuple[dict[str, Any], ...]
    sink_payload: bytes
    report: dict[str, Any]


class DeterministicCallbackAdapter:
    """Strict callback adapter used to validate host-backend boundary semantics."""

    def __init__(self) -> None:
        self.state = "CLOSED"
        self.lifecycle = ["CLOSED"]
        self._callback: Callable[..., dict[str, Any]] | None = None
        self.payload = bytearray()

    def _transition(self, expected: str, target: str) -> None:
        if self.state != expected:
            raise ContractError(
                f"callback adapter illegal lifecycle transition: {self.state} -> {target}"
            )
        self.state = target
        self.lifecycle.append(target)

    def open(self) -> None:
        self._transition("CLOSED", "OPEN")

    def register_callback(self, callback: Callable[..., dict[str, Any]]) -> None:
        if self.state != "OPEN":
            raise ContractError("callback registration requires OPEN state")
        if self._callback is not None:
            raise ContractError("callback already registered")
        self._callback = callback
        self.state = "CALLBACK_REGISTERED"
        self.lifecycle.append("CALLBACK_REGISTERED")

    def start(self) -> None:
        if self._callback is None:
            raise ContractError("callback adapter start requires registered callback")
        self._transition("CALLBACK_REGISTERED", "RUNNING")

    def request(
        self,
        *,
        force_error: bool = False,
        force_short_fill: bool = False,
        force_late: bool = False,
    ) -> dict[str, Any]:
        if self.state != "RUNNING" or self._callback is None:
            raise ContractError("callback request requires RUNNING state")
        transaction = self._callback(
            force_error=force_error,
            force_short_fill=force_short_fill,
            force_late=force_late,
        )
        payload = transaction.pop("_payload")
        self.payload.extend(payload)
        return transaction

    def stop(self) -> None:
        self._transition("RUNNING", "STOPPED")

    def close(self) -> None:
        self._transition("STOPPED", "CLOSED")


class CallbackEngine:
    """Exact frame-cursor callback engine over one provenance-bound RTIO-R0 plan."""

    def __init__(
        self,
        project: Any,
        revision_id: str,
        *,
        sample_rate_hz: int,
        output_channels: int = 2,
        block_size_frames: int = 256,
    ) -> None:
        self.project = project
        self.revision_id = str(revision_id)
        self.plan = build_realtime_execution_plan(
            project,
            revision_id,
            sample_rate_hz=sample_rate_hz,
            output_channels=output_channels,
            block_size_frames=block_size_frames,
        )
        routed = render_routed_mix(
            project,
            revision_id,
            mix_sample_rate_hz=sample_rate_hz,
        )
        payload, frame_count = _pcm_payload_from_routed_wav(
            routed.wav_bytes,
            sample_rate_hz=sample_rate_hz,
        )
        if frame_count != int(self.plan["duration_frames"]):
            raise ContractError("callback source frame count changed after plan construction")
        if routed.wav_sha256 != self.plan["source"]["routed_wav_sha256"]:
            raise ContractError("callback routed source WAV changed after plan construction")
        self._source_payload = payload
        self._frame_cursor = 0
        self._callback_index = 0
        self._ended = False

    @property
    def frame_cursor(self) -> int:
        return self._frame_cursor

    @property
    def callback_index(self) -> int:
        return self._callback_index

    def _expected_frame_count(self) -> int:
        remaining = int(self.plan["duration_frames"]) - self._frame_cursor
        if remaining <= 0:
            return 0
        return min(int(self.plan["block_size_frames"]), remaining)

    def callback(
        self,
        *,
        force_error: bool = False,
        force_short_fill: bool = False,
        force_late: bool = False,
    ) -> dict[str, Any]:
        if self._ended or self._frame_cursor >= int(self.plan["duration_frames"]):
            self._ended = True
            raise ContractError("callback invoked after end-of-stream")
        if force_error and force_short_fill:
            raise ContractError("callback ERROR and SHORT_FILL injection cannot overlap")

        requested = self._expected_frame_count()
        start = self._frame_cursor
        end = start + requested
        start_byte = start * 4
        end_byte = end * 4
        exact_payload = self._source_payload[start_byte:end_byte]

        if force_error:
            delivered_payload = b""
            status = "ERROR"
            error_code: str | None = "FORCED_CALLBACK_ERROR"
        elif force_short_fill:
            delivered_frames = max(0, requested // 2)
            delivered_payload = exact_payload[: delivered_frames * 4]
            status = "SHORT_FILL"
            error_code = "FORCED_SHORT_FILL"
        else:
            delivered_payload = exact_payload
            status = "OK"
            error_code = None

        delivered_frames = len(delivered_payload) // 4
        transaction = {
            "transaction_version": "0",
            "source": {
                "revision_id": self.revision_id,
                "realtime_execution_plan_sha256": str(
                    self.plan["realtime_execution_plan_sha256"]
                ),
            },
            "request": {
                "callback_index": self._callback_index,
                "start_frame": start,
                "requested_frame_count": requested,
                "end_frame_exclusive": end,
                "transport_state": "RUNNING",
            },
            "response": {
                "callback_index": self._callback_index,
                "start_frame": start,
                "requested_frame_count": requested,
                "delivered_frame_count": delivered_frames,
                "end_frame_exclusive": end,
                "payload_sha256": _sha256(delivered_payload),
                "payload_size_bytes": len(delivered_payload),
                "status": status,
                "error_code": error_code,
                "late": bool(force_late),
            },
        }
        validate_contract(transaction, "realtime-callback-transaction-v0.schema.json")

        self._frame_cursor = end
        self._callback_index += 1
        if self._frame_cursor == int(self.plan["duration_frames"]):
            self._ended = True
        transaction["_payload"] = delivered_payload
        return transaction


def _validate_injection_indices(
    *,
    total_callbacks: int,
    error_indices: set[int],
    short_fill_indices: set[int],
    late_indices: set[int],
) -> None:
    all_indices = error_indices | short_fill_indices | late_indices
    if any(index < 0 or index >= total_callbacks for index in all_indices):
        raise ContractError("callback failure injection index outside execution trace")
    overlap = error_indices & short_fill_indices
    if overlap:
        raise ContractError("callback ERROR and SHORT_FILL injection indices overlap")


def run_callback_harness(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    output_channels: int = 2,
    block_size_frames: int = 256,
    force_error_callback_indices: Iterable[int] = (),
    force_short_fill_callback_indices: Iterable[int] = (),
    force_late_callback_indices: Iterable[int] = (),
    stop_after_callbacks: int | None = None,
) -> CallbackRun:
    """Run deterministic callback transactions through the bounded test adapter."""

    engine = CallbackEngine(
        project,
        revision_id,
        sample_rate_hz=sample_rate_hz,
        output_channels=output_channels,
        block_size_frames=block_size_frames,
    )
    head_before = project.head_revision_id("main")

    duration = int(engine.plan["duration_frames"])
    block = int(engine.plan["block_size_frames"])
    total_callbacks = (duration + block - 1) // block
    if stop_after_callbacks is not None:
        if stop_after_callbacks <= 0 or stop_after_callbacks > total_callbacks:
            raise ContractError("stop_after_callbacks outside valid callback range")

    error_indices = {int(v) for v in force_error_callback_indices}
    short_indices = {int(v) for v in force_short_fill_callback_indices}
    late_indices = {int(v) for v in force_late_callback_indices}
    _validate_injection_indices(
        total_callbacks=total_callbacks,
        error_indices=error_indices,
        short_fill_indices=short_indices,
        late_indices=late_indices,
    )

    adapter = DeterministicCallbackAdapter()
    adapter.open()
    adapter.register_callback(engine.callback)
    adapter.start()

    transactions: list[dict[str, Any]] = []
    callbacks_requested = 0
    frames_requested = 0
    frames_delivered = 0
    error_count = 0
    short_fill_count = 0
    late_count = 0

    limit = stop_after_callbacks if stop_after_callbacks is not None else total_callbacks
    for index in range(limit):
        callbacks_requested += 1
        transaction = adapter.request(
            force_error=index in error_indices,
            force_short_fill=index in short_indices,
            force_late=index in late_indices,
        )
        transactions.append(transaction)
        response = transaction["response"]
        frames_requested += int(response["requested_frame_count"])
        frames_delivered += int(response["delivered_frame_count"])
        error_count += int(response["status"] == "ERROR")
        short_fill_count += int(response["status"] == "SHORT_FILL")
        late_count += int(response["late"])

    completion_status = (
        "END_OF_STREAM"
        if engine.frame_cursor == duration
        else "STOPPED_EARLY"
    )
    adapter.stop()
    adapter.close()

    if project.head_revision_id("main") != head_before:
        raise ContractError("callback execution mutated accepted Project HEAD")

    sink_payload = bytes(adapter.payload)
    report_base = {
        "report_version": "0",
        "classification": "derived_noncanonical",
        "source": {
            "revision_id": str(revision_id),
            "realtime_execution_plan_sha256": str(
                engine.plan["realtime_execution_plan_sha256"]
            ),
        },
        "adapter": {
            "adapter_id": ADAPTER_ID,
            "capability_sha256": callback_adapter_capability_sha256(),
        },
        "lifecycle": list(adapter.lifecycle),
        "completion_status": completion_status,
        "metrics": {
            "callbacks_requested": callbacks_requested,
            "callbacks_completed": len(transactions),
            "frames_requested": frames_requested,
            "frames_delivered": frames_delivered,
            "final_frame_cursor": engine.frame_cursor,
            "error_count": error_count,
            "short_fill_count": short_fill_count,
            "late_count": late_count,
            "xrun_equivalent_count": error_count + short_fill_count + late_count,
        },
        "sink": {
            "format": "pcm16_stereo_little_endian_payload",
            "payload_sha256": _sha256(sink_payload),
            "payload_size_bytes": len(sink_payload),
            "frame_count": frames_delivered,
        },
        "accepted_head_unchanged": True,
        "runtime_state_is_canonical": False,
    }
    report = dict(report_base)
    report["callback_run_report_sha256"] = _sha256(canonical_json_bytes(report_base))
    validate_contract(report, "realtime-callback-run-report-v0.schema.json")

    return CallbackRun(
        plan=engine.plan,
        transactions=tuple(transactions),
        sink_payload=sink_payload,
        report=report,
    )
