"""ATCM-R1 trusted native-audio track/clip edit authority.

Audio edits produce a non-canonical Blueprint preview. Imported bytes remain immutable
project resources; Preview never advances an accepted ref. Explicit Accept revalidates
the exact source revision and every project-bound audio asset before invoking the
Project Engine's internal audio-authorized commit boundary.
"""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any

from .audio_contracts import (
    audio_material_from_blueprint,
    validate_audio_material,
    validate_project_audio_material,
    validate_project_blueprint_audio,
)
from .contracts import ContractError, validate_contract, validate_revision
from .evidence import canonical_json_bytes

_DEFAULT_MIXER: dict[str, Any] = {
    "gain_db": 0.0,
    "pan": 0.0,
    "mute": False,
    "solo": False,
}


def blueprint_sha256(blueprint: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(blueprint)).hexdigest()


def audio_material_sha256(blueprint: dict[str, Any]) -> str:
    material = audio_material_from_blueprint(blueprint)
    assert material is not None
    return hashlib.sha256(canonical_json_bytes(material)).hexdigest()


def _authority_result(
    candidate_id: str,
    *,
    conflicts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    blocked = bool(conflicts)
    result = {
        "result_version": "0",
        "candidate_id": candidate_id,
        "status": "BLOCKED" if blocked else "READY_FOR_PREVIEW",
        "conflicts": conflicts or [],
        "preview_generation_allowed": not blocked,
        "explicit_accept_required": True,
        "project_mutation_authorized": False,
        "render_mutation_authorized": False,
    }
    validate_contract(result, "audio-authority-result-v0.schema.json")
    return result


def _conflict(
    ordinal: int,
    code: str,
    reason: str,
    *,
    track_id: str | None = None,
    clip_id: str | None = None,
    asset_id: str | None = None,
    rule_id: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "conflict_id": f"ATCM-R1-C-{ordinal:03d}",
        "code": code,
        "reason": reason,
    }
    if track_id is not None:
        value["track_id"] = track_id
    if clip_id is not None:
        value["clip_id"] = clip_id
    if asset_id is not None:
        value["asset_id"] = asset_id
    if rule_id is not None:
        value["rule_id"] = rule_id
    return value


def _revision_id(parent: dict[str, Any], candidate: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json_bytes(candidate)).hexdigest()[:16]
    return f"{parent['project']['revision_id']}-audio-{digest}"


def _actor_for_blueprint(kind: str) -> str:
    return "deterministic_transform" if kind == "system" else kind


def _find_track(material: dict[str, Any], track_id: str) -> dict[str, Any] | None:
    for track in material["tracks"]:
        if str(track["track_id"]) == track_id:
            return track
    return None


def _find_clip(track: dict[str, Any], clip_id: str) -> dict[str, Any] | None:
    for clip in track["clips"]:
        if str(clip["clip_id"]) == clip_id:
            return clip
    return None


def _all_clip_ids(material: dict[str, Any]) -> set[str]:
    return {
        str(clip["clip_id"])
        for track in material["tracks"]
        for clip in track["clips"]
    }


def _sort_material(material: dict[str, Any]) -> None:
    material["tracks"].sort(key=lambda track: (int(track["order"]), str(track["track_id"])))
    for track in material["tracks"]:
        track["clips"].sort(
            key=lambda clip: (float(clip["timeline_start_seconds"]), str(clip["clip_id"]))
        )


def _material_diff(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    before_tracks = {str(track["track_id"]): track for track in before["tracks"]}
    after_tracks = {str(track["track_id"]): track for track in after["tracks"]}
    changes: list[dict[str, Any]] = []
    for track_id in sorted(set(before_tracks) | set(after_tracks)):
        old_track = before_tracks.get(track_id)
        new_track = after_tracks.get(track_id)
        if old_track is None or new_track is None:
            changes.append(
                {
                    "track_id": track_id,
                    "op": "track_presence",
                    "before": copy.deepcopy(old_track),
                    "after": copy.deepcopy(new_track),
                }
            )
            continue
        old_clips = {str(clip["clip_id"]): clip for clip in old_track["clips"]}
        new_clips = {str(clip["clip_id"]): clip for clip in new_track["clips"]}
        for clip_id in sorted(set(old_clips) | set(new_clips)):
            old = old_clips.get(clip_id)
            new = new_clips.get(clip_id)
            if old is None:
                changes.append(
                    {
                        "track_id": track_id,
                        "clip_id": clip_id,
                        "op": "insert",
                        "before": None,
                        "after": copy.deepcopy(new),
                    }
                )
            elif new is None:
                changes.append(
                    {
                        "track_id": track_id,
                        "clip_id": clip_id,
                        "op": "delete",
                        "before": copy.deepcopy(old),
                        "after": None,
                    }
                )
            else:
                fields = {
                    key: {"before": old.get(key), "after": new.get(key)}
                    for key in (
                        "asset_id",
                        "timeline_start_seconds",
                        "source_in_seconds",
                        "source_out_seconds",
                        "gain_db",
                    )
                    if old.get(key) != new.get(key)
                }
                if fields:
                    changes.append(
                        {
                            "track_id": track_id,
                            "clip_id": clip_id,
                            "op": "update",
                            "changed_fields": fields,
                        }
                    )
    return changes


@dataclass(frozen=True)
class AudioEditPreview:
    authority_result: dict[str, Any]
    blueprint: dict[str, Any] | None
    material_diff: list[dict[str, Any]]
    source_revision_id: str
    source_blueprint_sha256: str
    source_audio_material_sha256: str
    candidate_blueprint_sha256: str | None
    candidate_audio_material_sha256: str | None
    changed_track_ids: list[str]
    changed_clip_ids: list[str]
    revision_conflicts: list[dict[str, str]]

    @property
    def ready(self) -> bool:
        return self.authority_result["status"] == "READY_FOR_PREVIEW"

    def as_dict(self) -> dict[str, Any]:
        return {
            "authority_result": copy.deepcopy(self.authority_result),
            "source_revision_id": self.source_revision_id,
            "source_blueprint_sha256": self.source_blueprint_sha256,
            "source_audio_material_sha256": self.source_audio_material_sha256,
            "candidate_blueprint_sha256": self.candidate_blueprint_sha256,
            "candidate_audio_material_sha256": self.candidate_audio_material_sha256,
            "material_diff": copy.deepcopy(self.material_diff),
            "changed_track_ids": list(self.changed_track_ids),
            "changed_clip_ids": list(self.changed_clip_ids),
            "revision_conflicts": copy.deepcopy(self.revision_conflicts),
        }


def _blocked_preview(
    parent: dict[str, Any],
    candidate: dict[str, Any],
    conflicts: list[dict[str, Any]],
) -> AudioEditPreview:
    return AudioEditPreview(
        authority_result=_authority_result(str(candidate["candidate_id"]), conflicts=conflicts),
        blueprint=None,
        material_diff=[],
        source_revision_id=str(parent["project"]["revision_id"]),
        source_blueprint_sha256=blueprint_sha256(parent),
        source_audio_material_sha256=audio_material_sha256(parent),
        candidate_blueprint_sha256=None,
        candidate_audio_material_sha256=None,
        changed_track_ids=[],
        changed_clip_ids=[],
        revision_conflicts=[],
    )


def build_audio_edit_preview(
    project: Any,
    parent_blueprint: dict[str, Any],
    candidate: dict[str, Any],
    *,
    branch: str | None = None,
    revision_id: str | None = None,
) -> AudioEditPreview:
    """Resolve one typed source-bound candidate into a non-canonical audio preview."""

    validate_contract(
        parent_blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    validate_contract(candidate, "audio-edit-candidate-v0.schema.json")
    validate_project_blueprint_audio(project, parent_blueprint)

    selected_branch = branch or project.current_branch()
    source = candidate["source"]
    source_blueprint_hash = blueprint_sha256(parent_blueprint)
    source_material_hash = audio_material_sha256(parent_blueprint)
    parent_revision_id = str(parent_blueprint["project"]["revision_id"])
    stale_reasons: list[str] = []
    if source["project_id"] != parent_blueprint["project"]["project_id"]:
        stale_reasons.append("project_id mismatch")
    if source["revision_id"] != parent_revision_id:
        stale_reasons.append("revision_id mismatch")
    if source["blueprint_sha256"] != source_blueprint_hash:
        stale_reasons.append("blueprint_sha256 mismatch")
    if source["audio_material_sha256"] != source_material_hash:
        stale_reasons.append("audio_material_sha256 mismatch")
    if project.head_revision_id(selected_branch) != parent_revision_id:
        stale_reasons.append("project branch HEAD no longer equals source revision")
    if stale_reasons:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "STALE_SOURCE", "; ".join(stale_reasons))],
        )

    operation_ids = [str(operation["operation_id"]) for operation in candidate["operations"]]
    if len(operation_ids) != len(set(operation_ids)):
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", "operation_id must be unique")],
        )

    parent_material = audio_material_from_blueprint(parent_blueprint)
    assert parent_material is not None
    working = copy.deepcopy(parent_blueprint)
    working_material = copy.deepcopy(parent_material)
    conflicts: list[dict[str, Any]] = []

    for ordinal, operation in enumerate(candidate["operations"], start=1):
        op = str(operation["op"])

        if op == "ADD_TRACK":
            track_id = str(operation["track_id"])
            if _find_track(working_material, track_id) is not None:
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        f"audio track_id already exists: {track_id}",
                        track_id=track_id,
                    )
                )
                continue
            working_material["tracks"].append(
                {
                    "track_id": track_id,
                    "order": int(operation["order"]),
                    "name": str(operation["name"]),
                    "mixer": copy.deepcopy(_DEFAULT_MIXER),
                    "clips": [],
                }
            )
            _sort_material(working_material)
            continue

        target = operation["target"]
        track_id = str(target["track_id"])
        track = _find_track(working_material, track_id)
        if track is None:
            conflicts.append(
                _conflict(
                    ordinal,
                    "UNKNOWN_TRACK",
                    f"unknown audio track: {track_id}",
                    track_id=track_id,
                )
            )
            continue

        if op == "ADD_CLIP":
            clip = copy.deepcopy(operation["clip"])
            clip_id = str(clip["clip_id"])
            asset_id = str(clip["asset_id"])
            if clip_id in _all_clip_ids(working_material):
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNREPRESENTABLE_EDIT",
                        f"audio clip_id already exists: {clip_id}",
                        track_id=track_id,
                        clip_id=clip_id,
                    )
                )
                continue
            track["clips"].append(clip)
            _sort_material(working_material)
            try:
                validate_project_audio_material(
                    project,
                    working_material,
                    project_duration_seconds=float(parent_blueprint["project"]["duration_seconds"]),
                )
            except ContractError as exc:
                track["clips"] = [
                    item for item in track["clips"] if str(item["clip_id"]) != clip_id
                ]
                conflicts.append(
                    _conflict(
                        ordinal,
                        "UNKNOWN_ASSET" if "asset" in str(exc).lower() else "INVALID_RANGE",
                        str(exc),
                        track_id=track_id,
                        clip_id=clip_id,
                        asset_id=asset_id,
                    )
                )
            continue

        clip_id = str(target["clip_id"])
        clip = _find_clip(track, clip_id)
        if clip is None:
            conflicts.append(
                _conflict(
                    ordinal,
                    "UNKNOWN_CLIP",
                    f"unknown audio clip: {track_id}/{clip_id}",
                    track_id=track_id,
                    clip_id=clip_id,
                )
            )
            continue

        if op == "MOVE_CLIP":
            clip["timeline_start_seconds"] = operation["timeline_start_seconds"]
            _sort_material(working_material)
        elif op == "TRIM_CLIP":
            clip["source_in_seconds"] = operation["source_in_seconds"]
            clip["source_out_seconds"] = operation["source_out_seconds"]
        elif op == "SET_CLIP_GAIN":
            clip["gain_db"] = operation["gain_db"]
        else:
            conflicts.append(
                _conflict(
                    ordinal,
                    "UNREPRESENTABLE_EDIT",
                    f"unsupported audio operation: {op}",
                    track_id=track_id,
                    clip_id=clip_id,
                )
            )
            continue

        try:
            validate_project_audio_material(
                project,
                working_material,
                project_duration_seconds=float(parent_blueprint["project"]["duration_seconds"]),
            )
        except ContractError as exc:
            conflicts.append(
                _conflict(
                    ordinal,
                    "INVALID_RANGE" if "source" in str(exc).lower() else "INVALID_TIME",
                    str(exc),
                    track_id=track_id,
                    clip_id=clip_id,
                    asset_id=str(clip["asset_id"]),
                )
            )

    if conflicts:
        return _blocked_preview(parent_blueprint, candidate, conflicts)

    try:
        validate_audio_material(
            working_material,
            project_duration_seconds=float(parent_blueprint["project"]["duration_seconds"]),
        )
        validate_project_audio_material(
            project,
            working_material,
            project_duration_seconds=float(parent_blueprint["project"]["duration_seconds"]),
        )
    except ContractError as exc:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", str(exc))],
        )

    working["materials"]["audio"] = working_material
    working["project"]["parent_revision_id"] = parent_revision_id
    working["project"]["revision_id"] = revision_id or _revision_id(parent_blueprint, candidate)
    provenance = working["provenance"]
    provenance["actor"] = _actor_for_blueprint(str(candidate["actor"]["kind"]))
    provenance["change_reason"] = candidate["reason"]
    provenance["source_revision"] = parent_revision_id
    selected = list(provenance.get("selected_mechanisms", []))
    selected.append(f"audio_edit_candidate:{candidate['candidate_id']}")
    selected.extend(f"audio_edit_operation:{operation_id}" for operation_id in operation_ids)
    provenance["selected_mechanisms"] = selected

    try:
        validate_contract(
            working,
            "music-blueprint-v0.schema.json",
            allow_nonempty_routing=True,
        )
        validate_project_blueprint_audio(project, working)
    except ContractError as exc:
        return _blocked_preview(
            parent_blueprint,
            candidate,
            [_conflict(1, "UNREPRESENTABLE_EDIT", str(exc))],
        )

    revision_conflicts = validate_revision(
        parent_blueprint,
        working,
        allow_nonempty_routing=True,
    )
    blocking = [item for item in revision_conflicts if item.status == "BLOCKED"]
    if blocking:
        mapped: list[dict[str, Any]] = []
        for ordinal, item in enumerate(blocking, start=1):
            code = (
                "HARD_LOCK_VIOLATION"
                if item.rule_type in {"lock", "note_lock", "automation_lock"}
                else "CONSTRAINT_VIOLATION"
                if item.rule_type == "constraint"
                else "UNREPRESENTABLE_EDIT"
            )
            mapped.append(_conflict(ordinal, code, item.reason, rule_id=item.rule_id))
        return _blocked_preview(parent_blueprint, candidate, mapped)

    diff = _material_diff(parent_material, working_material)
    return AudioEditPreview(
        authority_result=_authority_result(str(candidate["candidate_id"])),
        blueprint=working,
        material_diff=diff,
        source_revision_id=parent_revision_id,
        source_blueprint_sha256=source_blueprint_hash,
        source_audio_material_sha256=source_material_hash,
        candidate_blueprint_sha256=blueprint_sha256(working),
        candidate_audio_material_sha256=audio_material_sha256(working),
        changed_track_ids=sorted({str(item["track_id"]) for item in diff}),
        changed_clip_ids=sorted(
            {
                str(item["clip_id"])
                for item in diff
                if item.get("clip_id") is not None
            }
        ),
        revision_conflicts=[item.as_dict() for item in revision_conflicts],
    )


def accept_audio_edit_preview(
    project: Any,
    preview: AudioEditPreview,
    *,
    branch: str | None = None,
) -> dict[str, Any]:
    """Explicitly accept one READY audio preview through the trusted R1 boundary."""

    if not preview.ready or preview.blueprint is None:
        raise ContractError("only READY_FOR_PREVIEW audio candidates may be accepted")

    selected_branch = branch or project.current_branch()
    if project.head_revision_id(selected_branch) != preview.source_revision_id:
        raise ContractError("audio Preview source is stale: project HEAD changed")

    current = project.read_revision(preview.source_revision_id)
    if blueprint_sha256(current) != preview.source_blueprint_sha256:
        raise ContractError("audio Preview source Blueprint hash is stale")
    if audio_material_sha256(current) != preview.source_audio_material_sha256:
        raise ContractError("audio Preview source material hash is stale")

    if blueprint_sha256(preview.blueprint) != preview.candidate_blueprint_sha256:
        raise ContractError("audio Preview candidate Blueprint hash changed")
    if audio_material_sha256(preview.blueprint) != preview.candidate_audio_material_sha256:
        raise ContractError("audio Preview candidate material hash changed")

    validate_contract(
        preview.blueprint,
        "music-blueprint-v0.schema.json",
        allow_nonempty_routing=True,
    )
    validate_project_blueprint_audio(project, preview.blueprint)
    if preview.blueprint["project"].get("parent_revision_id") != preview.source_revision_id:
        raise ContractError("audio Preview candidate parent_revision_id is stale")

    provenance = preview.blueprint["provenance"]
    return project._commit_revision(
        preview.blueprint,
        branch=selected_branch,
        actor=str(provenance["actor"]),
        reason=str(provenance["change_reason"]),
        allow_audio_material_change=True,
    )
