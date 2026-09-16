"""Truthful, read-only M7-R6 Studio automation audition inspection.

This surface deliberately does not replace or reinterpret the historical
``studio-automation-view-v0`` contract. It projects only trusted R5 audition detail,
accepted Blueprint-derived R4 mapping eligibility, and exact accepted media identity.
Browser/audio state receives no canonical or reverse-promotion authority.
"""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

from .automation_contracts import automation_material_from_blueprint
from .automation_lowering import lower_automation_execution
from .automation_renderer import (
    AUTOMATION_RENDER_MAPPING_ID,
    AUTOMATION_RENDER_POLICY_ID,
    AUTOMATION_RENDER_POLICY_VERSION,
    automation_render_plan_sha256,
    build_automation_render_plan,
)
from .compiler import compile_blueprint
from .contracts import validate_contract
from .renderer import REFERENCE_RENDERER_ID
from .studio import StudioService, StudioServiceError


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _lane_ids(plan: dict[str, Any], key: str) -> list[str]:
    return [str(item["lane_id"]) for item in plan[key]]


class StudioAutomationAuditionSurface:
    """Read-only truthful inspection over already validated R4/R5 state."""

    def __init__(self, service: StudioService) -> None:
        self.service = service

    def _accepted_mapping(
        self,
        accepted: dict[str, Any],
    ) -> dict[str, Any]:
        explicit = automation_material_from_blueprint(accepted, materialize_empty=False)
        music_ir = compile_blueprint(accepted)
        execution = lower_automation_execution(accepted)
        plan = build_automation_render_plan(music_ir, execution)
        return {
            "automation_present": explicit is not None,
            "mapped_lane_ids": _lane_ids(plan, "mapped_lanes"),
            "unmapped_lane_ids": _lane_ids(plan, "unmapped_lanes"),
        }

    def _pending_audition(
        self,
        session: Any,
        accepted_revision_id: str,
    ) -> dict[str, Any] | None:
        pending = session.pending
        if pending is None or pending.descriptor.get("kind") != "automation_edit":
            return None
        if str(pending.descriptor.get("parent_revision_id")) != accepted_revision_id:
            raise StudioServiceError(
                "conflict",
                "pending automation audition is stale because the accepted revision changed",
            )

        proof = pending.detail.get("studio_audition")
        if not isinstance(proof, dict):
            raise StudioServiceError(
                "integrity_error",
                "pending automation Preview lacks trusted R5 studio_audition proof",
            )
        preview_id = str(pending.descriptor.get("preview_id", ""))
        candidate_revision_id = str(pending.descriptor.get("candidate_revision_id", ""))
        if str(proof.get("candidate_revision_id")) != candidate_revision_id:
            raise StudioServiceError(
                "integrity_error",
                "R5 audition proof candidate revision does not match pending Preview",
            )
        if not pending.wav_path.is_file() or not pending.midi_path.is_file():
            raise StudioServiceError(
                "integrity_error",
                "pending automation audition media is unavailable",
            )

        actual_wav_sha = _sha256_bytes(pending.wav_path.read_bytes())
        actual_midi_sha = _sha256_bytes(pending.midi_path.read_bytes())
        if actual_wav_sha != proof.get("preview_wav_sha256"):
            raise StudioServiceError(
                "integrity_error",
                "pending automation WAV does not match trusted R5 audition proof",
            )
        if actual_midi_sha != proof.get("preview_midi_sha256"):
            raise StudioServiceError(
                "integrity_error",
                "pending automation MIDI does not match trusted R5 audition proof",
            )

        music_ir = compile_blueprint(pending.candidate)
        execution = lower_automation_execution(pending.candidate)
        plan = build_automation_render_plan(music_ir, execution)
        mapped_lane_ids = _lane_ids(plan, "mapped_lanes")
        unmapped_lane_ids = _lane_ids(plan, "unmapped_lanes")
        plan_sha = automation_render_plan_sha256(plan)
        if plan_sha != proof.get("render_plan_sha256"):
            raise StudioServiceError(
                "integrity_error",
                "pending automation render plan does not match trusted R5 audition proof",
            )
        if mapped_lane_ids != list(proof.get("mapped_lane_ids", [])):
            raise StudioServiceError(
                "integrity_error",
                "pending mapped lanes do not match trusted R5 audition proof",
            )
        if unmapped_lane_ids != list(proof.get("unmapped_lane_ids", [])):
            raise StudioServiceError(
                "integrity_error",
                "pending unmapped lanes do not match trusted R5 audition proof",
            )
        if bool(proof.get("automation_applied")) != bool(mapped_lane_ids):
            raise StudioServiceError(
                "integrity_error",
                "pending automation_applied flag contradicts the R4 render plan",
            )
        if proof.get("project_ref_unchanged") is not True:
            raise StudioServiceError("integrity_error", "pending audition proof lost project-ref integrity")
        if proof.get("canonical") is not False or proof.get("reverse_promotion_authorized") is not False:
            raise StudioServiceError("integrity_error", "pending audition proof violates authority boundary")

        return {
            "preview_id": preview_id,
            "candidate_revision_id": candidate_revision_id,
            "automation_applied": bool(proof["automation_applied"]),
            "output_differs_from_baseline": bool(proof["output_differs_from_baseline"]),
            "mapped_lane_ids": mapped_lane_ids,
            "unmapped_lane_ids": unmapped_lane_ids,
            "render_plan_sha256": str(proof["render_plan_sha256"]),
            "baseline_wav_sha256": str(proof["baseline_wav_sha256"]),
            "preview_wav_sha256": actual_wav_sha,
            "preview_midi_sha256": actual_midi_sha,
            "project_ref_unchanged": True,
            "canonical": False,
            "reverse_promotion_authorized": False,
        }

    def _media_item(self, path: Path, source: str) -> dict[str, Any]:
        if not path.is_file():
            raise StudioServiceError("integrity_error", "accepted media path is unavailable")
        data = path.read_bytes()
        return {
            "available": True,
            "source": source,
            "sha256": _sha256_bytes(data),
            "size_bytes": len(data),
        }

    def _accepted_media(self, session: Any, revision_id: str) -> dict[str, Any]:
        bound_wav = self.service._artifact_media(session.project, revision_id, ".wav")
        bound_midi = self.service._artifact_media(session.project, revision_id, ".mid")
        fallback_wav: Path | None = None
        fallback_midi: Path | None = None

        if bound_wav is None or bound_midi is None:
            accepted = session.project.read_revision(revision_id)
            token = hashlib.sha256(revision_id.encode("utf-8")).hexdigest()[:16]
            fallback_midi, fallback_wav = self.service._render_to_cache(
                session,
                accepted,
                f"r6-inspect-{token}",
            )

        wav_path = bound_wav if bound_wav is not None else fallback_wav
        midi_path = bound_midi if bound_midi is not None else fallback_midi
        assert wav_path is not None and midi_path is not None
        return {
            "revision_id": revision_id,
            "wav": self._media_item(
                wav_path,
                "bound_artifact" if bound_wav is not None else "fallback_render",
            ),
            "midi": self._media_item(
                midi_path,
                "bound_artifact" if bound_midi is not None else "fallback_render",
            ),
        }

    def audition_view(self, session_id: str) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        try:
            branch = session.project.current_branch()
            revision_id = session.project.head_revision_id(branch)
            accepted = session.project.read_revision(revision_id)
            value = {
                "audition_view_version": "0",
                "project_id": str(accepted["project"]["project_id"]),
                "branch": str(branch),
                "accepted_revision_id": str(revision_id),
                "renderer_policy": {
                    "renderer_id": REFERENCE_RENDERER_ID,
                    "policy_id": AUTOMATION_RENDER_POLICY_ID,
                    "policy_version": AUTOMATION_RENDER_POLICY_VERSION,
                    "validated_mapping_families": [
                        {
                            "mapping_id": AUTOMATION_RENDER_MAPPING_ID,
                            "parameter_id": "mix.gain",
                            "scope": "project",
                            "owner_id": None,
                            "unit": "normalized",
                        }
                    ],
                },
                "accepted_mapping": self._accepted_mapping(accepted),
                "pending_audition": self._pending_audition(session, str(revision_id)),
                "accepted_media": self._accepted_media(session, str(revision_id)),
                "authority": {
                    "canonical": False,
                    "browser_mutation_authorized": False,
                    "project_mutation_authorized": False,
                    "reverse_promotion_authorized": False,
                    "explicit_accept_required": True,
                },
            }
            validate_contract(value, "studio-automation-audition-v0.schema.json")
            return copy.deepcopy(value)
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc
