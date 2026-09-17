"""ATCM-R2 mixer-field extension of the existing native-audio Preview/Accept authority.

This module creates the same ``AudioEditPreview`` consumed by
``accept_audio_edit_preview``. It therefore extends candidate generation without
creating a second acceptance system.
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any

from .audio_contracts import (
    audio_material_from_blueprint,
    validate_audio_material,
    validate_project_audio_material,
    validate_project_blueprint_audio,
)
from .audio_edit import AudioEditPreview, audio_material_sha256, blueprint_sha256
from .contracts import ContractError, validate_contract, validate_revision
from .evidence import canonical_json_bytes


def _result(candidate_id: str, conflicts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    blocked = bool(conflicts)
    value = {
        "result_version": "0",
        "candidate_id": candidate_id,
        "status": "BLOCKED" if blocked else "READY_FOR_PREVIEW",
        "conflicts": conflicts or [],
        "preview_generation_allowed": not blocked,
        "explicit_accept_required": True,
        "project_mutation_authorized": False,
        "render_mutation_authorized": False,
    }
    validate_contract(value, "audio-authority-result-v0.schema.json")
    return value


def _conflict(ordinal: int, code: str, reason: str, *, track_id: str | None = None, rule_id: str | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"conflict_id": f"ATCM-R2-C-{ordinal:03d}", "code": code, "reason": reason}
    if track_id is not None:
        value["track_id"] = track_id
    if rule_id is not None:
        value["rule_id"] = rule_id
    return value


def _blocked(parent: dict[str, Any], candidate: dict[str, Any], conflicts: list[dict[str, Any]]) -> AudioEditPreview:
    return AudioEditPreview(
        authority_result=_result(str(candidate["candidate_id"]), conflicts),
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


def _revision_id(parent: dict[str, Any], candidate: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json_bytes(candidate)).hexdigest()[:16]
    return f"{parent['project']['revision_id']}-mixer-{digest}"


def build_audio_mixer_edit_preview(project: Any, parent_blueprint: dict[str, Any], candidate: dict[str, Any], *, branch: str | None = None, revision_id: str | None = None) -> AudioEditPreview:
    """Build a non-canonical track-mixer Preview using the existing R1 accept type."""
    validate_contract(parent_blueprint, "music-blueprint-v0.schema.json")
    validate_contract(candidate, "audio-mixer-edit-candidate-v0.schema.json")
    validate_project_blueprint_audio(project, parent_blueprint)

    selected_branch = branch or project.current_branch()
    source = candidate["source"]
    parent_revision_id = str(parent_blueprint["project"]["revision_id"])
    stale: list[str] = []
    if source["project_id"] != parent_blueprint["project"]["project_id"]:
        stale.append("project_id mismatch")
    if source["revision_id"] != parent_revision_id:
        stale.append("revision_id mismatch")
    if source["blueprint_sha256"] != blueprint_sha256(parent_blueprint):
        stale.append("blueprint_sha256 mismatch")
    if source["audio_material_sha256"] != audio_material_sha256(parent_blueprint):
        stale.append("audio_material_sha256 mismatch")
    if project.head_revision_id(selected_branch) != parent_revision_id:
        stale.append("project branch HEAD no longer equals source revision")
    if stale:
        return _blocked(parent_blueprint, candidate, [_conflict(1, "STALE_SOURCE", "; ".join(stale))])

    operation_ids = [str(item["operation_id"]) for item in candidate["operations"]]
    if len(operation_ids) != len(set(operation_ids)):
        return _blocked(parent_blueprint, candidate, [_conflict(1, "UNREPRESENTABLE_EDIT", "operation_id must be unique")])

    parent_material = audio_material_from_blueprint(parent_blueprint)
    assert parent_material is not None
    working_material = copy.deepcopy(parent_material)
    changes: list[dict[str, Any]] = []
    for ordinal, operation in enumerate(candidate["operations"], start=1):
        track_id = str(operation["target"]["track_id"])
        track = next((item for item in working_material["tracks"] if str(item["track_id"]) == track_id), None)
        if track is None:
            return _blocked(parent_blueprint, candidate, [_conflict(ordinal, "UNKNOWN_TRACK", f"unknown audio track: {track_id}", track_id=track_id)])
        before = copy.deepcopy(track["mixer"])
        after = copy.deepcopy(operation["mixer"])
        track["mixer"] = after
        changes.append({"track_id": track_id, "op": "update_mixer", "before": before, "after": copy.deepcopy(after)})

    try:
        validate_audio_material(working_material, project_duration_seconds=float(parent_blueprint["project"]["duration_seconds"]))
        validate_project_audio_material(project, working_material, project_duration_seconds=float(parent_blueprint["project"]["duration_seconds"]))
    except ContractError as exc:
        return _blocked(parent_blueprint, candidate, [_conflict(1, "INVALID_VALUE", str(exc))])

    working = copy.deepcopy(parent_blueprint)
    working["materials"]["audio"] = working_material
    working["project"]["parent_revision_id"] = parent_revision_id
    working["project"]["revision_id"] = revision_id or _revision_id(parent_blueprint, candidate)
    provenance = working["provenance"]
    kind = str(candidate["actor"]["kind"])
    provenance["actor"] = "deterministic_transform" if kind == "system" else kind
    provenance["change_reason"] = candidate["reason"]
    provenance["source_revision"] = parent_revision_id
    selected = list(provenance.get("selected_mechanisms", []))
    selected.append(f"audio_edit_candidate:{candidate['candidate_id']}")
    selected.extend(f"audio_edit_operation:{value}" for value in operation_ids)
    selected.append("audio_mixer_semantics:atcm-r2-v0")
    provenance["selected_mechanisms"] = selected

    try:
        validate_contract(working, "music-blueprint-v0.schema.json")
        validate_project_blueprint_audio(project, working)
    except ContractError as exc:
        return _blocked(parent_blueprint, candidate, [_conflict(1, "UNREPRESENTABLE_EDIT", str(exc))])

    revision_conflicts = validate_revision(parent_blueprint, working)
    blocking = [item for item in revision_conflicts if item.status == "BLOCKED"]
    if blocking:
        mapped: list[dict[str, Any]] = []
        for ordinal, item in enumerate(blocking, start=1):
            code = "HARD_LOCK_VIOLATION" if item.rule_type in {"lock", "note_lock", "automation_lock"} else "CONSTRAINT_VIOLATION" if item.rule_type == "constraint" else "UNREPRESENTABLE_EDIT"
            mapped.append(_conflict(ordinal, code, item.reason, rule_id=item.rule_id))
        return _blocked(parent_blueprint, candidate, mapped)

    return AudioEditPreview(
        authority_result=_result(str(candidate["candidate_id"])),
        blueprint=working,
        material_diff=changes,
        source_revision_id=parent_revision_id,
        source_blueprint_sha256=blueprint_sha256(parent_blueprint),
        source_audio_material_sha256=audio_material_sha256(parent_blueprint),
        candidate_blueprint_sha256=blueprint_sha256(working),
        candidate_audio_material_sha256=audio_material_sha256(working),
        changed_track_ids=sorted({str(item["track_id"]) for item in changes}),
        changed_clip_ids=[],
        revision_conflicts=[item.as_dict() for item in revision_conflicts],
    )
