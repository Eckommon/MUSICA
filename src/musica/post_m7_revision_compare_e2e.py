"""Generate real-Chromium evidence for the accepted-revision A/B Compare surface."""

from __future__ import annotations

import argparse
import hashlib
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


def _load_blueprint() -> dict[str, Any]:
    value = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    value["project"]["project_id"] = "PRJ-POST-M7-COMPARE-BROWSER"
    value["project"]["revision_id"] = "rev-post-m7-compare-r1"
    value["project"]["parent_revision_id"] = None
    validate_contract(value, "music-blueprint-v0.schema.json")
    return value


def _prepare_project(workspace: Path) -> tuple[str, str]:
    project = create_project(workspace / "compare.musica", _load_blueprint())
    root_revision = project.head_revision_id()
    service = StudioService(workspace)
    service.open_project_session(
        project_slug="compare",
        session_id="compare-prep",
        provider_mode="fixture",
    )
    preview = service.preview_semantic_edit(
        "compare-prep",
        name="tension",
        operation="increase",
        value=0.18,
        scope_kind="final_section",
    )
    child_revision = str(preview["preview"]["candidate_revision_id"])
    accepted = service.accept_preview("compare-prep")
    if accepted["revision_record"]["revision_id"] != child_revision:
        raise RuntimeError("Compare Browser preparation accepted an unexpected revision")
    if project.head_revision_id() != child_revision:
        raise RuntimeError("Compare Browser preparation did not advance to the child revision")
    service.close_session("compare-prep")
    project.verify_integrity()
    return root_revision, child_revision


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
        raise RuntimeError("Compare Studio HTTP server thread did not stop cleanly")


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
            and "/revisions/" in request.url
            and "/media/audio.wav" in request.url
            and "ERR_ABORTED" in failure
        ):
            expected_media_aborts.append(record)
            return
        request_failures.append(record)

    page.on("requestfailed", on_request_failed)


def _open_project(page, base: str, expect) -> dict[str, Any]:
    page.goto(base + "/", wait_until="domcontentloaded")
    expect(page.locator("#connectionBadge")).to_contain_text("READY")
    page.locator("#openProjectSlug").fill("compare")
    page.locator("#openForm button[type=submit]").click()
    expect(page.locator("#activeProject")).to_be_visible()
    expect(page.locator("#projectStateBadge")).to_have_text("ACCEPTED")
    page.locator('button[data-tab="inspect"]').click()
    expect(page.locator("#panel-inspect")).to_be_visible()
    expect(page.locator("#revisionCompareCard")).to_be_visible()
    page.wait_for_function(
        """() => {
          const a = document.querySelector('#revisionCompareA');
          const b = document.querySelector('#revisionCompareB');
          return a && b && a.options.length >= 2 && b.options.length >= 2;
        }"""
    )
    raw = page.locator("#jsonView").text_content() or "{}"
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise RuntimeError("Compare Browser session JSON is unavailable")
    return value


def _browser_compare(page, expect, root_revision: str, child_revision: str) -> dict[str, Any]:
    page.locator("#revisionCompareA").select_option(root_revision)
    page.locator("#revisionCompareB").select_option(child_revision)
    page.locator("#revisionCompareRun").click()
    expect(page.locator("#revisionCompareResult")).to_be_visible()
    expect(page.locator("#revisionCompareBadge")).to_have_text("READ ONLY · NO RANKING")
    expect(page.locator("#revisionCompareALabel")).to_have_text(root_revision)
    expect(page.locator("#revisionCompareBLabel")).to_have_text(child_revision)
    expect(page.locator("#revisionCompareHead")).to_contain_text("head_unchanged=true")
    expect(page.locator("#revisionCompareStatus")).to_contain_text("without moving HEAD")
    page.wait_for_function(
        """({rootRevision, childRevision}) => {
          const a = document.querySelector('#revisionCompareAudioA');
          const b = document.querySelector('#revisionCompareAudioB');
          return a && b && a.controls && b.controls &&
            a.src.includes(`/revisions/${encodeURIComponent(rootRevision)}/media/audio.wav`) &&
            b.src.includes(`/revisions/${encodeURIComponent(childRevision)}/media/audio.wav`);
        }""",
        arg={"rootRevision": root_revision, "childRevision": child_revision},
    )
    value = page.evaluate(
        """async ({rootRevision, childRevision}) => {
          const response = await fetch(`/v0/sessions/${encodeURIComponent(window.MUSICA_AUTOMATION.state.sessionId)}/compare/${encodeURIComponent(rootRevision)}/${encodeURIComponent(childRevision)}`);
          if (!response.ok) throw new Error(`compare fetch failed: ${response.status}`);
          const payload = await response.json();
          return payload.data;
        }""",
        {"rootRevision": root_revision, "childRevision": child_revision},
    )
    if not isinstance(value, dict):
        raise RuntimeError("Compare Browser endpoint did not return a comparison object")
    return value


def _browser_revision_media_sha256(page, revision_id: str, filename: str) -> str:
    value = page.evaluate(
        """async ({revisionId, filename}) => {
          const sessionId = window.MUSICA_AUTOMATION.state.sessionId;
          const response = await fetch(`/v0/sessions/${encodeURIComponent(sessionId)}/revisions/${encodeURIComponent(revisionId)}/media/${filename}`);
          if (!response.ok) throw new Error(`revision media fetch failed: ${response.status}`);
          const bytes = await response.arrayBuffer();
          const digest = await crypto.subtle.digest('SHA-256', bytes);
          return Array.from(new Uint8Array(digest)).map((item) => item.toString(16).padStart(2, '0')).join('');
        }""",
        {"revisionId": revision_id, "filename": filename},
    )
    if not isinstance(value, str) or len(value) != 64:
        raise RuntimeError("Compare Browser failed to calculate exact revision-media SHA-256")
    return value


def _screenshot(page, path: Path) -> Path:
    page.screenshot(path=str(path), full_page=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Compare Browser screenshot was not created: {path}")
    return path


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Compare evidence requires browser dependencies: install with .[dev,e2e]") from exc

    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    workspace = root / "workspace"
    workspace.mkdir()
    root_revision, child_revision = _prepare_project(workspace)

    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []
    expected_media_aborts: list[str] = []
    screenshots: list[Path] = []

    service, server, thread, base = _start_server(workspace)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1500, "height": 1300}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        try:
            page = context.new_page()
            _attach_observers(page, console_errors, page_errors, request_failures, expected_media_aborts)
            opened = _open_project(page, base, expect)
            session_id = str(opened["session_id"])
            head_before = service._get_session(session_id).project.head_revision_id()
            if head_before != child_revision:
                raise RuntimeError("Compare Browser opened a different canonical HEAD")

            first = _browser_compare(page, expect, root_revision, child_revision)
            validate_contract(first, "studio-revision-compare-v0.schema.json")
            if first["revision_a"]["media"]["wav"]["source"] != "deterministic_fallback":
                raise RuntimeError("Compare Browser root revision did not report deterministic fallback media")
            if first["revision_b"]["media"]["wav"]["source"] != "bound_artifact":
                raise RuntimeError("Compare Browser child revision did not report bound artifact media")
            if not first["diff"]:
                raise RuntimeError("Compare Browser A_TO_B diff unexpectedly contains no changes")

            root_wav_sha = _browser_revision_media_sha256(page, root_revision, "audio.wav")
            child_wav_sha = _browser_revision_media_sha256(page, child_revision, "audio.wav")
            root_midi_sha = _browser_revision_media_sha256(page, root_revision, "preview.mid")
            child_midi_sha = _browser_revision_media_sha256(page, child_revision, "preview.mid")
            if root_wav_sha != first["revision_a"]["media"]["wav"]["sha256"]:
                raise RuntimeError("Compare Browser A WAV bytes do not match comparison provenance")
            if child_wav_sha != first["revision_b"]["media"]["wav"]["sha256"]:
                raise RuntimeError("Compare Browser B WAV bytes do not match comparison provenance")
            if root_midi_sha != first["revision_a"]["media"]["midi"]["sha256"]:
                raise RuntimeError("Compare Browser A MIDI bytes do not match comparison provenance")
            if child_midi_sha != first["revision_b"]["media"]["midi"]["sha256"]:
                raise RuntimeError("Compare Browser B MIDI bytes do not match comparison provenance")
            if service._get_session(session_id).project.head_revision_id() != head_before:
                raise RuntimeError("Compare Browser media/audition changed canonical HEAD")
            screenshots.append(_screenshot(page, root / "01-accepted-revision-ab-compare.png"))

            page.reload(wait_until="domcontentloaded")
            reopened = _open_project(page, base, expect)
            reopened_sid = str(reopened["session_id"])
            reopened_head_before = service._get_session(reopened_sid).project.head_revision_id()
            second = _browser_compare(page, expect, root_revision, child_revision)
            if second["diff"] != first["diff"]:
                raise RuntimeError("Compare Browser refresh/reopen changed deterministic structured diff")
            if second["revision_a"]["media"] != first["revision_a"]["media"]:
                raise RuntimeError("Compare Browser refresh/reopen changed revision A media provenance")
            if second["revision_b"]["media"] != first["revision_b"]["media"]:
                raise RuntimeError("Compare Browser refresh/reopen changed revision B media provenance")
            if service._get_session(reopened_sid).project.head_revision_id() != reopened_head_before:
                raise RuntimeError("Compare Browser refresh/reopen comparison changed canonical HEAD")
            screenshots.append(_screenshot(page, root / "02-refresh-reopen-compare.png"))
            page.close()
        finally:
            context.close()
            browser.close()
            _stop_server(server, thread)

    proof = {
        "proof_version": "0",
        "real_chromium_used": True,
        "two_accepted_revisions_visible": True,
        "explicit_a_to_b_direction": first["direction"] == "A_TO_B",
        "structured_diff_visible": bool(first["diff"]),
        "revision_a_fallback_truthful": first["revision_a"]["media"]["wav"]["source"] == "deterministic_fallback",
        "revision_b_bound_truthful": first["revision_b"]["media"]["wav"]["source"] == "bound_artifact",
        "independent_audio_controls_bound_to_exact_revisions": True,
        "browser_a_wav_hash_matches": root_wav_sha == first["revision_a"]["media"]["wav"]["sha256"],
        "browser_b_wav_hash_matches": child_wav_sha == first["revision_b"]["media"]["wav"]["sha256"],
        "browser_a_midi_hash_matches": root_midi_sha == first["revision_a"]["media"]["midi"]["sha256"],
        "browser_b_midi_hash_matches": child_midi_sha == first["revision_b"]["media"]["midi"]["sha256"],
        "head_unchanged": first["head_unchanged"] is True and head_before == child_revision,
        "refresh_reopen_same_diff": second["diff"] == first["diff"],
        "refresh_reopen_same_media_provenance": second["revision_a"]["media"] == first["revision_a"]["media"] and second["revision_b"]["media"] == first["revision_b"]["media"],
        "canonical": first["authority"]["canonical"],
        "browser_mutation_authorized": first["authority"]["browser_mutation_authorized"],
        "project_mutation_authorized": first["authority"]["project_mutation_authorized"],
        "reverse_promotion_authorized": first["authority"]["reverse_promotion_authorized"],
        "creative_ranking_authorized": first["authority"]["creative_ranking_authorized"],
        "implicit_accept_authorized": first["authority"]["implicit_accept_authorized"],
        "browser_console_error_count": len(console_errors),
        "browser_page_error_count": len(page_errors),
        "browser_request_failure_count": len(request_failures),
        "expected_media_abort_count": len(expected_media_aborts),
    }

    required_true = [
        "real_chromium_used",
        "two_accepted_revisions_visible",
        "explicit_a_to_b_direction",
        "structured_diff_visible",
        "revision_a_fallback_truthful",
        "revision_b_bound_truthful",
        "independent_audio_controls_bound_to_exact_revisions",
        "browser_a_wav_hash_matches",
        "browser_b_wav_hash_matches",
        "browser_a_midi_hash_matches",
        "browser_b_midi_hash_matches",
        "head_unchanged",
        "refresh_reopen_same_diff",
        "refresh_reopen_same_media_provenance",
    ]
    required_false = [
        "canonical",
        "browser_mutation_authorized",
        "project_mutation_authorized",
        "reverse_promotion_authorized",
        "creative_ranking_authorized",
        "implicit_accept_authorized",
    ]
    failed_true = [key for key in required_true if proof[key] is not True]
    failed_false = [key for key in required_false if proof[key] is not False]
    if failed_true or failed_false or console_errors or page_errors or request_failures:
        raise RuntimeError(
            "Accepted revision Compare real-browser proof failed: "
            f"true={failed_true}, false={failed_false}, console={console_errors}, "
            f"page={page_errors}, requests={request_failures}"
        )

    write_canonical_json(root / "first-compare.json", first)
    write_canonical_json(root / "reopened-compare.json", second)
    write_canonical_json(root / "proof.json", proof)
    write_canonical_json(root / "browser-console-errors.json", console_errors)
    write_canonical_json(root / "browser-page-errors.json", page_errors)
    write_canonical_json(root / "browser-request-failures.json", request_failures)
    write_canonical_json(root / "expected-media-aborts.json", expected_media_aborts)

    evidence_files = sorted(path for path in root.iterdir() if path.is_file())
    manifest = {
        "manifest_version": "0",
        "milestone": "POST-M7-REVISION-COMPARE-V0",
        "evidence_class": "REAL_BROWSER_ACCEPTED_REVISION_COMPARE_E2E_EVIDENCE",
        "revision_a": root_revision,
        "revision_b": child_revision,
        "current_head_revision_id": child_revision,
        "revision_a_wav_sha256": root_wav_sha,
        "revision_b_wav_sha256": child_wav_sha,
        "revision_a_midi_sha256": root_midi_sha,
        "revision_b_midi_sha256": child_midi_sha,
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
