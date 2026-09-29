"""RTIO-R2 exact-frame transport and deterministic latency/dropout instrumentation.

This layer owns only derived runtime transport state. It drives the validated RTIO-R1
callback engine from an explicit frame playhead and records deterministic transport,
latency and failure metrics. It never writes back into accepted Project state and makes
no host-native wall-clock latency claim.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .realtime_callback import CallbackEngine, DeterministicCallbackAdapter

TRANSPORT_ID = "musica-exact-frame-transport-v0"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class TransportRun:
    plan: dict[str, Any]
    events: tuple[dict[str, Any], ...]
    callback_transactions: tuple[dict[str, Any], ...]
    sink_payload: bytes
    report: dict[str, Any]


class ExactFrameTransport:
    """Bounded STOPPED/PLAYING/EOS transport over the RTIO-R1 callback engine."""

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
        seed = CallbackEngine(
            project,
            revision_id,
            sample_rate_hz=sample_rate_hz,
            output_channels=output_channels,
            block_size_frames=block_size_frames,
        )
        self.plan = seed.plan
        self.sample_rate_hz = int(sample_rate_hz)
        self.output_channels = int(output_channels)
        self.block_size_frames = int(block_size_frames)
        self.duration_frames = int(self.plan["duration_frames"])
        self.state = "STOPPED"
        self.playhead_frame = 0
        self._engine: CallbackEngine | None = None
        self._adapter: DeterministicCallbackAdapter | None = None
        self._segment_sink_bytes_consumed = 0
        self._events: list[dict[str, Any]] = []
        self._transactions: list[dict[str, Any]] = []
        self._sink = bytearray()
        self._head_before = project.head_revision_id("main")
        self._metrics = {
            "play_count": 0,
            "stop_count": 0,
            "seek_count": 0,
            "transport_discontinuity_count": 0,
            "callbacks_requested": 0,
            "frames_requested": 0,
            "frames_delivered": 0,
            "error_count": 0,
            "short_fill_count": 0,
            "late_count": 0,
        }

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)

    @property
    def callback_transactions(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._transactions)

    @property
    def sink_payload(self) -> bytes:
        return bytes(self._sink)

    def _record(
        self,
        *,
        command: str,
        state_before: str,
        state_after: str,
        playhead_before: int,
        playhead_after: int,
        target_frame: int | None = None,
        callback_index: int | None = None,
        status: str = "STATE_TRANSITION",
        error_code: str | None = None,
    ) -> dict[str, Any]:
        event = {
            "event_version": "0",
            "sequence_index": len(self._events),
            "source": {
                "revision_id": self.revision_id,
                "realtime_execution_plan_sha256": str(
                    self.plan["realtime_execution_plan_sha256"]
                ),
            },
            "command": command,
            "state_before": state_before,
            "state_after": state_after,
            "playhead_before": int(playhead_before),
            "playhead_after": int(playhead_after),
            "target_frame": target_frame,
            "callback_index": callback_index,
            "status": status,
            "error_code": error_code,
            "runtime_state_is_canonical": False,
        }
        validate_contract(event, "realtime-transport-event-v0.schema.json")
        self._events.append(event)
        return event

    def _new_segment(self) -> None:
        engine = CallbackEngine(
            self.project,
            self.revision_id,
            sample_rate_hz=self.sample_rate_hz,
            output_channels=self.output_channels,
            block_size_frames=self.block_size_frames,
            initial_frame=self.playhead_frame,
        )
        if engine.plan != self.plan:
            raise ContractError("transport callback plan changed across play segment")
        adapter = DeterministicCallbackAdapter()
        adapter.open()
        adapter.register_callback(engine.callback)
        adapter.start()
        self._engine = engine
        self._adapter = adapter
        self._segment_sink_bytes_consumed = 0

    def play(self) -> dict[str, Any]:
        if self.state != "STOPPED":
            raise ContractError(f"transport PLAY requires STOPPED state, got {self.state}")
        if self.playhead_frame >= self.duration_frames:
            raise ContractError("transport at end-of-stream requires SEEK before PLAY")
        before_state = self.state
        before_frame = self.playhead_frame
        self._new_segment()
        self.state = "PLAYING"
        self._metrics["play_count"] += 1
        return self._record(
            command="PLAY",
            state_before=before_state,
            state_after=self.state,
            playhead_before=before_frame,
            playhead_after=self.playhead_frame,
        )

    def stop(self) -> dict[str, Any]:
        if self.state != "PLAYING" or self._adapter is None:
            raise ContractError(f"transport STOP requires PLAYING state, got {self.state}")
        before_frame = self.playhead_frame
        self._adapter.stop()
        self._adapter.close()
        self._adapter = None
        self._engine = None
        self.state = "STOPPED"
        self._metrics["stop_count"] += 1
        return self._record(
            command="STOP",
            state_before="PLAYING",
            state_after="STOPPED",
            playhead_before=before_frame,
            playhead_after=self.playhead_frame,
        )

    def seek(self, target_frame: int) -> dict[str, Any]:
        if self.state not in {"STOPPED", "END_OF_STREAM"}:
            raise ContractError("transport SEEK requires STOPPED or END_OF_STREAM state")
        if not isinstance(target_frame, int) or target_frame < 0 or target_frame > self.duration_frames:
            raise ContractError("transport seek target outside valid frame range")
        before_state = self.state
        before_frame = self.playhead_frame
        self.playhead_frame = int(target_frame)
        self.state = "STOPPED"
        self._metrics["seek_count"] += 1
        if before_frame != self.playhead_frame:
            self._metrics["transport_discontinuity_count"] += 1
        return self._record(
            command="SEEK",
            state_before=before_state,
            state_after=self.state,
            playhead_before=before_frame,
            playhead_after=self.playhead_frame,
            target_frame=self.playhead_frame,
        )

    def callback(
        self,
        *,
        force_error: bool = False,
        force_short_fill: bool = False,
        force_late: bool = False,
    ) -> dict[str, Any]:
        if self.state != "PLAYING" or self._adapter is None or self._engine is None:
            raise ContractError("transport CALLBACK requires PLAYING state")
        before_frame = self.playhead_frame
        callback_index = self._engine.callback_index
        transaction = self._adapter.request(
            callback_index=callback_index,
            requested_start_frame=before_frame,
            force_error=force_error,
            force_short_fill=force_short_fill,
            force_late=force_late,
        )
        self._transactions.append(transaction)
        response = transaction["response"]
        request = transaction["request"]
        self.playhead_frame = self._engine.frame_cursor
        if int(request["start_frame"]) != before_frame:
            raise ContractError("transport/callback start cursor mismatch")
        if int(request["end_frame_exclusive"]) != self.playhead_frame:
            raise ContractError("transport/callback end cursor mismatch")

        payload_size = int(response["payload_size_bytes"])
        if payload_size:
            # Adapter already owns the exact delivered bytes; append only the newly delivered suffix.
            adapter_payload = bytes(self._adapter.payload)
            self._sink.extend(adapter_payload[self._segment_sink_bytes_consumed:])
            self._segment_sink_bytes_consumed = len(adapter_payload)

        self._metrics["callbacks_requested"] += 1
        self._metrics["frames_requested"] += int(response["requested_frame_count"])
        self._metrics["frames_delivered"] += int(response["delivered_frame_count"])
        self._metrics["error_count"] += int(response["status"] == "ERROR")
        self._metrics["short_fill_count"] += int(response["status"] == "SHORT_FILL")
        self._metrics["late_count"] += int(bool(response["late"]))

        callback_event = self._record(
            command="CALLBACK",
            state_before="PLAYING",
            state_after="PLAYING",
            playhead_before=before_frame,
            playhead_after=self.playhead_frame,
            callback_index=callback_index,
            status=str(response["status"]),
            error_code=response["error_code"],
        )

        if self.playhead_frame == self.duration_frames:
            self._adapter.stop()
            self._adapter.close()
            self._adapter = None
            self._engine = None
            self.state = "END_OF_STREAM"
            self._record(
                command="EOS",
                state_before="PLAYING",
                state_after="END_OF_STREAM",
                playhead_before=self.playhead_frame,
                playhead_after=self.playhead_frame,
            )
        return callback_event

    def drain_to_eos(
        self,
        *,
        force_error_callback_indices: set[int] | None = None,
        force_short_fill_callback_indices: set[int] | None = None,
        force_late_callback_indices: set[int] | None = None,
    ) -> None:
        if self.state != "PLAYING":
            raise ContractError("transport drain requires PLAYING state")
        errors = set() if force_error_callback_indices is None else set(force_error_callback_indices)
        shorts = set() if force_short_fill_callback_indices is None else set(force_short_fill_callback_indices)
        lates = set() if force_late_callback_indices is None else set(force_late_callback_indices)
        if errors & shorts:
            raise ContractError("transport ERROR and SHORT_FILL callback indices overlap")
        assert self._engine is not None
        remaining = self.duration_frames - self._engine.frame_cursor
        total_callbacks = (remaining + self.block_size_frames - 1) // self.block_size_frames
        all_indices = errors | shorts | lates
        if any(index < 0 or index >= total_callbacks for index in all_indices):
            raise ContractError("transport failure injection index outside current play segment")
        while self.state == "PLAYING":
            assert self._engine is not None
            index = self._engine.callback_index
            self.callback(
                force_error=index in errors,
                force_short_fill=index in shorts,
                force_late=index in lates,
            )

    def finalize(self) -> TransportRun:
        if self.state == "PLAYING":
            raise ContractError("transport finalize requires non-PLAYING state")
        if self.project.head_revision_id("main") != self._head_before:
            raise ContractError("transport execution mutated accepted Project HEAD")

        sink_payload = bytes(self._sink)
        xrun_equivalent = (
            self._metrics["error_count"]
            + self._metrics["short_fill_count"]
            + self._metrics["late_count"]
        )
        report_base = {
            "report_version": "0",
            "classification": "derived_noncanonical",
            "source": {
                "revision_id": self.revision_id,
                "realtime_execution_plan_sha256": str(
                    self.plan["realtime_execution_plan_sha256"]
                ),
            },
            "transport_policy": {
                "seek_while_playing": "fail_closed",
                "callback_index_policy": "reset_to_zero_per_play_segment",
                "position_authority": "exact_frame_cursor_not_wall_clock",
                "eos_policy": "terminal_until_seek",
            },
            "latency": {
                "configured_block_size_frames": self.block_size_frames,
                "nominal_output_latency_frames": int(
                    self.plan["backend"]["nominal_output_latency_frames"]
                ),
                "nominal_source": "simulated_backend_capability",
                "host_observed_latency_available": False,
                "wall_clock_guarantee_claimed": False,
            },
            "metrics": {
                **self._metrics,
                "xrun_dropout_equivalent_count": xrun_equivalent,
                "final_playhead_frame": self.playhead_frame,
                "final_callback_cursor": self.playhead_frame,
                "final_state": self.state,
            },
            "sink": {
                "format": "pcm16_stereo_little_endian_payload",
                "payload_sha256": _sha256(sink_payload),
                "payload_size_bytes": len(sink_payload),
                "frame_count": self._metrics["frames_delivered"],
            },
            "accepted_head_unchanged": True,
            "runtime_state_is_canonical": False,
        }
        report = dict(report_base)
        report["transport_run_report_sha256"] = _sha256(canonical_json_bytes(report_base))
        validate_contract(report, "realtime-transport-run-report-v0.schema.json")
        return TransportRun(
            plan=self.plan,
            events=tuple(self._events),
            callback_transactions=tuple(self._transactions),
            sink_payload=sink_payload,
            report=report,
        )
