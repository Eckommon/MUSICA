"""M6-R4 bounded DAWproject -> exact-note reconciliation.

This module does not grant DAWproject state authority.  It binds one MUSICA-origin
export to the accepted exact-note Blueprint, compares a returned artifact against
that exact normalized baseline, and emits an existing M6 NoteEditCandidate only
when one primitive note delta is uniquely provable.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any

from .compiler import PPQ, compile_blueprint
from .contracts import ContractError, exact_timeline, validate_contract
from .dawproject import DawProjectExport, InterchangeError, export_dawproject, inspect_dawproject
from .evidence import canonical_json_bytes
from .note_edit import NoteEditPreview, blueprint_sha256, build_note_edit_preview

IDENTITY_MAP_VERSION = "0"
RECONCILIATION_POLICY = "musica-m6-r4-single-primitive-v0"


class InterchangeNoteReconcileError(ContractError):
    """Raised when external note correspondence cannot be proven safely."""


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _event_signature(note: dict[str, Any]) -> tuple[int, int, int, int, int]:
    return (
        int(note["tick"]),
        int(note["duration"]),
        int(note["note"]),
        int(note["velocity"]),
        int(note["channel"]),
    )


def _exact_signature(note: dict[str, Any], channel: int) -> tuple[int, int, int, int, int]:
    return (
        round(float(note["start_beat"]) * PPQ),
        round(float(note["duration_beats"]) * PPQ),
        int(note["pitch"]),
        int(note["velocity"]),
        int(channel),
    )


def _motif_track(normalized: dict[str, Any]) -> dict[str, Any]:
    matches = [track for track in normalized["tracks"] if track.get("track_id") == "T-MOTIF"]
    if len(matches) != 1:
        raise InterchangeNoteReconcileError("M6-R4 requires exactly one traceable T-MOTIF track")
    track = matches[0]
    if not track.get("part_id"):
        raise InterchangeNoteReconcileError("M6-R4 requires traceable motif part_id")
    return track


def _find_section_id(blueprint: dict[str, Any], start_beat: float) -> str | None:
    bpm = float(blueprint["musical_context"]["tempo"]["bpm"])
    seconds = start_beat * 60.0 / bpm
    for section in blueprint["form"]["sections"]:
        if float(section["start"]) <= seconds < float(section["end"]):
            return str(section["section_id"])
    return None


@dataclass(frozen=True)
class InterchangeNoteIdentityBundle:
    """Hash-bound identity evidence for one exact MUSICA DAWproject export."""

    export: DawProjectExport
    identity_map: dict[str, Any]
    baseline_normalized: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "identity_map": copy.deepcopy(self.identity_map),
            "baseline_normalized": copy.deepcopy(self.baseline_normalized),
        }


@dataclass(frozen=True)
class InterchangeNoteReconciliation:
    candidate: dict[str, Any]
    preview: NoteEditPreview
    proof: dict[str, Any]

    @property
    def ready(self) -> bool:
        return self.preview.ready

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate": copy.deepcopy(self.candidate),
            "preview": self.preview.as_dict(),
            "proof": copy.deepcopy(self.proof),
        }


def build_interchange_note_identity_bundle(blueprint: dict[str, Any]) -> InterchangeNoteIdentityBundle:
    """Create a source-bound export baseline and stable-note identity map.

    v0 deliberately refuses duplicate lowered note signatures because DAWproject 1.0
    Note has no stable-ID field.  Array position is never accepted as identity.
    """

    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    timeline = exact_timeline(blueprint)
    if timeline is None:
        raise InterchangeNoteReconcileError("M6-R4 requires canonical exact-note material")

    ir = compile_blueprint(blueprint)
    motif_ir = [track for track in ir["tracks"] if track["track_id"] == "T-MOTIF"]
    if len(motif_ir) != 1:
        raise InterchangeNoteReconcileError("M6-R4 requires exactly one T-MOTIF Music-IR track")
    channel = int(motif_ir[0]["channel"])

    export = export_dawproject(blueprint, ir)
    baseline_inspection = inspect_dawproject(export.artifact)
    baseline = baseline_inspection["normalized"]
    motif = _motif_track(baseline)

    exact_notes = list(timeline["notes"])
    if len(exact_notes) != len(motif["notes"]):
        raise InterchangeNoteReconcileError("exact-note material does not map one-to-one to exported motif notes")

    signature_to_note: dict[tuple[int, int, int, int, int], dict[str, Any]] = {}
    for note in exact_notes:
        signature = _exact_signature(note, channel)
        if signature in signature_to_note:
            raise InterchangeNoteReconcileError(
                "ambiguous exact-note identity: duplicate lowered note signature is unsupported in M6-R4 v0"
            )
        signature_to_note[signature] = note

    exported_signatures = [_event_signature(note) for note in motif["notes"]]
    if len(exported_signatures) != len(set(exported_signatures)):
        raise InterchangeNoteReconcileError(
            "ambiguous export identity: duplicate normalized note signature is unsupported in M6-R4 v0"
        )
    if set(exported_signatures) != set(signature_to_note):
        raise InterchangeNoteReconcileError("exported motif notes are not an exact lowering of canonical exact notes")

    records = []
    for signature in sorted(signature_to_note):
        note = signature_to_note[signature]
        records.append(
            {
                "note_id": str(note["note_id"]),
                "part_id": str(note["part_id"]),
                "section_id": note.get("section_id"),
                "baseline_signature": {
                    "tick": signature[0],
                    "duration": signature[1],
                    "note": signature[2],
                    "velocity": signature[3],
                    "channel": signature[4],
                },
            }
        )

    identity_map = {
        "identity_map_version": IDENTITY_MAP_VERSION,
        "policy": RECONCILIATION_POLICY,
        "project_id": blueprint["project"]["project_id"],
        "source_revision_id": blueprint["project"]["revision_id"],
        "source_blueprint_sha256": blueprint_sha256(blueprint),
        "source_exact_timeline_sha256": _sha256_json(timeline),
        "source_music_ir_sha256": _sha256_json(ir),
        "export_artifact_sha256": export.manifest["artifact_sha256"],
        "baseline_normalized_sha256": _sha256_json(baseline),
        "track_id": "T-MOTIF",
        "part_id": str(motif["part_id"]),
        "records": records,
    }
    identity_map["identity_map_sha256"] = _sha256_json(identity_map)
    return InterchangeNoteIdentityBundle(export=export, identity_map=identity_map, baseline_normalized=baseline)


def _verify_bundle(blueprint: dict[str, Any], bundle: InterchangeNoteIdentityBundle) -> None:
    timeline = exact_timeline(blueprint)
    if timeline is None:
        raise InterchangeNoteReconcileError("current source no longer has exact-note material")
    identity = bundle.identity_map
    checks = {
        "project_id": blueprint["project"]["project_id"],
        "source_revision_id": blueprint["project"]["revision_id"],
        "source_blueprint_sha256": blueprint_sha256(blueprint),
        "source_exact_timeline_sha256": _sha256_json(timeline),
        "source_music_ir_sha256": _sha256_json(compile_blueprint(blueprint)),
        "baseline_normalized_sha256": _sha256_json(bundle.baseline_normalized),
        "export_artifact_sha256": hashlib.sha256(bundle.export.artifact).hexdigest(),
    }
    for key, observed in checks.items():
        if identity.get(key) != observed:
            raise InterchangeNoteReconcileError(f"stale or tampered M6-R4 identity bundle: {key} mismatch")

    regenerated = export_dawproject(blueprint)
    if regenerated.manifest["artifact_sha256"] != identity["export_artifact_sha256"]:
        raise InterchangeNoteReconcileError("source export is no longer deterministic/bound to identity bundle")


def _unchanged_non_motif_tracks(baseline: dict[str, Any], returned: dict[str, Any]) -> bool:
    def others(value: dict[str, Any]) -> list[dict[str, Any]]:
        return [track for track in value["tracks"] if track.get("track_id") != "T-MOTIF"]

    return others(baseline) == others(returned)


def _single_primitive_operation(
    blueprint: dict[str, Any],
    bundle: InterchangeNoteIdentityBundle,
    returned_normalized: dict[str, Any],
    returned_artifact_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    baseline = bundle.baseline_normalized
    if returned_normalized["transport"] != baseline["transport"]:
        raise InterchangeNoteReconcileError("M6-R4 v0 does not reconcile transport edits with note edits")
    if not _unchanged_non_motif_tracks(baseline, returned_normalized):
        raise InterchangeNoteReconcileError("M6-R4 v0 requires all non-motif tracks to remain unchanged")

    base_track = _motif_track(baseline)
    returned_track = _motif_track(returned_normalized)
    if returned_track["part_id"] != base_track["part_id"]:
        raise InterchangeNoteReconcileError("returned motif part mapping changed")

    base_by_sig = {_event_signature(note): note for note in base_track["notes"]}
    ret_by_sig = {_event_signature(note): note for note in returned_track["notes"]}
    if len(base_by_sig) != len(base_track["notes"]) or len(ret_by_sig) != len(returned_track["notes"]):
        raise InterchangeNoteReconcileError("ambiguous duplicate note signatures are unsupported")

    common = set(base_by_sig) & set(ret_by_sig)
    removed = sorted(set(base_by_sig) - common)
    added = sorted(set(ret_by_sig) - common)
    records = {
        tuple(
            int(record["baseline_signature"][field])
            for field in ("tick", "duration", "note", "velocity", "channel")
        ): record
        for record in bundle.identity_map["records"]
    }

    operation: dict[str, Any]
    interpretation: str
    if len(removed) == 1 and len(added) == 1:
        before = removed[0]
        after = added[0]
        record = records.get(before)
        if record is None:
            raise InterchangeNoteReconcileError("changed source note lacks stable identity mapping")
        differing = [index for index in range(5) if before[index] != after[index]]
        if len(differing) != 1 or differing[0] == 4:
            raise InterchangeNoteReconcileError("external note change is not one uniquely representable M6 primitive")
        target = {"note_id": record["note_id"], "part_id": record["part_id"]}
        field = differing[0]
        if field == 0:
            operation = {"op": "MOVE", "target": target, "start_beat": after[0] / PPQ}
        elif field == 1:
            operation = {"op": "RESIZE", "target": target, "duration_beats": after[1] / PPQ}
        elif field == 2:
            operation = {"op": "REPITCH", "target": target, "pitch": after[2]}
        else:
            operation = {"op": "SET_VELOCITY", "target": target, "velocity": after[3]}
        interpretation = operation["op"]
    elif len(removed) == 1 and not added:
        record = records.get(removed[0])
        if record is None:
            raise InterchangeNoteReconcileError("deleted source note lacks stable identity mapping")
        operation = {
            "op": "DELETE",
            "target": {"note_id": record["note_id"], "part_id": record["part_id"]},
        }
        interpretation = "DELETE"
    elif not removed and len(added) == 1:
        inserted = added[0]
        start_beat = inserted[0] / PPQ
        section_id = _find_section_id(blueprint, start_beat)
        if section_id is None:
            raise InterchangeNoteReconcileError("inserted note is outside a declared section")
        seed = {
            "source_revision_id": blueprint["project"]["revision_id"],
            "returned_artifact_sha256": returned_artifact_sha256,
            "signature": inserted,
        }
        note_id = f"N-IMPORT-{_sha256_json(seed)[:16]}"
        operation = {
            "op": "INSERT",
            "note": {
                "note_id": note_id,
                "part_id": str(base_track["part_id"]),
                "section_id": section_id,
                "start_beat": start_beat,
                "duration_beats": inserted[1] / PPQ,
                "pitch": inserted[2],
                "velocity": inserted[3],
            },
        }
        interpretation = "INSERT"
    else:
        raise InterchangeNoteReconcileError(
            "external note delta is ambiguous, empty, or contains more than one primitive change"
        )

    operation_seed = {
        "identity_map_sha256": bundle.identity_map["identity_map_sha256"],
        "returned_artifact_sha256": returned_artifact_sha256,
        "operation": operation,
    }
    operation["operation_id"] = f"OP-M6R4-{_sha256_json(operation_seed)[:16]}"
    proof = {
        "policy": RECONCILIATION_POLICY,
        "identity_map_sha256": bundle.identity_map["identity_map_sha256"],
        "baseline_normalized_sha256": bundle.identity_map["baseline_normalized_sha256"],
        "returned_normalized_sha256": _sha256_json(returned_normalized),
        "returned_artifact_sha256": returned_artifact_sha256,
        "common_note_count": len(common),
        "removed_signature_count": len(removed),
        "added_signature_count": len(added),
        "interpretation": interpretation,
        "array_index_used_as_identity": False,
        "heuristic_nearest_note_matching": False,
        "external_state_canonical_authority": False,
    }
    return operation, proof


def reconcile_dawproject_note_edit(
    blueprint: dict[str, Any],
    bundle: InterchangeNoteIdentityBundle,
    returned_artifact: bytes,
) -> InterchangeNoteReconciliation:
    """Translate one provable returned DAWproject note delta through existing M6 authority."""

    _verify_bundle(blueprint, bundle)
    returned_sha = hashlib.sha256(returned_artifact).hexdigest()
    try:
        returned = inspect_dawproject(returned_artifact)["normalized"]
    except InterchangeError as exc:
        raise InterchangeNoteReconcileError(str(exc)) from exc

    operation, proof = _single_primitive_operation(
        blueprint,
        bundle,
        returned,
        returned_sha,
    )
    candidate_seed = {
        "source_revision_id": blueprint["project"]["revision_id"],
        "identity_map_sha256": bundle.identity_map["identity_map_sha256"],
        "returned_artifact_sha256": returned_sha,
        "operation": operation,
    }
    candidate = {
        "candidate_version": "0",
        "candidate_id": f"NEC-M6R4-{_sha256_json(candidate_seed)[:16]}",
        "authority_target": "blueprint_exact_note_material",
        "source": {
            "project_id": blueprint["project"]["project_id"],
            "revision_id": blueprint["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(blueprint),
        },
        "actor": {"kind": "import", "actor_id": "dawproject-m6-r4"},
        "reason": (
            "Reconcile one source-bound representable DAWproject exact-note delta "
            f"from {returned_sha}."
        ),
        "operations": [operation],
        "preview_only": True,
    }
    validate_contract(candidate, "note-edit-candidate-v0.schema.json")
    preview = build_note_edit_preview(blueprint, candidate)
    proof.update(
        {
            "candidate_id": candidate["candidate_id"],
            "authority_status": preview.authority_result["status"],
            "preview_generation_allowed": preview.authority_result["preview_generation_allowed"],
            "explicit_accept_required": preview.authority_result["explicit_accept_required"],
            "project_mutation_authorized": preview.authority_result["project_mutation_authorized"],
            "music_ir_mutation_authorized": preview.authority_result["music_ir_mutation_authorized"],
        }
    )
    return InterchangeNoteReconciliation(candidate=candidate, preview=preview, proof=proof)
