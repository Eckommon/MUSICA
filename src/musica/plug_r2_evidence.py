"""Generate exact PLUG-R2 accepted-source ledger and audible-delay proof.

This is strictly a serial-signal-delay accounting proof, NOT multi-path PDC.
"""
from __future__ import annotations

import copy
import hashlib
import io
import os
import shutil
import struct
import tempfile
import wave
from pathlib import Path
from typing import Any

from .contracts import ContractError
from .evidence import canonical_json_bytes
from .plug_r0_evidence import _fixture
from .plug_r1_evidence import _add_op, _candidate
from .plugin_edit import accept_plugin_edit_preview, build_plugin_edit_preview
from .plugin_latency import (
    build_accepted_plugin_latency_plan,
    validate_accepted_plugin_latency_plan,
    validate_plugin_latency_plan,
)
from .plugin_reference import render_accepted_plugins
from .project import MusicaProject
from .routed_mixer import render_routed_mix

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATHS = [
    ROOT / "docs" / "PLUG_R2_LATENCY_DECISION.md",
    ROOT / "schemas" / "plugin-latency-plan-v0.schema.json",
    ROOT / "src" / "musica" / "plugin_latency.py",
    ROOT / "src" / "musica" / "plugin_reference.py",
    ROOT / "src" / "musica" / "plug_r2_evidence.py",
    ROOT / "tests" / "test_plug_r2_latency.py",
    ROOT / ".github" / "workflows" / "plug-r2-latency-ledger-evidence.yml",
]


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_json(out: Path, name: str, payload: Any) -> None:
    (out / name).write_bytes(canonical_json_bytes(payload))


def _pcm(wav_bytes: bytes) -> tuple[int, list[tuple[int, int]]]:
    with wave.open(io.BytesIO(wav_bytes), "rb") as reader:
        rate = reader.getframerate()
        assert reader.getnchannels() == 2 and reader.getsampwidth() == 2
        frames = reader.readframes(reader.getnframes())
    assert len(frames) % 4 == 0
    return rate, list(struct.iter_unpack("<hh", frames))


def _accept(project: MusicaProject, parent: dict[str, Any],
            candidate_id: str, ops: list[dict[str, Any]]) -> dict[str, Any]:
    preview = build_plugin_edit_preview(
        project, parent, _candidate(parent, candidate_id, ops)
    )
    if not preview.ready:
        raise RuntimeError(f"PLUG-R2 Preview blocked unexpectedly: {candidate_id}")
    record = accept_plugin_edit_preview(project, preview)
    return project.read_revision(record["revision_id"])


def generate_plug_r2_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-plug-r2-") as td:
        temporary = Path(td)
        project, routed = _fixture(temporary)
        rate = 8000
        baseline_revision = routed["project"]["revision_id"]
        empty = build_accepted_plugin_latency_plan(
            project, baseline_revision, sample_rate_hz=rate
        )
        assert empty["serial_effective_signal_delay_frames"] == 0
        assert empty["instances"] == []

        accepted = _accept(
            project, routed, "PLUG-R2-ADD",
            [_add_op(gain_db=0.0, delay_frames=4)],
        )
        revision = accepted["project"]["revision_id"]
        ledger = build_accepted_plugin_latency_plan(
            project, revision, sample_rate_hz=rate
        )
        validated_again = build_accepted_plugin_latency_plan(
            project, revision, sample_rate_hz=rate
        )
        assert ledger == validated_again
        validate_accepted_plugin_latency_plan(
            project, revision, ledger, sample_rate_hz=rate
        )

        routed_audio = render_routed_mix(project, revision, mix_sample_rate_hz=rate)
        plugin_audio = render_accepted_plugins(
            project, revision, sample_rate_hz=rate
        )
        assert ledger["serial_effective_signal_delay_frames"] == 4
        assert plugin_audio.plan["total_effective_latency_frames"] == 4
        assert ledger["source"]["routed_wav_sha256"] == routed_audio.wav_sha256

        rate_a, dry = _pcm(routed_audio.wav_bytes)
        rate_b, wet = _pcm(plugin_audio.wav_bytes)
        assert rate_a == rate_b == rate
        assert len(dry) == len(wet) and len(dry) > 4
        assert any(pair != (0, 0) for pair in dry)
        assert wet[:4] == [(0, 0)] * 4
        # Independent PCM16 oracle: gain=0dB must preserve EVERY frame,
        # shifting precisely four frames; no hash-only/metadata-only proof.
        assert wet[4:] == dry[:-4]
        first_dry = next(i for i, pair in enumerate(dry) if pair != (0, 0))
        first_wet = next(i for i, pair in enumerate(wet) if pair != (0, 0))
        assert first_wet - first_dry == 4

        head_before_error = project.head_revision_id("main")
        error_fail_closed = False
        try:
            render_accepted_plugins(
                project, revision, sample_rate_hz=rate,
                force_error_instance_ids={"PI-001"},
            )
        except ContractError:
            error_fail_closed = True
        assert error_fail_closed
        assert project.head_revision_id("main") == head_before_error

        # A re-hashed forgery still fails persisted-source revalidation.
        forged = copy.deepcopy(ledger)
        forged["source"]["plugin_material_sha256"] = "f" * 64
        digest_base = dict(forged)
        digest_base.pop("plugin_latency_plan_sha256")
        forged["plugin_latency_plan_sha256"] = _sha(canonical_json_bytes(digest_base))
        validate_plugin_latency_plan(forged)
        stale_blocked = False
        try:
            validate_accepted_plugin_latency_plan(
                project, revision, forged, sample_rate_hz=rate
            )
        except ContractError:
            stale_blocked = True
        assert stale_blocked

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(
            archive, temporary / "reopened.musica"
        )
        reopened_ledger = build_accepted_plugin_latency_plan(
            reopened, revision, sample_rate_hz=rate
        )
        reopened_wav = render_accepted_plugins(
            reopened, revision, sample_rate_hz=rate
        )
        assert reopened_ledger == ledger
        assert reopened_wav.wav_bytes == plugin_audio.wav_bytes

        changed = _accept(
            project, accepted, "PLUG-R2-STATE",
            [{
                "operation_id": "PLUG-R2-STATE-01",
                "op": "SET_STATE",
                "instance_id": "PI-001",
                "state": {"gain_db": 0.0, "delay_frames": 9},
            }],
        )
        state_revision = changed["project"]["revision_id"]
        changed_ledger = build_accepted_plugin_latency_plan(
            project, state_revision, sample_rate_hz=rate
        )
        assert changed_ledger["serial_effective_signal_delay_frames"] == 9

        bypassed = _accept(
            project, changed, "PLUG-R2-BYPASS",
            [{
                "operation_id": "PLUG-R2-BYPASS-01",
                "op": "SET_BYPASS",
                "instance_id": "PI-001",
                "bypass": True,
            }],
        )
        bypass_revision = bypassed["project"]["revision_id"]
        bypass_ledger = build_accepted_plugin_latency_plan(
            project, bypass_revision, sample_rate_hz=rate
        )
        bypass_audio = render_accepted_plugins(
            project, bypass_revision, sample_rate_hz=rate
        )
        bypass_routed = render_routed_mix(
            project, bypass_revision, mix_sample_rate_hz=rate
        )
        assert bypass_ledger["serial_effective_signal_delay_frames"] == 0
        assert bypass_ledger["instances"][0]["declared_signal_delay_frames"] == 9
        assert bypass_audio.wav_bytes == bypass_routed.wav_bytes

        removed = _accept(
            project, bypassed, "PLUG-R2-REMOVE",
            [{
                "operation_id": "PLUG-R2-REMOVE-01",
                "op": "REMOVE_INSTANCE",
                "instance_id": "PI-001",
            }],
        )
        remove_revision = removed["project"]["revision_id"]
        removed_ledger = build_accepted_plugin_latency_plan(
            project, remove_revision, sample_rate_hz=rate
        )
        removed_audio = render_accepted_plugins(
            project, remove_revision, sample_rate_hz=rate
        )
        removed_routed = render_routed_mix(
            project, remove_revision, mix_sample_rate_hz=rate
        )
        assert removed_ledger["instances"] == []
        assert removed_ledger["serial_effective_signal_delay_frames"] == 0
        assert removed_audio.wav_bytes == removed_routed.wav_bytes

        for name, obj in [
            ("ledger-empty.json", empty),
            ("ledger-active.json", ledger),
            ("ledger-state.json", changed_ledger),
            ("ledger-bypass.json", bypass_ledger),
            ("ledger-removed.json", removed_ledger),
        ]:
            _write_json(out, name, obj)
        for name, wav in [
            ("routed-baseline.wav", routed_audio.wav_bytes),
            ("plugin-active.wav", plugin_audio.wav_bytes),
            ("plugin-bypass.wav", bypass_audio.wav_bytes),
            ("plugin-removed.wav", removed_audio.wav_bytes),
        ]:
            (out / name).write_bytes(wav)

        proof = {
            "evidence_version": "0",
            "classification": "PLUG_R2_SERIAL_LEDGER_ONLY_NOT_PDC",
            "accepted_revision_id": revision,
            "sample_rate_hz": rate,
            "frame_count": len(dry),
            "numerical_frame_shift": first_wet - first_dry,
            "full_pcm_frame_equality_after_four_frame_shift": True,
            "ledger_effective_signal_delay_frames": 4,
            "changed_effective_signal_delay_frames": 9,
            "bypass_effective_signal_delay_frames": 0,
            "removed_effective_signal_delay_frames": 0,
            "bypass_exact_routed_wav": True,
            "remove_exact_routed_wav": True,
            "forced_processor_error_head_unchanged": True,
            "forged_source_even_with_rehash_blocked": True,
            "reopen_ledger_and_processed_wav_exact": True,
            "algorithmic_latency_measured": False,
            "parallel_path_compensation_proven": False,
            "creative_authority_written_from_derived_plan": False,
        }
        _write_json(out, "proof.json", proof)

    artifacts = []
    for path in sorted(out.iterdir(), key=lambda p: p.name):
        if path.name == "manifest.json":
            continue
        contents = path.read_bytes()
        artifacts.append({
            "path": path.name, "bytes": len(contents), "sha256": _sha(contents)
        })
    contract_inventory = []
    for path in CONTRACT_PATHS:
        contents = path.read_bytes()
        contract_inventory.append({
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": len(contents), "sha256": _sha(contents),
        })
    manifest = {
        "manifest_version": "0",
        "classification": "PLUG_R2_LEDGER_ONLY_NO_PDC_CLAIM",
        "artifacts": artifacts,
        "contract_inventory": contract_inventory,
    }
    _write_json(out, "manifest.json", manifest)
    return manifest


def main() -> None:
    output = os.environ.get(
        "MUSICA_PLUG_R2_EVIDENCE_OUT", "artifacts/plug-r2-latency-ledger"
    )
    report = generate_plug_r2_evidence(output)
    print(f"PLUG-R2 serial ledger evidence: {len(report['artifacts'])} payloads")


if __name__ == "__main__":
    main()
