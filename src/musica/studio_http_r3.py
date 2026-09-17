"""ATCM-R3 additive HTTP bridge for the Browser native-audio Studio surface.

The validated pre-R3 Studio handler remains intact. This module subclasses it to add
only native-audio projection/Preview/Accept/audition routes and same-origin UI assets.
"""

from __future__ import annotations

from http import HTTPStatus
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit

from .studio import StudioApplication, StudioService, StudioServiceError
from .studio_audio import StudioAudioSurface
from .studio_http import (
    DEFAULT_HOST,
    _browser_asset_bytes,
    _static_bytes,
    _status_for_error,
    make_handler as make_base_handler,
)


def make_handler(application: StudioApplication):
    base_handler = make_base_handler(application)
    audio_surface = StudioAudioSurface(application.service)

    class R3StudioRequestHandler(base_handler):
        server_version = "MUSICAStudio/0.7"

        def _send_static(self, clean_path: str) -> bool:
            if clean_path == "/assets/app.js":
                data = _browser_asset_bytes("app.js") + b"\n" + _static_bytes("native_audio.js")
                self._send_bytes(
                    HTTPStatus.OK,
                    "text/javascript; charset=utf-8",
                    data,
                    static_document=True,
                )
                return True
            if clean_path == "/assets/app.css":
                data = _browser_asset_bytes("app.css") + b"\n" + _static_bytes("native_audio.css")
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
                if (
                    method == "GET"
                    and len(parts) == 4
                    and parts[:2] == ["v0", "sessions"]
                    and parts[3] == "audio"
                ):
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
