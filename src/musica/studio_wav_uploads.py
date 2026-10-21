"""G3B1B: Studio-owned session/HEAD authority around bounded private WAV uploads.

Never accepts a client filesystem path, and never accepts a creative revision.
The G3B0 low-level staging primitive owns bytes; G3B1A owns immutable CAS.
"""
from __future__ import annotations

import hashlib
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .audio_assets import import_audio_asset_verified_path
from .contracts import ContractError
from .staged_wav import BoundedWavStaging, MAX_CHUNK_BYTES, MAX_STAGED_WAV_BYTES
from .studio import StudioService, StudioServiceError

_TTL_SECONDS = 15 * 60
_TOKEN = re.compile(r"[a-zA-Z0-9_-]{43}\Z")
_SHA256 = re.compile(r"[a-f0-9]{64}\Z")


@dataclass
class _Upload:
    session_id: str
    revision_id: str
    expected_sha256: str
    expected_size: int
    touched: float
    received: int = 0


class StudioWavUploads:
    """Volatile, per-server upload sessions and authoritative CAS finalize."""

    def __init__(self, service: StudioService) -> None:
        self.service = service
        self.root = service.workspace / ".wav-staging-g3b1b"
        self.root.mkdir(parents=True, exist_ok=True)
        # On restart previous process upload tokens cannot be recovered; clear
        # only temp files in this explicitly dedicated directory.
        for orphan in self.root.glob("wav-*"):
            if orphan.is_file() and not orphan.is_symlink():
                orphan.unlink()
        self.stage = BoundedWavStaging(self.root)
        self._lock = threading.RLock()
        self._uploads: dict[str, _Upload] = {}

    @staticmethod
    def _stage_session_id(session_id: str) -> str:
        # Core G3B0 IDs disallow '.', while Studio session IDs may contain it.
        # Bind the opaque core registry to a stable SHA256 of the validated ID.
        return hashlib.sha256(session_id.encode("utf-8")).hexdigest()

    def _session(self, session_id: str, *, allow_pending: bool = False) -> Any:
        session = self.service._get_session(session_id)
        if session.pending is not None and not allow_pending:
            raise StudioServiceError(
                "conflict", "Accept or Discard pending Preview before uploading WAV"
            )
        return session

    def _discard(self, session_id: str, token: str) -> None:
        self._uploads.pop(token, None)
        try:
            self.stage.cancel(session_id=self._stage_session_id(session_id), token=token)
        except ContractError:
            pass

    def _expire(self) -> None:
        now = time.monotonic()
        for token, record in list(self._uploads.items()):
            if now - record.touched > _TTL_SECONDS:
                self._discard(record.session_id, token)

    def _record(self, session_id: str, token: str) -> _Upload:
        self._expire()
        if not isinstance(token, str) or not _TOKEN.fullmatch(token):
            raise StudioServiceError("invalid_request", "invalid WAV upload token")
        record = self._uploads.get(token)
        if record is None or record.session_id != session_id:
            raise StudioServiceError("invalid_request", "unknown or cross-session WAV upload")
        return record

    def _source(self, session_id: str, token: str) -> tuple[_Upload, Any]:
        record = self._record(session_id, token)
        session = self._session(session_id)
        if session.project.head_revision_id() != record.revision_id:
            self._discard(session_id, token)
            raise StudioServiceError("conflict", "accepted revision changed during WAV upload")
        record.touched = time.monotonic()
        return record, session

    def check_chunk_authority(self, session_id: str, token: str, *,
                              offset: int | None = None,
                              length: int | None = None,
                              chunk_sha256: str | None = None) -> None:
        """Fail closed before HTTP reads bytes; verify exact offset and bounds."""
        with self._lock:
            record, _ = self._source(session_id, token)
            if offset is None and length is None and chunk_sha256 is None:
                return  # Initial authorization before parsing the headers.
            if (type(offset) is not int or offset != record.received
                    or type(length) is not int or not 1 <= length <= MAX_CHUNK_BYTES
                    or record.received + length > record.expected_size
                    or not isinstance(chunk_sha256, str)
                    or not _SHA256.fullmatch(chunk_sha256)):
                self._discard(session_id, token)
                raise StudioServiceError(
                    "invalid_request", "staged chunk preflight offset/length/hash failed"
                )

    def begin(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._expire()
            session = self._session(session_id)
            if set(payload) != {"size_bytes", "sha256"}:
                raise StudioServiceError("invalid_request", "require size_bytes and sha256 only")
            size = payload["size_bytes"]
            digest = payload["sha256"]
            if (type(size) is not int or not 44 <= size <= MAX_STAGED_WAV_BYTES
                    or not isinstance(digest, str) or not _SHA256.fullmatch(digest)):
                raise StudioServiceError("invalid_request", "invalid size or SHA-256")
            if any(rec.session_id == session_id for rec in self._uploads.values()):
                raise StudioServiceError("conflict", "only one upload per Studio session")
            session.project.verify_integrity()
            try:
                token = self.stage.begin(
                    session_id=self._stage_session_id(session_id), expected_size=size, expected_sha256=digest
                )
            except Exception as exc:
                raise self.service._wrap_core_error(exc) from exc
            head = session.project.head_revision_id()
            self._uploads[token] = _Upload(
                session_id, head, digest, size, time.monotonic()
            )
            return {
                "upload_id": token,
                "next_offset": 0,
                "max_chunk_bytes": MAX_CHUNK_BYTES,
                "expected_size_bytes": size,
                "accepted_revision_id": head,
                "accepted_revision_unchanged": True,
                "classification": "PRIVATE_STAGED_WAV_NOT_AN_ASSET_OR_CLIP",
            }

    def append(self, session_id: str, token: str, *, offset: int,
               chunk: bytes, chunk_sha256: str) -> dict[str, Any]:
        with self._lock:
            record, _ = self._source(session_id, token)
            try:
                next_offset = self.stage.append(
                    session_id=self._stage_session_id(session_id), token=token, offset=offset,
                    chunk=chunk, chunk_sha256=chunk_sha256,
                )
            except Exception as exc:
                self._discard(session_id, token)
                raise self.service._wrap_core_error(exc) from exc
            record.touched = time.monotonic()
            record.received = next_offset
            return {
                "upload_id": token,
                "next_offset": next_offset,
                "accepted_revision_id": record.revision_id,
                "accepted_revision_unchanged": True,
            }

    def finish(self, session_id: str, token: str) -> dict[str, Any]:
        with self._lock:
            record, session = self._source(session_id, token)
            try:
                project = session.project
                project.verify_integrity()
                path = self.stage.verified_path(session_id=self._stage_session_id(session_id), token=token)
                descriptor = import_audio_asset_verified_path(
                    project, path, expected_sha256=record.expected_sha256
                )
                if project.head_revision_id() != record.revision_id:
                    raise StudioServiceError("conflict", "WAV import changed accepted HEAD")
                project.verify_integrity()
                return {
                    "classification": "IMMUTABLE_AUDIO_ASSET_NOT_ACCEPTED_CLIP",
                    "asset": descriptor,
                    "staged_upload_sha256": record.expected_sha256,
                    "staged_upload_size_bytes": record.expected_size,
                    "accepted_revision_id": record.revision_id,
                    "accepted_revision_unchanged": True,
                    "requires_separate_clip_preview_and_explicit_accept": True,
                }
            except Exception as exc:
                raise self.service._wrap_core_error(exc) from exc
            finally:
                self._discard(session_id, token)

    def cancel(self, session_id: str, token: str) -> dict[str, Any]:
        with self._lock:
            # Cancellation is allowed even when a creative Preview is pending.
            self._session(session_id, allow_pending=True)
            self._record(session_id, token)
            self._discard(session_id, token)
            return {"cancelled": True, "accepted_revision_unchanged": True}

    def close(self) -> None:
        with self._lock:
            self.stage.close()
            self._uploads.clear()
