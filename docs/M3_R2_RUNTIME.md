# M3-R2 Runtime / OpenAI Provider Adapter 런타임

## 1. Role / 역할

M3-R2 implements an OpenAI Responses API transport adapter behind the already validated M3-R1 AI Music Director authority boundary.

M3-R2는 이미 검증된 M3-R1 AI Music Director 권한 경계 뒤에 OpenAI Responses API transport adapter를 구현합니다.

The adapter is **not** the canonical music engine. It is an interpretation provider.

Adapter는 공식 음악 엔진이 아니라 해석 provider입니다.

## 2. Runtime path / 실행 경로

```text
Director Request v0
  ↓
build_openai_response_payload()
  ↓
POST /v1/responses
  ↓
strict Structured Output creative body
  ↓
local full-schema validation
  ↓
MUSICA-owned reconstruction
  ├─ proposal_id
  ├─ provider metadata
  ├─ deterministic fallback seed
  ├─ explicit user preserve/exclusions
  ├─ exact edit time scope
  └─ current HARD-lock protected targets
  ↓
Director Proposal v0
  ↓
M3-R1 validate_director_proposal()
  ↓
Music Intent v0 or Semantic Control v0
  ↓
M1 deterministic core
  ↓
M2 explicit commit
```

## 3. Why the model returns a narrower object / 모델 출력이 더 좁은 이유

The model does not emit the final Director Proposal envelope. This prevents probabilistic output from choosing its own provider identity, proposal/request binding, user policy, protected paths, or acceptance status.

모델은 최종 Director Proposal envelope 전체를 출력하지 않습니다. 확률적 출력이 provider identity, request 결속, 사용자 정책, 보호 경로, 승인 상태를 스스로 결정하지 못하게 하기 위함입니다.

Create-mode model output may describe only:

- interpretation summary/confidence/assumptions/alternatives,
- title,
- duration/use-case/style suggestion,
- six semantic targets,
- bounded tempo intent,
- bounded tonal intent.

Edit-mode model output may describe only:

- interpretation metadata,
- one of the six implemented semantic axes,
- set/increase/decrease,
- bounded value,
- `whole_project`, `final_section`, or a declared `section_id` selector,
- interpretation notes.

Exact JSON Pointer mutation is not exposed to the model.

모델에는 정확한 JSON Pointer 변경 권한을 노출하지 않습니다.

## 4. OpenAI API shape / OpenAI API 형태

M3-R2 uses the Responses API endpoint and Structured Outputs contract verified during implementation:

```json
{
  "model": "gpt-5.6-sol",
  "instructions": "...bounded MUSICA authority instructions...",
  "input": [{"role": "user", "content": [{"type": "input_text", "text": "..."}]}],
  "text": {
    "format": {
      "type": "json_schema",
      "name": "musica_director_create_v0",
      "strict": true,
      "schema": {}
    }
  },
  "store": false
}
```

API credentials are never fields in this payload object. The live transport adds the bearer credential only to the HTTPS Authorization header at runtime.

API credential은 payload 필드가 아니며 live transport가 실행 시 HTTPS Authorization header에만 추가합니다.

## 5. Transport model / Transport 모델

`ResponsesTransport` is dependency injected.

- `UrllibResponsesTransport`: live HTTPS path; requires `OPENAI_API_KEY` by default.
- injected test transport: no network, no credential, deterministic fixture response.

Normal CI uses only the second form.

일반 CI에서는 두 번째 방식만 사용합니다.

## 6. Retry and failure policy / 재시도·실패 정책

Bounded retry is allowed only for transient transport classes:

- rate-limit,
- server,
- timeout,
- transport.

Authentication failure, refusal, incomplete model response, and invalid structured output never become accepted state.

인증 실패, refusal, incomplete 응답, invalid structured output은 공식 상태가 될 수 없습니다.

Stable adapter classifications:

```text
auth
rate_limit
server
timeout
transport
incomplete
refusal
invalid_output
```

## 7. Provenance / 실행 근거

A successful exchange stores no prompt text or credential in the compact exchange record. It records SHA-256 digests and execution metadata:

- requested/returned model IDs,
- response ID/status,
- request-payload digest,
- raw-response digest,
- structured-body digest,
- reconstructed Director Proposal digest,
- token usage when returned,
- timeout/max-attempt/actual-attempt policy,
- network-used flag,
- credential-source class,
- `secret_recorded=false`.

Canonical offline CI may separately preserve its injected fixture payload/response because they contain no user secret or live credential. Such evidence remains explicitly marked `ADAPTER_CONTRACT_EVIDENCE`.

## 8. Reproducibility meaning / 재현성 의미

M3-R2 does not claim that a live external LLM will emit byte-identical content on a future call.

M3-R2는 실제 외부 LLM이 미래 호출에서도 byte-identical 응답을 출력한다고 주장하지 않습니다.

Reproducibility means MUSICA can preserve and inspect:

```text
exact Director Request
+ requested model
+ adapter policy
+ exact response/proposal digests
+ accepted trusted contract
+ deterministic downstream Blueprint/project/render state
```

## 9. Security and authority boundaries / 보안·권한 경계

The OpenAI provider never receives a `MusicaProject` instance or filesystem mutation capability. Project state changes only through a later explicit M2 commit after M3-R1 and M1 validation.

OpenAI provider는 `MusicaProject` 인스턴스나 파일시스템 변경 권한을 받지 않습니다. 프로젝트 상태 변경은 M3-R1 및 M1 검증 이후 별도의 명시적 M2 commit에서만 발생합니다.

## 10. Evidence classes / 근거 등급

### `ADAPTER_CONTRACT_EVIDENCE`

Offline injected-transport proof. Demonstrates payload construction, response parsing, error handling, proposal reconstruction, authority validation, and downstream integration. **It is not a live OpenAI result.**

### `LIVE_PROVIDER_EVIDENCE`

May be emitted only when an authorized credential actually executes the network transport. Live evidence is optional for M3-R2 repository CI and must remain separately identified.
