"""MRAM-R2 deterministic lowering for accepted native mixer automation.

The canonical authority remains Blueprint automation material. This module binds an
exact accepted revision and lowers only native audio-track/routing-node gain/pan lanes
into frame-domain derived data consumed by the routed offline mixer.
"""

from __future__ import annotations

import hashlib
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from .automation_contracts import native_mixer_automation_lanes
from .automation_edit import automation_material_sha256, blueprint_sha256
from .audio_contracts import validate_project_blueprint_audio
from .audio_edit import audio_material_sha256
from .contracts import ContractError, validate_contract
from .evidence import canonical_json_bytes
from .native_mixer import _frame_index
from .routing_contracts import (
    routing_material_from_blueprint,
    routing_material_sha256,
    validate_blueprint_routing,
)

COMPILER_ID = "musica-native-mixer-automation-lowering-v0"


def beat_to_frame(
    beat: int | float | str | Decimal,
    *,
    bpm: int | float | str | Decimal,
    sample_rate_hz: int,
) -> int:
    """Convert quarter-note beats to frames with explicit Decimal half-up rounding."""

    beat_value = Decimal(str(beat))
    bpm_value = Decimal(str(bpm))
    if beat_value < 0:
        raise ContractError("native mixer automation beat cannot be negative")
    if bpm_value <= 0:
        raise ContractError("native mixer automation requires positive fixed BPM")
    frames = (
        beat_value
        * Decimal(60)
        * Decimal(int(sample_rate_hz))
        / bpm_value
    ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(frames)


def _lane_plan(
    lane: dict[str, Any],
    *,
    bpm: float,
    sample_rate_hz: int,
    duration_frames: int,
) -> dict[str, Any]:
    target = lane["target"]
    points = [
        {
            "point_id": str(point["point_id"]),
            "beat": point["beat"],
            "frame": beat_to_frame(
                point["beat"], bpm=bpm, sample_rate_hz=sample_rate_hz
            ),
            "value": point["value"],
            "interpolation": str(point["interpolation"]),
        }
        for point in lane["points"]
    ]
    frames = [int(point["frame"]) for point in points]
    if len(frames) != len(set(frames)):
        raise ContractError(
            f"native mixer automation lane {lane['lane_id']} has distinct beats that "
            "collapse to one frame"
        )
    if any(frame > duration_frames for frame in frames):
        raise ContractError(
            f"native mixer automation lane {lane['lane_id']} exceeds project frame duration"
        )

    segments = [
        {
            "start_point_id": start["point_id"],
            "end_point_id": end["point_id"],
            "start_frame": start["frame"],
            "end_frame": end["frame"],
            "start_value": start["value"],
            "end_value": end["value"],
            "interpolation": start["interpolation"],
        }
        for start, end in zip(points, points[1:])
    ]
    return {
        "lane_id": str(lane["lane_id"]),
        "target_kind": str(target["scope"]),
        "target_id": str(target["owner_id"]),
        "parameter_id": str(target["parameter_id"]),
        "unit": str(target["unit"]),
        "minimum": target["minimum"],
        "maximum": target["maximum"],
        "points": points,
        "segments": segments,
    }


def validate_native_mixer_automation_plan(plan: dict[str, Any]) -> None:
    validate_contract(plan, "native-mixer-automation-plan-v0.schema.json")
    base = dict(plan)
    claimed = str(base.pop("native_mixer_automation_plan_sha256"))
    actual = hashlib.sha256(canonical_json_bytes(base)).hexdigest()
    if claimed != actual:
        raise ContractError("native mixer automation plan SHA-256 mismatch")

    lane_ids = [str(lane["lane_id"]) for lane in plan["lanes"]]
    if lane_ids != sorted(lane_ids):
        raise ContractError("native mixer automation plan lanes must use lane_id order")
    if len(lane_ids) != len(set(lane_ids)):
        raise ContractError("native mixer automation plan lane_id must be unique")

    targets: list[tuple[str, str, str]] = []
    for lane in plan["lanes"]:
        target = (
            str(lane["target_kind"]),
            str(lane["target_id"]),
            str(lane["parameter_id"]),
        )
        targets.append(target)
        points = lane["points"]
        frames = [int(point["frame"]) for point in points]
        if frames != sorted(frames) or len(frames) != len(set(frames)):
            raise ContractError(
                f"native mixer automation lane {lane['lane_id']} frames must be unique and ordered"
            )
        if len(lane["segments"]) != max(0, len(points) - 1):
            raise ContractError(
                f"native mixer automation lane {lane['lane_id']} segment count mismatch"
            )
        for index, segment in enumerate(lane["segments"]):
            start = points[index]
            end = points[index + 1]
            expected = {
                "start_point_id": start["point_id"],
                "end_point_id": end["point_id"],
                "start_frame": start["frame"],
                "end_frame": end["frame"],
                "start_value": start["value"],
                "end_value": end["value"],
                "interpolation": start["interpolation"],
            }
            if segment != expected:
                raise ContractError(
                    f"native mixer automation lane {lane['lane_id']} segment mismatch"
                )
    if len(targets) != len(set(targets)):
        raise ContractError("native mixer automation target identity must be unique")


def build_native_mixer_automation_plan(
    project: Any,
    revision_id: str,
    *,
    mix_sample_rate_hz: int,
) -> dict[str, Any]:
    """Lower native mixer automation from one exact accepted routed revision."""

    if not isinstance(mix_sample_rate_hz, int) or not 8000 <= mix_sample_rate_hz <= 192000:
        raise ContractError("mix_sample_rate_hz must be an integer between 8000 and 192000")

    blueprint = project.read_revision(revision_id)
    if str(blueprint["project"]["revision_id"]) != str(revision_id):
        raise ContractError("native mixer automation revision binding mismatch")
    validate_project_blueprint_audio(project, blueprint)
    validate_blueprint_routing(blueprint, allow_nonempty=True)
    validate_contract(
        blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )

    tempo = blueprint["musical_context"]["tempo"]
    if tempo.get("policy") != "fixed":
        raise ContractError("native mixer automation v0 requires fixed tempo")
    bpm = float(tempo["bpm"])
    duration_frames = _frame_index(
        float(blueprint["project"]["duration_seconds"]), mix_sample_rate_hz
    )
    if duration_frames <= 0:
        raise ContractError("native mixer automation requires positive frame duration")

    routing = routing_material_from_blueprint(blueprint)
    assert routing is not None
    lanes = [
        _lane_plan(
            lane,
            bpm=bpm,
            sample_rate_hz=mix_sample_rate_hz,
            duration_frames=duration_frames,
        )
        for lane in native_mixer_automation_lanes(blueprint)
    ]

    plan_base: dict[str, Any] = {
        "plan_version": "0",
        "compiler_id": COMPILER_ID,
        "classification": "derived_noncanonical",
        "source": {
            "project_id": str(blueprint["project"]["project_id"]),
            "revision_id": str(revision_id),
            "blueprint_sha256": blueprint_sha256(blueprint),
            "automation_material_sha256": automation_material_sha256(blueprint),
            "audio_material_sha256": audio_material_sha256(blueprint),
            "routing_material_sha256": routing_material_sha256(routing),
        },
        "mix_sample_rate_hz": mix_sample_rate_hz,
        "duration_frames": duration_frames,
        "policy": {
            "time_base": "quarter_note_beat_fixed_tempo",
            "frame_quantization": "decimal_nearest_half_up_nonnegative",
            "endpoint_behavior": "hold_first_before_first_hold_last_after_last",
            "segment_interpolation": "outgoing_point_hold_or_linear",
            "parameter_application": "absolute_replaces_static_gain_db_or_pan_when_lane_present",
        },
        "lanes": lanes,
    }
    plan = dict(plan_base)
    plan["native_mixer_automation_plan_sha256"] = hashlib.sha256(
        canonical_json_bytes(plan_base)
    ).hexdigest()
    validate_native_mixer_automation_plan(plan)
    return plan


def automation_lane_map(plan: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    """Index a validated native automation plan by exact stable target identity."""

    validate_native_mixer_automation_plan(plan)
    return {
        (
            str(lane["target_kind"]),
            str(lane["target_id"]),
            str(lane["parameter_id"]),
        ): lane
        for lane in plan["lanes"]
    }


def value_at_frame(lane: dict[str, Any], frame: int) -> float:
    """Resolve one lane's absolute value for a zero-based rendered frame."""

    points = lane["points"]
    if not points:
        raise ContractError("native mixer automation lane has no points")
    index = int(frame)
    if index <= int(points[0]["frame"]):
        return float(points[0]["value"])
    if index >= int(points[-1]["frame"]):
        return float(points[-1]["value"])

    for start, end in zip(points, points[1:]):
        start_frame = int(start["frame"])
        end_frame = int(end["frame"])
        if start_frame <= index < end_frame:
            if str(start["interpolation"]) == "hold":
                return float(start["value"])
            span = end_frame - start_frame
            if span <= 0:
                raise ContractError("native mixer automation segment has non-positive frame span")
            fraction = float(index - start_frame) / float(span)
            return float(start["value"]) + (
                float(end["value"]) - float(start["value"])
            ) * fraction

    raise ContractError("native mixer automation frame resolution failed")
