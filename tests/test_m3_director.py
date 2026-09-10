from __future__ import annotations

import copy
import hashlib

import pytest

from musica.contracts import ContractError, get_pointer, validate_contract
from musica.director import (
    DirectorError,
    FixtureMusicDirectorProvider,
    build_create_request,
    build_edit_request,
    direct_create,
    direct_edit,
    request_provider_proposal,
)
from musica.evidence import canonical_json_bytes
from musica.project import create_project


def digest(value) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def create_request():
    return build_create_request(
        request_id="M3-R1-CREATE-001",
        user_text="Create a restrained dark electronic 20-second technology cue",
        locale="en-US",
        duration_seconds=20,
        use_case="advertisement",
        preserve_on_edit=["tempo", "melody_identity", "rhythm_identity"],
        exclusions=["vocals"],
    )


def created():
    provider = FixtureMusicDirectorProvider()
    request = create_request()
    return provider, request, direct_create(provider, request)


def edit_request(parent):
    return build_edit_request(
        parent,
        request_id="M3-R1-EDIT-001",
        user_text=(
            "Make the final section more urgent but keep tempo, melody and drum identity"
        ),
        locale="en-US",
    )


def test_create_request_and_proposal_are_machine_valid_and_deterministic():
    provider = FixtureMusicDirectorProvider()
    request = create_request()
    validate_contract(request, "director-request-v0.schema.json")
    validate_contract(provider.capabilities(), "director-provider-v0.schema.json")

    first = direct_create(provider, request)
    second = direct_create(provider, copy.deepcopy(request))

    assert first == second
    validate_contract(first["proposal"], "director-proposal-v0.schema.json")
    validate_contract(first["trace"], "director-trace-v0.schema.json")
    validate_contract(first["intent"], "music-intent-v0.schema.json")
    validate_contract(first["blueprint"], "music-blueprint-v0.schema.json")
    assert first["intent"]["provenance"]["actor"] == "ai"
    assert first["intent"]["duration_seconds"] == 20
    assert first["intent"]["use_case"] == "advertisement"
    assert first["intent"]["style_profile"] == "dark_electronic"
    assert first["intent"]["preserve_on_edit"] == [
        "tempo",
        "melody_identity",
        "rhythm_identity",
    ]
    assert first["intent"]["exclusions"] == ["vocals"]


def test_trace_hashes_bind_exact_request_proposal_capabilities_and_lowered_contract():
    provider, request, result = created()
    trace = result["trace"]
    assert trace["request_sha256"] == digest(request)
    assert trace["proposal_sha256"] == digest(result["proposal"])
    assert trace["provider_capabilities_sha256"] == digest(provider.capabilities())
    assert trace["accepted_contract_sha256"] == digest(result["intent"])
    assert trace["accepted_contract_kind"] == "music_intent_v0"
    assert trace["authority_status"] == "PROPOSAL_ONLY_MUSICA_CORE_ACCEPTED"


def test_provider_cannot_override_explicit_user_hint():
    class HintViolatingProvider(FixtureMusicDirectorProvider):
        def propose(self, request):
            proposal = super().propose(request)
            proposal["payload"]["duration_seconds"] = 30
            return proposal

    with pytest.raises(DirectorError, match="explicit user hint duration_seconds"):
        request_provider_proposal(HintViolatingProvider(), create_request())


def test_provider_identity_must_match_declared_capabilities():
    class IdentitySpoofingProvider(FixtureMusicDirectorProvider):
        def propose(self, request):
            proposal = super().propose(request)
            proposal["provider"]["model_id"] = "unreported-model"
            return proposal

    with pytest.raises(DirectorError, match="provider metadata mismatch"):
        request_provider_proposal(IdentitySpoofingProvider(), create_request())


def test_provider_cannot_inject_blueprint_or_patch_fields():
    class BlueprintInjectingProvider(FixtureMusicDirectorProvider):
        def propose(self, request):
            proposal = super().propose(request)
            proposal["blueprint"] = {"attempt": "direct canonical mutation"}
            return proposal

    class PatchInjectingProvider(FixtureMusicDirectorProvider):
        def propose(self, request):
            proposal = super().propose(request)
            proposal["payload"]["patch"] = [
                {"path": "/musical_context/tempo/bpm", "value": 200}
            ]
            return proposal

    with pytest.raises(ContractError, match="schema validation failed"):
        request_provider_proposal(BlueprintInjectingProvider(), create_request())
    with pytest.raises(ContractError, match="schema validation failed"):
        request_provider_proposal(PatchInjectingProvider(), create_request())


def test_provider_receives_defensive_request_copy():
    class MutatingInputProvider(FixtureMusicDirectorProvider):
        def propose(self, request):
            request["user_text"] = "Create a dark electronic 20-second technology cue"
            return super().propose(request)

    request = create_request()
    original = copy.deepcopy(request)
    request_provider_proposal(MutatingInputProvider(), request)
    assert request == original


def test_edit_request_is_bound_to_exact_blueprint_snapshot():
    provider, _, result = created()
    parent = result["blueprint"]
    request = edit_request(parent)
    assert request["context"]["revision_id"] == parent["project"]["revision_id"]
    assert request["context"]["blueprint_sha256"] == digest(parent)

    stale = copy.deepcopy(request)
    stale["context"]["blueprint_sha256"] = "0" * 64
    with pytest.raises(DirectorError, match="does not match the exact supplied Blueprint"):
        direct_edit(provider, stale, parent, revision_id="rev-stale-blocked")


def test_unsupported_semantic_axis_is_rejected_before_resolution():
    provider, _, result = created()
    parent = result["blueprint"]
    request = edit_request(parent)

    class UnsupportedAxisProvider(FixtureMusicDirectorProvider):
        def propose(self, request):
            proposal = super().propose(request)
            proposal["payload"]["name"] = "roughness"
            return proposal

    with pytest.raises(ContractError, match="schema validation failed"):
        direct_edit(
            UnsupportedAxisProvider(),
            request,
            parent,
            revision_id="rev-roughness-blocked",
        )


def test_provider_may_not_use_capability_it_did_not_declare():
    provider, _, result = created()
    parent = result["blueprint"]
    request = edit_request(parent)

    class UnderdeclaredProvider(FixtureMusicDirectorProvider):
        def capabilities(self):
            capabilities = super().capabilities()
            capabilities["supported_semantic_axes"] = [
                axis
                for axis in capabilities["supported_semantic_axes"]
                if axis != "tension"
            ]
            return capabilities

    with pytest.raises(DirectorError, match="does not declare semantic support"):
        direct_edit(
            UnderdeclaredProvider(),
            request,
            parent,
            revision_id="rev-underdeclared-blocked",
        )


def test_edit_is_side_effect_free_until_explicit_project_commit_and_preserves_hard_locks(tmp_path):
    provider, _, result = created()
    parent = result["blueprint"]
    project = create_project(tmp_path / "director-project.musica", parent)
    root_revision = parent["project"]["revision_id"]
    project.create_branch("ai-variation", from_revision_id=root_revision)

    request = edit_request(parent)
    edit = direct_edit(
        provider,
        request,
        parent,
        revision_id="rev-m3-ai-edit-001",
    )

    # Provider/director resolution is pure with respect to Project Bundle refs.
    assert project.head_revision_id("main") == root_revision
    assert project.head_revision_id("ai-variation") == root_revision

    protected = [
        "/musical_context/tempo/bpm",
        "/materials/melody/main_motif_id",
        "/materials/rhythm/drum_pattern_id",
    ]
    for pointer in protected:
        assert get_pointer(parent, pointer) == get_pointer(edit["candidate"], pointer)

    changed_paths = {item["path"] for item in edit["diff"]}
    assert not (set(protected) & changed_paths)
    assert any("section_overrides" in path for path in changed_paths)
    assert edit["control"]["name"] == "tension"
    assert edit["trace"]["accepted_contract_kind"] == "semantic_control_v0"
    assert edit["trace"]["accepted_contract_sha256"] == digest(edit["control"])

    record = project.commit_revision(
        edit["candidate"],
        branch="ai-variation",
        actor="ai",
        reason=(
            f"Accepted M3 Director proposal {edit['proposal']['proposal_id']} after "
            "trusted semantic and HARD-lock validation."
        ),
    )
    assert record["actor"] == "ai"
    assert project.head_revision_id("main") == root_revision
    assert project.head_revision_id("ai-variation") == "rev-m3-ai-edit-001"
    assert project.verify_integrity()["status"] == "PASS"


def test_malicious_edit_proposal_cannot_advance_project_ref(tmp_path):
    provider, _, result = created()
    parent = result["blueprint"]
    project = create_project(tmp_path / "malicious-project.musica", parent)
    root_revision = parent["project"]["revision_id"]
    project.create_branch("blocked-ai", from_revision_id=root_revision)
    request = edit_request(parent)

    class MaliciousEditProvider(FixtureMusicDirectorProvider):
        def propose(self, request):
            proposal = super().propose(request)
            proposal["payload"]["patch"] = [
                {"path": "/materials/melody/main_motif_id", "value": "forged"}
            ]
            return proposal

    with pytest.raises(ContractError, match="schema validation failed"):
        direct_edit(
            MaliciousEditProvider(),
            request,
            parent,
            revision_id="rev-malicious-blocked",
        )
    assert project.head_revision_id("blocked-ai") == root_revision
    assert project.head_revision_id("main") == root_revision
