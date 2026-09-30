"""REC-R3 real-Chromium recording/monitoring Preview-Accept + restart evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .audio_assets import list_audio_assets
from .audio_contracts import audio_material_from_blueprint
from .evidence import artifact_record, write_canonical_json
from .mram_r3_e2e import (
    _attach_observers,
    _open_project,
    _prepare_project,
    _screenshot,
    _start_server,
    _stop_server,
)
from .routed_mixer import render_routed_mix

ROOT = Path(__file__).resolve().parents[2]

CONTRACT_PATHS = [
    ROOT / "schemas" / "recording-capture-plan-v0.schema.json",
    ROOT / "schemas" / "recording-capture-run-report-v0.schema.json",
    ROOT / "schemas" / "recording-monitor-plan-v0.schema.json",
    ROOT / "schemas" / "recording-monitor-run-report-v0.schema.json",
    ROOT / "schemas" / "recording-finalize-candidate-v0.schema.json",
    ROOT / "schemas" / "recording-finalize-authority-result-v0.schema.json",
    ROOT / "schemas" / "studio-recording-view-v0.schema.json",
    ROOT / "src" / "musica" / "recording_capture.py",
    ROOT / "src" / "musica" / "recording_monitor.py",
    ROOT / "src" / "musica" / "recording_finalize.py",
    ROOT / "src" / "musica" / "studio_recording.py",
    ROOT / "src" / "musica" / "studio_http.py",
    ROOT / "src" / "musica" / "studio_web" / "recording_monitoring.js",
    ROOT / "src" / "musica" / "studio_web" / "recording_monitoring.css",
    ROOT / "tests" / "test_rec_r3_studio_recording.py",
    ROOT / "e2e" / "test_rec_r3_browser.py",
    ROOT / ".github" / "workflows" / "rec-r3-studio-recording-reopen-evidence.yml",
]


def _recording_state(page) -> dict[str, Any]:
    value = page.evaluate(
        """() => window.MUSICA_RECORDING ? {
          sessionId: window.MUSICA_RECORDING.state.sessionId,
          runtimeId: window.MUSICA_RECORDING.state.runtimeId,
          view: window.MUSICA_RECORDING.state.view
            ? JSON.parse(JSON.stringify(window.MUSICA_RECORDING.state.view))
            : null
        } : null"""
    )
    if not isinstance(value, dict):
        raise RuntimeError("REC-R3 Browser recording state unavailable")
    return value


def _clip_ids(project: Any, revision_id: str, track_id: str = "AT-001") -> set[str]:
    material = audio_material_from_blueprint(project.read_revision(revision_id))
    assert material is not None
    track = next(item for item in material["tracks"] if str(item["track_id"]) == track_id)
    return {str(clip["clip_id"]) for clip in track["clips"]}


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:
        raise RuntimeError("REC-R3 requires .[dev,e2e]") from exc

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
    final_revision = initial_revision
    runtime_id = ""

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1600, "height": 1700},
            reduced_motion="reduce",
        )
        context.set_default_timeout(30_000)
        try:
            page = context.new_page()
            teardown = {"active": False}
            _attach_observers(
                page,
                console_errors,
                page_errors,
                request_failures,
                expected_media_aborts,
                expected_teardown_aborts,
                http_error_responses,
                teardown,
            )
            opened = _open_project(page, base1, expect)
            session_id = str(opened["session_id"])
            if str(opened["head_revision_id"]) != initial_revision:
                raise RuntimeError("REC-R3 Browser opened wrong accepted revision")

            expect(page.locator("#recRuntimeCard")).to_be_visible()
            expect(page.locator("#recRuntimeBadge")).to_have_text("READY")
            page.wait_for_function(
                "() => window.MUSICA_RECORDING && window.MUSICA_RECORDING.state.view"
            )
            source_state = _recording_state(page)
            source_view = source_state["view"]
            if source_view["revision_id"] != initial_revision:
                raise RuntimeError("REC-R3 recording view not bound to accepted revision")
            if source_view["authority"]["recording_runtime_is_canonical"] is not False:
                raise RuntimeError("REC-R3 Browser mislabeled recording runtime authority")
            if source_view["authority"]["runtime_may_import_assets"] is not False:
                raise RuntimeError("REC-R3 Browser runtime gained asset import authority")
            if source_view["authority"]["runtime_may_commit_audio_material"] is not False:
                raise RuntimeError("REC-R3 Browser runtime gained audio commit authority")

            project1 = service1._get_session(session_id).project
            source_head = project1.head_revision_id()
            source_assets = list_audio_assets(project1)
            source_clips = _clip_ids(project1, source_head)
            screenshots.append(_screenshot(page, root / "01-recording-ready.png"))

            page.locator("#recRate").select_option("8000")
            page.locator("#recBlock").select_option("256")
            page.locator("#recFrames").fill("800")
            page.locator("#recMonitorEnabled").check()
            page.locator("#recStart").click()
            expect(page.locator("#recRuntimeBadge")).to_have_text("CLEAN CAPTURE")
            page.wait_for_function(
                "() => window.MUSICA_RECORDING.state.view && window.MUSICA_RECORDING.state.view.runtime"
            )
            capture_state = _recording_state(page)
            runtime = capture_state["view"]["runtime"]
            runtime_id = str(runtime["runtime_id"])
            if not runtime["capture_clean"]:
                raise RuntimeError("REC-R3 clean Browser capture reported dirty")
            if int(runtime["capture_metrics"]["frames_captured"]) != 800:
                raise RuntimeError("REC-R3 Browser captured frame count mismatch")
            if int(runtime["monitor_metrics"]["frames_written"]) != 800:
                raise RuntimeError("REC-R3 Browser monitor frame count mismatch")
            if project1.head_revision_id() != source_head:
                raise RuntimeError("REC-R3 capture/monitor runtime changed accepted HEAD")
            if list_audio_assets(project1) != source_assets:
                raise RuntimeError("REC-R3 capture/monitor runtime imported project asset")
            screenshots.append(_screenshot(page, root / "02-clean-capture-monitor.png"))

            page.locator("#recTrack").select_option("AT-001")
            page.locator("#recClip").fill("REC-R3-BROWSER-001")
            page.locator("#recStartSeconds").fill("0.4")
            page.locator("#recPreview").click()
            page.wait_for_function(
                """() => window.MUSICA_RECORDING.state.view
                  && window.MUSICA_RECORDING.state.view.runtime
                  && window.MUSICA_RECORDING.state.view.runtime.finalize_preview"""
            )
            preview_state = _recording_state(page)
            finalize_preview = preview_state["view"]["runtime"]["finalize_preview"]
            if finalize_preview["authority_result"]["status"] != "READY_FOR_PREVIEW":
                raise RuntimeError("REC-R3 Browser finalize Preview was not ready")
            if project1.head_revision_id() != source_head:
                raise RuntimeError("REC-R3 finalize Preview changed accepted HEAD")
            if list_audio_assets(project1) != source_assets:
                raise RuntimeError("REC-R3 finalize Preview imported asset before Accept")
            if _clip_ids(project1, source_head) != source_clips:
                raise RuntimeError("REC-R3 finalize Preview changed accepted clip state")
            screenshots.append(_screenshot(page, root / "03-recording-finalize-preview.png"))

            page.locator("#recAccept").click()
            expect(page.locator("#recRuntimeBadge")).to_have_text("READY")
            page.wait_for_function(
                """source => window.MUSICA_RECORDING.state.view
                  && window.MUSICA_RECORDING.state.view.revision_id !== source
                  && !window.MUSICA_RECORDING.state.view.runtime""",
                arg=source_head,
            )
            accepted_state = _recording_state(page)
            final_revision = str(accepted_state["view"]["revision_id"])
            if final_revision == source_head:
                raise RuntimeError("REC-R3 explicit Accept did not advance revision")
            if "REC-R3-BROWSER-001" not in _clip_ids(project1, final_revision):
                raise RuntimeError("REC-R3 accepted recording clip missing")
            if len(list_audio_assets(project1)) != len(source_assets) + 1:
                raise RuntimeError("REC-R3 accepted recording asset count mismatch")
            final_render_before = render_routed_mix(
                project1, final_revision, mix_sample_rate_hz=8000
            )
            screenshots.append(_screenshot(page, root / "04-recording-accepted.png"))

            # The accepted runtime handle is transient and removed after Accept.
            stale_handle = page.evaluate(
                """async ([sid, rid]) => {
                  const response = await fetch(
                    "/v0/sessions/" + encodeURIComponent(sid)
                      + "/recording/" + encodeURIComponent(rid) + "/accept",
                    {method:"POST",headers:{"Content-Type":"application/json","Accept":"application/json"},body:"{}"}
                  );
                  return {status:response.status,payload:await response.json()};
                }""",
                [session_id, runtime_id],
            )
            if stale_handle["status"] != 404 or stale_handle["payload"]["error"]["code"] != "not_found":
                raise RuntimeError("REC-R3 stale accepted runtime handle did not fail closed")

            # Dirty capture remains visible but cannot produce an accepted finalize Preview.
            dirty = page.evaluate(
                """async (sid) => {
                  const response = await fetch(
                    "/v0/sessions/" + encodeURIComponent(sid) + "/recording/run",
                    {
                      method:"POST",
                      headers:{"Content-Type":"application/json","Accept":"application/json"},
                      body:JSON.stringify({
                        sample_rate_hz:8000,input_channels:2,block_size_frames:256,
                        capture_frames:800,monitor_enabled:true,
                        force_short_fill_block_indices:[1]
                      })
                    }
                  );
                  return {status:response.status,payload:await response.json()};
                }""",
                session_id,
            )
            if dirty["status"] != 200:
                raise RuntimeError("REC-R3 dirty capture request failed unexpectedly")
            dirty_view = dirty["payload"]["data"]
            dirty_runtime_id = str(dirty_view["runtime"]["runtime_id"])
            if dirty_view["runtime"]["capture_clean"] is not False:
                raise RuntimeError("REC-R3 dirty capture was mislabeled clean")

            blocked = page.evaluate(
                """async ([sid, rid]) => {
                  const response = await fetch(
                    "/v0/sessions/" + encodeURIComponent(sid)
                      + "/recording/" + encodeURIComponent(rid) + "/preview",
                    {
                      method:"POST",
                      headers:{"Content-Type":"application/json","Accept":"application/json"},
                      body:JSON.stringify({track_id:"AT-001",clip_id:"REC-R3-DIRTY",timeline_start_seconds:0,gain_db:0})
                    }
                  );
                  return {status:response.status,payload:await response.json()};
                }""",
                [session_id, dirty_runtime_id],
            )
            if blocked["status"] != 200:
                raise RuntimeError("REC-R3 dirty finalize Preview HTTP request failed")
            blocked_data = blocked["payload"]["data"]
            if blocked_data["preview_installed"] is not False:
                raise RuntimeError("REC-R3 dirty capture incorrectly produced ready Preview")
            if blocked_data["authority_result"]["status"] != "BLOCKED":
                raise RuntimeError("REC-R3 dirty capture authority status mismatch")

            reset = page.evaluate(
                """async ([sid, rid]) => {
                  const response = await fetch(
                    "/v0/sessions/" + encodeURIComponent(sid)
                      + "/recording/" + encodeURIComponent(rid) + "/reset",
                    {method:"POST",headers:{"Content-Type":"application/json","Accept":"application/json"},body:"{}"}
                  );
                  return {status:response.status,payload:await response.json()};
                }""",
                [session_id, dirty_runtime_id],
            )
            if reset["status"] != 200 or reset["payload"]["data"]["runtime"] is not None:
                raise RuntimeError("REC-R3 dirty runtime reset failed")
            if project1.head_revision_id() != final_revision:
                raise RuntimeError("REC-R3 dirty capture/reset changed accepted HEAD")

            records["source_recording_view"] = source_view
            records["clean_capture_view"] = capture_state["view"]
            records["finalize_preview"] = finalize_preview
            records["accepted_recording_view"] = accepted_state["view"]
            records["dirty_capture_view"] = dirty_view
            records["dirty_finalize_result"] = blocked_data
            records["stale_runtime_result"] = stale_handle
            records["final_routed_plan"] = final_render_before.plan
            (root / "final-routed-before.wav").write_bytes(final_render_before.wav_bytes)

            page.wait_for_load_state("networkidle")
            teardown["active"] = True
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
                reopened = _open_project(reopen_page, base2, expect)
                reopened_session_id = str(reopened["session_id"])
                if str(reopened["head_revision_id"]) != final_revision:
                    raise RuntimeError("REC-R3 restart/reopen changed accepted revision")
                expect(reopen_page.locator("#recRuntimeCard")).to_be_visible()
                expect(reopen_page.locator("#recRuntimeBadge")).to_have_text("READY")
                reopen_page.wait_for_function(
                    "() => window.MUSICA_RECORDING && window.MUSICA_RECORDING.state.view"
                )
                reopen_state = _recording_state(reopen_page)
                if reopen_state["view"]["runtime"] is not None:
                    raise RuntimeError("REC-R3 transient recording runtime persisted across restart")

                project2 = service2._get_session(reopened_session_id).project
                if "REC-R3-BROWSER-001" not in _clip_ids(project2, final_revision):
                    raise RuntimeError("REC-R3 accepted recording missing after restart/reopen")
                if list_audio_assets(project2) != list_audio_assets(project1):
                    raise RuntimeError("REC-R3 accepted asset inventory changed after reopen")
                final_render_after = render_routed_mix(
                    project2, final_revision, mix_sample_rate_hz=8000
                )
                if final_render_after.plan != final_render_before.plan:
                    raise RuntimeError("REC-R3 routed plan changed after restart/reopen")
                if final_render_after.wav_bytes != final_render_before.wav_bytes:
                    raise RuntimeError("REC-R3 routed WAV changed after restart/reopen")
                if project2.verify_integrity()["status"] != "PASS":
                    raise RuntimeError("REC-R3 reopened project integrity failed")

                records["restart_recording_view"] = reopen_state["view"]
                (root / "final-routed-after.wav").write_bytes(final_render_after.wav_bytes)
                screenshots.append(_screenshot(reopen_page, root / "05-recording-reopened-reset.png"))
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
        write_canonical_json(root / f"{name.replace('_', '-')}.json", value)

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

    expected_http_errors = [
        value
        for value in http_error_responses
        if f"/recording/{runtime_id}/accept" in value and "HTTP 404" in value
    ]
    unexpected_http_errors = [
        value for value in http_error_responses if value not in expected_http_errors
    ]
    unexpected_console_errors = list(console_errors)
    generic_resource_errors = [
        value for value in unexpected_console_errors
        if value.startswith("Failed to load resource:")
    ]
    expected_generic_count = len(expected_http_errors) + len(expected_media_aborts)
    for _ in range(expected_generic_count):
        if not generic_resource_errors:
            break
        generic = generic_resource_errors.pop(0)
        if generic in unexpected_console_errors:
            unexpected_console_errors.remove(generic)

    proof = {
        "milestone": "REC-R3",
        "evidence_class": "REAL_BROWSER_RECORDING_MONITOR_PREVIEW_ACCEPT_RESTART_REOPEN",
        "real_chromium_used": True,
        "recording_view_bound_to_exact_accepted_revision": True,
        "runtime_state_labeled_noncanonical": True,
        "browser_runtime_asset_import_authorized": False,
        "browser_runtime_audio_commit_authorized": False,
        "clean_capture_monitor_visible": True,
        "capture_monitor_head_unchanged": True,
        "capture_monitor_asset_inventory_unchanged": True,
        "finalize_preview_head_unchanged": True,
        "finalize_preview_asset_inventory_unchanged": True,
        "finalize_preview_audio_material_unchanged": True,
        "explicit_accept_advanced_once": True,
        "accepted_asset_and_clip_visible": True,
        "stale_runtime_handle_blocked": True,
        "dirty_capture_visibly_blocked": True,
        "dirty_runtime_reset_head_unchanged": True,
        "restart_reopen_revision_exact": True,
        "restart_reopen_recording_exact": True,
        "transient_runtime_not_persisted": True,
        "restart_reopen_routed_plan_exact": True,
        "restart_reopen_routed_wav_exact": True,
        "final_routed_wav_sha256": hashlib.sha256(
            (root / "final-routed-before.wav").read_bytes()
        ).hexdigest(),
        "browser_console_error_count": len(unexpected_console_errors),
        "browser_page_error_count": len(page_errors),
        "browser_request_failure_count": len(request_failures),
        "unexpected_http_error_count": len(unexpected_http_errors),
        "expected_http_errors": expected_http_errors,
        "expected_media_aborts": expected_media_aborts,
        "expected_teardown_aborts": expected_teardown_aborts,
        "unexpected_console_errors": unexpected_console_errors,
        "request_failures": request_failures,
        "unexpected_http_errors": unexpected_http_errors,
    }
    write_canonical_json(root / "proof.json", proof)

    tracked = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.name != "manifest.json" and "workspace" not in path.parts
    ]
    manifest = {
        "manifest_version": "0",
        "milestone": "REC-R3",
        "evidence_class": "REAL_BROWSER_RECORDING_MONITOR_PREVIEW_ACCEPT_RESTART_REOPEN",
        "proof": proof,
        "final_revision_id": final_revision,
        "screenshots": [path.name for path in screenshots],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(tracked, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate REC-R3 real-browser evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
