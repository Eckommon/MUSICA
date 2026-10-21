"""ATCM-R3 additive HTTP bridge for the Browser native-audio Studio surface.

The validated pre-R3 Studio handler remains intact. This module subclasses it to add
only native-audio projection/Preview/Accept/audition routes and same-origin UI assets.
"""

from __future__ import annotations

from http import HTTPStatus
import socket
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit

from .audio_contracts import audio_material_from_blueprint
from .studio import StudioApplication, StudioService, StudioServiceError
from .studio_audio import StudioAudioSurface
from .studio_wav_uploads import StudioWavUploads
from .staged_wav import MAX_CHUNK_BYTES
from .studio_http import (
    DEFAULT_HOST,
    _browser_asset_bytes,
    _static_bytes,
    _status_for_error,
    make_handler as make_base_handler,
)


# A bounded direct binary transfer; never accept a client filesystem path.
MAX_WAV_IMPORT_BYTES = 16 * 1024 * 1024


def make_handler(application: StudioApplication):
    base_handler = make_base_handler(application)
    audio_surface = StudioAudioSurface(application.service)
    wav_uploads = StudioWavUploads(application.service)

    class R3StudioRequestHandler(base_handler):
        server_version = "MUSICAStudio/0.7"

        def _send_static(self, clean_path: str) -> bool:
            if clean_path == "/assets/app.js":
                data = _browser_asset_bytes("app.js") + b"\n" + _static_bytes("sha256_chunks.js") + b"\n" + _static_bytes("native_audio.js") + b"\n" + _static_bytes("production_guide.js")
                self._send_bytes(
                    HTTPStatus.OK,
                    "text/javascript; charset=utf-8",
                    data,
                    static_document=True,
                )
                return True
            if clean_path == "/assets/app.css":
                data = _browser_asset_bytes("app.css") + b"\n" + _static_bytes("native_audio.css") + b"\n" + _static_bytes("production_guide.css")
                self._send_bytes(
                    HTTPStatus.OK,
                    "text/css; charset=utf-8",
                    data,
                    static_document=True,
                )
                return True
            return super()._send_static(clean_path)

        def _route(self, method: str) -> None:
            clean_path = urlsplit(self.path).path
            parts = [part for part in clean_path.strip("/").split("/") if part]
            try:
                # G3B1B: localhost-first staged WAV intake. The browser sends
                # no filesystem path. Verify session/token/size BEFORE reading bytes.
                if (method == "POST" and len(parts) in {6, 7}
                        and parts[:2] == ["v0", "sessions"]
                        and parts[3:5] == ["audio", "stage"]):
                    # Always close staged-transfer connections after a response.
                    # If early validation fails, unread binary request data must
                    # never be interpreted as another HTTP/1.1 request.
                    self.close_connection = True
                    if self.headers.get("Transfer-Encoding"):
                        raise StudioServiceError(
                            "invalid_request", "Transfer-Encoding is forbidden for staged WAV"
                        )
                    session_id = parts[2]
                    if len(parts) == 6 and parts[5] == "start":
                        result = wav_uploads.begin(session_id, self._read_json())
                        self._send_json(HTTPStatus.OK, application._response("staged_wav_begin", result))
                        return
                    if len(parts) == 7:
                        token, operation = parts[5:7]
                        if operation == "chunk":
                            wav_uploads.check_chunk_authority(session_id, token)
                            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/octet-stream":
                                raise StudioServiceError(
                                    "invalid_request", "staged chunk must be application/octet-stream"
                                )
                            raw_length = self.headers.get("Content-Length", "")
                            raw_offset = self.headers.get("X-MUSICA-Chunk-Offset", "")
                            digest = self.headers.get("X-MUSICA-Chunk-SHA256", "")
                            if (not raw_length.isascii() or not raw_length.isdecimal()
                                    or not raw_offset.isascii() or not raw_offset.isdecimal()
                                    or not 1 <= int(raw_length) <= MAX_CHUNK_BYTES):
                                raise StudioServiceError(
                                    "invalid_request", "staged chunk needs bounded length/offset"
                                )
                            count, offset = int(raw_length), int(raw_offset)
                            try:
                                self.connection.settimeout(15.0)
                                data = self.rfile.read(count)
                            except (socket.timeout, ConnectionResetError, OSError):
                                try:
                                    wav_uploads.cancel(session_id, token)
                                except StudioServiceError:
                                    pass
                                self.close_connection = True
                                raise StudioServiceError(
                                    "invalid_request", "staged chunk connection failed"
                                )
                            if len(data) != count:
                                try:
                                    wav_uploads.cancel(session_id, token)
                                except StudioServiceError:
                                    pass
                                self.close_connection = True
                                raise StudioServiceError(
                                    "invalid_request", "staged WAV chunk truncated"
                                )
                            result = wav_uploads.append(
                                session_id, token, offset=offset, chunk=data,
                                chunk_sha256=digest,
                            )
                        elif operation in {"finish", "cancel"}:
                            if self._read_json():
                                raise StudioServiceError(
                                    "invalid_request", "staged finish/cancel must use empty JSON"
                                )
                            result = (wav_uploads.finish(session_id, token)
                                      if operation == "finish"
                                      else wav_uploads.cancel(session_id, token))
                        else:
                            raise StudioServiceError(
                                "not_found", "unknown staged WAV action"
                            )
                        self._send_json(
                            HTTPStatus.OK,
                            application._response("staged_wav_" + operation, result),
                        )
                        return

                if (
                    method == "POST"
                    and len(parts) == 5
                    and parts[:2] == ["v0", "sessions"]
                    and parts[3:] == ["audio", "import-wav"]
                ):
                    # Reject unknown sessions and concurrent Previews before reading
                    # any untrusted binary bytes; no creative revision is accepted.
                    application.service._get_session(parts[2])
                    if self.headers.get("Transfer-Encoding"):
                        raise StudioServiceError(
                            "invalid_request", "chunked WAV import is unsupported"
                        )
                    content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
                    if content_type != "audio/wav":
                        raise StudioServiceError(
                            "invalid_request", "WAV upload Content-Type must be audio/wav"
                        )
                    raw_length = self.headers.get("Content-Length")
                    if raw_length is None:
                        raise StudioServiceError(
                            "invalid_request", "WAV import requires Content-Length"
                        )
                    try:
                        size = int(raw_length)
                    except ValueError as exc:
                        raise StudioServiceError(
                            "invalid_request", "invalid WAV Content-Length"
                        ) from exc
                    if size < 44 or size > MAX_WAV_IMPORT_BYTES:
                        raise StudioServiceError(
                            "invalid_request", "WAV upload must be between 44 bytes and 16 MiB"
                        )
                    raw_wav = self.rfile.read(size)
                    if len(raw_wav) != size:
                        raise StudioServiceError(
                            "invalid_request", "WAV upload body was truncated"
                        )
                    data = audio_surface.import_wav_resource(parts[2], raw_wav)
                    self._send_json(
                        HTTPStatus.OK, application._response("import_native_wav_resource", data)
                    )
                    return

                if (
                    method == "GET"
                    and len(parts) == 4
                    and parts[:2] == ["v0", "sessions"]
                    and parts[3] == "audio"
                ):
                    # Native audio is an additive capability. A valid Studio session whose
                    # accepted Blueprint has no native-audio material is therefore a truthful
                    # unavailable projection, not an HTTP error. This keeps pre-R3 Browser
                    # surfaces (including accepted-revision Compare) clean while preserving
                    # fail-closed behavior for unknown sessions and actual integrity errors.
                    session = application.service._get_session(parts[2])
                    branch = session.project.current_branch()
                    revision_id = session.project.head_revision_id(branch)
                    accepted = session.project.read_revision(revision_id)
                    if audio_material_from_blueprint(accepted) is None:
                        data = None
                    else:
                        data = audio_surface.audio_view(parts[2])
                    self._send_json(HTTPStatus.OK, application._response("native_audio_view", data))
                    return

                if (
                    method == "GET"
                    and len(parts) == 5
                    and parts[:2] == ["v0", "sessions"]
                    and parts[3] == "audio"
                    and parts[4] in {"accepted.wav", "preview.wav"}
                ):
                    source_kind = "accepted" if parts[4] == "accepted.wav" else "preview"
                    rendered = audio_surface.audition(parts[2], source_kind=source_kind)
                    self._send_bytes(HTTPStatus.OK, "audio/wav", rendered.wav_bytes)
                    return

                if (
                    method == "POST"
                    and len(parts) == 6
                    and parts[:2] == ["v0", "sessions"]
                    and parts[3:5] == ["preview", "audio"]
                    and parts[5] in {"arrangement", "mixer"}
                ):
                    body = self._read_json()
                    candidate = body.get("candidate")
                    if not isinstance(candidate, dict):
                        raise StudioServiceError(
                            "invalid_request", "native-audio Preview requires candidate object"
                        )
                    data = audio_surface.preview_audio_edit(
                        parts[2], candidate=candidate, candidate_kind=parts[5]
                    )
                    self._send_json(
                        HTTPStatus.OK,
                        application._response("preview_native_audio_edit", data),
                    )
                    return

                if (
                    method == "POST"
                    and len(parts) == 5
                    and parts[:2] == ["v0", "sessions"]
                    and parts[3:] == ["audio", "accept"]
                ):
                    self._read_json()
                    data = audio_surface.accept_audio_preview(parts[2])
                    self._send_json(
                        HTTPStatus.OK,
                        application._response("accept_native_audio_preview", data),
                    )
                    return

                if (
                    method == "POST"
                    and len(parts) == 5
                    and parts[:2] == ["v0", "sessions"]
                    and parts[3:] == ["audio", "discard"]
                ):
                    self._read_json()
                    data = audio_surface.discard_audio_preview(parts[2])
                    self._send_json(
                        HTTPStatus.OK,
                        application._response("discard_native_audio_preview", data),
                    )
                    return

                return super()._route(method)
            except StudioServiceError as exc:
                self._send_json(_status_for_error(exc), {"ok": False, "error": exc.as_dict()})
            except Exception as exc:
                safe = StudioServiceError(
                    "internal_error", f"unhandled Studio R3 HTTP error: {type(exc).__name__}"
                )
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"ok": False, "error": safe.as_dict()},
                )

    return R3StudioRequestHandler


def create_local_server(
    service: StudioService,
    *,
    host: str = DEFAULT_HOST,
    port: int = 0,
) -> ThreadingHTTPServer:
    """Create the additive R3 local Studio server without widening loopback authority."""
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise StudioServiceError(
            "invalid_request", "MUSICA Studio HTTP server may bind only to loopback"
        )
    if not 0 <= int(port) <= 65535:
        raise StudioServiceError("invalid_request", "invalid Studio HTTP port")
    application = StudioApplication(service)
    return ThreadingHTTPServer((host, int(port)), make_handler(application))
