"""Deterministic Blueprint -> Music IR compiler for MUSICA M0-R2.

MUSICA M0-R2 결정론 Blueprint -> Music IR 컴파일러.
"""

from __future__ import annotations

import re
from typing import Any

from .contracts import ContractError, validate_contract

PPQ = 480
COMPILER_ID = "musica-deterministic-m0"
COMPILER_VERSION = "0.0.1"

_NOTE_PC = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}
_CHORD = re.compile(r"^([A-G](?:#|b)?)(m)?")


def _find_part(blueprint: dict[str, Any], roles: set[str]) -> dict[str, Any]:
    for part in blueprint["roles"]["instruments_or_parts"]:
        if part["role"] in roles:
            return part
    raise ContractError(f"M0 compiler requires a part with role in {sorted(roles)}")


def _chord_root_midi(symbol: str) -> int:
    match = _CHORD.match(symbol)
    if not match or match.group(1) not in _NOTE_PC:
        raise ContractError(f"M0 compiler cannot parse chord symbol: {symbol!r}")
    return 36 + _NOTE_PC[match.group(1)]  # C2-based bass register.


def _semantic_at(blueprint: dict[str, Any], seconds: float) -> dict[str, float]:
    section = None
    for item in blueprint["form"]["sections"]:
        if float(item["start"]) <= seconds < float(item["end"]):
            section = item
            break
    if section is None:
        section = blueprint["form"]["sections"][-1]

    values = dict(blueprint["semantics"]["global"])
    values.update(section.get("semantic_targets", {}))
    for override in blueprint["semantics"].get("section_overrides", []):
        if override["section_id"] == section["section_id"]:
            values.update(override["values"])
    return {key: float(value) for key, value in values.items()}


def _note_event(tick: int, duration: int, note: int, velocity: int) -> dict[str, int | str]:
    return {
        "type": "note",
        "tick": max(0, int(tick)),
        "duration": max(1, int(duration)),
        "note": max(0, min(127, int(note))),
        "velocity": max(1, min(127, int(velocity))),
    }


def _compile_motif(blueprint: dict[str, Any], total_beats: float) -> list[dict[str, Any]]:
    melody = blueprint["materials"]["melody"]
    pattern_length = float(melody.get("motif_length_beats", 0))
    notes = melody.get("motif_notes")
    if not pattern_length or not isinstance(notes, list) or not notes:
        raise ContractError("M0 compiler requires melody.motif_length_beats and melody.motif_notes")

    events: list[dict[str, Any]] = []
    cycle = 0.0
    while cycle < total_beats:
        for note in notes:
            beat = cycle + float(note["offset_beats"])
            if beat >= total_beats:
                continue
            duration_beats = min(float(note["duration_beats"]), total_beats - beat)
            events.append(
                _note_event(
                    round(beat * PPQ),
                    round(duration_beats * PPQ),
                    int(note["pitch"]),
                    int(note["velocity"]),
                )
            )
        cycle += pattern_length
    return sorted(events, key=lambda event: (event["tick"], event["note"]))


def _compile_drums(blueprint: dict[str, Any], total_beats: float) -> list[dict[str, Any]]:
    rhythm = blueprint["materials"]["rhythm"]
    pattern_length = float(rhythm.get("pattern_length_beats", 0))
    drum_events = rhythm.get("drum_events")
    if not pattern_length or not isinstance(drum_events, list) or not drum_events:
        raise ContractError("M0 compiler requires rhythm.pattern_length_beats and rhythm.drum_events")

    events: list[dict[str, Any]] = []
    cycle = 0.0
    while cycle < total_beats:
        for item in drum_events:
            beat = cycle + float(item["offset_beats"])
            if beat >= total_beats:
                continue
            duration_beats = min(float(item["duration_beats"]), total_beats - beat)
            events.append(
                _note_event(
                    round(beat * PPQ),
                    round(duration_beats * PPQ),
                    int(item["note"]),
                    int(item["velocity"]),
                )
            )
        cycle += pattern_length
    return sorted(events, key=lambda event: (event["tick"], event["note"]))


def _compile_bass(blueprint: dict[str, Any], total_beats: float, bpm: float) -> list[dict[str, Any]]:
    progression = blueprint["materials"]["harmony"].get("progression")
    if not isinstance(progression, list) or not progression:
        raise ContractError("M0 compiler requires harmony.progression")

    events: list[dict[str, Any]] = []
    bar = 0
    beat = 0.0
    while beat < total_beats:
        root = _chord_root_midi(str(progression[bar % len(progression)]))
        base_duration = min(1.5, total_beats - beat)
        events.append(_note_event(round(beat * PPQ), round(base_duration * PPQ), root, 76))

        seconds = beat * 60.0 / bpm
        semantic = _semantic_at(blueprint, seconds)
        tension = semantic.get("tension", 0.5)
        motion = semantic.get("motion", 0.5)
        # M0 lowering rule: sufficiently high semantic pressure adds one allowed
        # mid-bar bass event. Tempo, motif and drum pattern remain untouched.
        if (tension >= 0.75 or motion >= 0.72) and beat + 2.0 < total_beats:
            passing = root + 7
            events.append(_note_event(round((beat + 2.0) * PPQ), round(0.75 * PPQ), passing, 68))

        beat += 4.0
        bar += 1
    return sorted(events, key=lambda event: (event["tick"], event["note"]))


def compile_blueprint(blueprint: dict[str, Any]) -> dict[str, Any]:
    """Compile a validated M0 Blueprint into deterministic Music IR."""

    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    bpm = float(blueprint["musical_context"]["tempo"]["bpm"])
    duration_seconds = float(blueprint["project"]["duration_seconds"])
    total_beats = duration_seconds * bpm / 60.0

    bass_part = _find_part(blueprint, {"propulsion", "foundation"})
    motif_part = _find_part(blueprint, {"motif", "lead"})
    drum_part = _find_part(blueprint, {"pulse"})

    ir = {
        "ir_version": "0",
        "source_blueprint_revision": blueprint["project"]["revision_id"],
        "timing": {"ppq": PPQ},
        "tempo_events": [{"tick": 0, "bpm": bpm}],
        "tracks": [
            {
                "track_id": "T-MOTIF",
                "part_id": motif_part["part_id"],
                "channel": 0,
                "program": 81,
                "events": _compile_motif(blueprint, total_beats),
            },
            {
                "track_id": "T-BASS",
                "part_id": bass_part["part_id"],
                "channel": 1,
                "program": 38,
                "events": _compile_bass(blueprint, total_beats, bpm),
            },
            {
                "track_id": "T-DRUMS",
                "part_id": drum_part["part_id"],
                "channel": 9,
                "program": 0,
                "events": _compile_drums(blueprint, total_beats),
            },
        ],
        "compile_provenance": {
            "compiler_id": COMPILER_ID,
            "compiler_version": COMPILER_VERSION,
            "lowering_policy": "M0 explicit motif/drum events + chord-root bass + semantic-pressure bass density",
            "approximations": [
                "Semantic tension/motion are lowered only to a deterministic bass-density rule in M0.",
                "GM program numbers are preview intent, not production timbre guarantees."
            ],
        },
    }
    validate_contract(ir, "music-ir-v0.schema.json")
    return ir
