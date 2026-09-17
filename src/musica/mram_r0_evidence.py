"""Generate deterministic evidence for MRAM-R0 routing contracts and DAG lowering."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Callable

from .contracts import ContractError, validate_contract
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .routing_contracts import (
    build_routing_plan,
    validate_blueprint_routing,
    validate_routing_material,
)

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "routing-material-v0.schema.json",
    ROOT / "schemas" / "routing-plan-v0.schema.json",
    ROOT / "schemas" / "music-blueprint-v0.schema.json",
    ROOT / "src" / "musica" / "contracts.py",
    ROOT / "src" / "musica" / "routing_contracts.py",
    ROOT / "src" / "musica" / "mram_r0_evidence.py",
    ROOT / "tests" / "test_mram_r0_routing.py",
    ROOT / ".github" / "workflows" / "mram-r0-routing-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _blocked(fn: Callable[[], None]) -> bool:
    try:
        fn()
    except ContractError:
        return True
    return False


def _material() -> dict[str, Any]:
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


def _blueprint_candidate(material: dict[str, Any]) -> dict[str, Any]:
    intent = json.loads(INTENT_PATH.read_text(encoding="utf-8"))
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
        "audio_edit_candidate:mram-r0-evidence-fixture"
    )
    blueprint["materials"]["routing"] = material
    return blueprint


def generate_mram_r0_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    track_ids = ["AT-001", "AT-002"]
    material = _material()
    validate_routing_material(material, track_ids=track_ids)
    plan = build_routing_plan(material, track_ids=track_ids)
    repeat = build_routing_plan(copy.deepcopy(material), track_ids=list(reversed(track_ids)))

    cycle = copy.deepcopy(material)
    cycle["nodes"][0]["output_node_id"] = "RETURN-001"
    cycle["nodes"][1]["output_node_id"] = "BUS-001"

    missing_target = copy.deepcopy(material)
    missing_target["track_outputs"][0]["target_node_id"] = "MISSING"

    missing_track = copy.deepcopy(material)
    missing_track["track_outputs"].pop()

    master_send = copy.deepcopy(material)
    master_send["sends"].append(
        {
            "send_id": "SEND-002",
            "source": {"kind": "node", "source_id": "MASTER-001"},
            "target_node_id": "RETURN-001",
            "gain_db": -12.0,
            "tap": "post_fader",
        }
    )

    candidate = _blueprint_candidate(material)
    validate_blueprint_routing(candidate, allow_nonempty=True)
    canonical_acceptance_blocked = _blocked(
        lambda: validate_contract(candidate, "music-blueprint-v0.schema.json")
    )

    proof = {
        "milestone": "MRAM-R0",
        "validation_class": "BOUNDED_ROUTING_GRAPH_CONTRACT_AND_DETERMINISTIC_SIGNAL_FLOW_PLAN",
        "routing_material_valid": True,
        "plan_repeat_exact": plan == repeat,
        "routing_plan_sha256": plan["routing_plan_sha256"],
        "topological_node_ids": [node["node_id"] for node in plan["nodes"]],
        "unique_master_sink": plan["master_node_id"] == "MASTER-001",
        "track_outputs_complete": [item["track_id"] for item in plan["track_outputs"]] == track_ids,
        "post_fader_send_explicit": all(item["tap"] == "post_fader" for item in plan["sends"]),
        "cycle_fails_closed": _blocked(lambda: validate_routing_material(cycle, track_ids=track_ids)),
        "missing_target_fails_closed": _blocked(
            lambda: validate_routing_material(missing_target, track_ids=track_ids)
        ),
        "missing_track_route_fails_closed": _blocked(
            lambda: validate_routing_material(missing_track, track_ids=track_ids)
        ),
        "master_send_fails_closed": _blocked(
            lambda: validate_routing_material(master_send, track_ids=track_ids)
        ),
        "nonempty_routing_structurally_valid_when_explicitly_allowed": True,
        "nonempty_routing_canonical_acceptance_fails_closed": canonical_acceptance_blocked,
        "accepted_routing_claimed": False,
        "routed_audio_rendering_claimed": False,
        "automation_mapping_claimed": False,
        "browser_routing_claimed": False,
        "realtime_audio_claimed": False,
        "plugin_hosting_claimed": False,
    }
    _write_json(out / "routing-material.json", material)
    _write_json(out / "routing-plan.json", plan)
    _write_json(out / "proof.json", proof)

    contract_hashes = []
    for path in CONTRACT_PATHS:
        data = path.read_bytes()
        contract_hashes.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": _sha(data),
                "size_bytes": len(data),
            }
        )
    _write_json(out / "contract-hashes.json", contract_hashes)

    records = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json"):
        data = path.read_bytes()
        records.append(
            {
                "path": path.relative_to(out).as_posix(),
                "sha256": _sha(data),
                "size_bytes": len(data),
            }
        )
    manifest = {
        "manifest_version": "0",
        "milestone": "MRAM-R0",
        "artifact_name": "musica-mram-r0-routing-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_MRAM_R0_EVIDENCE_OUT", "artifacts/mram-r0-routing-evidence"
    )
    generate_mram_r0_evidence(destination)
