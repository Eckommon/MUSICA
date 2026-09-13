"""Generate canonical M6-R4 bounded interchange-reconciliation evidence."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

from lxml import etree

from .contracts import validate_contract
from .evidence import canonical_json_bytes
from .interchange_note_reconcile import (
    InterchangeNoteReconcileError,
    build_interchange_note_identity_bundle,
    reconcile_dawproject_note_edit,
)
from .note_edit import accept_note_edit_preview
from .project import create_project

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
MATERIAL_PATH = ROOT / "examples" / "note-material" / "valid" / "dark-electronic-explicit-timeline-v0.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _blueprint(*, locked: bool = False) -> dict[str, Any]:
    value = _load(BLUEPRINT_PATH)
    value["materials"]["melody"]["exact_timeline"] = _load(MATERIAL_PATH)
    if locked:
        value["materials"]["melody"]["exact_note_locks"] = [
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
                "reason": "M6-R4 evidence HARD-lock proof.",
            }
        ]
    validate_contract(value, "music-blueprint-v0.schema.json")
    return value


def _rewrite(artifact: bytes, mutate: Callable[[etree._Element, list[etree._Element]], None]) -> bytes:
    with zipfile.ZipFile(BytesIO(artifact), "r") as source:
        files = {name: source.read(name) for name in source.namelist()}
    root = etree.fromstring(files["project.xml"])
    motif = next(
        track
        for track in root.find("Structure").findall("Track")
        if "track_id=T-MOTIF" in (track.get("comment") or "")
    )
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


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _positive_artifacts(source: bytes) -> dict[str, bytes]:
    def attr(key: str, value: str) -> bytes:
        return _rewrite(source, lambda _root, notes: notes[0].set(key, value))

    def delete(_root: etree._Element, notes: list[etree._Element]) -> None:
        notes[0].getparent().remove(notes[0])

    def insert(_root: etree._Element, notes: list[etree._Element]) -> None:
        node = copy.deepcopy(notes[0])
        node.set("time", "3")
        node.set("duration", "0.5")
        node.set("key", "71")
        node.set("vel", f"{75 / 127:.6f}")
        notes[0].getparent().append(node)

    return {
        "MOVE": attr("time", "0.25"),
        "RESIZE": attr("duration", "0.5"),
        "REPITCH": attr("key", "64"),
        "SET_VELOCITY": attr("vel", f"{90 / 127:.6f}"),
        "DELETE": _rewrite(source, delete),
        "INSERT": _rewrite(source, insert),
    }


def generate_m6_r4_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    blueprint = _blueprint()
    bundle = build_interchange_note_identity_bundle(blueprint)
    _write_json(out / "source-blueprint.json", blueprint)
    _write_json(out / "identity-map.json", bundle.identity_map)
    _write_json(out / "baseline-normalized.json", bundle.baseline_normalized)
    (out / "source-export.dawproject").write_bytes(bundle.export.artifact)

    operations: dict[str, Any] = {}
    for name, artifact in _positive_artifacts(bundle.export.artifact).items():
        result = reconcile_dawproject_note_edit(blueprint, bundle, artifact)
        if result.candidate["operations"][0]["op"] != name:
            raise RuntimeError(f"M6-R4 operation mismatch: expected {name}")
        if not result.ready:
            raise RuntimeError(f"M6-R4 positive operation unexpectedly blocked: {name}")
        (out / "returned" / f"{name.lower()}.dawproject").parent.mkdir(parents=True, exist_ok=True)
        (out / "returned" / f"{name.lower()}.dawproject").write_bytes(artifact)
        _write_json(out / "candidates" / f"{name.lower()}.json", result.candidate)
        _write_json(out / "authority" / f"{name.lower()}.json", result.preview.authority_result)
        _write_json(out / "proofs" / f"{name.lower()}.json", result.proof)
        operations[name] = {
            "returned_artifact_sha256": _sha(artifact),
            "candidate_id": result.candidate["candidate_id"],
            "operation_id": result.candidate["operations"][0]["operation_id"],
            "authority_status": result.preview.authority_result["status"],
        }

    # Explicit acceptance proof through the existing M2 boundary.
    repitch_artifact = _positive_artifacts(bundle.export.artifact)["REPITCH"]
    repitch = reconcile_dawproject_note_edit(blueprint, bundle, repitch_artifact)
    with tempfile.TemporaryDirectory(prefix="musica-m6-r4-") as temp:
        project = create_project(Path(temp) / "project", blueprint)
        before_ref = project.head_revision_id()
        accepted_record = accept_note_edit_preview(project, repitch.preview)
        after_ref = project.head_revision_id()
        accepted = project.read_revision(after_ref)
        accepted_note = next(
            note
            for note in accepted["materials"]["melody"]["exact_timeline"]["notes"]
            if note["note_id"] == "N-MOTIF-001"
        )
        integrity = project.verify_integrity()
        acceptance = {
            "before_ref": before_ref,
            "after_ref": after_ref,
            "accepted_revision_id": accepted_record["revision_id"],
            "ref_advanced_exactly_to_commit": after_ref == accepted_record["revision_id"] and after_ref != before_ref,
            "accepted_pitch": accepted_note["pitch"],
            "accepted_pitch_expected": accepted_note["pitch"] == 64,
            "integrity": integrity,
        }
    _write_json(out / "m2-acceptance.json", acceptance)

    # HARD-lock proof: reconciliation succeeds, M6 authority remains final and blocks Preview.
    locked = _blueprint(locked=True)
    locked_bundle = build_interchange_note_identity_bundle(locked)
    locked_returned = _positive_artifacts(locked_bundle.export.artifact)["REPITCH"]
    locked_result = reconcile_dawproject_note_edit(locked, locked_bundle, locked_returned)
    hard_lock = locked_result.as_dict()
    _write_json(out / "negative" / "hard-lock.json", hard_lock)

    # Ambiguous multi-field external edit fails before candidate construction.
    def multi(_root: etree._Element, notes: list[etree._Element]) -> None:
        notes[0].set("time", "0.25")
        notes[0].set("key", "64")

    multi_artifact = _rewrite(bundle.export.artifact, multi)
    try:
        reconcile_dawproject_note_edit(blueprint, bundle, multi_artifact)
    except InterchangeNoteReconcileError as exc:
        ambiguity = {"blocked": True, "reason": str(exc), "artifact_sha256": _sha(multi_artifact)}
    else:
        raise RuntimeError("M6-R4 ambiguity evidence unexpectedly produced a candidate")
    _write_json(out / "negative" / "ambiguous-multi-field.json", ambiguity)

    stale = copy.deepcopy(blueprint)
    stale["project"]["revision_id"] = "rev-m6-r4-stale"
    try:
        reconcile_dawproject_note_edit(stale, bundle, bundle.export.artifact)
    except InterchangeNoteReconcileError as exc:
        stale_proof = {"blocked": True, "reason": str(exc)}
    else:
        raise RuntimeError("M6-R4 stale-source evidence unexpectedly reconciled")
    _write_json(out / "negative" / "stale-source.json", stale_proof)

    summary = {
        "milestone": "M6-R4",
        "policy": bundle.identity_map["policy"],
        "source_revision_id": bundle.identity_map["source_revision_id"],
        "source_blueprint_sha256": bundle.identity_map["source_blueprint_sha256"],
        "source_exact_timeline_sha256": bundle.identity_map["source_exact_timeline_sha256"],
        "source_music_ir_sha256": bundle.identity_map["source_music_ir_sha256"],
        "source_export_artifact_sha256": bundle.identity_map["export_artifact_sha256"],
        "identity_map_sha256": bundle.identity_map["identity_map_sha256"],
        "baseline_normalized_sha256": bundle.identity_map["baseline_normalized_sha256"],
        "all_six_primitives_reconciled": set(operations) == {
            "MOVE", "RESIZE", "REPITCH", "SET_VELOCITY", "DELETE", "INSERT"
        },
        "operations": operations,
        "array_index_used_as_identity": False,
        "heuristic_nearest_note_matching": False,
        "external_state_canonical_authority": False,
        "explicit_accept_required": True,
        "m2_acceptance_proven": acceptance["ref_advanced_exactly_to_commit"] and acceptance["accepted_pitch_expected"],
        "hard_lock_blocked": locked_result.preview.authority_result["status"] == "BLOCKED",
        "hard_lock_preview_generation_allowed": locked_result.preview.authority_result["preview_generation_allowed"],
        "ambiguity_blocked": ambiguity["blocked"],
        "stale_source_blocked": stale_proof["blocked"],
    }
    _write_json(out / "proof.json", summary)

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
        "milestone": "M6-R4",
        "artifact_name": "musica-m6-r4-interchange-note-reconciliation",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": summary, "manifest": manifest}


if __name__ == "__main__":
    import os

    destination = os.environ.get(
        "MUSICA_M6_R4_EVIDENCE_OUT", "artifacts/m6-r4-interchange-note-reconciliation"
    )
    generate_m6_r4_evidence(destination)
