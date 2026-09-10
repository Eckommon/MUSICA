"""Free/local deterministic MIDI and WAV preview renderers for MUSICA M0-R2.

MUSICA M0-R2용 무료·로컬 결정론 MIDI/WAV 프리뷰 렌더러.
"""

from __future__ import annotations

import io
import math
import struct
import wave
from pathlib import Path
from typing import Any

from .contracts import ContractError, validate_contract

RENDERER_VERSION = "0.0.1"
DEFAULT_SAMPLE_RATE = 22050


def _vlq(value: int) -> bytes:
    if value < 0:
        raise ContractError("MIDI delta time cannot be negative")
    buffer = [value & 0x7F]
    value >>= 7
    while value:
        buffer.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(buffer))


def _chunk(chunk_type: bytes, payload: bytes) -> bytes:
    return chunk_type + struct.pack(">I", len(payload)) + payload


def _midi_track(events: list[tuple[int, int, bytes]]) -> bytes:
    payload = bytearray()
    previous_tick = 0
    for tick, _priority, message in sorted(events, key=lambda item: (item[0], item[1], item[2])):
        if tick < previous_tick:
            raise ContractError("MIDI events must be non-decreasing")
        payload.extend(_vlq(tick - previous_tick))
        payload.extend(message)
        previous_tick = tick
    payload.extend(b"\x00\xff\x2f\x00")
    return _chunk(b"MTrk", bytes(payload))


def midi_bytes(ir: dict[str, Any]) -> bytes:
    """Serialize validated Music IR to deterministic Standard MIDI File bytes."""

    validate_contract(ir, "music-ir-v0.schema.json")
    ppq = int(ir["timing"]["ppq"])
    tempo_events = ir["tempo_events"]
    if len(tempo_events) != 1 or int(tempo_events[0]["tick"]) != 0:
        raise ContractError("M0 MIDI renderer supports exactly one tempo event at tick 0")

    bpm = float(tempo_events[0]["bpm"])
    micros = int(round(60_000_000 / bpm))
    tempo_message = b"\xff\x51\x03" + micros.to_bytes(3, "big")
    chunks = [_midi_track([(0, 0, tempo_message)])]

    for track in ir["tracks"]:
        channel = int(track["channel"])
        program = int(track["program"])
        events: list[tuple[int, int, bytes]] = [(0, 0, bytes([0xC0 | channel, program]))]
        for event in track["events"]:
            tick = int(event["tick"])
            if event["type"] == "note":
                note = int(event["note"])
                velocity = int(event["velocity"])
                duration = int(event["duration"])
                events.append((tick, 2, bytes([0x90 | channel, note, velocity])))
                events.append((tick + duration, 1, bytes([0x80 | channel, note, 0])))
            elif event["type"] == "control":
                events.append(
                    (
                        tick,
                        1,
                        bytes([0xB0 | channel, int(event["controller"]), int(event["value"])]),
                    )
                )
        chunks.append(_midi_track(events))

    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), ppq)
    return header + b"".join(chunks)


def render_midi(ir: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(midi_bytes(ir))
    return target


def _note_frequency(note: int) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def _envelope(index: int, count: int, sample_rate: int) -> float:
    attack = max(1, min(int(0.008 * sample_rate), max(1, count // 4)))
    release = max(1, min(int(0.06 * sample_rate), max(1, count // 2)))
    attack_gain = min(1.0, (index + 1) / attack)
    release_gain = min(1.0, (count - index) / release)
    return min(attack_gain, release_gain)


def _voice_sample(channel: int, note: int, phase_time: float, progress: float) -> float:
    if channel == 9:
        if note == 36:  # kick-like deterministic sine drop
            freq = 54.0 + 36.0 * (1.0 - progress)
            return math.sin(2.0 * math.pi * freq * phase_time) * math.exp(-5.0 * progress)
        if note == 38:  # snare-like deterministic inharmonic partials
            return (
                0.55 * math.sin(2.0 * math.pi * 181.0 * phase_time)
                + 0.30 * math.sin(2.0 * math.pi * 337.0 * phase_time)
                + 0.15 * math.sin(2.0 * math.pi * 509.0 * phase_time)
            ) * math.exp(-7.0 * progress)
        return (
            0.62 * math.sin(2.0 * math.pi * 3521.0 * phase_time)
            + 0.38 * math.sin(2.0 * math.pi * 5213.0 * phase_time)
        ) * math.exp(-12.0 * progress)

    freq = _note_frequency(note)
    if channel == 1:  # bass preview
        return math.sin(2.0 * math.pi * freq * phase_time) + 0.22 * math.sin(
            2.0 * math.pi * freq * 2.0 * phase_time
        )
    return math.sin(2.0 * math.pi * freq * phase_time) + 0.18 * math.sin(
        2.0 * math.pi * freq * 2.0 * phase_time
    )


def wav_bytes(
    ir: dict[str, Any], duration_seconds: float, sample_rate: int = DEFAULT_SAMPLE_RATE
) -> bytes:
    """Render a deterministic, intentionally simple mono PCM preview WAV."""

    validate_contract(ir, "music-ir-v0.schema.json")
    if duration_seconds <= 0:
        raise ContractError("WAV duration must be positive")
    if sample_rate < 8000:
        raise ContractError("WAV sample rate is below the M0 minimum")

    bpm = float(ir["tempo_events"][0]["bpm"])
    ppq = int(ir["timing"]["ppq"])
    total_samples = int(round(duration_seconds * sample_rate))
    mix = [0.0] * total_samples

    for track in ir["tracks"]:
        channel = int(track["channel"])
        track_gain = 0.105 if channel == 9 else (0.11 if channel == 1 else 0.095)
        for event in track["events"]:
            if event["type"] != "note":
                continue
            start_seconds = (float(event["tick"]) / ppq) * (60.0 / bpm)
            note_seconds = (float(event["duration"]) / ppq) * (60.0 / bpm)
            start = max(0, int(round(start_seconds * sample_rate)))
            count = max(1, int(round(note_seconds * sample_rate)))
            velocity_gain = float(event["velocity"]) / 127.0
            note = int(event["note"])

            for local_index in range(count):
                index = start + local_index
                if index >= total_samples:
                    break
                phase_time = local_index / sample_rate
                progress = local_index / max(1, count - 1)
                value = _voice_sample(channel, note, phase_time, progress)
                value *= _envelope(local_index, count, sample_rate)
                value *= velocity_gain * track_gain
                mix[index] += value

    peak = max((abs(value) for value in mix), default=0.0)
    normalization = 0.90 / peak if peak > 0.90 else 1.0
    pcm = bytearray()
    for value in mix:
        clipped = max(-1.0, min(1.0, value * normalization))
        pcm.extend(struct.pack("<h", int(round(clipped * 32767.0))))

    stream = io.BytesIO()
    with wave.open(stream, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(pcm))
    return stream.getvalue()


def render_wav(
    ir: dict[str, Any], path: str | Path, duration_seconds: float, sample_rate: int = DEFAULT_SAMPLE_RATE
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(wav_bytes(ir, duration_seconds=duration_seconds, sample_rate=sample_rate))
    return target
