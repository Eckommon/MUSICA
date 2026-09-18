from __future__ import annotations

import io
import json
import wave
from pathlib import Path

import pytest

from musica.audio_assets import import_audio_asset
from musica.audio_edit import (
    accept_audio_edit_preview,
    audio_material_sha256,
    blueprint_sha256,
    build_audio_edit_preview,
)
from musica.contracts import ContractError
from musica.creative import compose_blueprint
from musica.project import MusicaProject, create_project
from musica.routed_mixer import build_routed_mix_plan, render_routed_mix
from musica.routing_contracts import (
    routing_material_from_blueprint,
    routing_material_sha256,
)
from musica.routing_edit import (
    accept_routing_edit_preview,
    build_routing_edit_preview,
)
from musica.studio_audio import StudioAudioSurface

ROOT = Path(__file__).resolve().parents[1]
INTENT = ROOT / "examples" / "intents" / "dark-electronic-12s.json"


def _blueprint() -> dict:
    return compose_blueprint(json.loads(INTENT.read_text(encoding="utf-8")))


def _wav_bytes(value: int, *, rate: int = 8000, frames: int = 800) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        payload = bytearray()
        for _ in range(frames):
            payload.extend(int(value).to_bytes(2, "little", signed=True))
        writer.writeframes(bytes(payload))
    return stream.getvalue()


def _audio_source(parent: dict) -> dict:
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
    }


def _audio_candidate(parent: dict, candidate_id: str, operations: list[dict]) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_audio_material",
        "source": _audio_source(parent),
        "actor": {"kind": "user", "actor_id": "mram-r1-test"},
        "reason": candidate_id,
        "operations": operations,
        "preview_only": True,
    }


def _routing_source(parent: dict) -> dict:
    material = routing_material_from_blueprint(parent)
    assert material is not None
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(material),
    }


def _routing_candidate(parent: dict, candidate_id: str, operations: list[dict]) -> dict:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_routing_material",
        "source": _routing_source(parent),
        "actor": {"kind": "user", "actor_id": "mram-r1-test"},
        "reason": candidate_id,
        "operations": operations,
        "preview_only": True,
    }


def _accept_audio(tmp_path: Path):
    root = _blueprint()
    project = create_project(tmp_path / "song.musica", root)
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    a.write_bytes(_wav_bytes(16384))
    b.write_bytes(_wav_bytes(8192))
    aa = import_audio_asset(project, a)
    bb = import_audio_asset(project, b)
    candidate = _audio_candidate(
        root,
        "R1-AUDIO",
        [
            {"operation_id":"A-T1","op":"ADD_TRACK","track_id":"AT-001","order":0,"name":"A"},
            {"operation_id":"A-T2","op":"ADD_TRACK","track_id":"AT-002","order":1,"name":"B"},
            {"operation_id":"A-C1","op":"ADD_CLIP","target":{"track_id":"AT-001"},"clip":{"clip_id":"AC-001","asset_id":aa["asset_id"],"timeline_start_seconds":0.0,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
            {"operation_id":"A-C2","op":"ADD_CLIP","target":{"track_id":"AT-002"},"clip":{"clip_id":"AC-002","asset_id":bb["asset_id"],"timeline_start_seconds":0.0,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
        ],
    )
    preview = build_audio_edit_preview(project, root, candidate)
    assert preview.ready
    record = accept_audio_edit_preview(project, preview)
    return project, project.read_revision(record["revision_id"])


def _initial_routing_ops() -> list[dict]:
    return [
        {
            "operation_id":"R-N1","op":"ADD_NODE",
            "node":{"node_id":"BUS-001","order":0,"name":"Music Bus","node_type":"group","mixer":{"gain_db":0.0,"pan":0.0,"mute":False},"output_node_id":"MASTER-001"},
        },
        {
            "operation_id":"R-N2","op":"ADD_NODE",
            "node":{"node_id":"RETURN-001","order":1,"name":"Return","node_type":"return","mixer":{"gain_db":0.0,"pan":0.0,"mute":False},"output_node_id":"MASTER-001"},
        },
        {
            "operation_id":"R-N3","op":"ADD_NODE",
            "node":{"node_id":"MASTER-001","order":2,"name":"Master","node_type":"master","mixer":{"gain_db":0.0,"pan":0.0,"mute":False},"output_node_id":None},
        },
        {"operation_id":"R-O1","op":"SET_TRACK_OUTPUT","track_id":"AT-001","target_node_id":"BUS-001"},
        {"operation_id":"R-O2","op":"SET_TRACK_OUTPUT","track_id":"AT-002","target_node_id":"MASTER-001"},
        {
            "operation_id":"R-S1","op":"ADD_SEND",
            "send":{"send_id":"SEND-001","source":{"kind":"track","source_id":"AT-001"},"target_node_id":"RETURN-001","gain_db":-12.0,"tap":"post_fader"},
        },
    ]


def _accept_routing(tmp_path: Path):
    project, accepted = _accept_audio(tmp_path)
    before_id = accepted["project"]["revision_id"]
    candidate = _routing_candidate(accepted, "R1-ROUTING", _initial_routing_ops())
    preview = build_routing_edit_preview(project, accepted, candidate)
    assert preview.ready and preview.blueprint is not None
    assert project.head_revision_id("main") == before_id

    with pytest.raises(ContractError, match="routing material changes require trusted routing"):
        project.commit_revision(preview.blueprint)

    record = accept_routing_edit_preview(project, preview)
    assert record["parent_revision_id"] == before_id
    assert project.head_revision_id("main") == record["revision_id"]
    with pytest.raises(ContractError, match="stale|HEAD changed"):
        accept_routing_edit_preview(project, preview)
    return project, project.read_revision(record["revision_id"])


def test_routing_preview_accept_is_source_bound_and_generic_commit_stays_closed(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    material = routing_material_from_blueprint(routed)
    assert material is not None
    assert [node["node_id"] for node in material["nodes"]] == [
        "BUS-001","RETURN-001","MASTER-001"
    ]
    assert project.verify_integrity()["status"] == "PASS"


def test_routed_mix_plan_and_wav_are_byte_reproducible(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    revision_id = routed["project"]["revision_id"]
    plan_a = build_routed_mix_plan(project, revision_id, mix_sample_rate_hz=8000)
    plan_b = build_routed_mix_plan(project, revision_id, mix_sample_rate_hz=8000)
    assert plan_a == plan_b
    assert plan_a["routing"]["master_node_id"] == "MASTER-001"
    render_a = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    render_b = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    assert render_a.plan == render_b.plan
    assert render_a.wav_bytes == render_b.wav_bytes
    assert render_a.wav_sha256 == render_b.wav_sha256
    assert render_a.report()["rendered_audio_is_canonical"] is False


def test_controlled_send_gain_change_changes_only_derived_routed_output(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    before_id = routed["project"]["revision_id"]
    before = render_routed_mix(project, before_id, mix_sample_rate_hz=8000)
    candidate = _routing_candidate(
        routed,
        "R1-SEND-GAIN",
        [{"operation_id":"R-SG1","op":"SET_SEND_GAIN","send_id":"SEND-001","gain_db":-3.0}],
    )
    preview = build_routing_edit_preview(project, routed, candidate)
    assert preview.ready
    assert project.head_revision_id("main") == before_id
    record = accept_routing_edit_preview(project, preview)
    after = render_routed_mix(project, record["revision_id"], mix_sample_rate_hz=8000)
    assert after.plan["routed_mix_plan_sha256"] != before.plan["routed_mix_plan_sha256"]
    assert after.wav_sha256 != before.wav_sha256


def test_routed_reopen_preserves_exact_plan_and_wav(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    revision_id = routed["project"]["revision_id"]
    before = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    archive = project.export_to(tmp_path / "routed.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    restored = reopened.read_revision(revision_id)
    assert routing_material_from_blueprint(restored) == routing_material_from_blueprint(routed)
    after = render_routed_mix(reopened, revision_id, mix_sample_rate_hz=8000)
    assert after.plan == before.plan
    assert after.wav_bytes == before.wav_bytes
    assert reopened.verify_integrity()["status"] == "PASS"


def test_cycle_and_stale_routing_preview_fail_closed(tmp_path: Path) -> None:
    project, accepted = _accept_audio(tmp_path)
    bad_ops = _initial_routing_ops()
    bad_ops[0] = {
        "operation_id":"R-N1","op":"ADD_NODE",
        "node":{"node_id":"BUS-001","order":0,"name":"Music Bus","node_type":"group","mixer":{"gain_db":0.0,"pan":0.0,"mute":False},"output_node_id":"RETURN-001"},
    }
    bad_ops[1] = {
        "operation_id":"R-N2","op":"ADD_NODE",
        "node":{"node_id":"RETURN-001","order":1,"name":"Return","node_type":"return","mixer":{"gain_db":0.0,"pan":0.0,"mute":False},"output_node_id":"BUS-001"},
    }
    blocked = build_routing_edit_preview(
        project, accepted, _routing_candidate(accepted, "R1-CYCLE", bad_ops)
    )
    assert not blocked.ready
    assert blocked.authority_result["conflicts"][0]["code"] == "INVALID_GRAPH"

    good = build_routing_edit_preview(
        project, accepted, _routing_candidate(accepted, "R1-STALE", _initial_routing_ops())
    )
    assert good.ready
    audio_change = _audio_candidate(
        accepted,
        "R1-AUDIO-ADVANCE",
        [{"operation_id":"A-GAIN","op":"SET_CLIP_GAIN","target":{"track_id":"AT-001","clip_id":"AC-001"},"gain_db":-1.0}],
    )
    audio_preview = build_audio_edit_preview(project, accepted, audio_change)
    assert audio_preview.ready
    accept_audio_edit_preview(project, audio_preview)
    with pytest.raises(ContractError, match="stale|HEAD changed"):
        accept_routing_edit_preview(project, good)


def test_existing_audio_edit_authority_remains_usable_after_routing_accept(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    before_routing = routing_material_from_blueprint(routed)
    assert before_routing is not None
    candidate = _audio_candidate(
        routed,
        "R1-POST-ROUTING-AUDIO",
        [
            {
                "operation_id": "A-POST-GAIN",
                "op": "SET_CLIP_GAIN",
                "target": {"track_id": "AT-001", "clip_id": "AC-001"},
                "gain_db": -2.0,
            }
        ],
    )
    preview = build_audio_edit_preview(project, routed, candidate)
    assert preview.ready and preview.blueprint is not None
    assert routing_material_from_blueprint(preview.blueprint) == before_routing
    record = accept_audio_edit_preview(project, preview)
    accepted = project.read_revision(record["revision_id"])
    assert routing_material_from_blueprint(accepted) == before_routing
    assert project.verify_integrity()["status"] == "PASS"


def test_studio_audio_audition_uses_routed_mixer_when_routing_is_accepted(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    surface = StudioAudioSurface(object())  # _render_blueprint needs only its render cache.
    rendered = surface._render_blueprint(
        "mram-r1-test-session",
        project,
        routed,
        source_kind="accepted",
    )
    assert "routed_mix_plan_sha256" in rendered.plan
    direct = render_routed_mix(
        project,
        routed["project"]["revision_id"],
        mix_sample_rate_hz=8000,
    )
    assert rendered.wav_sha256 == direct.wav_sha256
