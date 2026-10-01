from __future__ import annotations

import copy
from pathlib import Path

import pytest

from musica.audio_assets import list_audio_assets
from musica.audio_contracts import audio_material_from_blueprint
from musica.routed_mixer import render_routed_mix
from musica.studio import StudioService, StudioServiceError
from musica.studio_recording import StudioRecordingSurface
from test_rtio_r0_realtime_simulated_backend import _fixture


def _studio_fixture(tmp_path: Path):
    project, accepted = _fixture(tmp_path)
    workspace = project.root.parent
    slug = project.root.name.removesuffix(".musica")
    service = StudioService(workspace)
    opened = service.open_project_session(
        project_slug=slug,
        session_id="rec-r3-session",
    )
    assert opened["session"]["head_revision_id"] == accepted["project"]["revision_id"]
    surface = StudioRecordingSurface(service)
    return project, accepted, service, surface, slug


def _track_clip_ids(project, revision_id: str, track_id: str = "AT-001") -> set[str]:
    material = audio_material_from_blueprint(project.read_revision(revision_id))
    assert material is not None
    track = next(item for item in material["tracks"] if item["track_id"] == track_id)
    return {str(clip["clip_id"]) for clip in track["clips"]}


def test_studio_recording_runtime_is_truthful_noncanonical_and_head_unchanged(
    tmp_path: Path,
) -> None:
    project, accepted, service, surface, _ = _studio_fixture(tmp_path)
    head_before = project.head_revision_id("main")
    assets_before = list_audio_assets(project)

    initial = surface.recording_view("rec-r3-session")
    assert initial["revision_id"] == head_before
    assert initial["runtime"] is None
    assert initial["authority"]["recording_runtime_is_canonical"] is False
    assert initial["authority"]["runtime_may_import_assets"] is False
    assert initial["authority"]["runtime_may_commit_audio_material"] is False

    view = surface.run_capture_monitor(
        "rec-r3-session",
        sample_rate_hz=8000,
        input_channels=2,
        block_size_frames=256,
        capture_frames=800,
        monitor_enabled=True,
    )
    runtime = view["runtime"]
    assert runtime is not None
    assert runtime["source_revision_id"] == head_before
    assert runtime["capture_clean"] is True
    assert runtime["capture_metrics"]["frames_captured"] == 800
    assert runtime["monitor_metrics"]["frames_written"] == 800
    assert runtime["monitor_enabled"] is True
    assert project.head_revision_id("main") == head_before
    assert list_audio_assets(project) == assets_before
    assert service.inspect_session("rec-r3-session")["head_revision_id"] == head_before


def test_studio_recording_preview_is_side_effect_free_and_accepts_through_rec_r1(
    tmp_path: Path,
) -> None:
    project, accepted, service, surface, _ = _studio_fixture(tmp_path)
    head_before = project.head_revision_id("main")
    assets_before = list_audio_assets(project)
    clips_before = _track_clip_ids(project, head_before)
    baseline = render_routed_mix(project, head_before, mix_sample_rate_hz=8000)

    view = surface.run_capture_monitor("rec-r3-session")
    runtime_id = str(view["runtime"]["runtime_id"])
    preview_result = surface.preview_finalize(
        "rec-r3-session",
        runtime_id,
        track_id="AT-001",
        clip_id="REC-R3-CLIP-001",
        timeline_start_seconds=0.3,
        gain_db=0.0,
    )
    assert preview_result["preview_installed"] is True
    preview = preview_result["recording_finalize"]
    assert preview["authority_result"]["status"] == "READY_FOR_PREVIEW"
    assert preview["source_revision_id"] == head_before
    assert preview["destination_track_id"] == "AT-001"
    assert preview["destination_clip_id"] == "REC-R3-CLIP-001"
    assert project.head_revision_id("main") == head_before
    assert list_audio_assets(project) == assets_before
    assert _track_clip_ids(project, head_before) == clips_before

    accepted_result = surface.accept_finalize("rec-r3-session", runtime_id)
    new_head = str(accepted_result["accepted_head_revision_id"])
    assert new_head != head_before
    assert accepted_result["revision_record"]["parent_revision_id"] == head_before
    assert accepted_result["runtime_reset"] is True
    assert accepted_result["recording_view"]["runtime"] is None
    assert "REC-R3-CLIP-001" in _track_clip_ids(project, new_head)
    assert len(list_audio_assets(project)) == len(assets_before) + 1

    after = render_routed_mix(project, new_head, mix_sample_rate_hz=8000)
    assert after.wav_sha256 != baseline.wav_sha256
    assert service.inspect_session("rec-r3-session")["head_revision_id"] == new_head


def test_dirty_capture_blocked_discard_and_reset_do_not_mutate_project(
    tmp_path: Path,
) -> None:
    project, _, _, surface, _ = _studio_fixture(tmp_path)
    head_before = project.head_revision_id("main")
    assets_before = list_audio_assets(project)

    view = surface.run_capture_monitor(
        "rec-r3-session",
        force_short_fill_block_indices=[1],
    )
    runtime_id = str(view["runtime"]["runtime_id"])
    assert view["runtime"]["capture_clean"] is False

    blocked = surface.preview_finalize(
        "rec-r3-session",
        runtime_id,
        track_id="AT-001",
        clip_id="REC-R3-DIRTY",
    )
    assert blocked["preview_installed"] is False
    assert blocked["authority_result"]["status"] == "BLOCKED"
    assert "complete captured frame count" in blocked["authority_result"]["conflicts"][0]["reason"]
    assert project.head_revision_id("main") == head_before
    assert list_audio_assets(project) == assets_before

    discarded = surface.discard_finalize_preview("rec-r3-session", runtime_id)
    assert discarded["runtime"]["finalize_preview"] is None
    reset = surface.reset_runtime("rec-r3-session", runtime_id)
    assert reset["runtime"] is None
    assert project.head_revision_id("main") == head_before
    assert list_audio_assets(project) == assets_before


def test_recording_runtime_and_preview_fail_closed_after_head_advance(
    tmp_path: Path,
) -> None:
    project, _, service, surface, _ = _studio_fixture(tmp_path)
    view = surface.run_capture_monitor("rec-r3-session")
    runtime_id = str(view["runtime"]["runtime_id"])
    preview = surface.preview_finalize(
        "rec-r3-session",
        runtime_id,
        track_id="AT-001",
        clip_id="REC-R3-STALE",
    )
    assert preview["preview_installed"] is True

    head = project.head_revision_id("main")
    parent = project.read_revision(head)
    candidate = copy.deepcopy(parent)
    candidate["project"]["parent_revision_id"] = head
    candidate["project"]["revision_id"] = head + "-advance"
    candidate["provenance"]["source_revision"] = head
    candidate["provenance"]["change_reason"] = "advance for stale REC-R3 test"
    project.commit_revision(
        candidate,
        branch="main",
        actor="user",
        reason="advance for stale REC-R3 test",
    )

    with pytest.raises(StudioServiceError, match="stale.*HEAD changed"):
        surface.recording_view("rec-r3-session")
    with pytest.raises(StudioServiceError, match="stale.*HEAD changed"):
        surface.accept_finalize("rec-r3-session", runtime_id)
    assert service.inspect_session("rec-r3-session")["head_revision_id"].endswith("-advance")


def test_fresh_service_reopen_preserves_accepted_recording_and_resets_runtime(
    tmp_path: Path,
) -> None:
    project, _, service, surface, slug = _studio_fixture(tmp_path)
    view = surface.run_capture_monitor("rec-r3-session")
    runtime_id = str(view["runtime"]["runtime_id"])
    preview = surface.preview_finalize(
        "rec-r3-session",
        runtime_id,
        track_id="AT-001",
        clip_id="REC-R3-REOPEN",
        timeline_start_seconds=0.6,
    )
    assert preview["preview_installed"] is True
    accepted_result = surface.accept_finalize("rec-r3-session", runtime_id)
    accepted_head = str(accepted_result["accepted_head_revision_id"])
    before_render = render_routed_mix(project, accepted_head, mix_sample_rate_hz=8000)
    before_assets = list_audio_assets(project)

    service.close_session("rec-r3-session")
    fresh_service = StudioService(project.root.parent)
    reopened = fresh_service.open_project_session(
        project_slug=slug,
        session_id="rec-r3-reopened",
    )
    assert reopened["session"]["head_revision_id"] == accepted_head
    fresh_surface = StudioRecordingSurface(fresh_service)
    reopened_view = fresh_surface.recording_view("rec-r3-reopened")
    assert reopened_view["runtime"] is None

    reopened_project = fresh_service._get_session("rec-r3-reopened").project
    assert "REC-R3-REOPEN" in _track_clip_ids(reopened_project, accepted_head)
    assert list_audio_assets(reopened_project) == before_assets
    after_render = render_routed_mix(
        reopened_project, accepted_head, mix_sample_rate_hz=8000
    )
    assert after_render.plan == before_render.plan
    assert after_render.wav_bytes == before_render.wav_bytes
    assert reopened_project.verify_integrity()["status"] == "PASS"
