from __future__ import annotations

import os
from pathlib import Path

from musica.m6_r3_e2e import run_suite


def test_m6_r3_real_browser_exact_note_e2e(tmp_path: Path) -> None:
    configured = os.environ.get("MUSICA_M6_R3_E2E_OUT")
    out = Path(configured) if configured else tmp_path / "m6-r3-real-browser-note-e2e"
    manifest = run_suite(out)
    proof = manifest["proof"]

    assert manifest["evidence_class"] == "REAL_BROWSER_EXACT_NOTE_E2E_EVIDENCE"
    assert proof["real_chromium_used"] is True
    assert proof["exact_note_project_opened_in_real_browser"] is True
    assert proof["browser_source_bound_to_project_revision_blueprint_hash"] is True
    assert proof["all_six_operations_browser_exercised"] is True
    assert proof["accepted_ref_unchanged_before_accept"] is True
    assert proof["preview_not_accepted_visible"] is True
    assert proof["explicit_accept_advanced_once_to_candidate"] is True
    assert proof["discard_preserved_accepted_ref"] is True
    assert proof["accepted_repitch_preserved"] is True
    assert proof["accepted_state_survives_restart_reopen"] is True
    assert proof["hard_lock_blocked"] is True
    assert proof["hard_lock_rule_context_visible"] is True
    assert proof["hard_lock_preview_installed"] is False
    assert proof["stale_source_blocked"] is True
    assert proof["stale_preview_installed"] is False
    assert proof["stale_response_rebound_to_current_accepted_source"] is True
    assert proof["legacy_reports_exact_editing_unavailable"] is True
    assert proof["legacy_has_no_fabricated_notes"] is True
    assert proof["browser_project_mutation_authorized"] is False
    assert proof["music_ir_mutation_authorized"] is False
    assert proof["external_provider_network_required"] is False
    assert proof["browser_console_error_count"] == 0
    assert proof["browser_page_error_count"] == 0
