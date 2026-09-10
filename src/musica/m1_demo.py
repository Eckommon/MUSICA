"""Generate the canonical MUSICA M1 Creative Core evidence bundle.

공식 MUSICA M1 Creative Core 근거 번들을 생성합니다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .compiler import COMPILER_ID, COMPILER_VERSION, compile_blueprint
from .contracts import validate_contract
from .creative import compose_blueprint
from .evidence import artifact_record, write_canonical_json
from .render import DEFAULT_SAMPLE_RATE, RENDERER_VERSION, render_midi, render_wav
from .semantic import M1_SEMANTIC_AXES, SEMANTIC_MECHANISM_REGISTRY, apply_semantic_control


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_render_bundle(root: Path, prefix: Path, blueprint: dict[str, Any]) -> list[Path]:
    ir = compile_blueprint(blueprint)
    duration = float(blueprint["project"]["duration_seconds"])
    paths = [
        write_canonical_json(root / prefix / "blueprint.json", blueprint),
        write_canonical_json(root / prefix / "music-ir.json", ir),
        render_midi(ir, root / prefix / "preview.mid"),
        render_wav(
            ir,
            root / prefix / "preview.wav",
            duration_seconds=duration,
            sample_rate=DEFAULT_SAMPLE_RATE,
        ),
    ]
    return paths


def run_suite(intent_paths: list[str | Path], out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    artifacts: list[Path] = []
    case_records: list[dict[str, Any]] = []
    canonical_blueprints: dict[str, dict[str, Any]] = {}

    for path in intent_paths:
        intent = _load(path)
        validate_contract(intent, "music-intent-v0.schema.json")
        blueprint = compose_blueprint(intent)
        profile = str(intent["style_profile"])
        canonical_blueprints[profile] = blueprint

        prefix = Path("cases") / profile
        artifacts.append(write_canonical_json(root / prefix / "intent.json", intent))
        artifacts.extend(_write_render_bundle(root, prefix, blueprint))
        case_records.append(
            {
                "intent_id": intent["intent_id"],
                "style_profile": profile,
                "seed": intent["seed"],
                "revision_id": blueprint["project"]["revision_id"],
                "tempo_bpm": blueprint["musical_context"]["tempo"]["bpm"],
                "tonal_center": blueprint["musical_context"]["tonal_center"],
                "mode": blueprint["musical_context"]["mode"],
            }
        )

    if "dark_electronic" not in canonical_blueprints:
        raise ValueError("M1 evidence requires a dark_electronic canonical case for semantic probes")

    parent = canonical_blueprints["dark_electronic"]
    final_section = parent["form"]["sections"][-1]
    scope = f"time:{float(final_section['start']):g}-{float(final_section['end']):g}"
    semantic_records: list[dict[str, Any]] = []

    for ordinal, axis in enumerate(M1_SEMANTIC_AXES, start=1):
        control = {
            "control_id": f"M1-PROBE-{ordinal:02d}-{axis.upper()}",
            "name": axis,
            "operation": "set",
            "value": 0.90,
            "scope": scope,
            "confidence": 1.0,
            "source": "deterministic_transform",
            "phrase": f"M1 deterministic semantic probe: set {axis} to 0.90 in final section.",
            "interpretation_notes": list(SEMANTIC_MECHANISM_REGISTRY[axis]["mechanisms"]),
            "protected_targets": [
                "/musical_context/tempo/bpm",
                "/materials/melody/main_motif_id",
                "/materials/rhythm/drum_pattern_id",
            ],
        }
        candidate, diff = apply_semantic_control(
            parent,
            control,
            revision_id=f"rev-sem-{ordinal:02d}-{axis}",
        )
        prefix = Path("semantic-probes") / axis
        artifacts.append(write_canonical_json(root / prefix / "control.json", control))
        artifacts.append(write_canonical_json(root / prefix / "diff.json", diff))
        artifacts.extend(_write_render_bundle(root, prefix, candidate))
        semantic_records.append(
            {
                "axis": axis,
                "revision_id": candidate["project"]["revision_id"],
                "scope": scope,
                "selected_mechanisms": candidate["provenance"]["selected_mechanisms"],
                "rejected_mechanisms": candidate["provenance"]["rejected_mechanisms"],
            }
        )

    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M1-Creative-Core-v0",
        "compiler": {"id": COMPILER_ID, "version": COMPILER_VERSION},
        "renderers": {
            "midi": {"id": "musica-smf-writer", "version": RENDERER_VERSION},
            "wav": {
                "id": "musica-local-preview-synth",
                "version": RENDERER_VERSION,
                "sample_rate": DEFAULT_SAMPLE_RATE,
                "channels": 1,
                "sample_width_bytes": 2,
            },
        },
        "creative_contract": {
            "input": "music-intent-v0.schema.json",
            "profiles": sorted(canonical_blueprints),
            "semantic_axes": list(M1_SEMANTIC_AXES),
        },
        "cases": sorted(case_records, key=lambda item: item["style_profile"]),
        "semantic_probes": semantic_records,
        "claim_boundary": [
            "bounded deterministic Creative Core v0",
            "not arbitrary free-form language understanding",
            "not universal genre or emotion modeling",
            "not production audio quality",
            "not perceptual melody-identity equivalence",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(artifacts, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M1 Creative Core evidence")
    parser.add_argument("--intents", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.intents, args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
