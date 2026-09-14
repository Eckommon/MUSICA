"""M7-R2 real-browser evidence driver using the keyboard-accessible stable-ID table.

The automation plot is a presentation surface. Evidence deliberately selects points
through the focusable lane/point table so the tested authority path is independent of
canvas/pixel hit-testing and directly exercises the required keyboard interaction path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import m7_r2_e2e as _e2e


def _select_point_by_stable_table(page: Any, expect: Any, lane_id: str, point_id: str) -> None:
    row = page.locator(
        f'#m7AutomationLanes tr[data-lane-id="{lane_id}"][data-point-id="{point_id}"]'
    ).first
    expect(row).to_be_visible()
    row.focus()
    row.press("Enter")
    expect(page.locator("#m7SelectedPoint")).to_contain_text(point_id)
    expect(page.locator("#m7SelectedPoint")).to_contain_text(lane_id)


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    """Run the canonical M7-R2 suite with stable-ID keyboard point selection."""

    original = _e2e._select_point
    _e2e._select_point = _select_point_by_stable_table
    try:
        return _e2e.run_suite(out_dir)
    finally:
        _e2e._select_point = original
