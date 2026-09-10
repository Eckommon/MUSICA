"""Thin localhost HTTP bridge for the M4-R1 Studio application service.

The bridge intentionally serves only application JSON and current session audio/MIDI.
No cloud binding, directory browsing, upload endpoint, CORS wildcard, or remote telemetry
is enabled by this module.
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from .studio import StudioApplication, StudioService, StudioServiceError

MAX_JSON_BODY_BYTES = 1_048_576
DEFAULT_HOST = "127.0.0.1"


def _status_for_error(error: StudioServiceError) -> int:
    if error.code == "not_found":
        return HTTPStatus.NOT_FOUND
    if error.code == "conflict":
        return HTTPStatus.CONFLICT
    if error.code in {"provider_error", "internal_error"}:
        return HTTPStatus.BAD_GATEWAY if error.code == "provider_error" else HTTPStatus.INTERNAL_SERVER_ERROR
    return HTTPStatus.BAD_REQUEST


def make_handler(application: StudioApplication):
    class StudioRequestHandler(BaseHTTPRequestHandler):
        server_version = "MUSICAStudio/0.1"
        protocol_version = "HTTP/1.1"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            # M4-R1 keeps the reusable bridge quiet; a product logger belongs later.
            return

        def _send_bytes(self, status: int, content_type: str, data: bytes) -> None:
            self.send_response(int(status))
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, status: int, value: Any) -> None:
            data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            self._send_bytes(status, "application/json; charset=utf-8", data)

        def _read_json(self) -> dict[str, Any]:
            content_type = self.headers.get("Content-Type", "")
            if "application/json" not in content_type.lower():
                raise StudioServiceError("invalid_request", "Content-Type must be application/json")
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                raise StudioServiceError("invalid_request", "Content-Length is required")
            try:
                length = int(raw_length)
            except ValueError as exc:
                raise StudioServiceError("invalid_request", "invalid Content-Length") from exc
            if length < 0 or length > MAX_JSON_BODY_BYTES:
                raise StudioServiceError("invalid_request", "JSON request body exceeds Studio limit")
            raw = self.rfile.read(length)
            if not raw:
                return {}
            try:
                value = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise StudioServiceError("invalid_request", "request body is not valid UTF-8 JSON") from exc
            if not isinstance(value, dict):
                raise StudioServiceError("invalid_request", "request body must be a JSON object")
            return value

        def _route(self, method: str) -> None:
            clean_path = urlsplit(self.path).path
            try:
                if method == "GET" and clean_path == "/v0/health":
                    self._send_json(
                        HTTPStatus.OK,
                        {
                            "service": "musica-studio",
                            "status": "ok",
                            "local_first": True,
                        },
                    )
                    return

                parts = [part for part in clean_path.strip("/").split("/") if part]
                if (
                    method == "GET"
                    and len(parts) == 5
                    and parts[:2] == ["v0", "sessions"]
                    and parts[3] == "media"
                    and parts[4] in {"audio.wav", "preview.mid"}
                ):
                    kind = "audio" if parts[4] == "audio.wav" else "midi"
                    data = application.service.media_bytes(parts[2], kind)
                    content_type = "audio/wav" if kind == "audio" else "audio/midi"
                    self._send_bytes(HTTPStatus.OK, content_type, data)
                    return

                body = self._read_json() if method == "POST" else None
                response = application.dispatch(method, clean_path, body)
                self._send_json(HTTPStatus.OK, response)
            except StudioServiceError as exc:
                self._send_json(_status_for_error(exc), {"ok": False, "error": exc.as_dict()})
            except Exception as exc:  # final HTTP trust boundary
                safe = StudioServiceError("internal_error", f"unhandled Studio HTTP error: {type(exc).__name__}")
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": safe.as_dict()})

        def do_GET(self) -> None:  # noqa: N802
            self._route("GET")

        def do_POST(self) -> None:  # noqa: N802
            self._route("POST")

    return StudioRequestHandler


def create_local_server(
    service: StudioService,
    *,
    host: str = DEFAULT_HOST,
    port: int = 0,
) -> ThreadingHTTPServer:
    """Create, but do not start, a local Studio HTTP server.

    M4-R1 intentionally accepts only loopback hosts. A future deployment mode must be a
    separate security decision rather than an accidental consequence of this helper.
    """

    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise StudioServiceError("invalid_request", "M4-R1 Studio HTTP server may bind only to loopback")
    if not 0 <= int(port) <= 65535:
        raise StudioServiceError("invalid_request", "invalid Studio HTTP port")
    application = StudioApplication(service)
    return ThreadingHTTPServer((host, int(port)), make_handler(application))
