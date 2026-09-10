"""Deterministic evidence utilities / 결정론적 근거 유틸리티."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def write_canonical_json(path: str | Path, value: Any) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(canonical_json_bytes(value))
    return target


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(path: str | Path, base: str | Path) -> dict[str, Any]:
    target = Path(path)
    root = Path(base)
    return {
        "path": target.relative_to(root).as_posix(),
        "size_bytes": target.stat().st_size,
        "sha256": sha256_file(target),
    }
