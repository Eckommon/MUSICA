from __future__ import annotations

import hashlib
import json
import threading
from urllib import error as urlerror
from urllib import request as urlrequest

import pytest

from musica.contracts import validate_contract
from musica.studio import StudioApplication, StudioService, StudioServiceError
from musica.studio_http import create_local_server


CREATE_ARGS = {
    "project_slug": "test-song",
    "user_text": "Create a restrained dark electronic technology cue",
    "session_id": "session-a",
    "provider_mode": "fixture",
    "locale": "en-US",
    "duration_seconds": 8,
    "use_case": "advertisement",
    "style_profile": "dark_electronic",
    "seed": 4242,
    "preserve_on_edit": ["tempo", "melody_identity", "rhythm_identity"],
    "exclusions": ["vocals"],
}


def create_service(tmp_path):
    service = StudioService(tmp_path / "workspace")
    result = service.create_project_session(**CREATE_ARGS)
    return service, result


def test_create_project_session_is_immediately_usable_and_integrity_valid(tmp_path):
    service, result = create_service(tmp_path)
    session = result["session"]
    validate_contract(session, "studio-session-v0.schema.json")
    assert session["session_id"] == "session-a"
    assert session["provider_mode"] == "fixture"
    assert session["project_relpath"] == "test-song.musica"
    assert session["integrity_status"] == "PASS"
    assert session["pending_preview"] is None
    assert session["audio_available"] is True
    assert session["midi_available"] is True
    assert service.media_bytes("session-a", "audio")[:4] == b"RIFF"
    assert service.media_bytes("session-a", "midi")[:4] == b"MThd"
    assert result["intent"]["duration_seconds"] == 8
    assert result["intent"]["style_profile"] == "dark_electronic"


def test_semantic_preview_is_noncanonical_until_explicit_accept(tmp_path):
    service, result = create_service(tmp_path)
    root_head = result["session"]["head_revision_id"]

    preview = service.preview_semantic_edit(
        "session-a",
        name="tension",
        operation="increase",
        value=0.18,
        scope_kind="final_section",
    )
    descriptor = preview["preview"]
    validate_contract(descriptor, "studio-preview-v0.schema.json")
    assert descriptor["parent_revision_id"] == root_head
    assert descriptor["candidate_revision_id"] != root_head
    assert service.inspect_session("session-a")["head_revision_id"] == root_head
    assert service.inspect_session("session-a")["pending_preview"]["preview_id"] == descriptor["preview_id"]
    assert service.media_bytes("session-a", "audio")[:4] == b"RIFF"

    accepted = service.accept_preview("session-a")
    assert accepted["revision_record"]["revision_id"] == descriptor["candidate_revision_id"]
    assert accepted["session"]["head_revision_id"] == descriptor["candidate_revision_id"]
    assert accepted["session"]["pending_preview"] is None
    assert accepted["project_verification"]["status"] == "PASS"
    assert len(accepted["artifact_manifest"]["artifacts"]) == 2


def test_discard_preview_keeps_branch_head_exactly_unchanged(tmp_path):
    service, result = create_service(tmp_path)
    head = result["session"]["head_revision_id"]
    preview = service.preview_semantic_edit(
        "session-a",
        name="density",
        operation="decrease",
        value=0.12,
        scope_kind="whole_project",
    )
    assert preview["preview"]["candidate_revision_id"] != head
    discarded = service.discard_preview("session-a")
    assert discarded["head_revision_id"] == head
    assert discarded["session"]["head_revision_id"] == head
    assert discarded["session"]["pending_preview"] is None


def test_branch_history_and_deterministic_export_work_without_git(tmp_path):
    service, result = create_service(tmp_path)
    root = result["session"]["head_revision_id"]
    branch_result = service.create_branch("session-a", branch_name="variation-a", checkout=True)
    assert branch_result["session"]["current_branch"] == "variation-a"
    assert branch_result["session"]["head_revision_id"] == root
    assert branch_result["session"]["branches"]["main"] == root

    preview = service.preview_semantic_edit(
        "session-a",
        name="brightness",
        operation="increase",
        value=0.20,
        scope_kind="final_section",
    )
    candidate = preview["preview"]["candidate_revision_id"]
    service.accept_preview("session-a")
    history = service.revision_history("session-a")
    assert history["current_branch"] == "variation-a"
    assert history["head_revision_id"] == candidate
    assert len(history["revisions"]) == 2
    assert service.inspect_session("session-a")["branches"]["main"] == root

    first = service.export_project("session-a")
    second = service.export_project("session-a")
    assert first["sha256"] == second["sha256"]
    assert first["size_bytes"] == second["size_bytes"]
    export_path = service.workspace / first["export_relpath"]
    assert hashlib.sha256(export_path.read_bytes()).hexdigest() == first["sha256"]


def test_pending_preview_blocks_branch_switch_and_export(tmp_path):
    service, _ = create_service(tmp_path)
    service.preview_semantic_edit(
        "session-a",
        name="motion",
        operation="increase",
        value=0.1,
        scope_kind="whole_project",
    )
    with pytest.raises(StudioServiceError) as branch_error:
        service.create_branch("session-a", branch_name="unsafe-branch")
    assert branch_error.value.code == "conflict"
    with pytest.raises(StudioServiceError) as export_error:
        service.export_project("session-a")
    assert export_error.value.code == "conflict"


def test_project_can_be_reopened_in_new_service_process_boundary(tmp_path):
    workspace = tmp_path / "workspace"
    first = StudioService(workspace)
    created = first.create_project_session(**CREATE_ARGS)
    expected_head = created["session"]["head_revision_id"]
    first.close_session("session-a")

    second = StudioService(workspace)
    reopened = second.open_project_session(
        project_slug="test-song",
        session_id="session-b",
        provider_mode="fixture",
    )
    assert reopened["session"]["head_revision_id"] == expected_head
    assert reopened["session"]["integrity_status"] == "PASS"
    assert second.media_bytes("session-b", "audio")[:4] == b"RIFF"


def test_studio_rejects_path_traversal_and_symlink_escape(tmp_path):
    workspace = tmp_path / "workspace"
    service = StudioService(workspace)
    with pytest.raises(StudioServiceError) as traversal:
        service.create_project_session(
            project_slug="../escape",
            user_text="bad path",
            session_id="safe-session",
        )
    assert traversal.value.code == "invalid_request"

    outside = tmp_path / "outside-project"
    outside.mkdir()
    link = workspace / "evil.musica"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")
    with pytest.raises(StudioServiceError) as symlink_error:
        service.open_project_session(project_slug="evil", session_id="symlink-session")
    assert symlink_error.value.code == "path_escape"


def test_studio_http_server_refuses_non_loopback_binding(tmp_path):
    service = StudioService(tmp_path / "workspace")
    with pytest.raises(StudioServiceError) as exc:
        create_local_server(service, host="0.0.0.0", port=0)
    assert exc.value.code == "invalid_request"


def _http_json(url, *, method="GET", body=None):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urlrequest.Request(url, data=data, method=method, headers=headers)
    with urlrequest.urlopen(req, timeout=10) as response:
        return response.status, response.headers.get_content_type(), json.loads(response.read().decode("utf-8"))


def test_loopback_http_bridge_can_create_inspect_and_stream_audio(tmp_path):
    service = StudioService(tmp_path / "workspace")
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        status, content_type, created = _http_json(
            base + "/v0/projects/create",
            method="POST",
            body=CREATE_ARGS,
        )
        assert status == 200
        assert content_type == "application/json"
        validate_contract(created, "studio-response-v0.schema.json")
        assert created["data"]["session"]["integrity_status"] == "PASS"

        status, _, inspected = _http_json(base + "/v0/sessions/session-a")
        assert status == 200
        assert inspected["data"]["head_revision_id"] == created["data"]["session"]["head_revision_id"]

        with urlrequest.urlopen(base + "/v0/sessions/session-a/media/audio.wav", timeout=10) as response:
            audio = response.read()
            assert response.status == 200
            assert response.headers.get_content_type() == "audio/wav"
            assert audio[:4] == b"RIFF"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_dispatch_surface_returns_machine_valid_envelope_and_errors_are_machine_valid(tmp_path):
    service, _ = create_service(tmp_path)
    app = StudioApplication(service)
    response = app.dispatch("GET", "/v0/sessions/session-a")
    validate_contract(response, "studio-response-v0.schema.json")
    assert response["ok"] is True

    with pytest.raises(StudioServiceError) as exc:
        app.dispatch("GET", "/v0/sessions/missing")
    error = exc.value.as_dict()
    validate_contract(error, "studio-error-v0.schema.json")
    assert error["code"] == "not_found"


def test_openai_mode_without_runtime_credential_fails_before_project_creation(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    service = StudioService(tmp_path / "workspace")
    args = dict(CREATE_ARGS)
    args["project_slug"] = "openai-no-key"
    args["session_id"] = "openai-session"
    args["provider_mode"] = "openai"
    with pytest.raises(StudioServiceError) as exc:
        service.create_project_session(**args)
    assert exc.value.code == "provider_error"
    assert not (service.workspace / "openai-no-key.musica").exists()
