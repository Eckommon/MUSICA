from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from urllib.request import urlopen

import pytest

from musica.automation_edit import automation_material_sha256, blueprint_sha256
from musica.contracts import validate_contract
from musica.project import create_project
from musica.studio import StudioService, StudioServiceError
from musica.studio_automation import StudioAutomationSurface
from musica.studio_automation_audition import StudioAutomationAuditionSurface
from musica.studio_http import create_local_server

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
    slug: str = "r6-song",
    sid: str = "r6-session",
) -> tuple[StudioService, StudioAutomationSurface, StudioAutomationAuditionSurface]:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    create_project(workspace / f"{slug}.musica", blueprint)
    service = StudioService(workspace)
    service.open_project_session(project_slug=slug, session_id=sid)
    return service, StudioAutomationSurface(service), StudioAutomationAuditionSurface(service)


def candidate(parent: dict, operations: list[dict], *, candidate_id: str = "AEC-M7-R6-001") -> dict:
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
        "actor": {"kind": "user", "actor_id": "m7-r6-test"},
        "reason": "M7-R6 truthful audition inspection test.",
        "operations": operations,
        "preview_only": True,
    }


def mix_gain_value_operation(value: float = 0.71) -> dict:
    return {
        "operation_id": "OP-R6-MIX-GAIN",
        "op": "SET_VALUE",
        "target": {"lane_id": "A-MIX-GAIN", "point_id": "P-GAIN-001"},
        "value": value,
    }


def cutoff_value_operation(value: float = 1200.0) -> dict:
    return {
        "operation_id": "OP-R6-CUTOFF",
        "op": "SET_VALUE",
        "target": {"lane_id": "B-SYNTH-CUTOFF", "point_id": "P-CUTOFF-001"},
        "value": value,
    }


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_historical_r2_view_remains_false_while_r6_reports_bounded_policy(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, automation, audition = open_session(tmp_path, parent)

    old_view = automation.automation_view("r6-session")
    new_view = audition.audition_view("r6-session")

    assert old_view["view_version"] == "0"
    assert old_view["capabilities"]["audible_automation_validated"] is False
    assert new_view["audition_view_version"] == "0"
    assert new_view["renderer_policy"]["renderer_id"] == "musica-reference-local"
    assert new_view["renderer_policy"]["policy_id"] == "reference-renderer-mix-gain-v0"
    assert new_view["renderer_policy"]["validated_mapping_families"] == [
        {
            "mapping_id": "reference.mix_gain.normalized",
            "parameter_id": "mix.gain",
            "scope": "project",
            "owner_id": None,
            "unit": "normalized",
        }
    ]
    assert new_view["accepted_mapping"] == {
        "automation_present": True,
        "mapped_lane_ids": ["A-MIX-GAIN"],
        "unmapped_lane_ids": ["B-SYNTH-CUTOFF"],
    }
    assert new_view["pending_audition"] is None
    assert new_view["accepted_media"]["wav"]["source"] == "fallback_render"
    assert new_view["accepted_media"]["midi"]["source"] == "fallback_render"
    assert new_view["authority"] == {
        "canonical": False,
        "browser_mutation_authorized": False,
        "project_mutation_authorized": False,
        "reverse_promotion_authorized": False,
        "explicit_accept_required": True,
    }


def test_pending_audition_exposes_exact_trusted_preview_without_replacing_accepted_media(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, automation, audition = open_session(tmp_path, parent)
    accepted_head = service._get_session("r6-session").project.head_revision_id()
    accepted_before = audition.audition_view("r6-session")

    result = automation.preview_automation_edit(
        "r6-session",
        candidate=candidate(parent, [mix_gain_value_operation()]),
    )
    view = audition.audition_view("r6-session")
    pending = view["pending_audition"]
    assert pending is not None

    assert service._get_session("r6-session").project.head_revision_id() == accepted_head
    assert view["accepted_revision_id"] == accepted_head
    assert view["accepted_media"] == accepted_before["accepted_media"]
    assert pending["preview_id"] == result["preview"]["preview_id"]
    assert pending["candidate_revision_id"] == result["preview"]["candidate_revision_id"]
    assert pending["automation_applied"] is True
    assert pending["output_differs_from_baseline"] is True
    assert pending["mapped_lane_ids"] == ["A-MIX-GAIN"]
    assert pending["unmapped_lane_ids"] == ["B-SYNTH-CUTOFF"]
    assert pending["preview_wav_sha256"] == _sha(service.media_bytes("r6-session", "audio"))
    assert pending["preview_midi_sha256"] == _sha(service.media_bytes("r6-session", "midi"))
    assert pending["canonical"] is False
    assert pending["reverse_promotion_authorized"] is False

    service.discard_preview("r6-session")
    discarded = audition.audition_view("r6-session")
    assert discarded["pending_audition"] is None
    assert discarded["accepted_revision_id"] == accepted_head
    assert discarded["accepted_media"] == accepted_before["accepted_media"]


def test_accept_and_reopen_report_exact_bound_preview_artifacts(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, automation, audition = open_session(tmp_path, parent)
    project = service._get_session("r6-session").project
    root_revision = project.head_revision_id()

    result = automation.preview_automation_edit(
        "r6-session",
        candidate=candidate(parent, [mix_gain_value_operation()]),
    )
    preview_view = audition.audition_view("r6-session")
    pending = preview_view["pending_audition"]
    assert pending is not None
    preview_wav_sha = pending["preview_wav_sha256"]
    preview_midi_sha = pending["preview_midi_sha256"]
    candidate_revision = result["preview"]["candidate_revision_id"]

    accepted = service.accept_preview("r6-session")
    accepted_view = audition.audition_view("r6-session")

    assert accepted["revision_record"]["revision_id"] == candidate_revision
    assert candidate_revision != root_revision
    assert len(service.revision_history("r6-session")["revisions"]) == 2
    assert accepted_view["pending_audition"] is None
    assert accepted_view["accepted_revision_id"] == candidate_revision
    assert accepted_view["accepted_media"]["wav"]["source"] == "bound_artifact"
    assert accepted_view["accepted_media"]["midi"]["source"] == "bound_artifact"
    assert accepted_view["accepted_media"]["wav"]["sha256"] == preview_wav_sha
    assert accepted_view["accepted_media"]["midi"]["sha256"] == preview_midi_sha

    workspace = service.workspace
    service.close_session("r6-session")
    reopened_service = StudioService(workspace)
    reopened_service.open_project_session(project_slug="r6-song", session_id="r6-reopen")
    reopened_view = StudioAutomationAuditionSurface(reopened_service).audition_view("r6-reopen")

    assert reopened_view["accepted_revision_id"] == candidate_revision
    assert reopened_view["accepted_media"] == accepted_view["accepted_media"]
    assert reopened_view["accepted_media"]["wav"]["sha256"] == _sha(
        reopened_service.media_bytes("r6-reopen", "audio")
    )
    assert reopened_view["accepted_media"]["midi"]["sha256"] == _sha(
        reopened_service.media_bytes("r6-reopen", "midi")
    )


def test_unsupported_only_automation_is_truthfully_unmapped_and_inaudible(tmp_path: Path) -> None:
    parent = automation_blueprint(cutoff_only=True)
    service, automation, audition = open_session(
        tmp_path,
        parent,
        slug="r6-cutoff-only",
        sid="r6-cutoff",
    )
    accepted = audition.audition_view("r6-cutoff")
    assert accepted["accepted_mapping"] == {
        "automation_present": True,
        "mapped_lane_ids": [],
        "unmapped_lane_ids": ["B-SYNTH-CUTOFF"],
    }

    automation.preview_automation_edit(
        "r6-cutoff",
        candidate=candidate(parent, [cutoff_value_operation()], candidate_id="AEC-R6-CUTOFF"),
    )
    pending = audition.audition_view("r6-cutoff")["pending_audition"]
    assert pending is not None
    assert pending["automation_applied"] is False
    assert pending["output_differs_from_baseline"] is False
    assert pending["mapped_lane_ids"] == []
    assert pending["unmapped_lane_ids"] == ["B-SYNTH-CUTOFF"]
    assert pending["preview_wav_sha256"] == pending["baseline_wav_sha256"]


def test_tampered_pending_media_or_proof_fails_closed_for_inspection(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, automation, audition = open_session(tmp_path, parent)
    automation.preview_automation_edit(
        "r6-session",
        candidate=candidate(parent, [mix_gain_value_operation()]),
    )
    pending = service._get_session("r6-session").pending
    assert pending is not None
    pending.detail["studio_audition"]["render_plan_sha256"] = "0" * 64

    with pytest.raises(StudioServiceError, match="render plan") as exc_info:
        audition.audition_view("r6-session")
    assert exc_info.value.code == "integrity_error"


def test_http_exposes_new_audition_endpoint_without_reinterpreting_automation_v0(tmp_path: Path) -> None:
    parent = automation_blueprint()
    service, _automation, _audition = open_session(tmp_path, parent)
    server = create_local_server(service, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    base = f"http://{host}:{port}"
    try:
        with urlopen(f"{base}/v0/sessions/r6-session/automation", timeout=30) as response:  # noqa: S310
            old_payload = json.loads(response.read().decode("utf-8"))
        with urlopen(f"{base}/v0/sessions/r6-session/automation/audition", timeout=30) as response:  # noqa: S310
            new_payload = json.loads(response.read().decode("utf-8"))

        assert old_payload["data"]["capabilities"]["audible_automation_validated"] is False
        assert new_payload["operation"] == "automation_audition_view"
        assert new_payload["data"]["renderer_policy"]["renderer_id"] == "musica-reference-local"
        assert new_payload["data"]["accepted_mapping"]["mapped_lane_ids"] == ["A-MIX-GAIN"]
        assert new_payload["data"]["authority"]["canonical"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
