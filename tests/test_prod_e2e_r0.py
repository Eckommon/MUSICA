"""PROD-E2E-R0 first audible song, trusted authority and archive evidence."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import struct
import wave

import pytest

from musica.prod_e2e_r0 import (
    DURATION_FRAMES, SAMPLE_RATE, generate_first_song,
)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def test_two_track_musical_vertical_slice_is_real_and_reopen_exact(tmp_path: Path) -> None:
    output = tmp_path / "song-a"
    proof = generate_first_song(output)
    assert proof["classification"] == "PROD_E2E_R0_OFFLINE_TWO_TRACK_MUSICAL_SLICE"
    assert proof["accepted_head_unchanged_by_offline_render"] is True
    assert proof["fresh_archive_reopen_exact_plan_and_wav"] is True
    assert proof["physical_device_recording_proven"] is False
    assert proof["actual_third_party_plugin_host_proven"] is False
    assert proof["commercial_release_ready"] is False
    assert len(proof["asset_ids"]) == 2
    assert len(set(proof["asset_ids"])) == 2
    assert proof["clipped_pcm_samples"] == 0
    assert 0 < proof["positive_peak_pcm16"] < 32767
    assert proof["accepted_audio_revision"] != proof["accepted_routing_revision"]
    assert proof["accepted_routing_revision"] != proof["accepted_automation_revision"]
    assert proof["accepted_automation_revision"] != proof["accepted_plugin_revision"]

    final = (output / "final-song.wav").read_bytes()
    pre = (output / "pre-plugin.wav").read_bytes()
    assert _sha(final) == proof["final_song_wav_sha256"]
    assert pre != final
    with wave.open(io.BytesIO(final), "rb") as wav:
        assert (wav.getframerate(), wav.getnchannels(), wav.getsampwidth(), wav.getnframes()) == (
            SAMPLE_RATE, 2, 2, DURATION_FRAMES
        )
        values = list(struct.iter_unpack("<hh", wav.readframes(DURATION_FRAMES)))
    assert values[:9] == [(0, 0)] * 9
    assert any(a != 0 or b != 0 for a, b in values[9:])
    assert max(max(abs(a), abs(b)) for a, b in values) == proof["positive_peak_pcm16"]
    assert sum(1 for a, b in values if abs(a) > 200 or abs(b) > 200) > 12000

    for item in ["source-melody.wav", "source-drums.wav"]:
        with wave.open(str(output / item), "rb") as w:
            assert w.getnchannels() == 1
            assert w.getsampwidth() == 2
            assert w.getframerate() == SAMPLE_RATE
            assert w.getnframes() == DURATION_FRAMES
    assert (output / "accepted-project.musica.zip").stat().st_size > 1000
    inventory = json.loads((output / "manifest.json").read_bytes())
    for member in inventory["artifacts"]:
        b = (output / member["path"]).read_bytes()
        assert len(b) == member["bytes"]
        assert _sha(b) == member["sha256"]


def test_two_clean_runs_generate_bit_exact_song_and_evidence(tmp_path: Path) -> None:
    generate_first_song(tmp_path / "first")
    generate_first_song(tmp_path / "second")
    one = {p.name: _sha(p.read_bytes()) for p in (tmp_path / "first").iterdir()}
    two = {p.name: _sha(p.read_bytes()) for p in (tmp_path / "second").iterdir()}
    assert one == two
    assert len(one) >= 7


def test_refuses_overwrite_of_existing_workspace(tmp_path: Path) -> None:
    target = tmp_path / "exists"
    target.mkdir()
    (target / "keep.txt").write_text("do not replace", encoding="utf-8")
    with pytest.raises(ValueError, match="absent or empty"):
        generate_first_song(target)
    assert (target / "keep.txt").read_text(encoding="utf-8") == "do not replace"
