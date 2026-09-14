from __future__ import annotations

import copy
import json
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from musica.automation_edit import automation_material_sha256, blueprint_sha256
from musica.contracts import validate_contract
from musica.project import create_project
from musica.studio import StudioService
from musica.studio_automation import AUTOMATION_OPERATIONS, StudioAutomationSurface
from musica.studio_http import create_local_server

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"
LOCK_PATH = ROOT / "examples" / "automation" / "valid" / "automation-lock-v0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def automation_blueprint(*, locked: bool = False) -> dict:
    blueprint = _load(BLUEPRINT_PATH)
    material = _load(AUTOMATION_PATH)
    # The reusable R0 fixture predates Blueprint ownership validation and uses S-INTRO.
    # R2 does not infer or rewrite ownership at runtime; the test fixture binds it explicitly.
    cutoff = next(lane for lane in material["lanes"] if lane["lane_id"] == "B-SYNTH-CUTOFF")
    cutoff["section_id"] = "S01"
    blueprint["materials"]["automation"] = material
    if locked:
        blueprint["materials"]["automation_locks"] = [_load(LOCK_PATH)]
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def open_session(tmp_path: Path, blueprint: dict, *, slug: str = "automation-song", sid: str = "studio-automation"):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    create_project(workspace / f"{slug}.musica", blueprint)
    service = StudioService(workspace)
    service.open_project_session(project_slug=slug, session_id=sid)
    return service, StudioAutomationSurface(service)


def candidate(parent: dict, operations: list[dict], *, candidate_id: str = "AEC-M7-R2-001") -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_automation_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
            "automation_material_sha256": automation_material_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "m7-r2-test"},
        "reason": "M7-R2 Browser Studio automation test.",
        "operations": operations,
        "preview_only": True,
    }


def point_target(*, lane_id: str = "A-MIX-GAIN", point_id: str = "P-GAIN-001") -> dict:
    return {"lane_id": lane_id, "point_id": point_id}


def operation_case(op: str) -> dict:
    if op == "INSERT_POINT":
        return {
            "operation_id": "OP-INSERT",
            "op": "INSERT_POINT",
            "target": {"lane_id": "A-MIX-GAIN"},
            "point": {
                "point_id": "P-GAIN-UI-003",
                "beat": 2.0,
                "value": 0.72,
                "interpolation": "linear",
            },
        }
    if op == "DELETE_POINT":
        return {
            "operation_id": "OP-DELETE",
            "op": "DELETE_POINT",
            "target": point_target(point_id="P-GAIN-002"),
        }
    if op == "MOVE_POINT":
        return {
            "operation_id": "OP-MOVE",
            "op": "MOVE_POINT",
            "target": point_target(point_id="P-GAIN-002"),
            "beat": 6.0,
        }
    if op == "SET_VALUE":
        return {
            "operation_id": "OP-VALUE",
            "op": "SET_VALUE",
            "target": point_target(),
            "value": 0.71,
        }
    if op == "SET_INTERPOLATION":
        return {
            "operation_id": "OP-CURVE",
            "op": "SET_INTERPOLATION",
            "target": point_target(),
            "interpolation": "hold",
        }
    raise AssertionError(op)


def test_automation_view_is_source_bound_stable_and_side_effect_free(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, surface = open_session(tmp_path, parent)
    project = service._get_session("studio-automation").project
    before = project.head_revision_id()

    view_a = surface.automation_view("studio-automation")
    view_b = surface.automation_view("studio-automation")

    assert view_a == view_b
    assert view_a["automation_editing_available"] is True
    assert view_a["project_id"] == parent["project"]["project_id"]
    assert view_a["revision_id"] == parent["project"]["revision_id"]
    assert view_a["blueprint_sha256"] == blueprint_sha256(parent)
    assert view_a["automation_material_sha256"] == automation_material_sha256(parent)
    assert [lane["lane_id"] for lane in view_a["lanes"]] == ["A-MIX-GAIN", "B-SYNTH-CUTOFF"]
    assert view_a["capabilities"]["operations"] == AUTOMATION_OPERATIONS
    assert view_a["capabilities"]["audible_automation_validated"] is False
    assert view_a["capabilities"]["music_ir_mutation_authorized"] is False
    assert project.head_revision_id() == before


def test_legacy_project_reports_no_canonical_automation_without_reverse_inference(tmp_path: Path) -> None:
    legacy = _load(BLUEPRINT_PATH)
    service, surface = open_session(tmp_path, legacy, slug="legacy-song", sid="studio-legacy")
    before = service._get_session("studio-legacy").project.head_revision_id()

    view = surface.automation_view("studio-legacy")

    assert view["automation_editing_available"] is False
    assert view["lanes"] == []
    assert view["automation_locks"] == []
    assert view["preview"] is None
    assert len(view["automation_material_sha256"]) == 64
    assert service._get_session("studio-legacy").project.head_revision_id() == before
    assert service.inspect_session("studio-legacy")["integrity_status"] == "PASS"


@pytest.mark.parametrize("op", AUTOMATION_OPERATIONS)
def test_all_five_operations_install_noncanonical_preview_without_ref_advance(tmp_path: Path, op: str) -> None:
    parent = automation_blueprint()
    sid = f"sid-{op.lower()}"
    service, surface = open_session(tmp_path, parent, slug=f"song-{op.lower()}", sid=sid)
    project = service._get_session(sid).project
    before = project.head_revision_id()

    result = surface.preview_automation_edit(
        sid,
        candidate=candidate(parent, [operation_case(op)], candidate_id=f"C-{op}"),
    )

    assert result["preview_installed"] is True
    assert result["authority_result"]["status"] == "READY_FOR_PREVIEW"
    assert project.head_revision_id() == before
    assert service.inspect_session(sid)["pending_preview"]["kind"] == "automation_edit"
    view = surface.automation_view(sid)
    assert view["preview"] is not None
    assert view["preview"]["changed_lane_ids"]
    assert result["detail"]["audible_automation_validated"] is False


def test_blocked_stale_material_hash_installs_no_preview(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, surface = open_session(tmp_path, parent)
    edit = candidate(parent, [operation_case("MOVE_POINT")])
    edit["source"]["automation_material_sha256"] = "0" * 64
    before = service._get_session("studio-automation").project.head_revision_id()

    result = surface.preview_automation_edit("studio-automation", candidate=edit)

    assert result["preview_installed"] is False
    assert result["authority_result"]["status"] == "BLOCKED"
    assert result["authority_result"]["conflicts"][0]["code"] == "STALE_SOURCE"
    assert service.inspect_session("studio-automation")["pending_preview"] is None
    assert service._get_session("studio-automation").project.head_revision_id() == before


@pytest.mark.parametrize(
    ("operation", "code"),
    [
        (
            {
                "operation_id": "OP-UNKNOWN-LANE",
                "op": "INSERT_POINT",
                "target": {"lane_id": "UNKNOWN-LANE"},
                "point": {"point_id": "P-X", "beat": 1.0, "value": 0.5, "interpolation": "linear"},
            },
            "UNKNOWN_LANE",
        ),
        (
            {
                "operation_id": "OP-UNKNOWN-POINT",
                "op": "SET_VALUE",
                "target": {"lane_id": "A-MIX-GAIN", "point_id": "UNKNOWN-POINT"},
                "value": 0.5,
            },
            "UNKNOWN_POINT",
        ),
        (
            {
                "operation_id": "OP-DUPLICATE-POINT",
                "op": "INSERT_POINT",
                "target": {"lane_id": "A-MIX-GAIN"},
                "point": {"point_id": "P-GAIN-001", "beat": 2.0, "value": 0.5, "interpolation": "linear"},
            },
            "UNREPRESENTABLE_EDIT",
        ),
        (
            {
                "operation_id": "OP-OCCUPIED-BEAT",
                "op": "MOVE_POINT",
                "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-002"},
                "beat": 0.0,
            },
            "INVALID_TIME",
        ),
        (
            {
                "operation_id": "OP-RANGE",
                "op": "SET_VALUE",
                "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-001"},
                "value": 2.0,
            },
            "INVALID_VALUE",
        ),
    ],
)
def test_identity_time_and_range_failures_are_visible_without_preview(tmp_path: Path, operation: dict, code: str) -> None:
    parent = automation_blueprint()
    service, surface = open_session(tmp_path, parent)
    result = surface.preview_automation_edit("studio-automation", candidate=candidate(parent, [operation]))
    assert result["preview_installed"] is False
    assert result["authority_result"]["status"] == "BLOCKED"
    assert result["authority_result"]["conflicts"][0]["code"] == code
    assert service.inspect_session("studio-automation")["pending_preview"] is None


def test_hard_exact_lock_blocks_value_change_and_installs_no_preview(tmp_path: Path) -> None:
    parent = automation_blueprint(locked=True)
    service, surface = open_session(tmp_path, parent)
    operation = {
        "operation_id": "OP-LOCKED-VALUE",
        "op": "SET_VALUE",
        "target": {"lane_id": "B-SYNTH-CUTOFF", "point_id": "P-CUTOFF-001"},
        "value": 1200.0,
    }
    result = surface.preview_automation_edit("studio-automation", candidate=candidate(parent, [operation]))
    assert result["preview_installed"] is False
    assert result["authority_result"]["status"] == "BLOCKED"
    assert result["authority_result"]["conflicts"][0]["code"] == "HARD_LOCK_VIOLATION"
    assert service.inspect_session("studio-automation")["pending_preview"] is None


def test_preview_accepts_once_through_existing_m2_and_survives_reopen(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, surface = open_session(tmp_path, parent)
    project = service._get_session("studio-automation").project
    root = project.head_revision_id()
    result = surface.preview_automation_edit(
        "studio-automation",
        candidate=candidate(parent, [operation_case("SET_VALUE")]),
    )
    candidate_revision = result["preview"]["candidate_revision_id"]
    assert project.head_revision_id() == root

    accepted = service.accept_preview("studio-automation")
    assert accepted["revision_record"]["revision_id"] == candidate_revision
    assert project.head_revision_id() == candidate_revision
    assert accepted["project_verification"]["status"] == "PASS"
    assert len(service.revision_history("studio-automation")["revisions"]) == 2

    service.close_session("studio-automation")
    service.open_project_session(project_slug="automation-song", session_id="studio-reopen")
    reopened = StudioAutomationSurface(service).automation_view("studio-reopen")
    lane = next(lane for lane in reopened["lanes"] if lane["lane_id"] == "A-MIX-GAIN")
    point = next(point for point in lane["points"] if point["point_id"] == "P-GAIN-001")
    assert point["value"] == 0.71
    assert reopened["revision_id"] == candidate_revision


def test_preview_discard_preserves_accepted_ref(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, surface = open_session(tmp_path, parent)
    project = service._get_session("studio-automation").project
    before = project.head_revision_id()
    surface.preview_automation_edit("studio-automation", candidate=candidate(parent, [operation_case("MOVE_POINT")]))
    discarded = service.discard_preview("studio-automation")
    assert discarded["head_revision_id"] == before
    assert project.head_revision_id() == before
    assert surface.automation_view("studio-automation")["preview"] is None


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


def test_http_automation_routes_and_same_origin_assets(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, _surface = open_session(tmp_path, parent)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        status, payload = _http_json(f"{base}/v0/sessions/studio-automation/automation")
        assert status == 200
        assert payload["ok"] is True
        assert payload["data"]["automation_editing_available"] is True
        assert payload["data"]["capabilities"]["audible_automation_validated"] is False

        edit = candidate(parent, [operation_case("SET_INTERPOLATION")])
        status, payload = _http_json(
            f"{base}/v0/sessions/studio-automation/preview/automation",
            method="POST",
            body={"candidate": edit},
        )
        assert status == 200
        assert payload["data"]["preview_installed"] is True
        assert service._get_session("studio-automation").project.head_revision_id() == parent["project"]["revision_id"]

        with urlopen(f"{base}/assets/app.js", timeout=5) as response:  # noqa: S310
            script = response.read().decode("utf-8")
        with urlopen(f"{base}/assets/app.css", timeout=5) as response:  # noqa: S310
            style = response.read().decode("utf-8")
        assert "MUSICA_AUTOMATION" in script
        assert "/preview/automation" in script
        assert "m7-lane-plot" in style
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
