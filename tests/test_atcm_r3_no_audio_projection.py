from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

from musica.creative import compose_blueprint
from musica.project import create_project
from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server

ROOT = Path(__file__).resolve().parents[1]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def _blueprint() -> dict:
    return compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))


def test_r3_valid_empty_audio_session_projects_without_http_error(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    create_project(workspace / "legacy.musica", _blueprint())
    service = StudioService(workspace)
    service.open_project_session(project_slug="legacy", session_id="studio-legacy")

    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        with urllib.request.urlopen(base + "/v0/sessions/studio-legacy/audio", timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 200
        assert payload["ok"] is True
        assert payload["operation"] == "native_audio_view"
        view = payload["data"]
        # The canonical root Blueprint already carries an empty audio-material contract.
        # That state must remain a usable R3 arrangement surface (e.g. Add Track), while
        # truthfully reporting that there is nothing renderable yet.
        assert view["accepted_state_is_canonical"] is True
        assert view["browser_state_is_canonical"] is False
        assert view["tracks"] == []
        assert view["accepted_audition"]["available"] is False
        assert "at least one accepted clip" in view["accepted_audition"]["error"]

        try:
            urllib.request.urlopen(base + "/v0/sessions/does-not-exist/audio", timeout=10)
        except urllib.error.HTTPError as exc:
            assert exc.code == 404
        else:  # pragma: no cover - fail closed if unknown sessions are accidentally normalized
            raise AssertionError("unknown Studio session unexpectedly returned HTTP 200")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
