"""G2B: browser two-bus graph bootstrap is source-bound, never auto-accepted."""
from __future__ import annotations
import threading
from urllib.request import urlopen
from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server

def test_g2b_routing_starter_uses_trusted_preview_and_exact_audio_source(tmp_path):
    service = StudioService(tmp_path / "ws")
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .01}, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        with urlopen(f"http://{host}:{port}/assets/app.js") as response:
            script = response.read().decode()
        assert "mramPreviewStarterTwoBus" in script
        routing = script.split("function previewStarterTwoBus() {")[1].split("function previewTrackOutput() {")[0]
        for term in (
            "audio.revision_id !== view.revision_id", "native.sessionId !== routing.sessionId",
            "tracks.length !== 2", "!t.clips.length", "ADD_NODE", "SET_TRACK_OUTPUT",
            "node_type: \"master\"", "sendPreview(operations",
        ):
            assert term in routing, term
        assert "audio/accept" not in routing
        assert "preview/accept" not in routing
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
