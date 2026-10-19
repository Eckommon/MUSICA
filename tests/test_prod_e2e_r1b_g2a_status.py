"""G2A source-bound Browser status smoke checks; not routing/audio effect proof."""
from __future__ import annotations
import threading
from urllib.request import urlopen
from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server

def test_source_bound_guide_never_labels_absent_graph_as_routed(tmp_path):
    service = StudioService(tmp_path / "ws")
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        with urlopen(f"http://{host}:{port}/assets/app.js") as response:
            script = response.read().decode("utf-8")
        start = script.index("// G2A: source-bound")
        guide = script[start:]
        for token in ("rv.revision_id === source", "av.revision_id === source",
                      "routing.sessionId === p.sessionId", "automation.sessionId === p.sessionId",
                      "ACCEPTED · NO ROUTING GRAPH", "ACCEPTED · NO AUTOMATION LANES",
                      "UNKNOWN · REFRESH", "musica:automation-view-ready"):
            assert token in guide
        assert "autoAccept" not in guide
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
