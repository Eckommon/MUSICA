from __future__ import annotations

import io
import wave
from pathlib import Path

import pytest

from musica.contracts import ContractError
from musica.project import MusicaProject
from musica.realtime_engine import (
    SimulatedOutputBackend,
    build_realtime_execution_plan,
    run_realtime_simulation,
    simulated_backend_capability,
    simulated_backend_capability_sha256,
)
from musica.routed_mixer import render_routed_mix
from test_mram_r1_routing_authority_mixer import _accept_routing
from test_mram_r2_native_mixer_automation import _accept_native, _lane


def _fixture(tmp_path: Path):
    project, routed = _accept_routing(tmp_path)
    lane = _lane(
        "AUTO-AT001-GAIN",
        scope="audio_track",
        owner_id="AT-001",
        parameter_id="mixer.gain_db",
        points=[
            ("RT-P1", 0.0, -3.0, "linear"),
            ("RT-P2", 1.0, -6.0, "hold"),
        ],
    )
    accepted = _accept_native(project, routed, "RTIO-R0-NATIVE", [lane])
    return project, accepted


def _wav_payload(wav_bytes: bytes) -> bytes:
    with wave.open(io.BytesIO(wav_bytes), "rb") as reader:
        assert reader.getnchannels() == 2
        assert reader.getsampwidth() == 2
        return reader.readframes(reader.getnframes())


def test_realtime_plan_binds_exact_routed_source_and_backend_capability(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    routed = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    plan = build_realtime_execution_plan(
        project,
        revision_id,
        sample_rate_hz=8000,
        output_channels=2,
        block_size_frames=256,
    )
    capability = simulated_backend_capability()

    assert capability["backend_id"] == "musica-simulated-output-v0"
    assert capability["deterministic"] is True
    assert plan["classification"] == "derived_noncanonical"
    assert plan["source"]["revision_id"] == revision_id
    assert plan["source"]["routed_mix_plan_sha256"] == routed.plan["routed_mix_plan_sha256"]
    assert plan["source"]["routed_wav_sha256"] == routed.wav_sha256
    assert plan["backend"]["capability_sha256"] == simulated_backend_capability_sha256()
    assert plan["sample_rate_hz"] == 8000
    assert plan["output_channels"] == 2
    assert plan["block_size_frames"] == 256
    assert plan["policy"]["source_rate_policy"] == "exact_match_required_no_resampling"
    assert plan["policy"]["runtime_state_is_canonical"] is False


def test_simulated_realtime_run_is_repeat_exact_and_concatenates_source_pcm(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    head_before = project.head_revision_id("main")
    routed = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)

    first = run_realtime_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
    )
    second = run_realtime_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
    )

    assert first.plan == second.plan
    assert first.block_trace == second.block_trace
    assert first.sink_payload == second.sink_payload
    assert first.report == second.report
    assert first.sink_payload == _wav_payload(routed.wav_bytes)
    assert first.report["metrics"]["frames_written"] == first.plan["duration_frames"]
    assert first.report["metrics"]["frames_requested"] == first.plan["duration_frames"]
    assert first.report["metrics"]["blocks_written"] == len(first.block_trace)
    assert first.report["metrics"]["xrun_count"] == 0
    assert first.report["lifecycle"] == ["CLOSED", "OPEN", "RUNNING", "STOPPED", "CLOSED"]
    assert first.report["accepted_head_unchanged"] is True
    assert project.head_revision_id("main") == head_before

    for index, block in enumerate(first.block_trace):
        assert block["block_index"] == index
        assert block["start_frame"] < block["end_frame_exclusive"]
        assert block["frame_count"] <= 256
        if index:
            assert block["start_frame"] == first.block_trace[index - 1]["end_frame_exclusive"]
    assert first.block_trace[-1]["end_frame_exclusive"] == first.plan["duration_frames"]


def test_forced_xrun_is_deterministic_observable_and_does_not_mutate_head(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    head_before = project.head_revision_id("main")

    first = run_realtime_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
        force_xrun_block_indices=[1],
    )
    second = run_realtime_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
        force_xrun_block_indices=[1],
    )
    baseline = run_realtime_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
    )

    assert first.report == second.report
    assert first.sink_payload == second.sink_payload
    assert first.report["metrics"]["xrun_count"] == 1
    assert first.report["metrics"]["blocks_requested"] == len(first.block_trace)
    assert first.report["metrics"]["blocks_written"] == len(first.block_trace) - 1
    assert first.report["metrics"]["frames_written"] == (
        first.plan["duration_frames"] - first.block_trace[1]["frame_count"]
    )
    assert first.report["sink"]["payload_sha256"] != baseline.report["sink"]["payload_sha256"]
    assert project.head_revision_id("main") == head_before


def test_invalid_realtime_config_and_lifecycle_fail_closed(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]

    with pytest.raises(ContractError, match="unsupported sample rate"):
        build_realtime_execution_plan(
            project, revision_id, sample_rate_hz=16000, block_size_frames=256
        )
    with pytest.raises(ContractError, match="unsupported output channels"):
        build_realtime_execution_plan(
            project,
            revision_id,
            sample_rate_hz=8000,
            output_channels=1,
            block_size_frames=256,
        )
    with pytest.raises(ContractError, match="unsupported block size"):
        build_realtime_execution_plan(
            project, revision_id, sample_rate_hz=8000, block_size_frames=333
        )
    with pytest.raises(ContractError, match="source sample-rate match"):
        build_realtime_execution_plan(
            project, revision_id, sample_rate_hz=44100, block_size_frames=256
        )
    with pytest.raises(ContractError, match="outside execution trace"):
        run_realtime_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=256,
            force_xrun_block_indices=[999999],
        )

    backend = SimulatedOutputBackend(
        sample_rate_hz=8000,
        output_channels=2,
        block_size_frames=256,
    )
    with pytest.raises(ContractError, match="write requires RUNNING"):
        backend.write_block(b"\x00" * 4, frame_count=1)
    with pytest.raises(ContractError, match="illegal lifecycle transition"):
        backend.start()
    backend.open()
    backend.start()
    with pytest.raises(ContractError, match="payload size mismatch"):
        backend.write_block(b"\x00" * 2, frame_count=1)
    backend.stop()
    backend.close()
    with pytest.raises(ContractError, match="illegal lifecycle transition"):
        backend.close()


def test_realtime_plan_and_run_reopen_exactness(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    before = run_realtime_simulation(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=128,
    )

    archive = project.export_to(tmp_path / "rtio-r0.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    after = run_realtime_simulation(
        reopened,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=128,
    )

    assert after.plan == before.plan
    assert after.block_trace == before.block_trace
    assert after.sink_payload == before.sink_payload
    assert after.report == before.report
    assert reopened.verify_integrity()["status"] == "PASS"
