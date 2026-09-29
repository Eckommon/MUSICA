from __future__ import annotations

from pathlib import Path

import pytest

from musica.contracts import ContractError
from musica.project import MusicaProject
from musica.realtime_callback import (
    CallbackEngine,
    DeterministicCallbackAdapter,
    callback_adapter_capability,
    callback_adapter_capability_sha256,
    run_callback_harness,
)
from musica.realtime_engine import run_realtime_simulation
from test_rtio_r0_realtime_simulated_backend import _fixture


def test_callback_adapter_capability_is_explicit_and_non_host_native() -> None:
    capability = callback_adapter_capability()
    assert capability["adapter_id"] == "musica-deterministic-callback-adapter-v0"
    assert capability["classification"] == "deterministic_test_adapter"
    assert capability["deterministic"] is True
    assert capability["callback_model"] == "registered_pull_callback"
    assert capability["supported_failure_injection"] == ["ERROR", "SHORT_FILL", "LATE"]
    assert capability["host_native_device_claimed"] is False
    assert len(callback_adapter_capability_sha256()) == 64


def test_normal_callback_run_is_repeat_exact_and_matches_rtio_r0_sink(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    head_before = project.head_revision_id("main")

    first = run_callback_harness(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=1024,
    )
    second = run_callback_harness(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=1024,
    )
    r0 = run_realtime_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=1024,
    )

    assert first.plan == second.plan == r0.plan
    assert first.transactions == second.transactions
    assert first.sink_payload == second.sink_payload == r0.sink_payload
    assert first.report == second.report
    assert first.report["completion_status"] == "END_OF_STREAM"
    assert first.report["accepted_head_unchanged"] is True
    assert first.report["runtime_state_is_canonical"] is False
    assert first.report["metrics"]["error_count"] == 0
    assert first.report["metrics"]["short_fill_count"] == 0
    assert first.report["metrics"]["late_count"] == 0
    assert first.report["metrics"]["frames_requested"] == first.plan["duration_frames"]
    assert first.report["metrics"]["frames_delivered"] == first.plan["duration_frames"]
    assert first.report["metrics"]["final_frame_cursor"] == first.plan["duration_frames"]
    assert project.head_revision_id("main") == head_before

    assert len(first.transactions) == 94
    assert first.transactions[-1]["request"]["requested_frame_count"] == 768
    assert first.transactions[-1]["response"]["delivered_frame_count"] == 768
    assert first.transactions[-1]["request"]["end_frame_exclusive"] == 96000

    for index, transaction in enumerate(first.transactions):
        request = transaction["request"]
        response = transaction["response"]
        assert request["callback_index"] == index
        assert response["callback_index"] == index
        assert response["start_frame"] == request["start_frame"]
        assert response["end_frame_exclusive"] == request["end_frame_exclusive"]
        assert response["requested_frame_count"] == request["requested_frame_count"]
        if index:
            assert request["start_frame"] == first.transactions[index - 1]["request"][
                "end_frame_exclusive"
            ]


def test_callback_failure_modes_are_deterministic_observable_and_advance_timeline(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    first = run_callback_harness(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
        force_error_callback_indices=[1],
        force_short_fill_callback_indices=[2],
        force_late_callback_indices=[3],
    )
    second = run_callback_harness(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
        force_error_callback_indices=[1],
        force_short_fill_callback_indices=[2],
        force_late_callback_indices=[3],
    )
    baseline = run_callback_harness(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
    )

    assert first.transactions == second.transactions
    assert first.sink_payload == second.sink_payload
    assert first.report == second.report
    assert first.report["completion_status"] == "END_OF_STREAM"
    assert first.report["metrics"]["error_count"] == 1
    assert first.report["metrics"]["short_fill_count"] == 1
    assert first.report["metrics"]["late_count"] == 1
    assert first.report["metrics"]["xrun_equivalent_count"] == 3
    assert first.report["metrics"]["final_frame_cursor"] == first.plan["duration_frames"]
    assert first.report["metrics"]["frames_requested"] == first.plan["duration_frames"]
    assert first.report["metrics"]["frames_delivered"] == first.plan["duration_frames"] - 384
    assert first.report["sink"]["payload_sha256"] != baseline.report["sink"]["payload_sha256"]

    assert first.transactions[1]["response"]["status"] == "ERROR"
    assert first.transactions[1]["response"]["delivered_frame_count"] == 0
    assert first.transactions[2]["response"]["status"] == "SHORT_FILL"
    assert first.transactions[2]["response"]["delivered_frame_count"] == 128
    assert first.transactions[3]["response"]["status"] == "OK"
    assert first.transactions[3]["response"]["late"] is True


def test_explicit_early_stop_has_exact_cursor_and_sink_prefix(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    stopped = run_callback_harness(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
        stop_after_callbacks=3,
    )
    full = run_callback_harness(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
    )

    assert stopped.report["completion_status"] == "STOPPED_EARLY"
    assert stopped.report["metrics"]["callbacks_requested"] == 3
    assert stopped.report["metrics"]["final_frame_cursor"] == 768
    assert stopped.report["metrics"]["frames_requested"] == 768
    assert stopped.report["metrics"]["frames_delivered"] == 768
    assert stopped.sink_payload == full.sink_payload[: 768 * 4]


def test_callback_engine_and_adapter_illegal_lifecycle_fail_closed(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    adapter = DeterministicCallbackAdapter()
    with pytest.raises(ContractError, match="RUNNING state"):
        adapter.request()
    with pytest.raises(ContractError, match="registered callback"):
        adapter.start()
    adapter.open()
    with pytest.raises(ContractError, match="OPEN state"):
        adapter.open()

    engine = CallbackEngine(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=1024,
    )
    adapter.register_callback(engine.callback)
    with pytest.raises(ContractError, match="already registered"):
        adapter.register_callback(engine.callback)
    adapter.start()
    while engine.frame_cursor < engine.plan["duration_frames"]:
        adapter.request()
    with pytest.raises(ContractError, match="end-of-stream"):
        adapter.request()
    adapter.stop()
    adapter.close()
    with pytest.raises(ContractError, match="illegal lifecycle transition"):
        adapter.close()

    with pytest.raises(ContractError, match="outside execution trace"):
        run_callback_harness(
            project,
            revision_id,
            sample_rate_hz=8000,
            force_error_callback_indices=[999999],
        )
    with pytest.raises(ContractError, match="overlap"):
        run_callback_harness(
            project,
            revision_id,
            sample_rate_hz=8000,
            force_error_callback_indices=[1],
            force_short_fill_callback_indices=[1],
        )
    with pytest.raises(ContractError, match="outside valid callback range"):
        run_callback_harness(
            project,
            revision_id,
            sample_rate_hz=8000,
            stop_after_callbacks=0,
        )


def test_callback_harness_reopen_exactness(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    before = run_callback_harness(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=1024,
        force_late_callback_indices=[2],
    )

    archive = project.export_to(tmp_path / "rtio-r1.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    after = run_callback_harness(
        reopened,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=1024,
        force_late_callback_indices=[2],
    )

    assert after.plan == before.plan
    assert after.transactions == before.transactions
    assert after.sink_payload == before.sink_payload
    assert after.report == before.report
    assert reopened.verify_integrity()["status"] == "PASS"
