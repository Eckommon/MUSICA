from __future__ import annotations

import copy
from pathlib import Path

import pytest

from musica.atcm_r3_e2e import _prepare_project, _source
from musica.audio_edit import accept_audio_edit_preview
from musica.audio_mixer_edit import build_audio_mixer_edit_preview
from musica.contracts import ContractError
from musica.native_mixer import render_native_mix
from musica.project import MusicaProject, ProjectIntegrityError


def _mixer_candidate(parent: dict, candidate_id: str, gain_db: float = -6.0, pan: float = 0.5) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_audio_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "atcm-r4-test"},
        "reason": f"ATCM-R4 {candidate_id}",
        "operations": [
            {
                "operation_id": f"{candidate_id}-MIX",
                "op": "SET_TRACK_MIXER",
                "target": {"track_id": "AT-R3-E2E"},
                "mixer": {"gain_db": gain_db, "pan": pan, "mute": False, "solo": False},
            }
        ],
        "preview_only": True,
    }


def _accepted_project(tmp_path: Path):
    workspace = tmp_path / "source"
    workspace.mkdir()
    project, accepted, asset = _prepare_project(workspace)
    preview = build_audio_mixer_edit_preview(project, accepted, _mixer_candidate(accepted, "R4-ACCEPT"))
    assert preview.ready
    record = accept_audio_edit_preview(project, preview)
    blueprint = project.read_revision(record["revision_id"])
    return project, blueprint, asset


def test_r4_export_import_preserves_exact_authority_and_mix(tmp_path: Path) -> None:
    project, accepted, _ = _accepted_project(tmp_path)
    head = accepted["project"]["revision_id"]
    before = render_native_mix(project, head, mix_sample_rate_hz=8000)
    archive = project.export_to(tmp_path / "native.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    after = render_native_mix(reopened, reopened.head_revision_id(), mix_sample_rate_hz=8000)

    assert reopened.verify_integrity()["status"] == "PASS"
    assert reopened.head_revision_id() == head
    assert reopened.read_revision(head) == accepted
    assert after.plan == before.plan
    assert after.wav_bytes == before.wav_bytes
    assert after.wav_sha256 == before.wav_sha256


def test_r4_unaccepted_preview_is_not_persisted_and_generic_bypass_stays_blocked(tmp_path: Path) -> None:
    project, accepted, _ = _accepted_project(tmp_path)
    head = accepted["project"]["revision_id"]
    preview = build_audio_mixer_edit_preview(project, accepted, _mixer_candidate(accepted, "R4-PENDING", -3.0, -0.25))
    assert preview.ready
    assert project.head_revision_id() == head

    archive = project.export_to(tmp_path / "pending.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "pending-reopened.musica")
    assert reopened.head_revision_id() == head
    assert reopened.read_revision(head) == accepted

    forged = copy.deepcopy(accepted)
    forged["project"]["parent_revision_id"] = head
    forged["project"]["revision_id"] = head + "-forged"
    forged["materials"]["audio"]["tracks"][0]["mixer"]["gain_db"] = -2.0
    with pytest.raises(ContractError, match="Preview/Accept authority"):
        reopened.commit_revision(forged)


def test_r4_corrupt_persisted_audio_fails_closed_after_import(tmp_path: Path) -> None:
    project, _, asset = _accepted_project(tmp_path)
    archive = project.export_to(tmp_path / "corrupt-source.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "corrupt-reopened.musica")
    object_path = reopened._object_path(asset["object_sha256"])
    object_path.write_bytes(object_path.read_bytes() + b"R4-CORRUPTION")

    with pytest.raises((ProjectIntegrityError, ContractError), match="hash mismatch|corrupt"):
        reopened.verify_integrity()
