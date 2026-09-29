"""Generate deterministic RTIO-R0 realtime simulated-backend evidence."""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import tempfile
import wave
from pathlib import Path
from typing import Any, Callable

from .automation_edit import accept_automation_edit_preview, automation_material_sha256, blueprint_sha256, build_automation_edit_preview
from .audio_assets import import_audio_asset
from .audio_edit import accept_audio_edit_preview, audio_material_sha256, build_audio_edit_preview
from .contracts import ContractError
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .mram_r1_evidence import _audio_candidate, _routing_candidate, _routing_ops, _wav_bytes
from .project import MusicaProject, create_project
from .realtime_engine import (
    build_realtime_execution_plan,
    run_realtime_simulation,
    simulated_backend_capability,
)
from .routed_mixer import render_routed_mix
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256
from .routing_edit import accept_routing_edit_preview, build_routing_edit_preview

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "realtime-backend-capability-v0.schema.json",
    ROOT / "schemas" / "realtime-execution-plan-v0.schema.json",
    ROOT / "schemas" / "realtime-run-report-v0.schema.json",
    ROOT / "src" / "musica" / "realtime_engine.py",
    ROOT / "src" / "musica" / "routed_mixer.py",
    ROOT / "src" / "musica" / "native_mixer_automation.py",
    ROOT / "src" / "musica" / "rtio_r0_evidence.py",
    ROOT / "tests" / "test_rtio_r0_realtime_simulated_backend.py",
    ROOT / ".github" / "workflows" / "rtio-r0-realtime-simulated-backend-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _blocked(fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        fn()
    except ContractError as exc:
        return {"blocked": True, "error": str(exc)}
    return {"blocked": False, "error": None}


def _automation_source(parent: dict[str, Any]) -> dict[str, Any]:
    routing = routing_material_from_blueprint(parent)
    assert routing is not None
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "automation_material_sha256": automation_material_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(routing),
    }


def _native_candidate(parent: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": "RTIO-R0-NATIVE",
        "authority_target": "blueprint_automation_material",
        "source": _automation_source(parent),
        "actor": {"kind": "user", "actor_id": "rtio-r0-evidence"},
        "reason": "RTIO-R0 native automation fixture.",
        "operations": [
            {
                "operation_id": "RT-N1",
                "op": "ADD_LANE",
                "lane": {
                    "lane_id": "AUTO-AT001-GAIN",
                    "target": {
                        "parameter_id": "mixer.gain_db",
                        "scope": "audio_track",
                        "owner_id": "AT-001",
                        "unit": "decibel",
                        "minimum": -60.0,
                        "maximum": 12.0,
                    },
                    "section_id": None,
                    "points": [
                        {"point_id": "RT-P1", "beat": 0.0, "value": -3.0, "interpolation": "linear"},
                        {"point_id": "RT-P2", "beat": 1.0, "value": -6.0, "interpolation": "hold"},
                    ],
                },
            }
        ],
        "preview_only": True,
    }


def _routed_payload(wav_bytes: bytes) -> bytes:
    with wave.open(io.BytesIO(wav_bytes), "rb") as reader:
        return reader.readframes(reader.getnframes())


def generate_rtio_r0_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-rtio-r0-") as temp_value:
        temp = Path(temp_value)
        root = compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))
        project = create_project(temp / "source.musica", root)

        wav_a = temp / "a.wav"
        wav_b = temp / "b.wav"
        wav_a.write_bytes(_wav_bytes(16384))
        wav_b.write_bytes(_wav_bytes(8192))
        asset_a = import_audio_asset(project, wav_a)
        asset_b = import_audio_asset(project, wav_b)

        audio_preview = build_audio_edit_preview(
            project,
            root,
            _audio_candidate(
                root,
                "RTIO-R0-AUDIO",
                [
                    {"operation_id": "A-T1", "op": "ADD_TRACK", "track_id": "AT-001", "order": 0, "name": "Primary"},
                    {"operation_id": "A-T2", "op": "ADD_TRACK", "track_id": "AT-002", "order": 1, "name": "Secondary"},
                    {
                        "operation_id": "A-C1",
                        "op": "ADD_CLIP",
                        "target": {"track_id": "AT-001"},
                        "clip": {
                            "clip_id": "AC-001",
                            "asset_id": asset_a["asset_id"],
                            "timeline_start_seconds": 0.0,
                            "source_in_seconds": 0.0,
                            "source_out_seconds": 0.1,
                            "gain_db": 0.0,
                        },
                    },
                    {
                        "operation_id": "A-C2",
                        "op": "ADD_CLIP",
                        "target": {"track_id": "AT-002"},
                        "clip": {
                            "clip_id": "AC-002",
                            "asset_id": asset_b["asset_id"],
                            "timeline_start_seconds": 0.0,
                            "source_in_seconds": 0.0,
                            "source_out_seconds": 0.1,
                            "gain_db": 0.0,
                        },
                    },
                ],
            ),
        )
        if not audio_preview.ready:
            raise RuntimeError("RTIO-R0 audio fixture Preview blocked")
        audio_record = accept_audio_edit_preview(project, audio_preview)
        audio = project.read_revision(audio_record["revision_id"])

        routing_preview = build_routing_edit_preview(
            project,
            audio,
            _routing_candidate(audio, "RTIO-R0-ROUTING", _routing_ops()),
        )
        if not routing_preview.ready:
            raise RuntimeError("RTIO-R0 routing fixture Preview blocked")
        routing_record = accept_routing_edit_preview(project, routing_preview)
        routed = project.read_revision(routing_record["revision_id"])

        native_preview = build_automation_edit_preview(
            routed,
            _native_candidate(routed),
            project=project,
        )
        if not native_preview.ready:
            raise RuntimeError("RTIO-R0 native automation fixture Preview blocked")
        native_record = accept_automation_edit_preview(project, native_preview)
        revision_id = str(native_record["revision_id"])

        head_before = project.head_revision_id("main")
        capability = simulated_backend_capability()
        plan_a = build_realtime_execution_plan(
            project, revision_id, sample_rate_hz=8000, block_size_frames=256
        )
        plan_b = build_realtime_execution_plan(
            project, revision_id, sample_rate_hz=8000, block_size_frames=256
        )
        run_a = run_realtime_simulation(
            project, revision_id, sample_rate_hz=8000, block_size_frames=256
        )
        run_b = run_realtime_simulation(
            project, revision_id, sample_rate_hz=8000, block_size_frames=256
        )
        xrun_a = run_realtime_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=256,
            force_xrun_block_indices=[1],
        )
        xrun_b = run_realtime_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=256,
            force_xrun_block_indices=[1],
        )

        routed_render = render_routed_mix(project, revision_id, mix_sample_rate_hz=8000)
        source_payload = _routed_payload(routed_render.wav_bytes)

        invalid = {
            "unsupported_sample_rate": _blocked(
                lambda: build_realtime_execution_plan(
                    project, revision_id, sample_rate_hz=16000, block_size_frames=256
                )
            ),
            "source_rate_mismatch": _blocked(
                lambda: build_realtime_execution_plan(
                    project, revision_id, sample_rate_hz=44100, block_size_frames=256
                )
            ),
            "unsupported_block_size": _blocked(
                lambda: build_realtime_execution_plan(
                    project, revision_id, sample_rate_hz=8000, block_size_frames=333
                )
            ),
            "forced_xrun_index_outside_trace": _blocked(
                lambda: run_realtime_simulation(
                    project,
                    revision_id,
                    sample_rate_hz=8000,
                    block_size_frames=256,
                    force_xrun_block_indices=[999999],
                )
            ),
        }

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_run = run_realtime_simulation(
            reopened, revision_id, sample_rate_hz=8000, block_size_frames=256
        )

        _write_json(out / "backend-capability.json", capability)
        _write_json(out / "realtime-plan.json", plan_a)
        _write_json(out / "block-trace.json", list(run_a.block_trace))
        _write_json(out / "run-report.json", run_a.report)
        (out / "sink.pcm").write_bytes(run_a.sink_payload)
        _write_json(out / "xrun-report.json", xrun_a.report)
        (out / "xrun-sink.pcm").write_bytes(xrun_a.sink_payload)
        _write_json(out / "invalid-config-results.json", invalid)

        proof = {
            "milestone": "RTIO-R0",
            "validation_class": "DETERMINISTIC_REALTIME_PLAN_AND_SIMULATED_BACKEND",
            "revision_id": revision_id,
            "plan_repeat_exact": plan_a == plan_b,
            "run_report_repeat_exact": run_a.report == run_b.report,
            "block_trace_repeat_exact": run_a.block_trace == run_b.block_trace,
            "sink_repeat_exact": run_a.sink_payload == run_b.sink_payload,
            "sink_matches_exact_routed_pcm_payload": run_a.sink_payload == source_payload,
            "accepted_head_unchanged": project.head_revision_id("main") == head_before,
            "normal_xrun_count_zero": run_a.report["metrics"]["xrun_count"] == 0,
            "forced_xrun_repeat_exact": xrun_a.report == xrun_b.report
            and xrun_a.sink_payload == xrun_b.sink_payload,
            "forced_xrun_count_one": xrun_a.report["metrics"]["xrun_count"] == 1,
            "forced_xrun_changes_sink": xrun_a.report["sink"]["payload_sha256"]
            != run_a.report["sink"]["payload_sha256"],
            "invalid_paths_all_blocked": all(item["blocked"] for item in invalid.values()),
            "reopen_plan_exact": reopened_run.plan == run_a.plan,
            "reopen_block_trace_exact": reopened_run.block_trace == run_a.block_trace,
            "reopen_sink_exact": reopened_run.sink_payload == run_a.sink_payload,
            "reopen_report_exact": reopened_run.report == run_a.report,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
            "runtime_state_is_canonical": False,
            "real_host_device_claimed": False,
            "recording_claimed": False,
            "resampling_claimed": False,
        }
        _write_json(out / "proof.json", proof)

    contract_hashes = []
    for path in CONTRACT_PATHS:
        data = path.read_bytes()
        contract_hashes.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": _sha(data),
                "size_bytes": len(data),
            }
        )
    _write_json(out / "contract-hashes.json", contract_hashes)

    records = []
    for path in sorted(
        p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json"
    ):
        data = path.read_bytes()
        records.append(
            {
                "path": path.relative_to(out).as_posix(),
                "sha256": _sha(data),
                "size_bytes": len(data),
            }
        )
    manifest = {
        "manifest_version": "0",
        "milestone": "RTIO-R0",
        "artifact_name": "musica-rtio-r0-realtime-simulated-backend-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_RTIO_R0_EVIDENCE_OUT",
        "artifacts/rtio-r0-realtime-simulated-backend-evidence",
    )
    generate_rtio_r0_evidence(destination)
