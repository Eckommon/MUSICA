from __future__ import annotations

from pathlib import Path

import pytest

from musica.audio_assets import list_audio_assets
from musica.audio_contracts import audio_material_from_blueprint
from musica.automation_edit import automation_material_sha256
from musica.audio_edit import audio_material_sha256, blueprint_sha256
from musica.contracts import ContractError
from musica.project import MusicaProject
from musica.recording_capture import SimulatedCaptureRun, run_recording_capture_simulation
from musica.recording_finalize import (
    accept_recording_finalize_preview,
    build_recording_finalize_preview,
    canonical_capture_wav_bytes,
)
from musica.routed_mixer import render_routed_mix
from musica.routing_contracts import routing_material_from_blueprint, routing_material_sha256
from test_rtio_r0_realtime_simulated_backend import _fixture


def _source(parent: dict) -> dict:
    routing = routing_material_from_blueprint(parent)
    assert routing is not None
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(routing),
        "automation_material_sha256": automation_material_sha256(parent),
    }


def _candidate(parent: dict, run: SimulatedCaptureRun, *, candidate_id: str = "REC-R1-C-001",
               track_id: str = "AT-001", clip_id: str = "REC-CLIP-001",
               timeline_start_seconds: float = 0.2) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "recording_finalize_to_audio_material",
        "source": _source(parent),
        "capture": {
            "recording_capture_plan_sha256": run.plan["recording_capture_plan_sha256"],
            "recording_capture_run_report_sha256": run.report["recording_capture_run_report_sha256"],
            "payload_sha256": run.report["payload"]["payload_sha256"],
            "payload_size_bytes": run.report["payload"]["payload_size_bytes"],
            "sample_rate_hz": run.report["payload"]["sample_rate_hz"],
            "channels": run.report["payload"]["channels"],
            "captured_frames": run.report["payload"]["captured_frames"],
            "sample_format": run.report["payload"]["format"],
        },
        "destination": {
            "track_id": track_id,
            "clip_id": clip_id,
            "timeline_start_seconds": timeline_start_seconds,
            "gain_db": 0.0,
        },
        "actor": {"kind": "user", "actor_id": "rec-r1-test"},
        "reason": candidate_id,
        "preview_only": True,
    }


def _capture(project, accepted, *, frames: int = 800) -> SimulatedCaptureRun:
    return run_recording_capture_simulation(
        project,
        accepted["project"]["revision_id"],
        sample_rate_hz=8000,
        input_channels=1,
        block_size_frames=256,
        capture_frames=frames,
    )


def test_recording_preview_is_asset_and_head_side_effect_free_then_accepts_once(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    run = _capture(project, accepted)
    head_before = project.head_revision_id("main")
    assets_before = list_audio_assets(project)
    baseline = render_routed_mix(project, head_before, mix_sample_rate_hz=8000)

    preview = build_recording_finalize_preview(
        project, accepted, _candidate(accepted, run), run
    )
    assert preview.ready and preview.blueprint is not None
    assert project.head_revision_id("main") == head_before
    assert list_audio_assets(project) == assets_before
    assert preview.prospective_asset_id == f"sha256:{preview.prospective_wav_sha256}"
    assert preview.prospective_wav_sha256 == __import__("hashlib").sha256(
        canonical_capture_wav_bytes(run)
    ).hexdigest()

    with pytest.raises(ContractError, match="trusted audio Preview/Accept authority"):
        project.commit_revision(preview.blueprint)
    assert project.head_revision_id("main") == head_before

    record = accept_recording_finalize_preview(project, preview, run)
    accepted_id = str(record["revision_id"])
    assert record["parent_revision_id"] == head_before
    assert project.head_revision_id("main") == accepted_id
    assert len(list_audio_assets(project)) == len(assets_before) + 1

    material = audio_material_from_blueprint(project.read_revision(accepted_id))
    assert material is not None
    track = next(item for item in material["tracks"] if item["track_id"] == "AT-001")
    clip = next(item for item in track["clips"] if item["clip_id"] == "REC-CLIP-001")
    assert clip["asset_id"] == preview.prospective_asset_id
    assert clip["source_in_seconds"] == 0.0
    assert clip["source_out_seconds"] == 0.1
    assert clip["timeline_start_seconds"] == 0.2
    assert clip["gain_db"] == 0.0

    after = render_routed_mix(project, accepted_id, mix_sample_rate_hz=8000)
    assert after.wav_sha256 != baseline.wav_sha256

    with pytest.raises(ContractError, match="stale|HEAD changed"):
        accept_recording_finalize_preview(project, preview, run)


def test_recording_capture_tamper_failure_capture_missing_track_duplicate_clip_and_discard_block(
    tmp_path: Path,
) -> None:
    project, accepted = _fixture(tmp_path)
    run = _capture(project, accepted)
    head_before = project.head_revision_id("main")
    assets_before = list_audio_assets(project)

    tampered = SimulatedCaptureRun(
        plan=run.plan,
        block_trace=run.block_trace,
        captured_payload=run.captured_payload + b"x",
        report=run.report,
    )
    tampered_preview = build_recording_finalize_preview(
        project, accepted, _candidate(accepted, run, candidate_id="REC-TAMPER"), tampered
    )
    assert not tampered_preview.ready
    assert "payload SHA-256 mismatch" in tampered_preview.authority_result["conflicts"][0]["reason"]

    failed = run_recording_capture_simulation(
        project,
        accepted["project"]["revision_id"],
        sample_rate_hz=8000,
        input_channels=1,
        block_size_frames=256,
        capture_frames=800,
        force_short_fill_block_indices=[1],
    )
    failed_preview = build_recording_finalize_preview(
        project, accepted, _candidate(accepted, failed, candidate_id="REC-FAILED"), failed
    )
    assert not failed_preview.ready
    assert "complete captured frame count" in failed_preview.authority_result["conflicts"][0]["reason"]

    missing = build_recording_finalize_preview(
        project,
        accepted,
        _candidate(accepted, run, candidate_id="REC-MISSING", track_id="AT-MISSING"),
        run,
    )
    assert not missing.ready
    assert missing.authority_result["conflicts"][0]["code"] == "UNKNOWN_TRACK"

    duplicate = build_recording_finalize_preview(
        project,
        accepted,
        _candidate(accepted, run, candidate_id="REC-DUP", clip_id="AC-001"),
        run,
    )
    assert not duplicate.ready
    assert duplicate.authority_result["conflicts"][0]["code"] == "DUPLICATE_CLIP"

    discard = build_recording_finalize_preview(
        project, accepted, _candidate(accepted, run, candidate_id="REC-DISCARD", clip_id="REC-DISCARD"), run
    )
    assert discard.ready
    del discard
    assert project.head_revision_id("main") == head_before
    assert list_audio_assets(project) == assets_before


def test_stale_recording_preview_and_capture_binding_fail_closed(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    run = _capture(project, accepted)
    stale_preview = build_recording_finalize_preview(
        project, accepted, _candidate(accepted, run, candidate_id="REC-STALE", clip_id="REC-STALE"), run
    )
    advance_preview = build_recording_finalize_preview(
        project, accepted, _candidate(accepted, run, candidate_id="REC-ADVANCE", clip_id="REC-ADVANCE"), run
    )
    assert stale_preview.ready and advance_preview.ready
    accept_recording_finalize_preview(project, advance_preview, run)
    with pytest.raises(ContractError, match="stale|HEAD changed"):
        accept_recording_finalize_preview(project, stale_preview, run)

    project2, accepted2 = _fixture(tmp_path / "binding")
    run2 = _capture(project2, accepted2)
    candidate = _candidate(accepted2, run2, candidate_id="REC-BINDING")
    candidate["capture"]["payload_sha256"] = "0" * 64
    blocked = build_recording_finalize_preview(project2, accepted2, candidate, run2)
    assert not blocked.ready
    assert "candidate capture binding mismatch" in blocked.authority_result["conflicts"][0]["reason"]


def test_recording_accept_reopen_preserves_asset_clip_and_routed_wav(tmp_path: Path) -> None:
    project, accepted = _fixture(tmp_path)
    run = _capture(project, accepted, frames=1024)
    preview = build_recording_finalize_preview(
        project,
        accepted,
        _candidate(
            accepted,
            run,
            candidate_id="REC-REOPEN",
            clip_id="REC-REOPEN",
            timeline_start_seconds=0.5,
        ),
        run,
    )
    assert preview.ready
    record = accept_recording_finalize_preview(project, preview, run)
    revision_id = str(record["revision_id"])
    before_blueprint = project.read_revision(revision_id)
    before_material = audio_material_from_blueprint(before_blueprint)
    before_render = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    before_assets = list_audio_assets(project)

    archive = project.export_to(tmp_path / "rec-r1.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    after_blueprint = reopened.read_revision(revision_id)
    after_material = audio_material_from_blueprint(after_blueprint)
    after_render = render_routed_mix(reopened, revision_id, mix_sample_rate_hz=8000)

    assert after_material == before_material
    assert list_audio_assets(reopened) == before_assets
    assert after_render.plan == before_render.plan
    assert after_render.wav_bytes == before_render.wav_bytes
    assert reopened.verify_integrity()["status"] == "PASS"
