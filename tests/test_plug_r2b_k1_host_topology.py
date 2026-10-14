"""PLUG-R2B K1: only an exact existing accepted-shaped 2-bus graph is eligible."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from musica.contracts import ContractError
from musica.plugin_host_topology import exact_two_bus_host_topology
from test_mram_r1_routing_authority_mixer import _accept_audio


def _topology(tmp_path: Path) -> dict:
    _, blueprint = _accept_audio(tmp_path)
    value = copy.deepcopy(blueprint)
    value["materials"]["routing"] = {
        "material_version": "0", "mode": "explicit_routing",
        "nodes": [
            {"node_id": "BUS-001", "order": 0, "name": "A Bus", "node_type": "bus",
             "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
             "output_node_id": "MASTER-001"},
            {"node_id": "BUS-002", "order": 1, "name": "B Bus", "node_type": "bus",
             "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
             "output_node_id": "MASTER-001"},
            {"node_id": "MASTER-001", "order": 2, "name": "Master", "node_type": "master",
             "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
             "output_node_id": None},
        ],
        "track_outputs": [
            {"track_id": "AT-001", "target_node_id": "BUS-001"},
            {"track_id": "AT-002", "target_node_id": "BUS-002"},
        ],
        "sends": [],
    }
    return value


def test_two_bus_gate_derives_stable_exact_owners_without_authority(tmp_path):
    blue = _topology(tmp_path)
    derived = exact_two_bus_host_topology(blue)
    assert derived["master_node_id"] == "MASTER-001"
    assert derived["paths"] == [
        {"track_id": "AT-001", "bus_node_id": "BUS-001"},
        {"track_id": "AT-002", "bus_node_id": "BUS-002"},
    ]
    assert not derived["accepted_host_plugin_authority"]
    assert not derived["algorithmic_latency_known"]
    assert not derived["compensation_executed"]
    assert derived == exact_two_bus_host_topology(copy.deepcopy(blue))


@pytest.mark.parametrize("change", [
    "send", "same_bus", "direct_master", "group_instead_of_bus",
    "extra_node", "no_master", "ambiguous_branch",
])
def test_unsupported_topology_fails_closed(tmp_path, change):
    blue = _topology(tmp_path)
    routing = blue["materials"]["routing"]
    if change == "send":
        routing["sends"] = [{
            "send_id": "SEND-001", "source": {"kind": "track", "source_id": "AT-001"},
            "target_node_id": "BUS-002", "gain_db": 0.0, "tap": "post_fader",
        }]
    elif change == "same_bus":
        routing["track_outputs"][1]["target_node_id"] = "BUS-001"
    elif change == "direct_master":
        routing["track_outputs"][1]["target_node_id"] = "MASTER-001"
    elif change == "group_instead_of_bus":
        routing["nodes"][0]["node_type"] = "group"
    elif change == "extra_node":
        routing["nodes"].append({
            "node_id": "RETURN-001", "order": 3, "name": "Extra",
            "node_type": "return", "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
            "output_node_id": "MASTER-001",
        })
    elif change == "no_master":
        routing["nodes"][2]["node_type"] = "group"
    else:
        routing["nodes"][0]["output_node_id"] = "BUS-002"
    with pytest.raises(ContractError):
        exact_two_bus_host_topology(blue)
