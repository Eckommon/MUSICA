"""PROD-E2E-R0: audible 12-second two-track production integration reference.

This is deliberately a supported 8 kHz PCM16 stereo **offline** vertical slice,
not a claim of finished DAW workflow, live provider, real plugin binary,
recorded microphone/device input, physical realtime PDC or mastering quality.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import struct
import tempfile
import wave

from .audio_assets import import_audio_asset
from .audio_edit import (
    accept_audio_edit_preview, audio_material_sha256, blueprint_sha256,
    build_audio_edit_preview,
)
from .automation_edit import (
    accept_automation_edit_preview, automation_material_sha256,
    build_automation_edit_preview,
)
from .bus_host_edit import (
    accept_bus_host_edit_preview, build_bus_host_edit_preview,
    source_for_bus_host_candidate,
)
from .bus_host_runtime import render_accepted_simulated_bus_host
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .project import MusicaProject, create_project
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256
from .routing_edit import accept_routing_edit_preview, build_routing_edit_preview
from .routed_mixer import render_routed_mix


SAMPLE_RATE = 8000
DURATION_FRAMES = 96000
DURATION_SECONDS = 12.0


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _pcm16_mono(samples: list[int]) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(struct.pack("<" + "h" * len(samples), *samples))
    return stream.getvalue()


def _musical_assets() -> tuple[bytes, bytes]:
    """Repeatable melodic motif and pulse, with no synthetic impulse test input."""
    motif = (220.0, 261.6255653, 329.6275569, 293.6647679,
             246.9416506, 293.6647679, 392.0, 329.6275569)
    melody: list[int] = []
    percussion: list[int] = []
    for i in range(DURATION_FRAMES):
        t = i / SAMPLE_RATE
        subdivision = t % 0.375
        pitch = motif[int(t / 0.375) % len(motif)]
        env = min(1.0, subdivision / 0.012) * math.exp(-2.7 * subdivision)
        carrier = math.sin(2 * math.pi * pitch * subdivision)
        harmonic = 0.19 * math.sin(2 * math.pi * pitch * 2.0 * subdivision)
        melody.append(round(6800 * env * (carrier + harmonic)))

        beat = t % 0.5
        kick = 6100 * math.exp(-28 * beat) * math.sin(2 * math.pi * (94 - 35 * beat) * beat)
        eighth = t % 0.25
        hat = 1100 * math.exp(-55 * eighth) * math.sin(2 * math.pi * 1380 * eighth)
        percussion.append(round(kick + hat))
    return _pcm16_mono(melody), _pcm16_mono(percussion)


def _source_audio(parent: dict) -> dict:
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
    }


def _accept(preview, project, method: str) -> dict:
    if not preview.ready or preview.blueprint is None:
        raise ValueError(f"{method} proposal was not ready for trusted Preview")
    before = project.head_revision_id("main")
    if before != preview.blueprint["project"]["parent_revision_id"]:
        raise ValueError(f"{method} exact accepted parent changed")
    handler = {
        "audio": accept_audio_edit_preview,
        "routing": accept_routing_edit_preview,
        "automation": accept_automation_edit_preview,
        "bus-plugin": accept_bus_host_edit_preview,
    }[method]
    record = handler(project, preview)
    if project.head_revision_id("main") != record["revision_id"] or record["revision_id"] == before:
        raise ValueError(f"{method} did not advance exactly one accepted revision")
    return project.read_revision(record["revision_id"])


def _propose_audio(project, parent, assets: tuple[str, str]):
    ops = [
        {"operation_id": "PROD-TRK-1", "op": "ADD_TRACK",
         "track_id": "AT-001", "order": 0, "name": "Melodic synth"},
        {"operation_id": "PROD-TRK-2", "op": "ADD_TRACK",
         "track_id": "AT-002", "order": 1, "name": "Drum pulse"},
    ]
    for idx, asset_id in enumerate(assets, 1):
        ops.append({
            "operation_id": f"PROD-CLIP-{idx}", "op": "ADD_CLIP",
            "target": {"track_id": f"AT-{idx:03d}"},
            "clip": {
                "clip_id": f"AC-{idx:03d}", "asset_id": asset_id,
                "timeline_start_seconds": 0.0, "source_in_seconds": 0.0,
                "source_out_seconds": DURATION_SECONDS, "gain_db": 0.0,
            },
        })
    candidate = {
        "candidate_version": "0", "candidate_id": "PROD-AUDIO-01",
        "authority_target": "blueprint_audio_material",
        "source": _source_audio(parent),
        "actor": {"kind": "user", "actor_id": "prod-e2e-r0"},
        "reason": "Accept two musical imported audio tracks and clips",
        "operations": ops, "preview_only": True,
    }
    return _accept(build_audio_edit_preview(project, parent, candidate), project, "audio")


def _propose_routing(project, parent):
    neutral = {"gain_db": 0.0, "pan": 0.0, "mute": False}
    ops = []
    for i in range(1, 3):
        ops.append({
            "operation_id": f"PROD-BUS-{i}", "op": "ADD_NODE",
            "node": {"node_id": f"BUS-{i:03d}", "order": i - 1,
                     "name": f"Production Bus {i}", "node_type": "bus",
                     "mixer": neutral, "output_node_id": "MASTER-001"},
        })
    ops.append({
        "operation_id": "PROD-MASTER", "op": "ADD_NODE",
        "node": {"node_id": "MASTER-001", "order": 2,
                 "name": "Master", "node_type": "master",
                 "mixer": neutral, "output_node_id": None},
    })
    for i in range(1, 3):
        ops.append({
            "operation_id": f"PROD-OUTPUT-{i}", "op": "SET_TRACK_OUTPUT",
            "track_id": f"AT-{i:03d}", "target_node_id": f"BUS-{i:03d}",
        })
    material = routing_material_from_blueprint(parent)
    if material is None:
        raise ValueError("missing initialized routing material")
    candidate = {
        "candidate_version": "0", "candidate_id": "PROD-ROUTE-01",
        "authority_target": "blueprint_routing_material",
        "source": {
            **_source_audio(parent),
            "routing_material_sha256": routing_material_sha256(material),
        },
        "actor": {"kind": "user", "actor_id": "prod-e2e-r0"},
        "reason": "Accept two distinct buses and neutral master",
        "operations": ops, "preview_only": True,
    }
    return _accept(build_routing_edit_preview(project, parent, candidate), project, "routing")


def _propose_automation(project, parent):
    lane = {
        "lane_id": "AUTO-PROD-GAIN-001",
        "target": {
            "parameter_id": "mixer.gain_db", "scope": "audio_track",
            "owner_id": "AT-001", "unit": "decibel",
            "minimum": -60.0, "maximum": 12.0,
        },
        "section_id": None,
        "points": [
            {"point_id": "PROD-AUTO-0", "beat": 0.0,
             "value": -3.0, "interpolation": "hold"},
            {"point_id": "PROD-AUTO-8", "beat": 8.0,
             "value": -6.0, "interpolation": "linear"},
        ],
    }
    material = routing_material_from_blueprint(parent)
    if material is None:
        raise ValueError("missing accepted routing")
    candidate = {
        "candidate_version": "0", "candidate_id": "PROD-AUTO-01",
        "authority_target": "blueprint_automation_material",
        "source": {
            **_source_audio(parent),
            "automation_material_sha256": automation_material_sha256(parent),
            "routing_material_sha256": routing_material_sha256(material),
        },
        "actor": {"kind": "user", "actor_id": "prod-e2e-r0"},
        "reason": "Accept melodic track native mixer gain automation",
        "operations": [{"operation_id": "PROD-AUTO-OP", "op": "ADD_LANE", "lane": lane}],
        "preview_only": True,
    }
    return _accept(build_automation_edit_preview(parent, candidate, project=project),
                   project, "automation")


def _propose_plugin(project, parent):
    instances = []
    for i, latency in enumerate((3, 9), 1):
        instances.append({
            "instance_id": f"BPI-{i:03d}", "owner_kind": "routing_node",
            "owner_bus_id": f"BUS-{i:03d}", "slot": 0,
            "processor_id": "musica-simulated-bus-latency-v0",
            "processor_version": "0",
            "latency_provenance": "accepted_explicit_simulated_reference",
            "algorithmic_latency_frames": latency,
            "creative_delay_frames": 0, "bypass": False,
        })
    candidate = {
        "candidate_version": "0", "candidate_id": "PROD-PLUG-01",
        "authority_target": "blueprint_bus_plugin_material",
        "source": source_for_bus_host_candidate(parent),
        "proposed_material": {
            "material_version": "0",
            "classification": "accepted_simulated_bus_host_material",
            "instances": instances,
        },
        "actor": {"kind": "user", "actor_id": "prod-e2e-r0"},
        "reason": "Accept simulated separate latency on two buses",
        "preview_only": True,
    }
    return _accept(build_bus_host_edit_preview(project, parent, candidate),
                   project, "bus-plugin")


def generate_first_song(out: Path) -> dict:
    """Write reproducible musical WAV, Project archive and gap report.

    A pre-existing nonempty destination is rejected, never silently overwritten.
    """
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError("destination must be absent or empty")
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="musica-prod-e2e-") as tmp:
        home = Path(tmp)
        intent_path = Path(__file__).resolve().parents[2] / "examples" / "intents" / "dark-electronic-12s.json"
        intent = json.loads(intent_path.read_text(encoding="utf-8"))
        blueprint = compose_blueprint(intent)
        project = create_project(home / "song.musica", blueprint)
        source_a, source_b = _musical_assets()
        a_path, b_path = home / "melodic-synth.wav", home / "drum-pulse.wav"
        a_path.write_bytes(source_a)
        b_path.write_bytes(source_b)
        a = import_audio_asset(project, a_path)
        b = import_audio_asset(project, b_path)

        root_id = project.head_revision_id("main")
        accepted_audio = _propose_audio(project, blueprint, (a["asset_id"], b["asset_id"]))
        accepted_route = _propose_routing(project, accepted_audio)
        accepted_auto = _propose_automation(project, accepted_route)
        source_id = accepted_auto["project"]["revision_id"]

        before_plugin = render_routed_mix(project, source_id, mix_sample_rate_hz=SAMPLE_RATE)
        plugin = _propose_plugin(project, accepted_auto)
        accepted_id = plugin["project"]["revision_id"]
        rendered = render_accepted_simulated_bus_host(
            project, accepted_id, sample_rate_hz=SAMPLE_RATE
        )
        if project.head_revision_id("main") != accepted_id:
            raise ValueError("offline execution mutated accepted HEAD")
        if rendered.wav_bytes == before_plugin.wav_bytes:
            raise ValueError("plugin insertion was inaudible")
        with wave.open(io.BytesIO(rendered.wav_bytes), "rb") as reader:
            if (reader.getframerate(), reader.getnchannels(),
                    reader.getsampwidth(), reader.getnframes()) != (
                SAMPLE_RATE, 2, 2, DURATION_FRAMES
            ):
                raise ValueError("rendered WAV violates fixed output contract")
            samples = list(struct.iter_unpack("<hh", reader.readframes(DURATION_FRAMES)))
        if not any((left != 0 or right != 0) for left, right in samples[9:]):
            raise ValueError("musical output is silent")
        if any(left != 0 or right != 0 for left, right in samples[:9]):
            raise ValueError("causal two-bus PDC emitted audio before frame 9")
        peak = max(max(abs(x), abs(y)) for x, y in samples)
        if peak >= 32767:
            raise ValueError("output has clipped PCM samples")

        archive = project.export_to(out / "accepted-project.musica.zip")
        reopened = MusicaProject.import_from(archive, home / "reopened.musica")
        if reopened.head_revision_id("main") != accepted_id:
            raise ValueError("Project archive did not preserve accepted HEAD")
        replay = render_accepted_simulated_bus_host(
            reopened, accepted_id, sample_rate_hz=SAMPLE_RATE
        )
        if replay.wav_bytes != rendered.wav_bytes or replay.plan != rendered.plan:
            raise ValueError("fresh import did not reproduce exact derived audio/plan")
        (out / "final-song.wav").write_bytes(rendered.wav_bytes)
        (out / "pre-plugin.wav").write_bytes(before_plugin.wav_bytes)
        (out / "source-melody.wav").write_bytes(source_a)
        (out / "source-drums.wav").write_bytes(source_b)

        proof = {
            "version": "0", "classification": "PROD_E2E_R0_OFFLINE_TWO_TRACK_MUSICAL_SLICE",
            "canonical_authority": "accepted_blueprint_revision",
            "project_initial_revision": root_id,
            "accepted_audio_revision": accepted_audio["project"]["revision_id"],
            "accepted_routing_revision": accepted_route["project"]["revision_id"],
            "accepted_automation_revision": source_id,
            "accepted_plugin_revision": accepted_id,
            "accepted_head_unchanged_by_offline_render": True,
            "fresh_archive_reopen_exact_plan_and_wav": True,
            "asset_ids": [a["asset_id"], b["asset_id"]],
            "musical_assets_generated": ["melodic_synth", "rhythmic_percussion"],
            "audio_kind": "two_track_musical_PCM16_offline",
            "frames": DURATION_FRAMES, "sample_rate_hz": SAMPLE_RATE,
            "channels": 2, "sample_width_bytes": 2,
            "positive_peak_pcm16": peak, "clipped_pcm_samples": 0,
            "first_compensated_audible_frame_at_or_after": 9,
            "final_song_wav_sha256": _sha(rendered.wav_bytes),
            "pre_plugin_wav_sha256": _sha(before_plugin.wav_bytes),
            "bus_host_processing_plan_sha256": rendered.plan["bus_host_processing_plan_sha256"],
            "provider_execution": "local_fixture_blueprint_not_live_AI",
            "physical_device_recording_proven": False,
            "actual_third_party_plugin_host_proven": False,
            "realtime_plugin_pdc_proven": False,
            "commercial_release_ready": False,
        }
        (out / "proof.json").write_bytes(canonical_json_bytes(proof))
        inventory = {
            "version": "0", "classification": proof["classification"],
            "artifacts": [
                {"path": p.name, "bytes": len(p.read_bytes()), "sha256": _sha(p.read_bytes())}
                for p in sorted(out.iterdir())
            ],
        }
        (out / "manifest.json").write_bytes(canonical_json_bytes(inventory))
        return proof

def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate a bounded audible MUSICA first-song offline integration demo"
    )
    parser.add_argument("--out", type=Path, required=True,
                        help="New or empty output directory (never overwritten)")
    args = parser.parse_args(argv)
    proof = generate_first_song(args.out)
    print(json.dumps({
        "classification": proof["classification"],
        "final_song": str(args.out / "final-song.wav"),
        "sha256": proof["final_song_wav_sha256"],
        "frames": proof["frames"],
        "sample_rate_hz": proof["sample_rate_hz"],
        "real_plugin_host": False,
        "physical_recording": False,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
