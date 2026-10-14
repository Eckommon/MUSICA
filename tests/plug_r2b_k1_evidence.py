"""Deterministic K1 source-bound two-bus reference evidence (not host PDC)."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from musica.evidence import canonical_json_bytes
from musica.plugin_host_bridge import render_accepted_bus_detached_alignment

# The reusable *test fixture* contains the accepted Audio + Routing Preview→Accept
# setup. This is evidence-only; the production bridge never imports tests.
from test_plug_r2b_k1_accepted_bridge import (
    _accepted_two_buses, _config, _pcm
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = [
    "src/musica/plugin_host_topology.py",
    "src/musica/plugin_host_bridge.py",
    "src/musica/plugin_alignment_reference.py",
    "tests/test_plug_r2b_k1_host_topology.py",
    "tests/test_plug_r2b_k1_accepted_bridge.py",
    "tests/plug_r2b_k1_evidence.py",
    "docs/PLUG_R2B_K1_ACCEPTED_HOST_CONTRACT.md",
    ".github/workflows/plug-r2b-k1-accepted-bus-reference-evidence.yml",
]


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_bytes(canonical_json_bytes(value))


def generate(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="musica-r2b-k1-") as temporary:
        project, revision = _accepted_two_buses(Path(temporary))
        before_head = project.head_revision_id("main")
        source, aligned = render_accepted_bus_detached_alignment(
            project, revision, sample_rate_hz=8000,
            latency_config_by_bus_id=_config()
        )
        _, dry = render_accepted_bus_detached_alignment(
            project, revision, sample_rate_hz=8000,
            latency_config_by_bus_id=_config(), compensate=False
        )
        _, creative = render_accepted_bus_detached_alignment(
            project, revision, sample_rate_hz=8000,
            latency_config_by_bus_id=_config(creative_a=5)
        )
        _, bypass = render_accepted_bus_detached_alignment(
            project, revision, sample_rate_hz=8000,
            latency_config_by_bus_id=_config(bypass_a=True)
        )
        expected = {
            "source": source.source,
            "source_provenance_sha256": source.provenance_sha256,
            "detached_plan": aligned.plan,
            "classification": "R2B_K1_ACCEPTED_BUSES_DETACHED_LATENCY_ONLY",
            "host_pdc_integrated": False,
            "accepted_host_plugin_authority": False,
        }
        _write_json(out / "derived-reference.json", expected)
        for name, raw in sorted(source.path_wav_by_id.items()):
            (out / f"input-{name}.wav").write_bytes(raw)
        for name, wav in [
            ("uncompensated.wav", dry.wav_bytes),
            ("compensated.wav", aligned.wav_bytes),
            ("creative-preserved.wav", creative.wav_bytes),
            ("bypass-recomputed.wav", bypass.wav_bytes),
        ]:
            (out / name).write_bytes(wav)

        first_input_a = _pcm(source.path_wav_by_id["BUS-001"])[0]
        first_input_b = _pcm(source.path_wav_by_id["BUS-002"])[0]
        uncomp = _pcm(dry.wav_bytes)
        comp = _pcm(aligned.wav_bytes)
        creative_frames = _pcm(creative.wav_bytes)
        bypass_frames = _pcm(bypass.wav_bytes)
        assert first_input_a == (16384, 16384)
        assert first_input_b == (8192, 8192)
        assert uncomp[3] == (16384, 16384)
        assert all(pair == (0, 0) for pair in comp[:9])
        assert comp[9] == (24576, 24576)
        assert creative_frames[9] == (8192, 8192)
        assert creative_frames[14] == (24576, 24576)
        assert bypass_frames[9] == (24576, 24576)
        assert project.head_revision_id("main") == before_head

        _write_json(out / "proof.json", {
            "proof_version": "0",
            "classification": "ACCEPTED_TWO_BUSES_DETACHED_REFERENCE_NOT_HOST_PDC",
            "source_revision_id": revision,
            "pre_master_pcm16_boundary": True,
            "first_source_samples": [first_input_a[0], first_input_b[0]],
            "uncompensated_first_bus_a_frame": 3,
            "compensated_common_frame": 9,
            "compensated_common_sample": list(comp[9]),
            "creative_delay_preserved_bus_a_frame": 14,
            "bypass_recomputed_common_frame": 9,
            "accepted_head_unchanged": True,
            "real_native_host_pdc_claimed": False,
        })

    manifest = {
        "version": "0",
        "classification": "PLUG_R2B_K1_ACCEPTED_SOURCE_DETACHED_LATENCY_EVIDENCE",
        "artifacts": [],
        "contracts": [],
    }
    for p in sorted(out.iterdir()):
        raw = p.read_bytes()
        manifest["artifacts"].append({
            "path": p.name, "sha256": _sha(raw), "bytes": len(raw),
        })
    for name in CONTRACTS:
        raw = (ROOT / name).read_bytes()
        manifest["contracts"].append({
            "path": name, "sha256": _sha(raw), "bytes": len(raw),
        })
    _write_json(out / "manifest.json", manifest)


if __name__ == "__main__":
    output = Path(os.environ.get(
        "MUSICA_PLUG_R2B_K1_OUT", "artifacts/plug-r2b-k1-reference"
    ))
    generate(output)
    print("PLUG-R2B K1 accepted-source/detached-latency evidence generated")
