"""Immutable native-audio project assets for ATCM-R0.

Source bytes reuse the M2 SHA-256 content-addressed object store. The project-side
asset descriptor is deterministic and derived only from the exact WAV bytes, while an
audit event binds the descriptor SHA to the import operation. Import alone is a project
resource operation; it does not create or accept a creative Blueprint revision.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
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


def _file_sha256(source: Path) -> str:
    h = hashlib.sha256()
    with source.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def _inspect_wav_file(source: Path) -> dict[str, Any]:
    """Validate exact source PCM frames while retaining only bounded chunks."""
    try:
        with wave.open(str(source), "rb") as reader:
            channels, width, rate = (
                int(reader.getnchannels()), int(reader.getsampwidth()),
                int(reader.getframerate()),
            )
            frame_count = int(reader.getnframes())
            compression = reader.getcomptype()
            if compression != "NONE" or channels not in {1, 2} or width not in {1, 2, 3, 4}:
                raise ContractError("staged WAV requires mono/stereo uncompressed integer PCM")
            if not 8000 <= rate <= 192000 or frame_count <= 0:
                raise ContractError("staged WAV sample rate or duration out of bounds")
            remaining = frame_count
            total = 0
            while remaining:
                requested = min(remaining, 65536)
                block = reader.readframes(requested)
                if not block or len(block) % (channels * width):
                    raise ContractError("staged WAV PCM frame payload truncated")
                frames = len(block) // (channels * width)
                remaining -= frames
                total += len(block)
            if total != frame_count * channels * width:
                raise ContractError("staged WAV PCM length mismatch")
    except (OSError, EOFError, wave.Error) as exc:
        raise ContractError("staged audio asset must be a readable RIFF/WAVE file") from exc
    return {
        "container": "wav", "codec": "pcm_integer", "channels": channels,
        "sample_rate_hz": rate, "sample_width_bytes": width,
        "frame_count": frame_count, "duration_seconds": frame_count / rate,
    }


def import_audio_asset_verified_path(
    project: MusicaProject, source: Path, *, expected_sha256: str
) -> dict[str, Any]:
    """Stream verified private staging bytes to immutable project CAS, without creative Accept.

    The source path MUST come from trusted BoundedWavStaging. Never expose this
    method as a user-provided HTTP filesystem path.
    """
    source = Path(source)
    if not source.is_file() or source.is_symlink():
        raise ContractError("verified staging file is unavailable")
    if _DIGEST.fullmatch(expected_sha256) is None:
        raise ContractError("invalid source SHA256")
    size = source.stat().st_size
    from .staged_wav import MAX_STAGED_WAV_BYTES
    if not 44 <= size <= MAX_STAGED_WAV_BYTES:
        raise ContractError("staged WAV source length outside 64MiB safety cap")
    actual_sha256 = _file_sha256(source)
    if actual_sha256 != expected_sha256:
        raise ContractError("staged WAV content digest mismatch")
    descriptor = {
        "asset_version": "0", "asset_id": f"sha256:{actual_sha256}",
        "media_type": "audio/wav", "object_sha256": actual_sha256,
        "size_bytes": size, "format": _inspect_wav_file(source),
    }
    validate_contract(descriptor, "audio-asset-v0.schema.json")
    asset_id = descriptor["asset_id"]
    descriptor_path = _descriptor_path(project, actual_sha256)
    if descriptor_path.exists():
        existing = read_audio_asset(project, asset_id)
        if existing != descriptor:
            raise ProjectIntegrityError("existing immutable asset descriptor mismatch")
        return existing

    # Full existing integrity before object publication: never heal corruption.
    verify_audio_assets(project)
    target = project._object_path(actual_sha256)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.stat().st_size != size or _file_sha256(target) != actual_sha256:
            raise ProjectIntegrityError("content-addressed object corruption")
    else:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix="staged-object-", delete=False) as temp:
            temporary = Path(temp.name)
        try:
            copied_digest = hashlib.sha256()
            copied_size = 0
            with temporary.open("wb") as target_stream, source.open("rb") as stream:
                while block := stream.read(1024 * 1024):
                    target_stream.write(block)
                    copied_digest.update(block)
                    copied_size += len(block)
                target_stream.flush()
                os.fsync(target_stream.fileno())
            if copied_digest.hexdigest() != actual_sha256 or copied_size != size:
                raise ProjectIntegrityError("source staging changed while copying CAS object")
            # Link without replacement: an existing CAS object must never be
            # overwritten, even on simultaneous imports.
            try:
                os.link(temporary, target)
            except FileExistsError:
                if target.stat().st_size != size or _file_sha256(target) != actual_sha256:
                    raise ProjectIntegrityError("concurrent content-addressed object corruption")
        finally:
            temporary.unlink(missing_ok=True)

    descriptor_sha = project._store_json(descriptor)
    _atomic_write(descriptor_path, _json_bytes(descriptor))
    project._append_audit(
        "import_audio_asset", asset_id=asset_id,
        object_sha256=actual_sha256, descriptor_sha256=descriptor_sha,
    )
    return read_audio_asset(project, asset_id)


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
    actual_digest = _file_sha256(object_path)
    if actual_digest != digest:
        raise ProjectIntegrityError(f"audio asset object hash mismatch: {asset_id}")
    if object_path.stat().st_size != int(descriptor["size_bytes"]):
        raise ProjectIntegrityError(f"audio asset object size mismatch: {asset_id}")

    try:
        actual_format = _inspect_wav_file(object_path)
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


def import_audio_asset_bytes(project: MusicaProject, data: bytes) -> dict[str, Any]:
    """Import exact WAV bytes into the immutable project CAS.

    This is a resource operation, not creative acceptance. REC-R1 calls it only after
    explicit recording Accept has revalidated the exact capture and accepted source.
    Re-importing identical bytes remains idempotent.
    """

    if not isinstance(data, (bytes, bytearray)):
        raise ContractError("audio asset bytes must be bytes")
    data = bytes(data)
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


def import_audio_asset(project: MusicaProject, source_path: str | Path) -> dict[str, Any]:
    """Import one bounded WAV source into the existing project CAS."""

    source = Path(source_path)
    if not source.is_file():
        raise ContractError(f"audio asset source does not exist: {source}")
    return import_audio_asset_bytes(project, source.read_bytes())


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
