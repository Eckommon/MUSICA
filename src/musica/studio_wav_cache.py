"""G3B2C-R2: accepted-head keyed, bounded, noncanonical WAV Range cache.

Only authoritative current accepted Project revision + trusted mix plan can
populate this cache. A source CAS digest, WAV output digest, and plan identity
are rechecked before reusing an existing derived audio file. One accepted WAV
is computed per session+revision, instead of rerendering for every seek.

This is NOT a user Preview/Accept authority; no creative state is changed.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .audio_assets import _file_sha256
from .contracts import ContractError
from .native_mixer import build_native_mix_plan
from .routed_mixer import build_routed_mix_plan
from .studio import StudioServiceError
from .streamed_native_mixer import render_native_mix_streamed
from .streamed_routed_mixer import render_routed_mix_streamed

CACHE_IDLE_TTL_SECONDS = 300.0
MAX_CACHE_FILES = 2
MAX_CACHE_FILE_BYTES = 256 * 1024 * 1024
MAX_CACHE_TOTAL_BYTES = MAX_CACHE_FILES * MAX_CACHE_FILE_BYTES


@dataclass(frozen=True)
class CachedAcceptedWav:
    wav_path: Path
    wav_sha256: str
    wav_size_bytes: int
    identity: str
    plan_sha256: str
    source_object_sha256: tuple[str, ...]


@dataclass
class _CacheEntry:
    result: CachedAcceptedWav
    source_objects: tuple[tuple[Path, str], ...]
    last_used: float


def _source_objects(project: Any, plan: dict[str, Any], *, routed: bool):
    tracks = plan["native_tracks"] if routed else plan["tracks"]
    unique = {}
    for track in tracks:
        for clip in track["clips"]:
            digest = str(clip["object_sha256"])
            if digest not in unique:
                path = project._object_path(digest)
                unique[digest] = path
    return tuple((unique[k], k) for k in sorted(unique))


class AcceptedWavFileCache:
    """Two files max, 5-minute idle TTL, per-service safe crash cleanup."""

    def __init__(self, workspace: str | Path) -> None:
        self.root = Path(workspace) / ".derived-accepted-wav-cache-g3b2c-r2"
        if self.root.is_symlink():
            raise ContractError("derived WAV cache root must not be a symlink")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._lock = threading.RLock()
        self._entries: dict[str, _CacheEntry] = {}
        self._leased: set[str] = set()
        self._renders = 0
        # Fresh service owns no prior leases: only our own naming namespace is
        # swept. An unexpected file is not opened or traversed.
        for stale in self.root.glob("wav-*.wav"):
            if stale.is_symlink() or stale.is_file():
                stale.unlink(missing_ok=True)

    @property
    def render_count(self) -> int:
        with self._lock:
            return self._renders

    def _evict(self, session_id: str) -> None:
        entry = self._entries.pop(session_id, None)
        if entry is not None:
            entry.result.wav_path.unlink(missing_ok=True)

    def _prune(self) -> None:
        now = time.monotonic()
        for sid, entry in list(self._entries.items()):
            if sid not in self._leased and now - entry.last_used > CACHE_IDLE_TTL_SECONDS:
                self._evict(sid)

    def release(self, session_id: str) -> None:
        with self._lock:
            self._leased.discard(session_id)
            if session_id in self._entries:
                self._entries[session_id].last_used = time.monotonic()
            self._prune()

    def clear_session(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._leased:
                raise StudioServiceError("conflict", "cannot evict in-flight WAV stream")
            self._evict(session_id)

    def clear_all_idle(self) -> None:
        with self._lock:
            for sid in list(self._entries):
                if sid not in self._leased:
                    self._evict(sid)

    def _validate_cached(self, entry: _CacheEntry) -> bool:
        result = entry.result
        output = result.wav_path
        if (output.is_symlink() or not output.is_file()
                or output.parent != self.root
                or output.stat().st_size != result.wav_size_bytes):
            return False
        for path, expected in entry.source_objects:
            if path.is_symlink() or not path.is_file() or _file_sha256(path) != expected:
                raise ContractError("accepted source CAS mutated since WAV cache render")
        return _file_sha256(output) == result.wav_sha256

    def acquire(
        self,
        session_id: str,
        project: Any,
        revision_id: str,
        *,
        mix_sample_rate_hz: int,
        routed: bool,
    ) -> CachedAcceptedWav:
        if project.head_revision_id(project.current_branch()) != revision_id:
            raise StudioServiceError("conflict", "accepted HEAD changed before cache validation")
        plan = (
            build_routed_mix_plan(project, revision_id,
                                  mix_sample_rate_hz=mix_sample_rate_hz)
            if routed else
            build_native_mix_plan(project, revision_id,
                                  mix_sample_rate_hz=mix_sample_rate_hz)
        )
        key = "routed_mix_plan_sha256" if routed else "mix_plan_sha256"
        plan_sha = str(plan[key])
        sources = _source_objects(project, plan, routed=routed)
        expected = hashlib.sha256(repr((
            session_id, str(project.root.resolve()), project.current_branch(),
            revision_id, mix_sample_rate_hz, routed, plan_sha,
            tuple(sha for _, sha in sources),
        )).encode("utf-8")).hexdigest()

        with self._lock:
            self._prune()
            if session_id in self._leased:
                raise StudioServiceError("conflict", "WAV cache session already leased")
            entry = self._entries.get(session_id)
            if entry is not None:
                if entry.result.identity != expected:
                    self._evict(session_id)
                elif self._validate_cached(entry):
                    self._leased.add(session_id)
                    entry.last_used = time.monotonic()
                    return entry.result
                else:
                    self._evict(session_id)
            # Reserve this exact session's lease before costly offline render.
            self._leased.add(session_id)

        original: Path | None = None
        cached_file: Path | None = None
        try:
            rendered = (
                render_routed_mix_streamed(
                    project, revision_id, mix_sample_rate_hz=mix_sample_rate_hz)
                if routed else
                render_native_mix_streamed(
                    project, revision_id, mix_sample_rate_hz=mix_sample_rate_hz)
            )
            original = rendered.wav_path
            if rendered.wav_size_bytes > MAX_CACHE_FILE_BYTES:
                raise ContractError("derived WAV exceeds cache maximum file size")
            if project.head_revision_id(project.current_branch()) != revision_id:
                raise StudioServiceError("conflict", "accepted HEAD changed while WAV rendered")
            for path, digest in sources:
                if path.is_symlink() or not path.is_file() or _file_sha256(path) != digest:
                    raise ContractError("accepted source CAS mutated during WAV cache render")
            cached_file = self.root / ("wav-" + secrets.token_hex(16) + ".wav")
            os.replace(original, cached_file)
            original = None
            result = CachedAcceptedWav(
                cached_file, rendered.wav_sha256, rendered.wav_size_bytes,
                expected, plan_sha, tuple(sha for _, sha in sources),
            )
            with self._lock:
                self._prune()
                if project.head_revision_id(project.current_branch()) != revision_id:
                    raise StudioServiceError("conflict", "accepted HEAD changed during cache publish")
                for sid in list(self._entries):
                    if sid not in self._leased and len(self._entries) >= MAX_CACHE_FILES:
                        self._evict(sid)
                if len(self._entries) >= MAX_CACHE_FILES:
                    raise StudioServiceError("conflict", "derived WAV cache quota exhausted")
                self._entries[session_id] = _CacheEntry(result, sources, time.monotonic())
                self._renders += 1
                cached_file = None
                return result
        except BaseException:
            if original is not None:
                original.unlink(missing_ok=True)
            if cached_file is not None:
                cached_file.unlink(missing_ok=True)
            with self._lock:
                self._leased.discard(session_id)
            raise
