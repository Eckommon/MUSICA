"""Generate canonical MUSICA M6-R4 bounded interchange reconciliation evidence."""

from __future__ import annotations

import argparse
import copy
import io
import json
import zipfile
from pathlib import Path
from typing import Any

from lxml import etree

from .contracts import clone_for_revision, validate_contract
from .dawproject import import_dawproject_candidate, inspect_dawproject
from .evidence import artifact_record, canonical_json_bytes, write_canonical_json
from .interchange_reconcile import (
    ReconciliationError,
    accept_dawproject_note_reconciliation,
    export_dawproject_note_roundtrip,
    reconcile_dawproject_note_edit,
)
from .note_edit import blueprint_sha256
from .project import create_project

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BLUEPRINT = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
DEFAULT_MATERIAL = ROOT / "examples" / "note-material" / "valid" / "dark-electronic-explicit-timeline-v0.json"


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _exact_blueprint(
    blueprint_path: str | Path = DEFAULT_BLUEPRINT,
    material_path: str | Path = DEFAULT_MATERIAL,
    *,
    locked: bool = False,
) -> dict[str, Any]:
    blueprint = _load(blueprint_path)
    blueprint["materials"]["melody"]["exact_timeline"] = _load(material_path)
    if locked:
        blueprint["materials"]["melody"]["exact_note_locks"] = [
            {
                "lock_version": "0",
                "lock_id": "L-M6-R4-EVIDENCE-PITCH",
                "strength": "HARD",
                "selector": {
                    "part_id": "P-SYNTH",
                    "note_id": "N-MOTIF-001",
                    "property": "pitch",
                },
                "mode": "exact",
                "inheriting": True,
                "value": 62,
                "reason": "Canonical M6-R4 negative proof protects the first motif pitch.",
            }
        ]
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _artifact_files(artifact: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(artifact), "r") as archive:
        return {
            info.filename: archive.read(info)
            for info in archive.infolist()
            if not info.is_dir()
        }


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


def _write_bytes(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def run_suite(
    out_dir: str | Path,
    *,
    blueprint_path: str | Path = DEFAULT_BLUEPRINT,
    material_path: str | Path = DEFAULT_MATERIAL,
) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    source = _exact_blueprint(blueprint_path, material_path)
    project = create_project(root / "workspace" / "source.musica", source)
    source_revision = project.head_revision_id()
    first_export = export_dawproject_note_roundtrip(source)
    second_export = export_dawproject_note_roundtrip(copy.deepcopy(source))
    if first_export.artifact != second_export.artifact or first_export.receipt != second_export.receipt:
        raise RuntimeError("M6-R4 deterministic source export/receipt proof failed")

    baseline_inspected = inspect_dawproject(first_export.artifact)
    source_out = write_canonical_json(root / "inputs" / "source-blueprint.json", source)
    baseline_out = write_canonical_json(root / "export" / "baseline-normalized.json", baseline_inspected["normalized"])
    receipt_out = write_canonical_json(root / "export" / "note-receipt.json", first_export.receipt)
    export_out = _write_bytes(root / "export" / "source.dawproject", first_export.artifact)

    variants: dict[str, dict[str, Any]] = {
        "MOVE": {"time": 0.25},
        "RESIZE": {"duration": 0.5},
        "REPITCH": {"pitch": 64, "reverse_motif_order": True},
        "SET_VELOCITY": {"velocity": 90},
        "DELETE": {"delete": True},
        "INSERT": {"insert": True},
    }
    reconciliations: dict[str, Any] = {}
    returned_paths: list[Path] = []
    reconciliation_paths: list[Path] = []
    for expected_op, kwargs in variants.items():
        returned = _rewrite(first_export.artifact, **kwargs)
        result = reconcile_dawproject_note_edit(project, first_export.receipt, returned)
        if not result.ready or result.operation is None or result.operation["op"] != expected_op:
            raise RuntimeError(f"M6-R4 {expected_op} did not reconcile to READY_FOR_PREVIEW")
        slug = expected_op.lower().replace("set_velocity", "velocity")
        returned_path = _write_bytes(root / "returned" / f"{slug}.dawproject", returned)
        result_path = write_canonical_json(root / "reconciliation" / f"{slug}.json", result.as_dict())
        returned_paths.append(returned_path)
        reconciliation_paths.append(result_path)
        reconciliations[expected_op] = result

    historical = import_dawproject_candidate(
        project,
        (root / "returned" / "repitch.dawproject").read_bytes(),
    )
    historical_out = write_canonical_json(
        root / "negative" / "m5-generic-import-note-blocked.json",
        historical,
    )

    compound_returned = _rewrite(first_export.artifact, compound=True)
    compound_result = reconcile_dawproject_note_edit(project, first_export.receipt, compound_returned)
    if compound_result.status != "BLOCKED":
        raise RuntimeError("M6-R4 compound delta must fail closed")
    compound_returned_out = _write_bytes(root / "negative" / "compound-returned.dawproject", compound_returned)
    compound_out = write_canonical_json(root / "negative" / "compound-result.json", compound_result.as_dict())

    other_track_returned = _rewrite(first_export.artifact, other_track=True)
    other_track_result = reconcile_dawproject_note_edit(project, first_export.receipt, other_track_returned)
    if other_track_result.status != "BLOCKED":
        raise RuntimeError("M6-R4 non-scoped track mutation must fail closed")
    other_track_out = write_canonical_json(
        root / "negative" / "other-track-result.json",
        other_track_result.as_dict(),
    )

    transport_returned = _rewrite(first_export.artifact, tempo=120)
    transport_result = reconcile_dawproject_note_edit(project, first_export.receipt, transport_returned)
    if transport_result.status != "BLOCKED":
        raise RuntimeError("M6-R4 transport mutation must fail closed")
    transport_out = write_canonical_json(
        root / "negative" / "transport-result.json",
        transport_result.as_dict(),
    )

    stale_project = create_project(root / "workspace" / "stale.musica", source)
    stale_export = export_dawproject_note_roundtrip(source)
    advanced = clone_for_revision(source, "rev-m6-r4-evidence-concurrent")
    advanced["intent"]["summary"] = "Concurrent accepted revision for M6-R4 stale proof."
    advanced["provenance"]["source_revision"] = source_revision
    advanced["provenance"]["change_reason"] = "Advance branch before returned interchange reconciliation."
    stale_project.commit_revision(advanced)
    stale_result = reconcile_dawproject_note_edit(
        stale_project,
        stale_export.receipt,
        _rewrite(stale_export.artifact, pitch=64),
    )
    if stale_result.preview is None or stale_result.preview.authority_result["conflicts"][0]["code"] != "STALE_SOURCE":
        raise RuntimeError("M6-R4 stale-source proof did not delegate to existing M6 authority")
    stale_out = write_canonical_json(root / "negative" / "stale-source-result.json", stale_result.as_dict())

    locked_source = _exact_blueprint(blueprint_path, material_path, locked=True)
    locked_project = create_project(root / "workspace" / "locked.musica", locked_source)
    locked_export = export_dawproject_note_roundtrip(locked_source)
    locked_result = reconcile_dawproject_note_edit(
        locked_project,
        locked_export.receipt,
        _rewrite(locked_export.artifact, pitch=64),
    )
    if locked_result.preview is None or locked_result.preview.authority_result["conflicts"][0]["code"] != "HARD_LOCK_VIOLATION":
        raise RuntimeError("M6-R4 HARD-lock proof did not delegate to existing M6 authority")
    lock_out = write_canonical_json(root / "negative" / "hard-lock-result.json", locked_result.as_dict())

    ambiguous_source = copy.deepcopy(source)
    duplicate = copy.deepcopy(ambiguous_source["materials"]["melody"]["exact_timeline"]["notes"][0])
    duplicate["note_id"] = "N-MOTIF-001-DUP"
    ambiguous_source["materials"]["melody"]["exact_timeline"]["notes"].append(duplicate)
    ambiguous_source["materials"]["melody"]["exact_timeline"]["notes"].sort(
        key=lambda item: (item["start_beat"], item["part_id"], item["pitch"], item["note_id"])
    )
    validate_contract(ambiguous_source, "music-blueprint-v0.schema.json")
    ambiguous_blocked = False
    ambiguous_reason = None
    try:
        export_dawproject_note_roundtrip(ambiguous_source)
    except ReconciliationError as exc:
        ambiguous_blocked = True
        ambiguous_reason = str(exc)
    ambiguous_out = write_canonical_json(
        root / "negative" / "ambiguous-identity-result.json",
        {"blocked": ambiguous_blocked, "reason": ambiguous_reason},
    )

    legacy = _load(blueprint_path)
    legacy_blocked = False
    legacy_reason = None
    try:
        export_dawproject_note_roundtrip(legacy)
    except ReconciliationError as exc:
        legacy_blocked = True
        legacy_reason = str(exc)
    legacy_out = write_canonical_json(
        root / "negative" / "legacy-no-fabrication-result.json",
        {"blocked": legacy_blocked, "reason": legacy_reason},
    )

    ref_before_accept = project.head_revision_id()
    repitch_result = reconciliations["REPITCH"]
    accepted_record = accept_dawproject_note_reconciliation(project, repitch_result)
    accepted_revision = project.head_revision_id()
    accepted_blueprint = project.read_revision(accepted_revision)
    accepted_note = next(
        note
        for note in accepted_blueprint["materials"]["melody"]["exact_timeline"]["notes"]
        if note["note_id"] == "N-MOTIF-001"
    )
    integrity = project.verify_integrity()
    accepted_record_out = write_canonical_json(root / "accepted" / "revision-record.json", accepted_record)
    accepted_blueprint_out = write_canonical_json(root / "accepted" / "blueprint.json", accepted_blueprint)
    integrity_out = write_canonical_json(root / "accepted" / "project-integrity.json", integrity)

    operation_map = {
        op: reconciliations[op].operation["op"]
        for op in sorted(reconciliations)
    }
    proof = {
        "proof_version": "0",
        "source_project_id": source["project"]["project_id"],
        "source_revision_id": source_revision,
        "source_blueprint_sha256": blueprint_sha256(source),
        "source_export_deterministic": first_export.artifact == second_export.artifact,
        "source_receipt_deterministic": first_export.receipt == second_export.receipt,
        "receipt_artifact_sha256": first_export.receipt["export"]["artifact_sha256"],
        "receipt_normalized_sha256": first_export.receipt["export"]["normalized_sha256"],
        "identity_map_sha256": first_export.receipt["identity_map_sha256"],
        "identity_map_note_ids": sorted(item["note_id"] for item in first_export.receipt["note_identity_map"]),
        "all_six_operations_reconciled": set(operation_map.values())
        == {"INSERT", "DELETE", "MOVE", "RESIZE", "REPITCH", "SET_VELOCITY"},
        "operation_map": operation_map,
        "xml_note_order_not_identity": reconciliations["REPITCH"].operation["target"]["note_id"] == "N-MOTIF-001",
        "all_ready_results_non_authoritative": all(
            item.preview is not None
            and item.preview.authority_result["project_mutation_authorized"] is False
            and item.preview.authority_result["music_ir_mutation_authorized"] is False
            and item.preview.authority_result["explicit_accept_required"] is True
            for item in reconciliations.values()
        ),
        "accepted_ref_unchanged_before_accept": ref_before_accept == source_revision,
        "explicit_accept_advanced_once": accepted_revision == accepted_record["revision_id"]
        and accepted_record["parent_revision_id"] == source_revision,
        "accepted_repitch_value": accepted_note["pitch"],
        "accepted_project_integrity": integrity["status"],
        "historical_m5_generic_note_import_still_blocked": historical["validation_status"] == "BLOCKED"
        and any(item["rule_id"] == "blueprint-v0-note-reverse-mapping" for item in historical["conflicts"]),
        "compound_delta_blocked": compound_result.status == "BLOCKED",
        "other_track_delta_blocked": other_track_result.status == "BLOCKED",
        "transport_delta_blocked": transport_result.status == "BLOCKED",
        "stale_source_blocked": stale_result.status == "BLOCKED"
        and stale_result.preview is not None
        and stale_result.preview.authority_result["conflicts"][0]["code"] == "STALE_SOURCE",
        "hard_lock_blocked": locked_result.status == "BLOCKED"
        and locked_result.preview is not None
        and locked_result.preview.authority_result["conflicts"][0]["code"] == "HARD_LOCK_VIOLATION",
        "ambiguous_identity_blocked": ambiguous_blocked,
        "legacy_exact_identity_not_fabricated": legacy_blocked,
        "external_project_mutation_authorized": False,
        "music_ir_mutation_authorized": False,
        "arbitrary_daw_reverse_mapping_validated": False,
        "real_external_daw_compatibility_validated": False,
    }
    required = [
        proof["source_export_deterministic"],
        proof["source_receipt_deterministic"],
        proof["all_six_operations_reconciled"],
        proof["xml_note_order_not_identity"],
        proof["all_ready_results_non_authoritative"],
        proof["accepted_ref_unchanged_before_accept"],
        proof["explicit_accept_advanced_once"],
        proof["accepted_repitch_value"] == 64,
        proof["accepted_project_integrity"] == "PASS",
        proof["historical_m5_generic_note_import_still_blocked"],
        proof["compound_delta_blocked"],
        proof["other_track_delta_blocked"],
        proof["transport_delta_blocked"],
        proof["stale_source_blocked"],
        proof["hard_lock_blocked"],
        proof["ambiguous_identity_blocked"],
        proof["legacy_exact_identity_not_fabricated"],
        proof["external_project_mutation_authorized"] is False,
        proof["music_ir_mutation_authorized"] is False,
        proof["arbitrary_daw_reverse_mapping_validated"] is False,
        proof["real_external_daw_compatibility_validated"] is False,
    ]
    if not all(required):
        raise RuntimeError("M6-R4 canonical evidence proof failed")

    proof_out = write_canonical_json(root / "proof.json", proof)
    tracked = [
        source_out,
        baseline_out,
        receipt_out,
        export_out,
        historical_out,
        compound_returned_out,
        compound_out,
        other_track_out,
        transport_out,
        stale_out,
        lock_out,
        ambiguous_out,
        legacy_out,
        accepted_record_out,
        accepted_blueprint_out,
        integrity_out,
        proof_out,
        *returned_paths,
        *reconciliation_paths,
    ]
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M6-R4-Bounded-Interchange-Reconciliation-v0",
        "proof": proof,
        "hash_bindings": {
            "source_blueprint_sha256": blueprint_sha256(source),
            "source_export_artifact_sha256": first_export.receipt["export"]["artifact_sha256"],
            "source_normalized_sha256": first_export.receipt["export"]["normalized_sha256"],
            "identity_map_sha256": first_export.receipt["identity_map_sha256"],
            "accepted_blueprint_sha256": blueprint_sha256(accepted_blueprint),
        },
        "claim_boundary": [
            "MUSICA-origin DAWproject 1.0 source/export receipt only",
            "one exact-note part and one primitive external note delta at a time",
            "stable identity proven from exact source plus deterministic exported baseline",
            "DAW note order/index is not identity",
            "existing M6 source/lock/constraint authority reused unchanged",
            "explicit acceptance through existing M2 only",
            "historical M5-R3 arbitrary-note import remains blocked",
            "not arbitrary DAW reverse mapping",
            "not multi-note heuristic matching",
            "not real external DAW compatibility evidence",
            "not every-part/polyphonic reconciliation",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(tracked, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M6-R4 interchange reconciliation evidence")
    parser.add_argument("--out", required=True)
    parser.add_argument("--blueprint", default=str(DEFAULT_BLUEPRINT))
    parser.add_argument("--material", default=str(DEFAULT_MATERIAL))
    args = parser.parse_args()
    manifest = run_suite(args.out, blueprint_path=args.blueprint, material_path=args.material)
    print(canonical_json_bytes(manifest).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
