from __future__ import annotations

import copy
import json
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from musica.contracts import validate_contract
from musica.note_edit import blueprint_sha256
from musica.project import create_project
from musica.studio import StudioService
from musica.studio_http import create_local_server
from musica.studio_notes import NOTE_OPERATIONS, StudioNoteSurface

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
MATERIAL_PATH = ROOT / "examples" / "note-material" / "valid" / "dark-electronic-explicit-timeline-v0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def exact_blueprint(*, locked: bool = False) -> dict:
    blueprint = _load(BLUEPRINT_PATH)
    blueprint["materials"]["melody"]["exact_timeline"] = _load(MATERIAL_PATH)
    if locked:
        blueprint["materials"]["melody"]["exact_note_locks"] = [
            {
                "lock_version": "0",
                "lock_id": "L-M6-R2-PITCH",
                "strength": "HARD",
                "selector": {
                    "part_id": "P-SYNTH",
                    "note_id": "N-MOTIF-001",
                    "property": "pitch",
                },
                "mode": "exact",
                "inheriting": True,
                "value": 62,
                "reason": "Protect the Browser Studio anchor pitch.",
            }
        ]
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def open_session(tmp_path: Path, blueprint: dict, *, slug: str = "exact-song", sid: str = "studio-exact"):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    create_project(workspace / f"{slug}.musica", blueprint)
    service = StudioService(workspace)
    service.open_project_session(project_slug=slug, session_id=sid)
    return service, StudioNoteSurface(service)


def candidate(parent: dict, operations: list[dict], *, candidate_id: str = "NEC-M6-R2-001") -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_exact_note_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "m6-r2-test"},
        "reason": "M6-R2 Browser Studio exact-note test.",
        "operations": operations,
        "preview_only": True,
    }


def target(note_id: str = "N-MOTIF-001") -> dict:
    return {"note_id": note_id, "part_id": "P-SYNTH"}


def operation_case(op: str) -> dict:
    if op == "INSERT":
        return {
            "operation_id": "OP-INSERT",
            "op": "INSERT",
            "note": {
                "note_id": "N-MOTIF-004",
                "part_id": "P-SYNTH",
                "section_id": "S01",
                "start_beat": 4.0,
                "duration_beats": 0.5,
                "pitch": 67,
                "velocity": 74,
            },
        }
    if op == "DELETE":
        return {"operation_id": "OP-DELETE", "op": "DELETE", "target": target()}
    if op == "MOVE":
        return {"operation_id": "OP-MOVE", "op": "MOVE", "target": target(), "start_beat": 0.25}
    if op == "RESIZE":
        return {"operation_id": "OP-RESIZE", "op": "RESIZE", "target": target(), "duration_beats": 0.5}
    if op == "REPITCH":
        return {"operation_id": "OP-REPITCH", "op": "REPITCH", "target": target(), "pitch": 64}
    if op == "SET_VELOCITY":
        return {"operation_id": "OP-VELOCITY", "op": "SET_VELOCITY", "target": target(), "velocity": 91}
    raise AssertionError(op)


def test_note_view_is_source_bound_canonical_and_side_effect_free(tmp_path: Path) -> None:
    parent = exact_blueprint()
    service, surface = open_session(tmp_path, parent)
    before = service._get_session("studio-exact").project.head_revision_id()

    view_a = surface.note_view("studio-exact")
    view_b = surface.note_view("studio-exact")

    assert view_a == view_b
    assert view_a["exact_note_editing_available"] is True
    assert view_a["project_id"] == parent["project"]["project_id"]
    assert view_a["revision_id"] == parent["project"]["revision_id"]
    assert view_a["blueprint_sha256"] == blueprint_sha256(parent)
    assert view_a["editable_part"]["part_id"] == "P-SYNTH"
    assert [note["note_id"] for note in view_a["notes"]] == ["N-MOTIF-001", "N-MOTIF-002", "N-MOTIF-003"]
    assert view_a["capabilities"]["operations"] == NOTE_OPERATIONS
    assert view_a["capabilities"]["music_ir_mutation_authorized"] is False
    assert service._get_session("studio-exact").project.head_revision_id() == before


def test_legacy_project_reports_exact_editing_unavailable_without_reverse_mapping(tmp_path: Path) -> None:
    legacy = _load(BLUEPRINT_PATH)
    service, surface = open_session(tmp_path, legacy, slug="legacy-song", sid="studio-legacy")
    view = surface.note_view("studio-legacy")
    assert view["exact_note_editing_available"] is False
    assert view["editable_part"] is None
    assert view["notes"] == []
    assert view["note_locks"] == []
    assert view["preview"] is None
    assert service.inspect_session("studio-legacy")["integrity_status"] == "PASS"


@pytest.mark.parametrize("op", NOTE_OPERATIONS)
def test_all_six_note_operations_install_noncanonical_preview_without_ref_advance(tmp_path: Path, op: str) -> None:
    parent = exact_blueprint()
    service, surface = open_session(tmp_path, parent, slug=f"song-{op.lower()}", sid=f"sid-{op.lower()}")
    sid = f"sid-{op.lower()}"
    project = service._get_session(sid).project
    before = project.head_revision_id()

    result = surface.preview_note_edit(sid, candidate=candidate(parent, [operation_case(op)], candidate_id=f"C-{op}"))

    assert result["preview_installed"] is True
    assert result["authority_result"]["status"] == "READY_FOR_PREVIEW"
    assert project.head_revision_id() == before
    assert service.inspect_session(sid)["pending_preview"]["kind"] == "note_edit"
    note_view = surface.note_view(sid)
    assert note_view["preview"] is not None
    assert note_view["preview"]["changed_note_ids"]


def test_blocked_stale_source_installs_no_preview(tmp_path: Path) -> None:
    parent = exact_blueprint()
    service, surface = open_session(tmp_path, parent)
    edit = candidate(parent, [operation_case("MOVE")])
    edit["source"]["blueprint_sha256"] = "0" * 64
    before = service._get_session("studio-exact").project.head_revision_id()

    result = surface.preview_note_edit("studio-exact", candidate=edit)

    assert result["preview_installed"] is False
    assert result["authority_result"]["status"] == "BLOCKED"
    assert result["authority_result"]["conflicts"][0]["code"] == "STALE_SOURCE"
    assert service.inspect_session("studio-exact")["pending_preview"] is None
    assert service._get_session("studio-exact").project.head_revision_id() == before


def test_blocked_stable_note_lock_installs_no_preview(tmp_path: Path) -> None:
    parent = exact_blueprint(locked=True)
    service, surface = open_session(tmp_path, parent)
    result = surface.preview_note_edit(
        "studio-exact",
        candidate=candidate(parent, [operation_case("REPITCH")]),
    )
    assert result["preview_installed"] is False
    assert result["authority_result"]["conflicts"][0]["code"] == "HARD_LOCK_VIOLATION"
    assert service.inspect_session("studio-exact")["pending_preview"] is None


def test_note_preview_accepts_once_through_existing_m2_and_survives_reopen(tmp_path: Path) -> None:
    parent = exact_blueprint()
    service, surface = open_session(tmp_path, parent)
    project = service._get_session("studio-exact").project
    root = project.head_revision_id()
    result = surface.preview_note_edit(
        "studio-exact",
        candidate=candidate(parent, [operation_case("REPITCH")]),
    )
    candidate_revision = result["preview"]["candidate_revision_id"]
    assert project.head_revision_id() == root

    accepted = service.accept_preview("studio-exact")
    assert accepted["revision_record"]["revision_id"] == candidate_revision
    assert project.head_revision_id() == candidate_revision
    assert accepted["project_verification"]["status"] == "PASS"
    assert len(service.revision_history("studio-exact")["revisions"]) == 2

    service.close_session("studio-exact")
    service.open_project_session(project_slug="exact-song", session_id="studio-reopen")
    reopened = StudioNoteSurface(service).note_view("studio-reopen")
    edited = next(note for note in reopened["notes"] if note["note_id"] == "N-MOTIF-001")
    assert edited["pitch"] == 64
    assert reopened["revision_id"] == candidate_revision


def test_note_preview_discard_preserves_accepted_ref(tmp_path: Path) -> None:
    parent = exact_blueprint()
    service, surface = open_session(tmp_path, parent)
    project = service._get_session("studio-exact").project
    before = project.head_revision_id()
    surface.preview_note_edit("studio-exact", candidate=candidate(parent, [operation_case("MOVE")]))
    discarded = service.discard_preview("studio-exact")
    assert discarded["head_revision_id"] == before
    assert project.head_revision_id() == before
    assert surface.note_view("studio-exact")["preview"] is None


def _http_json(url: str, *, method: str = "GET", body: dict | None = None) -> tuple[int, dict]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(url, method=method, data=data)
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urlopen(request, timeout=5) as response:  # noqa: S310 - loopback test server
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_http_note_routes_and_same_origin_precision_assets(tmp_path: Path) -> None:
    parent = exact_blueprint()
    service, _surface = open_session(tmp_path, parent)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        status, payload = _http_json(f"{base}/v0/sessions/studio-exact/notes")
        assert status == 200
        assert payload["ok"] is True
        assert payload["data"]["exact_note_editing_available"] is True

        edit = candidate(parent, [operation_case("MOVE")])
        status, payload = _http_json(
            f"{base}/v0/sessions/studio-exact/preview/notes",
            method="POST",
            body={"candidate": edit},
        )
        assert status == 200
        assert payload["data"]["preview_installed"] is True
        assert service._get_session("studio-exact").project.head_revision_id() == parent["project"]["revision_id"]

        with urlopen(f"{base}/assets/app.js", timeout=5) as response:  # noqa: S310
            script = response.read().decode("utf-8")
        with urlopen(f"{base}/assets/app.css", timeout=5) as response:  # noqa: S310
            style = response.read().decode("utf-8")
        assert "MUSICA_PRECISION" in script
        assert "/preview/notes" in script
        assert "m6-piano-roll" in style
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
