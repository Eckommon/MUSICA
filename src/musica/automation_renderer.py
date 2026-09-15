"""M7-R4 bounded reference-renderer automation mapping and audible WAV path.

This module consumes validated M7-R3 automation execution plus validated Music IR,
builds one renderer-specific derived plan, and applies only canonical `mix.gain` with
project scope and normalized unit to the deterministic reference WAV output.

It deliberately does not reuse MIDI CC11, mutate R3 execution, or grant rendered audio
any reverse authority over accepted Blueprint automation.
"""

from __future__ import annotations

import hashlib
import io
import struct
import wave
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from .automation_lowering import validate_automation_execution
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .render import DEFAULT_SAMPLE_RATE, RENDERER_VERSION, wav_bytes
from .renderer import REFERENCE_ADAPTER_VERSION, REFERENCE_RENDERER_ID, music_ir_sha256

AUTOMATION_RENDER_POLICY_ID = "reference-renderer-mix-gain-v0"
AUTOMATION_RENDER_POLICY_VERSION = "0.1.0"
AUTOMATION_RENDER_MAPPING_ID = "reference.mix_gain.normalized"
AUTOMATION_RENDER_APPLICATION = "post_normalization_pcm_gain"


def automation_execution_sha256(execution: dict[str, Any]) -> str:
    validate_automation_execution(execution)
    return hashlib.sha256(canonical_json_bytes(execution)).hexdigest()


def automation_render_plan_sha256(plan: dict[str, Any]) -> str:
    validate_contract(plan, "automation-render-plan-v0.schema.json")
    return hashlib.sha256(canonical_json_bytes(plan)).hexdigest()


def _reference_renderer_version() -> str:
    return f"adapter-{REFERENCE_ADAPTER_VERSION}/core-{RENDERER_VERSION}"


def _unmapped_lane(lane: dict[str, Any], code: str, reason: str) -> dict[str, Any]:
    return {
        "lane_id": str(lane["lane_id"]),
        "parameter_id": str(lane["parameter_id"]),
        "scope": str(lane["scope"]),
        "unit": str(lane["unit"]),
        "code": code,
        "reason": reason,
    }


def _mapping_eligibility(lane: dict[str, Any]) -> tuple[bool, str | None, str | None]:
    if str(lane["parameter_id"]) != "mix.gain":
        return False, "UNSUPPORTED_PARAMETER", "reference renderer R4 maps only mix.gain"
    if str(lane["scope"]) != "project" or lane.get("owner_id") is not None:
        return False, "UNSUPPORTED_SCOPE", "mix.gain R4 mapping requires project scope"
    if str(lane["unit"]) != "normalized":
        return False, "UNSUPPORTED_UNIT", "mix.gain R4 mapping requires normalized unit"
    if lane.get("section_id") is not None:
        return False, "SECTION_SCOPED_UNSUPPORTED", "R4 project mix.gain mapping is global only"
    if float(lane["minimum"]) != 0.0 or float(lane["maximum"]) != 1.0:
        return False, "UNSUPPORTED_RANGE", "R4 normalized mix.gain requires declared range [0, 1]"
    return True, None, None


def _mapped_lane(lane: dict[str, Any]) -> dict[str, Any]:
    return {
        "lane_id": str(lane["lane_id"]),
        "parameter_id": "mix.gain",
        "scope": "project",
        "owner_id": None,
        "section_id": None,
        "unit": "normalized",
        "minimum": 0.0,
        "maximum": 1.0,
        "mapping_id": AUTOMATION_RENDER_MAPPING_ID,
        "application": AUTOMATION_RENDER_APPLICATION,
        "points": [
            {
                "point_id": str(point["point_id"]),
                "tick": int(point["tick"]),
                "value": point["value"],
                "interpolation": str(point["interpolation"]),
            }
            for point in lane["points"]
        ],
        "segments": [
            {
                "start_point_id": str(segment["start_point_id"]),
                "end_point_id": str(segment["end_point_id"]),
                "start_tick": int(segment["start_tick"]),
                "end_tick": int(segment["end_tick"]),
                "start_value": segment["start_value"],
                "end_value": segment["end_value"],
                "interpolation": str(segment["interpolation"]),
            }
            for segment in lane["segments"]
        ],
    }


def _validate_sources(music_ir: dict[str, Any], execution: dict[str, Any]) -> None:
    validate_contract(music_ir, "music-ir-v0.schema.json")
    validate_automation_execution(execution)

    if str(music_ir["source_blueprint_revision"]) != str(execution["source"]["revision_id"]):
        raise ContractError("automation renderer source revision does not match Music IR")
    if int(music_ir["timing"]["ppq"]) != int(execution["lowering"]["ppq"]):
        raise ContractError("automation renderer PPQ does not match R3 execution")
    tempo_events = music_ir["tempo_events"]
    if len(tempo_events) != 1 or int(tempo_events[0]["tick"]) != 0:
        raise ContractError("M7-R4 reference automation renderer requires one fixed tempo at tick 0")


def _build_plan_payload(music_ir: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    _validate_sources(music_ir, execution)

    mapped: list[dict[str, Any]] = []
    unmapped: list[dict[str, Any]] = []
    for lane in execution["lanes"]:
        eligible, code, reason = _mapping_eligibility(lane)
        if eligible:
            mapped.append(_mapped_lane(lane))
        else:
            assert code is not None and reason is not None
            unmapped.append(_unmapped_lane(lane, code, reason))

    if len(mapped) > 1:
        raise ContractError("M7-R4 reference renderer permits at most one global mix.gain lane")

    return {
        "plan_version": "0",
        "classification": "derived_noncanonical",
        "source": {
            "project_id": str(execution["source"]["project_id"]),
            "revision_id": str(execution["source"]["revision_id"]),
            "music_ir_sha256": music_ir_sha256(music_ir),
            "automation_execution_sha256": automation_execution_sha256(execution),
        },
        "renderer": {
            "renderer_id": REFERENCE_RENDERER_ID,
            "renderer_version": _reference_renderer_version(),
        },
        "mapping": {
            "policy_id": AUTOMATION_RENDER_POLICY_ID,
            "policy_version": AUTOMATION_RENDER_POLICY_VERSION,
            "application_stage": "post_synthesis_post_safety_normalization",
            "time_domain": "music_ir_tick",
            "output": "wav_pcm_gain",
        },
        "authority": {
            "canonical": False,
            "project_mutation_authorized": False,
            "blueprint_mutation_authorized": False,
            "reverse_promotion_authorized": False,
            "midi_cc_semantics_authorized": False,
            "renderer_application_authorized": True,
            "audible_automation_evidence_required": True,
        },
        "mapped_lanes": mapped,
        "unmapped_lanes": unmapped,
    }


def build_automation_render_plan(
    music_ir: dict[str, Any], execution: dict[str, Any]
) -> dict[str, Any]:
    """Build the deterministic, renderer-specific M7-R4 plan without mutating inputs."""

    plan = _build_plan_payload(music_ir, execution)
    validate_contract(plan, "automation-render-plan-v0.schema.json")
    return plan


def validate_automation_render_plan(
    plan: dict[str, Any], music_ir: dict[str, Any], execution: dict[str, Any]
) -> None:
    """Fail closed if a supplied plan does not exactly match its bound source objects."""

    validate_contract(plan, "automation-render-plan-v0.schema.json")
    expected = _build_plan_payload(music_ir, execution)
    if plan != expected:
        raise ContractError("automation render plan does not exactly match bound Music IR/execution")


def _gain_at_tick_unvalidated(plan: dict[str, Any], position: Decimal) -> Decimal:
    if not plan["mapped_lanes"]:
        return Decimal("1")

    lane = plan["mapped_lanes"][0]
    points = lane["points"]
    first = points[0]
    last = points[-1]
    if position <= Decimal(int(first["tick"])):
        return Decimal(str(first["value"]))

    for segment in lane["segments"]:
        start_tick = Decimal(int(segment["start_tick"]))
        end_tick = Decimal(int(segment["end_tick"]))
        if start_tick <= position < end_tick:
            start_value = Decimal(str(segment["start_value"]))
            if segment["interpolation"] == "hold":
                return start_value
            end_value = Decimal(str(segment["end_value"]))
            ratio = (position - start_tick) / (end_tick - start_tick)
            return start_value + (end_value - start_value) * ratio

    return Decimal(str(last["value"]))


def gain_at_tick(plan: dict[str, Any], tick: int | float | str | Decimal) -> Decimal:
    """Evaluate the bounded global gain envelope at a Music-IR tick position."""

    validate_contract(plan, "automation-render-plan-v0.schema.json")
    position = Decimal(str(tick))
    if position < 0:
        raise ContractError("automation renderer tick cannot be negative")
    return _gain_at_tick_unvalidated(plan, position)


def _apply_gain_plan_to_wav(
    baseline_wav: bytes,
    plan: dict[str, Any],
    *,
    bpm: float,
    ppq: int,
    sample_rate: int,
) -> bytes:
    if not plan["mapped_lanes"]:
        return baseline_wav

    source = io.BytesIO(baseline_wav)
    with wave.open(source, "rb") as reader:
        params = reader.getparams()
        if reader.getnchannels() != 1 or reader.getsampwidth() != 2:
            raise ContractError("M7-R4 reference automation renderer requires mono 16-bit PCM")
        if reader.getframerate() != sample_rate:
            raise ContractError("M7-R4 sample rate does not match baseline WAV")
        frames = reader.readframes(reader.getnframes())

    tick_per_sample = (
        Decimal(str(bpm)) * Decimal(int(ppq)) / (Decimal(int(sample_rate)) * Decimal(60))
    )

    # Compile invariant plan values once. The previous implementation rebuilt these
    # Decimal constants and rescanned all segments for every sample. Positions are
    # monotonic, so the active segment can advance only forward while preserving the
    # exact same Decimal interpolation and ROUND_HALF_UP PCM semantics.
    lane = plan["mapped_lanes"][0]
    points = lane["points"]
    first_tick = Decimal(int(points[0]["tick"]))
    first_value = Decimal(str(points[0]["value"]))
    last_value = Decimal(str(points[-1]["value"]))
    segments = [
        (
            Decimal(int(segment["start_tick"])),
            Decimal(int(segment["end_tick"])),
            Decimal(str(segment["start_value"])),
            Decimal(str(segment["end_value"])),
            str(segment["interpolation"]),
        )
        for segment in lane["segments"]
    ]
    segment_index = 0

    pcm = bytearray()
    for index, packed in enumerate(struct.iter_unpack("<h", frames)):
        sample = int(packed[0])
        position = Decimal(index) * tick_per_sample
        if position <= first_tick:
            gain = first_value
        else:
            while (
                segment_index < len(segments)
                and position >= segments[segment_index][1]
            ):
                segment_index += 1
            if segment_index >= len(segments):
                gain = last_value
            else:
                start_tick, end_tick, start_value, end_value, interpolation = segments[
                    segment_index
                ]
                if interpolation == "hold":
                    gain = start_value
                else:
                    ratio = (position - start_tick) / (end_tick - start_tick)
                    gain = start_value + (end_value - start_value) * ratio

        scaled = (Decimal(sample) * gain).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        value = max(-32768, min(32767, int(scaled)))
        pcm.extend(struct.pack("<h", value))

    target = io.BytesIO()
    with wave.open(target, "wb") as writer:
        writer.setparams(params)
        writer.writeframes(bytes(pcm))
    return target.getvalue()


def automation_wav_bytes(
    music_ir: dict[str, Any],
    execution: dict[str, Any],
    *,
    duration_seconds: float,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> bytes:
    """Render reference WAV then apply the explicit R4 post-normalization gain envelope."""

    music_ir_before = canonical_json_bytes(music_ir)
    execution_before = canonical_json_bytes(execution)
    plan = build_automation_render_plan(music_ir, execution)
    validate_automation_render_plan(plan, music_ir, execution)

    baseline = wav_bytes(music_ir, duration_seconds=duration_seconds, sample_rate=sample_rate)
    bpm = float(music_ir["tempo_events"][0]["bpm"])
    output = _apply_gain_plan_to_wav(
        baseline,
        plan,
        bpm=bpm,
        ppq=int(music_ir["timing"]["ppq"]),
        sample_rate=sample_rate,
    )

    if canonical_json_bytes(music_ir) != music_ir_before:
        raise ContractError("automation renderer mutated Music IR")
    if canonical_json_bytes(execution) != execution_before:
        raise ContractError("automation renderer mutated R3 execution")
    return output


def render_automation_wav(
    music_ir: dict[str, Any],
    execution: dict[str, Any],
    path: str | Path,
    *,
    duration_seconds: float,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(
        automation_wav_bytes(
            music_ir,
            execution,
            duration_seconds=duration_seconds,
            sample_rate=sample_rate,
        )
    )
    return target
