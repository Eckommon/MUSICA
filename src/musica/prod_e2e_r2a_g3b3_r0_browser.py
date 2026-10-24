"""G3B3-R0: real Chromium, TWO user-picked 180s PCM sources -> explicit
track/clip Preview/Accept -> accepted 180s WAV output -> reopen byte-exact.

This is automated headless Chromium and deterministic PCM, NOT a human pilot,
real microphone, third-party plugin ABI, routed automation, or mastered song.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import wave

from .audio_assets import list_audio_assets
from .evidence import write_canonical_json
from .prod_e2e_r1a_browser import _server, _stop

FRAMES = 8_640_000
RATE = 48_000
EXPECTED_BYTES = 34_560_044


def _write_source(path: Path, left: int, right: int) -> str:
    # File-backed resource avoids encoding a 34.56MB WAV in a Playwright
    # in-memory set_input_files buffer; each PCM write is <= 1MiB.
    frame = struct.pack("<hh", left, right)
    with wave.open(str(path), "wb") as target:
        target.setnchannels(2)
        target.setsampwidth(2)
        target.setframerate(RATE)
        for _ in range(32):
            target.writeframesraw(frame * (262_144))
        target.writeframes(frame * (FRAMES - 32 * 262_144))
    assert path.stat().st_size == EXPECTED_BYTES
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()


def run_suite(dest: str | Path) -> dict:
    from playwright.sync_api import expect, sync_playwright

    out = Path(dest).resolve()
    out.mkdir(parents=True, exist_ok=True)
    workspace = out / "workspace"
    inputs = out / "user-picked"
    inputs.mkdir(exist_ok=True)
    names = [inputs / "first-180s.wav", inputs / "second-180s.wav"]
    hashes = [_write_source(names[0], 2000, -1000),
              _write_source(names[1], 1200, -400)]
    assert hashes[0] != hashes[1]
    project_slug = "g3b3-user-two-180s"
    events = []
    errors = []
    photos = []
    accepted_head = None
    output_hash = None

    studio, server, thread, url = _server(workspace)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1600, "height": 1200},
                accept_downloads=True,
            )
            context.set_default_timeout(180000)
            page = context.new_page()
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.on("console", lambda msg: errors.append(msg.text)
                    if msg.type == "error" else None)
            page.goto(url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#projectSlug").fill(project_slug)
            page.locator("#durationSeconds").fill("180")
            page.locator("#useCase").select_option("song")
            page.locator("#createForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible(timeout=120000)
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioImport")).to_be_visible()
            expect(page.locator("#r3AudioWorkspace")).to_be_visible()
            session = next(iter(studio._sessions.values()))
            prior = session.project.head_revision_id()

            def track_transition(label: str, before: str) -> str:
                expect(page.locator("#r3AudioAuthorityBadge")).to_have_text(
                    "PREVIEW · NOT ACCEPTED", timeout=120000
                )
                assert session.project.head_revision_id() == before, label
                pending = page.evaluate(
                    "() => window.MUSICA_NATIVE_AUDIO.state.view.preview"
                )
                assert pending and pending["preview_id"]
                assert pending["candidate_revision_id"] != before
                events.append({"step": label + " Preview", "head": before,
                               "pending_id": pending["preview_id"]})
                page.locator("#r3Accept").click()
                expect(page.locator("#r3AudioAuthorityBadge")).to_have_text(
                    "ACCEPTED", timeout=120000
                )
                head = session.project.head_revision_id()
                assert head != before
                events.append({"step": label + " explicit Accept", "head": head})
                return head

            for index in range(2):
                assert session.project.head_revision_id() == prior
                page.locator("#r3WavFile").set_input_files(str(names[index]))
                page.locator("#r3ImportWav").click()
                expect(page.locator("#r3NewAssetId")).to_have_value(
                    "sha256:" + hashes[index], timeout=180000
                )
                expect(page.locator("#r3ImportedAsset")).to_contain_text(
                    "NOT A CLIP")
                assert session.project.head_revision_id() == prior
                events.append({"step": f"file {index+1} resource-only",
                               "head": prior, "sha256": hashes[index]})

                page.locator("#r3SuggestTrackId").click()
                track_id = f"AT-UI-{index+1:03d}"
                expect(page.locator("#r3NewTrackId")).to_have_value(track_id)
                page.locator("#r3NewTrackName").fill(f"Long source {index+1}")
                page.locator("#r3AddTrack").click()
                prior = track_transition(f"track {index+1}", prior)

                page.locator("#r3ClipTrack").select_option(track_id)
                page.locator("#r3SuggestClipId").click()
                expect(page.locator("#r3NewClipId")).to_have_value(
                    f"AC-UI-{index+1:03d}"
                )
                page.locator("#r3AddClip").click()
                prior = track_transition(f"clip {index+1}", prior)

            resources = list_audio_assets(session.project)
            assert len(resources) == 2
            assert {x["object_sha256"] for x in resources} == set(hashes)
            view = page.evaluate(
                "() => JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.view))"
            )
            assert len(view["tracks"]) == 2
            assert [len(t["clips"]) for t in view["tracks"]] == [1, 1]
            assert [t["clips"][0]["asset_id"] for t in view["tracks"]] == [
                "sha256:" + h for h in hashes
            ]
            accepted_head = prior
            expect(page.locator("#r3StreamedAcceptedWavDownload")).to_be_visible()
            before_download = session.project.head_revision_id()
            page.wait_for_function("""() => {
                const player = document.getElementById("r3AudioPlayer");
                return player && player.readyState >= 1 &&
                    Number.isFinite(player.duration) &&
                    Math.abs(player.duration - 180) < 0.02;
            }""", timeout=240000)
            assert session.project.head_revision_id() == before_download
            page.screenshot(path=str(out / "01-two-180s-accepted-tracks.png"),
                            full_page=True)
            photos.append("01-two-180s-accepted-tracks.png")
            with page.expect_download(timeout=240000) as event:
                page.locator("#r3StreamedAcceptedWavDownload").click()
            wav = out / "browser-accepted-180s.wav"
            event.value.save_as(wav)
            assert wav.stat().st_size == EXPECTED_BYTES
            output_hash = hashlib.file_digest(wav.open("rb"), "sha256").hexdigest()
            with wave.open(str(wav), "rb") as reader:
                assert (reader.getframerate(), reader.getnchannels(),
                        reader.getsampwidth(), reader.getnframes()) == (
                    RATE, 2, 2, FRAMES
                )
                for index in (0, FRAMES // 2, FRAMES - 1):
                    reader.setpos(index)
                    assert struct.unpack("<hh", reader.readframes(1)) == (
                        3200, -1400
                    )
            assert session.project.head_revision_id() == before_download
            page.screenshot(path=str(out / "02-accepted-user-download.png"),
                            full_page=True)
            photos.append("02-accepted-user-download.png")
            assert session.project.verify_integrity()["status"] == "PASS"
            context.close()
            browser.close()
    finally:
        _stop(server, thread)

    # A *new* actual Browser + Studio process must reopen the user's project
    # and output the exact same PCM WAV without any implicit creative Accept.
    studio2, server2, thread2, url2 = _server(workspace)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1600, "height": 1200},
                accept_downloads=True,
            )
            context.set_default_timeout(180000)
            page = context.new_page()
            page.goto(url2 + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill(project_slug)
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioWorkspace")).to_be_visible()
            project = next(iter(studio2._sessions.values())).project
            assert project.head_revision_id() == accepted_head
            expect(page.locator("#r3StreamedAcceptedWavDownload")).to_be_visible()
            with page.expect_download(timeout=240000) as event:
                page.locator("#r3StreamedAcceptedWavDownload").click()
            reopened = out / "browser-reopened-180s.wav"
            event.value.save_as(reopened)
            assert reopened.stat().st_size == EXPECTED_BYTES
            assert hashlib.file_digest(
                reopened.open("rb"), "sha256"
            ).hexdigest() == output_hash
            assert project.head_revision_id() == accepted_head
            page.screenshot(path=str(out / "03-180s-project-reopened.png"),
                            full_page=True)
            photos.append("03-180s-project-reopened.png")
            context.close()
            browser.close()
    finally:
        _stop(server2, thread2)

    assert not errors, errors
    proof = {
        "milestone": "PROD-E2E-R2A-G3B3-R0",
        "actual_headless_chromium_ui": True,
        "first_party_user_selected_sources": 2,
        "source_wav_length_s": 180,
        "source_sample_rate_hz": RATE,
        "source_sha256": hashes,
        "source_pcm_stereo_levels": [[2000, -1000], [1200, -400]],
        "resource_import_auto_accept": False,
        "explicit_track_clip_accept_actions": 4,
        "audio_tracks": 2,
        "accepted_clips": 2,
        "derived_wav_bytes": EXPECTED_BYTES,
        "derived_wav_sha256": output_hash,
        "derived_stereo_pcm_at_start_middle_end": [3200, -1400],
        "accepted_head_reopened_equal": True,
        "reopened_wav_sha256_exact": True,
        "head_transitions": events,
        "console_errors": errors,
        "screenshots": photos,
        "full_routed_automation_preview_accept": False,
        "actual_human_pilot": False,
        "third_party_plugin_binary_or_device_latency": False,
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
