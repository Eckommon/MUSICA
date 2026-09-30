from __future__ import annotations

from pathlib import Path

import pytest

from musica.contracts import ContractError
from musica.recording_finalize import (
    accept_recording_finalize_preview,
    build_recording_finalize_preview,
)
from musica.recording_monitor import (
    build_recording_monitor_plan,
    run_recording_monitor_simulation,
)
from test_rec_r1_recording_finalize import _candidate
from test_rtio_r0_realtime_simulated_backend import _fixture


def _run(project, accepted, *, enabled: bool, **kwargs):
    return run_recording_monitor_simulation(
        project,
        accepted["project"]["revision_id"],
        sample_rate_hz=8000,
        input_channels=2,
        block_size_frames=256,
        capture_frames=800,
        monitor_enabled=enabled,
        **kwargs,
    )


def test_monitoring_on_off_preserves_exact_capture_bytes_and_head(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    head = project.head_revision_id("main")

    off = _run(project, accepted, enabled=False)
    on_a = _run(project, accepted, enabled=True)
    on_b = _run(project, accepted, enabled=True)

    assert off.capture_run.plan == on_a.capture_run.plan
    assert off.capture_run.captured_payload == on_a.capture_run.captured_payload
    assert off.capture_run.report == on_a.capture_run.report
    assert on_a.capture_run.captured_payload == on_a.monitor_sink_payload
    assert on_a.monitor_sink_payload == on_b.monitor_sink_payload
    assert on_a.monitoring_plan == on_b.monitoring_plan
    assert on_a.monitor_trace == on_b.monitor_trace
    assert on_a.report == on_b.report
    assert off.monitor_sink_payload == b""
    assert off.report["monitor"]["blocks_written"] == 0
    assert on_a.report["monitor"]["frames_written"] == 800
    assert on_a.report["monitor"]["output_xrun_count"] == 0
    assert project.head_revision_id("main") == head


def test_monitor_output_xrun_drops_monitor_only_not_capture(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    clean = _run(project, accepted, enabled=True)
    xrun = _run(
        project,
        accepted,
        enabled=True,
        force_monitor_xrun_block_indices=[1],
    )

    assert xrun.capture_run.plan == clean.capture_run.plan
    assert xrun.capture_run.captured_payload == clean.capture_run.captured_payload
    assert xrun.capture_run.report == clean.capture_run.report
    assert xrun.monitor_sink_payload != clean.monitor_sink_payload
    assert xrun.report["monitor"]["output_xrun_count"] == 1
    assert xrun.report["monitor"]["frames_written"] < clean.report["monitor"]["frames_written"]


def test_capture_failure_instrumentation_is_correlated_without_hidden_repair(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    run = _run(
        project,
        accepted,
        enabled=True,
        force_error_block_indices=[0],
        force_short_fill_block_indices=[1],
        force_late_block_indices=[2],
    )

    metrics = run.capture_run.report["metrics"]
    monitor = run.report["monitor"]
    assert metrics["error_count"] == 1
    assert metrics["short_fill_count"] == 1
    assert metrics["late_count"] == 1
    assert metrics["dropout_equivalent_count"] == 3
    assert monitor["input_error_drop_count"] == 1
    assert monitor["input_short_fill_count"] == 1
    assert monitor["input_late_count"] == 1
    assert monitor["frames_written"] == metrics["frames_captured"]
    assert run.monitor_trace[0]["status"] == "INPUT_ERROR_DROPPED"
    assert run.monitor_trace[1]["status"] == "SHORT_FILL_FORWARDED"
    assert run.monitor_trace[2]["status"] == "LATE_FORWARDED"


def test_monitor_configuration_fail_closed(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    with pytest.raises(ContractError, match="stereo input"):
        build_recording_monitor_plan(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=1,
            block_size_frames=256,
            capture_frames=800,
            monitor_enabled=True,
        )

    with pytest.raises(ContractError, match="unsupported sample rate"):
        build_recording_monitor_plan(
            project,
            revision_id,
            sample_rate_hz=16000,
            input_channels=2,
            block_size_frames=256,
            capture_frames=800,
            monitor_enabled=True,
        )

    with pytest.raises(ContractError, match="requires monitoring enabled"):
        run_recording_monitor_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=2,
            block_size_frames=256,
            capture_frames=800,
            monitor_enabled=False,
            force_monitor_xrun_block_indices=[0],
        )


def test_clean_monitored_capture_reuses_rec_r1_finalize_authority(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    run = _run(project, accepted, enabled=True)
    capture = run.capture_run
    head_before = project.head_revision_id("main")

    candidate = _candidate(
        accepted,
        capture,
        candidate_id="REC-R2-MONITORED-FINALIZE",
        clip_id="REC-R2-CLIP",
    )
    preview = build_recording_finalize_preview(project, accepted, candidate, capture)
    assert preview.ready and preview.blueprint is not None
    assert project.head_revision_id("main") == head_before

    record = accept_recording_finalize_preview(project, preview, capture)
    assert record["parent_revision_id"] == head_before
    assert project.head_revision_id("main") == record["revision_id"]
    assert run.report["monitor_state_is_canonical"] is False
    assert run.report["monitor_output_is_canonical"] is False


def test_monitor_plan_and_runtime_rebuild_exact_after_project_reopen(tmp_path: Path) -> None:
    from musica.project import MusicaProject

    project, accepted = _fixture(tmp_path)
    before = _run(project, accepted, enabled=True)
    revision_id = accepted["project"]["revision_id"]

    archive = project.export_to(tmp_path / "rec-r2.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    after = run_recording_monitor_simulation(
        reopened,
        revision_id,
        sample_rate_hz=8000,
        input_channels=2,
        block_size_frames=256,
        capture_frames=800,
        monitor_enabled=True,
    )

    assert after.monitoring_plan == before.monitoring_plan
    assert after.capture_run.plan == before.capture_run.plan
    assert after.capture_run.block_trace == before.capture_run.block_trace
    assert after.capture_run.captured_payload == before.capture_run.captured_payload
    assert after.capture_run.report == before.capture_run.report
    assert after.monitor_trace == before.monitor_trace
    assert after.monitor_sink_payload == before.monitor_sink_payload
    assert after.report == before.report
    assert reopened.verify_integrity()["status"] == "PASS"
