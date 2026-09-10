"""MUSICA M1 deterministic Creative Planner and Blueprint Composer.

MUSICA M1 결정론 Creative Planner 및 Blueprint Composer.

The M1 planner accepts a validated bounded Music Intent contract. It intentionally does
not claim arbitrary language understanding; later AI providers may produce the same
contract and reuse this deterministic creative core.
"""

from __future__ import annotations

import hashlib
from typing import Any, Sequence, TypeVar

from .contracts import ContractError, validate_contract
from .profiles import get_style_profile

T = TypeVar("T")

NOTE_PC = {
    "C": 0, "C#": 1, "D": 2, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11,
}
PC_NAME = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
}
M1_SEMANTIC_AXES = ("energy", "tension", "density", "motion", "brightness", "warmth")


def _digest_int(seed: int, label: str) -> int:
    payload = f"MUSICA-M1|{seed}|{label}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _pick(seed: int, label: str, values: Sequence[T]) -> T:
    if not values:
        raise ContractError(f"cannot select from empty sequence for {label}")
    return values[_digest_int(seed, label) % len(values)]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, round(float(value), 6)))


def _stable_token(seed: int, label: str, length: int = 12) -> str:
    payload = f"MUSICA-M1-TOKEN|{seed}|{label}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:length]


def _resolve_tempo(intent: dict[str, Any], profile: dict[str, Any]) -> float:
    preference = intent["tempo"]
    minimum = float(preference["min_bpm"])
    maximum = float(preference["max_bpm"])
    if minimum > maximum:
        raise ContractError("tempo.min_bpm must be <= tempo.max_bpm")

    explicit = preference["bpm"]
    if explicit is not None:
        bpm = float(explicit)
        if not minimum <= bpm <= maximum:
            raise ContractError("explicit tempo must fall inside the requested tempo range")
        return bpm

    default = float(profile["default_bpm"])
    if minimum <= default <= maximum:
        return default
    return round((minimum + maximum) / 2.0, 3)


def _progression(key: str, mode: str) -> list[str]:
    root = NOTE_PC[key]
    if mode == "major":
        degrees = [(0, ""), (7, ""), (9, "m"), (5, "")]
    else:
        degrees = [(0, "m"), (8, ""), (3, ""), (10, "")]
    return [f"{PC_NAME[(root + offset) % 12]}{quality}" for offset, quality in degrees]


def _motif_notes(
    *, seed: int, key: str, mode: str, profile: dict[str, Any], energy: float
) -> tuple[list[dict[str, Any]], float]:
    scale = SCALES[mode]
    root_pc = NOTE_PC[key]
    root_midi = 60 + root_pc
    desired = int(profile["motif_register_base"])
    while root_midi + 6 < desired:
        root_midi += 12
    while root_midi - 6 > desired:
        root_midi -= 12

    rhythm = [float(value) for value in profile["motif_rhythm"]]
    degree_pattern = list(profile["motif_degree_pattern"])
    events: list[dict[str, Any]] = []
    offset = 0.0
    base_velocity = int(round(58 + 34 * energy))

    for index, duration in enumerate(rhythm):
        base_degree = int(degree_pattern[index % len(degree_pattern)])
        variation = int(_pick(seed, f"motif-variation-{index}", [-1, 0, 0, 0, 1]))
        degree = max(0, min(6, base_degree + variation))
        octave = int(_pick(seed, f"motif-octave-{index}", [0, 0, 0, 1 if index == len(rhythm) - 1 else 0]))
        pitch = root_midi + scale[degree] + 12 * octave
        velocity_delta = int(_pick(seed, f"motif-velocity-{index}", [-5, -2, 0, 2, 4]))
        events.append(
            {
                "offset_beats": round(offset, 6),
                "pitch": max(0, min(127, pitch)),
                "duration_beats": round(max(0.25, duration), 6),
                "velocity": max(1, min(127, base_velocity + velocity_delta)),
            }
        )
        offset += duration

    motif_length = 4.0 if offset <= 4.0 else float(int(offset + 0.999999))
    return events, motif_length


def _section_semantics(targets: dict[str, float], stage: int) -> dict[str, float]:
    factors = (
        {"energy": 0.72, "tension": 0.72, "density": 0.78, "motion": 0.72},
        {"energy": 0.94, "tension": 0.94, "density": 0.96, "motion": 0.96},
        {"energy": 1.08, "tension": 1.12, "density": 1.06, "motion": 1.10},
    )[stage]
    values = dict(targets)
    for key, factor in factors.items():
        values[key] = _bounded(targets[key] * factor)
    return values


def plan_intent(intent: dict[str, Any]) -> dict[str, Any]:
    """Create a deterministic explicit creative plan from Music Intent v0."""

    validate_contract(intent, "music-intent-v0.schema.json")
    profile = get_style_profile(intent["style_profile"])
    bpm = _resolve_tempo(intent, profile)
    key = intent["tonal"]["center"] or profile["default_key"]
    mode = intent["tonal"]["mode"] or profile["default_mode"]
    if key not in NOTE_PC or mode not in SCALES:
        raise ContractError(f"unsupported M1 tonal selection: {key} {mode}")

    duration = float(intent["duration_seconds"])
    boundaries = [0.0, round(duration * 0.30, 6), round(duration * 0.70, 6), duration]
    targets = {axis: float(intent["semantic_targets"][axis]) for axis in M1_SEMANTIC_AXES}
    seed = int(intent["seed"])
    motif, motif_length = _motif_notes(seed=seed, key=key, mode=mode, profile=profile, energy=targets["energy"])

    return {
        "plan_version": "0",
        "intent_id": intent["intent_id"],
        "style_profile": intent["style_profile"],
        "seed": seed,
        "tempo_bpm": bpm,
        "tempo_range": [float(intent["tempo"]["min_bpm"]), float(intent["tempo"]["max_bpm"])],
        "key": key,
        "mode": mode,
        "duration_seconds": duration,
        "sections": [
            {
                "section_id": f"S{index + 1:02d}",
                "label": profile["section_labels"][index],
                "start": boundaries[index],
                "end": boundaries[index + 1],
                "semantic_targets": _section_semantics(targets, index),
            }
            for index in range(3)
        ],
        "progression": _progression(key, mode),
        "motif_notes": motif,
        "motif_length_beats": motif_length,
        "drum_events": profile["drum_events"],
        "drum_pattern_length_beats": 4.0,
        "semantic_targets": targets,
        "profile": profile,
        "motif_token": f"motif-{_stable_token(seed, intent['intent_id'] + '|' + key + '|' + mode)}",
        "rhythm_token": f"rhythm-{_stable_token(seed, intent['intent_id'] + '|' + intent['style_profile'])}",
    }


def compose_blueprint(intent: dict[str, Any]) -> dict[str, Any]:
    """Compose a valid Music Blueprint v0 from a bounded Music Intent v0."""

    plan = plan_intent(intent)
    profile = plan["profile"]
    preserve = set(intent["preserve_on_edit"])
    locks: list[dict[str, Any]] = []

    if "tempo" in preserve:
        locks.append(
            {
                "lock_id": "L-TEMPO",
                "strength": "HARD",
                "target": "/musical_context/tempo/bpm",
                "mode": "exact",
                "inheriting": True,
                "value": plan["tempo_bpm"],
                "tolerance": 0,
                "reason": "Requested by Music Intent preserve_on_edit."
            }
        )
    if "melody_identity" in preserve:
        locks.append(
            {
                "lock_id": "L-MELODY-IDENTITY",
                "strength": "HARD",
                "target": "/materials/melody/main_motif_id",
                "mode": "identity",
                "inheriting": True,
                "value": plan["motif_token"],
                "identity_basis": {"v0_policy": "explicit_identity_token"},
                "reason": "Requested by Music Intent preserve_on_edit."
            }
        )
    if "rhythm_identity" in preserve:
        locks.append(
            {
                "lock_id": "L-DRUM-PATTERN",
                "strength": "HARD",
                "target": "/materials/rhythm/drum_pattern_id",
                "mode": "identity",
                "inheriting": True,
                "value": plan["rhythm_token"],
                "identity_basis": {"v0_policy": "explicit_identity_token"},
                "reason": "Requested by Music Intent preserve_on_edit."
            }
        )

    lock_ids = [lock["lock_id"] for lock in locks]
    blueprint = {
        "blueprint_version": "0",
        "project": {
            "project_id": f"MUSICA-{intent['intent_id']}",
            "title": intent["title"],
            "revision_id": "rev-001",
            "parent_revision_id": None,
            "duration_seconds": plan["duration_seconds"],
        },
        "intent": {
            "summary": intent["raw_prompt"] or intent["title"],
            "use_case": intent["use_case"],
            "references": [],
            "exclusions": list(intent["exclusions"]),
            "uncertainties": [],
        },
        "musical_context": {
            "tempo": {"bpm": plan["tempo_bpm"], "policy": "fixed"},
            "meter": "4/4",
            "tonal_center": plan["key"],
            "mode": plan["mode"],
            "mode_candidates": [],
            "confidence": float(intent["provenance"]["confidence"]),
        },
        "form": {
            "sections": [
                {
                    "section_id": section["section_id"],
                    "label": section["label"],
                    "start": section["start"],
                    "end": section["end"],
                    "purpose": f"M1 {section['label']} stage from {intent['style_profile']} profile",
                    "semantic_targets": section["semantic_targets"],
                    "locks": lock_ids,
                    "constraints": ["C-TEMPO-RANGE"],
                }
                for section in plan["sections"]
            ]
        },
        "roles": {
            "instruments_or_parts": [
                {
                    "part_id": "P-MOTIF",
                    "instrument_family": profile["motif_family"],
                    "role": "motif",
                    "register": "mid",
                    "presence": _bounded(0.55 + plan["semantic_targets"]["brightness"] * 0.25),
                    "importance": 0.90,
                    "mutable": True,
                },
                {
                    "part_id": "P-BASS",
                    "instrument_family": profile["bass_family"],
                    "role": profile["bass_role"],
                    "register": "low",
                    "presence": _bounded(0.55 + plan["semantic_targets"]["energy"] * 0.28),
                    "importance": 0.78,
                    "mutable": True,
                },
                {
                    "part_id": "P-DRUMS",
                    "instrument_family": profile["pulse_family"],
                    "role": "pulse",
                    "register": "full",
                    "presence": _bounded(0.35 + plan["semantic_targets"]["motion"] * 0.35),
                    "importance": 0.72,
                    "mutable": True,
                },
            ]
        },
        "semantics": {
            "global": plan["semantic_targets"],
            "curves": [
                {"time": section["start"], "values": section["semantic_targets"]}
                for section in plan["sections"]
            ] + [{"time": plan["duration_seconds"], "values": plan["sections"][-1]["semantic_targets"]}],
            "section_overrides": [],
        },
        "materials": {
            "harmony": {
                "progression": plan["progression"],
                "harmonic_rhythm": "one_chord_per_bar",
                "generation_profile": intent["style_profile"],
            },
            "melody": {
                "main_motif_id": plan["motif_token"],
                "motif_length_beats": plan["motif_length_beats"],
                "motif_notes": plan["motif_notes"],
                "generation_seed": plan["seed"],
            },
            "rhythm": {
                "drum_pattern_id": plan["rhythm_token"],
                "subdivision": "1/8",
                "syncopation": _bounded(0.18 + plan["semantic_targets"]["motion"] * 0.45),
                "pattern_length_beats": plan["drum_pattern_length_beats"],
                "drum_events": plan["drum_events"],
                "generation_profile": intent["style_profile"],
            },
            "texture": {
                "layer_count": max(2, int(profile["texture_base_layers"] + round(plan["semantic_targets"]["density"] * 2))),
                "density_bias": plan["semantic_targets"]["density"],
            },
            "sound_design": {
                "character": list(profile["character"]),
                "brightness": plan["semantic_targets"]["brightness"],
                "warmth": plan["semantic_targets"]["warmth"],
                "motif_program": int(profile["motif_program"]),
                "bass_program": int(profile["bass_program"]),
            },
            "mix_intent": {
                "width": _bounded(0.45 + plan["semantic_targets"]["brightness"] * 0.25),
                "energy": plan["semantic_targets"]["energy"],
                "warmth": plan["semantic_targets"]["warmth"],
                "loudness_policy": "preview-safe",
            },
        },
        "locks": locks,
        "constraints": [
            {
                "constraint_id": "C-TEMPO-RANGE",
                "target": "/musical_context/tempo/bpm",
                "op": "between",
                "value": plan["tempo_range"],
                "hardness": "hard",
                "reason": "Music Intent tempo envelope."
            }
        ],
        "render_intent": {
            "targets": [
                {
                    "target_id": "R-M1-LOCAL",
                    "backend": "deterministic-local-preview",
                    "deterministic_required": True,
                    "seed": plan["seed"],
                    "profile": intent["style_profile"],
                }
            ],
            "quality_preferences": ["deterministic", "local", "editable", "inspectable"],
        },
        "provenance": {
            "created_from_intent_id": intent["intent_id"],
            "actor": "deterministic_transform",
            "change_reason": "Compose root Blueprint from validated Music Intent v0.",
            "source_revision": None,
            "selected_mechanisms": [
                f"style_profile:{intent['style_profile']}",
                f"stable_seed:{plan['seed']}",
                "three_stage_form",
                "diatonic_profile_progression",
                "seeded_scale_motif",
            ],
            "rejected_mechanisms": [],
        },
    }

    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    return blueprint
