"""MUSICA M6-R2 Browser Studio exact-note integration surface.

This module deliberately adapts the validated M6-R1 authority engine to the existing
Studio session/Preview boundary. Browser state is never project authority: accepted
notes are read from the current M2 revision, and a note edit can only become a pending
Studio Preview after the trusted M6-R1 source/lock/constraint checks succeed.
"""

from __future__ import annotations

import copy
from typing import Any

from .compiler import PPQ
from .contracts import exact_note_locks, exact_timeline, validate_contract
from .diff import structured_diff
from .note_edit import blueprint_sha256, build_note_edit_preview
from .studio import StudioService, StudioServiceError

NOTE_OPERATIONS = [
    "INSERT",
    "DELETE",
    "MOVE",
    "RESIZE",
    "REPITCH",
    "SET_VELOCITY",
]


def _editable_part(blueprint: dict[str, Any]) -> dict[str, Any] | None:
    for part in blueprint["roles"]["instruments_or_parts"]:
        if part["role"] in {"motif", "lead"}:
            return {
                "part_id": str(part["part_id"]),
                "role": str(part["role"]),
                "instrument_family": str(part["instrument_family"]),
            }
    return None


def _section_view(blueprint: dict[str, Any], bpm: float) -> list[dict[str, Any]]:
    return [
        {
            "section_id": str(section["section_id"]),
            "name": str(section.get("label") or section["section_id"]),
            "start_beat": float(section["start"]) * bpm / 60.0,
            "end_beat": float(section["end"]) * bpm / 60.0,
        }
        for section in blueprint["form"]["sections"]
    ]


def _capabilities() -> dict[str, Any]:
    return {
        "source_bound_candidates": True,
        "preview_only": True,
        "explicit_accept_required": True,
        "project_mutation_authorized": False,
        "music_ir_mutation_authorized": False,
        "operations": list(NOTE_OPERATIONS),
    }


class StudioNoteSurface:
    """Read/project exact notes and install only validated M6-R1 note Previews."""

    def __init__(self, service: StudioService) -> None:
        self.service = service

    def note_view(self, session_id: str) -> dict[str, Any]:
        """Return a deterministic read-only projection of accepted exact-note state."""

        session = self.service._get_session(session_id)
        try:
            branch = session.project.current_branch()
            revision_id = session.project.head_revision_id(branch)
            accepted = session.project.read_revision(revision_id)
            tempo = accepted["musical_context"]["tempo"]
            bpm = float(tempo["bpm"])
            total_beats = float(accepted["project"]["duration_seconds"]) * bpm / 60.0
            timeline = exact_timeline(accepted)
            available = timeline is not None
            part = _editable_part(accepted) if available else None
            notes = copy.deepcopy(timeline["notes"]) if timeline is not None else []
            locks = copy.deepcopy(exact_note_locks(accepted)) if timeline is not None else []

            preview_value: dict[str, Any] | None = None
            pending = session.pending
            if pending is not None and pending.descriptor.get("kind") == "note_edit":
                candidate_timeline = exact_timeline(pending.candidate)
                note_detail = pending.detail.get("note_edit", {})
                candidate_hash = note_detail.get("candidate_blueprint_sha256")
                if candidate_timeline is None or not isinstance(candidate_hash, str):
                    raise StudioServiceError(
                        "integrity_error",
                        "pending note Preview is missing exact-note authority detail",
                    )
                preview_value = {
                    "preview_id": str(pending.descriptor["preview_id"]),
                    "candidate_revision_id": str(pending.descriptor["candidate_revision_id"]),
                    "candidate_blueprint_sha256": candidate_hash,
                    "notes": copy.deepcopy(candidate_timeline["notes"]),
                    "stable_note_diff": copy.deepcopy(note_detail.get("stable_note_diff", [])),
                    "changed_note_ids": list(note_detail.get("changed_note_ids", [])),
                }

            value = {
                "view_version": "0",
                "exact_note_editing_available": available,
                "project_id": str(accepted["project"]["project_id"]),
                "revision_id": str(revision_id),
                "blueprint_sha256": blueprint_sha256(accepted),
                "branch": str(branch),
                "timing": {
                    "bpm": bpm,
                    "ppq": PPQ,
                    "total_beats": total_beats,
                },
                "editable_part": part,
                "sections": _section_view(accepted, bpm),
                "notes": notes,
                "note_locks": locks,
                "preview": preview_value,
                "capabilities": _capabilities(),
            }
            validate_contract(value, "studio-note-view-v0.schema.json")
            return value
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def preview_note_edit(
        self,
        session_id: str,
        *,
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        """Resolve a typed browser candidate through M6-R1 and optionally install Preview."""

        session = self.service._get_session(session_id)
        try:
            parent_revision_id = session.project.head_revision_id()
            parent = session.project.read_revision(parent_revision_id)
            revision_id = self.service._revision_id(parent_revision_id, "note_edit", candidate)
            resolved = build_note_edit_preview(parent, candidate, revision_id=revision_id)
            note_detail = resolved.as_dict()

            if not resolved.ready or resolved.blueprint is None:
                # Fail closed: a blocked candidate must not displace or install a pending Preview.
                return {
                    "preview_installed": False,
                    "authority_result": copy.deepcopy(resolved.authority_result),
                    "note_edit": note_detail,
                    "session": self.service.inspect_session(session_id),
                    "note_view": self.note_view(session_id),
                }

            generic_diff = structured_diff(parent, resolved.blueprint)
            installed = self.service._install_preview(
                session,
                kind="note_edit",
                candidate=resolved.blueprint,
                diff=generic_diff,
                actor=str(candidate["actor"]["kind"]),
                reason=str(candidate["reason"]),
                detail={
                    "note_edit": note_detail,
                    "candidate_id": str(candidate["candidate_id"]),
                    "operations": copy.deepcopy(candidate["operations"]),
                },
            )
            installed["preview_installed"] = True
            installed["authority_result"] = copy.deepcopy(resolved.authority_result)
            installed["note_edit"] = note_detail
            installed["note_view"] = self.note_view(session_id)
            return installed
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc
