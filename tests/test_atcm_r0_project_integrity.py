from __future__ import annotations

import io
import json
import zipfile
import wave
from pathlib import Path

import pytest

from musica.audio_assets import import_audio_asset
from musica.creative import compose_blueprint
from musica.project import MusicaProject, ProjectIntegrityError, create_project

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


def _project_with_asset(tmp_path: Path):
    project = create_project(tmp_path / "song.musica", _blueprint())
    source = tmp_path / "source.wav"
    source.write_bytes(_wav_bytes())
    descriptor = import_audio_asset(project, source)
    return project, descriptor


def test_project_integrity_aggregates_native_audio_assets(tmp_path: Path) -> None:
    project, descriptor = _project_with_asset(tmp_path)
    report = project.verify_integrity()
    assert report["status"] == "PASS"
    assert report["audio_asset_count"] == 1

    digest = descriptor["object_sha256"]
    descriptor_path = project.root / "assets" / "audio" / "sha256" / f"{digest}.json"
    value = json.loads(descriptor_path.read_text(encoding="utf-8"))
    value["size_bytes"] += 1
    descriptor_path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(ProjectIntegrityError, match="audio assets"):
        project.verify_integrity()
    with pytest.raises(ProjectIntegrityError, match="audio assets"):
        project.export_bytes()


def test_project_import_rejects_tampered_audio_descriptor_archive(tmp_path: Path) -> None:
    project, descriptor = _project_with_asset(tmp_path)
    archive = project.export_to(tmp_path / "clean.musica.zip")
    digest = descriptor["object_sha256"]
    descriptor_name = f"assets/audio/sha256/{digest}.json"

    with zipfile.ZipFile(archive, "r") as source_zip:
        members = {name: source_zip.read(name) for name in source_zip.namelist()}

    descriptor_value = json.loads(members[descriptor_name].decode("utf-8"))
    descriptor_value["size_bytes"] += 1
    members[descriptor_name] = json.dumps(
        descriptor_value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8") + b"\n"

    tampered = tmp_path / "tampered.musica.zip"
    with zipfile.ZipFile(tampered, "w", compression=zipfile.ZIP_DEFLATED) as target_zip:
        for name in sorted(members):
            target_zip.writestr(name, members[name])

    with pytest.raises(ProjectIntegrityError, match="audio assets"):
        MusicaProject.import_from(tampered, tmp_path / "rejected.musica")
