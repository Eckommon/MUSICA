"""Generate canonical MUSICA M3-R1 AI Music Director boundary evidence.

공식 MUSICA M3-R1 AI Music Director 경계 근거를 생성합니다.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from .compiler import compile_blueprint
from .contracts import ContractError
from .director import (
    DIRECTOR_BOUNDARY_VERSION,
    DirectorError,
    FixtureMusicDirectorProvider,
    build_create_request,
    build_edit_request,
    direct_create,
    direct_edit,
    validate_director_proposal,
)
from .evidence import artifact_record, write_canonical_json
from .project import PROJECT_ENGINE_ID, PROJECT_ENGINE_VERSION, create_project
from .render import DEFAULT_SAMPLE_RATE, render_midi, render_wav


def _write_create_artifacts(root: Path, result: dict[str, Any]) -> list[Path]:
    directory = root / "create"
    blueprint = result["blueprint"]
    ir = compile_blueprint(blueprint)
    paths = [
        write_canonical_json(directory / "provider-capabilities.json", result["provider_capabilities"]),
        write_canonical_json(directory / "proposal.json", result["proposal"]),
        write_canonical_json(directory / "music-intent.json", result["intent"]),
        write_canonical_json(directory / "director-trace.json", result["trace"]),
        write_canonical_json(directory / "blueprint.json", blueprint),
        write_canonical_json(directory / "music-ir.json", ir),
        render_midi(ir, directory / "preview.mid"),
        render_wav(
            ir,
            directory / "preview.wav",
            duration_seconds=float(blueprint["project"]["duration_seconds"]),
            sample_rate=DEFAULT_SAMPLE_RATE,
        ),
    ]
    return paths


def _write_edit_artifacts(root: Path, result: dict[str, Any]) -> list[Path]:
    directory = root / "edit"
    blueprint = result["candidate"]
    ir = compile_blueprint(blueprint)
    paths = [
        write_canonical_json(directory / "provider-capabilities.json", result["provider_capabilities"]),
        write_canonical_json(directory / "proposal.json", result["proposal"]),
        write_canonical_json(directory / "semantic-control.json", result["control"]),
        write_canonical_json(directory / "director-trace.json", result["trace"]),
        write_canonical_json(directory / "blueprint.json", blueprint),
        write_canonical_json(directory / "blueprint-diff.json", result["diff"]),
        write_canonical_json(directory / "music-ir.json", ir),
        render_midi(ir, directory / "preview.mid"),
        render_wav(
            ir,
            directory / "preview.wav",
            duration_seconds=float(blueprint["project"]["duration_seconds"]),
            sample_rate=DEFAULT_SAMPLE_RATE,
        ),
    ]
    return paths


def _negative_proofs(
    provider: FixtureMusicDirectorProvider,
    create_request: dict[str, Any],
    parent: dict[str, Any],
) -> dict[str, Any]:
    capabilities = provider.capabilities()

    injected = provider.propose(copy.deepcopy(create_request))
    injected["canonical_state"] = {"attempt": "provider declares canonical Blueprint"}
    direct_state_injection_blocked = False
    try:
        validate_director_proposal(create_request, injected, capabilities)
    except ContractError:
        direct_state_injection_blocked = True

    hint_violation = provider.propose(copy.deepcopy(create_request))
    hint_violation["payload"]["duration_seconds"] = 30
    explicit_hint_override_blocked = False
    try:
        validate_director_proposal(create_request, hint_violation, capabilities)
    except DirectorError:
        explicit_hint_override_blocked = True

    edit_request = build_edit_request(
        parent,
        request_id="M3-R1-NEGATIVE-STALE",
        user_text="Make the final section more urgent",
    )
    stale = copy.deepcopy(edit_request)
    stale["context"]["blueprint_sha256"] = "0" * 64
    stale_context_blocked = False
    try:
        direct_edit(provider, stale, parent, revision_id="rev-stale-must-not-exist")
    except DirectorError:
        stale_context_blocked = True

    bad_axis_request = build_edit_request(
        parent,
        request_id="M3-R1-NEGATIVE-AXIS",
        user_text="Make the final section more urgent",
    )
    bad_axis = provider.propose(copy.deepcopy(bad_axis_request))
    bad_axis["payload"]["name"] = "roughness"
    unsupported_axis_blocked = False
    try:
        validate_director_proposal(bad_axis_request, bad_axis, capabilities)
    except ContractError:
        unsupported_axis_blocked = True

    result = {
        "direct_canonical_state_injection": (
            "BLOCKED_AS_EXPECTED" if direct_state_injection_blocked else "FAILED_TO_BLOCK"
        ),
        "explicit_user_hint_override": (
            "BLOCKED_AS_EXPECTED" if explicit_hint_override_blocked else "FAILED_TO_BLOCK"
        ),
        "stale_revision_context": (
            "BLOCKED_AS_EXPECTED" if stale_context_blocked else "FAILED_TO_BLOCK"
        ),
        "unsupported_semantic_axis": (
            "BLOCKED_AS_EXPECTED" if unsupported_axis_blocked else "FAILED_TO_BLOCK"
        ),
    }
    if any(value != "BLOCKED_AS_EXPECTED" for value in result.values()):
        raise RuntimeError(f"M3-R1 negative authority proof failed: {result}")
    return result


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    provider = FixtureMusicDirectorProvider()

    create_request = build_create_request(
        request_id="M3-R1-CREATE-001",
        user_text="Create a restrained dark electronic 20-second technology cue",
        locale="en-US",
        duration_seconds=20,
        use_case="advertisement",
        preserve_on_edit=["tempo", "melody_identity", "rhythm_identity"],
        exclusions=["vocals"],
    )
    create_result = direct_create(provider, create_request)
    create_paths = [
        write_canonical_json(root / "create" / "request.json", create_request),
        *_write_create_artifacts(root, create_result),
    ]

    root_blueprint = create_result["blueprint"]
    project_root = root / "canonical-project.musica"
    project = create_project(project_root, root_blueprint)
    root_revision_id = root_blueprint["project"]["revision_id"]
    project.bind_artifacts(root_revision_id, create_paths)
    project.create_branch("ai-variation", from_revision_id=root_revision_id)

    edit_request = build_edit_request(
        root_blueprint,
        request_id="M3-R1-EDIT-001",
        user_text=(
            "Make the final section more urgent but keep tempo, melody and drum identity"
        ),
        locale="en-US",
    )
    edit_result = direct_edit(
        provider,
        edit_request,
        root_blueprint,
        revision_id="rev-m3-ai-edit-001",
    )

    if project.head_revision_id("ai-variation") != root_revision_id:
        raise RuntimeError("provider/director resolution mutated project ref before explicit acceptance")

    project.commit_revision(
        edit_result["candidate"],
        branch="ai-variation",
        actor="ai",
        reason=(
            f"Accepted M3-R1 Director proposal {edit_result['proposal']['proposal_id']} after "
            "typed proposal, semantic, and HARD-lock validation."
        ),
    )
    edit_paths = [
        write_canonical_json(root / "edit" / "request.json", edit_request),
        *_write_edit_artifacts(root, edit_result),
    ]
    project.bind_artifacts(edit_result["candidate"]["project"]["revision_id"], edit_paths)

    negative = _negative_proofs(provider, create_request, root_blueprint)
    negative_path = write_canonical_json(root / "negative-authority-proofs.json", negative)
    verification = project.verify_integrity()
    verification_path = write_canonical_json(root / "project-verification.json", verification)

    branch_state = {
        "main": project.head_revision_id("main"),
        "ai-variation": project.head_revision_id("ai-variation"),
        "expected_main": root_revision_id,
        "expected_ai_variation": edit_result["candidate"]["project"]["revision_id"],
        "current_branch": project.current_branch(),
        "provider_resolution_side_effect_free_before_commit": True,
    }
    branch_path = write_canonical_json(root / "branch-state.json", branch_state)

    project_files = sorted(path for path in project_root.rglob("*") if path.is_file())
    summary_paths = create_paths + edit_paths + [negative_path, verification_path, branch_path]
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M3-R1-AI-Music-Director-Provider-Boundary",
        "director_boundary_version": DIRECTOR_BOUNDARY_VERSION,
        "provider": provider.capabilities(),
        "project_engine": {"id": PROJECT_ENGINE_ID, "version": PROJECT_ENGINE_VERSION},
        "proof": {
            "create_language_to_validated_intent": True,
            "create_intent_to_blueprint": True,
            "root_revision_committed": project.head_revision_id("main") == root_revision_id,
            "edit_language_to_semantic_control": edit_result["control"]["name"] == "tension",
            "edit_candidate_lock_validated": True,
            "ai_variation_committed_only_after_explicit_acceptance": (
                project.head_revision_id("ai-variation")
                == edit_result["candidate"]["project"]["revision_id"]
            ),
            "provider_trace_bound_to_root_revision": True,
            "provider_trace_bound_to_edit_revision": True,
            "project_integrity_status": verification["status"],
            "all_negative_authority_proofs_blocked": all(
                value == "BLOCKED_AS_EXPECTED" for value in negative.values()
            ),
        },
        "claim_boundary": [
            "provider-neutral typed proposal boundary, not live external LLM execution",
            "fixture provider is a bounded deterministic test double, not general language intelligence",
            "providers are non-authoritative and cannot directly mutate canonical Blueprint or Project Bundle state",
            "external LLM output is not claimed deterministic; M3-R2 will preserve provider/request/response provenance",
            "M0/M1/M2 deterministic and integrity guarantees remain downstream authority",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(
                summary_paths + project_files,
                key=lambda item: item.relative_to(root).as_posix(),
            )
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate MUSICA M3-R1 AI Music Director provider-boundary evidence"
    )
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
