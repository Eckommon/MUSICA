"""Generate M6-R3 real-browser exact-note E2E and conflict-UX evidence.

This suite proves the already validated M6-R2 Browser Studio precision surface through
real Playwright Chromium. Browser/DOM state remains non-canonical: every edit still
passes through the M6-R1 trusted authority and existing M2 Accept/Discard boundary.
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import threading
from pathlib import Path
from typing import Any

from .contracts import validate_contract
from .evidence import artifact_record, write_canonical_json
from .note_edit import blueprint_sha256
from .project import create_project
from .studio import StudioService
from .studio_http import create_local_server
from .studio_notes import StudioNoteSurface

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
MATERIAL_PATH = ROOT / "examples" / "note-material" / "valid" / "dark-electronic-explicit-timeline-v0.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _blueprint(project_id: str, revision_id: str, *, exact: bool = True, locked: bool = False) -> dict[str, Any]:
    value = _load(BLUEPRINT_PATH)
    value["project"]["project_id"] = project_id
    value["project"]["revision_id"] = revision_id
    value["project"]["parent_revision_id"] = None
    if exact:
        value["materials"]["melody"]["exact_timeline"] = _load(MATERIAL_PATH)
    if locked:
        value["materials"]["melody"]["exact_note_locks"] = [
            {
                "lock_version": "0",
                "lock_id": "L-M6-R3-PITCH",
                "strength": "HARD",
                "selector": {
                    "part_id": "P-SYNTH",
                    "note_id": "N-MOTIF-001",
                    "property": "pitch",
                },
                "mode": "exact",
                "inheriting": True,
                "value": 62,
                "reason": "M6-R3 real-browser HARD-lock conflict evidence.",
            }
        ]
    validate_contract(value, "music-blueprint-v0.schema.json")
    return value


def _candidate(parent: dict[str, Any], *, candidate_id: str, operation: dict[str, Any], actor: str) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_exact_note_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": actor},
        "reason": "M6-R3 concurrent accepted revision for stale-source browser evidence.",
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


def _precision(page) -> dict[str, Any]:
    value = page.evaluate(
        """() => ({
          view: window.MUSICA_PRECISION ? JSON.parse(JSON.stringify(window.MUSICA_PRECISION.state.view)) : null,
          selectedKey: window.MUSICA_PRECISION ? window.MUSICA_PRECISION.state.selectedKey : null,
          lastSubmittedCandidate: window.MUSICA_PRECISION ? JSON.parse(JSON.stringify(window.MUSICA_PRECISION.state.lastSubmittedCandidate)) : null,
          lastAuthorityResult: window.MUSICA_PRECISION ? JSON.parse(JSON.stringify(window.MUSICA_PRECISION.state.lastAuthorityResult)) : null,
        })"""
    )
    if not isinstance(value, dict):
        raise RuntimeError("Browser precision state is unavailable")
    return value


def _screenshot(page, path: Path) -> Path:
    page.screenshot(path=str(path), full_page=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Browser screenshot was not created: {path}")
    return path


def _attach_page_observers(page, console_errors: list[str], page_errors: list[str], request_failures: list[str]) -> None:
    page.on(
        "console",
        lambda message: console_errors.append(message.text) if message.type == "error" else None,
    )
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.on(
        "requestfailed",
        lambda request: request_failures.append(f"{request.method} {request.url}: {request.failure}"),
    )


def _open_project(page, base: str, expect, slug: str, *, exact: bool) -> dict[str, Any]:
    page.goto(base + "/", wait_until="domcontentloaded")
    expect(page.locator("#connectionBadge")).to_contain_text("READY")
    page.locator("#openProjectSlug").fill(slug)
    page.locator("#openForm button[type=submit]").click()
    expect(page.locator("#activeProject")).to_be_visible()
    expect(page.locator("#notice")).to_contain_text("Project opened")
    expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
    page.locator('button[data-tab="inspect"]').click()
    expect(page.locator("#panel-inspect")).to_be_visible()
    if exact:
        expect(page.locator("#m6Availability")).to_have_text("EXACT · READY")
        expect(page.locator("#m6Workspace")).to_be_visible()
        expect(page.locator("#m6PianoRoll button.m6-note.accepted")).to_have_count(3)
    else:
        expect(page.locator("#m6Availability")).to_have_text("LEGACY · READ ONLY")
        expect(page.locator("#m6Unavailable")).to_be_visible()
    return _session(page)


def _select_anchor(page, expect) -> None:
    note = page.locator('#m6PianoRoll button.m6-note[data-note-key="P-SYNTH::N-MOTIF-001"]:not(.ghost)').first
    expect(note).to_be_visible()
    note.click()
    expect(page.locator("#m6SelectedId")).to_contain_text("N-MOTIF-001")


def _wait_preview(page, expect) -> tuple[dict[str, Any], dict[str, Any]]:
    expect(page.locator("#projectStateBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
    expect(page.locator("#m6PreviewBadge")).to_have_text("PREVIEW NOTES · NOT ACCEPTED")
    session = _session(page)
    precision = _precision(page)
    if not precision["view"] or not precision["view"].get("preview"):
        raise RuntimeError("Real browser did not expose a pending exact-note Preview")
    authority = precision.get("lastAuthorityResult") or {}
    if authority.get("status") != "READY_FOR_PREVIEW":
        raise RuntimeError("Browser Preview did not pass trusted authority")
    return session, precision


def _discard(page, expect, expected_head: str) -> None:
    page.locator("#discardButton").click()
    expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
    expect(page.locator("#m6PreviewBadge")).to_have_text("ACCEPTED NOTES")
    page.wait_for_function(
        "() => window.MUSICA_PRECISION && window.MUSICA_PRECISION.state.view && !window.MUSICA_PRECISION.state.view.preview"
    )
    if str(_session(page)["head_revision_id"]) != expected_head:
        raise RuntimeError("Discard changed the accepted project ref")


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("M6-R3 requires browser evidence dependencies: install with .[dev,e2e]") from exc

    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    workspace = root / "workspace"
    workspace.mkdir()

    exact = _blueprint("PRJ-M6-R3-EXACT", "rev-m6-r3-exact-r1")
    locked = _blueprint("PRJ-M6-R3-LOCKED", "rev-m6-r3-locked-r1", locked=True)
    stale = _blueprint("PRJ-M6-R3-STALE", "rev-m6-r3-stale-r1")
    legacy = _blueprint("PRJ-M6-R3-LEGACY", "rev-m6-r3-legacy-r1", exact=False)
    create_project(workspace / "exact.musica", exact)
    create_project(workspace / "locked.musica", locked)
    create_project(workspace / "stale.musica", stale)
    create_project(workspace / "legacy.musica", legacy)

    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []
    screenshots: list[Path] = []
    browser_actions: list[dict[str, Any]] = []
    operation_outcomes: list[dict[str, Any]] = []

    service1, server1, thread1, base1 = _start_server(workspace)
    server1_stopped = False

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1500, "height": 1200}, reduced_motion="reduce")
        context.set_default_timeout(30_000)

        try:
            # R3-E2E-01: open exact-note project and bind Browser UI to accepted source.
            page = context.new_page()
            _attach_page_observers(page, console_errors, page_errors, request_failures)
            initial_session = _open_project(page, base1, expect, "exact", exact=True)
            source_precision = _precision(page)
            source_view = source_precision["view"]
            if not source_view or source_view["blueprint_sha256"] != blueprint_sha256(exact):
                raise RuntimeError("Browser exact-note view is not bound to the accepted Blueprint hash")
            accepted_root = str(initial_session["head_revision_id"])
            screenshots.append(_screenshot(page, root / "01-exact-accepted.png"))
            browser_actions.append({"step": "open_exact", "head": accepted_root, "source": source_view})

            # R3-E2E-02: exercise five operations as visible non-canonical Previews and Discard.
            target_cases = [
                ("MOVE", "#m6Start", "0.25"),
                ("RESIZE", "#m6Duration", "0.5"),
                ("SET_VELOCITY", "#m6Velocity", "91"),
            ]
            for operation, selector, value in target_cases:
                _select_anchor(page, expect)
                page.locator(selector).fill(value)
                page.locator("#m6PreviewChanges").click()
                preview_session, state = _wait_preview(page, expect)
                if str(preview_session["head_revision_id"]) != accepted_root:
                    raise RuntimeError(f"{operation} Preview advanced accepted ref before Accept")
                submitted = state["lastSubmittedCandidate"]
                if not submitted or [item["op"] for item in submitted["operations"]] != [operation]:
                    raise RuntimeError(f"Browser did not submit exactly one {operation} operation")
                operation_outcomes.append(
                    {
                        "operation": operation,
                        "candidate": submitted,
                        "authority_result": state["lastAuthorityResult"],
                        "accepted_head_before_accept": preview_session["head_revision_id"],
                        "preview": state["view"]["preview"],
                        "resolution": "DISCARD",
                    }
                )
                _discard(page, expect, accepted_root)

            _select_anchor(page, expect)
            page.locator("#m6DeleteNote").click()
            preview_session, state = _wait_preview(page, expect)
            if str(preview_session["head_revision_id"]) != accepted_root:
                raise RuntimeError("DELETE Preview advanced accepted ref before Accept")
            if [item["op"] for item in state["lastSubmittedCandidate"]["operations"]] != ["DELETE"]:
                raise RuntimeError("Browser did not submit DELETE")
            operation_outcomes.append(
                {
                    "operation": "DELETE",
                    "candidate": state["lastSubmittedCandidate"],
                    "authority_result": state["lastAuthorityResult"],
                    "accepted_head_before_accept": preview_session["head_revision_id"],
                    "preview": state["view"]["preview"],
                    "resolution": "DISCARD",
                }
            )
            _discard(page, expect, accepted_root)

            page.locator("#m6InsertId").fill("N-M6-R3-INSERT")
            page.locator("#m6InsertStart").fill("1.25")
            page.locator("#m6InsertDuration").fill("0.5")
            page.locator("#m6InsertPitch").fill("67")
            page.locator("#m6InsertVelocity").fill("74")
            page.locator("#m6InsertNote").click()
            preview_session, state = _wait_preview(page, expect)
            if str(preview_session["head_revision_id"]) != accepted_root:
                raise RuntimeError("INSERT Preview advanced accepted ref before Accept")
            if [item["op"] for item in state["lastSubmittedCandidate"]["operations"]] != ["INSERT"]:
                raise RuntimeError("Browser did not submit INSERT")
            operation_outcomes.append(
                {
                    "operation": "INSERT",
                    "candidate": state["lastSubmittedCandidate"],
                    "authority_result": state["lastAuthorityResult"],
                    "accepted_head_before_accept": preview_session["head_revision_id"],
                    "preview": state["view"]["preview"],
                    "resolution": "DISCARD",
                }
            )
            screenshots.append(_screenshot(page, root / "02-insert-preview-not-accepted.png"))
            _discard(page, expect, accepted_root)

            # REPITCH is the sixth operation and the one explicitly accepted through existing M2.
            _select_anchor(page, expect)
            page.locator("#m6Pitch").fill("64")
            page.locator("#m6PreviewChanges").click()
            preview_session, state = _wait_preview(page, expect)
            if str(preview_session["head_revision_id"]) != accepted_root:
                raise RuntimeError("REPITCH Preview advanced accepted ref before Accept")
            if [item["op"] for item in state["lastSubmittedCandidate"]["operations"]] != ["REPITCH"]:
                raise RuntimeError("Browser did not submit REPITCH")
            repitch_candidate_revision = str(state["view"]["preview"]["candidate_revision_id"])
            operation_outcomes.append(
                {
                    "operation": "REPITCH",
                    "candidate": state["lastSubmittedCandidate"],
                    "authority_result": state["lastAuthorityResult"],
                    "accepted_head_before_accept": preview_session["head_revision_id"],
                    "preview": state["view"]["preview"],
                    "resolution": "ACCEPT",
                }
            )
            screenshots.append(_screenshot(page, root / "03-repitch-preview-not-accepted.png"))
            page.locator("#acceptButton").click()
            expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
            expect(page.locator("#m6PreviewBadge")).to_have_text("ACCEPTED NOTES")
            page.wait_for_function(
                "() => window.MUSICA_PRECISION && window.MUSICA_PRECISION.state.view && !window.MUSICA_PRECISION.state.view.preview"
            )
            accepted_session = _session(page)
            accepted_view = _precision(page)["view"]
            if str(accepted_session["head_revision_id"]) != repitch_candidate_revision:
                raise RuntimeError("Explicit browser Accept did not advance to the exact-note candidate")
            accepted_anchor = next(note for note in accepted_view["notes"] if note["note_id"] == "N-MOTIF-001")
            if accepted_anchor["pitch"] != 64:
                raise RuntimeError("Accepted Browser REPITCH did not persist exact pitch 64")
            screenshots.append(_screenshot(page, root / "04-repitch-accepted.png"))
            page.close()

            # R3-E2E-03: HARD-lock conflict through visible controls.
            lock_page = context.new_page()
            _attach_page_observers(lock_page, console_errors, page_errors, request_failures)
            locked_session = _open_project(lock_page, base1, expect, "locked", exact=True)
            locked_head = str(locked_session["head_revision_id"])
            _select_anchor(lock_page, expect)
            lock_badge = lock_page.locator('#m6SelectedLocks .m6-lock-badge[data-lock-id="L-M6-R3-PITCH"]')
            expect(lock_badge).to_be_visible()
            expect(lock_page.locator("#m6Pitch")).to_be_enabled()
            lock_page.locator("#m6Pitch").fill("65")
            lock_page.locator("#m6PreviewChanges").click()
            expect(lock_page.locator("#m6NoteStatus")).to_contain_text("HARD_LOCK_VIOLATION")
            expect(lock_page.locator("#m6NoteStatus")).to_contain_text("N-MOTIF-001")
            expect(lock_page.locator("#m6NoteStatus")).to_contain_text("L-M6-R3-PITCH")
            lock_state = _precision(lock_page)
            lock_server = service1.inspect_session(str(locked_session["session_id"]))
            if lock_state["lastAuthorityResult"]["status"] != "BLOCKED":
                raise RuntimeError("HARD-lock browser proposal was not BLOCKED")
            if lock_server["pending_preview"] is not None or str(lock_server["head_revision_id"]) != locked_head:
                raise RuntimeError("HARD-lock conflict installed Preview or changed accepted ref")
            hard_lock_evidence = {
                "status_text": lock_page.locator("#m6NoteStatus").text_content(),
                "candidate": lock_state["lastSubmittedCandidate"],
                "authority_result": lock_state["lastAuthorityResult"],
                "note_view": lock_state["view"],
                "server_session": lock_server,
            }
            screenshots.append(_screenshot(lock_page, root / "05-hard-lock-blocked.png"))
            lock_page.close()

            # R3-E2E-04: concurrent accepted revision makes browser source stale; no silent rebase.
            stale_page = context.new_page()
            _attach_page_observers(stale_page, console_errors, page_errors, request_failures)
            stale_session = _open_project(stale_page, base1, expect, "stale", exact=True)
            stale_sid = str(stale_session["session_id"])
            stale_browser_source = copy.deepcopy(_precision(stale_page)["view"])
            stale_project = service1._get_session(stale_sid).project
            stale_parent_id = stale_project.head_revision_id()
            stale_parent = stale_project.read_revision(stale_parent_id)
            concurrent_candidate = _candidate(
                stale_parent,
                candidate_id="NEC-M6-R3-CONCURRENT",
                actor="m6-r3-concurrent",
                operation={
                    "operation_id": "OP-M6-R3-CONCURRENT-MOVE",
                    "op": "MOVE",
                    "target": {"part_id": "P-SYNTH", "note_id": "N-MOTIF-001"},
                    "start_beat": 0.5,
                },
            )
            concurrent = StudioNoteSurface(service1).preview_note_edit(stale_sid, candidate=concurrent_candidate)
            if not concurrent["preview_installed"]:
                raise RuntimeError("Concurrent authority setup failed to install Preview")
            concurrent_revision = str(concurrent["preview"]["candidate_revision_id"])
            service1.accept_preview(stale_sid)
            if stale_project.head_revision_id() != concurrent_revision:
                raise RuntimeError("Concurrent accepted revision setup failed")

            _select_anchor(stale_page, expect)
            stale_page.locator("#m6Velocity").fill("88")
            stale_page.locator("#m6PreviewChanges").click()
            expect(stale_page.locator("#m6NoteStatus")).to_contain_text("STALE_SOURCE")
            stale_state = _precision(stale_page)
            stale_server = service1.inspect_session(stale_sid)
            if stale_state["lastAuthorityResult"]["status"] != "BLOCKED":
                raise RuntimeError("Stale browser candidate was not BLOCKED")
            if stale_server["pending_preview"] is not None:
                raise RuntimeError("Stale browser candidate installed a pending Preview")
            if str(stale_server["head_revision_id"]) != concurrent_revision:
                raise RuntimeError("Stale browser candidate changed the concurrently accepted ref")
            if stale_state["view"]["revision_id"] != concurrent_revision:
                raise RuntimeError("Blocked stale response did not rebind Browser note view to current accepted source")
            stale_evidence = {
                "browser_source_before_conflict": stale_browser_source,
                "concurrent_candidate": concurrent_candidate,
                "concurrent_revision_id": concurrent_revision,
                "status_text": stale_page.locator("#m6NoteStatus").text_content(),
                "candidate": stale_state["lastSubmittedCandidate"],
                "authority_result": stale_state["lastAuthorityResult"],
                "note_view_after_block": stale_state["view"],
                "server_session": stale_server,
            }
            screenshots.append(_screenshot(stale_page, root / "06-stale-source-blocked.png"))
            stale_page.close()

            # R3-E2E-05: legacy project remains explicit read-only with no fabricated canonical notes.
            legacy_page = context.new_page()
            _attach_page_observers(legacy_page, console_errors, page_errors, request_failures)
            _open_project(legacy_page, base1, expect, "legacy", exact=False)
            legacy_state = _precision(legacy_page)
            legacy_view = legacy_state["view"]
            if legacy_view["exact_note_editing_available"] is not False or legacy_view["notes"] != []:
                raise RuntimeError("Legacy Browser project fabricated canonical exact notes")
            if "will not fabricate" not in (legacy_page.locator("#m6Unavailable").text_content() or ""):
                raise RuntimeError("Legacy Browser UX does not explain the no-reverse-mapping boundary")
            screenshots.append(_screenshot(legacy_page, root / "07-legacy-read-only.png"))
            legacy_page.close()

            # R3-E2E-06: restart service and reopen accepted exact project in a fresh browser page.
            _stop_server(server1, thread1)
            server1_stopped = True
            service2, server2, thread2, base2 = _start_server(workspace)
            reopen_page = context.new_page()
            _attach_page_observers(reopen_page, console_errors, page_errors, request_failures)
            try:
                reopened_session = _open_project(reopen_page, base2, expect, "exact", exact=True)
                reopened_view = _precision(reopen_page)["view"]
                if str(reopened_session["head_revision_id"]) != repitch_candidate_revision:
                    raise RuntimeError("Restart/reopen did not preserve accepted exact-note revision")
                reopened_anchor = next(note for note in reopened_view["notes"] if note["note_id"] == "N-MOTIF-001")
                if reopened_anchor["pitch"] != 64:
                    raise RuntimeError("Restart/reopen did not preserve accepted REPITCH")
                server_reopened = service2.inspect_session(str(reopened_session["session_id"]))
                if server_reopened["integrity_status"] != "PASS":
                    raise RuntimeError("Restart/reopen project integrity failed")
                screenshots.append(_screenshot(reopen_page, root / "08-reopened-accepted.png"))
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
    required_operations = ["INSERT", "DELETE", "MOVE", "RESIZE", "REPITCH", "SET_VELOCITY"]
    all_six = sorted(operation_names) == sorted(required_operations)
    ref_unchanged = all(str(item["accepted_head_before_accept"]) == accepted_root for item in operation_outcomes)
    hard_conflicts = hard_lock_evidence["authority_result"]["conflicts"]
    stale_conflicts = stale_evidence["authority_result"]["conflicts"]

    proof = {
        "proof_version": "0",
        "real_chromium_used": True,
        "exact_note_project_opened_in_real_browser": True,
        "browser_source_bound_to_project_revision_blueprint_hash": (
            source_view["project_id"] == exact["project"]["project_id"]
            and source_view["revision_id"] == exact["project"]["revision_id"]
            and source_view["blueprint_sha256"] == blueprint_sha256(exact)
        ),
        "all_six_operations_browser_exercised": all_six,
        "accepted_ref_unchanged_before_accept": ref_unchanged,
        "preview_not_accepted_visible": True,
        "explicit_accept_advanced_once_to_candidate": accepted_session["head_revision_id"] == repitch_candidate_revision,
        "discard_preserved_accepted_ref": all(item["resolution"] != "DISCARD" or item["accepted_head_before_accept"] == accepted_root for item in operation_outcomes),
        "accepted_repitch_preserved": accepted_anchor["pitch"] == 64,
        "accepted_state_survives_restart_reopen": reopened_view["revision_id"] == repitch_candidate_revision and reopened_anchor["pitch"] == 64,
        "hard_lock_blocked": hard_lock_evidence["authority_result"]["status"] == "BLOCKED" and hard_conflicts[0]["code"] == "HARD_LOCK_VIOLATION",
        "hard_lock_rule_context_visible": "L-M6-R3-PITCH" in str(hard_lock_evidence["status_text"]),
        "hard_lock_preview_installed": hard_lock_evidence["server_session"]["pending_preview"] is not None,
        "stale_source_blocked": stale_evidence["authority_result"]["status"] == "BLOCKED" and stale_conflicts[0]["code"] == "STALE_SOURCE",
        "stale_preview_installed": stale_evidence["server_session"]["pending_preview"] is not None,
        "stale_response_rebound_to_current_accepted_source": stale_evidence["note_view_after_block"]["revision_id"] == concurrent_revision,
        "legacy_reports_exact_editing_unavailable": legacy_view["exact_note_editing_available"] is False,
        "legacy_has_no_fabricated_notes": legacy_view["notes"] == [],
        "browser_project_mutation_authorized": source_view["capabilities"]["project_mutation_authorized"],
        "music_ir_mutation_authorized": source_view["capabilities"]["music_ir_mutation_authorized"],
        "external_provider_network_required": False,
        "browser_console_error_count": len(console_errors),
        "browser_page_error_count": len(page_errors),
    }

    required_true = [
        "real_chromium_used",
        "exact_note_project_opened_in_real_browser",
        "browser_source_bound_to_project_revision_blueprint_hash",
        "all_six_operations_browser_exercised",
        "accepted_ref_unchanged_before_accept",
        "preview_not_accepted_visible",
        "explicit_accept_advanced_once_to_candidate",
        "discard_preserved_accepted_ref",
        "accepted_repitch_preserved",
        "accepted_state_survives_restart_reopen",
        "hard_lock_blocked",
        "hard_lock_rule_context_visible",
        "stale_source_blocked",
        "stale_response_rebound_to_current_accepted_source",
        "legacy_reports_exact_editing_unavailable",
        "legacy_has_no_fabricated_notes",
    ]
    if not all(bool(proof[key]) for key in required_true):
        raise RuntimeError("M6-R3 real-browser positive/negative proof failed")
    if proof["hard_lock_preview_installed"] or proof["stale_preview_installed"]:
        raise RuntimeError("Blocked M6-R3 conflict installed a pending Preview")
    if proof["browser_project_mutation_authorized"] or proof["music_ir_mutation_authorized"]:
        raise RuntimeError("M6-R3 Browser/Music-IR authority boundary was violated")

    tracked: list[Path] = [
        write_canonical_json(root / "source-note-view.json", source_view),
        write_canonical_json(root / "operation-outcomes.json", operation_outcomes),
        write_canonical_json(root / "accepted-note-view.json", accepted_view),
        write_canonical_json(root / "reopened-note-view.json", reopened_view),
        write_canonical_json(root / "hard-lock-browser.json", hard_lock_evidence),
        write_canonical_json(root / "stale-source-browser.json", stale_evidence),
        write_canonical_json(root / "legacy-note-view.json", legacy_view),
        write_canonical_json(root / "browser-actions.json", browser_actions),
        write_canonical_json(
            root / "browser-runtime.json",
            {
                "console_errors": console_errors,
                "page_errors": page_errors,
                "request_failures": request_failures,
            },
        ),
        write_canonical_json(root / "proof.json", proof),
    ]
    tracked.extend(screenshots)
    manifest = {
        "manifest_version": "0",
        "evidence_class": "REAL_BROWSER_EXACT_NOTE_E2E_EVIDENCE",
        "evidence_scope": "M6-R3-Real-Browser-Exact-Note-E2E-Lock-Conflict-UX-v0",
        "browser": "Playwright Chromium",
        "source_blueprint_sha256": blueprint_sha256(exact),
        "accepted_revision_id": repitch_candidate_revision,
        "accepted_blueprint_sha256": accepted_view["blueprint_sha256"],
        "proof": proof,
        "claim_boundary": [
            "real Chromium exact-note Browser Studio E2E",
            "all six existing M6 primitive operations through visible browser controls",
            "Preview remains non-canonical until explicit existing M2 Accept",
            "Discard preserves accepted state",
            "visible HARD-lock and stale-source fail-closed conflict UX",
            "restart/reopen persistence of accepted exact-note state",
            "legacy project no-fabrication behavior",
            "not full DAW piano-roll parity",
            "not arbitrary polyphonic/every-part editing",
            "not arbitrary tempo-map editing",
            "not human-subject usability or perceptual evidence",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(tracked, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M6-R3 real-browser exact-note evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
