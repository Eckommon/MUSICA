"""RTIO-R3 real-Chromium runtime inspection + fresh restart/reopen evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .evidence import artifact_record, write_canonical_json
from .mram_r3_e2e import (
    _attach_observers,
    _open_project,
    _prepare_project,
    _screenshot,
    _start_server,
    _stop_server,
)
from .realtime_engine import build_realtime_execution_plan
from .realtime_transport import ExactFrameTransport

ROOT = Path(__file__).resolve().parents[2]

CONTRACT_PATHS = [
    ROOT / "schemas" / "realtime-execution-plan-v0.schema.json",
    ROOT / "schemas" / "realtime-transport-event-v0.schema.json",
    ROOT / "schemas" / "realtime-transport-run-report-v0.schema.json",
    ROOT / "schemas" / "studio-realtime-runtime-view-v0.schema.json",
    ROOT / "src" / "musica" / "realtime_engine.py",
    ROOT / "src" / "musica" / "realtime_callback.py",
    ROOT / "src" / "musica" / "realtime_transport.py",
    ROOT / "src" / "musica" / "studio_realtime.py",
    ROOT / "src" / "musica" / "studio_http.py",
    ROOT / "src" / "musica" / "studio_web" / "realtime_runtime.js",
    ROOT / "src" / "musica" / "studio_web" / "realtime_runtime.css",
    ROOT / "tests" / "test_rtio_r3_studio_runtime.py",
    ROOT / "e2e" / "test_rtio_r3_browser.py",
    ROOT / ".github" / "workflows" / "rtio-r3-studio-runtime-reopen-evidence.yml",
]


def _runtime_state(page) -> dict[str, Any]:
    value = page.evaluate(
        """() => window.MUSICA_REALTIME ? {
          sessionId: window.MUSICA_REALTIME.state.sessionId,
          runtimeId: window.MUSICA_REALTIME.state.runtimeId,
          view: window.MUSICA_REALTIME.state.view
            ? JSON.parse(JSON.stringify(window.MUSICA_REALTIME.state.view))
            : null,
          lastErrorCode: window.MUSICA_REALTIME.state.lastErrorCode
        } : null"""
    )
    if not isinstance(value, dict):
        raise RuntimeError("RTIO-R3 Browser runtime state unavailable")
    return value


def _scenario(project: Any, revision_id: str):
    transport = ExactFrameTransport(
        project,
        revision_id,
        sample_rate_hz=8000,
        output_channels=2,
        block_size_frames=256,
    )
    transport.play()
    transport.callback()
    transport.callback()
    transport.callback()
    transport.stop()
    transport.seek(48000)
    transport.play()
    transport.drain_to_eos()
    return transport.finalize()


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:
        raise RuntimeError("RTIO-R3 requires .[dev,e2e]") from exc

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

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1600, "height": 1500},
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
                raise RuntimeError("RTIO-R3 Browser opened wrong accepted revision")

            expect(page.locator("#rtioRuntimeCard")).to_be_visible()
            page.locator("#rtioSampleRate").select_option("8000")
            page.locator("#rtioBlockSize").select_option("256")
            page.locator("#rtioOpen").click()
            expect(page.locator("#rtioRuntimeWorkspace")).to_be_visible()
            expect(page.locator("#rtioRuntimeBadge")).to_have_text("STOPPED")
            page.wait_for_function(
                "() => window.MUSICA_REALTIME && window.MUSICA_REALTIME.state.view"
            )

            opened_runtime = _runtime_state(page)
            source_view = opened_runtime["view"]
            if source_view["revision_id"] != initial_revision:
                raise RuntimeError("RTIO-R3 runtime is not bound to accepted revision")
            if source_view["transport"]["playhead_frame"] != 0:
                raise RuntimeError("RTIO-R3 runtime did not open at exact frame zero")
            if source_view["authority"]["runtime_state_is_canonical"] is not False:
                raise RuntimeError("RTIO-R3 Browser mislabeled runtime authority")
            if source_view["authority"]["project_mutation_authorized"] is not False:
                raise RuntimeError("RTIO-R3 Browser runtime gained project mutation authority")
            if source_view["latency"]["host_observed_latency_available"] is not False:
                raise RuntimeError("RTIO-R3 Browser mislabeled simulated latency as host-observed")
            if source_view["latency"]["wall_clock_guarantee_claimed"] is not False:
                raise RuntimeError("RTIO-R3 Browser claimed wall-clock guarantee")

            source_head = service1.inspect_session(session_id)["head_revision_id"]
            screenshots.append(_screenshot(page, root / "01-runtime-open-stopped.png"))

            page.locator("#rtioPlay").click()
            expect(page.locator("#rtioRuntimeBadge")).to_have_text("PLAYING")
            page.locator("#rtioStep").click()
            page.wait_for_function(
                "() => window.MUSICA_REALTIME.state.view.transport.playhead_frame === 256"
            )
            stepped = _runtime_state(page)["view"]
            if stepped["metrics"]["callbacks_requested"] != 1:
                raise RuntimeError("RTIO-R3 Browser callback metric mismatch")
            page.locator("#rtioStop").click()
            expect(page.locator("#rtioRuntimeBadge")).to_have_text("STOPPED")
            page.locator("#rtioSeekFrame").fill("48000")
            page.locator("#rtioSeek").click()
            page.wait_for_function(
                "() => window.MUSICA_REALTIME.state.view.transport.playhead_frame === 48000"
            )
            command_view = _runtime_state(page)["view"]
            if command_view["metrics"]["seek_count"] != 1:
                raise RuntimeError("RTIO-R3 Browser seek metric mismatch")
            if service1.inspect_session(session_id)["head_revision_id"] != source_head:
                raise RuntimeError("RTIO-R3 runtime commands changed accepted Project HEAD")
            screenshots.append(_screenshot(page, root / "02-runtime-seek-exact-frame.png"))

            # Unknown runtime IDs fail closed through the real Browser HTTP path.
            unknown = page.evaluate(
                """async (sid) => {
                  const response = await fetch(
                    "/v0/sessions/" + encodeURIComponent(sid) + "/realtime/rtio-missing",
                    {headers:{Accept:"application/json"}}
                  );
                  return {status: response.status, payload: await response.json()};
                }""",
                session_id,
            )
            if unknown["status"] != 404 or unknown["payload"]["error"]["code"] != "not_found":
                raise RuntimeError("RTIO-R3 unknown runtime did not fail closed")

            # Advance accepted creative state only through the already validated routing authority.
            page.locator("#mramSendSelect").select_option("SEND-001")
            page.locator("#mramSendGain").fill("-2")
            page.locator("#mramPreviewSendGain").click()
            expect(page.locator("#projectStateBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            page.locator("#acceptButton").click()
            expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
            page.wait_for_function(
                """source => {
                  const node = document.querySelector("#sideRevision");
                  return node && node.textContent && node.textContent !== source;
                }""",
                arg=source_head,
            )
            final_revision = str(service1.inspect_session(session_id)["head_revision_id"])
            if final_revision == source_head:
                raise RuntimeError("routing explicit Accept did not advance accepted HEAD")

            # The old runtime remains source-bound and therefore becomes stale.
            page.evaluate("() => window.MUSICA_REALTIME.refresh(false)")
            page.wait_for_function(
                "() => window.MUSICA_REALTIME.state.lastErrorCode === 'conflict'"
            )
            stale_state = _runtime_state(page)
            screenshots.append(_screenshot(page, root / "03-stale-runtime-blocked.png"))

            final_project = service1._get_session(session_id).project
            final_plan = build_realtime_execution_plan(
                final_project,
                final_revision,
                sample_rate_hz=8000,
                output_channels=2,
                block_size_frames=256,
            )
            scenario_before = _scenario(final_project, final_revision)
            if service1.inspect_session(session_id)["head_revision_id"] != final_revision:
                raise RuntimeError("deterministic RTIO scenario changed accepted HEAD")

            records["runtime_open_view"] = source_view
            records["runtime_command_view"] = command_view
            records["unknown_runtime_result"] = unknown
            records["stale_runtime_state"] = stale_state
            records["final_realtime_plan"] = final_plan
            records["scenario_before_events"] = list(scenario_before.events)
            records["scenario_before_report"] = scenario_before.report
            (root / "scenario-before-sink.pcm").write_bytes(scenario_before.sink_payload)

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
                    raise RuntimeError("RTIO-R3 fresh restart/reopen changed accepted revision")
                reopen_page.locator("#rtioSampleRate").select_option("8000")
                reopen_page.locator("#rtioBlockSize").select_option("256")
                reopen_page.locator("#rtioOpen").click()
                expect(reopen_page.locator("#rtioRuntimeBadge")).to_have_text("STOPPED")
                reopen_page.wait_for_function(
                    "() => window.MUSICA_REALTIME && window.MUSICA_REALTIME.state.view"
                )
                reopened_view = _runtime_state(reopen_page)["view"]
                if (
                    reopened_view["realtime_execution_plan_sha256"]
                    != final_plan["realtime_execution_plan_sha256"]
                ):
                    raise RuntimeError("restart/reopen realtime plan identity changed")
                if reopened_view["source"] != {
                    key: final_plan["source"][key]
                    for key in (
                        "blueprint_sha256",
                        "audio_material_sha256",
                        "routing_material_sha256",
                        "automation_material_sha256",
                        "routed_mix_plan_sha256",
                        "routed_wav_sha256",
                    )
                }:
                    raise RuntimeError("restart/reopen realtime source binding changed")
                if reopened_view["transport"]["playhead_frame"] != 0:
                    raise RuntimeError("runtime playhead was incorrectly persisted as creative state")
                if reopened_view["metrics"]["callbacks_requested"] != 0:
                    raise RuntimeError("runtime callback metrics were incorrectly persisted")

                reopened_project = service2._get_session(reopened_session_id).project
                scenario_after = _scenario(reopened_project, final_revision)
                if scenario_after.plan != scenario_before.plan:
                    raise RuntimeError("restart/reopen deterministic scenario plan changed")
                if scenario_after.events != scenario_before.events:
                    raise RuntimeError("restart/reopen deterministic transport events changed")
                if scenario_after.callback_transactions != scenario_before.callback_transactions:
                    raise RuntimeError("restart/reopen callback transactions changed")
                if scenario_after.sink_payload != scenario_before.sink_payload:
                    raise RuntimeError("restart/reopen deterministic sink changed")
                if scenario_after.report != scenario_before.report:
                    raise RuntimeError("restart/reopen deterministic transport report changed")
                if service2.inspect_session(reopened_session_id)["head_revision_id"] != final_revision:
                    raise RuntimeError("restart/reopen runtime inspection changed accepted HEAD")

                records["restart_runtime_view"] = reopened_view
                records["scenario_after_report"] = scenario_after.report
                (root / "scenario-after-sink.pcm").write_bytes(scenario_after.sink_payload)
                screenshots.append(_screenshot(reopen_page, root / "04-runtime-reopened-reset.png"))
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
        if "/realtime/rtio-missing" in value
        or ("/realtime/" in value and "HTTP 409" in value)
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
        "milestone": "RTIO-R3",
        "evidence_class": "REAL_BROWSER_RUNTIME_INSPECTION_RESTART_REOPEN_EVIDENCE",
        "real_chromium_used": True,
        "runtime_bound_to_exact_accepted_revision": True,
        "runtime_bound_to_exact_realtime_plan": True,
        "exact_frame_zero_visible": True,
        "runtime_state_labeled_noncanonical": True,
        "browser_project_mutation_authorized": False,
        "configured_latency_provenance_truthful": True,
        "wall_clock_guarantee_claimed": False,
        "runtime_play_step_stop_seek_head_unchanged": True,
        "exact_seek_frame_visible": True,
        "unknown_runtime_blocked": True,
        "accepted_head_advance_makes_old_runtime_stale": True,
        "restart_reopen_revision_exact": True,
        "restart_reopen_realtime_plan_exact": True,
        "restart_reopen_source_binding_exact": True,
        "runtime_playhead_not_persisted": True,
        "runtime_metrics_not_persisted": True,
        "restart_reopen_transport_events_exact": True,
        "restart_reopen_callback_transactions_exact": True,
        "restart_reopen_sink_exact": True,
        "restart_reopen_transport_report_exact": True,
        "scenario_sink_sha256": hashlib.sha256(
            (root / "scenario-before-sink.pcm").read_bytes()
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
        "milestone": "RTIO-R3",
        "evidence_class": "REAL_BROWSER_RUNTIME_INSPECTION_RESTART_REOPEN_EVIDENCE",
        "proof": proof,
        "final_revision_id": final_revision,
        "final_realtime_execution_plan_sha256": records["final_realtime_plan"][
            "realtime_execution_plan_sha256"
        ],
        "screenshots": [path.name for path in screenshots],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(tracked, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RTIO-R3 real-browser evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
