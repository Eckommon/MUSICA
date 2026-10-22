"""G3B2C-R1 first-party real Chromium explicit accepted-WAV streaming download.

Intentionally scoped to 12s accepted tracks: 180s human flow and Range cache
are later G3B2C/G3B3. This is an actual clicked Browser download over localhost.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from .evidence import write_canonical_json
from .prod_e2e_r1a_browser import _server, _stop
from .prod_e2e_r1b_g1_browser import suite as seed_accepted


def run(destination: str | Path) -> dict:
    from playwright.sync_api import expect, sync_playwright

    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    seed = root / "seed-accepted"
    seed_accepted(seed, sample_rate_hz=8000)
    accepted = (seed / "two-track-accepted.wav").read_bytes()
    expected_sha = hashlib.sha256(accepted).hexdigest()
    service, server, thread, base = _server(seed / "workspace")
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1200},
                                          accept_downloads=True)
            page = context.new_page()
            page.goto(base + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill("r1b-g1-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioWorkspace")).to_be_visible()
            download = page.locator("#r3StreamedAcceptedWavDownload")
            expect(download).to_be_visible(timeout=90000)
            assert download.get_attribute("href").endswith(
                "/audio/stream/accepted.wav?download=1"
            )
            before = next(iter(service._sessions.values())).project.head_revision_id()
            with page.expect_download(timeout=90000) as event:
                download.click()
            source = root / "clicked-accepted.wav"
            event.value.save_as(source)
            actual = hashlib.sha256(source.read_bytes()).hexdigest()
            assert actual == expected_sha, "clicked accepted WAV differs from prior canonical audio render"
            assert next(iter(service._sessions.values())).project.head_revision_id() == before
            page.screenshot(path=str(root / "01-accepted-bounded-download.png"), full_page=True)
            context.close()
            browser.close()
    finally:
        _stop(server, thread)
    proof = {
        "milestone": "PROD-E2E-R2A-G3B2C-R1",
        "real_chromium_clicked_explicit_download": True,
        "first_party_native_studio_panel": True,
        "expected_accepted_wav_sha256": expected_sha,
        "downloaded_wav_sha256": actual,
        "download_size_bytes": source.stat().st_size,
        "creative_accept_by_download": False,
        "head_unchanged_after_download": True,
        "stream_uses_project_private_temporary_wav": True,
        "duration_180s_browser_verified": False,
        "range_cache_efficiency_verified": False,
        "real_audio_hardware_verified": False,
        "screenshots": ["01-accepted-bounded-download.png"],
    }
    write_canonical_json(root / "proof.json", proof)
    return proof


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
