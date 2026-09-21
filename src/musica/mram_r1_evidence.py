"""Generate deterministic MRAM-R1 routing-authority and routed-mixer evidence."""

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

from .audio_assets import import_audio_asset
from .audio_edit import (
    accept_audio_edit_preview,
    audio_material_sha256,
    blueprint_sha256,
    build_audio_edit_preview,
)
from .contracts import ContractError
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .project import MusicaProject, create_project
from .routed_mixer import render_routed_mix
from .routing_contracts import routing_material_from_blueprint, routing_material_sha256
from .routing_edit import accept_routing_edit_preview, build_routing_edit_preview

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"

CONTRACT_PATHS = [
    ROOT / "schemas" / "routing-material-v0.schema.json",
    ROOT / "schemas" / "routing-plan-v0.schema.json",
    ROOT / "schemas" / "routing-edit-candidate-v0.schema.json",
    ROOT / "schemas" / "routing-authority-result-v0.schema.json",
    ROOT / "schemas" / "routed-mix-plan-v0.schema.json",
    ROOT / "src" / "musica" / "contracts.py",
    ROOT / "src" / "musica" / "compiler.py",
    ROOT / "src" / "musica" / "project.py",
    ROOT / "src" / "musica" / "routing_contracts.py",
    ROOT / "src" / "musica" / "routing_edit.py",
    ROOT / "src" / "musica" / "audio_edit.py",
    ROOT / "src" / "musica" / "audio_mixer_edit.py",
    ROOT / "src" / "musica" / "note_edit.py",
    ROOT / "src" / "musica" / "automation_edit.py",
    ROOT / "src" / "musica" / "studio_audio.py",
    ROOT / "src" / "musica" / "native_mixer.py",
    ROOT / "src" / "musica" / "routed_mixer.py",
    ROOT / "src" / "musica" / "mram_r1_evidence.py",
    ROOT / "tests" / "test_mram_r1_routing_authority_mixer.py",
    ROOT / ".github" / "workflows" / "mram-r1-routing-authority-mixer-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _blocked(fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except ContractError:
        return True
    return False


def _wav_bytes(value: int, *, rate: int = 8000, frames: int = 800) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        payload = bytearray()
        for _ in range(frames):
            payload.extend(int(value).to_bytes(2, "little", signed=True))
        writer.writeframes(bytes(payload))
    return stream.getvalue()


def _audio_source(parent: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
    }


def _audio_candidate(
    parent: dict[str, Any], candidate_id: str, operations: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_audio_material",
        "source": _audio_source(parent),
        "actor": {"kind": "user", "actor_id": "mram-r1-evidence"},
        "reason": candidate_id,
        "operations": operations,
        "preview_only": True,
    }


def _routing_source(parent: dict[str, Any]) -> dict[str, Any]:
    material = routing_material_from_blueprint(parent)
    assert material is not None
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
        "routing_material_sha256": routing_material_sha256(material),
    }


def _routing_candidate(
    parent: dict[str, Any], candidate_id: str, operations: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_routing_material",
        "source": _routing_source(parent),
        "actor": {"kind": "user", "actor_id": "mram-r1-evidence"},
        "reason": candidate_id,
        "operations": operations,
        "preview_only": True,
    }


def _routing_ops() -> list[dict[str, Any]]:
    return [
        {
            "operation_id": "R-N1",
            "op": "ADD_NODE",
            "node": {
                "node_id": "BUS-001",
                "order": 0,
                "name": "Music Bus",
                "node_type": "group",
                "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
                "output_node_id": "MASTER-001",
            },
        },
        {
            "operation_id": "R-N2",
            "op": "ADD_NODE",
            "node": {
                "node_id": "RETURN-001",
                "order": 1,
                "name": "Ambience Return",
                "node_type": "return",
                "mixer": {"gain_db": -3.0, "pan": 0.0, "mute": False},
                "output_node_id": "MASTER-001",
            },
        },
        {
            "operation_id": "R-N3",
            "op": "ADD_NODE",
            "node": {
                "node_id": "MASTER-001",
                "order": 2,
                "name": "Master",
                "node_type": "master",
                "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
                "output_node_id": None,
            },
        },
        {
            "operation_id": "R-O1",
            "op": "SET_TRACK_OUTPUT",
            "track_id": "AT-001",
            "target_node_id": "BUS-001",
        },
        {
            "operation_id": "R-O2",
            "op": "SET_TRACK_OUTPUT",
            "track_id": "AT-002",
            "target_node_id": "MASTER-001",
        },
        {
            "operation_id": "R-S1",
            "op": "ADD_SEND",
            "send": {
                "send_id": "SEND-001",
                "source": {"kind": "track", "source_id": "AT-001"},
                "target_node_id": "RETURN-001",
                "gain_db": -12.0,
                "tap": "post_fader",
            },
        },
    ]


def generate_mram_r1_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="musica-mram-r1-") as temp_value:
        temp = Path(temp_value)
        root = compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))
        project = create_project(temp / "source.musica", root)

        wav_a = temp / "a.wav"
        wav_b = temp / "b.wav"
        wav_a.write_bytes(_wav_bytes(16384))
        wav_b.write_bytes(_wav_bytes(8192))
        asset_a = import_audio_asset(project, wav_a)
        asset_b = import_audio_asset(project, wav_b)

        audio_candidate = _audio_candidate(
            root,
            "MRAM-R1-AUDIO",
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
        )
        audio_preview = build_audio_edit_preview(project, root, audio_candidate)
        if not audio_preview.ready:
            raise RuntimeError("MRAM-R1 evidence audio fixture Preview was blocked")
        audio_record = accept_audio_edit_preview(project, audio_preview)
        accepted_audio = project.read_revision(audio_record["revision_id"])

        source_head = project.head_revision_id("main")
        routing_candidate = _routing_candidate(
            accepted_audio, "MRAM-R1-ROUTING", _routing_ops()
        )
        routing_preview = build_routing_edit_preview(
            project, accepted_audio, routing_candidate
        )
        if not routing_preview.ready or routing_preview.blueprint is None:
            raise RuntimeError("MRAM-R1 routing Preview was blocked")
        preview_head_unchanged = project.head_revision_id("main") == source_head
        generic_commit_blocked = _blocked(
            lambda: project.commit_revision(routing_preview.blueprint)
        )

        routing_record = accept_routing_edit_preview(project, routing_preview)
        routed_revision_id = str(routing_record["revision_id"])
        routed_accepted = project.read_revision(routed_revision_id)
        routing_material = routing_material_from_blueprint(routed_accepted)
        assert routing_material is not None

        stale_reaccept_blocked = _blocked(
            lambda: accept_routing_edit_preview(project, routing_preview)
        )

        render_a = render_routed_mix(
            project, routed_revision_id, mix_sample_rate_hz=8000
        )
        render_b = render_routed_mix(
            project, routed_revision_id, mix_sample_rate_hz=8000
        )

        changed_candidate = _routing_candidate(
            routed_accepted,
            "MRAM-R1-SEND-GAIN",
            [
                {
                    "operation_id": "R-SG1",
                    "op": "SET_SEND_GAIN",
                    "send_id": "SEND-001",
                    "gain_db": -3.0,
                }
            ],
        )
        changed_preview = build_routing_edit_preview(
            project, routed_accepted, changed_candidate
        )
        if not changed_preview.ready:
            raise RuntimeError("MRAM-R1 controlled routing change was blocked")
        changed_record = accept_routing_edit_preview(project, changed_preview)
        changed_revision_id = str(changed_record["revision_id"])
        changed_accepted = project.read_revision(changed_revision_id)
        changed_render = render_routed_mix(
            project, changed_revision_id, mix_sample_rate_hz=8000
        )

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_render = render_routed_mix(
            reopened, changed_revision_id, mix_sample_rate_hz=8000
        )
        reopened_blueprint = reopened.read_revision(changed_revision_id)

        stale_candidate = _routing_candidate(
            changed_accepted,
            "MRAM-R1-STALE",
            [
                {
                    "operation_id": "R-M1",
                    "op": "SET_NODE_MIXER",
                    "node_id": "BUS-001",
                    "mixer": {"gain_db": -1.0, "pan": 0.0, "mute": False},
                }
            ],
        )
        stale_preview = build_routing_edit_preview(
            project, changed_accepted, stale_candidate
        )
        advance_candidate = _routing_candidate(
            changed_accepted,
            "MRAM-R1-ADVANCE",
            [
                {
                    "operation_id": "R-M2",
                    "op": "SET_NODE_MIXER",
                    "node_id": "RETURN-001",
                    "mixer": {"gain_db": -4.0, "pan": 0.0, "mute": False},
                }
            ],
        )
        advance_preview = build_routing_edit_preview(
            project, changed_accepted, advance_candidate
        )
        if not stale_preview.ready or not advance_preview.ready:
            raise RuntimeError("MRAM-R1 stale-source evidence Preview was blocked")
        accept_routing_edit_preview(project, advance_preview)
        stale_after_head_advance_blocked = _blocked(
            lambda: accept_routing_edit_preview(project, stale_preview)
        )

        cycle_ops = [
            {
                "operation_id": "C-A",
                "op": "ADD_NODE",
                "node": {
                    "node_id": "CYCLE-A",
                    "order": 3,
                    "name": "Cycle A",
                    "node_type": "bus",
                    "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
                    "output_node_id": "CYCLE-B",
                },
            },
            {
                "operation_id": "C-B",
                "op": "ADD_NODE",
                "node": {
                    "node_id": "CYCLE-B",
                    "order": 4,
                    "name": "Cycle B",
                    "node_type": "bus",
                    "mixer": {"gain_db": 0.0, "pan": 0.0, "mute": False},
                    "output_node_id": "CYCLE-A",
                },
            },
        ]
        latest = project.read_revision(project.head_revision_id("main"))
        cycle_preview = build_routing_edit_preview(
            project,
            latest,
            _routing_candidate(latest, "MRAM-R1-CYCLE", cycle_ops),
        )

        missing_preview = build_routing_edit_preview(
            project,
            latest,
            _routing_candidate(
                latest,
                "MRAM-R1-MISSING",
                [
                    {
                        "operation_id": "M-O1",
                        "op": "SET_TRACK_OUTPUT",
                        "track_id": "AT-001",
                        "target_node_id": "MISSING",
                    }
                ],
            ),
        )

        _write_json(out / "accepted-routing.json", routing_material)
        _write_json(out / "routed-plan.json", render_a.plan)
        (out / "routed-mix.wav").write_bytes(render_a.wav_bytes)
        changed_material = routing_material_from_blueprint(changed_accepted)
        assert changed_material is not None
        _write_json(out / "changed-routing.json", changed_material)
        _write_json(out / "changed-routed-plan.json", changed_render.plan)
        (out / "changed-routed-mix.wav").write_bytes(changed_render.wav_bytes)

        proof = {
            "milestone": "MRAM-R1",
            "validation_class": "TRUSTED_ROUTING_PREVIEW_ACCEPT_AND_DETERMINISTIC_ROUTED_OFFLINE_MIXER",
            "source_head_before_preview": source_head,
            "routing_preview_ready": routing_preview.ready,
            "routing_preview_head_unchanged": preview_head_unchanged,
            "generic_commit_routing_bypass_blocked": generic_commit_blocked,
            "routing_accept_advanced_exactly_once": (
                routing_record["parent_revision_id"] == source_head
                and project.read_revision_record(routed_revision_id)["revision_id"]
                == routed_revision_id
            ),
            "same_preview_second_accept_blocked": stale_reaccept_blocked,
            "accepted_routing_material_sha256": routing_material_sha256(
                routing_material
            ),
            "routed_plan_repeat_exact": render_a.plan == render_b.plan,
            "routed_wav_repeat_exact": render_a.wav_bytes == render_b.wav_bytes,
            "routed_mix_plan_sha256": render_a.plan["routed_mix_plan_sha256"],
            "routed_wav_sha256": render_a.wav_sha256,
            "controlled_send_change_changes_plan": (
                changed_render.plan["routed_mix_plan_sha256"]
                != render_a.plan["routed_mix_plan_sha256"]
            ),
            "controlled_send_change_changes_wav": (
                changed_render.wav_sha256 != render_a.wav_sha256
            ),
            "reopen_routing_exact": (
                routing_material_from_blueprint(reopened_blueprint)
                == routing_material_from_blueprint(changed_accepted)
            ),
            "reopen_plan_exact": reopened_render.plan == changed_render.plan,
            "reopen_wav_exact": reopened_render.wav_bytes == changed_render.wav_bytes,
            "reopen_integrity_pass": reopened.verify_integrity()["status"] == "PASS",
            "stale_preview_after_head_advance_blocked": stale_after_head_advance_blocked,
            "cycle_candidate_blocked": not cycle_preview.ready,
            "missing_target_candidate_blocked": not missing_preview.ready,
            "post_fader_send_explicit": all(
                item["tap"] == "post_fader"
                for item in render_a.plan["routing"]["sends"]
            ),
            "rendered_audio_is_canonical": False,
            "routing_runtime_is_canonical": False,
            "automation_mapping_claimed": False,
            "browser_routing_claimed": False,
            "realtime_audio_claimed": False,
            "recording_claimed": False,
            "plugin_hosting_claimed": False,
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
        "milestone": "MRAM-R1",
        "artifact_name": "musica-mram-r1-routing-authority-mixer-evidence",
        "files": records,
    }
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    destination = os.environ.get(
        "MUSICA_MRAM_R1_EVIDENCE_OUT",
        "artifacts/mram-r1-routing-authority-mixer-evidence",
    )
    generate_mram_r1_evidence(destination)
