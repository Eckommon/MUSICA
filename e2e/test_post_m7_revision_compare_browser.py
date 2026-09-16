from __future__ import annotations

import os
from pathlib import Path

from musica.post_m7_revision_compare_e2e import run_suite


def test_post_m7_accepted_revision_compare_real_browser(tmp_path: Path) -> None:
    from playwright.sync_api import expect

    expect.set_options(timeout=30_000)
    configured = os.environ.get("MUSICA_POST_M7_COMPARE_E2E_OUT")
    out = Path(configured) if configured else tmp_path / "post-m7-revision-compare-e2e"
    manifest = run_suite(out)
    proof = manifest["proof"]

    assert manifest["evidence_class"] == "REAL_BROWSER_ACCEPTED_REVISION_COMPARE_E2E_EVIDENCE"
    assert proof["real_chromium_used"] is True
    assert proof["two_accepted_revisions_visible"] is True
    assert proof["explicit_a_to_b_direction"] is True
    assert proof["structured_diff_visible"] is True
    assert proof["revision_a_fallback_truthful"] is True
    assert proof["revision_b_bound_truthful"] is True
    assert proof["independent_audio_controls_bound_to_exact_revisions"] is True
    assert proof["browser_a_wav_hash_matches"] is True
    assert proof["browser_b_wav_hash_matches"] is True
    assert proof["browser_a_midi_hash_matches"] is True
    assert proof["browser_b_midi_hash_matches"] is True
    assert proof["head_unchanged"] is True
    assert proof["refresh_reopen_same_diff"] is True
    assert proof["refresh_reopen_same_media_provenance"] is True
    assert proof["canonical"] is False
    assert proof["browser_mutation_authorized"] is False
    assert proof["project_mutation_authorized"] is False
    assert proof["reverse_promotion_authorized"] is False
    assert proof["creative_ranking_authorized"] is False
    assert proof["implicit_accept_authorized"] is False
    assert proof["browser_console_error_count"] == 0
    assert proof["browser_page_error_count"] == 0
    assert proof["browser_request_failure_count"] == 0
