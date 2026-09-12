"""MUSICA M6-R1 stable-ID exact-note edit authority engine.

Exact-note edits materialize Blueprint candidates only. They never mutate Music IR or
project refs directly; acceptance remains an explicit M2 Project Engine operation.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any

from .contracts import (
    ContractError,
    exact_note_locks,
    exact_timeline,
    find_exact_note,
    validate_contract,
    validate_revision,
)
from .evidence import canonical_json_bytes


def blueprint_sha256(blueprint: dict[str, Any]) -> str:
    """Return the canonical MUSICA Blueprint SHA-256 used by source binding."""

    return hashlib.sha256(canonical_json_bytes(blueprint)).hexdigest()


def _note_key(note: dict[str, Any]) -> tuple[str, str]:
    return str(note["part_id"]), str(note["note_id"])


def _sort_key(note: dict[str, Any]) -> tuple[float, str, int, str]:
    return (
        float(note["start_beat"]),
        str(note["part_id"]),
        int(note["pitch"]),
        str(note["note_id"]),
    )


def stable_note_diff(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    """Return deterministic note-ID-oriented changes independent of array indices."""

    before_timeline = exact_timeline(before)
    after_timeline = exact_timeline(after)
    before_map = {
        _note_key(note): copy.deepcopy(note)
        for note in (before_timeline or {}).get("notes", [])
    }
    after_map = {
        _note_key(note): copy.deepcopy(note)
        for note in (after_timeline or {}).get("notes", [])
    }
    changes: list[dict[str, Any]] = []
    for part_id, note_id in sorted(set(before_map) | set(after_map)):
        key = (part_id, note_id)
        old = before_map.get(key)
        new = after_map.get(key)
        if old is None:
            changes.append(
                {
                    "op": "insert",
                    "part_id": part_id,
                    "note_id": note_id,
                    "before": None,
                    "after": new,
                }
            )
            continue
        if new is None:
            changes.append(
                {
                    "op": "delete",
                    "part_id": part_id,
                    "note_id": note_id,
                    "before": old,
                    "after": None,
                }
            )
            continue
        changed_fields = {
            field: {"before": old.get(field), "after": new.get(field)}
            for field in sorted(set(old) | set(new))
            if old.get(field) != new.get(field)
        }
        if changed_fields:
            changes.append(
                {
                    "op": "update",
                    "part_id": part_id,
                    "note_id": note_id,
                    "changed_fields": changed_fields,
                }
            )
    return changes


def _authority_result(
    candidate_id: str,
    source_revision_id: str,
    *,
    conflicts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    blocked = bool(conflicts)
    result = {
        "result_version": "0",
        "candidate_id": candidate_id,
        "source_revision_id": source_revision_id,
        "status": "BLOCKED" if blocked else "READY_FOR_PREVIEW",
        "conflicts": conflicts or [],
        "preview_generation_allowed": not blocked,
        "explicit_accept_required": True,
        "project_mutation_authorized": False,
        "music_ir_mutation_authorized": False,
    }
    validate_contract(result, "note-edit-authority-result-v0.schema.json")
    return result


def _conflict(
    ordinal: int,
    code: str,
    reason: str,
    *,
    operation_id: str | None = None,
    note_id: str | None = None,
    rule_id: str | None = None,
) -> dict[str, Any]:
    return {
        "conflict_id": f"M6-R1-C-{ordinal:03d}",
        "code": code,
        "status": "BLOCKED",
        "operation_id": operation_id,
        "note_id": note_id,
        "rule_id": rule_id,
        "reason": reason,
    }


@dataclass(frozen=True)
class NoteEditPreview:
    """Non-canonical exact-note preview result."""

    authority_result: dict[str, Any]
    blueprint: dict[str, Any] | None
    stable_note_diff: list[dict[str, Any]]
    source_blueprint_sha256: str
    candidate_blueprint_sha256: str | None
    changed_note_ids: list[str]
    revision_conflicts: list[dict[str, str]]

    @property
    def ready(self) -> bool:
        return self.authority_result["status"] == "READY_FOR_PREVIEW"

    def as_dict(self) -> dict[str, Any]:
        return {
            "authority_result": copy.deepcopy(self.authority_result),
            "source_blueprint_sha256": self.source_blueprint_sha256,
            "candidate_blueprint_sha256": self.candidate_blueprint_sha256,
            "stable_note_diff": copy.deepcopy(self.stable_note_diff),
            "changed_note_ids": list(self.changed_note_ids),
            "revision_conflicts": copy.deepcopy(self.revision_conflicts),
        }


def _blocked_preview(
    parent: dict[str, Any], candidate: dict[str, Any], conflicts: list[dict[str, Any]]
) -> NoteEditPreview:
    return NoteEditPreview(
        authority_result=_authority_result(
            str(candidate["candidate_id"]),
            str(candidate["source"]["revision_id"]),
            conflicts=conflicts,
        ),
        blueprint=None,
        stable_note_diff=[],
        source_blueprint_sha256=blueprint_sha256(parent),
        candidate_blueprint_sha256=None,
        changed_note_ids=[],
        revision_conflicts=[],
    )


def _target_lookup(
    notes: list[dict[str, Any]], *, part_id: str, note_id: str
) -> tuple[int | None, str | None]:
    for index, note in enumerate(notes):
        if str(note["note_id"]) != note_id:
            continue
        if str(note["part_id"]) == part_id:
            return index, None
        return None, "PART_MISMATCH"
    return None, "UNKNOWN_NOTE"


def _lock_conflicts(parent: dict[str, Any], working: dict[str, Any]) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    for ordinal, lock in enumerate(exact_note_locks(parent), start=1):
        selector = lock["selector"]
        part_id = str(selector["part_id"])
        note_id = str(selector["note_id"])
        prop = str(selector["property"])
        before = find_exact_note(parent, part_id=part_id, note_id=note_id)
        after = find_exact_note(working, part_id=part_id, note_id=note_id)
        before_value = None if before is None else before.get(prop)
        after_value = None if after is None else after.get(prop)
        if before_value != after_value:
            conflicts.append(
                _conflict(
                    ordinal,
                    "HARD_LOCK_VIOLATION",
                    f"HARD exact-note lock {lock['lock_id']} protects {prop}: "
                    f"{before_value!r} -> {after_value!r}",
                    note_id=note_id,
                    rule_id=str(lock["lock_id"]),
                )
            )
    return conflicts


def _revision_id(parent: dict[str, Any], candidate: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json_bytes(candidate)).hexdigest()[:16]
    return f"{parent['project']['revision_id']}-note-{digest}"


def build_note_edit_preview(
    parent_blueprint: dict[str, Any],
    candidate: dict[str, Any],
    *,
    revision_id: str | None = None,
) -> NoteEditPreview:
    """Resolve one typed NoteEditCandidate into a non-canonical Blueprint preview."""

    validate_contract(parent_blueprint, "music-blueprint-v0.schema.json")
    validate_contract(candidate, "note-edit-candidate-v0.schema.json")
    source_hash = blueprint_sha256(parent_blueprint)
    source = candidate["source"]
    stale_reasons: list[str] = []
    if source["project_id"] != parent_blueprint["project"]["project_id"]:
        stale_reasons.append("project_id mismatch")
    if source["revision_id"] != parent_blueprint["project"]["revision_id"]:
        stale_reasons.append("revision_id mismatch")
    if source["blueprint_sha256"] != source_hash:
        stale_reasons.append("blueprint_sha256 mismatch")
    if stale_reasons:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "STALE_SOURCE", "; ".join(stale_reasons))],
        )

    operation_ids = [str(operation["operation_id"]) for operation in candidate["operations"]]
    if len(operation_ids) != len(set(operation_ids)):
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", "operation_id must be unique")],
        )

    parent_timeline = exact_timeline(parent_blueprint)
    if parent_timeline is None:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [
                _conflict(
                    1,
                    "UNREPRESENTABLE_EDIT",
                    "M6-R1 v0 requires an accepted melody.exact_timeline source",
                )
            ],
        )

    working = copy.deepcopy(parent_blueprint)
    timeline = exact_timeline(working)
    assert timeline is not None
    notes = timeline["notes"]
    operation_conflicts: list[dict[str, Any]] = []

    for ordinal, operation in enumerate(candidate["operations"], start=1):
        operation_id = str(operation["operation_id"])
        op = str(operation["op"])
        if op == "INSERT":
            note = copy.deepcopy(operation["note"])
            existing_index, mismatch = _target_lookup(
                notes,
                part_id=str(note["part_id"]),
                note_id=str(note["note_id"]),
            )
            if existing_index is not None or mismatch == "PART_MISMATCH":
                operation_conflicts.append(
                    _conflict(
                        ordinal,
                        "INVALID_NOTE",
                        f"INSERT note_id already exists: {note['note_id']}",
                        operation_id=operation_id,
                        note_id=str(note["note_id"]),
                    )
                )
                continue
            notes.append(note)
            continue

        target = operation["target"]
        part_id = str(target["part_id"])
        note_id = str(target["note_id"])
        index, lookup_error = _target_lookup(notes, part_id=part_id, note_id=note_id)
        if index is None:
            operation_conflicts.append(
                _conflict(
                    ordinal,
                    lookup_error or "UNKNOWN_NOTE",
                    (
                        f"note_id {note_id!r} exists under a different part"
                        if lookup_error == "PART_MISMATCH"
                        else f"unknown exact note target: {part_id}/{note_id}"
                    ),
                    operation_id=operation_id,
                    note_id=note_id,
                )
            )
            continue

        note = notes[index]
        if op == "DELETE":
            del notes[index]
        elif op == "MOVE":
            note["start_beat"] = operation["start_beat"]
        elif op == "RESIZE":
            note["duration_beats"] = operation["duration_beats"]
        elif op == "REPITCH":
            note["pitch"] = operation["pitch"]
        elif op == "SET_VELOCITY":
            note["velocity"] = operation["velocity"]
        else:  # schema validation should make this unreachable.
            operation_conflicts.append(
                _conflict(
                    ordinal,
                    "UNREPRESENTABLE_EDIT",
                    f"unsupported note operation: {op}",
                    operation_id=operation_id,
                    note_id=note_id,
                )
            )

    if operation_conflicts:
        return _blocked_preview(parent_blueprint, candidate, operation_conflicts)

    notes.sort(key=_sort_key)
    lock_conflicts = _lock_conflicts(parent_blueprint, working)
    if lock_conflicts:
        return _blocked_preview(parent_blueprint, candidate, lock_conflicts)

    working["project"]["parent_revision_id"] = parent_blueprint["project"]["revision_id"]
    working["project"]["revision_id"] = revision_id or _revision_id(parent_blueprint, candidate)
    provenance = working["provenance"]
    provenance["actor"] = candidate["actor"]["kind"]
    provenance["change_reason"] = candidate["reason"]
    provenance["source_revision"] = parent_blueprint["project"]["revision_id"]
    selected = list(provenance.get("selected_mechanisms", []))
    selected.append(f"note_edit_candidate:{candidate['candidate_id']}")
    selected.extend(f"note_edit_operation:{op_id}" for op_id in operation_ids)
    provenance["selected_mechanisms"] = selected

    try:
        validate_contract(working, "music-blueprint-v0.schema.json")
    except ContractError as exc:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "INVALID_NOTE", str(exc))],
        )

    revision_conflicts = validate_revision(parent_blueprint, working)
    blocking = [conflict for conflict in revision_conflicts if conflict.status == "BLOCKED"]
    if blocking:
        converted: list[dict[str, Any]] = []
        for ordinal, conflict in enumerate(blocking, start=1):
            if conflict.rule_type in {"lock", "note_lock"}:
                code = "HARD_LOCK_VIOLATION"
            elif conflict.rule_type == "constraint":
                code = "CONSTRAINT_VIOLATION"
            else:
                code = "UNREPRESENTABLE_EDIT"
            converted.append(
                _conflict(
                    ordinal,
                    code,
                    conflict.reason,
                    rule_id=conflict.rule_id,
                )
            )
        return _blocked_preview(parent_blueprint, candidate, converted)

    note_diff = stable_note_diff(parent_blueprint, working)
    candidate_hash = blueprint_sha256(working)
    changed_note_ids = sorted({str(item["note_id"]) for item in note_diff})
    authority = _authority_result(
        str(candidate["candidate_id"]),
        str(source["revision_id"]),
    )
    return NoteEditPreview(
        authority_result=authority,
        blueprint=working,
        stable_note_diff=note_diff,
        source_blueprint_sha256=source_hash,
        candidate_blueprint_sha256=candidate_hash,
        changed_note_ids=changed_note_ids,
        revision_conflicts=[conflict.as_dict() for conflict in revision_conflicts],
    )


def accept_note_edit_preview(
    project: Any,
    preview: NoteEditPreview,
    *,
    branch: str | None = None,
) -> dict[str, Any]:
    """Explicitly accept one READY preview through the existing M2 commit boundary."""

    if not preview.ready or preview.blueprint is None:
        raise ContractError("only READY_FOR_PREVIEW exact-note candidates may be accepted")
    provenance = preview.blueprint["provenance"]
    return project.commit_revision(
        preview.blueprint,
        branch=branch,
        actor=str(provenance["actor"]),
        reason=str(provenance["change_reason"]),
    )
