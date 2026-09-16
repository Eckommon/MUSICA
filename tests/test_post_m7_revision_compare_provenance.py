from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from urllib import request as urlrequest

from musica.project import create_project
from musica.studio import StudioService
from musica.studio_compare import StudioRevisionCompareSurface
from musica.studio_http import create_local_server

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"


def _service_with_mixed_provenance(tmp_path: Path) -> tuple[StudioService, str, str]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    project = create_project(workspace / "compare-provenance.musica", blueprint)
    root = project.head_revision_id()
    service = StudioService(workspace)
    service.open_project_session(project_slug="compare-provenance", session_id="compare-provenance")
    preview = service.preview_semantic_edit(
        "compare-provenance",
        name="tension",
        operation="increase",
        value=0.18,
        scope_kind="final_section",
    )
    child = str(preview["preview"]["candidate_revision_id"])
    service.accept_preview("compare-provenance")
    return service, root, child


def test_bound_media_exposes_exact_manifest_identity_while_fallback_exposes_none(tmp_path: Path) -> None:
    service, root, child = _service_with_mixed_provenance(tmp_path)
    view = StudioRevisionCompareSurface(service).compare_view(
        "compare-provenance",
        revision_a=root,
        revision_b=child,
    )

    for media in view["revision_a"]["media"].values():
        assert media["source"] == "deterministic_fallback"
        assert media["artifact_name"] is None
        assert media["artifact_manifest_sha256"] is None

    manifest_path = service._get_session("compare-provenance").project.root / "artifacts" / child / "manifest.json"
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    for media in view["revision_b"]["media"].values():
        assert media["source"] == "bound_artifact"
        assert media["artifact_name"] in {"preview.mid", "preview.wav"}
        assert media["artifact_manifest_sha256"] == manifest_sha


def test_browser_bundle_marks_user_choice_local_only_and_has_no_write_route(tmp_path: Path) -> None:
    service, _root, _child = _service_with_mixed_provenance(tmp_path)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    try:
        with urlrequest.urlopen(f"http://{host}:{port}/assets/app.js", timeout=30) as response:  # noqa: S310
            script = response.read().decode("utf-8")

        assert "Choose A · local only" in script
        assert "Choose B · local only" in script
        assert "USER CHOICE" in script
        assert "Browser-local only" in script
        assert "Canonical HEAD was not changed" in script
        assert "revisionCompareChooseA" in script
        assert "revisionCompareChooseB" in script
        assert "fetch(`/v0/sessions/${encodeURIComponent(sessionId)}/decision" not in script
        assert "implicit_accept_authorized" not in script
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
