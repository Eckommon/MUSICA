"""Deterministic accepted simulated two-bus host/PDC evidence.

Proves explicit trusted Preview→Accept and actual PCM. Does NOT prove native
third-party binary latency discovery, realtime PDC or Studio integration.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import wave

from musica.bus_host_material import bus_host_material_from_blueprint
from musica.bus_host_runtime import render_accepted_simulated_bus_host
from musica.contracts import ContractError
from musica.evidence import canonical_json_bytes
from musica.project import MusicaProject
from musica.routed_mixer import render_routed_mix
from test_plug_r2b_k1_accepted_bridge import _accepted_two_buses
from test_plug_r2b_k1b_accepted_bus_host import _accept, _instance, _material

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = [
    "schemas/music-blueprint-v0.schema.json",
    "schemas/accepted-bus-host-material-v0.schema.json",
    "schemas/bus-host-edit-candidate-v0.schema.json",
    "schemas/bus-host-processing-plan-v0.schema.json",
    "src/musica/contracts.py",
    "src/musica/project.py",
    "src/musica/bus_host_material.py",
    "src/musica/bus_host_edit.py",
    "src/musica/bus_host_runtime.py",
    "src/musica/plugin_host_bridge.py",
    "tests/test_plug_r2b_k1b_accepted_bus_host.py",
    "tests/test_plug_r2b_k1b_host_execution.py",
    "tests/plug_r2b_k1b_evidence.py",
    ".github/workflows/plug-r2b-k1b-accepted-bus-host-evidence.yml",
]


def _sha(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def _write_json(path: Path, data: object) -> None:
    path.write_bytes(canonical_json_bytes(data))


def _frames(wav: bytes) -> list[tuple[int, int]]:
    with wave.open(io.BytesIO(wav)) as w:
        assert w.getframerate() == 8000
        assert w.getnchannels() == 2 and w.getsampwidth() == 2
        return list(struct.iter_unpack("<hh", w.readframes(w.getnframes())))


def run(output: Path) -> dict:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="musica-k1b-") as value:
        project, baseline_revision = _accepted_two_buses(Path(value))
        parent = project.read_revision(baseline_revision)
        baseline = render_accepted_simulated_bus_host(
            project, baseline_revision, sample_rate_hz=8000
        )
        routed = render_routed_mix(
            project, baseline_revision, mix_sample_rate_hz=8000
        )
        assert baseline.wav_bytes == routed.wav_bytes
        material = _material([
            _instance(latency=3),
            _instance("BUS-002", instance_id="BPI-002", latency=9),
        ])
        accepted = _accept(project, parent, material, "EVIDENCE-PAIR")
        revision = accepted["project"]["revision_id"]
        head_before = project.head_revision_id("main")
        processed = render_accepted_simulated_bus_host(
            project, revision, sample_rate_hz=8000
        )
        replay = render_accepted_simulated_bus_host(
            project, revision, sample_rate_hz=8000
        )
        assert processed.plan == replay.plan and processed.wav_bytes == replay.wav_bytes
        assert processed.kernel_plan is not None
        assert _frames(processed.wav_bytes)[:9] == [(0, 0)] * 9
        assert _frames(processed.wav_bytes)[9] == (24576, 24576)
        offsets = {
            p["path_id"]: p["compensation_frames"]
            for p in processed.kernel_plan["paths"]
        }
        assert offsets == {"BUS-001": 6, "BUS-002": 0}

        forced_blocked = False
        try:
            render_accepted_simulated_bus_host(
                project, revision, sample_rate_hz=8000,
                force_error_instance_ids={"BPI-001"},
            )
        except ContractError:
            forced_blocked = True
        assert forced_blocked
        assert project.head_revision_id("main") == head_before

        changed = _accept(project, accepted, _material([
            _instance(latency=3, creative=5),
            _instance("BUS-002", instance_id="BPI-002", latency=9),
        ]), "EVIDENCE-CREATIVE")
        creative = render_accepted_simulated_bus_host(
            project, changed["project"]["revision_id"], sample_rate_hz=8000
        )
        assert _frames(creative.wav_bytes)[9] == (8192, 8192)
        assert _frames(creative.wav_bytes)[14] == (24576, 24576)

        bypassed = _accept(project, changed, _material([
            _instance(latency=3, creative=5, bypass=True),
            _instance("BUS-002", instance_id="BPI-002", latency=9),
        ]), "EVIDENCE-BYPASS")
        bypass = render_accepted_simulated_bus_host(
            project, bypassed["project"]["revision_id"], sample_rate_hz=8000
        )
        assert {p["path_id"]: p["compensation_frames"]
                for p in bypass.kernel_plan["paths"]} == {"BUS-001": 9, "BUS-002": 0}
        assert _frames(bypass.wav_bytes)[9] == (8192, 8192)
        assert _frames(bypass.wav_bytes)[14] == (24576, 24576)

        removed = _accept(project, bypassed, _material([]), "EVIDENCE-REMOVE")
        rid_removed = removed["project"]["revision_id"]
        empty = render_accepted_simulated_bus_host(
            project, rid_removed, sample_rate_hz=8000
        )
        original = render_routed_mix(project, rid_removed, mix_sample_rate_hz=8000)
        assert empty.wav_bytes == original.wav_bytes

        archive = project.export_to(output / "accepted-project.musica.zip")
        reopened = MusicaProject.import_from(
            archive, Path(value) / "reopened.musica"
        )
        reopened_processed = render_accepted_simulated_bus_host(
            reopened, revision, sample_rate_hz=8000
        )
        assert reopened_processed.plan == processed.plan
        assert reopened_processed.wav_bytes == processed.wav_bytes

        _write_json(output / "accepted-bus-material.json", bus_host_material_from_blueprint(accepted))
        _write_json(output / "derived-plan.json", processed.plan)
        _write_json(output / "kernel-plan.json", processed.kernel_plan)
        for name, payload in [
            ("baseline.wav", baseline.wav_bytes),
            ("accepted-pdc.wav", processed.wav_bytes),
            ("creative.wav", creative.wav_bytes),
            ("bypass.wav", bypass.wav_bytes),
            ("removed.wav", empty.wav_bytes),
        ]:
            (output / name).write_bytes(payload)
        _write_json(output / "proof.json", {
            "version": "0",
            "classification": "K1B_ACCEPTED_SIMULATED_BUS_PROCESSOR_OFFLINE_ONLY",
            "accepted_revision_id": revision,
            "reference_latency_frames": 9,
            "compensation_by_bus": offsets,
            "first_aligned_frame": 9,
            "first_aligned_stereo_pcm": [24576, 24576],
            "creative_delay_preserved_at_frame": 14,
            "bypass_recalculated": True,
            "no_processors_exact_legacy_routed_wav": True,
            "forced_processor_error_blocked": True,
            "accepted_head_unchanged_by_runtime": True,
            "reopen_exact_wav_and_plan": True,
            "native_third_party_latency_reporting": False,
            "realtime_plugin_host": False,
            "studio_pdc_integrated": False,
        })
    manifest = {
        "version": "0",
        "classification": "PLUG_R2B_K1B_ACCEPTED_SIMULATED_OFFLINE_EVIDENCE",
        "artifacts": [],
        "contracts": [],
    }
    for f in sorted(output.iterdir()):
        raw = f.read_bytes()
        manifest["artifacts"].append({
            "path": f.name, "sha256": _sha(raw), "bytes": len(raw)
        })
    for name in CONTRACTS:
        raw = (ROOT / name).read_bytes()
        manifest["contracts"].append({
            "path": name, "sha256": _sha(raw), "bytes": len(raw)
        })
    _write_json(output / "manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    out = Path(os.environ.get(
        "MUSICA_PLUG_R2B_K1B_OUT", "artifacts/plug-r2b-k1b-accepted"
    ))
    result = run(out)
    print("Accepted simulated bus-host K1-B artifacts:", len(result["artifacts"]))
