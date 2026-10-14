"""K1-B accepted simulated bus processor offline execution.

Only exact persisted bus-host material authorizes the simulated algorithmic
latency values. This is an offline bounded PDC *reference* on 2 accepted buses;
real third-party formats and Studio/realtime integration are not claimed.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .audio_edit import blueprint_sha256, audio_material_sha256
from .automation_edit import automation_material_sha256
from .bus_host_material import (
    bus_host_material_from_blueprint, accepted_bus_host_sha256,
    bus_host_latency_config, validate_bus_host_material,
)
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .plugin_reference import accepted_plugin_material_sha256
from .plugin_host_bridge import render_accepted_bus_detached_alignment
from .routed_mixer import render_routed_mix
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256

ENGINE_ID = "musica-accepted-simulated-bus-host-offline-v0"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _selfhash(plan: dict[str, Any]) -> str:
    value = dict(plan)
    value.pop("bus_host_processing_plan_sha256", None)
    return _sha(canonical_json_bytes(value))


def validate_bus_host_processing_plan(plan: dict[str, Any]) -> None:
    """Reject forged hashes and impossible mode/provenance combinations."""
    validate_contract(plan, "bus-host-processing-plan-v0.schema.json")
    if plan["bus_host_processing_plan_sha256"] != _selfhash(plan):
        raise ContractError("K1-B bus-host derived plan self hash changed")
    legacy = plan["mode"] == "legacy_routed_byte_exact_no_bus_processors"
    if legacy != (plan["kernel_plan_sha256"] is None):
        raise ContractError("K1-B plan kernel/mode mismatch")
    if legacy != (plan["source"]["accepted_bus_audio_provenance_sha256"] is None):
        raise ContractError("K1-B plan accepted bus input/mode mismatch")


@dataclass(frozen=True)
class BusHostRender:
    plan: dict[str, Any]
    wav_bytes: bytes
    wav_sha256: str
    kernel_plan: dict[str, Any] | None

    def report(self) -> dict[str, Any]:
        return {
            "bus_host_processing_plan_sha256": self.plan[
                "bus_host_processing_plan_sha256"
            ],
            "wav_sha256": self.wav_sha256,
            "mode": self.plan["mode"],
            "rendered_audio_is_canonical": False,
            "native_plugin_latency_reporting_proven": False,
            "real_time_host_integrated": False,
        }


def render_accepted_simulated_bus_host(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    force_error_instance_ids: set[str] | None = None,
) -> BusHostRender:
    """Read accepted source, replan and render; never mutate Project authority."""
    if type(sample_rate_hz) is not int or not 8000 <= sample_rate_hz <= 192000:
        raise ContractError("K1-B accepted host sample rate must be exact 8000..192000")
    blueprint = project.read_revision(revision_id)
    if str(blueprint["project"]["revision_id"]) != str(revision_id):
        raise ContractError("K1-B accepted host revision identity mismatch")
    material = bus_host_material_from_blueprint(blueprint)
    validate_bus_host_material(material, blueprint=blueprint)
    forced = force_error_instance_ids if force_error_instance_ids is not None else set()
    if type(forced) is not set or any(type(v) is not str for v in forced):
        raise ContractError("K1-B injected processor errors require exact instance IDs")
    ids = {str(item["instance_id"]) for item in material["instances"]}
    if forced - ids:
        raise ContractError("K1-B error injection references unknown bus processor")

    input_sha = None
    kernel = None
    if not material["instances"]:
        # Byte-exact legacy routing: NO independent bus quantization, delay,
        # resampling or change to existing native mix path.
        baseline = render_routed_mix(
            project, revision_id, mix_sample_rate_hz=sample_rate_hz
        )
        wav = baseline.wav_bytes
        mode = "legacy_routed_byte_exact_no_bus_processors"
        kernel_sha = None
    else:
        config = bus_host_latency_config(blueprint)
        error_buses = {
            str(item["owner_bus_id"])
            for item in material["instances"]
            if str(item["instance_id"]) in forced
        }
        bridge, derived = render_accepted_bus_detached_alignment(
            project, revision_id,
            sample_rate_hz=sample_rate_hz,
            latency_config_by_bus_id=config,
            force_error_path_ids=error_buses,
        )
        input_sha = bridge.provenance_sha256
        kernel = derived.plan
        kernel_sha = str(kernel["plugin_two_path_alignment_plan_sha256"])
        wav = derived.wav_bytes
        mode = "accepted_two_bus_simulated_reference_pdc"

    routing = routing_material_from_blueprint(blueprint)
    if routing is None:
        raise ContractError("K1-B source routing unavailable")
    payload: dict[str, Any] = {
        "plan_version": "0",
        "engine_id": ENGINE_ID,
        "classification": "derived_noncanonical",
        "source": {
            "project_id": str(blueprint["project"]["project_id"]),
            "revision_id": str(revision_id),
            "blueprint_sha256": blueprint_sha256(blueprint),
            "audio_material_sha256": audio_material_sha256(blueprint),
            "routing_material_sha256": routing_material_sha256(routing),
            "automation_material_sha256": automation_material_sha256(blueprint),
            "legacy_plugin_material_sha256": accepted_plugin_material_sha256(blueprint),
            "bus_host_material_sha256": accepted_bus_host_sha256(blueprint),
            "accepted_bus_audio_provenance_sha256": input_sha,
        },
        "sample_rate_hz": sample_rate_hz,
        "mode": mode,
        "kernel_plan_sha256": kernel_sha,
        "algorithmic_latency_provenance": "accepted_explicit_simulated_reference_not_native_plugin",
        "creative_delay_policy": "accepted_path_delay_preserved_independent_of_algorithmic_bypass",
    }
    plan = dict(payload)
    plan["bus_host_processing_plan_sha256"] = _selfhash(payload)
    validate_bus_host_processing_plan(plan)
    return BusHostRender(
        plan=plan,
        wav_bytes=wav,
        wav_sha256=_sha(wav),
        kernel_plan=kernel,
    )


def validate_accepted_bus_host_processing_plan(
    project: Any,
    revision_id: str,
    plan: dict[str, Any],
    *,
    sample_rate_hz: int,
) -> None:
    """Even a fully rehashed forgery fails authoritative source reconstruction."""
    validate_bus_host_processing_plan(plan)
    expected = render_accepted_simulated_bus_host(
        project, revision_id, sample_rate_hz=sample_rate_hz
    ).plan
    if plan != expected:
        raise ContractError("K1-B accepted bus host plan source is stale or forged")
