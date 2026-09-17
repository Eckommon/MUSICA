"""MUSICA M6-R4 bounded DAWproject exact-note reconciliation.

This module is intentionally additive to M5-R3. The historical generic
``import_dawproject_candidate`` path continues to block arbitrary external note
edits. M6-R4 only reconciles one MUSICA-origin, source-bound DAWproject export
when a single exact-note primitive can be proven without trusting DAW note order
or granting external state canonical authority.
"""

from __future__ import annotations

import copy
import hashlib
from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable

from .compiler import PPQ, compile_blueprint
from .contracts import ContractError, exact_timeline, validate_contract
from .dawproject import NORMALIZATION_POLICY, export_dawproject, inspect_dawproject
from .evidence import canonical_json_bytes
from .note_edit import (
    NoteEditPreview,
    accept_note_edit_preview,
    blueprint_sha256,
    build_note_edit_preview,
)


class ReconciliationError(ContractError):
    """Raised when a source-bound interchange reconciliation cannot be proven safely."""


SignatureTuple = tuple[int, int, int, int, int]


@dataclass(frozen=True)
class DawProjectNoteExport:
    """Deterministic DAWproject export plus its non-authoritative identity receipt."""

    artifact: bytes
    manifest: dict[str, Any]
    loss_report: dict[str, Any]
    receipt: dict[str, Any]


@dataclass(frozen=True)
class DawProjectNoteReconciliation:
    """One bounded reconciliation result.

    ``READY_FOR_PREVIEW`` means only that the generated typed M6 candidate passed
    the existing M6 authority engine. It does not authorize acceptance.
    """

    status: str
    returned_artifact_sha256: str
    returned_normalized_sha256: str
    operation: dict[str, Any] | None
    candidate: dict[str, Any] | None
    preview: NoteEditPreview | None
    conflicts: list[dict[str, Any]]

    @property
    def ready(self) -> bool:
        return self.status == "READY_FOR_PREVIEW" and self.preview is not None and self.preview.ready

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "returned_artifact_sha256": self.returned_artifact_sha256,
            "returned_normalized_sha256": self.returned_normalized_sha256,
            "operation": copy.deepcopy(self.operation),
            "candidate": copy.deepcopy(self.candidate),
            "preview": None if self.preview is None else self.preview.as_dict(),
            "conflicts": copy.deepcopy(self.conflicts),
            "external_project_mutation_authorized": False,
            "music_ir_mutation_authorized": False,
            "explicit_accept_required": True,
        }


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_hash(value: Any) -> str:
    return _sha256(canonical_json_bytes(value))


def _signature_dict(signature: SignatureTuple) -> dict[str, int]:
    tick, duration, pitch, velocity, channel = signature
    return {
        "tick": tick,
        "duration": duration,
        "pitch": pitch,
        "velocity": velocity,
        "channel": channel,
    }


def _signature_tuple(note: dict[str, Any]) -> SignatureTuple:
    return (
        int(note["tick"]),
        int(note["duration"]),
        int(note["note"] if "note" in note else note["pitch"]),
        int(note["velocity"]),
        int(note["channel"]),
    )


def _exact_note_signature(note: dict[str, Any], *, channel: int) -> SignatureTuple:
    return (
        round(float(note["start_beat"]) * PPQ),
        round(float(note["duration_beats"]) * PPQ),
        int(note["pitch"]),
        int(note["velocity"]),
        int(channel),
    )


def _single_exact_part(blueprint: dict[str, Any]) -> tuple[dict[str, Any], str]:
    timeline = exact_timeline(blueprint)
    if timeline is None:
        raise ReconciliationError("M6-R4 requires an accepted melody.exact_timeline source")
    notes = list(timeline["notes"])
    if notes:
        part_ids = {str(note["part_id"]) for note in notes}
        if len(part_ids) != 1:
            raise ReconciliationError("M6-R4 v0 supports one exact-note part only")
        return timeline, next(iter(part_ids))

    # Empty exact timelines are still canonical exact-note material. M6 v0 is
    # bounded to motif/lead, so derive the single supported part from Blueprint roles.
    supported = [
        str(part["part_id"])
        for part in blueprint["roles"]["instruments_or_parts"]
        if str(part.get("role")) in {"motif", "lead"}
    ]
    if len(supported) != 1:
        raise ReconciliationError("cannot identify one exact-note motif/lead part")
    return timeline, supported[0]


def _source_track(blueprint: dict[str, Any], *, part_id: str) -> dict[str, Any]:
    ir = compile_blueprint(blueprint)
    tracks = [track for track in ir["tracks"] if str(track["part_id"]) == part_id]
    if len(tracks) != 1:
        raise ReconciliationError(f"cannot identify one deterministic Music-IR track for part {part_id}")
    return tracks[0]


def _normalized_track(normalized: dict[str, Any], *, track_id: str, part_id: str) -> dict[str, Any]:
    tracks = [
        track
        for track in normalized["tracks"]
        if str(track.get("track_id")) == track_id and str(track.get("part_id")) == part_id
    ]
    if len(tracks) != 1:
        raise ReconciliationError(f"cannot identify one traceable DAWproject track for {track_id}/{part_id}")
    return tracks[0]


def export_dawproject_note_roundtrip(blueprint: dict[str, Any]) -> DawProjectNoteExport:
    """Create a deterministic MUSICA-origin DAWproject export and exact-note receipt.

    Receipt construction fails closed when two accepted exact notes collapse to the
    same interchange signature, because a later external edit could not be assigned
    to one stable MUSICA note identity without guessing.
    """

    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    timeline, part_id = _single_exact_part(blueprint)
    source_track = _source_track(blueprint, part_id=part_id)
    track_id = str(source_track["track_id"])
    channel = int(source_track["channel"])

    exported = export_dawproject(blueprint)
    inspected = inspect_dawproject(exported.artifact)
    normalized = inspected["normalized"]
    normalized_track = _normalized_track(normalized, track_id=track_id, part_id=part_id)

    source_pairs = [
        (str(note["note_id"]), _exact_note_signature(note, channel=channel))
        for note in timeline["notes"]
    ]
    source_counter = Counter(signature for _, signature in source_pairs)
    duplicates = [signature for signature, count in source_counter.items() if count > 1]
    if duplicates:
        raise ReconciliationError(
            "M6-R4 cannot create an identity receipt when accepted exact notes share one interchange signature"
        )

    exported_signatures = Counter(_signature_tuple(note) for note in normalized_track["notes"])
    if exported_signatures != source_counter:
        raise ReconciliationError(
            "deterministic DAWproject export does not exactly match accepted exact-note material for the scoped track"
        )

    identity_map = [
        {
            "note_id": note_id,
            "part_id": part_id,
            "track_id": track_id,
            "signature": _signature_dict(signature),
        }
        for note_id, signature in sorted(source_pairs, key=lambda item: item[0])
    ]
    receipt = {
        "receipt_version": "0",
        "source": {
            "project_id": str(blueprint["project"]["project_id"]),
            "revision_id": str(blueprint["project"]["revision_id"]),
            "blueprint_sha256": blueprint_sha256(blueprint),
        },
        "export": {
            "format": "DAWproject",
            "format_version": "1.0",
            "artifact_sha256": str(exported.manifest["artifact_sha256"]),
            "normalized_sha256": _canonical_hash(normalized),
            "normalization_policy": NORMALIZATION_POLICY,
        },
        "scope": {
            "track_id": track_id,
            "part_id": part_id,
            "channel": channel,
            "single_primitive_only": True,
        },
        "note_identity_map": identity_map,
        "identity_map_sha256": _canonical_hash(identity_map),
    }
    validate_contract(receipt, "interchange-note-receipt-v0.schema.json")
    return DawProjectNoteExport(
        artifact=exported.artifact,
        manifest=copy.deepcopy(exported.manifest),
        loss_report=copy.deepcopy(exported.loss_report),
        receipt=receipt,
    )


def _conflict(code: str, reason: str) -> dict[str, Any]:
    return {"code": code, "status": "BLOCKED", "reason": reason}


def _blocked(
    *,
    returned_artifact_sha256: str,
    returned_normalized_sha256: str,
    code: str,
    reason: str,
    operation: dict[str, Any] | None = None,
    candidate: dict[str, Any] | None = None,
    preview: NoteEditPreview | None = None,
    conflicts: list[dict[str, Any]] | None = None,
) -> DawProjectNoteReconciliation:
    return DawProjectNoteReconciliation(
        status="BLOCKED",
        returned_artifact_sha256=returned_artifact_sha256,
        returned_normalized_sha256=returned_normalized_sha256,
        operation=operation,
        candidate=candidate,
        preview=preview,
        conflicts=copy.deepcopy(conflicts) if conflicts is not None else [_conflict(code, reason)],
    )


def _track_key(track: dict[str, Any]) -> tuple[str | None, str | None]:
    track_id = track.get("track_id")
    part_id = track.get("part_id")
    return (
        None if track_id is None else str(track_id),
        None if part_id is None else str(part_id),
    )


def _signature_counter(notes: Iterable[dict[str, Any]]) -> Counter[SignatureTuple]:
    return Counter(_signature_tuple(note) for note in notes)


def _identity_by_signature(receipt: dict[str, Any]) -> dict[SignatureTuple, dict[str, Any]]:
    mapping: dict[SignatureTuple, dict[str, Any]] = {}
    for item in receipt["note_identity_map"]:
        signature = item["signature"]
        key = (
            int(signature["tick"]),
            int(signature["duration"]),
            int(signature["pitch"]),
            int(signature["velocity"]),
            int(signature["channel"]),
        )
        if key in mapping:
            raise ReconciliationError("receipt contains an ambiguous duplicate note signature")
        mapping[key] = item
    if _canonical_hash(receipt["note_identity_map"]) != receipt["identity_map_sha256"]:
        raise ReconciliationError("receipt identity-map hash mismatch")
    return mapping


def _section_for_insert(blueprint: dict[str, Any], *, start_beat: float, duration_beats: float) -> str:
    bpm = float(blueprint["musical_context"]["tempo"]["bpm"])
    start_seconds = start_beat * 60.0 / bpm
    end_seconds = (start_beat + duration_beats) * 60.0 / bpm
    matches = [
        str(section["section_id"])
        for section in blueprint["form"]["sections"]
        if float(section["start"]) <= start_seconds + 1e-9
        and end_seconds <= float(section["end"]) + 1e-9
    ]
    if len(matches) != 1:
        raise ReconciliationError("inserted note does not fit wholly inside one declared section")
    return matches[0]


def _candidate(
    source_blueprint: dict[str, Any],
    receipt: dict[str, Any],
    returned_artifact_sha256: str,
    operation: dict[str, Any],
) -> dict[str, Any]:
    seed = {
        "source": receipt["source"],
        "returned_artifact_sha256": returned_artifact_sha256,
        "operation": operation,
    }
    digest = _canonical_hash(seed)
    candidate = {
        "candidate_version": "0",
        "candidate_id": f"NEC-M6-R4-{digest[:20]}",
        "authority_target": "blueprint_exact_note_material",
        "source": copy.deepcopy(receipt["source"]),
        "actor": {"kind": "import", "actor_id": "dawproject-reconciliation-v0"},
        "reason": (
            "Reconcile one source-bound representable DAWproject exact-note delta "
            f"from artifact {returned_artifact_sha256}."
        ),
        "operations": [copy.deepcopy(operation)],
        "preview_only": True,
    }
    if candidate["source"]["blueprint_sha256"] != blueprint_sha256(source_blueprint):
        raise ReconciliationError("receipt source Blueprint hash does not match its source revision")
    validate_contract(candidate, "note-edit-candidate-v0.schema.json")
    return candidate


def _operation_from_delta(
    *,
    source_blueprint: dict[str, Any],
    receipt: dict[str, Any],
    returned_artifact_sha256: str,
    baseline_notes: list[dict[str, Any]],
    returned_notes: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, str | None]:
    baseline = _signature_counter(baseline_notes)
    returned = _signature_counter(returned_notes)
    removed = sorted((baseline - returned).elements())
    added = sorted((returned - baseline).elements())
    identity = _identity_by_signature(receipt)

    if not removed and not added:
        return None, "returned DAWproject contains no scoped exact-note delta"

    operation_seed = {
        "source": receipt["source"],
        "returned_artifact_sha256": returned_artifact_sha256,
        "removed": [_signature_dict(item) for item in removed],
        "added": [_signature_dict(item) for item in added],
    }
    operation_id = f"OP-M6-R4-{_canonical_hash(operation_seed)[:20]}"

    if len(removed) == 1 and not added:
        source_item = identity.get(removed[0])
        if source_item is None:
            return None, "deleted interchange note cannot be bound to one stable MUSICA note identity"
        return {
            "operation_id": operation_id,
            "op": "DELETE",
            "target": {"note_id": source_item["note_id"], "part_id": source_item["part_id"]},
        }, None

    if not removed and len(added) == 1:
        inserted = added[0]
        if inserted in baseline:
            return None, "v0 blocks insertion of a duplicate interchange signature because future identity would be ambiguous"
        tick, duration, pitch, velocity, channel = inserted
        if channel != int(receipt["scope"]["channel"]):
            return None, "inserted note changes the bounded channel/part mapping"
        start_beat = tick / PPQ
        duration_beats = duration / PPQ
        section_id = _section_for_insert(
            source_blueprint,
            start_beat=start_beat,
            duration_beats=duration_beats,
        )
        note_seed = {
            "source": receipt["source"],
            "returned_artifact_sha256": returned_artifact_sha256,
            "signature": _signature_dict(inserted),
        }
        note_id = f"N-IMP-{_canonical_hash(note_seed)[:20]}"
        existing_ids = {
            str(note["note_id"])
            for note in (exact_timeline(source_blueprint) or {}).get("notes", [])
        }
        if note_id in existing_ids:
            return None, "deterministic inserted note identity collides with an accepted note_id"
        return {
            "operation_id": operation_id,
            "op": "INSERT",
            "note": {
                "note_id": note_id,
                "part_id": str(receipt["scope"]["part_id"]),
                "section_id": section_id,
                "start_beat": start_beat,
                "duration_beats": duration_beats,
                "pitch": pitch,
                "velocity": velocity,
            },
        }, None

    if len(removed) == 1 and len(added) == 1:
        before = removed[0]
        after = added[0]
        source_item = identity.get(before)
        if source_item is None:
            return None, "changed interchange note cannot be bound to one stable MUSICA note identity"
        fields = ["tick", "duration", "pitch", "velocity", "channel"]
        changed = [field for field, old, new in zip(fields, before, after) if old != new]
        if len(changed) != 1:
            return None, "v0 requires exactly one primitive field change on one stable note"
        target = {"note_id": source_item["note_id"], "part_id": source_item["part_id"]}
        field = changed[0]
        if field == "tick":
            return {
                "operation_id": operation_id,
                "op": "MOVE",
                "target": target,
                "start_beat": after[0] / PPQ,
            }, None
        if field == "duration":
            return {
                "operation_id": operation_id,
                "op": "RESIZE",
                "target": target,
                "duration_beats": after[1] / PPQ,
            }, None
        if field == "pitch":
            return {
                "operation_id": operation_id,
                "op": "REPITCH",
                "target": target,
                "pitch": after[2],
            }, None
        if field == "velocity":
            return {
                "operation_id": operation_id,
                "op": "SET_VELOCITY",
                "target": target,
                "velocity": after[3],
            }, None
        return None, "DAWproject channel mutation is outside the bounded exact-note primitive vocabulary"

    return None, "v0 blocks multi-note or compound external deltas rather than guessing correspondence"


def reconcile_dawproject_note_edit(
    project: Any,
    receipt: dict[str, Any],
    returned_artifact: bytes,
    *,
    branch: str | None = None,
) -> DawProjectNoteReconciliation:
    """Reconcile one returned DAWproject against its exact MUSICA-origin baseline.

    The source export is regenerated from the exact historical source revision and
    must reproduce the receipt. Returned note order is irrelevant; comparison is
    performed as multisets of normalized musical signatures.
    """

    validate_contract(receipt, "interchange-note-receipt-v0.schema.json")
    source_revision_id = str(receipt["source"]["revision_id"])
    source_blueprint = project.read_revision(source_revision_id)
    if str(source_blueprint["project"]["project_id"]) != str(receipt["source"]["project_id"]):
        raise ReconciliationError("receipt project_id does not match its source revision")
    if blueprint_sha256(source_blueprint) != str(receipt["source"]["blueprint_sha256"]):
        raise ReconciliationError("receipt source Blueprint hash mismatch")

    rebuilt = export_dawproject_note_roundtrip(source_blueprint)
    if rebuilt.receipt != receipt:
        raise ReconciliationError("receipt does not reproduce from the exact source revision")

    baseline_inspected = inspect_dawproject(rebuilt.artifact)
    returned_inspected = inspect_dawproject(returned_artifact)
    baseline = baseline_inspected["normalized"]
    returned = returned_inspected["normalized"]
    returned_artifact_sha256 = str(returned_inspected["artifact_sha256"])
    returned_normalized_sha256 = _canonical_hash(returned)

    if returned_inspected["extras"]:
        return _blocked(
            returned_artifact_sha256=returned_artifact_sha256,
            returned_normalized_sha256=returned_normalized_sha256,
            code="UNREPRESENTABLE_EDIT",
            reason="R4 v0 blocks returned archives containing extra non-authoritative members",
        )
    if returned["transport"] != baseline["transport"]:
        return _blocked(
            returned_artifact_sha256=returned_artifact_sha256,
            returned_normalized_sha256=returned_normalized_sha256,
            code="UNREPRESENTABLE_EDIT",
            reason="R4 v0 note reconciliation requires unchanged tempo and meter",
        )

    baseline_keys = [_track_key(track) for track in baseline["tracks"]]
    returned_keys = [_track_key(track) for track in returned["tracks"]]
    if any(None in key for key in baseline_keys + returned_keys) or baseline_keys != returned_keys:
        return _blocked(
            returned_artifact_sha256=returned_artifact_sha256,
            returned_normalized_sha256=returned_normalized_sha256,
            code="UNREPRESENTABLE_EDIT",
            reason="R4 v0 requires identical traceable track/part mapping and order",
        )

    scope_key = (str(receipt["scope"]["track_id"]), str(receipt["scope"]["part_id"]))
    baseline_by_key = {_track_key(track): track for track in baseline["tracks"]}
    returned_by_key = {_track_key(track): track for track in returned["tracks"]}
    if scope_key not in baseline_by_key or scope_key not in returned_by_key:
        return _blocked(
            returned_artifact_sha256=returned_artifact_sha256,
            returned_normalized_sha256=returned_normalized_sha256,
            code="UNREPRESENTABLE_EDIT",
            reason="R4 scoped exact-note track is missing from the returned artifact",
        )

    for key, baseline_track in baseline_by_key.items():
        if key == scope_key:
            continue
        if returned_by_key[key]["notes"] != baseline_track["notes"]:
            return _blocked(
                returned_artifact_sha256=returned_artifact_sha256,
                returned_normalized_sha256=returned_normalized_sha256,
                code="UNREPRESENTABLE_EDIT",
                reason=f"R4 v0 blocks note changes outside the scoped exact-note track {scope_key}",
            )

    operation, operation_error = _operation_from_delta(
        source_blueprint=source_blueprint,
        receipt=receipt,
        returned_artifact_sha256=returned_artifact_sha256,
        baseline_notes=baseline_by_key[scope_key]["notes"],
        returned_notes=returned_by_key[scope_key]["notes"],
    )
    if operation is None:
        return _blocked(
            returned_artifact_sha256=returned_artifact_sha256,
            returned_normalized_sha256=returned_normalized_sha256,
            code="UNREPRESENTABLE_EDIT",
            reason=operation_error or "external note delta is not representable",
        )

    candidate = _candidate(source_blueprint, receipt, returned_artifact_sha256, operation)
    source_branch = branch or project.current_branch()
    current_blueprint = project.read_revision(project.head_revision_id(source_branch))
    preview = build_note_edit_preview(current_blueprint, candidate)
    if not preview.ready:
        return _blocked(
            returned_artifact_sha256=returned_artifact_sha256,
            returned_normalized_sha256=returned_normalized_sha256,
            code="UNREPRESENTABLE_EDIT",
            reason="existing M6 authority blocked the reconciled candidate",
            operation=operation,
            candidate=candidate,
            preview=preview,
            conflicts=preview.authority_result["conflicts"],
        )

    return DawProjectNoteReconciliation(
        status="READY_FOR_PREVIEW",
        returned_artifact_sha256=returned_artifact_sha256,
        returned_normalized_sha256=returned_normalized_sha256,
        operation=operation,
        candidate=candidate,
        preview=preview,
        conflicts=[],
    )


def accept_dawproject_note_reconciliation(
    project: Any,
    reconciliation: DawProjectNoteReconciliation,
    *,
    branch: str | None = None,
) -> dict[str, Any]:
    """Explicitly accept one READY reconciliation through the existing M2 path."""

    if not reconciliation.ready or reconciliation.preview is None:
        raise ReconciliationError("only READY_FOR_PREVIEW reconciliations may be accepted")
    return accept_note_edit_preview(project, reconciliation.preview, branch=branch)
