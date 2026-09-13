from __future__ import annotations

import copy
import json
import zipfile
from io import BytesIO
from pathlib import Path

import pytest
from lxml import etree

from musica.interchange_note_reconcile import (
    InterchangeNoteReconcileError,
    build_interchange_note_identity_bundle,
    reconcile_dawproject_note_edit,
)
from musica.note_edit import blueprint_sha256
from musica.contracts import validate_contract

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
MATERIAL_PATH = ROOT / "examples" / "note-material" / "valid" / "dark-electronic-explicit-timeline-v0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def exact_blueprint(*, locked: bool = False) -> dict:
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
                "reason": "Protect imported reconciliation pitch.",
            }
        ]
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _rewrite_artifact(artifact: bytes, mutate) -> bytes:
    with zipfile.ZipFile(BytesIO(artifact), "r") as source:
        files = {name: source.read(name) for name in source.namelist()}
    root = etree.fromstring(files["project.xml"])
    tracks = root.find("Structure").findall("Track")
    motif = next(track for track in tracks if "track_id=T-MOTIF" in (track.get("comment") or ""))
    lane = next(lane for lane in root.xpath(".//Lanes[@track]") if lane.get("track") == motif.get("id"))
    notes = lane.xpath("./Clips/Clip/Notes/Note")
    mutate(root, notes)
    files["project.xml"] = etree.tostring(
        root, encoding="UTF-8", xml_declaration=True, standalone=True, pretty_print=False
    )
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as output:
        for name in sorted(files):
            output.writestr(name, files[name])
    return stream.getvalue()


def _set_note_attr(artifact: bytes, index: int, key: str, value: str) -> bytes:
    return _rewrite_artifact(artifact, lambda _root, notes: notes[index].set(key, value))


def test_identity_bundle_is_bound_to_exact_source_and_uses_no_array_identity() -> None:
    blueprint = exact_blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)
    identity = bundle.identity_map
    assert identity["source_revision_id"] == blueprint["project"]["revision_id"]
    assert identity["source_blueprint_sha256"] == blueprint_sha256(blueprint)
    assert identity["track_id"] == "T-MOTIF"
    assert identity["part_id"] == "P-SYNTH"
    assert [record["note_id"] for record in identity["records"]] == [
        "N-MOTIF-001",
        "N-MOTIF-002",
        "N-MOTIF-003",
    ]


@pytest.mark.parametrize(
    "attribute,value,expected_op,expected_field,expected_value",
    [
        ("time", "0.25", "MOVE", "start_beat", 0.25),
        ("duration", "0.5", "RESIZE", "duration_beats", 0.5),
        ("key", "64", "REPITCH", "pitch", 64),
        ("vel", f"{90 / 127:.6f}", "SET_VELOCITY", "velocity", 90),
    ],
)
def test_single_update_is_translated_to_existing_m6_primitive(
    attribute: str,
    value: str,
    expected_op: str,
    expected_field: str,
    expected_value: object,
) -> None:
    blueprint = exact_blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)
    returned = _set_note_attr(bundle.export.artifact, 0, attribute, value)
    result = reconcile_dawproject_note_edit(blueprint, bundle, returned)
    operation = result.candidate["operations"][0]
    assert operation["op"] == expected_op
    assert operation["target"] == {"note_id": "N-MOTIF-001", "part_id": "P-SYNTH"}
    assert operation[expected_field] == expected_value
    assert result.ready is True
    assert result.proof["array_index_used_as_identity"] is False
    assert result.proof["heuristic_nearest_note_matching"] is False
    assert result.proof["external_state_canonical_authority"] is False
    assert result.proof["project_mutation_authorized"] is False
    assert result.proof["music_ir_mutation_authorized"] is False
    assert result.proof["explicit_accept_required"] is True


def test_single_delete_maps_to_stable_note_id() -> None:
    blueprint = exact_blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)

    def remove(_root, notes):
        notes[0].getparent().remove(notes[0])

    returned = _rewrite_artifact(bundle.export.artifact, remove)
    result = reconcile_dawproject_note_edit(blueprint, bundle, returned)
    assert result.candidate["operations"][0] == {
        "op": "DELETE",
        "target": {"note_id": "N-MOTIF-001", "part_id": "P-SYNTH"},
        "operation_id": result.candidate["operations"][0]["operation_id"],
    }
    assert result.ready is True


def test_single_insert_gets_deterministic_non_source_identity_and_m6_preview() -> None:
    blueprint = exact_blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)

    def insert(_root, notes):
        node = copy.deepcopy(notes[0])
        node.set("time", "3")
        node.set("duration", "0.5")
        node.set("key", "71")
        node.set("vel", f"{75 / 127:.6f}")
        notes[0].getparent().append(node)

    returned = _rewrite_artifact(bundle.export.artifact, insert)
    first = reconcile_dawproject_note_edit(blueprint, bundle, returned)
    second = reconcile_dawproject_note_edit(blueprint, bundle, returned)
    note = first.candidate["operations"][0]["note"]
    assert first.candidate == second.candidate
    assert note["note_id"].startswith("N-IMPORT-")
    assert note["part_id"] == "P-SYNTH"
    assert note["section_id"] is not None
    assert first.ready is True


def test_hard_lock_remains_final_authority_after_reconciliation() -> None:
    blueprint = exact_blueprint(locked=True)
    bundle = build_interchange_note_identity_bundle(blueprint)
    returned = _set_note_attr(bundle.export.artifact, 0, "key", "64")
    result = reconcile_dawproject_note_edit(blueprint, bundle, returned)
    assert result.candidate["operations"][0]["op"] == "REPITCH"
    assert result.preview.authority_result["status"] == "BLOCKED"
    assert result.preview.authority_result["preview_generation_allowed"] is False
    assert any(
        conflict["code"] == "HARD_LOCK_VIOLATION"
        for conflict in result.preview.authority_result["conflicts"]
    )


def test_multiple_field_change_fails_closed_instead_of_guessing() -> None:
    blueprint = exact_blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)

    def mutate(_root, notes):
        notes[0].set("time", "0.25")
        notes[0].set("key", "64")

    returned = _rewrite_artifact(bundle.export.artifact, mutate)
    with pytest.raises(InterchangeNoteReconcileError, match="not one uniquely representable M6 primitive"):
        reconcile_dawproject_note_edit(blueprint, bundle, returned)


def test_two_note_changes_fail_closed() -> None:
    blueprint = exact_blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)

    def mutate(_root, notes):
        notes[0].set("key", "64")
        notes[1].set("key", "67")

    returned = _rewrite_artifact(bundle.export.artifact, mutate)
    with pytest.raises(InterchangeNoteReconcileError, match="more than one primitive"):
        reconcile_dawproject_note_edit(blueprint, bundle, returned)


def test_unchanged_returned_artifact_is_not_an_edit_candidate() -> None:
    blueprint = exact_blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)
    with pytest.raises(InterchangeNoteReconcileError, match="ambiguous, empty"):
        reconcile_dawproject_note_edit(blueprint, bundle, bundle.export.artifact)


def test_transport_change_is_not_smuggled_with_note_reconciliation() -> None:
    blueprint = exact_blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)

    def mutate(root, _notes):
        root.find("Transport").find("Tempo").set("value", "130")

    returned = _rewrite_artifact(bundle.export.artifact, mutate)
    with pytest.raises(InterchangeNoteReconcileError, match="does not reconcile transport edits"):
        reconcile_dawproject_note_edit(blueprint, bundle, returned)


def test_stale_source_binding_fails_closed_before_external_reconciliation() -> None:
    blueprint = exact_blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)
    moved = copy.deepcopy(blueprint)
    moved["project"]["revision_id"] = "rev-moved-after-export"
    with pytest.raises(InterchangeNoteReconcileError, match="source_revision_id mismatch"):
        reconcile_dawproject_note_edit(moved, bundle, bundle.export.artifact)


def test_duplicate_lowered_exact_note_signature_is_refused_as_ambiguous_identity() -> None:
    blueprint = exact_blueprint()
    duplicate = copy.deepcopy(blueprint["materials"]["melody"]["exact_timeline"]["notes"][0])
    duplicate["note_id"] = "N-MOTIF-DUPLICATE"
    blueprint["materials"]["melody"]["exact_timeline"]["notes"].append(duplicate)
    blueprint["materials"]["melody"]["exact_timeline"]["notes"].sort(
        key=lambda item: (item["start_beat"], item["part_id"], item["pitch"], item["note_id"])
    )
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    with pytest.raises(InterchangeNoteReconcileError, match="duplicate lowered note signature"):
        build_interchange_note_identity_bundle(blueprint)
