"""PLUG-R2B K1: accepted track/bus audio, detached synthetic latency bridge."""
from __future__ import annotations

import io
from pathlib import Path
import struct
import wave

import pytest

from musica.contracts import ContractError
from musica.plugin_host_bridge import (
    build_accepted_bus_reference_inputs,
    render_accepted_bus_detached_alignment,
)
from musica.project import MusicaProject
from musica.routing_edit import build_routing_edit_preview, accept_routing_edit_preview
from test_mram_r1_routing_authority_mixer import _accept_audio, _routing_candidate


def _accepted_two_buses(tmp_path: Path):
    project, parent = _accept_audio(tmp_path)
    mixer = {"gain_db": 0.0, "pan": 0.0, "mute": False}
    ops = [
        {"operation_id": "K1-BUS-A", "op": "ADD_NODE",
         "node": {"node_id": "BUS-001", "order": 0, "name": "Bus A",
                  "node_type": "bus", "mixer": mixer, "output_node_id": "MASTER-001"}},
        {"operation_id": "K1-BUS-B", "op": "ADD_NODE",
         "node": {"node_id": "BUS-002", "order": 1, "name": "Bus B",
                  "node_type": "bus", "mixer": mixer, "output_node_id": "MASTER-001"}},
        {"operation_id": "K1-MASTER", "op": "ADD_NODE",
         "node": {"node_id": "MASTER-001", "order": 2, "name": "Master",
                  "node_type": "master", "mixer": mixer, "output_node_id": None}},
        {"operation_id": "K1-OUT-A", "op": "SET_TRACK_OUTPUT",
         "track_id": "AT-001", "target_node_id": "BUS-001"},
        {"operation_id": "K1-OUT-B", "op": "SET_TRACK_OUTPUT",
         "track_id": "AT-002", "target_node_id": "BUS-002"},
    ]
    preview = build_routing_edit_preview(
        project, parent, _routing_candidate(parent, "K1-ROUTE", ops)
    )
    assert preview.ready
    record = accept_routing_edit_preview(project, preview)
    return project, record["revision_id"]


def _pcm(raw: bytes) -> list[tuple[int, int]]:
    with wave.open(io.BytesIO(raw), "rb") as reader:
        assert reader.getnchannels() == 2
        assert reader.getsampwidth() == 2
        assert reader.getframerate() == 8000
        return list(struct.iter_unpack("<hh", reader.readframes(reader.getnframes())))


def _config(*, bypass_a: bool = False, creative_a: int = 0):
    return {
        "BUS-001": {
            "algorithmic_latency_frames": 3,
            "creative_delay_frames": creative_a,
            "bypass": bypass_a,
        },
        "BUS-002": {
            "algorithmic_latency_frames": 9,
            "creative_delay_frames": 0,
            "bypass": False,
        },
    }


def test_real_accepted_revision_bridges_exact_two_independent_bus_sources(tmp_path):
    project, revision = _accepted_two_buses(tmp_path)
    before_head = project.head_revision_id("main")
    a = build_accepted_bus_reference_inputs(
        project, revision, sample_rate_hz=8000
    )
    b = build_accepted_bus_reference_inputs(
        project, revision, sample_rate_hz=8000
    )
    assert a == b
    assert a.source["revision_id"] == revision
    assert a.source["host_pdc_integrated"] is False
    assert a.source["accepted_host_plugin_authority"] is False
    assert set(a.path_wav_by_id) == {"BUS-001", "BUS-002"}
    bus_a = _pcm(a.path_wav_by_id["BUS-001"])
    bus_b = _pcm(a.path_wav_by_id["BUS-002"])
    assert bus_a[0] == (16384, 16384)
    assert bus_b[0] == (8192, 8192)
    assert project.head_revision_id("main") == before_head


def test_compensation_is_audible_and_creative_offset_stays_independent(tmp_path):
    project, revision = _accepted_two_buses(tmp_path)
    before_head = project.head_revision_id("main")
    source, aligned = render_accepted_bus_detached_alignment(
        project, revision, sample_rate_hz=8000,
        latency_config_by_bus_id=_config(),
    )
    assert source.source["accepted_host_plugin_authority"] is False
    offsets = {item["path_id"]: item["compensation_frames"] for item in aligned.plan["paths"]}
    assert offsets == {"BUS-001": 6, "BUS-002": 0}
    samples = _pcm(aligned.wav_bytes)
    assert all(pair == (0, 0) for pair in samples[:9])
    assert samples[9] == (24576, 24576)
    assert aligned == render_accepted_bus_detached_alignment(
        project, revision, sample_rate_hz=8000,
        latency_config_by_bus_id=_config(),
    )[1]
    _, uncompensated = render_accepted_bus_detached_alignment(
        project, revision, sample_rate_hz=8000,
        latency_config_by_bus_id=_config(), compensate=False
    )
    assert _pcm(uncompensated.wav_bytes)[3] == (16384, 16384)
    assert _pcm(uncompensated.wav_bytes)[9] == (24576, 24576)
    _, creative = render_accepted_bus_detached_alignment(
        project, revision, sample_rate_hz=8000,
        latency_config_by_bus_id=_config(creative_a=5)
    )
    assert _pcm(creative.wav_bytes)[9] == (8192, 8192)
    assert _pcm(creative.wav_bytes)[14] == (24576, 24576)
    _, bypassed = render_accepted_bus_detached_alignment(
        project, revision, sample_rate_hz=8000,
        latency_config_by_bus_id=_config(bypass_a=True)
    )
    offsets_after_bypass = {item["path_id"]: item["compensation_frames"] for item in bypassed.plan["paths"]}
    assert offsets_after_bypass == {"BUS-001": 9, "BUS-002": 0}
    assert _pcm(bypassed.wav_bytes)[9] == (24576, 24576)
    assert project.head_revision_id("main") == before_head


def test_forged_owner_invalid_rate_and_forced_processor_fail_closed(tmp_path):
    project, revision = _accepted_two_buses(tmp_path)
    before_head = project.head_revision_id("main")
    wrong_config = _config()
    wrong_config["BUS-FAKE"] = wrong_config.pop("BUS-001")
    with pytest.raises(ContractError, match="accepted bus owner"):
        render_accepted_bus_detached_alignment(
            project, revision, sample_rate_hz=8000,
            latency_config_by_bus_id=wrong_config,
        )
    with pytest.raises(ContractError):
        render_accepted_bus_detached_alignment(
            project, revision, sample_rate_hz=16000,
            latency_config_by_bus_id=_config(),
        )
    with pytest.raises(ContractError, match="forced processor error"):
        render_accepted_bus_detached_alignment(
            project, revision, sample_rate_hz=8000,
            latency_config_by_bus_id=_config(),
            force_error_path_ids={"BUS-001"},
        )
    assert project.head_revision_id("main") == before_head


def test_export_import_reopen_rebuilds_exact_sources_and_pcm(tmp_path):
    project, revision = _accepted_two_buses(tmp_path)
    before, rendered = render_accepted_bus_detached_alignment(
        project, revision, sample_rate_hz=8000,
        latency_config_by_bus_id=_config(),
    )
    archive = project.export_to(tmp_path / "two-bus.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "reopened.musica")
    after, replayed = render_accepted_bus_detached_alignment(
        reopened, revision, sample_rate_hz=8000,
        latency_config_by_bus_id=_config(),
    )
    assert before.provenance_sha256 == after.provenance_sha256
    assert before.path_wav_by_id == after.path_wav_by_id
    assert rendered.plan == replayed.plan
    assert rendered.wav_bytes == replayed.wav_bytes
