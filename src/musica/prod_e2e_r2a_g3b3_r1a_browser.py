"""G3B3-R1A: actual Browser 180s mixer Preview A/B, Discard, explicit Accept.

Reuse R0's TWO real user-picked 180s WAVs imported and accepted by first-party
Chromium UI. Test a true pending mix *inside that same persisted user project*.
Do not claim routed automation, archive roundtrip, or human listening.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import wave

from .prod_e2e_r1a_browser import _server, _stop
from .prod_e2e_r2a_g3b3_r0_browser import FRAMES, RATE, EXPECTED_BYTES, run_suite


def _hash(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def _frame(path: Path, index: int) -> tuple[int, int]:
    with wave.open(str(path), "rb") as wav:
        assert (wav.getframerate(), wav.getnchannels(), wav.getsampwidth(),
                wav.getnframes()) == (RATE, 2, 2, FRAMES)
        wav.setpos(index)
        return struct.unpack("<hh", wav.readframes(1))


def _preview_range(
    base: str, session_id: str, preview_id: str, frame: int
) -> tuple[tuple[int, int], str]:
    begin = 44 + 4 * frame
    endpoint = (
        f"{base}/v0/sessions/{session_id}/audio/stream/preview.wav"
        f"?preview_id={preview_id}"
    )
    request = Request(endpoint, headers={"Range": f"bytes={begin}-{begin+3}"})
    with urlopen(request, timeout=240) as response:
        assert response.status == 206
        assert response.headers["Content-Range"] == (
            f"bytes {begin}-{begin+3}/{EXPECTED_BYTES}"
        )
        sample = struct.unpack("<hh", response.read())
        tag = response.headers["ETag"].strip('"')
        assert len(tag) == 64
        return sample, tag


def run_suite_r1a(destination: str | Path) -> dict:
    from playwright.sync_api import expect, sync_playwright

    out = Path(destination).resolve()
    out.mkdir(parents=True, exist_ok=True)
    seed = out / "seed-r0"
    base = run_suite(seed)
    assert base["explicit_track_clip_accept_actions"] == 4
    original_sha = base["derived_wav_sha256"]
    assert original_sha == _hash(seed / "browser-reopened-180s.wav")
    project_slug = "g3b3-user-two-180s"
    workspace = seed / "workspace"
    events = []
    errors = []
    accepted_revision = None
    accepted_after_edit_sha = None

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
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda msg: errors.append(msg.text)
                    if msg.type == "error" else None)
            page.goto(url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill(project_slug)
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioWorkspace")).to_be_visible()
            expect(page.locator("#r3TrackList .r3-track")).to_have_count(2)

            session_id = page.evaluate(
                "() => window.MUSICA_NATIVE_AUDIO.state.sessionId"
            )
            project = studio._get_session(session_id).project
            parent = project.head_revision_id()
            first = page.locator('article.r3-track[data-track-id="AT-UI-001"]')
            expect(first).to_be_visible()

            def preview_gain(db: str) -> str:
                first.locator('[data-field="track-gain"]').fill(db)
                first.locator('[data-action="preview-mixer"]').click()
                expect(page.locator("#r3AudioAuthorityBadge")).to_have_text(
                    "PREVIEW · NOT ACCEPTED", timeout=120000
                )
                assert project.head_revision_id() == parent
                preview = page.evaluate(
                    "() => window.MUSICA_NATIVE_AUDIO.state.view.preview"
                )
                assert preview and preview["preview_id"]
                preview_id = preview["preview_id"]
                player = page.locator("#r3AudioPlayer")
                expect(player).to_be_visible()
                assert (
                    "/audio/stream/preview.wav?preview_id=" + preview_id
                ) in player.get_attribute("src")
                page.wait_for_function("""() => {
                    const audio = document.getElementById("r3AudioPlayer");
                    return audio && audio.readyState >= 1 &&
                        Number.isFinite(audio.duration) &&
                        Math.abs(audio.duration - 180) < 0.02;
                }""", timeout=240000)
                assert project.head_revision_id() == parent
                events.append({
                    "action": "mixer Preview · NOT ACCEPTED",
                    "gain_db": db,
                    "preview_id": preview_id,
                    "head_unchanged": True,
                })
                return preview_id

            # A real 180s rejected candidate changes the sound but must never
            # change the accepted project. The old URL is invalidated by Discard.
            discarded = preview_gain("-3")
            rejected_sample, rejected_sha = _preview_range(
                url, session_id, discarded, 0
            )
            assert rejected_sample != (3200, -1400)
            assert rejected_sha != original_sha
            page.screenshot(path=str(out / "01-180s-pending-discard.png"),
                            full_page=True)
            page.locator("#r3Discard").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text(
                "ACCEPTED"
            )
            assert project.head_revision_id() == parent
            try:
                _preview_range(url, session_id, discarded, 0)
            except HTTPError as error:
                assert error.code == 404, f"old discarded preview HTTP {error.code}"
            else:
                raise AssertionError("Discarded Preview URL still returned sound")
            events.append({"action": "Discard", "head_unchanged": True})

            # Explicitly edit an actual native track. Compare numeric PCM at
            # three song positions. SHA must equal the accepted WAV only AFTER
            # the first-party Browser's explicit Accept event.
            accepted_candidate = preview_gain("-6")
            preview_sha = None
            for position in (0, FRAMES // 2, FRAMES - 1):
                sample, sha = _preview_range(
                    url, session_id, accepted_candidate, position
                )
                assert sample == (2202, -901), (position, sample)
                if preview_sha is None:
                    preview_sha = sha
                assert sha == preview_sha
            assert preview_sha != original_sha
            assert project.head_revision_id() == parent
            page.screenshot(path=str(out / "02-pending-180s-mixer-before-accept.png"),
                            full_page=True)
            page.locator("#r3Accept").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text(
                "ACCEPTED", timeout=120000
            )
            accepted_revision = project.head_revision_id()
            assert accepted_revision != parent
            events.append({
                "action": "Explicit Accept edited 180s native mixer",
                "accepted_revision": accepted_revision,
                "preview_wav_sha256": preview_sha,
            })
            expect(page.locator("#r3StreamedAcceptedWavDownload")).to_be_visible()
            with page.expect_download(timeout=240000) as event:
                page.locator("#r3StreamedAcceptedWavDownload").click()
            accepted = out / "browser-mixer-accepted-180s.wav"
            event.value.save_as(accepted)
            assert accepted.stat().st_size == EXPECTED_BYTES
            accepted_after_edit_sha = _hash(accepted)
            assert accepted_after_edit_sha == preview_sha
            assert accepted_after_edit_sha != original_sha
            for frame in (0, FRAMES // 2, FRAMES - 1):
                assert _frame(accepted, frame) == (2202, -901)
            assert project.head_revision_id() == accepted_revision
            page.screenshot(path=str(out / "03-accepted-180s-mixer.png"),
                            full_page=True)
            context.close()
            browser.close()
    finally:
        _stop(server, thread)

    # Restart the real first-party Studio and download the accepted edited
    # WAV again: identical SHA and no silent derived creative changes.
    studio2, server2, thread2, reopened_url = _server(workspace)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1600, "height": 1200}, accept_downloads=True
            )
            context.set_default_timeout(180000)
            page = context.new_page()
            page.goto(reopened_url + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill(project_slug)
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#r3AudioWorkspace")).to_be_visible()
            reopened_project = next(iter(studio2._sessions.values())).project
            assert reopened_project.head_revision_id() == accepted_revision
            with page.expect_download(timeout=240000) as event:
                page.locator("#r3StreamedAcceptedWavDownload").click()
            reopened = out / "browser-mixer-reopened-180s.wav"
            event.value.save_as(reopened)
            assert _hash(reopened) == accepted_after_edit_sha
            for frame in (0, FRAMES // 2, FRAMES - 1):
                assert _frame(reopened, frame) == (2202, -901)
            assert reopened_project.head_revision_id() == accepted_revision
            page.screenshot(path=str(out / "04-edited-180s-reopened.png"),
                            full_page=True)
            context.close()
            browser.close()
    finally:
        _stop(server2, thread2)

    assert not errors, errors
    proof = {
        "milestone": "PROD-E2E-R2A-G3B3-R1A",
        "real_chromium_two_independent_user_selected_180s_wavs": True,
        "original_accepted_wav_sha256": original_sha,
        "pending_mixer_before_accept": True,
        "pending_discard_preserved_parent_revision": True,
        "invalid_discarded_preview_url_denied": True,
        "pending_pcm_at_first_middle_last": [2202, -901],
        "original_accepted_pcm": [3200, -1400],
        "pending_preview_sha256": preview_sha,
        "accepted_wav_sha256": accepted_after_edit_sha,
        "pending_and_explicitly_accepted_sha_equal": (
            preview_sha == accepted_after_edit_sha
        ),
        "reopened_edited_wav_sha256_equal": True,
        "accepted_revision_id": accepted_revision,
        "actions": events,
        "browser_errors": errors,
        "full_routing_automation_verified": False,
        "actual_project_archive_roundtrip_verified": False,
        "human_musical_pilot_or_live_ai_quality_verified": False,
        "actual_audio_device_or_third_party_plugin_verified": False,
    }
    (out / "proof.json").write_text(
        json.dumps(proof, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return proof


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run_suite_r1a(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
