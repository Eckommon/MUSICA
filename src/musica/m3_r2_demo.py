"""Generate canonical M3-R2 OpenAI adapter-contract evidence without network or secrets.

This evidence proves the adapter contract and authority boundary only. It MUST NOT be
represented as a live OpenAI provider execution.
"""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

from .compiler import compile_blueprint
from .contracts import validate_contract
from .director import build_create_request, build_edit_request, direct_create, direct_edit
from .evidence import artifact_record, write_canonical_json
from .openai_provider import (
    OpenAIAdapterError,
    OpenAITransportHTTPError,
    OpenAITransportTimeout,
    OpenAIMusicDirectorProvider,
)
from .project import create_project
from .render import DEFAULT_SAMPLE_RATE, render_midi, render_wav


class CanonicalInjectedTransport:
    network_used = False
    requires_api_key = False

    def __init__(self, responses: list[Any]):
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def send(self, endpoint, payload, *, api_key, timeout_seconds):
        self.calls.append(
            {
                "endpoint": endpoint,
                "payload": copy.deepcopy(payload),
                "api_key_was_none": api_key is None,
                "timeout_seconds": timeout_seconds,
            }
        )
        if not self.responses:
            raise RuntimeError("canonical injected transport exhausted")
        value = self.responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return copy.deepcopy(value)


def _create_body() -> dict[str, Any]:
    return {
        "interpretation": {
            "summary": "Restrained dark electronic technology cue with controlled forward pressure.",
            "confidence": 0.91,
            "assumptions": ["Instrumental cue; no vocal lead."],
            "alternatives": ["A warmer ambient treatment could reduce tension."],
        },
        "title": "Controlled Signal",
        "duration_seconds": 24,
        "use_case": "score",
        "style_profile": "warm_ambient",
        "semantic_targets": {
            "energy": 0.58,
            "tension": 0.63,
            "density": 0.46,
            "motion": 0.55,
            "brightness": 0.42,
            "warmth": 0.38,
        },
        "tempo": {"bpm": 108, "min_bpm": 96, "max_bpm": 118},
        "tonal": {"center": "D", "mode": "minor"},
    }


def _edit_body() -> dict[str, Any]:
    return {
        "interpretation": {
            "summary": "Increase urgency in the final section while preserving protected identity.",
            "confidence": 0.94,
            "assumptions": ["Urgency maps primarily to tension for this bounded edit."],
            "alternatives": ["Increase motion instead if rhythmic drive is preferred."],
        },
        "name": "tension",
        "operation": "increase",
        "value": 0.18,
        "scope_kind": "final_section",
        "section_id": None,
        "interpretation_notes": ["Prefer harmonic/support pressure over identity change."],
    }


def _response(body: dict[str, Any], response_id: str) -> dict[str, Any]:
    return {
        "id": response_id,
        "object": "response",
        "status": "completed",
        "model": "gpt-5.6-sol-offline-fixture",
        "error": None,
        "incomplete_details": None,
        "output": [
            {
                "id": "msg-" + response_id,
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps(body, ensure_ascii=False, separators=(",", ":")),
                        "annotations": [],
                    }
                ],
            }
        ],
        "usage": {"input_tokens": 321, "output_tokens": 144, "total_tokens": 465},
    }


def _failure_case(name: str, transport: CanonicalInjectedTransport, request: dict[str, Any]) -> dict[str, Any]:
    provider = OpenAIMusicDirectorProvider(
        transport=transport,
        max_attempts=1,
        sleeper=lambda _: None,
    )
    try:
        direct_create(provider, request)
    except OpenAIAdapterError as exc:
        failure = provider.last_failure()
        if failure is None:
            raise RuntimeError(f"{name}: adapter failed without failure provenance") from exc
        validate_contract(failure, "openai-adapter-failure-v0.schema.json")
        return {"case": name, "status": "BLOCKED_AS_EXPECTED", "classification": exc.classification, "failure": failure}
    raise RuntimeError(f"{name}: invalid provider exchange was not blocked")


def run_suite(out_dir: str | Path) -> dict[str, Any]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    create_request = build_create_request(
        request_id="M3-R2-CREATE-001",
        user_text="Create a restrained dark electronic 20-second technology advertisement cue",
        locale="en-US",
        duration_seconds=20,
        use_case="advertisement",
        style_profile="dark_electronic",
        preserve_on_edit=["tempo", "melody_identity", "rhythm_identity"],
        exclusions=["vocals"],
    )
    create_raw = _response(_create_body(), "resp_m3_r2_create_fixture")
    transport = CanonicalInjectedTransport([create_raw, _response(_edit_body(), "resp_m3_r2_edit_fixture")])
    provider = OpenAIMusicDirectorProvider(
        transport=transport,
        timeout_seconds=45,
        max_attempts=2,
        sleeper=lambda _: None,
    )

    created = direct_create(provider, create_request)
    create_exchange = provider.last_exchange()
    if create_exchange is None or create_exchange["evidence_class"] != "ADAPTER_CONTRACT_EVIDENCE":
        raise RuntimeError("M3-R2 evidence class must be ADAPTER_CONTRACT_EVIDENCE")
    if create_exchange["network_used"] or not transport.calls[0]["api_key_was_none"]:
        raise RuntimeError("M3-R2 canonical evidence unexpectedly used network or credentials")

    project = create_project(root / "canonical-openai-adapter-project.musica", created["blueprint"])
    root_revision = created["blueprint"]["project"]["revision_id"]
    project.create_branch("openai-variation", from_revision_id=root_revision)

    edit_request = build_edit_request(
        created["blueprint"],
        request_id="M3-R2-EDIT-001",
        user_text="Make the final section more urgent but keep tempo, melody and drum identity",
        locale="en-US",
    )
    edited = direct_edit(
        provider,
        edit_request,
        created["blueprint"],
        revision_id="rev-m3-r2-openai-edit-001",
    )
    edit_exchange = provider.last_exchange()
    if edit_exchange is None or edit_exchange["evidence_class"] != "ADAPTER_CONTRACT_EVIDENCE":
        raise RuntimeError("M3-R2 edit exchange lost adapter-contract evidence classification")

    # Director resolution must remain side-effect free until explicit Project Engine commit.
    if project.head_revision_id("openai-variation") != root_revision:
        raise RuntimeError("provider/director resolution mutated project ref before explicit commit")
    project.commit_revision(
        edited["candidate"],
        branch="openai-variation",
        actor="ai",
        reason="Accept M3-R2 offline OpenAI-adapter proposal after trusted M3-R1 validation.",
    )

    with tempfile.TemporaryDirectory() as temp_name:
        temp = Path(temp_name)
        ir = compile_blueprint(edited["candidate"])
        midi = render_midi(ir, temp / "openai-variation.mid")
        wav = render_wav(
            ir,
            temp / "openai-variation.wav",
            duration_seconds=float(edited["candidate"]["project"]["duration_seconds"]),
            sample_rate=DEFAULT_SAMPLE_RATE,
        )
        artifact_binding = project.bind_artifacts(edited["candidate"]["project"]["revision_id"], [midi, wav])

    verification = project.verify_integrity()

    # Negative authority/output proofs.
    poisoned = _create_body()
    poisoned["blueprint"] = {"attempt": "canonical overwrite"}
    poisoned_result = _failure_case(
        "model_blueprint_injection",
        CanonicalInjectedTransport([_response(poisoned, "resp_poisoned")]),
        create_request,
    )

    refusal = _response(_create_body(), "resp_refusal")
    refusal["output"][0]["content"] = [{"type": "refusal", "refusal": "fixture refusal"}]
    refusal_result = _failure_case(
        "model_refusal",
        CanonicalInjectedTransport([refusal]),
        create_request,
    )

    incomplete = _response(_create_body(), "resp_incomplete")
    incomplete["status"] = "incomplete"
    incomplete["incomplete_details"] = {"reason": "max_output_tokens"}
    incomplete["output"] = []
    incomplete_result = _failure_case(
        "incomplete_response",
        CanonicalInjectedTransport([incomplete]),
        create_request,
    )

    rate_limit_result = _failure_case(
        "rate_limit",
        CanonicalInjectedTransport([
            OpenAITransportHTTPError(429, {"error": {"message": "fixture rate limit"}})
        ]),
        create_request,
    )

    timeout_result = _failure_case(
        "timeout",
        CanonicalInjectedTransport([OpenAITransportTimeout("fixture timeout")]),
        create_request,
    )
    negative = [poisoned_result, refusal_result, incomplete_result, rate_limit_result, timeout_result]

    files = [
        write_canonical_json(root / "create-request.json", create_request),
        write_canonical_json(root / "create-provider-payload.json", transport.calls[0]["payload"]),
        write_canonical_json(root / "create-raw-offline-response.json", create_raw),
        write_canonical_json(root / "create-proposal.json", created["proposal"]),
        write_canonical_json(root / "create-director-trace.json", created["trace"]),
        write_canonical_json(root / "create-exchange.json", create_exchange),
        write_canonical_json(root / "edit-request.json", edit_request),
        write_canonical_json(root / "edit-provider-payload.json", transport.calls[1]["payload"]),
        write_canonical_json(root / "edit-proposal.json", edited["proposal"]),
        write_canonical_json(root / "edit-control.json", edited["control"]),
        write_canonical_json(root / "edit-diff.json", edited["diff"]),
        write_canonical_json(root / "edit-director-trace.json", edited["trace"]),
        write_canonical_json(root / "edit-exchange.json", edit_exchange),
        write_canonical_json(root / "artifact-binding.json", artifact_binding),
        write_canonical_json(root / "project-verification.json", verification),
        write_canonical_json(root / "negative-cases.json", negative),
    ]

    project_files = sorted(
        path for path in (root / "canonical-openai-adapter-project.musica").rglob("*") if path.is_file()
    )
    manifest = {
        "manifest_version": "0",
        "evidence_scope": "M3-R2-OpenAI-Provider-Adapter-v0",
        "evidence_class": "ADAPTER_CONTRACT_EVIDENCE",
        "live_openai_call_performed": False,
        "network_used": False,
        "secret_used": False,
        "proof": {
            "create_openai_body_lowered_through_m3_r1": True,
            "explicit_user_hints_preserved": (
                created["intent"]["duration_seconds"] == 20
                and created["intent"]["use_case"] == "advertisement"
                and created["intent"]["style_profile"] == "dark_electronic"
            ),
            "project_ref_unchanged_before_explicit_commit": True,
            "edit_committed_after_trusted_validation": project.head_revision_id("openai-variation") == "rev-m3-r2-openai-edit-001",
            "project_integrity_status": verification["status"],
            "negative_cases_blocked": all(item["status"] == "BLOCKED_AS_EXPECTED" for item in negative),
            "negative_classifications": {item["case"]: item["classification"] for item in negative},
            "artifact_binding_count": len(artifact_binding["artifacts"]),
        },
        "claim_boundary": [
            "This is offline adapter-contract evidence, not a live OpenAI execution.",
            "No API key, Authorization header, or secret is stored in the evidence bundle.",
            "External model output is probabilistic; downstream accepted state remains contract validated.",
            "Production audio quality, universal language understanding, and model determinism are not claimed.",
        ],
        "artifacts": [
            artifact_record(path, root)
            for path in sorted(files + project_files, key=lambda item: item.relative_to(root).as_posix())
        ],
    }
    write_canonical_json(root / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate MUSICA M3-R2 offline OpenAI adapter evidence")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    manifest = run_suite(args.out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
