"""Generate M7-R2 real-browser canonical automation E2E evidence.

The Browser is a non-canonical projection/editor only. Every proposal is source-bound
and resolved by the already-validated M7-R1 authority; explicit Accept remains the M2
project mutation boundary. M7-R2 does not claim audible automation lowering/rendering.
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import threading
from pathlib import Path
from typing import Any

from .automation_edit import automation_material_sha256, blueprint_sha256
from .contracts import validate_contract
from .evidence import artifact_record, write_canonical_json
from .project import create_project
from .studio import StudioService
from .studio_automation import StudioAutomationSurface
from .studio_http import create_local_server

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"
LOCK_PATH = ROOT / "examples" / "automation" / "valid" / "automation-lock-v0.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _blueprint(
    project_id: str,
    revision_id: str,
    *,
    automation: bool = True,
    lock_kind: str | None = None,
) -> dict[str, Any]:
    value = _load(BLUEPRINT_PATH)
    value["project"]["project_id"] = project_id
    value["project"]["revision_id"] = revision_id
    value["project"]["parent_revision_id"] = None
    if automation:
        material = _load(AUTOMATION_PATH)
        cutoff = next(lane for lane in material["lanes"] if lane["lane_id"] == "B-SYNTH-CUTOFF")
        cutoff["section_id"] = "S01"
        value["materials"]["automation"] = material
        if lock_kind == "exact":
            value["materials"]["automation_locks"] = [_load(LOCK_PATH)]
        elif lock_kind == "presence":
            value["materials"]["automation_locks"] = [
                {
                    "lock_version": "0",
                    "lock_id": "L-M7-R2-PRESENCE",
                    "strength": "HARD",
                    "selector": {
                        "lane_id": "A-MIX-GAIN",
                        "point_id": "P-GAIN-002",
                        "parameter_id": "mix.gain",
                        "property": "point",
                    },
                    "mode": "presence",
                    "inheriting": True,
                    "reason": "M7-R2 real-browser evidence protects point presence.",
                }
            ]
    validate_contract(value, "music-blueprint-v0.schema.json")
    return value


def _candidate(
    parent: dict[str, Any], *, candidate_id: str, operation: dict[str, Any], actor: str
) -> dict[str, Any]:
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
        "actor": {"kind": "user", "actor_id": actor},
        "reason": "M7-R2 concurrent accepted automation revision for stale-source evidence.",
        "operations": [operation],
        "preview_only": True,
    }


def _start_server(workspace: Path):
    service = StudioService(workspace)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01},
        daemon=True,
    )
    thread.start()
    host, port = server.server_address[:2]
    return service, server, thread, f"http://{host}:{port}"


def _stop_server(server, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    if thread.is_alive():
        raise RuntimeError("Studio HTTP server thread did not stop cleanly")


def _session(page) -> dict[str, Any]:
    raw = page.locator("#jsonView").text_content() or "{}"
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise RuntimeError("Browser session JSON is not an object")
    return value


def _automation(page) -> dict[str, Any]:
    value = page.evaluate(
        """() => ({
          view: window.MUSICA_AUTOMATION ? JSON.parse(JSON.stringify(window.MUSICA_AUTOMATION.state.view)) : null,
          selectedKey: window.MUSICA_AUTOMATION ? window.MUSICA_AUTOMATION.state.selectedKey : null,
          lastSubmittedCandidate: window.MUSICA_AUTOMATION ? JSON.parse(JSON.stringify(window.MUSICA_AUTOMATION.state.lastSubmittedCandidate)) : null,
          lastAuthorityResult: window.MUSICA_AUTOMATION ? JSON.parse(JSON.stringify(window.MUSICA_AUTOMATION.state.lastAuthorityResult)) : null,
        })"""
    )
    if not isinstance(value, dict):
        raise RuntimeError("Browser automation state is unavailable")
    return value


def _screenshot(page, path: Path) -> Path:
    page.screenshot(path=str(path), full_page=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Browser screenshot was not created: {path}")
    return path


def _attach_page_observers(page, console_errors: list[str], page_errors: list[str], request_failures: list[str]) -> None:
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.on(
        "requestfailed",
        lambda request: request_failures.append(f"{request.method} {request.url}: {request.failure}"),
    )


def _open_project(page, base: str, expect, slug: str, *, available: bool) -> dict[str, Any]:
    page.goto(base + "/", wait_until="domcontentloaded")
    expect(page.locator("#connectionBadge")).to_contain_text("READY")
    page.locator("#openProjectSlug").fill(slug)
    page.locator("#openForm button[type=submit]").click()
    expect(page.locator("#activeProject")).to_be_visible()
    expect(page.locator("#notice")).to_contain_text("Project opened")
    expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
    page.locator('button[data-tab="inspect"]').click()
    expect(page.locator("#panel-inspect")).to_be_visible()
    if available:
        expect(page.locator("#m7AutomationAvailability")).to_have_text("AUTOMATION · READY")
        expect(page.locator("#m7AutomationWorkspace")).to_be_visible()
        expect(page.locator("#m7AutomationLanes .m7-lane")).to_have_count(2)
        expect(page.locator("#m7AutomationLanes .m7-point.accepted")).to_have_count(4)
    else:
        expect(page.locator("#m7AutomationAvailability")).to_have_text("NO CANONICAL AUTOMATION")
        expect(page.locator("#m7AutomationUnavailable")).to_be_visible()
    return _session(page)


def _select_point(page, expect, lane_id: str, point_id: str) -> None:
    point = page.locator(
        f'#m7AutomationLanes button.m7-point[data-lane-id="{lane_id}"][data-point-id="{point_id}"]'
    ).first
    expect(point).to_be_visible()
    point.click()
    expect(page.locator("#m7SelectedPoint")).to_contain_text(point_id)
    expect(page.locator("#m7SelectedPoint")).to_contain_text(lane_id)


def _wait_preview(page, expect) -> tuple[dict[str, Any], dict[str, Any]]:
    expect(page.locator("#projectStateBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
    expect(page.locator("#m7AutomationPreviewBadge")).to_have_text("PREVIEW AUTOMATION · NOT ACCEPTED")
    session = _session(page)
    state = _automation(page)
    if not state["view"] or not state["view"].get("preview"):
        raise RuntimeError("Real browser did not expose pending automation Preview")
    authority = state.get("lastAuthorityResult") or {}
    if authority.get("status") != "READY_FOR_PREVIEW":
        raise RuntimeError("Browser automation Preview did not pass trusted authority")
    return session, state


def _discard(page, expect, expected_head: str) -> None:
    page.locator("#discardButton").click()
    expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
    expect(page.locator("#m7AutomationPreviewBadge")).to_have_text("ACCEPTED AUTOMATION")
    page.wait_for_function(
        "() => window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state.view && !window.MUSICA_AUTOMATION.state.view.preview"
    )
    if str(_session(page)["head_revision_id"]) != expected_head:
        raise RuntimeError("Discard changed the accepted automation project ref")


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("M7-R2 requires browser evidence dependencies: install with .[dev,e2e]") from exc

    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    workspace = root / "workspace"
    workspace.mkdir()

    base = _blueprint("PRJ-M7-R2-AUTO", "rev-m7-r2-auto-r1")
    locked = _blueprint("PRJ-M7-R2-LOCKED", "rev-m7-r2-locked-r1", lock_kind="exact")
    presence = _blueprint("PRJ-M7-R2-PRESENCE", "rev-m7-r2-presence-r1", lock_kind="presence")
    stale = _blueprint("PRJ-M7-R2-STALE", "rev-m7-r2-stale-r1")
    legacy = _blueprint("PRJ-M7-R2-LEGACY", "rev-m7-r2-legacy-r1", automation=False)
    for slug, blueprint in (
        ("automation", base),
        ("locked", locked),
        ("presence", presence),
        ("stale", stale),
        ("legacy", legacy),
    ):
        create_project(workspace / f"{slug}.musica", blueprint)

    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []
    screenshots: list[Path] = []
    operation_outcomes: list[dict[str, Any]] = []

    service1, server1, thread1, base_url1 = _start_server(workspace)
    server1_stopped = False

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1500, "height": 1300}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        try:
            page = context.new_page()
            _attach_page_observers(page, console_errors, page_errors, request_failures)
            initial_session = _open_project(page, base_url1, expect, "automation", available=True)
            source_state = _automation(page)
            source_view = source_state["view"]
            if not source_view:
                raise RuntimeError("Browser automation view did not load")
            if (
                source_view["blueprint_sha256"] != blueprint_sha256(base)
                or source_view["automation_material_sha256"] != automation_material_sha256(base)
            ):
                raise RuntimeError("Browser automation view is not bound to accepted source hashes")
            accepted_root = str(initial_session["head_revision_id"])
            screenshots.append(_screenshot(page, root / "01-automation-accepted.png"))

            # MOVE_POINT -> Preview -> Discard.
            _select_point(page, expect, "A-MIX-GAIN", "P-GAIN-002")
            page.locator("#m7PointBeat").fill("6")
            page.locator("#m7PreviewPointChanges").click()
            preview_session, state = _wait_preview(page, expect)
            if [item["op"] for item in state["lastSubmittedCandidate"]["operations"]] != ["MOVE_POINT"]:
                raise RuntimeError("Browser did not submit exactly MOVE_POINT")
            operation_outcomes.append({"operation": "MOVE_POINT", "candidate": state["lastSubmittedCandidate"], "authority_result": state["lastAuthorityResult"], "accepted_head_before_accept": preview_session["head_revision_id"], "resolution": "DISCARD"})
            _discard(page, expect, accepted_root)

            # SET_INTERPOLATION -> Preview -> Discard.
            _select_point(page, expect, "A-MIX-GAIN", "P-GAIN-001")
            page.locator("#m7PointInterpolation").select_option("hold")
            page.locator("#m7PreviewPointChanges").click()
            preview_session, state = _wait_preview(page, expect)
            if [item["op"] for item in state["lastSubmittedCandidate"]["operations"]] != ["SET_INTERPOLATION"]:
                raise RuntimeError("Browser did not submit exactly SET_INTERPOLATION")
            operation_outcomes.append({"operation": "SET_INTERPOLATION", "candidate": state["lastSubmittedCandidate"], "authority_result": state["lastAuthorityResult"], "accepted_head_before_accept": preview_session["head_revision_id"], "resolution": "DISCARD"})
            _discard(page, expect, accepted_root)

            # DELETE_POINT -> Preview -> Discard.
            _select_point(page, expect, "A-MIX-GAIN", "P-GAIN-002")
            page.locator("#m7DeletePoint").click()
            preview_session, state = _wait_preview(page, expect)
            if [item["op"] for item in state["lastSubmittedCandidate"]["operations"]] != ["DELETE_POINT"]:
                raise RuntimeError("Browser did not submit exactly DELETE_POINT")
            operation_outcomes.append({"operation": "DELETE_POINT", "candidate": state["lastSubmittedCandidate"], "authority_result": state["lastAuthorityResult"], "accepted_head_before_accept": preview_session["head_revision_id"], "resolution": "DISCARD"})
            _discard(page, expect, accepted_root)

            # INSERT_POINT -> Preview -> Discard.
            page.locator("#m7InsertLane").select_option("A-MIX-GAIN")
            page.locator("#m7InsertPointId").fill("P-GAIN-UI-003")
            page.locator("#m7InsertBeat").fill("2")
            page.locator("#m7InsertValue").fill("0.72")
            page.locator("#m7InsertInterpolation").select_option("linear")
            page.locator("#m7InsertPoint").click()
            preview_session, state = _wait_preview(page, expect)
            if [item["op"] for item in state["lastSubmittedCandidate"]["operations"]] != ["INSERT_POINT"]:
                raise RuntimeError("Browser did not submit exactly INSERT_POINT")
            operation_outcomes.append({"operation": "INSERT_POINT", "candidate": state["lastSubmittedCandidate"], "authority_result": state["lastAuthorityResult"], "accepted_head_before_accept": preview_session["head_revision_id"], "resolution": "DISCARD"})
            screenshots.append(_screenshot(page, root / "02-insert-preview-not-accepted.png"))
            _discard(page, expect, accepted_root)

            # SET_VALUE -> Preview -> explicit Accept through existing Studio/M2 boundary.
            _select_point(page, expect, "A-MIX-GAIN", "P-GAIN-001")
            page.locator("#m7PointValue").fill("0.71")
            page.locator("#m7PreviewPointChanges").click()
            preview_session, state = _wait_preview(page, expect)
            if [item["op"] for item in state["lastSubmittedCandidate"]["operations"]] != ["SET_VALUE"]:
                raise RuntimeError("Browser did not submit exactly SET_VALUE")
            accepted_candidate_revision = str(state["view"]["preview"]["candidate_revision_id"])
            operation_outcomes.append({"operation": "SET_VALUE", "candidate": state["lastSubmittedCandidate"], "authority_result": state["lastAuthorityResult"], "accepted_head_before_accept": preview_session["head_revision_id"], "resolution": "ACCEPT"})
            screenshots.append(_screenshot(page, root / "03-value-preview-not-accepted.png"))
            page.locator("#acceptButton").click()
            expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
            expect(page.locator("#m7AutomationPreviewBadge")).to_have_text("ACCEPTED AUTOMATION")
            page.wait_for_function("() => window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state.view && !window.MUSICA_AUTOMATION.state.view.preview")
            accepted_session = _session(page)
            accepted_view = _automation(page)["view"]
            if str(accepted_session["head_revision_id"]) != accepted_candidate_revision:
                raise RuntimeError("Explicit Browser Accept did not advance to automation candidate")
            accepted_lane = next(lane for lane in accepted_view["lanes"] if lane["lane_id"] == "A-MIX-GAIN")
            accepted_point = next(point for point in accepted_lane["points"] if point["point_id"] == "P-GAIN-001")
            if float(accepted_point["value"]) != 0.71:
                raise RuntimeError("Accepted automation SET_VALUE did not persist")
            screenshots.append(_screenshot(page, root / "04-value-accepted.png"))
            page.close()

            # HARD exact-value lock conflict is visible; no Preview and no ref advance.
            lock_page = context.new_page()
            _attach_page_observers(lock_page, console_errors, page_errors, request_failures)
            locked_session = _open_project(lock_page, base_url1, expect, "locked", available=True)
            locked_head = str(locked_session["head_revision_id"])
            _select_point(lock_page, expect, "B-SYNTH-CUTOFF", "P-CUTOFF-001")
            expect(lock_page.locator('#m7SelectedLocks .m7-lock-badge[data-lock-id="L-M7R0-CUTOFF"]')).to_be_visible()
            lock_page.locator("#m7PointValue").fill("1200")
            lock_page.locator("#m7PreviewPointChanges").click()
            expect(lock_page.locator("#m7AutomationStatus")).to_contain_text("HARD_LOCK_VIOLATION")
            expect(lock_page.locator("#m7AutomationStatus")).to_contain_text("L-M7R0-CUTOFF")
            lock_state = _automation(lock_page)
            lock_server = service1.inspect_session(str(locked_session["session_id"]))
            if lock_state["lastAuthorityResult"]["status"] != "BLOCKED":
                raise RuntimeError("HARD exact automation lock was not BLOCKED")
            if lock_server["pending_preview"] is not None or str(lock_server["head_revision_id"]) != locked_head:
                raise RuntimeError("HARD exact lock installed Preview or changed accepted ref")
            hard_exact_evidence = {"status_text": lock_page.locator("#m7AutomationStatus").text_content(), "candidate": lock_state["lastSubmittedCandidate"], "authority_result": lock_state["lastAuthorityResult"], "automation_view": lock_state["view"], "server_session": lock_server}
            screenshots.append(_screenshot(lock_page, root / "05-hard-exact-blocked.png"))
            lock_page.close()

            # HARD point-presence lock blocks deletion through the same visible control.
            presence_page = context.new_page()
            _attach_page_observers(presence_page, console_errors, page_errors, request_failures)
            presence_session = _open_project(presence_page, base_url1, expect, "presence", available=True)
            presence_head = str(presence_session["head_revision_id"])
            _select_point(presence_page, expect, "A-MIX-GAIN", "P-GAIN-002")
            expect(presence_page.locator('#m7SelectedLocks .m7-lock-badge[data-lock-id="L-M7-R2-PRESENCE"]')).to_be_visible()
            presence_page.locator("#m7DeletePoint").click()
            expect(presence_page.locator("#m7AutomationStatus")).to_contain_text("HARD_LOCK_VIOLATION")
            expect(presence_page.locator("#m7AutomationStatus")).to_contain_text("L-M7-R2-PRESENCE")
            presence_state = _automation(presence_page)
            presence_server = service1.inspect_session(str(presence_session["session_id"]))
            if presence_state["lastAuthorityResult"]["status"] != "BLOCKED":
                raise RuntimeError("HARD presence automation lock was not BLOCKED")
            if presence_server["pending_preview"] is not None or str(presence_server["head_revision_id"]) != presence_head:
                raise RuntimeError("HARD presence lock installed Preview or changed accepted ref")
            hard_presence_evidence = {"status_text": presence_page.locator("#m7AutomationStatus").text_content(), "candidate": presence_state["lastSubmittedCandidate"], "authority_result": presence_state["lastAuthorityResult"], "automation_view": presence_state["view"], "server_session": presence_server}
            screenshots.append(_screenshot(presence_page, root / "06-hard-presence-blocked.png"))
            presence_page.close()

            # Concurrent accepted automation revision makes Browser source stale; no silent rebase.
            stale_page = context.new_page()
            _attach_page_observers(stale_page, console_errors, page_errors, request_failures)
            stale_session = _open_project(stale_page, base_url1, expect, "stale", available=True)
            stale_sid = str(stale_session["session_id"])
            stale_browser_source = copy.deepcopy(_automation(stale_page)["view"])
            stale_project = service1._get_session(stale_sid).project
            stale_parent_id = stale_project.head_revision_id()
            stale_parent = stale_project.read_revision(stale_parent_id)
            concurrent_candidate = _candidate(
                stale_parent,
                candidate_id="AEC-M7-R2-CONCURRENT",
                actor="m7-r2-concurrent",
                operation={
                    "operation_id": "OP-M7-R2-CONCURRENT-VALUE",
                    "op": "SET_VALUE",
                    "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-001"},
                    "value": 0.69,
                },
            )
            concurrent = StudioAutomationSurface(service1).preview_automation_edit(stale_sid, candidate=concurrent_candidate)
            if not concurrent["preview_installed"]:
                raise RuntimeError("Concurrent automation setup failed to install Preview")
            concurrent_revision = str(concurrent["preview"]["candidate_revision_id"])
            service1.accept_preview(stale_sid)
            if stale_project.head_revision_id() != concurrent_revision:
                raise RuntimeError("Concurrent accepted automation revision setup failed")

            _select_point(stale_page, expect, "A-MIX-GAIN", "P-GAIN-002")
            stale_page.locator("#m7PointBeat").fill("7")
            stale_page.locator("#m7PreviewPointChanges").click()
            expect(stale_page.locator("#m7AutomationStatus")).to_contain_text("STALE_SOURCE")
            stale_state = _automation(stale_page)
            stale_server = service1.inspect_session(stale_sid)
            if stale_state["lastAuthorityResult"]["status"] != "BLOCKED":
                raise RuntimeError("Stale Browser automation candidate was not BLOCKED")
            if stale_server["pending_preview"] is not None:
                raise RuntimeError("Stale Browser automation candidate installed Preview")
            if str(stale_server["head_revision_id"]) != concurrent_revision:
                raise RuntimeError("Stale Browser automation candidate changed concurrent accepted ref")
            if stale_state["view"]["revision_id"] != concurrent_revision:
                raise RuntimeError("Blocked stale response did not rebind Browser automation view")
            stale_evidence = {"browser_source_before_conflict": stale_browser_source, "concurrent_candidate": concurrent_candidate, "concurrent_revision_id": concurrent_revision, "status_text": stale_page.locator("#m7AutomationStatus").text_content(), "candidate": stale_state["lastSubmittedCandidate"], "authority_result": stale_state["lastAuthorityResult"], "automation_view_after_block": stale_state["view"], "server_session": stale_server}
            screenshots.append(_screenshot(stale_page, root / "07-stale-source-blocked.png"))
            stale_page.close()

            # Legacy accepted Blueprint remains explicit empty state; no reverse inference.
            legacy_page = context.new_page()
            _attach_page_observers(legacy_page, console_errors, page_errors, request_failures)
            _open_project(legacy_page, base_url1, expect, "legacy", available=False)
            legacy_state = _automation(legacy_page)
            legacy_view = legacy_state["view"]
            if legacy_view["automation_editing_available"] is not False or legacy_view["lanes"] != []:
                raise RuntimeError("Legacy Browser project fabricated canonical automation lanes")
            unavailable_text = legacy_page.locator("#m7AutomationUnavailable").text_content() or ""
            if "will not reverse-infer" not in unavailable_text:
                raise RuntimeError("Legacy Browser UX does not explain no-reverse-inference boundary")
            screenshots.append(_screenshot(legacy_page, root / "08-legacy-no-automation.png"))
            legacy_page.close()

            # Restart/reopen proves accepted automation state survives service/browser restart.
            _stop_server(server1, thread1)
            server1_stopped = True
            service2, server2, thread2, base_url2 = _start_server(workspace)
            reopen_page = context.new_page()
            _attach_page_observers(reopen_page, console_errors, page_errors, request_failures)
            try:
                reopened_session = _open_project(reopen_page, base_url2, expect, "automation", available=True)
                reopened_view = _automation(reopen_page)["view"]
                if str(reopened_session["head_revision_id"]) != accepted_candidate_revision:
                    raise RuntimeError("Restart/reopen did not preserve accepted automation revision")
                reopened_lane = next(lane for lane in reopened_view["lanes"] if lane["lane_id"] == "A-MIX-GAIN")
                reopened_point = next(point for point in reopened_lane["points"] if point["point_id"] == "P-GAIN-001")
                if float(reopened_point["value"]) != 0.71:
                    raise RuntimeError("Restart/reopen did not preserve accepted automation value")
                if service2.inspect_session(str(reopened_session["session_id"]))["integrity_status"] != "PASS":
                    raise RuntimeError("Restart/reopen project integrity failed")
                screenshots.append(_screenshot(reopen_page, root / "09-reopened-accepted.png"))
            finally:
                reopen_page.close()
                _stop_server(server2, thread2)
        finally:
            if not server1_stopped:
                _stop_server(server1, thread1)
            context.close()
            browser.close()

    if console_errors:
        raise RuntimeError(f"Browser console errors detected: {console_errors}")
    if page_errors:
        raise RuntimeError(f"Browser page errors detected: {page_errors}")

    operation_names = [item["operation"] for item in operation_outcomes]
    required_operations = ["INSERT_POINT", "DELETE_POINT", "MOVE_POINT", "SET_VALUE", "SET_INTERPOLATION"]
    all_five = sorted(operation_names) == sorted(required_operations)
    ref_unchanged = all(str(item["accepted_head_before_accept"]) == accepted_root for item in operation_outcomes)
    hard_exact_conflicts = hard_exact_evidence["authority_result"]["conflicts"]
    hard_presence_conflicts = hard_presence_evidence["authority_result"]["conflicts"]
    stale_conflicts = stale_evidence["authority_result"]["conflicts"]

    proof = {
        "proof_version": "0",
        "real_chromium_used": True,
        "automation_project_opened_in_real_browser": True,
        "browser_source_bound_to_project_revision_blueprint_and_material_hash": (
            source_view["project_id"] == base["project"]["project_id"]
            and source_view["revision_id"] == base["project"]["revision_id"]
            and source_view["blueprint_sha256"] == blueprint_sha256(base)
            and source_view["automation_material_sha256"] == automation_material_sha256(base)
        ),
        "stable_lane_point_dom_identity_present": True,
        "all_five_operations_browser_exercised": all_five,
        "accepted_ref_unchanged_before_accept": ref_unchanged,
        "preview_not_accepted_visible": True,
        "explicit_accept_advanced_once_to_candidate": accepted_session["head_revision_id"] == accepted_candidate_revision,
        "discard_preserved_accepted_ref": all(item["resolution"] != "DISCARD" or item["accepted_head_before_accept"] == accepted_root for item in operation_outcomes),
        "accepted_value_preserved": float(accepted_point["value"]) == 0.71,
        "accepted_state_survives_restart_reopen": reopened_view["revision_id"] == accepted_candidate_revision and float(reopened_point["value"]) == 0.71,
        "hard_exact_lock_blocked": hard_exact_evidence["authority_result"]["status"] == "BLOCKED" and hard_exact_conflicts[0]["code"] == "HARD_LOCK_VIOLATION",
        "hard_exact_lock_rule_context_visible": "L-M7R0-CUTOFF" in str(hard_exact_evidence["status_text"]),
        "hard_exact_preview_installed": hard_exact_evidence["server_session"]["pending_preview"] is not None,
        "hard_presence_lock_blocked": hard_presence_evidence["authority_result"]["status"] == "BLOCKED" and hard_presence_conflicts[0]["code"] == "HARD_LOCK_VIOLATION",
        "hard_presence_rule_context_visible": "L-M7-R2-PRESENCE" in str(hard_presence_evidence["status_text"]),
        "hard_presence_preview_installed": hard_presence_evidence["server_session"]["pending_preview"] is not None,
        "stale_source_blocked": stale_evidence["authority_result"]["status"] == "BLOCKED" and stale_conflicts[0]["code"] == "STALE_SOURCE",
        "stale_preview_installed": stale_evidence["server_session"]["pending_preview"] is not None,
        "stale_response_rebound_to_current_accepted_source": stale_evidence["automation_view_after_block"]["revision_id"] == concurrent_revision,
        "legacy_reports_automation_unavailable": legacy_view["automation_editing_available"] is False,
        "legacy_has_no_fabricated_lanes": legacy_view["lanes"] == [],
        "browser_project_mutation_authorized": source_view["capabilities"]["project_mutation_authorized"],
        "music_ir_mutation_authorized": source_view["capabilities"]["music_ir_mutation_authorized"],
        "audible_automation_validated": source_view["capabilities"]["audible_automation_validated"],
        "external_provider_network_required": False,
        "browser_console_error_count": len(console_errors),
        "browser_page_error_count": len(page_errors),
    }

    required_true = [
        "real_chromium_used",
        "automation_project_opened_in_real_browser",
        "browser_source_bound_to_project_revision_blueprint_and_material_hash",
        "stable_lane_point_dom_identity_present",
        "all_five_operations_browser_exercised",
        "accepted_ref_unchanged_before_accept",
        "preview_not_accepted_visible",
        "explicit_accept_advanced_once_to_candidate",
        "discard_preserved_accepted_ref",
        "accepted_value_preserved",
        "accepted_state_survives_restart_reopen",
        "hard_exact_lock_blocked",
        "hard_exact_lock_rule_context_visible",
        "hard_presence_lock_blocked",
        "hard_presence_rule_context_visible",
        "stale_source_blocked",
        "stale_response_rebound_to_current_accepted_source",
        "legacy_reports_automation_unavailable",
        "legacy_has_no_fabricated_lanes",
    ]
    if not all(bool(proof[key]) for key in required_true):
        raise RuntimeError("M7-R2 real-browser positive/negative proof failed")
    if proof["hard_exact_preview_installed"] or proof["hard_presence_preview_installed"] or proof["stale_preview_installed"]:
        raise RuntimeError("Blocked M7-R2 conflict installed a pending Preview")
    if proof["browser_project_mutation_authorized"] or proof["music_ir_mutation_authorized"] or proof["audible_automation_validated"]:
        raise RuntimeError("M7-R2 Browser/audible authority boundary was violated")

    tracked: list[Path] = [
        write_canonical_json(root / "source-automation-view.json", source_view),
        write_canonical_json(root / "operation-outcomes.json", operation_outcomes),
        write_canonical_json(root / "accepted-automation-view.json", accepted_view),
        write_canonical_json(root / "reopened-automation-view.json", reopened_view),
        write_canonical_json(root / "hard-exact-browser.json", hard_exact_evidence),
        write_canonical_json(root / "hard-presence-browser.json", hard_presence_evidence),
        write_canonical_json(root / "stale-source-browser.json", stale_evidence),
        write_canonical_json(root / "legacy-automation-view.json", legacy_view),
        write_canonical_json(
            root / "browser-runtime.json",
            {"console_errors": console_errors, "page_errors": page_errors, "request_failures": request_failures},
        ),
        write_canonical_json(root / "proof.json", proof),
    ]
    tracked.extend(screenshots)
    manifest = {
        "manifest_version": "0",
        "evidence_class": "REAL_BROWSER_AUTOMATION_E2E_EVIDENCE",
        "evidence_scope": "M7-R2-Real-Browser-Canonical-Automation-E2E-v0",
        "browser": "Playwright Chromium",
        "source_blueprint_sha256": blueprint_sha256(base),
        "source_automation_material_sha256": automation_material_sha256(base),
        "accepted_revision_id": accepted_candidate_revision,
        "accepted_blueprint_sha256": accepted_view["blueprint_sha256"],
        "accepted_automation_material_sha256": accepted_view["automation_material_sha256"],
        "proof": proof,
        "claim_boundary": [
            "real Chromium Browser Studio automation projection/edit E2E",
            "all five M7-R1 primitive point operations through visible browser controls",
            "stable lane_id/point_id identities with geometry treated as presentation only",
            "Preview remains non-canonical until explicit existing M2 Accept",
            "Discard preserves accepted state",
            "visible HARD exact/presence and stale-source fail-closed conflict UX",
            "restart/reopen persistence of accepted canonical automation state",
            "legacy project no-reverse-inference behavior",
            "not automation lowering into Music IR",
            "not audible automation rendering evidence",
            "not plug-in/device automation mapping",
            "not DAW automation reconciliation",
            "not human-subject usability or perceptual evidence",
        ],
        "artifacts": [artifact_record(path, root) for path in sorted(tracked, key=lambda item: item.relative_to(root).as_posix())],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M7-R2 real-browser automation evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
