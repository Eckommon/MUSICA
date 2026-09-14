from __future__ import annotations

import json
from pathlib import Path

import pytest

from musica.automation_edit import automation_material_sha256, blueprint_sha256
from musica.contracts import validate_contract
from musica.project import create_project
from musica.studio import StudioService, StudioServiceError
from musica.studio_automation import StudioAutomationSurface

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"
AUTOMATION_PATH = ROOT / "examples" / "automation" / "valid" / "automation-material-v0.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _blueprint() -> dict:
    blueprint = _load(BLUEPRINT_PATH)
    material = _load(AUTOMATION_PATH)
    next(lane for lane in material["lanes"] if lane["lane_id"] == "B-SYNTH-CUTOFF")["section_id"] = "S01"
    blueprint["materials"]["automation"] = material
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint


def _candidate(parent: dict) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": "AEC-M7-R2-PREVIEW-ISOLATION",
        "authority_target": "blueprint_automation_material",
        "source": {
            "project_id": parent["project"]["project_id"],
            "revision_id": parent["project"]["revision_id"],
            "blueprint_sha256": blueprint_sha256(parent),
            "automation_material_sha256": automation_material_sha256(parent),
        },
        "actor": {"kind": "user", "actor_id": "m7-r2-isolation-test"},
        "reason": "Prove automation cannot displace another pending Studio Preview.",
        "operations": [
            {
                "operation_id": "OP-M7-R2-ISOLATION",
                "op": "SET_VALUE",
                "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-001"},
                "value": 0.71,
            }
        ],
        "preview_only": True,
    }


def test_automation_preview_cannot_displace_pending_semantic_preview(tmp_path: Path) -> None:
    blueprint = _blueprint()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    create_project(workspace / "song.musica", blueprint)
    service = StudioService(workspace)
    service.open_project_session(project_slug="song", session_id="sid")
    project = service._get_session("sid").project
    accepted_head = project.head_revision_id()

    semantic = service.preview_semantic_edit(
        "sid",
        name="motion",
        operation="increase",
        value=0.05,
        scope_kind="whole_project",
    )
    semantic_preview_id = semantic["preview"]["preview_id"]
    assert service.inspect_session("sid")["pending_preview"]["kind"] == "semantic_control"

    with pytest.raises(StudioServiceError) as exc:
        StudioAutomationSurface(service).preview_automation_edit("sid", candidate=_candidate(blueprint))

    assert exc.value.code == "conflict"
    pending = service.inspect_session("sid")["pending_preview"]
    assert pending["kind"] == "semantic_control"
    assert pending["preview_id"] == semantic_preview_id
    assert project.head_revision_id() == accepted_head
