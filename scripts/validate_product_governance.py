#!/usr/bin/env python3
"""MUSICA product-goal governance contract verifier; stdlib only, read-only.

Intentional hard-fail if the plan loses explicit unsupported product blockers,
source-linked evidence or the selected next user-workflow action.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED = {
    "C01", "C02", "C03", "C04", "C05",
    "C06", "C07", "C08", "C09", "C10",
}
STATUS = {"bounded-verified", "partial-integrated", "in-progress", "not-verified"}
PRIORITY = {"P0", "P1", "P2"}
GRADES = {"E0", "E1", "E2", "E3", "E4"}


def validate(root: Path) -> dict:
    policy_path = root / "docs/PRODUCT_EXECUTION_LOOP.md"
    ledger_path = root / "governance/product_gap_ledger.json"
    report_path = root / "docs/PRODUCT_CAPABILITY_GAP_LEDGER.md"
    for path in (policy_path, ledger_path, report_path):
        if not path.is_file():
            raise ValueError(f"missing canonical goal-governance input: {path}")
    policy, report = policy_path.read_text("utf-8"), report_path.read_text("utf-8")
    data = json.loads(ledger_path.read_text("utf-8"))
    assert data.get("schema_version") == "1.0", "unsupported ledger schema"
    assert data.get("not_release_ready") is True, "cannot silently claim release readiness"
    assert data.get("evidence_grades") == ["E0", "E1", "E2", "E3", "E4"]
    assert set(data.get("status_values", [])) == STATUS, "status vocabulary drift"
    assert data.get("canonical_main_at_assessment"), "missing baseline exact HEAD"
    assert data.get("selection_rule") and data.get("next_selected_issue"), "missing next action"
    entries = data.get("gaps")
    assert isinstance(entries, list) and len(entries) >= len(EXPECTED)
    ids = [item.get("id") for item in entries]
    assert len(ids) == len(set(ids)), "duplicate capability gap"
    assert set(ids) >= EXPECTED, "missing mandatory product capability domain"
    assert "#217" in report, "next selected product issue not documented"
    assert str(data["next_selected_issue"]) in report, "active issue not in human report"
    for record in entries:
        for key in ("id", "domain", "priority", "status", "grade", "evidence", "unproven", "next_issue"):
            assert record.get(key), f"{record.get('id')}: missing {key}"
        assert record["priority"] in PRIORITY, record["id"]
        assert record["status"] in STATUS, record["id"]
        assert record["grade"] in GRADES, record["id"]
        assert isinstance(record["next_issue"], int) and record["next_issue"] > 0
        assert record["id"] in report, f"{record['id']}: human ledger out of sync"
        if record["status"] == "not-verified":
            assert record["grade"] not in {"E3", "E4"}, "unsupported human/release proof"
    for term in (
        "OBSERVE", "GAP", "PRIORITIZE", "PLAN", "EXECUTE",
        "VALIDATE", "IMPROVE", "RELEASE/ROLLBACK", "NEXT", "expected-head",
        "explicit", "Preview", "rollback",
    ):
        assert term.lower() in policy.lower(), f"missing loop or safeguard: {term}"
    assert "60/60" in report, "current implementation baseline was dropped"
    return {
        "schema_version": data["schema_version"],
        "capability_domains": len(entries),
        "unverified_or_partial": sum(x["status"] != "bounded-verified" for x in entries),
        "next_selected_issue": data["next_selected_issue"],
        "commercial_release_ready": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(validate(args.root.resolve()), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
