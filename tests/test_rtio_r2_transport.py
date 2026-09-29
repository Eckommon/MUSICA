from __future__ import annotations

from pathlib import Path

import pytest

from musica.contracts import ContractError
from musica.project import MusicaProject
from musica.realtime_callback import run_callback_harness
from musica.realtime_transport import ExactFrameTransport
from test_rtio_r0_realtime_simulated_backend import _fixture


def _full_source(project, revision_id: str, *, block_size_frames: int = 256) -> bytes:
    return run_callback_harness(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=block_size_frames,
    ).sink_payload


def test_transport_play_to_eos_is_repeat_exact_and_matches_callback_source(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    head_before = project.head_revision_id("main")

    first = ExactFrameTransport(
        project, revision_id, sample_rate_hz=8000, block_size_frames=1024
    )
    first.play()
    first.drain_to_eos()
    run_a = first.finalize()

    second = ExactFrameTransport(
        project, revision_id, sample_rate_hz=8000, block_size_frames=1024
    )
    second.play()
    second.drain_to_eos()
    run_b = second.finalize()

    source = _full_source(project, revision_id, block_size_frames=1024)
    assert run_a.plan == run_b.plan
    assert run_a.events == run_b.events
    assert run_a.callback_transactions == run_b.callback_transactions
    assert run_a.sink_payload == run_b.sink_payload == source
    assert run_a.report == run_b.report
    assert run_a.report["metrics"]["final_state"] == "END_OF_STREAM"
    assert run_a.report["metrics"]["final_playhead_frame"] == 96000
    assert run_a.report["metrics"]["callbacks_requested"] == 94
    assert run_a.report["metrics"]["frames_requested"] == 96000
    assert run_a.report["metrics"]["frames_delivered"] == 96000
    assert run_a.report["latency"]["configured_block_size_frames"] == 1024
    assert run_a.report["latency"]["nominal_output_latency_frames"] == 0
    assert run_a.report["latency"]["host_observed_latency_available"] is False
    assert run_a.report["latency"]["wall_clock_guarantee_claimed"] is False
    assert project.head_revision_id("main") == head_before


def test_stop_seek_play_resets_callback_index_and_uses_exact_requested_frame(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    source = _full_source(project, revision_id, block_size_frames=256)

    transport = ExactFrameTransport(
        project, revision_id, sample_rate_hz=8000, block_size_frames=256
    )
    transport.play()
    transport.callback()
    transport.callback()
    transport.stop()
    assert transport.playhead_frame == 512

    transport.seek(48000)
    transport.play()
    transport.callback()
    first_after_seek = transport.callback_transactions[-1]
    assert first_after_seek["request"]["callback_index"] == 0
    assert first_after_seek["request"]["start_frame"] == 48000
    assert first_after_seek["request"]["end_frame_exclusive"] == 48256
    transport.drain_to_eos()
    run = transport.finalize()

    expected = source[: 512 * 4] + source[48000 * 4 :]
    assert run.sink_payload == expected
    assert run.report["metrics"]["play_count"] == 2
    assert run.report["metrics"]["stop_count"] == 1
    assert run.report["metrics"]["seek_count"] == 1
    assert run.report["metrics"]["transport_discontinuity_count"] == 1
    assert run.report["metrics"]["final_state"] == "END_OF_STREAM"
    assert run.report["metrics"]["final_playhead_frame"] == 96000

    seek_events = [event for event in run.events if event["command"] == "SEEK"]
    assert len(seek_events) == 1
    assert seek_events[0]["playhead_before"] == 512
    assert seek_events[0]["playhead_after"] == 48000
    assert seek_events[0]["target_frame"] == 48000


def test_transport_failure_metrics_are_deterministic_and_do_not_change_timeline(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    def execute():
        transport = ExactFrameTransport(
            project, revision_id, sample_rate_hz=8000, block_size_frames=256
        )
        transport.play()
        transport.drain_to_eos(
            force_error_callback_indices={1},
            force_short_fill_callback_indices={2},
            force_late_callback_indices={3},
        )
        return transport.finalize()

    first = execute()
    second = execute()
    assert first.events == second.events
    assert first.callback_transactions == second.callback_transactions
    assert first.sink_payload == second.sink_payload
    assert first.report == second.report

    metrics = first.report["metrics"]
    assert metrics["error_count"] == 1
    assert metrics["short_fill_count"] == 1
    assert metrics["late_count"] == 1
    assert metrics["xrun_dropout_equivalent_count"] == 3
    assert metrics["final_playhead_frame"] == 96000
    assert metrics["final_callback_cursor"] == 96000
    assert metrics["frames_requested"] == 96000
    assert metrics["frames_delivered"] == 96000 - 384


def test_transport_invalid_state_seek_and_cursor_paths_fail_closed(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    transport = ExactFrameTransport(
        project, revision_id, sample_rate_hz=8000, block_size_frames=256
    )
    with pytest.raises(ContractError, match="CALLBACK requires PLAYING"):
        transport.callback()
    with pytest.raises(ContractError, match="STOP requires PLAYING"):
        transport.stop()
    with pytest.raises(ContractError, match="outside valid frame range"):
        transport.seek(-1)
    with pytest.raises(ContractError, match="outside valid frame range"):
        transport.seek(96001)

    transport.play()
    with pytest.raises(ContractError, match="PLAY requires STOPPED"):
        transport.play()
    with pytest.raises(ContractError, match="SEEK requires STOPPED or END_OF_STREAM"):
        transport.seek(10)
    with pytest.raises(ContractError, match="non-PLAYING"):
        transport.finalize()
    transport.stop()

    with pytest.raises(ContractError, match="STOP requires PLAYING"):
        transport.stop()
    transport.seek(96000)
    with pytest.raises(ContractError, match="requires SEEK before PLAY"):
        transport.play()

    transport.seek(0)
    transport.play()
    with pytest.raises(ContractError, match="outside current play segment"):
        transport.drain_to_eos(force_late_callback_indices={999999})


def test_seek_from_eos_and_fresh_reopen_are_exact(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    before = ExactFrameTransport(
        project, revision_id, sample_rate_hz=8000, block_size_frames=512
    )
    before.play()
    before.drain_to_eos()
    before.seek(32000)
    before.play()
    before.drain_to_eos()
    run_before = before.finalize()

    archive = project.export_to(tmp_path / "rtio-r2.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    after = ExactFrameTransport(
        reopened, revision_id, sample_rate_hz=8000, block_size_frames=512
    )
    after.play()
    after.drain_to_eos()
    after.seek(32000)
    after.play()
    after.drain_to_eos()
    run_after = after.finalize()

    assert run_after.plan == run_before.plan
    assert run_after.events == run_before.events
    assert run_after.callback_transactions == run_before.callback_transactions
    assert run_after.sink_payload == run_before.sink_payload
    assert run_after.report == run_before.report
    assert reopened.verify_integrity()["status"] == "PASS"
