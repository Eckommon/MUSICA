"""Executable contract checks for M7 automation authority.

M7-R0 introduced standalone automation contracts. M7-R1 reuses the same checks for
optional Blueprint-integrated canonical automation without granting derived state any
authority.
"""

from __future__ import annotations

import copy
from typing import Any

from .contracts import ContractError, RevisionConflict, validate_contract


EMPTY_AUTOMATION_MATERIAL: dict[str, Any] = {
    "material_version": "0",
    "mode": "explicit_automation",
    "time_base": {"unit": "quarter_note_beat", "origin_beat": 0.0},
    "lanes": [],
}


def empty_automation_material() -> dict[str, Any]:
    """Return the canonical empty material used for legacy/no-automation source binding."""

    return copy.deepcopy(EMPTY_AUTOMATION_MATERIAL)


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
    """Validate automation material schema plus deterministic cross-field invariants."""

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


def automation_material_from_blueprint(
    blueprint: dict[str, Any], *, materialize_empty: bool = True
) -> dict[str, Any] | None:
    """Return accepted explicit automation or the deterministic empty legacy material."""

    materials = blueprint.get("materials", {})
    value = materials.get("automation") if isinstance(materials, dict) else None
    if value is None:
        return empty_automation_material() if materialize_empty else None
    if not isinstance(value, dict):
        raise ContractError("materials.automation must be an object")
    return value


def automation_locks_from_blueprint(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    materials = blueprint.get("materials", {})
    value = materials.get("automation_locks", []) if isinstance(materials, dict) else []
    if value is None:
        return []
    if not isinstance(value, list):
        raise ContractError("materials.automation_locks must be an array")
    return value


def _validate_lock_shape(lock: dict[str, Any]) -> None:
    """Validate lock schema and mode/property semantics without resolving a target."""

    validate_contract(lock, "automation-lock-v0.schema.json")
    selector = lock["selector"]
    prop = str(selector["property"])
    mode = str(lock["mode"])
    if prop in {"point", "beat", "value", "interpolation"} and selector.get("point_id") is None:
        raise ContractError(f"automation lock property {prop} requires point_id")
    if prop == "lane" and mode != "presence":
        raise ContractError("automation lane lock requires presence mode")
    if prop == "point" and mode != "presence":
        raise ContractError("automation point lock requires presence mode")
    if mode == "presence" and prop not in {"lane", "point"}:
        raise ContractError("automation presence lock supports only lane or point property")
    if mode == "range" and prop not in {"beat", "value"}:
        raise ContractError("automation range lock supports only beat or value property")
    if mode == "range" and float(lock["minimum"]) > float(lock["maximum"]):
        raise ContractError(f"automation range lock {lock['lock_id']} minimum exceeds maximum")
    if prop == "parameter" and selector.get("parameter_id") is None:
        raise ContractError("automation parameter lock requires parameter_id")


def validate_automation_lock(
    lock: dict[str, Any],
    material: dict[str, Any],
    *,
    enforce_selected_value: bool = True,
) -> None:
    """Validate an automation lock against a material.

    R0 standalone/root validation enforces the selected value. Child revisions may
    structurally carry an inherited lock while `validate_revision` decides whether a
    proposed edit violates that parent authority.
    """

    validate_automation_material(material)
    _validate_lock_shape(lock)

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

    parameter_selector = selector.get("parameter_id")
    lane_parameter = str(lane["target"]["parameter_id"])
    if parameter_selector is not None and str(parameter_selector) != lane_parameter:
        raise ContractError(
            f"automation lock {lock['lock_id']} parameter_id does not match selected lane"
        )
    if prop == "parameter" and str(parameter_selector or "") != lane_parameter:
        raise ContractError("automation parameter lock requires matching parameter_id")

    if not enforce_selected_value:
        return

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
        numeric_actual = float(actual)
        if numeric_actual < minimum or numeric_actual > maximum:
            raise ContractError(
                f"automation range lock {lock['lock_id']} does not contain selected value"
            )


def validate_blueprint_automation(
    blueprint: dict[str, Any], *, part_ids: list[str], section_ids: list[str]
) -> None:
    """Validate optional M7-R1 Blueprint integration and ownership/time bounds."""

    actual = automation_material_from_blueprint(blueprint, materialize_empty=False)
    locks = automation_locks_from_blueprint(blueprint)
    if actual is None:
        if locks:
            raise ContractError("automation_locks require materials.automation")
        return

    validate_automation_material(actual)
    tempo = blueprint["musical_context"]["tempo"]
    if tempo.get("policy") != "fixed":
        raise ContractError("M7-R1 automation v0 requires fixed tempo policy")
    bpm = float(tempo["bpm"])
    duration_seconds = float(blueprint["project"]["duration_seconds"])
    total_beats = duration_seconds * bpm / 60.0
    epsilon = 1e-9
    part_set = set(part_ids)
    section_set = set(section_ids)

    for lane in actual["lanes"]:
        target = lane["target"]
        if target["scope"] == "part" and str(target["owner_id"]) not in part_set:
            raise ContractError(
                f"automation lane {lane['lane_id']} references unknown part_id: {target['owner_id']}"
            )
        section_id = lane.get("section_id")
        if section_id is not None and str(section_id) not in section_set:
            raise ContractError(
                f"automation lane {lane['lane_id']} references unknown section_id: {section_id}"
            )
        for point in lane["points"]:
            if float(point["beat"]) > total_beats + epsilon:
                raise ContractError(
                    f"automation point {point['point_id']} exceeds project duration"
                )

    lock_ids = [str(lock["lock_id"]) for lock in locks]
    _require_unique(lock_ids, "automation lock_id")
    top_level_lock_ids = {str(lock["lock_id"]) for lock in blueprint.get("locks", [])}
    if top_level_lock_ids.intersection(lock_ids):
        duplicate = sorted(top_level_lock_ids.intersection(lock_ids))[0]
        raise ContractError(f"automation lock_id collides with top-level lock_id: {duplicate}")

    is_root_revision = blueprint["project"].get("parent_revision_id") is None
    for lock in locks:
        if is_root_revision:
            validate_automation_lock(lock, actual, enforce_selected_value=True)
        else:
            _validate_lock_shape(lock)


def _selected_value(material: dict[str, Any], lock: dict[str, Any]) -> tuple[bool, Any]:
    selector = lock["selector"]
    lane = _find_lane(material, str(selector["lane_id"]))
    if lane is None:
        return False, None
    prop = str(selector["property"])
    if prop == "lane":
        return True, True
    point_id = selector.get("point_id")
    point = _find_point(lane, str(point_id)) if point_id is not None else None
    if prop == "point":
        return (point is not None), True if point is not None else None
    if prop == "parameter":
        return True, lane["target"]["parameter_id"]
    if point is None:
        return False, None
    if prop == "beat":
        return True, point["beat"]
    if prop == "value":
        return True, point["value"]
    if prop == "interpolation":
        return True, point["interpolation"]
    return False, None


def automation_revision_conflicts(
    parent: dict[str, Any], candidate: dict[str, Any]
) -> list[RevisionConflict]:
    """Protect inherited automation locks even against direct M2 commit attempts."""

    parent_material = automation_material_from_blueprint(parent)
    candidate_material = automation_material_from_blueprint(candidate)
    assert parent_material is not None and candidate_material is not None
    parent_locks = automation_locks_from_blueprint(parent)
    candidate_locks = automation_locks_from_blueprint(candidate)
    parent_lock_map = {str(lock["lock_id"]): lock for lock in parent_locks}
    candidate_lock_map = {str(lock["lock_id"]): lock for lock in candidate_locks}
    conflicts: list[RevisionConflict] = []

    # New child locks must be fully valid against the child material. R1 itself does
    # not create locks, but direct M2 commits may not persist an orphan/invalid lock.
    new_ordinal = 0
    for lock in candidate_locks:
        lock_id = str(lock["lock_id"])
        if lock_id in parent_lock_map:
            continue
        new_ordinal += 1
        try:
            validate_automation_lock(lock, candidate_material, enforce_selected_value=True)
        except ContractError as exc:
            conflicts.append(
                RevisionConflict(
                    conflict_id=f"C-AUTO-NEW-LOCK-{new_ordinal:03d}",
                    rule_type="automation_lock",
                    rule_id=lock_id,
                    target=f"automation://{lock['selector']['lane_id']}/new-lock",
                    status="BLOCKED",
                    reason=str(exc),
                )
            )

    for ordinal, lock in enumerate(parent_locks, start=1):
        lock_id = str(lock["lock_id"])
        strength = str(lock["strength"])
        blocked_status = "BLOCKED" if strength == "HARD" else "REQUIRES_ACCEPTANCE"
        selector = lock["selector"]
        target = (
            f"automation://{selector['lane_id']}/"
            f"{selector.get('point_id') or '-'}/{selector['property']}"
        )
        if lock.get("inheriting", True):
            inherited = candidate_lock_map.get(lock_id)
            critical = ("strength", "selector", "mode", "inheriting", "value", "minimum", "maximum")
            if inherited is None:
                conflicts.append(
                    RevisionConflict(
                        conflict_id=f"C-AUTO-LOCK-{ordinal:03d}",
                        rule_type="automation_lock",
                        rule_id=lock_id,
                        target=target,
                        status=blocked_status,
                        reason="inherited automation lock was removed from candidate",
                    )
                )
                continue
            if any(inherited.get(key) != lock.get(key) for key in critical):
                conflicts.append(
                    RevisionConflict(
                        conflict_id=f"C-AUTO-LOCK-{ordinal:03d}",
                        rule_type="automation_lock",
                        rule_id=lock_id,
                        target=target,
                        status=blocked_status,
                        reason="inherited automation lock semantics were changed",
                    )
                )
                continue

        exists, after = _selected_value(candidate_material, lock)
        mode = str(lock["mode"])
        violated = False
        reason = ""
        if mode == "presence":
            violated = not exists
            reason = "protected automation lane/point is missing"
        elif not exists:
            violated = True
            reason = "protected automation target is missing"
        elif mode == "exact":
            violated = after != lock["value"]
            reason = f"protected automation value changed to {after!r}"
        elif mode == "range":
            numeric = float(after)
            minimum = float(lock["minimum"])
            maximum = float(lock["maximum"])
            violated = numeric < minimum or numeric > maximum
            reason = f"protected automation value {numeric} outside [{minimum}, {maximum}]"
        if violated:
            conflicts.append(
                RevisionConflict(
                    conflict_id=f"C-AUTO-LOCK-{ordinal:03d}",
                    rule_type="automation_lock",
                    rule_id=lock_id,
                    target=target,
                    status=blocked_status,
                    reason=reason,
                )
            )

    return conflicts
