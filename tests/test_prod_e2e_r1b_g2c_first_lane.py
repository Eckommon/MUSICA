"""G2C: first native gain lane never bypasses source-bound user acceptance."""
from __future__ import annotations
import threading
from urllib.request import urlopen
from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server


def test_g2c_first_lane_is_rendered_through_trusted_browser_automation(tmp_path):
    service = StudioService(tmp_path / "workspace")
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .01}, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        with urlopen(f"http://{host}:{port}/assets/app.js") as response:
            script = response.read().decode("utf-8")
        assert "m7PreviewFirstGainLane" in script
        first = script.split("function gainLaneEligibility() {")[1].split("function render() {")[0]
        for required in (
            'v.revision_id === audio.revision_id',
            'v.revision_id === rv.revision_id',
            'routing.sessionId === automation.sessionId',
            'native.sessionId === automation.sessionId',
            '!audio.preview', '!rv.preview', '!v.preview',
            'ADD_LANE', 'mixer.gain_db', 'scope: "audio_track"',
            'sendPreview(', 'Number.isFinite', 'timing.total_beats',
        ):
            assert required in first, required
        assert '"/preview/accept"' not in first
        assert "autoAccept" not in first
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
