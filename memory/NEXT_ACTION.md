# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M3-R2 — OPENAI MUSIC DIRECTOR PROVIDER ADAPTER v0 / M3-R2 — OpenAI Music Director Provider Adapter v0**

M3-R1 provider-neutral authority boundary is validated. The next problem is to place a real network-model adapter behind that boundary without weakening any user-authority, schema, lock, project-integrity, or provenance guarantees.

M3-R1 provider-neutral 권한 경계는 검증되었습니다. 다음 문제는 사용자 권위, schema, lock, project integrity, provenance 보장을 약화하지 않으면서 실제 네트워크 모델 adapter를 그 경계 뒤에 연결하는 것입니다.

## Non-negotiable authority / 변경 불가 권한 규칙

```text
User language
  ↓
Director Request v0
  ↓
OpenAI adapter / external model transport
  ↓
UNTRUSTED Director Proposal v0
  ↓
M3-R1 schema + authority validation
  ↓
trusted Music Intent / Semantic Control
  ↓
M1 deterministic + lock-aware core
  ↓
explicit M2 commit
  ↓
Accepted Blueprint Revision
```

The OpenAI adapter MUST NOT receive direct write authority to `.musica` Project Bundle state and MUST NOT bypass `Director Proposal v0`.

OpenAI adapter는 `.musica` Project Bundle 상태에 대한 직접 쓰기 권한을 받아서는 안 되며 `Director Proposal v0`를 우회해서도 안 됩니다.

## Required sequence / 필수 순서

1. Verify the current official OpenAI API/model/structured-output contract from official OpenAI documentation before implementation. / 구현 전 공식 OpenAI 문서에서 현재 API·model·structured output 계약을 검증합니다.
2. Record a bounded adapter design decision and claim boundary. / 제한형 adapter 설계 결정과 주장 경계를 기록합니다.
3. Implement a transport-injected `OpenAIMusicDirectorProvider` behind the existing M3-R1 protocol. / 기존 M3-R1 protocol 뒤에 transport 주입형 provider를 구현합니다.
4. Keep credentials out of repository state; runtime environment/configuration only. / 자격정보는 레포 밖의 런타임 환경·설정으로만 관리합니다.
5. Request schema-constrained structured proposal output matching the create/edit proposal boundary. / create/edit proposal 경계에 맞는 schema-constrained 구조화 출력을 요청합니다.
6. Record provider/model/API configuration, request payload digest, raw/normalized response digest where safely available, and proposal digest. / provider/model/API 설정과 request·response·proposal digest를 기록합니다.
7. Classify transport/auth/rate-limit/server/timeout/invalid-output failures and fail closed. / transport·auth·rate-limit·server·timeout·invalid-output 오류를 분류하고 실패 폐쇄합니다.
8. Use dependency/transport injection so all adapter behavior is testable with no secret and no network in CI. / secret·network 없는 CI에서도 adapter 동작을 검증할 수 있도록 transport 주입을 사용합니다.
9. Prove that malicious or malformed external responses remain blocked by M3-R1 authority validation. / 악성·잘못된 외부 응답도 M3-R1 권한 검증에서 차단됨을 증명합니다.
10. Preserve all M0→M3-R1 regressions on Python 3.11/3.12. / Python 3.11/3.12에서 기존 회귀를 보존합니다.

## Evidence classes / 근거 등급

M3-R2 MUST distinguish these evidence classes:

M3-R2는 다음 근거 등급을 구분해야 합니다.

- **ADAPTER_CONTRACT_EVIDENCE** — offline injected-transport tests proving request construction, response normalization, structured proposal validation, error handling, and provenance. Required for M3-R2 acceptance.
- **LIVE_PROVIDER_EVIDENCE** — actual authorized external call evidence, only when a runtime credential is explicitly available. Optional unless a later milestone makes it mandatory.

Absence of a secret MUST NOT make normal CI fail, and offline adapter-contract evidence MUST NOT be mislabeled as a live OpenAI call.

Secret 부재로 일반 CI가 실패해서는 안 되며 오프라인 adapter 계약 근거를 실제 OpenAI 호출로 표시해서도 안 됩니다.

## Reproducibility rule / 재현성 규칙

External model output is probabilistic unless the external service explicitly guarantees otherwise. MUSICA MUST preserve enough evidence to identify exactly what was requested and accepted, but MUST NOT claim that a future call will reproduce identical language or proposal bytes.

외부 모델 출력은 외부 서비스가 명시적으로 보장하지 않는 한 확률적입니다. MUSICA는 무엇을 요청하고 무엇을 승인했는지 식별할 충분한 근거를 보존해야 하지만 미래 호출이 동일한 자연어 또는 proposal byte를 재현한다고 주장해서는 안 됩니다.

## M3-R2 acceptance boundary / M3-R2 수용 경계

M3-R2 may be accepted from deterministic offline transport-injected evidence plus current official API-contract grounding. A live call, if available and authorized, is recorded as an additional evidence class rather than silently required.

M3-R2는 결정론적 offline transport-injected 근거와 현재 공식 API 계약 근거로 수용할 수 있습니다. 실제 호출이 승인되어 가능할 경우 별도 근거 등급으로 추가 기록하며 암묵적으로 필수화하지 않습니다.

## Product sequence / 제품 순서

```text
M3-R2 OpenAI Provider Adapter
→ M3 closure: AI Music Director Provider Layer validated
→ M4 MUSICA Studio usable application MVP
→ M5 Renderer/DAW interoperability & quality expansion
→ M6 Product hardening / packaging / release candidate
```

## Development discipline / 개발 규율

```text
Official API verification
→ Issue
→ Branch
→ Contract/adapter design
→ Implementation
→ Offline tests
→ PR
→ exact-head CI
→ durable evidence
→ Merge
→ State update
```

Repository-backed contracts, official API evidence, and executable CI remain authoritative over conversation or model memory.

레포 기반 계약, 공식 API 근거, 실행 가능한 CI는 계속해서 대화 또는 모델 기억보다 우선합니다.
