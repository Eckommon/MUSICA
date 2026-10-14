"""PLUG-R2B K2: truthful Studio inspection and explicit accepted offline WAV.

Never substitutes a simulated bus-host WAV for existing Studio generic/realtime
media without a separate UI/user choice. A pending Preview does NOT change
this accepted-source-only surface.
"""
from __future__ import annotations

import copy
from typing import Any

from .bus_host_material import accepted_bus_host_sha256, bus_host_material_from_blueprint
from .bus_host_runtime import render_accepted_simulated_bus_host
from .contracts import ContractError
from .studio import StudioService, StudioServiceError
from .studio_audio import _mix_rate
from .audio_edit import blueprint_sha256
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256


class StudioBusHostSurface:
    """Read-only accepted processor inspection + opt-in offline render endpoint."""

    def __init__(self, service: StudioService) -> None:
        self.service = service

    def _current(self, session_id: str) -> tuple[Any, str, dict[str, Any]]:
        session = self.service._get_session(session_id)
        branch = session.project.current_branch()
        revision_id = session.project.head_revision_id(branch)
        blueprint = session.project.read_revision(revision_id)
        return session, revision_id, blueprint

    def bus_plugins_view(self, session_id: str) -> dict[str, Any]:
        session, revision_id, blueprint = self._current(session_id)
        try:
            material = bus_host_material_from_blueprint(blueprint)
            routing = routing_material_from_blueprint(blueprint)
            if routing is None:
                raise ContractError("accepted routing material is unavailable")
            preview_pending = session.pending is not None
            result: dict[str, Any] = {
                "view_version": "0",
                "project_id": str(blueprint["project"]["project_id"]),
                "revision_id": str(revision_id),
                "branch": session.project.current_branch(),
                "blueprint_sha256": blueprint_sha256(blueprint),
                "routing_material_sha256": routing_material_sha256(routing),
                "accepted_bus_host_material_sha256": accepted_bus_host_sha256(blueprint),
                "instances": copy.deepcopy(material["instances"]),
                "accepted_state_is_canonical": True,
                "pending_preview_is_not_included": True,
                "pending_unrelated_preview": preview_pending,
                "offline_audition": {
                    "available": False,
                    "wav_sha256": None,
                    "sample_rate_hz": None,
                    "duration_frames": None,
                    "processing_plan_sha256": None,
                    "mode": None,
                    "unavailable_reason": None,
                },
                "capabilities": {
                    "accepted_simulated_bus_host": True,
                    "explicit_preview_accept_required": True,
                    "preview_mutation_supported_here": False,
                    "render_is_derived": True,
                    "offline_only": True,
                    "default_studio_media_overridden": False,
                    "realtime_pdc": False,
                    "native_vst3_clap_au_host": False,
                },
            }
            try:
                rate = _mix_rate(session.project, blueprint)
                rendered = render_accepted_simulated_bus_host(
                    session.project, revision_id, sample_rate_hz=rate
                )
                result["offline_audition"] = {
                    "available": True,
                    "wav_sha256": rendered.wav_sha256,
                    "sample_rate_hz": rate,
                    "duration_frames": None if rendered.kernel_plan is None
                    else int(rendered.kernel_plan["duration_frames"]),
                    "processing_plan_sha256": rendered.plan["bus_host_processing_plan_sha256"],
                    "mode": rendered.plan["mode"],
                    "unavailable_reason": None,
                }
            except (ContractError, OSError, ValueError) as error:
                # A not-yet-routable Studio project still has inspectable
                # accepted identity; never falsely claim playable PDC.
                result["offline_audition"]["unavailable_reason"] = str(error)
            return result
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def accepted_offline_wav(self, session_id: str) -> bytes:
        session, revision_id, blueprint = self._current(session_id)
        try:
            rate = _mix_rate(session.project, blueprint)
            wav = render_accepted_simulated_bus_host(
                session.project, revision_id, sample_rate_hz=rate
            )
            if session.project.head_revision_id(session.project.current_branch()) != revision_id:
                raise StudioServiceError(
                    "conflict", "accepted offline audition source changed during render"
                )
            return wav.wav_bytes
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc
