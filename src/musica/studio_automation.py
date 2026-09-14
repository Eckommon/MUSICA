"""MUSICA M7-R2 Browser Studio automation integration surface.

This adapter projects accepted M7-R1 automation into Browser Studio and routes Browser
proposals through the existing trusted M7-R1 authority. Browser/DOM state never becomes
project authority.
"""

from __future__ import annotations

import copy
from typing import Any

from .automation_contracts import (
    automation_locks_from_blueprint,
    automation_material_from_blueprint,
)
from .automation_edit import (
    automation_material_sha256,
    blueprint_sha256,
    build_automation_edit_preview,
)
from .contracts import validate_contract
from .diff import structured_diff
from .studio import StudioService, StudioServiceError

AUTOMATION_OPERATIONS = [
    "INSERT_POINT",
    "DELETE_POINT",
    "MOVE_POINT",
    "SET_VALUE",
    "SET_INTERPOLATION",
]


def _capabilities() -> dict[str, Any]:
    return {
        "source_bound_candidates": True,
        "preview_only": True,
        "explicit_accept_required": True,
        "project_mutation_authorized": False,
        "music_ir_mutation_authorized": False,
        "audible_automation_validated": False,
        "operations": list(AUTOMATION_OPERATIONS),
    }


class StudioAutomationSurface:
    """Project accepted automation and install only validated M7-R1 Previews."""

    def __init__(self, service: StudioService) -> None:
        self.service = service

    def automation_view(self, session_id: str) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        try:
            branch = session.project.current_branch()
            revision_id = session.project.head_revision_id(branch)
            accepted = session.project.read_revision(revision_id)
            explicit = automation_material_from_blueprint(accepted, materialize_empty=False)
            available = explicit is not None
            material = automation_material_from_blueprint(accepted)
            assert material is not None
            tempo = accepted["musical_context"]["tempo"]
            bpm = float(tempo["bpm"])
            total_beats = float(accepted["project"]["duration_seconds"]) * bpm / 60.0

            preview_value: dict[str, Any] | None = None
            pending = session.pending
            if pending is not None and pending.descriptor.get("kind") == "automation_edit":
                candidate_material = automation_material_from_blueprint(
                    pending.candidate, materialize_empty=False
                )
                detail = pending.detail.get("automation_edit", {})
                candidate_blueprint_hash = detail.get("candidate_blueprint_sha256")
                candidate_material_hash = detail.get("candidate_automation_material_sha256")
                if (
                    candidate_material is None
                    or not isinstance(candidate_blueprint_hash, str)
                    or not isinstance(candidate_material_hash, str)
                ):
                    raise StudioServiceError(
                        "integrity_error",
                        "pending automation Preview is missing trusted authority detail",
                    )
                preview_value = {
                    "preview_id": str(pending.descriptor["preview_id"]),
                    "candidate_revision_id": str(pending.descriptor["candidate_revision_id"]),
                    "candidate_blueprint_sha256": candidate_blueprint_hash,
                    "candidate_automation_material_sha256": candidate_material_hash,
                    "lanes": copy.deepcopy(candidate_material["lanes"]),
                    "material_diff": copy.deepcopy(detail.get("material_diff", [])),
                    "changed_lane_ids": list(detail.get("changed_lane_ids", [])),
                    "changed_point_ids": list(detail.get("changed_point_ids", [])),
                }

            value = {
                "view_version": "0",
                "automation_editing_available": available,
                "project_id": str(accepted["project"]["project_id"]),
                "revision_id": str(revision_id),
                "blueprint_sha256": blueprint_sha256(accepted),
                "automation_material_sha256": automation_material_sha256(accepted),
                "branch": str(branch),
                "timing": {
                    "bpm": bpm,
                    "total_beats": total_beats,
                    "time_unit": "quarter_note_beat",
                },
                "lanes": copy.deepcopy(material["lanes"]) if available else [],
                "automation_locks": (
                    copy.deepcopy(automation_locks_from_blueprint(accepted)) if available else []
                ),
                "preview": preview_value,
                "capabilities": _capabilities(),
            }
            validate_contract(value, "studio-automation-view-v0.schema.json")
            return value
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def preview_automation_edit(
        self,
        session_id: str,
        *,
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        try:
            if session.pending is not None:
                raise StudioServiceError(
                    "conflict",
                    "accept or discard the pending Studio preview before automation editing",
                )
            parent_revision_id = session.project.head_revision_id()
            parent = session.project.read_revision(parent_revision_id)
            revision_id = self.service._revision_id(parent_revision_id, "automation_edit", candidate)
            resolved = build_automation_edit_preview(parent, candidate, revision_id=revision_id)
            automation_detail = resolved.as_dict()

            if not resolved.ready or resolved.blueprint is None:
                return {
                    "preview_installed": False,
                    "authority_result": copy.deepcopy(resolved.authority_result),
                    "automation_edit": automation_detail,
                    "session": self.service.inspect_session(session_id),
                    "automation_view": self.automation_view(session_id),
                }

            generic_diff = structured_diff(parent, resolved.blueprint)
            provenance_actor = str(resolved.blueprint["provenance"]["actor"])
            installed = self.service._install_preview(
                session,
                kind="automation_edit",
                candidate=resolved.blueprint,
                diff=generic_diff,
                actor=provenance_actor,
                reason=str(candidate["reason"]),
                detail={
                    "automation_edit": automation_detail,
                    "candidate_id": str(candidate["candidate_id"]),
                    "operations": copy.deepcopy(candidate["operations"]),
                    "audible_automation_validated": False,
                },
            )
            installed["preview_installed"] = True
            installed["authority_result"] = copy.deepcopy(resolved.authority_result)
            installed["automation_edit"] = automation_detail
            installed["automation_view"] = self.automation_view(session_id)
            return installed
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc
