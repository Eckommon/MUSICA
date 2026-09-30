"""Generate deterministic REC-R2 input-monitoring and instrumentation evidence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .audio_assets import import_audio_asset
from .audio_edit import accept_audio_edit_preview, build_audio_edit_preview
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .mram_r1_evidence import _audio_candidate, _routing_candidate, _routing_ops, _wav_bytes
from .project import MusicaProject, create_project
from .recording_finalize import (
    accept_recording_finalize_preview,
    build_recording_finalize_preview,
)
from .recording_monitor import run_recording_monitor_simulation
from .routing_edit import accept_routing_edit_preview, build_routing_edit_preview
from .rec_r1_evidence import _candidate as recording_candidate

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "recording-monitor-plan-v0.schema.json",
    ROOT / "schemas" / "recording-monitor-run-report-v0.schema.json",
    ROOT / "src" / "musica" / "recording_capture.py",
    ROOT / "src" / "musica" / "recording_finalize.py",
    ROOT / "src" / "musica" / "recording_monitor.py",
    ROOT / "src" / "musica" / "realtime_engine.py",
    ROOT / "src" / "musica" / "rec_r2_evidence.py",
    ROOT / "tests" / "test_rec_r2_monitoring.py",
    ROOT / ".github" / "workflows" / "rec-r2-monitoring-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def generate_rec_r2_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-rec-r2-") as temp_value:
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
                "REC-R2-AUDIO",
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
            raise RuntimeError("REC-R2 audio fixture Preview blocked")
        audio_record = accept_audio_edit_preview(project, audio_preview)
        accepted_audio = project.read_revision(audio_record["revision_id"])

        routing_preview = build_routing_edit_preview(
            project,
            accepted_audio,
            _routing_candidate(accepted_audio, "REC-R2-ROUTING", _routing_ops()),
        )
        if not routing_preview.ready:
            raise RuntimeError("REC-R2 routing fixture Preview blocked")
        routing_record = accept_routing_edit_preview(project, routing_preview)
        accepted = project.read_revision(routing_record["revision_id"])
        revision_id = str(accepted["project"]["revision_id"])
        head_before = project.head_revision_id("main")

        common = dict(
            sample_rate_hz=8000,
            input_channels=2,
            block_size_frames=256,
            capture_frames=800,
        )
        off = run_recording_monitor_simulation(
            project, revision_id, monitor_enabled=False, **common
        )
        on_a = run_recording_monitor_simulation(
            project, revision_id, monitor_enabled=True, **common
        )
        on_b = run_recording_monitor_simulation(
            project, revision_id, monitor_enabled=True, **common
        )
        output_xrun = run_recording_monitor_simulation(
            project,
            revision_id,
            monitor_enabled=True,
            force_monitor_xrun_block_indices=[1],
            **common,
        )
        failure = run_recording_monitor_simulation(
            project,
            revision_id,
            monitor_enabled=True,
            force_error_block_indices=[0],
            force_short_fill_block_indices=[1],
            force_late_block_indices=[2],
            **common,
        )

        finalize_candidate = recording_candidate(
            accepted,
            on_a.capture_run,
            candidate_id="REC-R2-MONITORED-FINALIZE",
            clip_id="REC-R2-CLIP",
        )
        finalize_preview = build_recording_finalize_preview(
            project,
            accepted,
            finalize_candidate,
            on_a.capture_run,
        )
        if not finalize_preview.ready:
            raise RuntimeError("REC-R2 clean monitored capture finalize Preview blocked")
        finalized_record = accept_recording_finalize_preview(
            project,
            finalize_preview,
            on_a.capture_run,
        )
        finalized_revision_id = str(finalized_record["revision_id"])

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_run = run_recording_monitor_simulation(
            reopened,
            revision_id,
            monitor_enabled=True,
            **common,
        )

        _write_json(out / "monitor-off-plan.json", off.monitoring_plan)
        _write_json(out / "monitor-off-report.json", off.report)
        (out / "monitor-off-capture.pcm").write_bytes(off.capture_run.captured_payload)
        _write_json(out / "monitor-on-plan.json", on_a.monitoring_plan)
        _write_json(out / "monitor-on-report.json", on_a.report)
        (out / "monitor-on-capture.pcm").write_bytes(on_a.capture_run.captured_payload)
        (out / "monitor-on-sink.pcm").write_bytes(on_a.monitor_sink_payload)
        _write_json(out / "monitor-xrun-report.json", output_xrun.report)
        (out / "monitor-xrun-sink.pcm").write_bytes(output_xrun.monitor_sink_payload)
        _write_json(out / "capture-failure-report.json", failure.report)
        _write_json(out / "recording-finalize-preview.json", finalize_preview.as_dict())

        proof = {
            "milestone": "REC-R2",
            "validation_class": "BOUNDED_INPUT_MONITORING_AND_CAPTURE_DROPOUT_INSTRUMENTATION",
            "source_revision_id": revision_id,
            "monitor_off_on_capture_plan_exact": off.capture_run.plan == on_a.capture_run.plan,
            "monitor_off_on_capture_trace_exact": off.capture_run.block_trace == on_a.capture_run.block_trace,
            "monitor_off_on_capture_payload_exact": off.capture_run.captured_payload == on_a.capture_run.captured_payload,
            "monitor_off_on_capture_report_exact": off.capture_run.report == on_a.capture_run.report,
            "monitor_off_has_no_sink_payload": off.monitor_sink_payload == b"",
            "monitor_on_sink_equals_clean_capture_payload": on_a.monitor_sink_payload == on_a.capture_run.captured_payload,
            "monitor_on_repeat_plan_exact": on_a.monitoring_plan == on_b.monitoring_plan,
            "monitor_on_repeat_trace_exact": on_a.monitor_trace == on_b.monitor_trace,
            "monitor_on_repeat_sink_exact": on_a.monitor_sink_payload == on_b.monitor_sink_payload,
            "monitor_on_repeat_report_exact": on_a.report == on_b.report,
            "monitor_xrun_capture_payload_unchanged": output_xrun.capture_run.captured_payload == on_a.capture_run.captured_payload,
            "monitor_xrun_capture_report_unchanged": output_xrun.capture_run.report == on_a.capture_run.report,
            "monitor_xrun_changes_sink": output_xrun.monitor_sink_payload != on_a.monitor_sink_payload,
            "monitor_xrun_count_exact": output_xrun.report["monitor"]["output_xrun_count"] == 1,
            "capture_failure_counts_exact": (
                failure.capture_run.report["metrics"]["error_count"] == 1
                and failure.capture_run.report["metrics"]["short_fill_count"] == 1
                and failure.capture_run.report["metrics"]["late_count"] == 1
                and failure.capture_run.report["metrics"]["dropout_equivalent_count"] == 3
            ),
            "monitor_failure_correlation_exact": (
                failure.report["monitor"]["input_error_drop_count"] == 1
                and failure.report["monitor"]["input_short_fill_count"] == 1
                and failure.report["monitor"]["input_late_count"] == 1
            ),
            "clean_monitored_capture_reuses_rec_r1_finalize": finalize_preview.ready,
            "finalize_advanced_exactly_once": finalized_record["parent_revision_id"] == revision_id,
            "accepted_head_changed_only_by_explicit_finalize": (
                head_before == revision_id
                and project.head_revision_id("main") == finalized_revision_id
            ),
            "reopen_monitor_plan_exact": reopened_run.monitoring_plan == on_a.monitoring_plan,
            "reopen_capture_plan_exact": reopened_run.capture_run.plan == on_a.capture_run.plan,
            "reopen_capture_trace_exact": reopened_run.capture_run.block_trace == on_a.capture_run.block_trace,
            "reopen_capture_payload_exact": reopened_run.capture_run.captured_payload == on_a.capture_run.captured_payload,
            "reopen_monitor_trace_exact": reopened_run.monitor_trace == on_a.monitor_trace,
            "reopen_monitor_sink_exact": reopened_run.monitor_sink_payload == on_a.monitor_sink_payload,
            "reopen_report_exact": reopened_run.report == on_a.report,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
            "monitor_state_is_canonical": False,
            "monitor_output_is_canonical": False,
            "monitor_gain_claimed": False,
            "host_native_monitoring_claimed": False,
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
        "milestone": "REC-R2",
        "artifact_name": "musica-rec-r2-monitoring-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_REC_R2_EVIDENCE_OUT",
        "artifacts/rec-r2-monitoring-evidence",
    )
    generate_rec_r2_evidence(destination)
