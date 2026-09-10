"""Generate the canonical MUSICA M2 Project & Version Engine evidence bundle.

공식 MUSICA M2 Project & Version Engine 근거 번들을 생성합니다.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .compiler import compile_blueprint
from .contracts import validate_contract
from .creative import compose_blueprint
from .evidence import artifact_record, sha256_file, write_canonical_json
from .project import PROJECT_ENGINE_ID, PROJECT_ENGINE_VERSION, MusicaProject, ProjectIntegrityError, create_project
from .render import DEFAULT_SAMPLE_RATE, render_midi, render_wav
from .semantic import apply_semantic_control


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _final_scope(blueprint: dict[str, Any]) -> str:
    section = blueprint["form"]["sections"][-1]
    return f"time:{float(section['start']):g}-{float(section['end']):g}"


def run_suite(intent_path: str | Path, out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    intent = _load(intent_path)
    validate_contract(intent, "music-intent-v0.schema.json")

    root_blueprint = compose_blueprint(intent)
    project_root = root / "canonical-project.musica"
    project = create_project(project_root, root_blueprint)
    root_revision_id = root_blueprint["project"]["revision_id"]

    project.create_branch("variation-a", from_revision_id=root_revision_id)
    control = {
        "control_id": "M2-VARIATION-A-TENSION",
        "name": "tension",
        "operation": "set",
        "value": 0.90,
        "scope": _final_scope(root_blueprint),
        "confidence": 1.0,
        "source": "deterministic_transform",
        "phrase": "Increase final-section pressure while preserving tempo, motif identity, and rhythm identity.",
        "interpretation_notes": ["M2 branch proof", "preserve inherited HARD locks"],
        "protected_targets": [
            "/musical_context/tempo/bpm",
            "/materials/melody/main_motif_id",
            "/materials/rhythm/drum_pattern_id"
        ]
    }
    variation, diff = apply_semantic_control(
        root_blueprint,
        control,
        revision_id="rev-m2-variation-a-001",
    )
    project.commit_revision(
        variation,
        branch="variation-a",
        actor="deterministic_transform",
        reason="M2 canonical branch variation under inherited HARD locks.",
    )

    if project.head_revision_id("main") != root_revision_id:
        raise RuntimeError("M2 invariant failed: main branch advanced unexpectedly")
    if project.head_revision_id("variation-a") != variation["project"]["revision_id"]:
        raise RuntimeError("M2 invariant failed: variation-a did not advance to R2")

    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        ir = compile_blueprint(variation)
        midi = render_midi(ir, temp / "variation-a.mid")
        wav = render_wav(
            ir,
            temp / "variation-a.wav",
            duration_seconds=float(variation["project"]["duration_seconds"]),
            sample_rate=DEFAULT_SAMPLE_RATE,
        )
        artifact_manifest = project.bind_artifacts(variation["project"]["revision_id"], [midi, wav])

    verification = project.verify_integrity()
    export_path = project.export_to(root / "canonical-project.musica.zip")
    export_sha = sha256_file(export_path)

    with tempfile.TemporaryDirectory() as import_name:
        imported_root = Path(import_name) / "imported.musica"
        imported = MusicaProject.import_from(export_path, imported_root)
        imported_verification = imported.verify_integrity()
        reexport = imported.export_bytes()
        export_reproducible = reexport == export_path.read_bytes()
        if not export_reproducible:
            raise RuntimeError("M2 deterministic export/import proof failed")

    with tempfile.TemporaryDirectory() as tamper_name:
        tampered_root = Path(tamper_name) / "tampered.musica"
        shutil.copytree(project_root, tampered_root)
        tampered = MusicaProject(tampered_root)
        target = tampered_root / "revisions" / variation["project"]["revision_id"] / "blueprint.json"
        target.write_bytes(target.read_bytes() + b" ")
        tamper_blocked = False
        tamper_reason = ""
        try:
            tampered.verify_integrity()
        except ProjectIntegrityError as exc:
            tamper_blocked = True
            tamper_reason = str(exc)
        if not tamper_blocked:
            raise RuntimeError("M2 integrity proof failed: tampering was not detected")

    branch_state = {
        "current_branch": project.current_branch(),
        "branches": {
            branch: project.head_revision_id(branch)
            for branch in project.list_branches()
        },
        "root_revision_id": root_revision_id,
        "variation_revision_id": variation["project"]["revision_id"],
        "variation_parent_revision_id": variation["project"]["parent_revision_id"],
        "variation_diff_count": len(diff),
    }
    tamper_result = {
        "status": "BLOCKED_AS_EXPECTED",
        "tamper_target": f"revisions/{variation['project']['revision_id']}/blueprint.json",
        "failure_contains_hash_mismatch": "hash mismatch" in tamper_reason,
    }
    import_export = {
        "status": "PASS",
        "export_sha256": export_sha,
        "reexport_byte_identical": export_reproducible,
        "imported_verification": imported_verification,
    }

    summary_files = [
        write_canonical_json(root / "canonical-control.json", control),
        write_canonical_json(root / "canonical-diff.json", diff),
        write_canonical_json(root / "branch-state.json", branch_state),
        write_canonical_json(root / "verification.json", verification),
        write_canonical_json(root / "artifact-binding.json", artifact_manifest),
        write_canonical_json(root / "import-export.json", import_export),
        write_canonical_json(root / "tamper-result.json", tamper_result),
        export_path,
    ]

    project_files = sorted(path for path in project_root.rglob("*") if path.is_file())
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M2-Project-Version-Engine-v0",
        "project_engine": {"id": PROJECT_ENGINE_ID, "version": PROJECT_ENGINE_VERSION},
        "proof": {
            "root_revision_id": root_revision_id,
            "variation_revision_id": variation["project"]["revision_id"],
            "main_ref_preserved": project.head_revision_id("main") == root_revision_id,
            "variation_ref_advanced": project.head_revision_id("variation-a") == variation["project"]["revision_id"],
            "artifact_binding_count": len(artifact_manifest["artifacts"]),
            "integrity_status": verification["status"],
            "tamper_blocked": tamper_blocked,
            "export_reimport_verified": imported_verification["status"] == "PASS",
            "reexport_byte_identical": export_reproducible,
        },
        "claim_boundary": [
            "filesystem Project Bundle v0, not a cloud collaboration service",
            "content integrity, not cryptographic signer identity/authenticity",
            "lightweight MUSICA refs, not Git interoperability",
            "local deterministic proof, not a production database",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(summary_files + project_files, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M2 Project & Version Engine evidence")
    parser.add_argument("--intent", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.intent, args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
