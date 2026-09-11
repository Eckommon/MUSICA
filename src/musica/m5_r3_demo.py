"""Generate durable M5-R3 bounded DAWproject interchange evidence."""

from __future__ import annotations

import argparse
import io
import json
import shutil
import zipfile
from pathlib import Path

from lxml import etree

from .compiler import compile_blueprint
from .dawproject import (
    EXPORTER_ID,
    EXPORTER_VERSION,
    FORMAT_VERSION,
    IMPORTER_ID,
    IMPORTER_VERSION,
    METADATA_XSD,
    NORMALIZATION_POLICY,
    PROJECT_XSD,
    UPSTREAM_COMMIT,
    UPSTREAM_LICENSE,
    UPSTREAM_REPOSITORY,
    accept_dawproject_candidate,
    export_dawproject,
    import_dawproject_candidate,
    inspect_dawproject,
)
from .evidence import artifact_record, sha256_file, write_canonical_json
from .project import create_project


def _rewrite(
    artifact: bytes,
    *,
    bpm: float | None = None,
    meter: str | None = None,
    note_delta: int = 0,
) -> bytes:
    with zipfile.ZipFile(io.BytesIO(artifact), "r") as archive:
        files = {info.filename: archive.read(info) for info in archive.infolist() if not info.is_dir()}
    root = etree.fromstring(files["project.xml"])
    if bpm is not None:
        root.find("./Transport/Tempo").set("value", str(bpm))
    if meter is not None:
        numerator, denominator = meter.split("/", 1)
        time_signature = root.find("./Transport/TimeSignature")
        time_signature.set("numerator", numerator)
        time_signature.set("denominator", denominator)
    if note_delta:
        note = root.find(".//Note")
        note.set("key", str(int(note.get("key")) + note_delta))
    files["project.xml"] = etree.tostring(
        root,
        encoding="UTF-8",
        xml_declaration=True,
        standalone=True,
        pretty_print=False,
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


def run(blueprint_path: Path, out: Path) -> dict:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    project = create_project(out / "project", blueprint)
    source_revision = project.head_revision_id()
    source_blueprint = project.read_revision(source_revision)
    source_ir = compile_blueprint(source_blueprint)

    first = export_dawproject(source_blueprint, source_ir)
    second = export_dawproject(source_blueprint, source_ir)
    if first.artifact != second.artifact:
        raise RuntimeError("deterministic DAWproject export proof failed")

    (out / "export-a.dawproject").write_bytes(first.artifact)
    (out / "export-b.dawproject").write_bytes(second.artifact)
    write_canonical_json(out / "export-manifest.json", first.manifest)
    write_canonical_json(out / "export-loss-report.json", first.loss_report)

    source_head_after_export = project.head_revision_id()
    original_inspection = inspect_dawproject(first.artifact)
    original_candidate = import_dawproject_candidate(
        project,
        first.artifact,
        expected_artifact_sha256=first.manifest["artifact_sha256"],
    )
    write_canonical_json(out / "candidate-original.json", original_candidate)

    tempo_artifact = _rewrite(first.artifact, bpm=130.0)
    (out / "external-tempo-edit.dawproject").write_bytes(tempo_artifact)
    tempo_candidate = import_dawproject_candidate(project, tempo_artifact)
    write_canonical_json(out / "candidate-tempo-blocked.json", tempo_candidate)

    note_artifact = _rewrite(first.artifact, note_delta=1)
    (out / "external-note-edit.dawproject").write_bytes(note_artifact)
    note_candidate = import_dawproject_candidate(project, note_artifact)
    write_canonical_json(out / "candidate-note-blocked.json", note_candidate)

    meter_artifact = _rewrite(first.artifact, meter="3/4")
    (out / "external-meter-edit.dawproject").write_bytes(meter_artifact)
    meter_candidate = import_dawproject_candidate(project, meter_artifact)
    write_canonical_json(out / "candidate-meter-ready.json", meter_candidate)

    head_before_accept = project.head_revision_id()
    accepted = accept_dawproject_candidate(project, meter_candidate)
    write_canonical_json(out / "accepted-import.json", accepted)
    head_after_accept = project.head_revision_id()
    accepted_blueprint = project.read_revision(head_after_accept)
    write_canonical_json(out / "accepted-blueprint.json", accepted_blueprint)
    integrity = project.verify_integrity()
    write_canonical_json(out / "project-integrity.json", integrity)

    files = sorted(path for path in out.iterdir() if path.is_file())
    evidence = {
        "evidence_version": "0",
        "milestone": "M5-R3",
        "verdict": "PASS_BOUNDED",
        "format": {
            "name": "DAWproject",
            "version": FORMAT_VERSION,
            "upstream_repository": UPSTREAM_REPOSITORY,
            "upstream_commit": UPSTREAM_COMMIT,
            "upstream_license": UPSTREAM_LICENSE,
            "project_xsd_sha256": sha256_file(PROJECT_XSD),
            "metadata_xsd_sha256": sha256_file(METADATA_XSD),
        },
        "adapters": {
            "exporter_id": EXPORTER_ID,
            "exporter_version": EXPORTER_VERSION,
            "importer_id": IMPORTER_ID,
            "importer_version": IMPORTER_VERSION,
            "normalization_policy": NORMALIZATION_POLICY,
        },
        "source": {
            "revision_id": source_revision,
            "blueprint_sha256": first.manifest["source_blueprint_sha256"],
            "music_ir_sha256": first.manifest["source_music_ir_sha256"],
        },
        "deterministic_export": {
            "artifact_sha256": first.manifest["artifact_sha256"],
            "project_xml_sha256": first.manifest["project_xml_sha256"],
            "metadata_xml_sha256": first.manifest["metadata_xml_sha256"],
            "export_a_equals_export_b": first.artifact == second.artifact,
            "head_unchanged_after_export": source_head_after_export == source_revision,
        },
        "roundtrip": {
            "original_candidate_status": original_candidate["status"],
            "original_validation_status": original_candidate["validation_status"],
            "original_normalized_sha256": original_candidate["normalized_candidate_sha256"],
            "original_diff_sha256": original_candidate["diff_sha256"],
            "original_loss_report_sha256": original_candidate["loss_report_sha256"],
            "bounded_track_count": len(original_inspection["normalized"]["tracks"]),
        },
        "authority_negatives": {
            "tempo_edit_validation": tempo_candidate["validation_status"],
            "tempo_edit_blocked_by_hard_lock": any(
                item["rule_id"] == "L-TEMPO" and item["status"] == "BLOCKED"
                for item in tempo_candidate["conflicts"]
            ),
            "note_edit_validation": note_candidate["validation_status"],
            "note_edit_reverse_mapping_blocked": any(
                item["rule_id"] == "blueprint-v0-note-reverse-mapping"
                for item in note_candidate["conflicts"]
            ),
            "head_unchanged_before_explicit_accept": head_before_accept == source_revision,
        },
        "explicit_accept": {
            "meter_candidate_status": meter_candidate["status"],
            "meter_candidate_validation": meter_candidate["validation_status"],
            "accepted_revision_id": accepted["accepted_revision_id"],
            "head_advanced_exactly_to_accepted_revision": head_after_accept == accepted["accepted_revision_id"],
            "accepted_meter": accepted_blueprint["musical_context"]["meter"],
            "accepted_actor": accepted_blueprint["provenance"]["actor"],
            "source_artifact_sha256": accepted["source_artifact_sha256"],
            "project_integrity": integrity["status"],
        },
        "claim_boundary": {
            "external_app_smoke": "NOT_VALIDATED",
            "arbitrary_note_edit_to_blueprint": "UNSUPPORTED_BLOCKING",
            "plugin_device_fidelity": "NOT_VALIDATED",
            "arbitrary_automation_mixer_fidelity": "NOT_VALIDATED",
            "real_daw_compatibility_tested": False,
        },
        "artifacts": [artifact_record(path, out) for path in files],
    }

    required = [
        evidence["deterministic_export"]["export_a_equals_export_b"],
        evidence["deterministic_export"]["head_unchanged_after_export"],
        evidence["roundtrip"]["original_candidate_status"] == "PENDING",
        evidence["roundtrip"]["original_validation_status"] == "PASS",
        evidence["authority_negatives"]["tempo_edit_validation"] == "BLOCKED",
        evidence["authority_negatives"]["tempo_edit_blocked_by_hard_lock"],
        evidence["authority_negatives"]["note_edit_validation"] == "BLOCKED",
        evidence["authority_negatives"]["note_edit_reverse_mapping_blocked"],
        evidence["authority_negatives"]["head_unchanged_before_explicit_accept"],
        evidence["explicit_accept"]["meter_candidate_validation"] == "PASS",
        evidence["explicit_accept"]["head_advanced_exactly_to_accepted_revision"],
        evidence["explicit_accept"]["accepted_meter"] == "3/4",
        evidence["explicit_accept"]["accepted_actor"] == "import",
        evidence["explicit_accept"]["project_integrity"] == "PASS",
    ]
    if not all(required):
        raise RuntimeError("M5-R3 evidence gate failed")

    write_canonical_json(out / "evidence.json", evidence)
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--blueprint",
        type=Path,
        default=Path("examples/blueprints/valid/dark-electronic-20s-r1.json"),
    )
    parser.add_argument("--out", type=Path, default=Path("artifacts/m5-r3-dawproject"))
    args = parser.parse_args()
    evidence = run(args.blueprint, args.out)
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
