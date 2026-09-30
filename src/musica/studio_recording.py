"""REC-R3 Studio/Browser recording and monitoring surface.

This surface exposes only derived REC-R2 runtime state and delegates creative
recording finalization to the already validated REC-R1 Preview -> explicit Accept
authority. Browser/runtime state never imports assets or commits audio material
directly.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from .automation_edit import automation_material_sha256
from .audio_contracts import audio_material_from_blueprint
from .audio_edit import audio_material_sha256, blueprint_sha256
from .contracts import ContractError
from .recording_finalize import (
    RecordingFinalizePreview,
    accept_recording_finalize_preview,
    build_recording_finalize_preview,
)
from .recording_monitor import SimulatedMonitorRun, run_recording_monitor_simulation
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256
from .studio import StudioService, StudioServiceError, _digest, _safe_name


@dataclass
class _StudioRecordingRuntime:
    runtime_id: str
    studio_session_id: str
    source_revision_id: str
    source_branch: str
    monitor_run: SimulatedMonitorRun
    finalize_preview: RecordingFinalizePreview | None = None
    finalize_candidate: dict[str, Any] | None = None


class StudioRecordingSurface:
    """Derived capture/monitor runtime plus REC-R1 finalize delegation."""

    def __init__(self, service: StudioService) -> None:
        self.service = service
        self._runtimes: dict[str, _StudioRecordingRuntime] = {}

    def _runtime_for_session(self, session_id: str) -> _StudioRecordingRuntime | None:
        matches = [
            runtime
            for runtime in self._runtimes.values()
            if runtime.studio_session_id == session_id
        ]
        if len(matches) > 1:
            raise StudioServiceError(
                "integrity_error",
                "Studio recording surface has multiple runtimes for one session",
            )
        return matches[0] if matches else None

    def _runtime(self, session_id: str, runtime_id: str) -> _StudioRecordingRuntime:
        safe = _safe_name(runtime_id, "runtime_id")
        runtime = self._runtimes.get(safe)
        if runtime is None or runtime.studio_session_id != session_id:
            raise StudioServiceError("not_found", f"unknown recording runtime: {safe}")
        return runtime

    def _assert_binding(self, runtime: _StudioRecordingRuntime) -> Any:
        session = self.service._get_session(runtime.studio_session_id)
        branch = session.project.current_branch()
        if branch != runtime.source_branch:
            raise StudioServiceError(
                "conflict",
                "recording runtime is stale because the Studio branch changed",
            )
        if session.project.head_revision_id(branch) != runtime.source_revision_id:
            raise StudioServiceError(
                "conflict",
                "recording runtime is stale because accepted Project HEAD changed",
            )
        source = runtime.monitor_run.monitoring_plan["source"]
        accepted = session.project.read_revision(runtime.source_revision_id)
        routing = routing_material_from_blueprint(accepted)
        assert routing is not None
        expected = {
            "project_id": str(accepted["project"]["project_id"]),
            "revision_id": runtime.source_revision_id,
            "blueprint_sha256": blueprint_sha256(accepted),
            "audio_material_sha256": audio_material_sha256(accepted),
            "routing_material_sha256": routing_material_sha256(routing),
            "automation_material_sha256": automation_material_sha256(accepted),
        }
        for key, value in expected.items():
            if str(source[key]) != str(value):
                raise StudioServiceError(
                    "integrity_error",
                    f"recording runtime source {key} no longer matches accepted state",
                )
        return session

    @staticmethod
    def _clean_capture(run: SimulatedMonitorRun) -> bool:
        capture = run.capture_run
        metrics = capture.report["metrics"]
        return (
            int(metrics["frames_captured"]) == int(capture.plan["capture_frames"])
            and int(metrics["error_count"]) == 0
            and int(metrics["short_fill_count"]) == 0
            and int(metrics["late_count"]) == 0
            and int(metrics["dropout_equivalent_count"]) == 0
        )

    @staticmethod
    def _source_binding(accepted: dict[str, Any]) -> dict[str, Any]:
        routing = routing_material_from_blueprint(accepted)
        assert routing is not None
        return {
            "project_id": str(accepted["project"]["project_id"]),
            "revision_id": str(accepted["project"]["revision_id"]),
            "blueprint_sha256": blueprint_sha256(accepted),
            "audio_material_sha256": audio_material_sha256(accepted),
            "routing_material_sha256": routing_material_sha256(routing),
            "automation_material_sha256": automation_material_sha256(accepted),
        }

    @staticmethod
    def _capture_binding(run: SimulatedMonitorRun) -> dict[str, Any]:
        capture = run.capture_run
        return {
            "recording_capture_plan_sha256": str(
                capture.plan["recording_capture_plan_sha256"]
            ),
            "recording_capture_run_report_sha256": str(
                capture.report["recording_capture_run_report_sha256"]
            ),
            "payload_sha256": str(capture.report["payload"]["payload_sha256"]),
            "payload_size_bytes": int(capture.report["payload"]["payload_size_bytes"]),
            "sample_rate_hz": int(capture.report["payload"]["sample_rate_hz"]),
            "channels": int(capture.report["payload"]["channels"]),
            "captured_frames": int(capture.report["payload"]["captured_frames"]),
            "sample_format": str(capture.report["payload"]["format"]),
        }

    def _candidate(
        self,
        accepted: dict[str, Any],
        runtime: _StudioRecordingRuntime,
        *,
        track_id: str,
        clip_id: str,
        timeline_start_seconds: float,
        gain_db: float,
    ) -> dict[str, Any]:
        payload = {
            "source_revision_id": runtime.source_revision_id,
            "recording_monitor_plan_sha256": runtime.monitor_run.monitoring_plan[
                "recording_monitor_plan_sha256"
            ],
            "capture_report_sha256": runtime.monitor_run.capture_run.report[
                "recording_capture_run_report_sha256"
            ],
            "track_id": str(track_id),
            "clip_id": str(clip_id),
            "timeline_start_seconds": float(timeline_start_seconds),
            "gain_db": float(gain_db),
        }
        candidate_id = "studio-rec-" + _digest(payload)[:24]
        return {
            "candidate_version": "0",
            "candidate_id": candidate_id,
            "authority_target": "recording_finalize_to_audio_material",
            "source": self._source_binding(accepted),
            "capture": self._capture_binding(runtime.monitor_run),
            "destination": {
                "track_id": str(track_id),
                "clip_id": str(clip_id),
                "timeline_start_seconds": float(timeline_start_seconds),
                "gain_db": float(gain_db),
            },
            "actor": {"kind": "user", "actor_id": "studio-browser"},
            "reason": f"Finalize Studio recording {clip_id} to track {track_id}.",
            "preview_only": True,
        }

    def recording_view(self, session_id: str) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        branch = session.project.current_branch()
        revision_id = session.project.head_revision_id(branch)
        accepted = session.project.read_revision(revision_id)
        source = self._source_binding(accepted)
        audio = audio_material_from_blueprint(accepted)
        assert audio is not None
        runtime = self._runtime_for_session(session_id)

        runtime_value: dict[str, Any] | None = None
        if runtime is not None:
            self._assert_binding(runtime)
            run = runtime.monitor_run
            preview = runtime.finalize_preview
            runtime_value = {
                "runtime_id": runtime.runtime_id,
                "source_revision_id": runtime.source_revision_id,
                "recording_monitor_plan_sha256": str(
                    run.monitoring_plan["recording_monitor_plan_sha256"]
                ),
                "recording_capture_plan_sha256": str(
                    run.capture_run.plan["recording_capture_plan_sha256"]
                ),
                "recording_capture_run_report_sha256": str(
                    run.capture_run.report["recording_capture_run_report_sha256"]
                ),
                "recording_monitor_run_report_sha256": str(
                    run.report["recording_monitor_run_report_sha256"]
                ),
                "capture_payload_sha256": str(
                    run.capture_run.report["payload"]["payload_sha256"]
                ),
                "monitor_enabled": bool(run.monitoring_plan["monitor_enabled"]),
                "capture_clean": self._clean_capture(run),
                "capture_metrics": copy.deepcopy(run.capture_run.report["metrics"]),
                "monitor_metrics": copy.deepcopy(run.report["monitor"]),
                "finalize_preview": None if preview is None else preview.as_dict(),
            }

        return {
            "view_version": "0",
            "project_id": source["project_id"],
            "revision_id": revision_id,
            "branch": branch,
            "source": {
                "blueprint_sha256": source["blueprint_sha256"],
                "audio_material_sha256": source["audio_material_sha256"],
                "routing_material_sha256": source["routing_material_sha256"],
                "automation_material_sha256": source["automation_material_sha256"],
            },
            "audio_tracks": [
                {
                    "track_id": str(track["track_id"]),
                    "name": str(track["name"]),
                    "clip_ids": [str(clip["clip_id"]) for clip in track["clips"]],
                }
                for track in audio["tracks"]
            ],
            "runtime": runtime_value,
            "authority": {
                "accepted_project_state_is_canonical": True,
                "recording_runtime_is_canonical": False,
                "monitor_state_is_canonical": False,
                "browser_state_is_canonical": False,
                "runtime_may_import_assets": False,
                "runtime_may_commit_audio_material": False,
                "finalize_authority": "REC-R1_PREVIEW_EXPLICIT_ACCEPT",
            },
            "capabilities": {
                "simulated_input_only": True,
                "simulated_monitor_output_only": True,
                "capture_monitor_runtime": True,
                "finalize_preview": True,
                "explicit_accept_required": True,
                "restart_resets_runtime": True,
            },
        }

    def run_capture_monitor(
        self,
        session_id: str,
        *,
        sample_rate_hz: int = 8000,
        input_channels: int = 2,
        block_size_frames: int = 256,
        capture_frames: int = 800,
        monitor_enabled: bool = True,
        force_error_block_indices: list[int] | None = None,
        force_short_fill_block_indices: list[int] | None = None,
        force_late_block_indices: list[int] | None = None,
        force_monitor_xrun_block_indices: list[int] | None = None,
    ) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        if session.pending is not None:
            raise StudioServiceError(
                "conflict",
                "accept or discard the pending Studio Preview before recording",
            )
        if self._runtime_for_session(session_id) is not None:
            raise StudioServiceError(
                "conflict",
                "reset the existing recording runtime before starting another capture",
            )
        try:
            branch = session.project.current_branch()
            revision_id = session.project.head_revision_id(branch)
            head_before = revision_id
            run = run_recording_monitor_simulation(
                session.project,
                revision_id,
                sample_rate_hz=int(sample_rate_hz),
                input_channels=int(input_channels),
                block_size_frames=int(block_size_frames),
                capture_frames=int(capture_frames),
                monitor_enabled=bool(monitor_enabled),
                force_error_block_indices=force_error_block_indices or (),
                force_short_fill_block_indices=force_short_fill_block_indices or (),
                force_late_block_indices=force_late_block_indices or (),
                force_monitor_xrun_block_indices=force_monitor_xrun_block_indices or (),
            )
            runtime_id = "rec-" + _digest(
                {
                    "session_id": session_id,
                    "revision_id": revision_id,
                    "monitor_plan_sha256": run.monitoring_plan[
                        "recording_monitor_plan_sha256"
                    ],
                    "monitor_report_sha256": run.report[
                        "recording_monitor_run_report_sha256"
                    ],
                }
            )[:24]
            if session.project.head_revision_id(branch) != head_before:
                raise ContractError("recording runtime changed accepted Project HEAD")
            self._runtimes[runtime_id] = _StudioRecordingRuntime(
                runtime_id=runtime_id,
                studio_session_id=session_id,
                source_revision_id=revision_id,
                source_branch=branch,
                monitor_run=run,
            )
            return self.recording_view(session_id)
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def preview_finalize(
        self,
        session_id: str,
        runtime_id: str,
        *,
        track_id: str,
        clip_id: str,
        timeline_start_seconds: float = 0.0,
        gain_db: float = 0.0,
    ) -> dict[str, Any]:
        runtime = self._runtime(session_id, runtime_id)
        try:
            session = self._assert_binding(runtime)
            accepted = session.project.read_revision(runtime.source_revision_id)
            candidate = self._candidate(
                accepted,
                runtime,
                track_id=track_id,
                clip_id=clip_id,
                timeline_start_seconds=timeline_start_seconds,
                gain_db=gain_db,
            )
            preview = build_recording_finalize_preview(
                session.project,
                accepted,
                candidate,
                runtime.monitor_run.capture_run,
                branch=runtime.source_branch,
            )
            runtime.finalize_candidate = copy.deepcopy(candidate)
            runtime.finalize_preview = preview
            return {
                "preview_installed": preview.ready,
                "authority_result": copy.deepcopy(preview.authority_result),
                "recording_finalize": preview.as_dict(),
                "recording_view": self.recording_view(session_id),
            }
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def accept_finalize(self, session_id: str, runtime_id: str) -> dict[str, Any]:
        runtime = self._runtime(session_id, runtime_id)
        try:
            session = self._assert_binding(runtime)
            preview = runtime.finalize_preview
            if preview is None:
                raise StudioServiceError(
                    "not_found",
                    "recording runtime has no finalize Preview to accept",
                )
            if not preview.ready:
                raise StudioServiceError(
                    "conflict",
                    "blocked recording finalize Preview cannot be accepted",
                )
            record = accept_recording_finalize_preview(
                session.project,
                preview,
                runtime.monitor_run.capture_run,
                branch=runtime.source_branch,
            )
            accepted_runtime_id = runtime.runtime_id
            self._runtimes.pop(runtime.runtime_id, None)
            return {
                "accepted_runtime_id": accepted_runtime_id,
                "revision_record": record,
                "accepted_head_revision_id": session.project.head_revision_id(
                    runtime.source_branch
                ),
                "runtime_reset": True,
                "recording_view": self.recording_view(session_id),
            }
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def discard_finalize_preview(
        self, session_id: str, runtime_id: str
    ) -> dict[str, Any]:
        runtime = self._runtime(session_id, runtime_id)
        session = self._assert_binding(runtime)
        head_before = session.project.head_revision_id(runtime.source_branch)
        runtime.finalize_preview = None
        runtime.finalize_candidate = None
        if session.project.head_revision_id(runtime.source_branch) != head_before:
            raise StudioServiceError(
                "integrity_error",
                "discarding recording Preview changed accepted Project HEAD",
            )
        return self.recording_view(session_id)

    def reset_runtime(self, session_id: str, runtime_id: str) -> dict[str, Any]:
        runtime = self._runtime(session_id, runtime_id)
        session = self._assert_binding(runtime)
        head_before = session.project.head_revision_id(runtime.source_branch)
        self._runtimes.pop(runtime.runtime_id, None)
        if session.project.head_revision_id(runtime.source_branch) != head_before:
            raise StudioServiceError(
                "integrity_error",
                "resetting recording runtime changed accepted Project HEAD",
            )
        return self.recording_view(session_id)
