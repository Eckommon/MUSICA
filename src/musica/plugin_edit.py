"""PLUG-R1 trusted accepted-plugin Preview→Accept authority."""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any

from .audio_edit import audio_material_sha256, blueprint_sha256
from .automation_edit import automation_material_sha256
from .contracts import ContractError, validate_contract, validate_revision
from .evidence import canonical_json_bytes
from .plugin_reference import (
    accepted_plugin_material_from_blueprint,
    accepted_plugin_material_sha256,
    plugin_material_sha256,
    validate_plugin_material,
)
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256


def _routing_hash(blueprint: dict[str, Any]) -> str:
    material = routing_material_from_blueprint(blueprint)
    assert material is not None
    return routing_material_sha256(material)


def _authority_result(
    candidate_id: str, *, conflicts: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    blocked = bool(conflicts)
    value = {
        "result_version": "0",
        "candidate_id": candidate_id,
        "status": "BLOCKED" if blocked else "READY_FOR_PREVIEW",
        "conflicts": conflicts or [],
        "preview_generation_allowed": not blocked,
        "explicit_accept_required": True,
        "project_mutation_authorized": False,
        "render_mutation_authorized": False,
    }
    validate_contract(value, "plugin-authority-result-v0.schema.json")
    return value


def _conflict(
    ordinal: int,
    code: str,
    reason: str,
    *,
    instance_id: str | None = None,
    plugin_id: str | None = None,
    node_id: str | None = None,
    rule_id: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "conflict_id": f"PLUG-R1-C-{ordinal:03d}",
        "code": code,
        "reason": reason,
    }
    if instance_id is not None:
        value["instance_id"] = instance_id
    if plugin_id is not None:
        value["plugin_id"] = plugin_id
    if node_id is not None:
        value["node_id"] = node_id
    if rule_id is not None:
        value["rule_id"] = rule_id
    return value


def _revision_id(parent: dict[str, Any], candidate: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json_bytes(candidate)).hexdigest()[:16]
    return f"{parent['project']['revision_id']}-plugin-{digest}"


def _actor_for_blueprint(kind: str) -> str:
    return "deterministic_transform" if kind == "system" else kind


def _sort_material(material: dict[str, Any]) -> None:
    material["descriptors"].sort(key=lambda item: str(item["plugin_id"]))
    material["instances"].sort(
        key=lambda item: (
            str(item["owner"]["owner_id"]),
            int(item["slot"]),
            str(item["instance_id"]),
        )
    )


def _instance(material: dict[str, Any], instance_id: str) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in material["instances"]
            if str(item["instance_id"]) == instance_id
        ),
        None,
    )


def _descriptor(material: dict[str, Any], plugin_id: str) -> dict[str, Any] | None:
    return next(
        (
            item
            for item in material["descriptors"]
            if str(item["plugin_id"]) == plugin_id
        ),
        None,
    )


@dataclass(frozen=True)
class PluginEditPreview:
    authority_result: dict[str, Any]
    blueprint: dict[str, Any] | None
    source_revision_id: str
    source_blueprint_sha256: str
    source_audio_material_sha256: str
    source_routing_material_sha256: str
    source_automation_material_sha256: str
    source_plugin_material_sha256: str
    candidate_blueprint_sha256: str | None
    candidate_plugin_material_sha256: str | None
    changed_instance_ids: list[str]
    revision_conflicts: list[dict[str, str]]

    @property
    def ready(self) -> bool:
        return self.authority_result["status"] == "READY_FOR_PREVIEW"

    def as_dict(self) -> dict[str, Any]:
        return {
            "authority_result": copy.deepcopy(self.authority_result),
            "source_revision_id": self.source_revision_id,
            "source_blueprint_sha256": self.source_blueprint_sha256,
            "source_audio_material_sha256": self.source_audio_material_sha256,
            "source_routing_material_sha256": self.source_routing_material_sha256,
            "source_automation_material_sha256": self.source_automation_material_sha256,
            "source_plugin_material_sha256": self.source_plugin_material_sha256,
            "candidate_blueprint_sha256": self.candidate_blueprint_sha256,
            "candidate_plugin_material_sha256": self.candidate_plugin_material_sha256,
            "changed_instance_ids": list(self.changed_instance_ids),
            "revision_conflicts": copy.deepcopy(self.revision_conflicts),
        }


def _blocked(
    parent: dict[str, Any],
    candidate: dict[str, Any],
    conflicts: list[dict[str, Any]],
) -> PluginEditPreview:
    return PluginEditPreview(
        authority_result=_authority_result(
            str(candidate["candidate_id"]), conflicts=conflicts
        ),
        blueprint=None,
        source_revision_id=str(parent["project"]["revision_id"]),
        source_blueprint_sha256=blueprint_sha256(parent),
        source_audio_material_sha256=audio_material_sha256(parent),
        source_routing_material_sha256=_routing_hash(parent),
        source_automation_material_sha256=automation_material_sha256(parent),
        source_plugin_material_sha256=accepted_plugin_material_sha256(parent),
        candidate_blueprint_sha256=None,
        candidate_plugin_material_sha256=None,
        changed_instance_ids=[],
        revision_conflicts=[],
    )


def build_plugin_edit_preview(
    project: Any,
    parent_blueprint: dict[str, Any],
    candidate: dict[str, Any],
    *,
    branch: str | None = None,
    revision_id: str | None = None,
) -> PluginEditPreview:
    """Resolve a source-bound plugin candidate without mutating accepted state."""

    validate_contract(
        parent_blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    validate_contract(candidate, "plugin-edit-candidate-v0.schema.json")

    selected_branch = branch or project.current_branch()
    parent_revision_id = str(parent_blueprint["project"]["revision_id"])
    source = candidate["source"]

    source_blueprint_hash = blueprint_sha256(parent_blueprint)
    source_audio_hash = audio_material_sha256(parent_blueprint)
    source_routing_hash = _routing_hash(parent_blueprint)
    source_automation_hash = automation_material_sha256(parent_blueprint)
    source_plugin_hash = accepted_plugin_material_sha256(parent_blueprint)

    stale: list[str] = []
    if source["project_id"] != parent_blueprint["project"]["project_id"]:
        stale.append("project_id mismatch")
    if source["revision_id"] != parent_revision_id:
        stale.append("revision_id mismatch")
    if source["blueprint_sha256"] != source_blueprint_hash:
        stale.append("blueprint_sha256 mismatch")
    if source["audio_material_sha256"] != source_audio_hash:
        stale.append("audio_material_sha256 mismatch")
    if source["routing_material_sha256"] != source_routing_hash:
        stale.append("routing_material_sha256 mismatch")
    if source["automation_material_sha256"] != source_automation_hash:
        stale.append("automation_material_sha256 mismatch")
    if source["plugin_material_sha256"] != source_plugin_hash:
        stale.append("plugin_material_sha256 mismatch")
    if project.head_revision_id(selected_branch) != parent_revision_id:
        stale.append("project branch HEAD no longer equals source revision")

    if not stale:
        persisted = project.read_revision(parent_revision_id)
        checks = [
            ("persisted source Blueprint hash mismatch", blueprint_sha256(persisted), source_blueprint_hash),
            ("persisted source audio material hash mismatch", audio_material_sha256(persisted), source_audio_hash),
            ("persisted source routing material hash mismatch", _routing_hash(persisted), source_routing_hash),
            ("persisted source automation material hash mismatch", automation_material_sha256(persisted), source_automation_hash),
            ("persisted source plugin material hash mismatch", accepted_plugin_material_sha256(persisted), source_plugin_hash),
        ]
        stale.extend(reason for reason, actual, expected in checks if actual != expected)

    if stale:
        return _blocked(
            parent_blueprint,
            candidate,
            [_conflict(1, "STALE_SOURCE", "; ".join(stale))],
        )

    operation_ids = [str(item["operation_id"]) for item in candidate["operations"]]
    if len(operation_ids) != len(set(operation_ids)):
        return _blocked(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", "operation_id must be unique")],
        )

    working = copy.deepcopy(parent_blueprint)
    material = accepted_plugin_material_from_blueprint(working)
    working_material = copy.deepcopy(material)
    changed: set[str] = set()
    conflicts: list[dict[str, Any]] = []

    for ordinal, operation in enumerate(candidate["operations"], start=1):
        op = str(operation["op"])
        if op == "ADD_INSTANCE":
            descriptor = copy.deepcopy(operation["descriptor"])
            instance = copy.deepcopy(operation["instance"])
            plugin_id = str(descriptor["plugin_id"])
            instance_id = str(instance["instance_id"])
            if str(instance["plugin_id"]) != plugin_id:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        "ADD_INSTANCE descriptor plugin_id must equal instance plugin_id",
                        instance_id=instance_id,
                        plugin_id=plugin_id,
                    )
                )
                continue
            if _instance(working_material, instance_id) is not None:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        f"plugin instance_id already exists: {instance_id}",
                        instance_id=instance_id,
                    )
                )
                continue
            existing_descriptor = _descriptor(working_material, plugin_id)
            if existing_descriptor is None:
                working_material["descriptors"].append(descriptor)
            elif existing_descriptor != descriptor:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        f"plugin descriptor identity mismatch: {plugin_id}",
                        plugin_id=plugin_id,
                    )
                )
                continue
            working_material["instances"].append(instance)
            changed.add(instance_id)
        else:
            instance_id = str(operation["instance_id"])
            instance = _instance(working_material, instance_id)
            if instance is None:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "INVALID_TARGET",
                        f"unknown plugin instance_id: {instance_id}",
                        instance_id=instance_id,
                    )
                )
                continue
            if op == "REMOVE_INSTANCE":
                removed_plugin_id = str(instance["plugin_id"])
                working_material["instances"] = [
                    item
                    for item in working_material["instances"]
                    if str(item["instance_id"]) != instance_id
                ]
                if not any(
                    str(item["plugin_id"]) == removed_plugin_id
                    for item in working_material["instances"]
                ):
                    working_material["descriptors"] = [
                        item
                        for item in working_material["descriptors"]
                        if str(item["plugin_id"]) != removed_plugin_id
                    ]
            elif op == "SET_STATE":
                instance["state"] = copy.deepcopy(operation["state"])
            elif op == "SET_BYPASS":
                instance["bypass"] = bool(operation["bypass"])
            else:  # schema makes this unreachable; keep fail-closed.
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        f"unsupported plugin operation: {op}",
                        instance_id=instance_id,
                    )
                )
                continue
            changed.add(instance_id)

    if conflicts:
        return _blocked(parent_blueprint, candidate, conflicts)

    _sort_material(working_material)
    try:
        validate_plugin_material(working_material, blueprint=parent_blueprint)
    except ContractError as exc:
        return _blocked(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", str(exc))],
        )

    working.setdefault("materials", {})["plugins"] = working_material
    working["project"]["parent_revision_id"] = parent_revision_id
    working["project"]["revision_id"] = revision_id or _revision_id(
        parent_blueprint, candidate
    )
    working["provenance"]["actor"] = _actor_for_blueprint(
        str(candidate["actor"]["kind"])
    )
    working["provenance"]["change_reason"] = str(candidate["reason"])
    working["provenance"]["source_revision"] = parent_revision_id

    try:
        validate_contract(
            working,
            "music-blueprint-v0.schema.json",
            allow_nonempty_routing=True,
        )
    except ContractError as exc:
        return _blocked(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", str(exc))],
        )

    revision_conflicts = validate_revision(
        parent_blueprint,
        working,
        allow_nonempty_routing=True,
    )
    blocking = [item for item in revision_conflicts if item.status == "BLOCKED"]
    if blocking:
        return _blocked(
            parent_blueprint,
            candidate,
            [
                _conflict(
                    ordinal,
                    "REVISION_CONFLICT",
                    item.reason,
                    rule_id=item.rule_id,
                )
                for ordinal, item in enumerate(blocking, start=1)
            ],
        )

    candidate_plugin = accepted_plugin_material_from_blueprint(working)
    return PluginEditPreview(
        authority_result=_authority_result(str(candidate["candidate_id"])),
        blueprint=working,
        source_revision_id=parent_revision_id,
        source_blueprint_sha256=source_blueprint_hash,
        source_audio_material_sha256=source_audio_hash,
        source_routing_material_sha256=source_routing_hash,
        source_automation_material_sha256=source_automation_hash,
        source_plugin_material_sha256=source_plugin_hash,
        candidate_blueprint_sha256=blueprint_sha256(working),
        candidate_plugin_material_sha256=plugin_material_sha256(candidate_plugin),
        changed_instance_ids=sorted(changed),
        revision_conflicts=[item.as_dict() for item in revision_conflicts],
    )


def accept_plugin_edit_preview(
    project: Any,
    preview: PluginEditPreview,
    *,
    branch: str | None = None,
) -> dict[str, Any]:
    """Explicitly accept one READY plugin Preview after exact revalidation."""

    if not preview.ready or preview.blueprint is None:
        raise ContractError("only READY_FOR_PREVIEW plugin candidates may be accepted")

    selected_branch = branch or project.current_branch()
    if project.head_revision_id(selected_branch) != preview.source_revision_id:
        raise ContractError("plugin Preview source is stale: project HEAD changed")

    current = project.read_revision(preview.source_revision_id)
    checks = [
        ("plugin Preview source Blueprint hash is stale", blueprint_sha256(current), preview.source_blueprint_sha256),
        ("plugin Preview source audio material hash is stale", audio_material_sha256(current), preview.source_audio_material_sha256),
        ("plugin Preview source routing material hash is stale", _routing_hash(current), preview.source_routing_material_sha256),
        ("plugin Preview source automation material hash is stale", automation_material_sha256(current), preview.source_automation_material_sha256),
        ("plugin Preview source plugin material hash is stale", accepted_plugin_material_sha256(current), preview.source_plugin_material_sha256),
    ]
    for reason, actual, expected in checks:
        if actual != expected:
            raise ContractError(reason)

    if blueprint_sha256(preview.blueprint) != preview.candidate_blueprint_sha256:
        raise ContractError("plugin Preview candidate Blueprint hash changed")
    candidate_material = accepted_plugin_material_from_blueprint(preview.blueprint)
    if plugin_material_sha256(candidate_material) != preview.candidate_plugin_material_sha256:
        raise ContractError("plugin Preview candidate plugin material hash changed")
    if preview.blueprint["project"].get("parent_revision_id") != preview.source_revision_id:
        raise ContractError("plugin Preview candidate parent_revision_id is stale")

    validate_contract(
        preview.blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    validate_plugin_material(candidate_material, blueprint=preview.blueprint)

    provenance = preview.blueprint["provenance"]
    return project._commit_revision(
        preview.blueprint,
        branch=selected_branch,
        actor=str(provenance["actor"]),
        reason=str(provenance["change_reason"]),
        allow_audio_material_change=False,
        allow_routing_material_change=False,
        allow_native_automation_change=False,
        allow_plugin_material_change=True,
    )
