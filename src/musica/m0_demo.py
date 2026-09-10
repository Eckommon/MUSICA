"""Generate the canonical MUSICA M0-R2 evidence bundle.

공식 MUSICA M0-R2 근거 번들을 생성합니다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .compiler import COMPILER_ID, COMPILER_VERSION, compile_blueprint
from .contracts import validate_contract
from .evidence import artifact_record, write_canonical_json
from .render import DEFAULT_SAMPLE_RATE, RENDERER_VERSION, render_midi, render_wav
from .semantic import apply_semantic_control


def _load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_demo(blueprint_path: str | Path, control_path: str | Path, out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    parent = _load(blueprint_path)
    control = _load(control_path)
    validate_contract(parent, "music-blueprint-v0.schema.json")
    validate_contract(control, "semantic-control-v0.schema.json")

    candidate, diff = apply_semantic_control(parent, control, revision_id="rev-002")
    parent_ir = compile_blueprint(parent)
    candidate_ir = compile_blueprint(candidate)

    paths = [
        write_canonical_json(root / "blueprint-r1.json", parent),
        write_canonical_json(root / "semantic-control.json", control),
        write_canonical_json(root / "blueprint-r2.json", candidate),
        write_canonical_json(root / "blueprint-diff.json", diff),
        write_canonical_json(root / "music-ir-r1.json", parent_ir),
        write_canonical_json(root / "music-ir-r2.json", candidate_ir),
        render_midi(parent_ir, root / "preview-r1.mid"),
        render_midi(candidate_ir, root / "preview-r2.mid"),
        render_wav(
            parent_ir,
            root / "preview-r1.wav",
            duration_seconds=float(parent["project"]["duration_seconds"]),
            sample_rate=DEFAULT_SAMPLE_RATE,
        ),
        render_wav(
            candidate_ir,
            root / "preview-r2.wav",
            duration_seconds=float(candidate["project"]["duration_seconds"]),
            sample_rate=DEFAULT_SAMPLE_RATE,
        ),
    ]

    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M0-R2-minimal-deterministic-music-loop",
        "project_id": parent["project"]["project_id"],
        "parent_revision": parent["project"]["revision_id"],
        "candidate_revision": candidate["project"]["revision_id"],
        "semantic_control_id": control["control_id"],
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
        "runtime_claim_boundary": [
            "deterministic M0 contract demo only",
            "not production audio quality",
            "not general semantic music intelligence",
            "not perceptual melody-identity validation",
        ],
        "artifacts": [artifact_record(path, root) for path in sorted(paths, key=lambda item: item.name)],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M0-R2 deterministic evidence bundle")
    parser.add_argument("--blueprint", required=True)
    parser.add_argument("--control", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_demo(args.blueprint, args.control, args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
