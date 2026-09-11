"""Generate M5-R2 real FluidSynth renderer evidence.

M5-R2 실제 FluidSynth renderer 근거를 생성합니다.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
from pathlib import Path
from typing import Any

from .compiler import compile_blueprint
from .contracts import validate_contract
from .evidence import artifact_record, canonical_json_bytes, sha256_file, write_canonical_json
from .fluidsynth_renderer import (
    FLUIDSYNTH_RENDERER_ID,
    FLUIDSYNTH_TARGET_VERSION,
    build_fluidsynth_request,
)
from .renderer import (
    build_renderer_request,
    get_renderer,
    music_ir_sha256,
    reference_renderer_capability,
    render_with_registry,
    verify_result_artifacts,
)


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _artifact_hashes(result: dict[str, Any]) -> dict[str, str]:
    return {str(item["role"]): str(item["sha256"]) for item in result["artifacts"]}


def _single_json(root: Path, filename: str) -> Path:
    matches = list(root.rglob(filename))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {filename} below {root}, found {len(matches)}")
    return matches[0]


def run_suite(blueprint_path: str | Path, out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    soundfont_env = os.environ.get("MUSICA_FLUIDSYNTH_SOUNDFONT")
    if not soundfont_env:
        raise RuntimeError("MUSICA_FLUIDSYNTH_SOUNDFONT is required for M5-R2 evidence")
    soundfont = Path(soundfont_env).resolve()
    if not soundfont.is_file() or soundfont.stat().st_size <= 0:
        raise RuntimeError("M5-R2 evidence SoundFont is missing or empty")
    soundfont_id = os.environ.get("MUSICA_FLUIDSYNTH_SOUNDFONT_ID", "FluidR3_GM-3.1")
    soundfont_sha = sha256_file(soundfont)

    checkout = Path.cwd().resolve()
    if soundfont == checkout or checkout in soundfont.parents:
        raise RuntimeError("M5-R2 evidence SoundFont must be provisioned outside the repository")

    blueprint = _load(blueprint_path)
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    music_ir = compile_blueprint(blueprint)
    validate_contract(music_ir, "music-ir-v0.schema.json")
    ir_before = canonical_json_bytes(music_ir)
    ir_hash = music_ir_sha256(music_ir)
    duration = float(blueprint["project"]["duration_seconds"])

    reference_capability = reference_renderer_capability()
    fluidsynth_capability = get_renderer(FLUIDSYNTH_RENDERER_ID).capability()

    reference_request = build_renderer_request(
        music_ir,
        request_id="M5-R2-REFERENCE-001",
        outputs=["midi", "wav"],
        duration_seconds=duration,
        sample_rate=48000,
        channels=1,
        sample_width_bytes=2,
    )
    fluidsynth_request = build_fluidsynth_request(
        music_ir,
        request_id="M5-R2-FLUIDSYNTH-001",
        soundfont_id=soundfont_id,
        soundfont_sha256=soundfont_sha,
        duration_seconds=duration,
        outputs=["midi", "wav"],
        sample_rate=48000,
        sample_width_bytes=2,
    )

    tracked: list[Path] = []
    tracked.append(write_canonical_json(root / "input" / "blueprint.json", blueprint))
    tracked.append(write_canonical_json(root / "input" / "music-ir.json", music_ir))
    tracked.append(
        write_canonical_json(root / "contracts" / "reference-capability.json", reference_capability)
    )
    tracked.append(
        write_canonical_json(root / "contracts" / "fluidsynth-capability.json", fluidsynth_capability)
    )
    tracked.append(
        write_canonical_json(root / "contracts" / "reference-request.json", reference_request)
    )
    tracked.append(
        write_canonical_json(root / "contracts" / "fluidsynth-request.json", fluidsynth_request)
    )

    reference_result = render_with_registry(reference_request, music_ir, root / "reference")
    high_a = render_with_registry(fluidsynth_request, music_ir, root / "fluidsynth-a")
    high_b = render_with_registry(fluidsynth_request, music_ir, root / "fluidsynth-b")

    verify_result_artifacts(reference_result, root / "reference")
    verify_result_artifacts(high_a, root / "fluidsynth-a")
    verify_result_artifacts(high_b, root / "fluidsynth-b")

    tracked.append(
        write_canonical_json(root / "reference" / "renderer-result.json", reference_result)
    )
    tracked.append(write_canonical_json(root / "fluidsynth-a" / "renderer-result.json", high_a))
    tracked.append(write_canonical_json(root / "fluidsynth-b" / "renderer-result.json", high_b))

    ref_qa_path = _single_json(root / "reference", "audio-quality.json")
    high_a_qa_path = _single_json(root / "fluidsynth-a", "audio-quality.json")
    high_b_qa_path = _single_json(root / "fluidsynth-b", "audio-quality.json")
    ref_qa = _load(ref_qa_path)
    high_a_qa = _load(high_a_qa_path)
    high_b_qa = _load(high_b_qa_path)
    for report in (ref_qa, high_a_qa, high_b_qa):
        validate_contract(report, "audio-quality-report-v0.schema.json")

    high_a_provenance_path = (
        root / "fluidsynth-a" / high_a["provenance"]["manifest_path"]
    )
    high_b_provenance_path = (
        root / "fluidsynth-b" / high_b["provenance"]["manifest_path"]
    )
    high_a_provenance = _load(high_a_provenance_path)
    high_b_provenance = _load(high_b_provenance_path)
    normalization_a = high_a_provenance["render_settings"]["duration_normalization"]
    normalization_b = high_b_provenance["render_settings"]["duration_normalization"]

    ref_hashes = _artifact_hashes(reference_result)
    high_a_hashes = _artifact_hashes(high_a)
    high_b_hashes = _artifact_hashes(high_b)
    byte_exact_observed = high_a_hashes == high_b_hashes
    raw_engine_artifacts_absent = not list(root.rglob("render.engine.wav"))

    proof = {
        "proof_version": "0",
        "platform": platform.platform(),
        "platform_system": platform.system(),
        "music_ir_sha256": ir_hash,
        "all_requests_bound_to_same_exact_music_ir": all(
            result["music_ir_sha256"] == ir_hash
            for result in (reference_result, high_a, high_b)
        ),
        "input_music_ir_unchanged_after_all_renders": canonical_json_bytes(music_ir) == ir_before,
        "reference": {
            "renderer_id": reference_result["renderer"]["renderer_id"],
            "artifact_hashes": ref_hashes,
            "sample_rate": ref_qa["container"]["sample_rate"],
            "channels": ref_qa["container"]["channels"],
            "sample_width_bytes": ref_qa["container"]["sample_width_bytes"],
            "qa_status": ref_qa["status"],
        },
        "fluidsynth": {
            "renderer_id": high_a["renderer"]["renderer_id"],
            "target_version": FLUIDSYNTH_TARGET_VERSION,
            "observed_version": high_a_provenance["engine"]["version"],
            "executable_sha256": high_a_provenance["engine"]["executable_sha256"],
            "soundfont_id": soundfont_id,
            "soundfont_sha256": soundfont_sha,
            "soundfont_size_bytes": soundfont.stat().st_size,
            "soundfont_outside_repository": not (
                soundfont == checkout or checkout in soundfont.parents
            ),
            "run_a_artifact_hashes": high_a_hashes,
            "run_b_artifact_hashes": high_b_hashes,
            "byte_exact_reproducibility_observed": byte_exact_observed,
            "declared_reproducibility": high_a["reproducibility"]["claim"],
            "individual_result_verified": high_a["reproducibility"]["verified"],
            "sample_rate": high_a_qa["container"]["sample_rate"],
            "channels": high_a_qa["container"]["channels"],
            "sample_width_bytes": high_a_qa["container"]["sample_width_bytes"],
            "run_a_qa_status": high_a_qa["status"],
            "run_b_qa_status": high_b_qa["status"],
            "run_a_non_zero_samples": high_a_qa["signal"]["non_zero_sample_count"],
            "run_a_clipping_samples": high_a_qa["signal"]["clipping_sample_count"],
            "run_a_duration_within_tolerance": high_a_qa["duration"]["within_tolerance"],
            "final_duration_seconds": high_a_qa["duration"]["actual_seconds"],
            "raw_duration_seconds": normalization_a["raw_duration_seconds"],
            "raw_sha256": normalization_a["raw_sha256"],
            "duration_normalization_policy": normalization_a["policy"],
            "duration_normalization_applied": normalization_a["normalization_applied"],
            "trimmed_frame_count": normalization_a["trimmed_frame_count"],
            "padding_applied": normalization_a["padding_applied"],
            "normalization_reproducible_between_runs": normalization_a == normalization_b,
            "raw_engine_artifacts_absent_from_evidence_bundle": raw_engine_artifacts_absent,
            "project_authority": high_a_provenance["project_authority"],
        },
        "capability_uplift": {
            "stereo_output_proven": high_a_qa["container"]["channels"] == 2
            and ref_qa["container"]["channels"] == 1,
            "48khz_output_proven": high_a_qa["container"]["sample_rate"] == 48000,
            "external_soundfont_hash_bound": (
                fluidsynth_request.get("resources", [{}])[0].get("sha256") == soundfont_sha
                and high_a_provenance["resources"][0]["sha256"] == soundfont_sha
            ),
        },
        "provisioning": {
            "fluidsynth_source_url": os.environ.get("MUSICA_FLUIDSYNTH_SOURCE_URL"),
            "fluidsynth_archive_sha256": os.environ.get("MUSICA_FLUIDSYNTH_SOURCE_SHA256"),
            "soundfont_source_url": os.environ.get("MUSICA_FLUIDSYNTH_SOUNDFONT_SOURCE_URL"),
            "soundfont_source_archive_sha256": os.environ.get(
                "MUSICA_FLUIDSYNTH_SOUNDFONT_SOURCE_SHA256"
            ),
            "soundfont_license": os.environ.get(
                "MUSICA_FLUIDSYNTH_SOUNDFONT_LICENSE", "MIT"
            ),
        },
        "perceptual_quality_superiority": "UNKNOWN",
    }

    required = [
        proof["all_requests_bound_to_same_exact_music_ir"],
        proof["input_music_ir_unchanged_after_all_renders"],
        proof["fluidsynth"]["observed_version"] == FLUIDSYNTH_TARGET_VERSION,
        proof["fluidsynth"]["soundfont_outside_repository"],
        proof["fluidsynth"]["run_a_qa_status"] in {"PASS", "WARN"},
        proof["fluidsynth"]["run_b_qa_status"] in {"PASS", "WARN"},
        int(proof["fluidsynth"]["run_a_non_zero_samples"] or 0) > 0,
        proof["fluidsynth"]["run_a_clipping_samples"] == 0,
        proof["fluidsynth"]["run_a_duration_within_tolerance"],
        proof["fluidsynth"]["final_duration_seconds"] == duration,
        float(proof["fluidsynth"]["raw_duration_seconds"]) >= duration,
        proof["fluidsynth"]["padding_applied"] is False,
        proof["fluidsynth"]["normalization_reproducible_between_runs"],
        proof["fluidsynth"]["raw_engine_artifacts_absent_from_evidence_bundle"],
        proof["fluidsynth"]["project_authority"] is False,
        proof["reference"]["qa_status"] in {"PASS", "WARN"},
        proof["capability_uplift"]["stereo_output_proven"],
        proof["capability_uplift"]["48khz_output_proven"],
        proof["capability_uplift"]["external_soundfont_hash_bound"],
        proof["platform_system"] == "Windows",
    ]
    if not all(required):
        raise RuntimeError("M5-R2 real renderer proof failed")

    proof_out = write_canonical_json(root / "proof.json", proof)
    tracked.extend(
        [
            ref_qa_path,
            high_a_qa_path,
            high_b_qa_path,
            high_a_provenance_path,
            high_b_provenance_path,
            proof_out,
        ]
    )
    for result, run_root in (
        (reference_result, root / "reference"),
        (high_a, root / "fluidsynth-a"),
        (high_b, root / "fluidsynth-b"),
    ):
        for item in result["artifacts"]:
            tracked.append(run_root / item["path"])

    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M5-R2-First-Higher-Fidelity-Local-Renderer-Adapter-v0",
        "source_blueprint": str(Path(blueprint_path).as_posix()),
        "music_ir_sha256": ir_hash,
        "proof": proof,
        "claim_boundary": [
            "real FluidSynth 2.6.0 execution on Windows CI",
            "exact external SoundFont hash/provenance binding",
            "same canonical Music IR rendered by reference and FluidSynth adapters",
            "objective 48 kHz stereo PCM signal validity",
            "deterministic trim of engine release/effect tail to explicit requested duration",
            "raw engine hash/duration retained in provenance without retaining unmanaged raw audio",
            "renderer artifact-only authority",
            "observed repeatability recorded without self-verification inflation",
            "perceptual quality superiority remains UNKNOWN",
            "not professional/mastering quality",
            "not DAW/VST interoperability",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(set(tracked), key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M5-R2 real FluidSynth evidence")
    parser.add_argument("--blueprint", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.blueprint, args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
