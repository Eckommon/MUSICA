"""Bounded M1 creative style profiles / 제한된 M1 창작 스타일 프로필.

Profiles are explicit implementation data, not claims of universal genre modeling.
프로필은 명시적 구현 데이터이며 보편적 장르 모델을 주장하지 않습니다.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

STYLE_PROFILES: dict[str, dict[str, Any]] = {
    "dark_electronic": {
        "default_bpm": 112,
        "tempo_range": [96, 124],
        "default_key": "D",
        "default_mode": "minor",
        "motif_program": 81,
        "bass_program": 38,
        "motif_family": "dark_synth",
        "bass_family": "bass_synth",
        "pulse_family": "electronic_drums",
        "bass_role": "propulsion",
        "motif_register_base": 62,
        "motif_degree_pattern": [0, 2, 4, 3],
        "motif_rhythm": [0.75, 0.75, 1.50],
        "drum_events": [
            {"offset_beats": 0.0, "note": 36, "duration_beats": 0.18, "velocity": 108},
            {"offset_beats": 1.0, "note": 42, "duration_beats": 0.12, "velocity": 66},
            {"offset_beats": 2.0, "note": 38, "duration_beats": 0.18, "velocity": 96},
            {"offset_beats": 3.0, "note": 42, "duration_beats": 0.12, "velocity": 70}
        ],
        "texture_base_layers": 4,
        "character": ["dark", "synthetic", "controlled"],
        "section_labels": ["reveal", "build", "resolve-pressure"]
    },
    "warm_ambient": {
        "default_bpm": 84,
        "tempo_range": [68, 98],
        "default_key": "G",
        "default_mode": "major",
        "motif_program": 89,
        "bass_program": 43,
        "motif_family": "soft_pad",
        "bass_family": "warm_low_strings",
        "pulse_family": "soft_percussion",
        "bass_role": "foundation",
        "motif_register_base": 67,
        "motif_degree_pattern": [0, 4, 2, 5],
        "motif_rhythm": [1.50, 1.00, 1.25],
        "drum_events": [
            {"offset_beats": 0.0, "note": 36, "duration_beats": 0.22, "velocity": 64},
            {"offset_beats": 2.0, "note": 42, "duration_beats": 0.16, "velocity": 46}
        ],
        "texture_base_layers": 3,
        "character": ["warm", "open", "ambient"],
        "section_labels": ["open", "float", "settle"]
    },
    "kinetic_minimal": {
        "default_bpm": 124,
        "tempo_range": [108, 138],
        "default_key": "A",
        "default_mode": "minor",
        "motif_program": 80,
        "bass_program": 39,
        "motif_family": "minimal_pluck",
        "bass_family": "tight_synth_bass",
        "pulse_family": "minimal_electronic_drums",
        "bass_role": "propulsion",
        "motif_register_base": 69,
        "motif_degree_pattern": [0, 1, 4, 2],
        "motif_rhythm": [0.50, 0.50, 1.00, 1.00],
        "drum_events": [
            {"offset_beats": 0.0, "note": 36, "duration_beats": 0.14, "velocity": 104},
            {"offset_beats": 1.0, "note": 42, "duration_beats": 0.10, "velocity": 72},
            {"offset_beats": 1.5, "note": 42, "duration_beats": 0.10, "velocity": 58},
            {"offset_beats": 2.0, "note": 38, "duration_beats": 0.14, "velocity": 92},
            {"offset_beats": 3.0, "note": 42, "duration_beats": 0.10, "velocity": 76},
            {"offset_beats": 3.5, "note": 42, "duration_beats": 0.10, "velocity": 60}
        ],
        "texture_base_layers": 3,
        "character": ["kinetic", "minimal", "precise"],
        "section_labels": ["pulse", "drive", "focus"]
    }
}


def get_style_profile(name: str) -> dict[str, Any]:
    """Return a defensive copy of one accepted M1 profile."""

    try:
        return deepcopy(STYLE_PROFILES[name])
    except KeyError as exc:
        raise ValueError(f"unknown M1 style profile: {name}") from exc
