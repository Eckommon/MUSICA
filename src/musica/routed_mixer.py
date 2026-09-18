"""MRAM-R1 deterministic routed native offline mixer.

Consumes an exact accepted revision with non-empty routing material. The routed plan
and WAV are derived/non-canonical. Numeric decode/gain/pan/clipping rules intentionally
reuse ATCM-R2 primitives.
"""

from __future__ import annotations

import hashlib
import io
import struct
import wave
from dataclasses import dataclass
from typing import Any

from .audio_assets import audio_asset_bytes
from .audio_contracts import audio_material_from_blueprint, validate_project_blueprint_audio
from .audio_edit import audio_material_sha256, blueprint_sha256
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .native_mixer import (
    _decode_pcm_frames,
    _gain_linear,
    _pan_coefficients,
    _pcm16_sample,
    build_native_mix_plan,
)
from .routing_contracts import (
    build_routing_plan,
    routing_material_from_blueprint,
    routing_material_sha256,
    validate_blueprint_routing,
)

ENGINE_ID = "musica-routed-native-offline-mixer-v0"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_routed_mix_plan(
    project: Any,
    revision_id: str,
    *,
    mix_sample_rate_hz: int,
) -> dict[str, Any]:
    """Bind accepted audio+routing state into one deterministic derived plan."""

    blueprint = project.read_revision(revision_id)
    if str(blueprint["project"]["revision_id"]) != str(revision_id):
        raise ContractError("routed mixer revision binding mismatch")
    validate_project_blueprint_audio(project, blueprint)
    validate_blueprint_routing(blueprint, allow_nonempty=True)

    audio = audio_material_from_blueprint(blueprint)
    routing = routing_material_from_blueprint(blueprint)
    assert audio is not None and routing is not None
    if not routing["nodes"]:
        raise ContractError("routed mixer requires accepted non-empty routing material")

    track_ids = [str(track["track_id"]) for track in audio["tracks"]]
    native = build_native_mix_plan(
        project,
        revision_id,
        mix_sample_rate_hz=mix_sample_rate_hz,
    )
    routing_plan = build_routing_plan(routing, track_ids=track_ids)

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
            "native_mix_plan_sha256": str(native["mix_plan_sha256"]),
            "routing_plan_sha256": str(routing_plan["routing_plan_sha256"]),
        },
        "mix_sample_rate_hz": int(native["mix_sample_rate_hz"]),
        "duration_frames": int(native["duration_frames"]),
        "policy": {
            "send_tap": "post_fader",
            "node_processing": "input_sum_then_static_gain_pan_mute_then_primary_output_and_sends",
            "pan_law": "linear_balance",
            "internal_precision": "float64",
            "clipping": "hard_clip_unit_range_before_pcm16",
            "output_format": "wav_pcm16_stereo_little_endian",
        },
        "native_tracks": native["tracks"],
        "routing": routing_plan,
    }
    plan = dict(plan_base)
    plan["routed_mix_plan_sha256"] = _sha256(canonical_json_bytes(plan_base))
    validate_contract(plan, "routed-mix-plan-v0.schema.json")
    return plan


def _empty_buffer(frame_count: int) -> tuple[list[float], list[float]]:
    return [0.0] * frame_count, [0.0] * frame_count


def _add_scaled(
    destination: tuple[list[float], list[float]],
    source: tuple[list[float], list[float]],
    gain: float = 1.0,
) -> None:
    dl, dr = destination
    sl, sr = source
    scalar = float(gain)
    for index in range(len(dl)):
        dl[index] += sl[index] * scalar
        dr[index] += sr[index] * scalar


def _track_buffer(
    project: Any,
    track: dict[str, Any],
    duration_frames: int,
    decoded_cache: dict[str, tuple[int, int, int, list[tuple[float, ...]]]],
) -> tuple[list[float], list[float]]:
    left, right = _empty_buffer(duration_frames)
    mixer = track["mixer"]
    if not bool(mixer["audible"]):
        return left, right

    track_gain = float(mixer["gain_linear"])
    left_coeff = float(mixer["left_coefficient"])
    right_coeff = float(mixer["right_coefficient"])
    for clip in track["clips"]:
        asset_id = str(clip["asset_id"])
        decoded = decoded_cache.get(asset_id)
        if decoded is None:
            decoded = _decode_pcm_frames(audio_asset_bytes(project, asset_id))
            decoded_cache[asset_id] = decoded
        channels, sample_width, sample_rate, frames = decoded
        if channels != int(clip["channels"]):
            raise ContractError(f"routed mixer channel metadata changed: {asset_id}")
        if sample_width != int(clip["sample_width_bytes"]):
            raise ContractError(f"routed mixer sample-width metadata changed: {asset_id}")
        if sample_rate != int(clip["sample_rate_hz"]):
            raise ContractError(f"routed mixer sample-rate metadata changed: {asset_id}")

        source_start = int(clip["source_start_frame"])
        source_end = int(clip["source_end_frame"])
        timeline_start = int(clip["timeline_start_frame"])
        combined_gain = track_gain * float(clip["gain_linear"])
        for offset, source_index in enumerate(range(source_start, source_end)):
            destination = timeline_start + offset
            frame = frames[source_index]
            if channels == 1:
                mono = frame[0] * combined_gain
                left[destination] += mono * left_coeff
                right[destination] += mono * right_coeff
            else:
                left[destination] += frame[0] * combined_gain * left_coeff
                right[destination] += frame[1] * combined_gain * right_coeff
    return left, right


def _process_node(
    source: tuple[list[float], list[float]],
    mixer: dict[str, Any],
) -> tuple[list[float], list[float]]:
    left = list(source[0])
    right = list(source[1])
    if bool(mixer["mute"]):
        return [0.0] * len(left), [0.0] * len(right)
    gain = _gain_linear(float(mixer["gain_db"]))
    left_coeff, right_coeff = _pan_coefficients(float(mixer["pan"]))
    for index in range(len(left)):
        left[index] *= gain * left_coeff
        right[index] *= gain * right_coeff
    return left, right


@dataclass(frozen=True)
class RoutedMixRender:
    plan: dict[str, Any]
    wav_bytes: bytes
    wav_sha256: str
    peak_pre_clip: float
    clipped_sample_count: int

    def report(self) -> dict[str, Any]:
        return {
            "routed_mix_plan_sha256": self.plan["routed_mix_plan_sha256"],
            "wav_sha256": self.wav_sha256,
            "wav_size_bytes": len(self.wav_bytes),
            "peak_pre_clip": self.peak_pre_clip,
            "clipped_sample_count": self.clipped_sample_count,
            "rendered_audio_is_canonical": False,
        }


def render_routed_mix(
    project: Any,
    revision_id: str,
    *,
    mix_sample_rate_hz: int,
) -> RoutedMixRender:
    """Render exact accepted routing into deterministic stereo PCM16 WAV bytes."""

    plan = build_routed_mix_plan(
        project,
        revision_id,
        mix_sample_rate_hz=mix_sample_rate_hz,
    )
    frame_count = int(plan["duration_frames"])
    routing = plan["routing"]

    track_output = {
        str(item["track_id"]): str(item["target_node_id"])
        for item in routing["track_outputs"]
    }
    track_sends: dict[str, list[dict[str, Any]]] = {}
    node_sends: dict[str, list[dict[str, Any]]] = {}
    for send in routing["sends"]:
        target = track_sends if send["source_kind"] == "track" else node_sends
        target.setdefault(str(send["source_id"]), []).append(send)

    node_inputs = {
        str(node["node_id"]): _empty_buffer(frame_count)
        for node in routing["nodes"]
    }
    decoded_cache: dict[str, tuple[int, int, int, list[tuple[float, ...]]]] = {}

    for track in plan["native_tracks"]:
        track_id = str(track["track_id"])
        buffer = _track_buffer(project, track, frame_count, decoded_cache)
        _add_scaled(node_inputs[track_output[track_id]], buffer)
        for send in track_sends.get(track_id, []):
            _add_scaled(
                node_inputs[str(send["target_node_id"])],
                buffer,
                _gain_linear(float(send["gain_db"])),
            )

    master_id = str(routing["master_node_id"])
    master_output: tuple[list[float], list[float]] | None = None
    for node in routing["nodes"]:
        node_id = str(node["node_id"])
        output = _process_node(node_inputs[node_id], node["mixer"])

        for send in node_sends.get(node_id, []):
            _add_scaled(
                node_inputs[str(send["target_node_id"])],
                output,
                _gain_linear(float(send["gain_db"])),
            )

        target = node.get("output_node_id")
        if target is None:
            if node_id != master_id:
                raise ContractError("routed mixer found non-master terminal node")
            master_output = output
        else:
            _add_scaled(node_inputs[str(target)], output)

    if master_output is None:
        raise ContractError("routed mixer did not resolve a master output")

    left, right = master_output
    peak_pre_clip = 0.0
    clipped_sample_count = 0
    payload = bytearray()
    for l_value, r_value in zip(left, right):
        peak_pre_clip = max(peak_pre_clip, abs(l_value), abs(r_value))
        if l_value < -1.0 or l_value > 1.0:
            clipped_sample_count += 1
        if r_value < -1.0 or r_value > 1.0:
            clipped_sample_count += 1
        payload.extend(struct.pack("<hh", _pcm16_sample(l_value), _pcm16_sample(r_value)))

    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(int(plan["mix_sample_rate_hz"]))
        writer.writeframes(bytes(payload))
    wav_bytes = stream.getvalue()
    return RoutedMixRender(
        plan=plan,
        wav_bytes=wav_bytes,
        wav_sha256=_sha256(wav_bytes),
        peak_pre_clip=peak_pre_clip,
        clipped_sample_count=clipped_sample_count,
    )
