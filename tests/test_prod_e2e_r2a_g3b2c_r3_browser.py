"""G3B2C-R3: real Chromium opens 180s accepted Studio view without full PCM buffers."""
from __future__ import annotations

import json
import os
import shutil
import threading

import pytest
from pathlib import Path

from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server
from test_prod_e2e_r2a_g3b2a_streamed_native import _two_accepted_long_sources


def test_chromium_180s_native_studio_metadata_uses_bounded_range(tmp_path):
    # Base matrix has no Playwright dependency; the permanent R3-specific
    # workflow installs Chromium and MUST actually execute this exact test.
    playwright_sync = pytest.importorskip("playwright.sync_api")
    expect, sync_playwright = playwright_sync.expect, playwright_sync.sync_playwright

    project, head, a, b = _two_accepted_long_sources(tmp_path)
    service = StudioService(tmp_path / "studio")
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01}, daemon=True,
    )
    thread.start()
    _, port = server.server_address[:2]
    url = f"http://127.0.0.1:{port}"
    artefact_dir = tmp_path / "browser-proof"
    artefact_dir.mkdir()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1600, "height": 1200}, accept_downloads=True
            )
            page = context.new_page()
            page.set_default_timeout(60000)
            page.goto(url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill("g3b2-long-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible(timeout=120000)
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioWorkspace")).to_be_visible(timeout=120000)
            expect(page.locator("#r3AuditionMeta")).to_contain_text(
                "bounded Range streaming", timeout=120000
            )
            player = page.locator("#r3AudioPlayer")
            expect(player).to_be_visible()
            assert player.get_attribute("src").endswith(
                "/audio/stream/accepted.wav"
            )
            expect(page.locator("#r3StreamedAcceptedWavDownload")).to_be_visible()
            # This is an actual browser <audio> WAV metadata fetch via the
            # session-bound 200/206 Range transport, not a fabricated duration.
            page.wait_for_function(
                """() => {
                  const player = document.getElementById("r3AudioPlayer");
                  return player && player.readyState >= 1 &&
                    Number.isFinite(player.duration) &&
                    Math.abs(player.duration - 180) < 0.02;
                }""",
                timeout=240000,
            )
            before = project.head_revision_id()
            assert before == head
            assert len(page.evaluate(
                "() => window.MUSICA_NATIVE_AUDIO.state.view.tracks"
            )) == 2
            browser_duration = page.locator("#r3AudioPlayer").evaluate(
                "element => element.duration"
            )
            screenshot = artefact_dir / "01-real-chromium-180s-native-stream.png"
            page.screenshot(path=str(screenshot), full_page=True)
            assert project.head_revision_id() == head
            proof = {
                "milestone": "PROD-E2E-R2A-G3B2C-R3",
                "real_chromium_180s_accepted_audio_metadata": True,
                "accepted_revision_id": head,
                "accepted_two_distinct_pcm_sources": a["asset_id"] != b["asset_id"],
                "browser_audio_duration_seconds": browser_duration,
                "browser_accepted_range_player": True,
                "source_accepted_head_unchanged": True,
                "full_180s_browser_manual_composition_verified": False,
                "long_pending_preview_audition_verified": False,
                "low_latency_hardware_audio_verified": False,
                "screenshot": screenshot.name,
            }
            (artefact_dir / "proof.json").write_text(
                json.dumps(proof, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert not thread.is_alive()
    audit = os.environ.get("MUSICA_G3B2C_R3_ARTIFACT_DIR")
    if audit:
        result_dir = Path(audit).resolve()
        result_dir.mkdir(parents=True, exist_ok=True)
        for original in artefact_dir.iterdir():
            shutil.copy2(original, result_dir / original.name)
