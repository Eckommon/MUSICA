"""PROD-E2E G2B actual Chromium 2-bus routed source and output proof.

Reuses the real G1 operator-generated two-WAV project, then independently
operates first-party routing Preview and explicit user Accept from the Browser.
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
from .prod_e2e_r1a_browser import _record_request_failure, _server, _stop
from .prod_e2e_r1b_g1_browser import suite as seed_g1


def _pcm(data: bytes) -> tuple[int, int, int, list[int]]:
    import struct
    with wave.open(io.BytesIO(data), "rb") as reader:
        channels, width, rate, frames = (
            reader.getnchannels(), reader.getsampwidth(),
            reader.getframerate(), reader.getnframes()
        )
        raw = reader.readframes(frames)
    if width != 2 or channels != 2:
        raise AssertionError("Routed mix must be exact stereo PCM16")
    return rate, channels, frames, list(struct.unpack("<" + "h" * (len(raw) // 2), raw))


def run_suite(destination: str | Path) -> dict:
    from playwright.sync_api import expect, sync_playwright
    out = Path(destination)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    seed_g1(out / "seed-g1")
    workspace = out / "seed-g1" / "workspace"
    baseline = (out / "seed-g1" / "two-track-accepted.wav").read_bytes()
    rate, channels, frames, original = _pcm(baseline)
    assert (rate, channels, frames) == (8000, 2, 96000)
    errors, page_errors, failures, images = [], [], [], []
    service, server, thread, url = _server(workspace)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1200}, accept_downloads=True)
            context.set_default_timeout(35000)
            page = context.new_page()
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            page.on("requestfailed", lambda request: _record_request_failure(request, failures))
            page.goto(url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill("r1b-g1-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioWorkspace")).to_be_visible()
            expect(page.locator("#mramRoutingWorkspace")).to_be_visible()
            expect(page.locator("#mramPreviewStarterTwoBus")).to_be_visible()
            session = next(iter(service._sessions.values()))
            baseline_head = session.project.head_revision_id()
            page.locator("#mramPreviewStarterTwoBus").click()
            expect(page.locator("#mramRoutingBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            assert session.project.head_revision_id() == baseline_head
            expect(page.locator("#mramNodes [data-mram-type=node]")).to_have_count(3)
            expect(page.locator("#mramTrackOutputs [data-mram-type=track-output]")).to_have_count(2)
            image = "01-two-bus-routing-preview.png"
            page.screenshot(path=str(out / image), full_page=True)
            images.append(image)
            page.locator("#acceptButton").click()
            expect(page.locator("#mramRoutingBadge")).to_have_text("ACCEPTED ROUTING")
            expect(page.locator("#mramNodes [data-mram-type=node]")).to_have_count(3)
            routed_head = session.project.head_revision_id()
            assert routed_head != baseline_head
            page.wait_for_function("""head => {
              const view = window.MUSICA_ROUTING?.state?.view;
              return view && !view.preview && view.revision_id === head &&
                view.nodes?.length === 3 && view.track_outputs?.length === 2;
            }""", arg=routed_head, timeout=35000)
            view = page.evaluate("() => window.MUSICA_ROUTING.state.view")
            assert [x["track_id"] for x in view["track_outputs"]] == ["AT-UI-001", "AT-UI-002"]
            assert [x["target_node_id"] for x in view["track_outputs"]] == ["BUS-UI-001", "BUS-UI-002"]
            expect(page.locator("#mramPreviewStarterTwoBus")).to_be_disabled()
            page.locator("#mramNodeSelect").select_option("BUS-UI-001")
            page.locator("#mramNodeGain").fill("-6")
            page.locator("#mramPreviewNodeMixer").click()
            expect(page.locator("#mramRoutingBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            assert session.project.head_revision_id() == routed_head
            image = "02-bus-gain-preview.png"
            page.screenshot(path=str(out / image), full_page=True)
            images.append(image)
            page.locator("#acceptButton").click()
            expect(page.locator("#mramRoutingBadge")).to_have_text("ACCEPTED ROUTING")
            gain_head = session.project.head_revision_id()
            assert gain_head != routed_head
            # The badge may say ACCEPTED while its read-only routing GET
            # still refers to the previous accepted revision. Require the
            # exact new authoritative HEAD AND mixer value before proceeding.
            page.wait_for_function("""head => {
              const view = window.MUSICA_ROUTING?.state?.view;
              const bus = view?.nodes?.find(n => n.node_id === "BUS-UI-001");
              return view && !view.preview && view.revision_id === head &&
                bus && bus.mixer.gain_db === -6;
            }""", arg=gain_head, timeout=35000)
            accepted = page.evaluate("() => window.MUSICA_ROUTING.state.view")
            assert next(n for n in accepted["nodes"] if n["node_id"]=="BUS-UI-001")["mixer"]["gain_db"] == -6.0
            # A trusted routing Accept advances the exact project HEAD. A
            # previously enabled button from the earlier audio-only revision
            # is NOT proof that the accepted-derived WAV is current.
            page.wait_for_function("""() => {
              const audio = window.MUSICA_NATIVE_AUDIO?.state?.view;
              const route = window.MUSICA_ROUTING?.state?.view;
              return audio && route && !audio.preview && !route.preview &&
                audio.revision_id === route.revision_id &&
                audio.accepted_audition?.available;
            }""", timeout=35000)
            expect(page.locator("#r1bDownloadWav")).to_be_enabled()
            with page.expect_download() as info:
                page.locator("#r1bDownloadWav").click()
            info.value.save_as(out / "routed-accepted.wav")
            mixed = (out / "routed-accepted.wav").read_bytes()
            new_rate, new_channels, new_frames, changed = _pcm(mixed)
            assert (new_rate, new_channels, new_frames) == (rate, channels, frames)
            assert changed != original, "accepted routing mixer gain had no sound effect"
            assert max(abs(changed[i]) for i in range(0, len(changed), 2)) < max(
                abs(original[i]) for i in range(0, len(original), 2)
            ), "first bus must attenuate left channel"
            assert all(changed[i] == original[i] for i in range(1, len(changed), 2)), (
                "unmodified second bus must preserve right-channel source PCM exactly"
            )
            image = "03-accepted-bus-output.png"
            page.screenshot(path=str(out / image), full_page=True)
            images.append(image)
            page.locator("#exportButton").click()
            expect(page.locator("#exportResult")).to_contain_text(".musica")
            context.close()
            browser.close()
    finally:
        _stop(server, thread)

    service2, server2, thread2, url2 = _server(workspace)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True, viewport={"width": 1600, "height": 1200})
            page = context.new_page()
            page.goto(url2 + "/", wait_until="domcontentloaded")
            page.locator("#openProjectSlug").fill("r1b-g1-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#mramRoutingBadge")).to_have_text("ACCEPTED ROUTING")
            assert next(iter(service2._sessions.values())).project.head_revision_id() == gain_head
            with page.expect_download() as dl:
                page.locator("#r1bDownloadWav").click()
            dl.value.save_as(out / "routed-reopened.wav")
            assert (out / "routed-reopened.wav").read_bytes() == mixed
            image = "04-reopened-routed-output.png"
            page.screenshot(path=str(out / image), full_page=True)
            images.append(image)
            context.close()
            browser.close()
    finally:
        _stop(server2, thread2)

    assert not (errors or page_errors or failures), (errors, page_errors, failures)
    result = {
        "milestone": "PROD-E2E-R1B-G2B",
        "automated_real_chromium_controls": True,
        "two_distinct_accepted_source_wavs_seeded_by_g1": True,
        "two_bus_plus_master_manual_preview_and_accept": True,
        "route_preview_mutated_head": False,
        "bus_gain_preview_mutated_head": False,
        "accepted_bus_gain_db": -6.0,
        "channels": channels, "sample_rate_hz": rate, "frames": frames,
        "original_wav_sha256": hashlib.sha256(baseline).hexdigest(),
        "routed_wav_sha256": hashlib.sha256(mixed).hexdigest(),
        "routed_changed_pcm": True,
        "second_bus_preserved_right_pcm": True,
        "restart_reopen_exact_wav": True,
        "screenshots": images,
        "console_error_count": len(errors), "page_error_count": len(page_errors),
        "network_error_count": len(failures),
        "automation_lane_accepted": False,
        "real_plugin_binary_proven": False, "physical_device_proven": False,
        "commercial_song_readiness": False,
    }
    write_canonical_json(out / "proof.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_suite(args.out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
