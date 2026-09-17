"""Typed native-audio contracts for the ATCM commercial-workstation program.

R0 established the immutable source-audio/resource boundary. R1 adds project-bound
asset/reference validation and a provenance-readable shape for trusted Preview/Accept
revisions without making a provenance marker itself sufficient commit authority.
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

AUDIO_AUTHORITY_MECHANISM_PREFIX = "audio_edit_candidate:"


def empty_audio_material() -> dict[str, Any]:
    """Return a fresh canonical empty native-audio material."""

    return copy.deepcopy(EMPTY_AUDIO_MATERIAL)


def audio_material_from_blueprint(
    blueprint: dict[str, Any], *, materialize_empty: bool = True
) -> dict[str, Any] | None:
    """Read the optional additive ``materials.audio`` extension."""

    materials = blueprint.get("materials", {})
    value = materials.get("audio") if isinstance(materials, dict) else None
    if value is None:
        return empty_audio_material() if materialize_empty else None
    if not isinstance(value, dict):
        raise ContractError("materials.audio must be an object")
    return value


def has_audio_authority_provenance(blueprint: dict[str, Any]) -> bool:
    """Return whether the Blueprint carries durable R1 audio-edit provenance.

    This marker makes an already-authorized accepted revision structurally readable.
    It is deliberately *not* sufficient to authorize project mutation; the Project
    Engine separately blocks audio-material changes unless the trusted R1 accept path
    invokes its internal audio-authorized commit boundary.
    """

    provenance = blueprint.get("provenance", {})
    mechanisms = provenance.get("selected_mechanisms", []) if isinstance(provenance, dict) else []
    if not isinstance(mechanisms, list):
        return False
    return any(
        isinstance(value, str) and value.startswith(AUDIO_AUTHORITY_MECHANISM_PREFIX)
        for value in mechanisms
    )


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


def validate_blueprint_audio(
    blueprint: dict[str, Any], *, allow_nonempty: bool = False
) -> None:
    """Validate the optional audio extension without granting mutation authority.

    R0 keeps non-empty native audio fail-closed by default. R1 accepted revisions carry
    durable ``audio_edit_candidate:*`` provenance so they remain readable by generic
    Blueprint/revision validation after acceptance. Mutation authority is still enforced
    separately by the Project Engine and cannot be obtained merely by forging this marker.
    """

    value = audio_material_from_blueprint(blueprint, materialize_empty=False)
    if value is None:
        return
    duration = float(blueprint["project"]["duration_seconds"])
    validate_audio_material(value, project_duration_seconds=duration)
    if value["tracks"] and not (allow_nonempty or has_audio_authority_provenance(blueprint)):
        raise ContractError(
            "ATCM-R0 does not grant accepted non-empty native audio material authority"
        )


def validate_project_audio_material(
    project: Any,
    material: dict[str, Any],
    *,
    project_duration_seconds: float | None = None,
) -> None:
    """Validate native audio material against exact immutable assets in one project."""

    validate_audio_material(material, project_duration_seconds=project_duration_seconds)

    # Local import avoids a module cycle: audio_assets uses MusicaProject storage helpers.
    from .audio_assets import read_audio_asset

    epsilon = 1e-9
    for track in material["tracks"]:
        for clip in track["clips"]:
            clip_id = str(clip["clip_id"])
            asset_id = str(clip["asset_id"])
            descriptor = read_audio_asset(project, asset_id)
            asset_duration = float(descriptor["format"]["duration_seconds"])
            source_out = float(clip["source_out_seconds"])
            if source_out > asset_duration + epsilon:
                raise ContractError(
                    f"audio clip {clip_id} source_out_seconds {source_out} exceeds "
                    f"asset duration {asset_duration}: {asset_id}"
                )


def validate_project_blueprint_audio(project: Any, blueprint: dict[str, Any]) -> None:
    """Validate one accepted/candidate Blueprint against project-owned audio assets."""

    material = audio_material_from_blueprint(blueprint)
    assert material is not None
    validate_project_audio_material(
        project,
        material,
        project_duration_seconds=float(blueprint["project"]["duration_seconds"]),
    )
