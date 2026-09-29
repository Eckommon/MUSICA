"""MRAM-R3 real-Chromium routing/native-automation lifecycle evidence."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import threading
import wave
from pathlib import Path
from typing import Any

from .automation_edit import (
    accept_automation_edit_preview,
    automation_material_sha256,
    blueprint_sha256,
    build_automation_edit_preview,
)
from .audio_assets import import_audio_asset
from .audio_edit import accept_audio_edit_preview, audio_material_sha256, build_audio_edit_preview
from .creative import compose_blueprint
from .evidence import artifact_record, write_canonical_json
from .project import create_project
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256
from .routing_edit import accept_routing_edit_preview, build_routing_edit_preview
from .studio import StudioService
from .studio_http import create_local_server
from .studio_routing import StudioRoutingSurface

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "studio-preview-v0.schema.json",
    ROOT / "schemas" / "studio-session-v0.schema.json",
    ROOT / "schemas" / "studio-automation-view-v0.schema.json",
    ROOT / "schemas" / "studio-routing-view-v0.schema.json",
    ROOT / "src" / "musica" / "studio.py",
    ROOT / "src" / "musica" / "studio_audio.py",
    ROOT / "src" / "musica" / "studio_automation.py",
    ROOT / "src" / "musica" / "studio_routing.py",
    ROOT / "src" / "musica" / "studio_http.py",
    ROOT / "src" / "musica" / "routing_edit.py",
    ROOT / "src" / "musica" / "automation_edit.py",
    ROOT / "src" / "musica" / "studio_web" / "routing_editing.js",
    ROOT / "src" / "musica" / "studio_web" / "routing_editing.css",
    ROOT / "src" / "musica" / "studio_web" / "automation_editing.js",
    ROOT / "tests" / "test_mram_r3_studio_routing.py",
    ROOT / "e2e" / "test_mram_r3_browser.py",
    ROOT / ".github" / "workflows" / "mram-r3-browser-routing-reopen-evidence.yml",
]


def _wav_bytes(value: int, *, rate: int = 8000, frames: int = 800) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        payload = bytearray()
        for _ in range(frames):
            payload.extend(int(value).to_bytes(2, "little", signed=True))
        writer.writeframes(bytes(payload))
    return stream.getvalue()


def _audio_source(parent: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
    }


def _routing_source(parent: dict[str, Any]) -> dict[str, Any]:
    routing = routing_material_from_blueprint(parent)
    assert routing is not None
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(routing),
    }


def _automation_source(parent: dict[str, Any]) -> dict[str, Any]:
    routing = routing_material_from_blueprint(parent)
    assert routing is not None
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "automation_material_sha256": automation_material_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(routing),
    }


def _prepare_project(workspace: Path) -> tuple[str, str]:
    root = compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))
    root["project"]["project_id"] = "PRJ-MRAM-R3-BROWSER"
    root["project"]["revision_id"] = "rev-mram-r3-root"
    project = create_project(workspace / "routing.musica", root)

    a = workspace / "a.wav"
    b = workspace / "b.wav"
    a.write_bytes(_wav_bytes(16384))
    b.write_bytes(_wav_bytes(8192))
    aa = import_audio_asset(project, a)
    bb = import_audio_asset(project, b)

    audio_candidate = {
        "candidate_version": "0",
        "candidate_id": "MRAM-R3-AUDIO",
        "authority_target": "blueprint_audio_material",
        "source": _audio_source(root),
        "actor": {"kind": "user", "actor_id": "mram-r3-e2e"},
        "reason": "MRAM-R3 browser audio fixture.",
        "operations": [
            {"operation_id":"A-T1","op":"ADD_TRACK","track_id":"AT-001","order":0,"name":"Primary"},
            {"operation_id":"A-T2","op":"ADD_TRACK","track_id":"AT-002","order":1,"name":"Secondary"},
            {"operation_id":"A-C1","op":"ADD_CLIP","target":{"track_id":"AT-001"},"clip":{"clip_id":"AC-001","asset_id":aa["asset_id"],"timeline_start_seconds":0.0,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
            {"operation_id":"A-C2","op":"ADD_CLIP","target":{"track_id":"AT-002"},"clip":{"clip_id":"AC-002","asset_id":bb["asset_id"],"timeline_start_seconds":0.0,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
        ],
        "preview_only": True,
    }
    audio_preview = build_audio_edit_preview(project, root, audio_candidate)
    if not audio_preview.ready:
        raise RuntimeError("MRAM-R3 audio fixture Preview blocked")
    audio_record = accept_audio_edit_preview(project, audio_preview)
    audio = project.read_revision(audio_record["revision_id"])

    routing_candidate = {
        "candidate_version": "0",
        "candidate_id": "MRAM-R3-ROUTING",
        "authority_target": "blueprint_routing_material",
        "source": _routing_source(audio),
        "actor": {"kind": "user", "actor_id": "mram-r3-e2e"},
        "reason": "MRAM-R3 browser routing fixture.",
        "operations": [
            {"operation_id":"R-N1","op":"ADD_NODE","node":{"node_id":"BUS-001","order":0,"name":"Music Bus","node_type":"group","mixer":{"gain_db":0.0,"pan":0.0,"mute":False},"output_node_id":"MASTER-001"}},
            {"operation_id":"R-N2","op":"ADD_NODE","node":{"node_id":"RETURN-001","order":1,"name":"Return","node_type":"return","mixer":{"gain_db":0.0,"pan":0.0,"mute":False},"output_node_id":"MASTER-001"}},
            {"operation_id":"R-N3","op":"ADD_NODE","node":{"node_id":"MASTER-001","order":2,"name":"Master","node_type":"master","mixer":{"gain_db":0.0,"pan":0.0,"mute":False},"output_node_id":None}},
            {"operation_id":"R-O1","op":"SET_TRACK_OUTPUT","track_id":"AT-001","target_node_id":"BUS-001"},
            {"operation_id":"R-O2","op":"SET_TRACK_OUTPUT","track_id":"AT-002","target_node_id":"MASTER-001"},
            {"operation_id":"R-S1","op":"ADD_SEND","send":{"send_id":"SEND-001","source":{"kind":"track","source_id":"AT-001"},"target_node_id":"RETURN-001","gain_db":-12.0,"tap":"post_fader"}},
        ],
        "preview_only": True,
    }
    routing_preview = build_routing_edit_preview(project, audio, routing_candidate)
    if not routing_preview.ready:
        raise RuntimeError("MRAM-R3 routing fixture Preview blocked")
    routing_record = accept_routing_edit_preview(project, routing_preview)
    routed = project.read_revision(routing_record["revision_id"])

    native_candidate = {
        "candidate_version": "0",
        "candidate_id": "MRAM-R3-NATIVE",
        "authority_target": "blueprint_automation_material",
        "source": _automation_source(routed),
        "actor": {"kind": "user", "actor_id": "mram-r3-e2e"},
        "reason": "MRAM-R3 native automation fixture.",
        "operations": [
            {
                "operation_id": "N-1",
                "op": "ADD_LANE",
                "lane": {
                    "lane_id": "AUTO-AT001-GAIN",
                    "target": {
                        "parameter_id": "mixer.gain_db",
                        "scope": "audio_track",
                        "owner_id": "AT-001",
                        "unit": "decibel",
                        "minimum": -60.0,
                        "maximum": 12.0,
                    },
                    "section_id": None,
                    "points": [
                        {"point_id":"P-R3-1","beat":0.0,"value":-3.0,"interpolation":"linear"},
                        {"point_id":"P-R3-2","beat":1.0,"value":-6.0,"interpolation":"hold"},
                    ],
                },
            },
            {
                "operation_id": "N-2",
                "op": "ADD_LANE",
                "lane": {
                    "lane_id": "AUTO-BUS001-PAN",
                    "target": {
                        "parameter_id": "mixer.pan",
                        "scope": "routing_node",
                        "owner_id": "BUS-001",
                        "unit": "normalized",
                        "minimum": -1.0,
                        "maximum": 1.0,
                    },
                    "section_id": None,
                    "points": [
                        {"point_id":"P-R3-3","beat":0.0,"value":0.25,"interpolation":"hold"},
                        {"point_id":"P-R3-4","beat":1.0,"value":0.25,"interpolation":"linear"},
                    ],
                },
            },
        ],
        "preview_only": True,
    }
    native_preview = build_automation_edit_preview(routed, native_candidate, project=project)
    if not native_preview.ready:
        raise RuntimeError("MRAM-R3 native automation fixture Preview blocked")
    native_record = accept_automation_edit_preview(project, native_preview)
    return str(root["project"]["revision_id"]), str(native_record["revision_id"])


def _start_server(workspace: Path):
    service = StudioService(workspace)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01},
        daemon=True,
    )
    thread.start()
    host, port = server.server_address[:2]
    return service, server, thread, f"http://{host}:{port}"


def _stop_server(server, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    if thread.is_alive():
        raise RuntimeError("MRAM-R3 Studio server did not stop")


def _session(page) -> dict[str, Any]:
    return json.loads(page.locator("#jsonView").text_content() or "{}")


def _routing_state(page) -> dict[str, Any]:
    value = page.evaluate(
        """() => ({
          view: window.MUSICA_ROUTING ? JSON.parse(JSON.stringify(window.MUSICA_ROUTING.state.view)) : null,
          lastSubmittedCandidate: window.MUSICA_ROUTING ? JSON.parse(JSON.stringify(window.MUSICA_ROUTING.state.lastSubmittedCandidate)) : null,
          lastAuthorityResult: window.MUSICA_ROUTING ? JSON.parse(JSON.stringify(window.MUSICA_ROUTING.state.lastAuthorityResult)) : null
        })"""
    )
    if not isinstance(value, dict):
        raise RuntimeError("MRAM-R3 Browser routing state unavailable")
    return value


def _automation_state(page) -> dict[str, Any]:
    value = page.evaluate(
        """() => ({
          view: window.MUSICA_AUTOMATION ? JSON.parse(JSON.stringify(window.MUSICA_AUTOMATION.state.view)) : null,
          lastSubmittedCandidate: window.MUSICA_AUTOMATION ? JSON.parse(JSON.stringify(window.MUSICA_AUTOMATION.state.lastSubmittedCandidate)) : null,
          lastAuthorityResult: window.MUSICA_AUTOMATION ? JSON.parse(JSON.stringify(window.MUSICA_AUTOMATION.state.lastAuthorityResult)) : null
        })"""
    )
    if not isinstance(value, dict):
        raise RuntimeError("MRAM-R3 Browser automation state unavailable")
    return value


def _screenshot(page, path: Path) -> Path:
    page.screenshot(path=str(path), full_page=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"MRAM-R3 screenshot missing: {path}")
    return path


def _attach_observers(
    page,
    console_errors: list[str],
    page_errors: list[str],
    request_failures: list[str],
    expected_media_aborts: list[str],
    expected_teardown_aborts: list[str],
    http_error_responses: list[str],
    teardown_state: dict[str, bool],
) -> None:
    page.on(
        "console",
        lambda message: console_errors.append(message.text)
        if message.type == "error"
        else None,
    )
    page.on("pageerror", lambda error: page_errors.append(str(error)))

    def on_request_failed(request) -> None:
        failure = str(request.failure or "")
        record = f"{request.method} {request.url}: {failure}"
        if (
            request.method == "GET"
            and "/mixer-routing/media/preview.wav" in request.url
            and "ERR_ABORTED" in failure
        ):
            expected_media_aborts.append(record)
            return
        if teardown_state.get("active") and "ERR_ABORTED" in failure:
            expected_teardown_aborts.append(record)
            return
        request_failures.append(record)

    def on_response(response) -> None:
        if response.status >= 400:
            record = f"{response.request.method} {response.url}: HTTP {response.status}"
            if (
                response.request.method == "GET"
                and "/mixer-routing/media/preview.wav" in response.url
                and response.status in {400, 404, 409}
            ):
                expected_media_aborts.append(record)
                return
            http_error_responses.append(record)

    page.on("requestfailed", on_request_failed)
    page.on("response", on_response)


def _open_project(page, base: str, expect) -> dict[str, Any]:
    page.goto(base + "/", wait_until="domcontentloaded")
    expect(page.locator("#connectionBadge")).to_contain_text("READY")
    page.locator("#openProjectSlug").fill("routing")
    page.locator("#openForm button[type=submit]").click()
    expect(page.locator("#activeProject")).to_be_visible()
    expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
    page.locator('button[data-tab="inspect"]').click()
    expect(page.locator("#panel-inspect")).to_be_visible()
    expect(page.locator("#mramRoutingBadge")).to_have_text("ACCEPTED ROUTING")
    expect(page.locator('#mramNodes .mram-row[data-mram-id="BUS-001"]')).to_be_visible()
    expect(page.locator('#mramSends .mram-row[data-mram-id="SEND-001"]')).to_be_visible()
    expect(page.locator('#mramNativeAutomation .mram-row[data-mram-id="AUTO-AT001-GAIN"]')).to_be_visible()
    expect(page.locator("#m7AutomationWorkspace")).to_be_visible()
    return _session(page)


def _browser_audio_sha(page) -> str:
    return page.evaluate(
        """async () => {
          const audio = document.querySelector("#mramRoutingAudio");
          const response = await fetch(audio.src);
          if (!response.ok) throw new Error("routed audio fetch failed: " + response.status);
          const bytes = await response.arrayBuffer();
          const digest = await crypto.subtle.digest("SHA-256", bytes);
          return Array.from(new Uint8Array(digest)).map((value) => value.toString(16).padStart(2, "0")).join("");
        }"""
    )


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:
        raise RuntimeError("MRAM-R3 requires .[dev,e2e]") from exc

    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    workspace = root / "workspace"
    workspace.mkdir()
    _root_revision, initial_revision = _prepare_project(workspace)

    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []
    expected_media_aborts: list[str] = []
    expected_teardown_aborts: list[str] = []
    http_error_responses: list[str] = []
    screenshots: list[Path] = []
    records: dict[str, Any] = {}

    service1, server1, thread1, base1 = _start_server(workspace)
    server1_stopped = False

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1600, "height": 1400}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        try:
            page = context.new_page()
            page_teardown = {"active": False}
            _attach_observers(
                page,
                console_errors,
                page_errors,
                request_failures,
                expected_media_aborts,
                expected_teardown_aborts,
                http_error_responses,
                page_teardown,
            )
            opened = _open_project(page, base1, expect)
            if str(opened["head_revision_id"]) != initial_revision:
                raise RuntimeError("MRAM-R3 Browser opened wrong accepted revision")

            source_routing = _routing_state(page)["view"]
            source_automation = _automation_state(page)["view"]
            if not source_routing or not source_automation:
                raise RuntimeError("MRAM-R3 Browser projections did not load")
            if source_routing["revision_id"] != source_automation["revision_id"]:
                raise RuntimeError("routing/automation Browser projections are not revision-bound")
            if source_routing["automation_material_sha256"] != source_automation["automation_material_sha256"]:
                raise RuntimeError("routing/automation Browser projections disagree on automation hash")
            if source_routing["routing_material_sha256"] != source_automation["routing_material_sha256"]:
                raise RuntimeError("routing/automation Browser projections disagree on routing hash")
            browser_source_audio_sha = _browser_audio_sha(page)
            if browser_source_audio_sha != source_routing["accepted_audition"]["wav_sha256"]:
                raise RuntimeError("Browser routed audio bytes do not match accepted routed WAV hash")
            screenshots.append(_screenshot(page, root / "01-accepted-routing-automation.png"))

            source_head = str(opened["head_revision_id"])
            page.locator("#mramSendSelect").select_option("SEND-001")
            page.locator("#mramSendGain").fill("-2")
            page.locator("#mramPreviewSendGain").click()
            expect(page.locator("#projectStateBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            expect(page.locator("#mramRoutingBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            page.wait_for_function("() => window.MUSICA_ROUTING && window.MUSICA_ROUTING.state.view && window.MUSICA_ROUTING.state.view.preview")
            routing_preview_state = _routing_state(page)
            routing_preview = routing_preview_state["view"]["preview"]
            if service1.inspect_session(str(opened["session_id"]))["head_revision_id"] != source_head:
                raise RuntimeError("routing Browser Preview changed accepted HEAD")
            if [op["op"] for op in routing_preview_state["lastSubmittedCandidate"]["operations"]] != ["SET_SEND_GAIN"]:
                raise RuntimeError("routing Browser did not submit exactly SET_SEND_GAIN")
            preview_audio_sha = _browser_audio_sha(page)
            if preview_audio_sha != routing_preview["audition"]["wav_sha256"]:
                raise RuntimeError("Browser routing Preview audio does not match exact routed candidate")
            if preview_audio_sha == browser_source_audio_sha:
                raise RuntimeError("controlled routing Preview did not change routed WAV")
            routing_candidate_revision = str(routing_preview["candidate_revision_id"])
            screenshots.append(_screenshot(page, root / "02-routing-preview.png"))

            page.locator("#acceptButton").click()
            expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
            page.wait_for_function("() => window.MUSICA_ROUTING && window.MUSICA_ROUTING.state.view && !window.MUSICA_ROUTING.state.view.preview")
            accepted_routing = _routing_state(page)["view"]
            if str(_session(page)["head_revision_id"]) != routing_candidate_revision:
                raise RuntimeError("routing explicit Accept did not advance exactly to candidate")
            send = next(item for item in accepted_routing["sends"] if item["send_id"] == "SEND-001")
            if float(send["gain_db"]) != -2.0:
                raise RuntimeError("accepted routing send gain did not persist")
            screenshots.append(_screenshot(page, root / "03-routing-accepted.png"))

            # Existing M7 table now edits the MRAM-R2 native lane through the trusted R2 path.
            row = page.locator('#m7AutomationLanes tr[data-lane-id="AUTO-AT001-GAIN"][data-point-id="P-R3-1"]').first
            expect(row).to_be_visible()
            row.focus()
            row.press("Enter")
            page.locator("#m7PointValue").fill("-12")
            page.locator("#m7PreviewPointChanges").click()
            expect(page.locator("#projectStateBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            page.wait_for_function("() => window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state.view && window.MUSICA_AUTOMATION.state.view.preview")
            auto_state = _automation_state(page)
            if auto_state["lastAuthorityResult"]["status"] != "READY_FOR_PREVIEW":
                raise RuntimeError("native automation Browser edit did not pass trusted authority")
            auto_session = service1.inspect_session(str(opened["session_id"]))
            pending = service1._get_session(str(opened["session_id"])).pending
            if pending is None or pending.detail.get("studio_audition", {}).get("path") != "mram-r2-routed-native-mixer":
                raise RuntimeError("native automation Browser Preview did not use routed mixer")
            if auto_session["head_revision_id"] != routing_candidate_revision:
                raise RuntimeError("native automation Preview changed accepted HEAD")
            auto_candidate_revision = str(auto_state["view"]["preview"]["candidate_revision_id"])
            screenshots.append(_screenshot(page, root / "04-native-automation-preview.png"))

            page.locator("#acceptButton").click()
            expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
            page.wait_for_function("() => window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state.view && !window.MUSICA_AUTOMATION.state.view.preview")
            accepted_auto = _automation_state(page)["view"]
            if str(_session(page)["head_revision_id"]) != auto_candidate_revision:
                raise RuntimeError("native automation explicit Accept did not advance exactly once")
            accepted_lane = next(lane for lane in accepted_auto["lanes"] if lane["lane_id"] == "AUTO-AT001-GAIN")
            accepted_point = next(point for point in accepted_lane["points"] if point["point_id"] == "P-R3-1")
            if float(accepted_point["value"]) != -12.0:
                raise RuntimeError("native automation Browser value did not persist")
            page.wait_for_function(
                """revisionId => window.MUSICA_ROUTING
                  && window.MUSICA_ROUTING.state.view
                  && window.MUSICA_ROUTING.state.view.revision_id === revisionId
                  && !window.MUSICA_ROUTING.state.view.preview""",
                arg=auto_candidate_revision,
            )
            final_routing = _routing_state(page)["view"]
            final_audio_sha = _browser_audio_sha(page)
            if final_audio_sha != final_routing["accepted_audition"]["wav_sha256"]:
                raise RuntimeError("post-automation Browser audio is not exact routed accepted WAV")
            screenshots.append(_screenshot(page, root / "05-native-automation-accepted.png"))

            # Unknown stable ID fails closed from a real Browser request.
            unknown = page.evaluate(
                """async () => {
                  const view = window.MUSICA_ROUTING.state.view;
                  const candidate = {
                    candidate_version: "0",
                    candidate_id: "R3-UNKNOWN-SEND",
                    authority_target: "blueprint_routing_material",
                    source: {
                      project_id: view.project_id,
                      revision_id: view.revision_id,
                      blueprint_sha256: view.blueprint_sha256,
                      audio_material_sha256: view.audio_material_sha256,
                      routing_material_sha256: view.routing_material_sha256
                    },
                    actor: {kind: "user", actor_id: "browser-negative"},
                    reason: "unknown send negative",
                    operations: [{operation_id:"NEG-1",op:"SET_SEND_GAIN",send_id:"SEND-MISSING",gain_db:-1}],
                    preview_only: true
                  };
                  const response = await fetch("/v0/sessions/" + encodeURIComponent(window.MUSICA_ROUTING.state.sessionId) + "/preview/routing", {
                    method:"POST", headers:{"Content-Type":"application/json","Accept":"application/json"}, body:JSON.stringify({candidate})
                  });
                  return await response.json();
                }"""
            )
            unknown_data = unknown["data"]
            if unknown_data["preview_installed"] is not False:
                raise RuntimeError("unknown routing ID installed Browser Preview")
            if unknown_data["authority_result"]["conflicts"][0]["code"] != "UNKNOWN_SEND":
                raise RuntimeError("unknown routing ID did not fail closed as UNKNOWN_SEND")

            # The original pre-routing Browser source is now stale and must not silently rebase.
            stale_candidate = {
                "candidate_version": "0",
                "candidate_id": "R3-STALE-SOURCE",
                "authority_target": "blueprint_routing_material",
                "source": {
                    "project_id": source_routing["project_id"],
                    "revision_id": source_routing["revision_id"],
                    "blueprint_sha256": source_routing["blueprint_sha256"],
                    "audio_material_sha256": source_routing["audio_material_sha256"],
                    "routing_material_sha256": source_routing["routing_material_sha256"],
                },
                "actor": {"kind": "user", "actor_id": "browser-negative"},
                "reason": "stale routing negative",
                "operations": [{"operation_id":"NEG-2","op":"SET_SEND_GAIN","send_id":"SEND-001","gain_db":-4.0}],
                "preview_only": True,
            }
            stale = page.evaluate(
                """async (candidate) => {
                  const sid = window.MUSICA_ROUTING.state.sessionId;
                  const response = await fetch("/v0/sessions/" + encodeURIComponent(sid) + "/preview/routing", {
                    method:"POST", headers:{"Content-Type":"application/json","Accept":"application/json"}, body:JSON.stringify({candidate})
                  });
                  return await response.json();
                }""",
                stale_candidate,
            )
            if stale["data"]["preview_installed"] is not False:
                raise RuntimeError("stale Browser routing source installed Preview")
            if stale["data"]["authority_result"]["conflicts"][0]["code"] != "STALE_SOURCE":
                raise RuntimeError("stale Browser routing source did not fail closed")

            records["source_routing_view"] = source_routing
            records["routing_preview"] = routing_preview_state
            records["accepted_routing_view"] = accepted_routing
            records["accepted_automation_view"] = accepted_auto
            records["final_routing_view"] = final_routing
            records["unknown_id_result"] = unknown_data
            records["stale_source_result"] = stale["data"]
            final_revision = str(_session(page)["head_revision_id"])
            page.wait_for_load_state("networkidle")
            page_teardown["active"] = True
            page.close()

            _stop_server(server1, thread1)
            server1_stopped = True

            service2, server2, thread2, base2 = _start_server(workspace)
            reopen_page = context.new_page()
            reopen_teardown = {"active": False}
            _attach_observers(
                reopen_page,
                console_errors,
                page_errors,
                request_failures,
                expected_media_aborts,
                expected_teardown_aborts,
                http_error_responses,
                reopen_teardown,
            )
            try:
                reopened_session = _open_project(reopen_page, base2, expect)
                reopened_routing = _routing_state(reopen_page)["view"]
                reopened_auto = _automation_state(reopen_page)["view"]
                reopened_audio_sha = _browser_audio_sha(reopen_page)
                if str(reopened_session["head_revision_id"]) != final_revision:
                    raise RuntimeError("fresh restart/reopen changed accepted revision")
                if reopened_routing["routing_material_sha256"] != final_routing["routing_material_sha256"]:
                    raise RuntimeError("restart/reopen routing hash changed")
                if reopened_routing["automation_material_sha256"] != final_routing["automation_material_sha256"]:
                    raise RuntimeError("restart/reopen automation hash changed")
                if reopened_routing["native_automation_lanes"] != final_routing["native_automation_lanes"]:
                    raise RuntimeError("restart/reopen native automation identities changed")
                if reopened_routing["accepted_audition"]["routed_mix_plan_sha256"] != final_routing["accepted_audition"]["routed_mix_plan_sha256"]:
                    raise RuntimeError("restart/reopen routed plan hash changed")
                if reopened_audio_sha != final_audio_sha:
                    raise RuntimeError("restart/reopen routed WAV hash changed")
                if service2.inspect_session(str(reopened_session["session_id"]))["integrity_status"] != "PASS":
                    raise RuntimeError("restart/reopen integrity failed")
                records["reopened_routing_view"] = reopened_routing
                records["reopened_automation_view"] = reopened_auto
                screenshots.append(_screenshot(reopen_page, root / "06-reopened-exact.png"))
                reopen_page.wait_for_load_state("networkidle")
            finally:
                reopen_teardown["active"] = True
                reopen_page.close()
                _stop_server(server2, thread2)
        finally:
            if not server1_stopped:
                _stop_server(server1, thread1)
            context.close()
            browser.close()

    for name, value in records.items():
        write_canonical_json(root / f"{name.replace('_','-')}.json", value)

    contract_hashes = []
    for source_path in CONTRACT_PATHS:
        data = source_path.read_bytes()
        contract_hashes.append(
            {
                "path": source_path.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
            }
        )
    write_canonical_json(root / "contract-hashes.json", contract_hashes)

    generic_resource_errors = [
        value
        for value in console_errors
        if value.startswith("Failed to load resource:")
    ]
    unexpected_console_errors = list(console_errors)
    for _item in expected_media_aborts:
        if generic_resource_errors:
            generic = generic_resource_errors.pop(0)
            if generic in unexpected_console_errors:
                unexpected_console_errors.remove(generic)

    proof = {
        "milestone": "MRAM-R3",
        "evidence_class": "REAL_BROWSER_ROUTING_NATIVE_AUTOMATION_REOPEN_EVIDENCE",
        "real_chromium_used": True,
        "stable_routing_ids_visible": True,
        "stable_native_automation_ids_visible": True,
        "routing_and_automation_views_bound_to_same_exact_source": True,
        "accepted_routed_audio_hash_matches_browser_bytes": True,
        "routing_preview_head_unchanged": True,
        "routing_preview_exact_routed_audio_changed": True,
        "routing_explicit_accept_advanced_once": True,
        "native_automation_preview_head_unchanged": True,
        "native_automation_preview_used_routed_mixer": True,
        "native_automation_explicit_accept_advanced_once": True,
        "unknown_id_blocked": True,
        "stale_source_blocked": True,
        "restart_reopen_revision_exact": True,
        "restart_reopen_routing_hash_exact": True,
        "restart_reopen_automation_hash_exact": True,
        "restart_reopen_native_identities_exact": True,
        "restart_reopen_routed_plan_exact": True,
        "restart_reopen_routed_wav_exact": True,
        "browser_project_mutation_authorized": False,
        "browser_state_is_canonical": False,
        "browser_console_error_count": len(unexpected_console_errors),
        "browser_page_error_count": len(page_errors),
        "browser_request_failure_count": len(request_failures),
        "expected_media_abort_count": len(expected_media_aborts),
        "unexpected_console_errors": unexpected_console_errors,
        "request_failures": request_failures,
        "http_error_responses": http_error_responses,
        "expected_media_aborts": expected_media_aborts,
        "expected_teardown_aborts": expected_teardown_aborts,
    }
    write_canonical_json(root / "proof.json", proof)

    tracked = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.name != "manifest.json" and "workspace" not in path.parts
    ]
    manifest = {
        "manifest_version": "0",
        "milestone": "MRAM-R3",
        "evidence_class": "REAL_BROWSER_ROUTING_NATIVE_AUTOMATION_REOPEN_EVIDENCE",
        "proof": proof,
        "final_revision_id": final_revision,
        "final_routed_wav_sha256": final_audio_sha,
        "screenshots": [path.name for path in screenshots],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(tracked, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MRAM-R3 real-browser evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
