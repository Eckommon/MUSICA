"""MRAM-R0 bounded routing contracts and deterministic signal-flow lowering.

R0 defines topology semantics only. Non-empty accepted Blueprint routing remains
fail-closed until a later trusted Preview→Accept authority rung explicitly opens it.
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any

from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes

EMPTY_ROUTING_MATERIAL: dict[str, Any] = {
    "material_version": "0",
    "mode": "explicit_routing",
    "nodes": [],
    "track_outputs": [],
    "sends": [],
}


def empty_routing_material() -> dict[str, Any]:
    return copy.deepcopy(EMPTY_ROUTING_MATERIAL)


def routing_material_from_blueprint(
    blueprint: dict[str, Any], *, materialize_empty: bool = True
) -> dict[str, Any] | None:
    materials = blueprint.get("materials", {})
    value = materials.get("routing") if isinstance(materials, dict) else None
    if value is None:
        return empty_routing_material() if materialize_empty else None
    if not isinstance(value, dict):
        raise ContractError("materials.routing must be an object")
    return value


def routing_material_sha256(material: dict[str, Any]) -> str:
    validate_contract(material, "routing-material-v0.schema.json")
    return hashlib.sha256(canonical_json_bytes(material)).hexdigest()


def _require_unique(values: list[Any], label: str) -> None:
    if len(values) != len(set(values)):
        raise ContractError(f"{label} must be unique")


def _node_key(node: dict[str, Any]) -> tuple[int, str]:
    return int(node["order"]), str(node["node_id"])


def _graph_edges(material: dict[str, Any]) -> dict[str, set[str]]:
    nodes = material["nodes"]
    edges = {str(node["node_id"]): set() for node in nodes}
    for node in nodes:
        source = str(node["node_id"])
        target = node.get("output_node_id")
        if target is not None:
            edges[source].add(str(target))
    for send in material["sends"]:
        source = send["source"]
        if source["kind"] == "node":
            edges[str(source["source_id"])].add(str(send["target_node_id"]))
    return edges


def _topological_node_ids(material: dict[str, Any]) -> list[str]:
    nodes = material["nodes"]
    if not nodes:
        return []
    node_map = {str(node["node_id"]): node for node in nodes}
    edges = _graph_edges(material)
    indegree = {node_id: 0 for node_id in node_map}
    for targets in edges.values():
        for target in targets:
            indegree[target] += 1
    ready = sorted(
        (node_id for node_id, degree in indegree.items() if degree == 0),
        key=lambda node_id: _node_key(node_map[node_id]),
    )
    ordered: list[str] = []
    while ready:
        node_id = ready.pop(0)
        ordered.append(node_id)
        for target in sorted(edges[node_id], key=lambda value: _node_key(node_map[value])):
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
                ready.sort(key=lambda value: _node_key(node_map[value]))
    if len(ordered) != len(node_map):
        raise ContractError("routing graph must be acyclic")
    return ordered


def validate_routing_material(
    material: dict[str, Any], *, track_ids: list[str] | tuple[str, ...] | None = None
) -> None:
    """Validate routing schema and cross-field topology invariants."""

    validate_contract(material, "routing-material-v0.schema.json")
    nodes = material["nodes"]
    outputs = material["track_outputs"]
    sends = material["sends"]

    node_ids = [str(node["node_id"]) for node in nodes]
    node_orders = [int(node["order"]) for node in nodes]
    _require_unique(node_ids, "routing node_id")
    _require_unique(node_orders, "routing node order")
    if nodes != sorted(nodes, key=_node_key):
        raise ContractError("routing nodes must use canonical order (order, node_id)")

    output_track_ids = [str(item["track_id"]) for item in outputs]
    _require_unique(output_track_ids, "routing track output track_id")
    if output_track_ids != sorted(output_track_ids):
        raise ContractError("routing track_outputs must use canonical track_id order")

    send_ids = [str(send["send_id"]) for send in sends]
    _require_unique(send_ids, "routing send_id")
    if send_ids != sorted(send_ids):
        raise ContractError("routing sends must use canonical send_id order")

    known_tracks: set[str] | None = None
    if track_ids is not None:
        normalized_tracks = [str(value) for value in track_ids]
        _require_unique(normalized_tracks, "routing source track_id")
        known_tracks = set(normalized_tracks)

    if not nodes:
        if outputs or sends:
            raise ContractError("empty routing graph cannot contain track outputs or sends")
        return

    node_map = {str(node["node_id"]): node for node in nodes}
    masters = [node for node in nodes if node["node_type"] == "master"]
    if len(masters) != 1:
        raise ContractError("non-empty routing graph must contain exactly one master node")
    master_id = str(masters[0]["node_id"])

    for node in nodes:
        node_id = str(node["node_id"])
        target = node.get("output_node_id")
        if node["node_type"] == "master":
            if target is not None:
                raise ContractError("routing master node must be the terminal sink")
            continue
        if target is None:
            raise ContractError(f"routing node {node_id} must declare output_node_id")
        target_id = str(target)
        if target_id not in node_map:
            raise ContractError(f"routing node {node_id} references unknown output node: {target_id}")
        if target_id == node_id:
            raise ContractError(f"routing node {node_id} cannot output to itself")

    for item in outputs:
        track_id = str(item["track_id"])
        target_id = str(item["target_node_id"])
        if target_id not in node_map:
            raise ContractError(f"routing track {track_id} references unknown output node: {target_id}")
        if known_tracks is not None and track_id not in known_tracks:
            raise ContractError(f"routing references unknown audio track_id: {track_id}")

    if known_tracks is not None and set(output_track_ids) != known_tracks:
        missing = sorted(known_tracks - set(output_track_ids))
        extra = sorted(set(output_track_ids) - known_tracks)
        raise ContractError(
            f"explicit routing must map every known audio track exactly once; missing={missing}, extra={extra}"
        )

    for send in sends:
        send_id = str(send["send_id"])
        source = send["source"]
        source_kind = str(source["kind"])
        source_id = str(source["source_id"])
        target_id = str(send["target_node_id"])
        if target_id not in node_map:
            raise ContractError(f"routing send {send_id} references unknown target node: {target_id}")
        if source_kind == "track":
            if known_tracks is not None and source_id not in known_tracks:
                raise ContractError(f"routing send {send_id} references unknown track: {source_id}")
        elif source_kind == "node":
            if source_id not in node_map:
                raise ContractError(f"routing send {send_id} references unknown source node: {source_id}")
            if source_id == master_id:
                raise ContractError("routing master node cannot source a send")
            if source_id == target_id:
                raise ContractError(f"routing send {send_id} cannot target its own source node")
        else:
            raise ContractError(f"unsupported routing send source kind: {source_kind}")

    _topological_node_ids(material)

    # Every non-master primary output chain must terminate at the unique master.
    for node in nodes:
        node_id = str(node["node_id"])
        if node_id == master_id:
            continue
        current = node_id
        visited: set[str] = set()
        while current != master_id:
            if current in visited:
                raise ContractError("routing primary output chain contains a cycle")
            visited.add(current)
            target = node_map[current].get("output_node_id")
            if target is None:
                raise ContractError(f"routing node {current} does not reach master {master_id}")
            current = str(target)


def validate_blueprint_routing(
    blueprint: dict[str, Any], *, allow_nonempty: bool = False
) -> None:
    """Validate optional Blueprint routing while preserving the R0 authority boundary."""

    material = routing_material_from_blueprint(blueprint, materialize_empty=False)
    if material is None:
        return

    from .audio_contracts import audio_material_from_blueprint

    audio = audio_material_from_blueprint(blueprint)
    assert audio is not None
    track_ids = [str(track["track_id"]) for track in audio["tracks"]]
    validate_routing_material(material, track_ids=track_ids)

    nonempty = bool(material["nodes"] or material["track_outputs"] or material["sends"])
    if nonempty and not allow_nonempty:
        raise ContractError(
            "MRAM-R0 does not grant accepted non-empty routing material authority"
        )


def validate_routing_plan(plan: dict[str, Any]) -> None:
    validate_contract(plan, "routing-plan-v0.schema.json")
    base = dict(plan)
    claimed = str(base.pop("routing_plan_sha256"))
    actual = hashlib.sha256(canonical_json_bytes(base)).hexdigest()
    if claimed != actual:
        raise ContractError("routing plan SHA-256 does not match canonical plan payload")

    nodes = plan["nodes"]
    node_ids = [str(node["node_id"]) for node in nodes]
    _require_unique(node_ids, "routing plan node_id")
    indices = [int(node["topological_index"]) for node in nodes]
    if indices != list(range(len(nodes))):
        raise ContractError("routing plan topological_index must be contiguous and ordered")

    source_tracks = [str(value) for value in plan["source"]["track_ids"]]
    if source_tracks != sorted(source_tracks):
        raise ContractError("routing plan source track_ids must use canonical sorted order")


def build_routing_plan(
    material: dict[str, Any], *, track_ids: list[str] | tuple[str, ...]
) -> dict[str, Any]:
    """Lower validated routing material into a deterministic derived signal-flow plan."""

    validate_routing_material(material, track_ids=track_ids)
    ordered_ids = _topological_node_ids(material)
    node_map = {str(node["node_id"]): node for node in material["nodes"]}
    masters = [str(node["node_id"]) for node in material["nodes"] if node["node_type"] == "master"]
    master_id = masters[0] if masters else None

    plan_nodes = []
    for index, node_id in enumerate(ordered_ids):
        node = node_map[node_id]
        plan_nodes.append(
            {
                "node_id": node_id,
                "order": int(node["order"]),
                "topological_index": index,
                "name": str(node["name"]),
                "node_type": str(node["node_type"]),
                "mixer": {
                    "gain_db": float(node["mixer"]["gain_db"]),
                    "pan": float(node["mixer"]["pan"]),
                    "mute": bool(node["mixer"]["mute"]),
                },
                "output_node_id": node.get("output_node_id"),
            }
        )

    plan_base: dict[str, Any] = {
        "plan_version": "0",
        "classification": "derived_noncanonical",
        "source": {
            "routing_material_sha256": routing_material_sha256(material),
            "track_ids": sorted(str(value) for value in track_ids),
        },
        "policy": {
            "graph_policy": "acyclic_fail_closed",
            "send_tap": "post_fader",
            "node_ordering": "topological_then_order_node_id",
            "master_policy": "exactly_one_sink_when_nonempty",
        },
        "nodes": plan_nodes,
        "track_outputs": [
            {
                "track_id": str(item["track_id"]),
                "target_node_id": str(item["target_node_id"]),
            }
            for item in material["track_outputs"]
        ],
        "sends": [
            {
                "send_id": str(send["send_id"]),
                "source_kind": str(send["source"]["kind"]),
                "source_id": str(send["source"]["source_id"]),
                "target_node_id": str(send["target_node_id"]),
                "gain_db": float(send["gain_db"]),
                "tap": "post_fader",
            }
            for send in material["sends"]
        ],
        "master_node_id": master_id,
    }
    plan = dict(plan_base)
    plan["routing_plan_sha256"] = hashlib.sha256(canonical_json_bytes(plan_base)).hexdigest()
    validate_routing_plan(plan)
    return plan
