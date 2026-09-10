"""Live-ready OpenAI Responses API adapter for MUSICA M3-R2.

The adapter sits behind the validated M3-R1 provider-neutral authority boundary.
It never receives a MusicaProject and never grants the model direct Blueprint or
project-write authority. The model emits only a narrow structured creative body;
trusted MUSICA code reconstructs Director Proposal v0 and the M3-R1 validators
remain authoritative.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import socket
import time
from pathlib import Path
from typing import Any, Callable, Protocol
from urllib import error as urlerror
from urllib import request as urlrequest

from .contracts import ContractError, validate_contract
from .director import DirectorError, validate_director_proposal
from .evidence import canonical_json_bytes
from .semantic import M1_SEMANTIC_AXES

OPENAI_PROVIDER_ID = "openai-responses-api"
OPENAI_PROVIDER_VERSION = "0.1.0"
OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
DEFAULT_OPENAI_MODEL = "gpt-5.6-sol"
_SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"
_COMMON_STYLE_PROFILES = ("dark_electronic", "warm_ambient", "kinetic_minimal")


class OpenAIAdapterError(DirectorError):
    """Fail-closed adapter error with a stable machine classification."""

    def __init__(
        self,
        classification: str,
        message: str,
        *,
        http_status: int | None = None,
        response_status: str | None = None,
    ) -> None:
        super().__init__(message)
        self.classification = classification
        self.http_status = http_status
        self.response_status = response_status


class OpenAITransportHTTPError(RuntimeError):
    def __init__(self, status_code: int, body: Any = None) -> None:
        super().__init__(f"OpenAI HTTP transport returned status {status_code}")
        self.status_code = int(status_code)
        self.body = body


class OpenAITransportTimeout(RuntimeError):
    pass


class OpenAITransportError(RuntimeError):
    pass


class ResponsesTransport(Protocol):
    """Dependency-injected transport used by the adapter.

    Offline CI transports set ``network_used=False`` and ``requires_api_key=False``.
    The live stdlib transport uses the OpenAI API key only in the Authorization header.
    """

    network_used: bool
    requires_api_key: bool

    def send(
        self,
        endpoint: str,
        payload: dict[str, Any],
        *,
        api_key: str | None,
        timeout_seconds: float,
    ) -> dict[str, Any]:
        ...


class UrllibResponsesTransport:
    """Minimal live HTTPS transport using only the Python standard library."""

    network_used = True
    requires_api_key = True

    def send(
        self,
        endpoint: str,
        payload: dict[str, Any],
        *,
        api_key: str | None,
        timeout_seconds: float,
    ) -> dict[str, Any]:
        if not api_key:
            raise OpenAITransportHTTPError(401, {"error": {"message": "missing API key"}})
        body = canonical_json_bytes(payload)
        req = urlrequest.Request(
            endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlrequest.urlopen(req, timeout=timeout_seconds) as response:
                raw = response.read()
        except urlerror.HTTPError as exc:
            raw = exc.read()
            parsed: Any
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except Exception:
                parsed = {"raw": raw.decode("utf-8", errors="replace")[:1000]}
            raise OpenAITransportHTTPError(exc.code, parsed) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise OpenAITransportTimeout("OpenAI request timed out") from exc
        except urlerror.URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise OpenAITransportTimeout("OpenAI request timed out") from exc
            raise OpenAITransportError(f"OpenAI transport failed: {exc.reason}") from exc
        except OSError as exc:
            raise OpenAITransportError(f"OpenAI transport failed: {exc}") from exc

        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise OpenAITransportError("OpenAI response was not valid UTF-8 JSON") from exc
        if not isinstance(value, dict):
            raise OpenAITransportError("OpenAI response root must be a JSON object")
        return value


def _load_schema(name: str) -> dict[str, Any]:
    path = _SCHEMA_DIR / name
    if not path.exists():
        raise ContractError(f"unknown OpenAI adapter schema: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _stable_seed(request_value: dict[str, Any]) -> int:
    material = copy.deepcopy(request_value)
    # Request IDs are operational identity, not musical intent. Excluding the ID lets
    # the same user instruction/hints produce the same downstream seed when no seed
    # was explicitly supplied.
    material.pop("request_id", None)
    digest = hashlib.sha256(canonical_json_bytes(material)).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF


def _credential_source(transport: ResponsesTransport) -> str:
    return "OPENAI_API_KEY environment" if transport.network_used else "injected-no-secret"


def _classify_http(status: int) -> str:
    if status in {401, 403}:
        return "auth"
    if status == 429:
        return "rate_limit"
    if status >= 500:
        return "server"
    return "transport"


def _retryable(classification: str) -> bool:
    return classification in {"rate_limit", "server", "timeout", "transport"}


def _compact_error_message(value: Any) -> str:
    if isinstance(value, dict):
        error = value.get("error")
        if isinstance(error, dict) and error.get("message"):
            return str(error["message"])[:1600]
    return str(value)[:1600]


def _usage(response: dict[str, Any]) -> dict[str, int | None]:
    usage = response.get("usage")
    if not isinstance(usage, dict):
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    result: dict[str, int | None] = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        value = usage.get(key)
        result[key] = int(value) if isinstance(value, int) and value >= 0 else None
    return result


def _extract_structured_text(response: dict[str, Any]) -> str:
    output = response.get("output")
    if not isinstance(output, list):
        raise OpenAIAdapterError("invalid_output", "OpenAI response output must be an array")

    texts: list[str] = []
    refusals: list[str] = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict):
                continue
            part_type = part.get("type")
            if part_type == "refusal":
                refusals.append(str(part.get("refusal") or "model refusal"))
            elif part_type == "output_text" and isinstance(part.get("text"), str):
                texts.append(part["text"])

    if refusals:
        raise OpenAIAdapterError("refusal", "OpenAI model refused the request: " + " | ".join(refusals)[:1500])
    if len(texts) != 1:
        raise OpenAIAdapterError(
            "invalid_output",
            f"expected exactly one structured output_text item, got {len(texts)}",
        )
    return texts[0]


def _scope_from_body(body: dict[str, Any], context: dict[str, Any]) -> str:
    sections = context["sections"]
    duration = float(context["duration_seconds"])
    kind = body["scope_kind"]
    section_id = body["section_id"]

    if kind == "whole_project":
        if section_id is not None:
            raise OpenAIAdapterError("invalid_output", "whole_project scope requires section_id=null")
        return f"time:0-{duration:g}"
    if kind == "final_section":
        if section_id is not None:
            raise OpenAIAdapterError("invalid_output", "final_section scope requires section_id=null")
        section = sections[-1]
        return f"time:{float(section['start']):g}-{float(section['end']):g}"
    if kind == "section_id":
        if not section_id:
            raise OpenAIAdapterError("invalid_output", "section_id scope requires a section_id")
        for section in sections:
            if section["section_id"] == section_id:
                return f"time:{float(section['start']):g}-{float(section['end']):g}"
        raise OpenAIAdapterError("invalid_output", f"unknown section_id in OpenAI proposal: {section_id}")
    raise OpenAIAdapterError("invalid_output", f"unsupported scope_kind: {kind}")


def _protected_targets(context: dict[str, Any]) -> list[str]:
    return sorted({str(lock["target"]) for lock in context.get("hard_locks", [])})


def _proposal_id(response: dict[str, Any], body: dict[str, Any], request_id: str) -> str:
    material = {
        "response_id": response.get("id"),
        "response_model": response.get("model"),
        "request_id": request_id,
        "body": body,
    }
    return "oa-" + _sha256_json(material)[:32]


def _create_body_to_payload(request_value: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    hints = request_value["user_hints"]
    return {
        "kind": "create_intent",
        "title": body["title"],
        "duration_seconds": (
            float(hints["duration_seconds"])
            if hints["duration_seconds"] is not None
            else float(body["duration_seconds"])
        ),
        "use_case": hints["use_case"] if hints["use_case"] is not None else body["use_case"],
        "style_profile": (
            hints["style_profile"]
            if hints["style_profile"] is not None
            else body["style_profile"]
        ),
        "seed": int(hints["seed"]) if hints["seed"] is not None else _stable_seed(request_value),
        "semantic_targets": copy.deepcopy(body["semantic_targets"]),
        "tempo": copy.deepcopy(body["tempo"]),
        "tonal": copy.deepcopy(body["tonal"]),
        "preserve_on_edit": list(hints["preserve_on_edit"]),
        "exclusions": list(hints["exclusions"]),
    }


def _edit_body_to_payload(request_value: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    context = request_value["context"]
    if not isinstance(context, dict):
        raise OpenAIAdapterError("invalid_output", "edit request is missing validated context")
    scope = _scope_from_body(body, context)
    notes = list(body["interpretation_notes"])
    notes.append(
        "MUSICA adapter resolved provider scope selector to exact canonical time scope: " + scope
    )
    return {
        "kind": "semantic_edit",
        "name": body["name"],
        "operation": body["operation"],
        "value": float(body["value"]),
        "scope": scope,
        "protected_targets": _protected_targets(context),
        "interpretation_notes": notes,
    }


def _schema_for_mode(mode: str) -> tuple[str, dict[str, Any]]:
    if mode == "create":
        return "musica_director_create_v0", _load_schema("openai-director-create-body-v0.schema.json")
    if mode == "edit":
        return "musica_director_edit_v0", _load_schema("openai-director-edit-body-v0.schema.json")
    raise ContractError(f"unsupported Director mode: {mode}")


def build_openai_response_payload(request_value: dict[str, Any], model_id: str) -> dict[str, Any]:
    """Build the secret-free OpenAI Responses payload from Director Request v0."""

    validate_contract(request_value, "director-request-v0.schema.json")
    schema_name, schema = _schema_for_mode(request_value["mode"])
    instructions = (
        "You are the bounded MUSICA AI Music Director interpretation layer. "
        "Return only the JSON object required by the supplied strict schema. "
        "You may interpret musical intent, but you have no authority to accept state, mutate a project, "
        "edit a Music Blueprint directly, bypass locks, invent JSON paths, or change explicit user policy. "
        "For create mode, choose only among the exposed MUSICA style profiles and six semantic axes. "
        "For edit mode, choose one supported semantic axis and a bounded scope selector. "
        "When uncertain, record assumptions and alternatives instead of fabricating precision."
    )
    provider_input = {
        "request_version": request_value["request_version"],
        "mode": request_value["mode"],
        "user_text": request_value["user_text"],
        "locale": request_value["locale"],
        "user_hints": copy.deepcopy(request_value["user_hints"]),
        "context": copy.deepcopy(request_value["context"]),
    }
    return {
        "model": model_id,
        "instructions": instructions,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": canonical_json_bytes(provider_input).decode("utf-8"),
                    }
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "strict": True,
                "schema": schema,
            }
        },
        "store": False,
    }


class OpenAIMusicDirectorProvider:
    """OpenAI Responses adapter implementing the M3-R1 MusicDirectorProvider protocol."""

    def __init__(
        self,
        *,
        model_id: str = DEFAULT_OPENAI_MODEL,
        transport: ResponsesTransport | None = None,
        api_key_env: str = "OPENAI_API_KEY",
        timeout_seconds: float = 45.0,
        max_attempts: int = 2,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if not model_id:
            raise ValueError("model_id must not be empty")
        if not 0 < float(timeout_seconds) <= 300:
            raise ValueError("timeout_seconds must be within (0, 300]")
        if not 1 <= int(max_attempts) <= 5:
            raise ValueError("max_attempts must be within [1, 5]")
        self.model_id = model_id
        self.transport: ResponsesTransport = transport or UrllibResponsesTransport()
        self.api_key_env = api_key_env
        self.timeout_seconds = float(timeout_seconds)
        self.max_attempts = int(max_attempts)
        self.sleeper = sleeper
        self._last_exchange: dict[str, Any] | None = None
        self._last_failure: dict[str, Any] | None = None

    def capabilities(self) -> dict[str, Any]:
        result = {
            "capability_version": "0",
            "provider_id": OPENAI_PROVIDER_ID,
            "provider_version": OPENAI_PROVIDER_VERSION,
            "model_id": self.model_id,
            "deterministic": False,
            "network_required": True,
            "supported_modes": ["create", "edit"],
            "supported_style_profiles": list(_COMMON_STYLE_PROFILES),
            "supported_semantic_axes": list(M1_SEMANTIC_AXES),
            "claim_boundary": [
                "External model output is probabilistic and non-authoritative.",
                "The model emits only narrow structured creative bodies; MUSICA constructs and validates Director Proposal v0.",
                "The provider never receives MusicaProject authority or project-write capability.",
                "Reproducibility records request/model/response digests and downstream deterministic state, not identical future model text.",
            ],
        }
        validate_contract(result, "director-provider-v0.schema.json")
        return result

    def last_exchange(self) -> dict[str, Any] | None:
        return copy.deepcopy(self._last_exchange)

    def last_failure(self) -> dict[str, Any] | None:
        return copy.deepcopy(self._last_failure)

    def _record_failure(
        self,
        classification: str,
        message: str,
        request_payload: dict[str, Any],
        *,
        http_status: int | None = None,
        response_status: str | None = None,
    ) -> None:
        failure = {
            "failure_version": "0",
            "classification": classification,
            "message": message[:2000],
            "http_status": http_status,
            "response_status": response_status,
            "request_payload_sha256": _sha256_json(request_payload),
            "network_used": bool(self.transport.network_used),
            "credential_source": _credential_source(self.transport),
            "secret_recorded": False,
        }
        validate_contract(failure, "openai-adapter-failure-v0.schema.json")
        self._last_failure = failure
        self._last_exchange = None

    def _send_with_retry(self, payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
        api_key: str | None = None
        if self.transport.requires_api_key:
            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                self._record_failure("auth", f"missing required environment variable {self.api_key_env}", payload)
                raise OpenAIAdapterError("auth", f"missing required environment variable {self.api_key_env}")

        last_error: OpenAIAdapterError | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.transport.send(
                    OPENAI_RESPONSES_ENDPOINT,
                    copy.deepcopy(payload),
                    api_key=api_key,
                    timeout_seconds=self.timeout_seconds,
                )
                if not isinstance(response, dict):
                    raise OpenAITransportError("transport returned a non-object response")
                return response, attempt
            except OpenAITransportHTTPError as exc:
                classification = _classify_http(exc.status_code)
                message = _compact_error_message(exc.body)
                last_error = OpenAIAdapterError(
                    classification,
                    message,
                    http_status=exc.status_code,
                )
            except OpenAITransportTimeout as exc:
                last_error = OpenAIAdapterError("timeout", str(exc))
            except OpenAITransportError as exc:
                last_error = OpenAIAdapterError("transport", str(exc))
            except (TimeoutError, socket.timeout) as exc:
                last_error = OpenAIAdapterError("timeout", str(exc) or "transport timeout")
            except OSError as exc:
                last_error = OpenAIAdapterError("transport", str(exc))

            if last_error is None:
                break
            if attempt < self.max_attempts and _retryable(last_error.classification):
                self.sleeper(min(0.25 * attempt, 1.0))
                continue
            self._record_failure(
                last_error.classification,
                str(last_error),
                payload,
                http_status=last_error.http_status,
            )
            raise last_error

        raise OpenAIAdapterError("transport", "OpenAI transport exhausted without a response")

    def propose(self, request_value: dict[str, Any]) -> dict[str, Any]:
        """Return a validated, non-authoritative Director Proposal v0.

        This method does not mutate MUSICA project state. The model-generated body is
        validated first, then trusted adapter code reconstructs the Director Proposal.
        """

        validate_contract(request_value, "director-request-v0.schema.json")
        self._last_exchange = None
        self._last_failure = None
        payload = build_openai_response_payload(request_value, self.model_id)
        response, attempt_count = self._send_with_retry(payload)

        response_status = str(response.get("status") or "missing")
        if response_status == "incomplete":
            reason = response.get("incomplete_details")
            message = "OpenAI response incomplete"
            if isinstance(reason, dict) and reason.get("reason"):
                message += f": {reason['reason']}"
            self._record_failure("incomplete", message, payload, response_status=response_status)
            raise OpenAIAdapterError("incomplete", message, response_status=response_status)
        if response_status != "completed":
            error_value = response.get("error")
            classification = "server" if response_status == "failed" else "transport"
            message = f"OpenAI response status is {response_status}: {_compact_error_message(error_value)}"
            self._record_failure(classification, message, payload, response_status=response_status)
            raise OpenAIAdapterError(classification, message, response_status=response_status)

        try:
            text = _extract_structured_text(response)
            body = json.loads(text)
            if not isinstance(body, dict):
                raise OpenAIAdapterError("invalid_output", "structured output root must be an object")
            body_schema = (
                "openai-director-create-body-v0.schema.json"
                if request_value["mode"] == "create"
                else "openai-director-edit-body-v0.schema.json"
            )
            validate_contract(body, body_schema)
            proposal = {
                "proposal_version": "0",
                "proposal_id": _proposal_id(response, body, request_value["request_id"]),
                "request_id": request_value["request_id"],
                "mode": request_value["mode"],
                "provider": {
                    "provider_id": OPENAI_PROVIDER_ID,
                    "provider_version": OPENAI_PROVIDER_VERSION,
                    "model_id": self.model_id,
                },
                "interpretation": copy.deepcopy(body["interpretation"]),
                "payload": (
                    _create_body_to_payload(request_value, body)
                    if request_value["mode"] == "create"
                    else _edit_body_to_payload(request_value, body)
                ),
            }
            capabilities = self.capabilities()
            validate_director_proposal(request_value, proposal, capabilities)
        except OpenAIAdapterError as exc:
            self._record_failure(
                exc.classification,
                str(exc),
                payload,
                http_status=exc.http_status,
                response_status=response_status,
            )
            raise
        except (json.JSONDecodeError, ContractError, KeyError, TypeError, ValueError) as exc:
            message = f"invalid OpenAI structured output: {exc}"
            self._record_failure("invalid_output", message, payload, response_status=response_status)
            raise OpenAIAdapterError("invalid_output", message, response_status=response_status) from exc

        exchange = {
            "exchange_version": "0",
            "evidence_class": (
                "LIVE_PROVIDER_EVIDENCE" if self.transport.network_used else "ADAPTER_CONTRACT_EVIDENCE"
            ),
            "api_family": "openai-responses",
            "endpoint": OPENAI_RESPONSES_ENDPOINT,
            "provider_id": OPENAI_PROVIDER_ID,
            "provider_version": OPENAI_PROVIDER_VERSION,
            "requested_model_id": self.model_id,
            "response_model_id": (
                str(response["model"]) if response.get("model") is not None else None
            ),
            "response_id": str(response["id"]) if response.get("id") is not None else None,
            "response_status": response_status,
            "request_payload_sha256": _sha256_json(payload),
            "raw_response_sha256": _sha256_json(response),
            "structured_body_sha256": _sha256_json(body),
            "director_proposal_sha256": _sha256_json(proposal),
            "usage": _usage(response),
            "attempt_count": attempt_count,
            "max_attempts": self.max_attempts,
            "timeout_seconds": self.timeout_seconds,
            "network_used": bool(self.transport.network_used),
            "credential_source": _credential_source(self.transport),
            "secret_recorded": False,
        }
        validate_contract(exchange, "openai-adapter-exchange-v0.schema.json")
        self._last_exchange = exchange
        self._last_failure = None
        return copy.deepcopy(proposal)
