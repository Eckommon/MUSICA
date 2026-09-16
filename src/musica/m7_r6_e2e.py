"""Generate M7-R6 real-browser truthful audition lifecycle evidence."""

from __future__ import annotations

import argparse
import json
import shutil
import threading
from pathlib import Path
from typing import Any

from .contracts import validate_contract
from .evidence import artifact_record, write_canonical_json
from .project import create_project
from .studio import StudioService
from .studio_http import create_local_server

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _blueprint() -> dict[str, Any]:
    value = _load(BLUEPRINT_PATH)
    value["project"]["project_id"] = "PRJ-M7-R6-BROWSER"
    value["project"]["revision_id"] = "rev-m7-r6-browser-r1"
    value["project"]["parent_revision_id"] = None
    material = _load(AUTOMATION_PATH)
    cutoff = next(lane for lane in material["lanes"] if lane["lane_id"] == "B-SYNTH-CUTOFF")
    cutoff["section_id"] = "S01"
    value["materials"]["automation"] = material
    validate_contract(value, "music-blueprint-v0.schema.json")
    return value


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
        raise RuntimeError("M7-R6 Studio HTTP server thread did not stop cleanly")


def _session(page) -> dict[str, Any]:
    raw = page.locator("#jsonView").text_content() or "{}"
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise RuntimeError("M7-R6 Browser session JSON is not an object")
    return value


def _automation_view(page) -> dict[str, Any]:
    value = page.evaluate(
        """() => window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state
          ? JSON.parse(JSON.stringify(window.MUSICA_AUTOMATION.state.view))
          : null"""
    )
    if not isinstance(value, dict):
        raise RuntimeError("M7-R6 historical Browser automation view is unavailable")
    return value


def _audition(page) -> dict[str, Any]:
    value = page.evaluate(
        """() => window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state
          ? JSON.parse(JSON.stringify(window.MUSICA_AUTOMATION.state.auditionView))
          : null"""
    )
    if not isinstance(value, dict):
        raise RuntimeError("M7-R6 Browser audition inspection state is unavailable")
    return value


def _screenshot(page, path: Path) -> Path:
    page.screenshot(path=str(path), full_page=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"M7-R6 Browser screenshot was not created: {path}")
    return path


def _attach_observers(
    page,
    console_errors: list[str],
    page_errors: list[str],
    request_failures: list[str],
    expected_media_aborts: list[str],
) -> None:
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page.on("pageerror", lambda error: page_errors.append(str(error)))

    def on_request_failed(request) -> None:
        failure = str(request.failure or "")
        record = f"{request.method} {request.url}: {failure}"
        if (
            request.method == "GET"
            and "/media/audio.wav?v=" in request.url
            and "ERR_ABORTED" in failure
        ):
            # The Studio intentionally changes the cache-busted <audio> source when the
            # Preview/accepted lifecycle changes. Chromium cancels the superseded media
            # request; classify only that exact same-origin audio cancellation as expected.
            expected_media_aborts.append(record)
            return
        request_failures.append(record)

    page.on("requestfailed", on_request_failed)


def _open_project(page, base: str, expect, slug: str) -> dict[str, Any]:
    page.goto(base + "/", wait_until="domcontentloaded")
    expect(page.locator("#connectionBadge")).to_contain_text("READY")
    page.locator("#openProjectSlug").fill(slug)
    page.locator("#openForm button[type=submit]").click()
    expect(page.locator("#activeProject")).to_be_visible()
    expect(page.locator("#notice")).to_contain_text("Project opened")
    expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
    page.locator('button[data-tab="inspect"]').click()
    expect(page.locator("#panel-inspect")).to_be_visible()
    expect(page.locator("#m7AutomationAvailability")).to_have_text("AUTOMATION · READY")
    expect(page.locator("#m7AuditionInspector")).to_be_visible()
    page.wait_for_function(
        "() => window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state.auditionView !== null"
    )
    expect(page.locator("#m7AuditionBadge")).to_have_text("ACCEPTED MEDIA")
    return _session(page)


def _select_mix_gain(page, expect) -> None:
    row = page.locator(
        '#m7AutomationLanes tr[data-lane-id="A-MIX-GAIN"][data-point-id="P-GAIN-001"]'
    ).first
    expect(row).to_be_visible()
    row.press("Enter")
    expect(page.locator("#m7SelectedPoint")).to_contain_text("P-GAIN-001")
    expect(page.locator("#m7SelectedPoint")).to_contain_text("A-MIX-GAIN")


def _preview_mix_gain(page, expect, value: str = "0.71") -> dict[str, Any]:
    _select_mix_gain(page, expect)
    page.locator("#m7PointValue").fill(value)
    page.locator("#m7PreviewPointChanges").click()
    expect(page.locator("#projectStateBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
    expect(page.locator("#m7AutomationPreviewBadge")).to_have_text("PREVIEW AUTOMATION · NOT ACCEPTED")
    expect(page.locator("#m7AuditionBadge")).to_have_text("AUDIBLE PREVIEW · NOT ACCEPTED")
    page.wait_for_function(
        "() => window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state.auditionView && window.MUSICA_AUTOMATION.state.auditionView.pending_audition"
    )
    return _audition(page)


def _browser_media_sha256(page, session_id: str, filename: str) -> str:
    value = page.evaluate(
        """async ({sessionId, filename}) => {
          const response = await fetch(`/v0/sessions/${encodeURIComponent(sessionId)}/media/${filename}`);
          if (!response.ok) throw new Error(`media fetch failed: ${response.status}`);
          const bytes = await response.arrayBuffer();
          const digest = await crypto.subtle.digest('SHA-256', bytes);
          return Array.from(new Uint8Array(digest)).map((item) => item.toString(16).padStart(2, '0')).join('');
        }""",
        {"sessionId": session_id, "filename": filename},
    )
    if not isinstance(value, str) or len(value) != 64:
        raise RuntimeError("M7-R6 Browser failed to calculate exact media SHA-256")
    return value


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("M7-R6 requires browser evidence dependencies: install with .[dev,e2e]") from exc

    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    workspace = root / "workspace"
    workspace.mkdir()
    blueprint = _blueprint()
    create_project(workspace / "audition.musica", blueprint)

    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []
    expected_media_aborts: list[str] = []
    screenshots: list[Path] = []

    service1, server1, thread1, base1 = _start_server(workspace)
    server1_stopped = False

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1500, "height": 1300}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        try:
            page = context.new_page()
            _attach_observers(
                page,
                console_errors,
                page_errors,
                request_failures,
                expected_media_aborts,
            )
            opened = _open_project(page, base1, expect, "audition")
            session_id = str(opened["session_id"])
            accepted_root = str(opened["head_revision_id"])
            historical_r2 = _automation_view(page)
            accepted_initial = _audition(page)
            if historical_r2["capabilities"]["audible_automation_validated"] is not False:
                raise RuntimeError("R6 Browser reinterpreted the historical R2 audible capability")
            if accepted_initial["accepted_revision_id"] != accepted_root:
                raise RuntimeError("R6 accepted inspection is not bound to the opened head")
            if accepted_initial["accepted_mapping"]["mapped_lane_ids"] != ["A-MIX-GAIN"]:
                raise RuntimeError("R6 accepted mapping omitted bounded mix.gain lane")
            if accepted_initial["accepted_mapping"]["unmapped_lane_ids"] != ["B-SYNTH-CUTOFF"]:
                raise RuntimeError("R6 accepted mapping did not preserve unsupported cutoff lane")
            if accepted_initial["pending_audition"] is not None:
                raise RuntimeError("R6 accepted state unexpectedly reports pending audition")
            if accepted_initial["accepted_media"]["wav"]["source"] != "fallback_render":
                raise RuntimeError("R6 root accepted WAV should truthfully report fallback_render")
            if accepted_initial["accepted_media"]["midi"]["source"] != "fallback_render":
                raise RuntimeError("R6 root accepted MIDI should truthfully report fallback_render")
            screenshots.append(_screenshot(page, root / "01-accepted-media.png"))

            first_preview = _preview_mix_gain(page, expect)
            first_pending = first_preview["pending_audition"]
            if first_pending is None:
                raise RuntimeError("R6 real browser did not expose pending audition")
            preview_audio_sha = _browser_media_sha256(page, session_id, "audio.wav")
            preview_midi_sha = _browser_media_sha256(page, session_id, "preview.mid")
            if preview_audio_sha != first_pending["preview_wav_sha256"]:
                raise RuntimeError("R6 Browser audio bytes do not match pending inspection hash")
            if preview_midi_sha != first_pending["preview_midi_sha256"]:
                raise RuntimeError("R6 Browser MIDI bytes do not match pending inspection hash")
            if first_preview["accepted_media"] != accepted_initial["accepted_media"]:
                raise RuntimeError("R6 pending audition contaminated accepted-media inspection")
            if first_pending["mapped_lane_ids"] != ["A-MIX-GAIN"]:
                raise RuntimeError("R6 pending audition did not identify mapped mix.gain")
            if first_pending["unmapped_lane_ids"] != ["B-SYNTH-CUTOFF"]:
                raise RuntimeError("R6 pending audition did not identify unmapped cutoff")
            screenshots.append(_screenshot(page, root / "02-audible-preview-not-accepted.png"))

            page.locator("#discardButton").click()
            expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
            expect(page.locator("#m7AuditionBadge")).to_have_text("ACCEPTED MEDIA")
            page.wait_for_function(
                "() => window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state.auditionView && !window.MUSICA_AUTOMATION.state.auditionView.pending_audition"
            )
            discarded = _audition(page)
            if discarded["accepted_revision_id"] != accepted_root:
                raise RuntimeError("R6 Browser Discard changed accepted revision")
            if discarded["accepted_media"] != accepted_initial["accepted_media"]:
                raise RuntimeError("R6 Browser Discard changed accepted media identity")
            screenshots.append(_screenshot(page, root / "03-discard-restored-accepted.png"))

            second_preview = _preview_mix_gain(page, expect)
            second_pending = second_preview["pending_audition"]
            if second_pending is None:
                raise RuntimeError("R6 second Preview did not expose pending audition")
            if second_pending["preview_wav_sha256"] != preview_audio_sha:
                raise RuntimeError("R6 repeated Preview WAV is not deterministic")
            if second_pending["preview_midi_sha256"] != preview_midi_sha:
                raise RuntimeError("R6 repeated Preview MIDI is not deterministic")
            candidate_revision = str(second_pending["candidate_revision_id"])

            page.locator("#acceptButton").click()
            expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
            expect(page.locator("#m7AuditionBadge")).to_have_text("ACCEPTED MEDIA")
            page.wait_for_function(
                """(candidate) => {
                  const view = window.MUSICA_AUTOMATION && window.MUSICA_AUTOMATION.state.auditionView;
                  return view && !view.pending_audition && view.accepted_revision_id === candidate &&
                    view.accepted_media.wav.source === 'bound_artifact' &&
                    view.accepted_media.midi.source === 'bound_artifact';
                }""",
                arg=candidate_revision,
            )
            accepted = _audition(page)
            if accepted["accepted_media"]["wav"]["sha256"] != preview_audio_sha:
                raise RuntimeError("R6 accepted bound WAV does not equal exact Preview WAV")
            if accepted["accepted_media"]["midi"]["sha256"] != preview_midi_sha:
                raise RuntimeError("R6 accepted bound MIDI does not equal exact Preview MIDI")
            history = service1.revision_history(session_id)["revisions"]
            if len(history) != 2:
                raise RuntimeError("R6 explicit Accept did not advance exactly one accepted revision")
            screenshots.append(_screenshot(page, root / "04-accepted-bound-artifacts.png"))
            page.close()

            _stop_server(server1, thread1)
            server1_stopped = True

            service2, server2, thread2, base2 = _start_server(workspace)
            try:
                reopen_page = context.new_page()
                _attach_observers(
                    reopen_page,
                    console_errors,
                    page_errors,
                    request_failures,
                    expected_media_aborts,
                )
                reopened_session = _open_project(reopen_page, base2, expect, "audition")
                reopened = _audition(reopen_page)
                if str(reopened_session["head_revision_id"]) != candidate_revision:
                    raise RuntimeError("R6 restart/reopen did not preserve accepted revision")
                if reopened["accepted_media"] != accepted["accepted_media"]:
                    raise RuntimeError("R6 restart/reopen changed exact accepted artifact identity")
                reopened_sid = str(reopened_session["session_id"])
                if _browser_media_sha256(reopen_page, reopened_sid, "audio.wav") != preview_audio_sha:
                    raise RuntimeError("R6 reopened Browser audio bytes differ from accepted Preview")
                if _browser_media_sha256(reopen_page, reopened_sid, "preview.mid") != preview_midi_sha:
                    raise RuntimeError("R6 reopened Browser MIDI bytes differ from accepted Preview")
                screenshots.append(_screenshot(reopen_page, root / "05-reopen-bound-artifacts.png"))
                reopen_page.close()
            finally:
                _stop_server(server2, thread2)
        finally:
            if not server1_stopped:
                _stop_server(server1, thread1)
            context.close()
            browser.close()

    proof = {
        "proof_version": "0",
        "real_chromium_used": True,
        "historical_r2_view_preserved": historical_r2["capabilities"]["audible_automation_validated"] is False,
        "accepted_mapping_mix_gain_only": accepted_initial["accepted_mapping"]["mapped_lane_ids"] == ["A-MIX-GAIN"],
        "unsupported_cutoff_truthfully_unmapped": accepted_initial["accepted_mapping"]["unmapped_lane_ids"] == ["B-SYNTH-CUTOFF"],
        "initial_accepted_media_fallback_truthful": accepted_initial["accepted_media"]["wav"]["source"] == "fallback_render" and accepted_initial["accepted_media"]["midi"]["source"] == "fallback_render",
        "audible_preview_visible_not_accepted": first_pending["automation_applied"] is True and first_pending["canonical"] is False,
        "browser_audio_hash_matches_pending_inspection": preview_audio_sha == first_pending["preview_wav_sha256"],
        "browser_midi_hash_matches_pending_inspection": preview_midi_sha == first_pending["preview_midi_sha256"],
        "pending_does_not_replace_accepted_media": first_preview["accepted_media"] == accepted_initial["accepted_media"],
        "discard_restores_accepted_identity": discarded["accepted_media"] == accepted_initial["accepted_media"],
        "repeat_preview_deterministic": second_pending["preview_wav_sha256"] == preview_audio_sha and second_pending["preview_midi_sha256"] == preview_midi_sha,
        "explicit_accept_advanced_exactly_once": len(history) == 2 and accepted["accepted_revision_id"] == candidate_revision,
        "accepted_wav_is_exact_preview_bound_artifact": accepted["accepted_media"]["wav"]["source"] == "bound_artifact" and accepted["accepted_media"]["wav"]["sha256"] == preview_audio_sha,
        "accepted_midi_is_exact_preview_bound_artifact": accepted["accepted_media"]["midi"]["source"] == "bound_artifact" and accepted["accepted_media"]["midi"]["sha256"] == preview_midi_sha,
        "reopen_preserves_exact_bound_artifacts": reopened["accepted_media"] == accepted["accepted_media"],
        "canonical": accepted["authority"]["canonical"],
        "browser_mutation_authorized": accepted["authority"]["browser_mutation_authorized"],
        "project_mutation_authorized": accepted["authority"]["project_mutation_authorized"],
        "reverse_promotion_authorized": accepted["authority"]["reverse_promotion_authorized"],
        "explicit_accept_required": accepted["authority"]["explicit_accept_required"],
        "browser_console_error_count": len(console_errors),
        "browser_page_error_count": len(page_errors),
        "browser_request_failure_count": len(request_failures),
        "expected_media_abort_count": len(expected_media_aborts),
    }

    required_true = [
        "real_chromium_used",
        "historical_r2_view_preserved",
        "accepted_mapping_mix_gain_only",
        "unsupported_cutoff_truthfully_unmapped",
        "initial_accepted_media_fallback_truthful",
        "audible_preview_visible_not_accepted",
        "browser_audio_hash_matches_pending_inspection",
        "browser_midi_hash_matches_pending_inspection",
        "pending_does_not_replace_accepted_media",
        "discard_restores_accepted_identity",
        "repeat_preview_deterministic",
        "explicit_accept_advanced_exactly_once",
        "accepted_wav_is_exact_preview_bound_artifact",
        "accepted_midi_is_exact_preview_bound_artifact",
        "reopen_preserves_exact_bound_artifacts",
        "explicit_accept_required",
    ]
    failed_true = [key for key in required_true if proof[key] is not True]
    required_false = ["canonical", "browser_mutation_authorized", "project_mutation_authorized", "reverse_promotion_authorized"]
    failed_false = [key for key in required_false if proof[key] is not False]
    if failed_true or failed_false or console_errors or page_errors or request_failures:
        raise RuntimeError(
            "M7-R6 real-browser proof failed: "
            f"true={failed_true}, false={failed_false}, console={console_errors}, "
            f"page={page_errors}, requests={request_failures}"
        )

    write_canonical_json(root / "historical-r2-view.json", historical_r2)
    write_canonical_json(root / "accepted-initial.json", accepted_initial)
    write_canonical_json(root / "first-preview.json", first_preview)
    write_canonical_json(root / "discarded.json", discarded)
    write_canonical_json(root / "second-preview.json", second_preview)
    write_canonical_json(root / "accepted.json", accepted)
    write_canonical_json(root / "reopened.json", reopened)
    write_canonical_json(root / "proof.json", proof)
    write_canonical_json(root / "browser-console-errors.json", console_errors)
    write_canonical_json(root / "browser-page-errors.json", page_errors)
    write_canonical_json(root / "browser-request-failures.json", request_failures)
    write_canonical_json(root / "expected-media-aborts.json", expected_media_aborts)

    evidence_files = sorted(path for path in root.iterdir() if path.is_file())
    manifest = {
        "manifest_version": "0",
        "milestone": "M7-R6",
        "evidence_class": "REAL_BROWSER_AUDITION_LIFECYCLE_E2E_EVIDENCE",
        "accepted_revision_id": candidate_revision,
        "accepted_wav_sha256": preview_audio_sha,
        "accepted_midi_sha256": preview_midi_sha,
        "records": [artifact_record(path, root) for path in evidence_files],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return {**manifest, "proof": proof}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_suite(args.out)


if __name__ == "__main__":
    main()
