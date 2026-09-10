from __future__ import annotations

import copy
import hashlib
import json

import pytest

from musica.contracts import ContractError, get_pointer, validate_contract
from musica.director import (
    FixtureMusicDirectorProvider,
    build_create_request,
    build_edit_request,
    direct_create,
    direct_edit,
)
from musica.evidence import canonical_json_bytes
from musica.openai_provider import (
    DEFAULT_OPENAI_MODEL,
    OPENAI_RESPONSES_ENDPOINT,
    OpenAIAdapterError,
    OpenAITransportHTTPError,
    OpenAITransportTimeout,
    OpenAIMusicDirectorProvider,
    build_openai_response_payload,
)


def digest(value) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def create_body(**overrides):
    body = {
        "interpretation": {
            "summary": "Restrained dark electronic technology cue with controlled forward pressure.",
            "confidence": 0.91,
            "assumptions": ["Instrumental cue; no vocal lead."],
            "alternatives": ["A warmer ambient interpretation could reduce tension."],
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
    body.update(overrides)
    return body


def edit_body(**overrides):
    body = {
        "interpretation": {
            "summary": "Increase urgency in the final section without changing protected identity.",
            "confidence": 0.94,
            "assumptions": ["Urgency maps primarily to tension in this bounded request."],
            "alternatives": ["Motion could be raised instead if rhythmic drive is preferred."],
        },
        "name": "tension",
        "operation": "increase",
        "value": 0.18,
        "scope_kind": "final_section",
        "section_id": None,
        "interpretation_notes": ["Prefer harmonic/support pressure over identity changes."],
    }
    body.update(overrides)
    return body


def response_for(body, *, response_id="resp_fixture_001", status="completed", model="gpt-5.6-sol-snapshot"):
    return {
        "id": response_id,
        "object": "response",
        "status": status,
        "model": model,
        "error": None,
        "incomplete_details": None,
        "output": [
            {
                "id": "msg_fixture_001",
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


class InjectedTransport:
    network_used = False
    requires_api_key = False

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def send(self, endpoint, payload, *, api_key, timeout_seconds):
        self.calls.append(
            {
                "endpoint": endpoint,
                "payload": copy.deepcopy(payload),
                "api_key": api_key,
                "timeout_seconds": timeout_seconds,
            }
        )
        if not self.responses:
            raise AssertionError("fixture transport exhausted")
        value = self.responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return copy.deepcopy(value)


def create_request():
    return build_create_request(
        request_id="M3-R2-CREATE-001",
        user_text="Create a restrained dark electronic 20-second technology advertisement cue",
        locale="en-US",
        duration_seconds=20,
        use_case="advertisement",
        style_profile="dark_electronic",
        preserve_on_edit=["tempo", "melody_identity", "rhythm_identity"],
        exclusions=["vocals"],
    )


def parent_blueprint():
    fixture = FixtureMusicDirectorProvider()
    return direct_create(fixture, create_request())["blueprint"]


def test_payload_uses_responses_strict_json_schema_and_contains_no_secret():
    request = create_request()
    payload = build_openai_response_payload(request, DEFAULT_OPENAI_MODEL)
    assert payload["model"] == "gpt-5.6-sol"
    assert payload["store"] is False
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["strict"] is True
    assert payload["text"]["format"]["name"] == "musica_director_create_v0"
    assert payload["text"]["format"]["schema"]["additionalProperties"] is False
    serialized = canonical_json_bytes(payload)
    assert b"OPENAI_API_KEY" not in serialized
    assert b"Authorization" not in serialized
    assert b"MusicaProject" not in serialized


def test_create_adapter_preserves_explicit_user_authority_and_records_contract_evidence():
    transport = InjectedTransport([response_for(create_body())])
    provider = OpenAIMusicDirectorProvider(transport=transport, sleeper=lambda _: None)
    request = create_request()
    result = direct_create(provider, request)

    assert result["intent"]["duration_seconds"] == 20
    assert result["intent"]["use_case"] == "advertisement"
    assert result["intent"]["style_profile"] == "dark_electronic"
    assert result["intent"]["preserve_on_edit"] == ["tempo", "melody_identity", "rhythm_identity"]
    assert result["intent"]["exclusions"] == ["vocals"]
    assert result["intent"]["seed"] == result["blueprint"]["project"]["seed"]

    exchange = provider.last_exchange()
    assert exchange is not None
    validate_contract(exchange, "openai-adapter-exchange-v0.schema.json")
    assert exchange["evidence_class"] == "ADAPTER_CONTRACT_EVIDENCE"
    assert exchange["network_used"] is False
    assert exchange["credential_source"] == "injected-no-secret"
    assert exchange["secret_recorded"] is False
    assert exchange["attempt_count"] == 1
    assert exchange["request_payload_sha256"] == digest(transport.calls[0]["payload"])
    assert exchange["director_proposal_sha256"] == digest(result["proposal"])
    assert provider.last_failure() is None


def test_same_semantic_request_gets_stable_downstream_seed_even_when_request_id_changes():
    first_request = create_request()
    second_request = copy.deepcopy(first_request)
    second_request["request_id"] = "M3-R2-CREATE-002"
    first_provider = OpenAIMusicDirectorProvider(
        transport=InjectedTransport([response_for(create_body(), response_id="resp_a")]),
        sleeper=lambda _: None,
    )
    second_provider = OpenAIMusicDirectorProvider(
        transport=InjectedTransport([response_for(create_body(), response_id="resp_b")]),
        sleeper=lambda _: None,
    )
    first = direct_create(first_provider, first_request)
    second = direct_create(second_provider, second_request)
    assert first["intent"]["seed"] == second["intent"]["seed"]


def test_edit_adapter_resolves_final_section_and_injects_exact_hard_lock_targets():
    parent = parent_blueprint()
    request = build_edit_request(
        parent,
        request_id="M3-R2-EDIT-001",
        user_text="Make the final section more urgent but keep tempo, melody and drum identity",
    )
    provider = OpenAIMusicDirectorProvider(
        transport=InjectedTransport([response_for(edit_body(), response_id="resp_edit")]),
        sleeper=lambda _: None,
    )
    result = direct_edit(provider, request, parent, revision_id="rev-m3-r2-edit-001")
    final_section = parent["form"]["sections"][-1]
    expected_scope = f"time:{float(final_section['start']):g}-{float(final_section['end']):g}"
    assert result["control"]["scope"] == expected_scope
    assert result["control"]["protected_targets"] == sorted(
        [
            "/musical_context/tempo/bpm",
            "/materials/melody/main_motif_id",
            "/materials/rhythm/drum_pattern_id",
        ]
    )
    for pointer in result["control"]["protected_targets"]:
        assert get_pointer(parent, pointer) == get_pointer(result["candidate"], pointer)


def test_model_cannot_inject_blueprint_patch_or_acceptance_fields():
    poisoned = create_body()
    poisoned["blueprint"] = {"attempt": "overwrite canonical state"}
    provider = OpenAIMusicDirectorProvider(
        transport=InjectedTransport([response_for(poisoned)]),
        sleeper=lambda _: None,
    )
    with pytest.raises(OpenAIAdapterError) as exc:
        direct_create(provider, create_request())
    assert exc.value.classification == "invalid_output"
    failure = provider.last_failure()
    assert failure is not None and failure["classification"] == "invalid_output"


def test_unknown_edit_section_is_rejected_before_director_proposal_acceptance():
    parent = parent_blueprint()
    request = build_edit_request(parent, request_id="M3-R2-EDIT-BAD-SCOPE", user_text="Raise tension in S99")
    body = edit_body(scope_kind="section_id", section_id="S99")
    provider = OpenAIMusicDirectorProvider(
        transport=InjectedTransport([response_for(body)]),
        sleeper=lambda _: None,
    )
    with pytest.raises(OpenAIAdapterError) as exc:
        direct_edit(provider, request, parent, revision_id="rev-never-accepted")
    assert exc.value.classification == "invalid_output"


def test_refusal_is_distinct_and_fail_closed():
    response = response_for(create_body())
    response["output"][0]["content"] = [{"type": "refusal", "refusal": "I cannot comply."}]
    provider = OpenAIMusicDirectorProvider(transport=InjectedTransport([response]), sleeper=lambda _: None)
    with pytest.raises(OpenAIAdapterError) as exc:
        direct_create(provider, create_request())
    assert exc.value.classification == "refusal"
    assert provider.last_failure()["classification"] == "refusal"


def test_incomplete_response_is_distinct_and_fail_closed():
    response = response_for(create_body(), status="incomplete")
    response["incomplete_details"] = {"reason": "max_output_tokens"}
    response["output"] = []
    provider = OpenAIMusicDirectorProvider(transport=InjectedTransport([response]), sleeper=lambda _: None)
    with pytest.raises(OpenAIAdapterError) as exc:
        direct_create(provider, create_request())
    assert exc.value.classification == "incomplete"
    assert provider.last_failure()["response_status"] == "incomplete"


def test_invalid_json_output_is_classified_fail_closed():
    response = response_for(create_body())
    response["output"][0]["content"][0]["text"] = "{not-json"
    provider = OpenAIMusicDirectorProvider(transport=InjectedTransport([response]), sleeper=lambda _: None)
    with pytest.raises(OpenAIAdapterError) as exc:
        direct_create(provider, create_request())
    assert exc.value.classification == "invalid_output"


@pytest.mark.parametrize(
    ("status", "classification"),
    [(401, "auth"), (403, "auth"), (429, "rate_limit"), (500, "server"), (503, "server"), (400, "transport")],
)
def test_http_failures_are_classified(status, classification):
    provider = OpenAIMusicDirectorProvider(
        transport=InjectedTransport([OpenAITransportHTTPError(status, {"error": {"message": "fixture failure"}})]),
        max_attempts=1,
        sleeper=lambda _: None,
    )
    with pytest.raises(OpenAIAdapterError) as exc:
        direct_create(provider, create_request())
    assert exc.value.classification == classification
    assert provider.last_failure()["http_status"] == status


def test_retryable_server_failure_retries_then_records_success_attempt_count():
    transport = InjectedTransport(
        [
            OpenAITransportHTTPError(503, {"error": {"message": "temporary"}}),
            response_for(create_body(), response_id="resp_after_retry"),
        ]
    )
    provider = OpenAIMusicDirectorProvider(
        transport=transport,
        max_attempts=2,
        sleeper=lambda _: None,
    )
    direct_create(provider, create_request())
    assert len(transport.calls) == 2
    assert provider.last_exchange()["attempt_count"] == 2


def test_timeout_retries_then_fails_closed():
    transport = InjectedTransport([OpenAITransportTimeout("timeout-a"), OpenAITransportTimeout("timeout-b")])
    provider = OpenAIMusicDirectorProvider(
        transport=transport,
        max_attempts=2,
        sleeper=lambda _: None,
    )
    with pytest.raises(OpenAIAdapterError) as exc:
        direct_create(provider, create_request())
    assert exc.value.classification == "timeout"
    assert len(transport.calls) == 2
    assert provider.last_failure()["classification"] == "timeout"


def test_live_transport_requires_environment_key_before_network_call(monkeypatch):
    class NetworkTransport:
        network_used = True
        requires_api_key = True

        def __init__(self):
            self.called = False

        def send(self, endpoint, payload, *, api_key, timeout_seconds):
            self.called = True
            raise AssertionError("must not reach network transport without credential")

    monkeypatch.delenv("MUSICA_TEST_OPENAI_KEY", raising=False)
    transport = NetworkTransport()
    provider = OpenAIMusicDirectorProvider(
        transport=transport,
        api_key_env="MUSICA_TEST_OPENAI_KEY",
        sleeper=lambda _: None,
    )
    with pytest.raises(OpenAIAdapterError) as exc:
        direct_create(provider, create_request())
    assert exc.value.classification == "auth"
    assert transport.called is False
    failure = provider.last_failure()
    assert failure["network_used"] is True
    assert failure["credential_source"] == "OPENAI_API_KEY environment"
    assert failure["secret_recorded"] is False


def test_offline_transport_never_receives_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-leak-into-offline-transport")
    transport = InjectedTransport([response_for(create_body())])
    provider = OpenAIMusicDirectorProvider(transport=transport, sleeper=lambda _: None)
    direct_create(provider, create_request())
    assert transport.calls[0]["api_key"] is None
    assert OPENAI_RESPONSES_ENDPOINT == transport.calls[0]["endpoint"]
