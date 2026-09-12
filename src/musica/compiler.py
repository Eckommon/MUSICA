"""Deterministic Blueprint -> Music IR compiler for MUSICA.

MUSICA 결정론 Blueprint -> Music IR 컴파일러.

Legacy motif lowering remains unchanged. M6 adds an explicit exact-note timeline path
whose accepted note properties lower faithfully without hidden semantic rescaling.
"""

from __future__ import annotations

import re
from typing import Any

from .contracts import ContractError, exact_timeline, validate_contract

PPQ = 480
COMPILER_ID = "musica-deterministic-core"
COMPILER_VERSION = "0.1.0"

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
    raise ContractError(f"MUSICA compiler requires a part with role in {sorted(roles)}")


def _chord_root_midi(symbol: str) -> int:
    match = _CHORD.match(symbol)
    if not match or match.group(1) not in _NOTE_PC:
        raise ContractError(f"MUSICA compiler cannot parse chord symbol: {symbol!r}")
    return 36 + _NOTE_PC[match.group(1)]


def _section_for_seconds(blueprint: dict[str, Any], seconds: float) -> dict[str, Any]:
    for item in blueprint["form"]["sections"]:
        if float(item["start"]) <= seconds < float(item["end"]):
            return item
    return blueprint["form"]["sections"][-1]


def _semantic_at(blueprint: dict[str, Any], seconds: float) -> dict[str, float]:
    section = _section_for_seconds(blueprint, seconds)
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


def _control_event(tick: int, controller: int, value: float) -> dict[str, int | str]:
    normalized = max(0.0, min(1.0, float(value)))
    return {
        "type": "control",
        "tick": max(0, int(tick)),
        "controller": int(controller),
        "value": max(0, min(127, int(round(normalized * 127.0)))),
    }


def _semantic_controls(blueprint: dict[str, Any], bpm: float) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for section in blueprint["form"]["sections"]:
        seconds = float(section["start"])
        tick = round(seconds * bpm / 60.0 * PPQ)
        semantic = _semantic_at(blueprint, min(seconds + 1e-6, float(section["end"]) - 1e-6))
        events.extend(
            [
                _control_event(tick, 11, semantic.get("energy", 0.5)),
                _control_event(tick, 74, semantic.get("brightness", 0.5)),
                _control_event(tick, 71, semantic.get("warmth", 0.5)),
            ]
        )
    return sorted(events, key=lambda event: (event["tick"], event["controller"]))


def _compile_motif(
    blueprint: dict[str, Any], total_beats: float, bpm: float
) -> list[dict[str, Any]]:
    """Legacy motif path. Keep byte/logical behavior stable for existing projects."""

    melody = blueprint["materials"]["melody"]
    pattern_length = float(melody.get("motif_length_beats", 0))
    notes = melody.get("motif_notes")
    if not pattern_length or not isinstance(notes, list) or not notes:
        raise ContractError("MUSICA compiler requires melody.motif_length_beats and melody.motif_notes")

    events: list[dict[str, Any]] = []
    cycle = 0.0
    while cycle < total_beats:
        for note in notes:
            beat = cycle + float(note["offset_beats"])
            if beat >= total_beats:
                continue
            duration_beats = min(float(note["duration_beats"]), total_beats - beat)
            seconds = beat * 60.0 / bpm
            energy = _semantic_at(blueprint, seconds).get("energy", 0.5)
            expression = 0.72 + 0.56 * energy
            velocity = int(round(int(note["velocity"]) * expression))
            events.append(
                _note_event(
                    round(beat * PPQ),
                    round(duration_beats * PPQ),
                    int(note["pitch"]),
                    velocity,
                )
            )
        cycle += pattern_length
    return sorted(events, key=lambda event: (event["tick"], event["note"]))


def _compile_exact_timeline(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    """Lower accepted exact-note material faithfully to Music IR note events."""

    timeline = exact_timeline(blueprint)
    if timeline is None:
        raise ContractError("exact-note lowering requires melody.exact_timeline")
    events = [
        _note_event(
            round(float(note["start_beat"]) * PPQ),
            round(float(note["duration_beats"]) * PPQ),
            int(note["pitch"]),
            int(note["velocity"]),
        )
        for note in timeline["notes"]
    ]
    return sorted(
        events,
        key=lambda event: (event["tick"], event["note"], event["duration"], event["velocity"]),
    )


def _compile_drums(blueprint: dict[str, Any], total_beats: float) -> list[dict[str, Any]]:
    rhythm = blueprint["materials"]["rhythm"]
    pattern_length = float(rhythm.get("pattern_length_beats", 0))
    drum_events = rhythm.get("drum_events")
    if not pattern_length or not isinstance(drum_events, list) or not drum_events:
        raise ContractError("MUSICA compiler requires rhythm.pattern_length_beats and rhythm.drum_events")

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
        raise ContractError("MUSICA compiler requires harmony.progression")

    events: list[dict[str, Any]] = []
    bar = 0
    beat = 0.0
    while beat < total_beats:
        root = _chord_root_midi(str(progression[bar % len(progression)]))
        seconds = beat * 60.0 / bpm
        semantic = _semantic_at(blueprint, seconds)
        energy = semantic.get("energy", 0.5)
        tension = semantic.get("tension", 0.5)
        density = semantic.get("density", 0.5)
        motion = semantic.get("motion", 0.5)

        base_duration = min(1.5, total_beats - beat)
        base_velocity = int(round(58 + 32 * energy))
        events.append(_note_event(round(beat * PPQ), round(base_duration * PPQ), root, base_velocity))

        if density >= 0.68 and beat + 1.0 < total_beats:
            events.append(
                _note_event(round((beat + 1.0) * PPQ), round(0.50 * PPQ), root, int(round(48 + 24 * energy)))
            )
        if (tension >= 0.75 or motion >= 0.72) and beat + 2.0 < total_beats:
            events.append(
                _note_event(round((beat + 2.0) * PPQ), round(0.75 * PPQ), root + 7, int(round(52 + 22 * energy)))
            )
        if (density >= 0.82 or motion >= 0.82) and beat + 3.0 < total_beats:
            events.append(
                _note_event(round((beat + 3.0) * PPQ), round(0.45 * PPQ), root + 12, int(round(46 + 20 * energy)))
            )

        beat += 4.0
        bar += 1
    return sorted(events, key=lambda event: (event["tick"], event["note"]))


def compile_blueprint(blueprint: dict[str, Any]) -> dict[str, Any]:
    """Compile a validated Blueprint into deterministic Music IR v0."""

    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    bpm = float(blueprint["musical_context"]["tempo"]["bpm"])
    duration_seconds = float(blueprint["project"]["duration_seconds"])
    total_beats = duration_seconds * bpm / 60.0

    bass_part = _find_part(blueprint, {"propulsion", "foundation"})
    motif_part = _find_part(blueprint, {"motif", "lead"})
    drum_part = _find_part(blueprint, {"pulse"})
    sound_design = blueprint["materials"].get("sound_design", {})
    motif_program = int(sound_design.get("motif_program", 81))
    bass_program = int(sound_design.get("bass_program", 38))
    controls = _semantic_controls(blueprint, bpm)
    has_exact_timeline = exact_timeline(blueprint) is not None
    motif_events = (
        _compile_exact_timeline(blueprint)
        if has_exact_timeline
        else _compile_motif(blueprint, total_beats, bpm)
    )

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
                "program": motif_program,
                "events": sorted(
                    motif_events + controls,
                    key=lambda event: (event["tick"], 0 if event["type"] == "control" else 1, event.get("note", 0)),
                ),
            },
            {
                "track_id": "T-BASS",
                "part_id": bass_part["part_id"],
                "channel": 1,
                "program": bass_program,
                "events": sorted(
                    _compile_bass(blueprint, total_beats, bpm) + controls,
                    key=lambda event: (event["tick"], 0 if event["type"] == "control" else 1, event.get("note", 0)),
                ),
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
            "lowering_policy": (
                "explicit exact-note timeline + chord-root support + semantic controls + profile programs"
                if has_exact_timeline
                else "explicit motif/drums + chord-root support + six-axis semantic lowering + profile programs"
            ),
            "approximations": [
                "M1 semantic axes use explicit deterministic musical mechanisms, not universal perceptual models.",
                "CC71 is used as a MUSICA preview warmth control; external devices may interpret it differently.",
                "GM program numbers are preview intent, not production timbre guarantees.",
            ],
        },
    }
    validate_contract(ir, "music-ir-v0.schema.json")
    return ir
