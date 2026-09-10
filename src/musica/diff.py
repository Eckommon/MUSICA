"""Deterministic structured Blueprint diff / 결정론적 Blueprint 구조 diff."""

from __future__ import annotations

from typing import Any


def _escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def structured_diff(before: Any, after: Any, path: str = "") -> list[dict[str, Any]]:
    """Return a stable JSON-Pointer-oriented change list."""

    if type(before) is not type(after):
        return [{"op": "replace", "path": path or "/", "before": before, "after": after}]

    if isinstance(before, dict):
        changes: list[dict[str, Any]] = []
        keys = sorted(set(before) | set(after))
        for key in keys:
            child = f"{path}/{_escape(str(key))}"
            if key not in before:
                changes.append({"op": "add", "path": child, "before": None, "after": after[key]})
            elif key not in after:
                changes.append({"op": "remove", "path": child, "before": before[key], "after": None})
            else:
                changes.extend(structured_diff(before[key], after[key], child))
        return changes

    if isinstance(before, list):
        if len(before) != len(after):
            return [{"op": "replace", "path": path or "/", "before": before, "after": after}]
        changes: list[dict[str, Any]] = []
        for index, (old, new) in enumerate(zip(before, after, strict=True)):
            changes.extend(structured_diff(old, new, f"{path}/{index}"))
        return changes

    if before != after:
        return [{"op": "replace", "path": path or "/", "before": before, "after": after}]
    return []
