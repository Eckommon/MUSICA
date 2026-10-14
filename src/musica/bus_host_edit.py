"""Trusted K1-B accepted simulated bus processor Preview -> explicit Accept.

This is NOT a native VST/CLAP/AU host. The accepted processor has distinct
synthetic algorithmic and creative delays. Derived audio has no mutation rights.
"""
from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any

from .audio_edit import audio_material_sha256, blueprint_sha256
from .automation_edit import automation_material_sha256
from .bus_host_material import (
    accepted_bus_host_sha256,
    bus_host_material_from_blueprint,
    bus_host_material_sha256,
    validate_bus_host_material,
)
from .contracts import ContractError, validate_contract, validate_revision
from .evidence import canonical_json_bytes
from .plugin_reference import accepted_plugin_material_sha256
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256


def _source(blueprint: dict[str, Any]) -> dict[str, str]:
    routing = routing_material_from_blueprint(blueprint)
    if routing is None:
        raise ContractError("K1-B source lacks routing identity")
    return {
        "project_id": str(blueprint["project"]["project_id"]),
        "revision_id": str(blueprint["project"]["revision_id"]),
        "blueprint_sha256": blueprint_sha256(blueprint),
        "audio_material_sha256": audio_material_sha256(blueprint),
        "routing_material_sha256": routing_material_sha256(routing),
        "automation_material_sha256": automation_material_sha256(blueprint),
        "legacy_plugin_material_sha256": accepted_plugin_material_sha256(blueprint),
        "bus_host_material_sha256": accepted_bus_host_sha256(blueprint),
    }


def source_for_bus_host_candidate(blueprint: dict[str, Any]) -> dict[str, str]:
    """Exact read-only source signature for the proposal UI/API."""
    validate_contract(blueprint, "music-blueprint-v0.schema.json", allow_nonempty_routing=True)
    return _source(blueprint)


@dataclass(frozen=True)
class BusHostPreview:
    status: str
    reason: str
    blueprint: dict[str, Any] | None
    source: dict[str, str]
    proposed_material_sha256: str | None
    candidate_blueprint_sha256: str | None
    changed_instance_ids: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return self.status == "READY_FOR_PREVIEW"


def _blocked(source: dict[str, str], why: str) -> BusHostPreview:
    return BusHostPreview(
        status="BLOCKED", reason=why, blueprint=None, source=source,
        proposed_material_sha256=None, candidate_blueprint_sha256=None,
        changed_instance_ids=(),
    )


def build_bus_host_edit_preview(
    project: Any,
    parent_blueprint: dict[str, Any],
    candidate: dict[str, Any],
    *,
    branch: str | None = None,
) -> BusHostPreview:
    """Build noncanonical preview from persisted exact accepted revision."""
    validate_contract(parent_blueprint, "music-blueprint-v0.schema.json", allow_nonempty_routing=True)
    validate_contract(candidate, "bus-host-edit-candidate-v0.schema.json")
    source = _source(parent_blueprint)
    selected = branch or project.current_branch()
    if (
        candidate["source"] != source
        or project.head_revision_id(selected) != source["revision_id"]
    ):
        return _blocked(source, "stale candidate source or branch HEAD")
    persisted = project.read_revision(source["revision_id"])
    if _source(persisted) != source or persisted != parent_blueprint:
        return _blocked(source, "forged or stale persisted parent source")

    proposal = copy.deepcopy(candidate["proposed_material"])
    try:
        validate_bus_host_material(proposal, blueprint=parent_blueprint)
    except ContractError as exc:
        return _blocked(source, str(exc))
    accepted_before = bus_host_material_from_blueprint(parent_blueprint)
    if proposal == accepted_before:
        return _blocked(source, "no-op bus-host proposal")
    working = copy.deepcopy(parent_blueprint)
    working.setdefault("materials", {})["bus_plugins"] = proposal
    working["project"]["parent_revision_id"] = source["revision_id"]
    candidate_hash = hashlib.sha256(canonical_json_bytes(candidate)).hexdigest()[:16]
    working["project"]["revision_id"] = (
        f"{source['revision_id']}-bus-host-{candidate_hash}"
    )
    actor_kind = str(candidate["actor"]["kind"])
    working["provenance"]["actor"] = (
        "deterministic_transform" if actor_kind == "system" else actor_kind
    )
    working["provenance"]["change_reason"] = str(candidate["reason"])
    working["provenance"]["source_revision"] = source["revision_id"]

    try:
        validate_contract(working, "music-blueprint-v0.schema.json", allow_nonempty_routing=True)
        conflicts = validate_revision(
            parent_blueprint, working, allow_nonempty_routing=True
        )
        if any(c.status == "BLOCKED" for c in conflicts):
            return _blocked(source, "; ".join(c.reason for c in conflicts if c.status == "BLOCKED"))
    except ContractError as exc:
        return _blocked(source, str(exc))

    before = {i["instance_id"]: i for i in accepted_before["instances"]}
    after = {i["instance_id"]: i for i in proposal["instances"]}
    changed = tuple(sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k)))
    return BusHostPreview(
        status="READY_FOR_PREVIEW", reason="exact source bound; explicit Accept required",
        blueprint=working, source=source,
        proposed_material_sha256=bus_host_material_sha256(proposal),
        candidate_blueprint_sha256=blueprint_sha256(working),
        changed_instance_ids=changed,
    )


def accept_bus_host_edit_preview(
    project: Any,
    preview: BusHostPreview,
    *,
    branch: str | None = None,
) -> dict[str, Any]:
    """Commit exactly one approved host material revision, never derived output."""
    if not preview.ready or preview.blueprint is None:
        raise ContractError("only READY_FOR_PREVIEW bus-host candidate can be accepted")
    selected = branch or project.current_branch()
    if project.head_revision_id(selected) != preview.source["revision_id"]:
        raise ContractError("bus-host Preview source HEAD is stale")
    current = project.read_revision(preview.source["revision_id"])
    if _source(current) != preview.source:
        raise ContractError("bus-host Preview source material is stale")
    if blueprint_sha256(preview.blueprint) != preview.candidate_blueprint_sha256:
        raise ContractError("bus-host Preview candidate Blueprint was changed")
    material = bus_host_material_from_blueprint(preview.blueprint)
    if bus_host_material_sha256(material) != preview.proposed_material_sha256:
        raise ContractError("bus-host Preview material was changed")
    if preview.blueprint["project"].get("parent_revision_id") != preview.source["revision_id"]:
        raise ContractError("bus-host Preview parent revision mismatch")
    validate_contract(preview.blueprint, "music-blueprint-v0.schema.json", allow_nonempty_routing=True)
    validate_bus_host_material(material, blueprint=preview.blueprint)
    changes = validate_revision(current, preview.blueprint, allow_nonempty_routing=True)
    if any(x.status == "BLOCKED" for x in changes):
        raise ContractError("bus-host Preview blocked by revision conflict")
    provenance = preview.blueprint["provenance"]
    return project._commit_revision(
        preview.blueprint,
        branch=selected,
        actor=str(provenance["actor"]),
        reason=str(provenance["change_reason"]),
        allow_audio_material_change=False,
        allow_routing_material_change=False,
        allow_native_automation_change=False,
        allow_plugin_material_change=False,
        allow_bus_plugin_material_change=True,
    )
