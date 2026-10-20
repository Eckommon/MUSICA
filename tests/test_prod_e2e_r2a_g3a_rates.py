"""R2A-G3A: exact standard-rate PCM fixtures and mixed-rate fail-closed."""
from __future__ import annotations

import io
import wave

import pytest

from musica import studio_audio
from musica.contracts import ContractError
from musica.prod_e2e_r1b_g1_browser import source_wav


@pytest.mark.parametrize("rate", [8000, 44100, 48000])
def test_user_chosen_wav_fixture_retains_exact_pcm_source(rate):
    data, samples = source_wav(3000, rate)
    with wave.open(io.BytesIO(data), "rb") as stream:
        assert stream.getnchannels() == 1
        assert stream.getsampwidth() == 2
        assert stream.getframerate() == rate
        assert stream.getnframes() == 2 * rate
        assert stream.readframes(stream.getnframes()) != bytes(4 * rate)
    assert len(samples) == 2 * rate
    assert max(map(abs, samples)) == 3000


def test_mixed_rates_explicitly_rejected_not_silently_resampled(monkeypatch):
    blueprint = {}
    monkeypatch.setattr(studio_audio, "_material", lambda _: {
        "tracks": [{"clips": [{"asset_id": "WAV-A"}, {"asset_id": "WAV-B"}]}]
    })
    monkeypatch.setattr(
        studio_audio, "read_audio_asset",
        lambda project, asset_id: {"format": {
            "sample_rate_hz": 44100 if asset_id == "WAV-A" else 48000
        }},
    )
    with pytest.raises(ContractError, match="one exact source sample rate"):
        studio_audio._mix_rate(object(), blueprint)
