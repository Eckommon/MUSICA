"""G3B2C-R1: bounded HTTP Range transport for accepted derived WAV only.

The client selects a session-bound route, never a filesystem path. A fresh
accepted revision is lowered and rendered by G3B2A/B fixed-window engines
to a private derived temporary WAV. HTTP copies at most 1MiB per write.
This stage deliberately does NOT change Preview/Accept or legacy paths.
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
from .streamed_native_mixer import render_native_mix_streamed
from .streamed_routed_mixer import render_routed_mix_streamed

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
        self._global_limit = threading.BoundedSemaphore(2)

    def _enter(self, session_id: str) -> None:
        if not self._global_limit.acquire(blocking=False):
            raise StudioServiceError("conflict", "too many derived WAV HTTP streams")
        try:
            with self._available:
                # HTTP clients may have received the previous Content-Length
                # while its server thread is still in finally/cleanup. Wait a
                # small bounded grace rather than returning a spurious 409.
                # This does NOT permit overlapping renders for one session.
                available = self._available.wait_for(
                    lambda: session_id not in self._busy, timeout=3.0
                )
                if not available:
                    raise StudioServiceError(
                        "conflict", "accepted WAV stream already active for session"
                    )
                self._busy.add(session_id)
        except BaseException:
            self._global_limit.release()
            raise

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
        """Render accepted HEAD, send bounded bytes, delete temporary output.

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
            result = (
                render_routed_mix_streamed(project, revision_id, mix_sample_rate_hz=rate)
                if has_routing
                else render_native_mix_streamed(project, revision_id, mix_sample_rate_hz=rate)
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
        except BaseException:
            if headers_sent:
                handler.close_connection = True
                return
            raise
        finally:
            if output is not None:
                output.unlink(missing_ok=True)
            self._exit(session_id)
