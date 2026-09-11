"""Generate M4-R3 real-browser E2E evidence with Playwright Chromium.

Playwright is an optional test/evidence dependency. This module deliberately imports it
inside ``run_suite`` so normal MUSICA runtime/import paths do not require browser tooling.
"""

from __future__ import annotations

import argparse
import json
import threading
from pathlib import Path
from typing import Any

from .evidence import artifact_record, sha256_file, write_canonical_json
from .studio import StudioService
from .studio_http import create_local_server


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


def _session_from_page(page) -> dict[str, Any]:
    raw = page.locator("#jsonView").text_content() or "{}"
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise RuntimeError("Code/session JSON is not an object")
    return value


def _probe_audio(page) -> dict[str, Any]:
    player = page.locator("#audioPlayer")
    src = player.evaluate("el => el.currentSrc || el.src")
    if not src:
        raise RuntimeError("Browser audio element has no media source")
    response = page.context.request.get(src)
    body = response.body()
    content_type = response.headers.get("content-type", "")
    if not response.ok:
        raise RuntimeError(f"Browser-managed audio request failed: HTTP {response.status}")
    if not content_type.startswith("audio/wav"):
        raise RuntimeError(f"Unexpected audio content type: {content_type}")
    if body[:4] != b"RIFF":
        raise RuntimeError("Browser-managed audio response is not RIFF/WAV")
    return {
        "src": src,
        "http_status": response.status,
        "content_type": content_type,
        "size_bytes": len(body),
        "riff": True,
    }


def _screenshot(page, target: Path) -> Path:
    page.screenshot(path=str(target), full_page=True)
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError(f"Browser screenshot was not created: {target}")
    return target


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:  # pragma: no cover - exercised only without optional dependency
        raise RuntimeError(
            "M4-R3 requires optional browser evidence dependencies: install with .[dev,e2e]"
        ) from exc

    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    workspace = root / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    screenshots: list[Path] = []
    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []

    service1, server1, thread1, base1 = _start_server(workspace)
    first_server_stopped = False

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1100},
            reduced_motion="reduce",
        )
        context.set_default_timeout(30_000)
        page = context.new_page()
        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on(
            "requestfailed",
            lambda request: request_failures.append(
                f"{request.method} {request.url}: {request.failure}"
            ),
        )

        try:
            # E2E-01: real browser create + accepted media.
            page.goto(base1 + "/", wait_until="networkidle")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#projectSlug").fill("browser-e2e")
            page.locator("#createPrompt").fill(
                "Create a restrained dark electronic 8-second technology cue that becomes more urgent near the end."
            )
            page.locator("#durationSeconds").fill("8")
            page.locator("#useCase").select_option("advertisement")
            page.locator("#providerMode").select_option("fixture")
            page.locator("#styleProfile").select_option("dark_electronic")
            page.locator("#generateButton").click()
            expect(page.locator("#activeProject")).to_be_visible()
            expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
            expect(page.locator("#sideIntegrity")).to_have_text("PASS")
            expect(page.locator("#notice")).to_contain_text("Project created and accepted")

            created_session = _session_from_page(page)
            session_id = str(created_session["session_id"])
            accepted_root_head = str(created_session["head_revision_id"])
            if created_session.get("pending_preview") is not None:
                raise RuntimeError("New browser-created project unexpectedly has pending preview")
            accepted_audio = _probe_audio(page)
            screenshots.append(_screenshot(page, root / "01-created-accepted.png"))

            # Exercise progressive disclosure through visible tabs.
            for tab_name in ("shape", "inspect", "code", "direct", "shape"):
                tab = page.locator(f'button[data-tab="{tab_name}"]')
                expect(tab).to_be_enabled()
                tab.click()
                expect(page.locator(f'#panel-{tab_name}')).to_be_visible()

            # E2E-02: Shape semantic control -> non-canonical preview.
            tension = page.locator('input[type="range"][data-axis="tension"]')
            current_tension = float(tension.input_value())
            target_tension = 0.91 if abs(current_tension - 0.91) > 0.05 else 0.12
            tension.evaluate(
                """(el, value) => {
                    el.value = String(value);
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    el.dispatchEvent(new Event('change', {bubbles: true}));
                }""",
                target_tension,
            )
            page.locator("#scopeKind").select_option("final_section")
            page.locator("#previewSemanticButton").click()

            expect(page.locator("#panel-inspect")).to_be_visible()
            expect(page.locator("#previewDecision")).to_be_visible()
            expect(page.locator("#projectStateBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            preview_session = _session_from_page(page)
            pending = preview_session.get("pending_preview")
            if not isinstance(pending, dict):
                raise RuntimeError("Browser preview did not expose pending preview descriptor")
            if str(preview_session["head_revision_id"]) != accepted_root_head:
                raise RuntimeError("Browser preview advanced canonical head before Accept")
            candidate_revision = str(pending["candidate_revision_id"])
            if candidate_revision == accepted_root_head:
                raise RuntimeError("Preview candidate revision equals accepted parent")

            diff_count = page.locator("#diffList .diff-item").count()
            lock_count = page.locator("#inspectLocks .lock-item").count()
            if diff_count <= 0:
                raise RuntimeError("Inspect surface did not expose preview diff entries")
            if lock_count <= 0:
                raise RuntimeError("Inspect surface did not expose HARD locks")
            if not page.locator("#createBranchButton").is_disabled():
                raise RuntimeError("Branch creation remained enabled during pending preview")
            if not page.locator("#checkoutButton").is_disabled():
                raise RuntimeError("Checkout remained enabled during pending preview")
            if not page.locator("#exportButton").is_disabled():
                raise RuntimeError("Export remained enabled during pending preview")
            preview_audio = _probe_audio(page)
            screenshots.append(_screenshot(page, root / "02-preview-not-accepted.png"))

            # Cross-check that server authority agrees with the browser display.
            server_preview_session = service1.inspect_session(session_id)
            if server_preview_session["head_revision_id"] != accepted_root_head:
                raise RuntimeError("Server canonical head changed during browser preview")
            if server_preview_session["pending_preview"]["candidate_revision_id"] != candidate_revision:
                raise RuntimeError("Browser/server preview candidate mismatch")

            # E2E-03: explicit Accept is the only promotion step.
            page.locator("#acceptButton").click()
            expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
            expect(page.locator("#previewDecision")).to_be_hidden()
            accepted_session = _session_from_page(page)
            accepted_revision = str(accepted_session["head_revision_id"])
            if accepted_revision != candidate_revision:
                raise RuntimeError("Explicit Accept did not advance to preview candidate")
            if accepted_session.get("pending_preview") is not None:
                raise RuntimeError("Pending preview remained after explicit Accept")
            accepted_v2_audio = _probe_audio(page)
            screenshots.append(_screenshot(page, root / "03-accepted-revision.png"))

            # E2E-04: branch + history + export through visible controls.
            page.locator("#newBranchName").fill("browser-variation")
            page.locator("#createBranchButton").click()
            expect(page.locator("#sideBranch")).to_have_text("browser-variation")
            expect(page.locator("#branchSelect")).to_have_value("browser-variation")
            history_count = page.locator("#historyList .history-item").count()
            if history_count < 2:
                raise RuntimeError("Browser history did not expose accepted revisions")
            page.locator("#exportButton").click()
            expect(page.locator("#exportResult")).to_contain_text("exports/")
            export_text = page.locator("#exportResult").text_content() or ""
            if "sha256:" not in export_text:
                raise RuntimeError("Browser export result did not expose hash summary")
            branch_session = _session_from_page(page)
            if branch_session["current_branch"] != "browser-variation":
                raise RuntimeError("Browser branch create/checkout did not update session state")
            if branch_session["head_revision_id"] != accepted_revision:
                raise RuntimeError("Branch creation unexpectedly changed accepted revision")
            screenshots.append(_screenshot(page, root / "04-branch-history-export.png"))

            # E2E-05: Code view is server-backed and read-only.
            page.locator('button[data-tab="code"]').click()
            expect(page.locator("#panel-code")).to_be_visible()
            code_session = _session_from_page(page)
            if code_session["current_branch"] != "browser-variation":
                raise RuntimeError("Code view branch differs from browser/server state")
            if code_session["head_revision_id"] != accepted_revision:
                raise RuntimeError("Code view head differs from accepted state")
            raw_mutation_controls = page.locator(
                "#panel-code textarea, #panel-code input, #panel-code select"
            ).count()
            if raw_mutation_controls != 0:
                raise RuntimeError("Code view exposes unexpected raw mutation controls")
            screenshots.append(_screenshot(page, root / "05-code-view.png"))

            first_phase = {
                "session_id": session_id,
                "accepted_root_head": accepted_root_head,
                "preview_candidate_revision": candidate_revision,
                "preview_displayed_head": preview_session["head_revision_id"],
                "accepted_revision": accepted_revision,
                "branch": branch_session["current_branch"],
                "diff_count": diff_count,
                "hard_lock_count": lock_count,
                "history_count": history_count,
                "accepted_audio": accepted_audio,
                "preview_audio": preview_audio,
                "accepted_v2_audio": accepted_v2_audio,
                "export_text": export_text,
                "integrity_status": branch_session["integrity_status"],
            }

            # E2E-06: restart application service, then reopen through visible browser UI.
            page.close()
            _stop_server(server1, thread1)
            first_server_stopped = True

            service2, server2, thread2, base2 = _start_server(workspace)
            page2 = context.new_page()
            page2.on(
                "console",
                lambda message: console_errors.append(message.text)
                if message.type == "error"
                else None,
            )
            page2.on("pageerror", lambda error: page_errors.append(str(error)))
            page2.on(
                "requestfailed",
                lambda request: request_failures.append(
                    f"{request.method} {request.url}: {request.failure}"
                ),
            )
            try:
                page2.goto(base2 + "/", wait_until="networkidle")
                expect(page2.locator("#connectionBadge")).to_contain_text("READY")
                page2.locator("#openProjectSlug").fill("browser-e2e")
                page2.locator("#openForm button[type=submit]").click()
                expect(page2.locator("#activeProject")).to_be_visible()
                expect(page2.locator("#notice")).to_contain_text("Project opened")
                expect(page2.locator("#projectStateBadge")).to_have_text("ACCEPTED")
                expect(page2.locator("#sideIntegrity")).to_have_text("PASS")
                reopened_session = _session_from_page(page2)
                if reopened_session["current_branch"] != "browser-variation":
                    raise RuntimeError("Restart/reopen did not restore durable current branch")
                if reopened_session["head_revision_id"] != accepted_revision:
                    raise RuntimeError("Restart/reopen did not restore durable accepted head")
                if reopened_session.get("pending_preview") is not None:
                    raise RuntimeError("Restart/reopen restored an ephemeral pending preview")
                reopened_audio = _probe_audio(page2)
                screenshots.append(_screenshot(page2, root / "06-reopened-after-restart.png"))

                server_reopened = service2.inspect_session(str(reopened_session["session_id"]))
                if server_reopened["head_revision_id"] != accepted_revision:
                    raise RuntimeError("Fresh service disagrees with reopened browser head")
                if server_reopened["integrity_status"] != "PASS":
                    raise RuntimeError("Fresh service project integrity did not pass")

                restart_phase = {
                    "new_session_id": reopened_session["session_id"],
                    "current_branch": reopened_session["current_branch"],
                    "head_revision_id": reopened_session["head_revision_id"],
                    "integrity_status": reopened_session["integrity_status"],
                    "audio": reopened_audio,
                }
            finally:
                page2.close()
                _stop_server(server2, thread2)

        finally:
            if not first_server_stopped:
                _stop_server(server1, thread1)
            context.close()
            browser.close()

    if console_errors:
        raise RuntimeError(f"Browser console errors detected: {console_errors}")
    if page_errors:
        raise RuntimeError(f"Browser page errors detected: {page_errors}")
    # Media element shutdown or page-close may cancel non-essential browser requests; keep
    # the list as evidence instead of making unrelated teardown noise a promotion blocker.

    proof = {
        "real_chromium_used": True,
        "project_created_via_visible_browser_controls": True,
        "accepted_audio_browser_retrieval_valid": first_phase["accepted_audio"]["riff"],
        "progressive_disclosure_tabs_exercised": ["Direct", "Shape", "Inspect", "Code"],
        "preview_not_accepted_visible": True,
        "preview_ref_unchanged_before_accept": first_phase["preview_displayed_head"]
        == first_phase["accepted_root_head"],
        "preview_candidate_differs_from_parent": first_phase["preview_candidate_revision"]
        != first_phase["accepted_root_head"],
        "preview_diff_count": first_phase["diff_count"],
        "hard_lock_count": first_phase["hard_lock_count"],
        "preview_conflict_controls_disabled": True,
        "explicit_accept_advanced_to_candidate": first_phase["accepted_revision"]
        == first_phase["preview_candidate_revision"],
        "branch_created_and_checked_out": first_phase["branch"] == "browser-variation",
        "history_visible": first_phase["history_count"] >= 2,
        "export_visible_with_hash": "sha256:" in first_phase["export_text"],
        "code_view_read_only": True,
        "restart_reopen_preserved_branch": restart_phase["current_branch"] == "browser-variation",
        "restart_reopen_preserved_head": restart_phase["head_revision_id"]
        == first_phase["accepted_revision"],
        "restart_reopen_integrity": restart_phase["integrity_status"],
        "reopened_audio_browser_retrieval_valid": restart_phase["audio"]["riff"],
        "external_provider_network_required": False,
        "browser_console_error_count": len(console_errors),
        "browser_page_error_count": len(page_errors),
        "browser_request_failure_count": len(request_failures),
    }

    write_canonical_json(root / "first-browser-phase.json", first_phase)
    write_canonical_json(root / "restart-reopen-phase.json", restart_phase)
    write_canonical_json(root / "browser-console-errors.json", console_errors)
    write_canonical_json(root / "browser-page-errors.json", page_errors)
    write_canonical_json(root / "browser-request-failures.json", request_failures)
    write_canonical_json(root / "proof.json", proof)

    files = sorted(path for path in root.rglob("*") if path.is_file() and path.name != "manifest.json")
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M4-R3-Usable-MVP-Real-Browser-E2E-v0",
        "evidence_class": "REAL_BROWSER_E2E_EVIDENCE",
        "browser": "Chromium via Playwright",
        "network_policy": {
            "studio_bind": "loopback-only",
            "provider_mode": "fixture",
            "external_provider_network_required": False,
            "live_openai_call_performed": False,
        },
        "proof": proof,
        "claim_boundary": [
            "Automated real-browser operability is validated; human usability-study evidence is not claimed.",
            "Media validity/playability is machine-proven; human auditory perception is not claimed.",
            "Production mastering, desktop packaging, cloud collaboration, live OpenAI execution and DAW/VST interoperability are not claimed.",
        ],
        "artifacts": [artifact_record(path, root) for path in files],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M4-R3 real-browser E2E evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
