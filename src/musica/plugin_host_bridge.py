"""PLUG-R2B K1: read-only, accepted-source two-bus PCM reference bridge.

This extracts pre-master bus audio from immutable accepted project assets and
MRAM routing. Detached simulated latency is still NOT accepted plugin authority.
Only the existing K0 kernel may compensate these derived WAVs. No Project write.
"""
from __future__ import annotations

import hashlib
import io
import struct
import wave
from dataclasses import dataclass
from typing import Any

from .audio_edit import blueprint_sha256, audio_material_sha256
from .automation_edit import automation_material_sha256
from .contracts import ContractError
from .evidence import canonical_json_bytes
from .plugin_host_topology import exact_two_bus_host_topology
from .plugin_reference import accepted_plugin_material_from_blueprint, accepted_plugin_material_sha256
from .plugin_alignment_reference import (
    build_two_path_alignment_plan,
    render_two_path_alignment,
    TwoPathReferenceRender,
)
from .routed_mixer import (
    _process_node,
    _track_buffer,
    build_routed_mix_plan,
)
from .native_mixer import _pcm16_sample
from .native_mixer_automation import automation_lane_map

BRIDGE_ID = "musica-accepted-two-bus-detached-reference-bridge-v0"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _encode_bus_pcm(
    buffer: tuple[list[float], list[float]], sample_rate_hz: int
) -> bytes:
    samples = bytearray()
    for left, right in zip(*buffer, strict=True):
        samples.extend(struct.pack("<hh", _pcm16_sample(left), _pcm16_sample(right)))
    out = io.BytesIO()
    with wave.open(out, "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate_hz)
        writer.writeframes(bytes(samples))
    return out.getvalue()


@dataclass(frozen=True)
class AcceptedBusReferenceInputs:
    source: dict[str, Any]
    path_wav_by_id: dict[str, bytes]
    provenance_sha256: str


def build_accepted_bus_reference_inputs(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
) -> AcceptedBusReferenceInputs:
    """Extract TWO immutable accepted track->bus pre-master PCM paths.

    Rebuilds the native routed plan and asset decoding from the stored revision.
    Input WAV bytes are not accepted from the caller. Conversion into PCM16
    occurs at the explicit pre-master bus boundary; output may therefore differ
    from float64-first legacy routing due to intermediate PCM16 quantization.
    """
    if type(sample_rate_hz) is not int or not 8000 <= sample_rate_hz <= 192000:
        raise ContractError("K1 bridge unsupported exact sample rate")
    blueprint = project.read_revision(revision_id)
    if str(blueprint["project"]["revision_id"]) != str(revision_id):
        raise ContractError("K1 bridge accepted revision identity mismatch")
    topology = exact_two_bus_host_topology(blueprint)
    if accepted_plugin_material_from_blueprint(blueprint)["instances"]:
        raise ContractError("K1 bridge excludes any accepted R1 master plugin")
    routed = build_routed_mix_plan(
        project, revision_id, mix_sample_rate_hz=sample_rate_hz
    )
    if routed["mix_sample_rate_hz"] != sample_rate_hz:
        raise ContractError("K1 bridge no implicit resampling")
    duration = routed["duration_frames"]
    if type(duration) is not int or not 1 <= duration <= 1_000_000:
        raise ContractError("K1 bridge duration exceeds reference kernel bounds")
    node_map = {
        str(node["node_id"]): node for node in routed["routing"]["nodes"]
    }
    master = node_map[topology["master_node_id"]]
    if master["mixer"] != {"gain_db": 0.0, "pan": 0.0, "mute": False}:
        raise ContractError("K1 reference requires neutral, unmuted master")
    automation = (
        automation_lane_map(routed["native_mixer_automation"])
        if "native_mixer_automation" in routed else {}
    )
    if any(key[0] == "routing_node" and key[1] == topology["master_node_id"] for key in automation):
        raise ContractError("K1 reference rejects master automation before integration")
    tracks = {str(track["track_id"]): track for track in routed["native_tracks"]}
    decoded: dict[str, Any] = {}
    inputs: dict[str, bytes] = {}
    for path in topology["paths"]:
        track_id = path["track_id"]
        bus_id = path["bus_node_id"]
        track = tracks[track_id]
        track_audio = _track_buffer(project, track, duration, decoded, automation)
        bus = node_map[bus_id]
        bus_audio = _process_node(
            track_audio, bus["mixer"], node_id=bus_id, automation=automation
        )
        inputs[bus_id] = _encode_bus_pcm(bus_audio, sample_rate_hz)

    source = {
        "bridge_version": "0",
        "engine_id": BRIDGE_ID,
        "classification": "derived_noncanonical_accepted_source_detached_latency",
        "project_id": str(blueprint["project"]["project_id"]),
        "revision_id": str(revision_id),
        "blueprint_sha256": blueprint_sha256(blueprint),
        "audio_material_sha256": audio_material_sha256(blueprint),
        "routing_material_sha256": topology["routing_material_sha256"],
        "automation_material_sha256": automation_material_sha256(blueprint),
        "accepted_plugin_material_sha256": accepted_plugin_material_sha256(blueprint),
        "routed_mix_plan_sha256": routed["routed_mix_plan_sha256"],
        "sample_rate_hz": sample_rate_hz,
        "duration_frames": duration,
        "topology": topology,
        "input_pcm_boundary": "post_bus_gain_pan_to_pcm16_before_neutral_master",
        "path_wav_sha256": [
            {"path_id": name, "sha256": _sha(raw)}
            for name, raw in sorted(inputs.items())
        ],
        "accepted_host_plugin_authority": False,
        "host_pdc_integrated": False,
    }
    return AcceptedBusReferenceInputs(
        source=source,
        path_wav_by_id=inputs,
        provenance_sha256=_sha(canonical_json_bytes(source)),
    )


def render_accepted_bus_detached_alignment(
    project: Any,
    revision_id: str,
    *,
    sample_rate_hz: int,
    latency_config_by_bus_id: dict[str, dict[str, Any]],
    force_error_path_ids: set[str] | None = None,
    compensate: bool = True,
) -> tuple[AcceptedBusReferenceInputs, TwoPathReferenceRender]:
    """Read accepted audio/routing; apply ONLY detached synthetic K0 latency.

    This deliberately does not read algorithmic latency from accepted R1 plugin
    delay_frames and never authorizes mutations or user WAV source injection.
    """
    inputs = build_accepted_bus_reference_inputs(
        project, revision_id, sample_rate_hz=sample_rate_hz
    )
    if not isinstance(latency_config_by_bus_id, dict) or set(latency_config_by_bus_id) != set(inputs.path_wav_by_id):
        raise ContractError("K1 bridge requires exact accepted bus owner IDs")
    configs = []
    for name in sorted(inputs.path_wav_by_id):
        value = latency_config_by_bus_id[name]
        if not isinstance(value, dict) or set(value) != {
            "algorithmic_latency_frames", "creative_delay_frames", "bypass"
        }:
            raise ContractError("K1 bridge rejects unversioned/unknown detached latency fields")
        configs.append({"path_id": name, **value})
    plan = build_two_path_alignment_plan(
        configs, sample_rate_hz=sample_rate_hz,
        input_wav_by_path=inputs.path_wav_by_id
    )
    output = render_two_path_alignment(
        plan, input_wav_by_path=inputs.path_wav_by_id,
        force_error_path_ids=force_error_path_ids, compensate=compensate
    )
    return inputs, output
