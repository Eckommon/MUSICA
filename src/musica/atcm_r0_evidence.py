"""Generate deterministic evidence for ATCM-R0 native audio authority and assets."""

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

from .audio_assets import (
    audio_asset_bytes,
    import_audio_asset,
    read_audio_asset,
    verify_audio_assets,
)
from .audio_contracts import validate_audio_material, validate_blueprint_audio
from .contracts import ContractError, validate_contract
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .project import MusicaProject, ProjectIntegrityError, create_project

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "audio-asset-v0.schema.json",
    ROOT / "schemas" / "audio-material-v0.schema.json",
    ROOT / "schemas" / "music-blueprint-v0.schema.json",
    ROOT / "src" / "musica" / "contracts.py",
    ROOT / "src" / "musica" / "project.py",
    ROOT / "src" / "musica" / "audio_assets.py",
    ROOT / "src" / "musica" / "audio_contracts.py",
    ROOT / "src" / "musica" / "atcm_r0_evidence.py",
    ROOT / "tests" / "test_atcm_r0_audio_assets.py",
    ROOT / "tests" / "test_atcm_r0_project_integrity.py",
    ROOT / "tests" / "test_atcm_r0_authority_boundary.py",
    ROOT / ".github" / "workflows" / "atcm-r0-native-audio-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _wav_bytes(*, channels: int = 2, sample_rate: int = 8000, frames: int = 64) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        frame = bytes([0, 0]) * channels
        writer.writeframes(frame * frames)
    return stream.getvalue()


def _blocked(fn: Callable[[], None]) -> bool:
    try:
        fn()
    except (ContractError, ProjectIntegrityError):
        return True
    return False


def _material(asset_id: str) -> dict[str, Any]:
    return {
        "material_version": "0",
        "mode": "audio_tracks",
        "tracks": [
            {
                "track_id": "AT-001",
                "order": 0,
                "name": "Imported audio",
                "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False, "solo": False},
                "clips": [
                    {
                        "clip_id": "AC-001",
                        "asset_id": asset_id,
                        "timeline_start_seconds": 1.0,
                        "source_in_seconds": 0.0,
                        "source_out_seconds": 0.008,
                        "gain_db": -3.0,
                    }
                ],
            }
        ],
    }


def generate_atcm_r0_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    intent = json.loads(INTENT_PATH.read_text(encoding="utf-8"))
    blueprint = compose_blueprint(intent)
    root_revision_id = str(blueprint["project"]["revision_id"])
    wav_bytes = _wav_bytes()
    (out / "source.wav").write_bytes(wav_bytes)

    with tempfile.TemporaryDirectory(prefix="musica-atcm-r0-") as temp_value:
        temp = Path(temp_value)
        source_a = temp / "source-a.wav"
        source_b = temp / "renamed-source.wav"
        source_a.write_bytes(wav_bytes)
        source_b.write_bytes(wav_bytes)

        project = create_project(temp / "song.musica", blueprint)
        head_before = project.head_revision_id()
        blueprint_before = copy.deepcopy(project.read_revision(head_before))
        audit_before = len(project._audit_events())

        descriptor = import_audio_asset(project, source_a)
        audit_after_first = len(project._audit_events())
        descriptor_second = import_audio_asset(project, source_b)
        audit_after_second = len(project._audit_events())
        head_after_import = project.head_revision_id()
        blueprint_after_import = project.read_revision(head_after_import)
        asset_bytes = audio_asset_bytes(project, descriptor["asset_id"])
        asset_integrity = verify_audio_assets(project)
        project_integrity = project.verify_integrity()

        material = _material(str(descriptor["asset_id"]))
        validate_audio_material(
            material,
            project_duration_seconds=float(blueprint["project"]["duration_seconds"]),
        )
        candidate = copy.deepcopy(blueprint)
        candidate["project"]["parent_revision_id"] = root_revision_id
        candidate["project"]["revision_id"] = "rev-atcm-r0-audio-authority-attempt"
        candidate["materials"]["audio"] = material
        validate_blueprint_audio(candidate, allow_nonempty=True)
        canonical_acceptance_blocked = _blocked(
            lambda: validate_contract(candidate, "music-blueprint-v0.schema.json")
        )
        commit_acceptance_blocked = _blocked(lambda: project.commit_revision(candidate, branch="main"))
        head_after_rejected_accept = project.head_revision_id()
        root_after_rejected_accept = project.read_revision(root_revision_id)

        duplicate_track = copy.deepcopy(material)
        duplicate_track["tracks"].append(copy.deepcopy(duplicate_track["tracks"][0]))
        duplicate_track["tracks"][1]["order"] = 1

        bad_range = copy.deepcopy(material)
        bad_range["tracks"][0]["clips"][0]["source_in_seconds"] = 0.009

        malformed = temp / "malformed.wav"
        malformed.write_bytes(b"not-a-wave")

        archive = project.export_to(out / "project.musica.zip")
        imported = MusicaProject.import_from(archive, temp / "imported.musica")
        imported_descriptor = read_audio_asset(imported, str(descriptor["asset_id"]))
        imported_bytes = audio_asset_bytes(imported, str(descriptor["asset_id"]))
        imported_integrity = imported.verify_integrity()
        reexport_identical = imported.export_bytes() == archive.read_bytes()

        tamper_object = imported._object_path(str(descriptor["object_sha256"]))
        pristine_object = tamper_object.read_bytes()
        tamper_object.write_bytes(pristine_object + b"x")
        tampered_object_blocked = _blocked(lambda: verify_audio_assets(imported))
        tampered_object_project_blocked = _blocked(lambda: imported.verify_integrity())
        tampered_object_export_blocked = _blocked(lambda: imported.export_bytes())
        tamper_object.write_bytes(pristine_object)

        digest = str(descriptor["object_sha256"])
        descriptor_path = imported.root / "assets" / "audio" / "sha256" / f"{digest}.json"
        pristine_descriptor = descriptor_path.read_bytes()
        tampered_descriptor = json.loads(pristine_descriptor.decode("utf-8"))
        tampered_descriptor["size_bytes"] += 1
        descriptor_path.write_bytes(canonical_json_bytes(tampered_descriptor))
        tampered_descriptor_project_blocked = _blocked(lambda: imported.verify_integrity())
        tampered_descriptor_export_blocked = _blocked(lambda: imported.export_bytes())
        descriptor_path.write_bytes(pristine_descriptor)

        proof = {
            "milestone": "ATCM-R0",
            "validation_class": "BOUNDED_NATIVE_AUDIO_AUTHORITY_AND_IMMUTABLE_ASSET_STORE",
            "root_revision_id": root_revision_id,
            "source_sha256": _sha(wav_bytes),
            "source_size_bytes": len(wav_bytes),
            "descriptor": descriptor,
            "asset_id_is_source_sha256": descriptor["asset_id"] == f"sha256:{_sha(wav_bytes)}",
            "source_bytes_roundtrip_exact": asset_bytes == wav_bytes,
            "identical_import_descriptor_equal": descriptor_second == descriptor,
            "identical_import_idempotent": audit_after_second == audit_after_first,
            "first_import_added_one_audit_event": audit_after_first == audit_before + 1,
            "import_did_not_advance_head": head_before == head_after_import,
            "import_did_not_mutate_accepted_blueprint": blueprint_before == blueprint_after_import,
            "audio_material_structure_valid": True,
            "nonempty_audio_canonical_acceptance_fails_closed": canonical_acceptance_blocked,
            "nonempty_audio_commit_fails_closed": commit_acceptance_blocked,
            "rejected_accept_did_not_advance_head": head_after_rejected_accept == root_revision_id,
            "rejected_accept_preserved_root_blueprint": root_after_rejected_accept == blueprint,
            "duplicate_track_id_fails_closed": _blocked(lambda: validate_audio_material(duplicate_track)),
            "invalid_source_range_fails_closed": _blocked(lambda: validate_audio_material(bad_range)),
            "malformed_wav_fails_closed": _blocked(lambda: import_audio_asset(project, malformed)),
            "audio_asset_integrity_status": asset_integrity["status"],
            "project_integrity_status": project_integrity["status"],
            "project_integrity_audio_asset_count": project_integrity["audio_asset_count"],
            "imported_project_integrity_status": imported_integrity["status"],
            "imported_project_audio_asset_count": imported_integrity["audio_asset_count"],
            "export_import_descriptor_exact": imported_descriptor == descriptor,
            "export_import_source_bytes_exact": imported_bytes == wav_bytes,
            "reexport_byte_identical": reexport_identical,
            "tampered_source_object_fails_closed": tampered_object_blocked,
            "tampered_source_object_project_integrity_fails_closed": tampered_object_project_blocked,
            "tampered_source_object_export_fails_closed": tampered_object_export_blocked,
            "tampered_descriptor_project_integrity_fails_closed": tampered_descriptor_project_blocked,
            "tampered_descriptor_export_fails_closed": tampered_descriptor_export_blocked,
            "accepted_native_audio_claimed": False,
            "audio_edit_authority_claimed": False,
            "multitrack_mix_execution_claimed": False,
            "browser_arrangement_claimed": False,
            "recording_claimed": False,
            "plugin_hosting_claimed": False,
        }
        _write_json(out / "descriptor.json", descriptor)
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
        "milestone": "ATCM-R0",
        "artifact_name": "musica-atcm-r0-native-audio-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    import os

    destination = os.environ.get(
        "MUSICA_ATCM_R0_EVIDENCE_OUT", "artifacts/atcm-r0-native-audio-evidence"
    )
    generate_atcm_r0_evidence(destination)
