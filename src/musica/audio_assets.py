"""Immutable native-audio project assets for ATCM-R0.

Source bytes reuse the M2 SHA-256 content-addressed object store. The project-side
asset descriptor is deterministic and derived only from the exact WAV bytes, while an
audit event binds the descriptor SHA to the import operation. Import alone is a project
resource operation; it does not create or accept a creative Blueprint revision.
"""

from __future__ import annotations

import hashlib
import json
import re
import wave
from io import BytesIO
from pathlib import Path
from typing import Any

from .contracts import ContractError, validate_contract
from .project import (
    MusicaProject,
    ProjectIntegrityError,
    _atomic_write,
    _json_bytes,
    _sha256_bytes,
)

_ASSET_ID = re.compile(r"^sha256:([0-9a-f]{64})$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _asset_digest(asset_id: str) -> str:
    match = _ASSET_ID.fullmatch(str(asset_id))
    if match is None:
        raise ContractError(f"invalid audio asset_id: {asset_id!r}")
    return match.group(1)


def _descriptor_root(project: MusicaProject) -> Path:
    return project.root / "assets" / "audio" / "sha256"


def _descriptor_path(project: MusicaProject, digest: str) -> Path:
    if _DIGEST.fullmatch(digest) is None:
        raise ContractError(f"invalid audio asset digest: {digest!r}")
    return _descriptor_root(project) / f"{digest}.json"


def _inspect_wav(data: bytes) -> dict[str, Any]:
    try:
        with wave.open(BytesIO(data), "rb") as reader:
            channels = int(reader.getnchannels())
            sample_width = int(reader.getsampwidth())
            sample_rate = int(reader.getframerate())
            frame_count = int(reader.getnframes())
            compression = str(reader.getcomptype())
            payload = reader.readframes(frame_count)
    except (wave.Error, EOFError, OSError) as exc:
        raise ContractError("audio asset must be a readable RIFF/WAVE file") from exc

    if compression != "NONE":
        raise ContractError("ATCM-R0 supports only uncompressed PCM WAV")
    if channels not in {1, 2}:
        raise ContractError("ATCM-R0 supports only mono or stereo WAV")
    if sample_width not in {1, 2, 3, 4}:
        raise ContractError("ATCM-R0 supports PCM sample widths of 1, 2, 3, or 4 bytes")
    if sample_rate < 8000 or sample_rate > 192000:
        raise ContractError("ATCM-R0 WAV sample rate must be between 8000 and 192000 Hz")
    if frame_count <= 0:
        raise ContractError("ATCM-R0 WAV must contain at least one audio frame")

    expected_payload_bytes = frame_count * channels * sample_width
    if len(payload) != expected_payload_bytes:
        raise ContractError("ATCM-R0 WAV frame payload is truncated or inconsistent")

    return {
        "container": "wav",
        "codec": "pcm_integer",
        "channels": channels,
        "sample_rate_hz": sample_rate,
        "sample_width_bytes": sample_width,
        "frame_count": frame_count,
        "duration_seconds": frame_count / sample_rate,
    }


def _descriptor_for_bytes(data: bytes) -> dict[str, Any]:
    digest = _sha256_bytes(data)
    descriptor = {
        "asset_version": "0",
        "asset_id": f"sha256:{digest}",
        "media_type": "audio/wav",
        "object_sha256": digest,
        "size_bytes": len(data),
        "format": _inspect_wav(data),
    }
    validate_contract(descriptor, "audio-asset-v0.schema.json")
    return descriptor


def _read_descriptor_file(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectIntegrityError(f"cannot read audio asset descriptor: {path}") from exc
    if not isinstance(value, dict):
        raise ProjectIntegrityError(f"audio asset descriptor must be an object: {path}")
    try:
        validate_contract(value, "audio-asset-v0.schema.json")
    except ContractError as exc:
        raise ProjectIntegrityError(f"invalid audio asset descriptor {path.name}: {exc}") from exc
    return value


def _require_import_audit(
    project: MusicaProject,
    *,
    asset_id: str,
    object_sha256: str,
    descriptor_sha256: str,
) -> None:
    for event in project._audit_events():
        if event.get("event_type") != "import_audio_asset":
            continue
        payload = event.get("payload", {})
        if (
            payload.get("asset_id") == asset_id
            and payload.get("object_sha256") == object_sha256
            and payload.get("descriptor_sha256") == descriptor_sha256
        ):
            return
    raise ProjectIntegrityError(f"audio asset lacks matching import audit binding: {asset_id}")


def read_audio_asset(project: MusicaProject, asset_id: str) -> dict[str, Any]:
    """Read and fully integrity-check one immutable audio asset descriptor."""

    digest = _asset_digest(asset_id)
    descriptor_path = _descriptor_path(project, digest)
    if not descriptor_path.is_file():
        raise ProjectIntegrityError(f"unknown or missing audio asset descriptor: {asset_id}")

    descriptor = _read_descriptor_file(descriptor_path)
    if descriptor["asset_id"] != asset_id:
        raise ProjectIntegrityError(f"audio asset descriptor/id mismatch: {asset_id}")
    if descriptor["object_sha256"] != digest:
        raise ProjectIntegrityError(f"audio asset descriptor/object mismatch: {asset_id}")

    object_path = project._object_path(digest)
    if not object_path.is_file():
        raise ProjectIntegrityError(f"missing audio asset object: {asset_id}")
    data = object_path.read_bytes()
    actual_digest = _sha256_bytes(data)
    if actual_digest != digest:
        raise ProjectIntegrityError(f"audio asset object hash mismatch: {asset_id}")
    if len(data) != int(descriptor["size_bytes"]):
        raise ProjectIntegrityError(f"audio asset object size mismatch: {asset_id}")

    try:
        actual_format = _inspect_wav(data)
    except ContractError as exc:
        raise ProjectIntegrityError(f"audio asset WAV integrity failed: {asset_id}: {exc}") from exc
    if actual_format != descriptor["format"]:
        raise ProjectIntegrityError(f"audio asset format metadata mismatch: {asset_id}")

    descriptor_bytes = _json_bytes(descriptor)
    descriptor_sha = _sha256_bytes(descriptor_bytes)
    descriptor_object = project._object_path(descriptor_sha)
    if not descriptor_object.is_file() or descriptor_object.read_bytes() != descriptor_bytes:
        raise ProjectIntegrityError(f"missing/corrupt audio asset descriptor object: {asset_id}")

    _require_import_audit(
        project,
        asset_id=asset_id,
        object_sha256=digest,
        descriptor_sha256=descriptor_sha,
    )
    return descriptor


def audio_asset_bytes(project: MusicaProject, asset_id: str) -> bytes:
    """Return exact source bytes only after descriptor/object integrity succeeds."""

    descriptor = read_audio_asset(project, asset_id)
    return project._object_path(str(descriptor["object_sha256"])).read_bytes()


def import_audio_asset(project: MusicaProject, source_path: str | Path) -> dict[str, Any]:
    """Import one bounded WAV source into the existing project CAS.

    The internal asset path is derived only from SHA-256; an untrusted source filename
    is never used as a project-relative path. Re-importing identical bytes is idempotent.
    """

    source = Path(source_path)
    if not source.is_file():
        raise ContractError(f"audio asset source does not exist: {source}")
    data = source.read_bytes()
    expected = _descriptor_for_bytes(data)
    digest = str(expected["object_sha256"])
    asset_id = str(expected["asset_id"])
    descriptor_path = _descriptor_path(project, digest)

    if descriptor_path.exists():
        existing = read_audio_asset(project, asset_id)
        if existing != expected:
            raise ProjectIntegrityError(f"immutable audio asset descriptor changed: {asset_id}")
        if audio_asset_bytes(project, asset_id) != data:
            raise ProjectIntegrityError(f"immutable audio asset bytes changed: {asset_id}")
        return existing

    # Validate all existing audio assets before adding another resource. This prevents
    # an import operation from silently healing or bypassing an already-corrupt store.
    verify_audio_assets(project)

    stored_digest = project._store_bytes(data)
    if stored_digest != digest:
        raise ProjectIntegrityError("audio asset CAS returned an unexpected digest")
    descriptor_sha = project._store_json(expected)
    _atomic_write(descriptor_path, _json_bytes(expected))
    project._append_audit(
        "import_audio_asset",
        asset_id=asset_id,
        object_sha256=digest,
        descriptor_sha256=descriptor_sha,
    )
    return read_audio_asset(project, asset_id)


def list_audio_assets(project: MusicaProject) -> list[dict[str, Any]]:
    """Return all valid project audio assets in deterministic asset-id order."""

    root = _descriptor_root(project)
    if not root.exists():
        return []
    descriptors: list[dict[str, Any]] = []
    for path in sorted(root.iterdir(), key=lambda item: item.name):
        if not path.is_file() or not path.name.endswith(".json"):
            raise ProjectIntegrityError(f"unexpected audio asset descriptor entry: {path.name}")
        digest = path.name[:-5]
        if _DIGEST.fullmatch(digest) is None:
            raise ProjectIntegrityError(f"invalid audio asset descriptor filename: {path.name}")
        descriptors.append(read_audio_asset(project, f"sha256:{digest}"))
    return descriptors


def verify_audio_assets(project: MusicaProject) -> dict[str, Any]:
    """Fail closed if any native audio descriptor, object, or audit binding is corrupt."""

    descriptors = list_audio_assets(project)
    return {
        "status": "PASS",
        "audio_asset_count": len(descriptors),
        "asset_ids": [str(item["asset_id"]) for item in descriptors],
    }
