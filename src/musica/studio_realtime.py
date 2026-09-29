"""RTIO-R3 Studio runtime inspection and bounded runtime-command surface.

Runtime sessions are deliberately separate from accepted Studio project sessions.
They bind one exact accepted revision and RTIO execution plan, delegate commands to
RTIO-R2 ExactFrameTransport, and never gain Project mutation authority.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from .contracts import ContractError, validate_contract
from .realtime_transport import ExactFrameTransport
from .studio import StudioService, StudioServiceError, _digest, _safe_name


@dataclass
class _StudioRealtimeRuntime:
    runtime_id: str
    studio_session_id: str
    source_revision_id: str
    source_branch: str
    realtime_execution_plan_sha256: str
    transport: ExactFrameTransport


class StudioRealtimeSurface:
    """Derived realtime runtime sessions bound to accepted Studio revisions."""

    def __init__(self, service: StudioService) -> None:
        self.service = service
        self._runtimes: dict[str, _StudioRealtimeRuntime] = {}

    def _runtime(self, studio_session_id: str, runtime_id: str) -> _StudioRealtimeRuntime:
        safe = _safe_name(runtime_id, "runtime_id")
        runtime = self._runtimes.get(safe)
        if runtime is None or runtime.studio_session_id != studio_session_id:
            raise StudioServiceError("not_found", f"unknown realtime runtime: {safe}")
        return runtime

    def _assert_binding(self, runtime: _StudioRealtimeRuntime) -> Any:
        session = self.service._get_session(runtime.studio_session_id)
        branch = session.project.current_branch()
        head = session.project.head_revision_id(branch)
        if branch != runtime.source_branch:
            raise StudioServiceError(
                "conflict", "realtime runtime is stale because the Studio branch changed"
            )
        if head != runtime.source_revision_id:
            raise StudioServiceError(
                "conflict", "realtime runtime is stale because accepted Project HEAD changed"
            )
        actual_plan_sha = str(
            runtime.transport.plan["realtime_execution_plan_sha256"]
        )
        if actual_plan_sha != runtime.realtime_execution_plan_sha256:
            raise StudioServiceError(
                "integrity_error", "realtime runtime execution-plan identity changed"
            )
        return session

    def _ensure_single_runtime(self, studio_session_id: str) -> None:
        active = [
            runtime.runtime_id
            for runtime in self._runtimes.values()
            if runtime.studio_session_id == studio_session_id
        ]
        if active:
            raise StudioServiceError(
                "conflict",
                f"Studio session already has an open realtime runtime: {active[0]}",
            )

    def open_runtime(
        self,
        studio_session_id: str,
        *,
        sample_rate_hz: int = 8000,
        output_channels: int = 2,
        block_size_frames: int = 256,
    ) -> dict[str, Any]:
        session = self.service._get_session(studio_session_id)
        if session.pending is not None:
            raise StudioServiceError(
                "conflict",
                "accept or discard the pending Studio Preview before opening realtime runtime",
            )
        self._ensure_single_runtime(studio_session_id)
        try:
            branch = session.project.current_branch()
            revision_id = session.project.head_revision_id(branch)
            head_before = revision_id
            transport = ExactFrameTransport(
                session.project,
                revision_id,
                sample_rate_hz=int(sample_rate_hz),
                output_channels=int(output_channels),
                block_size_frames=int(block_size_frames),
            )
            plan_sha = str(transport.plan["realtime_execution_plan_sha256"])
            runtime_id = "rtio-" + _digest(
                {
                    "studio_session_id": studio_session_id,
                    "revision_id": revision_id,
                    "branch": branch,
                    "realtime_execution_plan_sha256": plan_sha,
                    "sample_rate_hz": int(sample_rate_hz),
                    "output_channels": int(output_channels),
                    "block_size_frames": int(block_size_frames),
                }
            )[:24]
            if runtime_id in self._runtimes:
                raise StudioServiceError(
                    "conflict", f"realtime runtime already exists: {runtime_id}"
                )
            if session.project.head_revision_id(branch) != head_before:
                raise StudioServiceError(
                    "integrity_error", "opening realtime runtime changed accepted Project HEAD"
                )
            self._runtimes[runtime_id] = _StudioRealtimeRuntime(
                runtime_id=runtime_id,
                studio_session_id=studio_session_id,
                source_revision_id=revision_id,
                source_branch=branch,
                realtime_execution_plan_sha256=plan_sha,
                transport=transport,
            )
            return self.runtime_view(studio_session_id, runtime_id)
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def runtime_view(
        self, studio_session_id: str, runtime_id: str
    ) -> dict[str, Any]:
        runtime = self._runtime(studio_session_id, runtime_id)
        try:
            session = self._assert_binding(runtime)
            snapshot = runtime.transport.inspection_snapshot()
            plan = runtime.transport.plan
            source = plan["source"]
            view = {
                "view_version": "0",
                "runtime_id": runtime.runtime_id,
                "studio_session_id": studio_session_id,
                "project_id": str(source["project_id"]),
                "revision_id": runtime.source_revision_id,
                "branch": runtime.source_branch,
                "source": {
                    "blueprint_sha256": str(source["blueprint_sha256"]),
                    "audio_material_sha256": str(source["audio_material_sha256"]),
                    "routing_material_sha256": str(source["routing_material_sha256"]),
                    "automation_material_sha256": str(
                        source["automation_material_sha256"]
                    ),
                    "routed_mix_plan_sha256": str(
                        source["routed_mix_plan_sha256"]
                    ),
                    "routed_wav_sha256": str(source["routed_wav_sha256"]),
                },
                "realtime_execution_plan_sha256": runtime.realtime_execution_plan_sha256,
                "backend": {
                    "backend_id": str(plan["backend"]["backend_id"]),
                    "classification": str(plan["backend"]["classification"]),
                    "capability_sha256": str(plan["backend"]["capability_sha256"]),
                },
                "configuration": {
                    "sample_rate_hz": int(plan["sample_rate_hz"]),
                    "output_channels": int(plan["output_channels"]),
                    "block_size_frames": int(plan["block_size_frames"]),
                    "duration_frames": int(plan["duration_frames"]),
                },
                "transport": {
                    "transport_id": str(snapshot["transport_id"]),
                    "state": str(snapshot["state"]),
                    "playhead_frame": int(snapshot["playhead_frame"]),
                    "callback_index": snapshot["callback_index"],
                },
                "latency": copy.deepcopy(snapshot["latency"]),
                "metrics": copy.deepcopy(snapshot["metrics"]),
                "authority": {
                    "accepted_project_state_is_canonical": True,
                    "runtime_state_is_canonical": False,
                    "browser_state_is_canonical": False,
                    "project_mutation_authorized": False,
                    "runtime_commands_mutate_project": False,
                    "position_authority": "exact_frame_cursor_not_wall_clock",
                },
            }
            validate_contract(view, "studio-realtime-runtime-view-v0.schema.json")
            if session.project.head_revision_id(runtime.source_branch) != runtime.source_revision_id:
                raise StudioServiceError(
                    "integrity_error", "runtime inspection changed accepted Project HEAD"
                )
            return view
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def _command(
        self,
        studio_session_id: str,
        runtime_id: str,
        operation: str,
        fn,
    ) -> dict[str, Any]:
        runtime = self._runtime(studio_session_id, runtime_id)
        try:
            session = self._assert_binding(runtime)
            head_before = session.project.head_revision_id(runtime.source_branch)
            result = fn(runtime.transport)
            if session.project.head_revision_id(runtime.source_branch) != head_before:
                raise ContractError(
                    f"realtime runtime {operation} mutated accepted Project HEAD"
                )
            return {
                "operation": operation,
                "event": copy.deepcopy(result),
                "runtime": self.runtime_view(studio_session_id, runtime_id),
            }
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def play(self, studio_session_id: str, runtime_id: str) -> dict[str, Any]:
        return self._command(
            studio_session_id, runtime_id, "PLAY", lambda transport: transport.play()
        )

    def callback(self, studio_session_id: str, runtime_id: str) -> dict[str, Any]:
        return self._command(
            studio_session_id,
            runtime_id,
            "CALLBACK",
            lambda transport: transport.callback(),
        )

    def stop(self, studio_session_id: str, runtime_id: str) -> dict[str, Any]:
        return self._command(
            studio_session_id, runtime_id, "STOP", lambda transport: transport.stop()
        )

    def seek(
        self, studio_session_id: str, runtime_id: str, *, target_frame: int
    ) -> dict[str, Any]:
        return self._command(
            studio_session_id,
            runtime_id,
            "SEEK",
            lambda transport: transport.seek(int(target_frame)),
        )

    def drain_to_eos(
        self, studio_session_id: str, runtime_id: str
    ) -> dict[str, Any]:
        runtime = self._runtime(studio_session_id, runtime_id)
        try:
            session = self._assert_binding(runtime)
            head_before = session.project.head_revision_id(runtime.source_branch)
            runtime.transport.drain_to_eos()
            if session.project.head_revision_id(runtime.source_branch) != head_before:
                raise ContractError(
                    "realtime runtime drain mutated accepted Project HEAD"
                )
            return self.runtime_view(studio_session_id, runtime_id)
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def close_runtime(
        self, studio_session_id: str, runtime_id: str
    ) -> dict[str, Any]:
        runtime = self._runtime(studio_session_id, runtime_id)
        try:
            session = self._assert_binding(runtime)
            if runtime.transport.state == "PLAYING":
                raise StudioServiceError(
                    "conflict", "stop realtime transport before closing runtime"
                )
            head_before = session.project.head_revision_id(runtime.source_branch)
            run = runtime.transport.finalize()
            if session.project.head_revision_id(runtime.source_branch) != head_before:
                raise ContractError(
                    "closing realtime runtime mutated accepted Project HEAD"
                )
            self._runtimes.pop(runtime.runtime_id, None)
            return {
                "closed_runtime_id": runtime.runtime_id,
                "source_revision_id": runtime.source_revision_id,
                "realtime_execution_plan_sha256": runtime.realtime_execution_plan_sha256,
                "transport_report": copy.deepcopy(run.report),
                "sink_sha256": str(run.report["sink"]["payload_sha256"]),
                "accepted_head_unchanged": True,
                "runtime_state_is_canonical": False,
            }
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc
