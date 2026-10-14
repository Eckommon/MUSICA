"""PLUG-R3-B real Chromium creator workflow and bounded audio proof."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import struct
from threading import Thread
import wave

from playwright.sync_api import sync_playwright, expect

from musica.bus_host_material import bus_host_material_from_blueprint
from musica.bus_host_runtime import render_accepted_simulated_bus_host
from musica.evidence import canonical_json_bytes
from musica.studio import StudioService
from musica.studio_http import create_local_server

# Reuse the actual accepted audio/routing fixture; the Browser never gets
# direct access to these trusted test-only constructor helpers.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from test_plug_r2b_k2_studio_bus_plugins import _service


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _pcm(payload: bytes) -> list[tuple[int, int]]:
    with wave.open(io.BytesIO(payload)) as reader:
        assert reader.getframerate() == 8000
        assert reader.getnchannels() == 2 and reader.getsampwidth() == 2
        return list(struct.iter_unpack("<hh", reader.readframes(reader.getnframes())))


def test_browser_real_bus_plugin_editor_authority(tmp_path: Path) -> None:
    evidence = Path(os.environ.get("MUSICA_PLUG_R3B_E2E_OUT", str(tmp_path / "evidence")))
    evidence.mkdir(parents=True, exist_ok=True)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    service, _fixture_sid, project, initial = _service(workspace)
    server = create_local_server(service, host="127.0.0.1", port=0)
    worker = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    worker.start()
    base = f"http://127.0.0.1:{server.server_port}"
    console_errors: list[str] = []
    page_errors: list[str] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 1100}, reduced_motion="reduce")
            context.set_default_timeout(45_000)
            page = context.new_page()
            page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda err: page_errors.append(str(err)))
            page.goto(base + "/", wait_until="domcontentloaded")
            expect(page.locator("#connectionBadge")).to_contain_text("READY")
            page.locator("#openProjectSlug").fill("song")
            page.locator("#openForm button[type=submit]").click()
            expect(page.locator("#activeProject")).to_be_visible()
            page.locator('button[data-tab="inspect"]').click()
            expect(page.locator("#plugBrowserBadge")).to_have_text("ACCEPTED")
            expect(page.locator("#plugBrowserBus option")).to_have_count(2)
            assert project.head_revision_id("main") == initial

            page.locator("#plugBrowserBus").select_option("BUS-001")
            page.locator("#plugBrowserLatency").fill("3")
            page.locator("#plugBrowserCreative").fill("0")
            page.locator("#plugBrowserPropose").click()
            expect(page.locator("#plugBrowserPending")).to_be_visible()
            expect(page.locator("#plugBrowserPending")).to_contain_text("PREVIEW ONLY")
            assert project.head_revision_id("main") == initial
            assert page.locator("#plugBrowserPreviewAudio").get_attribute("src")
            page.locator("#plugBrowserAccept").click()
            expect(page.locator("#plugBrowserPending")).to_be_hidden()
            first = project.head_revision_id("main")
            assert first != initial
            assert len(bus_host_material_from_blueprint(project.read_revision(first))["instances"]) == 1

            page.locator("#plugBrowserBus").select_option("BUS-002")
            page.locator("#plugBrowserLatency").fill("9")
            page.locator("#plugBrowserPropose").click()
            expect(page.locator("#plugBrowserPending")).to_be_visible()
            assert project.head_revision_id("main") == first
            page.locator("#plugBrowserAccept").click()
            expect(page.locator("#plugBrowserPending")).to_be_hidden()
            second = project.head_revision_id("main")
            assert second != first
            accepted = project.read_revision(second)
            assert len(bus_host_material_from_blueprint(accepted)["instances"]) == 2
            expected = render_accepted_simulated_bus_host(project, second, sample_rate_hz=8000)
            assert _pcm(expected.wav_bytes)[:9] == [(0, 0)] * 9
            assert _pcm(expected.wav_bytes)[9] == (24576, 24576)

            page.locator("#plugBrowserBus").select_option("BUS-001")
            page.locator("#plugBrowserLatency").fill("3")
            page.locator("#plugBrowserCreative").fill("5")
            page.locator("#plugBrowserBypass").check()
            page.locator("#plugBrowserPropose").click()
            expect(page.locator("#plugBrowserPending")).to_be_visible()
            assert project.head_revision_id("main") == second
            page.locator("#plugBrowserDiscard").click()
            expect(page.locator("#plugBrowserPending")).to_be_hidden()
            assert project.head_revision_id("main") == second

            # Explicitly ACCEPT an independent intentional creative delay while
            # bypassing the simulated algorithmic processing latency. The
            # browser must never silently collapse these two user controls.
            page.locator("#plugBrowserBus").select_option("BUS-001")
            page.locator("#plugBrowserCreative").fill("5")
            page.locator("#plugBrowserBypass").check()
            page.locator("#plugBrowserPropose").click()
            expect(page.locator("#plugBrowserPending")).to_be_visible()
            assert project.head_revision_id("main") == second
            page.locator("#plugBrowserAccept").click()
            expect(page.locator("#plugBrowserPending")).to_be_hidden()
            bypassed = project.head_revision_id("main")
            assert bypassed != second
            accepted_bypass = render_accepted_simulated_bus_host(
                project, bypassed, sample_rate_hz=8000
            )
            assert _pcm(accepted_bypass.wav_bytes)[9] == (8192, 8192)
            assert _pcm(accepted_bypass.wav_bytes)[14] == (24576, 24576)

            # The browser obtains a source from the server; a forged/stale copy
            # never installs a Preview and never advances canonical authority.
            blocked = page.evaluate(
                """async () => {
                  const state = window.MUSICA_BUS_HOST.state;
                  const material = JSON.parse(JSON.stringify(state.editor.accepted_material));
                  const candidate = {
                    candidate_version: "0", candidate_id: "BROWSER-FORGED",
                    authority_target: "blueprint_bus_plugin_material",
                    source: {...state.editor.source, blueprint_sha256: "f".repeat(64)},
                    proposed_material: {...material, instances: []},
                    actor: {kind:"user",actor_id:"r3b-e2e"},
                    reason:"forged stale test",
                    preview_only:true
                  };
                  const id = state.sessionId;
                  const response = await fetch("/v0/sessions/" + encodeURIComponent(id) +
                    "/preview/bus-plugins", {method:"POST",
                    headers:{"Content-Type":"application/json"},
                    body:JSON.stringify({candidate})});
                  const json = await response.json();
                  return {status:response.status, installed:json.data?.preview_installed,
                    reason:json.data?.reason || json.error?.message};
                }"""
            )
            assert blocked["installed"] is False
            assert project.head_revision_id("main") == bypassed

            page.locator("#plugBrowserBus").select_option("BUS-002")
            page.locator("#plugBrowserRemove").click()
            expect(page.locator("#plugBrowserPending")).to_be_visible()
            page.locator("#plugBrowserAccept").click()
            expect(page.locator("#plugBrowserPending")).to_be_hidden()
            final = project.head_revision_id("main")
            assert final != bypassed
            material = bus_host_material_from_blueprint(project.read_revision(final))
            assert [v["owner_bus_id"] for v in material["instances"]] == ["BUS-001"]

            # UI never endorses native or realtime hosting.
            ui = page.locator("#plugBrowserCard").inner_text()
            assert "not VST3/CLAP/AU or realtime PDC" in ui
            assert not page_errors, page_errors
            assert not console_errors, console_errors
            context.close()
            browser.close()

        restarted = StudioService(workspace)
        reopened = restarted.open_project_session(project_slug="song", session_id="r3b-reopened")
        assert reopened["session"]["head_revision_id"] == final
        _ = restarted._get_session("r3b-reopened").project.read_revision(final)
        proof = {
            "evidence_version": "0",
            "class": "REAL_CHROMIUM_STUDIO_BUS_PROCESSOR_PREVIEW_ACCEPT",
            "real_chromium": True,
            "project_initial_revision_id": initial,
            "accepted_revision_ids": [first, second, bypassed, final],
            "browser_bypass_accept_preserved_creative_delay": True,
            "bypass_frame_9_pcm": [8192, 8192],
            "bypass_frame_14_pcm": [24576, 24576],
            "preview_did_not_advance_head": True,
            "accept_advanced_exactly_once_per_action": True,
            "two_bus_compensated_sample_at_frame_9": [24576, 24576],
            "accepted_offline_wav_sha256": _sha(expected.wav_bytes),
            "discard_did_not_advance_head": True,
            "stale_hash_preview_blocked": True,
            "remove_required_explicit_accept": True,
            "restart_reopen_exact_head": True,
            "browser_page_errors": page_errors,
            "browser_console_errors": console_errors,
            "default_studio_media_overridden": False,
            "native_third_party_plugins_proven": False,
            "realtime_pdc_proven": False,
        }
        (evidence / "proof.json").write_bytes(canonical_json_bytes(proof))
        (evidence / "accepted-two-bus.wav").write_bytes(expected.wav_bytes)
        (evidence / "manifest.json").write_bytes(canonical_json_bytes({
            "version": "0",
            "artifacts": [
                {
                    "path": name,
                    "size_bytes": (evidence / name).stat().st_size,
                    "sha256": _sha((evidence / name).read_bytes()),
                } for name in ["proof.json", "accepted-two-bus.wav"]
            ],
        }))
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=10)
