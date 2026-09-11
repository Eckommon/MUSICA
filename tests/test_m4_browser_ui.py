from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from importlib import resources
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from musica.studio import StudioService
from musica.studio_http import create_local_server
from musica.studio_server import build_parser


@contextmanager
def running_server(tmp_path):
    service = StudioService(tmp_path / "workspace")
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    try:
        yield service, f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def http_get(base, path):
    with urlopen(base + path, timeout=5) as response:
        return response.status, dict(response.headers.items()), response.read()


def http_json(base, method, path, body=None):
    raw = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(
        base + path,
        data=raw,
        method=method,
        headers={"Accept": "application/json", **({"Content-Type": "application/json"} if raw is not None else {})},
    )
    with urlopen(request, timeout=10) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def test_packaged_browser_assets_have_progressive_disclosure_and_no_remote_dependencies():
    package = resources.files("musica.studio_web")
    html = package.joinpath("index.html").read_text(encoding="utf-8")
    css = package.joinpath("app.css").read_text(encoding="utf-8")
    js = package.joinpath("app.js").read_text(encoding="utf-8")

    for label in ("Direct", "Shape", "Inspect", "Code"):
        assert label in html
    for control_id in (
        "createForm",
        "audioPlayer",
        "semanticControls",
        "previewSemanticButton",
        "previewDecision",
        "acceptButton",
        "discardButton",
        "branchSelect",
        "historyList",
        "jsonView",
    ):
        assert f'id="{control_id}"' in html

    assert '<script src="/assets/app.js" defer></script>' in html
    assert '<link rel="stylesheet" href="/assets/app.css">' in html
    assert "https://" not in html
    assert "http://" not in html
    assert "https://" not in css
    assert "http://" not in css
    assert "https://" not in js
    assert "http://" not in js
    assert "telemetry" not in js.lower()
    assert "cdn" not in js.lower()


def test_browser_assets_are_served_same_origin_with_strict_security_headers(tmp_path):
    with running_server(tmp_path) as (_, base):
        status, headers, html = http_get(base, "/")
        assert status == 200
        assert headers["Content-Type"].startswith("text/html")
        assert "default-src 'self'" in headers["Content-Security-Policy"]
        assert "script-src 'self'" in headers["Content-Security-Policy"]
        assert "connect-src 'self'" in headers["Content-Security-Policy"]
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
        assert headers["Referrer-Policy"] == "no-referrer"
        assert headers["X-Frame-Options"] == "DENY"
        assert b"MUSICA Studio" in html

        css_status, css_headers, css = http_get(base, "/assets/app.css")
        js_status, js_headers, js = http_get(base, "/assets/app.js")
        assert css_status == js_status == 200
        assert css_headers["Content-Type"].startswith("text/css")
        assert js_headers["Content-Type"].startswith("text/javascript")
        assert len(css) > 1000
        assert len(js) > 1000


def test_browser_visible_http_flow_preserves_preview_accept_authority(tmp_path):
    with running_server(tmp_path) as (_, base):
        status, created = http_json(
            base,
            "POST",
            "/v0/projects/create",
            {
                "project_slug": "browser-proof",
                "user_text": "Create a restrained dark electronic 20-second technology cue",
                "provider_mode": "fixture",
                "duration_seconds": 20,
                "use_case": "advertisement",
                "style_profile": "dark_electronic",
                "preserve_on_edit": ["tempo", "melody_identity", "rhythm_identity"],
                "exclusions": ["vocals"],
            },
        )
        assert status == 200 and created["ok"] is True
        session = created["data"]["session"]
        session_id = session["session_id"]
        accepted_head = session["head_revision_id"]
        assert session["pending_preview"] is None

        _, preview = http_json(
            base,
            "POST",
            f"/v0/sessions/{session_id}/preview/semantic",
            {
                "name": "tension",
                "operation": "set",
                "value": 0.82,
                "scope_kind": "final_section",
                "section_id": None,
            },
        )
        preview_session = preview["data"]["session"]
        assert preview_session["head_revision_id"] == accepted_head
        assert preview_session["pending_preview"] is not None
        assert preview["data"]["diff"]

        audio_status, audio_headers, audio = http_get(base, f"/v0/sessions/{session_id}/media/audio.wav")
        assert audio_status == 200
        assert audio_headers["Content-Type"] == "audio/wav"
        assert audio[:4] == b"RIFF"

        _, accepted = http_json(base, "POST", f"/v0/sessions/{session_id}/preview/accept", {})
        accepted_session = accepted["data"]["session"]
        assert accepted_session["head_revision_id"] != accepted_head
        assert accepted_session["pending_preview"] is None
        assert accepted_session["integrity_status"] == "PASS"

        _, history = http_json(base, "GET", f"/v0/sessions/{session_id}/history")
        assert len(history["data"]["revisions"]) == 2

        _, exported = http_json(base, "POST", f"/v0/sessions/{session_id}/export", {})
        assert exported["data"]["export_relpath"].startswith("exports/")
        assert len(exported["data"]["sha256"]) == 64


def test_static_unknown_path_does_not_expose_package_or_filesystem(tmp_path):
    with running_server(tmp_path) as (_, base):
        for path in ("/assets/../studio.py", "/pyproject.toml", "/.git/config"):
            try:
                http_get(base, path)
            except HTTPError as exc:
                assert exc.code == 404
            else:
                raise AssertionError(f"unexpected static exposure: {path}")


def test_studio_launcher_defaults_to_local_first_workspace_and_loopback():
    args = build_parser().parse_args(["--no-browser"])
    assert args.host == "127.0.0.1"
    assert args.port == 8765
    assert args.no_browser is True
    assert "MUSICA-Workspace" in args.workspace
