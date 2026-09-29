"""MRAM-R3 truthful Studio/Browser routing and native-automation surface.

This layer projects exact accepted routing plus MRAM-R2 native automation identities,
creates only typed routing candidates, and delegates Preview/Accept authority to the
already validated MRAM-R1/R2 engines. Browser/session state is derived and non-canonical.
"""

from __future__ import annotations

import copy
import shutil
from typing import Any

from .automation_contracts import native_mixer_automation_lanes
from .automation_edit import automation_material_sha256
from .audio_edit import audio_material_sha256, blueprint_sha256
from .contracts import ContractError
from .contracts import validate_contract
from .diff import structured_diff
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256
from .routing_edit import build_routing_edit_preview
from .studio import StudioService, StudioServiceError, _PendingPreview
from .studio_audio import StudioAudioSurface


def _routing(blueprint: dict[str, Any]) -> dict[str, Any]:
    material = routing_material_from_blueprint(blueprint)
    if material is None:
        raise ContractError("routing material is unavailable")
    return material


class StudioRoutingSurface:
    """Read accepted routing and install trusted non-canonical routing Previews."""

    def __init__(self, service: StudioService) -> None:
        self.service = service
        self.audio_surface = StudioAudioSurface(service)

    def _audition(
        self,
        session_id: str,
        project: Any,
        blueprint: dict[str, Any],
        *,
        source_kind: str,
    ) -> dict[str, Any]:
        material = _routing(blueprint)
        if not material["nodes"]:
            return {
                "available": False,
                "source_kind": source_kind,
                "mix_sample_rate_hz": None,
                "routed_mix_plan_sha256": None,
                "wav_sha256": None,
                "wav_size_bytes": None,
                "rendered_audio_is_canonical": False,
                "error": "accepted non-empty routing is required",
            }
        try:
            rendered = self.audio_surface._render_blueprint(
                session_id,
                project,
                blueprint,
                source_kind=source_kind,
            )
            return {
                "available": True,
                "source_kind": source_kind,
                "mix_sample_rate_hz": int(rendered.plan["mix_sample_rate_hz"]),
                "routed_mix_plan_sha256": str(rendered.plan["routed_mix_plan_sha256"]),
                "wav_sha256": str(rendered.wav_sha256),
                "wav_size_bytes": len(rendered.wav_bytes),
                "rendered_audio_is_canonical": False,
                "error": None,
            }
        except Exception as exc:
            return {
                "available": False,
                "source_kind": source_kind,
                "mix_sample_rate_hz": None,
                "routed_mix_plan_sha256": None,
                "wav_sha256": None,
                "wav_size_bytes": None,
                "rendered_audio_is_canonical": False,
                "error": str(exc),
            }

    def routing_view(self, session_id: str) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        try:
            branch = session.project.current_branch()
            revision_id = session.project.head_revision_id(branch)
            accepted = session.project.read_revision(revision_id)
            routing = copy.deepcopy(_routing(accepted))

            preview_value: dict[str, Any] | None = None
            pending = session.pending
            if pending is not None and pending.descriptor.get("kind") == "routing_edit":
                detail = pending.detail.get("routing_edit")
                if not isinstance(detail, dict):
                    raise StudioServiceError(
                        "integrity_error",
                        "pending routing Preview is missing trusted authority detail",
                    )
                candidate_routing = copy.deepcopy(_routing(pending.candidate))
                candidate_blueprint_hash = detail.get("candidate_blueprint_sha256")
                candidate_routing_hash = detail.get("candidate_routing_material_sha256")
                if not isinstance(candidate_blueprint_hash, str) or not isinstance(
                    candidate_routing_hash, str
                ):
                    raise StudioServiceError(
                        "integrity_error",
                        "pending routing Preview is missing exact candidate hashes",
                    )
                preview_value = {
                    "preview_id": str(pending.descriptor["preview_id"]),
                    "candidate_revision_id": str(
                        pending.descriptor["candidate_revision_id"]
                    ),
                    "candidate_blueprint_sha256": candidate_blueprint_hash,
                    "candidate_routing_material_sha256": candidate_routing_hash,
                    "track_outputs": candidate_routing["track_outputs"],
                    "nodes": candidate_routing["nodes"],
                    "sends": candidate_routing["sends"],
                    "changed_track_ids": list(detail.get("changed_track_ids", [])),
                    "changed_node_ids": list(detail.get("changed_node_ids", [])),
                    "changed_send_ids": list(detail.get("changed_send_ids", [])),
                    "audition": copy.deepcopy(pending.detail.get("routed_audition", {})),
                }

            value = {
                "view_version": "0",
                "project_id": str(accepted["project"]["project_id"]),
                "revision_id": str(revision_id),
                "branch": str(branch),
                "blueprint_sha256": blueprint_sha256(accepted),
                "audio_material_sha256": audio_material_sha256(accepted),
                "routing_material_sha256": routing_material_sha256(routing),
                "automation_material_sha256": automation_material_sha256(accepted),
                "accepted_state_is_canonical": True,
                "browser_state_is_canonical": False,
                "track_outputs": routing["track_outputs"],
                "nodes": routing["nodes"],
                "sends": routing["sends"],
                "native_automation_lanes": native_mixer_automation_lanes(accepted),
                "accepted_audition": self._audition(
                    session_id,
                    session.project,
                    accepted,
                    source_kind="accepted-routing",
                ),
                "preview": preview_value,
                "capabilities": {
                    "source_bound_candidates": True,
                    "preview_only": True,
                    "explicit_accept_required": True,
                    "project_mutation_authorized": False,
                    "browser_state_is_canonical": False,
                    "routed_audition": True,
                    "operations": [
                        "SET_TRACK_OUTPUT",
                        "SET_SEND_GAIN",
                        "SET_NODE_MIXER",
                    ],
                },
            }
            validate_contract(value, "studio-routing-view-v0.schema.json")
            return value
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def preview_routing_edit(
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
                    "accept or discard the pending Studio preview before routing editing",
                )
            branch = session.project.current_branch()
            parent_revision_id = session.project.head_revision_id(branch)
            parent = session.project.read_revision(parent_revision_id)
            revision_id = self.service._revision_id(
                parent_revision_id, "routing_edit", candidate
            )
            resolved = build_routing_edit_preview(
                session.project,
                parent,
                candidate,
                branch=branch,
                revision_id=revision_id,
            )
            authority = resolved.as_dict()
            if not resolved.ready or resolved.blueprint is None:
                return {
                    "preview_installed": False,
                    "authority_result": copy.deepcopy(resolved.authority_result),
                    "routing_edit": authority,
                    "session": self.service.inspect_session(session_id),
                    "routing_view": self.routing_view(session_id),
                }

            rendered = self.audio_surface._render_blueprint(
                session_id,
                session.project,
                resolved.blueprint,
                source_kind="preview-routing",
            )
            if session.project.head_revision_id(branch) != parent_revision_id:
                raise StudioServiceError(
                    "conflict",
                    "routing Preview source changed during routed audition",
                )

            preview_id = self.service._preview_id(
                parent_revision_id,
                str(resolved.blueprint["project"]["revision_id"]),
            )
            cache_root = self.service._confined(
                self.service._session_cache(session_id) / "mram-r3" / preview_id
            )
            if cache_root.exists():
                shutil.rmtree(cache_root)
            cache_root.mkdir(parents=True, exist_ok=True)
            wav_path = cache_root / "preview.wav"
            wav_path.write_bytes(rendered.wav_bytes)
            midi_path = cache_root / "preview.mid"

            generic_diff = structured_diff(parent, resolved.blueprint)
            descriptor = {
                "preview_version": "0",
                "preview_id": preview_id,
                "kind": "routing_edit",
                "parent_revision_id": parent_revision_id,
                "candidate_revision_id": str(
                    resolved.blueprint["project"]["revision_id"]
                ),
                "branch": branch,
                "diff_count": len(generic_diff),
                "audio_available": True,
                "midi_available": False,
            }
            validate_contract(descriptor, "studio-preview-v0.schema.json")
            audition = {
                "available": True,
                "source_kind": "preview-routing",
                "mix_sample_rate_hz": int(rendered.plan["mix_sample_rate_hz"]),
                "routed_mix_plan_sha256": str(
                    rendered.plan["routed_mix_plan_sha256"]
                ),
                "wav_sha256": str(rendered.wav_sha256),
                "wav_size_bytes": len(rendered.wav_bytes),
                "rendered_audio_is_canonical": False,
                "error": None,
            }
            self.service._clear_pending(session)
            session.pending = _PendingPreview(
                descriptor=descriptor,
                candidate=copy.deepcopy(resolved.blueprint),
                diff=generic_diff,
                midi_path=midi_path,
                wav_path=wav_path,
                actor=str(resolved.blueprint["provenance"]["actor"]),
                reason=str(candidate["reason"]),
                detail={
                    "routing_edit": authority,
                    "source_candidate": copy.deepcopy(candidate),
                    "candidate_id": str(candidate["candidate_id"]),
                    "operations": copy.deepcopy(candidate["operations"]),
                    "routed_audition": copy.deepcopy(audition),
                    "browser_state_is_canonical": False,
                    "project_mutation_authorized": False,
                },
            )
            return {
                "preview_installed": True,
                "preview": copy.deepcopy(descriptor),
                "diff": copy.deepcopy(generic_diff),
                "detail": copy.deepcopy(session.pending.detail),
                "authority_result": copy.deepcopy(resolved.authority_result),
                "routing_edit": authority,
                "session": self.service.inspect_session(session_id),
                "routing_view": self.routing_view(session_id),
            }
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def discard_routing_preview(self, session_id: str) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        if session.pending is None or session.pending.descriptor.get("kind") != "routing_edit":
            raise StudioServiceError(
                "not_found", "no pending routing Studio Preview to discard"
            )
        result = self.service.discard_preview(session_id)
        self.audio_surface._render_cache.clear()
        result["routing_view"] = self.routing_view(session_id)
        return result

    def audition_bytes(self, session_id: str, *, source_kind: str) -> bytes:
        session = self.service._get_session(session_id)
        try:
            if source_kind == "accepted":
                revision_id = session.project.head_revision_id()
                blueprint = session.project.read_revision(revision_id)
            elif source_kind == "preview":
                pending = session.pending
                if pending is None or pending.descriptor.get("kind") not in {
                    "routing_edit",
                    "automation_edit",
                }:
                    raise StudioServiceError(
                        "not_found",
                        "no pending routed/automation Preview audition",
                    )
                blueprint = pending.candidate
            else:
                raise StudioServiceError(
                    "invalid_request",
                    f"unsupported routed audition source: {source_kind}",
                )
            if not _routing(blueprint)["nodes"]:
                raise StudioServiceError(
                    "invalid_request",
                    "routed audition requires accepted non-empty routing",
                )
            rendered = self.audio_surface._render_blueprint(
                session_id,
                session.project,
                blueprint,
                source_kind=f"mram-r3-{source_kind}",
            )
            return rendered.wav_bytes
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc
