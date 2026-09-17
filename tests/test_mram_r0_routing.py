from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from musica.contracts import ContractError, validate_contract
from musica.creative import compose_blueprint
from musica.routing_contracts import (
    build_routing_plan,
    empty_routing_material,
    validate_blueprint_routing,
    validate_routing_material,
    validate_routing_plan,
)

ROOT = Path(__file__).resolve().parents[1]
INTENT = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def _material() -> dict:
    return {
        "material_version": "0",
        "mode": "explicit_routing",
        "nodes": [
            {
                "node_id": "BUS-001",
                "order": 0,
                "name": "Music Bus",
                "node_type": "group",
                "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
                "output_node_id": "MASTER-001",
            },
            {
                "node_id": "RETURN-001",
                "order": 1,
                "name": "Ambience Return",
                "node_type": "return",
                "mixer": {"gain_db": -3.0, "pan": 0.0, "mute": False},
                "output_node_id": "MASTER-001",
            },
            {
                "node_id": "MASTER-001",
                "order": 2,
                "name": "Master",
                "node_type": "master",
                "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
                "output_node_id": None,
            },
        ],
        "track_outputs": [
            {"track_id": "AT-001", "target_node_id": "BUS-001"},
            {"track_id": "AT-002", "target_node_id": "MASTER-001"},
        ],
        "sends": [
            {
                "send_id": "SEND-001",
                "source": {"kind": "track", "source_id": "AT-001"},
                "target_node_id": "RETURN-001",
                "gain_db": -6.0,
                "tap": "post_fader",
            }
        ],
    }


def _blueprint_with_audio_tracks() -> dict:
    intent = json.loads(INTENT.read_text(encoding="utf-8"))
    blueprint = compose_blueprint(intent)
    blueprint["materials"]["audio"] = {
        "material_version": "0",
        "mode": "audio_tracks",
        "tracks": [
            {
                "track_id": "AT-001",
                "order": 0,
                "name": "A",
                "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False, "solo": False},
                "clips": [],
            },
            {
                "track_id": "AT-002",
                "order": 1,
                "name": "B",
                "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False, "solo": False},
                "clips": [],
            },
        ],
    }
    blueprint["provenance"].setdefault("selected_mechanisms", []).append(
        "audio_edit_candidate:mram-r0-fixture"
    )
    return blueprint


def test_valid_routing_graph_lowers_deterministically() -> None:
    material = _material()
    validate_routing_material(material, track_ids=["AT-001", "AT-002"])
    plan_a = build_routing_plan(material, track_ids=["AT-002", "AT-001"])
    plan_b = build_routing_plan(copy.deepcopy(material), track_ids=["AT-001", "AT-002"])
    assert plan_a == plan_b
    validate_routing_plan(plan_a)
    assert [node["node_id"] for node in plan_a["nodes"]] == [
        "BUS-001",
        "RETURN-001",
        "MASTER-001",
    ]
    assert plan_a["master_node_id"] == "MASTER-001"
    assert plan_a["classification"] == "derived_noncanonical"


def test_empty_routing_remains_backward_compatible() -> None:
    material = empty_routing_material()
    validate_routing_material(material, track_ids=["AT-001"])
    plan = build_routing_plan(material, track_ids=["AT-001"])
    assert plan["nodes"] == []
    assert plan["track_outputs"] == []
    assert plan["master_node_id"] is None


def test_explicit_routing_requires_every_known_track_once() -> None:
    material = _material()
    material["track_outputs"].pop()
    with pytest.raises(ContractError, match="map every known audio track"):
        validate_routing_material(material, track_ids=["AT-001", "AT-002"])


def test_unknown_route_target_fails_closed() -> None:
    material = _material()
    material["track_outputs"][0]["target_node_id"] = "MISSING"
    with pytest.raises(ContractError, match="unknown output node"):
        validate_routing_material(material, track_ids=["AT-001", "AT-002"])


def test_node_send_cycle_fails_closed() -> None:
    material = _material()
    material["nodes"][0]["output_node_id"] = "RETURN-001"
    material["nodes"][1]["output_node_id"] = "BUS-001"
    with pytest.raises(ContractError, match="acyclic"):
        validate_routing_material(material, track_ids=["AT-001", "AT-002"])


def test_master_cannot_source_send() -> None:
    material = _material()
    material["sends"].append(
        {
            "send_id": "SEND-002",
            "source": {"kind": "node", "source_id": "MASTER-001"},
            "target_node_id": "RETURN-001",
            "gain_db": -12.0,
            "tap": "post_fader",
        }
    )
    with pytest.raises(ContractError, match="master node cannot source"):
        validate_routing_material(material, track_ids=["AT-001", "AT-002"])


def test_noncanonical_node_order_fails_closed() -> None:
    material = _material()
    material["nodes"][0], material["nodes"][1] = material["nodes"][1], material["nodes"][0]
    with pytest.raises(ContractError, match="canonical order"):
        validate_routing_material(material, track_ids=["AT-001", "AT-002"])


def test_blueprint_nonempty_routing_authority_remains_closed() -> None:
    blueprint = _blueprint_with_audio_tracks()
    blueprint["materials"]["routing"] = _material()

    validate_blueprint_routing(blueprint, allow_nonempty=True)
    with pytest.raises(ContractError, match="does not grant accepted non-empty routing"):
        validate_contract(blueprint, "music-blueprint-v0.schema.json")


def test_blueprint_absent_or_empty_routing_remains_valid() -> None:
    intent = json.loads(INTENT.read_text(encoding="utf-8"))
    blueprint = compose_blueprint(intent)
    validate_contract(blueprint, "music-blueprint-v0.schema.json")

    blueprint["materials"]["routing"] = empty_routing_material()
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
