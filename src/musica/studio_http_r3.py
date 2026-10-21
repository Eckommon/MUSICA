"""ATCM-R3 additive HTTP bridge for the Browser native-audio Studio surface.

The validated pre-R3 Studio handler remains intact. This module subclasses it to add
only native-audio projection/Preview/Accept/audition routes and same-origin UI assets.
"""

from __future__ import annotations

from http import HTTPStatus
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit

from .audio_contracts import audio_material_from_blueprint
from .studio import StudioApplication, StudioService, StudioServiceError
from .studio_audio import StudioAudioSurface
from .studio_wav_staging import WavStagingStore, STAGED_CHUNK_BYTES
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
    wav_staging = WavStagingStore(application.service, audio_surface)

    class R3StudioRequestHandler(base_handler):
        server_version = "MUSICAStudio/0.7"

        def _send_static(self, clean_path: str) -> bool:
            if clean_path == "/assets/app.js":
                data = _browser_asset_bytes("app.js") + b"\n" + _static_bytes("native_audio.js") + b"\n" + _static_bytes("production_guide.js")
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
                # G3B-0: opaque local session-bound staged transport; no
                # accepted creative revision is changed by start/chunk/finish.
                # Keep the old 16 MiB direct-upload route independently intact.
                if (method == "POST" and len(parts) == 6 and
                        parts[:2] == ["v0", "sessions"] and
                        parts[3:5] == ["audio", "stage"] and parts[5] == "start"):
                    data = wav_staging.start(parts[2], self._read_json())
                    self._send_json(HTTPStatus.OK, application._response("start_staged_wav", data))
                    return
                if (method == "POST" and len(parts) == 7 and
                        parts[:2] == ["v0", "sessions"] and
                        parts[3:5] == ["audio", "stage"]):
                    upload_id, operation = parts[5], parts[6]
                    if operation == "chunk":
                        if self.headers.get("Transfer-Encoding"):
                            raise StudioServiceError(
                                "invalid_request", "unbounded chunked transfer encoding unsupported"
                            )
                        if self.headers.get("Content-Type", "").split(";", 1)[0].lower() != "application/octet-stream":
                            raise StudioServiceError(
                                "invalid_request", "staged chunk must be application/octet-stream"
                            )
                        try:
                            size = int(self.headers.get("Content-Length", ""))
                            offset = int(self.headers.get("X-MUSICA-Chunk-Offset", ""))
                        except ValueError as exc:
                            raise StudioServiceError(
                                "invalid_request", "staged chunk requires numeric size/offset"
                            ) from exc
                        if not 1 <= size <= STAGED_CHUNK_BYTES or offset < 0:
                            raise StudioServiceError("invalid_request", "staged chunk exceeds 1 MiB cap")
                        data = self.rfile.read(size)
                        if len(data) != size:
                            raise StudioServiceError("invalid_request", "staged WAV chunk truncated")
                        result = wav_staging.chunk(
                            parts[2], upload_id, offset, data,
                            self.headers.get("X-MUSICA-Chunk-SHA256", "")
                        )
                        self._send_json(HTTPStatus.OK, application._response("staged_wav_chunk", result))
                        return
                    if operation in {"finish", "cancel"}:
                        if self._read_json():
                            raise StudioServiceError("invalid_request", "staged finish/cancel body must be empty")
                        result = (wav_staging.finish(parts[2], upload_id)
                                  if operation == "finish" else wav_staging.cancel(parts[2], upload_id))
                        self._send_json(HTTPStatus.OK, application._response("staged_wav_" + operation, result))
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
