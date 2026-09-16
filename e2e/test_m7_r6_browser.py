from __future__ import annotations

import os
from pathlib import Path

from musica.m7_r6_e2e import run_suite


def test_m7_r6_real_browser_audition_lifecycle(tmp_path: Path) -> None:
    from playwright.sync_api import expect

    expect.set_options(timeout=30_000)
    configured = os.environ.get("MUSICA_M7_R6_E2E_OUT")
    out = Path(configured) if configured else tmp_path / "m7-r6-real-browser-audition-e2e"
    manifest = run_suite(out)
    proof = manifest["proof"]

    assert manifest["evidence_class"] == "REAL_BROWSER_AUDITION_LIFECYCLE_E2E_EVIDENCE"
    assert proof["real_chromium_used"] is True
    assert proof["historical_r2_view_preserved"] is True
    assert proof["accepted_mapping_mix_gain_only"] is True
    assert proof["unsupported_cutoff_truthfully_unmapped"] is True
    assert proof["initial_accepted_media_fallback_truthful"] is True
    assert proof["audible_preview_visible_not_accepted"] is True
    assert proof["browser_audio_hash_matches_pending_inspection"] is True
    assert proof["browser_midi_hash_matches_pending_inspection"] is True
    assert proof["pending_does_not_replace_accepted_media"] is True
    assert proof["discard_restores_accepted_identity"] is True
    assert proof["repeat_preview_deterministic"] is True
    assert proof["explicit_accept_advanced_exactly_once"] is True
    assert proof["accepted_wav_is_exact_preview_bound_artifact"] is True
    assert proof["accepted_midi_is_exact_preview_bound_artifact"] is True
    assert proof["reopen_preserves_exact_bound_artifacts"] is True
    assert proof["canonical"] is False
    assert proof["browser_mutation_authorized"] is False
    assert proof["project_mutation_authorized"] is False
    assert proof["reverse_promotion_authorized"] is False
    assert proof["explicit_accept_required"] is True
    assert proof["browser_console_error_count"] == 0
    assert proof["browser_page_error_count"] == 0
    assert proof["browser_request_failure_count"] == 0
