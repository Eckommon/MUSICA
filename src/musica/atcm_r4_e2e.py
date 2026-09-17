"""ATCM-R4 restart/reopen native-audio lifecycle evidence.

This evidence deliberately crosses a deterministic Project Bundle export/import boundary,
then starts a fresh Studio service and a fresh Chromium session. Runtime/browser Preview
state is never serialized and therefore cannot become accepted authority across restart.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .atcm_r3_e2e import (
    _browser_state,
    _open,
    _prepare_project,
    _record_request_failure,
    _source,
    _start,
    _stop,
)
from .audio_edit import accept_audio_edit_preview
from .audio_mixer_edit import build_audio_mixer_edit_preview
from .contracts import ContractError
from .evidence import write_canonical_json
from .native_mixer import render_native_mix
from .project import MusicaProject, ProjectIntegrityError


def _mixer_candidate(parent: dict[str, Any], candidate_id: str, *, gain_db: float, pan: float) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_audio_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "atcm-r4-e2e"},
        "reason": f"ATCM-R4 lifecycle {candidate_id}",
        "operations": [
            {
                "operation_id": f"{candidate_id}-MIX",
                "op": "SET_TRACK_MIXER",
                "target": {"track_id": "AT-R3-E2E"},
                "mixer": {"gain_db": gain_db, "pan": pan, "mute": False, "solo": False},
            }
        ],
        "preview_only": True,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("ATCM-R4 requires .[dev,e2e] and Playwright Chromium") from exc

    out = Path(out_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    source_workspace = out / "source-workspace"
    source_workspace.mkdir()
    project, accepted, asset = _prepare_project(source_workspace)

    accepted_mixer_preview = build_audio_mixer_edit_preview(
        project,
        accepted,
        _mixer_candidate(accepted, "R4-ACCEPTED-MIXER", gain_db=-6.0, pan=0.5),
    )
    if not accepted_mixer_preview.ready:
        raise RuntimeError("R4 accepted mixer fixture was blocked")
    accepted_record = accept_audio_edit_preview(project, accepted_mixer_preview)
    accepted_head = str(accepted_record["revision_id"])
    accepted_blueprint = project.read_revision(accepted_head)
    accepted_render = render_native_mix(project, accepted_head, mix_sample_rate_hz=8000)
    accepted_integrity = project.verify_integrity()

    console_errors: list[str] = []
    page_errors: list[str] = []
    request_failures: list[str] = []
    screenshots: list[str] = []

    service1, server1, thread1, base1 = _start(source_workspace)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1500, "height": 1300}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        page = context.new_page()
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("requestfailed", lambda request: _record_request_failure(request, request_failures))
        try:
            initial = _open(page, base1, expect)
            if str(initial["view"]["revision_id"]) != accepted_head:
                raise RuntimeError("R4 source Browser did not project accepted HEAD")
            if initial["view"]["tracks"][0]["mixer"] != {"gain_db": -6.0, "pan": 0.5, "mute": False, "solo": False}:
                raise RuntimeError("R4 source Browser mixer projection mismatch")
            initial_audition = initial["view"]["accepted_audition"]
            if initial_audition["mix_plan_sha256"] != accepted_render.plan["mix_plan_sha256"]:
                raise RuntimeError("R4 source Browser mix-plan binding mismatch")
            if initial_audition["wav_sha256"] != accepted_render.wav_sha256:
                raise RuntimeError("R4 source Browser WAV binding mismatch")

            shot = out / "01-source-accepted.png"
            page.screenshot(path=str(shot), full_page=True)
            screenshots.append(shot.name)

            track = page.locator('[data-track-id="AT-R3-E2E"]')
            track.locator('[data-field="track-gain"]').fill("-3")
            track.locator('[data-field="track-pan"]').fill("-0.25")
            track.locator('[data-action="preview-mixer"]').click()
            expect(page.locator("#r3AudioAuthorityBadge")).to_have_text("PREVIEW · NOT ACCEPTED")
            page.wait_for_function("() => window.MUSICA_NATIVE_AUDIO.state.view && window.MUSICA_NATIVE_AUDIO.state.view.preview !== null")
            pending = _browser_state(page)
            if str(pending["view"]["revision_id"]) != accepted_head:
                raise RuntimeError("R4 pending Preview changed accepted Browser revision")
            session1 = service1._get_session(next(iter(service1._sessions)))
            if session1.project.head_revision_id() != accepted_head:
                raise RuntimeError("R4 pending Preview advanced accepted project HEAD")

            shot = out / "02-pending-preview-before-restart.png"
            page.screenshot(path=str(shot), full_page=True)
            screenshots.append(shot.name)

            archive_path = out / "native-r4.musica.zip"
            project.export_to(archive_path)
        finally:
            context.close()
            browser.close()
    _stop(server1, thread1)

    archive_sha256 = _sha256(archive_path)
    reopened_workspace = out / "reopened-workspace"
    reopened_workspace.mkdir()
    reopened = MusicaProject.import_from(archive_path, reopened_workspace / "native.musica")
    reopened_integrity = reopened.verify_integrity()
    reopened_head = reopened.head_revision_id()
    if reopened_head != accepted_head:
        raise RuntimeError("R4 import/reopen changed accepted HEAD")
    reopened_blueprint = reopened.read_revision(reopened_head)
    if reopened_blueprint != accepted_blueprint:
        raise RuntimeError("R4 import/reopen changed accepted Blueprint bytes/structure")
    reopened_render = render_native_mix(reopened, reopened_head, mix_sample_rate_hz=8000)
    if reopened_render.plan != accepted_render.plan:
        raise RuntimeError("R4 reopened native mix plan changed")
    if reopened_render.wav_bytes != accepted_render.wav_bytes:
        raise RuntimeError("R4 reopened native WAV changed")

    service2, server2, thread2, base2 = _start(reopened_workspace)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1500, "height": 1300}, reduced_motion="reduce")
        context.set_default_timeout(30_000)
        page = context.new_page()
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("requestfailed", lambda request: _record_request_failure(request, request_failures))
        try:
            fresh = _open(page, base2, expect)
            if str(fresh["view"]["revision_id"]) != accepted_head:
                raise RuntimeError("R4 fresh Browser did not reopen exact accepted HEAD")
            if fresh["view"].get("preview") is not None:
                raise RuntimeError("R4 fresh Browser resurrected non-canonical Preview state")
            if fresh["lastSubmittedCandidate"] is not None or fresh["lastAuthorityResult"] is not None:
                raise RuntimeError("R4 fresh Browser inherited prior runtime authority state")
            if fresh["view"]["tracks"][0]["mixer"] != {"gain_db": -6.0, "pan": 0.5, "mute": False, "solo": False}:
                raise RuntimeError("R4 fresh Browser did not restore accepted mixer state")
            audition = fresh["view"]["accepted_audition"]
            if audition["mix_plan_sha256"] != accepted_render.plan["mix_plan_sha256"]:
                raise RuntimeError("R4 fresh Browser mix-plan hash changed after restart/import")
            if audition["wav_sha256"] != accepted_render.wav_sha256:
                raise RuntimeError("R4 fresh Browser WAV hash changed after restart/import")
            shot = out / "03-fresh-reopened-accepted.png"
            page.screenshot(path=str(shot), full_page=True)
            screenshots.append(shot.name)
        finally:
            context.close()
            browser.close()
    _stop(server2, thread2)

    bypass_candidate = copy.deepcopy(reopened_blueprint)
    bypass_candidate["project"]["parent_revision_id"] = accepted_head
    bypass_candidate["project"]["revision_id"] = accepted_head + "-forged-bypass"
    bypass_candidate["materials"]["audio"]["tracks"][0]["mixer"]["gain_db"] = -2.0
    bypass_blocked = False
    try:
        reopened.commit_revision(bypass_candidate)
    except ContractError:
        bypass_blocked = True
    if not bypass_blocked:
        raise RuntimeError("R4 reopened project allowed generic native-audio commit bypass")

    corrupt_root = out / "corrupt-reopened.musica"
    corrupt_project = MusicaProject.import_from(archive_path, corrupt_root)
    corrupt_object = corrupt_project._object_path(str(asset["object_sha256"]))
    corrupt_object.write_bytes(corrupt_object.read_bytes() + b"R4-CORRUPTION")
    corruption_blocked = False
    try:
        corrupt_project.verify_integrity()
    except (ProjectIntegrityError, ContractError):
        corruption_blocked = True
    if not corruption_blocked:
        raise RuntimeError("R4 corrupted persisted audio object did not fail closed")

    if console_errors or page_errors or request_failures:
        raise RuntimeError(
            f"R4 Browser errors: console={console_errors}, page={page_errors}, requests={request_failures}"
        )

    proof = {
        "evidence_version": "0",
        "milestone": "ATCM-R4",
        "project_id": "PRJ-ATCM-R3-E2E",
        "accepted_head": accepted_head,
        "reopened_head": reopened_head,
        "asset_id": asset["asset_id"],
        "asset_object_sha256": asset["object_sha256"],
        "archive_sha256": archive_sha256,
        "accepted_mix_plan_sha256": accepted_render.plan["mix_plan_sha256"],
        "reopened_mix_plan_sha256": reopened_render.plan["mix_plan_sha256"],
        "accepted_wav_sha256": accepted_render.wav_sha256,
        "reopened_wav_sha256": reopened_render.wav_sha256,
        "accepted_blueprint_equal_after_import": reopened_blueprint == accepted_blueprint,
        "project_integrity_before_export": accepted_integrity["status"] == "PASS",
        "project_integrity_after_import": reopened_integrity["status"] == "PASS",
        "pending_preview_head_unchanged": True,
        "pending_preview_not_promoted_across_restart": True,
        "fresh_browser_runtime_authority_state_empty": True,
        "fresh_browser_mixer_state_exact": True,
        "fresh_browser_mix_hashes_exact": True,
        "generic_commit_bypass_after_reopen_blocked": bypass_blocked,
        "corrupt_persisted_audio_fails_closed": corruption_blocked,
        "rendered_audio_is_canonical": False,
        "browser_state_is_canonical": False,
        "runtime_preview_is_canonical": False,
        "recording_claimed": False,
        "realtime_device_engine_claimed": False,
        "plugin_hosting_claimed": False,
        "screenshots": screenshots,
        "console_error_count": len(console_errors),
        "page_error_count": len(page_errors),
        "request_failure_count": len(request_failures),
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
