from __future__ import annotations

from pathlib import Path

import pytest

from musica.contracts import ContractError
from musica.project import MusicaProject
from musica.recording_capture import (
    SimulatedInputBackend,
    build_recording_capture_plan,
    deterministic_input_payload,
    run_recording_capture_simulation,
    simulated_input_capability,
    simulated_input_capability_sha256,
)
from test_rtio_r0_realtime_simulated_backend import _fixture


def test_capture_plan_binds_exact_accepted_source_and_input_capability(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    plan = build_recording_capture_plan(
        project,
        revision_id,
        sample_rate_hz=8000,
        input_channels=1,
        block_size_frames=256,
        capture_frames=2048,
    )
    capability = simulated_input_capability()

    assert capability["backend_id"] == "musica-simulated-input-v0"
    assert capability["classification"] == "simulated_test_input_backend"
    assert capability["deterministic"] is True
    assert capability["host_native_input_claimed"] is False
    assert plan["classification"] == "derived_noncanonical"
    assert plan["source"]["revision_id"] == revision_id
    assert plan["input"]["capability_sha256"] == simulated_input_capability_sha256()
    assert plan["sample_rate_hz"] == 8000
    assert plan["input_channels"] == 1
    assert plan["block_size_frames"] == 256
    assert plan["capture_frames"] == 2048
    assert plan["policy"]["source_rate_policy"] == "exact_match_required_no_resampling"
    assert plan["policy"]["runtime_state_is_canonical"] is False
    assert plan["policy"]["captured_payload_is_canonical"] is False


def test_normal_capture_is_repeat_exact_and_matches_deterministic_source(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    head_before = project.head_revision_id("main")

    first = run_recording_capture_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        input_channels=2,
        block_size_frames=256,
        capture_frames=2050,
    )
    second = run_recording_capture_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        input_channels=2,
        block_size_frames=256,
        capture_frames=2050,
    )

    assert first.plan == second.plan
    assert first.block_trace == second.block_trace
    assert first.captured_payload == second.captured_payload
    assert first.report == second.report
    assert first.captured_payload == deterministic_input_payload(
        start_frame=0,
        frame_count=2050,
        input_channels=2,
    )
    assert first.report["metrics"] == {
        "blocks_requested": 9,
        "blocks_captured": 9,
        "frames_requested": 2050,
        "frames_captured": 2050,
        "final_capture_cursor": 2050,
        "error_count": 0,
        "short_fill_count": 0,
        "late_count": 0,
        "dropout_equivalent_count": 0,
    }
    assert first.report["lifecycle"] == [
        "CLOSED",
        "OPEN",
        "READY",
        "CAPTURING",
        "STOPPED",
        "FINALIZED",
        "CLOSED",
    ]
    assert first.report["accepted_head_unchanged"] is True
    assert first.report["captured_payload_is_canonical"] is False
    assert project.head_revision_id("main") == head_before

    for index, block in enumerate(first.block_trace):
        assert block["block_index"] == index
        assert block["start_frame"] == (0 if index == 0 else first.block_trace[index - 1]["end_frame_exclusive"])
        assert block["requested_frame_count"] <= 256
        assert block["captured_frame_count"] == block["requested_frame_count"]
        assert block["status"] == "OK"
    assert first.block_trace[-1]["end_frame_exclusive"] == 2050
    assert first.block_trace[-1]["requested_frame_count"] == 2


def test_capture_failure_injection_is_deterministic_and_observable(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    head_before = project.head_revision_id("main")

    first = run_recording_capture_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        input_channels=1,
        block_size_frames=256,
        capture_frames=2048,
        force_error_block_indices=[1],
        force_short_fill_block_indices=[2],
        force_late_block_indices=[3],
    )
    second = run_recording_capture_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        input_channels=1,
        block_size_frames=256,
        capture_frames=2048,
        force_error_block_indices=[1],
        force_short_fill_block_indices=[2],
        force_late_block_indices=[3],
    )
    baseline = run_recording_capture_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        input_channels=1,
        block_size_frames=256,
        capture_frames=2048,
    )

    assert first.block_trace == second.block_trace
    assert first.captured_payload == second.captured_payload
    assert first.report == second.report
    assert first.report["metrics"]["error_count"] == 1
    assert first.report["metrics"]["short_fill_count"] == 1
    assert first.report["metrics"]["late_count"] == 1
    assert first.report["metrics"]["dropout_equivalent_count"] == 3
    assert first.report["metrics"]["frames_requested"] == 2048
    assert first.report["metrics"]["frames_captured"] == 1664
    assert first.report["metrics"]["final_capture_cursor"] == 2048
    assert first.report["payload"]["payload_sha256"] != baseline.report["payload"]["payload_sha256"]
    assert first.block_trace[1]["status"] == "ERROR"
    assert first.block_trace[1]["captured_frame_count"] == 0
    assert first.block_trace[2]["status"] == "SHORT_FILL"
    assert first.block_trace[2]["captured_frame_count"] == 128
    assert first.block_trace[3]["status"] == "LATE"
    assert first.block_trace[3]["captured_frame_count"] == 256
    assert project.head_revision_id("main") == head_before


def test_invalid_input_config_and_lifecycle_fail_closed(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    with pytest.raises(ContractError, match="unsupported sample rate"):
        build_recording_capture_plan(
            project,
            revision_id,
            sample_rate_hz=16000,
            input_channels=1,
            block_size_frames=256,
            capture_frames=1024,
        )
    with pytest.raises(ContractError, match="unsupported input channels"):
        build_recording_capture_plan(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=3,
            block_size_frames=256,
            capture_frames=1024,
        )
    with pytest.raises(ContractError, match="unsupported block size"):
        build_recording_capture_plan(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=1,
            block_size_frames=333,
            capture_frames=1024,
        )
    with pytest.raises(ContractError, match="capture_frames"):
        build_recording_capture_plan(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=1,
            block_size_frames=256,
            capture_frames=0,
        )
    with pytest.raises(ContractError, match="outside capture trace"):
        run_recording_capture_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=1,
            block_size_frames=256,
            capture_frames=1024,
            force_error_block_indices=[999],
        )
    with pytest.raises(ContractError, match="cannot overlap"):
        run_recording_capture_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=1,
            block_size_frames=256,
            capture_frames=1024,
            force_error_block_indices=[1],
            force_short_fill_block_indices=[1],
        )

    backend = SimulatedInputBackend(
        sample_rate_hz=8000,
        input_channels=1,
        block_size_frames=256,
        capture_frames=1024,
    )
    with pytest.raises(ContractError, match="capture requires CAPTURING"):
        backend.capture_block(start_frame=0, requested_frame_count=256)
    with pytest.raises(ContractError, match="illegal lifecycle transition"):
        backend.start()
    backend.open()
    backend.ready()
    backend.start()
    with pytest.raises(ContractError, match="outside capture plan"):
        backend.capture_block(start_frame=900, requested_frame_count=256)
    backend.stop()
    backend.finalize()
    backend.close()
    with pytest.raises(ContractError, match="illegal lifecycle transition"):
        backend.close()


def test_capture_plan_and_runtime_reopen_exactness(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    before = run_recording_capture_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        input_channels=2,
        block_size_frames=128,
        capture_frames=1537,
    )

    archive = project.export_to(tmp_path / "rec-r0.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    after = run_recording_capture_simulation(
        reopened,
        revision_id,
        sample_rate_hz=8000,
        input_channels=2,
        block_size_frames=128,
        capture_frames=1537,
    )

    assert after.plan == before.plan
    assert after.block_trace == before.block_trace
    assert after.captured_payload == before.captured_payload
    assert after.report == before.report
    assert reopened.verify_integrity()["status"] == "PASS"
