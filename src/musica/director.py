"""Provider-neutral AI Music Director boundary for MUSICA M3-R1.

MUSICA M3-R1용 provider-neutral AI Music Director 경계.

Providers are proposal engines only. They never receive a MusicaProject object and they
cannot directly emit or mutate canonical Blueprint state. Trusted MUSICA code validates
and lowers bounded proposals into existing M1 contracts before deterministic resolution.
"""

from __future__ import annotations

import copy
import hashlib
import re
from typing import Any, Protocol

from .contracts import ContractError, validate_contract
from .creative import compose_blueprint
from .evidence import canonical_json_bytes
from .profiles import get_style_profile
from .semantic import M1_SEMANTIC_AXES, apply_semantic_control

DIRECTOR_BOUNDARY_VERSION = "0.1.0"
_COMMON_PROTECTED_TARGETS = (
    "/musical_context/tempo/bpm",
    "/materials/melody/main_motif_id",
    "/materials/rhythm/drum_pattern_id",
)
_TIME_SCOPE = re.compile(r"^time:(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$")
_DURATION_EN = re.compile(r"\b(\d+(?:\.\d+)?)\s*[- ]?(?:seconds?|secs?|s)\b", re.IGNORECASE)
_DURATION_KO = re.compile(r"(\d+(?:\.\d+)?)\s*초")


class DirectorError(ContractError):
    """Raised when a Music Director request/proposal violates the authority boundary."""


class MusicDirectorProvider(Protocol):
    """Minimal provider protocol. Implementations receive data, never project authority."""

    def capabilities(self) -> dict[str, Any]:
        """Return a machine-valid Director Provider Capability v0 object."""

    def propose(self, request: dict[str, Any]) -> dict[str, Any]:
        """Return a non-authoritative Director Proposal v0 object."""


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, round(float(value), 6)))


def _stable_seed(request: dict[str, Any]) -> int:
    digest = hashlib.sha256(canonical_json_bytes(request)).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF


def _empty_hints(
    *,
    duration_seconds: float | None = None,
    use_case: str | None = None,
    style_profile: str | None = None,
    seed: int | None = None,
    preserve_on_edit: list[str] | None = None,
    exclusions: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "duration_seconds": duration_seconds,
        "use_case": use_case,
        "style_profile": style_profile,
        "seed": seed,
        "preserve_on_edit": list(preserve_on_edit or []),
        "exclusions": list(exclusions or []),
    }


def build_create_request(
    *,
    request_id: str,
    user_text: str,
    locale: str = "en-US",
    duration_seconds: float | None = None,
    use_case: str | None = None,
    style_profile: str | None = None,
    seed: int | None = None,
    preserve_on_edit: list[str] | None = None,
    exclusions: list[str] | None = None,
) -> dict[str, Any]:
    """Build one validated create request from language plus optional explicit user hints."""

    request = {
        "request_version": "0",
        "request_id": request_id,
        "mode": "create",
        "user_text": user_text,
        "locale": locale,
        "user_hints": _empty_hints(
            duration_seconds=duration_seconds,
            use_case=use_case,
            style_profile=style_profile,
            seed=seed,
            preserve_on_edit=preserve_on_edit,
            exclusions=exclusions,
        ),
        "context": None,
    }
    validate_contract(request, "director-request-v0.schema.json")
    return request


def _edit_context_from_blueprint(blueprint: dict[str, Any]) -> dict[str, Any]:
    validate_contract(blueprint, "music-blueprint-v0.schema.json")
    hard_locks = [
        {
            "lock_id": str(lock["lock_id"]),
            "target": str(lock["target"]),
            "mode": str(lock["mode"]),
        }
        for lock in blueprint.get("locks", [])
        if lock.get("strength") == "HARD" and lock.get("target") in _COMMON_PROTECTED_TARGETS
    ]
    return {
        "project_id": blueprint["project"]["project_id"],
        "revision_id": blueprint["project"]["revision_id"],
        "blueprint_sha256": _sha256_json(blueprint),
        "duration_seconds": float(blueprint["project"]["duration_seconds"]),
        "sections": [
            {
                "section_id": section["section_id"],
                "label": section["label"],
                "start": float(section["start"]),
                "end": float(section["end"]),
            }
            for section in blueprint["form"]["sections"]
        ],
        "hard_locks": hard_locks,
        "semantic_global": {
            axis: float(blueprint["semantics"]["global"][axis])
            for axis in M1_SEMANTIC_AXES
        },
        "supported_semantic_axes": list(M1_SEMANTIC_AXES),
    }


def build_edit_request(
    parent: dict[str, Any],
    *,
    request_id: str,
    user_text: str,
    locale: str = "en-US",
) -> dict[str, Any]:
    """Build a validated edit request bound to an exact canonical Blueprint snapshot."""

    request = {
        "request_version": "0",
        "request_id": request_id,
        "mode": "edit",
        "user_text": user_text,
        "locale": locale,
        "user_hints": _empty_hints(),
        "context": _edit_context_from_blueprint(parent),
    }
    validate_contract(request, "director-request-v0.schema.json")
    return request


def validate_provider_capabilities(capabilities: dict[str, Any]) -> None:
    validate_contract(capabilities, "director-provider-v0.schema.json")


def _require_explicit_hints_preserved(request: dict[str, Any], proposal: dict[str, Any]) -> None:
    if request["mode"] != "create":
        return
    hints = request["user_hints"]
    payload = proposal["payload"]
    for key in ("duration_seconds", "use_case", "style_profile", "seed"):
        if hints[key] is not None and payload[key] != hints[key]:
            raise DirectorError(
                f"provider proposal conflicts with explicit user hint {key}: "
                f"expected {hints[key]!r}, got {payload[key]!r}"
            )
    if payload["preserve_on_edit"] != hints["preserve_on_edit"]:
        raise DirectorError("provider may not silently add/remove preserve_on_edit user policy")
    if payload["exclusions"] != hints["exclusions"]:
        raise DirectorError("provider may not silently add/remove explicit exclusions")


def validate_director_proposal(
    request: dict[str, Any],
    proposal: dict[str, Any],
    capabilities: dict[str, Any],
) -> None:
    """Validate schema, provider identity, requested mode, capabilities, and user authority."""

    validate_contract(request, "director-request-v0.schema.json")
    validate_provider_capabilities(capabilities)
    validate_contract(proposal, "director-proposal-v0.schema.json")

    if proposal["request_id"] != request["request_id"]:
        raise DirectorError("provider proposal request_id does not match the request")
    if proposal["mode"] != request["mode"]:
        raise DirectorError("provider proposal mode does not match the request")
    if request["mode"] not in capabilities["supported_modes"]:
        raise DirectorError(f"provider does not support request mode: {request['mode']}")

    provider = proposal["provider"]
    for key in ("provider_id", "provider_version", "model_id"):
        if provider[key] != capabilities[key]:
            raise DirectorError(f"proposal provider metadata mismatch for {key}")

    payload = proposal["payload"]
    if request["mode"] == "create":
        if payload["kind"] != "create_intent":
            raise DirectorError("create request requires create_intent proposal")
        if payload["style_profile"] not in capabilities["supported_style_profiles"]:
            raise DirectorError(
                f"provider does not declare style support: {payload['style_profile']}"
            )
        if float(payload["tempo"]["min_bpm"]) > float(payload["tempo"]["max_bpm"]):
            raise DirectorError("proposal tempo.min_bpm must be <= tempo.max_bpm")
        explicit_bpm = payload["tempo"]["bpm"]
        if explicit_bpm is not None and not (
            float(payload["tempo"]["min_bpm"])
            <= float(explicit_bpm)
            <= float(payload["tempo"]["max_bpm"])
        ):
            raise DirectorError("proposal explicit tempo falls outside its proposed range")
        _require_explicit_hints_preserved(request, proposal)
    else:
        if payload["kind"] != "semantic_edit":
            raise DirectorError("edit request requires semantic_edit proposal")
        if payload["name"] not in capabilities["supported_semantic_axes"]:
            raise DirectorError(f"provider does not declare semantic support: {payload['name']}")
        context = request["context"]
        if payload["name"] not in context["supported_semantic_axes"]:
            raise DirectorError(f"request context does not support semantic axis: {payload['name']}")
        match = _TIME_SCOPE.fullmatch(str(payload["scope"]))
        if not match:
            raise DirectorError("M3-R1 edit proposal must use an explicit time scope")
        start, end = float(match.group(1)), float(match.group(2))
        if end <= start or end > float(context["duration_seconds"]):
            raise DirectorError("edit proposal time scope is outside the request context")


def request_provider_proposal(
    provider: MusicDirectorProvider,
    request: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Call a provider on a defensive copy and validate its non-authoritative proposal."""

    validate_contract(request, "director-request-v0.schema.json")
    capabilities = copy.deepcopy(provider.capabilities())
    validate_provider_capabilities(capabilities)
    if request["mode"] not in capabilities["supported_modes"]:
        raise DirectorError(f"provider does not support mode: {request['mode']}")

    proposal = provider.propose(copy.deepcopy(request))
    if not isinstance(proposal, dict):
        raise DirectorError("provider must return a Director Proposal object")
    validate_director_proposal(request, proposal, capabilities)
    return copy.deepcopy(proposal), capabilities


def _trace(
    request: dict[str, Any],
    proposal: dict[str, Any],
    capabilities: dict[str, Any],
    accepted_contract: dict[str, Any],
    accepted_contract_kind: str,
) -> dict[str, Any]:
    trace = {
        "trace_version": "0",
        "request_id": request["request_id"],
        "proposal_id": proposal["proposal_id"],
        "mode": request["mode"],
        "provider_id": capabilities["provider_id"],
        "provider_version": capabilities["provider_version"],
        "model_id": capabilities["model_id"],
        "request_sha256": _sha256_json(request),
        "proposal_sha256": _sha256_json(proposal),
        "provider_capabilities_sha256": _sha256_json(capabilities),
        "accepted_contract_kind": accepted_contract_kind,
        "accepted_contract_sha256": _sha256_json(accepted_contract),
        "authority_status": "PROPOSAL_ONLY_MUSICA_CORE_ACCEPTED",
        "warnings": [
            "Provider output is non-authoritative and becomes usable only after MUSICA contract validation.",
            "Provider reproducibility means recorded request/model/proposal provenance, not guaranteed identical future model output.",
        ],
    }
    validate_contract(trace, "director-trace-v0.schema.json")
    return trace


def lower_create_proposal(
    request: dict[str, Any],
    proposal: dict[str, Any],
    capabilities: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Lower a validated provider create proposal into trusted Music Intent v0."""

    validate_director_proposal(request, proposal, capabilities)
    if request["mode"] != "create":
        raise DirectorError("lower_create_proposal requires a create request")
    payload = proposal["payload"]
    intent = {
        "intent_version": "0",
        "intent_id": f"director-{proposal['proposal_id']}",
        "title": payload["title"],
        "duration_seconds": float(payload["duration_seconds"]),
        "use_case": payload["use_case"],
        "raw_prompt": request["user_text"],
        "style_profile": payload["style_profile"],
        "seed": int(payload["seed"]),
        "semantic_targets": copy.deepcopy(payload["semantic_targets"]),
        "tempo": copy.deepcopy(payload["tempo"]),
        "tonal": copy.deepcopy(payload["tonal"]),
        "preserve_on_edit": list(payload["preserve_on_edit"]),
        "exclusions": list(payload["exclusions"]),
        "provenance": {
            "actor": "ai",
            "source": (
                f"music-director:{capabilities['provider_id']}:{capabilities['model_id']}:"
                f"{proposal['proposal_id']}"
            ),
            "confidence": float(proposal["interpretation"]["confidence"]),
        },
    }
    validate_contract(intent, "music-intent-v0.schema.json")
    return intent, _trace(request, proposal, capabilities, intent, "music_intent_v0")


def lower_edit_proposal(
    request: dict[str, Any],
    proposal: dict[str, Any],
    capabilities: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Lower a validated provider edit proposal into trusted Semantic Control v0."""

    validate_director_proposal(request, proposal, capabilities)
    if request["mode"] != "edit":
        raise DirectorError("lower_edit_proposal requires an edit request")
    payload = proposal["payload"]
    notes = list(payload["interpretation_notes"])
    notes.extend(f"provider assumption: {item}" for item in proposal["interpretation"]["assumptions"])
    control = {
        "control_id": f"director-{proposal['proposal_id']}",
        "name": payload["name"],
        "operation": payload["operation"],
        "value": float(payload["value"]),
        "scope": payload["scope"],
        "confidence": float(proposal["interpretation"]["confidence"]),
        "source": "ai_inference",
        "phrase": request["user_text"],
        "interpretation_notes": notes,
        "protected_targets": list(payload["protected_targets"]),
    }
    validate_contract(control, "semantic-control-v0.schema.json")
    return control, _trace(request, proposal, capabilities, control, "semantic_control_v0")


def direct_create(
    provider: MusicDirectorProvider,
    request: dict[str, Any],
) -> dict[str, Any]:
    """Produce a validated create proposal, trusted Intent, and deterministic Blueprint.

    This function has no project-storage side effects.
    """

    if request.get("mode") != "create":
        raise DirectorError("direct_create requires mode=create")
    proposal, capabilities = request_provider_proposal(provider, request)
    intent, trace = lower_create_proposal(request, proposal, capabilities)
    blueprint = compose_blueprint(intent)
    return {
        "provider_capabilities": capabilities,
        "proposal": proposal,
        "intent": intent,
        "trace": trace,
        "blueprint": blueprint,
    }


def direct_edit(
    provider: MusicDirectorProvider,
    request: dict[str, Any],
    parent: dict[str, Any],
    *,
    revision_id: str,
) -> dict[str, Any]:
    """Produce a validated semantic proposal and lock-aware candidate Blueprint.

    The request context must equal a freshly derived snapshot of the supplied parent,
    preventing stale or substituted revision context from reaching canonical resolution.
    This function has no project-storage side effects.
    """

    if request.get("mode") != "edit":
        raise DirectorError("direct_edit requires mode=edit")
    validate_contract(parent, "music-blueprint-v0.schema.json")
    validate_contract(request, "director-request-v0.schema.json")
    expected_context = _edit_context_from_blueprint(parent)
    if request["context"] != expected_context:
        raise DirectorError("edit request context does not match the exact supplied Blueprint revision")

    proposal, capabilities = request_provider_proposal(provider, request)
    control, trace = lower_edit_proposal(request, proposal, capabilities)
    candidate, diff = apply_semantic_control(parent, control, revision_id=revision_id)
    return {
        "provider_capabilities": capabilities,
        "proposal": proposal,
        "control": control,
        "trace": trace,
        "candidate": candidate,
        "diff": diff,
    }


class FixtureMusicDirectorProvider:
    """Deterministic bounded reference provider for M3-R1 CI and contract evidence.

    This is intentionally not represented as general natural-language intelligence. It
    implements a small transparent vocabulary sufficient to exercise the provider boundary.
    """

    PROVIDER_ID = "musica-fixture-director"
    PROVIDER_VERSION = "0.1.0"
    MODEL_ID = "bounded-rule-fixture-v0"

    def capabilities(self) -> dict[str, Any]:
        return {
            "capability_version": "0",
            "provider_id": self.PROVIDER_ID,
            "provider_version": self.PROVIDER_VERSION,
            "model_id": self.MODEL_ID,
            "deterministic": True,
            "network_required": False,
            "supported_modes": ["create", "edit"],
            "supported_style_profiles": [
                "dark_electronic",
                "warm_ambient",
                "kinetic_minimal",
            ],
            "supported_semantic_axes": list(M1_SEMANTIC_AXES),
            "claim_boundary": [
                "bounded transparent rule fixture for provider-contract CI only",
                "not general natural-language understanding",
                "not a substitute for a live model provider",
                "never authoritative over canonical MUSICA state",
            ],
        }

    def _provider_meta(self) -> dict[str, str]:
        return {
            "provider_id": self.PROVIDER_ID,
            "provider_version": self.PROVIDER_VERSION,
            "model_id": self.MODEL_ID,
        }

    @staticmethod
    def _proposal_id(request: dict[str, Any]) -> str:
        return f"P-{_sha256_json(request)[:20]}"

    @staticmethod
    def _duration(text: str, hint: float | None) -> float:
        if hint is not None:
            return float(hint)
        match = _DURATION_EN.search(text) or _DURATION_KO.search(text)
        if match:
            value = next(group for group in match.groups() if group is not None)
            return float(value)
        return 20.0

    @staticmethod
    def _style(text: str, hint: str | None) -> str:
        if hint is not None:
            return hint
        lowered = text.lower()
        if "warm ambient" in lowered or "따뜻" in text or "앰비언트" in text:
            return "warm_ambient"
        if "kinetic minimal" in lowered or "minimal" in lowered or "미니멀" in text:
            return "kinetic_minimal"
        if "dark electronic" in lowered or "dark" in lowered or "다크" in text:
            return "dark_electronic"
        raise DirectorError("fixture provider cannot resolve a supported style from user language")

    @staticmethod
    def _use_case(text: str, hint: str | None) -> str:
        if hint is not None:
            return hint
        lowered = text.lower()
        if any(token in lowered for token in ("advertisement", "commercial", " ad ")) or "광고" in text:
            return "advertisement"
        if "game" in lowered or "게임" in text:
            return "game"
        if "ambient" in lowered or "앰비언트" in text:
            return "ambient"
        if "song" in lowered or "노래" in text:
            return "song"
        return "score"

    @staticmethod
    def _semantic_targets(style: str, text: str) -> dict[str, float]:
        bases: dict[str, dict[str, float]] = {
            "dark_electronic": {
                "energy": 0.62,
                "tension": 0.66,
                "density": 0.58,
                "motion": 0.60,
                "brightness": 0.34,
                "warmth": 0.30,
            },
            "warm_ambient": {
                "energy": 0.36,
                "tension": 0.28,
                "density": 0.42,
                "motion": 0.30,
                "brightness": 0.62,
                "warmth": 0.82,
            },
            "kinetic_minimal": {
                "energy": 0.72,
                "tension": 0.54,
                "density": 0.46,
                "motion": 0.82,
                "brightness": 0.62,
                "warmth": 0.38,
            },
        }
        values = dict(bases[style])
        lowered = text.lower()
        if "restrained" in lowered or "절제" in text:
            values["energy"] -= 0.12
            values["density"] -= 0.08
            values["motion"] -= 0.05
        if "urgent" in lowered or "긴박" in text:
            values["tension"] += 0.16
            values["motion"] += 0.10
        if "bright" in lowered or "밝" in text:
            values["brightness"] += 0.14
        if "warm" in lowered or "따뜻" in text:
            values["warmth"] += 0.12
        return {key: _bounded(value) for key, value in values.items()}

    @staticmethod
    def _edit_axis(text: str) -> str:
        lowered = text.lower()
        if any(token in lowered for token in ("urgent", "tension")) or any(token in text for token in ("긴박", "긴장")):
            return "tension"
        if any(token in lowered for token in ("energy", "powerful", "intense")) or "에너지" in text:
            return "energy"
        if any(token in lowered for token in ("dense", "busy", "layered")) or "밀도" in text:
            return "density"
        if any(token in lowered for token in ("driving", "motion", "propulsive")) or "추진" in text:
            return "motion"
        if "bright" in lowered or "밝" in text:
            return "brightness"
        if "warm" in lowered or "따뜻" in text:
            return "warmth"
        raise DirectorError("fixture provider cannot resolve a supported semantic axis")

    @staticmethod
    def _edit_operation(text: str) -> tuple[str, float]:
        lowered = text.lower()
        if any(token in lowered for token in ("less", "reduce", "decrease")) or any(token in text for token in ("줄", "낮")):
            return "decrease", 0.18
        amount = 0.10 if "slightly" in lowered or "조금" in text else 0.20
        return "increase", amount

    @staticmethod
    def _edit_scope(request: dict[str, Any]) -> str:
        text = request["user_text"]
        lowered = text.lower()
        sections = request["context"]["sections"]
        if any(token in lowered for token in ("final", "last")) or "마지막" in text:
            section = sections[-1]
        elif any(token in lowered for token in ("whole", "overall", "entire")) or "전체" in text:
            return f"time:0-{float(request['context']['duration_seconds']):g}"
        else:
            raise DirectorError("fixture provider requires an explicit final/last or whole-project scope")
        return f"time:{float(section['start']):g}-{float(section['end']):g}"

    def propose(self, request: dict[str, Any]) -> dict[str, Any]:
        validate_contract(request, "director-request-v0.schema.json")
        proposal_id = self._proposal_id(request)
        text = request["user_text"]
        hints = request["user_hints"]

        if request["mode"] == "create":
            style = self._style(text, hints["style_profile"])
            profile = get_style_profile(style)
            duration = self._duration(text, hints["duration_seconds"])
            proposal = {
                "proposal_version": "0",
                "proposal_id": proposal_id,
                "request_id": request["request_id"],
                "mode": "create",
                "provider": self._provider_meta(),
                "interpretation": {
                    "summary": f"Bounded create interpretation using {style}.",
                    "confidence": 0.94,
                    "assumptions": [
                        "The fixture maps only its documented bounded vocabulary.",
                        "Explicit user hints are preserved exactly and outrank inferred values.",
                    ],
                    "alternatives": [
                        "Use another declared style profile while preserving explicit user hints."
                    ],
                },
                "payload": {
                    "kind": "create_intent",
                    "title": f"MUSICA Director — {style.replace('_', ' ').title()}",
                    "duration_seconds": duration,
                    "use_case": self._use_case(text, hints["use_case"]),
                    "style_profile": style,
                    "seed": int(hints["seed"] if hints["seed"] is not None else _stable_seed(request)),
                    "semantic_targets": self._semantic_targets(style, text),
                    "tempo": {
                        "bpm": float(profile["default_bpm"]),
                        "min_bpm": float(profile["tempo_range"][0]),
                        "max_bpm": float(profile["tempo_range"][1]),
                    },
                    "tonal": {
                        "center": profile["default_key"],
                        "mode": profile["default_mode"],
                    },
                    "preserve_on_edit": list(hints["preserve_on_edit"]),
                    "exclusions": list(hints["exclusions"]),
                },
            }
        else:
            axis = self._edit_axis(text)
            operation, amount = self._edit_operation(text)
            protected = [
                lock["target"]
                for lock in request["context"]["hard_locks"]
                if lock["target"] in _COMMON_PROTECTED_TARGETS
            ]
            proposal = {
                "proposal_version": "0",
                "proposal_id": proposal_id,
                "request_id": request["request_id"],
                "mode": "edit",
                "provider": self._provider_meta(),
                "interpretation": {
                    "summary": f"Bounded {axis} {operation} interpretation over explicit time scope.",
                    "confidence": 0.96,
                    "assumptions": [
                        "The requested adjective maps to one implemented M1 semantic axis.",
                        "Existing HARD lock targets remain protected regardless of provider preference.",
                    ],
                    "alternatives": [
                        "Use a smaller semantic delta while preserving the same protected targets."
                    ],
                },
                "payload": {
                    "kind": "semantic_edit",
                    "name": axis,
                    "operation": operation,
                    "value": amount,
                    "scope": self._edit_scope(request),
                    "protected_targets": protected,
                    "interpretation_notes": [
                        "M3-R1 bounded fixture interpretation",
                        "scope resolved from exact request revision context",
                    ],
                },
            }

        validate_contract(proposal, "director-proposal-v0.schema.json")
        return proposal
