"""MUSICA M7-R1 bounded canonical automation edit authority engine.

Automation edits materialize non-canonical Blueprint previews only. They never mutate
Music IR or project refs directly; explicit acceptance remains an M2 Project Engine
operation.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any

from .automation_contracts import (
    NATIVE_MIXER_AUTOMATION_SCOPES,
    automation_locks_from_blueprint,
    automation_material_from_blueprint,
    automation_revision_conflicts,
    native_mixer_automation_lanes,
    validate_automation_material,
    validate_blueprint_automation,
)
from .audio_contracts import validate_project_blueprint_audio
from .audio_edit import audio_material_sha256
from .routing_contracts import (
    routing_material_from_blueprint,
    routing_material_sha256,
    validate_blueprint_routing,
)
from .contracts import ContractError, validate_contract, validate_revision
from .evidence import canonical_json_bytes


def blueprint_sha256(blueprint: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(blueprint)).hexdigest()


def automation_material_sha256(blueprint: dict[str, Any]) -> str:
    material = automation_material_from_blueprint(blueprint)
    assert material is not None
    return hashlib.sha256(canonical_json_bytes(material)).hexdigest()


def _authority_result(
    candidate_id: str,
    *,
    conflicts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    blocked = bool(conflicts)
    result = {
        "result_version": "0",
        "candidate_id": candidate_id,
        "status": "BLOCKED" if blocked else "READY_FOR_PREVIEW",
        "conflicts": conflicts or [],
        "preview_generation_allowed": not blocked,
        "explicit_accept_required": True,
        "project_mutation_authorized": False,
        "music_ir_mutation_authorized": False,
    }
    validate_contract(result, "automation-authority-result-v0.schema.json")
    return result


def _conflict(
    ordinal: int,
    code: str,
    reason: str,
    *,
    lane_id: str | None = None,
    point_id: str | None = None,
    rule_id: str | None = None,
) -> dict[str, Any]:
    return {
        "conflict_id": f"M7-R1-C-{ordinal:03d}",
        "code": code,
        "lane_id": lane_id,
        "point_id": point_id,
        "rule_id": rule_id,
        "reason": reason,
    }


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


def _all_point_ids(material: dict[str, Any]) -> set[str]:
    return {
        str(point["point_id"])
        for lane in material["lanes"]
        for point in lane["points"]
    }


def _point_sort_key(point: dict[str, Any]) -> tuple[float, str]:
    return float(point["beat"]), str(point["point_id"])


def _revision_id(parent: dict[str, Any], candidate: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json_bytes(candidate)).hexdigest()[:16]
    return f"{parent['project']['revision_id']}-auto-{digest}"


def _total_beats(blueprint: dict[str, Any]) -> float:
    tempo = blueprint["musical_context"]["tempo"]
    if tempo.get("policy") != "fixed":
        raise ContractError("M7-R1 automation v0 requires fixed tempo policy")
    return float(blueprint["project"]["duration_seconds"]) * float(tempo["bpm"]) / 60.0


def _actor_for_blueprint(kind: str) -> str:
    return "deterministic_transform" if kind == "system" else kind


def _material_diff(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    """Return deterministic stable-ID-oriented automation changes."""

    before_lanes = {str(lane["lane_id"]): lane for lane in before["lanes"]}
    after_lanes = {str(lane["lane_id"]): lane for lane in after["lanes"]}
    changes: list[dict[str, Any]] = []
    for lane_id in sorted(set(before_lanes) | set(after_lanes)):
        old_lane = before_lanes.get(lane_id)
        new_lane = after_lanes.get(lane_id)
        if old_lane is None or new_lane is None:
            changes.append({"lane_id": lane_id, "op": "lane_presence", "before": old_lane, "after": new_lane})
            continue
        old_points = {str(point["point_id"]): point for point in old_lane["points"]}
        new_points = {str(point["point_id"]): point for point in new_lane["points"]}
        for point_id in sorted(set(old_points) | set(new_points)):
            old = old_points.get(point_id)
            new = new_points.get(point_id)
            if old is None:
                changes.append({"lane_id": lane_id, "point_id": point_id, "op": "insert", "before": None, "after": copy.deepcopy(new)})
            elif new is None:
                changes.append({"lane_id": lane_id, "point_id": point_id, "op": "delete", "before": copy.deepcopy(old), "after": None})
            else:
                fields = {
                    key: {"before": old.get(key), "after": new.get(key)}
                    for key in ("beat", "value", "interpolation")
                    if old.get(key) != new.get(key)
                }
                if fields:
                    changes.append({"lane_id": lane_id, "point_id": point_id, "op": "update", "changed_fields": fields})
    return changes


@dataclass(frozen=True)
class AutomationEditPreview:
    authority_result: dict[str, Any]
    blueprint: dict[str, Any] | None
    material_diff: list[dict[str, Any]]
    source_blueprint_sha256: str
    source_automation_material_sha256: str
    candidate_blueprint_sha256: str | None
    candidate_automation_material_sha256: str | None
    changed_lane_ids: list[str]
    changed_point_ids: list[str]
    revision_conflicts: list[dict[str, str]]
    source_revision_id: str | None = None
    source_audio_material_sha256: str | None = None
    source_routing_material_sha256: str | None = None
    native_target_lane_ids: tuple[str, ...] = ()

    @property
    def ready(self) -> bool:
        return self.authority_result["status"] == "READY_FOR_PREVIEW"

    def as_dict(self) -> dict[str, Any]:
        value = {
            "authority_result": copy.deepcopy(self.authority_result),
            "source_blueprint_sha256": self.source_blueprint_sha256,
            "source_automation_material_sha256": self.source_automation_material_sha256,
            "candidate_blueprint_sha256": self.candidate_blueprint_sha256,
            "candidate_automation_material_sha256": self.candidate_automation_material_sha256,
            "material_diff": copy.deepcopy(self.material_diff),
            "changed_lane_ids": list(self.changed_lane_ids),
            "changed_point_ids": list(self.changed_point_ids),
            "revision_conflicts": copy.deepcopy(self.revision_conflicts),
        }
        if self.native_target_lane_ids:
            value["source_revision_id"] = self.source_revision_id
            value["source_audio_material_sha256"] = self.source_audio_material_sha256
            value["source_routing_material_sha256"] = self.source_routing_material_sha256
            value["native_target_lane_ids"] = list(self.native_target_lane_ids)
        return value


def _native_lane_ids_for_candidate(
    material: dict[str, Any], candidate: dict[str, Any]
) -> tuple[str, ...]:
    lanes = {str(lane["lane_id"]): lane for lane in material["lanes"]}
    native: set[str] = set()
    for operation in candidate["operations"]:
        if str(operation["op"]) == "ADD_LANE":
            lane = operation["lane"]
            if str(lane["target"]["scope"]) in NATIVE_MIXER_AUTOMATION_SCOPES:
                native.add(str(lane["lane_id"]))
            continue
        target = operation.get("target", {})
        lane = lanes.get(str(target.get("lane_id", "")))
        if lane is not None and str(lane["target"]["scope"]) in NATIVE_MIXER_AUTOMATION_SCOPES:
            native.add(str(lane["lane_id"]))
    return tuple(sorted(native))


def _routing_hash(blueprint: dict[str, Any]) -> str:
    material = routing_material_from_blueprint(blueprint)
    assert material is not None
    return routing_material_sha256(material)


def _blocked_preview(
    parent: dict[str, Any],
    candidate: dict[str, Any],
    conflicts: list[dict[str, Any]],
    *,
    native_target_lane_ids: tuple[str, ...] = (),
) -> AutomationEditPreview:
    return AutomationEditPreview(
        authority_result=_authority_result(str(candidate["candidate_id"]), conflicts=conflicts),
        blueprint=None,
        material_diff=[],
        source_blueprint_sha256=blueprint_sha256(parent),
        source_automation_material_sha256=automation_material_sha256(parent),
        candidate_blueprint_sha256=None,
        candidate_automation_material_sha256=None,
        changed_lane_ids=[],
        changed_point_ids=[],
        revision_conflicts=[],
        source_revision_id=str(parent["project"]["revision_id"]),
        source_audio_material_sha256=audio_material_sha256(parent),
        source_routing_material_sha256=_routing_hash(parent),
        native_target_lane_ids=native_target_lane_ids,
    )


def build_automation_edit_preview(
    parent_blueprint: dict[str, Any],
    candidate: dict[str, Any],
    *,
    revision_id: str | None = None,
    project: Any | None = None,
    branch: str | None = None,
) -> AutomationEditPreview:
    """Resolve one typed AutomationEditCandidate into a non-canonical Blueprint preview."""

    validate_contract(
        parent_blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    validate_contract(candidate, "automation-edit-candidate-v0.schema.json")

    source = candidate["source"]
    source_blueprint_hash = blueprint_sha256(parent_blueprint)
    source_material_hash = automation_material_sha256(parent_blueprint)
    parent_material = automation_material_from_blueprint(parent_blueprint)
    assert parent_material is not None
    native_target_lane_ids = _native_lane_ids_for_candidate(parent_material, candidate)
    source_audio_hash = audio_material_sha256(parent_blueprint)
    source_routing_hash = _routing_hash(parent_blueprint)
    stale_reasons: list[str] = []
    if source["project_id"] != parent_blueprint["project"]["project_id"]:
        stale_reasons.append("project_id mismatch")
    if source["revision_id"] != parent_blueprint["project"]["revision_id"]:
        stale_reasons.append("revision_id mismatch")
    if source["blueprint_sha256"] != source_blueprint_hash:
        stale_reasons.append("blueprint_sha256 mismatch")
    if source["automation_material_sha256"] != source_material_hash:
        stale_reasons.append("automation_material_sha256 mismatch")
    if native_target_lane_ids:
        if project is None:
            stale_reasons.append("native mixer automation Preview requires Project Engine context")
        else:
            selected_branch = branch or project.current_branch()
            if project.head_revision_id(selected_branch) != str(parent_blueprint["project"]["revision_id"]):
                stale_reasons.append("project branch HEAD no longer equals source revision")
        if source.get("audio_material_sha256") != source_audio_hash:
            stale_reasons.append("audio_material_sha256 mismatch")
        if source.get("routing_material_sha256") != source_routing_hash:
            stale_reasons.append("routing_material_sha256 mismatch")
    if stale_reasons:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "STALE_SOURCE", "; ".join(stale_reasons))],
            native_target_lane_ids=native_target_lane_ids,
        )

    operation_ids = [str(operation["operation_id"]) for operation in candidate["operations"]]
    if len(operation_ids) != len(set(operation_ids)):
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", "operation_id must be unique")],
        )

    working = copy.deepcopy(parent_blueprint)
    working_material = copy.deepcopy(parent_material)
    total_beats = _total_beats(parent_blueprint)
    conflicts: list[dict[str, Any]] = []

    for ordinal, operation in enumerate(candidate["operations"], start=1):
        op = str(operation["op"])
        if op == "ADD_LANE":
            lane = copy.deepcopy(operation["lane"])
            lane_id = str(lane["lane_id"])
            if _find_lane(working_material, lane_id) is not None:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        f"automation lane_id already exists: {lane_id}",
                        lane_id=lane_id,
                    )
                )
                continue
            target_signature = (
                str(lane["target"]["parameter_id"]),
                str(lane["target"]["scope"]),
                str(lane["target"]["owner_id"]),
                lane.get("section_id"),
            )
            duplicate_target = any(
                (
                    str(existing["target"]["parameter_id"]),
                    str(existing["target"]["scope"]),
                    str(existing["target"].get("owner_id")),
                    existing.get("section_id"),
                )
                == target_signature
                for existing in working_material["lanes"]
            )
            if duplicate_target:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        f"automation target already has a lane: {target_signature}",
                        lane_id=lane_id,
                    )
                )
                continue
            working_material["lanes"].append(lane)
            working_material["lanes"].sort(key=lambda item: str(item["lane_id"]))
            continue

        target = operation["target"]
        lane_id = str(target["lane_id"])
        lane = _find_lane(working_material, lane_id)
        if lane is None:
            conflicts.append(_conflict(ordinal, "UNKNOWN_LANE", f"unknown automation lane: {lane_id}", lane_id=lane_id))
            continue

        if op == "INSERT_POINT":
            point = copy.deepcopy(operation["point"])
            point_id = str(point["point_id"])
            if point_id in _all_point_ids(working_material):
                conflicts.append(_conflict(ordinal, "UNREPRESENTABLE_EDIT", f"point_id already exists: {point_id}", lane_id=lane_id, point_id=point_id))
                continue
            beat = float(point["beat"])
            if beat > total_beats + 1e-9:
                conflicts.append(_conflict(ordinal, "INVALID_TIME", f"point beat {beat} exceeds project duration", lane_id=lane_id, point_id=point_id))
                continue
            if any(float(existing["beat"]) == beat for existing in lane["points"]):
                conflicts.append(_conflict(ordinal, "INVALID_TIME", f"automation lane {lane_id} already has a point at beat {beat}", lane_id=lane_id, point_id=point_id))
                continue
            minimum = float(lane["target"]["minimum"])
            maximum = float(lane["target"]["maximum"])
            value = float(point["value"])
            if value < minimum or value > maximum:
                conflicts.append(_conflict(ordinal, "INVALID_VALUE", f"value {value} outside [{minimum}, {maximum}]", lane_id=lane_id, point_id=point_id))
                continue
            lane["points"].append(point)
            lane["points"].sort(key=_point_sort_key)
            continue

        point_id = str(target["point_id"])
        point = _find_point(lane, point_id)
        if point is None:
            conflicts.append(_conflict(ordinal, "UNKNOWN_POINT", f"unknown automation point: {lane_id}/{point_id}", lane_id=lane_id, point_id=point_id))
            continue

        if op == "DELETE_POINT":
            lane["points"] = [item for item in lane["points"] if str(item["point_id"]) != point_id]
            if not lane["points"]:
                conflicts.append(_conflict(ordinal, "UNREPRESENTABLE_EDIT", "R1 cannot leave an existing lane with zero points", lane_id=lane_id, point_id=point_id))
        elif op == "MOVE_POINT":
            beat = float(operation["beat"])
            if beat > total_beats + 1e-9:
                conflicts.append(_conflict(ordinal, "INVALID_TIME", f"point beat {beat} exceeds project duration", lane_id=lane_id, point_id=point_id))
                continue
            if any(str(other["point_id"]) != point_id and float(other["beat"]) == beat for other in lane["points"]):
                conflicts.append(_conflict(ordinal, "INVALID_TIME", f"automation lane {lane_id} already has a point at beat {beat}", lane_id=lane_id, point_id=point_id))
                continue
            point["beat"] = operation["beat"]
            lane["points"].sort(key=_point_sort_key)
        elif op == "SET_VALUE":
            minimum = float(lane["target"]["minimum"])
            maximum = float(lane["target"]["maximum"])
            value = float(operation["value"])
            if value < minimum or value > maximum:
                conflicts.append(_conflict(ordinal, "INVALID_VALUE", f"value {value} outside [{minimum}, {maximum}]", lane_id=lane_id, point_id=point_id))
                continue
            point["value"] = operation["value"]
        elif op == "SET_INTERPOLATION":
            point["interpolation"] = operation["interpolation"]
        else:
            conflicts.append(_conflict(ordinal, "UNREPRESENTABLE_EDIT", f"unsupported automation operation: {op}", lane_id=lane_id, point_id=point_id))

    if conflicts:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            conflicts,
            native_target_lane_ids=native_target_lane_ids,
        )

    try:
        validate_automation_material(working_material)
    except ContractError as exc:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", str(exc))],
            native_target_lane_ids=native_target_lane_ids,
        )

    working["materials"]["automation"] = working_material
    working["project"]["parent_revision_id"] = parent_blueprint["project"]["revision_id"]
    working["project"]["revision_id"] = revision_id or _revision_id(parent_blueprint, candidate)
    provenance = working["provenance"]
    provenance["actor"] = _actor_for_blueprint(str(candidate["actor"]["kind"]))
    provenance["change_reason"] = candidate["reason"]
    provenance["source_revision"] = parent_blueprint["project"]["revision_id"]
    selected = list(provenance.get("selected_mechanisms", []))
    selected.append(f"automation_edit_candidate:{candidate['candidate_id']}")
    selected.extend(f"automation_edit_operation:{operation_id}" for operation_id in operation_ids)
    provenance["selected_mechanisms"] = selected

    part_ids = [str(part["part_id"]) for part in working["roles"]["instruments_or_parts"]]
    section_ids = [str(section["section_id"]) for section in working["form"]["sections"]]
    try:
        validate_blueprint_automation(working, part_ids=part_ids, section_ids=section_ids)
        validate_contract(
            working,
            "music-blueprint-v0.schema.json",
            allow_nonempty_routing=True,
        )
    except ContractError as exc:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", str(exc))],
            native_target_lane_ids=native_target_lane_ids,
        )

    automation_conflicts = automation_revision_conflicts(parent_blueprint, working)
    blocking_auto = [item for item in automation_conflicts if item.status == "BLOCKED"]
    if blocking_auto:
        mapped = [
            _conflict(
                ordinal,
                "HARD_LOCK_VIOLATION",
                item.reason,
                rule_id=item.rule_id,
            )
            for ordinal, item in enumerate(blocking_auto, start=1)
        ]
        return _blocked_preview(
            parent_blueprint,
            candidate,
            mapped,
            native_target_lane_ids=native_target_lane_ids,
        )

    revision_conflicts = validate_revision(
        parent_blueprint,
        working,
        allow_nonempty_routing=True,
    )
    blocking = [item for item in revision_conflicts if item.status == "BLOCKED"]
    if blocking:
        mapped: list[dict[str, Any]] = []
        for ordinal, item in enumerate(blocking, start=1):
            code = "HARD_LOCK_VIOLATION" if item.rule_type in {"lock", "note_lock", "automation_lock"} else "CONSTRAINT_VIOLATION" if item.rule_type == "constraint" else "UNREPRESENTABLE_EDIT"
            mapped.append(_conflict(ordinal, code, item.reason, rule_id=item.rule_id))
        return _blocked_preview(
            parent_blueprint,
            candidate,
            mapped,
            native_target_lane_ids=native_target_lane_ids,
        )

    if native_target_lane_ids:
        if audio_material_sha256(working) != source_audio_hash:
            return _blocked_preview(
                parent_blueprint,
                candidate,
                [_conflict(1, "UNREPRESENTABLE_EDIT", "native automation edit changed audio material")],
                native_target_lane_ids=native_target_lane_ids,
            )
        if _routing_hash(working) != source_routing_hash:
            return _blocked_preview(
                parent_blueprint,
                candidate,
                [_conflict(1, "UNREPRESENTABLE_EDIT", "native automation edit changed routing material")],
                native_target_lane_ids=native_target_lane_ids,
            )

    diff = _material_diff(parent_material, working_material)
    return AutomationEditPreview(
        authority_result=_authority_result(str(candidate["candidate_id"])),
        blueprint=working,
        material_diff=diff,
        source_blueprint_sha256=source_blueprint_hash,
        source_automation_material_sha256=source_material_hash,
        candidate_blueprint_sha256=blueprint_sha256(working),
        candidate_automation_material_sha256=hashlib.sha256(canonical_json_bytes(working_material)).hexdigest(),
        changed_lane_ids=sorted({str(item["lane_id"]) for item in diff}),
        changed_point_ids=sorted({str(item["point_id"]) for item in diff if item.get("point_id") is not None}),
        revision_conflicts=[item.as_dict() for item in revision_conflicts],
        source_revision_id=str(parent_blueprint["project"]["revision_id"]),
        source_audio_material_sha256=source_audio_hash,
        source_routing_material_sha256=source_routing_hash,
        native_target_lane_ids=native_target_lane_ids,
    )


def accept_automation_edit_preview(
    project: Any,
    preview: AutomationEditPreview,
    *,
    branch: str | None = None,
) -> dict[str, Any]:
    """Explicitly accept one READY automation preview through existing M2 authority."""

    if not preview.ready or preview.blueprint is None:
        raise ContractError("only READY_FOR_PREVIEW automation candidates may be accepted")
    provenance = preview.blueprint["provenance"]

    if not preview.native_target_lane_ids:
        return project.commit_revision(
            preview.blueprint,
            branch=branch,
            actor=str(provenance["actor"]),
            reason=str(provenance["change_reason"]),
        )

    selected_branch = branch or project.current_branch()
    if preview.source_revision_id is None:
        raise ContractError("native automation Preview lacks source revision binding")
    if project.head_revision_id(selected_branch) != preview.source_revision_id:
        raise ContractError("native automation Preview source is stale: project HEAD changed")

    current = project.read_revision(preview.source_revision_id)
    if blueprint_sha256(current) != preview.source_blueprint_sha256:
        raise ContractError("native automation Preview source Blueprint hash is stale")
    if automation_material_sha256(current) != preview.source_automation_material_sha256:
        raise ContractError("native automation Preview source automation material hash is stale")
    if audio_material_sha256(current) != preview.source_audio_material_sha256:
        raise ContractError("native automation Preview source audio material hash is stale")
    if _routing_hash(current) != preview.source_routing_material_sha256:
        raise ContractError("native automation Preview source routing material hash is stale")

    if blueprint_sha256(preview.blueprint) != preview.candidate_blueprint_sha256:
        raise ContractError("native automation Preview candidate Blueprint hash changed")
    if automation_material_sha256(preview.blueprint) != preview.candidate_automation_material_sha256:
        raise ContractError("native automation Preview candidate automation material hash changed")
    if audio_material_sha256(preview.blueprint) != preview.source_audio_material_sha256:
        raise ContractError("native automation Preview candidate changed audio material")
    if _routing_hash(preview.blueprint) != preview.source_routing_material_sha256:
        raise ContractError("native automation Preview candidate changed routing material")
    if preview.blueprint["project"].get("parent_revision_id") != preview.source_revision_id:
        raise ContractError("native automation Preview candidate parent_revision_id is stale")

    validate_contract(
        preview.blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    validate_project_blueprint_audio(project, preview.blueprint)
    validate_blueprint_routing(preview.blueprint, allow_nonempty=True)

    accepted_native_ids = {
        str(lane["lane_id"]) for lane in native_mixer_automation_lanes(preview.blueprint)
    }
    if not set(preview.native_target_lane_ids).issubset(accepted_native_ids):
        raise ContractError("native automation Preview target identity changed before Accept")

    return project._commit_revision(
        preview.blueprint,
        branch=selected_branch,
        actor=str(provenance["actor"]),
        reason=str(provenance["change_reason"]),
        allow_audio_material_change=False,
        allow_routing_material_change=False,
        allow_native_automation_change=True,
    )
