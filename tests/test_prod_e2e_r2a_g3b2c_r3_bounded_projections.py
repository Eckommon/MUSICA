"""G3B2C-R3: full-song Studio projection must NEVER invoke legacy full-buffer render."""
from __future__ import annotations

from musica.studio import StudioService
from musica.studio_audio import (
    StudioAudioSurface, LONG_AUDIO_STREAM_REQUIRED,
    LONG_PREVIEW_STREAM_UNAVAILABLE, long_audio_needs_streaming,
)
from musica.studio_routing import StudioRoutingSurface

from test_prod_e2e_r2a_g3b2a_streamed_native import _two_accepted_long_sources
from test_prod_e2e_r2a_g3b2b_streamed_routed import _accept_long_two_buses


def _trap(*args, **kwargs):
    raise AssertionError("whole-song legacy renderer called during read-only Studio projection")


def test_180s_native_studio_view_avoids_whole_buffer_and_keeps_head(tmp_path):
    original_project, head, a, b = _two_accepted_long_sources(tmp_path)
    service = StudioService(tmp_path / "studio")
    service.open_project_session(
        project_slug="g3b2-long-two-track",
        session_id="native-long-view",
    )
    project = service._get_session("native-long-view").project
    surface = StudioAudioSurface(service)
    surface._render_blueprint = _trap
    blueprint = project.read_revision(head)
    assert long_audio_needs_streaming(project, blueprint)
    original_objects = len(list((project.root / "objects").glob("**/*")))
    view = surface.audio_view("native-long-view")
    assert view["revision_id"] == head
    assert len(view["tracks"]) == 2
    assert view["accepted_audition"]["available"] is False
    assert view["accepted_audition"]["wav_sha256"] is None
    assert view["accepted_audition"]["error"].startswith(LONG_AUDIO_STREAM_REQUIRED)
    assert project.head_revision_id() == head
    assert len(list((project.root / "objects").glob("**/*"))) == original_objects
    preview = surface._audition_summary(
        "native-long-view", project, blueprint, source_kind="preview",
    )
    assert preview["available"] is False
    assert preview["error"].startswith(LONG_PREVIEW_STREAM_UNAVAILABLE)
    assert project.head_revision_id() == head


def test_180s_routed_studio_view_avoids_full_buffers_and_false_preview(tmp_path):
    project, head, a, b = _accept_long_two_buses(tmp_path)
    service = StudioService(tmp_path / "studio")
    service.open_project_session(
        project_slug="g3b2-long-two-track",
        session_id="routed-long-view",
    )
    accepted = service._get_session("routed-long-view").project
    routed = StudioRoutingSurface(service)
    routed.audio_surface._render_blueprint = _trap
    view = routed.routing_view("routed-long-view")
    assert view["revision_id"] == head
    assert view["accepted_audition"]["available"] is False
    assert view["accepted_audition"]["error"].startswith(LONG_AUDIO_STREAM_REQUIRED)
    assert len(view["nodes"]) >= 3
    preview = routed._audition(
        "routed-long-view",
        accepted,
        accepted.read_revision(head),
        source_kind="preview-routing",
    )
    assert preview["available"] is False
    assert preview["error"].startswith(LONG_PREVIEW_STREAM_UNAVAILABLE)
    assert accepted.head_revision_id() == head
