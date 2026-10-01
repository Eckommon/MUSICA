"""Generate deterministic PLUG-R0 simulated plugin processor evidence."""

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
from .contracts import ContractError
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .mram_r1_evidence import (
    INTENT_PATH,
    _audio_candidate,
    _routing_candidate,
    _routing_ops,
    _wav_bytes,
)
from .plugin_reference import (
    build_plugin_processing_plan,
    plugin_material_sha256,
    render_simulated_plugins,
)
from .project import MusicaProject, create_project
from .routed_mixer import render_routed_mix
from .routing_edit import accept_routing_edit_preview, build_routing_edit_preview

ROOT = Path(__file__).resolve().parents[2]

CONTRACT_PATHS = [
    ROOT / "schemas" / "plugin-material-v0.schema.json",
    ROOT / "schemas" / "plugin-processing-plan-v0.schema.json",
    ROOT / "src" / "musica" / "plugin_reference.py",
    ROOT / "src" / "musica" / "project.py",
    ROOT / "src" / "musica" / "routed_mixer.py",
    ROOT / "src" / "musica" / "plug_r0_evidence.py",
    ROOT / "tests" / "test_plug_r0_simulated_processor.py",
    ROOT / ".github" / "workflows" / "plug-r0-simulated-processor-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _material(*, gain_db: float, delay_frames: int, bypass: bool = False) -> dict[str, Any]:
    return {
        "material_version": "0",
        "classification": "noncanonical_proposal",
        "descriptors": [
            {
                "plugin_id": "PLUG-REF-001",
                "format": "simulated_reference_v0",
                "vendor": "MUSICA",
                "name": "Reference Gain Delay",
                "version": "0",
                "processor_id": "musica-simulated-gain-delay-v0",
                "io": {
                    "input_channels": 2,
                    "output_channels": 2,
                    "sample_format": "float64",
                    "sample_rate_policy": "exact_match_required_no_resampling",
                },
                "parameters": [
                    {
                        "parameter_id": "gain_db",
                        "unit": "decibel",
                        "minimum": -60.0,
                        "maximum": 12.0,
                        "default": 0.0,
                    },
                    {
                        "parameter_id": "delay_frames",
                        "unit": "frames",
                        "minimum": 0.0,
                        "maximum": 4096.0,
                        "default": 0.0,
                    },
                ],
            }
        ],
        "instances": [
            {
                "instance_id": "PI-001",
                "plugin_id": "PLUG-REF-001",
                "owner": {"kind": "routing_node", "owner_id": "MASTER-001"},
                "slot": 0,
                "bypass": bypass,
                "state": {"gain_db": gain_db, "delay_frames": delay_frames},
            }
        ],
    }


def _fixture(root_dir: Path):
    root = compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))
    project = create_project(root_dir / "plug-r0-source.musica", root)

    wav_a = root_dir / "plug-a.wav"
    wav_b = root_dir / "plug-b.wav"
    wav_a.write_bytes(_wav_bytes(16384))
    wav_b.write_bytes(_wav_bytes(8192))
    asset_a = import_audio_asset(project, wav_a)
    asset_b = import_audio_asset(project, wav_b)

    audio_preview = build_audio_edit_preview(
        project,
        root,
        _audio_candidate(
            root,
            "PLUG-R0-AUDIO",
            [
                {
                    "operation_id": "A-T1",
                    "op": "ADD_TRACK",
                    "track_id": "AT-001",
                    "order": 0,
                    "name": "Primary",
                },
                {
                    "operation_id": "A-T2",
                    "op": "ADD_TRACK",
                    "track_id": "AT-002",
                    "order": 1,
                    "name": "Secondary",
                },
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
        raise RuntimeError("PLUG-R0 audio fixture Preview blocked")
    audio_record = accept_audio_edit_preview(project, audio_preview)
    accepted_audio = project.read_revision(audio_record["revision_id"])

    routing_preview = build_routing_edit_preview(
        project,
        accepted_audio,
        _routing_candidate(accepted_audio, "PLUG-R0-ROUTING", _routing_ops()),
    )
    if not routing_preview.ready:
        raise RuntimeError("PLUG-R0 routing fixture Preview blocked")
    routing_record = accept_routing_edit_preview(project, routing_preview)
    accepted_routed = project.read_revision(routing_record["revision_id"])
    return project, accepted_routed


def generate_plug_r0_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-plug-r0-") as temp_value:
        temp = Path(temp_value)
        project, accepted = _fixture(temp)
        revision_id = str(accepted["project"]["revision_id"])
        head_before = project.head_revision_id("main")

        baseline = render_routed_mix(
            project, revision_id, mix_sample_rate_hz=8000
        )
        material_a = _material(gain_db=-6.0, delay_frames=4)
        material_b = _material(gain_db=-12.0, delay_frames=4)
        material_bypass = _material(gain_db=12.0, delay_frames=128, bypass=True)

        plan_a1 = build_plugin_processing_plan(
            project, revision_id, material_a, sample_rate_hz=8000
        )
        plan_a2 = build_plugin_processing_plan(
            project, revision_id, material_a, sample_rate_hz=8000
        )
        render_a1 = render_simulated_plugins(
            project, revision_id, material_a, sample_rate_hz=8000
        )
        render_a2 = render_simulated_plugins(
            project, revision_id, material_a, sample_rate_hz=8000
        )
        render_b = render_simulated_plugins(
            project, revision_id, material_b, sample_rate_hz=8000
        )
        bypassed = render_simulated_plugins(
            project, revision_id, material_bypass, sample_rate_hz=8000
        )

        forced_error_blocked = False
        try:
            render_simulated_plugins(
                project,
                revision_id,
                material_a,
                sample_rate_hz=8000,
                force_error_instance_ids={"PI-001"},
            )
        except ContractError:
            forced_error_blocked = True

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_plan = build_plugin_processing_plan(
            reopened, revision_id, material_a, sample_rate_hz=8000
        )
        reopened_render = render_simulated_plugins(
            reopened, revision_id, material_a, sample_rate_hz=8000
        )

        _write_json(out / "plugin-material-a.json", material_a)
        _write_json(out / "plugin-material-b.json", material_b)
        _write_json(out / "plugin-material-bypass.json", material_bypass)
        _write_json(out / "plugin-plan-a.json", plan_a1)
        _write_json(out / "plugin-plan-b.json", render_b.plan)
        _write_json(out / "plugin-plan-bypass.json", bypassed.plan)
        _write_json(out / "baseline-routed-plan.json", baseline.plan)
        (out / "baseline-routed.wav").write_bytes(baseline.wav_bytes)
        (out / "plugin-a.wav").write_bytes(render_a1.wav_bytes)
        (out / "plugin-b.wav").write_bytes(render_b.wav_bytes)
        (out / "plugin-bypass.wav").write_bytes(bypassed.wav_bytes)

        proof = {
            "milestone": "PLUG-R0",
            "validation_class": "DETACHED_PLUGIN_CONTRACT_AND_DETERMINISTIC_SIMULATED_PROCESSOR",
            "accepted_head_unchanged": project.head_revision_id("main") == head_before,
            "plugin_material_is_canonical": False,
            "plugin_runtime_is_canonical": False,
            "processed_audio_is_canonical": False,
            "accepted_plugin_mutation_authority_open": False,
            "material_a_sha256": plugin_material_sha256(material_a),
            "material_b_sha256": plugin_material_sha256(material_b),
            "plan_repeat_exact": plan_a1 == plan_a2,
            "render_repeat_exact": render_a1.wav_bytes == render_a2.wav_bytes,
            "baseline_routed_wav_sha256": baseline.wav_sha256,
            "plugin_a_wav_sha256": render_a1.wav_sha256,
            "plugin_b_wav_sha256": render_b.wav_sha256,
            "bypass_wav_sha256": bypassed.wav_sha256,
            "active_plugin_changes_output": render_a1.wav_sha256 != baseline.wav_sha256,
            "controlled_gain_change_changes_plan": (
                render_a1.plan["plugin_processing_plan_sha256"]
                != render_b.plan["plugin_processing_plan_sha256"]
            ),
            "controlled_gain_change_changes_output": (
                render_a1.wav_sha256 != render_b.wav_sha256
            ),
            "bypass_is_byte_exact_routed_baseline": bypassed.wav_bytes
            == baseline.wav_bytes,
            "declared_latency_frames": int(
                render_a1.plan["total_effective_latency_frames"]
            ),
            "forced_processor_error_blocked": forced_error_blocked,
            "reopen_plan_exact": reopened_plan == plan_a1,
            "reopen_wav_exact": reopened_render.wav_bytes == render_a1.wav_bytes,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
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
        "milestone": "PLUG-R0",
        "artifact_name": "musica-plug-r0-simulated-processor-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_PLUG_R0_EVIDENCE_OUT",
        "artifacts/plug-r0-simulated-processor-evidence",
    )
    generate_plug_r0_evidence(destination)
