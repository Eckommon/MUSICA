from __future__ import annotations

import copy
import io
import json
import wave
from pathlib import Path

import pytest

from musica.audio_assets import import_audio_asset
from musica.audio_contracts import (
    audio_material_from_blueprint,
    validate_project_blueprint_audio,
)
from musica.audio_edit import (
    accept_audio_edit_preview,
    audio_material_sha256,
    blueprint_sha256,
    build_audio_edit_preview,
)
from musica.contracts import ContractError, validate_contract
from musica.creative import compose_blueprint
from musica.project import MusicaProject, ProjectIntegrityError, create_project

ROOT = Path(__file__).resolve().parents[1]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def _blueprint() -> dict:
    return compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))


def _wav_bytes(*, frames: int = 800) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(8000)
        writer.writeframes(bytes([0, 0, 0, 0]) * frames)
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
        "actor": {"kind": "user", "actor_id": "test-user"},
        "reason": f"ATCM-R1 test candidate {candidate_id}",
        "operations": operations,
        "preview_only": True,
    }


def _add_track_clip_candidate(parent: dict, asset_id: str, *, source_out: float = 0.05) -> dict:
    return _candidate(
        parent,
        "C-AUDIO-001",
        [
            {
                "operation_id": "OP-TRACK-001",
                "op": "ADD_TRACK",
                "track_id": "AT-001",
                "order": 0,
                "name": "Imported audio",
            },
            {
                "operation_id": "OP-CLIP-001",
                "op": "ADD_CLIP",
                "target": {"track_id": "AT-001"},
                "clip": {
                    "clip_id": "AC-001",
                    "asset_id": asset_id,
                    "timeline_start_seconds": 1.0,
                    "source_in_seconds": 0.0,
                    "source_out_seconds": source_out,
                    "gain_db": -3.0,
                },
            },
        ],
    )


def _project_with_asset(tmp_path: Path) -> tuple[MusicaProject, dict, dict]:
    root = _blueprint()
    project = create_project(tmp_path / "song.musica", root)
    source = tmp_path / "source.wav"
    source.write_bytes(_wav_bytes())
    descriptor = import_audio_asset(project, source)
    return project, root, descriptor


def test_r1_preview_accepts_project_bound_asset_without_advancing_head(tmp_path: Path) -> None:
    project, root, descriptor = _project_with_asset(tmp_path)
    root_id = root["project"]["revision_id"]
    candidate = _add_track_clip_candidate(root, descriptor["asset_id"])

    preview = build_audio_edit_preview(project, root, candidate)

    assert preview.ready
    assert preview.authority_result["status"] == "READY_FOR_PREVIEW"
    assert project.head_revision_id("main") == root_id
    assert preview.blueprint is not None
    validate_project_blueprint_audio(project, preview.blueprint)
    material = audio_material_from_blueprint(preview.blueprint)
    assert material is not None
    assert material["tracks"][0]["track_id"] == "AT-001"
    assert material["tracks"][0]["mixer"] == {
        "gain_db": 0.0,
        "pan": 0.0,
        "mute": False,
        "solo": False,
    }
    assert material["tracks"][0]["clips"][0]["asset_id"] == descriptor["asset_id"]


def test_r1_explicit_accept_advances_exactly_once_and_reopens(tmp_path: Path) -> None:
    project, root, descriptor = _project_with_asset(tmp_path)
    root_id = root["project"]["revision_id"]
    preview = build_audio_edit_preview(
        project,
        root,
        _add_track_clip_candidate(root, descriptor["asset_id"]),
    )
    assert preview.ready and preview.blueprint is not None

    record = accept_audio_edit_preview(project, preview)
    accepted_id = str(record["revision_id"])

    assert accepted_id != root_id
    assert project.head_revision_id("main") == accepted_id
    accepted = project.read_revision(accepted_id)
    material = audio_material_from_blueprint(accepted)
    assert material is not None
    assert material["tracks"][0]["track_id"] == "AT-001"
    assert material["tracks"][0]["clips"][0]["clip_id"] == "AC-001"
    assert material["tracks"][0]["clips"][0]["asset_id"] == descriptor["asset_id"]

    with pytest.raises(ContractError, match="stale|HEAD changed"):
        accept_audio_edit_preview(project, preview)
    assert project.head_revision_id("main") == accepted_id

    archive = project.export_to(tmp_path / "accepted.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    assert reopened.head_revision_id("main") == accepted_id
    reopened_blueprint = reopened.read_revision(accepted_id)
    assert audio_material_from_blueprint(reopened_blueprint) == material
    assert reopened.verify_integrity()["status"] == "PASS"


def test_marker_alone_cannot_bypass_public_audio_commit_gate(tmp_path: Path) -> None:
    project, root, descriptor = _project_with_asset(tmp_path)
    preview = build_audio_edit_preview(
        project,
        root,
        _add_track_clip_candidate(root, descriptor["asset_id"]),
    )
    assert preview.ready and preview.blueprint is not None

    # R1 provenance makes an authorized accepted shape structurally readable, but the
    # public Project Engine commit boundary must still reject an audio material change.
    validate_contract(preview.blueprint, "music-blueprint-v0.schema.json")
    with pytest.raises(ContractError, match="trusted audio Preview/Accept authority"):
        project.commit_revision(preview.blueprint, branch="main")
    assert project.head_revision_id("main") == root["project"]["revision_id"]


def test_unknown_cross_project_and_out_of_range_assets_fail_closed(tmp_path: Path) -> None:
    project_a, root_a, descriptor = _project_with_asset(tmp_path / "a")

    root_b = _blueprint()
    project_b = create_project(tmp_path / "b" / "song.musica", root_b)
    cross = build_audio_edit_preview(
        project_b,
        root_b,
        _add_track_clip_candidate(root_b, descriptor["asset_id"]),
    )
    assert not cross.ready
    assert cross.authority_result["status"] == "BLOCKED"
    assert any(item["code"] == "UNKNOWN_ASSET" for item in cross.authority_result["conflicts"])

    out_of_range = build_audio_edit_preview(
        project_a,
        root_a,
        _add_track_clip_candidate(root_a, descriptor["asset_id"], source_out=0.2),
    )
    assert not out_of_range.ready
    assert any(item["code"] == "INVALID_RANGE" for item in out_of_range.authority_result["conflicts"])


def test_move_trim_gain_preview_is_noncanonical_and_discardable(tmp_path: Path) -> None:
    project, root, descriptor = _project_with_asset(tmp_path)
    initial = build_audio_edit_preview(
        project,
        root,
        _add_track_clip_candidate(root, descriptor["asset_id"]),
    )
    accept_audio_edit_preview(project, initial)
    accepted_id = project.head_revision_id("main")
    accepted = project.read_revision(accepted_id)

    candidate = _candidate(
        accepted,
        "C-AUDIO-002",
        [
            {
                "operation_id": "OP-MOVE-001",
                "op": "MOVE_CLIP",
                "target": {"track_id": "AT-001", "clip_id": "AC-001"},
                "timeline_start_seconds": 2.0,
            },
            {
                "operation_id": "OP-TRIM-001",
                "op": "TRIM_CLIP",
                "target": {"track_id": "AT-001", "clip_id": "AC-001"},
                "source_in_seconds": 0.01,
                "source_out_seconds": 0.08,
            },
            {
                "operation_id": "OP-GAIN-001",
                "op": "SET_CLIP_GAIN",
                "target": {"track_id": "AT-001", "clip_id": "AC-001"},
                "gain_db": -6.0,
            },
        ],
    )
    preview = build_audio_edit_preview(project, accepted, candidate)
    assert preview.ready and preview.blueprint is not None
    assert project.head_revision_id("main") == accepted_id

    material = audio_material_from_blueprint(preview.blueprint)
    assert material is not None
    clip = material["tracks"][0]["clips"][0]
    assert clip["timeline_start_seconds"] == 2.0
    assert clip["source_in_seconds"] == 0.01
    assert clip["source_out_seconds"] == 0.08
    assert clip["gain_db"] == -6.0

    # Discard is intentionally a no-op: dropping Preview cannot change authority.
    del preview
    assert project.head_revision_id("main") == accepted_id


def test_stale_source_and_asset_corruption_between_preview_and_accept_block(tmp_path: Path) -> None:
    project, root, descriptor = _project_with_asset(tmp_path)
    preview = build_audio_edit_preview(
        project,
        root,
        _add_track_clip_candidate(root, descriptor["asset_id"]),
    )
    assert preview.ready

    # Advance HEAD through an unrelated accepted revision; original audio Preview is stale.
    unrelated = copy.deepcopy(root)
    unrelated["project"]["parent_revision_id"] = root["project"]["revision_id"]
    unrelated["project"]["revision_id"] = "rev-unrelated-before-audio-accept"
    unrelated["provenance"]["change_reason"] = "Unrelated accepted revision."
    project.commit_revision(unrelated, branch="main")
    with pytest.raises(ContractError, match="stale|HEAD changed"):
        accept_audio_edit_preview(project, preview)

    project2, root2, descriptor2 = _project_with_asset(tmp_path / "corrupt")
    preview2 = build_audio_edit_preview(
        project2,
        root2,
        _add_track_clip_candidate(root2, descriptor2["asset_id"]),
    )
    assert preview2.ready
    object_path = project2._object_path(descriptor2["object_sha256"])
    object_path.write_bytes(object_path.read_bytes() + b"x")
    with pytest.raises(ProjectIntegrityError, match="hash mismatch"):
        accept_audio_edit_preview(project2, preview2)
    assert project2.head_revision_id("main") == root2["project"]["revision_id"]


def test_unrelated_revision_after_audio_accept_preserves_audio_and_is_allowed(tmp_path: Path) -> None:
    project, root, descriptor = _project_with_asset(tmp_path)
    preview = build_audio_edit_preview(
        project,
        root,
        _add_track_clip_candidate(root, descriptor["asset_id"]),
    )
    accept_audio_edit_preview(project, preview)
    accepted_id = project.head_revision_id("main")
    accepted = project.read_revision(accepted_id)
    accepted_audio = copy.deepcopy(audio_material_from_blueprint(accepted))

    unrelated = copy.deepcopy(accepted)
    unrelated["project"]["parent_revision_id"] = accepted_id
    unrelated["project"]["revision_id"] = "rev-after-audio-unrelated"
    unrelated["provenance"]["change_reason"] = "Non-audio revision preserving native audio."
    record = project.commit_revision(unrelated, branch="main")

    assert record["revision_id"] == "rev-after-audio-unrelated"
    assert project.head_revision_id("main") == "rev-after-audio-unrelated"
    assert audio_material_from_blueprint(project.read_revision("rev-after-audio-unrelated")) == accepted_audio


def test_public_commit_cannot_change_already_accepted_audio_material(tmp_path: Path) -> None:
    project, root, descriptor = _project_with_asset(tmp_path)
    preview = build_audio_edit_preview(
        project,
        root,
        _add_track_clip_candidate(root, descriptor["asset_id"]),
    )
    accept_audio_edit_preview(project, preview)
    accepted_id = project.head_revision_id("main")
    accepted = project.read_revision(accepted_id)

    forged = copy.deepcopy(accepted)
    forged["project"]["parent_revision_id"] = accepted_id
    forged["project"]["revision_id"] = "rev-forged-direct-audio-change"
    forged["materials"]["audio"]["tracks"][0]["clips"][0]["gain_db"] = -12.0
    forged["provenance"]["change_reason"] = "Attempt direct audio mutation."

    with pytest.raises(ContractError, match="trusted audio Preview/Accept authority"):
        project.commit_revision(forged, branch="main")
    assert project.head_revision_id("main") == accepted_id
