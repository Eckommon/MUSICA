"""G3B2C-R1: bounded HTTP Range transport for accepted derived WAV only.

The client selects a session-bound route, never a filesystem path. An
accepted revision uses a bounded private WAV cache keyed by exact trusted
plan and source CAS, allowing multiple byte Ranges without a fresh render.
HTTP still copies at most 1MiB per write. Preview/Accept is untouched.
"""
from __future__ import annotations

import re
import threading
from http import HTTPStatus
from pathlib import Path
from typing import Any

from .contracts import ContractError
from .routing_contracts import routing_material_from_blueprint
from .studio import StudioService, StudioServiceError
from .studio_audio import _mix_rate
from .studio_wav_cache import AcceptedWavFileCache

HTTP_WRITE_CHUNK_BYTES = 1 << 20
_RANGE = re.compile(r"bytes=(\d*)-(\d*)\Z", re.ASCII)


def wav_byte_range(value: str | None, size: int) -> tuple[int, int, int]:
    """Return (HTTP status, inclusive start, inclusive end), one range only.

    Invalid, multiple, excessive and unsatisfiable Range values always fail 416.
    Ignored Range is NOT accepted to prevent partial requests silently returning
    unexpected full data.
    """
    if not isinstance(size, int) or size <= 0:
        raise ValueError("WAV has no bytes")
    if value is None:
        return int(HTTPStatus.OK), 0, size - 1
    if len(value) > 96 or _RANGE.fullmatch(value) is None:
        raise ValueError("invalid single WAV byte Range")
    m = _RANGE.fullmatch(value)
    assert m is not None
    first, last = m.groups()
    if not first and not last:
        raise ValueError("empty byte Range")
    if first:
        start = int(first)
        end = min(int(last), size - 1) if last else size - 1
        if start >= size or end < start:
            raise ValueError("unsatisfiable byte Range")
    else:
        suffix = int(last)
        if suffix <= 0:
            raise ValueError("zero-length suffix Range")
        start = max(0, size - suffix)
        end = size - 1
    return int(HTTPStatus.PARTIAL_CONTENT), start, end


class AcceptedWavRangeHTTP:
    """Two-server-transfer and one-per-session accepted-WAV file boundary."""

    def __init__(self, service: StudioService) -> None:
        self._service = service
        self._guard = threading.Lock()
        self._available = threading.Condition(self._guard)
        self._busy: set[str] = set()
        # Prevent a Browser's metadata seek + immediate user download from
        # creating an unbounded number of server-side blocked request threads.
        self._waiting: dict[str, int] = {}
        self._global_limit = threading.BoundedSemaphore(2)
        self._cache = AcceptedWavFileCache(service.workspace)

    def _enter(self, session_id: str) -> None:
        # 180s accepted WAV creation can take materially longer than the
        # previous 3s cleanup grace. Chromium often requests <audio> metadata
        # and a user-clicked full download simultaneously on Project reopen.
        # Admit one renderer/stream per session, but *queue* at most two same-
        # session requests for up to 120s. Waiters do NOT occupy the separate
        # global two-stream semaphore while blocked.
        with self._available:
            if session_id in self._busy:
                waiting = self._waiting.get(session_id, 0)
                if waiting >= 2:
                    raise StudioServiceError(
                        "conflict", "too many queued accepted WAV requests for session"
                    )
                self._waiting[session_id] = waiting + 1
                try:
                    available = self._available.wait_for(
                        lambda: session_id not in self._busy, timeout=120.0
                    )
                    if not available:
                        raise StudioServiceError(
                            "conflict", "accepted WAV renderer still busy for session"
                        )
                finally:
                    remaining = self._waiting[session_id] - 1
                    if remaining:
                        self._waiting[session_id] = remaining
                    else:
                        self._waiting.pop(session_id, None)
            self._busy.add(session_id)
        if not self._global_limit.acquire(blocking=False):
            with self._available:
                self._busy.remove(session_id)
                self._available.notify_all()
            raise StudioServiceError("conflict", "too many derived WAV HTTP streams")

    def _exit(self, session_id: str) -> None:
        try:
            with self._available:
                self._busy.remove(session_id)
                self._available.notify_all()
        finally:
            self._global_limit.release()

    def serve(
        self,
        handler: Any,
        session_id: str,
        *,
        range_headers: list[str],
        attachment: bool,
    ) -> None:
        """Lease accepted HEAD, send bounded bytes, expire derived output on TTL.

        No exceptions after response headers are emitted can be turned into a
        second response. We close the connection if the peer disconnects.
        """
        self._enter(session_id)
        output: Path | None = None
        headers_sent = False
        try:
            session = self._service._get_session(session_id)
            project = session.project
            revision_id = project.head_revision_id(project.current_branch())
            blueprint = project.read_revision(revision_id)
            rate = _mix_rate(project, blueprint)
            material = routing_material_from_blueprint(blueprint)
            assert material is not None
            has_routing = bool(material["nodes"] or material["track_outputs"] or material["sends"])
            result = self._cache.acquire(
                session_id, project, revision_id,
                mix_sample_rate_hz=rate, routed=has_routing
            )
            output = result.wav_path
            if project.head_revision_id(project.current_branch()) != revision_id:
                raise StudioServiceError("conflict", "accepted HEAD changed before WAV response")
            size = result.wav_size_bytes
            if len(range_headers) > 1:
                requested = "__invalid_multiple__"
            else:
                requested = range_headers[0] if range_headers else None
            try:
                status, start, end = wav_byte_range(requested, size)
            except ValueError:
                handler.send_response(int(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE))
                handler.send_header("Content-Range", f"bytes */{size}")
                handler.send_header("Content-Length", "0")
                handler.send_header("Cache-Control", "no-store")
                handler.send_header("Accept-Ranges", "bytes")
                handler.send_header("X-Content-Type-Options", "nosniff")
                handler.end_headers()
                headers_sent = True
                return
            with output.open("rb") as src:
                handler.send_response(status)
                handler.send_header("Content-Type", "audio/wav")
                handler.send_header("Content-Length", str(end - start + 1))
                handler.send_header("Accept-Ranges", "bytes")
                handler.send_header("Cache-Control", "no-store")
                handler.send_header("X-Content-Type-Options", "nosniff")
                handler.send_header("Referrer-Policy", "no-referrer")
                handler.send_header("X-Frame-Options", "DENY")
                handler.send_header("Cross-Origin-Resource-Policy", "same-origin")
                handler.send_header("ETag", '"' + result.wav_sha256 + '"')
                if status == int(HTTPStatus.PARTIAL_CONTENT):
                    handler.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                if attachment:
                    handler.send_header("Content-Disposition", 'attachment; filename="musica-accepted.wav"')
                handler.end_headers()
                headers_sent = True
                src.seek(start)
                remaining = end - start + 1
                while remaining:
                    if project.head_revision_id(project.current_branch()) != revision_id:
                        handler.close_connection = True
                        return
                    block = src.read(min(HTTP_WRITE_CHUNK_BYTES, remaining))
                    if not block:
                        handler.close_connection = True
                        return
                    handler.wfile.write(block)
                    remaining -= len(block)
        except (BrokenPipeError, ConnectionResetError):
            handler.close_connection = True
        except ContractError as exc:
            if headers_sent:
                handler.close_connection = True
                return
            # A user may explicitly Accept a new revision while Chromium's
            # prior 180s metadata request is rendering. This is a stale
            # accepted-HEAD conflict, never an internal server failure and
            # never permission to serve an obsolete derived WAV.
            if "accepted HEAD changed" in str(exc):
                raise StudioServiceError(
                    "conflict", "accepted HEAD changed during WAV streaming"
                ) from exc
            raise
        except BaseException:
            if headers_sent:
                handler.close_connection = True
                return
            raise
        finally:
            # Cached derived audio remains private and noncanonical until idle
            # TTL eviction; session lease ends regardless of peer disconnect.
            if output is not None:
                self._cache.release(session_id)
            self._exit(session_id)
