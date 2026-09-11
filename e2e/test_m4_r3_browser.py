from __future__ import annotations

import os
from pathlib import Path

from musica.m4_r3_e2e import run_suite


def test_m4_r3_real_browser_e2e(tmp_path):
    configured = os.environ.get("MUSICA_E2E_OUT")
    out = Path(configured) if configured else tmp_path / "m4-r3-browser-e2e"
    manifest = run_suite(out)
    proof = manifest["proof"]

    assert manifest["evidence_class"] == "REAL_BROWSER_E2E_EVIDENCE"
    assert proof["real_chromium_used"] is True
    assert proof["project_created_via_visible_browser_controls"] is True
    assert proof["accepted_audio_browser_retrieval_valid"] is True
    assert proof["preview_not_accepted_visible"] is True
    assert proof["preview_ref_unchanged_before_accept"] is True
    assert proof["preview_candidate_differs_from_parent"] is True
    assert proof["preview_diff_count"] > 0
    assert proof["hard_lock_count"] > 0
    assert proof["preview_conflict_controls_disabled"] is True
    assert proof["explicit_accept_advanced_to_candidate"] is True
    assert proof["branch_created_and_checked_out"] is True
    assert proof["history_visible"] is True
    assert proof["export_visible_with_hash"] is True
    assert proof["code_view_read_only"] is True
    assert proof["restart_reopen_preserved_branch"] is True
    assert proof["restart_reopen_preserved_head"] is True
    assert proof["restart_reopen_integrity"] == "PASS"
    assert proof["reopened_audio_browser_retrieval_valid"] is True
    assert proof["external_provider_network_required"] is False
    assert proof["browser_console_error_count"] == 0
    assert proof["browser_page_error_count"] == 0
