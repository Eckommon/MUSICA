"""G3B-0: bounded, opaque, local staged WAV-byte intake.

This is deliberately NOT a creative project edit or finalized CAS import.
No user-controlled path is accepted. Only a later G3B phase may expose a
Studio endpoint/finalize asset audit, after project-integrity integration.
"""
from __future__ import annotations

import hashlib
import os
import re
import secrets
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

from .contracts import ContractError

MAX_STAGED_WAV_BYTES = 64 * 1024 * 1024
MAX_CHUNK_BYTES = 1024 * 1024
MAX_ACTIVE_TRANSFERS = 2
_SHA256 = re.compile(r"[a-f0-9]{64}\Z")


@dataclass
class _Transfer:
    session_id: str
    expected_size: int
    expected_sha256: str
    path: Path
    received: int = 0


class BoundedWavStaging:
    """Thread-safe sequential intake, isolated from canonical project HEAD.

    Each chunk uses an exact next offset. A missing, incorrect, duplicated,
    oversized or corrupt chunk rejects without changing the staged file.
    The caller must explicitly discard or finalize; finalization returns
    only a read-only verified *private* path to trusted application code.
    """

    def __init__(self, private_directory: str | Path) -> None:
        self._root = Path(private_directory).resolve()
        self._root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._lock = threading.RLock()
        self._transfers: dict[str, _Transfer] = {}

    @staticmethod
    def _check_session(session_id: str) -> None:
        if not isinstance(session_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,96}", session_id):
            raise ContractError("invalid opaque upload session identity")

    def begin(self, *, session_id: str, expected_size: int, expected_sha256: str) -> str:
        self._check_session(session_id)
        if type(expected_size) is not int or not 44 <= expected_size <= MAX_STAGED_WAV_BYTES:
            raise ContractError("staged WAV length out of bounds")
        if not isinstance(expected_sha256, str) or not _SHA256.fullmatch(expected_sha256):
            raise ContractError("invalid staged WAV digest")
        with self._lock:
            if len(self._transfers) >= MAX_ACTIVE_TRANSFERS:
                raise ContractError("too many concurrent WAV uploads")
            handle = tempfile.NamedTemporaryFile(dir=self._root, prefix="wav-", delete=False)
            try:
                os.chmod(handle.name, 0o600)
                path = Path(handle.name)
            finally:
                handle.close()
            token = secrets.token_urlsafe(32)
            self._transfers[token] = _Transfer(
                session_id, expected_size, expected_sha256, path
            )
            return token

    def _get(self, session_id: str, token: str) -> _Transfer:
        self._check_session(session_id)
        if not isinstance(token, str) or token not in self._transfers:
            raise ContractError("unknown staged WAV transfer")
        transfer = self._transfers[token]
        if transfer.session_id != session_id:
            raise ContractError("staged WAV session mismatch")
        return transfer

    def append(self, *, session_id: str, token: str, offset: int,
               chunk: bytes, chunk_sha256: str) -> int:
        with self._lock:
            transfer = self._get(session_id, token)
            if type(offset) is not int or offset != transfer.received:
                raise ContractError("staged WAV non-sequential byte offset")
            if not isinstance(chunk, bytes) or not 1 <= len(chunk) <= MAX_CHUNK_BYTES:
                raise ContractError("staged WAV chunk size out of bounds")
            if transfer.received + len(chunk) > transfer.expected_size:
                raise ContractError("staged WAV exceeds declared source size")
            if not isinstance(chunk_sha256, str) or hashlib.sha256(chunk).hexdigest() != chunk_sha256:
                raise ContractError("staged WAV chunk digest mismatch")
            # Existing files are always private tempfiles made by begin().
            # Re-check file length to detect unintended on-disk tampering.
            if transfer.path.stat().st_size != transfer.received:
                raise ContractError("staged WAV private file size mismatch")
            with transfer.path.open("ab") as stream:
                stream.write(chunk)
                stream.flush()
            transfer.received += len(chunk)
            return transfer.received

    def verified_path(self, *, session_id: str, token: str) -> Path:
        with self._lock:
            transfer = self._get(session_id, token)
            if transfer.received != transfer.expected_size:
                raise ContractError("staged WAV upload incomplete")
            h = hashlib.sha256()
            with transfer.path.open("rb") as stream:
                while block := stream.read(MAX_CHUNK_BYTES):
                    h.update(block)
            if h.hexdigest() != transfer.expected_sha256:
                raise ContractError("staged WAV complete digest mismatch")
            return transfer.path

    def cancel(self, *, session_id: str, token: str) -> None:
        with self._lock:
            transfer = self._get(session_id, token)
            transfer.path.unlink(missing_ok=True)
            del self._transfers[token]

    def close(self) -> None:
        """Application-shutdown cleanup; no canonical audio assets mutated."""
        with self._lock:
            for transfer in self._transfers.values():
                transfer.path.unlink(missing_ok=True)
            self._transfers.clear()
