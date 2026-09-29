from __future__ import annotations

import os
from pathlib import Path

from musica.mram_r3_e2e import run_suite


def test_mram_r3_real_browser_routing_native_automation_reopen(tmp_path: Path) -> None:
    from playwright.sync_api import expect

    expect.set_options(timeout=30_000)
    configured = os.environ.get("MUSICA_MRAM_R3_E2E_OUT")
    out = Path(configured) if configured else tmp_path / "mram-r3-real-browser"
    manifest = run_suite(out)
    proof = manifest["proof"]

    assert manifest["milestone"] == "MRAM-R3"
    assert proof["real_chromium_used"] is True
    assert proof["stable_routing_ids_visible"] is True
    assert proof["stable_native_automation_ids_visible"] is True
    assert proof["routing_and_automation_views_bound_to_same_exact_source"] is True
    assert proof["accepted_routed_audio_hash_matches_browser_bytes"] is True
    assert proof["routing_preview_head_unchanged"] is True
    assert proof["routing_preview_exact_routed_audio_changed"] is True
    assert proof["routing_explicit_accept_advanced_once"] is True
    assert proof["native_automation_preview_head_unchanged"] is True
    assert proof["native_automation_preview_used_routed_mixer"] is True
    assert proof["native_automation_explicit_accept_advanced_once"] is True
    assert proof["unknown_id_blocked"] is True
    assert proof["stale_source_blocked"] is True
    assert proof["restart_reopen_revision_exact"] is True
    assert proof["restart_reopen_routing_hash_exact"] is True
    assert proof["restart_reopen_automation_hash_exact"] is True
    assert proof["restart_reopen_native_identities_exact"] is True
    assert proof["restart_reopen_routed_plan_exact"] is True
    assert proof["restart_reopen_routed_wav_exact"] is True
    assert proof["browser_project_mutation_authorized"] is False
    assert proof["browser_state_is_canonical"] is False
    assert proof["browser_console_error_count"] == 0, {
        "unexpected_console_errors": proof.get("unexpected_console_errors", []),
        "expected_media_aborts": proof.get("expected_media_aborts", []),
        "request_failures": proof.get("request_failures", []),
        "http_error_responses": proof.get("http_error_responses", []),
        "page_error_count": proof.get("browser_page_error_count"),
        "request_failure_count": proof.get("browser_request_failure_count"),
    }
    assert proof["browser_page_error_count"] == 0
    assert proof["browser_request_failure_count"] == 0
