"""G3B2C-R5 cache proof: 180s real source-bound candidate, 3 seeks, 1 DSP."""
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
from musica.studio import StudioService, StudioServiceError
from musica.studio_audio import StudioAudioSurface
from musica.studio_pending_cache import PendingWavFileCache, PENDING_CACHE_TTL_SECONDS
from musica.studio_pending_wav import PendingWavRangeHTTP
from test_atcm_r2_native_mixer import _candidate
from test_prod_e2e_r2a_g3b2a_streamed_native import _two_accepted_long_sources
from test_prod_e2e_r2a_g3b2c_http_range import _Response


def _pending_session(tmp_path):
    project, head, first, second = _two_accepted_long_sources(tmp_path)
    service = StudioService(tmp_path / "studio")
    service.open_project_session(
        project_slug="g3b2-long-two-track", session_id="r5-source-bound"
    )
    accepted = service._get_session("r5-source-bound").project.read_revision(head)
    preview = StudioAudioSurface(service).preview_audio_edit(
        "r5-source-bound",
        candidate=_candidate(
            accepted, "G3B2C-R5-PENDING-NATIVE",
            [{"operation_id": "R5-A-GAIN", "op": "SET_TRACK_MIXER",
              "target": {"track_id": "AT-G3B2-A"},
              "mixer": {"gain_db": -6.0, "pan": 0.0,
                        "mute": False, "solo": False}}],
        ),
        candidate_kind="mixer",
    )
    assert preview["preview_installed"]
    pending_id = service._get_session("r5-source-bound").pending.descriptor["preview_id"]
    return service, project, head, pending_id, first, second


def test_real_180s_three_preview_ranges_one_dsp_and_discard_denial(tmp_path):
    service, project, head, token, aa, bb = _pending_session(tmp_path)
    transport = PendingWavRangeHTTP(service)
    etag = None
    for label in ("bytes=44-47", "bytes=17280044-17280047", "bytes=-4"):
        response = _Response()
        transport.serve(
            response, "r5-source-bound", preview_id=token,
            range_headers=[label],
        )
        assert response.status == 206
        assert response.headers["Content-Length"] == "4"
        assert response.headers["Content-Range"].endswith("/34560044")
        assert struct.unpack("<hh", response.wfile.getvalue()) == (2005, -2500)
        if etag is None:
            etag = response.headers["ETag"]
        assert response.headers["ETag"] == etag
        assert transport._cache.render_count == 1
        assert project.head_revision_id() == head

    cached_wavs = list(transport._cache.root.glob("pending-*.wav"))
    assert len(cached_wavs) == 1
    output = cached_wavs[0]
    assert output.stat().st_size == 34_560_044
    with wave.open(str(output), "rb") as reader:
        assert (reader.getframerate(), reader.getnchannels(),
                reader.getsampwidth(), reader.getnframes()) == (
            48000, 2, 2, 8_640_000,
        )
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    assert etag == '"' + digest + '"'
    assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss < 512 * 1024
    artifact = os.getenv("MUSICA_G3B2C_R5_ARTIFACT_DIR")
    if artifact:
        root = Path(artifact).resolve()
        root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, root / "pending-180s-source-bound.wav")
        (root / "proof.json").write_text(
            json.dumps(
                {
                    "milestone": "PROD-E2E-R2A-G3B2C-R5",
                    "accepted_head": head,
                    "source_a_sha256": aa["object_sha256"],
                    "source_b_sha256": bb["object_sha256"],
                    "preview_id": token,
                    "pending_is_canonical": False,
                    "sample_rate_hz": 48000,
                    "channels": 2,
                    "sample_width_bytes": 2,
                    "duration_seconds": 180,
                    "wav_size_bytes": output.stat().st_size,
                    "wav_sha256": digest,
                    "range_headers": ["bytes=44-47", "bytes=17280044-17280047", "bytes=-4"],
                    "dsp_render_count": transport._cache.render_count,
                    "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    "accepted_head_unchanged": project.head_revision_id() == head,
                    "actual_human_browser_session_verified": False,
                },
                sort_keys=True, indent=2,
            ) + "\n",
            encoding="utf-8",
        )
    # A cached derivative is untrusted too: mutate one PCM byte on disk.
    # The next trusted Range must detect its SHA mismatch, evict it and
    # rerender from the unchanged authoritative accepted source CAS.
    with output.open("r+b") as handle:
        handle.seek(44)
        current = handle.read(1)
        handle.seek(44)
        handle.write(bytes([current[0] ^ 0xFF]))
    corrected = _Response()
    transport.serve(corrected, "r5-source-bound",
                    preview_id=token, range_headers=["bytes=44-47"])
    assert corrected.status == 206
    assert struct.unpack("<hh", corrected.wfile.getvalue()) == (2005, -2500)
    assert corrected.headers["ETag"] == etag
    assert transport._cache.render_count == 2
    assert len(list(transport._cache.root.glob("pending-*.wav"))) == 1
    with pytest.raises(StudioServiceError, match="no longer active"):
        transport.serve(_Response(), "r5-source-bound",
                        preview_id="invalid-preview", range_headers=[])
    service.discard_preview("r5-source-bound")
    # Product lifecycle: eager derived cleanup on Discard, not merely lazy TTL.
    assert not list(transport._cache.root.glob("pending-*.wav"))
    with pytest.raises(StudioServiceError, match="no longer active"):
        transport.serve(_Response(), "r5-source-bound",
                        preview_id=token, range_headers=[])
    assert project.head_revision_id() == head
    transport._cache.clear_session("r5-source-bound")
    assert not list(transport._cache.root.glob("pending-*.wav"))


def test_preview_cache_ttl_and_symlink_safety(tmp_path, monkeypatch):
    import musica.studio_pending_cache as module

    service, project, head, token, aa, bb = _pending_session(tmp_path)
    clock = [30000.0]
    monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])
    transport = PendingWavRangeHTTP(service)
    first = _Response()
    transport.serve(first, "r5-source-bound", preview_id=token,
                    range_headers=["bytes=44-47"])
    assert transport._cache.render_count == 1
    clock[0] += PENDING_CACHE_TTL_SECONDS + 1.0
    second = _Response()
    transport.serve(second, "r5-source-bound", preview_id=token,
                    range_headers=["bytes=44-47"])
    assert second.wfile.getvalue() == first.wfile.getvalue()
    assert transport._cache.render_count == 2
    assert len(list(transport._cache.root.glob("pending-*.wav"))) == 1
    transport._cache.clear_all_idle()
    assert project.head_revision_id() == head


def test_pending_preview_cache_root_rejects_symlink_without_touching_user_files(tmp_path):
    service = StudioService(tmp_path / "studio")
    other = tmp_path / "user-files"
    other.mkdir()
    important = other / "real-project.wav"
    important.write_bytes(b"keep user file")
    Path(service.workspace, ".derived-pending-wav-cache-g3b2c-r5").symlink_to(
        other, target_is_directory=True,
    )
    with pytest.raises(ContractError, match="symlink"):
        PendingWavFileCache(service)
    assert important.read_bytes() == b"keep user file"


def test_preview_cache_defers_eviction_while_stream_lease_active(tmp_path):
    service, project, head, token, aa, bb = _pending_session(tmp_path)
    cache = PendingWavFileCache(service)
    render = cache.acquire("r5-source-bound", token)
    assert render.wav_path.exists()
    cache.invalidate_session("r5-source-bound")
    assert render.wav_path.exists(), "an in-flight stream must retain its WAV"
    cache.release("r5-source-bound")
    assert not render.wav_path.exists(), "deferred eviction must run on release"
    assert project.head_revision_id() == head


def test_pending_cached_wav_is_eagerly_deleted_on_replace_and_close(tmp_path):
    service, project, head, token, aa, bb = _pending_session(tmp_path)
    transport = PendingWavRangeHTTP(service)
    first = _Response()
    transport.serve(first, "r5-source-bound", preview_id=token,
                    range_headers=["bytes=44-47"])
    assert len(list(transport._cache.root.glob("pending-*.wav"))) == 1
    service.discard_preview("r5-source-bound")
    assert not list(transport._cache.root.glob("pending-*.wav"))
    accepted = service._get_session("r5-source-bound").project.read_revision(head)
    result = StudioAudioSurface(service).preview_audio_edit(
        "r5-source-bound",
        candidate=_candidate(
            accepted, "G3B2C-R5-REPLACED-CANDIDATE",
            [{"operation_id": "R5-B-GAIN", "op": "SET_TRACK_MIXER",
              "target": {"track_id": "AT-G3B2-A"},
              "mixer": {"gain_db": -8.0, "pan": 0.0,
                        "mute": False, "solo": False}}],
        ), candidate_kind="mixer",
    )
    assert result["preview_installed"]
    second_token = service._get_session("r5-source-bound").pending.descriptor["preview_id"]
    second = _Response()
    transport.serve(second, "r5-source-bound", preview_id=second_token,
                    range_headers=["bytes=44-47"])
    assert len(list(transport._cache.root.glob("pending-*.wav"))) == 1
    service.close_session("r5-source-bound")
    assert not list(transport._cache.root.glob("pending-*.wav"))
    assert project.head_revision_id() == head
