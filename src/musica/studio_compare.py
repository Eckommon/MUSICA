"""Read-only accepted-revision A/B comparison for MUSICA Studio.

The surface projects already accepted M2 authority into deterministic Blueprint diffs
and exact revision-specific audition media. It has no Accept, checkout, ranking, or
reverse-promotion authority.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from .contracts import validate_contract
from .diff import structured_diff
from .evidence import canonical_json_bytes
from .studio import StudioService, StudioServiceError, _safe_name


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _record_sha256(record: dict[str, Any]) -> str:
    return _sha256_bytes(canonical_json_bytes(record))


class StudioRevisionCompareSurface:
    """Truthful read-only projection over two immutable accepted revisions."""

    def __init__(self, service: StudioService) -> None:
        self.service = service

    def _bound_artifact_provenance(
        self,
        project: Any,
        revision_id: str,
        path: Path,
    ) -> tuple[str, str]:
        manifest_path = project.root / "artifacts" / revision_id / "manifest.json"
        if not manifest_path.is_file():
            raise StudioServiceError("integrity_error", "bound artifact lacks immutable manifest")
        manifest_bytes = manifest_path.read_bytes()
        try:
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StudioServiceError("integrity_error", "bound artifact manifest is unreadable") from exc
        validate_contract(manifest, "artifact-manifest-v0.schema.json")
        if str(manifest["revision_id"]) != revision_id:
            raise StudioServiceError("integrity_error", "bound artifact manifest revision identity differs")
        record = next((item for item in manifest["artifacts"] if item["name"] == path.name), None)
        if record is None:
            raise StudioServiceError("integrity_error", "bound artifact file is absent from immutable manifest")
        data = path.read_bytes()
        if record["sha256"] != _sha256_bytes(data) or int(record["size_bytes"]) != len(data):
            raise StudioServiceError("integrity_error", "bound artifact bytes differ from immutable manifest")
        return path.name, _sha256_bytes(manifest_bytes)

    def _media_item(
        self,
        path: Path,
        *,
        source: str,
        media_type: str,
        artifact_name: str | None,
        artifact_manifest_sha256: str | None,
    ) -> dict[str, Any]:
        if not path.is_file():
            raise StudioServiceError("integrity_error", "accepted revision media is unavailable")
        data = path.read_bytes()
        return {
            "available": True,
            "source": source,
            "sha256": _sha256_bytes(data),
            "size_bytes": len(data),
            "media_type": media_type,
            "artifact_name": artifact_name,
            "artifact_manifest_sha256": artifact_manifest_sha256,
        }

    def _revision_media(
        self,
        session: Any,
        revision_id: str,
        blueprint: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Path]]:
        bound_wav = self.service._artifact_media(session.project, revision_id, ".wav")
        bound_midi = self.service._artifact_media(session.project, revision_id, ".mid")
        fallback_wav: Path | None = None
        fallback_midi: Path | None = None

        if bound_wav is None or bound_midi is None:
            token = hashlib.sha256(revision_id.encode("utf-8")).hexdigest()[:16]
            fallback_midi, fallback_wav = self.service._render_to_cache(
                session,
                blueprint,
                f"compare-{token}",
            )

        wav_path = bound_wav if bound_wav is not None else fallback_wav
        midi_path = bound_midi if bound_midi is not None else fallback_midi
        if wav_path is None or midi_path is None:
            raise StudioServiceError("integrity_error", "accepted revision media resolution failed")

        wav_name: str | None = None
        wav_manifest_sha: str | None = None
        midi_name: str | None = None
        midi_manifest_sha: str | None = None
        if bound_wav is not None:
            wav_name, wav_manifest_sha = self._bound_artifact_provenance(
                session.project,
                revision_id,
                bound_wav,
            )
        if bound_midi is not None:
            midi_name, midi_manifest_sha = self._bound_artifact_provenance(
                session.project,
                revision_id,
                bound_midi,
            )

        media = {
            "wav": self._media_item(
                wav_path,
                source="bound_artifact" if bound_wav is not None else "deterministic_fallback",
                media_type="audio/wav",
                artifact_name=wav_name,
                artifact_manifest_sha256=wav_manifest_sha,
            ),
            "midi": self._media_item(
                midi_path,
                source="bound_artifact" if bound_midi is not None else "deterministic_fallback",
                media_type="audio/midi",
                artifact_name=midi_name,
                artifact_manifest_sha256=midi_manifest_sha,
            ),
        }
        return media, {"audio": wav_path, "midi": midi_path}

    def _revision_side(
        self,
        session: Any,
        revision_id: str,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
        safe_revision_id = _safe_name(revision_id, "revision_id")
        record = session.project.read_revision_record(safe_revision_id)
        blueprint = session.project.read_revision(safe_revision_id)
        if str(record["project_id"]) != str(blueprint["project"]["project_id"]):
            raise StudioServiceError("integrity_error", "revision record and Blueprint project identities differ")
        if str(record["revision_id"]) != safe_revision_id:
            raise StudioServiceError("integrity_error", "revision record identity differs from requested revision")
        media, paths = self._revision_media(session, safe_revision_id, blueprint)
        side = {
            "revision_id": safe_revision_id,
            "revision_record_sha256": _record_sha256(record),
            "blueprint_sha256": str(record["blueprint_sha256"]),
            "media": media,
        }
        return side, blueprint, paths

    def compare_view(
        self,
        session_id: str,
        *,
        revision_a: str,
        revision_b: str,
    ) -> dict[str, Any]:
        session = self.service._get_session(session_id)
        try:
            session.project.verify_integrity()
            branch_before = session.project.current_branch()
            head_before = session.project.head_revision_id(branch_before)

            side_a, blueprint_a, _paths_a = self._revision_side(session, revision_a)
            side_b, blueprint_b, _paths_b = self._revision_side(session, revision_b)
            if blueprint_a["project"]["project_id"] != blueprint_b["project"]["project_id"]:
                raise StudioServiceError("invalid_request", "revisions must belong to the same MUSICA project")

            diff = structured_diff(blueprint_a, blueprint_b)

            session.project.verify_integrity()
            branch_after = session.project.current_branch()
            head_after = session.project.head_revision_id(branch_after)
            if branch_before != branch_after or head_before != head_after:
                raise StudioServiceError("integrity_error", "revision comparison changed canonical project HEAD")

            value = {
                "compare_version": "0",
                "project_id": str(blueprint_a["project"]["project_id"]),
                "current_branch": str(branch_after),
                "current_head_revision_id": str(head_after),
                "direction": "A_TO_B",
                "revision_a": side_a,
                "revision_b": side_b,
                "diff": diff,
                "head_unchanged": True,
                "authority": {
                    "canonical": False,
                    "browser_mutation_authorized": False,
                    "project_mutation_authorized": False,
                    "reverse_promotion_authorized": False,
                    "creative_ranking_authorized": False,
                    "implicit_accept_authorized": False,
                },
            }
            validate_contract(value, "studio-revision-compare-v0.schema.json")
            return copy.deepcopy(value)
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc

    def media_bytes(
        self,
        session_id: str,
        *,
        revision_id: str,
        kind: str,
    ) -> bytes:
        if kind not in {"audio", "midi"}:
            raise StudioServiceError("invalid_request", f"unsupported revision media kind: {kind}")
        session = self.service._get_session(session_id)
        try:
            session.project.verify_integrity()
            branch_before = session.project.current_branch()
            head_before = session.project.head_revision_id(branch_before)
            _side, _blueprint, paths = self._revision_side(session, revision_id)
            path = paths[kind]
            if not path.is_file():
                raise StudioServiceError("not_found", f"accepted revision {kind} media is unavailable")
            data = path.read_bytes()
            branch_after = session.project.current_branch()
            head_after = session.project.head_revision_id(branch_after)
            if branch_before != branch_after or head_before != head_after:
                raise StudioServiceError("integrity_error", "revision media access changed canonical project HEAD")
            return data
        except Exception as exc:
            raise self.service._wrap_core_error(exc) from exc
