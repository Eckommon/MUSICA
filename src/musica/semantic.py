"""Bounded deterministic semantic resolver for MUSICA M1.

MUSICA M1 제한형 결정론 의미 해석기.

M1 intentionally implements six explicit semantic axes. The registry documents the
musical mechanisms used by the deterministic core; it is not a claim that subjective
musical meaning has a single universal mapping.
"""

from __future__ import annotations

import re
from typing import Any

from .contracts import (
    ContractError,
    clone_for_revision,
    get_pointer,
    validate_contract,
    validate_revision,
)
from .diff import structured_diff

_TIME_SCOPE = re.compile(r"^time:(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$")
M1_SEMANTIC_AXES = ("energy", "tension", "density", "motion", "brightness", "warmth")

SEMANTIC_MECHANISM_REGISTRY: dict[str, dict[str, Any]] = {
    "energy": {
        "mechanisms": ["note_velocity_expression", "midi_cc11_expression"],
        "lowering": "section energy controls note velocity and expression without changing tempo",
    },
    "tension": {
        "mechanisms": ["bass_pressure_density", "harmonic_motion_intent", "forward_motion_coupling"],
        "lowering": "high tension may add deterministic bass pressure events and bounded motion coupling",
    },
    "density": {
        "mechanisms": ["bass_event_density", "texture_density_intent"],
        "lowering": "high density adds deterministic supporting bass events while preserving the motif token",
    },
    "motion": {
        "mechanisms": ["bass_forward_motion", "anticipatory_support_events"],
        "lowering": "high motion adds deterministic forward-moving support events",
    },
    "brightness": {
        "mechanisms": ["midi_cc74_brightness", "preview_harmonic_brightness"],
        "lowering": "section brightness is emitted as CC74 and interpreted by the local preview synth",
    },
    "warmth": {
        "mechanisms": ["midi_cc71_warmth", "preview_fundamental_warmth"],
        "lowering": "section warmth is emitted as CC71 and interpreted by the local preview synth",
    },
}


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, round(float(value), 6)))


def _resolve_time_scope(blueprint: dict[str, Any], scope: str) -> list[str]:
    match = _TIME_SCOPE.match(scope)
    if not match:
        raise ContractError(f"M1 supports explicit time scopes only, got: {scope}")
    start, end = (float(match.group(1)), float(match.group(2)))
    if end <= start:
        raise ContractError("semantic time scope end must be greater than start")
    if end > float(blueprint["project"]["duration_seconds"]):
        raise ContractError("semantic time scope exceeds project duration")

    section_ids: list[str] = []
    for section in blueprint["form"]["sections"]:
        if float(section["end"]) > start and float(section["start"]) < end:
            section_ids.append(section["section_id"])
    if not section_ids:
        raise ContractError("semantic time scope resolves to no section")
    return section_ids


def _override_for(candidate: dict[str, Any], section_id: str) -> dict[str, Any]:
    for override in candidate["semantics"]["section_overrides"]:
        if override["section_id"] == section_id:
            return override["values"]
    values: dict[str, Any] = {}
    candidate["semantics"]["section_overrides"].append({"section_id": section_id, "values": values})
    return values


def _base_value(candidate: dict[str, Any], section_id: str, name: str) -> float:
    for section in candidate["form"]["sections"]:
        if section["section_id"] == section_id:
            return float(
                section["semantic_targets"].get(
                    name,
                    candidate["semantics"]["global"].get(name, 0.5),
                )
            )
    raise ContractError(f"unknown section: {section_id}")


def _resolve_value(current: float, operation: str, amount: float) -> float:
    if operation == "increase":
        return _bounded(current + amount)
    if operation == "decrease":
        return _bounded(current - amount)
    if operation == "set":
        return _bounded(amount)
    raise ContractError(f"unsupported semantic operation: {operation}")


def _rejected_lock_mechanisms(parent: dict[str, Any]) -> list[str]:
    by_id = {lock["lock_id"]: lock for lock in parent.get("locks", []) if lock.get("strength") == "HARD"}
    rejected: list[str] = []
    if "L-TEMPO" in by_id:
        rejected.append("tempo_change: blocked by L-TEMPO")
    if "L-MELODY-IDENTITY" in by_id:
        rejected.append("motif_identity_rewrite: blocked by L-MELODY-IDENTITY")
    if "L-DRUM-PATTERN" in by_id:
        rejected.append("rhythm_identity_rewrite: blocked by L-DRUM-PATTERN")
    return rejected


def apply_semantic_control(
    parent: dict[str, Any],
    control: dict[str, Any],
    revision_id: str = "rev-002",
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Apply one supported M1 semantic control and emit candidate + structured diff.

    HARD locks and explicit protected targets fail closed. M1 supports exactly six
    axes; schema-valid future vocabulary is rejected until an implementation exists.
    """

    validate_contract(parent, "music-blueprint-v0.schema.json")
    validate_contract(control, "semantic-control-v0.schema.json")
    axis = str(control["name"])
    if axis not in M1_SEMANTIC_AXES:
        raise ContractError(
            f"M1 semantic runtime supports only {', '.join(M1_SEMANTIC_AXES)}, got {axis!r}"
        )

    section_ids = _resolve_time_scope(parent, str(control["scope"]))
    candidate = clone_for_revision(parent, revision_id)
    amount = float(control["value"])
    operation = str(control["operation"])

    for section_id in section_ids:
        values = _override_for(candidate, section_id)
        current = float(values.get(axis, _base_value(candidate, section_id, axis)))
        values[axis] = _resolve_value(current, operation, amount)

        # Explicit bounded coupling retained from M0: tension can increase/decrease
        # forward motion, but never tempo, motif identity, or rhythm identity.
        if axis == "tension" and operation in {"increase", "decrease"}:
            motion_current = float(values.get("motion", _base_value(candidate, section_id, "motion")))
            delta = amount * (0.60 if operation == "increase" else -0.40)
            values["motion"] = _bounded(motion_current + delta)

    if axis == "tension":
        candidate["materials"]["harmony"]["semantic_tension_mechanism"] = (
            "deterministic_support_pressure"
        )
        candidate["materials"]["texture"]["semantic_change"] = "bounded_tension_pressure"
    elif axis == "density":
        candidate["materials"]["texture"]["semantic_change"] = "bounded_density_change"

    registry = SEMANTIC_MECHANISM_REGISTRY[axis]
    candidate["provenance"]["actor"] = "deterministic_transform"
    candidate["provenance"]["change_reason"] = (
        control.get("phrase") or f"Apply M1 semantic {axis} control."
    )
    candidate["provenance"]["source_revision"] = parent["project"]["revision_id"]
    candidate["provenance"]["selected_mechanisms"] = list(registry["mechanisms"])
    candidate["provenance"]["rejected_mechanisms"] = _rejected_lock_mechanisms(parent)

    conflicts = validate_revision(parent, candidate)
    blocking = [conflict for conflict in conflicts if conflict.status == "BLOCKED"]
    if blocking:
        reasons = " | ".join(f"{c.rule_id}: {c.reason}" for c in blocking)
        raise ContractError(f"semantic candidate blocked: {reasons}")

    for pointer in control.get("protected_targets", []):
        before = get_pointer(parent, pointer)
        after = get_pointer(candidate, pointer)
        if before != after:
            raise ContractError(f"protected target changed: {pointer}")

    return candidate, structured_diff(parent, candidate)
