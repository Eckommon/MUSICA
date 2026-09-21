"""MRAM-R1 trusted routing Preview→Accept authority.

Routing edits are source-bound, non-canonical previews. Explicit Accept revalidates the
exact accepted source, current audio-track identities and the resulting DAG before
using the Project Engine's narrow routing-authorized commit boundary.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any

from .audio_contracts import audio_material_from_blueprint, validate_project_blueprint_audio
from .audio_edit import audio_material_sha256, blueprint_sha256
from .contracts import ContractError, validate_contract, validate_revision
from .evidence import canonical_json_bytes
from .routing_contracts import (
    empty_routing_material,
    routing_material_from_blueprint,
    routing_material_sha256,
    validate_blueprint_routing,
    validate_routing_material,
)


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
    validate_contract(value, "routing-authority-result-v0.schema.json")
    return value


def _conflict(
    ordinal: int,
    code: str,
    reason: str,
    *,
    track_id: str | None = None,
    node_id: str | None = None,
    send_id: str | None = None,
    rule_id: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "conflict_id": f"MRAM-R1-C-{ordinal:03d}",
        "code": code,
        "reason": reason,
    }
    if track_id is not None:
        value["track_id"] = track_id
    if node_id is not None:
        value["node_id"] = node_id
    if send_id is not None:
        value["send_id"] = send_id
    if rule_id is not None:
        value["rule_id"] = rule_id
    return value


def _revision_id(parent: dict[str, Any], candidate: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json_bytes(candidate)).hexdigest()[:16]
    return f"{parent['project']['revision_id']}-routing-{digest}"


def _actor_for_blueprint(kind: str) -> str:
    return "deterministic_transform" if kind == "system" else kind


def _sort_material(material: dict[str, Any]) -> None:
    material["nodes"].sort(key=lambda node: (int(node["order"]), str(node["node_id"])))
    material["track_outputs"].sort(key=lambda item: str(item["track_id"]))
    material["sends"].sort(key=lambda send: str(send["send_id"]))


def _node(material: dict[str, Any], node_id: str) -> dict[str, Any] | None:
    return next(
        (item for item in material["nodes"] if str(item["node_id"]) == node_id),
        None,
    )


def _send(material: dict[str, Any], send_id: str) -> dict[str, Any] | None:
    return next(
        (item for item in material["sends"] if str(item["send_id"]) == send_id),
        None,
    )


def _track_output(material: dict[str, Any], track_id: str) -> dict[str, Any] | None:
    return next(
        (item for item in material["track_outputs"] if str(item["track_id"]) == track_id),
        None,
    )


@dataclass(frozen=True)
class RoutingEditPreview:
    authority_result: dict[str, Any]
    blueprint: dict[str, Any] | None
    source_revision_id: str
    source_blueprint_sha256: str
    source_audio_material_sha256: str
    source_routing_material_sha256: str
    candidate_blueprint_sha256: str | None
    candidate_routing_material_sha256: str | None
    changed_node_ids: list[str]
    changed_send_ids: list[str]
    changed_track_ids: list[str]
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
            "candidate_blueprint_sha256": self.candidate_blueprint_sha256,
            "candidate_routing_material_sha256": self.candidate_routing_material_sha256,
            "changed_node_ids": list(self.changed_node_ids),
            "changed_send_ids": list(self.changed_send_ids),
            "changed_track_ids": list(self.changed_track_ids),
            "revision_conflicts": copy.deepcopy(self.revision_conflicts),
        }


def _blocked(
    parent: dict[str, Any],
    candidate: dict[str, Any],
    conflicts: list[dict[str, Any]],
) -> RoutingEditPreview:
    material = routing_material_from_blueprint(parent)
    assert material is not None
    return RoutingEditPreview(
        authority_result=_authority_result(str(candidate["candidate_id"]), conflicts=conflicts),
        blueprint=None,
        source_revision_id=str(parent["project"]["revision_id"]),
        source_blueprint_sha256=blueprint_sha256(parent),
        source_audio_material_sha256=audio_material_sha256(parent),
        source_routing_material_sha256=routing_material_sha256(material),
        candidate_blueprint_sha256=None,
        candidate_routing_material_sha256=None,
        changed_node_ids=[],
        changed_send_ids=[],
        changed_track_ids=[],
        revision_conflicts=[],
    )


def build_routing_edit_preview(
    project: Any,
    parent_blueprint: dict[str, Any],
    candidate: dict[str, Any],
    *,
    branch: str | None = None,
    revision_id: str | None = None,
) -> RoutingEditPreview:
    """Resolve one source-bound routing candidate into a non-canonical Preview."""

    validate_contract(
        parent_blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    validate_contract(candidate, "routing-edit-candidate-v0.schema.json")
    validate_project_blueprint_audio(project, parent_blueprint)
    validate_blueprint_routing(parent_blueprint, allow_nonempty=True)

    selected_branch = branch or project.current_branch()
    parent_revision_id = str(parent_blueprint["project"]["revision_id"])
    parent_routing = routing_material_from_blueprint(parent_blueprint)
    assert parent_routing is not None
    source = candidate["source"]

    source_blueprint_hash = blueprint_sha256(parent_blueprint)
    source_audio_hash = audio_material_sha256(parent_blueprint)
    source_routing_hash = routing_material_sha256(parent_routing)
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
    if project.head_revision_id(selected_branch) != parent_revision_id:
        stale.append("project branch HEAD no longer equals source revision")
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

    audio = audio_material_from_blueprint(parent_blueprint)
    assert audio is not None
    track_ids = [str(track["track_id"]) for track in audio["tracks"]]
    known_tracks = set(track_ids)

    working = copy.deepcopy(parent_blueprint)
    material = copy.deepcopy(parent_routing)
    changed_nodes: set[str] = set()
    changed_sends: set[str] = set()
    changed_tracks: set[str] = set()
    conflicts: list[dict[str, Any]] = []

    for ordinal, operation in enumerate(candidate["operations"], start=1):
        op = str(operation["op"])
        if op == "ADD_NODE":
            node = copy.deepcopy(operation["node"])
            node_id = str(node["node_id"])
            if _node(material, node_id) is not None:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        f"routing node_id already exists: {node_id}",
                        node_id=node_id,
                    )
                )
                continue
            material["nodes"].append(node)
            changed_nodes.add(node_id)
            continue

        if op == "SET_TRACK_OUTPUT":
            track_id = str(operation["track_id"])
            target_id = str(operation["target_node_id"])
            if track_id not in known_tracks:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNKNOWN_TRACK",
                        f"unknown audio track: {track_id}",
                        track_id=track_id,
                    )
                )
                continue
            current = _track_output(material, track_id)
            if current is None:
                material["track_outputs"].append(
                    {"track_id": track_id, "target_node_id": target_id}
                )
            else:
                current["target_node_id"] = target_id
            changed_tracks.add(track_id)
            continue

        if op == "ADD_SEND":
            send = copy.deepcopy(operation["send"])
            send_id = str(send["send_id"])
            if _send(material, send_id) is not None:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        f"routing send_id already exists: {send_id}",
                        send_id=send_id,
                    )
                )
                continue
            material["sends"].append(send)
            changed_sends.add(send_id)
            continue

        send_id = str(operation.get("send_id", ""))
        if op in {"REMOVE_SEND", "SET_SEND_GAIN"}:
            current_send = _send(material, send_id)
            if current_send is None:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNKNOWN_SEND",
                        f"unknown routing send: {send_id}",
                        send_id=send_id,
                    )
                )
                continue
            if op == "REMOVE_SEND":
                material["sends"] = [
                    item
                    for item in material["sends"]
                    if str(item["send_id"]) != send_id
                ]
            else:
                current_send["gain_db"] = operation["gain_db"]
            changed_sends.add(send_id)
            continue

        if op == "SET_NODE_MIXER":
            node_id = str(operation["node_id"])
            current_node = _node(material, node_id)
            if current_node is None:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNKNOWN_NODE",
                        f"unknown routing node: {node_id}",
                        node_id=node_id,
                    )
                )
                continue
            current_node["mixer"] = copy.deepcopy(operation["mixer"])
            changed_nodes.add(node_id)
            continue

        conflicts.append(
            _conflict(
                ordinal,
                "UNREPRESENTABLE_EDIT",
                f"unsupported routing operation: {op}",
            )
        )

    if conflicts:
        return _blocked(parent_blueprint, candidate, conflicts)

    _sort_material(material)
    try:
        validate_routing_material(material, track_ids=track_ids)
    except ContractError as exc:
        return _blocked(
            parent_blueprint,
            candidate,
            [_conflict(1, "INVALID_GRAPH", str(exc))],
        )

    working["materials"]["routing"] = material
    working["project"]["parent_revision_id"] = parent_revision_id
    working["project"]["revision_id"] = revision_id or _revision_id(parent_blueprint, candidate)
    provenance = working["provenance"]
    provenance["actor"] = _actor_for_blueprint(str(candidate["actor"]["kind"]))
    provenance["change_reason"] = candidate["reason"]
    provenance["source_revision"] = parent_revision_id
    selected = list(provenance.get("selected_mechanisms", []))
    selected.append(f"routing_edit_candidate:{candidate['candidate_id']}")
    selected.extend(f"routing_edit_operation:{value}" for value in operation_ids)
    provenance["selected_mechanisms"] = selected

    try:
        validate_contract(
            working,
            "music-blueprint-v0.schema.json",
            allow_nonempty_routing=True,
        )
        validate_project_blueprint_audio(project, working)
        validate_blueprint_routing(working, allow_nonempty=True)
    except ContractError as exc:
        return _blocked(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", str(exc))],
        )

    if audio_material_sha256(working) != source_audio_hash:
        return _blocked(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", "routing edit changed native audio material")],
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
            code = (
                "HARD_LOCK_VIOLATION"
                if item.rule_type in {"lock", "note_lock", "automation_lock"}
                else "CONSTRAINT_VIOLATION"
                if item.rule_type == "constraint"
                else "UNREPRESENTABLE_EDIT"
            )
            mapped.append(
                _conflict(ordinal, code, item.reason, rule_id=item.rule_id)
            )
        return _blocked(parent_blueprint, candidate, mapped)

    return RoutingEditPreview(
        authority_result=_authority_result(str(candidate["candidate_id"])),
        blueprint=working,
        source_revision_id=parent_revision_id,
        source_blueprint_sha256=source_blueprint_hash,
        source_audio_material_sha256=source_audio_hash,
        source_routing_material_sha256=source_routing_hash,
        candidate_blueprint_sha256=blueprint_sha256(working),
        candidate_routing_material_sha256=routing_material_sha256(material),
        changed_node_ids=sorted(changed_nodes),
        changed_send_ids=sorted(changed_sends),
        changed_track_ids=sorted(changed_tracks),
        revision_conflicts=[item.as_dict() for item in revision_conflicts],
    )


def accept_routing_edit_preview(
    project: Any,
    preview: RoutingEditPreview,
    *,
    branch: str | None = None,
) -> dict[str, Any]:
    """Explicitly accept one READY routing Preview through the trusted R1 boundary."""

    if not preview.ready or preview.blueprint is None:
        raise ContractError("only READY_FOR_PREVIEW routing candidates may be accepted")

    selected_branch = branch or project.current_branch()
    if project.head_revision_id(selected_branch) != preview.source_revision_id:
        raise ContractError("routing Preview source is stale: project HEAD changed")

    current = project.read_revision(preview.source_revision_id)
    current_routing = routing_material_from_blueprint(current)
    assert current_routing is not None
    if blueprint_sha256(current) != preview.source_blueprint_sha256:
        raise ContractError("routing Preview source Blueprint hash is stale")
    if audio_material_sha256(current) != preview.source_audio_material_sha256:
        raise ContractError("routing Preview source audio material hash is stale")
    if routing_material_sha256(current_routing) != preview.source_routing_material_sha256:
        raise ContractError("routing Preview source routing material hash is stale")

    if blueprint_sha256(preview.blueprint) != preview.candidate_blueprint_sha256:
        raise ContractError("routing Preview candidate Blueprint hash changed")
    candidate_routing = routing_material_from_blueprint(preview.blueprint)
    assert candidate_routing is not None
    if routing_material_sha256(candidate_routing) != preview.candidate_routing_material_sha256:
        raise ContractError("routing Preview candidate routing material hash changed")
    if audio_material_sha256(preview.blueprint) != preview.source_audio_material_sha256:
        raise ContractError("routing Preview candidate changed native audio material")

    validate_contract(
        preview.blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    validate_project_blueprint_audio(project, preview.blueprint)
    validate_blueprint_routing(preview.blueprint, allow_nonempty=True)
    if preview.blueprint["project"].get("parent_revision_id") != preview.source_revision_id:
        raise ContractError("routing Preview candidate parent_revision_id is stale")

    provenance = preview.blueprint["provenance"]
    return project._commit_revision(
        preview.blueprint,
        branch=selected_branch,
        actor=str(provenance["actor"]),
        reason=str(provenance["change_reason"]),
        allow_audio_material_change=False,
        allow_routing_material_change=True,
    )
