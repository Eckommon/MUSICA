"""Generate deterministic RTIO-R2 exact-frame transport evidence."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from .contracts import ContractError
from .evidence import canonical_json_bytes
from .project import MusicaProject
from .realtime_transport import ExactFrameTransport
from .rtio_r1_evidence import _fixture

ROOT = Path(__file__).resolve().parents[2]

CONTRACT_PATHS = [
    ROOT / "schemas" / "realtime-execution-plan-v0.schema.json",
    ROOT / "schemas" / "realtime-callback-adapter-capability-v0.schema.json",
    ROOT / "schemas" / "realtime-callback-transaction-v0.schema.json",
    ROOT / "schemas" / "realtime-callback-run-report-v0.schema.json",
    ROOT / "schemas" / "realtime-transport-event-v0.schema.json",
    ROOT / "schemas" / "realtime-transport-run-report-v0.schema.json",
    ROOT / "src" / "musica" / "realtime_callback.py",
    ROOT / "src" / "musica" / "realtime_transport.py",
    ROOT / "src" / "musica" / "rtio_r2_evidence.py",
    ROOT / "tests" / "test_rtio_r2_transport.py",
    ROOT / ".github" / "workflows" / "rtio-r2-exact-frame-transport-evidence.yml",
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


def _normal(project: Any, revision_id: str):
    transport = ExactFrameTransport(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=1024,
    )
    transport.play()
    transport.drain_to_eos()
    return transport.finalize()


def _segmented(project: Any, revision_id: str):
    transport = ExactFrameTransport(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
    )
    transport.play()
    transport.callback()
    transport.callback()
    transport.callback()
    transport.stop()
    transport.seek(48000)
    transport.play()
    transport.drain_to_eos()
    return transport.finalize()


def _failure(project: Any, revision_id: str):
    transport = ExactFrameTransport(
        project,
        revision_id,
        sample_rate_hz=8000,
        block_size_frames=256,
    )
    transport.play()
    transport.drain_to_eos(
        force_error_callback_indices={1},
        force_short_fill_callback_indices={2},
        force_late_callback_indices={3},
    )
    return transport.finalize()


def generate_rtio_r2_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-rtio-r2-") as temp_value:
        temp = Path(temp_value)
        project, revision_id = _fixture(temp)
        head_before = project.head_revision_id("main")

        normal_a = _normal(project, revision_id)
        normal_b = _normal(project, revision_id)
        segmented_a = _segmented(project, revision_id)
        segmented_b = _segmented(project, revision_id)
        failure_a = _failure(project, revision_id)
        failure_b = _failure(project, revision_id)

        invalid_transport = ExactFrameTransport(
            project,
            revision_id,
            sample_rate_hz=8000,
            block_size_frames=256,
        )
        invalid = {
            "callback_while_stopped": _blocked(lambda: invalid_transport.callback()),
            "stop_while_stopped": _blocked(lambda: invalid_transport.stop()),
            "negative_seek": _blocked(lambda: invalid_transport.seek(-1)),
            "seek_beyond_eos": _blocked(lambda: invalid_transport.seek(96001)),
        }
        invalid_transport.play()
        invalid["double_play"] = _blocked(lambda: invalid_transport.play())
        invalid["seek_while_playing"] = _blocked(lambda: invalid_transport.seek(100))
        invalid["finalize_while_playing"] = _blocked(lambda: invalid_transport.finalize())
        invalid_transport.stop()
        invalid["double_stop"] = _blocked(lambda: invalid_transport.stop())
        invalid_transport.seek(96000)
        invalid["play_at_eos_without_seek_away"] = _blocked(lambda: invalid_transport.play())
        invalid_transport.seek(0)
        invalid_transport.play()
        invalid["failure_index_outside_segment"] = _blocked(
            lambda: invalid_transport.drain_to_eos(
                force_late_callback_indices={999999}
            )
        )

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_segmented = _segmented(reopened, revision_id)

        _write_json(out / "realtime-plan.json", normal_a.plan)
        _write_json(out / "normal-transport-events.json", list(normal_a.events))
        _write_json(out / "normal-callback-trace.json", list(normal_a.callback_transactions))
        _write_json(out / "normal-transport-report.json", normal_a.report)
        (out / "normal-sink.pcm").write_bytes(normal_a.sink_payload)

        _write_json(out / "segmented-transport-events.json", list(segmented_a.events))
        _write_json(out / "segmented-callback-trace.json", list(segmented_a.callback_transactions))
        _write_json(out / "segmented-transport-report.json", segmented_a.report)
        (out / "segmented-sink.pcm").write_bytes(segmented_a.sink_payload)

        _write_json(out / "failure-transport-events.json", list(failure_a.events))
        _write_json(out / "failure-callback-trace.json", list(failure_a.callback_transactions))
        _write_json(out / "failure-transport-report.json", failure_a.report)
        (out / "failure-sink.pcm").write_bytes(failure_a.sink_payload)
        _write_json(out / "invalid-transport-results.json", invalid)
        _write_json(out / "latency-metadata.json", normal_a.report["latency"])

        segmented_seek = [
            event for event in segmented_a.events if event["command"] == "SEEK"
        ][0]
        first_after_seek = next(
            tx
            for tx in segmented_a.callback_transactions
            if tx["request"]["start_frame"] == 48000
        )
        proof = {
            "milestone": "RTIO-R2",
            "validation_class": "EXACT_FRAME_TRANSPORT_AND_LATENCY_DROPOUT_INSTRUMENTATION",
            "revision_id": revision_id,
            "normal_repeat_exact": normal_a == normal_b,
            "normal_reaches_eos": normal_a.report["metrics"]["final_state"] == "END_OF_STREAM"
            and normal_a.report["metrics"]["final_playhead_frame"] == 96000,
            "segmented_repeat_exact": segmented_a == segmented_b,
            "segmented_stop_seek_play": segmented_a.report["metrics"]["play_count"] == 2
            and segmented_a.report["metrics"]["stop_count"] == 1
            and segmented_a.report["metrics"]["seek_count"] == 1,
            "seek_exact_48000": segmented_seek["playhead_after"] == 48000,
            "callback_index_resets_after_seek": first_after_seek["request"]["callback_index"] == 0,
            "first_callback_after_seek_starts_48000": first_after_seek["request"]["start_frame"] == 48000,
            "failure_repeat_exact": failure_a == failure_b,
            "forced_error_count_one": failure_a.report["metrics"]["error_count"] == 1,
            "forced_short_fill_count_one": failure_a.report["metrics"]["short_fill_count"] == 1,
            "forced_late_count_one": failure_a.report["metrics"]["late_count"] == 1,
            "xrun_dropout_equivalent_three": failure_a.report["metrics"]["xrun_dropout_equivalent_count"] == 3,
            "failure_timeline_reaches_eos": failure_a.report["metrics"]["final_playhead_frame"] == 96000,
            "latency_is_configured_or_simulated_not_host_observed": (
                normal_a.report["latency"]["nominal_source"] == "simulated_backend_capability"
                and normal_a.report["latency"]["host_observed_latency_available"] is False
                and normal_a.report["latency"]["wall_clock_guarantee_claimed"] is False
            ),
            "invalid_paths_all_blocked": all(item["blocked"] for item in invalid.values()),
            "accepted_head_unchanged": project.head_revision_id("main") == head_before,
            "reopen_plan_exact": reopened_segmented.plan == segmented_a.plan,
            "reopen_events_exact": reopened_segmented.events == segmented_a.events,
            "reopen_callback_trace_exact": (
                reopened_segmented.callback_transactions
                == segmented_a.callback_transactions
            ),
            "reopen_sink_exact": reopened_segmented.sink_payload == segmented_a.sink_payload,
            "reopen_report_exact": reopened_segmented.report == segmented_a.report,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
            "runtime_state_is_canonical": False,
            "host_native_latency_claimed": False,
            "recording_claimed": False,
            "realtime_browser_control_claimed": False,
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
        "milestone": "RTIO-R2",
        "artifact_name": "musica-rtio-r2-exact-frame-transport-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_RTIO_R2_EVIDENCE_OUT",
        "artifacts/rtio-r2-exact-frame-transport-evidence",
    )
    generate_rtio_r2_evidence(destination)
