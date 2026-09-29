from __future__ import annotations

import os
from pathlib import Path

from musica.rtio_r3_e2e import run_suite


def test_rtio_r3_real_browser_runtime_inspection_restart_reopen(tmp_path: Path) -> None:
    from playwright.sync_api import expect

    expect.set_options(timeout=30_000)
    configured = os.environ.get("MUSICA_RTIO_R3_E2E_OUT")
    out = Path(configured) if configured else tmp_path / "rtio-r3-real-browser"
    manifest = run_suite(out)
    proof = manifest["proof"]

    assert manifest["milestone"] == "RTIO-R3"
    assert proof["real_chromium_used"] is True
    assert proof["runtime_bound_to_exact_accepted_revision"] is True
    assert proof["runtime_bound_to_exact_realtime_plan"] is True
    assert proof["exact_frame_zero_visible"] is True
    assert proof["runtime_state_labeled_noncanonical"] is True
    assert proof["browser_project_mutation_authorized"] is False
    assert proof["configured_latency_provenance_truthful"] is True
    assert proof["wall_clock_guarantee_claimed"] is False
    assert proof["runtime_play_step_stop_seek_head_unchanged"] is True
    assert proof["exact_seek_frame_visible"] is True
    assert proof["unknown_runtime_blocked"] is True
    assert proof["accepted_head_advance_makes_old_runtime_stale"] is True
    assert proof["restart_reopen_revision_exact"] is True
    assert proof["restart_reopen_realtime_plan_exact"] is True
    assert proof["restart_reopen_source_binding_exact"] is True
    assert proof["runtime_playhead_not_persisted"] is True
    assert proof["runtime_metrics_not_persisted"] is True
    assert proof["restart_reopen_transport_events_exact"] is True
    assert proof["restart_reopen_callback_transactions_exact"] is True
    assert proof["restart_reopen_sink_exact"] is True
    assert proof["restart_reopen_transport_report_exact"] is True
    assert proof["browser_console_error_count"] == 0, proof["unexpected_console_errors"]
    assert proof["browser_page_error_count"] == 0
    assert proof["browser_request_failure_count"] == 0, proof["request_failures"]
    assert proof["unexpected_http_error_count"] == 0, proof["unexpected_http_errors"]
