"""Generate M5-R4 controlled paired renderer-comparison evidence.

M5-R4 통제 쌍대 renderer 비교 근거를 생성합니다.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np

from .audio_compare import (
    ANALYZER_ID,
    ANALYZER_VERSION,
    build_audio_comparison,
    comparison_sha256,
)
from .compiler import compile_blueprint
from .contracts import ContractError, validate_contract
from .evidence import artifact_record, canonical_json_bytes, sha256_file, write_canonical_json
from .fluidsynth_renderer import FLUIDSYNTH_RENDERER_ID, FLUIDSYNTH_TARGET_VERSION, build_fluidsynth_request
from .renderer import build_renderer_request, music_ir_sha256, render_with_registry, verify_result_artifacts

REFERENCE_RENDERER_ID = "musica-reference-local"
FLUIDR3_VERSION = "3.1"


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _single_file(root: Path, filename: str) -> Path:
    matches = list(root.rglob(filename))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {filename} under {root}, found {len(matches)}")
    return matches[0]


def _artifact_by_role(result: dict[str, Any], role: str) -> dict[str, Any]:
    matches = [item for item in result["artifacts"] if item["role"] == role]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {role} artifact, found {len(matches)}")
    return matches[0]


def _request_config_hash(request: dict[str, Any]) -> str:
    config = {
        "renderer_id": request["renderer_id"],
        "outputs": request["outputs"],
        "seed": request.get("seed"),
        "audio": request["audio"],
        "hints": request.get("hints", {}),
        "resources": request.get("resources", []),
    }
    return _canonical_hash(config)


def _source_binding(blueprint: dict[str, Any], music_ir: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": str(blueprint["project"]["project_id"]),
        "blueprint_revision_id": str(blueprint["project"]["revision_id"]),
        "blueprint_sha256": _canonical_hash(blueprint),
        "music_ir_sha256": music_ir_sha256(music_ir),
        "target_duration_seconds": float(blueprint["project"]["duration_seconds"]),
    }


def _artifact_evidence(
    artifact: dict[str, Any],
    qa: dict[str, Any],
) -> dict[str, Any]:
    return {
        "role": "wav",
        "sha256": artifact["sha256"],
        "size_bytes": int(artifact["size_bytes"]),
        "sample_rate": int(qa["container"]["sample_rate"]),
        "channels": int(qa["container"]["channels"]),
        "bit_depth": int(qa["container"]["bit_depth"]),
        "duration_seconds": float(qa["duration"]["actual_seconds"]),
    }


def _qa_binding(qa: dict[str, Any], qa_path: Path) -> dict[str, Any]:
    return {
        "report_id": qa["report_id"],
        "report_sha256": sha256_file(qa_path),
        "status": qa["status"],
    }


def _reference_side(
    *,
    source: dict[str, Any],
    request: dict[str, Any],
    result: dict[str, Any],
    qa: dict[str, Any],
    qa_path: Path,
) -> dict[str, Any]:
    return {
        "renderer_id": result["renderer"]["renderer_id"],
        "renderer_version": result["renderer"]["renderer_version"],
        "bound_music_ir_sha256": result["music_ir_sha256"],
        "runtime": {
            "kind": "in_process",
            "name": "CPython",
            "version": platform.python_version(),
            "executable_sha256": sha256_file(Path(sys.executable)),
            "os": platform.system(),
            "architecture": platform.machine() or "unknown",
        },
        "content": [],
        "config_sha256": _request_config_hash(request),
        "raw_artifact": _artifact_evidence(_artifact_by_role(result, "wav"), qa),
        "audio_quality_report": _qa_binding(qa, qa_path),
        "renderer_normalizations": [
            {
                "type": "direct_requested_duration_v0",
                "status": "NOT_APPLIED",
                "description": "Reference renderer emitted the requested final comparison duration directly.",
            }
        ],
        "_source_binding": dict(source),
    }


def _fluidsynth_side(
    *,
    source: dict[str, Any],
    request: dict[str, Any],
    result: dict[str, Any],
    qa: dict[str, Any],
    qa_path: Path,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    resource = provenance["resources"][0]
    normalization = provenance["render_settings"]["duration_normalization"]
    return {
        "renderer_id": result["renderer"]["renderer_id"],
        "renderer_version": result["renderer"]["renderer_version"],
        "bound_music_ir_sha256": result["music_ir_sha256"],
        "runtime": {
            "kind": "external_process",
            "name": provenance["engine"]["name"],
            "version": provenance["engine"]["version"],
            "executable_sha256": provenance["engine"]["executable_sha256"],
            "os": platform.system(),
            "architecture": platform.machine() or "unknown",
        },
        "content": [
            {
                "content_id": resource["resource_id"],
                "version": FLUIDR3_VERSION,
                "sha256": resource["sha256"],
            }
        ],
        "config_sha256": _request_config_hash(request),
        "raw_artifact": _artifact_evidence(_artifact_by_role(result, "wav"), qa),
        "audio_quality_report": _qa_binding(qa, qa_path),
        "renderer_normalizations": [
            {
                "type": normalization["policy"],
                "status": "APPLIED" if normalization["normalization_applied"] else "NOT_APPLIED",
                "description": (
                    f"Raw engine duration={normalization['raw_duration_seconds']:.9f}s; "
                    f"target={normalization['target_duration_seconds']:.9f}s; "
                    f"trimmed_frames={normalization['trimmed_frame_count']}; padding=false."
                ),
            }
        ],
        "_source_binding": dict(source),
    }


def _render_pair(
    *,
    root: Path,
    token: str,
    music_ir: dict[str, Any],
    source: dict[str, Any],
    soundfont_id: str,
    soundfont_sha: str,
) -> dict[str, Any]:
    duration = float(source["target_duration_seconds"])
    ref_request = build_renderer_request(
        music_ir,
        request_id=f"M5-R4-REF-{token}",
        outputs=["midi", "wav"],
        renderer_id=REFERENCE_RENDERER_ID,
        duration_seconds=duration,
        sample_rate=22050,
        channels=1,
        sample_width_bytes=2,
    )
    fluid_request = build_fluidsynth_request(
        music_ir,
        request_id=f"M5-R4-FLUID-{token}",
        soundfont_id=soundfont_id,
        soundfont_sha256=soundfont_sha,
        duration_seconds=duration,
        outputs=["midi", "wav"],
        sample_rate=48000,
        sample_width_bytes=2,
    )
    ref_root = root / f"pair-{token}" / "reference"
    fluid_root = root / f"pair-{token}" / "fluidsynth"
    ref_result = render_with_registry(ref_request, music_ir, ref_root)
    fluid_result = render_with_registry(fluid_request, music_ir, fluid_root)
    verify_result_artifacts(ref_result, ref_root)
    verify_result_artifacts(fluid_result, fluid_root)

    ref_qa_path = _single_file(ref_root, "audio-quality.json")
    fluid_qa_path = _single_file(fluid_root, "audio-quality.json")
    ref_qa = _load(ref_qa_path)
    fluid_qa = _load(fluid_qa_path)
    validate_contract(ref_qa, "audio-quality-report-v0.schema.json")
    validate_contract(fluid_qa, "audio-quality-report-v0.schema.json")

    provenance_path = fluid_root / fluid_result["provenance"]["manifest_path"]
    provenance = _load(provenance_path)
    ref_wav = ref_root / _artifact_by_role(ref_result, "wav")["path"]
    fluid_wav = fluid_root / _artifact_by_role(fluid_result, "wav")["path"]

    ref_side = _reference_side(
        source=source,
        request=ref_request,
        result=ref_result,
        qa=ref_qa,
        qa_path=ref_qa_path,
    )
    fluid_side = _fluidsynth_side(
        source=source,
        request=fluid_request,
        result=fluid_result,
        qa=fluid_qa,
        qa_path=fluid_qa_path,
        provenance=provenance,
    )
    comparison = build_audio_comparison(
        comparison_id="M5-R4-PAIR-001",
        source_binding=source,
        source_binding_a=ref_side["_source_binding"],
        source_binding_b=fluid_side["_source_binding"],
        renderer_a=ref_side,
        renderer_b=fluid_side,
        wav_a=ref_wav,
        wav_b=fluid_wav,
        qa_a=ref_qa,
        qa_b=fluid_qa,
    )
    return {
        "reference_request": ref_request,
        "fluidsynth_request": fluid_request,
        "reference_result": ref_result,
        "fluidsynth_result": fluid_result,
        "reference_qa": ref_qa,
        "fluidsynth_qa": fluid_qa,
        "fluidsynth_provenance": provenance,
        "reference_side": ref_side,
        "fluidsynth_side": fluid_side,
        "reference_wav": ref_wav,
        "fluidsynth_wav": fluid_wav,
        "reference_qa_path": ref_qa_path,
        "fluidsynth_qa_path": fluid_qa_path,
        "fluidsynth_provenance_path": provenance_path,
        "comparison": comparison,
    }


def _negative_cases(pair: dict[str, Any], source: dict[str, Any]) -> dict[str, bool]:
    source_mismatch = copy.deepcopy(pair["fluidsynth_side"]["_source_binding"])
    source_mismatch["music_ir_sha256"] = "0" * 64
    mismatch = build_audio_comparison(
        comparison_id="M5-R4-NEG-SOURCE",
        source_binding=source,
        source_binding_a=pair["reference_side"]["_source_binding"],
        source_binding_b=source_mismatch,
        renderer_a=pair["reference_side"],
        renderer_b=pair["fluidsynth_side"],
        wav_a=pair["reference_wav"],
        wav_b=pair["fluidsynth_wav"],
        qa_a=pair["reference_qa"],
        qa_b=pair["fluidsynth_qa"],
    )

    failed_qa = copy.deepcopy(pair["fluidsynth_qa"])
    failed_qa["status"] = "FAIL"
    failed_qa_side = copy.deepcopy(pair["fluidsynth_side"])
    failed_qa_side["audio_quality_report"]["report_sha256"] = _canonical_hash(failed_qa)
    failed_qa_side["audio_quality_report"]["status"] = "FAIL"
    qa_fail = build_audio_comparison(
        comparison_id="M5-R4-NEG-QA",
        source_binding=source,
        source_binding_a=pair["reference_side"]["_source_binding"],
        source_binding_b=failed_qa_side["_source_binding"],
        renderer_a=pair["reference_side"],
        renderer_b=failed_qa_side,
        wav_a=pair["reference_wav"],
        wav_b=pair["fluidsynth_wav"],
        qa_a=pair["reference_qa"],
        qa_b=failed_qa,
    )

    missing_provenance_side = copy.deepcopy(pair["fluidsynth_side"])
    missing_provenance_side["content"] = []
    missing = build_audio_comparison(
        comparison_id="M5-R4-NEG-PROVENANCE",
        source_binding=source,
        source_binding_a=pair["reference_side"]["_source_binding"],
        source_binding_b=missing_provenance_side["_source_binding"],
        renderer_a=pair["reference_side"],
        renderer_b=missing_provenance_side,
        wav_a=pair["reference_wav"],
        wav_b=pair["fluidsynth_wav"],
        qa_a=pair["reference_qa"],
        qa_b=pair["fluidsynth_qa"],
    )

    tampered = copy.deepcopy(pair["comparison"])
    tampered["claim_boundary"]["perceptual_superiority"] = "RENDERER_B_BETTER"
    claim_tamper_rejected = False
    try:
        validate_contract(tampered, "audio-comparison-result-v0.schema.json")
    except ContractError:
        claim_tamper_rejected = True

    return {
        "different_music_ir_source_not_comparable": mismatch["comparability"]["status"] == "NOT_COMPARABLE",
        "failed_qa_not_comparable": qa_fail["comparability"]["status"] == "NOT_COMPARABLE",
        "missing_required_content_provenance_not_comparable": missing["comparability"]["status"] == "NOT_COMPARABLE",
        "perceptual_superiority_schema_tamper_rejected": claim_tamper_rejected,
    }


def run_suite(blueprint_path: str | Path, out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    soundfont_env = os.environ.get("MUSICA_FLUIDSYNTH_SOUNDFONT")
    if not soundfont_env:
        raise RuntimeError("MUSICA_FLUIDSYNTH_SOUNDFONT is required for M5-R4 evidence")
    soundfont = Path(soundfont_env).resolve()
    if not soundfont.is_file() or soundfont.stat().st_size <= 0:
        raise RuntimeError("M5-R4 evidence SoundFont is missing or empty")
    checkout = Path.cwd().resolve()
    if soundfont == checkout or checkout in soundfont.parents:
        raise RuntimeError("M5-R4 SoundFont must remain external to the repository")
    soundfont_id = os.environ.get("MUSICA_FLUIDSYNTH_SOUNDFONT_ID", "FluidR3_GM-3.1")
    soundfont_sha = sha256_file(soundfont)

    blueprint = _load(blueprint_path)
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    music_ir = compile_blueprint(blueprint)
    validate_contract(music_ir, "music-ir-v0.schema.json")
    source = _source_binding(blueprint, music_ir)
    ir_before = canonical_json_bytes(music_ir)

    tracked: list[Path] = []
    tracked.append(write_canonical_json(root / "input" / "blueprint.json", blueprint))
    tracked.append(write_canonical_json(root / "input" / "music-ir.json", music_ir))
    tracked.append(write_canonical_json(root / "input" / "source-binding.json", source))

    pair_a = _render_pair(
        root=root,
        token="A",
        music_ir=music_ir,
        source=source,
        soundfont_id=soundfont_id,
        soundfont_sha=soundfont_sha,
    )
    pair_b = _render_pair(
        root=root,
        token="B",
        music_ir=music_ir,
        source=source,
        soundfont_id=soundfont_id,
        soundfont_sha=soundfont_sha,
    )

    compare_a_path = write_canonical_json(root / "comparison-a.json", pair_a["comparison"])
    compare_b_path = write_canonical_json(root / "comparison-b.json", pair_b["comparison"])
    tracked.extend([compare_a_path, compare_b_path])

    negatives = _negative_cases(pair_a, source)
    negatives_path = write_canonical_json(root / "negative-cases.json", negatives)
    tracked.append(negatives_path)

    reference_hash_equal = (
        pair_a["reference_side"]["raw_artifact"]["sha256"]
        == pair_b["reference_side"]["raw_artifact"]["sha256"]
    )
    fluidsynth_hash_equal = (
        pair_a["fluidsynth_side"]["raw_artifact"]["sha256"]
        == pair_b["fluidsynth_side"]["raw_artifact"]["sha256"]
    )
    comparison_hash_equal = comparison_sha256(pair_a["comparison"]) == comparison_sha256(pair_b["comparison"])
    metric_equality = (
        pair_a["comparison"]["objective_metrics_a"] == pair_b["comparison"]["objective_metrics_a"]
        and pair_a["comparison"]["objective_metrics_b"] == pair_b["comparison"]["objective_metrics_b"]
        and pair_a["comparison"]["paired_deltas"] == pair_b["comparison"]["paired_deltas"]
    )

    proof = {
        "proof_version": "0",
        "milestone": "M5-R4B",
        "platform": platform.platform(),
        "platform_system": platform.system(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "analyzer_id": ANALYZER_ID,
        "analyzer_version": ANALYZER_VERSION,
        "source_binding": source,
        "input_music_ir_unchanged_after_all_renders": canonical_json_bytes(music_ir) == ir_before,
        "pair_a_verdict": pair_a["comparison"]["verdict"],
        "pair_a_comparability": pair_a["comparison"]["comparability"],
        "pair_a_analysis_policy": pair_a["comparison"]["analysis_policy"],
        "reference_format": pair_a["reference_side"]["raw_artifact"],
        "fluidsynth_format": pair_a["fluidsynth_side"]["raw_artifact"],
        "confounds": pair_a["comparison"]["confounds"],
        "claim_boundary": pair_a["comparison"]["claim_boundary"],
        "reproducibility": {
            "reference_wav_sha256_equal": reference_hash_equal,
            "fluidsynth_wav_sha256_equal": fluidsynth_hash_equal,
            "comparison_canonical_sha256_equal": comparison_hash_equal,
            "objective_metrics_and_deltas_equal": metric_equality,
            "comparison_a_sha256": comparison_sha256(pair_a["comparison"]),
            "comparison_b_sha256": comparison_sha256(pair_b["comparison"]),
        },
        "negative_cases": negatives,
        "fluidsynth": {
            "target_version": FLUIDSYNTH_TARGET_VERSION,
            "observed_version": pair_a["fluidsynth_provenance"]["engine"]["version"],
            "executable_sha256": pair_a["fluidsynth_provenance"]["engine"]["executable_sha256"],
            "soundfont_id": soundfont_id,
            "soundfont_sha256": soundfont_sha,
            "soundfont_size_bytes": soundfont.stat().st_size,
            "soundfont_outside_repository": True,
            "source_url": os.environ.get("MUSICA_FLUIDSYNTH_SOURCE_URL"),
            "source_archive_sha256": os.environ.get("MUSICA_FLUIDSYNTH_SOURCE_SHA256"),
            "soundfont_source_url": os.environ.get("MUSICA_FLUIDSYNTH_SOUNDFONT_SOURCE_URL"),
            "soundfont_source_archive_sha256": os.environ.get("MUSICA_FLUIDSYNTH_SOUNDFONT_SOURCE_SHA256"),
        },
    }

    required = [
        proof["platform_system"] == "Windows",
        proof["input_music_ir_unchanged_after_all_renders"],
        proof["pair_a_verdict"] == "COMPARABLE_OBJECTIVE_ONLY",
        proof["pair_a_comparability"]["status"] == "COMPARABLE",
        proof["claim_boundary"]["human_subject_evidence"] == "NOT_VALIDATED",
        proof["claim_boundary"]["perceptual_superiority"] == "UNKNOWN",
        proof["claim_boundary"]["human_preference_claim_allowed"] is False,
        proof["fluidsynth"]["observed_version"] == FLUIDSYNTH_TARGET_VERSION,
        proof["reference_format"]["sample_rate"] == 22050,
        proof["reference_format"]["channels"] == 1,
        proof["fluidsynth_format"]["sample_rate"] == 48000,
        proof["fluidsynth_format"]["channels"] == 2,
        reference_hash_equal,
        fluidsynth_hash_equal,
        comparison_hash_equal,
        metric_equality,
        all(negatives.values()),
    ]
    if not all(required):
        raise RuntimeError("M5-R4 controlled comparison proof failed")

    proof_path = write_canonical_json(root / "proof.json", proof)
    tracked.append(proof_path)

    for pair in (pair_a, pair_b):
        token = "A" if pair is pair_a else "B"
        pair_root = root / f"pair-{token}"
        for key, value in (
            ("reference-request.json", pair["reference_request"]),
            ("fluidsynth-request.json", pair["fluidsynth_request"]),
            ("reference-result.json", pair["reference_result"]),
            ("fluidsynth-result.json", pair["fluidsynth_result"]),
        ):
            tracked.append(write_canonical_json(pair_root / "records" / key, value))
        tracked.extend(
            [
                pair["reference_qa_path"],
                pair["fluidsynth_qa_path"],
                pair["fluidsynth_provenance_path"],
                pair["reference_wav"],
                pair["fluidsynth_wav"],
            ]
        )

    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M5-R4-Controlled-Paired-Render-Evaluation-v0",
        "source_blueprint": str(Path(blueprint_path).as_posix()),
        "source_binding": source,
        "proof": proof,
        "claim_boundary": [
            "same exact canonical Music IR rendered by both existing adapters",
            "native raw final artifacts preserved without comparison-time resampling or gain matching",
            "objective signal descriptors only",
            "sample-rate and channel-layout differences retained as explicit confounds",
            "paired deltas are descriptive and do not encode preference",
            "human-subject evidence NOT_VALIDATED",
            "perceptual superiority UNKNOWN",
            "not professional/mastering quality",
            "not a universal renderer ranking",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(set(tracked), key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M5-R4 paired audio evidence")
    parser.add_argument("--blueprint", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.blueprint, args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
