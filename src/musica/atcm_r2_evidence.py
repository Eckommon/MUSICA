"""Generate deterministic ATCM-R2 native-mixer evidence."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
import wave
from pathlib import Path
from typing import Any

from .audio_assets import import_audio_asset
from .audio_edit import accept_audio_edit_preview, audio_material_sha256, blueprint_sha256, build_audio_edit_preview
from .audio_mixer_edit import build_audio_mixer_edit_preview
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .native_mixer import build_native_mix_plan, render_native_mix
from .project import MusicaProject, create_project

ROOT = Path(__file__).resolve().parents[2]
INTENT_PATH = ROOT / "examples" / "intents" / "dark-electronic-12s.json"
CONTRACT_PATHS = [
    ROOT / "schemas" / "native-mix-plan-v0.schema.json",
    ROOT / "schemas" / "audio-mixer-edit-candidate-v0.schema.json",
    ROOT / "src" / "musica" / "native_mixer.py",
    ROOT / "src" / "musica" / "audio_mixer_edit.py",
    ROOT / "src" / "musica" / "atcm_r2_evidence.py",
    ROOT / "tests" / "test_atcm_r2_native_mixer.py",
    ROOT / ".github" / "workflows" / "atcm-r2-native-mixer-evidence.yml",
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value))


def _wav_bytes(*, channels: int, frames: int, left: int, right: int = 0) -> bytes:
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(2)
        writer.setframerate(8000)
        payload = bytearray()
        for _ in range(frames):
            payload.extend(int(left).to_bytes(2, "little", signed=True))
            if channels == 2:
                payload.extend(int(right).to_bytes(2, "little", signed=True))
        writer.writeframes(bytes(payload))
    return stream.getvalue()


def _source(parent: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": parent["project"]["project_id"],
        "revision_id": parent["project"]["revision_id"],
        "blueprint_sha256": blueprint_sha256(parent),
        "audio_material_sha256": audio_material_sha256(parent),
    }


def _candidate(parent: dict[str, Any], candidate_id: str, operations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "candidate_version": "0",
        "candidate_id": candidate_id,
        "authority_target": "blueprint_audio_material",
        "source": _source(parent),
        "actor": {"kind": "user", "actor_id": "atcm-r2-evidence"},
        "reason": f"ATCM-R2 evidence candidate {candidate_id}",
        "operations": operations,
        "preview_only": True,
    }


def generate_atcm_r2_evidence(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    root = compose_blueprint(json.loads(INTENT_PATH.read_text(encoding="utf-8")))
    source_a_bytes = _wav_bytes(channels=1, frames=800, left=24576)
    source_b_bytes = _wav_bytes(channels=2, frames=800, left=24576, right=24576)

    with tempfile.TemporaryDirectory(prefix="musica-atcm-r2-") as temp_value:
        temp = Path(temp_value)
        project = create_project(temp / "song.musica", root)
        source_a = temp / "a.wav"
        source_b = temp / "b.wav"
        source_a.write_bytes(source_a_bytes)
        source_b.write_bytes(source_b_bytes)
        asset_a = import_audio_asset(project, source_a)
        asset_b = import_audio_asset(project, source_b)
        head_after_import = project.head_revision_id("main")

        arrangement = _candidate(root, "C-R2-EVIDENCE-ARRANGE", [
            {"operation_id":"OP-T1","op":"ADD_TRACK","track_id":"AT-001","order":0,"name":"Mono"},
            {"operation_id":"OP-T2","op":"ADD_TRACK","track_id":"AT-002","order":1,"name":"Stereo"},
            {"operation_id":"OP-C1","op":"ADD_CLIP","target":{"track_id":"AT-001"},"clip":{"clip_id":"AC-001","asset_id":asset_a["asset_id"],"timeline_start_seconds":0.0,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
            {"operation_id":"OP-C2","op":"ADD_CLIP","target":{"track_id":"AT-002"},"clip":{"clip_id":"AC-002","asset_id":asset_b["asset_id"],"timeline_start_seconds":0.05,"source_in_seconds":0.0,"source_out_seconds":0.1,"gain_db":0.0}},
        ])
        arrangement_preview = build_audio_edit_preview(project, root, arrangement)
        if not arrangement_preview.ready:
            raise RuntimeError("ATCM-R2 deterministic arrangement Preview was blocked")
        head_during_arrangement_preview = project.head_revision_id("main")
        arrangement_record = accept_audio_edit_preview(project, arrangement_preview)
        arrangement_id = str(arrangement_record["revision_id"])
        arrangement_blueprint = project.read_revision(arrangement_id)

        plan_before = build_native_mix_plan(project, arrangement_id, mix_sample_rate_hz=8000)
        render_before_a = render_native_mix(project, arrangement_id, mix_sample_rate_hz=8000)
        render_before_b = render_native_mix(project, arrangement_id, mix_sample_rate_hz=8000)

        mixer_candidate = _candidate(arrangement_blueprint, "C-R2-EVIDENCE-MIXER", [
            {"operation_id":"OP-M1","op":"SET_TRACK_MIXER","target":{"track_id":"AT-001"},"mixer":{"gain_db":-6.0,"pan":-0.5,"mute":False,"solo":True}},
            {"operation_id":"OP-M2","op":"SET_TRACK_MIXER","target":{"track_id":"AT-002"},"mixer":{"gain_db":0.0,"pan":1.0,"mute":True,"solo":True}},
        ])
        mixer_preview = build_audio_mixer_edit_preview(project, arrangement_blueprint, mixer_candidate)
        if not mixer_preview.ready:
            raise RuntimeError("ATCM-R2 deterministic mixer Preview was blocked")
        head_during_mixer_preview = project.head_revision_id("main")
        mixer_record = accept_audio_edit_preview(project, mixer_preview)
        mixer_revision_id = str(mixer_record["revision_id"])

        plan_after = build_native_mix_plan(project, mixer_revision_id, mix_sample_rate_hz=8000)
        render_after_a = render_native_mix(project, mixer_revision_id, mix_sample_rate_hz=8000)
        render_after_b = render_native_mix(project, mixer_revision_id, mix_sample_rate_hz=8000)
        _write_json(out / "mix-plan-before.json", plan_before)
        _write_json(out / "mix-plan-after.json", plan_after)
        (out / "mix-before.wav").write_bytes(render_before_a.wav_bytes)
        (out / "mix-after.wav").write_bytes(render_after_a.wav_bytes)

        archive = project.export_to(out / "project.musica.zip")
        reopened = MusicaProject.import_from(archive, temp / "reopened.musica")
        reopened_plan = build_native_mix_plan(reopened, mixer_revision_id, mix_sample_rate_hz=8000)
        reopened_render = render_native_mix(reopened, mixer_revision_id, mix_sample_rate_hz=8000)
        proof = {
            "milestone": "ATCM-R2",
            "validation_class": "BOUNDED_DETERMINISTIC_NATIVE_MULTITRACK_MIXER",
            "root_revision_id": root["project"]["revision_id"],
            "head_after_asset_import": head_after_import,
            "asset_import_did_not_advance_head": head_after_import == root["project"]["revision_id"],
            "arrangement_preview_did_not_advance_head": head_during_arrangement_preview == root["project"]["revision_id"],
            "arrangement_revision_id": arrangement_id,
            "mixer_preview_did_not_advance_head": head_during_mixer_preview == arrangement_id,
            "mixer_revision_id": mixer_revision_id,
            "plan_before_sha256": plan_before["mix_plan_sha256"],
            "plan_after_sha256": plan_after["mix_plan_sha256"],
            "wav_before_sha256": render_before_a.wav_sha256,
            "wav_after_sha256": render_after_a.wav_sha256,
            "plan_repeat_exact": plan_before == build_native_mix_plan(project, arrangement_id, mix_sample_rate_hz=8000),
            "wav_before_repeat_exact": render_before_a.wav_bytes == render_before_b.wav_bytes,
            "wav_after_repeat_exact": render_after_a.wav_bytes == render_after_b.wav_bytes,
            "controlled_mixer_state_changes_plan": plan_before["mix_plan_sha256"] != plan_after["mix_plan_sha256"],
            "controlled_mixer_state_changes_wav": render_before_a.wav_sha256 != render_after_a.wav_sha256,
            "overlap_clipping_observed_before": render_before_a.clipped_sample_count > 0,
            "reopen_plan_exact": reopened_plan == plan_after,
            "reopen_wav_exact": reopened_render.wav_bytes == render_after_a.wav_bytes,
            "reopen_wav_sha256_exact": reopened_render.wav_sha256 == render_after_a.wav_sha256,
            "rendered_audio_is_canonical": False,
            "realtime_audio_claimed": False,
            "browser_mixer_claimed": False,
            "recording_claimed": False,
            "plugin_hosting_claimed": False,
        }
        _write_json(out / "proof.json", proof)

    contract_hashes = []
    for path in CONTRACT_PATHS:
        data = path.read_bytes()
        contract_hashes.append({"path": path.relative_to(ROOT).as_posix(), "sha256": _sha(data), "size_bytes": len(data)})
    _write_json(out / "contract-hashes.json", contract_hashes)
    records = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "manifest.json"):
        data = path.read_bytes()
        records.append({"path": path.relative_to(out).as_posix(), "sha256": _sha(data), "size_bytes": len(data)})
    manifest = {"manifest_version":"0","milestone":"ATCM-R2","artifact_name":"musica-atcm-r2-native-mixer-evidence","files":records}
    _write_json(out / "manifest.json", manifest)
    return {"proof": proof, "manifest": manifest}


if __name__ == "__main__":
    import os
    generate_atcm_r2_evidence(os.environ.get("MUSICA_ATCM_R2_EVIDENCE_OUT", "artifacts/atcm-r2-native-mixer-evidence"))
