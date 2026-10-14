"""PLUG-R2-B K0: causal, detached two-path signal-alignment reference.

This is a real numerical two-path delay-alignment kernel, but NOT an accepted
MUSICA plugin host or routing integration. Its declared algorithmic latencies
are *simulated reference inputs*, distinct from intentional creative delays.
No result can mutate accepted Project/Blueprint authority.
"""
from __future__ import annotations

import hashlib
import io
import struct
import wave
from dataclasses import dataclass
from typing import Any

from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .native_mixer import _pcm16_sample

ENGINE_ID = "musica-two-path-pdc-reference-v0"
MAX_LATENCY = 4096
MAX_FRAMES = 1_000_000


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_wav(payload: bytes, expected_rate: int | None = None) -> tuple[int, list[tuple[int, int]]]:
    """Validate exact PCM stereo input and reject mismatched/truncated payloads."""
    try:
        with wave.open(io.BytesIO(payload), "rb") as reader:
            if reader.getcomptype() != "NONE":
                raise ContractError("two-path alignment requires uncompressed PCM16")
            if reader.getnchannels() != 2 or reader.getsampwidth() != 2:
                raise ContractError("two-path alignment requires stereo PCM16")
            rate = reader.getframerate()
            if type(rate) is not int or not 8000 <= rate <= 192000:
                raise ContractError("unsupported sample rate")
            if expected_rate is not None and rate != expected_rate:
                raise ContractError("two-path sample-rate mismatch")
            count = reader.getnframes()
            if not 1 <= count <= MAX_FRAMES:
                raise ContractError("unsupported two-path duration")
            data = reader.readframes(count)
    except (EOFError, wave.Error, OSError) as exc:
        raise ContractError("invalid two-path WAV input") from exc
    if len(data) != count * 4:
        raise ContractError("truncated two-path WAV input")
    return rate, list(struct.iter_unpack("<hh", data))


def _validate_delay(value: Any, field: str) -> int:
    if type(value) is not int or not 0 <= value <= MAX_LATENCY:
        raise ContractError(f"unsupported {field}; expected integer frames 0..{MAX_LATENCY}")
    return value


def validate_two_path_alignment_plan(plan: dict[str, Any]) -> None:
    """Validate schema/self-hash, unique path identity and causal offset rules."""
    validate_contract(plan, "plugin-two-path-alignment-reference-v0.schema.json")
    without_hash = dict(plan)
    claimed = without_hash.pop("plugin_two_path_alignment_plan_sha256")
    if _sha(canonical_json_bytes(without_hash)) != claimed:
        raise ContractError("two-path alignment plan self-hash mismatch")
    paths = plan["paths"]
    ids = [str(path["path_id"]) for path in paths]
    if ids != sorted(ids) or len(set(ids)) != 2:
        raise ContractError("two-path alignment requires two distinct sorted path IDs")
    effective: list[int] = []
    for path in paths:
        declared = _validate_delay(
            path["declared_algorithmic_latency_frames"], "algorithmic latency"
        )
        _validate_delay(path["creative_delay_frames"], "creative delay")
        actual = path["effective_algorithmic_latency_frames"]
        expected = 0 if path["bypass"] else declared
        if type(actual) is not int or actual != expected:
            raise ContractError("two-path alignment bypass/effective latency mismatch")
        effective.append(actual)
    reference = max(effective)
    if plan["reference_algorithmic_latency_frames"] != reference:
        raise ContractError("two-path alignment reference latency mismatch")
    for path, delay in zip(paths, effective, strict=True):
        adjustment = path["compensation_frames"]
        if type(adjustment) is not int or adjustment != reference - delay:
            raise ContractError("two-path alignment compensation offset mismatch")


def build_two_path_alignment_plan(
    paths: list[dict[str, Any]],
    *,
    sample_rate_hz: int,
    input_wav_by_path: dict[str, bytes],
) -> dict[str, Any]:
    """Plan from exactly two explicit detached WAV paths and simulated latencies.

    Each config has path_id, algorithmic_latency_frames, creative_delay_frames
    and bypass; all fields required. No accepted plugin material is inferred.
    """
    if type(sample_rate_hz) is not int or not 8000 <= sample_rate_hz <= 192000:
        raise ContractError("invalid two-path sample rate")
    if not isinstance(paths, list) or len(paths) != 2:
        raise ContractError("exactly two paths are required")
    ids: list[str] = []
    frames_count: int | None = None
    validated: list[dict[str, Any]] = []
    for item in paths:
        if not isinstance(item, dict) or set(item) != {
            "path_id", "algorithmic_latency_frames", "creative_delay_frames", "bypass"
        }:
            raise ContractError("unexpected two-path reference configuration")
        path_id = item["path_id"]
        if not isinstance(path_id, str) or not path_id:
            raise ContractError("invalid path identity")
        if path_id not in input_wav_by_path:
            raise ContractError("missing two-path WAV identity")
        declared = _validate_delay(item["algorithmic_latency_frames"], "algorithmic latency")
        creative = _validate_delay(item["creative_delay_frames"], "creative delay")
        bypass = item["bypass"]
        if type(bypass) is not bool:
            raise ContractError("bypass must be boolean")
        raw = input_wav_by_path[path_id]
        if not isinstance(raw, bytes):
            raise ContractError("two-path source WAV must be bytes")
        rate, frames = _read_wav(raw, expected_rate=sample_rate_hz)
        assert rate == sample_rate_hz
        if frames_count is None:
            frames_count = len(frames)
        elif frames_count != len(frames):
            raise ContractError("two-path inputs require identical duration")
        ids.append(path_id)
        validated.append({
            "path_id": path_id,
            "input_wav_sha256": _sha(raw),
            "declared_algorithmic_latency_frames": declared,
            "creative_delay_frames": creative,
            "bypass": bypass,
            "effective_algorithmic_latency_frames": 0 if bypass else declared,
        })
    if len(set(ids)) != 2 or set(input_wav_by_path) != set(ids):
        raise ContractError("two-path inputs require exact unique path identities")
    validated.sort(key=lambda item: item["path_id"])
    reference = max(p["effective_algorithmic_latency_frames"] for p in validated)
    for path in validated:
        path["compensation_frames"] = reference - path["effective_algorithmic_latency_frames"]

    base = {
        "plan_version": "0",
        "engine_id": ENGINE_ID,
        "classification": "detached_derived_reference_only",
        "sample_rate_hz": sample_rate_hz,
        "channels": 2,
        "sample_format": "pcm16_stereo_little_endian",
        "duration_frames": frames_count,
        "policy": {
            "topology": "two_independent_stereo_paths_to_one_output",
            "algorithmic_latency_provenance": "simulated_explicit_reference_only",
            "creative_delay_policy": "preserved_not_compensated",
            "alignment": "delay_faster_path_to_max_algorithmic_latency",
            "time": "causal_fixed_length_truncate_tail_no_lookahead",
            "host_authority": "none_detached_not_accepted",
        },
        "reference_algorithmic_latency_frames": reference,
        "paths": validated,
    }
    plan = dict(base)
    plan["plugin_two_path_alignment_plan_sha256"] = _sha(canonical_json_bytes(base))
    validate_two_path_alignment_plan(plan)
    return plan


@dataclass(frozen=True)
class TwoPathReferenceRender:
    plan: dict[str, Any]
    wav_bytes: bytes
    wav_sha256: str

    def report(self) -> dict[str, Any]:
        return {
            "plan_sha256": self.plan["plugin_two_path_alignment_plan_sha256"],
            "wav_sha256": self.wav_sha256,
            "reference_algorithmic_latency_frames": self.plan[
                "reference_algorithmic_latency_frames"
            ],
            "accepted_state_mutation_authorized": False,
            "host_pdc_integrated": False,
        }


def render_two_path_alignment(
    plan: dict[str, Any],
    *,
    input_wav_by_path: dict[str, bytes],
    force_error_path_ids: set[str] | None = None,
    compensate: bool = True,
) -> TwoPathReferenceRender:
    """Perform causal delays then stereo sum; no future reads or state writes."""
    validate_two_path_alignment_plan(plan)
    if set(input_wav_by_path) != {path["path_id"] for path in plan["paths"]}:
        raise ContractError("two-path render input identities mismatch")
    if type(compensate) is not bool:
        raise ContractError("invalid two-path compensation switch")
    forced = force_error_path_ids or set()
    if not isinstance(forced, set) or not all(isinstance(x, str) for x in forced):
        raise ContractError("invalid forced-error paths")
    if forced - set(input_wav_by_path):
        raise ContractError("unknown forced-error path")
    count = plan["duration_frames"]
    sums = [[0.0, 0.0] for _ in range(count)]
    for path in plan["paths"]:
        name = path["path_id"]
        raw = input_wav_by_path[name]
        if not isinstance(raw, bytes) or _sha(raw) != path["input_wav_sha256"]:
            raise ContractError("stale or forged two-path WAV bytes")
        rate, frames = _read_wav(raw, expected_rate=plan["sample_rate_hz"])
        if len(frames) != count or rate != plan["sample_rate_hz"]:
            raise ContractError("two-path WAV duration/rate changed")
        if name in forced and not path["bypass"]:
            raise ContractError(f"two-path forced processor error: {name}")
        offset = (
            path["effective_algorithmic_latency_frames"]
            + path["creative_delay_frames"]
            + (path["compensation_frames"] if compensate else 0)
        )
        if offset >= count:
            raise ContractError("two-path entire branch exceeds fixed output duration")
        for source_index, (left, right) in enumerate(frames):
            destination = source_index + offset
            if destination >= count:
                break
            sums[destination][0] += left / 32768.0
            sums[destination][1] += right / 32768.0
    payload = bytearray()
    for left, right in sums:
        payload.extend(struct.pack("<hh", _pcm16_sample(left), _pcm16_sample(right)))
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(plan["sample_rate_hz"])
        writer.writeframes(bytes(payload))
    result = stream.getvalue()
    return TwoPathReferenceRender(plan=plan, wav_bytes=result, wav_sha256=_sha(result))
