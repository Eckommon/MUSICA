"""PLUG-R3 Studio trusted simulated bus insert Preview -> explicit Accept.

Only a persisted source-bound K1-B candidate may reach Studio's pending slot.
Derived preview WAV is transient; accepted bus-host audio remains available only
through the explicit K2 endpoint. The default legacy Studio media is not rebound.
"""
from __future__ import annotations

import copy
import hashlib
import shutil
from typing import Any

from .bus_host_edit import (
    build_bus_host_edit_preview,
    source_for_bus_host_candidate,
)
from .bus_host_material import bus_host_material_from_blueprint
from .bus_host_runtime import render_accepted_simulated_bus_host
from .contracts import ContractError, validate_contract
from .diff import structured_diff
from .plugin_host_topology import exact_two_bus_host_topology
from .studio import StudioService, StudioServiceError, _PendingPreview
from .studio_audio import _BlueprintProjectProxy, _mix_rate


class StudioBusHostEditSurface:
    """No direct state mutations: inspect eligible buses, Preview and audition."""

    def __init__(self, service: StudioService) -> None:
        self.service = service

    def editor_view(self, session_id: str) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        try:
            branch = session.project.current_branch()
            rid = session.project.head_revision_id(branch)
            accepted = session.project.read_revision(rid)
            eligible = True
            buses: list[dict[str, str]] = []
            why: str | None = None
            try:
                topology = exact_two_bus_host_topology(accepted)
                buses = copy.deepcopy(topology["paths"])
            except ContractError as exc:
                eligible = False
                why = str(exc)
            return {
                "view_version": "0",
                "revision_id": rid,
                "branch": branch,
                "source": source_for_bus_host_candidate(accepted),
                "accepted_material": copy.deepcopy(bus_host_material_from_blueprint(accepted)),
                "supported_buses": buses,
                "eligible_for_bounded_preview": eligible,
                "ineligible_reason": why,
                "preview_pending": session.pending is not None,
                "capabilities": {
                    "preview_then_explicit_accept": True,
                    "generic_project_commit_authorized": False,
                    "simulated_algorithmic_latency_only": True,
                    "realtime_pdc": False,
                    "native_binary_plugin_host": False,
                    "default_studio_media_overridden": False,
                },
            }
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def preview_edit(
        self, session_id: str, *, candidate: dict[str, Any]
    ) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        if session.pending is not None:
            raise StudioServiceError(
                "conflict", "accept or discard pending Studio Preview before bus processor editing"
            )
        try:
            branch = session.project.current_branch()
            rid = session.project.head_revision_id(branch)
            parent = session.project.read_revision(rid)
            resolved = build_bus_host_edit_preview(
                session.project, parent, candidate, branch=branch
            )
            if not resolved.ready or resolved.blueprint is None:
                return {
                    "preview_installed": False,
                    "status": resolved.status,
                    "reason": resolved.reason,
                    "source": resolved.source,
                    "session": self.service.inspect_session(session_id),
                }
            proposed = resolved.blueprint
            preview_rid = str(proposed["project"]["revision_id"])
            proxy = _BlueprintProjectProxy(session.project, proposed)
            rate = _mix_rate(session.project, proposed)
            rendered = render_accepted_simulated_bus_host(
                proxy, preview_rid, sample_rate_hz=rate
            )
            if session.project.head_revision_id(branch) != rid:
                raise StudioServiceError(
                    "conflict", "bus processor Preview source changed while auditioning"
                )
            preview_id = self.service._preview_id(rid, preview_rid)
            root = self.service._confined(
                self.service._session_cache(session_id) / "plug-r3" / preview_id
            )
            if root.exists():
                shutil.rmtree(root)
            root.mkdir(parents=True, exist_ok=True)
            wav_path = root / "preview.wav"
            wav_path.write_bytes(rendered.wav_bytes)
            midi_path = root / "preview.mid"  # intentional: no MIDI artifact
            diff = structured_diff(parent, proposed)
            descriptor = {
                "preview_version": "0",
                "preview_id": preview_id,
                "kind": "bus_host_edit",
                "parent_revision_id": rid,
                "candidate_revision_id": preview_rid,
                "branch": branch,
                "diff_count": len(diff),
                "audio_available": True,
                "midi_available": False,
            }
            validate_contract(descriptor, "studio-preview-v0.schema.json")
            detail = {
                "source_candidate": copy.deepcopy(candidate),
                "source": copy.deepcopy(resolved.source),
                "candidate_blueprint_sha256": resolved.candidate_blueprint_sha256,
                "proposed_material_sha256": resolved.proposed_material_sha256,
                "changed_instance_ids": list(resolved.changed_instance_ids),
                "offline_preview": {
                    "wav_sha256": rendered.wav_sha256,
                    "processing_plan_sha256": rendered.plan["bus_host_processing_plan_sha256"],
                    "sample_rate_hz": rate,
                    "derived_noncanonical": True,
                    "default_studio_media_overridden": False,
                },
            }
            session.pending = _PendingPreview(
                descriptor=descriptor,
                candidate=copy.deepcopy(proposed),
                diff=diff,
                midi_path=midi_path,
                wav_path=wav_path,
                actor=str(proposed["provenance"]["actor"]),
                reason=str(candidate["reason"]),
                detail=detail,
            )
            return {
                "preview_installed": True,
                "preview": copy.deepcopy(descriptor),
                "diff": copy.deepcopy(diff),
                "detail": copy.deepcopy(detail),
                "session": self.service.inspect_session(session_id),
            }
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def preview_wav(self, session_id: str) -> bytes:
        session = self.service._get_session(session_id)
        pending = session.pending
        if pending is None or pending.descriptor.get("kind") != "bus_host_edit":
            raise StudioServiceError("not_found", "no accepted-source bus-host Studio Preview")
        branch = session.project.current_branch()
        if branch != pending.descriptor["branch"] or (
            session.project.head_revision_id(branch) != pending.descriptor["parent_revision_id"]
        ):
            raise StudioServiceError("conflict", "pending bus-host Preview source is stale")
        raw = pending.wav_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != pending.detail["offline_preview"]["wav_sha256"]:
            raise StudioServiceError("integrity_error", "bus-host Preview WAV bytes changed")
        return raw
