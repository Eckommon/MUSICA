"""PLUG-R2B K1 read-only eligibility gate for an exact accepted two-bus topology.

This proves *routing shape only*. It does not authorize plugin insertion, derive
algorithmic latency from R1 creative delay or process an accepted host signal.
"""
from __future__ import annotations

from typing import Any

from .audio_contracts import audio_material_from_blueprint
from .contracts import ContractError
from .routing_contracts import (
    routing_material_from_blueprint,
    routing_material_sha256,
    validate_blueprint_routing,
)


def exact_two_bus_host_topology(blueprint: dict[str, Any]) -> dict[str, Any]:
    """Identify 2 tracks -> 2 buses -> 1 master from validated accepted state.

    No sends, hidden branch, direct track-to-master path, unknown owner or
    inferred track display name is accepted. Pure non-authoritative projection.
    """
    validate_blueprint_routing(blueprint, allow_nonempty=True)
    material = routing_material_from_blueprint(blueprint)
    audio = audio_material_from_blueprint(blueprint)
    if audio is None:
        raise ContractError("PLUG-R2B K1 requires accepted audio material")
    tracks = [str(item["track_id"]) for item in audio["tracks"]]
    if len(tracks) != 2 or len(set(tracks)) != 2:
        raise ContractError("PLUG-R2B K1 requires exactly two distinct accepted tracks")
    if material["sends"]:
        raise ContractError("PLUG-R2B K1 prohibits sends and side paths")
    nodes = material["nodes"]
    buses = [item for item in nodes if item["node_type"] == "bus"]
    masters = [item for item in nodes if item["node_type"] == "master"]
    if len(nodes) != 3 or len(buses) != 2 or len(masters) != 1:
        raise ContractError("PLUG-R2B K1 requires exactly two buses and one master")
    master_id = str(masters[0]["node_id"])
    bus_ids = {str(item["node_id"]) for item in buses}
    if len(bus_ids) != 2 or any(
        str(item["output_node_id"]) != master_id for item in buses
    ):
        raise ContractError("PLUG-R2B K1 buses must converge directly on master")
    assignments = material["track_outputs"]
    if len(assignments) != 2:
        raise ContractError("PLUG-R2B K1 requires exactly two routing assignments")
    targets = [str(item["target_node_id"]) for item in assignments]
    if set(targets) != bus_ids or len(set(targets)) != 2:
        raise ContractError("PLUG-R2B K1 each track must own a distinct bus")
    if set(str(item["track_id"]) for item in assignments) != set(tracks):
        raise ContractError("PLUG-R2B K1 track identity mismatch")
    return {
        "topology_version": "0",
        "classification": "derived_noncanonical_topology_eligibility_only",
        "routing_material_sha256": routing_material_sha256(material),
        "master_node_id": master_id,
        "paths": [
            {
                "track_id": str(item["track_id"]),
                "bus_node_id": str(item["target_node_id"]),
            }
            for item in assignments
        ],
        "accepted_host_plugin_authority": False,
        "algorithmic_latency_known": False,
        "compensation_executed": False,
    }
