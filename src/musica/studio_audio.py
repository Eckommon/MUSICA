"""ATCM-R3 Studio/Browser native-audio arrangement and mixer surface.

This adapter projects exact accepted native-audio state into Studio and routes Browser
proposals through the already validated R1/R2 AudioEditPreview authority family.
Browser state, preview WAV bytes, controls and transport never become project authority.
"""

from __future__ import annotations

import copy
import shutil
from typing import Any

from .audio_assets import read_audio_asset
from .audio_contracts import audio_material_from_blueprint, validate_project_blueprint_audio
from .audio_edit import (
    AudioEditPreview,
    accept_audio_edit_preview,
    audio_material_sha256,
    blueprint_sha256,
    build_audio_edit_preview,
)
from .audio_mixer_edit import build_audio_mixer_edit_preview
from .contracts import ContractError, validate_contract
from .diff import structured_diff
from .native_mixer import NativeMixRender, render_native_mix
from .routed_mixer import RoutedMixRender, render_routed_mix
from .routing_contracts import routing_material_from_blueprint
from .studio import StudioService, StudioServiceError, _PendingPreview


class _BlueprintProjectProxy:
    """Read one non-canonical Blueprint while delegating immutable project resources."""

    def __init__(self, project: Any, blueprint: dict[str, Any]) -> None:
        self._project = project
        self._blueprint = copy.deepcopy(blueprint)
        self.root = project.root

    def read_revision(self, revision_id: str) -> dict[str, Any]:
        if str(revision_id) == str(self._blueprint["project"]["revision_id"]):
            return copy.deepcopy(self._blueprint)
        return self._project.read_revision(revision_id)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._project, name)


def _material(blueprint: dict[str, Any]) -> dict[str, Any]:
    value = audio_material_from_blueprint(blueprint)
    if value is None:
        raise ContractError("native audio material is unavailable")
    return value


def _mix_rate(project: Any, blueprint: dict[str, Any]) -> int:
    rates: set[int] = set()
    for track in _material(blueprint)["tracks"]:
        for clip in track["clips"]:
            descriptor = read_audio_asset(project, str(clip["asset_id"]))
            rates.add(int(descriptor["format"]["sample_rate_hz"]))
    if not rates:
        raise ContractError("native audio audition requires at least one accepted clip")
    if len(rates) != 1:
        raise ContractError(
            "native audio audition requires one exact source sample rate; "
            f"found {sorted(rates)}"
        )
    return next(iter(rates))


class StudioAudioSurface:
    """Truthful Studio projection and trusted Preview/Accept bridge for ATCM-R3."""

    def __init__(self, service: StudioService) -> None:
        self.service = service
        self._render_cache: dict[tuple[str, str, str, int], NativeMixRender | RoutedMixRender] = {}

    def _render_blueprint(
        self,
        session_id: str,
        project: Any,
        blueprint: dict[str, Any],
        *,
        source_kind: str,
    ) -> NativeMixRender | RoutedMixRender:
        rate = _mix_rate(project, blueprint)
        digest = blueprint_sha256(blueprint)
        key = (session_id, source_kind, digest, rate)
        cached = self._render_cache.get(key)
        if cached is not None:
            return cached
        revision_id = str(blueprint["project"]["revision_id"])
        routing = routing_material_from_blueprint(blueprint)
        assert routing is not None
        routed = bool(routing["nodes"] or routing["track_outputs"] or routing["sends"])
        source_project = project
        if revision_id != project.head_revision_id(project.current_branch()):
            source_project = _BlueprintProjectProxy(project, blueprint)
        if routed:
            rendered = render_routed_mix(
                source_project, revision_id, mix_sample_rate_hz=rate
            )
        else:
            rendered = render_native_mix(
                source_project, revision_id, mix_sample_rate_hz=rate
            )
        self._render_cache[key] = rendered
        return rendered

    def _audition_summary(
        self,
        session_id: str,
        project: Any,
        blueprint: dict[str, Any],
        *,
        source_kind: str,
    ) -> dict[str, Any]:
        try:
            rendered = self._render_blueprint(
                session_id, project, blueprint, source_kind=source_kind
            )
            return {
                "available": True,
                "source_kind": source_kind,
                "mix_sample_rate_hz": int(rendered.plan["mix_sample_rate_hz"]),
                "mix_plan_sha256": str(
                    rendered.plan.get("mix_plan_sha256")
                    or rendered.plan["routed_mix_plan_sha256"]
                ),
                "wav_sha256": str(rendered.wav_sha256),
                "wav_size_bytes": len(rendered.wav_bytes),
                "rendered_audio_is_canonical": False,
                "error": None,
            }
        except (ContractError, OSError) as exc:
            return {
                "available": False,
                "source_kind": source_kind,
                "mix_sample_rate_hz": None,
                "mix_plan_sha256": None,
                "wav_sha256": None,
                "wav_size_bytes": None,
                "rendered_audio_is_canonical": False,
                "error": str(exc),
            }

    def audio_view(self, session_id: str) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        try:
            branch = session.project.current_branch()
            revision_id = session.project.head_revision_id(branch)
            accepted = session.project.read_revision(revision_id)
            validate_project_blueprint_audio(session.project, accepted)
            material = copy.deepcopy(_material(accepted))

            preview_value: dict[str, Any] | None = None
            pending = session.pending
            if pending is not None and pending.descriptor.get("kind") == "native_audio_edit":
                detail = pending.detail.get("native_audio")
                if not isinstance(detail, dict):
                    raise StudioServiceError(
                        "integrity_error",
                        "pending native-audio Preview is missing authority detail",
                    )
                preview_material = copy.deepcopy(_material(pending.candidate))
                preview_value = {
                    "preview_id": str(pending.descriptor["preview_id"]),
                    "candidate_revision_id": str(
                        pending.descriptor["candidate_revision_id"]
                    ),
                    "candidate_kind": str(detail["candidate_kind"]),
                    "candidate_id": str(detail["candidate"]["candidate_id"]),
                    "tracks": preview_material["tracks"],
                    "material_diff": copy.deepcopy(detail["authority"]["material_diff"]),
                    "authority_result": copy.deepcopy(
                        detail["authority"]["authority_result"]
                    ),
                    "audition": self._audition_summary(
                        session_id,
                        session.project,
                        pending.candidate,
                        source_kind="preview",
                    ),
                }

            value = {
                "view_version": "0",
                "project_id": str(accepted["project"]["project_id"]),
                "branch": str(branch),
                "revision_id": str(revision_id),
                "blueprint_sha256": blueprint_sha256(accepted),
                "audio_material_sha256": audio_material_sha256(accepted),
                "accepted_state_is_canonical": True,
                "browser_state_is_canonical": False,
                "tracks": material["tracks"],
                "accepted_audition": self._audition_summary(
                    session_id, session.project, accepted, source_kind="accepted"
                ),
                "preview": preview_value,
                "capabilities": {
                    "arrangement_preview": True,
                    "mixer_preview": True,
                    "explicit_audio_accept_required": True,
                    "discard": True,
                    "native_mix_audition": True,
                    "direct_blueprint_mutation": False,
                    "recording": False,
                    "realtime_device_engine": False,
                    "plugin_hosting": False,
                    "resampling": False,
                },
            }
            validate_contract(value, "studio-audio-view-v0.schema.json")
            return value
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def _resolve(
        self,
        session: Any,
        candidate: dict[str, Any],
        *,
        candidate_kind: str,
        revision_id: str | None = None,
    ) -> AudioEditPreview:
        parent_id = session.project.head_revision_id()
        parent = session.project.read_revision(parent_id)
        if candidate_kind == "arrangement":
            return build_audio_edit_preview(
                session.project, parent, candidate, revision_id=revision_id
            )
        if candidate_kind == "mixer":
            return build_audio_mixer_edit_preview(
                session.project, parent, candidate, revision_id=revision_id
            )
        raise StudioServiceError(
            "invalid_request", f"unsupported native-audio candidate kind: {candidate_kind}"
        )

    def preview_audio_edit(
        self,
        session_id: str,
        *,
        candidate: dict[str, Any],
        candidate_kind: str,
    ) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        try:
            resolved = self._resolve(
                session, candidate, candidate_kind=candidate_kind
            )
            authority = resolved.as_dict()
            if not resolved.ready or resolved.blueprint is None:
                return {
                    "preview_installed": False,
                    "authority_result": copy.deepcopy(resolved.authority_result),
                    "native_audio": authority,
                    "session": self.service.inspect_session(session_id),
                    "audio_view": self.audio_view(session_id),
                }

            rendered = self._render_blueprint(
                session_id,
                session.project,
                resolved.blueprint,
                source_kind="preview",
            )
            parent_revision_id = session.project.head_revision_id()
            if resolved.source_revision_id != parent_revision_id:
                raise StudioServiceError(
                    "conflict", "native-audio Preview source changed before installation"
                )
            preview_id = self.service._preview_id(
                parent_revision_id,
                str(resolved.blueprint["project"]["revision_id"]),
            )
            cache_root = self.service._confined(
                self.service._session_cache(session_id)
                / "native-audio"
                / preview_id
            )
            if cache_root.exists():
                shutil.rmtree(cache_root)
            cache_root.mkdir(parents=True, exist_ok=True)
            wav_path = cache_root / "preview.wav"
            wav_path.write_bytes(rendered.wav_bytes)
            midi_path = cache_root / "preview.mid"

            descriptor = {
                "preview_version": "0",
                "preview_id": preview_id,
                "kind": "native_audio_edit",
                "parent_revision_id": parent_revision_id,
                "candidate_revision_id": str(
                    resolved.blueprint["project"]["revision_id"]
                ),
                "branch": session.project.current_branch(),
                "diff_count": len(resolved.material_diff),
                "audio_available": True,
                "midi_available": False,
            }
            validate_contract(descriptor, "studio-preview-v0.schema.json")
            generic_diff = structured_diff(
                session.project.read_revision(parent_revision_id),
                resolved.blueprint,
            )
            self.service._clear_pending(session)
            session.pending = _PendingPreview(
                descriptor=descriptor,
                candidate=copy.deepcopy(resolved.blueprint),
                diff=generic_diff,
                midi_path=midi_path,
                wav_path=wav_path,
                actor=str(candidate["actor"]["kind"]),
                reason=str(candidate["reason"]),
                detail={
                    "native_audio": {
                        "candidate_kind": candidate_kind,
                        "candidate": copy.deepcopy(candidate),
                        "authority": authority,
                        "audition": rendered.report(),
                    }
                },
            )
            return {
                "preview_installed": True,
                "authority_result": copy.deepcopy(resolved.authority_result),
                "native_audio": authority,
                "session": self.service.inspect_session(session_id),
                "audio_view": self.audio_view(session_id),
            }
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def accept_audio_preview(self, session_id: str) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        pending = session.pending
        if pending is None or pending.descriptor.get("kind") != "native_audio_edit":
            raise StudioServiceError(
                "not_found", "no pending native-audio Studio Preview to accept"
            )
        current_head = session.project.head_revision_id()
        if current_head != pending.descriptor["parent_revision_id"]:
            raise StudioServiceError(
                "conflict", "pending native-audio Preview is stale because HEAD changed"
            )
        detail = pending.detail.get("native_audio")
        if not isinstance(detail, dict):
            raise StudioServiceError(
                "integrity_error", "pending native-audio Preview authority detail is missing"
            )
        candidate = detail.get("candidate")
        candidate_kind = detail.get("candidate_kind")
        if not isinstance(candidate, dict) or candidate_kind not in {
            "arrangement",
            "mixer",
        }:
            raise StudioServiceError(
                "integrity_error", "pending native-audio candidate binding is invalid"
            )
        try:
            resolved = self._resolve(
                session,
                candidate,
                candidate_kind=str(candidate_kind),
                revision_id=str(pending.descriptor["candidate_revision_id"]),
            )
            if not resolved.ready or resolved.blueprint is None:
                raise StudioServiceError(
                    "conflict", "pending native-audio Preview no longer passes authority"
                )
            if blueprint_sha256(resolved.blueprint) != blueprint_sha256(
                pending.candidate
            ):
                raise StudioServiceError(
                    "integrity_error",
                    "recomputed native-audio Preview differs from pending candidate",
                )
            accepted_preview_id = str(pending.descriptor["preview_id"])
            record = accept_audio_edit_preview(session.project, resolved)
            self.service._clear_pending(session)
            self._render_cache.clear()
            verification = session.project.verify_integrity()
            return {
                "accepted_preview_id": accepted_preview_id,
                "revision_record": record,
                "project_verification": verification,
                "session": self.service.inspect_session(session_id),
                "audio_view": self.audio_view(session_id),
            }
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def discard_audio_preview(self, session_id: str) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        if session.pending is None or session.pending.descriptor.get("kind") != "native_audio_edit":
            raise StudioServiceError(
                "not_found", "no pending native-audio Studio Preview to discard"
            )
        result = self.service.discard_preview(session_id)
        self._render_cache.clear()
        result["audio_view"] = self.audio_view(session_id)
        return result

    def audition(self, session_id: str, *, source_kind: str) -> NativeMixRender:
        session = self.service._get_session(session_id)
        try:
            if source_kind == "accepted":
                revision_id = session.project.head_revision_id()
                blueprint = session.project.read_revision(revision_id)
            elif source_kind == "preview":
                pending = session.pending
                if pending is None or pending.descriptor.get("kind") != "native_audio_edit":
                    raise StudioServiceError(
                        "not_found", "no pending native-audio Preview audition"
                    )
                blueprint = pending.candidate
            else:
                raise StudioServiceError(
                    "invalid_request", f"unsupported audition source: {source_kind}"
                )
            return self._render_blueprint(
                session_id,
                session.project,
                blueprint,
                source_kind=source_kind,
            )
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc
