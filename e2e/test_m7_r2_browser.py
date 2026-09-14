from __future__ import annotations

import os
from pathlib import Path

from musica.m7_r2_browser_driver import run_suite


def test_m7_r2_real_browser_automation_e2e(tmp_path: Path) -> None:
    configured = os.environ.get("MUSICA_M7_R2_E2E_OUT")
    out = Path(configured) if configured else tmp_path / "m7-r2-real-browser-automation-e2e"
    manifest = run_suite(out)
    proof = manifest["proof"]

    assert manifest["evidence_class"] == "REAL_BROWSER_AUTOMATION_E2E_EVIDENCE"
    assert proof["real_chromium_used"] is True
    assert proof["automation_project_opened_in_real_browser"] is True
    assert proof["browser_source_bound_to_project_revision_blueprint_and_material_hash"] is True
    assert proof["stable_lane_point_dom_identity_present"] is True
    assert proof["all_five_operations_browser_exercised"] is True
    assert proof["accepted_ref_unchanged_before_accept"] is True
    assert proof["preview_not_accepted_visible"] is True
    assert proof["explicit_accept_advanced_once_to_candidate"] is True
    assert proof["discard_preserved_accepted_ref"] is True
    assert proof["accepted_value_preserved"] is True
    assert proof["accepted_state_survives_restart_reopen"] is True
    assert proof["hard_exact_lock_blocked"] is True
    assert proof["hard_exact_lock_rule_context_visible"] is True
    assert proof["hard_exact_preview_installed"] is False
    assert proof["hard_presence_lock_blocked"] is True
    assert proof["hard_presence_rule_context_visible"] is True
    assert proof["hard_presence_preview_installed"] is False
    assert proof["stale_source_blocked"] is True
    assert proof["stale_preview_installed"] is False
    assert proof["stale_response_rebound_to_current_accepted_source"] is True
    assert proof["legacy_reports_automation_unavailable"] is True
    assert proof["legacy_has_no_fabricated_lanes"] is True
    assert proof["browser_project_mutation_authorized"] is False
    assert proof["music_ir_mutation_authorized"] is False
    assert proof["audible_automation_validated"] is False
    assert proof["external_provider_network_required"] is False
    assert proof["browser_console_error_count"] == 0
    assert proof["browser_page_error_count"] == 0
