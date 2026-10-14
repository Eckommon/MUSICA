"""K2 reproducible truthful Studio accepted-bus-host view and opt-in WAV proof."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import io
import wave
import tempfile

from musica.evidence import canonical_json_bytes
from musica.bus_host_runtime import render_accepted_simulated_bus_host
from musica.studio_bus_plugins import StudioBusHostSurface
from test_plug_r2b_k2_studio_bus_plugins import _service, _pair
from test_plug_r2b_k1b_accepted_bus_host import _accept

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = [
    "src/musica/studio_bus_plugins.py",
    "src/musica/studio_http.py",
    "src/musica/bus_host_runtime.py",
    "tests/test_plug_r2b_k2_studio_bus_plugins.py",
    "tests/plug_r2b_k2_evidence.py",
    ".github/workflows/plug-r2b-k2-studio-bus-host-evidence.yml",
    "docs/PLUG_R2B_K2_STUDIO_INSPECTION.md",
]


def _sha(contents: bytes) -> str:
    return hashlib.sha256(contents).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_bytes(canonical_json_bytes(value))


def _frames(raw: bytes) -> list[tuple[int, int]]:
    with wave.open(io.BytesIO(raw)) as handle:
        assert handle.getframerate() == 8000
        assert handle.getnchannels() == 2 and handle.getsampwidth() == 2
        return list(struct.iter_unpack("<hh", handle.readframes(handle.getnframes())))


def generate(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="musica-plug-k2-") as td:
        service, sid, project, revision = _service(Path(td))
        surface = StudioBusHostSurface(service)
        before = surface.bus_plugins_view(sid)
        assert before["offline_audition"]["available"] is True
        base_wav = surface.accepted_offline_wav(sid)
        initial = project.head_revision_id("main")

        accepted = _accept(project, project.read_revision(revision), _pair(), "K2-EVIDENCE")
        rid = accepted["project"]["revision_id"]
        assert rid != initial
        view = surface.bus_plugins_view(sid)
        wav = surface.accepted_offline_wav(sid)
        expected = render_accepted_simulated_bus_host(project, rid, sample_rate_hz=8000)
        assert wav == expected.wav_bytes
        assert view["accepted_bus_host_material_sha256"] == expected.plan["source"]["bus_host_material_sha256"]
        assert view["offline_audition"]["processing_plan_sha256"] == expected.plan["bus_host_processing_plan_sha256"]
        assert view["offline_audition"]["wav_sha256"] == _sha(wav)
        assert not view["capabilities"]["realtime_pdc"]
        assert not view["capabilities"]["default_studio_media_overridden"]
        assert project.head_revision_id("main") == rid
        frames = _frames(wav)
        assert len(frames) == 96000 and frames[:9] == [(0, 0)] * 9
        assert frames[9] == (24576, 24576)
        assert _frames(base_wav)[3] == (24576, 24576)

        _write_json(out / "view.json", view)
        _write_json(out / "baseline-view.json", before)
        (out / "accepted-opt-in.wav").write_bytes(wav)
        (out / "legacy.wav").write_bytes(base_wav)
        _write_json(out / "proof.json", {
            "proof_version": "0",
            "classification": "K2_STUDIO_ACCEPTED_HOST_EXPLICIT_OFFLINE_AUDITION_ONLY",
            "accepted_revision_id": rid,
            "view_matches_exact_accepted_material": True,
            "view_matches_exact_accepted_wav": True,
            "frame_count": len(frames),
            "first_aligned_frame": 9,
            "first_aligned_sample": [24576, 24576],
            "default_studio_media_overridden": False,
            "browser_user_interaction_or_realtime_pdc_proven": False,
            "project_head_unchanged_by_view_and_audition": True,
        })

    inventory = {
        "manifest_version": "0",
        "classification": "K2_ACCEPTED_STUDIO_INSPECTION_OFFLINE_ONLY",
        "artifacts": [
            {"path": p.name, "bytes": len(p.read_bytes()), "sha256": _sha(p.read_bytes())}
            for p in sorted(out.iterdir())
        ],
        "contracts": [
            {"path": name, "bytes": len((ROOT / name).read_bytes()), "sha256": _sha((ROOT / name).read_bytes())}
            for name in CONTRACTS
        ],
    }
    _write_json(out / "manifest.json", inventory)


if __name__ == "__main__":
    generate(Path(os.environ.get("MUSICA_K2_EVIDENCE_OUT", "artifacts/plug-r2b-k2-studio")))
    print("K2 Studio inspection evidence generated")
