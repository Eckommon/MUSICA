from __future__ import annotations

import copy
import io
import json
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from musica.compiler import compile_blueprint
from musica.dawproject import (
    MAX_MEMBER_BYTES,
    InterchangeError,
    accept_dawproject_candidate,
    export_dawproject,
    import_dawproject_candidate,
    inspect_dawproject,
)
from musica.project import create_project

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"


def _blueprint() -> dict:
    return json.loads(BLUEPRINT.read_text(encoding="utf-8"))


def _rewrite(artifact: bytes, *, bpm: float | None = None, meter: str | None = None, note_delta: int = 0) -> bytes:
    with zipfile.ZipFile(io.BytesIO(artifact), "r") as archive:
        files = {info.filename: archive.read(info) for info in archive.infolist() if not info.is_dir()}
    root = etree.fromstring(files["project.xml"])
    if bpm is not None:
        root.find("./Transport/Tempo").set("value", str(bpm))
    if meter is not None:
        numerator, denominator = meter.split("/", 1)
        ts = root.find("./Transport/TimeSignature")
        ts.set("numerator", numerator)
        ts.set("denominator", denominator)
    if note_delta:
        note = root.find(".//Note")
        note.set("key", str(int(note.get("key")) + note_delta))
    files["project.xml"] = etree.tostring(
        root, encoding="UTF-8", xml_declaration=True, standalone=True, pretty_print=False
    )
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[name])
    return stream.getvalue()


def _project(tmp_path):
    return create_project(tmp_path / "demo.musica", _blueprint())


def test_export_is_deterministic_xsd_valid_and_non_mutating(tmp_path):
    project = _project(tmp_path)
    revision = project.head_revision_id()
    blueprint = project.read_revision(revision)
    ir = compile_blueprint(blueprint)

    first = export_dawproject(blueprint, ir)
    second = export_dawproject(blueprint, ir)

    assert first.artifact == second.artifact
    assert first.manifest == second.manifest
    inspected = inspect_dawproject(first.artifact)
    assert inspected["normalized"]["transport"] == {"bpm": 112.0, "meter": "4/4"}
    assert [track["track_id"] for track in inspected["normalized"]["tracks"]] == [
        "T-MOTIF",
        "T-BASS",
        "T-DRUMS",
    ]
    assert project.head_revision_id() == revision


def test_unedited_roundtrip_preserves_bounded_notes_and_mapping(tmp_path):
    project = _project(tmp_path)
    blueprint = project.read_revision(project.head_revision_id())
    exported = export_dawproject(blueprint)
    candidate = import_dawproject_candidate(project, exported.artifact)

    assert candidate["status"] == "PENDING"
    assert candidate["validation_status"] == "PASS"
    assert candidate["proposed_changes"] == []
    states = {item["semantic"]: item["state"] for item in candidate["loss_report"]["classifications"]}
    assert states["track_part_mapping"] == "PRESERVED"
    assert states["note_pitch"] == "PRESERVED"
    assert project.head_revision_id() == blueprint["project"]["revision_id"]


def test_tempo_edit_is_blocked_by_existing_hard_lock_and_constraint(tmp_path):
    project = _project(tmp_path)
    blueprint = project.read_revision(project.head_revision_id())
    artifact = export_dawproject(blueprint).artifact
    edited = _rewrite(artifact, bpm=130)
    candidate = import_dawproject_candidate(project, edited)

    assert candidate["status"] == "PENDING"
    assert candidate["validation_status"] == "BLOCKED"
    assert any(item["rule_id"] == "L-TEMPO" and item["status"] == "BLOCKED" for item in candidate["conflicts"])
    assert project.head_revision_id() == blueprint["project"]["revision_id"]
    with pytest.raises(InterchangeError):
        accept_dawproject_candidate(project, candidate)


def test_meter_edit_can_be_explicitly_accepted_through_m2(tmp_path):
    project = _project(tmp_path)
    source_revision = project.head_revision_id()
    blueprint = project.read_revision(source_revision)
    artifact = export_dawproject(blueprint).artifact
    edited = _rewrite(artifact, meter="3/4")
    candidate = import_dawproject_candidate(project, edited)

    assert candidate["validation_status"] == "PASS"
    assert project.head_revision_id() == source_revision

    accepted = accept_dawproject_candidate(project, candidate)
    assert accepted["candidate_id"] == candidate["candidate_id"]
    assert project.head_revision_id() == accepted["accepted_revision_id"]
    accepted_blueprint = project.read_revision(accepted["accepted_revision_id"])
    assert accepted_blueprint["musical_context"]["meter"] == "3/4"
    assert accepted_blueprint["provenance"]["actor"] == "import"
    assert accepted_blueprint["project"]["parent_revision_id"] == source_revision
    assert project.verify_integrity()["status"] == "PASS"


def test_external_note_edit_fails_closed_without_blueprint_reverse_mapping(tmp_path):
    project = _project(tmp_path)
    source_revision = project.head_revision_id()
    artifact = export_dawproject(project.read_revision(source_revision)).artifact
    edited = _rewrite(artifact, note_delta=1)
    candidate = import_dawproject_candidate(project, edited)

    assert candidate["validation_status"] == "BLOCKED"
    assert any(item["rule_id"] == "blueprint-v0-note-reverse-mapping" for item in candidate["conflicts"])
    assert project.head_revision_id() == source_revision


def test_candidate_becomes_stale_if_branch_moves_before_accept(tmp_path):
    project = _project(tmp_path)
    root = project.read_revision(project.head_revision_id())
    candidate = import_dawproject_candidate(project, _rewrite(export_dawproject(root).artifact, meter="3/4"))
    other = copy.deepcopy(root)
    other["project"]["parent_revision_id"] = root["project"]["revision_id"]
    other["project"]["revision_id"] = "rev-unrelated"
    other["intent"]["summary"] = "A deliberately different accepted revision."
    other["provenance"]["source_revision"] = root["project"]["revision_id"]
    other["provenance"]["change_reason"] = "Advance branch before interchange acceptance."
    project.commit_revision(other)

    with pytest.raises(InterchangeError, match="stale"):
        accept_dawproject_candidate(project, candidate)


def test_expected_artifact_hash_mismatch_fails_closed(tmp_path):
    import hashlib

    project = _project(tmp_path)
    artifact = export_dawproject(project.read_revision(project.head_revision_id())).artifact
    expected = hashlib.sha256(artifact).hexdigest()
    tampered = artifact + b"x"
    with pytest.raises(InterchangeError, match="hash mismatch"):
        import_dawproject_candidate(project, tampered, expected_artifact_sha256=expected)


def test_malformed_zip_fails_closed(tmp_path):
    project = _project(tmp_path)
    before = project.head_revision_id()
    with pytest.raises(InterchangeError, match="ZIP"):
        import_dawproject_candidate(project, b"not-a-zip")
    assert project.head_revision_id() == before


def test_missing_project_xml_fails_closed(tmp_path):
    project = _project(tmp_path)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("metadata.xml", "<MetaData/>")
    with pytest.raises(InterchangeError, match="missing project.xml"):
        import_dawproject_candidate(project, stream.getvalue())


def test_malformed_xml_fails_closed(tmp_path):
    project = _project(tmp_path)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("project.xml", b"<Project")
    with pytest.raises(InterchangeError, match="malformed project.xml"):
        import_dawproject_candidate(project, stream.getvalue())


def test_xsd_invalid_project_fails_closed(tmp_path):
    project = _project(tmp_path)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr(
            "project.xml",
            b'<?xml version="1.0"?><Project version="1.0"><Application name="x"/></Project>',
        )
    with pytest.raises(InterchangeError, match="XSD-valid"):
        import_dawproject_candidate(project, stream.getvalue())


@pytest.mark.parametrize("name", ["../project.xml", "/project.xml", "safe\\..\\project.xml"])
def test_unsafe_archive_paths_fail_closed(tmp_path, name):
    project = _project(tmp_path)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr(name, b"x")
        if name != "project.xml":
            archive.writestr("project.xml", b"x")
    with pytest.raises(InterchangeError, match="unsafe"):
        import_dawproject_candidate(project, stream.getvalue())


def test_duplicate_critical_entry_fails_closed(tmp_path):
    project = _project(tmp_path)
    artifact = export_dawproject(project.read_revision(project.head_revision_id())).artifact
    with zipfile.ZipFile(io.BytesIO(artifact), "r") as source:
        project_xml = source.read("project.xml")
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("project.xml", project_xml)
        archive.writestr("Project.xml", project_xml)
    with pytest.raises(InterchangeError, match="duplicate/ambiguous"):
        import_dawproject_candidate(project, stream.getvalue())


def test_doctype_or_entity_is_rejected(tmp_path):
    project = _project(tmp_path)
    payload = b'<!DOCTYPE Project [<!ENTITY xxe "x">]><Project version="1.0"><Application name="x" version="1"/></Project>'
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("project.xml", payload)
    with pytest.raises(InterchangeError, match="forbidden"):
        import_dawproject_candidate(project, stream.getvalue())


def test_unsupported_version_is_rejected(tmp_path):
    project = _project(tmp_path)
    artifact = export_dawproject(project.read_revision(project.head_revision_id())).artifact
    with zipfile.ZipFile(io.BytesIO(artifact), "r") as source:
        files = {name: source.read(name) for name in source.namelist()}
    root = etree.fromstring(files["project.xml"])
    root.set("version", "2.0")
    files["project.xml"] = etree.tostring(root, encoding="UTF-8", xml_declaration=True, standalone=True)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, payload in files.items():
            archive.writestr(name, payload)
    with pytest.raises(InterchangeError):
        import_dawproject_candidate(project, stream.getvalue())


def test_size_policy_rejects_large_member_before_authority_change(tmp_path):
    project = _project(tmp_path)
    before = project.head_revision_id()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("project.xml", b"x" * (MAX_MEMBER_BYTES + 1))
    with pytest.raises(InterchangeError, match="size policy"):
        import_dawproject_candidate(project, stream.getvalue())
    assert project.head_revision_id() == before
