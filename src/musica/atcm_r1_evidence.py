"""Generate deterministic evidence for ATCM-R1 accepted audio track/clip authority."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import shutil
import tempfile
import wave
from pathlib import Path
from typing import Any, Callable

from .audio_assets import import_audio_asset
from .audio_contracts import audio_material_from_blueprint, validate_project_blueprint_audio
from .audio_edit import (
    accept_audio_edit_preview,
    audio_material_sha256,
    blueprint_sha256,
    build_audio_edit_preview,
)
from .contracts import ContractError
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .project import MusicaProject, ProjectIntegrityError, create_project

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "audio-asset-v0.schema.json",
    ROOT / "schemas" / "audio-material-v0.schema.json",
    ROOT / "schemas" / "audio-edit-candidate-v0.schema.json",
    ROOT / "schemas" / "audio-authority-result-v0.schema.json",
    ROOT / "schemas" / "music-blueprint-v0.schema.json",
    ROOT / "src" / "musica" / "audio_assets.py",
    ROOT / "src" / "musica" / "audio_contracts.py",
    ROOT / "src" / "musica" / "audio_edit.py",
    ROOT / "src" / "musica" / "project.py",
    ROOT / "src" / "musica" / "atcm_r1_evidence.py",
    ROOT / "tests" / "test_atcm_r1_audio_authority.py",
    ROOT / ".github" / "workflows" / "atcm-r1-audio-authority-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _wav_bytes(*, frames: int = 800) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(8000)
        writer.writeframes(bytes([0, 0, 0, 0]) * frames)
    return stream.getvalue()


def _source(parent: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
    }


def _candidate(
    parent: dict[str, Any], candidate_id: str, operations: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_audio_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "atcm-r1-evidence"},
        "reason": f"ATCM-R1 evidence candidate {candidate_id}",
        "operations": operations,
        "preview_only": True,
    }


def _add_candidate(parent: dict[str, Any], asset_id: str, *, source_out: float = 0.05) -> dict[str, Any]:
    return _candidate(
        parent,
        "C-R1-ADD-001",
        [
            {
                "operation_id": "OP-R1-TRACK-001",
                "op": "ADD_TRACK",
                "track_id": "AT-001",
                "order": 0,
                "name": "Evidence audio",
            },
            {
                "operation_id": "OP-R1-CLIP-001",
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


def _edit_candidate(parent: dict[str, Any]) -> dict[str, Any]:
    return _candidate(
        parent,
        "C-R1-EDIT-002",
        [
            {
                "operation_id": "OP-R1-MOVE-001",
                "op": "MOVE_CLIP",
                "target": {"track_id": "AT-001", "clip_id": "AC-001"},
                "timeline_start_seconds": 2.0,
            },
            {
                "operation_id": "OP-R1-TRIM-001",
                "op": "TRIM_CLIP",
                "target": {"track_id": "AT-001", "clip_id": "AC-001"},
                "source_in_seconds": 0.01,
                "source_out_seconds": 0.08,
            },
            {
                "operation_id": "OP-R1-GAIN-001",
                "op": "SET_CLIP_GAIN",
                "target": {"track_id": "AT-001", "clip_id": "AC-001"},
                "gain_db": -6.0,
            },
        ],
    )


def _blocked_call(fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except (ContractError, ProjectIntegrityError):
        return True
    return False


def _new_project(root: Path, blueprint: dict[str, Any], wav_bytes: bytes) -> tuple[MusicaProject, dict[str, Any]]:
    project = create_project(root, copy.deepcopy(blueprint))
    source = root.parent / f"{root.name}-source.wav"
    source.write_bytes(wav_bytes)
    descriptor = import_audio_asset(project, source)
    return project, descriptor


def generate_atcm_r1_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    intent = json.loads(INTENT_PATH.read_text(encoding="utf-8"))
    root_blueprint = compose_blueprint(intent)
    wav_bytes = _wav_bytes()
    (out / "source.wav").write_bytes(wav_bytes)

    with tempfile.TemporaryDirectory(prefix="musica-atcm-r1-") as temp_value:
        temp = Path(temp_value)
        project, descriptor = _new_project(temp / "main.musica", root_blueprint, wav_bytes)
        root_revision_id = project.head_revision_id("main")
        head_after_import = project.head_revision_id("main")

        add_candidate = _add_candidate(root_blueprint, str(descriptor["asset_id"]))
        add_preview = build_audio_edit_preview(project, root_blueprint, add_candidate)
        head_after_add_preview = project.head_revision_id("main")
        if not add_preview.ready or add_preview.blueprint is None:
            raise RuntimeError("ATCM-R1 add Preview unexpectedly blocked")
        add_record = accept_audio_edit_preview(project, add_preview)
        first_revision_id = str(add_record["revision_id"])
        first_accepted = project.read_revision(first_revision_id)

        edit_candidate = _edit_candidate(first_accepted)
        edit_preview = build_audio_edit_preview(project, first_accepted, edit_candidate)
        head_after_edit_preview = project.head_revision_id("main")
        if not edit_preview.ready or edit_preview.blueprint is None:
            raise RuntimeError("ATCM-R1 edit Preview unexpectedly blocked")
        edit_record = accept_audio_edit_preview(project, edit_preview)
        second_revision_id = str(edit_record["revision_id"])
        second_accepted = project.read_revision(second_revision_id)
        validate_project_blueprint_audio(project, second_accepted)

        material = audio_material_from_blueprint(second_accepted)
        assert material is not None
        clip = material["tracks"][0]["clips"][0]

        # Preview-only discard proof: build a valid later candidate and simply do not accept it.
        discard_candidate = _candidate(
            second_accepted,
            "C-R1-DISCARD-003",
            [
                {
                    "operation_id": "OP-R1-DISCARD-GAIN-001",
                    "op": "SET_CLIP_GAIN",
                    "target": {"track_id": "AT-001", "clip_id": "AC-001"},
                    "gain_db": -9.0,
                }
            ],
        )
        discard_preview = build_audio_edit_preview(project, second_accepted, discard_candidate)
        head_before_discard = project.head_revision_id("main")
        if not discard_preview.ready:
            raise RuntimeError("ATCM-R1 discard Preview unexpectedly blocked")
        del discard_preview
        head_after_discard = project.head_revision_id("main")

        # Public direct mutation remains blocked even though accepted provenance is readable.
        forged = copy.deepcopy(second_accepted)
        forged["project"]["parent_revision_id"] = second_revision_id
        forged["project"]["revision_id"] = "rev-r1-forged-direct-audio"
        forged["materials"]["audio"]["tracks"][0]["clips"][0]["gain_db"] = -12.0
        forged["provenance"]["change_reason"] = "Attempt direct audio bypass."
        direct_audio_bypass_blocked = _blocked_call(
            lambda: project.commit_revision(forged, branch="main")
        )

        # Out-of-range source reference is blocked at Preview.
        bad_range = build_audio_edit_preview(
            project,
            second_accepted,
            _candidate(
                second_accepted,
                "C-R1-BAD-RANGE",
                [
                    {
                        "operation_id": "OP-R1-BAD-RANGE",
                        "op": "TRIM_CLIP",
                        "target": {"track_id": "AT-001", "clip_id": "AC-001"},
                        "source_in_seconds": 0.0,
                        "source_out_seconds": 0.2,
                    }
                ],
            ),
        )

        # Same asset id without an import binding in another bundle is not a valid reference.
        cross_project = create_project(temp / "cross.musica", copy.deepcopy(root_blueprint))
        cross_preview = build_audio_edit_preview(
            cross_project,
            root_blueprint,
            _add_candidate(root_blueprint, str(descriptor["asset_id"])),
        )

        # A source-bound Preview becomes stale after an unrelated accepted revision advances HEAD.
        stale_project, stale_descriptor = _new_project(
            temp / "stale.musica", root_blueprint, wav_bytes
        )
        stale_preview = build_audio_edit_preview(
            stale_project,
            root_blueprint,
            _add_candidate(root_blueprint, str(stale_descriptor["asset_id"])),
        )
        unrelated = copy.deepcopy(root_blueprint)
        unrelated["project"]["parent_revision_id"] = root_revision_id
        unrelated["project"]["revision_id"] = "rev-r1-unrelated-stale"
        unrelated["provenance"]["change_reason"] = "Advance HEAD outside audio Preview."
        stale_project.commit_revision(unrelated, branch="main")
        stale_accept_blocked = _blocked_call(
            lambda: accept_audio_edit_preview(stale_project, stale_preview)
        )

        # Asset corruption after Preview must block Accept.
        corrupt_project, corrupt_descriptor = _new_project(
            temp / "corrupt.musica", root_blueprint, wav_bytes
        )
        corrupt_preview = build_audio_edit_preview(
            corrupt_project,
            root_blueprint,
            _add_candidate(root_blueprint, str(corrupt_descriptor["asset_id"])),
        )
        corrupt_object = corrupt_project._object_path(str(corrupt_descriptor["object_sha256"]))
        corrupt_object.write_bytes(corrupt_object.read_bytes() + b"x")
        corrupt_after_preview_blocked = _blocked_call(
            lambda: accept_audio_edit_preview(corrupt_project, corrupt_preview)
        )

        archive = project.export_to(out / "accepted-project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_blueprint = reopened.read_revision(second_revision_id)
        reopened_material = audio_material_from_blueprint(reopened_blueprint)
        reopened_integrity = reopened.verify_integrity()
        reexport_byte_identical = reopened.export_bytes() == archive.read_bytes()

        _write_json(out / "add-candidate.json", add_candidate)
        _write_json(out / "add-preview.json", add_preview.as_dict())
        _write_json(out / "edit-candidate.json", edit_candidate)
        _write_json(out / "edit-preview.json", edit_preview.as_dict())
        _write_json(out / "accepted-blueprint.json", second_accepted)

        proof = {
            "milestone": "ATCM-R1",
            "validation_class": "BOUNDED_ACCEPTED_AUDIO_TRACK_CLIP_AUTHORITY_AND_ASSET_BINDING",
            "source_sha256": _sha(wav_bytes),
            "source_size_bytes": len(wav_bytes),
            "asset_id": descriptor["asset_id"],
            "root_revision_id": root_revision_id,
            "first_accepted_revision_id": first_revision_id,
            "second_accepted_revision_id": second_revision_id,
            "import_did_not_advance_head": head_after_import == root_revision_id,
            "add_preview_ready": add_preview.ready,
            "add_preview_did_not_advance_head": head_after_add_preview == root_revision_id,
            "first_accept_advanced_exactly_from_root": first_accepted["project"]["parent_revision_id"] == root_revision_id,
            "edit_preview_ready": edit_preview.ready,
            "edit_preview_did_not_advance_head": head_after_edit_preview == first_revision_id,
            "second_accept_advanced_exactly_from_first": second_accepted["project"]["parent_revision_id"] == first_revision_id,
            "accepted_asset_id_exact": clip["asset_id"] == descriptor["asset_id"],
            "accepted_track_id": material["tracks"][0]["track_id"],
            "accepted_clip_id": clip["clip_id"],
            "accepted_timeline_start_seconds": clip["timeline_start_seconds"],
            "accepted_source_in_seconds": clip["source_in_seconds"],
            "accepted_source_out_seconds": clip["source_out_seconds"],
            "accepted_clip_gain_db": clip["gain_db"],
            "accepted_track_mixer_defaults_preserved": material["tracks"][0]["mixer"] == {"gain_db": 0.0, "pan": 0.0, "mute": False, "solo": False},
            "discard_preview_did_not_advance_head": head_before_discard == head_after_discard == second_revision_id,
            "direct_audio_commit_bypass_fails_closed": direct_audio_bypass_blocked,
            "out_of_asset_range_preview_fails_closed": not bad_range.ready,
            "cross_project_unimported_asset_fails_closed": not cross_preview.ready,
            "stale_source_accept_fails_closed": stale_accept_blocked,
            "corrupt_asset_after_preview_accept_fails_closed": corrupt_after_preview_blocked,
            "reopen_head_exact": reopened.head_revision_id("main") == second_revision_id,
            "reopen_material_exact": reopened_material == material,
            "reopen_project_integrity_status": reopened_integrity["status"],
            "reexport_byte_identical": reexport_byte_identical,
            "candidate_blueprint_sha256": blueprint_sha256(second_accepted),
            "candidate_audio_material_sha256": audio_material_sha256(second_accepted),
            "multitrack_mixer_execution_claimed": False,
            "track_mixer_edit_semantics_claimed": False,
            "browser_arrangement_claimed": False,
            "recording_claimed": False,
            "plugin_hosting_claimed": False,
        }
        _write_json(out / "proof.json", proof)

    contract_hashes = []
    for path in CONTRACT_PATHS:
        data = path.read_bytes()
        contract_hashes.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": _sha(data),
                "size_bytes": len(data),
            }
        )
    _write_json(out / "contract-hashes.json", contract_hashes)

    records = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json"):
        data = path.read_bytes()
        records.append(
            {
                "path": path.relative_to(out).as_posix(),
                "sha256": _sha(data),
                "size_bytes": len(data),
            }
        )
    manifest = {
        "manifest_version": "0",
        "milestone": "ATCM-R1",
        "artifact_name": "musica-atcm-r1-audio-authority-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    import os

    destination = os.environ.get(
        "MUSICA_ATCM_R1_EVIDENCE_OUT", "artifacts/atcm-r1-audio-authority-evidence"
    )
    generate_atcm_r1_evidence(destination)
