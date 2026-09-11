"""Local-first MUSICA Studio application/session boundary for M4-R1.

This module deliberately sits above the validated music, Director, and Project Engine
layers. Preview candidates remain non-canonical until ``accept_preview`` explicitly
commits them through M2. All project/cache/export paths are confined to one configured
workspace.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .compiler import compile_blueprint
from .contracts import ContractError, validate_contract
from .director import (
    DirectorError,
    FixtureMusicDirectorProvider,
    build_create_request,
    build_edit_request,
    direct_create,
    direct_edit,
)
from .evidence import canonical_json_bytes
from .openai_provider import OpenAIAdapterError, OpenAIMusicDirectorProvider
from .project import MusicaProject, ProjectIntegrityError, create_project
from .render import DEFAULT_SAMPLE_RATE, render_midi, render_wav
from .semantic import M1_SEMANTIC_AXES, apply_semantic_control

STUDIO_SERVICE_ID = "musica-studio-service"
STUDIO_SERVICE_VERSION = "0.1.0"
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class StudioServiceError(RuntimeError):
    """Stable user-application error independent from internal exception details."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = bool(retryable)

    def as_dict(self) -> dict[str, Any]:
        value = {
            "error_version": "0",
            "code": self.code,
            "message": str(self)[:2000],
            "retryable": self.retryable,
        }
        validate_contract(value, "studio-error-v0.schema.json")
        return value


@dataclass
class _PendingPreview:
    descriptor: dict[str, Any]
    candidate: dict[str, Any]
    diff: list[dict[str, Any]]
    midi_path: Path
    wav_path: Path
    actor: str
    reason: str
    detail: dict[str, Any]


@dataclass
class _StudioSession:
    session_id: str
    provider_mode: str
    project_slug: str
    project: MusicaProject
    pending: _PendingPreview | None = None


def _digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _require_mapping(value: Any, label: str = "request body") -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise StudioServiceError("invalid_request", f"{label} must be a JSON object")
    return value


def _safe_name(value: str, label: str) -> str:
    text = str(value)
    if not _SAFE_NAME.fullmatch(text):
        raise StudioServiceError(
            "invalid_request",
            f"invalid {label}: use 1-64 ASCII letters, digits, '.', '_' or '-' and start with alphanumeric",
        )
    return text


class StudioService:
    """Filesystem-backed, local-first application service over the validated core."""

    def __init__(
        self,
        workspace: str | Path,
        *,
        provider_factories: dict[str, Callable[[], Any]] | None = None,
    ) -> None:
        root = Path(workspace).expanduser()
        root.mkdir(parents=True, exist_ok=True)
        self.workspace = root.resolve()
        self._sessions: dict[str, _StudioSession] = {}
        self._provider_factories: dict[str, Callable[[], Any]] = {
            "fixture": FixtureMusicDirectorProvider,
            "openai": OpenAIMusicDirectorProvider,
        }
        if provider_factories:
            for name, factory in provider_factories.items():
                if name not in {"fixture", "openai"}:
                    raise ValueError(f"unsupported Studio provider mode: {name}")
                self._provider_factories[name] = factory

        self._studio_root = self._confined(self.workspace / ".studio")
        self._studio_root.mkdir(parents=True, exist_ok=True)
        self._exports_root = self._confined(self.workspace / "exports")
        self._exports_root.mkdir(parents=True, exist_ok=True)

    def _confined(self, value: str | Path) -> Path:
        candidate = Path(value).expanduser().resolve(strict=False)
        try:
            candidate.relative_to(self.workspace)
        except ValueError as exc:
            raise StudioServiceError(
                "path_escape",
                "Studio path escapes the configured workspace",
            ) from exc
        return candidate

    def _project_path(self, project_slug: str) -> Path:
        slug = _safe_name(project_slug, "project_slug")
        return self._confined(self.workspace / f"{slug}.musica")

    def _session_cache(self, session_id: str) -> Path:
        safe = _safe_name(session_id, "session_id")
        return self._confined(self._studio_root / "sessions" / safe)

    def _new_session_id(self) -> str:
        return "studio-" + uuid.uuid4().hex[:20]

    def _provider(self, mode: str) -> Any:
        if mode not in self._provider_factories:
            raise StudioServiceError("invalid_request", f"unsupported provider mode: {mode}")
        try:
            return self._provider_factories[mode]()
        except Exception as exc:
            raise StudioServiceError("provider_error", f"cannot initialize provider: {exc}") from exc

    def _get_session(self, session_id: str) -> _StudioSession:
        safe = _safe_name(session_id, "session_id")
        session = self._sessions.get(safe)
        if session is None:
            raise StudioServiceError("not_found", f"unknown Studio session: {safe}")
        return session

    def _wrap_core_error(self, exc: Exception) -> StudioServiceError:
        if isinstance(exc, StudioServiceError):
            return exc
        if isinstance(exc, ProjectIntegrityError):
            return StudioServiceError("integrity_error", str(exc))
        if isinstance(exc, OpenAIAdapterError):
            return StudioServiceError(
                "provider_error",
                f"OpenAI provider {exc.classification}: {exc}",
                retryable=exc.classification in {"rate_limit", "server", "timeout", "transport"},
            )
        if isinstance(exc, DirectorError):
            return StudioServiceError("provider_error", str(exc))
        if isinstance(exc, ContractError):
            return StudioServiceError("invalid_request", str(exc))
        return StudioServiceError("internal_error", str(exc))

    def _request_id(self, operation: str, session_id: str, payload: Any) -> str:
        token = _digest({"operation": operation, "session_id": session_id, "payload": payload})[:24]
        return f"studio-{operation}-{token}"

    def _revision_id(self, parent_revision_id: str, operation: str, payload: Any) -> str:
        token = _digest(
            {
                "parent_revision_id": parent_revision_id,
                "operation": operation,
                "payload": payload,
            }
        )[:24]
        return f"rev-studio-{token}"

    def _preview_id(self, parent_revision_id: str, candidate_revision_id: str) -> str:
        return "preview-" + _digest(
            {"parent": parent_revision_id, "candidate": candidate_revision_id}
        )[:24]

    def _scope(self, blueprint: dict[str, Any], scope_kind: str, section_id: str | None) -> str:
        sections = blueprint["form"]["sections"]
        duration = float(blueprint["project"]["duration_seconds"])
        if scope_kind == "whole_project":
            if section_id is not None:
                raise StudioServiceError("invalid_request", "whole_project scope does not accept section_id")
            return f"time:0-{duration:g}"
        if scope_kind == "final_section":
            if section_id is not None:
                raise StudioServiceError("invalid_request", "final_section scope does not accept section_id")
            section = sections[-1]
            return f"time:{float(section['start']):g}-{float(section['end']):g}"
        if scope_kind == "section_id":
            if not section_id:
                raise StudioServiceError("invalid_request", "section_id scope requires section_id")
            for section in sections:
                if section["section_id"] == section_id:
                    return f"time:{float(section['start']):g}-{float(section['end']):g}"
            raise StudioServiceError("not_found", f"unknown section: {section_id}")
        raise StudioServiceError("invalid_request", f"unsupported scope_kind: {scope_kind}")

    def _hard_lock_targets(self, blueprint: dict[str, Any]) -> list[str]:
        return sorted(
            {
                str(lock["target"])
                for lock in blueprint.get("locks", [])
                if lock.get("strength") == "HARD"
            }
        )

    def _render_to_cache(
        self,
        session: _StudioSession,
        blueprint: dict[str, Any],
        cache_key: str,
    ) -> tuple[Path, Path]:
        cache_root = self._confined(self._session_cache(session.session_id) / "renders" / cache_key)
        if cache_root.exists():
            shutil.rmtree(cache_root)
        cache_root.mkdir(parents=True, exist_ok=True)
        ir = compile_blueprint(blueprint)
        midi = render_midi(ir, cache_root / "preview.mid")
        wav = render_wav(
            ir,
            cache_root / "preview.wav",
            duration_seconds=float(blueprint["project"]["duration_seconds"]),
            sample_rate=DEFAULT_SAMPLE_RATE,
        )
        self._confined(midi)
        self._confined(wav)
        return midi, wav

    def _artifact_media(self, project: MusicaProject, revision_id: str, suffix: str) -> Path | None:
        root = project.root / "artifacts" / revision_id / "files"
        if not root.exists():
            return None
        matches = sorted(path for path in root.iterdir() if path.is_file() and path.suffix.lower() == suffix)
        if not matches:
            return None
        return self._confined(matches[0])

    def _accepted_media(self, session: _StudioSession, suffix: str) -> Path:
        revision_id = session.project.head_revision_id()
        existing = self._artifact_media(session.project, revision_id, suffix)
        if existing is not None:
            return existing
        blueprint = session.project.read_revision(revision_id)
        midi, wav = self._render_to_cache(session, blueprint, f"accepted-{_digest(revision_id)[:16]}")
        return midi if suffix == ".mid" else wav

    def _clear_pending(self, session: _StudioSession) -> None:
        if session.pending is None:
            return
        preview_root = session.pending.wav_path.parent
        try:
            confined = self._confined(preview_root)
            if confined.exists():
                shutil.rmtree(confined)
        finally:
            session.pending = None

    def _install_preview(
        self,
        session: _StudioSession,
        *,
        kind: str,
        candidate: dict[str, Any],
        diff: list[dict[str, Any]],
        actor: str,
        reason: str,
        detail: dict[str, Any],
    ) -> dict[str, Any]:
        parent_revision_id = session.project.head_revision_id()
        if candidate["project"].get("parent_revision_id") != parent_revision_id:
            raise StudioServiceError("conflict", "preview candidate is not based on the current branch head")

        self._clear_pending(session)
        before_ref = session.project.head_revision_id()
        preview_id = self._preview_id(parent_revision_id, candidate["project"]["revision_id"])
        midi, wav = self._render_to_cache(session, candidate, preview_id)
        after_ref = session.project.head_revision_id()
        if before_ref != after_ref:
            raise StudioServiceError("integrity_error", "preview rendering changed the canonical branch ref")

        descriptor = {
            "preview_version": "0",
            "preview_id": preview_id,
            "kind": kind,
            "parent_revision_id": parent_revision_id,
            "candidate_revision_id": candidate["project"]["revision_id"],
            "branch": session.project.current_branch(),
            "diff_count": len(diff),
            "audio_available": wav.is_file(),
            "midi_available": midi.is_file(),
        }
        validate_contract(descriptor, "studio-preview-v0.schema.json")
        session.pending = _PendingPreview(
            descriptor=descriptor,
            candidate=copy.deepcopy(candidate),
            diff=copy.deepcopy(diff),
            midi_path=midi,
            wav_path=wav,
            actor=actor,
            reason=reason,
            detail=copy.deepcopy(detail),
        )
        return {
            "preview": copy.deepcopy(descriptor),
            "diff": copy.deepcopy(diff),
            "detail": copy.deepcopy(detail),
            "session": self.inspect_session(session.session_id),
        }

    def _bind_initial_render(self, session: _StudioSession, blueprint: dict[str, Any]) -> None:
        revision_id = blueprint["project"]["revision_id"]
        midi, wav = self._render_to_cache(session, blueprint, f"initial-{_digest(revision_id)[:16]}")
        session.project.bind_artifacts(revision_id, [midi, wav])
        cache_root = midi.parent
        if cache_root.exists():
            shutil.rmtree(cache_root)

    def create_project_session(
        self,
        *,
        project_slug: str,
        user_text: str,
        session_id: str | None = None,
        provider_mode: str = "fixture",
        locale: str = "en-US",
        duration_seconds: float | None = None,
        use_case: str | None = None,
        style_profile: str | None = None,
        seed: int | None = None,
        preserve_on_edit: list[str] | None = None,
        exclusions: list[str] | None = None,
    ) -> dict[str, Any]:
        sid = _safe_name(session_id or self._new_session_id(), "session_id")
        slug = _safe_name(project_slug, "project_slug")
        if sid in self._sessions:
            raise StudioServiceError("conflict", f"Studio session already exists: {sid}")
        project_path = self._project_path(slug)
        if project_path.exists() or project_path.is_symlink():
            raise StudioServiceError("conflict", f"project already exists: {slug}")
        provider = self._provider(provider_mode)
        request_payload = {
            "user_text": user_text,
            "locale": locale,
            "duration_seconds": duration_seconds,
            "use_case": use_case,
            "style_profile": style_profile,
            "seed": seed,
            "preserve_on_edit": preserve_on_edit or [],
            "exclusions": exclusions or [],
        }
        try:
            request = build_create_request(
                request_id=self._request_id("create", sid, request_payload),
                user_text=user_text,
                locale=locale,
                duration_seconds=duration_seconds,
                use_case=use_case,
                style_profile=style_profile,
                seed=seed,
                preserve_on_edit=preserve_on_edit,
                exclusions=exclusions,
            )
            result = direct_create(provider, request)
            project = create_project(project_path, result["blueprint"])
            session = _StudioSession(
                session_id=sid,
                provider_mode=provider_mode,
                project_slug=slug,
                project=project,
            )
            self._sessions[sid] = session
            self._bind_initial_render(session, result["blueprint"])
            project.verify_integrity()
        except Exception as exc:
            self._sessions.pop(sid, None)
            if project_path.exists() and not project_path.is_symlink():
                shutil.rmtree(project_path, ignore_errors=True)
            raise self._wrap_core_error(exc) from exc
        return {
            "session": self.inspect_session(sid),
            "director_trace": result["trace"],
            "intent": result["intent"],
        }

    def open_project_session(
        self,
        *,
        project_slug: str,
        session_id: str | None = None,
        provider_mode: str = "fixture",
    ) -> dict[str, Any]:
        sid = _safe_name(session_id or self._new_session_id(), "session_id")
        slug = _safe_name(project_slug, "project_slug")
        if sid in self._sessions:
            raise StudioServiceError("conflict", f"Studio session already exists: {sid}")
        project_path = self._project_path(slug)
        if not project_path.exists():
            raise StudioServiceError("not_found", f"project does not exist: {slug}")
        if not project_path.is_dir():
            raise StudioServiceError("invalid_request", f"project path is not a directory: {slug}")
        try:
            project = MusicaProject(project_path)
            project.verify_integrity()
            self._provider(provider_mode)  # validate provider mode/constructor at session-open time
            self._sessions[sid] = _StudioSession(
                session_id=sid,
                provider_mode=provider_mode,
                project_slug=slug,
                project=project,
            )
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc
        return {"session": self.inspect_session(sid)}

    def close_session(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        self._clear_pending(session)
        sid = session.session_id
        self._sessions.pop(sid, None)
        cache = self._session_cache(sid)
        if cache.exists():
            shutil.rmtree(cache)
        return {"closed_session_id": sid}

    def inspect_session(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        try:
            verification = session.project.verify_integrity()
            branch = session.project.current_branch()
            head_revision_id = session.project.head_revision_id(branch)
            blueprint = session.project.read_revision(head_revision_id)
            branches = {
                name: session.project.head_revision_id(name)
                for name in session.project.list_branches()
            }
            pending = copy.deepcopy(session.pending.descriptor) if session.pending else None
            audio = session.pending.wav_path if session.pending else self._artifact_media(session.project, head_revision_id, ".wav")
            midi = session.pending.midi_path if session.pending else self._artifact_media(session.project, head_revision_id, ".mid")
            view = {
                "session_version": "0",
                "session_id": session.session_id,
                "provider_mode": session.provider_mode,
                "project_slug": session.project_slug,
                "project_relpath": session.project.root.relative_to(self.workspace).as_posix(),
                "project_id": blueprint["project"]["project_id"],
                "current_branch": branch,
                "head_revision_id": head_revision_id,
                "integrity_status": verification["status"],
                "branches": branches,
                "sections": [
                    {
                        "section_id": section["section_id"],
                        "name": str(section.get("label") or section["section_id"]),
                        "start": float(section["start"]),
                        "end": float(section["end"]),
                    }
                    for section in blueprint["form"]["sections"]
                ],
                "semantic_state": {
                    axis: float(blueprint["semantics"]["global"][axis])
                    for axis in M1_SEMANTIC_AXES
                },
                "hard_locks": [
                    {
                        "lock_id": str(lock["lock_id"]),
                        "target": str(lock["target"]),
                        "mode": str(lock["mode"]),
                    }
                    for lock in blueprint.get("locks", [])
                    if lock.get("strength") == "HARD"
                ],
                "pending_preview": pending,
                "audio_available": bool(audio and audio.is_file()),
                "midi_available": bool(midi and midi.is_file()),
            }
            validate_contract(view, "studio-session-v0.schema.json")
            return view
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc

    def preview_semantic_edit(
        self,
        session_id: str,
        *,
        name: str,
        operation: str,
        value: float,
        scope_kind: str = "whole_project",
        section_id: str | None = None,
    ) -> dict[str, Any]:
        session = self._get_session(session_id)
        if name not in M1_SEMANTIC_AXES:
            raise StudioServiceError("invalid_request", f"unsupported Studio semantic axis: {name}")
        try:
            parent_revision_id = session.project.head_revision_id()
            parent = session.project.read_revision(parent_revision_id)
            scope = self._scope(parent, scope_kind, section_id)
            command = {
                "name": name,
                "operation": operation,
                "value": float(value),
                "scope": scope,
            }
            revision_id = self._revision_id(parent_revision_id, "semantic", command)
            control = {
                "control_id": "studio-" + _digest(command)[:24],
                "name": name,
                "operation": operation,
                "value": float(value),
                "scope": scope,
                "confidence": 1.0,
                "source": "user_control",
                "phrase": None,
                "interpretation_notes": ["Direct Studio semantic control."],
                "protected_targets": self._hard_lock_targets(parent),
            }
            candidate, diff = apply_semantic_control(parent, control, revision_id=revision_id)
            return self._install_preview(
                session,
                kind="semantic_control",
                candidate=candidate,
                diff=diff,
                actor="user",
                reason=f"Accept Studio semantic edit: {name} {operation} {float(value):g}.",
                detail={"control": control},
            )
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc

    def preview_director_edit(
        self,
        session_id: str,
        *,
        user_text: str,
        locale: str = "en-US",
    ) -> dict[str, Any]:
        session = self._get_session(session_id)
        try:
            parent_revision_id = session.project.head_revision_id()
            parent = session.project.read_revision(parent_revision_id)
            request_payload = {"user_text": user_text, "locale": locale, "parent": parent_revision_id}
            request = build_edit_request(
                parent,
                request_id=self._request_id("edit", session.session_id, request_payload),
                user_text=user_text,
                locale=locale,
            )
            revision_id = self._revision_id(parent_revision_id, "director", request_payload)
            result = direct_edit(
                self._provider(session.provider_mode),
                request,
                parent,
                revision_id=revision_id,
            )
            return self._install_preview(
                session,
                kind="director_edit",
                candidate=result["candidate"],
                diff=result["diff"],
                actor="ai",
                reason="Accept validated Studio AI Music Director edit.",
                detail={
                    "control": result["control"],
                    "director_trace": result["trace"],
                    "proposal": result["proposal"],
                },
            )
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc

    def accept_preview(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        pending = session.pending
        if pending is None:
            raise StudioServiceError("not_found", "no pending Studio preview to accept")
        branch = session.project.current_branch()
        current_head = session.project.head_revision_id(branch)
        if current_head != pending.descriptor["parent_revision_id"]:
            raise StudioServiceError(
                "conflict",
                "pending preview is stale because the branch head changed",
            )
        try:
            record = session.project.commit_revision(
                pending.candidate,
                branch=branch,
                actor=pending.actor,
                reason=pending.reason,
            )
            manifest = session.project.bind_artifacts(
                pending.candidate["project"]["revision_id"],
                [pending.midi_path, pending.wav_path],
            )
            accepted_preview_id = pending.descriptor["preview_id"]
            self._clear_pending(session)
            verification = session.project.verify_integrity()
            return {
                "accepted_preview_id": accepted_preview_id,
                "revision_record": record,
                "artifact_manifest": manifest,
                "project_verification": verification,
                "session": self.inspect_session(session_id),
            }
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc

    def discard_preview(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        pending = session.pending
        if pending is None:
            raise StudioServiceError("not_found", "no pending Studio preview to discard")
        preview_id = pending.descriptor["preview_id"]
        head_before = session.project.head_revision_id()
        self._clear_pending(session)
        head_after = session.project.head_revision_id()
        if head_before != head_after:
            raise StudioServiceError("integrity_error", "discard changed the canonical branch ref")
        return {
            "discarded_preview_id": preview_id,
            "head_revision_id": head_after,
            "session": self.inspect_session(session_id),
        }

    def create_branch(
        self,
        session_id: str,
        *,
        branch_name: str,
        checkout: bool = False,
    ) -> dict[str, Any]:
        session = self._get_session(session_id)
        if session.pending is not None:
            raise StudioServiceError("conflict", "accept or discard the pending preview before branching")
        try:
            name = _safe_name(branch_name, "branch_name")
            ref = session.project.create_branch(name, from_revision_id=session.project.head_revision_id())
            if checkout:
                session.project.checkout(name)
            return {"created_ref": ref, "session": self.inspect_session(session_id)}
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc

    def checkout_branch(self, session_id: str, *, branch_name: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        if session.pending is not None:
            raise StudioServiceError("conflict", "accept or discard the pending preview before checkout")
        try:
            session.project.checkout(_safe_name(branch_name, "branch_name"))
            return {"session": self.inspect_session(session_id)}
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc

    def revision_history(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        try:
            records: list[dict[str, Any]] = []
            revision_root = session.project.root / "revisions"
            for directory in sorted(path for path in revision_root.iterdir() if path.is_dir()):
                records.append(session.project.read_revision_record(directory.name))
            records.sort(key=lambda item: (int(item["logical_sequence"]), str(item["revision_id"])))
            return {
                "current_branch": session.project.current_branch(),
                "head_revision_id": session.project.head_revision_id(),
                "revisions": records,
            }
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc

    def export_project(self, session_id: str) -> dict[str, Any]:
        session = self._get_session(session_id)
        if session.pending is not None:
            raise StudioServiceError(
                "conflict",
                "accept or discard the pending preview before exporting canonical project state",
            )
        try:
            target = self._confined(self._exports_root / f"{session.project_slug}.musica.zip")
            exported = session.project.export_to(target)
            return {
                "export_relpath": exported.relative_to(self.workspace).as_posix(),
                "size_bytes": exported.stat().st_size,
                "sha256": hashlib.sha256(exported.read_bytes()).hexdigest(),
            }
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc

    def media_path(self, session_id: str, kind: str) -> Path:
        session = self._get_session(session_id)
        suffix = ".wav" if kind == "audio" else ".mid" if kind == "midi" else None
        if suffix is None:
            raise StudioServiceError("invalid_request", f"unsupported media kind: {kind}")
        if session.pending is not None:
            path = session.pending.wav_path if kind == "audio" else session.pending.midi_path
            return self._confined(path)
        try:
            return self._accepted_media(session, suffix)
        except Exception as exc:
            raise self._wrap_core_error(exc) from exc

    def media_bytes(self, session_id: str, kind: str) -> bytes:
        path = self.media_path(session_id, kind)
        if not path.is_file():
            raise StudioServiceError("not_found", f"{kind} media is unavailable")
        return path.read_bytes()


class StudioApplication:
    """Small JSON dispatch surface used by the M4-R1 HTTP bridge and tests."""

    def __init__(self, service: StudioService):
        self.service = service

    def _response(self, operation: str, data: Any) -> dict[str, Any]:
        value = {
            "response_version": "0",
            "ok": True,
            "operation": operation,
            "data": data,
        }
        validate_contract(value, "studio-response-v0.schema.json")
        return value

    def dispatch(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        method = method.upper()
        payload = _require_mapping(body)
        clean = "/" + path.strip("/")
        parts = [part for part in clean.split("/") if part]

        if method == "POST" and clean == "/v0/projects/create":
            return self._response("create_project", self.service.create_project_session(**payload))
        if method == "POST" and clean == "/v0/projects/open":
            return self._response("open_project", self.service.open_project_session(**payload))

        if len(parts) < 3 or parts[:2] != ["v0", "sessions"]:
            raise StudioServiceError("not_found", f"unknown Studio route: {method} {clean}")
        session_id = parts[2]

        if len(parts) == 3 and method == "GET":
            return self._response("inspect_session", self.service.inspect_session(session_id))
        if parts[3:] == ["preview", "semantic"] and method == "POST":
            return self._response(
                "preview_semantic_edit",
                self.service.preview_semantic_edit(session_id, **payload),
            )
        if parts[3:] == ["preview", "direct"] and method == "POST":
            return self._response(
                "preview_director_edit",
                self.service.preview_director_edit(session_id, **payload),
            )
        if parts[3:] == ["preview", "accept"] and method == "POST":
            return self._response("accept_preview", self.service.accept_preview(session_id))
        if parts[3:] == ["preview", "discard"] and method == "POST":
            return self._response("discard_preview", self.service.discard_preview(session_id))
        if parts[3:] == ["branches"] and method == "POST":
            return self._response("create_branch", self.service.create_branch(session_id, **payload))
        if parts[3:] == ["checkout"] and method == "POST":
            return self._response("checkout_branch", self.service.checkout_branch(session_id, **payload))
        if parts[3:] == ["history"] and method == "GET":
            return self._response("revision_history", self.service.revision_history(session_id))
        if parts[3:] == ["export"] and method == "POST":
            return self._response("export_project", self.service.export_project(session_id))
        if parts[3:] == ["close"] and method == "POST":
            return self._response("close_session", self.service.close_session(session_id))

        raise StudioServiceError("not_found", f"unknown Studio route: {method} {clean}")
