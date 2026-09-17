from __future__ import annotations

import io
import json
import math
import wave
from pathlib import Path

import pytest

from musica.audio_assets import import_audio_asset
from musica.audio_edit import (
    accept_audio_edit_preview,
    audio_material_sha256,
    blueprint_sha256,
    build_audio_edit_preview,
)
from musica.audio_mixer_edit import build_audio_mixer_edit_preview
from musica.contracts import ContractError
from musica.creative import compose_blueprint
from musica.native_mixer import build_native_mix_plan, render_native_mix
from musica.project import ProjectIntegrityError, create_project

ROOT = Path(__file__).resolve().parents[1]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def _blueprint() -> dict:
    return compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))


def _wav_bytes(*, channels: int = 1, sample_rate: int = 8000, frames: int = 800, left: int = 8192, right: int = -8192) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        payload = bytearray()
        for _ in range(frames):
            payload.extend(int(left).to_bytes(2, "little", signed=True))
            if channels == 2:
                payload.extend(int(right).to_bytes(2, "little", signed=True))
        writer.writeframes(bytes(payload))
    return stream.getvalue()


def _source(parent: dict) -> dict:
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
    }


def _candidate(parent: dict, candidate_id: str, operations: list[dict]) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_audio_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "r2-test"},
        "reason": f"ATCM-R2 candidate {candidate_id}",
        "operations": operations,
        "preview_only": True,
    }


def _accept_arrangement(tmp_path: Path, *, rate_b: int = 8000):
    root = _blueprint()
    project = create_project(tmp_path / "song.musica", root)
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    a.write_bytes(_wav_bytes(channels=1, sample_rate=8000, left=24576))
    # Every fixture is exactly 0.1 s long regardless of sample rate. This lets R1
    # accept the arrangement before R2 independently tests source-rate policy.
    b.write_bytes(
        _wav_bytes(
            channels=2,
            sample_rate=rate_b,
            frames=rate_b // 10,
            left=24576,
            right=24576,
        )
    )
    asset_a = import_audio_asset(project, a)
    asset_b = import_audio_asset(project, b)
    candidate = _candidate(root, "C-R2-ARRANGE", [
        {"operation_id":"OP-T1","op":"ADD_TRACK","track_id":"AT-001","order":0,"name":"Mono"},
        {"operation_id":"OP-T2","op":"ADD_TRACK","track_id":"AT-002","order":1,"name":"Stereo"},
        {"operation_id":"OP-C1","op":"ADD_CLIP","target":{"track_id":"AT-001"},"clip":{"clip_id":"AC-001","asset_id":asset_a["asset_id"],"timeline_start_seconds":0.0,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
        {"operation_id":"OP-C2","op":"ADD_CLIP","target":{"track_id":"AT-002"},"clip":{"clip_id":"AC-002","asset_id":asset_b["asset_id"],"timeline_start_seconds":0.05,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
    ])
    preview = build_audio_edit_preview(project, root, candidate)
    assert preview.ready
    record = accept_audio_edit_preview(project, preview)
    return project, project.read_revision(record["revision_id"]), asset_a, asset_b


def test_r2_plan_and_wav_are_byte_reproducible(tmp_path: Path) -> None:
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    plan_a = build_native_mix_plan(project, revision_id, mix_sample_rate_hz=8000)
    plan_b = build_native_mix_plan(project, revision_id, mix_sample_rate_hz=8000)
    assert plan_a == plan_b
    assert plan_a["tracks"][0]["clips"][0]["timeline_start_frame"] == 0
    assert plan_a["tracks"][1]["clips"][0]["timeline_start_frame"] == 400
    assert plan_a["tracks"][0]["clips"][0]["source_end_frame"] == 800
    render_a = render_native_mix(project, revision_id, mix_sample_rate_hz=8000)
    render_b = render_native_mix(project, revision_id, mix_sample_rate_hz=8000)
    assert render_a.plan == render_b.plan
    assert render_a.wav_bytes == render_b.wav_bytes
    assert render_a.wav_sha256 == render_b.wav_sha256
    assert render_a.clipped_sample_count > 0
    with wave.open(io.BytesIO(render_a.wav_bytes), "rb") as reader:
        assert reader.getnchannels() == 2
        assert reader.getsampwidth() == 2
        assert reader.getframerate() == 8000


def test_r2_mixer_edit_reuses_r1_accept_and_changes_derived_output(tmp_path: Path) -> None:
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    before_id = accepted["project"]["revision_id"]
    before = render_native_mix(project, before_id, mix_sample_rate_hz=8000)
    candidate = _candidate(accepted, "C-R2-MIXER", [
        {"operation_id":"OP-MIX-1","op":"SET_TRACK_MIXER","target":{"track_id":"AT-001"},"mixer":{"gain_db":-6.0,"pan":-0.5,"mute":False,"solo":True}},
        {"operation_id":"OP-MIX-2","op":"SET_TRACK_MIXER","target":{"track_id":"AT-002"},"mixer":{"gain_db":0.0,"pan":1.0,"mute":True,"solo":True}},
    ])
    preview = build_audio_mixer_edit_preview(project, accepted, candidate)
    assert preview.ready and preview.blueprint is not None
    assert project.head_revision_id("main") == before_id
    record = accept_audio_edit_preview(project, preview)
    after_id = record["revision_id"]
    plan = build_native_mix_plan(project, after_id, mix_sample_rate_hz=8000)
    assert plan["tracks"][0]["mixer"]["audible"] is True
    assert plan["tracks"][1]["mixer"]["audible"] is False
    assert plan["tracks"][0]["mixer"]["left_coefficient"] == 1.0
    assert plan["tracks"][0]["mixer"]["right_coefficient"] == 0.5
    assert plan["tracks"][1]["mixer"]["left_coefficient"] == 0.0
    assert plan["tracks"][1]["mixer"]["right_coefficient"] == 1.0
    assert math.isclose(plan["tracks"][0]["mixer"]["gain_linear"], 10 ** (-6 / 20))
    after = render_native_mix(project, after_id, mix_sample_rate_hz=8000)
    assert after.wav_sha256 != before.wav_sha256
    assert after.plan["mix_plan_sha256"] != before.plan["mix_plan_sha256"]


def test_r2_preview_is_noncanonical_and_stale_mixer_preview_fails(tmp_path: Path) -> None:
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    source_id = accepted["project"]["revision_id"]
    candidate = _candidate(accepted, "C-R2-STALE", [{"operation_id":"OP-MIX-STALE","op":"SET_TRACK_MIXER","target":{"track_id":"AT-001"},"mixer":{"gain_db":-3.0,"pan":0.0,"mute":False,"solo":False}}])
    preview = build_audio_mixer_edit_preview(project, accepted, candidate)
    assert preview.ready
    assert project.head_revision_id("main") == source_id
    unrelated = _candidate(accepted, "C-R2-CLIP-GAIN", [{"operation_id":"OP-GAIN","op":"SET_CLIP_GAIN","target":{"track_id":"AT-001","clip_id":"AC-001"},"gain_db":-1.0}])
    unrelated_preview = build_audio_edit_preview(project, accepted, unrelated)
    accept_audio_edit_preview(project, unrelated_preview)
    with pytest.raises(ContractError, match="stale|HEAD changed"):
        accept_audio_edit_preview(project, preview)


def test_r2_rate_mismatch_fails_closed_after_valid_r1_accept(tmp_path: Path) -> None:
    project, accepted, _, _ = _accept_arrangement(tmp_path, rate_b=16000)
    revision_id = accepted["project"]["revision_id"]
    with pytest.raises(ContractError, match="sample-rate match"):
        build_native_mix_plan(project, revision_id, mix_sample_rate_hz=8000)


def test_r2_corrupt_asset_fails_closed_independently_of_rate_policy(tmp_path: Path) -> None:
    project, accepted, _, asset_b = _accept_arrangement(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    object_path = project._object_path(asset_b["object_sha256"])
    object_path.write_bytes(object_path.read_bytes() + b"x")
    with pytest.raises((ProjectIntegrityError, ContractError), match="hash mismatch|corrupt"):
        build_native_mix_plan(project, revision_id, mix_sample_rate_hz=8000)


def test_r2_reopen_preserves_plan_and_wav_identity(tmp_path: Path) -> None:
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    before = render_native_mix(project, revision_id, mix_sample_rate_hz=8000)
    archive = project.export_to(tmp_path / "r2.musica.zip")
    from musica.project import MusicaProject
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    after = render_native_mix(reopened, revision_id, mix_sample_rate_hz=8000)
    assert before.plan == after.plan
    assert before.wav_bytes == after.wav_bytes
    assert before.wav_sha256 == after.wav_sha256
