from __future__ import annotations

import json
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

from musica.m6_r3_e2e import _blueprint, _start_server, _stop_server
from musica.project import create_project


def _open(page, base: str, slug: str) -> None:
    page.goto(base + "/", wait_until="domcontentloaded")
    page.locator("#connectionBadge").wait_for(state="visible")
    page.locator("#openProjectSlug").fill(slug)
    page.locator("#openForm button[type=submit]").click()
    page.locator("#activeProject").wait_for(state="visible")
    page.locator('button[data-tab="inspect"]').click()
    page.locator("#panel-inspect").wait_for(state="visible")


def _wait_badge(page, text: str) -> None:
    page.wait_for_function(
        "expected => document.getElementById('projectStateBadge')?.textContent === expected",
        text,
    )


def main() -> None:
    root = Path("artifacts/m6-r3-http-diagnostic")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    workspace = root / "workspace"
    workspace.mkdir()

    create_project(workspace / "exact.musica", _blueprint("PRJ-M6-R3-DIAG-EXACT", "rev-m6-r3-diag-exact-r1"))
    create_project(
        workspace / "locked.musica",
        _blueprint("PRJ-M6-R3-DIAG-LOCKED", "rev-m6-r3-diag-locked-r1", locked=True),
    )
    create_project(workspace / "stale.musica", _blueprint("PRJ-M6-R3-DIAG-STALE", "rev-m6-r3-diag-stale-r1"))
    create_project(
        workspace / "legacy.musica",
        _blueprint("PRJ-M6-R3-DIAG-LEGACY", "rev-m6-r3-diag-legacy-r1", exact=False),
    )

    http_errors: list[dict[str, object]] = []
    console_errors: list[dict[str, str]] = []
    service, server, thread, base = _start_server(workspace)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1500, "height": 1200}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        context.on(
            "response",
            lambda response: http_errors.append(
                {
                    "status": response.status,
                    "method": response.request.method,
                    "resource_type": response.request.resource_type,
                    "url": response.url,
                }
            )
            if response.status >= 400
            else None,
        )

        try:
            for slug in ("exact", "locked", "stale", "legacy"):
                page = context.new_page()
                page.on(
                    "console",
                    lambda message, slug=slug: console_errors.append(
                        {"slug": slug, "text": message.text}
                    )
                    if message.type == "error"
                    else None,
                )
                _open(page, base, slug)

                if slug == "exact":
                    note = page.locator(
                        '#m6PianoRoll button.m6-note[data-note-key="P-SYNTH::N-MOTIF-001"]:not(.ghost)'
                    ).first
                    note.click()
                    page.locator("#m6Start").fill("0.25")
                    page.locator("#m6PreviewChanges").click()
                    _wait_badge(page, "PREVIEW · NOT ACCEPTED")
                    page.locator("#discardButton").click()
                    _wait_badge(page, "ACCEPTED")
                page.close()

            _stop_server(server, thread)
            service, server, thread, base = _start_server(workspace)
            page = context.new_page()
            page.on(
                "console",
                lambda message: console_errors.append({"slug": "exact-reopen", "text": message.text})
                if message.type == "error"
                else None,
            )
            _open(page, base, "exact")
            page.close()
        finally:
            try:
                _stop_server(server, thread)
            except Exception:
                pass
            context.close()
            browser.close()

    result = {"http_errors": http_errors, "console_errors": console_errors}
    (root / "diagnostic.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
