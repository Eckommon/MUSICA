"""PLUG-R2: source-bound, offline/reference-only serial plugin delay ledger.

The accepted R1 delay_frames parameter displaces real audio; it is *not*
a measured plugin algorithmic latency and it does not establish multi-path PDC.
This read-only projection never writes Project/Blueprint or modifies WAV data.
"""
from __future__ import annotations

import hashlib
from typing import Any

from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .plugin_reference import (
    build_accepted_plugin_processing_plan,
    validate_plugin_processing_plan,
)

LEDGER_ENGINE_ID = "musica-plugin-latency-ledger-v0"
MAX_INSTANCE_DELAY_FRAMES = 4096
MAX_SERIAL_DELAY_FRAMES = 256 * MAX_INSTANCE_DELAY_FRAMES


def _hash_document(document: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(document)).hexdigest()


def validate_plugin_latency_plan(
    plan: dict[str, Any],
    *,
    processing_plan: dict[str, Any] | None = None,
) -> None:
    """Check the schema, self-hash and *semantic* invariants; optionally rebind R1.

    A self-consistent but forged plan cannot pass the optional exact-R1-plan
    comparison. Call validate_accepted_plugin_latency_plan for persisted sources.
    """
    validate_contract(plan, "plugin-latency-plan-v0.schema.json")
    without_hash = dict(plan)
    claimed_hash = without_hash.pop("plugin_latency_plan_sha256")
    if _hash_document(without_hash) != claimed_hash:
        raise ContractError("PLUG-R2 plugin latency plan self-hash mismatch")

    instances = plan["instances"]
    ordered = sorted(
        instances,
        key=lambda item: (
            str(item["owner_id"]),
            int(item["slot"]),
            str(item["instance_id"]),
        ),
    )
    if instances != ordered:
        raise ContractError("PLUG-R2 latency instances must use canonical slot ordering")

    ids = [str(item["instance_id"]) for item in instances]
    slots = [(str(item["owner_id"]), int(item["slot"])) for item in instances]
    if len(set(ids)) != len(ids):
        raise ContractError("PLUG-R2 duplicate plugin instance ID")
    if len(set(slots)) != len(slots):
        raise ContractError("PLUG-R2 duplicate master insertion slot")
    if len({str(item["owner_id"]) for item in instances}) > 1:
        raise ContractError("PLUG-R2 supports only one serial master node")

    total = 0
    for item in instances:
        declared = item["declared_signal_delay_frames"]
        effective = item["effective_signal_delay_frames"]
        if type(declared) is not int or not 0 <= declared <= MAX_INSTANCE_DELAY_FRAMES:
            raise ContractError("PLUG-R2 unsupported signal delay")
        if type(effective) is not int or effective != (
            0 if item["bypass"] else declared
        ):
            raise ContractError("PLUG-R2 bypass/effective delay mismatch")
        total += effective
        if total > MAX_SERIAL_DELAY_FRAMES:
            raise ContractError("PLUG-R2 serial signal delay overflow")

    if plan["serial_effective_signal_delay_frames"] != total:
        raise ContractError("PLUG-R2 serial delay total mismatch")
    if processing_plan is not None:
        expected = _latency_projection_from_processing_plan(processing_plan)
        if plan != expected:
            raise ContractError("PLUG-R2 latency plan is stale or forged against R1 processing plan")


def _latency_projection_from_processing_plan(
    processing_plan: dict[str, Any],
) -> dict[str, Any]:
    """Deterministic projection of validated R1 material; no audio reprocessing."""
    validate_plugin_processing_plan(processing_plan)
    instances: list[dict[str, Any]] = []
    for item in processing_plan["instances"]:
        declared = item["delay_frames"]
        effective = item["effective_latency_frames"]
        if type(declared) is not int or not 0 <= declared <= MAX_INSTANCE_DELAY_FRAMES:
            raise ContractError("PLUG-R2 unsupported R1 delay")
        if type(effective) is not int or effective != (
            0 if item["bypass"] else declared
        ):
            raise ContractError("PLUG-R2 invalid R1 effective latency")
        instances.append(
            {
                "instance_id": item["instance_id"],
                "plugin_id": item["plugin_id"],
                "owner_kind": "routing_node",
                "owner_id": item["owner_node_id"],
                "slot": item["slot"],
                "bypass": item["bypass"],
                "declared_signal_delay_frames": declared,
                "effective_signal_delay_frames": effective,
            }
        )

    source = dict(processing_plan["source"])
    source["plugin_processing_plan_sha256"] = processing_plan[
        "plugin_processing_plan_sha256"
    ]
    payload: dict[str, Any] = {
        "plan_version": "0",
        "engine_id": LEDGER_ENGINE_ID,
        "classification": "derived_noncanonical",
        "source": source,
        "sample_rate_hz": processing_plan["sample_rate_hz"],
        "channels": processing_plan["channels"],
        "sample_format": processing_plan["sample_format"],
        "stage": "post_routed_master_pcm16_reference_stage",
        "policy": {
            "topology": "serial_master_only",
            "delay_semantics": "accepted_state_signal_delay_frames",
            "algorithmic_latency": "UNMEASURED_NOT_INFERRED",
            "compensation": "NONE_SERIAL_ONLY",
            "runtime_scope": "OFFLINE_REFERENCE_ONLY",
        },
        "instances": instances,
        "serial_effective_signal_delay_frames": sum(
            item["effective_signal_delay_frames"] for item in instances
        ),
        "compensation_applied_frames": 0,
    }
    if payload["serial_effective_signal_delay_frames"] > MAX_SERIAL_DELAY_FRAMES:
        raise ContractError("PLUG-R2 serial signal delay overflow")
    plan = dict(payload)
    plan["plugin_latency_plan_sha256"] = _hash_document(payload)
    validate_plugin_latency_plan(plan)
    return plan


def build_accepted_plugin_latency_plan(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    routed_render: Any | None = None,
) -> dict[str, Any]:
    """Build only from exact persisted accepted R1 plugin/routing authority."""
    processing = build_accepted_plugin_processing_plan(
        project,
        revision_id,
        sample_rate_hz=sample_rate_hz,
        routed_render=routed_render,
    )
    return _latency_projection_from_processing_plan(processing)


def validate_accepted_plugin_latency_plan(
    project: Any,
    revision_id: str,
    plan: dict[str, Any],
    *,
    sample_rate_hz: int,
    routed_render: Any | None = None,
) -> None:
    """Reject even rehashed stale or forged plans by rebuilding accepted source."""
    expected = build_accepted_plugin_latency_plan(
        project,
        revision_id,
        sample_rate_hz=sample_rate_hz,
        routed_render=routed_render,
    )
    validate_plugin_latency_plan(plan)
    if plan != expected:
        raise ContractError("PLUG-R2 latency plan does not match accepted revision")
