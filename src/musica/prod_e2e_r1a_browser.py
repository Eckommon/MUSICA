"""PROD-E2E-R1A real-Chromium user-operated WAV resource import evidence.

This is a bounded real browser click/file-picker lifecycle, not proof of general
music quality, 48kHz hardware performance, or full end-to-end song production.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import threading
import wave
from pathlib import Path

from .audio_assets import read_audio_asset
from .evidence import write_canonical_json
from .studio import StudioService
from .studio_http_r3 import create_local_server


def _wav() -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b"".join(
            int(4100 if index % 4 < 2 else -4100).to_bytes(2, "little", signed=True)
            for index in range(800)
        ))
    return stream.getvalue()


def _server(workspace):
    service = StudioService(workspace)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    host, port = server.server_address[:2]
    return service, server, thread, f"http://{host}:{port}"


def _stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    if thread.is_alive():
        raise RuntimeError("Browser Studio HTTP server failed to shut down")


def _head(service):
    session = next(iter(service._sessions.values()))
    return session.project.head_revision_id(), session


def _record_request_failure(request, failures):
    if request.failure != "net::ERR_ABORTED":
        failures.append(f"{request.method} {request.url} :: {request.failure}")


def run_suite(out_dir: str | Path) -> dict:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:
        raise RuntimeError("R1A requires .[dev,e2e] and Playwright Chromium") from exc

    out = Path(out_dir)
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
            context = browser.new_context(viewport={"width": 1500, "height": 1200})
            context.set_default_timeout(35_000)
            page = context.new_page()
            page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            page.on("requestfailed", lambda r: _record_request_failure(r, request_failures))
            page.goto(url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#projectSlug").fill("browser-first-song")
            page.locator("#durationSeconds").fill("12")
            page.locator("#useCase").select_option("song")
            page.locator("#createForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            first_head, session = _head(service)
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioImport")).to_be_visible()
            page.locator("#r3WavFile").set_input_files({
                "name": "my-melody.wav", "mimeType": "audio/wav", "buffer": wav
            })
            page.locator("#r3ImportWav").click()
            expect(page.locator("#r3NewAssetId")).to_have_value(asset_id)
            expect(page.locator("#r3ImportedAsset")).to_contain_text("NOT A CLIP")
            assert session.project.head_revision_id() == first_head, "import advanced creative HEAD"
            assert read_audio_asset(session.project, asset_id)["format"]["frame_count"] == 800
            name = "01-browser-import-resource.png"
            page.screenshot(path=str(out / name), full_page=True)
            screenshots.append(name)

            expect(page.locator("#r3NewTrackOrder")).to_have_value("0")
            page.locator("#r3AddTrack").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            assert session.project.head_revision_id() == first_head, "track Preview advanced HEAD"
            assert page.locator("#r3AudioPlayer").is_hidden(), "empty track fabricated audio"
            name = "02-empty-track-preview.png"
            page.screenshot(path=str(out / name), full_page=True)
            screenshots.append(name)
            page.locator("#r3Accept").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("ACCEPTED")
            track_head = session.project.head_revision_id()
            assert track_head != first_head, "explicit track Accept did not advance HEAD"

            expect(page.locator("#r3NewAssetId")).to_have_value(asset_id)
            page.locator("#r3AddClip").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            assert session.project.head_revision_id() == track_head, "clip Preview advanced HEAD"
            name = "03-audible-clip-preview.png"
            page.screenshot(path=str(out / name), full_page=True)
            screenshots.append(name)
            page.locator("#r3Accept").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("ACCEPTED")
            clip_head = session.project.head_revision_id()
            assert clip_head != track_head, "explicit clip Accept did not advance HEAD"
            page.wait_for_function(
                "() => window.MUSICA_NATIVE_AUDIO && "
                "window.MUSICA_NATIVE_AUDIO.state.view && "
                "window.MUSICA_NATIVE_AUDIO.state.view.accepted_audition.available"
            )
            audio_state = page.evaluate(
                "() => JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.view))"
            )
            assert audio_state["tracks"][0]["clips"][0]["asset_id"] == asset_id
            assert audio_state["accepted_audition"]["available"] is True
            page.locator("#exportButton").click()
            expect(page.locator("#exportResult")).to_contain_text(".musica")
            name = "04-accepted-export.png"
            page.screenshot(path=str(out / name), full_page=True)
            screenshots.append(name)
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
            context = browser.new_context(viewport={"width": 1500, "height": 1200})
            page = context.new_page()
            page.goto(reopened_url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill("browser-first-song")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("ACCEPTED")
            page.wait_for_function(
                "() => window.MUSICA_NATIVE_AUDIO && "
                "window.MUSICA_NATIVE_AUDIO.state.view && "
                "window.MUSICA_NATIVE_AUDIO.state.view.accepted_audition.available"
            )
            reopened_head, reopened_session = _head(reopened_service)
            assert reopened_head == clip_head, "restart changed accepted HEAD"
            assert read_audio_asset(reopened_session.project, asset_id)["format"]["frame_count"] == 800
            replay_state = page.evaluate(
                "() => JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.view))"
            )
            assert replay_state["accepted_audition"]["wav_sha256"] == audio_state["accepted_audition"]["wav_sha256"]
            assert reopened_session.project.verify_integrity()["status"] == "PASS"
            name = "05-reopened-browser-audio.png"
            page.screenshot(path=str(out / name), full_page=True)
            screenshots.append(name)
            context.close()
            browser.close()
    finally:
        _stop(reopened_server, reopened_thread)

    if console_errors or page_errors or request_failures:
        raise RuntimeError(
            f"Browser errors: console={console_errors}, page={page_errors}, requests={request_failures}"
        )
    proof = {
        "evidence_version": "0", "milestone": "PROD-E2E-R1A",
        "user_operated_real_chromium": True,
        "direct_local_wav_import": True,
        "asset_id": asset_id, "asset_sha256": hashlib.sha256(wav).hexdigest(),
        "initial_head": first_head, "track_accepted_head": track_head,
        "clip_accepted_head": clip_head, "reopened_head": reopened_head,
        "import_kept_creative_head": True, "track_preview_not_accepted": True,
        "empty_track_audio_fabricated": False, "clip_preview_not_accepted": True,
        "explicit_browser_track_accept": True, "explicit_browser_clip_accept": True,
        "accepted_wav_sha256": audio_state["accepted_audition"]["wav_sha256"],
        "reopened_wav_sha256": replay_state["accepted_audition"]["wav_sha256"],
        "physical_mic_or_device_proven": False, "third_party_plugin_binary_proven": False,
        "commercial_release_ready": False,
        "screenshots": screenshots,
        "console_error_count": len(console_errors),
        "page_error_count": len(page_errors),
        "request_failure_count": len(request_failures),
    }
    write_canonical_json(out / "proof.json", proof)
    return proof


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_suite(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
