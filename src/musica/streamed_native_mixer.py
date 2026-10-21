"""G3B2A — bounded, derived native offline WAV-to-file mixing.

A deliberately opt-in alternative to the legacy whole-song WAV-bytes renderer.
Consumes ONLY an exact, already accepted Project revision and its immutable CAS WAV
assets; never creates or Accepts a creative state. G3B2B will extend this engine to
routed/automated bus processing after deterministic native parity is proven.
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
from .native_mixer import _pcm16_sample, build_native_mix_plan

DEFAULT_BLOCK_FRAMES = 4096
MAX_BLOCK_FRAMES = 16384
MAX_DERIVED_WAV_BYTES = 256 * 1024 * 1024


@dataclass(frozen=True)
class StreamedNativeMix:
    plan: dict[str, Any]
    wav_path: Path
    wav_sha256: str
    wav_size_bytes: int
    peak_pre_clip: float
    clipped_sample_count: int
    blocks_written: int

    def report(self) -> dict[str, Any]:
        return {
            "mix_plan_sha256": self.plan["mix_plan_sha256"],
            "wav_sha256": self.wav_sha256,
            "wav_size_bytes": self.wav_size_bytes,
            "peak_pre_clip": self.peak_pre_clip,
            "clipped_sample_count": self.clipped_sample_count,
            "blocks_written": self.blocks_written,
            "rendered_audio_is_canonical": False,
            "streamed_output_not_accepted_project_asset": True,
        }


def _pcm_float(raw: bytes, index: int, width: int) -> float:
    """Match ATCM-R2's integer decode scale and 24-bit sign extension."""
    if width == 1:
        return float(raw[index] - 128) / 128.0
    if width == 2:
        return float(struct.unpack_from("<h", raw, index)[0]) / 32768.0
    if width == 3:
        sign = b"\xff" if raw[index + 2] & 0x80 else b"\x00"
        number = int.from_bytes(raw[index:index + 3] + sign, "little", signed=True)
        return float(number) / 8388608.0
    if width == 4:
        return float(struct.unpack_from("<i", raw, index)[0]) / 2147483648.0
    raise ContractError("streamed native mixer PCM sample width unsupported")


def render_native_mix_streamed(
    project: Any,
    revision_id: str,
    *,
    mix_sample_rate_hz: int,
    block_frames: int = DEFAULT_BLOCK_FRAMES,
    cancelled: Callable[[], bool] | None = None,
) -> StreamedNativeMix:
    """Stream an accepted native mix into a private, derived WAV file.

    Peak buffering is O(block_frames * channels), not O(song_seconds).
    Returned output is NONCANONICAL, and caller must delete it after use.
    A cancelled, stale, corrupt, or incomplete render deletes its output.
    """
    if type(block_frames) is not int or not 1 <= block_frames <= MAX_BLOCK_FRAMES:
        raise ContractError("G3B2A block_frames must be between 1 and 16384")
    if revision_id != project.head_revision_id():
        raise ContractError("G3B2A requires the current accepted Project HEAD")
    plan = build_native_mix_plan(project, revision_id,
                                 mix_sample_rate_hz=mix_sample_rate_hz)
    duration = int(plan["duration_frames"])
    size = 44 + duration * 4
    if size > MAX_DERIVED_WAV_BYTES:
        raise ContractError("G3B2A derived WAV exceeds explicit 256MiB output bound")

    derived_root = Path(project.root) / ".derived-streamed-native-g3b2"
    if derived_root.is_symlink():
        raise ContractError("G3B2A derived output directory cannot be a symlink")
    derived_root.mkdir(mode=0o700, parents=True, exist_ok=True)

    descriptor_by_asset: dict[str, tuple[Path, int, int, int, int, str]] = {}
    for track in plan["tracks"]:
        for clip in track["clips"]:
            asset_id = str(clip["asset_id"])
            if asset_id in descriptor_by_asset:
                continue
            path = project._object_path(str(clip["object_sha256"]))
            if not path.is_file() or path.is_symlink():
                raise ContractError(f"G3B2A missing or symlinked source: {asset_id}")
            descriptor_by_asset[asset_id] = (
                path, int(clip["channels"]), int(clip["sample_width_bytes"]),
                int(clip["sample_rate_hz"]), int(clip["source_end_frame"]),
                str(clip["object_sha256"]),
            )
    # Source hash is validated by build_native_mix_plan/read_audio_asset, and
    # checked AGAIN after render to catch changes during file processing.
    path: Path | None = None
    peak = 0.0
    clipping = 0
    blocks = 0
    try:
        with tempfile.NamedTemporaryFile(
            dir=derived_root, prefix="native-", suffix=".wav", delete=False
        ) as temporary:
            path = Path(temporary.name)
        with ExitStack() as stack:
            readers: dict[str, wave.Wave_read] = {}
            for asset_id, (source, ch, width, rate, _end, _digest) in descriptor_by_asset.items():
                reader = stack.enter_context(wave.open(str(source), "rb"))
                if (reader.getcomptype() != "NONE" or reader.getnchannels() != ch
                        or reader.getsampwidth() != width or reader.getframerate() != rate):
                    raise ContractError(f"G3B2A source WAV header changed: {asset_id}")
                readers[asset_id] = reader
            with path.open("wb") as handle:
                with wave.open(handle, "wb") as writer:
                    writer.setnchannels(2)
                    writer.setsampwidth(2)
                    writer.setframerate(mix_sample_rate_hz)
                    writer.setnframes(duration)
                    for start in range(0, duration, block_frames):
                        if cancelled is not None and cancelled():
                            raise ContractError("G3B2A render cancelled")
                        if project.head_revision_id() != revision_id:
                            raise ContractError("G3B2A accepted HEAD changed during render")
                        count = min(block_frames, duration - start)
                        left, right = [0.0] * count, [0.0] * count
                        for track in plan["tracks"]:
                            mixer = track["mixer"]
                            if not mixer["audible"]:
                                continue
                            track_gain = float(mixer["gain_linear"])
                            lcoeff = float(mixer["left_coefficient"])
                            rcoeff = float(mixer["right_coefficient"])
                            for clip in track["clips"]:
                                clip_start = int(clip["timeline_start_frame"])
                                clip_end = clip_start + (
                                    int(clip["source_end_frame"]) - int(clip["source_start_frame"])
                                )
                                overlap_start = max(start, clip_start)
                                overlap_end = min(start + count, clip_end)
                                if overlap_end <= overlap_start:
                                    continue
                                source_at = int(clip["source_start_frame"]) + overlap_start - clip_start
                                wanted = overlap_end - overlap_start
                                reader = readers[str(clip["asset_id"])]
                                reader.setpos(source_at)
                                payload = reader.readframes(wanted)
                                channels = int(clip["channels"])
                                width = int(clip["sample_width_bytes"])
                                frame_bytes = channels * width
                                if len(payload) != wanted * frame_bytes:
                                    raise ContractError("G3B2A source PCM truncated mid-render")
                                gain = track_gain * float(clip["gain_linear"])
                                local = overlap_start - start
                                for pos in range(wanted):
                                    offset = pos * frame_bytes
                                    a = _pcm_float(payload, offset, width)
                                    b = _pcm_float(payload, offset + width, width) if channels == 2 else a
                                    index = local + pos
                                    # Exactly the ATCM-R2 multiplication order.
                                    if channels == 1:
                                        mono = a * gain
                                        left[index] += mono * lcoeff
                                        right[index] += mono * rcoeff
                                    else:
                                        left[index] += a * gain * lcoeff
                                        right[index] += b * gain * rcoeff
                        pcm = bytearray()
                        for lval, rval in zip(left, right):
                            peak = max(peak, abs(lval), abs(rval))
                            clipping += int(lval < -1.0 or lval > 1.0)
                            clipping += int(rval < -1.0 or rval > 1.0)
                            pcm.extend(struct.pack("<hh", _pcm16_sample(lval),
                                                   _pcm16_sample(rval)))
                        writer.writeframesraw(pcm)
                        blocks += 1
                handle.flush()
                os.fsync(handle.fileno())
        if project.head_revision_id() != revision_id:
            raise ContractError("G3B2A accepted HEAD changed after render")
        for source, _ch, _width, _rate, _end, expected_sha in descriptor_by_asset.values():
            if _file_sha256(source) != expected_sha:
                raise ContractError("G3B2A source CAS mutated during render")
        if path.stat().st_size != size:
            raise ContractError("G3B2A output WAV length mismatch")
        return StreamedNativeMix(
            plan, path, _file_sha256(path), size, peak, clipping, blocks
        )
    except BaseException:
        if path is not None:
            path.unlink(missing_ok=True)
        raise
