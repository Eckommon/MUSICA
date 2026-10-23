"""G3B2C-R2 accepted source-bound WAV cache: real PCM reuse and fail-closed lifecycle."""
from __future__ import annotations

import os
import json
import shutil
import hashlib
import struct
import wave
from pathlib import Path

import pytest

from musica.contracts import ContractError
from musica.project import ProjectIntegrityError
from musica.studio_wav_cache import AcceptedWavFileCache, CACHE_IDLE_TTL_SECONDS
from musica.studio_wav_http_range import AcceptedWavRangeHTTP
from test_atcm_r2_native_mixer import _accept_arrangement
from test_prod_e2e_r2a_g3b2c_http_range import _Response, _Service
from test_prod_e2e_r2a_g3b2a_streamed_native import _two_accepted_long_sources


def test_multiple_accepted_pcm_ranges_only_render_once_then_clear(tmp_path: Path):
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    service = _Service(project)
    transport = AcceptedWavRangeHTTP(service)
    head = accepted["project"]["revision_id"]
    assert transport._cache.render_count == 0
    initial = _Response()
    transport.serve(initial, "trusted-test-session", range_headers=[], attachment=False)
    assert initial.status == 200
    assert transport._cache.render_count == 1
    directory = transport._cache.root
    derived = list(directory.glob("wav-*.wav"))
    assert len(derived) == 1
    assert derived[0].stat().st_size == len(initial.wfile.getvalue())

    for header in ("bytes=0-43", "bytes=44-79", "bytes=-8", "bytes=0-0"):
        result = _Response()
        transport.serve(result, "trusted-test-session",
                        range_headers=[header], attachment=False)
        assert result.status == 206
        assert result.headers["ETag"] == initial.headers["ETag"]
        assert transport._cache.render_count == 1
    assert project.head_revision_id() == head
    assert len(list(directory.glob("wav-*.wav"))) == 1
    transport._cache.clear_all_idle()
    assert not list(directory.glob("wav-*.wav"))


def test_cache_ttl_and_clean_restart_orphans(tmp_path: Path, monkeypatch):
    import musica.studio_wav_cache as module

    project, accepted, _, _ = _accept_arrangement(tmp_path)
    clock = [10000.0]
    monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])
    first = AcceptedWavRangeHTTP(_Service(project))
    old = _Response()
    first.serve(old, "trusted-test-session", range_headers=["bytes=44-49"],
                attachment=False)
    assert first._cache.render_count == 1
    assert len(list(first._cache.root.glob("wav-*.wav"))) == 1
    clock[0] += CACHE_IDLE_TTL_SECONDS + 0.5
    new = _Response()
    first.serve(new, "trusted-test-session", range_headers=["bytes=44-49"],
                attachment=False)
    assert first._cache.render_count == 2
    assert old.wfile.getvalue() == new.wfile.getvalue()
    assert len(list(first._cache.root.glob("wav-*.wav"))) == 1
    # Simulate an unclean Studio server restart with one orphan derived WAV.
    restarted = AcceptedWavRangeHTTP(_Service(project))
    assert restarted._cache.render_count == 0
    assert not list(first._cache.root.glob("wav-*.wav"))
    assert project.head_revision_id() == accepted["project"]["revision_id"]


def test_cache_refuses_symlink_workspace_and_tampered_source(tmp_path: Path):
    project, _accepted, _, _ = _accept_arrangement(tmp_path)
    cache = AcceptedWavFileCache(project.root.parent)
    data = cache.acquire("owner", project, project.head_revision_id(),
                         mix_sample_rate_hz=8000, routed=False)
    cache.release("owner")
    assert data.wav_path.is_file()
    entry = cache._entries["owner"]
    path, expected = entry.source_objects[0]
    assert path.is_file()
    # A digest violation may NEVER be returned from an older cached output.
    with path.open("r+b") as stream:
        stream.seek(-1, os.SEEK_END)
        before = stream.read(1)
        stream.seek(-1, os.SEEK_END)
        stream.write(bytes([before[0] ^ 0xFF]))
    with pytest.raises((ContractError, ProjectIntegrityError)):
        cache.acquire("owner", project, project.head_revision_id(),
                      mix_sample_rate_hz=8000, routed=False)
    cache.clear_all_idle()


def test_two_distinct_real_180s_sources_reuse_many_http_seeks_with_constant_rss(tmp_path):
    import resource

    project, head, a, b = _two_accepted_long_sources(tmp_path)
    transport = AcceptedWavRangeHTTP(_Service(project))
    ranges = [("bytes=44-51", (4000, -2500, 4000, -2500)),
              ("bytes=17280044-17280051", (4000, -2500, 4000, -2500)),
              ("bytes=-8", (4000, -2500, 4000, -2500))]
    etag = None
    for header, sample in ranges:
        h = _Response()
        transport.serve(h, "trusted-test-session",
                        range_headers=[header], attachment=False)
        assert h.status == 206
        assert h.headers["Content-Length"] == "8"
        assert len(h.wfile.getvalue()) == 8
        assert struct.unpack("<hhhh", h.wfile.getvalue()) == sample
        assert h.headers["Content-Range"].endswith("/34560044")
        if etag is None:
            etag = h.headers["ETag"]
        assert h.headers["ETag"] == etag
        assert transport._cache.render_count == 1
    assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss < 512 * 1024
    assert project.head_revision_id() == head
    assert a["asset_id"] != b["asset_id"]
    fixture = next(transport._cache.root.glob("wav-*.wav"))
    with wave.open(str(fixture), "rb") as source:
        assert (
            source.getframerate(), source.getnchannels(),
            source.getsampwidth(), source.getnframes()
        ) == (48000, 2, 2, 8_640_000)
    output_sha = hashlib.sha256(fixture.read_bytes()).hexdigest()
    artifact_dir = os.environ.get("MUSICA_G3B2C_R2_ARTIFACT_DIR")
    if artifact_dir:
        destination = Path(artifact_dir).resolve()
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fixture, destination / "accepted-range-cached-180s.wav")
        proof = {
            "milestone": "PROD-E2E-R2A-G3B2C-R2",
            "accepted_revision_id": head,
            "source_a_sha256": a["object_sha256"],
            "source_b_sha256": b["object_sha256"],
            "two_distinct_accepted_sources": a["asset_id"] != b["asset_id"],
            "format": "48000Hz stereo PCM16, 8640000 frames / 180s",
            "wav_size_bytes": fixture.stat().st_size,
            "wav_sha256": output_sha,
            "range_headers": [item[0] for item in ranges],
            "render_count_for_three_distinct_ranges": transport._cache.render_count,
            "cache_file_count": len(list(transport._cache.root.glob("wav-*.wav"))),
            "peak_process_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "accepted_head_unchanged": project.head_revision_id() == head,
            "browser_180s_full_flow_verified": False,
            "physical_device_verified": False,
        }
        (destination / "proof.json").write_text(
            json.dumps(proof, indent=2, sort_keys=True) + "\n",
            encoding="utf-8"
        )
    transport._cache.clear_all_idle()


def test_cache_output_corruption_forces_sha_verified_rerender(tmp_path: Path):
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    transport = AcceptedWavRangeHTTP(_Service(project))
    original = _Response()
    transport.serve(original, "trusted-test-session",
                    range_headers=["bytes=44-71"], attachment=False)
    assert transport._cache.render_count == 1
    output = next(transport._cache.root.glob("wav-*.wav"))
    with output.open("r+b") as stream:
        stream.seek(44)
        previous = stream.read(1)
        stream.seek(44)
        stream.write(bytes([previous[0] ^ 0xFF]))
    corrected = _Response()
    transport.serve(corrected, "trusted-test-session",
                    range_headers=["bytes=44-71"], attachment=False)
    assert transport._cache.render_count == 2
    assert corrected.wfile.getvalue() == original.wfile.getvalue()
    assert corrected.headers["ETag"] == original.headers["ETag"]
    assert len(list(transport._cache.root.glob("wav-*.wav"))) == 1
    assert project.head_revision_id() == accepted["project"]["revision_id"]


def test_cache_rejects_symlinked_root_without_touching_target(tmp_path: Path):
    workspace = tmp_path / "studio"
    workspace.mkdir()
    target = tmp_path / "user-directory"
    target.mkdir()
    important = target / "user-file.wav"
    important.write_bytes(b"private file remains untouched")
    (workspace / ".derived-accepted-wav-cache-g3b2c-r2").symlink_to(
        target, target_is_directory=True
    )
    with pytest.raises(ContractError, match="symlink"):
        AcceptedWavFileCache(workspace)
    assert important.read_bytes() == b"private file remains untouched"
