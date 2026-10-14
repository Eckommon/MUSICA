"""PLUG-R2-B K0 — independent frame-index oracle for real causal two-path alignment.

Test source is intentionally detached; accepted plugin host integration is NOT claimed.
"""
from __future__ import annotations

import copy
import hashlib
import io
import struct
import wave

import pytest

from musica.contracts import ContractError
from musica.evidence import canonical_json_bytes
from musica.plugin_alignment_reference import (
    build_two_path_alignment_plan,
    render_two_path_alignment,
    validate_two_path_alignment_plan,
)


def _wav(*, channel: str, position: int = 4, value: int = 8000,
         frames: int = 80, rate: int = 8000) -> bytes:
    pcm = bytearray()
    for i in range(frames):
        left = value if channel == "left" and i == position else 0
        right = value if channel == "right" and i == position else 0
        pcm += struct.pack("<hh", left, right)
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(pcm))
    return out.getvalue()


def _frames(data: bytes) -> list[tuple[int, int]]:
    with wave.open(io.BytesIO(data)) as w:
        assert w.getnchannels() == 2 and w.getsampwidth() == 2
        return list(struct.iter_unpack("<hh", w.readframes(w.getnframes())))


def _fixture(a_latency=3, b_latency=9, creative_a=0, bypass_a=False):
    inputs = {
        "PATH-A": _wav(channel="left", value=8000),
        "PATH-B": _wav(channel="right", value=-6000),
    }
    configs = [
        {"path_id": "PATH-A", "algorithmic_latency_frames": a_latency,
         "creative_delay_frames": creative_a, "bypass": bypass_a},
        {"path_id": "PATH-B", "algorithmic_latency_frames": b_latency,
         "creative_delay_frames": 0, "bypass": False},
    ]
    return inputs, configs


def _plan(inputs, configs):
    return build_two_path_alignment_plan(configs, sample_rate_hz=8000,
                                         input_wav_by_path=inputs)


def _indices(pcm, axis):
    return [i for i, x in enumerate(pcm) if x[axis] != 0]


def _rehash(p):
    base = dict(p)
    base.pop("plugin_two_path_alignment_plan_sha256")
    p["plugin_two_path_alignment_plan_sha256"] = hashlib.sha256(
        canonical_json_bytes(base)
    ).hexdigest()


def test_numeric_two_path_pdc_is_real_and_causal():
    inputs, configs = _fixture()
    plan = _plan(inputs, configs)
    assert plan["reference_algorithmic_latency_frames"] == 9
    assert [(p["path_id"], p["compensation_frames"])
            for p in plan["paths"]] == [("PATH-A", 6), ("PATH-B", 0)]
    assert plan["classification"] == "detached_derived_reference_only"

    uncomp = _frames(render_two_path_alignment(
        plan, input_wav_by_path=inputs, compensate=False
    ).wav_bytes)
    comp = _frames(render_two_path_alignment(
        plan, input_wav_by_path=inputs, compensate=True
    ).wav_bytes)
    # Two independent impulse channels show actual unsynchronised audio.
    assert _indices(uncomp, 0) == [7]
    assert _indices(uncomp, 1) == [13]
    # The faster path must be delayed 6 frames; not a metadata-only plan.
    assert _indices(comp, 0) == [13]
    assert _indices(comp, 1) == [13]
    assert comp[13] == (8000, -6000)
    assert comp[:13] == [(0, 0)] * 13
    assert render_two_path_alignment(plan, input_wav_by_path=inputs).wav_bytes == (
        render_two_path_alignment(plan, input_wav_by_path=inputs).wav_bytes
    )


def test_creative_delay_is_never_cancelled_by_pdc():
    inputs, configs = _fixture(creative_a=5)
    plan = _plan(inputs, configs)
    assert [p["compensation_frames"] for p in plan["paths"]] == [6, 0]
    result = _frames(render_two_path_alignment(plan, input_wav_by_path=inputs).wav_bytes)
    # Processing latency is aligned, but intentional +5 frame creative delay survives.
    assert _indices(result, 0) == [18]
    assert _indices(result, 1) == [13]


def test_bypass_recomputes_algorithmic_latency_without_stale_offset():
    inputs, configs = _fixture(bypass_a=True)
    plan = _plan(inputs, configs)
    assert plan["paths"][0]["effective_algorithmic_latency_frames"] == 0
    assert [p["compensation_frames"] for p in plan["paths"]] == [9, 0]
    result = _frames(render_two_path_alignment(plan, input_wav_by_path=inputs).wav_bytes)
    assert _indices(result, 0) == _indices(result, 1) == [13]


def test_removing_algorithmic_latency_rebuilds_plan():
    inputs, configs = _fixture()
    previous = _plan(inputs, configs)
    configs[0]["algorithmic_latency_frames"] = 0
    current = _plan(inputs, configs)
    assert previous["plugin_two_path_alignment_plan_sha256"] != (
        current["plugin_two_path_alignment_plan_sha256"]
    )
    assert current["paths"][0]["compensation_frames"] == 9
    assert _indices(_frames(render_two_path_alignment(
        current, input_wav_by_path=inputs
    ).wav_bytes), 0) == [13]


def test_plan_must_bind_exact_source_bytes_and_ids():
    inputs, configs = _fixture()
    plan = _plan(inputs, configs)
    forged = dict(inputs)
    forged["PATH-A"] = _wav(channel="left", value=7000)
    with pytest.raises(ContractError, match="stale or forged"):
        render_two_path_alignment(plan, input_wav_by_path=forged)
    with pytest.raises(ContractError, match="identities"):
        render_two_path_alignment(plan, input_wav_by_path={"PATH-A": inputs["PATH-A"]})
    with pytest.raises(ContractError, match="unique"):
        _plan(inputs, [configs[0], configs[0]])
    with pytest.raises(ContractError, match="exact unique"):
        _plan({**inputs, "EXTRA": inputs["PATH-A"]}, configs)


def test_schema_semantic_selfhash_and_rehashed_forgery_rejected():
    inputs, configs = _fixture()
    valid = _plan(inputs, configs)
    for mutation in ("hash", "offset", "reference", "creative", "duplicate_id", "unsorted"):
        plan = copy.deepcopy(valid)
        if mutation == "hash":
            plan["plugin_two_path_alignment_plan_sha256"] = "f" * 64
        elif mutation == "offset":
            plan["paths"][0]["compensation_frames"] += 1
            _rehash(plan)
        elif mutation == "reference":
            plan["reference_algorithmic_latency_frames"] += 1
            _rehash(plan)
        elif mutation == "creative":
            plan["paths"][0]["creative_delay_frames"] = -1
            _rehash(plan)
        elif mutation == "duplicate_id":
            plan["paths"][1]["path_id"] = "PATH-A"
            _rehash(plan)
        else:
            plan["paths"].reverse()
            _rehash(plan)
        with pytest.raises(ContractError):
            validate_two_path_alignment_plan(plan)


def test_rate_duration_values_and_unknown_path_fail_closed():
    inputs, configs = _fixture()
    for bad in (-1, 1.5, True, 4097):
        changed = copy.deepcopy(configs)
        changed[0]["algorithmic_latency_frames"] = bad
        with pytest.raises(ContractError):
            _plan(inputs, changed)
    changed = copy.deepcopy(configs)
    changed[1]["creative_delay_frames"] = -1
    with pytest.raises(ContractError):
        _plan(inputs, changed)
    altered = dict(inputs)
    altered["PATH-B"] = _wav(channel="right", rate=44100)
    with pytest.raises(ContractError, match="sample-rate mismatch"):
        _plan(altered, configs)
    altered["PATH-B"] = _wav(channel="right", frames=60)
    with pytest.raises(ContractError, match="identical duration"):
        _plan(altered, configs)
    with pytest.raises(ContractError, match="unknown forced-error path"):
        render_two_path_alignment(_plan(inputs, configs), input_wav_by_path=inputs,
                                  force_error_path_ids={"UNKNOWN"})


def test_forced_failure_is_atomic_and_bypass_skips_inactive_processor():
    inputs, configs = _fixture()
    plan = _plan(inputs, configs)
    inputs_before = {k: v for k, v in inputs.items()}
    plan_before = copy.deepcopy(plan)
    with pytest.raises(ContractError, match="forced processor error"):
        render_two_path_alignment(plan, input_wav_by_path=inputs,
                                  force_error_path_ids={"PATH-A"})
    assert plan == plan_before and inputs == inputs_before
    configs[0]["bypass"] = True
    bypass_plan = _plan(inputs, configs)
    result = render_two_path_alignment(
        bypass_plan, input_wav_by_path=inputs, force_error_path_ids={"PATH-A"}
    )
    assert result.wav_bytes
    assert result.report()["accepted_state_mutation_authorized"] is False
    assert result.report()["host_pdc_integrated"] is False
