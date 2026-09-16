from __future__ import annotations

import copy
import io
import json
import wave
from pathlib import Path

import pytest

from musica.audio_assets import (
    audio_asset_bytes,
    import_audio_asset,
    list_audio_assets,
    read_audio_asset,
    verify_audio_assets,
)
from musica.audio_contracts import (
    audio_material_from_blueprint,
    empty_audio_material,
    validate_audio_material,
    validate_blueprint_audio,
)
from musica.contracts import ContractError, validate_contract
from musica.creative import compose_blueprint
from musica.project import MusicaProject, ProjectIntegrityError, create_project

ROOT = Path(__file__).resolve().parents[1]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def _blueprint() -> dict:
    intent = json.loads(INTENT_PATH.read_text(encoding="utf-8"))
    return compose_blueprint(intent)


def _wav_bytes(
    *, channels: int = 2, sample_rate: int = 8000, sample_width: int = 2, frames: int = 64
) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(sample_width)
        writer.setframerate(sample_rate)
        frame = bytes([0] * channels * sample_width)
        writer.writeframes(frame * frames)
    return stream.getvalue()


def _write_wav(path: Path, **kwargs) -> bytes:
    data = _wav_bytes(**kwargs)
    path.write_bytes(data)
    return data


def _material(asset_id: str = "sha256:" + "a" * 64) -> dict:
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
                        "source_out_seconds": 2.0,
                        "gain_db": -3.0,
                    }
                ],
            }
        ],
    }


def test_legacy_blueprint_has_deterministic_empty_audio_material() -> None:
    blueprint = _blueprint()
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    assert audio_material_from_blueprint(blueprint) == empty_audio_material()
    assert audio_material_from_blueprint(blueprint, materialize_empty=False) is None
    validate_blueprint_audio(blueprint)


def test_blueprint_allows_explicit_valid_audio_material() -> None:
    blueprint = _blueprint()
    blueprint["materials"]["audio"] = _material()
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    validate_blueprint_audio(blueprint)
    assert audio_material_from_blueprint(blueprint, materialize_empty=False) == _material()


def test_audio_material_rejects_duplicate_ids_bad_ranges_and_noncanonical_order() -> None:
    duplicate_tracks = _material()
    second = copy.deepcopy(duplicate_tracks["tracks"][0])
    second["order"] = 1
    duplicate_tracks["tracks"].append(second)
    with pytest.raises(ContractError, match="track_id.*unique"):
        validate_audio_material(duplicate_tracks)

    duplicate_clips = _material()
    second_clip = copy.deepcopy(duplicate_clips["tracks"][0]["clips"][0])
    second_clip["timeline_start_seconds"] = 4.0
    duplicate_clips["tracks"][0]["clips"].append(second_clip)
    with pytest.raises(ContractError, match="clip_id.*unique"):
        validate_audio_material(duplicate_clips)

    bad_range = _material()
    bad_range["tracks"][0]["clips"][0]["source_in_seconds"] = 2.0
    with pytest.raises(ContractError, match="source_out_seconds must exceed"):
        validate_audio_material(bad_range)

    overrun = _material()
    overrun["tracks"][0]["clips"][0]["timeline_start_seconds"] = 11.5
    with pytest.raises(ContractError, match="exceeds project duration"):
        validate_audio_material(overrun, project_duration_seconds=12.0)

    unordered = _material()
    first = unordered["tracks"][0]
    first["order"] = 1
    earlier = copy.deepcopy(first)
    earlier["track_id"] = "AT-000"
    earlier["order"] = 0
    earlier["clips"] = []
    unordered["tracks"].append(earlier)
    with pytest.raises(ContractError, match="canonical order"):
        validate_audio_material(unordered)


def test_supported_wav_import_is_content_addressed_and_idempotent(tmp_path: Path) -> None:
    project = create_project(tmp_path / "song.musica", _blueprint())
    source_a = tmp_path / "source-a.wav"
    source_b = tmp_path / "renamed-source.wav"
    data = _write_wav(source_a)
    source_b.write_bytes(data)

    first = import_audio_asset(project, source_a)
    audit_after_first = len(project._audit_events())
    second = import_audio_asset(project, source_b)

    assert first == second
    assert second["asset_id"].startswith("sha256:")
    assert second["object_sha256"] == second["asset_id"].split(":", 1)[1]
    assert second["size_bytes"] == len(data)
    assert second["format"] == {
        "container": "wav",
        "codec": "pcm_integer",
        "channels": 2,
        "sample_rate_hz": 8000,
        "sample_width_bytes": 2,
        "frame_count": 64,
        "duration_seconds": 64 / 8000,
    }
    assert audio_asset_bytes(project, second["asset_id"]) == data
    assert list_audio_assets(project) == [second]
    assert verify_audio_assets(project)["audio_asset_count"] == 1
    assert len(project._audit_events()) == audit_after_first
    assert project.verify_integrity()["status"] == "PASS"


def test_asset_export_import_and_reexport_preserve_exact_identity(tmp_path: Path) -> None:
    project = create_project(tmp_path / "song.musica", _blueprint())
    source = tmp_path / "source.wav"
    data = _write_wav(source, channels=1, sample_rate=16000, frames=80)
    descriptor = import_audio_asset(project, source)

    archive = project.export_to(tmp_path / "project.musica.zip")
    imported = MusicaProject.import_from(archive, tmp_path / "imported.musica")

    assert verify_audio_assets(imported)["status"] == "PASS"
    assert read_audio_asset(imported, descriptor["asset_id"]) == descriptor
    assert audio_asset_bytes(imported, descriptor["asset_id"]) == data
    assert imported.export_bytes() == archive.read_bytes()


def test_invalid_and_unsupported_audio_fail_closed(tmp_path: Path) -> None:
    project = create_project(tmp_path / "song.musica", _blueprint())

    malformed = tmp_path / "malformed.wav"
    malformed.write_bytes(b"not-a-wave")
    with pytest.raises(ContractError, match="RIFF/WAVE"):
        import_audio_asset(project, malformed)

    too_many_channels = tmp_path / "three-channel.wav"
    _write_wav(too_many_channels, channels=3)
    with pytest.raises(ContractError, match="mono or stereo"):
        import_audio_asset(project, too_many_channels)

    low_rate = tmp_path / "low-rate.wav"
    _write_wav(low_rate, sample_rate=4000)
    with pytest.raises(ContractError, match="8000 and 192000"):
        import_audio_asset(project, low_rate)


def test_missing_tampered_and_descriptor_corruption_fail_closed(tmp_path: Path) -> None:
    project = create_project(tmp_path / "song.musica", _blueprint())
    source = tmp_path / "source.wav"
    _write_wav(source)
    descriptor = import_audio_asset(project, source)
    digest = descriptor["object_sha256"]

    object_path = project._object_path(digest)
    original = object_path.read_bytes()
    object_path.write_bytes(original + b"x")
    with pytest.raises(ProjectIntegrityError, match="object hash mismatch"):
        project.verify_integrity()
    with pytest.raises(ProjectIntegrityError, match="object hash mismatch"):
        verify_audio_assets(project)

    object_path.write_bytes(original)
    assert verify_audio_assets(project)["status"] == "PASS"

    descriptor_path = project.root / "assets" / "audio" / "sha256" / f"{digest}.json"
    value = json.loads(descriptor_path.read_text(encoding="utf-8"))
    value["size_bytes"] += 1
    descriptor_path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ProjectIntegrityError, match="size mismatch|descriptor object"):
        read_audio_asset(project, descriptor["asset_id"])

    descriptor_path.write_bytes(project._object_path(
        next(
            event["payload"]["descriptor_sha256"]
            for event in project._audit_events()
            if event["event_type"] == "import_audio_asset"
        )
    ).read_bytes())
    assert verify_audio_assets(project)["status"] == "PASS"

    object_path.unlink()
    with pytest.raises(ProjectIntegrityError, match="missing audio asset object"):
        verify_audio_assets(project)


def test_asset_identifier_cannot_escape_project_boundary(tmp_path: Path) -> None:
    project = create_project(tmp_path / "song.musica", _blueprint())
    with pytest.raises(ContractError, match="invalid audio asset_id"):
        read_audio_asset(project, "sha256:../../revisions/main")
    with pytest.raises(ContractError, match="invalid audio asset_id"):
        read_audio_asset(project, "../outside")
