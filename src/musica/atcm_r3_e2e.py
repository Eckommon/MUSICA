"""ATCM-R3 real-Chromium native-audio arrangement/mixer lifecycle evidence."""

from __future__ import annotations

import argparse
import io
import json
import shutil
import threading
import wave
from pathlib import Path
from typing import Any

from .audio_assets import import_audio_asset
from .audio_edit import (
    accept_audio_edit_preview,
    audio_material_sha256,
    blueprint_sha256,
    build_audio_edit_preview,
)
from .creative import compose_blueprint
from .evidence import write_canonical_json
from .project import create_project
from .studio import StudioService
from .studio_http_r3 import create_local_server

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def _wav_bytes() -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(8000)
        payload = bytearray()
        for index in range(800):
            value = 14000 if index % 4 < 2 else -14000
            payload.extend(int(value).to_bytes(2, "little", signed=True))
        writer.writeframes(bytes(payload))
    return stream.getvalue()


def _source(parent: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
    }


def _candidate(parent: dict[str, Any], candidate_id: str, operations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_audio_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "atcm-r3-e2e"},
        "reason": f"ATCM-R3 E2E {candidate_id}",
        "operations": operations,
        "preview_only": True,
    }


def _prepare_project(workspace: Path) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    root = compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))
    root["project"]["project_id"] = "PRJ-ATCM-R3-E2E"
    root["project"]["revision_id"] = "rev-atcm-r3-root"
    project = create_project(workspace / "native.musica", root)
    source_path = workspace / "r3-source.wav"
    source_path.write_bytes(_wav_bytes())
    asset = import_audio_asset(project, source_path)
    setup = _candidate(root, "R3-E2E-SETUP", [
        {"operation_id":"R3-E2E-SETUP-T","op":"ADD_TRACK","track_id":"AT-R3-E2E","order":0,"name":"Browser Native"},
        {"operation_id":"R3-E2E-SETUP-C","op":"ADD_CLIP","target":{"track_id":"AT-R3-E2E"},"clip":{"clip_id":"AC-R3-E2E","asset_id":asset["asset_id"],"timeline_start_seconds":0.0,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
    ])
    preview = build_audio_edit_preview(project, root, setup)
    if not preview.ready:
        raise RuntimeError("R3 E2E setup arrangement was blocked")
    record = accept_audio_edit_preview(project, preview)
    return project, project.read_revision(record["revision_id"]), asset


def _start(workspace: Path):
    service = StudioService(workspace)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval":0.01}, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    return service, server, thread, f"http://{host}:{port}"


def _stop(server, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    if thread.is_alive():
        raise RuntimeError("R3 Studio server thread did not stop")


def _browser_state(page) -> dict[str, Any]:
    value = page.evaluate(
        """() => window.MUSICA_NATIVE_AUDIO ? {
          view: JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.view)),
          lastSubmittedCandidate: window.MUSICA_NATIVE_AUDIO.state.lastSubmittedCandidate ? JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.lastSubmittedCandidate)) : null,
          lastAuthorityResult: window.MUSICA_NATIVE_AUDIO.state.lastAuthorityResult ? JSON.parse(JSON.stringify(window.MUSICA_NATIVE_AUDIO.state.lastAuthorityResult)) : null
        } : null"""
    )
    if not isinstance(value, dict):
        raise RuntimeError("R3 Browser native-audio state is unavailable")
    return value


def _open(page, base_url: str, expect) -> dict[str, Any]:
    page.goto(base_url + "/", wait_until="domcontentloaded")
    expect(page.locator("#connectionBadge")).to_contain_text("READY")
    page.locator("#openProjectSlug").fill("native")
    page.locator("#openForm button[type=submit]").click()
    expect(page.locator("#activeProject")).to_be_visible()
    page.locator('button[data-tab="inspect"]').click()
    expect(page.locator("#r3AudioCard")).to_be_visible()
    expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("ACCEPTED")
    expect(page.locator('#r3TrackList [data-track-id="AT-R3-E2E"]')).to_be_visible()
    page.wait_for_function("() => window.MUSICA_NATIVE_AUDIO && window.MUSICA_NATIVE_AUDIO.state.view")
    return _browser_state(page)


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("ATCM-R3 requires .[dev,e2e] and Playwright Chromium") from exc

    out = Path(out_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    workspace = out / "workspace"
    workspace.mkdir()
    project, accepted, asset = _prepare_project(workspace)
    source_head = str(accepted["project"]["revision_id"])

    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []
    screenshots: list[str] = []

    service1, server1, thread1, base1 = _start(workspace)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width":1500,"height":1300}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        page = context.new_page()
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("requestfailed", lambda request: request_failures.append(f"{request.method} {request.url}"))
        try:
            initial = _open(page, base1, expect)
            accepted_mix = initial["view"]["accepted_audition"]
            if not accepted_mix["available"]:
                raise RuntimeError("R3 accepted native mix is not auditionable")
            shot = out / "01-accepted-native-audio.png"
            page.screenshot(path=str(shot), full_page=True)
            screenshots.append(shot.name)

            # Arrangement Preview: move the exact accepted clip, prove HEAD unchanged, then discard.
            clip = page.locator('[data-clip-id="AC-R3-E2E"]')
            clip.locator('[data-field="timeline"]').fill("0.2")
            clip.locator('[data-action="preview-clip"]').click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            page.wait_for_function("() => window.MUSICA_NATIVE_AUDIO.state.view.preview !== null")
            arrangement_preview = _browser_state(page)
            if service1._get_session(next(iter(service1._sessions))).project.head_revision_id() != source_head:
                raise RuntimeError("R3 arrangement Preview advanced accepted HEAD")
            if arrangement_preview["lastAuthorityResult"]["status"] != "READY_FOR_PREVIEW":
                raise RuntimeError("R3 arrangement Preview did not pass trusted authority")
            preview_wav = arrangement_preview["view"]["preview"]["audition"]["wav_sha256"]
            if preview_wav == accepted_mix["wav_sha256"]:
                raise RuntimeError("Controlled arrangement Preview did not change derived WAV")
            shot = out / "02-arrangement-preview.png"
            page.screenshot(path=str(shot), full_page=True)
            screenshots.append(shot.name)
            page.locator("#r3Discard").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("ACCEPTED")
            if service1._get_session(next(iter(service1._sessions))).project.head_revision_id() != source_head:
                raise RuntimeError("R3 discard changed accepted HEAD")

            # Mixer Preview then trusted explicit native-audio Accept.
            track = page.locator('[data-track-id="AT-R3-E2E"]')
            track.locator('[data-field="track-gain"]').fill("-6")
            track.locator('[data-field="track-pan"]').fill("0.5")
            track.locator('[data-action="preview-mixer"]').click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            page.wait_for_function("() => window.MUSICA_NATIVE_AUDIO.state.view.preview && window.MUSICA_NATIVE_AUDIO.state.view.preview.candidate_kind === 'mixer'")
            mixer_preview = _browser_state(page)
            if service1._get_session(next(iter(service1._sessions))).project.head_revision_id() != source_head:
                raise RuntimeError("R3 mixer Preview advanced accepted HEAD")
            page.locator("#r3Accept").click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("ACCEPTED")
            page.wait_for_function("() => window.MUSICA_NATIVE_AUDIO.state.view && window.MUSICA_NATIVE_AUDIO.state.view.preview === null")
            accepted_after = _browser_state(page)
            new_head = str(accepted_after["view"]["revision_id"])
            if new_head == source_head:
                raise RuntimeError("R3 explicit native-audio Accept did not advance exactly one revision")
            shot = out / "03-mixer-accepted.png"
            page.screenshot(path=str(shot), full_page=True)
            screenshots.append(shot.name)
        finally:
            context.close()
            browser.close()
    _stop(server1, thread1)

    # Restart/reopen with a fresh service and Browser process.
    service2, server2, thread2, base2 = _start(workspace)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width":1500,"height":1300}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        page = context.new_page()
        try:
            reopened = _open(page, base2, expect)
            track_state = reopened["view"]["tracks"][0]["mixer"]
            if track_state != {"gain_db":-6.0,"pan":0.5,"mute":False,"solo":False}:
                raise RuntimeError(f"R3 reopen did not preserve accepted mixer state: {track_state}")
            reopened_head = str(reopened["view"]["revision_id"])

            # Install a Browser Preview, then advance HEAD independently and prove stale Accept rejection.
            track = page.locator('[data-track-id="AT-R3-E2E"]')
            track.locator('[data-field="track-gain"]').fill("-3")
            track.locator('[data-action="preview-mixer"]').click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            session_id = next(iter(service2._sessions))
            session = service2._get_session(session_id)
            current = session.project.read_revision(reopened_head)
            concurrent = _candidate(current, "R3-E2E-CONCURRENT", [
                {"operation_id":"R3-E2E-CONCURRENT-GAIN","op":"SET_CLIP_GAIN","target":{"track_id":"AT-R3-E2E","clip_id":"AC-R3-E2E"},"gain_db":-1.0}
            ])
            resolved = build_audio_edit_preview(session.project, current, concurrent)
            if not resolved.ready:
                raise RuntimeError("R3 concurrent stale-source fixture was blocked")
            concurrent_record = accept_audio_edit_preview(session.project, resolved)
            concurrent_head = str(concurrent_record["revision_id"])
            page.locator("#r3Accept").click()
            expect(page.locator("#r3AudioStatus")).to_contain_text("stale")
            if session.project.head_revision_id() != concurrent_head:
                raise RuntimeError("Rejected stale Browser Preview changed concurrent accepted HEAD")
            shot = out / "04-stale-preview-rejected.png"
            page.screenshot(path=str(shot), full_page=True)
            screenshots.append(shot.name)
        finally:
            context.close()
            browser.close()
    _stop(server2, thread2)

    proof = {
        "evidence_version":"0",
        "milestone":"ATCM-R3",
        "project_id":"PRJ-ATCM-R3-E2E",
        "asset_id":asset["asset_id"],
        "source_head":source_head,
        "accepted_head_after_mixer":new_head,
        "reopened_head":reopened_head,
        "concurrent_head_after_stale_fixture":concurrent_head,
        "arrangement_preview_head_unchanged":True,
        "discard_head_unchanged":True,
        "mixer_preview_head_unchanged":True,
        "explicit_audio_accept_advanced_once":True,
        "reopen_preserved_mixer_state":True,
        "stale_preview_accept_rejected":True,
        "accepted_mix_plan_sha256":accepted_mix["mix_plan_sha256"],
        "accepted_wav_sha256":accepted_mix["wav_sha256"],
        "arrangement_preview_wav_sha256":preview_wav,
        "mixer_preview_plan_sha256":mixer_preview["view"]["preview"]["audition"]["mix_plan_sha256"],
        "final_accepted_wav_sha256":accepted_after["view"]["accepted_audition"]["wav_sha256"],
        "rendered_audio_is_canonical":False,
        "browser_state_is_canonical":False,
        "recording_claimed":False,
        "realtime_device_engine_claimed":False,
        "plugin_hosting_claimed":False,
        "screenshots":screenshots,
        "console_error_count":len(console_errors),
        "page_error_count":len(page_errors),
        "request_failure_count":len(request_failures),
    }
    if console_errors or page_errors or request_failures:
        raise RuntimeError(
            f"R3 Browser errors: console={console_errors}, page={page_errors}, requests={request_failures}"
        )
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
