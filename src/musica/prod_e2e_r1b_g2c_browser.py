"""G2C real Chromium first-user-created native gain automation lane evidence.

A full G2B Browser project is produced through separate trusted Previews
and Accepts first. This suite never injects accepted creative state.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import shutil
import struct
import wave
from pathlib import Path

from .evidence import write_canonical_json
from .prod_e2e_r1a_browser import _server, _stop, _record_request_failure
from .prod_e2e_r1b_g2b_browser import run_suite as seed_g2b


def pcm(wav: bytes) -> tuple[int, int, int, tuple[int, ...]]:
    with wave.open(io.BytesIO(wav), "rb") as reader:
        channel, width, rate, count = (
            reader.getnchannels(), reader.getsampwidth(),
            reader.getframerate(), reader.getnframes(),
        )
        samples = reader.readframes(count)
    assert (channel, width, rate, count) == (2, 2, 8000, 96000)
    return channel, rate, count, struct.unpack("<" + "h" * (len(samples) // 2), samples)


def run_suite(destination: str | Path) -> dict:
    from playwright.sync_api import expect, sync_playwright
    out = Path(destination)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    seed_g2b(out / "seed-g2b")
    ws = out / "seed-g2b" / "seed-g1" / "workspace"
    base_wav = (out / "seed-g2b" / "routed-accepted.wav").read_bytes()
    channels, rate, frames, before_pcm = pcm(base_wav)
    console, page_errors, network = [], [], []
    shots = []
    service, server, thread, url = _server(ws)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1200}, accept_downloads=True)
            context.set_default_timeout(35_000)
            page = context.new_page()
            page.on("console", lambda msg: console.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))
            page.on("requestfailed", lambda req: _record_request_failure(req, network))
            page.goto(url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill("r1b-g1-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#m7AutomationCard")).to_be_visible()
            expect(page.locator("#m7AutomationAvailability")).to_have_text("NO CANONICAL AUTOMATION")
            # Eligibility requires accepted native audio and G2B routing GETs
            # to converge at one exact persisted accepted revision.
            expect(page.locator("#m7PreviewFirstGainLane")).to_be_enabled(timeout=35_000)
            expect(page.locator("#m7FirstGainTrack option")).to_have_count(2)
            page.locator("#m7FirstGainTrack").select_option("AT-UI-001")
            page.locator("#m7FirstGainStart").fill("-3")
            page.locator("#m7FirstGainEndBeat").fill("1")
            page.locator("#m7FirstGainEnd").fill("-9")
            before_head = next(iter(service._sessions.values())).project.head_revision_id()
            page.locator("#m7PreviewFirstGainLane").click()
            expect(page.locator("#m7AutomationAvailability")).to_have_text("PREVIEW FIRST LANE · NOT ACCEPTED")
            expect(page.locator("#m7AutomationStatus")).to_contain_text("Preview ready")
            session = next(iter(service._sessions.values()))
            assert session.project.head_revision_id() == before_head
            assert session.pending is not None
            expect(page.locator("#r1bDownloadWav")).to_be_disabled()
            assert session.pending.detail["automation_edit"]["native_target_lane_ids"] == ["AUTO-UI-GAIN-AT-UI-001"]
            image = "01-automation-preview-not-accepted.png"
            page.screenshot(path=str(out / image), full_page=True)
            shots.append(image)

            page.locator("#acceptButton").click()
            expect(page.locator("#m7AutomationAvailability")).to_have_text("AUTOMATION · READY")
            expect(page.locator("#m7AutomationLanes")).to_be_visible()
            accepted_head = session.project.head_revision_id()
            assert accepted_head != before_head
            assert session.pending is None
            page.wait_for_function("""() => {
              const a = window.MUSICA_NATIVE_AUDIO?.state?.view;
              const r = window.MUSICA_ROUTING?.state?.view;
              const e = window.MUSICA_AUTOMATION?.state?.view;
              return a && r && e && !a.preview && !r.preview && !e.preview &&
                a.revision_id === r.revision_id && a.revision_id === e.revision_id &&
                e.lanes.length === 1 && a.accepted_audition?.available;
            }""", timeout=35_000)
            expect(page.locator("#r1bDownloadWav")).to_be_enabled()
            with page.expect_download() as result:
                page.locator("#r1bDownloadWav").click()
            result.value.save_as(out / "automated-accepted.wav")
            wav = (out / "automated-accepted.wav").read_bytes()
            _, _, _, after_pcm = pcm(wav)
            assert wav != base_wav
            assert all(after_pcm[i] == before_pcm[i] for i in range(1, len(after_pcm), 2)), (
                "unchanged right source/channel must remain sample-exact"
            )
            # Native lane fades gain for the first two seconds of nonzero
            # source audio. Compare independent input-to-output attenuation
            # early vs late to demonstrate actual audible time dependence.
            early_index, late_index = 1600, 9600
            old_early, new_early = abs(before_pcm[2 * early_index]), abs(after_pcm[2 * early_index])
            old_late, new_late = abs(before_pcm[2 * late_index]), abs(after_pcm[2 * late_index])
            assert min(old_early, old_late) > 0
            early_ratio, late_ratio = new_early / old_early, new_late / old_late
            assert 0 < late_ratio < early_ratio < 1, (early_ratio, late_ratio)
            assert max(map(abs, after_pcm)) < 32767
            image = "02-accepted-automation-audio.png"
            page.screenshot(path=str(out / image), full_page=True)
            shots.append(image)
            page.locator("#exportButton").click()
            expect(page.locator("#exportResult")).to_contain_text(".musica")
            context.close()
            browser.close()
    finally:
        _stop(server, thread)

    reopened, server2, thread2, url2 = _server(ws)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1200}, accept_downloads=True)
            page = context.new_page()
            page.goto(url2 + "/", wait_until="domcontentloaded")
            page.locator("#openProjectSlug").fill("r1b-g1-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#m7AutomationAvailability")).to_have_text("AUTOMATION · READY")
            assert next(iter(reopened._sessions.values())).project.head_revision_id() == accepted_head
            with page.expect_download() as result:
                page.locator("#r1bDownloadWav").click()
            result.value.save_as(out / "automated-reopened.wav")
            assert (out / "automated-reopened.wav").read_bytes() == wav
            image = "03-reopened-automation-audio.png"
            page.screenshot(path=str(out / image), full_page=True)
            shots.append(image)
            context.close()
            browser.close()
    finally:
        _stop(server2, thread2)

    assert not (console or page_errors or network), (console, page_errors, network)
    proof = {
        "milestone": "PROD-E2E-R1B-G2C",
        "real_chromium_ui_automated": True,
        "user_clicked_first_gain_lane_preview": True,
        "preview_mutated_head": False,
        "separate_explicit_accept": True,
        "accepted_lane_id": "AUTO-UI-GAIN-AT-UI-001",
        "accepted_audio_sha256": hashlib.sha256(wav).hexdigest(),
        "baseline_routed_wav_sha256": hashlib.sha256(base_wav).hexdigest(),
        "sample_rate_hz": rate, "channels": channels, "frames": frames,
        "time_varying_gain_ratio_early": early_ratio,
        "time_varying_gain_ratio_late": late_ratio,
        "right_pcm_exact_unchanged": True,
        "reopened_exact_wav": True,
        "console_errors": len(console), "page_errors": len(page_errors),
        "network_errors": len(network), "screenshots": shots,
        "physical_device_proven": False,
        "real_plugin_binary_proven": False,
        "commercial_song_readiness": False,
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
