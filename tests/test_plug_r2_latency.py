"""PLUG-R2 latency ledger: R1-anchored semantics and adversarial checks."""
from __future__ import annotations

import copy
import hashlib

import pytest

from musica.contracts import ContractError
from musica.evidence import canonical_json_bytes
from musica.plugin_reference import _delay_and_gain
from musica.plugin_latency import (
    _latency_projection_from_processing_plan,
    build_accepted_plugin_latency_plan,
    validate_accepted_plugin_latency_plan,
    validate_plugin_latency_plan,
)
import musica.plugin_latency as plugin_latency


def _hash(value: dict) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _r1_plan(delays: tuple[int, ...] = (), bypass: tuple[bool, ...] = ()) -> dict:
    if not bypass:
        bypass = (False,) * len(delays)
    assert len(delays) == len(bypass)
    instances = [
        {
            "instance_id": f"PI-{index:03}",
            "plugin_id": "PLUG-REF-001",
            "owner_node_id": "MASTER-001",
            "slot": index,
            "bypass": disabled,
            "processor_id": "musica-simulated-gain-delay-v0",
            "gain_db": 0.0,
            "gain_linear": 1.0,
            "delay_frames": frames,
            "effective_latency_frames": 0 if disabled else frames,
        }
        for index, (frames, disabled) in enumerate(zip(delays, bypass, strict=True))
    ]
    fields = [
        "blueprint_sha256",
        "audio_material_sha256",
        "routing_material_sha256",
        "automation_material_sha256",
        "routed_mix_plan_sha256",
        "routed_wav_sha256",
        "plugin_material_sha256",
    ]
    source = {"project_id": "P-001", "revision_id": "R-001"}
    source.update({field: str(index + 1) * 64 for index, field in enumerate(fields)})
    content = {
        "plan_version": "0",
        "engine_id": "musica-simulated-plugin-processor-v0",
        "classification": "derived_noncanonical",
        "source": source,
        "sample_rate_hz": 8000,
        "channels": 2,
        "sample_format": "float64_internal_pcm16_io",
        "policy": {
            "insertion_point": "post_routed_master_pcm16_reference_stage",
            "ordering": "slot_then_instance_id",
            "latency": "serial_sum_of_nonbypassed_fixed_delay_frames",
            "resampling": "forbidden",
            "channel_conversion": "forbidden_stereo_only",
            "output_clipping": "hard_clip_unit_range_before_pcm16",
        },
        "instances": instances,
        "total_effective_latency_frames": sum(
            i["effective_latency_frames"] for i in instances
        ),
    }
    content["plugin_processing_plan_sha256"] = _hash(content)
    return content


def _rehash_r2(document: dict) -> None:
    base = dict(document)
    base.pop("plugin_latency_plan_sha256", None)
    document["plugin_latency_plan_sha256"] = _hash(base)


@pytest.mark.parametrize(
    ("delays", "bypass", "expected"),
    [
        ((), (), 0),
        ((4,), (False,), 4),
        ((4, 9, 7), (False, False, False), 20),
        ((4, 9, 7), (False, True, False), 11),
        ((128,), (True,), 0),
        ((4096, 4096), (False, False), 8192),
    ],
)
def test_accepted_serial_delay_ledger_is_deterministic(delays, bypass, expected):
    original = _r1_plan(delays, bypass)
    a = _latency_projection_from_processing_plan(original)
    b = _latency_projection_from_processing_plan(original)
    assert canonical_json_bytes(a) == canonical_json_bytes(b)
    assert a["serial_effective_signal_delay_frames"] == expected
    assert a["compensation_applied_frames"] == 0
    assert a["policy"]["compensation"] == "NONE_SERIAL_ONLY"
    assert a["policy"]["algorithmic_latency"] == "UNMEASURED_NOT_INFERRED"
    assert a["source"]["plugin_processing_plan_sha256"] == original[
        "plugin_processing_plan_sha256"
    ]
    validate_plugin_latency_plan(a, processing_plan=original)


def test_rehashed_forgery_still_fails_exact_source_binding():
    accepted = _r1_plan((4, 9))
    plan = _latency_projection_from_processing_plan(accepted)
    forged = copy.deepcopy(plan)
    forged["source"]["plugin_material_sha256"] = "f" * 64
    _rehash_r2(forged)
    validate_plugin_latency_plan(forged)  # hash alone cannot establish authority
    with pytest.raises(ContractError, match="stale or forged"):
        validate_plugin_latency_plan(forged, processing_plan=accepted)


@pytest.mark.parametrize("field", [
    "plugin_latency_plan_sha256", "serial_effective_signal_delay_frames",
    "compensation_applied_frames", "sample_rate_hz",
])
def test_tampered_plan_rejected(field):
    plan = _latency_projection_from_processing_plan(_r1_plan((2, 5)))
    if field == "plugin_latency_plan_sha256":
        plan[field] = "f" * 64
    elif field == "sample_rate_hz":
        plan[field] = 48000
    else:
        plan[field] += 1
    with pytest.raises(ContractError):
        validate_plugin_latency_plan(plan)


def test_rehashed_semantic_forgery_rejected():
    accepted = _r1_plan((4, 9))
    for attack in ("wrong_total", "bypass_leftover", "duplicate_slot", "wrong_order"):
        altered = _latency_projection_from_processing_plan(accepted)
        if attack == "wrong_total":
            altered["serial_effective_signal_delay_frames"] += 1
        elif attack == "bypass_leftover":
            altered["instances"][0]["bypass"] = True
        elif attack == "duplicate_slot":
            altered["instances"][1]["slot"] = 0
        else:
            altered["instances"].reverse()
        _rehash_r2(altered)
        with pytest.raises(ContractError):
            validate_plugin_latency_plan(altered)


def test_r1_processing_plan_rejects_rehashed_duplicate_instance_and_bad_latency():
    for attack in ("duplicate_instance", "oversize_delay", "invalid_effective"):
        r1 = _r1_plan((4, 9))
        if attack == "duplicate_instance":
            r1["instances"][1]["instance_id"] = r1["instances"][0]["instance_id"]
        elif attack == "oversize_delay":
            r1["instances"][0]["delay_frames"] = 4097
            r1["instances"][0]["effective_latency_frames"] = 4097
            r1["total_effective_latency_frames"] += 4093
        else:
            r1["instances"][0]["effective_latency_frames"] = 3
            r1["total_effective_latency_frames"] -= 1
        base = dict(r1)
        base.pop("plugin_processing_plan_sha256")
        r1["plugin_processing_plan_sha256"] = _hash(base)
        with pytest.raises(ContractError):
            _latency_projection_from_processing_plan(r1)


def test_numerical_audible_delay_is_not_pdc():
    # Independently calculated displacement for R1 reference processor:
    # the first nonzero stereo impulse must arrive at sum(delay_frames).
    original = [(0.0, 0.0)] * 32
    original[1] = (0.5, -0.25)
    serial = _delay_and_gain(original, gain_linear=1.0, delay_frames=4)
    serial = _delay_and_gain(serial, gain_linear=1.0, delay_frames=9)
    assert [i for i, frame in enumerate(serial) if frame != (0.0, 0.0)] == [14]
    assert serial[14] == (0.5, -0.25)
    assert serial[1] == (0.0, 0.0)
    # Bypass removes an actual signal delay; it never compensates another path.
    bypass_second = _delay_and_gain(original, gain_linear=1.0, delay_frames=4)
    assert bypass_second[5] == (0.5, -0.25)
    assert original[1] == (0.5, -0.25)


def test_persisted_source_builder_is_the_only_public_accepted_entry(monkeypatch):
    accepted = _r1_plan((2, 3))
    calls = []
    def source_bound_builder(project, revision_id, *, sample_rate_hz, routed_render=None):
        calls.append((project, revision_id, sample_rate_hz, routed_render))
        return copy.deepcopy(accepted)
    monkeypatch.setattr(
        plugin_latency, "build_accepted_plugin_processing_plan", source_bound_builder
    )
    project = object()
    generated = build_accepted_plugin_latency_plan(project, "R-001", sample_rate_hz=8000)
    validate_accepted_plugin_latency_plan(
        project, "R-001", generated, sample_rate_hz=8000
    )
    assert len(calls) == 2 and all(row[:3] == (project, "R-001", 8000) for row in calls)
    forged = copy.deepcopy(generated)
    forged["source"]["revision_id"] = "R-999"
    _rehash_r2(forged)
    with pytest.raises(ContractError, match="does not match accepted revision"):
        validate_accepted_plugin_latency_plan(
            project, "R-001", forged, sample_rate_hz=8000
        )
