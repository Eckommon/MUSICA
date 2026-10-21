"""G3B-0 — bounded same-origin WAV staging; never an accepted creative edit.

A staged transfer is intentionally not an asset or a canonical clip until its
declared length and whole-file SHA match. Finishing delegates the *existing*
immutable resource import; it currently uses bounded whole-file memory and is
not a streaming CAS or a long-song performance claim (G3B-1/-2).
"""
from __future__ import annotations

import hashlib
import re
import secrets
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .studio import StudioService, StudioServiceError
from .studio_audio import StudioAudioSurface

MAX_STAGED_WAV_BYTES = 64 * 1024 * 1024
STAGED_CHUNK_BYTES = 1024 * 1024
MAX_ACTIVE_STAGES = 4
STAGE_TTL_SECONDS = 15 * 60
_DIGEST = re.compile(r"[a-f0-9]{64}\Z")
_TOKEN = re.compile(r"[a-f0-9]{32}\Z")


@dataclass
class _Stage:
    token: str
    session_id: str
    revision_id: str
    expected_size: int
    expected_sha: str
    path: Path
    hasher: Any
    offset: int
    last_used: float


class WavStagingStore:
    """One-server volatile upload registry, server-chosen opaque staging paths."""

    def __init__(self, service: StudioService, audio: StudioAudioSurface) -> None:
        self.service = service
        self.audio = audio
        self.root = service.workspace / ".wav-staging-g3b0"
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._stages: dict[str, _Stage] = {}
        # Previous server crashes may leave orphaned temp files; never expose
        # their paths through the API and never treat them as imported assets.
        self._sweep_orphans()

    def _sweep_orphans(self) -> None:
        now = time.time()
        active = {stage.path for stage in self._stages.values()}
        for path in self.root.glob("musica-*.part"):
            if path not in active and path.is_file():
                try:
                    if now - path.stat().st_mtime > STAGE_TTL_SECONDS:
                        path.unlink()
                except FileNotFoundError:
                    pass

    def _delete(self, stage: _Stage) -> None:
        self._stages.pop(stage.token, None)
        stage.path.unlink(missing_ok=True)

    def _clean_expired(self) -> None:
        now = time.monotonic()
        for stage in list(self._stages.values()):
            if now - stage.last_used > STAGE_TTL_SECONDS:
                self._delete(stage)
        self._sweep_orphans()

    def _session(self, session_id: str):
        session = self.service._get_session(session_id)
        if session.pending is not None:
            raise StudioServiceError(
                "conflict", "Accept or Discard pending Preview before staging WAV"
            )
        return session

    def _active(self, session_id: str, upload_id: str) -> _Stage:
        if _TOKEN.fullmatch(upload_id) is None:
            raise StudioServiceError("invalid_request", "invalid opaque upload ID")
        stage = self._stages.get(upload_id)
        if stage is None or stage.session_id != session_id:
            raise StudioServiceError("invalid_request", "unknown staged WAV upload")
        return stage

    def _source(self, stage: _Stage):
        session = self._session(stage.session_id)
        if session.project.head_revision_id() != stage.revision_id:
            self._delete(stage)
            raise StudioServiceError("conflict", "accepted project revision changed while staging")
        return session

    def start(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._clean_expired()
            session = self._session(session_id)
            if set(payload) != {"size_bytes", "sha256"}:
                raise StudioServiceError("invalid_request", "expected size_bytes and sha256 only")
            size = payload["size_bytes"]
            sha = payload["sha256"]
            if (type(size) is not int or not 44 <= size <= MAX_STAGED_WAV_BYTES or
                    not isinstance(sha, str) or _DIGEST.fullmatch(sha) is None):
                raise StudioServiceError("invalid_request", "invalid bounded WAV size or SHA-256")
            if len(self._stages) >= MAX_ACTIVE_STAGES or any(
                s.session_id == session_id for s in self._stages.values()
            ):
                raise StudioServiceError("conflict", "one staged WAV per Studio session, maximum four")
            session.project.verify_integrity()
            fd, raw_path = tempfile.mkstemp(prefix="musica-", suffix=".part", dir=self.root)
            import os
            os.close(fd)
            token = secrets.token_hex(16)
            stage = _Stage(
                token, session_id, session.project.head_revision_id(),
                size, sha, Path(raw_path), hashlib.sha256(), 0, time.monotonic()
            )
            self._stages[token] = stage
            return {
                "upload_id": token, "next_offset": 0,
                "max_chunk_bytes": STAGED_CHUNK_BYTES,
                "expected_size_bytes": size,
                "accepted_revision_id": stage.revision_id,
                "accepted_revision_unchanged": True,
                "classification": "TEMPORARY_WAV_NOT_ACCEPTED_ASSET_OR_CLIP",
            }

    def chunk(
        self, session_id: str, upload_id: str, offset: int,
        data: bytes, chunk_sha: str
    ) -> dict[str, Any]:
        with self._lock:
            self._clean_expired()
            stage = self._active(session_id, upload_id)
            self._source(stage)
            if (
                type(offset) is not int or offset != stage.offset or
                not isinstance(data, bytes) or not 1 <= len(data) <= STAGED_CHUNK_BYTES or
                stage.offset + len(data) > stage.expected_size or
                not isinstance(chunk_sha, str) or _DIGEST.fullmatch(chunk_sha) is None
            ):
                self._delete(stage)
                raise StudioServiceError("invalid_request", "staged WAV offset/size/hash contract failed")
            if hashlib.sha256(data).hexdigest() != chunk_sha:
                self._delete(stage)
                raise StudioServiceError("invalid_request", "staged WAV chunk SHA-256 mismatch")
            with stage.path.open("ab") as handle:
                handle.write(data)
            stage.hasher.update(data)
            stage.offset += len(data)
            stage.last_used = time.monotonic()
            return {
                "upload_id": stage.token, "next_offset": stage.offset,
                "accepted_revision_id": stage.revision_id,
                "accepted_revision_unchanged": True
            }

    def finish(self, session_id: str, upload_id: str) -> dict[str, Any]:
        with self._lock:
            self._clean_expired()
            stage = self._active(session_id, upload_id)
            self._source(stage)
            try:
                if (stage.offset != stage.expected_size or
                        stage.path.stat().st_size != stage.expected_size or
                        stage.hasher.hexdigest() != stage.expected_sha):
                    raise StudioServiceError("invalid_request", "staged WAV incomplete or SHA mismatch")
                # G3B-0 only: bounded 64 MiB in-memory finalization through
                # preexisting audited CAS. G3B-1 must replace this read.
                raw = stage.path.read_bytes()
                result = self.audio.import_wav_resource(session_id, raw)
                if result["accepted_revision_id"] != stage.revision_id:
                    raise StudioServiceError("conflict", "accepted HEAD changed on asset finalize")
                result["staged_upload_sha256"] = stage.expected_sha
                result["staged_upload_size_bytes"] = stage.expected_size
                return result
            finally:
                self._delete(stage)

    def cancel(self, session_id: str, upload_id: str) -> dict[str, Any]:
        with self._lock:
            self._clean_expired()
            self.service._get_session(session_id)
            stage = self._active(session_id, upload_id)
            self._delete(stage)
            return {"cancelled": True, "accepted_revision_unchanged": True}
