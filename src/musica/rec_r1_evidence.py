"""Generate deterministic REC-R1 recording-finalize authority evidence."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from .audio_assets import import_audio_asset, list_audio_assets
from .audio_contracts import audio_material_from_blueprint
from .audio_edit import (
    accept_audio_edit_preview,
    audio_material_sha256,
    blueprint_sha256,
    build_audio_edit_preview,
)
from .automation_edit import automation_material_sha256
from .contracts import ContractError
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .mram_r1_evidence import _audio_candidate, _routing_candidate, _routing_ops, _wav_bytes
from .project import MusicaProject, create_project
from .recording_capture import SimulatedCaptureRun, run_recording_capture_simulation
from .recording_finalize import (
    accept_recording_finalize_preview,
    build_recording_finalize_preview,
    canonical_capture_wav_bytes,
)
from .routed_mixer import render_routed_mix
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256
from .routing_edit import accept_routing_edit_preview, build_routing_edit_preview

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "recording-finalize-candidate-v0.schema.json",
    ROOT / "schemas" / "recording-finalize-authority-result-v0.schema.json",
    ROOT / "src" / "musica" / "audio_assets.py",
    ROOT / "src" / "musica" / "recording_capture.py",
    ROOT / "src" / "musica" / "recording_finalize.py",
    ROOT / "src" / "musica" / "rec_r1_evidence.py",
    ROOT / "tests" / "test_rec_r1_recording_finalize.py",
    ROOT / ".github" / "workflows" / "rec-r1-recording-finalize-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _blocked(fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:
        return {"blocked": True, "error": str(exc)}
    return {"blocked": False, "error": None}


def _source(parent: dict[str, Any]) -> dict[str, Any]:
    routing = routing_material_from_blueprint(parent)
    assert routing is not None
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(routing),
        "automation_material_sha256": automation_material_sha256(parent),
    }


def _candidate(
    parent: dict[str, Any],
    run: SimulatedCaptureRun,
    *,
    candidate_id: str,
    track_id: str = "AT-001",
    clip_id: str = "REC-CLIP-001",
    timeline_start_seconds: float = 0.2,
) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "recording_finalize_to_audio_material",
        "source": _source(parent),
        "capture": {
            "recording_capture_plan_sha256": run.plan["recording_capture_plan_sha256"],
            "recording_capture_run_report_sha256": run.report["recording_capture_run_report_sha256"],
            "payload_sha256": run.report["payload"]["payload_sha256"],
            "payload_size_bytes": run.report["payload"]["payload_size_bytes"],
            "sample_rate_hz": run.report["payload"]["sample_rate_hz"],
            "channels": run.report["payload"]["channels"],
            "captured_frames": run.report["payload"]["captured_frames"],
            "sample_format": run.report["payload"]["format"],
        },
        "destination": {
            "track_id": track_id,
            "clip_id": clip_id,
            "timeline_start_seconds": timeline_start_seconds,
            "gain_db": 0.0,
        },
        "actor": {"kind": "user", "actor_id": "rec-r1-evidence"},
        "reason": candidate_id,
        "preview_only": True,
    }


def generate_rec_r1_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-rec-r1-") as temp_value:
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
                "REC-R1-AUDIO",
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
            raise RuntimeError("REC-R1 audio fixture Preview blocked")
        audio_record = accept_audio_edit_preview(project, audio_preview)
        accepted_audio = project.read_revision(audio_record["revision_id"])

        routing_preview = build_routing_edit_preview(
            project,
            accepted_audio,
            _routing_candidate(accepted_audio, "REC-R1-ROUTING", _routing_ops()),
        )
        if not routing_preview.ready:
            raise RuntimeError("REC-R1 routing fixture Preview blocked")
        routing_record = accept_routing_edit_preview(project, routing_preview)
        source = project.read_revision(routing_record["revision_id"])
        source_revision_id = str(source["project"]["revision_id"])
        head_before = project.head_revision_id("main")
        baseline = render_routed_mix(project, source_revision_id, mix_sample_rate_hz=8000)
        assets_before = list_audio_assets(project)

        capture = run_recording_capture_simulation(
            project,
            source_revision_id,
            sample_rate_hz=8000,
            input_channels=1,
            block_size_frames=256,
            capture_frames=800,
        )
        candidate = _candidate(source, capture, candidate_id="REC-R1-FINALIZE")
        preview = build_recording_finalize_preview(project, source, candidate, capture)
        if not preview.ready or preview.blueprint is None:
            raise RuntimeError("REC-R1 recording Preview blocked")
        preview_head_unchanged = project.head_revision_id("main") == head_before
        preview_asset_store_unchanged = list_audio_assets(project) == assets_before
        generic_commit_blocked = _blocked(lambda: project.commit_revision(preview.blueprint))

        record = accept_recording_finalize_preview(project, preview, capture)
        accepted_revision_id = str(record["revision_id"])
        accepted = project.read_revision(accepted_revision_id)
        accepted_material = audio_material_from_blueprint(accepted)
        assert accepted_material is not None
        assets_after = list_audio_assets(project)
        accepted_render = render_routed_mix(project, accepted_revision_id, mix_sample_rate_hz=8000)
        second_accept_blocked = _blocked(
            lambda: accept_recording_finalize_preview(project, preview, capture)
        )

        tampered = SimulatedCaptureRun(
            plan=capture.plan,
            block_trace=capture.block_trace,
            captured_payload=capture.captured_payload + b"x",
            report=capture.report,
        )
        latest = accepted
        latest_capture = run_recording_capture_simulation(
            project,
            accepted_revision_id,
            sample_rate_hz=8000,
            input_channels=1,
            block_size_frames=256,
            capture_frames=800,
        )
        tamper_preview = build_recording_finalize_preview(
            project,
            latest,
            _candidate(latest, latest_capture, candidate_id="REC-R1-TAMPER", clip_id="REC-TAMPER"),
            SimulatedCaptureRun(
                plan=latest_capture.plan,
                block_trace=latest_capture.block_trace,
                captured_payload=latest_capture.captured_payload + b"x",
                report=latest_capture.report,
            ),
        )
        missing_preview = build_recording_finalize_preview(
            project,
            latest,
            _candidate(latest, latest_capture, candidate_id="REC-R1-MISSING", track_id="AT-MISSING", clip_id="REC-MISSING"),
            latest_capture,
        )
        duplicate_preview = build_recording_finalize_preview(
            project,
            latest,
            _candidate(latest, latest_capture, candidate_id="REC-R1-DUP", clip_id="AC-001"),
            latest_capture,
        )
        discard_preview = build_recording_finalize_preview(
            project,
            latest,
            _candidate(latest, latest_capture, candidate_id="REC-R1-DISCARD", clip_id="REC-DISCARD"),
            latest_capture,
        )
        discard_head_before = project.head_revision_id("main")
        discard_assets_before = list_audio_assets(project)
        del discard_preview
        discard_no_mutation = (
            project.head_revision_id("main") == discard_head_before
            and list_audio_assets(project) == discard_assets_before
        )

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_blueprint = reopened.read_revision(accepted_revision_id)
        reopened_render = render_routed_mix(
            reopened, accepted_revision_id, mix_sample_rate_hz=8000
        )

        descriptor = next(
            item for item in assets_after if item["asset_id"] == preview.prospective_asset_id
        )
        _write_json(out / "capture-plan.json", capture.plan)
        _write_json(out / "capture-report.json", capture.report)
        (out / "captured-input.pcm").write_bytes(capture.captured_payload)
        (out / "finalized-recording.wav").write_bytes(canonical_capture_wav_bytes(capture))
        _write_json(out / "recording-candidate.json", candidate)
        _write_json(out / "recording-preview.json", preview.as_dict())
        _write_json(out / "accepted-audio-material.json", accepted_material)
        _write_json(out / "accepted-recording-asset.json", descriptor)
        _write_json(out / "baseline-routed-plan.json", baseline.plan)
        (out / "baseline-routed.wav").write_bytes(baseline.wav_bytes)
        _write_json(out / "accepted-routed-plan.json", accepted_render.plan)
        (out / "accepted-routed.wav").write_bytes(accepted_render.wav_bytes)

        proof = {
            "milestone": "REC-R1",
            "validation_class": "TRUSTED_CAPTURED_ASSET_FINALIZE_AND_RECORDING_PREVIEW_ACCEPT_AUTHORITY",
            "source_revision_id": source_revision_id,
            "preview_ready": preview.ready,
            "preview_head_unchanged": preview_head_unchanged,
            "preview_asset_store_unchanged": preview_asset_store_unchanged,
            "generic_commit_bypass_blocked": generic_commit_blocked["blocked"],
            "accept_advanced_exactly_once": record["parent_revision_id"] == source_revision_id,
            "same_preview_second_accept_blocked": second_accept_blocked["blocked"],
            "prospective_asset_id_matches_accepted": descriptor["asset_id"] == preview.prospective_asset_id,
            "accepted_recording_changes_routed_plan": accepted_render.plan["routed_mix_plan_sha256"] != baseline.plan["routed_mix_plan_sha256"],
            "accepted_recording_changes_routed_wav": accepted_render.wav_sha256 != baseline.wav_sha256,
            "tampered_payload_preview_blocked": not tamper_preview.ready,
            "missing_track_preview_blocked": not missing_preview.ready,
            "duplicate_clip_preview_blocked": not duplicate_preview.ready,
            "discard_no_mutation": discard_no_mutation,
            "reopen_audio_material_exact": audio_material_from_blueprint(reopened_blueprint) == accepted_material,
            "reopen_assets_exact": list_audio_assets(reopened) == assets_after,
            "reopen_routed_plan_exact": reopened_render.plan == accepted_render.plan,
            "reopen_routed_wav_exact": reopened_render.wav_bytes == accepted_render.wav_bytes,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
            "capture_runtime_is_canonical": False,
            "capture_payload_is_canonical": False,
            "asset_resource_alone_is_creative_authority": False,
            "browser_recording_claimed": False,
            "monitoring_claimed": False,
            "host_native_input_claimed": False,
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
        "milestone": "REC-R1",
        "artifact_name": "musica-rec-r1-recording-finalize-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_REC_R1_EVIDENCE_OUT",
        "artifacts/rec-r1-recording-finalize-evidence",
    )
    generate_rec_r1_evidence(destination)
