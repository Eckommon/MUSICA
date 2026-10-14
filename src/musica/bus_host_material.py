"""K1-B accepted simulated bus-plugin material; never legacy R1 creative delay.

The material lives on an immutable accepted Blueprint only through a separate
trusted authority path. R1 master plugins and simulated *algorithmic* latency
remain explicitly distinct.
"""
from __future__ import annotations
import copy
import hashlib
from typing import Any

from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .plugin_host_topology import exact_two_bus_host_topology

ENGINE_ID = "musica-simulated-bus-latency-v0"


def empty_bus_host_material() -> dict[str, Any]:
    return {
        "material_version": "0",
        "classification": "accepted_simulated_bus_host_material",
        "instances": [],
    }


def bus_host_material_from_blueprint(blueprint: dict[str, Any]) -> dict[str, Any]:
    materials = blueprint.get("materials")
    value = materials.get("bus_plugins") if isinstance(materials, dict) else None
    if value is None:
        return empty_bus_host_material()
    if not isinstance(value, dict):
        raise ContractError("materials.bus_plugins must be an object")
    validate_contract(value, "accepted-bus-host-material-v0.schema.json")
    return value


def bus_host_material_sha256(material: dict[str, Any]) -> str:
    validate_contract(material, "accepted-bus-host-material-v0.schema.json")
    return hashlib.sha256(canonical_json_bytes(material)).hexdigest()


def accepted_bus_host_sha256(blueprint: dict[str, Any]) -> str:
    return bus_host_material_sha256(bus_host_material_from_blueprint(blueprint))


def validate_bus_host_material(
    material: dict[str, Any], *, blueprint: dict[str, Any]
) -> None:
    """Enforce independent bus IDs and exact supported accepted topology."""
    validate_contract(material, "accepted-bus-host-material-v0.schema.json")
    instances = material["instances"]
    if not instances:
        return
    topology = exact_two_bus_host_topology(blueprint)
    expected_buses = {p["bus_node_id"] for p in topology["paths"]}
    ids = [str(i["instance_id"]) for i in instances]
    buses = [str(i["owner_bus_id"]) for i in instances]
    if len(ids) != len(set(ids)):
        raise ContractError("K1-B duplicate bus processor instance_id")
    if len(buses) != len(set(buses)):
        raise ContractError("K1-B supports at most one simulated plugin per bus")
    if buses != sorted(buses):
        raise ContractError("K1-B bus plugins must use canonical owner_bus_id order")
    if not set(buses) <= expected_buses:
        raise ContractError("K1-B unknown or unsupported accepted bus owner")
    for instance in instances:
        for field in ("algorithmic_latency_frames", "creative_delay_frames"):
            n = instance[field]
            if type(n) is not int or not 0 <= n <= 4096:
                raise ContractError(f"K1-B invalid {field}")


def validate_blueprint_bus_host(blueprint: dict[str, Any]) -> None:
    validate_bus_host_material(
        bus_host_material_from_blueprint(blueprint), blueprint=blueprint
    )


def bus_host_latency_config(blueprint: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Reconstruct exact K0-compatible config ONLY from accepted source."""
    material = bus_host_material_from_blueprint(blueprint)
    validate_bus_host_material(material, blueprint=blueprint)
    topology = exact_two_bus_host_topology(blueprint)
    configs = {
        path["bus_node_id"]: {
            "algorithmic_latency_frames": 0,
            "creative_delay_frames": 0,
            "bypass": False,
        }
        for path in topology["paths"]
    }
    for instance in material["instances"]:
        configs[str(instance["owner_bus_id"])] = {
            "algorithmic_latency_frames": int(instance["algorithmic_latency_frames"]),
            "creative_delay_frames": int(instance["creative_delay_frames"]),
            "bypass": bool(instance["bypass"]),
        }
    return configs
