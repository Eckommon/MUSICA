"""MUSICA M2 durable Project & Version Engine.

MUSICA M2 영속 Project & Version Engine.

The user project format is intentionally independent from Git. Accepted revisions are
immutable, canonical JSON is content-addressed by SHA-256, branch refs are lightweight,
and integrity verification fails closed on tampering.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from .contracts import ContractError, validate_contract, validate_revision
from .diff import structured_diff
from .evidence import canonical_json_bytes

BUNDLE_VERSION = "0"
PROJECT_ENGINE_ID = "musica-project-engine"
PROJECT_ENGINE_VERSION = "0.1.0"
_BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class ProjectIntegrityError(ContractError):
    """Raised when persisted MUSICA project state fails integrity verification."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return canonical_json_bytes(value)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectIntegrityError(f"cannot read canonical JSON: {path}") from exc


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    temp.replace(path)


def _validate_branch(name: str) -> str:
    if not _BRANCH.fullmatch(name):
        raise ContractError(f"invalid MUSICA branch name: {name!r}")
    return name


def _media_type(path: Path) -> str:
    explicit = {
        ".mid": "audio/midi",
        ".midi": "audio/midi",
        ".wav": "audio/wav",
        ".json": "application/json",
    }
    return explicit.get(path.suffix.lower(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")


class MusicaProject:
    """A filesystem-backed, Git-independent MUSICA Project Bundle."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    @property
    def project_path(self) -> Path:
        return self.root / "project.json"

    @property
    def history_path(self) -> Path:
        return self.root / "audit" / "history.jsonl"

    @property
    def audit_head_path(self) -> Path:
        return self.root / "audit" / "HEAD"

    @property
    def head_path(self) -> Path:
        return self.root / "refs" / "HEAD.json"

    def _object_path(self, digest: str) -> Path:
        return self.root / "objects" / "sha256" / digest

    def _revision_dir(self, revision_id: str) -> Path:
        return self.root / "revisions" / revision_id

    def _ref_path(self, branch: str) -> Path:
        return self.root / "refs" / "heads" / f"{_validate_branch(branch)}.json"

    def metadata(self) -> dict[str, Any]:
        value = _read_json(self.project_path)
        validate_contract(value, "project-bundle-v0.schema.json")
        return value

    def current_branch(self) -> str:
        head = _read_json(self.head_path)
        if set(head) != {"head_version", "symbolic_ref"} or head.get("head_version") != "0":
            raise ProjectIntegrityError("invalid refs/HEAD.json")
        symbolic = str(head["symbolic_ref"])
        prefix = "refs/heads/"
        if not symbolic.startswith(prefix):
            raise ProjectIntegrityError("HEAD must be symbolic to refs/heads/*")
        return _validate_branch(symbolic[len(prefix) :])

    def _write_head(self, branch: str) -> None:
        branch = _validate_branch(branch)
        _atomic_write(
            self.head_path,
            _json_bytes({"head_version": "0", "symbolic_ref": f"refs/heads/{branch}"}),
        )

    def _store_bytes(self, data: bytes) -> str:
        digest = _sha256_bytes(data)
        target = self._object_path(digest)
        if target.exists():
            if target.read_bytes() != data:
                raise ProjectIntegrityError(f"object collision or corruption: {digest}")
            return digest
        _atomic_write(target, data)
        return digest

    def _store_json(self, value: Any) -> str:
        return self._store_bytes(_json_bytes(value))

    def _audit_events(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []
        events: list[dict[str, Any]] = []
        for line in self.history_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ProjectIntegrityError("invalid audit JSONL") from exc
        return events

    def _append_audit(self, event_type: str, **payload: Any) -> dict[str, Any]:
        events = self._audit_events()
        previous = None
        if events:
            previous = _sha256_bytes(_json_bytes(events[-1]))
        event = {
            "audit_version": "0",
            "sequence": len(events) + 1,
            "event_type": event_type,
            "previous_event_sha256": previous,
            "payload": payload,
        }
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("ab") as handle:
            handle.write(_json_bytes(event))
        digest = _sha256_bytes(_json_bytes(event))
        _atomic_write(self.audit_head_path, (digest + "\n").encode("ascii"))
        return event

    def _next_audit_sequence(self) -> int:
        return len(self._audit_events()) + 1

    def _read_ref(self, branch: str) -> dict[str, Any]:
        path = self._ref_path(branch)
        if not path.exists():
            raise ContractError(f"unknown MUSICA branch: {branch}")
        ref = _read_json(path)
        validate_contract(ref, "project-ref-v0.schema.json")
        return ref

    def _write_ref(self, branch: str, revision_id: str, record_sha: str) -> None:
        branch = _validate_branch(branch)
        ref = {
            "ref_version": "0",
            "ref_name": f"refs/heads/{branch}",
            "revision_id": revision_id,
            "revision_record_sha256": record_sha,
        }
        validate_contract(ref, "project-ref-v0.schema.json")
        _atomic_write(self._ref_path(branch), _json_bytes(ref))

    def list_branches(self) -> list[str]:
        root = self.root / "refs" / "heads"
        if not root.exists():
            return []
        return sorted(path.stem for path in root.glob("*.json"))

    def head_revision_id(self, branch: str | None = None) -> str:
        selected = branch or self.current_branch()
        return str(self._read_ref(selected)["revision_id"])

    def read_revision_record(self, revision_id: str) -> dict[str, Any]:
        path = self._revision_dir(revision_id) / "revision.json"
        if not path.exists():
            raise ContractError(f"unknown MUSICA revision: {revision_id}")
        record = _read_json(path)
        validate_contract(record, "revision-record-v0.schema.json")
        return record

    def read_revision(self, revision_id: str) -> dict[str, Any]:
        record = self.read_revision_record(revision_id)
        path = self._revision_dir(revision_id) / "blueprint.json"
        blueprint = _read_json(path)
        validate_contract(blueprint, "music-blueprint-v0.schema.json")
        if _sha256_bytes(path.read_bytes()) != record["blueprint_sha256"]:
            raise ProjectIntegrityError(f"blueprint hash mismatch for revision {revision_id}")
        return blueprint

    def read_diff(self, revision_id: str) -> list[dict[str, Any]]:
        record = self.read_revision_record(revision_id)
        path = self._revision_dir(revision_id) / "diff.json"
        diff = _read_json(path)
        if not isinstance(diff, list):
            raise ProjectIntegrityError(f"revision diff must be a list: {revision_id}")
        if _sha256_bytes(path.read_bytes()) != record["diff_sha256"]:
            raise ProjectIntegrityError(f"diff hash mismatch for revision {revision_id}")
        return diff

    def commit_revision(
        self,
        blueprint: dict[str, Any],
        *,
        branch: str | None = None,
        actor: str | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Commit one immutable accepted Blueprint and advance only the selected ref."""

        validate_contract(blueprint, "music-blueprint-v0.schema.json")
        metadata = self.metadata()
        if blueprint["project"]["project_id"] != metadata["project_id"]:
            raise ContractError("Blueprint project_id does not match Project Bundle")

        selected = _validate_branch(branch or self.current_branch())
        revision_id = str(blueprint["project"]["revision_id"])
        revision_dir = self._revision_dir(revision_id)
        if revision_dir.exists():
            raise ContractError(f"accepted revision is immutable and already exists: {revision_id}")

        ref_path = self._ref_path(selected)
        parent_blueprint: dict[str, Any] | None = None
        parent_revision_id: str | None = None
        parent_record_sha: str | None = None
        if ref_path.exists():
            ref = self._read_ref(selected)
            parent_revision_id = str(ref["revision_id"])
            parent_record_sha = str(ref["revision_record_sha256"])
            parent_blueprint = self.read_revision(parent_revision_id)
            conflicts = validate_revision(parent_blueprint, blueprint)
            blocking = [conflict for conflict in conflicts if conflict.status == "BLOCKED"]
            if blocking:
                details = " | ".join(f"{c.rule_id}: {c.reason}" for c in blocking)
                raise ContractError(f"revision commit blocked: {details}")
        elif blueprint["project"].get("parent_revision_id") is not None:
            raise ContractError("first branch revision must be a root Blueprint")

        if parent_revision_id != blueprint["project"].get("parent_revision_id"):
            raise ContractError(
                f"Blueprint parent_revision_id must equal branch tip {parent_revision_id!r}"
            )

        diff = [] if parent_blueprint is None else structured_diff(parent_blueprint, blueprint)
        blueprint_bytes = _json_bytes(blueprint)
        diff_bytes = _json_bytes(diff)
        blueprint_sha = self._store_bytes(blueprint_bytes)
        diff_sha = self._store_bytes(diff_bytes)

        provenance = blueprint.get("provenance", {})
        resolved_actor = actor or str(provenance.get("actor", "user"))
        resolved_reason = reason or str(provenance.get("change_reason") or "Accept Blueprint revision.")
        record = {
            "record_version": "0",
            "project_id": metadata["project_id"],
            "revision_id": revision_id,
            "parent_revision_id": parent_revision_id,
            "blueprint_sha256": blueprint_sha,
            "diff_sha256": diff_sha,
            "parent_record_sha256": parent_record_sha,
            "actor": resolved_actor,
            "reason": resolved_reason,
            "logical_sequence": self._next_audit_sequence(),
        }
        validate_contract(record, "revision-record-v0.schema.json")
        record_bytes = _json_bytes(record)
        record_sha = self._store_bytes(record_bytes)

        revision_dir.mkdir(parents=True, exist_ok=False)
        _atomic_write(revision_dir / "blueprint.json", blueprint_bytes)
        _atomic_write(revision_dir / "diff.json", diff_bytes)
        _atomic_write(revision_dir / "revision.json", record_bytes)
        self._write_ref(selected, revision_id, record_sha)
        self._append_audit(
            "commit_revision",
            branch=selected,
            revision_id=revision_id,
            revision_record_sha256=record_sha,
        )
        return record

    def create_branch(self, name: str, *, from_revision_id: str | None = None) -> dict[str, Any]:
        name = _validate_branch(name)
        if self._ref_path(name).exists():
            raise ContractError(f"branch already exists: {name}")
        source_revision = from_revision_id or self.head_revision_id()
        record = self.read_revision_record(source_revision)
        record_sha = _sha256_bytes(_json_bytes(record))
        self._write_ref(name, source_revision, record_sha)
        self._append_audit(
            "create_branch",
            branch=name,
            from_revision_id=source_revision,
            revision_record_sha256=record_sha,
        )
        return self._read_ref(name)

    def checkout(self, branch: str) -> None:
        branch = _validate_branch(branch)
        self._read_ref(branch)
        self._write_head(branch)
        self._append_audit("checkout", branch=branch, revision_id=self.head_revision_id(branch))

    def bind_artifacts(self, revision_id: str, files: Iterable[str | Path]) -> dict[str, Any]:
        """Copy and hash-bind immutable output artifacts to an exact accepted revision."""

        record = self.read_revision_record(revision_id)
        record_sha = _sha256_bytes(_json_bytes(record))
        artifact_root = self.root / "artifacts" / revision_id
        manifest_path = artifact_root / "manifest.json"
        if manifest_path.exists():
            raise ContractError(f"artifact manifest is immutable and already exists: {revision_id}")

        file_root = artifact_root / "files"
        records: list[dict[str, Any]] = []
        seen: set[str] = set()
        for source_value in files:
            source = Path(source_value)
            if not source.is_file():
                raise ContractError(f"artifact does not exist: {source}")
            if source.name in seen:
                raise ContractError(f"duplicate artifact filename: {source.name}")
            seen.add(source.name)
            data = source.read_bytes()
            digest = self._store_bytes(data)
            target = file_root / source.name
            _atomic_write(target, data)
            records.append(
                {
                    "name": source.name,
                    "media_type": _media_type(source),
                    "size_bytes": len(data),
                    "sha256": digest,
                    "object_sha256": digest,
                }
            )

        manifest = {
            "manifest_version": "0",
            "project_id": self.metadata()["project_id"],
            "revision_id": revision_id,
            "revision_record_sha256": record_sha,
            "artifacts": sorted(records, key=lambda item: item["name"]),
        }
        validate_contract(manifest, "artifact-manifest-v0.schema.json")
        _atomic_write(manifest_path, _json_bytes(manifest))
        self._store_json(manifest)
        self._append_audit(
            "bind_artifacts",
            revision_id=revision_id,
            manifest_sha256=_sha256_bytes(_json_bytes(manifest)),
            artifact_count=len(records),
        )
        return manifest

    def verify_integrity(self) -> dict[str, Any]:
        """Verify all persisted cross-links, hashes, lineage, refs, artifacts, and audit chain."""

        metadata = self.metadata()
        errors: list[str] = []

        object_root = self.root / "objects" / "sha256"
        object_count = 0
        for path in sorted(object_root.glob("*")) if object_root.exists() else []:
            if not path.is_file():
                continue
            object_count += 1
            actual = _sha256_bytes(path.read_bytes())
            if path.name != actual:
                errors.append(f"object hash mismatch: {path.name} != {actual}")

        revision_root = self.root / "revisions"
        revision_ids = sorted(path.name for path in revision_root.iterdir() if path.is_dir()) if revision_root.exists() else []
        record_hashes: dict[str, str] = {}
        blueprints: dict[str, dict[str, Any]] = {}
        records: dict[str, dict[str, Any]] = {}
        for revision_id in revision_ids:
            try:
                record = self.read_revision_record(revision_id)
                blueprint_path = self._revision_dir(revision_id) / "blueprint.json"
                diff_path = self._revision_dir(revision_id) / "diff.json"
                blueprint = _read_json(blueprint_path)
                diff = _read_json(diff_path)
                validate_contract(blueprint, "music-blueprint-v0.schema.json")
                if record["revision_id"] != revision_id:
                    errors.append(f"revision directory/id mismatch: {revision_id}")
                if record["project_id"] != metadata["project_id"]:
                    errors.append(f"revision project mismatch: {revision_id}")
                if blueprint["project"]["revision_id"] != revision_id:
                    errors.append(f"Blueprint revision mismatch: {revision_id}")
                blueprint_sha = _sha256_bytes(blueprint_path.read_bytes())
                diff_sha = _sha256_bytes(diff_path.read_bytes())
                if blueprint_sha != record["blueprint_sha256"]:
                    errors.append(f"blueprint hash mismatch: {revision_id}")
                if diff_sha != record["diff_sha256"]:
                    errors.append(f"diff hash mismatch: {revision_id}")
                for digest in (record["blueprint_sha256"], record["diff_sha256"]):
                    obj = self._object_path(str(digest))
                    if not obj.exists() or _sha256_bytes(obj.read_bytes()) != digest:
                        errors.append(f"missing/corrupt revision object {digest}: {revision_id}")
                record_sha = _sha256_bytes(_json_bytes(record))
                record_hashes[revision_id] = record_sha
                record_obj = self._object_path(record_sha)
                if not record_obj.exists() or record_obj.read_bytes() != _json_bytes(record):
                    errors.append(f"missing/corrupt revision record object: {revision_id}")
                records[revision_id] = record
                blueprints[revision_id] = blueprint
                if not isinstance(diff, list):
                    errors.append(f"diff is not a list: {revision_id}")
            except ContractError as exc:
                errors.append(f"revision {revision_id}: {exc}")

        for revision_id, record in records.items():
            parent_id = record["parent_revision_id"]
            blueprint = blueprints[revision_id]
            if parent_id is None:
                if blueprint["project"].get("parent_revision_id") is not None:
                    errors.append(f"root Blueprint has parent: {revision_id}")
            else:
                if parent_id not in records:
                    errors.append(f"missing parent revision {parent_id}: {revision_id}")
                    continue
                if record.get("parent_record_sha256") != record_hashes[parent_id]:
                    errors.append(f"parent record hash mismatch: {revision_id}")
                try:
                    conflicts = validate_revision(blueprints[parent_id], blueprint)
                    if any(conflict.status == "BLOCKED" for conflict in conflicts):
                        errors.append(f"stored revision violates inherited rules: {revision_id}")
                except ContractError as exc:
                    errors.append(f"stored revision validation failed {revision_id}: {exc}")
                expected_diff = structured_diff(blueprints[parent_id], blueprint)
                if _json_bytes(expected_diff) != (self._revision_dir(revision_id) / "diff.json").read_bytes():
                    errors.append(f"stored diff mismatch: {revision_id}")

        ref_root = self.root / "refs" / "heads"
        ref_count = 0
        for path in sorted(ref_root.glob("*.json")) if ref_root.exists() else []:
            ref_count += 1
            try:
                ref = _read_json(path)
                validate_contract(ref, "project-ref-v0.schema.json")
                branch = path.stem
                if ref["ref_name"] != f"refs/heads/{branch}":
                    errors.append(f"ref name/path mismatch: {branch}")
                revision_id = str(ref["revision_id"])
                if revision_id not in record_hashes:
                    errors.append(f"ref points to missing revision: {branch}")
                elif ref["revision_record_sha256"] != record_hashes[revision_id]:
                    errors.append(f"ref record hash mismatch: {branch}")
            except ContractError as exc:
                errors.append(f"ref {path.name}: {exc}")

        try:
            current = self.current_branch()
            if not self._ref_path(current).exists():
                errors.append("HEAD points to missing branch")
        except ContractError as exc:
            errors.append(f"HEAD: {exc}")

        artifact_count = 0
        artifact_root = self.root / "artifacts"
        if artifact_root.exists():
            for revision_dir in sorted(path for path in artifact_root.iterdir() if path.is_dir()):
                manifest_path = revision_dir / "manifest.json"
                if not manifest_path.exists():
                    errors.append(f"artifact directory lacks manifest: {revision_dir.name}")
                    continue
                try:
                    manifest = _read_json(manifest_path)
                    validate_contract(manifest, "artifact-manifest-v0.schema.json")
                    revision_id = str(manifest["revision_id"])
                    if revision_id != revision_dir.name or revision_id not in record_hashes:
                        errors.append(f"artifact manifest revision mismatch: {revision_dir.name}")
                        continue
                    if manifest["revision_record_sha256"] != record_hashes[revision_id]:
                        errors.append(f"artifact revision record mismatch: {revision_id}")
                    for item in manifest["artifacts"]:
                        artifact_count += 1
                        path = revision_dir / "files" / item["name"]
                        if not path.exists():
                            errors.append(f"missing artifact file: {revision_id}/{item['name']}")
                            continue
                        data = path.read_bytes()
                        digest = _sha256_bytes(data)
                        if digest != item["sha256"] or len(data) != item["size_bytes"]:
                            errors.append(f"artifact hash/size mismatch: {revision_id}/{item['name']}")
                        obj = self._object_path(str(item["object_sha256"]))
                        if not obj.exists() or obj.read_bytes() != data:
                            errors.append(f"artifact object mismatch: {revision_id}/{item['name']}")
                    manifest_sha = _sha256_bytes(_json_bytes(manifest))
                    manifest_obj = self._object_path(manifest_sha)
                    if not manifest_obj.exists() or manifest_obj.read_bytes() != _json_bytes(manifest):
                        errors.append(f"artifact manifest object mismatch: {revision_id}")
                except ContractError as exc:
                    errors.append(f"artifact manifest {revision_dir.name}: {exc}")

        events = self._audit_events()
        previous: str | None = None
        for index, event in enumerate(events, start=1):
            if event.get("audit_version") != "0" or event.get("sequence") != index:
                errors.append(f"audit sequence/version mismatch at {index}")
            if event.get("previous_event_sha256") != previous:
                errors.append(f"audit chain mismatch at {index}")
            previous = _sha256_bytes(_json_bytes(event))
        expected_audit_head = previous
        if events:
            if not self.audit_head_path.exists():
                errors.append("missing audit HEAD")
            else:
                actual_head = self.audit_head_path.read_text(encoding="ascii").strip()
                if actual_head != expected_audit_head:
                    errors.append("audit HEAD hash mismatch")
        elif self.audit_head_path.exists():
            errors.append("audit HEAD exists without history")

        if metadata["root_revision_id"] not in record_hashes:
            errors.append("project root_revision_id does not exist")

        if errors:
            raise ProjectIntegrityError("project integrity verification failed: " + " | ".join(errors))

        return {
            "status": "PASS",
            "project_id": metadata["project_id"],
            "revision_count": len(revision_ids),
            "ref_count": ref_count,
            "object_count": object_count,
            "artifact_count": artifact_count,
            "audit_event_count": len(events),
            "audit_head_sha256": expected_audit_head,
        }

    def export_bytes(self) -> bytes:
        """Create a deterministic ZIP representation of the current Project Bundle."""

        self.verify_integrity()
        stream = BytesIO()
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            files = sorted(path for path in self.root.rglob("*") if path.is_file())
            for path in files:
                relative = path.relative_to(self.root).as_posix()
                info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        return stream.getvalue()

    def export_to(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(self.export_bytes())
        return target

    @classmethod
    def import_from(cls, archive_path: str | Path, destination: str | Path) -> "MusicaProject":
        destination = Path(destination)
        if destination.exists() and any(destination.iterdir()):
            raise ContractError(f"import destination is not empty: {destination}")
        destination.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path, "r") as archive:
            for member in archive.infolist():
                pure = PurePosixPath(member.filename)
                if pure.is_absolute() or ".." in pure.parts:
                    raise ContractError(f"unsafe project archive path: {member.filename}")
                if member.is_dir():
                    continue
                target = destination.joinpath(*pure.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(member))
        project = cls(destination)
        project.verify_integrity()
        return project


def create_project(
    root: str | Path,
    blueprint: dict[str, Any],
    *,
    default_branch: str = "main",
) -> MusicaProject:
    """Create a new MUSICA Project Bundle and accept its root Blueprint revision."""

    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    default_branch = _validate_branch(default_branch)
    root = Path(root)
    if root.exists() and any(root.iterdir()):
        raise ContractError(f"Project Bundle destination is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)

    project_data = {
        "bundle_version": BUNDLE_VERSION,
        "project_id": blueprint["project"]["project_id"],
        "title": blueprint["project"]["title"],
        "default_branch": default_branch,
        "root_revision_id": blueprint["project"]["revision_id"],
        "created_from_intent_id": blueprint.get("provenance", {}).get("created_from_intent_id"),
        "format_policy": {
            "hash": "sha256",
            "canonical_json": "utf8-sort-keys-compact-newline-v0",
            "audit_clock": "logical-sequence",
            "git_required": False,
        },
    }
    validate_contract(project_data, "project-bundle-v0.schema.json")
    project = MusicaProject(root)
    _atomic_write(project.project_path, _json_bytes(project_data))
    project._write_head(default_branch)
    project.commit_revision(
        blueprint,
        branch=default_branch,
        actor=str(blueprint.get("provenance", {}).get("actor", "user")),
        reason=str(blueprint.get("provenance", {}).get("change_reason") or "Create project root revision."),
    )
    project.verify_integrity()
    return project
