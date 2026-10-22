"""PROD-E2E-R1B-G1: real Chromium two-source two-track production and PCM oracle.

User clicks only existing, governed first-party Studio editing controls; no
programmatic creative Accept. Real hardware, third-party DSP and commercial
mastering are expressly outside this bounded product evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import struct
import wave
from pathlib import Path

from .evidence import write_canonical_json
from .prod_e2e_r1a_browser import _record_request_failure, _server, _stop


def source_wav(level: int, sample_rate_hz: int = 8000) -> tuple[bytes, list[int]]:
    samples = [level if index % 4 < 2 else -level for index in range(2 * sample_rate_hz)]
    file = io.BytesIO()
    with wave.open(file, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate_hz)
        output.writeframes(struct.pack("<" + "h" * len(samples), *samples))
    return file.getvalue(), samples


def suite(destination: str | Path, *, sample_rate_hz: int = 8000) -> dict:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:
        raise RuntimeError("G1 requires .[dev,e2e] and real Playwright Chromium") from exc

    out = Path(destination)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    workspace = out / "workspace"
    workspace.mkdir()
    if sample_rate_hz not in (8000, 44100, 48000):
        raise ValueError("G1 evidence requires a declared tested 8k/44.1k/48k exact sample rate")
    source_frames = 2 * sample_rate_hz
    output_frames = 12 * sample_rate_hz
    assets = [source_wav(3000, sample_rate_hz), source_wav(6200, sample_rate_hz)]
    asset_ids = ["sha256:" + hashlib.sha256(item[0]).hexdigest() for item in assets]
    assert asset_ids[0] != asset_ids[1]
    console_errors, page_errors, network_errors, images, http_errors = [], [], [], [], []

    service, server, thread, url = _server(workspace)
    browser = None
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1200}, accept_downloads=True)
            context.set_default_timeout(35000)
            page = context.new_page()
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.on("requestfailed", lambda req: _record_request_failure(req, network_errors))
            page.on("response", lambda response: http_errors.append(
                f"{response.status} {response.request.method} {response.url}"
            ) if response.status >= 400 else None)
            page.goto(url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#projectSlug").fill("r1b-g1-two-track")
            page.locator("#durationSeconds").fill("12")
            page.locator("#useCase").select_option("song")
            page.locator("#createForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioWorkspace")).to_be_visible()
            session = next(iter(service._sessions.values()))
            original = session.project.head_revision_id()

            def import_wav(index: int):
                prior = session.project.head_revision_id()
                page.locator("#r3WavFile").set_input_files({
                    "name": "source-" + str(index + 1) + ".wav",
                    "mimeType": "audio/wav",
                    "buffer": assets[index][0],
                })
                page.locator("#r3ImportWav").click()
                expect(page.locator("#r3NewAssetId")).to_have_value(asset_ids[index])
                assert session.project.head_revision_id() == prior

            def accept_preview(before: str, label: str):
                try:
                    expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
                except AssertionError as exc:
                    diagnostic = page.evaluate("""() => ({
                        status: document.getElementById("r3AudioStatus")?.textContent,
                        statusClass: document.getElementById("r3AudioStatus")?.className,
                        authority: window.MUSICA_NATIVE_AUDIO?.state?.lastAuthorityResult,
                        candidate: window.MUSICA_NATIVE_AUDIO?.state?.lastSubmittedCandidate
                    })""")
                    raise AssertionError(label + " failed to install Preview: " +
                                         json.dumps(diagnostic, ensure_ascii=False)) from exc
                assert session.project.head_revision_id() == before, label + " Preview mutated HEAD"
                expect(page.locator("#r1bDownloadWav")).to_be_disabled()
                page.locator("#r3Accept").click()
                expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("ACCEPTED")
                after = session.project.head_revision_id()
                assert after != before, label + " explicit Accept did not advance HEAD"
                return after

            import_wav(0)
            page.locator("#r3SuggestTrackId").click()
            expect(page.locator("#r3NewTrackId")).to_have_value("AT-UI-001")
            assert session.project.head_revision_id() == original
            page.locator("#r3NewTrackName").fill("Melody")
            page.locator("#r3AddTrack").click()
            head = accept_preview(original, "track1")
            page.locator("#r3SuggestClipId").click()
            expect(page.locator("#r3NewClipId")).to_have_value("AC-UI-001")
            page.locator("#r3AddClip").click()
            head = accept_preview(head, "clip1")

            first = "01-first-source.png"
            page.screenshot(path=str(out / first), full_page=True)
            images.append(first)
            import_wav(1)
            page.locator("#r3SuggestTrackId").click()
            expect(page.locator("#r3NewTrackId")).to_have_value("AT-UI-002")
            expect(page.locator("#r3NewTrackOrder")).to_have_value("1")
            page.locator("#r3NewTrackName").fill("Drums")
            page.locator("#r3AddTrack").click()
            head = accept_preview(head, "track2")
            page.locator("#r3ClipTrack").select_option("AT-UI-002")
            page.locator("#r3SuggestClipId").click()
            expect(page.locator("#r3NewClipId")).to_have_value("AC-UI-002")
            page.locator("#r3AddClip").click()
            head = accept_preview(head, "clip2")

            expect(page.locator("#r1bStepState2")).to_have_text("2 TRACKS / 2 CLIPS ACCEPTED")
            view = page.evaluate("() => JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.view))")
            assert len(view["tracks"]) == 2
            assert [t["clips"][0]["asset_id"] for t in view["tracks"]] == asset_ids
            second = "02-two-accepted-tracks.png"
            page.screenshot(path=str(out / second), full_page=True)
            images.append(second)

            # Each mono source is independently panned to one output channel.
            for track_id, pan in (("AT-UI-001", "-1"), ("AT-UI-002", "1")):
                track = page.locator('#r3TrackList .r3-track[data-track-id="' + track_id + '"]')
                track.locator('[data-field="track-pan"]').fill(pan)
                track.locator('[data-action="preview-mixer"]').click()
                head = accept_preview(head, "mixer " + track_id)
            expect(page.locator("#r1bDownloadWav")).to_be_enabled()
            view = page.evaluate("() => JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.view))")
            assert [t["mixer"]["pan"] for t in view["tracks"]] == [-1.0, 1.0]
            wav_sha = view["accepted_audition"]["wav_sha256"]
            with page.expect_download() as result:
                page.locator("#r1bDownloadWav").click()
            downloaded = result.value
            assert downloaded.suggested_filename == "musica-accepted-" + wav_sha[:12] + ".wav"
            downloaded.save_as(out / "two-track-accepted.wav")
            rendered = (out / "two-track-accepted.wav").read_bytes()
            assert hashlib.sha256(rendered).hexdigest() == wav_sha
            with wave.open(io.BytesIO(rendered), "rb") as reader:
                assert (reader.getnchannels(), reader.getframerate(), reader.getsampwidth(), reader.getnframes()) == (2, sample_rate_hz, 2, output_frames)
                payload = reader.readframes(reader.getnframes())
            mix = struct.unpack("<" + "h" * (len(payload) // 2), payload)
            left, right = mix[::2], mix[1::2]
            # Independent deterministic PCM oracle: each track contributes an
            # exact different source only to its assigned stereo channel.
            assert list(left[:source_frames]) == assets[0][1], "Melody contribution missing or altered"
            assert list(right[:source_frames]) == assets[1][1], "Drum contribution missing or altered"
            assert all(value == 0 for value in left[source_frames:] + right[source_frames:])
            assert max(map(abs, mix)) == 6200
            assert sum(abs(value) >= 32767 for value in mix) == 0

            page.locator("#r1bGo6").click()
            page.locator("#exportButton").click()
            expect(page.locator("#exportResult")).to_contain_text(".musica")
            third = "03-pan-separated-stereo-export.png"
            page.screenshot(path=str(out / third), full_page=True)
            images.append(third)
            context.close()
            browser.close()
            browser = None
    finally:
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass  # Preserve primary failure after Playwright context exit.
        _stop(server, thread)

    reopened_service, reopened_server, reopened_thread, reopened_url = _server(workspace)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1200}, accept_downloads=True)
            page = context.new_page()
            page.goto(reopened_url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill("r1b-g1-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r1bStepState2")).to_have_text("2 TRACKS / 2 CLIPS ACCEPTED")
            reopened_session = next(iter(reopened_service._sessions.values()))
            assert reopened_session.project.head_revision_id() == head
            assert reopened_session.project.verify_integrity()["status"] == "PASS"
            view = page.evaluate("() => JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.view))")
            assert [t["clips"][0]["asset_id"] for t in view["tracks"]] == asset_ids
            assert [t["mixer"]["pan"] for t in view["tracks"]] == [-1.0, 1.0]
            assert view["accepted_audition"]["wav_sha256"] == wav_sha
            with page.expect_download() as result:
                page.locator("#r1bDownloadWav").click()
            result.value.save_as(out / "two-track-reopened.wav")
            assert (out / "two-track-reopened.wav").read_bytes() == rendered
            fourth = "04-reopened-multitrack.png"
            page.screenshot(path=str(out / fourth), full_page=True)
            images.append(fourth)
            context.close()
            browser.close()
    finally:
        _stop(reopened_server, reopened_thread)

    if console_errors or page_errors or network_errors:
        raise RuntimeError(
            "Unexpected Chromium error console=%r page=%r network=%r http=%r"
            % (console_errors, page_errors, network_errors, http_errors)
        )
    report = {
        "milestone": "PROD-E2E-R1B-G1", "proof_version": "0",
        "automated_real_chromium_controls": True,
        "distinct_imported_assets": asset_ids,
        "accepted_tracks": 2, "accepted_clips": 2,
        "distinct_manual_source_authorities": 2,
        "explicit_accept_operations": 6,
        "preview_or_import_mutated_head": False,
        "stereo_pan": [-1.0, 1.0],
        "independent_pcm_oracle": True,
        "output_wav_sha256": wav_sha,
        "output_sample_rate_hz": sample_rate_hz, "output_frames": output_frames,
        "nonzero_scalar_samples": 2 * source_frames,
        "peak_pcm16": 6200, "clipped_samples": 0,
        "accepted_head_reopened_exact": True,
        "wav_reopened_byte_exact": True,
        "screenshots": images,
        "console_errors": len(console_errors), "page_errors": len(page_errors),
        "network_errors": len(network_errors),
        "real_mic_or_device": False,
        "real_third_party_plugin_binary": False,
        "commercial_mastered_song": False
    }
    write_canonical_json(out / "proof.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    suite(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
