"""G3B2C-R5: source-bound ephemeral WAV reuse for an *unaccepted* Studio Preview.

This cache is strictly separate from the accepted WAV cache. A session's
candidate is authenticated against its in-memory pending Preview authority,
accepted parent HEAD and the actual immutable source CAS before every seek.
Only noncanonical derived output is cached; no Preview is Accept'ed here.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import threading
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .audio_assets import _file_sha256
from .audio_edit import blueprint_sha256
from .contracts import ContractError
from .native_mixer import build_native_mix_plan
from .routed_mixer import build_routed_mix_plan
from .routing_contracts import routing_material_from_blueprint
from .studio import StudioService, StudioServiceError
from .studio_audio import _mix_rate
from .studio_pending_wav import (
    PendingStreamedWav, _ExactPendingCandidateProject,
    render_pending_preview_streamed,
)
from .studio_wav_cache import _source_objects

PENDING_CACHE_TTL_SECONDS = 300.0
MAX_PENDING_CACHED_WAV_BYTES = 256 * 1024 * 1024
MAX_PENDING_CACHE_FILES = 2


@dataclass
class _PendingFile:
    render: PendingStreamedWav
    identity: str
    sources: tuple[tuple[Path, str], ...]
    last_access: float


class PendingWavFileCache:
    """Two private WAVs max, exact pending revision binding, idle TTL."""

    def __init__(self, service: StudioService) -> None:
        self._service = service
        self.root = Path(service.workspace) / ".derived-pending-wav-cache-g3b2c-r5"
        if self.root.is_symlink():
            raise ContractError("pending WAV cache root may not be a symlink")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._guard = threading.RLock()
        self._entries: dict[str, _PendingFile] = {}
        self._leases: set[str] = set()
        self._invalidate_after_release: set[str] = set()
        self._render_count = 0
        # On fresh startup no current service process can own these files.
        for orphan in self.root.glob("pending-*.wav"):
            if orphan.is_symlink() or orphan.is_file():
                orphan.unlink(missing_ok=True)

    @property
    def render_count(self) -> int:
        with self._guard:
            return self._render_count

    def _evict(self, session_id: str) -> None:
        if session_id in self._leases:
            raise StudioServiceError("conflict", "pending WAV is still in use")
        entry = self._entries.pop(session_id, None)
        if entry is not None:
            entry.render.wav_path.unlink(missing_ok=True)

    def invalidate_session(self, session_id: str) -> None:
        """Eagerly discard invalid Preview data; defer deletion only if leased.

        Never block canonical Accept/Discard while HTTP is finishing a chunk.
        The streaming authority rechecks the live candidate per output chunk.
        """
        with self._guard:
            if session_id in self._leases:
                self._invalidate_after_release.add(session_id)
            else:
                self._evict(session_id)

    def clear_session(self, session_id: str) -> None:
        with self._guard:
            self._evict(session_id)

    def clear_all_idle(self) -> None:
        with self._guard:
            for key in list(self._entries):
                if key not in self._leases:
                    self._evict(key)

    def _prune(self) -> None:
        now = time.monotonic()
        for key, entry in list(self._entries.items()):
            if key not in self._leases and now - entry.last_access > PENDING_CACHE_TTL_SECONDS:
                self._evict(key)

    def release(self, session_id: str) -> None:
        with self._guard:
            self._leases.discard(session_id)
            if session_id in self._invalidate_after_release:
                self._invalidate_after_release.remove(session_id)
                self._evict(session_id)
            elif session_id in self._entries:
                self._entries[session_id].last_access = time.monotonic()
            self._prune()

    def _trusted_inputs(self, session_id: str, preview_id: str):
        session = self._service._get_session(session_id)
        project = session.project
        pending = session.pending
        if pending is None or pending.descriptor.get("preview_id") != preview_id:
            raise StudioServiceError("not_found", "pending Preview no longer active")
        branch = pending.descriptor.get("branch")
        accepted_parent = pending.descriptor.get("parent_revision_id")
        candidate_revision = pending.descriptor.get("candidate_revision_id")
        if project.current_branch() != branch or project.head_revision_id(branch) != accepted_parent:
            raise StudioServiceError("conflict", "pending Preview accepted parent changed")
        candidate = pending.candidate
        if candidate["project"]["revision_id"] != candidate_revision:
            raise StudioServiceError("integrity_error", "pending candidate revision changed")
        overlay = _ExactPendingCandidateProject(project, candidate)
        material = routing_material_from_blueprint(candidate)
        routed = bool(material["nodes"] or material["track_outputs"] or material["sends"])
        rate = _mix_rate(overlay, candidate)
        plan = (build_routed_mix_plan(
            overlay, candidate_revision, mix_sample_rate_hz=rate
        ) if routed else build_native_mix_plan(
            overlay, candidate_revision, mix_sample_rate_hz=rate
        ))
        plan_sha = str(plan[
            "routed_mix_plan_sha256" if routed else "mix_plan_sha256"
        ])
        objects = _source_objects(project, plan, routed=routed)
        blueprint_digest = blueprint_sha256(candidate)
        fingerprint = hashlib.sha256(repr((
            session_id, str(project.root.resolve()), id(pending),
            branch, accepted_parent, preview_id, candidate_revision,
            blueprint_digest, routed, plan_sha, rate,
            tuple(digest for _, digest in objects),
        )).encode("utf-8")).hexdigest()
        return session, pending, accepted_parent, blueprint_digest, objects, fingerprint

    def _still_current(self, session: Any, pending: Any,
                       accepted_parent: str, blueprint_digest: str) -> bool:
        return (
            session.pending is pending and
            session.project.head_revision_id(session.project.current_branch()) == accepted_parent and
            blueprint_sha256(pending.candidate) == blueprint_digest
        )

    def _cache_ok(self, entry: _PendingFile) -> bool:
        file = entry.render.wav_path
        if (file.is_symlink() or not file.is_file() or
                file.parent != self.root or
                file.stat().st_size != entry.render.wav_size_bytes):
            return False
        for original, digest in entry.sources:
            if original.is_symlink() or not original.is_file() or _file_sha256(original) != digest:
                raise ContractError("pending Preview immutable source CAS integrity violated")
        return _file_sha256(file) == entry.render.wav_sha256

    def acquire(self, session_id: str, preview_id: str) -> PendingStreamedWav:
        session, pending, parent, digest, objects, identity = self._trusted_inputs(
            session_id, preview_id
        )
        with self._guard:
            self._prune()
            if session_id in self._leases:
                raise StudioServiceError("conflict", "pending WAV is already leased")
            existing = self._entries.get(session_id)
            if existing is not None:
                if existing.identity != identity:
                    self._evict(session_id)
                elif self._cache_ok(existing) and self._still_current(session, pending, parent, digest):
                    self._leases.add(session_id)
                    existing.last_access = time.monotonic()
                    return existing.render
                else:
                    self._evict(session_id)
            self._leases.add(session_id)
        temporary: Path | None = None
        published: Path | None = None
        try:
            render = render_pending_preview_streamed(
                self._service, session_id, preview_id=preview_id
            )
            temporary = render.wav_path
            if render.wav_size_bytes > MAX_PENDING_CACHED_WAV_BYTES:
                raise ContractError("pending WAV exceeds source-bound cache maximum")
            if not self._still_current(session, pending, parent, digest):
                raise StudioServiceError("conflict", "pending Preview changed during DSP")
            for path, expected in objects:
                if path.is_symlink() or not path.is_file() or _file_sha256(path) != expected:
                    raise ContractError("pending Preview CAS source changed during DSP")
            published = self.root / ("pending-" + secrets.token_hex(16) + ".wav")
            os.replace(temporary, published)
            temporary = None
            result = replace(render, wav_path=published)
            with self._guard:
                if not self._still_current(session, pending, parent, digest):
                    raise StudioServiceError("conflict", "pending Preview changed before publication")
                for sid, entry in sorted(self._entries.items(), key=lambda kv: kv[1].last_access):
                    if len(self._entries) < MAX_PENDING_CACHE_FILES:
                        break
                    if sid not in self._leases:
                        self._evict(sid)
                if len(self._entries) >= MAX_PENDING_CACHE_FILES:
                    raise StudioServiceError("conflict", "pending WAV cache quota exhausted")
                # A Discard/Accept during the lengthy 180-second render may
                # defer eviction until HTTP releases this same session.
                if session_id in self._invalidate_after_release:
                    raise StudioServiceError("conflict", "Preview invalidated before cached publication")
                self._entries[session_id] = _PendingFile(
                    result, identity, objects, time.monotonic()
                )
                self._render_count += 1
                published = None
                return result
        except BaseException:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            if published is not None:
                published.unlink(missing_ok=True)
            with self._guard:
                self._leases.discard(session_id)
                self._invalidate_after_release.discard(session_id)
            raise
