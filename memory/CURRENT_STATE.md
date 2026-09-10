# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M3 — AI MUSIC DIRECTOR PROVIDER LAYER: VALIDATED (BOUNDED) / M3 — AI Music Director Provider 계층: 제한 범위 검증 완료**

M0, M1, and M2 remain validated. M3 now adds both a provider-neutral AI Music Director authority boundary and a live-ready OpenAI Responses adapter contract. The validated M3 claim is deliberately bounded: **offline adapter-contract execution is validated; an actual live OpenAI network call is not yet validated evidence.**

M0, M1, M2는 계속 검증 상태입니다. M3는 provider-neutral AI Music Director 권한 경계와 live-ready OpenAI Responses adapter 계약을 추가했습니다. M3 검증 주장은 의도적으로 제한됩니다. **offline adapter-contract 실행은 검증되었지만 실제 OpenAI live 네트워크 호출은 아직 검증 근거가 아닙니다.**

## Canonical core proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

## Canonical milestone evidence / 공식 마일스톤 근거

### M0 — VALIDATED

- M0-R1 merge: `5260f29c62a39bd0912532ca99e54c79f40046a6`
- M0-R2 merge: `b8132d8524fec5fc9f22214a9fa4aee21849379b`
- durable evidence: `evidence/M0_R2_VALIDATION.md`

### M1 — VALIDATED

- implementation PR: `#8`
- implementation merge: `a189f34e9c6d6843fecba03a8086c907c445c18d`
- exact-head CI: `34508569414`
- durable evidence: `evidence/M1_VALIDATION.md`

### M2 — VALIDATED

- implementation PR: `#12`
- exact final head: `6c22bb11ee6fc49c09e8c155907b95a3c0158cac`
- exact-head CI: `34510135960`
- final artifact: `musica-m2-project-version`, ID `10165479188`
- implementation merge: `e439d884f53ed9f36b6e8b62232c07e0d4cfed4c`
- closure merge: `989b5e9209f02a9cba7b3a4468c0c105a9fc71b3`
- durable evidence: `evidence/M2_VALIDATION.md`

### M3-R1 — VALIDATED

- implementation PR: `#16`
- exact final head: `090bc9aa9cd4554a2240689af5f992fbd805332d`
- exact-head CI: `34513681557`
- final artifact: `musica-m3-r1-director-boundary`, ID `10166839248`
- implementation merge: `327a6b68f844e7ee4ab67c1ebe571a7ad48117bd`
- closure merge: `5ad40f86f9bf596688e90391c72d799bd480fe60`
- durable evidence: `evidence/M3_R1_VALIDATION.md`
- status: **VALIDATED**

### M3-R2 — VALIDATED AS ADAPTER CONTRACT / ADAPTER 계약으로 검증 완료

- implementation PR: `#20`
- exact final head: `771dabaae99c9c1775fdd720edb3a6a94d3af395`
- exact-head PR CI: `34539071018`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- M0/M1/M2/M3-R1/M3-R2 evidence generation/upload: **SUCCESS**
- final artifact: `musica-m3-r2-openai-adapter`, ID `10176581649`
- final artifact digest: `sha256:e2449edbd7365c70a588e36b481a6baa03130d6b12aa5d3bbfa08183f8c7d2d6`
- implementation merge: `d93b63037ad8dac9c90f12a8b218765c89bf93bc`
- durable evidence: `evidence/M3_R2_VALIDATION.md`
- evidence class: `ADAPTER_CONTRACT_EVIDENCE`
- actual live OpenAI call validated: **NO**

## Validated capabilities / 검증된 기능

The following claims are evidence-backed only within bounded M0→M3 contracts. / 다음 주장은 제한된 M0→M3 계약 범위에서만 레포 근거로 검증되었습니다.

- strict Music Intent, Music Blueprint, Semantic Control, Music IR contracts / 엄격한 핵심 음악 계약
- deterministic Intent → Blueprint composition / 결정론 Intent → Blueprint 작곡
- three bounded style profiles and six semantic axes / 세 제한형 스타일 프로필·6축 의미 제어
- HARD-lock/constraint fail-closed revision validation / HARD lock·constraint 실패 폐쇄 리비전 검증
- deterministic MIDI and bounded local WAV preview / 결정론 MIDI·제한형 로컬 WAV 프리뷰
- Git-independent `.musica` Project Bundle with immutable revisions, refs, integrity, audit and export/import / Git 독립 프로젝트 저장·버전 엔진
- provider-neutral Director Request/Proposal/Trace boundary / provider-neutral Director 경계
- user explicit intent outranks provider inference / 사용자 명시 의도 우선권
- exact revision/context binding for AI edits / AI 수정의 정확한 리비전·context 결속
- provider output cannot directly mutate accepted Blueprint/project state / provider의 공식 상태 직접 변경 차단
- OpenAI Responses adapter payload construction with strict mode-specific structured-output contracts / OpenAI Responses adapter의 제한형 구조화 출력 계약
- model creative body → MUSICA-owned Director Proposal reconstruction / 모델 creative body → MUSICA 소유 Proposal 재구성
- environment-only live credential boundary / 환경변수 기반 live credential 경계
- dependency-injected no-network/no-secret adapter testing / network·secret 없는 주입형 adapter 테스트
- bounded retry and classified fail-closed handling for auth/rate-limit/server/timeout/transport/incomplete/refusal/invalid-output / 오류 분류·실패 폐쇄
- request/raw-response/structured-body/proposal SHA-256 exchange provenance / 교환 provenance
- explicit evidence separation between `ADAPTER_CONTRACT_EVIDENCE` and `LIVE_PROVIDER_EVIDENCE` / offline·live 근거 등급 분리

## Canonical authority rule / 공식 권한 규칙

**AI providers may propose; they never own canonical MUSICA state.**

**AI provider는 제안할 수 있지만 MUSICA 공식 상태를 소유하지 않습니다.**

```text
User language
→ Director Request
→ AI Provider / OpenAI adapter (proposal only)
→ strict structured body
→ MUSICA-owned Director Proposal
→ schema + authority validation
→ Music Intent / Semantic Control
→ deterministic MUSICA core
→ HARD lock / constraint validation
→ explicit Project Engine commit
→ Accepted Blueprint Revision
```

## Claim boundaries / 주장 경계

M3 does **not** validate or imply / M3는 다음을 검증하거나 암시하지 않습니다:

- successful live OpenAI API execution / 실제 OpenAI API 호출 성공,
- deterministic external model output / 외부 모델 출력 결정론성,
- universal free-form natural-language music understanding / 보편 자유형 자연어 음악 이해,
- autonomous AI authority over accepted state / 승인 상태에 대한 AI 자율 권한,
- production/mastering audio quality / 상용·마스터링급 음질,
- polished end-user Studio application / 완성형 사용자 Studio 앱,
- professional DAW/VST/sampler interoperability / 전문 DAW·VST·sampler 상호운용.

A future authorized live smoke run, if performed, MUST be recorded separately as `LIVE_PROVIDER_EVIDENCE`; it does not change the meaning of the validated offline adapter contract. / 향후 승인된 live smoke는 반드시 별도 `LIVE_PROVIDER_EVIDENCE`로 기록합니다.

## Evidence status / 근거 상태

- Core product proposition: **ACCEPTED**
- Foundation design package v0.1: **ACCEPTED**
- Repository SoT contract: **IMPLEMENTED**
- M0 milestone: **VALIDATED**
- M1 milestone: **VALIDATED**
- M2 milestone: **VALIDATED**
- M3-R1 provider-neutral Director boundary: **VALIDATED**
- M3-R2 OpenAI adapter contract: **IMPLEMENTED + TESTED + MERGED + VALIDATED (ADAPTER_CONTRACT_EVIDENCE)**
- M3 AI Music Director Provider Layer: **VALIDATED (BOUNDED)**
- Live OpenAI provider execution: **NOT VALIDATED**
- User application/UI: **NOT IMPLEMENTED**
- Production renderer/DAW adapters: **NOT IMPLEMENTED**

## Resume authority / 재개 권위

Before substantive work inspect, in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. normative design specifications / 규범 설계 명세
5. M0/M1/M2 acceptance + durable evidence
6. `docs/M3_R1_ACCEPTANCE.md` + `evidence/M3_R1_VALIDATION.md`
7. `docs/M3_R2_ACCEPTANCE.md` + `evidence/M3_R2_VALIDATION.md`
8. this file / 본 파일
9. `memory/NEXT_ACTION.md`
10. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 계속해서 대화 또는 모델 기억보다 우선합니다.
