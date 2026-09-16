"""Typed native-audio contracts for the ATCM commercial-workstation program.

R0 defines the future accepted track/clip/mixer shape without yet granting audio edits,
mixing, Browser state, or imported bytes any acceptance authority.
"""

from __future__ import annotations

import copy
from typing import Any

from .contracts import ContractError, validate_contract


EMPTY_AUDIO_MATERIAL: dict[str, Any] = {
    "material_version": "0",
    "mode": "audio_tracks",
    "tracks": [],
}


def empty_audio_material() -> dict[str, Any]:
    """Return a fresh canonical empty native-audio material."""

    return copy.deepcopy(EMPTY_AUDIO_MATERIAL)


def audio_material_from_blueprint(
    blueprint: dict[str, Any], *, materialize_empty: bool = True
) -> dict[str, Any] | None:
    """Read the optional additive ``materials.audio`` extension.

    R0 deliberately keeps this helper separate from acceptance/edit authority. Later
    ATCM rungs may source-bind and mutate this material only through Preview/Accept.
    """

    materials = blueprint.get("materials", {})
    value = materials.get("audio") if isinstance(materials, dict) else None
    if value is None:
        return empty_audio_material() if materialize_empty else None
    if not isinstance(value, dict):
        raise ContractError("materials.audio must be an object")
    return value


def _require_unique(values: list[Any], label: str) -> None:
    if len(values) != len(set(values)):
        raise ContractError(f"{label} must be unique")


def validate_audio_material(
    material: dict[str, Any], *, project_duration_seconds: float | None = None
) -> None:
    """Validate native audio schema plus deterministic cross-field invariants."""

    validate_contract(material, "audio-material-v0.schema.json")
    tracks = material["tracks"]

    track_ids = [str(track["track_id"]) for track in tracks]
    track_orders = [int(track["order"]) for track in tracks]
    _require_unique(track_ids, "audio track_id")
    _require_unique(track_orders, "audio track order")

    track_keys = [(int(track["order"]), str(track["track_id"])) for track in tracks]
    if track_keys != sorted(track_keys):
        raise ContractError("audio tracks must use canonical order (order, track_id)")

    global_clip_ids: list[str] = []
    for track in tracks:
        track_id = str(track["track_id"])
        clips = track["clips"]
        clip_ids = [str(clip["clip_id"]) for clip in clips]
        _require_unique(clip_ids, f"audio clip_id in track {track_id}")
        global_clip_ids.extend(clip_ids)

        clip_keys = [
            (float(clip["timeline_start_seconds"]), str(clip["clip_id"]))
            for clip in clips
        ]
        if clip_keys != sorted(clip_keys):
            raise ContractError(
                f"audio clips in track {track_id} must use canonical order "
                "(timeline_start_seconds, clip_id)"
            )

        for clip in clips:
            clip_id = str(clip["clip_id"])
            source_in = float(clip["source_in_seconds"])
            source_out = float(clip["source_out_seconds"])
            if source_out <= source_in:
                raise ContractError(
                    f"audio clip {clip_id} source_out_seconds must exceed source_in_seconds"
                )
            if project_duration_seconds is not None:
                duration = source_out - source_in
                timeline_end = float(clip["timeline_start_seconds"]) + duration
                if timeline_end > float(project_duration_seconds) + 1e-9:
                    raise ContractError(
                        f"audio clip {clip_id} exceeds project duration"
                    )

    _require_unique(global_clip_ids, "audio clip_id across material")


def validate_blueprint_audio(blueprint: dict[str, Any]) -> None:
    """Explicitly validate the optional R0 audio extension of a Blueprint."""

    value = audio_material_from_blueprint(blueprint, materialize_empty=False)
    if value is None:
        return
    duration = float(blueprint["project"]["duration_seconds"])
    validate_audio_material(value, project_duration_seconds=duration)
