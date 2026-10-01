from __future__ import annotations

import copy
import io
import wave
from pathlib import Path

import pytest

from musica.contracts import ContractError, validate_contract
from musica.plugin_reference import (
    build_plugin_processing_plan,
    plugin_material_sha256,
    render_simulated_plugins,
    validate_plugin_material,
)
from musica.project import MusicaProject
from musica.routed_mixer import render_routed_mix
from test_mram_r1_routing_authority_mixer import _accept_routing


def _material(
    *,
    gain_db: float = -6.0,
    delay_frames: int = 4,
    bypass: bool = False,
    owner_id: str = "MASTER-001",
) -> dict:
    return {
        "material_version": "0",
        "classification": "noncanonical_proposal",
        "descriptors": [
            {
                "plugin_id": "PLUG-REF-001",
                "format": "simulated_reference_v0",
                "vendor": "MUSICA",
                "name": "Reference Gain Delay",
                "version": "0",
                "processor_id": "musica-simulated-gain-delay-v0",
                "io": {
                    "input_channels": 2,
                    "output_channels": 2,
                    "sample_format": "float64",
                    "sample_rate_policy": "exact_match_required_no_resampling",
                },
                "latency": {
                    "mode": "state_parameter",
                    "parameter_id": "delay_frames",
                    "unit": "frames",
                },
                "parameters": [
                    {
                        "parameter_id": "gain_db",
                        "unit": "decibel",
                        "minimum": -60.0,
                        "maximum": 12.0,
                        "default": 0.0,
                    },
                    {
                        "parameter_id": "delay_frames",
                        "unit": "frames",
                        "minimum": 0.0,
                        "maximum": 4096.0,
                        "default": 0.0,
                    },
                ],
            }
        ],
        "instances": [
            {
                "instance_id": "PI-001",
                "plugin_id": "PLUG-REF-001",
                "owner": {"kind": "routing_node", "owner_id": owner_id},
                "slot": 0,
                "bypass": bypass,
                "state": {
                    "gain_db": gain_db,
                    "delay_frames": delay_frames,
                },
            }
        ],
    }


def _pcm16_frames(wav_bytes: bytes) -> list[tuple[int, int]]:
    with wave.open(io.BytesIO(wav_bytes), "rb") as reader:
        assert reader.getnchannels() == 2
        assert reader.getsampwidth() == 2
        payload = reader.readframes(reader.getnframes())
    return [
        (
            int.from_bytes(payload[offset : offset + 2], "little", signed=True),
            int.from_bytes(payload[offset + 2 : offset + 4], "little", signed=True),
        )
        for offset in range(0, len(payload), 4)
    ]


def test_plug_r0_plan_and_render_are_repeat_exact_and_latency_is_explicit(
    tmp_path: Path,
) -> None:
    project, routed = _accept_routing(tmp_path)
    revision_id = routed["project"]["revision_id"]
    material = _material(gain_db=-6.0, delay_frames=4)

    plan_a = build_plugin_processing_plan(
        project, revision_id, material, sample_rate_hz=8000
    )
    plan_b = build_plugin_processing_plan(
        project, revision_id, copy.deepcopy(material), sample_rate_hz=8000
    )
    assert plan_a == plan_b
    assert plan_a["classification"] == "derived_noncanonical"
    assert plan_a["total_effective_latency_frames"] == 4
    assert plan_a["instances"][0]["effective_latency_frames"] == 4
    assert plan_a["source"]["plugin_material_sha256"] == plugin_material_sha256(
        material
    )

    render_a = render_simulated_plugins(
        project, revision_id, material, sample_rate_hz=8000
    )
    render_b = render_simulated_plugins(
        project, revision_id, copy.deepcopy(material), sample_rate_hz=8000
    )
    assert render_a.plan == render_b.plan
    assert render_a.wav_bytes == render_b.wav_bytes
    assert render_a.wav_sha256 == render_b.wav_sha256

    baseline = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    assert render_a.wav_sha256 != baseline.wav_sha256
    frames = _pcm16_frames(render_a.wav_bytes)
    assert frames[:4] == [(0, 0)] * 4


def test_bypass_is_byte_exact_routed_baseline(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    revision_id = routed["project"]["revision_id"]
    baseline = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
    bypassed = render_simulated_plugins(
        project,
        revision_id,
        _material(gain_db=12.0, delay_frames=128, bypass=True),
        sample_rate_hz=8000,
    )
    assert bypassed.plan["total_effective_latency_frames"] == 0
    assert bypassed.wav_bytes == baseline.wav_bytes
    assert bypassed.wav_sha256 == baseline.wav_sha256


def test_controlled_gain_change_changes_plan_and_output(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    revision_id = routed["project"]["revision_id"]
    a = render_simulated_plugins(
        project,
        revision_id,
        _material(gain_db=-3.0, delay_frames=0),
        sample_rate_hz=8000,
    )
    b = render_simulated_plugins(
        project,
        revision_id,
        _material(gain_db=-12.0, delay_frames=0),
        sample_rate_hz=8000,
    )
    assert (
        a.plan["plugin_processing_plan_sha256"]
        != b.plan["plugin_processing_plan_sha256"]
    )
    assert a.wav_sha256 != b.wav_sha256
    assert b.peak_pre_clip < a.peak_pre_clip


def test_material_identity_and_configuration_fail_closed(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    revision_id = routed["project"]["revision_id"]

    wrong_owner = _material(owner_id="BUS-001")
    with pytest.raises(ContractError, match="supports only exact master"):
        build_plugin_processing_plan(
            project, revision_id, wrong_owner, sample_rate_hz=8000
        )

    unknown_plugin = _material()
    unknown_plugin["instances"][0]["plugin_id"] = "PLUG-MISSING"
    with pytest.raises(ContractError, match="unknown plugin_id"):
        build_plugin_processing_plan(
            project, revision_id, unknown_plugin, sample_rate_hz=8000
        )

    duplicate = _material()
    duplicate["instances"].append(copy.deepcopy(duplicate["instances"][0]))
    duplicate["instances"][1]["instance_id"] = "PI-002"
    with pytest.raises(ContractError, match="slot must be unique"):
        build_plugin_processing_plan(
            project, revision_id, duplicate, sample_rate_hz=8000
        )

    bad_descriptor = _material()
    bad_descriptor["descriptors"][0]["parameters"][0]["default"] = -1.0
    with pytest.raises(ContractError, match="exact canonical"):
        validate_plugin_material(bad_descriptor, blueprint=routed)

    bad_rate = _material()
    with pytest.raises(ContractError, match="sample-rate"):
        build_plugin_processing_plan(
            project, revision_id, bad_rate, sample_rate_hz=44100
        )


def test_forced_processor_error_is_fail_closed_and_project_head_is_unchanged(
    tmp_path: Path,
) -> None:
    project, routed = _accept_routing(tmp_path)
    revision_id = routed["project"]["revision_id"]
    head_before = project.head_revision_id("main")
    with pytest.raises(ContractError, match="forced processor error"):
        render_simulated_plugins(
            project,
            revision_id,
            _material(),
            sample_rate_hz=8000,
            force_error_instance_ids={"PI-001"},
        )
    assert project.head_revision_id("main") == head_before


def test_accepted_blueprint_plugin_mutation_remains_structurally_closed(
    tmp_path: Path,
) -> None:
    project, routed = _accept_routing(tmp_path)
    candidate = copy.deepcopy(routed)
    candidate["materials"]["plugins"] = _material()
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_contract(
            candidate,
            "music-blueprint-v0.schema.json",
            allow_nonempty_routing=True,
        )
    with pytest.raises(ContractError, match="schema validation failed"):
        project.commit_revision(candidate)


def test_export_import_reopen_reproduces_detached_plan_and_output(
    tmp_path: Path,
) -> None:
    project, routed = _accept_routing(tmp_path)
    revision_id = routed["project"]["revision_id"]
    material = _material(gain_db=-4.5, delay_frames=7)

    plan_before = build_plugin_processing_plan(
        project, revision_id, material, sample_rate_hz=8000
    )
    render_before = render_simulated_plugins(
        project, revision_id, material, sample_rate_hz=8000
    )

    archive = project.export_to(tmp_path / "plug-r0.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    plan_after = build_plugin_processing_plan(
        reopened, revision_id, material, sample_rate_hz=8000
    )
    render_after = render_simulated_plugins(
        reopened, revision_id, material, sample_rate_hz=8000
    )
    assert plan_after == plan_before
    assert render_after.wav_bytes == render_before.wav_bytes
    assert reopened.verify_integrity()["status"] == "PASS"


def test_serial_instance_order_and_latency_are_deterministic(tmp_path: Path) -> None:
    project, routed = _accept_routing(tmp_path)
    revision_id = routed["project"]["revision_id"]
    material = _material(gain_db=-3.0, delay_frames=3)
    second = copy.deepcopy(material["instances"][0])
    second["instance_id"] = "PI-002"
    second["slot"] = 1
    second["state"] = {"gain_db": -2.0, "delay_frames": 4}
    material["instances"].append(second)

    plan = build_plugin_processing_plan(
        project, revision_id, material, sample_rate_hz=8000
    )
    assert [item["instance_id"] for item in plan["instances"]] == ["PI-001", "PI-002"]
    assert plan["total_effective_latency_frames"] == 7

    rendered = render_simulated_plugins(
        project, revision_id, material, sample_rate_hz=8000
    )
    frames = _pcm16_frames(rendered.wav_bytes)
    assert frames[:7] == [(0, 0)] * 7
