"""Executable contract validation for MUSICA.

실행 가능한 MUSICA 계약 검증 모듈.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


class ContractError(ValueError):
    """Raised when an object violates a MUSICA schema contract."""


@dataclass(frozen=True)
class RevisionConflict:
    """Machine-readable revision conflict / 기계 판독 가능한 리비전 충돌."""

    conflict_id: str
    rule_type: str
    rule_id: str
    target: str
    status: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "conflict_id": self.conflict_id,
            "rule_type": self.rule_type,
            "rule_id": self.rule_id,
            "target": self.target,
            "status": self.status,
            "reason": self.reason,
        }


def _load_schema(schema_name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / schema_name
    if not path.exists():
        raise ContractError(f"unknown schema: {schema_name}")
    return json.loads(path.read_text(encoding="utf-8"))


def _decode_pointer_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def get_pointer(document: Any, pointer: str) -> Any:
    """Resolve an RFC 6901-style JSON Pointer used by v0 locks/constraints."""

    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ContractError(f"invalid JSON Pointer target: {pointer}")
    current = document
    for raw in pointer[1:].split("/"):
        token = _decode_pointer_token(raw)
        if isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError) as exc:
                raise ContractError(f"unresolvable JSON Pointer: {pointer}") from exc
        elif isinstance(current, dict):
            if token not in current:
                raise ContractError(f"unresolvable JSON Pointer: {pointer}")
            current = current[token]
        else:
            raise ContractError(f"unresolvable JSON Pointer: {pointer}")
    return current


def _require_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ContractError(f"{label} must be unique")


def exact_timeline(blueprint: dict[str, Any]) -> dict[str, Any] | None:
    """Return the optional canonical exact-note material."""

    melody = blueprint.get("materials", {}).get("melody", {})
    value = melody.get("exact_timeline") if isinstance(melody, dict) else None
    return value if isinstance(value, dict) else None


def exact_note_locks(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    """Return additive stable-ID exact-note locks declared by M6."""

    melody = blueprint.get("materials", {}).get("melody", {})
    value = melody.get("exact_note_locks", []) if isinstance(melody, dict) else []
    if value is None:
        return []
    if not isinstance(value, list):
        raise ContractError("melody.exact_note_locks must be an array")
    return value


def find_exact_note(
    blueprint: dict[str, Any], *, part_id: str, note_id: str
) -> dict[str, Any] | None:
    timeline = exact_timeline(blueprint)
    if timeline is None:
        return None
    for note in timeline.get("notes", []):
        if note.get("part_id") == part_id and note.get("note_id") == note_id:
            return note
    return None


def _motif_part_id(blueprint: dict[str, Any]) -> str:
    for part in blueprint["roles"]["instruments_or_parts"]:
        if part["role"] in {"motif", "lead"}:
            return str(part["part_id"])
    raise ContractError("M6 exact-note v0 requires a motif/lead part")


def _exact_note_sort_key(note: dict[str, Any]) -> tuple[float, str, int, str]:
    return (
        float(note["start_beat"]),
        str(note["part_id"]),
        int(note["pitch"]),
        str(note["note_id"]),
    )


def _validate_exact_note_blueprint_invariants(
    blueprint: dict[str, Any], *, section_ids: list[str], part_ids: list[str]
) -> None:
    timeline = exact_timeline(blueprint)
    note_locks = exact_note_locks(blueprint)
    if timeline is None:
        if note_locks:
            raise ContractError("exact_note_locks require melody.exact_timeline")
        return

    validate_contract(timeline, "exact-note-material-v0.schema.json")
    tempo = blueprint["musical_context"]["tempo"]
    if tempo.get("policy") != "fixed":
        raise ContractError("M6 exact-note v0 requires fixed tempo policy")
    bpm = float(tempo["bpm"])

    notes = timeline["notes"]
    note_ids = [str(note["note_id"]) for note in notes]
    _require_unique(note_ids, "exact note_id")
    if notes != sorted(notes, key=_exact_note_sort_key):
        raise ContractError(
            "exact_timeline.notes must use canonical order (start_beat, part_id, pitch, note_id)"
        )

    motif_part_id = _motif_part_id(blueprint)
    section_map = {str(section["section_id"]): section for section in blueprint["form"]["sections"]}
    duration_seconds = float(blueprint["project"]["duration_seconds"])
    total_beats = duration_seconds * bpm / 60.0
    epsilon = 1e-9

    for note in notes:
        part_id = str(note["part_id"])
        if part_id not in part_ids:
            raise ContractError(f"exact note references unknown part_id: {part_id}")
        if part_id != motif_part_id:
            raise ContractError(
                f"M6-R1 exact-note v0 supports only motif/lead part {motif_part_id!r}, got {part_id!r}"
            )
        start_beat = float(note["start_beat"])
        end_beat = start_beat + float(note["duration_beats"])
        if end_beat > total_beats + epsilon:
            raise ContractError(f"exact note {note['note_id']} exceeds project duration")

        section_id = note.get("section_id")
        if section_id is not None:
            section_key = str(section_id)
            if section_key not in section_map:
                raise ContractError(f"exact note references unknown section_id: {section_key}")
            section = section_map[section_key]
            section_start_beat = float(section["start"]) * bpm / 60.0
            section_end_beat = float(section["end"]) * bpm / 60.0
            if start_beat < section_start_beat - epsilon or end_beat > section_end_beat + epsilon:
                raise ContractError(
                    f"exact note {note['note_id']} falls outside declared section {section_key}"
                )

    note_lock_ids: list[str] = []
    top_level_lock_ids = {str(lock["lock_id"]) for lock in blueprint.get("locks", [])}
    is_root_revision = blueprint["project"].get("parent_revision_id") is None
    for lock in note_locks:
        validate_contract(lock, "exact-note-lock-v0.schema.json")
        lock_id = str(lock["lock_id"])
        note_lock_ids.append(lock_id)
        if lock_id in top_level_lock_ids:
            raise ContractError(f"exact note lock_id collides with top-level lock_id: {lock_id}")
        selector = lock["selector"]
        note = find_exact_note(
            blueprint,
            part_id=str(selector["part_id"]),
            note_id=str(selector["note_id"]),
        )
        if note is None:
            raise ContractError(f"exact note lock {lock_id} references unknown note")
        prop = str(selector["property"])
        if is_root_revision and note[prop] != lock["value"]:
            raise ContractError(
                f"root exact note lock {lock_id} declares value {lock['value']!r} "
                f"but selected note contains {note[prop]!r}"
            )
    _require_unique(note_lock_ids, "exact note lock_id")


def _validate_blueprint_invariants(blueprint: dict[str, Any]) -> None:
    """Validate cross-field rules JSON Schema alone cannot express clearly."""

    duration = float(blueprint["project"]["duration_seconds"])
    sections = blueprint["form"]["sections"]
    section_ids = [section["section_id"] for section in sections]
    _require_unique(section_ids, "section_id")

    previous_end = 0.0
    for section in sections:
        start = float(section["start"])
        end = float(section["end"])
        if end <= start:
            raise ContractError(f"section {section['section_id']} end must be greater than start")
        if start < previous_end:
            raise ContractError(f"section {section['section_id']} overlaps or is out of order")
        if end > duration:
            raise ContractError(f"section {section['section_id']} exceeds project duration")
        previous_end = end

    part_ids = [part["part_id"] for part in blueprint["roles"]["instruments_or_parts"]]
    _require_unique(part_ids, "part_id")

    locks = blueprint.get("locks", [])
    lock_ids = [lock["lock_id"] for lock in locks]
    _require_unique(lock_ids, "lock_id")
    lock_id_set = set(lock_ids)
    is_root_revision = blueprint["project"].get("parent_revision_id") is None
    for lock in locks:
        actual = get_pointer(blueprint, lock["target"])
        if is_root_revision and "value" in lock and actual != lock["value"]:
            raise ContractError(
                f"root lock {lock['lock_id']} declares value {lock['value']!r} but target contains {actual!r}"
            )

    constraints = blueprint.get("constraints", [])
    constraint_ids = [constraint["constraint_id"] for constraint in constraints]
    _require_unique(constraint_ids, "constraint_id")
    constraint_id_set = set(constraint_ids)
    for constraint in constraints:
        get_pointer(blueprint, constraint["target"])

    for section in sections:
        unknown_locks = set(section.get("locks", [])) - lock_id_set
        unknown_constraints = set(section.get("constraints", [])) - constraint_id_set
        if unknown_locks:
            raise ContractError(
                f"section {section['section_id']} references unknown locks: {sorted(unknown_locks)}"
            )
        if unknown_constraints:
            raise ContractError(
                f"section {section['section_id']} references unknown constraints: {sorted(unknown_constraints)}"
            )

    section_id_set = set(section_ids)
    for override in blueprint["semantics"].get("section_overrides", []):
        if override["section_id"] not in section_id_set:
            raise ContractError(f"semantic override references unknown section: {override['section_id']}")

    for point in blueprint["semantics"].get("curves", []):
        if float(point["time"]) > duration:
            raise ContractError(f"semantic curve point exceeds project duration: {point['time']}")

    _validate_exact_note_blueprint_invariants(
        blueprint,
        section_ids=[str(value) for value in section_ids],
        part_ids=[str(value) for value in part_ids],
    )


def validate_contract(instance: dict[str, Any], schema_name: str) -> None:
    """Validate one object against a MUSICA JSON Schema and v0 invariants."""

    schema = _load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda err: list(err.absolute_path))
    if errors:
        details = []
        for err in errors:
            pointer = "/" + "/".join(str(p) for p in err.absolute_path)
            details.append(f"{pointer or '/'}: {err.message}")
        raise ContractError("schema validation failed: " + " | ".join(details))
    if schema_name == "music-blueprint-v0.schema.json":
        _validate_blueprint_invariants(instance)


def _hard_locks(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    return [lock for lock in blueprint.get("locks", []) if lock.get("strength") == "HARD"]


def _constraint_conflict(
    candidate: dict[str, Any], constraint: dict[str, Any], ordinal: int
) -> RevisionConflict | None:
    target = constraint["target"]
    try:
        actual = get_pointer(candidate, target)
    except ContractError as exc:
        return RevisionConflict(
            conflict_id=f"C-CONSTRAINT-{ordinal:03d}",
            rule_type="constraint",
            rule_id=constraint["constraint_id"],
            target=target,
            status="BLOCKED",
            reason=str(exc),
        )

    op = constraint["op"]
    expected = constraint["value"]
    ok = False
    if op == "between":
        ok = (
            isinstance(expected, list)
            and len(expected) == 2
            and isinstance(actual, (int, float))
            and expected[0] <= actual <= expected[1]
        )
    elif op == "eq":
        ok = actual == expected
    elif op == "gte":
        ok = isinstance(actual, (int, float)) and actual >= expected
    elif op == "lte":
        ok = isinstance(actual, (int, float)) and actual <= expected

    if ok:
        return None
    return RevisionConflict(
        conflict_id=f"C-CONSTRAINT-{ordinal:03d}",
        rule_type="constraint",
        rule_id=constraint["constraint_id"],
        target=target,
        status="BLOCKED" if constraint.get("hardness") == "hard" else "REQUIRES_ACCEPTANCE",
        reason=f"constraint {op} expected {expected!r}, got {actual!r}",
    )


def _note_lock_target(lock: dict[str, Any]) -> str:
    selector = lock["selector"]
    return f"note://{selector['part_id']}/{selector['note_id']}/{selector['property']}"


def _note_lock_value(blueprint: dict[str, Any], lock: dict[str, Any]) -> Any:
    selector = lock["selector"]
    note = find_exact_note(
        blueprint,
        part_id=str(selector["part_id"]),
        note_id=str(selector["note_id"]),
    )
    if note is None:
        raise ContractError(f"exact note lock {lock['lock_id']} selected note is missing")
    return note[str(selector["property"])]


def validate_revision(parent: dict[str, Any], candidate: dict[str, Any]) -> list[RevisionConflict]:
    """Validate a candidate Blueprint revision against its parent.

    HARD locks fail closed. SOFT rules are represented as acceptance-required conflicts.
    v0 identity locks preserve an explicit identity token exactly; perceptual similarity
    is intentionally out of scope until evidence-backed identity metrics exist.
    """

    validate_contract(parent, "music-blueprint-v0.schema.json")
    validate_contract(candidate, "music-blueprint-v0.schema.json")

    conflicts: list[RevisionConflict] = []
    parent_revision = parent["project"]["revision_id"]
    if candidate["project"].get("parent_revision_id") != parent_revision:
        conflicts.append(
            RevisionConflict(
                conflict_id="C-PARENT-001",
                rule_type="revision",
                rule_id="parent_revision_id",
                target="/project/parent_revision_id",
                status="BLOCKED",
                reason=f"candidate must reference parent revision {parent_revision!r}",
            )
        )

    candidate_lock_map = {lock["lock_id"]: lock for lock in candidate.get("locks", [])}
    for ordinal, lock in enumerate(_hard_locks(parent), start=1):
        lock_id = lock["lock_id"]
        inherited = lock.get("inheriting", True)
        if inherited:
            candidate_lock = candidate_lock_map.get(lock_id)
            if candidate_lock is None:
                conflicts.append(
                    RevisionConflict(
                        conflict_id=f"C-LOCK-{ordinal:03d}",
                        rule_type="lock",
                        rule_id=lock_id,
                        target=lock["target"],
                        status="BLOCKED",
                        reason="inherited HARD lock was removed from candidate",
                    )
                )
                continue
            critical = ("strength", "target", "mode", "inheriting", "value", "tolerance", "identity_basis")
            if any(candidate_lock.get(key) != lock.get(key) for key in critical):
                conflicts.append(
                    RevisionConflict(
                        conflict_id=f"C-LOCK-{ordinal:03d}",
                        rule_type="lock",
                        rule_id=lock_id,
                        target=lock["target"],
                        status="BLOCKED",
                        reason="inherited HARD lock semantics were changed",
                    )
                )
                continue

        target = lock["target"]
        try:
            before = get_pointer(parent, target)
            after = get_pointer(candidate, target)
        except ContractError as exc:
            conflicts.append(
                RevisionConflict(
                    conflict_id=f"C-LOCK-{ordinal:03d}",
                    rule_type="lock",
                    rule_id=lock_id,
                    target=target,
                    status="BLOCKED",
                    reason=str(exc),
                )
            )
            continue

        mode = lock["mode"]
        if mode == "exact":
            tolerance = lock.get("tolerance", 0.0)
            if isinstance(before, (int, float)) and isinstance(after, (int, float)):
                preserved = abs(float(before) - float(after)) <= float(tolerance)
            else:
                preserved = before == after
        elif mode == "identity":
            preserved = before == after
        else:
            preserved = False

        if not preserved:
            conflicts.append(
                RevisionConflict(
                    conflict_id=f"C-LOCK-{ordinal:03d}",
                    rule_type="lock",
                    rule_id=lock_id,
                    target=target,
                    status="BLOCKED",
                    reason=f"HARD {mode} lock changed value from {before!r} to {after!r}",
                )
            )

    candidate_note_lock_map = {
        str(lock["lock_id"]): lock for lock in exact_note_locks(candidate)
    }
    for ordinal, lock in enumerate(exact_note_locks(parent), start=1):
        lock_id = str(lock["lock_id"])
        target = _note_lock_target(lock)
        if lock.get("inheriting", True):
            candidate_lock = candidate_note_lock_map.get(lock_id)
            if candidate_lock is None:
                conflicts.append(
                    RevisionConflict(
                        conflict_id=f"C-NOTE-LOCK-{ordinal:03d}",
                        rule_type="note_lock",
                        rule_id=lock_id,
                        target=target,
                        status="BLOCKED",
                        reason="inherited HARD exact-note lock was removed from candidate",
                    )
                )
                continue
            critical = ("strength", "selector", "mode", "inheriting", "value")
            if any(candidate_lock.get(key) != lock.get(key) for key in critical):
                conflicts.append(
                    RevisionConflict(
                        conflict_id=f"C-NOTE-LOCK-{ordinal:03d}",
                        rule_type="note_lock",
                        rule_id=lock_id,
                        target=target,
                        status="BLOCKED",
                        reason="inherited HARD exact-note lock semantics were changed",
                    )
                )
                continue

        try:
            before = _note_lock_value(parent, lock)
            after = _note_lock_value(candidate, lock)
        except ContractError as exc:
            conflicts.append(
                RevisionConflict(
                    conflict_id=f"C-NOTE-LOCK-{ordinal:03d}",
                    rule_type="note_lock",
                    rule_id=lock_id,
                    target=target,
                    status="BLOCKED",
                    reason=str(exc),
                )
            )
            continue
        if before != after:
            conflicts.append(
                RevisionConflict(
                    conflict_id=f"C-NOTE-LOCK-{ordinal:03d}",
                    rule_type="note_lock",
                    rule_id=lock_id,
                    target=target,
                    status="BLOCKED",
                    reason=f"HARD exact-note lock changed value from {before!r} to {after!r}",
                )
            )

    for ordinal, constraint in enumerate(parent.get("constraints", []), start=1):
        conflict = _constraint_conflict(candidate, constraint, ordinal)
        if conflict is not None:
            conflicts.append(conflict)

    return conflicts


def clone_for_revision(parent: dict[str, Any], revision_id: str) -> dict[str, Any]:
    """Create a structurally safe candidate copy for deterministic transforms."""

    candidate = copy.deepcopy(parent)
    candidate["project"]["parent_revision_id"] = parent["project"]["revision_id"]
    candidate["project"]["revision_id"] = revision_id
    return candidate
