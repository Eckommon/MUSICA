"""Executable contract-only checks for M7-R0 automation authority.

This module validates standalone automation contracts and cross-field invariants.
It intentionally does not mutate Project bundles, generate Preview state, lower to
Music IR, render audio, or communicate with external applications.
"""

from __future__ import annotations

from typing import Any

from .contracts import ContractError, validate_contract


def _require_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ContractError(f"{label} must be unique")


def _lane_target_signature(lane: dict[str, Any]) -> tuple[str, str, str | None, str | None]:
    target = lane["target"]
    owner = target.get("owner_id")
    section = lane.get("section_id")
    return (
        str(target["parameter_id"]),
        str(target["scope"]),
        None if owner is None else str(owner),
        None if section is None else str(section),
    )


def validate_automation_material(material: dict[str, Any]) -> None:
    """Validate M7-R0 automation material schema plus deterministic invariants."""

    validate_contract(material, "automation-material-v0.schema.json")

    lanes = material["lanes"]
    lane_ids = [str(lane["lane_id"]) for lane in lanes]
    _require_unique(lane_ids, "automation lane_id")
    if lane_ids != sorted(lane_ids):
        raise ContractError("automation lanes must use canonical order by lane_id")

    target_signatures = [_lane_target_signature(lane) for lane in lanes]
    if len(target_signatures) != len(set(target_signatures)):
        raise ContractError("automation lane target signatures must be unique")

    global_point_ids: list[str] = []
    for lane in lanes:
        lane_id = str(lane["lane_id"])
        target = lane["target"]
        minimum = float(target["minimum"])
        maximum = float(target["maximum"])
        if minimum >= maximum:
            raise ContractError(f"automation lane {lane_id} minimum must be less than maximum")

        points = lane["points"]
        point_ids = [str(point["point_id"]) for point in points]
        _require_unique(point_ids, f"automation point_id in lane {lane_id}")
        global_point_ids.extend(point_ids)

        sort_keys = [(float(point["beat"]), str(point["point_id"])) for point in points]
        if sort_keys != sorted(sort_keys):
            raise ContractError(
                f"automation lane {lane_id} points must use canonical order (beat, point_id)"
            )

        beats = [float(point["beat"]) for point in points]
        if len(beats) != len(set(beats)):
            raise ContractError(f"automation lane {lane_id} point beats must be unique")

        for point in points:
            value = float(point["value"])
            if value < minimum or value > maximum:
                raise ContractError(
                    f"automation point {point['point_id']} value {value} outside lane range "
                    f"[{minimum}, {maximum}]"
                )

    _require_unique(global_point_ids, "automation point_id across material")


def _find_lane(material: dict[str, Any], lane_id: str) -> dict[str, Any] | None:
    for lane in material["lanes"]:
        if str(lane["lane_id"]) == lane_id:
            return lane
    return None


def _find_point(lane: dict[str, Any], point_id: str) -> dict[str, Any] | None:
    for point in lane["points"]:
        if str(point["point_id"]) == point_id:
            return point
    return None


def validate_automation_lock(lock: dict[str, Any], material: dict[str, Any]) -> None:
    """Validate a standalone automation lock against validated automation material."""

    validate_automation_material(material)
    validate_contract(lock, "automation-lock-v0.schema.json")

    selector = lock["selector"]
    lane_id = str(selector["lane_id"])
    lane = _find_lane(material, lane_id)
    if lane is None:
        raise ContractError(f"automation lock {lock['lock_id']} references unknown lane_id: {lane_id}")

    prop = str(selector["property"])
    mode = str(lock["mode"])
    point_id_raw = selector.get("point_id")
    point = None
    if point_id_raw is not None:
        point = _find_point(lane, str(point_id_raw))
        if point is None:
            raise ContractError(
                f"automation lock {lock['lock_id']} references unknown point_id: {point_id_raw}"
            )

    if prop in {"point", "beat", "value", "interpolation"} and point is None:
        raise ContractError(f"automation lock property {prop} requires point_id")
    if prop == "lane" and mode != "presence":
        raise ContractError("automation lane lock requires presence mode")
    if prop == "point" and mode != "presence":
        raise ContractError("automation point lock requires presence mode")
    if mode == "presence" and prop not in {"lane", "point"}:
        raise ContractError("automation presence lock supports only lane or point property")
    if mode == "range" and prop not in {"beat", "value"}:
        raise ContractError("automation range lock supports only beat or value property")

    parameter_selector = selector.get("parameter_id")
    lane_parameter = str(lane["target"]["parameter_id"])
    if parameter_selector is not None and str(parameter_selector) != lane_parameter:
        raise ContractError(
            f"automation lock {lock['lock_id']} parameter_id does not match selected lane"
        )
    if prop == "parameter" and str(parameter_selector or "") != lane_parameter:
        raise ContractError("automation parameter lock requires matching parameter_id")

    if prop == "beat":
        actual: Any = point["beat"]
    elif prop == "value":
        actual = point["value"]
    elif prop == "interpolation":
        actual = point["interpolation"]
    elif prop == "parameter":
        actual = lane_parameter
    else:
        actual = None

    if mode == "exact" and actual != lock["value"]:
        raise ContractError(
            f"automation exact lock {lock['lock_id']} value {lock['value']!r} "
            f"does not match selected value {actual!r}"
        )
    if mode == "range":
        minimum = float(lock["minimum"])
        maximum = float(lock["maximum"])
        if minimum > maximum:
            raise ContractError(f"automation range lock {lock['lock_id']} minimum exceeds maximum")
        numeric_actual = float(actual)
        if numeric_actual < minimum or numeric_actual > maximum:
            raise ContractError(
                f"automation range lock {lock['lock_id']} does not contain selected value"
            )
