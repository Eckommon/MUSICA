from __future__ import annotations

import hashlib
import json
from pathlib import Path

from musica.automation_edit import automation_material_sha256, blueprint_sha256
from musica.contracts import validate_contract
from musica.project import create_project
from musica.studio import StudioService
from musica.studio_automation import StudioAutomationSurface

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def automation_blueprint(*, cutoff_only: bool = False) -> dict:
    blueprint = _load(BLUEPRINT_PATH)
    material = _load(AUTOMATION_PATH)
    cutoff = next(lane for lane in material["lanes"] if lane["lane_id"] == "B-SYNTH-CUTOFF")
    cutoff["section_id"] = "S01"
    if cutoff_only:
        material["lanes"] = [cutoff]
    blueprint["materials"]["automation"] = material
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def open_session(
    tmp_path: Path,
    blueprint: dict,
    *,
    slug: str = "r5-song",
    sid: str = "r5-session",
) -> tuple[StudioService, StudioAutomationSurface]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    create_project(workspace / f"{slug}.musica", blueprint)
    service = StudioService(workspace)
    service.open_project_session(project_slug=slug, session_id=sid)
    return service, StudioAutomationSurface(service)


def candidate(
    parent: dict,
    operations: list[dict],
    *,
    candidate_id: str = "AEC-M7-R5-001",
) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_automation_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
            "automation_material_sha256": automation_material_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "m7-r5-test"},
        "reason": "M7-R5 Studio audible automation test.",
        "operations": operations,
        "preview_only": True,
    }


def mix_gain_value_operation(value: float = 0.71) -> dict:
    return {
        "operation_id": "OP-R5-MIX-GAIN",
        "op": "SET_VALUE",
        "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-001"},
        "value": value,
    }


def cutoff_value_operation(value: float = 1200.0) -> dict:
    return {
        "operation_id": "OP-R5-CUTOFF",
        "op": "SET_VALUE",
        "target": {"lane_id": "B-SYNTH-CUTOFF", "point_id": "P-CUTOFF-001"},
        "value": value,
    }


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_mix_gain_preview_is_audible_source_bound_and_noncanonical(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, surface = open_session(tmp_path, parent)
    project = service._get_session("r5-session").project
    accepted_head = project.head_revision_id()

    result = surface.preview_automation_edit(
        "r5-session",
        candidate=candidate(parent, [mix_gain_value_operation()]),
    )

    proof = result["studio_audition"]
    assert result["preview_installed"] is True
    assert project.head_revision_id() == accepted_head
    assert proof["candidate_revision_id"] == result["preview"]["candidate_revision_id"]
    assert proof["path"] == "m7-r3-to-m7-r4-reference-renderer"
    assert proof["automation_applied"] is True
    assert proof["output_differs_from_baseline"] is True
    assert proof["mapped_lane_ids"] == ["A-MIX-GAIN"]
    assert proof["unmapped_lane_ids"] == ["B-SYNTH-CUTOFF"]
    assert proof["project_ref_unchanged"] is True
    assert proof["canonical"] is False
    assert proof["reverse_promotion_authorized"] is False
    assert _sha(service.media_bytes("r5-session", "audio")) == proof["preview_wav_sha256"]
    assert _sha(service.media_bytes("r5-session", "midi")) == proof["preview_midi_sha256"]
    assert result["detail"]["audible_automation_validated"] is False
    assert result["automation_view"]["capabilities"]["audible_automation_validated"] is False


def test_discard_removes_audible_preview_and_preserves_accepted_media(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, surface = open_session(tmp_path, parent)
    project = service._get_session("r5-session").project
    accepted_head = project.head_revision_id()
    accepted_audio_before = service.media_bytes("r5-session", "audio")

    surface.preview_automation_edit(
        "r5-session",
        candidate=candidate(parent, [mix_gain_value_operation()]),
    )
    pending = service._get_session("r5-session").pending
    assert pending is not None
    preview_root = pending.wav_path.parent
    assert service.media_bytes("r5-session", "audio") != accepted_audio_before

    discarded = service.discard_preview("r5-session")

    assert discarded["head_revision_id"] == accepted_head
    assert project.head_revision_id() == accepted_head
    assert not preview_root.exists()
    assert service.media_bytes("r5-session", "audio") == accepted_audio_before


def test_accept_persists_exact_preview_wav_and_midi(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, surface = open_session(tmp_path, parent)
    project = service._get_session("r5-session").project
    accepted_head = project.head_revision_id()

    result = surface.preview_automation_edit(
        "r5-session",
        candidate=candidate(parent, [mix_gain_value_operation()]),
    )
    preview_wav = service.media_bytes("r5-session", "audio")
    preview_midi = service.media_bytes("r5-session", "midi")
    candidate_revision = result["preview"]["candidate_revision_id"]

    accepted = service.accept_preview("r5-session")

    assert accepted["revision_record"]["revision_id"] == candidate_revision
    assert project.head_revision_id() == candidate_revision
    assert project.head_revision_id() != accepted_head
    assert accepted["project_verification"]["status"] == "PASS"
    assert len(accepted["artifact_manifest"]["artifacts"]) == 2
    assert service.media_bytes("r5-session", "audio") == preview_wav
    assert service.media_bytes("r5-session", "midi") == preview_midi


def test_reopen_serves_exact_accepted_audible_artifact(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, surface = open_session(tmp_path, parent)
    result = surface.preview_automation_edit(
        "r5-session",
        candidate=candidate(parent, [mix_gain_value_operation()]),
    )
    preview_wav = service.media_bytes("r5-session", "audio")
    preview_midi = service.media_bytes("r5-session", "midi")
    candidate_revision = result["preview"]["candidate_revision_id"]
    service.accept_preview("r5-session")
    workspace = service.workspace
    service.close_session("r5-session")

    reopened_service = StudioService(workspace)
    reopened = reopened_service.open_project_session(
        project_slug="r5-song",
        session_id="r5-reopen",
    )

    assert reopened["session"]["head_revision_id"] == candidate_revision
    assert reopened["session"]["integrity_status"] == "PASS"
    assert reopened_service.media_bytes("r5-reopen", "audio") == preview_wav
    assert reopened_service.media_bytes("r5-reopen", "midi") == preview_midi


def test_unsupported_only_lane_remains_unmapped_and_baseline_equivalent(tmp_path: Path) -> None:
    parent = automation_blueprint(cutoff_only=True)
    service, surface = open_session(
        tmp_path,
        parent,
        slug="r5-cutoff-only",
        sid="r5-cutoff",
    )

    result = surface.preview_automation_edit(
        "r5-cutoff",
        candidate=candidate(parent, [cutoff_value_operation()], candidate_id="AEC-R5-CUTOFF"),
    )
    proof = result["studio_audition"]

    assert result["preview_installed"] is True
    assert proof["automation_applied"] is False
    assert proof["output_differs_from_baseline"] is False
    assert proof["mapped_lane_ids"] == []
    assert proof["unmapped_lane_ids"] == ["B-SYNTH-CUTOFF"]
    assert proof["baseline_wav_sha256"] == proof["preview_wav_sha256"]
    assert result["detail"]["audible_automation_validated"] is False
