"""ATCM-R2 deterministic native multitrack offline mixer.

The mixer consumes one exact accepted revision plus immutable project audio assets.
Its mix plan and WAV bytes are derived outputs and never mutate Blueprint authority.
"""

from __future__ import annotations

import hashlib
import io
import math
import struct
import wave
from dataclasses import dataclass
from typing import Any

from .audio_assets import audio_asset_bytes, read_audio_asset
from .audio_contracts import audio_material_from_blueprint, validate_project_blueprint_audio
from .audio_edit import audio_material_sha256, blueprint_sha256
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes

ENGINE_ID = "musica-native-offline-mixer-v0"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _frame_index(seconds: float, sample_rate_hz: int) -> int:
    """Quantize non-negative seconds with exact round-half-up semantics."""
    value = float(seconds)
    if value < 0:
        raise ContractError("native mixer time values must be non-negative")
    return int(math.floor(value * int(sample_rate_hz) + 0.5))


def _gain_linear(gain_db: float) -> float:
    return float(10.0 ** (float(gain_db) / 20.0))


def _pan_coefficients(pan: float) -> tuple[float, float]:
    """Linear stereo balance law preserving unity at center."""
    value = float(pan)
    if value < -1.0 or value > 1.0:
        raise ContractError(f"native mixer pan out of range: {value}")
    left = 1.0 if value <= 0.0 else 1.0 - value
    right = 1.0 if value >= 0.0 else 1.0 + value
    return float(left), float(right)


def _descriptor_sha256(descriptor: dict[str, Any]) -> str:
    return _sha256(canonical_json_bytes(descriptor))


def build_native_mix_plan(project: Any, revision_id: str, *, mix_sample_rate_hz: int) -> dict[str, Any]:
    """Lower one exact accepted revision into a deterministic native mix plan."""
    if not isinstance(mix_sample_rate_hz, int) or not 8000 <= mix_sample_rate_hz <= 192000:
        raise ContractError("mix_sample_rate_hz must be an integer between 8000 and 192000")

    blueprint = project.read_revision(revision_id)
    if str(blueprint["project"]["revision_id"]) != str(revision_id):
        raise ContractError("native mixer revision binding mismatch")
    validate_project_blueprint_audio(project, blueprint)
    material = audio_material_from_blueprint(blueprint)
    assert material is not None
    duration_frames = _frame_index(float(blueprint["project"]["duration_seconds"]), mix_sample_rate_hz)
    if duration_frames <= 0:
        raise ContractError("native mixer project duration must produce at least one frame")

    any_solo = any(bool(track["mixer"]["solo"]) for track in material["tracks"])
    plan_tracks: list[dict[str, Any]] = []
    for track in material["tracks"]:
        mixer = track["mixer"]
        pan = float(mixer["pan"])
        left_coeff, right_coeff = _pan_coefficients(pan)
        audible = (not bool(mixer["mute"])) and ((not any_solo) or bool(mixer["solo"]))
        clips: list[dict[str, Any]] = []
        for clip in track["clips"]:
            asset_id = str(clip["asset_id"])
            descriptor = read_audio_asset(project, asset_id)
            fmt = descriptor["format"]
            if fmt["container"] != "wav" or fmt["codec"] != "pcm_integer":
                raise ContractError(f"unsupported native mixer asset format: {asset_id}")
            if int(fmt["channels"]) not in (1, 2):
                raise ContractError(f"unsupported native mixer channel count: {asset_id}")
            if int(fmt["sample_rate_hz"]) != mix_sample_rate_hz:
                raise ContractError(
                    "native mixer v0 requires exact source sample-rate match: "
                    f"{asset_id}={fmt['sample_rate_hz']} vs mix={mix_sample_rate_hz}"
                )
            source_start = _frame_index(float(clip["source_in_seconds"]), mix_sample_rate_hz)
            source_end = _frame_index(float(clip["source_out_seconds"]), mix_sample_rate_hz)
            timeline_start = _frame_index(float(clip["timeline_start_seconds"]), mix_sample_rate_hz)
            if source_end <= source_start:
                raise ContractError(f"native mixer clip has empty frame range: {clip['clip_id']}")
            if source_end > int(fmt["frame_count"]):
                raise ContractError(f"native mixer clip exceeds exact asset frames: {clip['clip_id']}")
            if timeline_start + (source_end - source_start) > duration_frames:
                raise ContractError(f"native mixer clip exceeds exact project frame duration: {clip['clip_id']}")
            clips.append({
                "clip_id": str(clip["clip_id"]),
                "asset_id": asset_id,
                "object_sha256": str(descriptor["object_sha256"]),
                "descriptor_sha256": _descriptor_sha256(descriptor),
                "channels": int(fmt["channels"]),
                "sample_rate_hz": int(fmt["sample_rate_hz"]),
                "sample_width_bytes": int(fmt["sample_width_bytes"]),
                "timeline_start_frame": timeline_start,
                "source_start_frame": source_start,
                "source_end_frame": source_end,
                "gain_db": float(clip["gain_db"]),
                "gain_linear": _gain_linear(float(clip["gain_db"])),
            })
        plan_tracks.append({
            "track_id": str(track["track_id"]),
            "order": int(track["order"]),
            "mixer": {
                "gain_db": float(mixer["gain_db"]),
                "gain_linear": _gain_linear(float(mixer["gain_db"])),
                "pan": pan,
                "left_coefficient": left_coeff,
                "right_coefficient": right_coeff,
                "mute": bool(mixer["mute"]),
                "solo": bool(mixer["solo"]),
                "audible": audible,
            },
            "clips": clips,
        })

    plan_base: dict[str, Any] = {
        "plan_version": "0",
        "engine_id": ENGINE_ID,
        "source": {
            "project_id": str(blueprint["project"]["project_id"]),
            "revision_id": str(revision_id),
            "blueprint_sha256": blueprint_sha256(blueprint),
            "audio_material_sha256": audio_material_sha256(blueprint),
        },
        "mix_sample_rate_hz": mix_sample_rate_hz,
        "duration_frames": duration_frames,
        "policy": {
            "time_quantization": "nonnegative_round_half_up_to_frame",
            "source_rate_policy": "exact_match_required_no_resampling",
            "channel_policy": "mono_or_stereo_to_stereo",
            "internal_precision": "float64",
            "pan_law": "linear_balance",
            "mute_solo_precedence": "mute_wins_then_solo_isolates",
            "summing_order": "track_order_track_id_then_timeline_clip_id",
            "clipping": "hard_clip_unit_range_before_pcm16",
            "output_format": "wav_pcm16_stereo_little_endian",
        },
        "tracks": plan_tracks,
    }
    plan = dict(plan_base)
    plan["mix_plan_sha256"] = _sha256(canonical_json_bytes(plan_base))
    validate_contract(plan, "native-mix-plan-v0.schema.json")
    return plan


def _decode_pcm_frames(data: bytes) -> tuple[int, int, int, list[tuple[float, ...]]]:
    try:
        stream = io.BytesIO(data)
        with wave.open(stream, "rb") as reader:
            if reader.getcomptype() != "NONE":
                raise ContractError("native mixer supports only uncompressed integer PCM WAV")
            channels = int(reader.getnchannels())
            sample_width = int(reader.getsampwidth())
            sample_rate = int(reader.getframerate())
            frame_count = int(reader.getnframes())
            payload = reader.readframes(frame_count)
    except (wave.Error, EOFError) as exc:
        raise ContractError("native mixer cannot decode malformed WAV") from exc
    if channels not in (1, 2) or sample_width not in (1, 2, 3, 4):
        raise ContractError("native mixer WAV format is outside the bounded v0 policy")
    frame_size = channels * sample_width
    if len(payload) != frame_count * frame_size:
        raise ContractError("native mixer WAV payload length mismatch")
    frames: list[tuple[float, ...]] = []
    for frame_index in range(frame_count):
        base = frame_index * frame_size
        values: list[float] = []
        for channel in range(channels):
            start = base + channel * sample_width
            raw = payload[start:start + sample_width]
            if sample_width == 1:
                integer, scale = raw[0] - 128, 128.0
            elif sample_width == 2:
                integer, scale = int.from_bytes(raw, "little", signed=True), 32768.0
            elif sample_width == 3:
                integer = int.from_bytes(raw + (b"\xff" if raw[2] & 0x80 else b"\x00"), "little", signed=True)
                scale = 8388608.0
            else:
                integer, scale = int.from_bytes(raw, "little", signed=True), 2147483648.0
            values.append(float(integer) / scale)
        frames.append(tuple(values))
    return channels, sample_width, sample_rate, frames


def _pcm16_sample(value: float) -> int:
    clipped = max(-1.0, min(1.0, float(value)))
    scaled = clipped * 32768.0
    integer = int(math.floor(scaled + 0.5)) if scaled >= 0.0 else int(math.ceil(scaled - 0.5))
    return max(-32768, min(32767, integer))


@dataclass(frozen=True)
class NativeMixRender:
    plan: dict[str, Any]
    wav_bytes: bytes
    wav_sha256: str
    peak_pre_clip: float
    clipped_sample_count: int

    def report(self) -> dict[str, Any]:
        return {
            "mix_plan_sha256": self.plan["mix_plan_sha256"],
            "wav_sha256": self.wav_sha256,
            "wav_size_bytes": len(self.wav_bytes),
            "peak_pre_clip": self.peak_pre_clip,
            "clipped_sample_count": self.clipped_sample_count,
            "rendered_audio_is_canonical": False,
        }


def render_native_mix(project: Any, revision_id: str, *, mix_sample_rate_hz: int) -> NativeMixRender:
    """Render deterministic stereo PCM16 WAV bytes from one accepted revision."""
    plan = build_native_mix_plan(project, revision_id, mix_sample_rate_hz=mix_sample_rate_hz)
    duration_frames = int(plan["duration_frames"])
    left = [0.0] * duration_frames
    right = [0.0] * duration_frames
    decoded_cache: dict[str, tuple[int, int, int, list[tuple[float, ...]]]] = {}
    for track in plan["tracks"]:
        mixer = track["mixer"]
        if not mixer["audible"]:
            continue
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
                raise ContractError(f"native mixer channel metadata changed: {asset_id}")
            if sample_width != int(clip["sample_width_bytes"]):
                raise ContractError(f"native mixer sample-width metadata changed: {asset_id}")
            if sample_rate != int(clip["sample_rate_hz"]):
                raise ContractError(f"native mixer sample-rate metadata changed: {asset_id}")
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
    return NativeMixRender(plan=plan, wav_bytes=wav_bytes, wav_sha256=_sha256(wav_bytes), peak_pre_clip=peak_pre_clip, clipped_sample_count=clipped_sample_count)
