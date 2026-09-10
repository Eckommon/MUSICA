# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M3-R1 — AI MUSIC DIRECTOR PROVIDER CONTRACT & AUTHORITY BOUNDARY / M3-R1 — AI Music Director Provider 계약 및 권한 경계**

M2 Project & Version Engine v0 is validated. The next problem is not persistence. It is how MUSICA can accept convenient natural-language direction from a user while keeping probabilistic AI outside the canonical-authority boundary.

M2 Project & Version Engine v0는 검증되었습니다. 다음 문제는 영속 저장이 아닙니다. 이제 확률적 AI를 공식 권위 경계 밖에 유지하면서 사용자의 편리한 자연어 디렉션을 MUSICA가 어떻게 받을 것인지 증명해야 합니다.

## Architectural decision / 아키텍처 결정

The AI Music Director is a **proposal engine, never the canonical state owner**.

AI Music Director는 **제안 엔진이며 공식 상태 소유자가 아닙니다**.

```text
User language / 사용자 자연어
        ↓
Director Request
        ↓
AI Provider
        ↓
Typed Director Proposal
        ↓
Schema + authority validation
        ↓
MUSICA deterministic core
        ↓
Lock / constraint validation
        ↓
Accepted Music Intent or Blueprint revision
        ↓
M2 Project Bundle
```

A provider MUST NOT directly overwrite an accepted Blueprint, bypass a HARD lock, mutate a `.musica` Project Bundle, or declare its own output accepted.

Provider는 승인 Blueprint를 직접 덮어쓰거나 HARD lock을 우회하거나 `.musica` Project Bundle을 직접 변경하거나 자신의 출력을 스스로 승인 상태로 선언해서는 안 됩니다.

## M3 staged sequence / M3 단계 순서

### M3-R1 — Provider-neutral contract + deterministic reference provider

Prove the provider boundary without depending on external network availability or secrets.

외부 네트워크·secret에 의존하지 않고 provider 경계를 먼저 증명합니다.

Required / 필수:

1. machine-valid `Director Request v0` / 기계 검증 가능한 Director Request v0,
2. machine-valid `Director Proposal v0` with create/edit proposal kinds / create·edit 종류의 Director Proposal v0,
3. provider protocol and capability declaration / provider protocol·역량 선언,
4. deterministic fixture/reference provider for CI / CI용 결정론 fixture/reference provider,
5. proposal validator that rejects malformed, over-authoritative, or unsupported output / 잘못되거나 과도한 권위를 주장하거나 미지원 출력을 거부하는 validator,
6. create path: natural-language request → proposed Music Intent → M1 composer / 생성 경로,
7. edit path: natural-language request + exact current revision context → proposed Semantic Control → M1 semantic resolver / 수정 경로,
8. uncertainty, assumptions, alternatives, provider/model metadata, and response digest provenance / 불확실성·가정·대안·provider/model 메타데이터·응답 digest provenance,
9. negative tests proving provider output cannot bypass locks or inject arbitrary Blueprint paths / lock 우회·임의 Blueprint path 주입 차단 테스트,
10. M0/M1/M2 regression preservation / 기존 회귀 보존.

### M3-R2 — OpenAI provider adapter + bounded live-ready path

After R1 is accepted, add an OpenAI adapter against the then-current official API contract, with credentials supplied only through runtime environment/configuration and never committed to the repository.

R1 승인 후 당시 공식 API 계약을 기준으로 OpenAI adapter를 추가합니다. 자격정보는 런타임 환경·설정으로만 주입하며 레포에 커밋하지 않습니다.

Required / 필수:

1. structured/schema-constrained provider response / 구조화·schema 제약 응답,
2. explicit model/provider provenance / 명시적 model/provider provenance,
3. timeout/retry/error classification with fail-closed behavior / timeout·retry·오류 분류 및 실패 폐쇄,
4. transport-injected offline tests / transport 주입형 오프라인 테스트,
5. no-secret CI path / secret 없는 CI 경로,
6. optional live smoke evidence only when authorized credentials are available / 승인된 자격정보가 있을 때만 선택적 live smoke 근거,
7. live evidence MUST be distinguished from adapter-contract evidence / live 근거와 adapter 계약 근거 구분.

M3 may be validated without pretending that an external provider call is deterministic. Reproducibility means preserving the exact request contract, provider/model identifiers, configuration, response/proposal digest, accepted proposal, and downstream deterministic state—not claiming that the provider will emit identical text forever.

M3는 외부 provider 호출 자체가 결정론적이라고 가장하지 않습니다. 재현성이란 provider가 영원히 같은 텍스트를 출력한다고 주장하는 것이 아니라, 정확한 request 계약·provider/model 식별자·설정·response/proposal digest·승인 제안·이후 결정론 상태를 보존하는 것을 의미합니다.

## Canonical M3 proof / 공식 M3 증명

Two bounded flows MUST be demonstrated.

두 제한형 흐름을 반드시 증명합니다.

### A. Create / 생성

```text
"Create a restrained dark electronic 20-second technology cue"
        ↓
Director Request
        ↓
Provider proposal
        ↓
validated Music Intent v0
        ↓
M1 Blueprint Composer
        ↓
validated Blueprint R1
        ↓
M2 project commit
        ↓
MIDI/WAV evidence
```

### B. Edit / 수정

```text
"Make the final section more urgent but keep tempo, melody and drum identity"
        ↓
Director Request + exact project revision context
        ↓
Provider proposal
        ↓
validated Semantic Control v0
        ↓
M1 semantic resolver
        ↓
HARD lock check
        ↓
Blueprint R2
        ↓
M2 branch/commit + diff + artifact binding
```

A deliberately malicious or malformed provider proposal MUST be rejected before it can become canonical state.

의도적으로 악의적이거나 잘못된 provider 제안은 공식 상태가 되기 전에 반드시 거부되어야 합니다.

## M3 non-goals / M3 비목표

M3 does not yet require a polished chat UI, autonomous long-running agent behavior, provider fine-tuning, model training, universal natural-language music understanding, direct DAW control, production mastering, or cloud collaboration.

M3는 아직 완성형 채팅 UI, 장기 자율 에이전트, provider fine-tuning, 모델 학습, 보편 자연어 음악 이해, 직접 DAW 제어, 상용 마스터링, 클라우드 협업을 요구하지 않습니다.

## Product sequence after M3 / M3 이후 제품 순서

```text
M3 AI Music Director Provider Layer
→ M4 MUSICA Studio usable application MVP
→ M5 Renderer/DAW interoperability & quality expansion
→ M6 Product hardening / packaging / release candidate
```

## Development discipline / 개발 규율

```text
Issue → Branch → Contract → Implementation → Tests → PR → exact-head CI → Evidence → Merge → State update
```

Repository-backed contracts and evidence remain authoritative over conversation or model memory.

레포 기반 계약과 근거는 계속해서 대화 또는 모델 기억보다 우선합니다.
