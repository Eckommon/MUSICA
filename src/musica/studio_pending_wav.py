"""G3B2C-R4: bounded noncanonical PCM renderer for one authoritative Pending Preview.

A trusted Pending Preview may have a candidate revision not persisted as a
canonical Project revision. The temporary read-only overlay advertises this
candidate to the pre-existing fixed-window renderers without writing any
branch ref. A separate watchdog always checks the *real* accepted parent
revision and pending object identity at each render block and after output.
"""
from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
import threading
from pathlib import Path
from typing import Any

from .audio_edit import blueprint_sha256
from .contracts import ContractError
from .routing_contracts import routing_material_from_blueprint
from .studio import StudioService, StudioServiceError
from .studio_audio import _BlueprintProjectProxy, _mix_rate
from .streamed_native_mixer import render_native_mix_streamed
from .streamed_routed_mixer import render_routed_mix_streamed


_SUPPORTED_PENDING_KINDS = frozenset({
    "native_audio_edit", "routing_edit", "automation_edit",
})


class _ExactPendingCandidateProject(_BlueprintProjectProxy):
    """Ephemeral source-bound candidate read overlay; no disk revision write."""

    def __init__(self, real_project: Any, candidate: dict[str, Any]) -> None:
        super().__init__(real_project, candidate)
        self._pending_revision = str(candidate["project"]["revision_id"])

    def head_revision_id(self, branch: str | None = None) -> str:
        return self._pending_revision


@dataclass(frozen=True)
class PendingStreamedWav:
    wav_path: Path
    wav_sha256: str
    wav_size_bytes: int
    candidate_revision_id: str
    preview_id: str
    candidate_blueprint_sha256: str
    accepted_parent_revision_id: str
    routed: bool
    rendered_audio_is_canonical: bool = False


def render_pending_preview_streamed(
    service: StudioService,
    session_id: str,
    *,
    preview_id: str,
) -> PendingStreamedWav:
    """Safely derive a WAV from *one* already validated Studio candidate.

    Do not accept or recreate an arbitrary candidate provided by HTTP. The
    only source is the existing, stored trusted Pending Preview. This stage
    produces a private derived WAV and the caller must unlink it after use.
    """
    session = service._get_session(session_id)
    real = session.project
    pending = session.pending
    if pending is None or str(pending.descriptor.get("preview_id")) != preview_id:
        raise StudioServiceError(
            "not_found", "no matching source-bound pending Preview"
        )
    descriptor = pending.descriptor
    if descriptor.get("kind") not in _SUPPORTED_PENDING_KINDS:
        raise StudioServiceError(
            "invalid_request", "pending candidate is not a native/routed audio Preview"
        )
    parent = str(descriptor.get("parent_revision_id"))
    branch = str(descriptor.get("branch"))
    candidate_revision = str(descriptor.get("candidate_revision_id"))
    if real.current_branch() != branch or real.head_revision_id(branch) != parent:
        raise StudioServiceError("conflict", "pending Preview parent accepted HEAD is stale")
    candidate = pending.candidate
    if str(candidate["project"]["revision_id"]) != candidate_revision:
        raise StudioServiceError("integrity_error", "pending revision identity mismatch")
    digest = blueprint_sha256(candidate)
    if not digest or len(digest) != 64:
        raise StudioServiceError("integrity_error", "invalid pending blueprint fingerprint")
    overlay = _ExactPendingCandidateProject(real, candidate)
    source_kind = descriptor["kind"]
    routing = routing_material_from_blueprint(candidate)
    if routing is None:
        raise StudioServiceError("integrity_error", "pending routing material is missing")
    routed = bool(routing["nodes"] or routing["track_outputs"] or routing["sends"])
    if source_kind in {"routing_edit", "automation_edit"} and not routed:
        raise StudioServiceError(
            "invalid_request", "pending routing/automation candidate requires a valid routing graph"
        )
    rate = _mix_rate(overlay, candidate)

    def stale() -> bool:
        return (
            session.pending is not pending or
            real.current_branch() != branch or
            real.head_revision_id(branch) != parent or
            str(pending.descriptor.get("preview_id")) != preview_id or
            blueprint_sha256(pending.candidate) != digest
        )

    if stale():
        raise StudioServiceError("conflict", "pending Preview changed before render")
    output = None
    try:
        output = (
            render_routed_mix_streamed(
                overlay, candidate_revision, mix_sample_rate_hz=rate,
                cancelled=stale,
            ) if routed else render_native_mix_streamed(
                overlay, candidate_revision, mix_sample_rate_hz=rate,
                cancelled=stale,
            )
        )
        if stale():
            raise StudioServiceError("conflict", "pending Preview changed during render")
        return PendingStreamedWav(
            wav_path=output.wav_path,
            wav_sha256=output.wav_sha256,
            wav_size_bytes=output.wav_size_bytes,
            candidate_revision_id=candidate_revision,
            preview_id=preview_id,
            candidate_blueprint_sha256=digest,
            accepted_parent_revision_id=parent,
            routed=routed,
        )
    except BaseException:
        if output is not None:
            output.wav_path.unlink(missing_ok=True)
        raise


class PendingWavRangeHTTP:
    """A bounded local-only transport for a single trusted active Preview.

    This first increment purposely regenerates for a subsequent Range; unlike
    accepted WAV cache it never reuses a Preview after discard/replacement.
    """

    def __init__(self, service: StudioService) -> None:
        self._service = service
        self._global = threading.BoundedSemaphore(2)
        self._guard = threading.Lock()
        self._available = threading.Condition(self._guard)
        self._busy: set[str] = set()

    def serve(
        self,
        handler: Any,
        session_id: str,
        *,
        preview_id: str,
        range_headers: list[str],
    ) -> None:
        from .studio_wav_http_range import wav_byte_range, HTTP_WRITE_CHUNK_BYTES

        # Reject invalid or stale IDs before lease/cleanup status can mask 404.
        preflight = self._service._get_session(session_id).pending
        if preflight is None or preflight.descriptor.get("preview_id") != preview_id:
            raise StudioServiceError("not_found", "pending Preview ID is no longer active")
        if not self._global.acquire(blocking=False):
            raise StudioServiceError("conflict", "too many active Preview WAV streams")
        admitted = False
        output: Path | None = None
        headers_sent = False
        try:
            with self._available:
                # Finished Content-Length can precede prior request's cleanup.
                # Bounded wait preserves one render/session with no false 409.
                available = self._available.wait_for(
                    lambda: session_id not in self._busy, timeout=3.0
                )
                if not available:
                    raise StudioServiceError("conflict", "Preview WAV stream already active")
                self._busy.add(session_id)
                admitted = True
            pending = self._service._get_session(session_id).pending
            if pending is not preflight or pending.descriptor.get("preview_id") != preview_id:
                raise StudioServiceError("not_found", "pending Preview ID is no longer active")
            rendered = render_pending_preview_streamed(
                self._service, session_id, preview_id=preview_id
            )
            output = rendered.wav_path
            size = rendered.wav_size_bytes
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
                handler.send_header("Accept-Ranges", "bytes")
                handler.send_header("Cache-Control", "no-store")
                handler.send_header("X-Content-Type-Options", "nosniff")
                handler.end_headers()
                headers_sent = True
                return
            if not self._still_current(session_id, pending, rendered):
                raise StudioServiceError("conflict", "pending Preview changed before HTTP response")
            with output.open("rb") as stream:
                stream.seek(start)
                handler.send_response(status)
                handler.send_header("Content-Type", "audio/wav")
                handler.send_header("Content-Length", str(end - start + 1))
                handler.send_header("Cache-Control", "no-store")
                handler.send_header("Accept-Ranges", "bytes")
                handler.send_header("X-Content-Type-Options", "nosniff")
                handler.send_header("Cross-Origin-Resource-Policy", "same-origin")
                handler.send_header("ETag", '"' + rendered.wav_sha256 + '"')
                handler.send_header("X-MUSICA-Pending-Preview-ID", preview_id)
                if status == int(HTTPStatus.PARTIAL_CONTENT):
                    handler.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                handler.end_headers()
                headers_sent = True
                remaining = end - start + 1
                while remaining:
                    if not self._still_current(session_id, pending, rendered):
                        handler.close_connection = True
                        return
                    data = stream.read(min(HTTP_WRITE_CHUNK_BYTES, remaining))
                    if not data:
                        handler.close_connection = True
                        return
                    handler.wfile.write(data)
                    remaining -= len(data)
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
            if admitted:
                with self._available:
                    self._busy.remove(session_id)
                    self._available.notify_all()
            self._global.release()

    def _still_current(
        self, session_id: str, pending: Any, rendered: PendingStreamedWav
    ) -> bool:
        try:
            session = self._service._get_session(session_id)
            return (
                session.pending is pending and
                session.project.head_revision_id() ==
                rendered.accepted_parent_revision_id and
                pending.descriptor.get("preview_id") == rendered.preview_id and
                blueprint_sha256(pending.candidate) ==
                rendered.candidate_blueprint_sha256
            )
        except (StudioServiceError, ContractError, KeyError):
            return False
