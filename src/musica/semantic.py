"""Minimal deterministic semantic resolver for MUSICA M0-R2.

M0-R2용 최소 결정론 의미 해석기. This is deliberately narrow: runtime support
proves one canonical `tension` edit rather than claiming general music intelligence.
"""

from __future__ import annotations

import re
from typing import Any

from .contracts import ContractError, clone_for_revision, validate_contract, validate_revision
from .diff import structured_diff

_TIME_SCOPE = re.compile(r"^time:(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$")


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, round(value, 6)))


def _resolve_time_scope(blueprint: dict[str, Any], scope: str) -> list[str]:
    match = _TIME_SCOPE.match(scope)
    if not match:
        raise ContractError(f"M0-R2 supports explicit time scopes only, got: {scope}")
    start, end = (float(match.group(1)), float(match.group(2)))
    if end <= start:
        raise ContractError("semantic time scope end must be greater than start")
    if end > float(blueprint["project"]["duration_seconds"]):
        raise ContractError("semantic time scope exceeds project duration")

    section_ids = []
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
            return float(section["semantic_targets"].get(name, candidate["semantics"]["global"].get(name, 0.5)))
    raise ContractError(f"unknown section: {section_id}")


def apply_semantic_control(
    parent: dict[str, Any], control: dict[str, Any], revision_id: str = "rev-002"
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Apply the canonical M0 semantic edit and return candidate + structured diff.

    Runtime scope is intentionally limited to `tension`. Other vocabulary is schema-valid
    for future expansion but not silently pretended to be implemented.
    """

    validate_contract(parent, "music-blueprint-v0.schema.json")
    validate_contract(control, "semantic-control-v0.schema.json")
    if control["name"] != "tension":
        raise ContractError(
            f"M0-R2 runtime semantic resolver implements only 'tension', got {control['name']!r}"
        )

    section_ids = _resolve_time_scope(parent, control["scope"])
    candidate = clone_for_revision(parent, revision_id)
    amount = float(control["value"])

    for section_id in section_ids:
        values = _override_for(candidate, section_id)
        current = float(values.get("tension", _base_value(candidate, section_id, "tension")))
        operation = control["operation"]
        if operation == "increase":
            resolved = current + amount
        elif operation == "decrease":
            resolved = current - amount
        elif operation == "set":
            resolved = amount
        else:  # schema prevents this; retained as a fail-closed guard.
            raise ContractError(f"unsupported semantic operation: {operation}")
        values["tension"] = _bounded(resolved)

        # M0 deterministic many-to-many mapping: tension also raises forward motion
        # without touching locked tempo, motif identity, or drum pattern identity.
        motion_current = float(values.get("motion", _base_value(candidate, section_id, "motion")))
        if operation == "increase":
            values["motion"] = _bounded(motion_current + amount * 0.60)
        elif operation == "decrease":
            values["motion"] = _bounded(motion_current - amount * 0.40)

    candidate["materials"]["harmony"]["semantic_tension_mechanism"] = "increase_final_section_harmonic_motion"
    candidate["materials"]["texture"]["layer_count"] = int(candidate["materials"]["texture"].get("layer_count", 1)) + 1
    candidate["materials"]["texture"]["semantic_change"] = "increase_final_section_density"

    candidate["provenance"]["actor"] = "deterministic_transform"
    candidate["provenance"]["change_reason"] = control.get("phrase") or "Apply M0 semantic tension edit."
    candidate["provenance"]["source_revision"] = parent["project"]["revision_id"]
    candidate["provenance"]["selected_mechanisms"] = [
        "increase_final_section_bass_activity",
        "increase_final_section_harmonic_motion",
        "increase_texture_layer_intent",
    ]
    candidate["provenance"]["rejected_mechanisms"] = [
        "tempo_increase: blocked by L-TEMPO",
        "motif_rewrite: blocked by L-MELODY-IDENTITY",
        "drum_pattern_change: blocked by L-DRUM-PATTERN",
    ]

    conflicts = validate_revision(parent, candidate)
    blocking = [conflict for conflict in conflicts if conflict.status == "BLOCKED"]
    if blocking:
        reasons = " | ".join(f"{c.rule_id}: {c.reason}" for c in blocking)
        raise ContractError(f"semantic candidate blocked: {reasons}")

    return candidate, structured_diff(parent, candidate)
