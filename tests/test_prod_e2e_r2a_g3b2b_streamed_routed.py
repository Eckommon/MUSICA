"""G3B2B: routed PCM short exactness, native automation parity, 180s routed buses."""
from __future__ import annotations

import hashlib
import json
import os
import resource
import shutil
import struct
import wave
from pathlib import Path

import pytest

from musica.contracts import ContractError
from musica.native_mixer import _gain_linear, _pcm16_sample
from musica.project import MusicaProject
from musica.routed_mixer import render_routed_mix
from musica.routing_edit import accept_routing_edit_preview, build_routing_edit_preview
from musica.streamed_routed_mixer import render_routed_mix_streamed

from test_mram_r1_routing_authority_mixer import _accept_routing, _routing_candidate
from test_mram_r2_native_mixer_automation import _accept_native, _lane
from test_prod_e2e_r2a_g3b2a_streamed_native import _two_accepted_long_sources


def test_routed_short_legacy_byte_exact_with_send_return(tmp_path: Path):
    project, accepted = _accept_routing(tmp_path)
    rev = accepted["project"]["revision_id"]
    reference = render_routed_mix(project, rev, mix_sample_rate_hz=8000)
    for frames in (317, 4096):
        mixed = render_routed_mix_streamed(
            project, rev, mix_sample_rate_hz=8000, block_frames=frames
        )
        assert mixed.plan == reference.plan
        assert mixed.wav_path.read_bytes() == reference.wav_bytes
        assert mixed.wav_sha256 == reference.wav_sha256
        assert mixed.peak_pre_clip == reference.peak_pre_clip
        assert mixed.clipped_sample_count == reference.clipped_sample_count
        mixed.wav_path.unlink()
    assert project.head_revision_id() == rev


def test_automation_gain_pan_legacy_byte_exact_and_cancel(tmp_path: Path):
    project, routed = _accept_routing(tmp_path)
    lanes = [
        _lane(
            "AUTO-G3B2B-TRACK", scope="audio_track", owner_id="AT-001",
            parameter_id="mixer.gain_db",
            points=[("GT-0", 0.0, -3.0, "linear"),
                    ("GT-1", 2.0, -12.0, "hold")],
        ),
        _lane(
            "AUTO-G3B2B-BUS", scope="routing_node", owner_id="BUS-001",
            parameter_id="mixer.pan",
            points=[("GB-0", 0.0, -0.6, "linear"),
                    ("GB-1", 2.0, 0.5, "hold")],
        ),
    ]
    accepted = _accept_native(project, routed, "G3B2B-NATIVE-AUTOMATION", lanes)
    rev = accepted["project"]["revision_id"]
    reference = render_routed_mix(project, rev, mix_sample_rate_hz=8000)
    mixed = render_routed_mix_streamed(
        project, rev, mix_sample_rate_hz=8000, block_frames=263
    )
    assert mixed.plan == reference.plan
    assert mixed.wav_path.read_bytes() == reference.wav_bytes
    assert mixed.wav_sha256 == reference.wav_sha256
    mixed.wav_path.unlink()
    with pytest.raises(ContractError, match="cancelled"):
        render_routed_mix_streamed(
            project, rev, mix_sample_rate_hz=8000,
            block_frames=512, cancelled=lambda: True,
        )
    assert not list((project.root / ".derived-streamed-routed-g3b2b").glob("*.wav"))
    assert project.head_revision_id() == rev


def _accept_long_two_buses(tmp_path: Path):
    project, rev, a, b = _two_accepted_long_sources(tmp_path)
    accepted = project.read_revision(rev)
    candidate = _routing_candidate(
        accepted, "G3B2B-180S-ROUTED",
        [
            {
                "operation_id": "G3B2B-NODE-A", "op": "ADD_NODE",
                "node": {
                    "node_id": "BUS-G3B2-A", "order": 0, "name": "Bus A",
                    "node_type": "group",
                    "mixer": {"gain_db": -6.0, "pan": 0.0, "mute": False},
                    "output_node_id": "MASTER-G3B2",
                },
            },
            {
                "operation_id": "G3B2B-NODE-B", "op": "ADD_NODE",
                "node": {
                    "node_id": "BUS-G3B2-B", "order": 1, "name": "Bus B",
                    "node_type": "group",
                    "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
                    "output_node_id": "MASTER-G3B2",
                },
            },
            {
                "operation_id": "G3B2B-MASTER", "op": "ADD_NODE",
                "node": {
                    "node_id": "MASTER-G3B2", "order": 2, "name": "Master",
                    "node_type": "master",
                    "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
                    "output_node_id": None,
                },
            },
            {
                "operation_id": "G3B2B-OUT-A", "op": "SET_TRACK_OUTPUT",
                "track_id": "AT-G3B2-A", "target_node_id": "BUS-G3B2-A",
            },
            {
                "operation_id": "G3B2B-OUT-B", "op": "SET_TRACK_OUTPUT",
                "track_id": "AT-G3B2-B", "target_node_id": "BUS-G3B2-B",
            },
        ],
    )
    preview = build_routing_edit_preview(project, accepted, candidate)
    assert preview.ready, preview.authority_result
    assert project.head_revision_id() == rev
    new = accept_routing_edit_preview(project, preview)
    return project, new["revision_id"], a, b


def test_two_accepted_180s_buses_is_bounded_and_restart_deterministic(tmp_path: Path):
    project, rev, a, b = _accept_long_two_buses(tmp_path)
    mixed = render_routed_mix_streamed(
        project, rev, mix_sample_rate_hz=48000, block_frames=4096
    )
    max_rss_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    assert max_rss_kib < 512 * 1024
    assert mixed.wav_size_bytes == 34_560_044
    assert mixed.blocks_written > 2000
    assert mixed.clipped_sample_count == 0
    assert project.head_revision_id() == rev
    # Stereo integer PCM16 oracle after Bus A -6dB, neutral Bus B, master.
    expected_left = _pcm16_sample((4000.0 / 32768.0) * _gain_linear(-6))
    expected_stereo = (expected_left, -2500)
    with wave.open(str(mixed.wav_path), "rb") as src:
        assert (src.getnframes(), src.getframerate(),
                src.getnchannels(), src.getsampwidth()) == (8640000, 48000, 2, 2)
        for index in (0, 48000, 4320000, 8639999):
            src.setpos(index)
            assert struct.unpack("<hh", src.readframes(1)) == expected_stereo
    archive = project.export_to(tmp_path / "g3b2b-routed-project.musica.zip")
    reopened = MusicaProject.import_from(archive, tmp_path / "g3b2b-reopened.musica")
    assert reopened.head_revision_id() == rev
    rerendered = render_routed_mix_streamed(
        reopened, rev, mix_sample_rate_hz=48000, block_frames=8191
    )
    assert mixed.wav_sha256 == rerendered.wav_sha256
    assert mixed.plan == rerendered.plan

    artifact = os.getenv("MUSICA_G3B2B_ARTIFACT_DIR")
    if artifact:
        dest = Path(artifact).resolve()
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(mixed.wav_path, dest / "routed-180s.wav")
        proof = {
            "milestone": "PROD-E2E-R2A-G3B2B",
            "exact_accepted_revision": rev,
            "two_independent_180s_sources": a["asset_id"] != b["asset_id"],
            "source_a_sha256": a["object_sha256"],
            "source_b_sha256": b["object_sha256"],
            "sample_rate_hz": 48000,
            "channels": 2,
            "frames": 8_640_000,
            "duration_seconds": 180,
            "output_size_bytes": mixed.wav_size_bytes,
            "output_sha256": mixed.wav_sha256,
            "reopened_sha256": rerendered.wav_sha256,
            "first_middle_last_pcm16": list(expected_stereo),
            "clipped_samples": mixed.clipped_sample_count,
            "peak_process_rss_kib": max_rss_kib,
            "native_automation_short_exact_parity": True,
            "automation_long_180s_verified": False,
            "browser_audition_long_song_verified": False,
            "physical_device_verified": False,
        }
        (dest / "proof.json").write_text(
            json.dumps(proof, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8"
        )
    mixed.wav_path.unlink()
    rerendered.wav_path.unlink()


def test_two_180s_buses_accepted_native_gain_ramp_across_window_boundaries(tmp_path):
    """G3B2B: long project dynamic automation, not merely a 12s parity test."""
    project, routed_rev, a, b = _accept_long_two_buses(tmp_path)
    routed_blueprint = project.read_revision(routed_rev)
    lane = _lane(
        "AUTO-G3B2B-LONG-BUS-A",
        scope="routing_node",
        owner_id="BUS-G3B2-A",
        parameter_id="mixer.gain_db",
        points=[
            ("G3B2B-LONG-0", 0.0, -6.0, "linear"),
            ("G3B2B-LONG-1", 80.0, -12.0, "hold"),
        ],
    )
    accepted = _accept_native(
        project, routed_blueprint, "G3B2B-180S-BUS-A-RAMP", [lane]
    )
    new_rev = accepted["project"]["revision_id"]
    assert new_rev != routed_rev
    output = render_routed_mix_streamed(
        project, new_rev, mix_sample_rate_hz=48000, block_frames=3072
    )
    assert output.wav_size_bytes == 34_560_044
    assert output.clipped_sample_count == 0
    plan_lane = output.plan["native_mixer_automation"]["lanes"][0]
    assert plan_lane["target_kind"] == "routing_node"
    assert plan_lane["target_id"] == "BUS-G3B2-A"
    fade_end_frame = int(plan_lane["points"][1]["frame"])
    assert 0 < fade_end_frame < 8_640_000
    observed = []
    with wave.open(str(output.wav_path), "rb") as wav:
        assert wav.getnframes() == 8_640_000
        for frame in (0, fade_end_frame // 2, fade_end_frame, 4_320_000, 8_639_999):
            wav.setpos(frame)
            actual = struct.unpack("<hh", wav.readframes(1))
            fraction = min(1.0, frame / fade_end_frame)
            db = -6.0 + (-6.0) * fraction
            expected_left = _pcm16_sample((4000.0 / 32768.0) * (10.0 ** (db / 20.0)))
            assert actual == (expected_left, -2500)
            observed.append({"frame": frame, "gain_db": db, "pcm16": list(actual)})
    assert project.head_revision_id() == new_rev
    assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss < 512 * 1024
    destination = os.getenv("MUSICA_G3B2B_ARTIFACT_DIR")
    if destination:
        root = Path(destination).resolve()
        root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output.wav_path, root / "routed-automated-180s.wav")
        (root / "automation-proof.json").write_text(
            json.dumps(
                {
                    "milestone": "PROD-E2E-R2A-G3B2B-LONG-AUTOMATION",
                    "accepted_revision_id": new_rev,
                    "automated_bus": "BUS-G3B2-A",
                    "target_parameter": "mixer.gain_db",
                    "fade_end_frame": fade_end_frame,
                    "samples": observed,
                    "wav_sha256": output.wav_sha256,
                    "wav_size_bytes": output.wav_size_bytes,
                    "sample_rate_hz": 48000,
                    "frames": 8_640_000,
                    "clipped_samples": output.clipped_sample_count,
                    "accepted_head_unchanged_by_derived_render": project.head_revision_id() == new_rev,
                    "physical_audio_device_proven": False,
                },
                sort_keys=True, indent=2
            ) + "\n",
            encoding="utf-8"
        )
    output.wav_path.unlink()
