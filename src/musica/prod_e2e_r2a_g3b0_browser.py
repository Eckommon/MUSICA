"""G3B-0 bounded >16MiB Browser user-file selection -> staged CAS resource.

Automated Chromium, not human full-song recording or real-time DAW performance.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import wave
from pathlib import Path

from .evidence import write_canonical_json
from .audio_assets import list_audio_assets
from .prod_e2e_r1a_browser import _record_request_failure, _server, _stop


def run_suite(destination: str | Path) -> dict:
    from playwright.sync_api import expect, sync_playwright
    out = Path(destination)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    workspace = out / "workspace"

    # ~17 MiB 48kHz stereo PCM16 synthetic take, exceeds untouched direct
    # 16 MiB body boundary. The imported file is not a canonical clip.
    frames = 4_300_000
    sample = b"\x2a\x00\x00\x00" * frames
    sink = io.BytesIO()
    with wave.open(sink, "wb") as writer:
        writer.setnchannels(2)
        writer.setsampwidth(2)
        writer.setframerate(48000)
        writer.writeframes(sample)
    payload = sink.getvalue()
    sha = hashlib.sha256(payload).hexdigest()
    assert 16 * 1024 * 1024 < len(payload) < 64 * 1024 * 1024

    errors, page_errors, failures, screenshots = [], [], [], []
    service, server, thread, url = _server(workspace)
    try:
        with sync_playwright() as browser_driver:
            browser = browser_driver.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1200})
            context.set_default_timeout(100000)
            page = context.new_page()
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.on("requestfailed", lambda req: _record_request_failure(req, failures))
            page.goto(url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#projectSlug").fill("g3b0-large-wav")
            page.locator("#durationSeconds").fill("12")
            page.locator("#useCase").select_option("song")
            page.locator("#createForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioImport")).to_be_visible()
            session = next(iter(service._sessions.values()))
            head = session.project.head_revision_id()
            audit_before = len(session.project._audit_events())
            page.locator("#r3WavFile").set_input_files({
                "name": "user-long-stereo-take.wav",
                "mimeType": "audio/wav",
                "buffer": payload
            })
            page.locator("#r3ImportWav").click()
            expect(page.locator("#r3NewAssetId")).to_have_value("sha256:" + sha, timeout=100000)
            expect(page.locator("#r3ImportedAsset")).to_contain_text("NOT A CLIP")
            expect(page.locator("#r3CancelStagedWav")).to_be_hidden()
            assert session.project.head_revision_id() == head
            descriptors = list_audio_assets(session.project)
            assert len(descriptors) == 1
            assert descriptors[0]["object_sha256"] == sha
            assert descriptors[0]["size_bytes"] == len(payload)
            assert len(session.project._audit_events()) == audit_before + 1
            assert session.project.verify_integrity()["status"] == "PASS"
            assert not list((service.workspace / ".wav-staging-g3b0").glob("*.part"))
            screenshot = "01-user-picked-17MiB-wav-resource.png"
            page.screenshot(path=str(out / screenshot), full_page=True)
            screenshots.append(screenshot)
            context.close()
            browser.close()
    finally:
        _stop(server, thread)
    assert not (errors or page_errors or failures), (errors, page_errors, failures)
    proof = {
        "milestone": "PROD-E2E-R2A-G3B0",
        "real_chromium_user_file_picker": True,
        "source_size_bytes": len(payload),
        "source_sha256": sha,
        "source_rate_hz": 48000,
        "source_channels": 2,
        "source_pcm_width_bytes": 2,
        "source_duration_seconds": frames / 48000,
        "exceeds_old_16_mib_boundary": True,
        "new_staged_limit_bytes": 64 * 1024 * 1024,
        "accepted_project_head_unchanged": True,
        "immutable_asset_written": True,
        "new_track_or_clip_accepted": False,
        "staging_files_remaining": 0,
        "screenshots": screenshots,
        "three_minute_two_track_mix_proven": False,
        "streaming_finalize_proven": False,
        "physical_audio_io_proven": False,
    }
    write_canonical_json(out / "proof.json", proof)
    return proof


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_suite(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
