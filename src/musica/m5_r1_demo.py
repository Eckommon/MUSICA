"""Generate canonical M5-R1 renderer-boundary and audio-QA evidence.

공식 M5-R1 renderer 경계 및 audio-QA 근거를 생성합니다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .compiler import compile_blueprint
from .contracts import validate_contract
from .evidence import artifact_record, canonical_json_bytes, sha256_file, write_canonical_json
from .renderer import (
    build_renderer_request,
    music_ir_sha256,
    reference_renderer_capability,
    render_with_registry,
    verify_result_artifacts,
)


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _artifact_hashes(result: dict[str, Any]) -> dict[str, str]:
    return {str(item["role"]): str(item["sha256"]) for item in result["artifacts"]}


def run_suite(blueprint_path: str | Path, out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    blueprint = _load(blueprint_path)
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    music_ir = compile_blueprint(blueprint)
    validate_contract(music_ir, "music-ir-v0.schema.json")
    ir_before = canonical_json_bytes(music_ir)
    duration = float(blueprint["project"]["duration_seconds"])

    request = build_renderer_request(
        music_ir,
        request_id="M5-R1-REFERENCE-001",
        outputs=["midi", "wav"],
        duration_seconds=duration,
    )
    capability = reference_renderer_capability()

    blueprint_out = write_canonical_json(root / "input" / "blueprint.json", blueprint)
    ir_out = write_canonical_json(root / "input" / "music-ir.json", music_ir)
    request_out = write_canonical_json(root / "contracts" / "renderer-request.json", request)
    capability_out = write_canonical_json(root / "contracts" / "renderer-capability.json", capability)

    result_a = render_with_registry(request, music_ir, root / "run-a")
    result_b = render_with_registry(request, music_ir, root / "run-b")
    result_a_out = write_canonical_json(root / "run-a" / "renderer-result.json", result_a)
    result_b_out = write_canonical_json(root / "run-b" / "renderer-result.json", result_b)
    verify_result_artifacts(result_a, root / "run-a")
    verify_result_artifacts(result_b, root / "run-b")

    qa_files_a = list((root / "run-a").rglob("audio-quality.json"))
    qa_files_b = list((root / "run-b").rglob("audio-quality.json"))
    if len(qa_files_a) != 1 or len(qa_files_b) != 1:
        raise RuntimeError("M5-R1 expected exactly one AudioQualityReport per reference render")
    qa_a = _load(qa_files_a[0])
    qa_b = _load(qa_files_b[0])
    validate_contract(qa_a, "audio-quality-report-v0.schema.json")
    validate_contract(qa_b, "audio-quality-report-v0.schema.json")

    hashes_a = _artifact_hashes(result_a)
    hashes_b = _artifact_hashes(result_b)
    proof = {
        "proof_version": "0",
        "music_ir_sha256": music_ir_sha256(music_ir),
        "request_bound_to_exact_music_ir": request["music_ir_sha256"] == music_ir_sha256(music_ir),
        "renderer_id": capability["renderer_id"],
        "renderer_classification": capability["classification"],
        "renderer_has_project_authority": False,
        "input_music_ir_unchanged_after_render": canonical_json_bytes(music_ir) == ir_before,
        "requested_outputs": list(request["outputs"]),
        "run_a_artifact_hashes": hashes_a,
        "run_b_artifact_hashes": hashes_b,
        "byte_exact_reproducibility": hashes_a == hashes_b,
        "run_a_audio_qa_status": qa_a["status"],
        "run_b_audio_qa_status": qa_b["status"],
        "run_a_audio_container_valid": qa_a["container"]["valid"],
        "run_a_audio_non_zero_samples": qa_a["signal"]["non_zero_sample_count"],
        "run_a_audio_clipping_samples": qa_a["signal"]["clipping_sample_count"],
        "run_a_duration_within_tolerance": qa_a["duration"]["within_tolerance"],
        "integrated_loudness_status": qa_a["loudness"]["measurement_status"],
    }
    if not all(
        [
            proof["request_bound_to_exact_music_ir"],
            proof["input_music_ir_unchanged_after_render"],
            proof["byte_exact_reproducibility"],
            proof["run_a_audio_container_valid"],
            proof["run_a_duration_within_tolerance"],
            int(proof["run_a_audio_non_zero_samples"] or 0) > 0,
            proof["run_a_audio_clipping_samples"] == 0,
            qa_a["status"] in {"PASS", "WARN"},
            qa_b["status"] in {"PASS", "WARN"},
        ]
    ):
        raise RuntimeError("M5-R1 positive reference proof failed")

    proof_out = write_canonical_json(root / "proof.json", proof)
    tracked = [
        blueprint_out,
        ir_out,
        request_out,
        capability_out,
        result_a_out,
        result_b_out,
        qa_files_a[0],
        qa_files_b[0],
        proof_out,
    ]
    for result, run_root in ((result_a, root / "run-a"), (result_b, root / "run-b")):
        for item in result["artifacts"]:
            tracked.append(run_root / item["path"])

    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M5-R1-Renderer-Adapter-Contract-Audio-QA-Baseline-v0",
        "source_blueprint": str(Path(blueprint_path).as_posix()),
        "music_ir_sha256": music_ir_sha256(music_ir),
        "renderer": {
            "renderer_id": capability["renderer_id"],
            "renderer_version": capability["renderer_version"],
            "classification": capability["classification"],
            "reproducibility": capability["reproducibility"],
        },
        "proof": proof,
        "claim_boundary": [
            "renderer-neutral authority boundary",
            "objective PCM WAV signal-validity baseline",
            "reference renderer byte reproducibility",
            "not professional or mastering audio quality",
            "not perceptual quality validation",
            "not VST/AU or DAW interoperability",
            "not a higher-fidelity renderer backend",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(set(tracked), key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M5-R1 renderer evidence")
    parser.add_argument("--blueprint", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.blueprint, args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
