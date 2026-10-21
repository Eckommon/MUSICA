"""G3B2A — exact native short parity and two independently accepted 180s 48k WAVs."""
from __future__ import annotations

import hashlib
import io
import resource
import wave
from pathlib import Path

import pytest

from musica.audio_assets import import_audio_asset_verified_path, read_audio_asset
from musica.audio_edit import (
    accept_audio_edit_preview, audio_material_sha256,
    blueprint_sha256, build_audio_edit_preview,
)
from musica.contracts import ContractError
from musica.native_mixer import render_native_mix
from musica.project import MusicaProject
from musica.studio import StudioService
from musica.streamed_native_mixer import render_native_mix_streamed
from test_atcm_r2_native_mixer import _accept_arrangement


def _sha(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def test_streamed_short_wav_matches_legacy_atcm_byte_exact(tmp_path: Path):
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    reference = render_native_mix(project, revision_id, mix_sample_rate_hz=8000)
    for block in (1, 317, 4096):
        actual = render_native_mix_streamed(
            project, revision_id, mix_sample_rate_hz=8000, block_frames=block
        )
        assert actual.plan == reference.plan
        assert actual.wav_path.read_bytes() == reference.wav_bytes
        assert actual.wav_sha256 == reference.wav_sha256
        assert actual.clipped_sample_count == reference.clipped_sample_count
        assert actual.peak_pre_clip == reference.peak_pre_clip
        assert actual.report()["rendered_audio_is_canonical"] is False
        actual.wav_path.unlink()


def test_cancel_refuses_output_and_preserves_creative_head(tmp_path: Path):
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    before = project.head_revision_id()
    with pytest.raises(ContractError, match="cancelled"):
        render_native_mix_streamed(
            project, before, mix_sample_rate_hz=8000,
            cancelled=lambda: True, block_frames=256,
        )
    assert project.head_revision_id() == before
    assert not list((project.root / ".derived-streamed-native-g3b2").glob("*.wav"))
    with pytest.raises(ContractError, match="block_frames"):
        render_native_mix_streamed(project, before, mix_sample_rate_hz=8000,
                                   block_frames=16385)
    with pytest.raises(ContractError, match="sample-rate match"):
        render_native_mix_streamed(project, before, mix_sample_rate_hz=48000)


def _long_wav(path: Path, *, left: int, right: int):
    sample = (left.to_bytes(2, "little", signed=True) +
              right.to_bytes(2, "little", signed=True))
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(48000)
        for _ in range(1054):
            writer.writeframesraw(sample * 8192)
        writer.writeframesraw(sample * 5632)
        writer.writeframes(b"")
    assert path.stat().st_size == 34_560_044


def _two_accepted_long_sources(tmp_path: Path):
    service = StudioService(tmp_path / "studio")
    service.create_project_session(
        project_slug="g3b2-long-two-track", session_id="g3b2",
        user_text="Create two long independent audio tracks",
        provider_mode="fixture", duration_seconds=180,
        use_case="song", style_profile="dark_electronic", seed=201,
    )
    project = service._get_session("g3b2").project
    first = tmp_path / "a.wav"
    second = tmp_path / "b.wav"
    _long_wav(first, left=4000, right=0)
    _long_wav(second, left=0, right=-2500)
    a = import_audio_asset_verified_path(project, first, expected_sha256=_sha(first))
    b = import_audio_asset_verified_path(project, second, expected_sha256=_sha(second))
    assert a["asset_id"] != b["asset_id"]
    before = project.head_revision_id()
    blueprint = project.read_revision(before)
    candidate = {
        "candidate_version": "0",
        "candidate_id": "G3B2-ACCEPTED-TWO-TRACKS",
        "authority_target": "blueprint_audio_material",
        "source": {
            "project_id": blueprint["project"]["project_id"],
            "revision_id": before,
            "blueprint_sha256": blueprint_sha256(blueprint),
            "audio_material_sha256": audio_material_sha256(blueprint),
        },
        "actor": {"kind": "user", "actor_id": "g3b2-test"},
        "reason": "Two independent accepted three-minute WAVs",
        "operations": [
            {"operation_id":"G3B2-TRACK-A","op":"ADD_TRACK",
             "track_id":"AT-G3B2-A","order":0,"name":"Left"},
            {"operation_id":"G3B2-TRACK-B","op":"ADD_TRACK",
             "track_id":"AT-G3B2-B","order":1,"name":"Right"},
            {"operation_id":"G3B2-CLIP-A","op":"ADD_CLIP",
             "target":{"track_id":"AT-G3B2-A"},
             "clip":{"clip_id":"AC-G3B2-A","asset_id":a["asset_id"],
                     "timeline_start_seconds":0.0,"source_in_seconds":0.0,
                     "source_out_seconds":180.0,"gain_db":0.0}},
            {"operation_id":"G3B2-CLIP-B","op":"ADD_CLIP",
             "target":{"track_id":"AT-G3B2-B"},
             "clip":{"clip_id":"AC-G3B2-B","asset_id":b["asset_id"],
                     "timeline_start_seconds":0.0,"source_in_seconds":0.0,
                     "source_out_seconds":180.0,"gain_db":0.0}},
        ],
        "preview_only": True,
    }
    preview = build_audio_edit_preview(project, blueprint, candidate)
    assert preview.ready, preview.authority_result
    assert project.head_revision_id() == before
    accepted = accept_audio_edit_preview(project, preview)
    return project, accepted["revision_id"], a, b


def test_two_distinct_180s_tracks_exact_pcm_reopen_and_bounded_python_heap(tmp_path):
    project, revision_id, a, b = _two_accepted_long_sources(tmp_path)
    mixed = render_native_mix_streamed(
        project, revision_id, mix_sample_rate_hz=48000,
        block_frames=4096,
    )
    # Linux CI ru_maxrss is KiB. Includes actual Studio project setup and CAS
    # validation, so this generous ceiling tests whole-process, not just lists.
    peak_rss_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    assert mixed.wav_size_bytes == 34_560_044
    assert mixed.wav_path.stat().st_size == 34_560_044
    assert mixed.clipped_sample_count == 0
    assert mixed.peak_pre_clip < 1.0
    assert mixed.blocks_written > 2000
    assert peak_rss_kib < 512 * 1024
    with wave.open(str(mixed.wav_path), "rb") as reader:
        assert (reader.getframerate(), reader.getnchannels(),
                reader.getsampwidth(), reader.getnframes()) == (48000, 2, 2, 8_640_000)
        for frame_index in (0, 1, 96000, 4_320_000, 8_639_999):
            reader.setpos(frame_index)
            frame = reader.readframes(1)
            assert (int.from_bytes(frame[:2], "little", signed=True),
                    int.from_bytes(frame[2:], "little", signed=True)) == (4000, -2500)
    assert mixed.wav_sha256 == _sha(mixed.wav_path)
    assert project.head_revision_id() == revision_id
    reloaded = MusicaProject(project.root)
    assert read_audio_asset(reloaded, a["asset_id"]) == a
    assert read_audio_asset(reloaded, b["asset_id"]) == b
    replay = render_native_mix_streamed(
        reloaded, revision_id, mix_sample_rate_hz=48000,
        block_frames=8191,
    )
    assert replay.wav_sha256 == mixed.wav_sha256
    assert replay.plan == mixed.plan
    assert reloaded.head_revision_id() == revision_id
    mixed.wav_path.unlink()
    replay.wav_path.unlink()
