from __future__ import annotations

import copy
import io
import json
import wave
from pathlib import Path

import pytest

from musica.audio_assets import import_audio_asset
from musica.audio_contracts import validate_audio_material, validate_blueprint_audio
from musica.contracts import ContractError, validate_contract
from musica.creative import compose_blueprint
from musica.project import create_project

ROOT = Path(__file__).resolve().parents[1]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def _blueprint() -> dict:
    return compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))


def _wav_bytes() -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(8000)
        writer.writeframes(bytes([0, 0, 0, 0]) * 64)
    return stream.getvalue()


def _material(asset_id: str) -> dict:
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


def test_r0_can_validate_future_audio_structure_without_granting_acceptance(tmp_path: Path) -> None:
    root = _blueprint()
    project = create_project(tmp_path / "song.musica", root)
    root_id = root["project"]["revision_id"]

    source = tmp_path / "source.wav"
    source.write_bytes(_wav_bytes())
    descriptor = import_audio_asset(project, source)
    material = _material(descriptor["asset_id"])

    validate_audio_material(material, project_duration_seconds=float(root["project"]["duration_seconds"]))

    candidate = copy.deepcopy(root)
    candidate["project"]["parent_revision_id"] = root_id
    candidate["project"]["revision_id"] = "rev-atcm-r0-audio-authority-attempt"
    candidate["materials"]["audio"] = material

    validate_blueprint_audio(candidate, allow_nonempty=True)

    with pytest.raises(ContractError, match="does not grant accepted non-empty"):
        validate_contract(candidate, "music-blueprint-v0.schema.json")
    with pytest.raises(ContractError, match="does not grant accepted non-empty"):
        project.commit_revision(candidate, branch="main")

    assert project.head_revision_id("main") == root_id
    assert project.read_revision(root_id) == root
    assert project.verify_integrity()["audio_asset_count"] == 1
