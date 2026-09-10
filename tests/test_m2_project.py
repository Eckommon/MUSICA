from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from musica.compiler import compile_blueprint
from musica.contracts import ContractError
from musica.creative import compose_blueprint
from musica.m2_demo import run_suite
from musica.project import MusicaProject, ProjectIntegrityError, create_project
from musica.render import render_midi, render_wav
from musica.semantic import apply_semantic_control

ROOT = Path(__file__).resolve().parents[1]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def load_intent() -> dict:
    return json.loads(INTENT_PATH.read_text(encoding="utf-8"))


def root_blueprint() -> dict:
    return compose_blueprint(load_intent())


def make_variation(parent: dict, revision_id: str = "rev-m2-test-variation") -> dict:
    section = parent["form"]["sections"][-1]
    control = {
        "control_id": "M2-TEST-TENSION",
        "name": "tension",
        "operation": "set",
        "value": 0.90,
        "scope": f"time:{float(section['start']):g}-{float(section['end']):g}",
        "confidence": 1.0,
        "source": "deterministic_transform",
        "phrase": "M2 test variation",
        "interpretation_notes": [],
        "protected_targets": [
            "/musical_context/tempo/bpm",
            "/materials/melody/main_motif_id",
            "/materials/rhythm/drum_pattern_id",
        ],
    }
    candidate, _ = apply_semantic_control(parent, control, revision_id=revision_id)
    return candidate


def test_create_open_and_root_revision_are_exact(tmp_path: Path):
    blueprint = root_blueprint()
    project = create_project(tmp_path / "song.musica", blueprint)

    reopened = MusicaProject(tmp_path / "song.musica")
    assert reopened.metadata()["project_id"] == blueprint["project"]["project_id"]
    assert reopened.current_branch() == "main"
    assert reopened.head_revision_id("main") == blueprint["project"]["revision_id"]
    assert reopened.read_revision(blueprint["project"]["revision_id"]) == blueprint
    assert reopened.verify_integrity()["status"] == "PASS"


def test_branch_commit_advances_only_selected_ref_and_preserves_lineage(tmp_path: Path):
    parent = root_blueprint()
    project = create_project(tmp_path / "song.musica", parent)
    root_id = parent["project"]["revision_id"]
    project.create_branch("variation-a", from_revision_id=root_id)

    candidate = make_variation(parent)
    record = project.commit_revision(candidate, branch="variation-a")

    assert project.head_revision_id("main") == root_id
    assert project.head_revision_id("variation-a") == candidate["project"]["revision_id"]
    assert record["parent_revision_id"] == root_id
    assert record["parent_record_sha256"] == project._read_ref("main")["revision_record_sha256"]
    assert project.read_diff(candidate["project"]["revision_id"])
    assert project.verify_integrity()["revision_count"] == 2


def test_inherited_hard_lock_still_fails_closed_after_reload_and_branch(tmp_path: Path):
    parent = root_blueprint()
    project = create_project(tmp_path / "song.musica", parent)
    root_id = parent["project"]["revision_id"]
    project.create_branch("illegal", from_revision_id=root_id)

    reloaded_parent = MusicaProject(tmp_path / "song.musica").read_revision(root_id)
    illegal = copy.deepcopy(reloaded_parent)
    illegal["project"]["parent_revision_id"] = root_id
    illegal["project"]["revision_id"] = "rev-illegal-tempo"
    illegal["musical_context"]["tempo"]["bpm"] += 4

    with pytest.raises(ContractError, match="revision commit blocked"):
        project.commit_revision(illegal, branch="illegal")
    assert project.head_revision_id("illegal") == root_id


def test_accepted_revision_and_artifact_manifest_are_immutable(tmp_path: Path):
    parent = root_blueprint()
    project = create_project(tmp_path / "song.musica", parent)
    with pytest.raises(ContractError, match="immutable"):
        project.commit_revision(parent, branch="main")

    revision_id = parent["project"]["revision_id"]
    artifact = tmp_path / "preview.mid"
    artifact.write_bytes(b"MThd-test")
    project.bind_artifacts(revision_id, [artifact])
    with pytest.raises(ContractError, match="artifact manifest is immutable"):
        project.bind_artifacts(revision_id, [artifact])


def test_rendered_artifacts_are_hash_bound_to_exact_revision(tmp_path: Path):
    parent = root_blueprint()
    project = create_project(tmp_path / "song.musica", parent)
    root_id = parent["project"]["revision_id"]
    project.create_branch("variation-a", from_revision_id=root_id)
    candidate = make_variation(parent)
    project.commit_revision(candidate, branch="variation-a")

    ir = compile_blueprint(candidate)
    midi = render_midi(ir, tmp_path / "candidate.mid")
    wav = render_wav(ir, tmp_path / "candidate.wav", duration_seconds=1.0, sample_rate=8000)
    manifest = project.bind_artifacts(candidate["project"]["revision_id"], [midi, wav])

    assert manifest["revision_id"] == candidate["project"]["revision_id"]
    assert {item["name"] for item in manifest["artifacts"]} == {"candidate.mid", "candidate.wav"}
    assert project.verify_integrity()["artifact_count"] == 2


def test_blueprint_tampering_fails_closed(tmp_path: Path):
    parent = root_blueprint()
    project = create_project(tmp_path / "song.musica", parent)
    revision_id = parent["project"]["revision_id"]
    target = project.root / "revisions" / revision_id / "blueprint.json"
    target.write_bytes(target.read_bytes() + b" ")

    with pytest.raises(ProjectIntegrityError, match="hash mismatch"):
        project.verify_integrity()


def test_object_tampering_fails_closed(tmp_path: Path):
    parent = root_blueprint()
    project = create_project(tmp_path / "song.musica", parent)
    record = project.read_revision_record(parent["project"]["revision_id"])
    target = project.root / "objects" / "sha256" / record["blueprint_sha256"]
    target.write_bytes(target.read_bytes() + b"x")

    with pytest.raises(ProjectIntegrityError, match="object hash mismatch|missing/corrupt revision object"):
        project.verify_integrity()


def test_export_import_and_reexport_are_byte_identical(tmp_path: Path):
    parent = root_blueprint()
    project = create_project(tmp_path / "song.musica", parent)
    root_id = parent["project"]["revision_id"]
    project.create_branch("variation-a", from_revision_id=root_id)
    candidate = make_variation(parent)
    project.commit_revision(candidate, branch="variation-a")

    archive_a = project.export_to(tmp_path / "a.musica.zip")
    archive_b = project.export_to(tmp_path / "b.musica.zip")
    assert archive_a.read_bytes() == archive_b.read_bytes()

    imported = MusicaProject.import_from(archive_a, tmp_path / "imported.musica")
    assert imported.verify_integrity()["status"] == "PASS"
    assert imported.export_bytes() == archive_a.read_bytes()
    assert imported.head_revision_id("main") == root_id
    assert imported.head_revision_id("variation-a") == candidate["project"]["revision_id"]


def test_m2_canonical_evidence_suite_is_reproducible(tmp_path: Path):
    manifest_a = run_suite(INTENT_PATH, tmp_path / "evidence-a")
    manifest_b = run_suite(INTENT_PATH, tmp_path / "evidence-b")

    assert manifest_a == manifest_b
    proof = manifest_a["proof"]
    assert proof["main_ref_preserved"] is True
    assert proof["variation_ref_advanced"] is True
    assert proof["artifact_binding_count"] == 2
    assert proof["integrity_status"] == "PASS"
    assert proof["tamper_blocked"] is True
    assert proof["export_reimport_verified"] is True
    assert proof["reexport_byte_identical"] is True
