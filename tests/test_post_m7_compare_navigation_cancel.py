"""Post-M7 navigation cancellation classifier: narrow, audited no-waiver tests."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from musica.post_m7_revision_compare_e2e import _attach_observers


@dataclass(eq=False)
class Request:
    method: str
    url: str
    failure: str = "net::ERR_ABORTED"


class FakePage:
    def __init__(self) -> None:
        self.handlers = defaultdict(list)

    def on(self, event, callback):
        self.handlers[event].append(callback)

    def emit(self, event, payload):
        for handler in self.handlers[event]:
            handler(payload)


def recorder():
    page = FakePage()
    console_errors, page_errors, failed, expected = [], [], [], []
    arm = _attach_observers(page, console_errors, page_errors, failed, expected)
    return page, arm, failed, expected


def test_navigation_allows_only_preexisting_session_audio_and_health_get_aborts():
    page, arm, failed, expected = recorder()
    audio = Request("GET", "http://127.0.0.1:4321/v0/sessions/studio-1/media/audio.wav?v=987")
    health = Request("GET", "http://127.0.0.1:4321/v0/health")
    for item in (audio, health):
        page.emit("request", item)
    arm()
    for item in (audio, health):
        page.emit("requestfailed", item)
    assert len(expected) == 2
    assert not failed


def test_new_health_abort_after_reload_arm_is_a_real_failure():
    page, arm, failed, expected = recorder()
    arm()
    new_health = Request("GET", "http://127.0.0.1:4321/v0/health")
    page.emit("request", new_health)
    page.emit("requestfailed", new_health)
    assert len(failed) == 1 and not expected


def test_old_nonmedia_400_and_other_transport_errors_remain_failures():
    page, arm, failed, expected = recorder()
    history = Request("GET", "http://127.0.0.1:4321/v0/sessions/studio-1/history")
    post = Request("POST", "http://127.0.0.1:4321/v0/sessions/studio-1/media/audio.wav")
    for item in (history, post):
        page.emit("request", item)
    arm()
    page.emit("requestfailed", history)
    page.emit("requestfailed", post)
    assert len(failed) == 2
    assert not expected


def test_audio_abort_without_intentional_reload_remains_failure():
    page, arm, failed, expected = recorder()
    audio = Request("GET", "http://127.0.0.1:4321/v0/sessions/s1/media/audio.wav")
    page.emit("request", audio)
    page.emit("requestfailed", audio)
    assert len(failed) == 1
    assert not expected


def test_original_revision_media_source_switch_abort_still_expected():
    page, arm, failed, expected = recorder()
    audio = Request("GET", "http://127.0.0.1:4321/v0/sessions/s1/revisions/r1/media/audio.wav")
    page.emit("request", audio)
    page.emit("requestfailed", audio)
    assert expected and not failed


def test_http_error_remains_hard_failure_even_at_reload():
    page, arm, failed, expected = recorder()
    req = Request("GET", "http://127.0.0.1:4321/v0/health")
    page.emit("request", req)
    arm()
    class Response:
        status = 502
        request = req
        url = req.url
        def text(self): return "Server Error"
    page.emit("response", Response())
    assert len(failed) == 1 and "HTTP 502" in failed[0]
    assert not expected


def test_explicit_browser_close_only_categorizes_prior_health_probe():
    """An in-flight health poll abort on page.close is not a server failure."""
    page, arm_close, failed, expected = recorder()
    stale_health = Request("GET", "http://127.0.0.1:4321/v0/health")
    page.emit("request", stale_health)
    arm_close()  # immediately before the test explicitly calls page.close()
    page.emit("requestfailed", stale_health)
    new_health = Request("GET", "http://127.0.0.1:4321/v0/health")
    page.emit("request", new_health)
    page.emit("requestfailed", new_health)
    assert len(expected) == 1 and "/v0/health" in expected[0]
    assert len(failed) == 1 and "/v0/health" in failed[0]
