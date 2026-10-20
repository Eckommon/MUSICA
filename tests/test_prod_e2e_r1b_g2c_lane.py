"""G2C bounded trusted Browser ADD_LANE authoring contract checks."""
from __future__ import annotations
import threading
from urllib.request import urlopen
from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server

def test_native_gain_lane_ui_is_noncanonical_preview_only(tmp_path):
    service = StudioService(tmp_path / "workspace")
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        with urlopen(f"http://{host}:{port}/assets/app.js") as response:
            script = response.read().decode("utf-8")
        body = script.split("function previewNativeLane() {", 1)[1].split("function previewSelectedChanges() {", 1)[0]
        for token in ("m7PreviewNativeLane", "rv.revision_id !== view.revision_id",
                      "av.revision_id !== view.revision_id", "mixer.gain_db",
                      "ADD_LANE", "sendPreview(", "lastBeat", "value: start",
                      "value: end", "scope: \"audio_track\""):
            assert token in script if token == "m7PreviewNativeLane" else token in body
        assert "preview/accept" not in body
        assert "autoAccept" not in body
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
