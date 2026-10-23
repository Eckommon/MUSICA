"""G3B2C-R4 browser proof: real Chromium sees *pending* 180s WAV, not accepted."""
from __future__ import annotations

import json
import os
import shutil
import threading
from pathlib import Path

import pytest

from musica.studio import StudioService
from musica.studio_audio import StudioAudioSurface
from musica.studio_http_r3 import create_local_server
from test_atcm_r2_native_mixer import _candidate
from test_prod_e2e_r2a_g3b2a_streamed_native import _two_accepted_long_sources


def test_real_chromium_pending_preview_180s_metadata_and_safe_discard(tmp_path):
    playwright_sync = pytest.importorskip("playwright.sync_api")
    expect, sync_playwright = playwright_sync.expect, playwright_sync.sync_playwright
    project, head, aa, bb = _two_accepted_long_sources(tmp_path)
    studio = StudioService(tmp_path / "studio")
    server = create_local_server(studio, host="127.0.0.1", port=0)
    server_thread = threading.Thread(target=server.serve_forever,
                                     kwargs={"poll_interval": 0.01}, daemon=True)
    server_thread.start()
    _, port = server.server_address[:2]
    target = f"http://127.0.0.1:{port}"
    output = tmp_path / "r4-chromium-proof"
    output.mkdir()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1200})
            page = context.new_page()
            page.goto(target + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            # Activate a genuine Project in first-party Studio before
            # entering Inspect; the tab is intentionally disabled without it.
            page.locator("#openProjectSlug").fill("g3b2-long-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible(timeout=120000)
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioWorkspace")).to_be_visible()
            page.wait_for_function(
                "() => Boolean(window.MUSICA_NATIVE_AUDIO?.state?.sessionId)",
                timeout=30000,
            )
            session_id = page.evaluate(
                "() => window.MUSICA_NATIVE_AUDIO.state.sessionId"
            )
            assert session_id
            # The candidate is installed by the trusted backend Preview API
            # into this *actual browser-owned session*, not fabricated in JS.
            surface = StudioAudioSurface(studio)
            accepted = studio._get_session(session_id).project.read_revision(head)
            pending_response = surface.preview_audio_edit(
                session_id,
                candidate=_candidate(
                    accepted, "R4-BROWSER-180S-UNACCEPTED",
                    [{"operation_id": "R4-CHROMIUM-GAIN", "op": "SET_TRACK_MIXER",
                      "target": {"track_id": "AT-G3B2-A"},
                      "mixer": {"gain_db": -6.0, "pan": 0.0,
                                "mute": False, "solo": False}}],
                ),
                candidate_kind="mixer",
            )
            assert pending_response["preview_installed"]
            pending = studio._get_session(session_id).pending
            assert pending is not None
            preview_id = pending.descriptor["preview_id"]
            assert project.head_revision_id() == head
            page.evaluate(
                "async () => await window.MUSICA_NATIVE_AUDIO.refresh(true)"
            )
            label = page.locator("#r3AuditionMeta")
            expect(label).to_contain_text("PREVIEW · NOT ACCEPTED", timeout=120000)
            player = page.locator("#r3AudioPlayer")
            expect(player).to_be_visible()
            assert player.get_attribute("src").endswith(
                "/audio/stream/preview.wav?preview_id=" + preview_id
            )
            page.wait_for_function("""() => {
              const a = document.getElementById("r3AudioPlayer");
              return a && a.readyState >= 1 && Number.isFinite(a.duration) &&
                Math.abs(a.duration - 180) < 0.02;
            }""", timeout=240000)
            assert project.head_revision_id() == head
            duration = player.evaluate("node => node.duration")
            image = output / "01-chromium-180s-pending-not-accepted.png"
            page.screenshot(path=str(image), full_page=True)
            context.close()
            browser.close()
        assert project.head_revision_id() == head
        studio.discard_preview(session_id)
        assert project.head_revision_id() == head
        proof = {
            "milestone": "PROD-E2E-R2A-G3B2C-R4",
            "actual_chromium_pending_180s_metadata": True,
            "trusted_candidate_installed_only_in_server_session": True,
            "preview_id": preview_id,
            "accepted_revision_before_and_after": head,
            "browser_duration_seconds": duration,
            "preview_label": "PREVIEW · NOT ACCEPTED",
            "pending_candidate_wav_endpoint": True,
            "auto_accepted_during_playback": False,
            "discard_without_creative_head_mutation": True,
            "full_human_editor_import_accept_reopen": False,
            "physical_audio_device_latency_verified": False,
            "screenshot": image.name,
        }
        (output / "proof.json").write_text(
            json.dumps(proof, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        audit = os.environ.get("MUSICA_G3B2C_R4_BROWSER_ARTIFACT_DIR")
        if audit:
            destination = Path(audit).resolve()
            destination.mkdir(parents=True, exist_ok=True)
            for item in output.iterdir():
                shutil.copy2(item, destination / item.name)
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)
    assert not server_thread.is_alive()
