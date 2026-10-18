"""PROD-E2E-R1B-G0: real Chromium proof of guided local production controls.

This is an automated UI exercise of bounded audio, not a human usability study
or professional-length song/physical sound device/plugin evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import wave
from pathlib import Path

from .audio_assets import read_audio_asset
from .evidence import write_canonical_json
from .prod_e2e_r1a_browser import _server, _stop, _record_request_failure


def _wav() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        # Two seconds of nonzero, deterministic, signed 16-bit test audio.
        output.writeframes(b"".join(
            int(3500 if i % 4 < 2 else -3500).to_bytes(2, "little", signed=True)
            for i in range(16000)
        ))
    return buffer.getvalue()


def run_suite(destination: str | Path) -> dict:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:
        raise RuntimeError("Install MUSICA .[dev,e2e] and Playwright Chromium") from exc
    out = Path(destination)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    workspace = out / "workspace"
    workspace.mkdir()
    wav = _wav()
    asset_id = "sha256:" + hashlib.sha256(wav).hexdigest()
    console_errors, page_errors, request_failures, screenshots = [], [], [], []
    service, server, thread, url = _server(workspace)
    browser = None
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1500, "height": 1200}, accept_downloads=True)
            context.set_default_timeout(35_000)
            page = context.new_page()
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.on("requestfailed", lambda request: _record_request_failure(request, request_failures))
            page.goto(url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#projectSlug").fill("r1b-guide-first-song")
            page.locator("#durationSeconds").fill("12")
            page.locator("#useCase").select_option("song")
            page.locator("#createForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            session = next(iter(service._sessions.values()))
            first_head = session.project.head_revision_id()

            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r1bGuide")).to_be_visible()
            expect(page.locator("#r1bStepState0")).to_have_text("ACCEPTED SESSION")
            expect(page.locator("#r1bDownloadWav")).to_be_disabled()
            page.locator("#r1bGo1").click()
            expect(page.locator("#r3WavFile")).to_be_focused()
            page.locator("#r3WavFile").set_input_files({
                "name": "user-recording.wav", "mimeType": "audio/wav", "buffer": wav
            })
            page.locator("#r3ImportWav").click()
            expect(page.locator("#r3NewAssetId")).to_have_value(asset_id)
            assert session.project.head_revision_id() == first_head, "Resource import changed accepted HEAD"
            assert read_audio_asset(session.project, asset_id)["format"]["frame_count"] == 16000
            expect(page.locator("#r1bStepState2")).to_have_text("TRACK / CLIP NEEDED")
            image = "01-guide-import.png"
            page.screenshot(path=str(out / image), full_page=True)
            screenshots.append(image)

            page.locator("#r1bGo2").click()
            page.locator("#r3AddTrack").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            assert session.project.head_revision_id() == first_head
            expect(page.locator("#r1bDownloadWav")).to_be_disabled()
            page.locator("#r3Accept").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("ACCEPTED")
            track_head = session.project.head_revision_id()
            assert track_head != first_head
            expect(page.locator("#r1bStepState2")).to_contain_text("TRACK ACCEPTED")
            page.locator("#r3AddClip").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            assert session.project.head_revision_id() == track_head
            expect(page.locator("#r1bDownloadWav")).to_be_disabled()
            image = "02-guide-preview-blocks-delivery.png"
            page.screenshot(path=str(out / image), full_page=True)
            screenshots.append(image)
            page.locator("#r3Accept").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("ACCEPTED")
            clip_head = session.project.head_revision_id()
            assert clip_head != track_head
            expect(page.locator("#r1bStepState2")).to_have_text("ACCEPTED CLIP")
            expect(page.locator("#r1bDownloadWav")).to_be_enabled()
            accepted = page.evaluate(
                "() => JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.view))"
            )
            wav_sha = accepted["accepted_audition"]["wav_sha256"]
            with page.expect_download() as download_info:
                page.locator("#r1bDownloadWav").click()
            download = download_info.value
            assert download.suggested_filename == "musica-accepted-" + wav_sha[:12] + ".wav"
            delivery_path = out / "accepted-guide.wav"
            download.save_as(delivery_path)
            delivered = delivery_path.read_bytes()
            assert hashlib.sha256(delivered).hexdigest() == wav_sha
            assert delivered[:4] == b"RIFF" and delivered[8:12] == b"WAVE"
            with wave.open(io.BytesIO(delivered), "rb") as handle:
                assert handle.getnchannels() == 1
                assert handle.getframerate() == 8000
                assert handle.getnframes() > 0
                assert any(b != 0 for b in handle.readframes(handle.getnframes()))
            page.locator("#r1bGo6").click()
            page.locator("#exportButton").click()
            expect(page.locator("#exportResult")).to_contain_text(".musica")
            image = "03-guide-accepted-delivery.png"
            page.screenshot(path=str(out / image), full_page=True)
            screenshots.append(image)
            context.close()
            browser.close()
            browser = None
    finally:
        if browser is not None:
            browser.close()
        _stop(server, thread)

    reopened_service, reopened_server, reopened_thread, reopened_url = _server(workspace)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1500, "height": 1200}, accept_downloads=True)
            page = context.new_page()
            page.goto(reopened_url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill("r1b-guide-first-song")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r1bStepState2")).to_have_text("ACCEPTED CLIP")
            expect(page.locator("#r1bDownloadWav")).to_be_enabled()
            reopened_session = next(iter(reopened_service._sessions.values()))
            assert reopened_session.project.head_revision_id() == clip_head
            assert reopened_session.project.verify_integrity()["status"] == "PASS"
            with page.expect_download() as reopened_info:
                page.locator("#r1bDownloadWav").click()
            reopened_info.value.save_as(out / "accepted-reopened.wav")
            assert (out / "accepted-reopened.wav").read_bytes() == delivered
            image = "04-guide-reopened.png"
            page.screenshot(path=str(out / image), full_page=True)
            screenshots.append(image)
            context.close()
            browser.close()
    finally:
        _stop(reopened_server, reopened_thread)

    if console_errors or page_errors or request_failures:
        raise RuntimeError(
            "Unexpected Browser errors: console=%r page=%r network=%r"
            % (console_errors, page_errors, request_failures)
        )
    proof = {
        "milestone": "PROD-E2E-R1B-G0",
        "proof_version": "0",
        "automated_real_chromium_controls": True,
        "imported_asset_id": asset_id,
        "import_mutated_accepted_head": False,
        "track_preview_mutated_head": False,
        "clip_preview_mutated_head": False,
        "explicit_track_accept": True,
        "explicit_clip_accept": True,
        "download_blocked_before_accept": True,
        "accepted_wav_sha256": wav_sha,
        "delivered_bytes": len(delivered),
        "reopened_exact_accepted_wav": True,
        "project_head": clip_head,
        "screenshots": screenshots,
        "console_error_count": len(console_errors),
        "page_error_count": len(page_errors),
        "network_failure_count": len(request_failures),
        "physical_io_proven": False,
        "third_party_plugin_binary_proven": False,
        "full_song_commercial_readiness": False,
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
