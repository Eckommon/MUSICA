"""G3B2C-R4: genuine 180s pending candidate rendered in fixed blocks, never Accept."""
from __future__ import annotations

import resource
import struct
import threading
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import wave

import pytest

from musica.studio import StudioService, StudioServiceError
from musica.studio_audio import StudioAudioSurface, LONG_PREVIEW_STREAM_UNAVAILABLE
from musica.studio_routing import StudioRoutingSurface
from musica.studio_pending_wav import render_pending_preview_streamed
from musica.studio_http_r3 import create_local_server
from musica.streamed_native_mixer import render_native_mix_streamed

from test_atcm_r2_native_mixer import _candidate
from test_mram_r1_routing_authority_mixer import _routing_candidate
from test_prod_e2e_r2a_g3b2a_streamed_native import _two_accepted_long_sources
from test_prod_e2e_r2a_g3b2b_streamed_routed import _accept_long_two_buses


def _never_in_memory(*args, **kwargs):
    raise AssertionError("long Preview tried to decode whole song into memory")


def test_real_180s_native_preview_can_render_without_accept_or_legacy_heap(tmp_path):
    project, head, a, b = _two_accepted_long_sources(tmp_path)
    service = StudioService(tmp_path / "studio")
    service.open_project_session(project_slug="g3b2-long-two-track", session_id="pending-native")
    accepted = service._get_session("pending-native").project.read_revision(head)
    surface = StudioAudioSurface(service)
    surface._render_blueprint = _never_in_memory
    candidate = _candidate(
        accepted, "G3B2C-R4-PREVIEW-NATIVE",
        [{"operation_id": "R4-GAIN-A", "op": "SET_TRACK_MIXER",
          "target": {"track_id": "AT-G3B2-A"},
          "mixer": {"gain_db": -6.0, "pan": 0.0, "mute": False, "solo": False}}],
    )
    pending_response = surface.preview_audio_edit(
        "pending-native", candidate=candidate, candidate_kind="mixer"
    )
    assert pending_response["preview_installed"]
    session = service._get_session("pending-native")
    pending = session.pending
    assert pending is not None
    assert pending.descriptor["audio_available"] is False
    assert not pending.wav_path.exists()
    assert pending_response["audio_view"]["preview"]["audition"]["error"].startswith(
        LONG_PREVIEW_STREAM_UNAVAILABLE
    )
    assert project.head_revision_id() == head
    with pytest.raises(StudioServiceError, match="matching"):
        render_pending_preview_streamed(
            service, "pending-native", preview_id="wrong-preview-token"
        )
    derived = render_pending_preview_streamed(
        service, "pending-native", preview_id=pending.descriptor["preview_id"]
    )
    assert derived.candidate_revision_id != head
    assert derived.wav_size_bytes == 34_560_044
    assert derived.rendered_audio_is_canonical is False
    with wave.open(str(derived.wav_path), "rb") as reader:
        assert reader.getnframes() == 8_640_000
        for index in (0, 4_320_000, 8_639_999):
            reader.setpos(index)
            assert struct.unpack("<hh", reader.readframes(1)) == (2005, -2500)
    assert project.head_revision_id() == head
    assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss < 512 * 1024
    preview_sha = derived.wav_sha256
    derived.wav_path.unlink()
    # An actual localhost HTTP Range request must return the PENDING
    # candidate, not the accepted WAV and never accept the creative revision.
    server = create_local_server(service, host="127.0.0.1", port=0)
    runner = threading.Thread(target=server.serve_forever,
                              kwargs={"poll_interval": 0.01}, daemon=True)
    runner.start()
    try:
        _, port = server.server_address[:2]
        endpoint = (f"http://127.0.0.1:{port}/v0/sessions/pending-native/"
                    "audio/stream/preview.wav?preview_id=" +
                    pending.descriptor["preview_id"])
        with urlopen(Request(endpoint, headers={"Range": "bytes=44-47"}),
                     timeout=240) as response:
            assert response.status == 206
            assert response.headers["Content-Range"] == "bytes 44-47/34560044"
            assert response.headers["ETag"] == '"' + preview_sha + '"'
            assert response.headers["X-MUSICA-Pending-Preview-ID"] == pending.descriptor["preview_id"]
            assert struct.unpack("<hh", response.read()) == (2005, -2500)
        with pytest.raises(HTTPError) as refused:
            urlopen(endpoint + "-invalid", timeout=5)
        assert refused.value.code == 404
        assert project.head_revision_id() == head
    finally:
        server.shutdown()
        server.server_close()
        runner.join(timeout=5)
    assert not runner.is_alive()
    # Only an explicit trusted user Accept changes the canonical creative HEAD.
    surface.accept_audio_preview("pending-native")
    newly_accepted = project.head_revision_id()
    assert newly_accepted != head
    accepted_mix = render_native_mix_streamed(
        project, newly_accepted, mix_sample_rate_hz=48000, block_frames=8191
    )
    assert accepted_mix.wav_sha256 == preview_sha
    accepted_mix.wav_path.unlink()
    with pytest.raises(StudioServiceError, match="matching"):
        render_pending_preview_streamed(
            service, "pending-native", preview_id=pending.descriptor["preview_id"]
        )


def test_real_180s_routing_preview_separate_from_accepted_head(tmp_path):
    project, head, a, b = _accept_long_two_buses(tmp_path)
    service = StudioService(tmp_path / "studio")
    service.open_project_session(project_slug="g3b2-long-two-track", session_id="pending-routed")
    accepted = service._get_session("pending-routed").project.read_revision(head)
    surface = StudioRoutingSurface(service)
    surface.audio_surface._render_blueprint = _never_in_memory
    candidate = _routing_candidate(
        accepted, "G3B2C-R4-PREVIEW-ROUTE",
        [{"operation_id": "R4-ROUTE-A", "op": "SET_TRACK_OUTPUT",
          "track_id": "AT-G3B2-A", "target_node_id": "MASTER-G3B2"}],
    )
    response = surface.preview_routing_edit("pending-routed", candidate=candidate)
    assert response["preview_installed"]
    pending = service._get_session("pending-routed").pending
    assert pending is not None
    assert pending.descriptor["audio_available"] is False
    assert pending.detail["routed_audition"]["error"].startswith(
        LONG_PREVIEW_STREAM_UNAVAILABLE
    )
    assert project.head_revision_id() == head
    preview = render_pending_preview_streamed(
        service, "pending-routed", preview_id=pending.descriptor["preview_id"]
    )
    assert preview.routed
    assert preview.wav_size_bytes == 34_560_044
    with wave.open(str(preview.wav_path), "rb") as reader:
        for frame in (0, 4_320_000, 8_639_999):
            reader.setpos(frame)
            assert struct.unpack("<hh", reader.readframes(1)) == (4000, -2500)
    assert project.head_revision_id() == head
    assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss < 512 * 1024
    preview.wav_path.unlink()
    service.discard_preview("pending-routed")
    assert project.head_revision_id() == head
