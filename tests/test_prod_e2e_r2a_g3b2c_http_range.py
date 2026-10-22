"""G3B2C-R1: accepted-source local HTTP transport, single-range and cleanup."""
from __future__ import annotations

import io
import struct
import resource
import hashlib
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from types import SimpleNamespace

import pytest

from musica.native_mixer import render_native_mix
from musica.audio_assets import import_audio_asset
from musica.audio_edit import build_audio_edit_preview, accept_audio_edit_preview
from musica.studio import StudioService
from musica.studio_http_r3 import create_local_server
from musica.studio import StudioServiceError
from musica.studio_wav_http_range import (
    AcceptedWavRangeHTTP, HTTP_WRITE_CHUNK_BYTES, wav_byte_range,
)
from test_atcm_r2_native_mixer import _accept_arrangement, _candidate, _wav_bytes
from test_prod_e2e_r2a_g3b2a_streamed_native import _two_accepted_long_sources


class _Service:
    def __init__(self, project) -> None:
        self.project = project

    def _get_session(self, session_id: str):
        if session_id != "trusted-test-session":
            raise StudioServiceError("not_found", "unknown accepted session")
        return SimpleNamespace(project=self.project)


class _Response:
    def __init__(self) -> None:
        self.status: int | None = None
        self.headers: dict[str, str] = {}
        self.wfile = io.BytesIO()
        self.close_connection = False
        self.ended = False

    def send_response(self, status: int) -> None:
        self.status = int(status)

    def send_header(self, name: str, value: str) -> None:
        self.headers[name] = value

    def end_headers(self) -> None:
        self.ended = True


@pytest.mark.parametrize(
    ("header", "size", "expected"),
    [
        (None, 100, (200, 0, 99)),
        ("bytes=0-0", 100, (206, 0, 0)),
        ("bytes=30-60", 100, (206, 30, 60)),
        ("bytes=30-", 100, (206, 30, 99)),
        ("bytes=90-150", 100, (206, 90, 99)),
        ("bytes=-7", 100, (206, 93, 99)),
        ("bytes=-200", 100, (206, 0, 99)),
    ],
)
def test_byte_ranges_are_exact_single_closed_or_suffix(header, size, expected):
    assert wav_byte_range(header, size) == expected


@pytest.mark.parametrize(
    "header",
    [
        "", "bytes=", "bytes=-", "bytes=100-",
        "bytes=22-21", "bytes=0-0,10-11", "Bytes=0-5",
        "bytes=1--2", "bytes=-0", "bytes= 1-5",
        "bytes=1-5 ", "bytes=+1-5", "bytes=0-0\r\nContent-Length: 4",
        "bytes=" + "1" * 110 + "-",
    ],
)
def test_bad_or_multiple_ranges_fail_closed(header):
    with pytest.raises(ValueError):
        wav_byte_range(header, 100)


def test_actual_accepted_pcm_byte_ranges_preserve_head_and_cleanup(tmp_path):
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    revision_id = accepted["project"]["revision_id"]
    expected = render_native_mix(
        project, revision_id, mix_sample_rate_hz=8000
    ).wav_bytes
    service = _Service(project)
    server = AcceptedWavRangeHTTP(service)

    original = _Response()
    server.serve(
        original, "trusted-test-session",
        range_headers=[], attachment=True
    )
    assert original.status == 200
    assert original.wfile.getvalue() == expected
    assert original.headers["Content-Type"] == "audio/wav"
    assert original.headers["Content-Length"] == str(len(expected))
    assert original.headers["Accept-Ranges"] == "bytes"
    assert original.headers["Content-Disposition"] == 'attachment; filename="musica-accepted.wav"'

    partial = _Response()
    server.serve(
        partial, "trusted-test-session",
        range_headers=["bytes=44-88"], attachment=False
    )
    assert partial.status == 206
    assert partial.headers["Content-Range"] == f"bytes 44-88/{len(expected)}"
    assert int(partial.headers["Content-Length"]) == 45
    assert partial.wfile.getvalue() == expected[44:89]
    assert partial.headers["ETag"] == original.headers["ETag"]
    assert "Content-Disposition" not in partial.headers

    suffix = _Response()
    server.serve(
        suffix, "trusted-test-session",
        range_headers=["bytes=-19"], attachment=False
    )
    assert suffix.status == 206
    assert suffix.wfile.getvalue() == expected[-19:]

    refused = _Response()
    server.serve(
        refused, "trusted-test-session",
        range_headers=["bytes=0-4", "bytes=15-20"], attachment=False
    )
    assert refused.status == 416
    assert refused.headers["Content-Range"] == f"bytes */{len(expected)}"
    assert refused.wfile.getvalue() == b""
    assert project.head_revision_id() == revision_id
    assert not list((project.root / ".derived-streamed-native-g3b2").glob("*.wav"))
    assert HTTP_WRITE_CHUNK_BYTES <= 1024 * 1024


def test_untrusted_session_and_busy_fail_without_new_output(tmp_path):
    project, accepted, _, _ = _accept_arrangement(tmp_path)
    server = AcceptedWavRangeHTTP(_Service(project))
    with pytest.raises(StudioServiceError, match="unknown accepted session"):
        server.serve(
            _Response(), "foreign", range_headers=[], attachment=False
        )
    server._enter("trusted-test-session")
    try:
        with pytest.raises(StudioServiceError, match="already active"):
            server.serve(
                _Response(), "trusted-test-session",
                range_headers=[], attachment=False,
            )
    finally:
        server._exit("trusted-test-session")
    assert project.head_revision_id() == accepted["project"]["revision_id"]


def test_real_local_http_200_206_416_acceptance_and_no_head_mutation(tmp_path):
    """Actual loopback ThreadingHTTPServer, not a fake handler."""
    service = StudioService(tmp_path / "workspace")
    service.create_project_session(
        project_slug="g3b2c-http-stream",
        session_id="range-owner",
        user_text="Test 12 second accepted WAV",
        provider_mode="fixture",
        duration_seconds=12, use_case="song",
        style_profile="dark_electronic", seed=205,
    )
    project = service._get_session("range-owner").project
    before = project.read_revision(project.head_revision_id())
    src = tmp_path / "short.wav"
    src.write_bytes(_wav_bytes(channels=1, sample_rate=8000, frames=800,
                               left=4800))
    asset = import_audio_asset(project, src)
    operations = [
        {"operation_id": "RANGE-TRACK", "op": "ADD_TRACK",
         "track_id": "AT-RANGE", "order": 0, "name": "Range proof"},
        {"operation_id": "RANGE-CLIP", "op": "ADD_CLIP",
         "target": {"track_id": "AT-RANGE"},
         "clip": {"clip_id": "AC-RANGE", "asset_id": asset["asset_id"],
                  "timeline_start_seconds": 0.0, "source_in_seconds": 0.0,
                  "source_out_seconds": 0.1, "gain_db": 0.0}},
    ]
    preview = build_audio_edit_preview(
        project, before, _candidate(before, "RANGE-HTTP-ACCEPT", operations)
    )
    assert preview.ready
    assert project.head_revision_id() == before["project"]["revision_id"]
    accepted = accept_audio_edit_preview(project, preview)
    head = accepted["revision_id"]
    reference = render_native_mix(
        project, head, mix_sample_rate_hz=8000
    ).wav_bytes

    server = create_local_server(service, host="127.0.0.1", port=0)
    runner = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01},
        daemon=True,
    )
    runner.start()
    try:
        host, port = server.server_address[:2]
        address = f"http://{host}:{port}/v0/sessions/range-owner/audio/stream/accepted.wav"
        with urlopen(address, timeout=45) as response:
            assert response.status == 200
            assert response.headers["Content-Length"] == str(len(reference))
            assert response.read() == reference
            etag = response.headers["ETag"]
        request = Request(address, headers={"Range": "bytes=44-90"})
        with urlopen(request, timeout=45) as response:
            assert response.status == 206
            assert response.headers["Content-Range"] == f"bytes 44-90/{len(reference)}"
            assert response.headers["ETag"] == etag
            assert response.read() == reference[44:91]
        request = Request(address + "?download=1", headers={"Range": "bytes=-2"})
        with urlopen(request, timeout=45) as response:
            assert response.status == 206
            assert "attachment" in response.headers["Content-Disposition"]
            assert response.read() == reference[-2:]
        request = Request(address, headers={"Range": "bytes=99999999-"})
        with pytest.raises(HTTPError) as unsatisfied:
            urlopen(request, timeout=45)
        assert unsatisfied.value.code == 416
        assert unsatisfied.value.headers["Content-Range"] == f"bytes */{len(reference)}"
        assert project.head_revision_id() == head
        assert not list((project.root / ".derived-streamed-native-g3b2").glob("*.wav"))
    finally:
        server.shutdown()
        server.server_close()
        runner.join(timeout=5)


def test_real_local_http_180s_accepted_stereo_range_memory_and_cleanup(tmp_path):
    """Real HTTP single-range from the two-track accepted 180s project."""
    project, head, left_source, right_source = _two_accepted_long_sources(tmp_path)
    service = StudioService(tmp_path / "studio")
    service.open_project_session(
        project_slug="g3b2-long-two-track",
        session_id="long-range",
    )
    current = service._get_session("long-range").project
    assert current.head_revision_id() == head
    server = create_local_server(service, host="127.0.0.1", port=0)
    runner = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01}, daemon=True,
    )
    runner.start()
    try:
        host, port = server.server_address[:2]
        url = (f"http://{host}:{port}/v0/sessions/long-range/audio/stream/"
               "accepted.wav")
        request = Request(url, headers={"Range": "bytes=44-51"})
        with urlopen(request, timeout=180) as response:
            assert response.status == 206
            assert response.headers["Content-Range"] == "bytes 44-51/34560044"
            assert response.headers["Content-Length"] == "8"
            assert struct.unpack("<hhhh", response.read()) == (
                4000, -2500, 4000, -2500
            )
            assert response.headers["Accept-Ranges"] == "bytes"
        assert current.head_revision_id() == head
        assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss < 512 * 1024
        assert not list((current.root / ".derived-streamed-native-g3b2").glob("*.wav"))
        assert left_source["asset_id"] != right_source["asset_id"]
    finally:
        server.shutdown()
        server.server_close()
        runner.join(timeout=5)
