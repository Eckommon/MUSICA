"""Generate deterministic non-browser evidence for accepted-revision A/B Compare v0."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .contracts import validate_contract
from .diff import structured_diff
from .evidence import artifact_record, write_canonical_json
from .project import create_project
from .studio import StudioService
from .studio_compare import StudioRevisionCompareSurface

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "examples" / "blueprints" / "valid" / "dark-electronic-20s-r1.json"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _key_set(value: Any) -> set[str]:
    if isinstance(value, dict):
        result = {str(key) for key in value}
        for child in value.values():
            result |= _key_set(child)
        return result
    if isinstance(value, list):
        result: set[str] = set()
        for child in value:
            result |= _key_set(child)
        return result
    return set()


def _blueprint() -> dict[str, Any]:
    value = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))
    value["project"]["project_id"] = "PRJ-POST-M7-COMPARE-DEMO"
    value["project"]["revision_id"] = "rev-post-m7-compare-demo-r1"
    value["project"]["parent_revision_id"] = None
    validate_contract(value, "music-blueprint-v0.schema.json")
    return value


def run_demo(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    workspace = root / "workspace"
    workspace.mkdir()

    project = create_project(workspace / "compare-demo.musica", _blueprint())
    revision_a = project.head_revision_id()
    service = StudioService(workspace)
    service.open_project_session(
        project_slug="compare-demo",
        session_id="compare-demo-session",
        provider_mode="fixture",
    )
    preview = service.preview_semantic_edit(
        "compare-demo-session",
        name="tension",
        operation="increase",
        value=0.18,
        scope_kind="final_section",
    )
    revision_b = str(preview["preview"]["candidate_revision_id"])
    service.accept_preview("compare-demo-session")

    session = service._get_session("compare-demo-session")
    surface = StudioRevisionCompareSurface(service)
    head_before = session.project.head_revision_id()
    forward = surface.compare_view(
        "compare-demo-session",
        revision_a=revision_a,
        revision_b=revision_b,
    )
    reverse = surface.compare_view(
        "compare-demo-session",
        revision_a=revision_b,
        revision_b=revision_a,
    )
    identity = surface.compare_view(
        "compare-demo-session",
        revision_a=revision_a,
        revision_b=revision_a,
    )
    validate_contract(forward, "studio-revision-compare-v0.schema.json")
    validate_contract(reverse, "studio-revision-compare-v0.schema.json")
    validate_contract(identity, "studio-revision-compare-v0.schema.json")

    a_wav = surface.media_bytes("compare-demo-session", revision_id=revision_a, kind="audio")
    a_midi = surface.media_bytes("compare-demo-session", revision_id=revision_a, kind="midi")
    b_wav = surface.media_bytes("compare-demo-session", revision_id=revision_b, kind="audio")
    b_midi = surface.media_bytes("compare-demo-session", revision_id=revision_b, kind="midi")
    (root / "revision-a.wav").write_bytes(a_wav)
    (root / "revision-a.mid").write_bytes(a_midi)
    (root / "revision-b.wav").write_bytes(b_wav)
    (root / "revision-b.mid").write_bytes(b_midi)

    expected_forward = structured_diff(
        session.project.read_revision(revision_a),
        session.project.read_revision(revision_b),
    )
    expected_reverse = structured_diff(
        session.project.read_revision(revision_b),
        session.project.read_revision(revision_a),
    )
    forbidden_keys = {"winner", "score", "better", "preference_probability"}
    present_forbidden = sorted(forbidden_keys & _key_set(forward))
    head_after = session.project.head_revision_id()

    proof = {
        "proof_version": "0",
        "revision_a": revision_a,
        "revision_b": revision_b,
        "mixed_provenance_truthful": forward["revision_a"]["media"]["wav"]["source"] == "deterministic_fallback" and forward["revision_b"]["media"]["wav"]["source"] == "bound_artifact",
        "forward_diff_exact": forward["diff"] == expected_forward,
        "reverse_diff_exact": reverse["diff"] == expected_reverse,
        "identity_zero_diff": identity["diff"] == [],
        "identity_wav_equal": identity["revision_a"]["media"]["wav"]["sha256"] == identity["revision_b"]["media"]["wav"]["sha256"],
        "identity_midi_equal": identity["revision_a"]["media"]["midi"]["sha256"] == identity["revision_b"]["media"]["midi"]["sha256"],
        "revision_a_wav_exact": _sha(a_wav) == forward["revision_a"]["media"]["wav"]["sha256"],
        "revision_a_midi_exact": _sha(a_midi) == forward["revision_a"]["media"]["midi"]["sha256"],
        "revision_b_wav_exact": _sha(b_wav) == forward["revision_b"]["media"]["wav"]["sha256"],
        "revision_b_midi_exact": _sha(b_midi) == forward["revision_b"]["media"]["midi"]["sha256"],
        "head_unchanged": head_before == head_after == revision_b,
        "forbidden_creative_verdict_keys": present_forbidden,
        "canonical": forward["authority"]["canonical"],
        "browser_mutation_authorized": forward["authority"]["browser_mutation_authorized"],
        "project_mutation_authorized": forward["authority"]["project_mutation_authorized"],
        "reverse_promotion_authorized": forward["authority"]["reverse_promotion_authorized"],
        "creative_ranking_authorized": forward["authority"]["creative_ranking_authorized"],
        "implicit_accept_authorized": forward["authority"]["implicit_accept_authorized"],
    }
    required_true = [
        "mixed_provenance_truthful",
        "forward_diff_exact",
        "reverse_diff_exact",
        "identity_zero_diff",
        "identity_wav_equal",
        "identity_midi_equal",
        "revision_a_wav_exact",
        "revision_a_midi_exact",
        "revision_b_wav_exact",
        "revision_b_midi_exact",
        "head_unchanged",
    ]
    required_false = [
        "canonical",
        "browser_mutation_authorized",
        "project_mutation_authorized",
        "reverse_promotion_authorized",
        "creative_ranking_authorized",
        "implicit_accept_authorized",
    ]
    failed_true = [key for key in required_true if proof[key] is not True]
    failed_false = [key for key in required_false if proof[key] is not False]
    if failed_true or failed_false or present_forbidden:
        raise RuntimeError(
            "Accepted revision Compare deterministic proof failed: "
            f"true={failed_true}, false={failed_false}, forbidden={present_forbidden}"
        )

    write_canonical_json(root / "forward.json", forward)
    write_canonical_json(root / "reverse.json", reverse)
    write_canonical_json(root / "identity.json", identity)
    write_canonical_json(root / "proof.json", proof)

    service.close_session("compare-demo-session")
    if workspace.exists():
        shutil.rmtree(workspace)

    evidence_files = sorted(path for path in root.iterdir() if path.is_file())
    manifest = {
        "manifest_version": "0",
        "milestone": "POST-M7-REVISION-COMPARE-V0",
        "evidence_class": "DETERMINISTIC_ACCEPTED_REVISION_COMPARE_EVIDENCE",
        "revision_a": revision_a,
        "revision_b": revision_b,
        "revision_a_wav_sha256": _sha(a_wav),
        "revision_a_midi_sha256": _sha(a_midi),
        "revision_b_wav_sha256": _sha(b_wav),
        "revision_b_midi_sha256": _sha(b_midi),
        "records": [artifact_record(path, root) for path in evidence_files],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return {**manifest, "proof": proof}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    run_demo(args.out)


if __name__ == "__main__":
    main()
