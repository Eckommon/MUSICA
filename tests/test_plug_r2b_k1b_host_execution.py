"""PLUG-R2B K1-B accepted simulated processor authority -> real PCM alignment."""
from __future__ import annotations

import copy
import hashlib
import io
from pathlib import Path
import struct
import wave

import pytest

from musica.bus_host_edit import accept_bus_host_edit_preview, build_bus_host_edit_preview
from musica.bus_host_material import accepted_bus_host_sha256, bus_host_material_from_blueprint
from musica.bus_host_runtime import (
    render_accepted_simulated_bus_host,
    validate_accepted_bus_host_processing_plan,
    validate_bus_host_processing_plan,
)
from musica.contracts import ContractError
from musica.evidence import canonical_json_bytes
from musica.project import MusicaProject
from musica.routed_mixer import render_routed_mix
from test_plug_r2b_k1_accepted_bridge import _accepted_two_buses
from test_plug_r2b_k1b_accepted_bus_host import _candidate, _instance, _material, _accept


def _frames(payload: bytes) -> list[tuple[int, int]]:
    with wave.open(io.BytesIO(payload)) as reader:
        assert reader.getframerate() == 8000 and reader.getnchannels() == 2
        assert reader.getsampwidth() == 2
        return list(struct.iter_unpack("<hh", reader.readframes(reader.getnframes())))


def _two_processors():
    return _material([
        _instance(latency=3),
        _instance("BUS-002", instance_id="BPI-002", latency=9),
    ])


def test_empty_host_preserves_exact_preexisting_routed_wav(tmp_path: Path):
    project, revision = _accepted_two_buses(tmp_path)
    baseline = render_routed_mix(project, revision, mix_sample_rate_hz=8000)
    host = render_accepted_simulated_bus_host(
        project, revision, sample_rate_hz=8000
    )
    assert host.plan["mode"] == "legacy_routed_byte_exact_no_bus_processors"
    assert host.kernel_plan is None
    assert host.wav_bytes == baseline.wav_bytes
    assert host.wav_sha256 == baseline.wav_sha256
    validate_accepted_bus_host_processing_plan(
        project, revision, host.plan, sample_rate_hz=8000
    )


def test_accepted_bus_processor_pdc_is_audible_and_source_bound(tmp_path: Path):
    project, revision = _accepted_two_buses(tmp_path)
    parent = project.read_revision(revision)
    accepted = _accept(project, parent, _two_processors(), "PAIR")
    rid = accepted["project"]["revision_id"]
    before_head = project.head_revision_id("main")
    a = render_accepted_simulated_bus_host(project, rid, sample_rate_hz=8000)
    b = render_accepted_simulated_bus_host(project, rid, sample_rate_hz=8000)
    assert a.plan == b.plan and a.wav_bytes == b.wav_bytes
    assert a.plan["mode"] == "accepted_two_bus_simulated_reference_pdc"
    assert a.plan["source"]["bus_host_material_sha256"] == accepted_bus_host_sha256(accepted)
    assert a.kernel_plan is not None
    offsets = {x["path_id"]: x["compensation_frames"] for x in a.kernel_plan["paths"]}
    assert offsets == {"BUS-001": 6, "BUS-002": 0}
    assert a.kernel_plan["reference_algorithmic_latency_frames"] == 9
    pcm = _frames(a.wav_bytes)
    assert len(pcm) == 96000
    assert pcm[:9] == [(0, 0)] * 9
    assert pcm[9] == (24576, 24576)
    validate_accepted_bus_host_processing_plan(
        project, rid, a.plan, sample_rate_hz=8000
    )
    assert project.head_revision_id("main") == before_head


def test_creative_delay_bypass_remove_and_legacy_identity(tmp_path: Path):
    project, revision = _accepted_two_buses(tmp_path)
    parent = project.read_revision(revision)
    accepted = _accept(project, parent, _two_processors(), "PAIR")
    changed = _accept(project, accepted, _material([
        _instance(latency=3, creative=5),
        _instance("BUS-002", instance_id="BPI-002", latency=9),
    ]), "CREATIVE")
    creative = render_accepted_simulated_bus_host(
        project, changed["project"]["revision_id"], sample_rate_hz=8000
    )
    pcm = _frames(creative.wav_bytes)
    assert pcm[9] == (8192, 8192)
    assert pcm[14] == (24576, 24576)
    # Bypass cancels algorithmic latency, but the separately accepted creative
    # path delay is intentionally preserved, not silently removed.
    bypassed = _accept(project, changed, _material([
        _instance(latency=3, creative=5, bypass=True),
        _instance("BUS-002", instance_id="BPI-002", latency=9),
    ]), "BYPASS")
    output = render_accepted_simulated_bus_host(
        project, bypassed["project"]["revision_id"], sample_rate_hz=8000
    )
    offsets = {i["path_id"]: i["compensation_frames"] for i in output.kernel_plan["paths"]}
    assert offsets == {"BUS-001": 9, "BUS-002": 0}
    assert _frames(output.wav_bytes)[9] == (8192, 8192)
    assert _frames(output.wav_bytes)[14] == (24576, 24576)
    removed = _accept(project, bypassed, _material([]), "REMOVE")
    rid = removed["project"]["revision_id"]
    baseline = render_routed_mix(project, rid, mix_sample_rate_hz=8000)
    empty = render_accepted_simulated_bus_host(project, rid, sample_rate_hz=8000)
    assert empty.plan["mode"] == "legacy_routed_byte_exact_no_bus_processors"
    assert empty.wav_bytes == baseline.wav_bytes


def test_error_and_rehashed_derived_plan_fail_closed(tmp_path: Path):
    project, revision = _accepted_two_buses(tmp_path)
    accepted = _accept(project, project.read_revision(revision), _two_processors(), "PAIR")
    rid = accepted["project"]["revision_id"]
    head = project.head_revision_id("main")
    with pytest.raises(ContractError, match="forced processor error"):
        render_accepted_simulated_bus_host(
            project, rid, sample_rate_hz=8000,
            force_error_instance_ids={"BPI-001"},
        )
    with pytest.raises(ContractError, match="unknown"):
        render_accepted_simulated_bus_host(
            project, rid, sample_rate_hz=8000,
            force_error_instance_ids={"BPI-FORGED"},
        )
    original = render_accepted_simulated_bus_host(project, rid, sample_rate_hz=8000)
    plan = copy.deepcopy(original.plan)
    plan["source"]["bus_host_material_sha256"] = "f" * 64
    base = dict(plan)
    base.pop("bus_host_processing_plan_sha256")
    plan["bus_host_processing_plan_sha256"] = hashlib.sha256(
        canonical_json_bytes(base)
    ).hexdigest()
    validate_bus_host_processing_plan(plan)
    with pytest.raises(ContractError, match="stale or forged"):
        validate_accepted_bus_host_processing_plan(
            project, rid, plan, sample_rate_hz=8000
        )
    assert project.head_revision_id("main") == head


def test_accepted_host_reopen_bytes_and_plan_are_identical(tmp_path: Path):
    project, revision = _accepted_two_buses(tmp_path)
    accepted = _accept(project, project.read_revision(revision), _two_processors(), "PAIR")
    rid = accepted["project"]["revision_id"]
    a = render_accepted_simulated_bus_host(project, rid, sample_rate_hz=8000)
    archive = project.export_to(tmp_path / "k1-b.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "k1-b-reopened.musica")
    b = render_accepted_simulated_bus_host(reopened, rid, sample_rate_hz=8000)
    assert a.plan == b.plan
    assert a.wav_bytes == b.wav_bytes
    assert bus_host_material_from_blueprint(reopened.read_revision(rid)) == _two_processors()


def test_empty_host_never_silently_skips_existing_r1_master_chain(tmp_path: Path):
    from musica.plugin_edit import build_plugin_edit_preview, accept_plugin_edit_preview
    from musica.plugin_reference import render_accepted_plugins
    from test_plug_r1_accepted_plugin_authority import _candidate as r1_candidate, _add_op as r1_add
    project, revision = _accepted_two_buses(tmp_path)
    parent = project.read_revision(revision)
    candidate = r1_candidate(parent, "K1-B-R1-COMPAT", [r1_add()])
    preview = build_plugin_edit_preview(project, parent, candidate)
    assert preview.ready
    record = accept_plugin_edit_preview(project, preview)
    rid = record["revision_id"]
    assert render_accepted_plugins(project, rid, sample_rate_hz=8000).wav_bytes
    with pytest.raises(ContractError, match="does not silently skip accepted R1"):
        render_accepted_simulated_bus_host(project, rid, sample_rate_hz=8000)
