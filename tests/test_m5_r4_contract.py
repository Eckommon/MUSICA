from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from musica.contracts import ContractError, validate_contract

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/audio-comparisons/valid/contract-fixture-not-evidence.json"
SCHEMA = "audio-comparison-result-v0.schema.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_m5_r4_contract_fixture_validates():
    validate_contract(load_fixture(), SCHEMA)


def test_m5_r4_v0_rejects_perceptual_superiority_claim():
    candidate = load_fixture()
    candidate["claim_boundary"]["perceptual_superiority"] = "RENDERER_B_BETTER"
    candidate["claim_boundary"]["human_preference_claim_allowed"] = True
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_contract(candidate, SCHEMA)


def test_comparable_requires_all_technical_gates_true():
    candidate = load_fixture()
    candidate["comparability"] = {"status": "COMPARABLE", "reasons": []}
    candidate["verdict"] = "COMPARABLE_OBJECTIVE_ONLY"
    candidate["technical_validity"]["qa_acceptable"] = False
    candidate["technical_validity"]["provenance_complete"] = True
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_contract(candidate, SCHEMA)


def test_comparable_contract_can_exist_only_with_all_gates_true():
    candidate = load_fixture()
    candidate["comparability"] = {"status": "COMPARABLE", "reasons": []}
    candidate["verdict"] = "COMPARABLE_OBJECTIVE_ONLY"
    candidate["technical_validity"] = {
        "source_hash_match": True,
        "blueprint_binding_match": True,
        "qa_acceptable": True,
        "target_duration_match": True,
        "provenance_complete": True,
    }
    validate_contract(candidate, SCHEMA)


def test_not_comparable_requires_machine_readable_reason():
    candidate = load_fixture()
    candidate["comparability"]["reasons"] = []
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_contract(candidate, SCHEMA)


def test_v0_forbids_hidden_comparison_resampling_or_gain_matching():
    candidate = copy.deepcopy(load_fixture())
    candidate["analysis_policy"]["comparison_resampling"] = "LINEAR"
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_contract(candidate, SCHEMA)

    candidate = copy.deepcopy(load_fixture())
    candidate["analysis_policy"]["comparison_gain_matching"] = "RMS"
    with pytest.raises(ContractError, match="schema validation failed"):
        validate_contract(candidate, SCHEMA)
