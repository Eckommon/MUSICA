"""G3B2B: fixed-window derived routed PCM mix, never a creative Accept.

All topology and automation come from one exact accepted revision lowered
through MRAM-R1/R2 contracts. Existing legacy render_routed_mix is deliberately
untouched: it supplies the byte-exact short-song reference oracle.
"""
from __future__ import annotations

import hashlib
import os
import struct
import tempfile
import wave
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .audio_assets import _file_sha256
from .contracts import ContractError
from .native_mixer import _gain_linear, _pan_coefficients, _pcm16_sample
from .native_mixer_automation import automation_lane_map, value_at_frame
from .routed_mixer import build_routed_mix_plan
from .streamed_native_mixer import (
    DEFAULT_BLOCK_FRAMES, MAX_BLOCK_FRAMES, MAX_DERIVED_WAV_BYTES, _pcm_float,
)


def _empty(count: int) -> tuple[list[float], list[float]]:
    return [0.0] * count, [0.0] * count


def _add(
    dst: tuple[list[float], list[float]],
    src: tuple[list[float], list[float]],
    gain: float = 1.0,
) -> None:
    dl, dr = dst
    sl, sr = src
    # Preserve legacy _add_scaled operation order: additions track-order
    # then send-order, with each sample performing multiply and add once.
    scale = float(gain)
    for index in range(len(dl)):
        dl[index] += sl[index] * scale
        dr[index] += sr[index] * scale


def _track_window(
    track: dict[str, Any],
    readers: dict[str, wave.Wave_read],
    start: int,
    count: int,
    automation: dict[tuple[str, str, str], dict[str, Any]],
) -> tuple[list[float], list[float]]:
    left, right = _empty(count)
    mix = track["mixer"]
    if not mix["audible"]:
        return left, right
    track_id = str(track["track_id"])
    gain_lane = automation.get(("audio_track", track_id, "mixer.gain_db"))
    pan_lane = automation.get(("audio_track", track_id, "mixer.pan"))
    track_gain = float(mix["gain_linear"])
    base_left = float(mix["left_coefficient"])
    base_right = float(mix["right_coefficient"])
    for clip in track["clips"]:
        clip_start = int(clip["timeline_start_frame"])
        source_in = int(clip["source_start_frame"])
        clip_end = clip_start + int(clip["source_end_frame"]) - source_in
        overlap_start, overlap_end = max(start, clip_start), min(start + count, clip_end)
        if overlap_end <= overlap_start:
            continue
        source_at = source_in + overlap_start - clip_start
        wanted = overlap_end - overlap_start
        reader = readers[str(clip["asset_id"])]
        reader.setpos(source_at)
        data = reader.readframes(wanted)
        channels = int(clip["channels"])
        width = int(clip["sample_width_bytes"])
        stride = channels * width
        if len(data) != wanted * stride:
            raise ContractError("G3B2B source PCM truncated mid-render")
        clip_gain = float(clip["gain_linear"])
        combined_gain = track_gain * clip_gain
        for offset in range(wanted):
            absolute_frame = overlap_start + offset
            sample_offset = offset * stride
            a = _pcm_float(data, sample_offset, width)
            b = _pcm_float(data, sample_offset + width, width) if channels == 2 else a
            if gain_lane is None and pan_lane is None:
                gain, lc, rc = combined_gain, base_left, base_right
            else:
                db = (value_at_frame(gain_lane, absolute_frame) if gain_lane is not None
                      else float(mix["gain_db"]))
                pan = (value_at_frame(pan_lane, absolute_frame) if pan_lane is not None
                       else float(mix["pan"]))
                gain = _gain_linear(db) * clip_gain
                lc, rc = _pan_coefficients(pan)
            index = absolute_frame - start
            if channels == 1:
                mono = a * gain
                left[index] += mono * lc
                right[index] += mono * rc
            else:
                left[index] += a * gain * lc
                right[index] += b * gain * rc
    return left, right


def _node_window(
    input_buffer: tuple[list[float], list[float]],
    mixer: dict[str, Any],
    *,
    node_id: str,
    start: int,
    automation: dict[tuple[str, str, str], dict[str, Any]],
) -> tuple[list[float], list[float]]:
    left = list(input_buffer[0])
    right = list(input_buffer[1])
    if bool(mixer["mute"]):
        return _empty(len(left))
    gain_lane = automation.get(("routing_node", node_id, "mixer.gain_db"))
    pan_lane = automation.get(("routing_node", node_id, "mixer.pan"))
    if gain_lane is None and pan_lane is None:
        gain = _gain_linear(float(mixer["gain_db"]))
        lc, rc = _pan_coefficients(float(mixer["pan"]))
        for index in range(len(left)):
            left[index] *= gain * lc
            right[index] *= gain * rc
        return left, right
    for index in range(len(left)):
        frame = start + index
        db = (value_at_frame(gain_lane, frame) if gain_lane is not None
              else float(mixer["gain_db"]))
        pan = (value_at_frame(pan_lane, frame) if pan_lane is not None
               else float(mixer["pan"]))
        gain = _gain_linear(db)
        lc, rc = _pan_coefficients(pan)
        left[index] *= gain * lc
        right[index] *= gain * rc
    return left, right


@dataclass(frozen=True)
class StreamedRoutedMix:
    plan: dict[str, Any]
    wav_path: Path
    wav_sha256: str
    wav_size_bytes: int
    peak_pre_clip: float
    clipped_sample_count: int
    blocks_written: int

    def report(self) -> dict[str, Any]:
        return {
            "routed_mix_plan_sha256": self.plan["routed_mix_plan_sha256"],
            "wav_sha256": self.wav_sha256,
            "wav_size_bytes": self.wav_size_bytes,
            "peak_pre_clip": self.peak_pre_clip,
            "clipped_sample_count": self.clipped_sample_count,
            "blocks_written": self.blocks_written,
            "rendered_audio_is_canonical": False,
        }


def render_routed_mix_streamed(
    project: Any,
    revision_id: str,
    *,
    mix_sample_rate_hz: int,
    block_frames: int = DEFAULT_BLOCK_FRAMES,
    cancelled: Callable[[], bool] | None = None,
) -> StreamedRoutedMix:
    """Render accepted routed buses and native automation to a private WAV.

    Memory scales with block_frames * (routing_nodes + active_tracks),
    not song seconds. The caller owns output file deletion.
    """
    if type(block_frames) is not int or not 1 <= block_frames <= MAX_BLOCK_FRAMES:
        raise ContractError("G3B2B block_frames must be between 1 and 16384")
    if project.head_revision_id() != revision_id:
        raise ContractError("G3B2B must render current accepted HEAD")
    plan = build_routed_mix_plan(
        project, revision_id, mix_sample_rate_hz=mix_sample_rate_hz
    )
    duration = int(plan["duration_frames"])
    size = 44 + 4 * duration
    if size > MAX_DERIVED_WAV_BYTES:
        raise ContractError("G3B2B derived stereo WAV exceeds 256MiB bound")
    routing = plan["routing"]
    track_outputs = {
        str(x["track_id"]): str(x["target_node_id"])
        for x in routing["track_outputs"]
    }
    track_sends: dict[str, list[dict[str, Any]]] = {}
    node_sends: dict[str, list[dict[str, Any]]] = {}
    for send in routing["sends"]:
        index = track_sends if send["source_kind"] == "track" else node_sends
        index.setdefault(str(send["source_id"]), []).append(send)
    automation = (
        automation_lane_map(plan["native_mixer_automation"])
        if "native_mixer_automation" in plan else {}
    )

    source_info: dict[str, tuple[Path, str, int, int, int]] = {}
    for track in plan["native_tracks"]:
        for clip in track["clips"]:
            aid = str(clip["asset_id"])
            if aid not in source_info:
                source_path = project._object_path(str(clip["object_sha256"]))
                if not source_path.is_file() or source_path.is_symlink():
                    raise ContractError(f"G3B2B source unavailable: {aid}")
                source_info[aid] = (
                    source_path, str(clip["object_sha256"]),
                    int(clip["channels"]), int(clip["sample_width_bytes"]),
                    int(clip["sample_rate_hz"]),
                )
    tmp_root = Path(project.root) / ".derived-streamed-routed-g3b2b"
    if tmp_root.is_symlink():
        raise ContractError("G3B2B derived output directory cannot be symlinked")
    tmp_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    output: Path | None = None
    peak, clipped, blocks = 0.0, 0, 0
    try:
        with tempfile.NamedTemporaryFile(
            dir=tmp_root, prefix="routed-", suffix=".wav", delete=False
        ) as tmp:
            output = Path(tmp.name)
        with ExitStack() as stack:
            readers: dict[str, wave.Wave_read] = {}
            for asset_id, (source_path, _digest, channels, width, rate) in source_info.items():
                rd = stack.enter_context(wave.open(str(source_path), "rb"))
                if (rd.getcomptype() != "NONE" or rd.getnchannels() != channels or
                        rd.getsampwidth() != width or rd.getframerate() != rate):
                    raise ContractError(f"G3B2B WAV format changed: {asset_id}")
                readers[asset_id] = rd
            with output.open("wb") as stream:
                with wave.open(stream, "wb") as wav_out:
                    wav_out.setnchannels(2)
                    wav_out.setsampwidth(2)
                    wav_out.setframerate(mix_sample_rate_hz)
                    wav_out.setnframes(duration)
                    for start in range(0, duration, block_frames):
                        if cancelled is not None and cancelled():
                            raise ContractError("G3B2B render cancelled")
                        if project.head_revision_id() != revision_id:
                            raise ContractError("G3B2B HEAD changed during render")
                        count = min(block_frames, duration - start)
                        node_inputs = {
                            str(n["node_id"]): _empty(count)
                            for n in routing["nodes"]
                        }
                        for track in plan["native_tracks"]:
                            tid = str(track["track_id"])
                            buf = _track_window(track, readers, start, count, automation)
                            _add(node_inputs[track_outputs[tid]], buf)
                            for send in track_sends.get(tid, []):
                                _add(node_inputs[str(send["target_node_id"])], buf,
                                     _gain_linear(float(send["gain_db"])))
                        master = None
                        for node in routing["nodes"]:
                            nid = str(node["node_id"])
                            processed = _node_window(
                                node_inputs[nid], node["mixer"],
                                node_id=nid, start=start, automation=automation,
                            )
                            for send in node_sends.get(nid, []):
                                _add(node_inputs[str(send["target_node_id"])], processed,
                                     _gain_linear(float(send["gain_db"])))
                            target = node.get("output_node_id")
                            if target is None:
                                if nid != str(routing["master_node_id"]):
                                    raise ContractError("G3B2B terminal non-master node")
                                master = processed
                            else:
                                _add(node_inputs[str(target)], processed)
                        if master is None:
                            raise ContractError("G3B2B master output not reached")
                        payload = bytearray()
                        for lval, rval in zip(*master):
                            peak = max(peak, abs(lval), abs(rval))
                            clipped += int(lval < -1.0 or lval > 1.0)
                            clipped += int(rval < -1.0 or rval > 1.0)
                            payload.extend(struct.pack("<hh",
                                _pcm16_sample(lval), _pcm16_sample(rval)))
                        wav_out.writeframesraw(payload)
                        blocks += 1
                stream.flush()
                os.fsync(stream.fileno())
        if project.head_revision_id() != revision_id:
            raise ContractError("G3B2B HEAD changed after render")
        for source_path, expected, _ch, _width, _rate in source_info.values():
            if _file_sha256(source_path) != expected:
                raise ContractError("G3B2B immutable CAS changed during render")
        if output.stat().st_size != size:
            raise ContractError("G3B2B derived WAV length mismatch")
        return StreamedRoutedMix(
            plan, output, _file_sha256(output), size, peak, clipped, blocks
        )
    except BaseException:
        if output is not None:
            output.unlink(missing_ok=True)
        raise
