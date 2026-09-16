from __future__ import annotations

import copy
import hashlib
import json
import threading
from pathlib import Path
from urllib import error as urlerror
from urllib import request as urlrequest

import pytest

from musica.contracts import validate_contract
from musica.diff import structured_diff
from musica.project import create_project
from musica.studio import StudioService, StudioServiceError
from musica.studio_compare import StudioRevisionCompareSurface
from musica.studio_http import create_local_server

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"


def _load_blueprint() -> dict:
    return json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _open_unbound_root(
    tmp_path: Path,
    *,
    slug: str = "compare-song",
    sid: str = "compare-session",
) -> tuple[StudioService, str]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    project = create_project(workspace / f"{slug}.musica", _load_blueprint())
    root_revision = project.head_revision_id()
    service = StudioService(workspace)
    service.open_project_session(project_slug=slug, session_id=sid)
    return service, root_revision


def _preview_child(service: StudioService, sid: str = "compare-session") -> tuple[str, dict]:
    result = service.preview_semantic_edit(
        sid,
        name="tension",
        operation="increase",
        value=0.18,
        scope_kind="final_section",
    )
    pending = service._get_session(sid).pending
    assert pending is not None
    return str(result["preview"]["candidate_revision_id"]), copy.deepcopy(pending.candidate)


def _accept_bound_child(service: StudioService, sid: str = "compare-session") -> str:
    candidate_revision, _candidate = _preview_child(service, sid)
    accepted = service.accept_preview(sid)
    assert accepted["revision_record"]["revision_id"] == candidate_revision
    return candidate_revision


def _commit_fallback_child(service: StudioService, sid: str = "compare-session") -> str:
    candidate_revision, candidate = _preview_child(service, sid)
    service.discard_preview(sid)
    project = service._get_session(sid).project
    record = project.commit_revision(
        candidate,
        actor="user",
        reason="Create accepted comparison revision without bound media for fallback proof.",
    )
    assert record["revision_id"] == candidate_revision
    project.verify_integrity()
    return candidate_revision


def _bind_revision_media(service: StudioService, revision_id: str, sid: str = "compare-session") -> None:
    session = service._get_session(sid)
    blueprint = session.project.read_revision(revision_id)
    midi, wav = service._render_to_cache(session, blueprint, f"test-bind-{revision_id}")
    session.project.bind_artifacts(revision_id, [midi, wav])
    session.project.verify_integrity()


def _key_set(value) -> set[str]:
    if isinstance(value, dict):
        result = {str(key) for key in value}
        for child in value.values():
            result |= _key_set(child)
        return result
    if isinstance(value, list):
        result: set[str] = set()
        for child in value:
            result |= _key_set(child)
        return result
    return set()


def test_mixed_fallback_bound_compare_is_exact_read_only_and_contract_valid(tmp_path: Path) -> None:
    service, root = _open_unbound_root(tmp_path)
    child = _accept_bound_child(service)
    surface = StudioRevisionCompareSurface(service)
    project = service._get_session("compare-session").project
    head_before = project.head_revision_id()
    branch_before = project.current_branch()

    view = surface.compare_view("compare-session", revision_a=root, revision_b=child)
    validate_contract(view, "studio-revision-compare-v0.schema.json")

    assert view["direction"] == "A_TO_B"
    assert view["revision_a"]["revision_id"] == root
    assert view["revision_b"]["revision_id"] == child
    assert view["revision_a"]["media"]["wav"]["source"] == "deterministic_fallback"
    assert view["revision_a"]["media"]["midi"]["source"] == "deterministic_fallback"
    assert view["revision_b"]["media"]["wav"]["source"] == "bound_artifact"
    assert view["revision_b"]["media"]["midi"]["source"] == "bound_artifact"
    assert view["diff"] == structured_diff(project.read_revision(root), project.read_revision(child))
    assert view["head_unchanged"] is True
    assert project.current_branch() == branch_before
    assert project.head_revision_id() == head_before == child
    assert view["authority"] == {
        "canonical": False,
        "browser_mutation_authorized": False,
        "project_mutation_authorized": False,
        "reverse_promotion_authorized": False,
        "creative_ranking_authorized": False,
        "implicit_accept_authorized": False,
    }
    keys = _key_set(view)
    assert "winner" not in keys
    assert "score" not in keys
    assert "better" not in keys
    assert "preference_probability" not in keys


def test_reverse_and_identity_comparison_are_deterministic(tmp_path: Path) -> None:
    service, root = _open_unbound_root(tmp_path)
    child = _commit_fallback_child(service)
    surface = StudioRevisionCompareSurface(service)
    project = service._get_session("compare-session").project
    head = project.head_revision_id()

    forward = surface.compare_view("compare-session", revision_a=root, revision_b=child)
    reverse = surface.compare_view("compare-session", revision_a=child, revision_b=root)
    identity = surface.compare_view("compare-session", revision_a=root, revision_b=root)

    assert forward["diff"] == structured_diff(project.read_revision(root), project.read_revision(child))
    assert reverse["diff"] == structured_diff(project.read_revision(child), project.read_revision(root))
    assert identity["diff"] == []
    assert identity["revision_a"]["media"]["wav"]["source"] == "deterministic_fallback"
    assert identity["revision_b"]["media"]["wav"]["source"] == "deterministic_fallback"
    assert identity["revision_a"]["media"]["wav"]["sha256"] == identity["revision_b"]["media"]["wav"]["sha256"]
    assert identity["revision_a"]["media"]["midi"]["sha256"] == identity["revision_b"]["media"]["midi"]["sha256"]
    assert project.head_revision_id() == head == child


def test_bound_bound_media_and_served_bytes_match_exact_hashes(tmp_path: Path) -> None:
    service, root = _open_unbound_root(tmp_path)
    _bind_revision_media(service, root)
    child = _accept_bound_child(service)
    surface = StudioRevisionCompareSurface(service)
    view = surface.compare_view("compare-session", revision_a=root, revision_b=child)

    for side_name, revision_id in (("revision_a", root), ("revision_b", child)):
        side = view[side_name]
        assert side["media"]["wav"]["source"] == "bound_artifact"
        assert side["media"]["midi"]["source"] == "bound_artifact"
        wav = surface.media_bytes("compare-session", revision_id=revision_id, kind="audio")
        midi = surface.media_bytes("compare-session", revision_id=revision_id, kind="midi")
        assert wav[:4] == b"RIFF"
        assert midi[:4] == b"MThd"
        assert _sha(wav) == side["media"]["wav"]["sha256"]
        assert _sha(midi) == side["media"]["midi"]["sha256"]


def test_compare_preserves_pending_preview_and_accepted_head(tmp_path: Path) -> None:
    service, root = _open_unbound_root(tmp_path)
    child = _accept_bound_child(service)
    pending = service.preview_semantic_edit(
        "compare-session",
        name="density",
        operation="decrease",
        value=0.12,
        scope_kind="whole_project",
    )["preview"]
    surface = StudioRevisionCompareSurface(service)
    project = service._get_session("compare-session").project

    view = surface.compare_view("compare-session", revision_a=root, revision_b=child)

    assert view["current_head_revision_id"] == child
    assert project.head_revision_id() == child
    assert service.inspect_session("compare-session")["pending_preview"]["preview_id"] == pending["preview_id"]
    service.discard_preview("compare-session")
    assert project.head_revision_id() == child


def test_unknown_or_tampered_revision_fails_closed(tmp_path: Path) -> None:
    service, root = _open_unbound_root(tmp_path)
    child = _accept_bound_child(service)
    surface = StudioRevisionCompareSurface(service)

    with pytest.raises(StudioServiceError) as missing:
        surface.compare_view("compare-session", revision_a="missing-revision", revision_b=child)
    assert missing.value.code == "invalid_request"

    project = service._get_session("compare-session").project
    artifact = project.root / "artifacts" / child / "files" / "preview.wav"
    assert artifact.is_file()
    artifact.write_bytes(artifact.read_bytes() + b"tamper")

    with pytest.raises(StudioServiceError) as tampered:
        surface.compare_view("compare-session", revision_a=root, revision_b=child)
    assert tampered.value.code == "integrity_error"


def _http_json(url: str) -> tuple[int, str, dict]:
    with urlrequest.urlopen(url, timeout=30) as response:  # noqa: S310
        return response.status, response.headers.get_content_type(), json.loads(response.read().decode("utf-8"))


def test_http_compare_and_arbitrary_revision_media_are_exact_and_read_only(tmp_path: Path) -> None:
    service, root = _open_unbound_root(tmp_path)
    child = _accept_bound_child(service)
    project = service._get_session("compare-session").project
    head_before = project.head_revision_id()

    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        status, content_type, payload = _http_json(
            f"{base}/v0/sessions/compare-session/compare/{root}/{child}"
        )
        assert status == 200
        assert content_type == "application/json"
        assert payload["operation"] == "revision_compare"
        view = payload["data"]
        validate_contract(view, "studio-revision-compare-v0.schema.json")

        with urlrequest.urlopen(  # noqa: S310
            f"{base}/v0/sessions/compare-session/revisions/{root}/media/audio.wav",
            timeout=30,
        ) as response:
            root_wav = response.read()
            assert response.headers.get_content_type() == "audio/wav"
        with urlrequest.urlopen(  # noqa: S310
            f"{base}/v0/sessions/compare-session/revisions/{child}/media/preview.mid",
            timeout=30,
        ) as response:
            child_midi = response.read()
            assert response.headers.get_content_type() == "audio/midi"

        assert _sha(root_wav) == view["revision_a"]["media"]["wav"]["sha256"]
        assert _sha(child_midi) == view["revision_b"]["media"]["midi"]["sha256"]
        assert project.head_revision_id() == head_before == child

        with pytest.raises(urlerror.HTTPError) as missing:
            _http_json(f"{base}/v0/sessions/compare-session/compare/missing-revision/{child}")
        assert missing.value.code == 400
        assert project.head_revision_id() == child
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_browser_bundle_contains_compare_surface_without_creative_ranking_controls(tmp_path: Path) -> None:
    service, _root = _open_unbound_root(tmp_path)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        with urlrequest.urlopen(base + "/assets/app.js", timeout=30) as response:  # noqa: S310
            script = response.read().decode("utf-8")
        with urlrequest.urlopen(base + "/assets/app.css", timeout=30) as response:  # noqa: S310
            css = response.read().decode("utf-8")

        assert "Accepted revision A/B" in script
        assert "Compare A → B" in script
        assert "/compare/" in script
        assert "/revisions/" in script
        assert "never ranks a creative winner" in script
        assert "revision-compare-card" in css
        assert "winnerScore" not in script
        assert "preferenceProbability" not in script
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
