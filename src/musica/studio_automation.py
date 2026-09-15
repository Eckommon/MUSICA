"""MUSICA Browser Studio automation integration surface.

R2 established Browser automation inspect/edit authority. M7-R5 extends only the
installed automation Preview audio path: after the existing trusted Preview is created,
its pending WAV is replaced through the already validated R3 lowering and R4 bounded
reference-renderer ``mix.gain`` path. Browser/renderer state remains non-canonical and
explicit M2 Accept remains the only authority that advances project state.
"""

from __future__ import annotations

import copy
import hashlib
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
from .automation_lowering import lower_automation_execution
from .automation_renderer import (
    automation_render_plan_sha256,
    build_automation_render_plan,
    render_automation_wav,
)
from .compiler import compile_blueprint
from .contracts import validate_contract
from .diff import structured_diff
from .render import DEFAULT_SAMPLE_RATE
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
        # Preserve the ratified R2 view contract. R5 evidence is exposed separately
        # as studio_audition on an installed automation Preview.
        "audible_automation_validated": False,
        "operations": list(AUTOMATION_OPERATIONS),
    }


class StudioAutomationSurface:
    """Project accepted automation and install only trusted automation Previews."""

    def __init__(self, service: StudioService) -> None:
        self.service = service

    def _install_audible_preview(
        self,
        session: Any,
        candidate_blueprint: dict[str, Any],
    ) -> dict[str, Any]:
        """Replace only the pending automation Preview WAV through the R3→R4 path.

        The existing Studio Preview installation is deliberately retained for MIDI,
        cache ownership and authority semantics. Any failure clears the non-canonical
        pending Preview and leaves the accepted project ref unchanged.
        """

        pending = session.pending
        if pending is None or pending.descriptor.get("kind") != "automation_edit":
            raise StudioServiceError(
                "integrity_error",
                "audible automation installation requires one pending automation Preview",
            )

        accepted_head_before = session.project.head_revision_id()
        baseline_wav = pending.wav_path.read_bytes()
        preview_midi = pending.midi_path.read_bytes()
        baseline_wav_sha256 = hashlib.sha256(baseline_wav).hexdigest()
        preview_midi_sha256 = hashlib.sha256(preview_midi).hexdigest()

        try:
            music_ir = compile_blueprint(candidate_blueprint)
            execution = lower_automation_execution(candidate_blueprint)
            plan = build_automation_render_plan(music_ir, execution)
            render_automation_wav(
                music_ir,
                execution,
                pending.wav_path,
                duration_seconds=float(candidate_blueprint["project"]["duration_seconds"]),
                sample_rate=DEFAULT_SAMPLE_RATE,
            )
            accepted_head_after = session.project.head_revision_id()
            if accepted_head_after != accepted_head_before:
                raise StudioServiceError(
                    "integrity_error",
                    "audible automation Preview rendering changed the canonical project ref",
                )

            preview_wav_sha256 = hashlib.sha256(pending.wav_path.read_bytes()).hexdigest()
            proof = {
                "audition_version": "0",
                "candidate_revision_id": str(candidate_blueprint["project"]["revision_id"]),
                "path": "m7-r3-to-m7-r4-reference-renderer",
                "automation_applied": bool(plan["mapped_lanes"]),
                "output_differs_from_baseline": preview_wav_sha256 != baseline_wav_sha256,
                "mapped_lane_ids": [str(lane["lane_id"]) for lane in plan["mapped_lanes"]],
                "unmapped_lane_ids": [str(lane["lane_id"]) for lane in plan["unmapped_lanes"]],
                "render_plan_sha256": automation_render_plan_sha256(plan),
                "baseline_wav_sha256": baseline_wav_sha256,
                "preview_wav_sha256": preview_wav_sha256,
                "preview_midi_sha256": preview_midi_sha256,
                "project_ref_unchanged": True,
                "canonical": False,
                "reverse_promotion_authorized": False,
            }
            pending.detail["studio_audition"] = copy.deepcopy(proof)
            return proof
        except Exception:
            self.service._clear_pending(session)
            raise

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
            audition = self._install_audible_preview(session, resolved.blueprint)
            installed["detail"]["studio_audition"] = copy.deepcopy(audition)
            installed["studio_audition"] = copy.deepcopy(audition)
            installed["preview_installed"] = True
            installed["authority_result"] = copy.deepcopy(resolved.authority_result)
            installed["automation_edit"] = automation_detail
            installed["automation_view"] = self.automation_view(session_id)
            return installed
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc
