from __future__ import annotations

from pathlib import Path

from musica.post_m7_revision_compare_e2e import (
    _attach_observers,
    _browser_compare,
    _open_project,
    _prepare_project,
    _start_server,
    _stop_server,
)


def test_post_m7_user_ab_choice_is_browser_local_only(tmp_path: Path) -> None:
    from playwright.sync_api import expect, sync_playwright

    expect.set_options(timeout=30_000)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    root_revision, child_revision = _prepare_project(workspace)
    service, server, thread, base = _start_server(workspace)
    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []
    expected_media_aborts: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1500, "height": 1100}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        try:
            page = context.new_page()
            _attach_observers(page, console_errors, page_errors, request_failures, expected_media_aborts)
            opened = _open_project(page, base, expect)
            session_id = str(opened["session_id"])
            project = service._get_session(session_id).project
            head_before = project.head_revision_id()
            assert head_before == child_revision

            _browser_compare(page, expect, root_revision, child_revision)

            page.locator("#revisionCompareChooseA").click()
            expect(page.locator("#revisionCompareChoice")).to_contain_text("USER CHOICE · A · LOCAL ONLY")
            expect(page.locator("#revisionCompareChoice")).to_contain_text(root_revision)
            expect(page.locator("#revisionCompareChooseA")).to_have_attribute("aria-pressed", "true")
            assert project.head_revision_id() == head_before

            page.locator("#revisionCompareChooseB").click()
            expect(page.locator("#revisionCompareChoice")).to_contain_text("USER CHOICE · B · LOCAL ONLY")
            expect(page.locator("#revisionCompareChoice")).to_contain_text(child_revision)
            expect(page.locator("#revisionCompareChooseB")).to_have_attribute("aria-pressed", "true")
            expect(page.locator("#revisionCompareStatus")).to_contain_text("Canonical HEAD was not changed")
            assert page.evaluate("() => window.MUSICA_AUTOMATION.revisionCompareState.userChoice") == "B"
            assert project.head_revision_id() == head_before == child_revision
        finally:
            context.close()
            browser.close()
            _stop_server(server, thread)

    assert console_errors == []
    assert page_errors == []
    assert request_failures == []
