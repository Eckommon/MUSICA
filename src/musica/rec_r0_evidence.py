"""Generate deterministic REC-R0 simulated input capture evidence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from .contracts import ContractError
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .project import MusicaProject, create_project
from .recording_capture import (
    SimulatedInputBackend,
    build_recording_capture_plan,
    run_recording_capture_simulation,
    simulated_input_capability,
)

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "recording-input-capability-v0.schema.json",
    ROOT / "schemas" / "recording-capture-plan-v0.schema.json",
    ROOT / "schemas" / "recording-capture-run-report-v0.schema.json",
    ROOT / "src" / "musica" / "recording_capture.py",
    ROOT / "src" / "musica" / "rec_r0_evidence.py",
    ROOT / "tests" / "test_rec_r0_capture.py",
    ROOT / ".github" / "workflows" / "rec-r0-input-capture-evidence.yml",
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


def _invalid_lifecycle() -> dict[str, Any]:
    backend = SimulatedInputBackend(
        sample_rate_hz=8000,
        input_channels=1,
        block_size_frames=256,
        capture_frames=1024,
    )
    before_open_capture = _blocked(
        lambda: backend.capture_block(start_frame=0, requested_frame_count=256)
    )
    start_before_open = _blocked(backend.start)
    backend.open()
    backend.ready()
    backend.start()
    range_outside_plan = _blocked(
        lambda: backend.capture_block(start_frame=900, requested_frame_count=256)
    )
    backend.stop()
    backend.finalize()
    backend.close()
    double_close = _blocked(backend.close)
    return {
        "capture_before_open": before_open_capture,
        "start_before_open": start_before_open,
        "range_outside_plan": range_outside_plan,
        "double_close": double_close,
    }


def generate_rec_r0_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-rec-r0-") as temp_value:
        temp = Path(temp_value)
        root = compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))
        project = create_project(temp / "source.musica", root)
        revision_id = str(root["project"]["revision_id"])
        head_before = project.head_revision_id("main")

        capability = simulated_input_capability()
        plan_a = build_recording_capture_plan(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=2,
            block_size_frames=256,
            capture_frames=2050,
        )
        plan_b = build_recording_capture_plan(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=2,
            block_size_frames=256,
            capture_frames=2050,
        )
        normal_a = run_recording_capture_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=2,
            block_size_frames=256,
            capture_frames=2050,
        )
        normal_b = run_recording_capture_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=2,
            block_size_frames=256,
            capture_frames=2050,
        )
        failure_a = run_recording_capture_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=1,
            block_size_frames=256,
            capture_frames=2048,
            force_error_block_indices=[1],
            force_short_fill_block_indices=[2],
            force_late_block_indices=[3],
        )
        failure_b = run_recording_capture_simulation(
            project,
            revision_id,
            sample_rate_hz=8000,
            input_channels=1,
            block_size_frames=256,
            capture_frames=2048,
            force_error_block_indices=[1],
            force_short_fill_block_indices=[2],
            force_late_block_indices=[3],
        )

        invalid = {
            "unsupported_sample_rate": _blocked(
                lambda: build_recording_capture_plan(
                    project,
                    revision_id,
                    sample_rate_hz=16000,
                    input_channels=1,
                    block_size_frames=256,
                    capture_frames=1024,
                )
            ),
            "unsupported_channels": _blocked(
                lambda: build_recording_capture_plan(
                    project,
                    revision_id,
                    sample_rate_hz=8000,
                    input_channels=3,
                    block_size_frames=256,
                    capture_frames=1024,
                )
            ),
            "unsupported_block_size": _blocked(
                lambda: build_recording_capture_plan(
                    project,
                    revision_id,
                    sample_rate_hz=8000,
                    input_channels=1,
                    block_size_frames=333,
                    capture_frames=1024,
                )
            ),
            "invalid_capture_frames": _blocked(
                lambda: build_recording_capture_plan(
                    project,
                    revision_id,
                    sample_rate_hz=8000,
                    input_channels=1,
                    block_size_frames=256,
                    capture_frames=0,
                )
            ),
            "failure_index_outside_trace": _blocked(
                lambda: run_recording_capture_simulation(
                    project,
                    revision_id,
                    sample_rate_hz=8000,
                    input_channels=1,
                    block_size_frames=256,
                    capture_frames=1024,
                    force_error_block_indices=[999],
                )
            ),
            "error_short_overlap": _blocked(
                lambda: run_recording_capture_simulation(
                    project,
                    revision_id,
                    sample_rate_hz=8000,
                    input_channels=1,
                    block_size_frames=256,
                    capture_frames=1024,
                    force_error_block_indices=[1],
                    force_short_fill_block_indices=[1],
                )
            ),
            "lifecycle": _invalid_lifecycle(),
        }

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_run = run_recording_capture_simulation(
            reopened,
            revision_id,
            sample_rate_hz=8000,
            input_channels=2,
            block_size_frames=256,
            capture_frames=2050,
        )

        _write_json(out / "input-capability.json", capability)
        _write_json(out / "capture-plan.json", plan_a)
        _write_json(out / "normal-block-trace.json", list(normal_a.block_trace))
        _write_json(out / "normal-run-report.json", normal_a.report)
        (out / "normal-capture.pcm").write_bytes(normal_a.captured_payload)
        _write_json(out / "failure-block-trace.json", list(failure_a.block_trace))
        _write_json(out / "failure-run-report.json", failure_a.report)
        (out / "failure-capture.pcm").write_bytes(failure_a.captured_payload)
        _write_json(out / "invalid-results.json", invalid)

        lifecycle_blocked = all(
            item["blocked"] for item in invalid["lifecycle"].values()
        )
        proof = {
            "milestone": "REC-R0",
            "validation_class": "DETERMINISTIC_SIMULATED_INPUT_CAPTURE_SUBSTRATE",
            "revision_id": revision_id,
            "plan_repeat_exact": plan_a == plan_b,
            "normal_trace_repeat_exact": normal_a.block_trace == normal_b.block_trace,
            "normal_payload_repeat_exact": normal_a.captured_payload == normal_b.captured_payload,
            "normal_report_repeat_exact": normal_a.report == normal_b.report,
            "failure_trace_repeat_exact": failure_a.block_trace == failure_b.block_trace,
            "failure_payload_repeat_exact": failure_a.captured_payload == failure_b.captured_payload,
            "failure_report_repeat_exact": failure_a.report == failure_b.report,
            "failure_counts_exact": (
                failure_a.report["metrics"]["error_count"] == 1
                and failure_a.report["metrics"]["short_fill_count"] == 1
                and failure_a.report["metrics"]["late_count"] == 1
                and failure_a.report["metrics"]["dropout_equivalent_count"] == 3
            ),
            "failure_changes_payload": (
                failure_a.report["payload"]["payload_sha256"]
                != normal_a.report["payload"]["payload_sha256"]
            ),
            "invalid_config_paths_blocked": all(
                value["blocked"]
                for key, value in invalid.items()
                if key != "lifecycle"
            ),
            "invalid_lifecycle_paths_blocked": lifecycle_blocked,
            "accepted_head_unchanged": project.head_revision_id("main") == head_before,
            "reopen_plan_exact": reopened_run.plan == normal_a.plan,
            "reopen_trace_exact": reopened_run.block_trace == normal_a.block_trace,
            "reopen_payload_exact": reopened_run.captured_payload == normal_a.captured_payload,
            "reopen_report_exact": reopened_run.report == normal_a.report,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
            "runtime_state_is_canonical": False,
            "captured_payload_is_canonical": False,
            "captured_payload_imported_as_asset": False,
            "accepted_audio_material_changed": False,
            "host_native_input_claimed": False,
            "recording_accept_authority_claimed": False,
            "monitoring_claimed": False,
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
        "milestone": "REC-R0",
        "artifact_name": "musica-rec-r0-input-capture-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_REC_R0_EVIDENCE_OUT",
        "artifacts/rec-r0-input-capture-evidence",
    )
    generate_rec_r0_evidence(destination)
