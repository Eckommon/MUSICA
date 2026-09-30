from __future__ import annotations

import os
from pathlib import Path

from musica.rec_r3_e2e import run_suite


def test_rec_r3_real_browser_recording_monitor_preview_accept_restart(
    tmp_path: Path,
) -> None:
    from playwright.sync_api import expect

    expect.set_options(timeout=30_000)
    configured = os.environ.get("MUSICA_REC_R3_E2E_OUT")
    out = Path(configured) if configured else tmp_path / "rec-r3-real-browser"
    manifest = run_suite(out)
    proof = manifest["proof"]

    assert manifest["milestone"] == "REC-R3"
    assert proof["real_chromium_used"] is True
    assert proof["recording_view_bound_to_exact_accepted_revision"] is True
    assert proof["runtime_state_labeled_noncanonical"] is True
    assert proof["browser_runtime_asset_import_authorized"] is False
    assert proof["browser_runtime_audio_commit_authorized"] is False
    assert proof["clean_capture_monitor_visible"] is True
    assert proof["capture_monitor_head_unchanged"] is True
    assert proof["capture_monitor_asset_inventory_unchanged"] is True
    assert proof["finalize_preview_head_unchanged"] is True
    assert proof["finalize_preview_asset_inventory_unchanged"] is True
    assert proof["finalize_preview_audio_material_unchanged"] is True
    assert proof["explicit_accept_advanced_once"] is True
    assert proof["accepted_asset_and_clip_visible"] is True
    assert proof["stale_runtime_handle_blocked"] is True
    assert proof["dirty_capture_visibly_blocked"] is True
    assert proof["dirty_runtime_reset_head_unchanged"] is True
    assert proof["restart_reopen_revision_exact"] is True
    assert proof["restart_reopen_recording_exact"] is True
    assert proof["transient_runtime_not_persisted"] is True
    assert proof["restart_reopen_routed_plan_exact"] is True
    assert proof["restart_reopen_routed_wav_exact"] is True
    assert proof["browser_console_error_count"] == 0, proof["unexpected_console_errors"]
    assert proof["browser_page_error_count"] == 0
    assert proof["browser_request_failure_count"] == 0, proof["request_failures"]
    assert proof["unexpected_http_error_count"] == 0, proof["unexpected_http_errors"]
