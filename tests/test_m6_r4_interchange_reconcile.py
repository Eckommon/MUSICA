from __future__ import annotations

import copy
import io
import json
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from musica.contracts import clone_for_revision, validate_contract
from musica.dawproject import import_dawproject_candidate
from musica.interchange_reconcile import (
    ReconciliationError,
    accept_dawproject_note_reconciliation,
    export_dawproject_note_roundtrip,
    reconcile_dawproject_note_edit,
)
from musica.project import create_project

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
MATERIAL_PATH = ROOT / "examples" / "note-material" / "valid" / "dark-electronic-explicit-timeline-v0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _exact_blueprint(*, locked: bool = False) -> dict:
    blueprint = _load(BLUEPRINT_PATH)
    blueprint["materials"]["melody"]["exact_timeline"] = _load(MATERIAL_PATH)
    if locked:
        blueprint["materials"]["melody"]["exact_note_locks"] = [
            {
                "lock_version": "0",
                "lock_id": "L-M6-R4-PITCH",
                "strength": "HARD",
                "selector": {
                    "part_id": "P-SYNTH",
                    "note_id": "N-MOTIF-001",
                    "property": "pitch",
                },
                "mode": "exact",
                "inheriting": True,
                "value": 62,
                "reason": "Protect R4 source pitch.",
            }
        ]
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _project(tmp_path: Path, *, locked: bool = False):
    return create_project(tmp_path / "r4.musica", _exact_blueprint(locked=locked))


def _artifact_files(artifact: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(artifact), "r") as archive:
        return {info.filename: archive.read(info) for info in archive.infolist() if not info.is_dir()}


def _zip(files: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[name])
    return stream.getvalue()


def _rewrite(
    artifact: bytes,
    *,
    pitch: int | None = None,
    time: float | None = None,
    duration: float | None = None,
    velocity: int | None = None,
    delete: bool = False,
    insert: bool = False,
    compound: bool = False,
    multi: bool = False,
    other_track: bool = False,
    tempo: float | None = None,
    reverse_motif_order: bool = False,
) -> bytes:
    files = _artifact_files(artifact)
    root = etree.fromstring(files["project.xml"])
    if tempo is not None:
        root.find("./Transport/Tempo").set("value", str(tempo))

    note_groups = root.xpath(".//Notes")
    motif_notes = note_groups[0]
    notes = motif_notes.findall("Note")
    first = notes[0]

    if pitch is not None:
        first.set("key", str(pitch))
    if time is not None:
        first.set("time", str(time))
    if duration is not None:
        first.set("duration", str(duration))
    if velocity is not None:
        first.set("vel", f"{velocity / 127.0:.6f}")
    if compound:
        first.set("key", str(int(first.get("key")) + 1))
        first.set("time", "0.25")
    if multi:
        first.set("key", str(int(first.get("key")) + 1))
        notes[1].set("key", str(int(notes[1].get("key")) + 1))
    if delete:
        motif_notes.remove(first)
    if insert:
        etree.SubElement(
            motif_notes,
            "Note",
            time="3",
            duration="0.5",
            channel=first.get("channel"),
            key="67",
            vel=f"{74 / 127.0:.6f}",
        )
    if other_track:
        external = note_groups[1].find("Note")
        external.set("key", str(int(external.get("key")) + 1))
    if reverse_motif_order:
        current = motif_notes.findall("Note")
        for note in current:
            motif_notes.remove(note)
        for note in reversed(current):
            motif_notes.append(note)

    files["project.xml"] = etree.tostring(
        root,
        encoding="UTF-8",
        xml_declaration=True,
        standalone=True,
        pretty_print=False,
    )
    return _zip(files)


def _roundtrip(project):
    source = project.read_revision(project.head_revision_id())
    return source, export_dawproject_note_roundtrip(source)


def test_receipt_is_source_bound_schema_valid_and_non_mutating(tmp_path: Path) -> None:
    project = _project(tmp_path)
    source_revision = project.head_revision_id()
    source, roundtrip = _roundtrip(project)

    validate_contract(roundtrip.receipt, "interchange-note-receipt-v0.schema.json")
    assert roundtrip.receipt["source"]["revision_id"] == source_revision
    assert roundtrip.receipt["scope"] == {
        "track_id": "T-MOTIF",
        "part_id": "P-SYNTH",
        "channel": 0,
        "single_primitive_only": True,
    }
    assert [item["note_id"] for item in roundtrip.receipt["note_identity_map"]] == [
        "N-MOTIF-001",
        "N-MOTIF-002",
        "N-MOTIF-003",
    ]
    assert project.head_revision_id() == source["project"]["revision_id"]


@pytest.mark.parametrize(
    "rewrite_kwargs,op,field,value",
    [
        ({"pitch": 64}, "REPITCH", "pitch", 64),
        ({"time": 0.25}, "MOVE", "start_beat", 0.25),
        ({"duration": 0.5}, "RESIZE", "duration_beats", 0.5),
        ({"velocity": 90}, "SET_VELOCITY", "velocity", 90),
    ],
)
def test_single_update_primitive_reconciles_through_existing_m6_authority(
    tmp_path: Path, rewrite_kwargs: dict, op: str, field: str, value: object
) -> None:
    project = _project(tmp_path)
    source, roundtrip = _roundtrip(project)
    returned = _rewrite(roundtrip.artifact, **rewrite_kwargs)

    result = reconcile_dawproject_note_edit(project, roundtrip.receipt, returned)

    assert result.ready is True
    assert result.operation["op"] == op
    assert result.operation["target"] == {"note_id": "N-MOTIF-001", "part_id": "P-SYNTH"}
    assert result.operation[field] == value
    assert result.candidate["actor"]["kind"] == "import"
    assert result.preview.authority_result["project_mutation_authorized"] is False
    assert result.preview.authority_result["music_ir_mutation_authorized"] is False
    assert project.head_revision_id() == source["project"]["revision_id"]


def test_xml_note_order_is_not_used_as_identity(tmp_path: Path) -> None:
    project = _project(tmp_path)
    _, roundtrip = _roundtrip(project)
    returned = _rewrite(roundtrip.artifact, pitch=64, reverse_motif_order=True)

    result = reconcile_dawproject_note_edit(project, roundtrip.receipt, returned)

    assert result.ready is True
    assert result.operation["op"] == "REPITCH"
    assert result.operation["target"]["note_id"] == "N-MOTIF-001"


def test_delete_reconciles_to_stable_id_target(tmp_path: Path) -> None:
    project = _project(tmp_path)
    _, roundtrip = _roundtrip(project)
    result = reconcile_dawproject_note_edit(project, roundtrip.receipt, _rewrite(roundtrip.artifact, delete=True))

    assert result.ready is True
    assert result.operation == {
        "operation_id": result.operation["operation_id"],
        "op": "DELETE",
        "target": {"note_id": "N-MOTIF-001", "part_id": "P-SYNTH"},
    }


def test_insert_gets_deterministic_new_identity_and_section(tmp_path: Path) -> None:
    project = _project(tmp_path)
    _, roundtrip = _roundtrip(project)
    returned = _rewrite(roundtrip.artifact, insert=True)

    first = reconcile_dawproject_note_edit(project, roundtrip.receipt, returned)
    second = reconcile_dawproject_note_edit(project, roundtrip.receipt, returned)

    assert first.ready is True
    assert second.ready is True
    assert first.operation == second.operation
    assert first.operation["op"] == "INSERT"
    assert first.operation["note"]["note_id"].startswith("N-IMP-")
    assert first.operation["note"]["part_id"] == "P-SYNTH"
    assert first.operation["note"]["section_id"] == "S01"
    assert first.operation["note"]["pitch"] == 67


def test_explicit_accept_advances_once_through_m2(tmp_path: Path) -> None:
    project = _project(tmp_path)
    source, roundtrip = _roundtrip(project)
    returned = _rewrite(roundtrip.artifact, pitch=64)
    result = reconcile_dawproject_note_edit(project, roundtrip.receipt, returned)

    assert project.head_revision_id() == source["project"]["revision_id"]
    accepted = accept_dawproject_note_reconciliation(project, result)
    assert project.head_revision_id() == accepted["revision_id"]
    accepted_blueprint = project.read_revision(accepted["revision_id"])
    note = next(
        note
        for note in accepted_blueprint["materials"]["melody"]["exact_timeline"]["notes"]
        if note["note_id"] == "N-MOTIF-001"
    )
    assert note["pitch"] == 64
    assert accepted_blueprint["provenance"]["actor"] == "import"
    assert project.verify_integrity()["status"] == "PASS"


def test_historical_m5_generic_import_still_blocks_same_external_note_edit(tmp_path: Path) -> None:
    project = _project(tmp_path)
    _, roundtrip = _roundtrip(project)
    returned = _rewrite(roundtrip.artifact, pitch=64)

    legacy_candidate = import_dawproject_candidate(project, returned)
    r4 = reconcile_dawproject_note_edit(project, roundtrip.receipt, returned)

    assert legacy_candidate["validation_status"] == "BLOCKED"
    assert any(item["rule_id"] == "blueprint-v0-note-reverse-mapping" for item in legacy_candidate["conflicts"])
    assert r4.ready is True


@pytest.mark.parametrize(
    "kwargs,reason_fragment",
    [
        ({"compound": True}, "exactly one primitive"),
        ({"multi": True}, "multi-note or compound"),
        ({"other_track": True}, "outside the scoped exact-note track"),
        ({"tempo": 120}, "unchanged tempo and meter"),
    ],
)
def test_unsupported_or_compound_returned_changes_fail_closed(
    tmp_path: Path, kwargs: dict, reason_fragment: str
) -> None:
    project = _project(tmp_path)
    source, roundtrip = _roundtrip(project)
    result = reconcile_dawproject_note_edit(project, roundtrip.receipt, _rewrite(roundtrip.artifact, **kwargs))

    assert result.ready is False
    assert result.status == "BLOCKED"
    assert result.conflicts[0]["code"] == "UNREPRESENTABLE_EDIT"
    assert reason_fragment in result.conflicts[0]["reason"]
    assert project.head_revision_id() == source["project"]["revision_id"]


def test_no_external_note_delta_does_not_create_candidate(tmp_path: Path) -> None:
    project = _project(tmp_path)
    _, roundtrip = _roundtrip(project)
    result = reconcile_dawproject_note_edit(project, roundtrip.receipt, roundtrip.artifact)

    assert result.status == "BLOCKED"
    assert result.candidate is None
    assert "no scoped exact-note delta" in result.conflicts[0]["reason"]


def test_stale_source_is_delegated_to_existing_m6_authority(tmp_path: Path) -> None:
    project = _project(tmp_path)
    source, roundtrip = _roundtrip(project)
    returned = _rewrite(roundtrip.artifact, pitch=64)

    advanced = clone_for_revision(source, "rev-r4-concurrent")
    advanced["intent"]["summary"] = "Concurrent accepted change before R4 reconciliation."
    advanced["provenance"]["source_revision"] = source["project"]["revision_id"]
    advanced["provenance"]["change_reason"] = "Advance branch before returned DAWproject reconciliation."
    project.commit_revision(advanced)

    result = reconcile_dawproject_note_edit(project, roundtrip.receipt, returned)

    assert result.status == "BLOCKED"
    assert result.preview is not None
    assert result.preview.authority_result["conflicts"][0]["code"] == "STALE_SOURCE"
    assert project.head_revision_id() == "rev-r4-concurrent"


def test_hard_note_lock_remains_authoritative(tmp_path: Path) -> None:
    project = _project(tmp_path, locked=True)
    source, roundtrip = _roundtrip(project)
    returned = _rewrite(roundtrip.artifact, pitch=64)

    result = reconcile_dawproject_note_edit(project, roundtrip.receipt, returned)

    assert result.status == "BLOCKED"
    assert result.preview is not None
    conflict = result.preview.authority_result["conflicts"][0]
    assert conflict["code"] == "HARD_LOCK_VIOLATION"
    assert conflict["rule_id"] == "L-M6-R4-PITCH"
    assert project.head_revision_id() == source["project"]["revision_id"]


def test_legacy_non_exact_project_cannot_fabricate_identity_receipt() -> None:
    legacy = _load(BLUEPRINT_PATH)
    with pytest.raises(ReconciliationError, match="exact_timeline"):
        export_dawproject_note_roundtrip(legacy)


def test_duplicate_accepted_interchange_signature_fails_receipt_creation() -> None:
    blueprint = _exact_blueprint()
    duplicate = copy.deepcopy(blueprint["materials"]["melody"]["exact_timeline"]["notes"][0])
    duplicate["note_id"] = "N-MOTIF-001-DUP"
    blueprint["materials"]["melody"]["exact_timeline"]["notes"].append(duplicate)
    blueprint["materials"]["melody"]["exact_timeline"]["notes"].sort(
        key=lambda item: (item["start_beat"], item["part_id"], item["pitch"], item["note_id"])
    )
    validate_contract(blueprint, "music-blueprint-v0.schema.json")

    with pytest.raises(ReconciliationError, match="share one interchange signature"):
        export_dawproject_note_roundtrip(blueprint)


def test_tampered_receipt_hash_fails_closed_before_mapping(tmp_path: Path) -> None:
    project = _project(tmp_path)
    _, roundtrip = _roundtrip(project)
    receipt = copy.deepcopy(roundtrip.receipt)
    receipt["identity_map_sha256"] = "0" * 64

    with pytest.raises(ReconciliationError, match="does not reproduce|hash mismatch"):
        reconcile_dawproject_note_edit(project, receipt, _rewrite(roundtrip.artifact, pitch=64))
