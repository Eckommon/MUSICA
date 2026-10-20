"""Real Chromium G2C source-bound gain automation after verified two-bus project."""
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
from .prod_e2e_r1a_browser import _server, _stop, _record_request_failure
from .prod_e2e_r1b_g2b_browser import run_suite as seed_g2b


def _pcm(path: Path, *, expected_rate_hz: int = 8000):
    data = path.read_bytes()
    with wave.open(io.BytesIO(data), "rb") as wav:
        assert wav.getnchannels() == 2 and wav.getsampwidth() == 2 and wav.getframerate() == expected_rate_hz
        frames = wav.getnframes()
        samples = struct.unpack("<" + "h" * (frames * 2), wav.readframes(frames))
    return data, frames, samples


def run_suite(destination: str | Path, *, sample_rate_hz: int = 8000) -> dict:
    from playwright.sync_api import sync_playwright, expect
    out = Path(destination)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    await_audio_timeout_ms = 90000 if sample_rate_hz >= 44100 else 35000
    seed_g2b(out / "seed-g2b", sample_rate_hz=sample_rate_hz)
    workspace = out / "seed-g2b" / "seed-g1" / "workspace"
    baseline, baseline_frames, baseline_pcm = _pcm(out / "seed-g2b" / "routed-accepted.wav", expected_rate_hz=sample_rate_hz)
    errors, page_errors, failed_requests, screenshots = [], [], [], []
    service, server, thread, url = _server(workspace)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1600, "height": 1200}, accept_downloads=True)
            context.set_default_timeout(35000)
            page = context.new_page()
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            page.on("requestfailed", lambda req: _record_request_failure(req, failed_requests))
            page.goto(url + "/", wait_until="domcontentloaded")
            page.locator("#openProjectSlug").fill("r1b-g1-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            session = next(iter(service._sessions.values()))
            before = session.project.head_revision_id()
            # Opening a standard-rate routed project may schedule several
            # expensive accepted WAV projections. Wait for exact view lineage
            # before asserting the user can click the first native lane.
            try:
                page.wait_for_function("""() => {
                  const a = window.MUSICA_AUTOMATION?.state;
                  const r = window.MUSICA_ROUTING?.state;
                  const n = window.MUSICA_NATIVE_AUDIO?.state;
                  if (!a?.view || !r?.view || !n?.view ||
                      a.sessionId !== r.sessionId || a.sessionId !== n.sessionId)
                    return false;
                  const head = a.view.revision_id;
                  return head === r.view.revision_id && head === n.view.revision_id &&
                    !a.view.preview && !r.view.preview && !n.view.preview &&
                    r.view.nodes?.length > 0 &&
                    r.view.track_outputs?.some(o => o.track_id === "AT-UI-001") &&
                    n.view.tracks?.some(t => t.track_id === "AT-UI-001" && t.clips?.length);
                }""", timeout=await_audio_timeout_ms)
                expect(page.locator("#m7PreviewNativeLane")).to_be_enabled(timeout=await_audio_timeout_ms)
            except Exception:
                snapshot = page.evaluate("""() => {
                  const a=window.MUSICA_AUTOMATION?.state;
                  const r=window.MUSICA_ROUTING?.state;
                  const n=window.MUSICA_NATIVE_AUDIO?.state;
                  return {
                    a_session:a?.sessionId, r_session:r?.sessionId, n_session:n?.sessionId,
                    a_revision:a?.view?.revision_id, r_revision:r?.view?.revision_id,
                    n_revision:n?.view?.revision_id,
                    a_preview:!!a?.view?.preview, r_preview:!!r?.view?.preview,
                    n_preview:!!n?.view?.preview,
                    node_count:r?.view?.nodes?.length,
                    track_outputs:r?.view?.track_outputs?.length,
                    clip_count:n?.view?.tracks?.reduce((x,t)=>x+(t.clips?.length||0),0),
                    lane_button_disabled:document.querySelector("#m7PreviewNativeLane")?.disabled,
                    status:document.querySelector("#m7AutomationStatus")?.textContent,
                  };
                }""")
                (out / "pre-lane-readiness-failure.json").write_text(
                    json.dumps(snapshot, sort_keys=True, indent=2), encoding="utf-8"
                )
                page.screenshot(path=str(out / "pre-lane-readiness-failure.png"), full_page=True)
                raise
            page.locator("#m7NewNativeLaneTrack").select_option("AT-UI-001")
            page.locator("#m7NewNativeLaneStart").fill("-3")
            page.locator("#m7NewNativeLaneEnd").fill("-12")
            page.locator("#m7PreviewNativeLane").click()
            expect(page.locator("#m7AutomationAvailability")).to_have_text("PREVIEW · NOT ACCEPTED", timeout=await_audio_timeout_ms)
            assert session.project.head_revision_id() == before, "Automation Preview advanced HEAD"
            expect(page.locator("#r1bDownloadWav")).to_be_disabled()
            image = "01-native-gain-lane-preview.png"
            page.screenshot(path=str(out / image), full_page=True)
            screenshots.append(image)
            page.locator("#acceptButton").click()
            page.wait_for_function("""() => {
              const a = window.MUSICA_AUTOMATION?.state?.view;
              const n = window.MUSICA_NATIVE_AUDIO?.state?.view;
              return a && n && !a.preview && !n.preview &&
                a.revision_id === n.revision_id &&
                a.lanes?.some(l => l.lane_id === "AUTO-UI-001");
            }""", timeout=await_audio_timeout_ms)
            assert session.project.head_revision_id() != before
            accepted = page.evaluate("() => window.MUSICA_AUTOMATION.state.view")
            lanes = [x for x in accepted["lanes"] if x["lane_id"] == "AUTO-UI-001"]
            assert len(lanes) == 1 and len(lanes[0]["points"]) == 2
            expect(page.locator("#r1bDownloadWav")).to_be_enabled()
            with page.expect_download() as download:
                page.locator("#r1bDownloadWav").click()
            download.value.save_as(out / "gain-automated.wav")
            mixed, frames, pcm = _pcm(out / "gain-automated.wav", expected_rate_hz=sample_rate_hz)
            assert frames == baseline_frames
            assert mixed != baseline, "Accepted lane did not change rendered audio bytes"
            assert any(pcm[i] != baseline_pcm[i] for i in range(0, 32000, 2)), "No left track gain effect"
            assert all(pcm[i] == baseline_pcm[i] for i in range(1, len(pcm), 2)), "Second track changed unexpectedly"
            image = "02-accepted-gain-lane.png"
            page.screenshot(path=str(out / image), full_page=True)
            screenshots.append(image)
            page.locator("#exportButton").click()
            expect(page.locator("#exportResult")).to_contain_text(".musica")
            accepted_head = session.project.head_revision_id()
            context.close()
            browser.close()
    finally:
        _stop(server, thread)
    service2, server2, thread2, url2 = _server(workspace)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            page.goto(url2 + "/", wait_until="domcontentloaded")
            page.locator("#openProjectSlug").fill("r1b-g1-two-track")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            page.wait_for_function("""() => {
              const a = window.MUSICA_AUTOMATION?.state?.view;
              return a && a.lanes?.some(l => l.lane_id === "AUTO-UI-001");
            }""")
            assert next(iter(service2._sessions.values())).project.head_revision_id() == accepted_head
            with page.expect_download() as download:
                page.locator("#r1bDownloadWav").click()
            download.value.save_as(out / "gain-reopened.wav")
            assert (out / "gain-reopened.wav").read_bytes() == mixed
            image = "03-reopened-gain-lane.png"
            page.screenshot(path=str(out / image), full_page=True)
            screenshots.append(image)
            context.close()
            browser.close()
    finally:
        _stop(server2, thread2)
    assert not errors and not page_errors and not failed_requests, (errors, page_errors, failed_requests)
    proof = {
        "milestone": "PROD-E2E-R1B-G2C",
        "real_chromium_automated_user_operation": True,
        "two_source_routed_bus_seed": True,
        "sample_rate_hz": sample_rate_hz,
        "new_native_gain_lane_preview_mutated_head": False,
        "explicit_accept": True,
        "source_track": "AT-UI-001",
        "start_gain_db": -3, "end_gain_db": -12,
        "rendered_sound_changed": True,
        "second_source_pcm_exact": True,
        "accepted_wav_sha256": hashlib.sha256(mixed).hexdigest(),
        "reopen_wav_byte_exact": True,
        "screenshots": screenshots,
        "human_usability_study": False,
        "actual_hardware": False,
        "real_third_party_plugin": False,
        "commercial_release_ready": False,
    }
    write_canonical_json(out / "proof.json", proof)
    return proof


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    arguments = parser.parse_args()
    run_suite(arguments.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
