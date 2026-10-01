"""PLUG-R0 deterministic simulated plugin processor.

R0 deliberately keeps plugin material detached from accepted Blueprint authority.
It validates an explicit non-canonical proposal, binds it to one exact accepted routed
revision, lowers it into a derived processing plan, and processes the accepted routed
PCM through a bounded deterministic simulated gain+delay chain.
"""

from __future__ import annotations

import hashlib
import io
import math
import struct
import wave
from dataclasses import dataclass
from typing import Any

from .audio_edit import audio_material_sha256, blueprint_sha256
from .automation_edit import automation_material_sha256
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .native_mixer import _gain_linear, _pcm16_sample
from .routed_mixer import RoutedMixRender, render_routed_mix
from .routing_contracts import (
    routing_material_from_blueprint,
    routing_material_sha256,
    validate_blueprint_routing,
)

ENGINE_ID = "musica-simulated-plugin-processor-v0"
PROCESSOR_ID = "musica-simulated-gain-delay-v0"

_CANONICAL_PARAMETERS = [
    {
        "parameter_id": "gain_db",
        "unit": "decibel",
        "minimum": -60.0,
        "maximum": 12.0,
        "default": 0.0,
    },
    {
        "parameter_id": "delay_frames",
        "unit": "frames",
        "minimum": 0.0,
        "maximum": 4096.0,
        "default": 0.0,
    },
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def plugin_material_sha256(material: dict[str, Any]) -> str:
    validate_contract(material, "plugin-material-v0.schema.json")
    return _sha256(canonical_json_bytes(material))


def _routing_master_id(blueprint: dict[str, Any]) -> str:
    routing = routing_material_from_blueprint(blueprint)
    assert routing is not None
    validate_blueprint_routing(blueprint, allow_nonempty=True)
    if not routing["nodes"]:
        raise ContractError("PLUG-R0 requires accepted non-empty routing")
    masters = [
        str(node["node_id"])
        for node in routing["nodes"]
        if str(node["node_type"]) == "master"
    ]
    if len(masters) != 1:
        raise ContractError("PLUG-R0 requires exactly one accepted master routing node")
    return masters[0]


def validate_plugin_material(
    material: dict[str, Any],
    *,
    blueprint: dict[str, Any],
) -> None:
    """Validate one detached plugin proposal against an exact accepted routed source."""

    validate_contract(material, "plugin-material-v0.schema.json")
    master_id = _routing_master_id(blueprint)

    descriptors = material["descriptors"]
    descriptor_ids = [str(item["plugin_id"]) for item in descriptors]
    if descriptor_ids != sorted(descriptor_ids):
        raise ContractError("plugin descriptors must use canonical plugin_id order")
    if len(descriptor_ids) != len(set(descriptor_ids)):
        raise ContractError("plugin descriptor plugin_id must be unique")

    descriptor_map: dict[str, dict[str, Any]] = {}
    for descriptor in descriptors:
        plugin_id = str(descriptor["plugin_id"])
        descriptor_map[plugin_id] = descriptor
        if descriptor["parameters"] != _CANONICAL_PARAMETERS:
            raise ContractError(
                f"PLUG-R0 descriptor {plugin_id} must expose the exact canonical "
                "gain_db/delay_frames parameter contract"
            )

    instances = material["instances"]
    instance_ids = [str(item["instance_id"]) for item in instances]
    if len(instance_ids) != len(set(instance_ids)):
        raise ContractError("plugin instance_id must be unique")
    expected_order = sorted(
        instances,
        key=lambda item: (
            str(item["owner"]["owner_id"]),
            int(item["slot"]),
            str(item["instance_id"]),
        ),
    )
    if instances != expected_order:
        raise ContractError(
            "plugin instances must use canonical (owner_id, slot, instance_id) order"
        )

    slots: list[tuple[str, int]] = []
    for instance in instances:
        instance_id = str(instance["instance_id"])
        plugin_id = str(instance["plugin_id"])
        if plugin_id not in descriptor_map:
            raise ContractError(
                f"plugin instance {instance_id} references unknown plugin_id: {plugin_id}"
            )
        owner = instance["owner"]
        owner_id = str(owner["owner_id"])
        if owner_id != master_id:
            raise ContractError(
                f"PLUG-R0 supports only exact master routing-node owner {master_id!r}, "
                f"got {owner_id!r}"
            )
        slots.append((owner_id, int(instance["slot"])))

    if len(slots) != len(set(slots)):
        raise ContractError("plugin insertion slot must be unique per owner")


def validate_plugin_processing_plan(plan: dict[str, Any]) -> None:
    """Validate derived plan schema, canonical ordering, latency total and self-hash."""

    validate_contract(plan, "plugin-processing-plan-v0.schema.json")
    base = dict(plan)
    claimed = str(base.pop("plugin_processing_plan_sha256"))
    actual = _sha256(canonical_json_bytes(base))
    if claimed != actual:
        raise ContractError("plugin processing plan SHA-256 mismatch")

    instances = plan["instances"]
    expected = sorted(
        instances,
        key=lambda item: (
            str(item["owner_node_id"]),
            int(item["slot"]),
            str(item["instance_id"]),
        ),
    )
    if instances != expected:
        raise ContractError("plugin processing plan instances are not canonical")
    instance_ids = [str(item["instance_id"]) for item in instances]
    if len(instance_ids) != len(set(instance_ids)):
        raise ContractError("plugin processing plan instance_id must be unique")
    slots = [(str(item["owner_node_id"]), int(item["slot"])) for item in instances]
    if len(slots) != len(set(slots)):
        raise ContractError("plugin processing plan slot must be unique per owner")

    expected_latency = sum(
        int(item["effective_latency_frames"]) for item in instances
    )
    if int(plan["total_effective_latency_frames"]) != expected_latency:
        raise ContractError("plugin processing plan latency total mismatch")

    for item in instances:
        expected_effective = 0 if bool(item["bypass"]) else int(item["delay_frames"])
        if int(item["effective_latency_frames"]) != expected_effective:
            raise ContractError(
                f"plugin processing plan effective latency mismatch: {item['instance_id']}"
            )


def _decode_stereo_pcm16_wav(data: bytes, *, sample_rate_hz: int) -> list[tuple[float, float]]:
    try:
        stream = io.BytesIO(data)
        with wave.open(stream, "rb") as reader:
            if reader.getcomptype() != "NONE":
                raise ContractError("PLUG-R0 accepts only uncompressed PCM routed WAV")
            channels = int(reader.getnchannels())
            width = int(reader.getsampwidth())
            rate = int(reader.getframerate())
            frame_count = int(reader.getnframes())
            payload = reader.readframes(frame_count)
    except (wave.Error, EOFError) as exc:
        raise ContractError("PLUG-R0 cannot decode routed WAV") from exc

    if channels != 2 or width != 2:
        raise ContractError("PLUG-R0 v0 requires exact stereo PCM16 input")
    if rate != int(sample_rate_hz):
        raise ContractError(
            f"PLUG-R0 requires exact sample-rate match: routed={rate} vs plugin={sample_rate_hz}"
        )
    if len(payload) != frame_count * 4:
        raise ContractError("PLUG-R0 routed PCM payload length mismatch")

    frames: list[tuple[float, float]] = []
    for offset in range(0, len(payload), 4):
        left, right = struct.unpack_from("<hh", payload, offset)
        frames.append((float(left) / 32768.0, float(right) / 32768.0))
    return frames


def build_plugin_processing_plan(
    project: Any,
    revision_id: str,
    plugin_material: dict[str, Any],
    *,
    sample_rate_hz: int,
    routed_render: RoutedMixRender | None = None,
) -> dict[str, Any]:
    """Lower detached plugin proposal against one exact accepted routed render."""

    if not isinstance(sample_rate_hz, int) or not 8000 <= sample_rate_hz <= 192000:
        raise ContractError("PLUG-R0 sample_rate_hz must be an integer between 8000 and 192000")

    blueprint = project.read_revision(revision_id)
    if str(blueprint["project"]["revision_id"]) != str(revision_id):
        raise ContractError("PLUG-R0 accepted revision binding mismatch")
    validate_plugin_material(plugin_material, blueprint=blueprint)

    routed = routed_render or render_routed_mix(
        project,
        revision_id,
        mix_sample_rate_hz=sample_rate_hz,
    )
    if int(routed.plan["mix_sample_rate_hz"]) != sample_rate_hz:
        raise ContractError("PLUG-R0 routed render sample-rate binding mismatch")

    routing = routing_material_from_blueprint(blueprint)
    assert routing is not None
    _decode_stereo_pcm16_wav(routed.wav_bytes, sample_rate_hz=sample_rate_hz)

    descriptor_map = {
        str(item["plugin_id"]): item for item in plugin_material["descriptors"]
    }
    plan_instances: list[dict[str, Any]] = []
    for instance in plugin_material["instances"]:
        descriptor = descriptor_map[str(instance["plugin_id"])]
        state = instance["state"]
        bypass = bool(instance["bypass"])
        delay_frames = int(state["delay_frames"])
        plan_instances.append(
            {
                "instance_id": str(instance["instance_id"]),
                "plugin_id": str(instance["plugin_id"]),
                "owner_node_id": str(instance["owner"]["owner_id"]),
                "slot": int(instance["slot"]),
                "bypass": bypass,
                "processor_id": str(descriptor["processor_id"]),
                "gain_db": float(state["gain_db"]),
                "gain_linear": _gain_linear(float(state["gain_db"])),
                "delay_frames": delay_frames,
                "effective_latency_frames": 0 if bypass else delay_frames,
            }
        )

    plugin_hash = plugin_material_sha256(plugin_material)
    plan_base: dict[str, Any] = {
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
            "routed_mix_plan_sha256": str(routed.plan["routed_mix_plan_sha256"]),
            "routed_wav_sha256": str(routed.wav_sha256),
            "plugin_material_sha256": plugin_hash,
        },
        "sample_rate_hz": sample_rate_hz,
        "channels": 2,
        "sample_format": "float64_internal_pcm16_io",
        "policy": {
            "insertion_point": "post_routed_master_pcm16_reference_stage",
            "ordering": "slot_then_instance_id",
            "latency": "serial_sum_of_nonbypassed_fixed_delay_frames",
            "resampling": "forbidden",
            "channel_conversion": "forbidden_stereo_only",
            "output_clipping": "hard_clip_unit_range_before_pcm16",
        },
        "instances": plan_instances,
        "total_effective_latency_frames": sum(
            int(item["effective_latency_frames"]) for item in plan_instances
        ),
    }
    plan = dict(plan_base)
    plan["plugin_processing_plan_sha256"] = _sha256(canonical_json_bytes(plan_base))
    validate_plugin_processing_plan(plan)
    return plan


def _delay_and_gain(
    frames: list[tuple[float, float]],
    *,
    gain_linear: float,
    delay_frames: int,
) -> list[tuple[float, float]]:
    frame_count = len(frames)
    output: list[tuple[float, float]] = [(0.0, 0.0)] * frame_count
    for source_index, (left, right) in enumerate(frames):
        destination = source_index + int(delay_frames)
        if destination >= frame_count:
            continue
        output[destination] = (
            float(left) * float(gain_linear),
            float(right) * float(gain_linear),
        )
    return output


@dataclass(frozen=True)
class PluginRender:
    plan: dict[str, Any]
    wav_bytes: bytes
    wav_sha256: str
    peak_pre_clip: float
    clipped_sample_count: int

    def report(self) -> dict[str, Any]:
        return {
            "plugin_processing_plan_sha256": self.plan[
                "plugin_processing_plan_sha256"
            ],
            "wav_sha256": self.wav_sha256,
            "wav_size_bytes": len(self.wav_bytes),
            "peak_pre_clip": self.peak_pre_clip,
            "clipped_sample_count": self.clipped_sample_count,
            "total_effective_latency_frames": self.plan[
                "total_effective_latency_frames"
            ],
            "plugin_runtime_is_canonical": False,
            "processed_audio_is_canonical": False,
        }


def render_simulated_plugins(
    project: Any,
    revision_id: str,
    plugin_material: dict[str, Any],
    *,
    sample_rate_hz: int,
    force_error_instance_ids: set[str] | None = None,
) -> PluginRender:
    """Process exact accepted routed PCM through the deterministic PLUG-R0 chain."""

    routed = render_routed_mix(
        project,
        revision_id,
        mix_sample_rate_hz=sample_rate_hz,
    )
    plan = build_plugin_processing_plan(
        project,
        revision_id,
        plugin_material,
        sample_rate_hz=sample_rate_hz,
        routed_render=routed,
    )
    forced = force_error_instance_ids or set()

    if all(bool(item["bypass"]) for item in plan["instances"]):
        return PluginRender(
            plan=plan,
            wav_bytes=routed.wav_bytes,
            wav_sha256=routed.wav_sha256,
            peak_pre_clip=routed.peak_pre_clip,
            clipped_sample_count=routed.clipped_sample_count,
        )

    frames = _decode_stereo_pcm16_wav(
        routed.wav_bytes, sample_rate_hz=sample_rate_hz
    )
    for instance in plan["instances"]:
        if bool(instance["bypass"]):
            continue
        instance_id = str(instance["instance_id"])
        if instance_id in forced:
            raise ContractError(
                f"PLUG-R0 deterministic forced processor error: {instance_id}"
            )
        frames = _delay_and_gain(
            frames,
            gain_linear=float(instance["gain_linear"]),
            delay_frames=int(instance["delay_frames"]),
        )

    peak_pre_clip = 0.0
    clipped_sample_count = 0
    payload = bytearray()
    for left, right in frames:
        peak_pre_clip = max(peak_pre_clip, abs(left), abs(right))
        if left < -1.0 or left > 1.0:
            clipped_sample_count += 1
        if right < -1.0 or right > 1.0:
            clipped_sample_count += 1
        payload.extend(struct.pack("<hh", _pcm16_sample(left), _pcm16_sample(right)))

    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate_hz)
        writer.writeframes(bytes(payload))
    wav_bytes = stream.getvalue()
    return PluginRender(
        plan=plan,
        wav_bytes=wav_bytes,
        wav_sha256=_sha256(wav_bytes),
        peak_pre_clip=peak_pre_clip,
        clipped_sample_count=clipped_sample_count,
    )
