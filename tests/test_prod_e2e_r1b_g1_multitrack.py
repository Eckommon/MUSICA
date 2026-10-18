"""R1B-G1: source-bound repeated Browser audio editing is present and non-autoritative."""
from __future__ import annotations

import hashlib
from musica.prod_e2e_r1b_g1_browser import source_wav


def test_distinct_deterministic_pcm_sources_and_real_wav_headers():
    import io
    import wave
    first, a = source_wav(3000)
    second, b = source_wav(6200)
    assert hashlib.sha256(first).hexdigest() != hashlib.sha256(second).hexdigest()
    assert len(a) == len(b) == 16000
    with wave.open(io.BytesIO(first), "rb") as w:
        assert (w.getnframes(), w.getnchannels(), w.getframerate(), w.getsampwidth()) == (16000, 1, 8000, 2)


def test_multitrack_browser_unique_id_suggestions_do_not_accept_or_submit():
    from importlib import resources
    script = resources.files("musica.studio_web").joinpath("native_audio.js").read_text()
    guide = resources.files("musica.studio_web").joinpath("production_guide.js").read_text()
    assert 'id="r3SuggestTrackId"' in script
    assert 'id="r3SuggestClipId"' in script
    assert 'function uniqueId(prefix, used)' in script
    assert 'function suggestTrackId()' in script
    assert 'function suggestClipId()' in script
    assert 'const previouslySelectedTrack = select.value' in script
    assert 'select.value = previouslySelectedTrack' in script
    # The suggestion-only bodies may change HTML input values, but must not
    # submit creative candidates or call trusted Accept.
    block = script.split("function suggestTrackId() {", 1)[1].split("function previewAddTrack()", 1)[0]
    assert "audio/accept" not in block and "submit(" not in block
    assert "2 TRACKS / " not in script and 'String(p.trackCount) + " TRACKS / "' in guide


def test_repeated_audio_and_mixer_revisions_are_parent_bound_and_bounded():
    from musica.audio_edit import _revision_id as next_arrangement
    from musica.audio_mixer_edit import _revision_id as next_mixer

    # Simulate a legacy long revision, then 30 consecutive user edits.
    parent = {"project": {"revision_id": "rev-old-" + ("x" * 320)}}
    identities = set()
    for index in range(30):
        candidate = {
            "candidate_id": "G1-" + str(index),
            "source": {"revision_id": parent["project"]["revision_id"]},
            "operations": [{"operation_id": "G1-OP-" + str(index)}],
        }
        revision_id = (next_arrangement if index % 2 == 0 else next_mixer)(parent, candidate)
        same = (next_arrangement if index % 2 == 0 else next_mixer)(parent, candidate)
        assert revision_id == same, "identical parent/candidate must replay identically"
        assert revision_id.startswith("rev-audio-" if index % 2 == 0 else "rev-mixer-")
        assert len(revision_id) <= 64, "repeated user edits must not grow revision IDs"
        assert revision_id not in identities
        identities.add(revision_id)
        parent = {"project": {"revision_id": revision_id}}

    forged_parent = {"project": {"revision_id": "rev-different"}}
    assert next_arrangement(forged_parent, candidate) != next_arrangement(parent, candidate)
