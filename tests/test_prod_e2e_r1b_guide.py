"""PROD-E2E-R1B-G0: guide availability and trusted export authority checks."""
from __future__ import annotations

import io
import json
import threading
import wave
from urllib.request import urlopen

from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server


def test_production_guide_is_served_only_from_first_party_browser_assets(tmp_path):
    service = StudioService(tmp_path / "workspace")
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    host, port = server.server_address[:2]
    try:
        with urlopen(f"http://{host}:{port}/assets/app.js") as response:
            script = response.read().decode("utf-8")
            assert response.headers["content-security-policy"].find("script-src 'self'") != -1
        with urlopen(f"http://{host}:{port}/assets/app.css") as response:
            css = response.read().decode("utf-8")
        for required in (
            "MUSICA_PRODUCTION_GUIDE", "r1bDownloadWav", "r1bGuideSteps",
            "pending_preview", "audio/accepted.wav", "accepted_audition",
            "window.MUSICA_NATIVE_AUDIO", "downloadAcceptedWav",
        ):
            assert required in script
        assert "r1b-guide-step" in css
        # Native audio remains served and the R1B guide cannot commit a project.
        assert "MUSICA_NATIVE_AUDIO" in script
        guide_source = script.split("// PROD-E2E-R1B-G0:")[1]
        assert "audio/accept" not in guide_source
        assert "preview/accept" not in guide_source
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
