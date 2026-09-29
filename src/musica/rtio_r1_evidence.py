"""Generate deterministic RTIO-R1 callback-engine evidence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from .automation_edit import accept_automation_edit_preview, build_automation_edit_preview
from .audio_assets import import_audio_asset
from .audio_edit import accept_audio_edit_preview, build_audio_edit_preview
from .contracts import ContractError
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .mram_r1_evidence import _audio_candidate, _routing_candidate, _routing_ops, _wav_bytes
from .project import MusicaProject, create_project
from .realtime_callback import (
    CallbackEngine,
    DeterministicCallbackAdapter,
    callback_adapter_capability,
    run_callback_harness,
)
from .realtime_engine import run_realtime_simulation
from .routing_edit import accept_routing_edit_preview, build_routing_edit_preview
from .rtio_r0_evidence import _native_candidate

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "realtime-backend-capability-v0.schema.json",
    ROOT / "schemas" / "realtime-execution-plan-v0.schema.json",
    ROOT / "schemas" / "realtime-callback-adapter-capability-v0.schema.json",
    ROOT / "schemas" / "realtime-callback-transaction-v0.schema.json",
    ROOT / "schemas" / "realtime-callback-run-report-v0.schema.json",
    ROOT / "src" / "musica" / "realtime_engine.py",
    ROOT / "src" / "musica" / "realtime_callback.py",
    ROOT / "src" / "musica" / "rtio_r1_evidence.py",
    ROOT / "tests" / "test_rtio_r1_callback_engine.py",
    ROOT / ".github" / "workflows" / "rtio-r1-callback-engine-evidence.yml",
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


def _fixture(temp: Path) -> tuple[Any, str]:
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
            "RTIO-R1-AUDIO",
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
        raise RuntimeError("RTIO-R1 audio fixture Preview blocked")
    audio_record = accept_audio_edit_preview(project, audio_preview)
    audio = project.read_revision(audio_record["revision_id"])

    routing_preview = build_routing_edit_preview(
        project,
        audio,
        _routing_candidate(audio, "RTIO-R1-ROUTING", _routing_ops()),
    )
    if not routing_preview.ready:
        raise RuntimeError("RTIO-R1 routing fixture Preview blocked")
    routing_record = accept_routing_edit_preview(project, routing_preview)
    routed = project.read_revision(routing_record["revision_id"])

    native_preview = build_automation_edit_preview(
        routed,
        _native_candidate(routed),
        project=project,
    )
    if not native_preview.ready:
        raise RuntimeError("RTIO-R1 native automation fixture Preview blocked")
    native_record = accept_automation_edit_preview(project, native_preview)
    return project, str(native_record["revision_id"])


def generate_rtio_r1_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-rtio-r1-") as temp_value:
        temp = Path(temp_value)
        project, revision_id = _fixture(temp)
        head_before = project.head_revision_id("main")

        capability = callback_adapter_capability()
        normal_a = run_callback_harness(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=1024,
        )
        normal_b = run_callback_harness(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=1024,
        )
        r0 = run_realtime_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=1024,
        )

        failure_a = run_callback_harness(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=256,
            force_error_callback_indices=[1],
            force_short_fill_callback_indices=[2],
            force_late_callback_indices=[3],
        )
        failure_b = run_callback_harness(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=256,
            force_error_callback_indices=[1],
            force_short_fill_callback_indices=[2],
            force_late_callback_indices=[3],
        )
        early = run_callback_harness(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=256,
            stop_after_callbacks=3,
        )

        engine = CallbackEngine(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=1024,
        )
        adapter = DeterministicCallbackAdapter()
        invalid = {
            "request_before_running": _blocked(lambda: adapter.request()),
            "start_before_callback_registration": _blocked(lambda: adapter.start()),
            "invalid_failure_index": _blocked(
                lambda: run_callback_harness(
                    project,
                    revision_id,
                    sample_rate_hz=8000,
                    force_error_callback_indices=[999999],
                )
            ),
            "overlapping_error_short_fill": _blocked(
                lambda: run_callback_harness(
                    project,
                    revision_id,
                    sample_rate_hz=8000,
                    force_error_callback_indices=[1],
                    force_short_fill_callback_indices=[1],
                )
            ),
            "invalid_early_stop_count": _blocked(
                lambda: run_callback_harness(
                    project,
                    revision_id,
                    sample_rate_hz=8000,
                    stop_after_callbacks=0,
                )
            ),
        }
        adapter.open()
        adapter.register_callback(engine.callback)
        adapter.start()
        while engine.frame_cursor < int(engine.plan["duration_frames"]):
            adapter.request()
        invalid["callback_after_end_of_stream"] = _blocked(lambda: adapter.request())
        adapter.stop()
        adapter.close()
        invalid["double_close"] = _blocked(lambda: adapter.close())

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_run = run_callback_harness(
            reopened,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=1024,
        )

        _write_json(out / "adapter-capability.json", capability)
        _write_json(out / "realtime-plan.json", normal_a.plan)
        _write_json(out / "callback-trace.json", list(normal_a.transactions))
        _write_json(out / "callback-run-report.json", normal_a.report)
        (out / "callback-sink.pcm").write_bytes(normal_a.sink_payload)
        _write_json(out / "failure-callback-trace.json", list(failure_a.transactions))
        _write_json(out / "failure-callback-run-report.json", failure_a.report)
        (out / "failure-callback-sink.pcm").write_bytes(failure_a.sink_payload)
        _write_json(out / "early-stop-report.json", early.report)
        _write_json(out / "invalid-callback-results.json", invalid)

        final = normal_a.transactions[-1]
        proof = {
            "milestone": "RTIO-R1",
            "validation_class": "BOUNDED_CALLBACK_ENGINE_AND_HOST_BACKEND_ADAPTER_BOUNDARY",
            "revision_id": revision_id,
            "normal_plan_matches_rtio_r0": normal_a.plan == r0.plan,
            "normal_trace_repeat_exact": normal_a.transactions == normal_b.transactions,
            "normal_sink_repeat_exact": normal_a.sink_payload == normal_b.sink_payload,
            "normal_report_repeat_exact": normal_a.report == normal_b.report,
            "normal_sink_matches_rtio_r0": normal_a.sink_payload == r0.sink_payload,
            "final_callback_is_partial": final["request"]["requested_frame_count"] == 768,
            "final_callback_ends_exactly_at_duration": final["request"]["end_frame_exclusive"]
            == normal_a.plan["duration_frames"],
            "failure_trace_repeat_exact": failure_a.transactions == failure_b.transactions,
            "failure_sink_repeat_exact": failure_a.sink_payload == failure_b.sink_payload,
            "failure_report_repeat_exact": failure_a.report == failure_b.report,
            "forced_error_count_one": failure_a.report["metrics"]["error_count"] == 1,
            "forced_short_fill_count_one": failure_a.report["metrics"]["short_fill_count"] == 1,
            "forced_late_count_one": failure_a.report["metrics"]["late_count"] == 1,
            "failure_cursor_reaches_end": failure_a.report["metrics"]["final_frame_cursor"]
            == failure_a.plan["duration_frames"],
            "early_stop_exact_cursor": early.report["completion_status"] == "STOPPED_EARLY"
            and early.report["metrics"]["final_frame_cursor"] == 768,
            "invalid_paths_all_blocked": all(item["blocked"] for item in invalid.values()),
            "accepted_head_unchanged": project.head_revision_id("main") == head_before,
            "reopen_plan_exact": reopened_run.plan == normal_a.plan,
            "reopen_trace_exact": reopened_run.transactions == normal_a.transactions,
            "reopen_sink_exact": reopened_run.sink_payload == normal_a.sink_payload,
            "reopen_report_exact": reopened_run.report == normal_a.report,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
            "runtime_state_is_canonical": False,
            "host_native_device_claimed": False,
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
        "milestone": "RTIO-R1",
        "artifact_name": "musica-rtio-r1-callback-engine-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_RTIO_R1_EVIDENCE_OUT",
        "artifacts/rtio-r1-callback-engine-evidence",
    )
    generate_rtio_r1_evidence(destination)
