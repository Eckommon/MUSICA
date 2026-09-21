"""M7-R3 deterministic canonical-automation lowering.

This module produces a backend-independent compiled target package from accepted
Blueprint automation. The package is derived/non-canonical and deliberately stops
before MIDI CC, renderer, plug-in, DAW, or audible automation mapping.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from .automation_contracts import (
    automation_material_from_blueprint,
    empty_automation_material,
    validate_automation_material,
)
from .automation_edit import automation_material_sha256, blueprint_sha256
from .contracts import ContractError, validate_contract

AUTOMATION_EXECUTION_COMPILER_ID = "musica-automation-lowering"
AUTOMATION_EXECUTION_COMPILER_VERSION = "0.1.0"
AUTOMATION_EXECUTION_POLICY_ID = "automation-execution-v0-generic-segments"
AUTOMATION_EXECUTION_PPQ = 480
AUTOMATION_EXECUTION_TICK_ROUNDING = "decimal_nearest_half_up_nonnegative"


def beat_to_tick(beat: int | float | str | Decimal) -> int:
    """Convert non-negative quarter-note beat to PPQ ticks using explicit half-up rounding."""

    value = Decimal(str(beat))
    if value < 0:
        raise ContractError("automation execution beat cannot be negative")
    ticks = (value * Decimal(AUTOMATION_EXECUTION_PPQ)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    return int(ticks)


def _source_point(point: dict[str, Any]) -> dict[str, Any]:
    return {
        "point_id": str(point["point_id"]),
        "beat": point["beat"],
        "tick": beat_to_tick(point["beat"]),
        "value": point["value"],
        "interpolation": str(point["interpolation"]),
    }


def _lane_execution(lane: dict[str, Any]) -> dict[str, Any]:
    target = lane["target"]
    points = [_source_point(point) for point in lane["points"]]

    # If two distinct canonical beats collapse to one integer execution tick, do not
    # silently lose timing resolution. A later version may ratify a higher-resolution
    # policy; v0 fails closed instead.
    ticks = [int(point["tick"]) for point in points]
    if len(ticks) != len(set(ticks)):
        raise ContractError(
            f"automation lane {lane['lane_id']} has distinct source beats that collapse "
            f"under {AUTOMATION_EXECUTION_PPQ} PPQ tick quantization"
        )

    segments = []
    for start, end in zip(points, points[1:]):
        segments.append(
            {
                "start_point_id": start["point_id"],
                "end_point_id": end["point_id"],
                "start_tick": start["tick"],
                "end_tick": end["tick"],
                "start_value": start["value"],
                "end_value": end["value"],
                # Canonical point interpolation governs the outgoing segment.
                "interpolation": start["interpolation"],
            }
        )

    return {
        "lane_id": str(lane["lane_id"]),
        "parameter_id": str(target["parameter_id"]),
        "scope": str(target["scope"]),
        "owner_id": target.get("owner_id"),
        "section_id": lane.get("section_id"),
        "unit": str(target["unit"]),
        "minimum": target["minimum"],
        "maximum": target["maximum"],
        "derivation_status": "DERIVED_GENERIC",
        "backend_mapping": {"status": "UNMAPPED"},
        "points": points,
        "segments": segments,
    }


def validate_automation_execution(execution: dict[str, Any]) -> None:
    """Validate schema plus deterministic cross-field execution invariants."""

    validate_contract(execution, "automation-execution-v0.schema.json")

    lanes = execution["lanes"]
    lane_ids = [str(lane["lane_id"]) for lane in lanes]
    if lane_ids != sorted(lane_ids):
        raise ContractError("automation execution lanes must use canonical lane_id order")
    if len(lane_ids) != len(set(lane_ids)):
        raise ContractError("automation execution lane_id must be unique")

    if not execution["source"]["explicit_automation_present"] and lanes:
        raise ContractError("legacy/no-automation execution cannot contain derived lanes")

    global_point_ids: list[str] = []
    for lane in lanes:
        points = lane["points"]
        point_ids = [str(point["point_id"]) for point in points]
        global_point_ids.extend(point_ids)
        if len(point_ids) != len(set(point_ids)):
            raise ContractError(f"automation execution lane {lane['lane_id']} point_id must be unique")

        point_order = [(float(point["beat"]), str(point["point_id"])) for point in points]
        if point_order != sorted(point_order):
            raise ContractError(
                f"automation execution lane {lane['lane_id']} points must preserve canonical beat/point order"
            )

        for point in points:
            if int(point["tick"]) != beat_to_tick(point["beat"]):
                raise ContractError(
                    f"automation execution point {point['point_id']} tick does not match lowering policy"
                )

        expected_segments = max(0, len(points) - 1)
        if len(lane["segments"]) != expected_segments:
            raise ContractError(
                f"automation execution lane {lane['lane_id']} segment count must equal point_count - 1"
            )

        for index, segment in enumerate(lane["segments"]):
            start = points[index]
            end = points[index + 1]
            expected = {
                "start_point_id": start["point_id"],
                "end_point_id": end["point_id"],
                "start_tick": start["tick"],
                "end_tick": end["tick"],
                "start_value": start["value"],
                "end_value": end["value"],
                "interpolation": start["interpolation"],
            }
            if segment != expected:
                raise ContractError(
                    f"automation execution lane {lane['lane_id']} segment {index} does not match source points"
                )

        if lane["backend_mapping"] != {"status": "UNMAPPED"}:
            raise ContractError("M7-R3 backend mapping must remain explicitly UNMAPPED")

    if len(global_point_ids) != len(set(global_point_ids)):
        raise ContractError("automation execution point_id must be globally unique")


def lower_automation_execution(blueprint: dict[str, Any]) -> dict[str, Any]:
    """Lower a validated accepted Blueprint into derived automation execution v0.

    The input object is only read. No project ref, Blueprint, Music IR, Browser Preview,
    renderer state, or canonical automation material is mutated.
    """

    validate_contract(
        blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    explicit = automation_material_from_blueprint(blueprint, materialize_empty=False)
    explicit_present = explicit is not None
    material = explicit if explicit is not None else empty_automation_material()
    validate_automation_material(material)

    execution = {
        "execution_version": "0",
        "classification": "derived_noncanonical",
        "source": {
            "project_id": str(blueprint["project"]["project_id"]),
            "revision_id": str(blueprint["project"]["revision_id"]),
            "blueprint_sha256": blueprint_sha256(blueprint),
            "automation_material_sha256": automation_material_sha256(blueprint),
            "explicit_automation_present": explicit_present,
        },
        "lowering": {
            "compiler_id": AUTOMATION_EXECUTION_COMPILER_ID,
            "compiler_version": AUTOMATION_EXECUTION_COMPILER_VERSION,
            "policy_id": AUTOMATION_EXECUTION_POLICY_ID,
            "ppq": AUTOMATION_EXECUTION_PPQ,
            "tick_rounding": AUTOMATION_EXECUTION_TICK_ROUNDING,
        },
        "authority": {
            "canonical": False,
            "project_mutation_authorized": False,
            "blueprint_mutation_authorized": False,
            "reverse_promotion_authorized": False,
            "renderer_mapping_authorized": False,
            "audible_automation_validated": False,
        },
        "lanes": [_lane_execution(lane) for lane in material["lanes"]],
        "unsupported": [],
    }
    validate_automation_execution(execution)
    return execution
