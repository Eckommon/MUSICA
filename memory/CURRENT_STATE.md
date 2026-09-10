# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M3-R1 — AI MUSIC DIRECTOR PROVIDER BOUNDARY: VALIDATED / M3-R1 — AI Music Director Provider 경계: 검증 완료**

M0, M1, and M2 remain validated. M3-R1 adds a provider-neutral, non-authoritative AI Music Director proposal boundary above the deterministic/lock-aware core.

M0, M1, M2는 계속 검증 상태입니다. M3-R1은 결정론·lock-aware 코어 위에 provider-neutral·비권위 AI Music Director proposal 경계를 추가했습니다.

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
- exact final-head CI run: `34513681557`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- M0/M1/M2/M3-R1 evidence generation/upload: **SUCCESS**
- final M3-R1 artifact: `musica-m3-r1-director-boundary`, ID `10166839248`
- final artifact digest: `sha256:86b1798836d9e14880091b2ddd1b40e46c5a1247c2fd426b02ef3542d445d989`
- implementation merge: `327a6b68f844e7ee4ab67c1ebe571a7ad48117bd`
- durable evidence: `evidence/M3_R1_VALIDATION.md`
- acceptance: `docs/M3_R1_ACCEPTANCE.md`
- runtime: `docs/M3_R1_RUNTIME.md`
- status: **VALIDATED**

## Validated capabilities / 검증된 기능

The following claims are evidence-backed only within bounded M0→M3-R1 contracts.

다음 주장은 제한된 M0→M3-R1 계약 범위에서만 근거로 검증되었습니다.

- strict Music Intent, Music Blueprint, Semantic Control, Music IR contracts / 엄격한 핵심 음악 계약
- deterministic Intent → Blueprint composition / 결정론 Intent → Blueprint 작곡
- six-axis semantic editing with HARD-lock/constraint fail-closed validation / 6축 semantic 수정 및 HARD lock·constraint 실패 폐쇄
- deterministic MIDI and bounded local WAV preview / 결정론 MIDI·제한형 로컬 WAV 프리뷰
- Git-independent `.musica` Project Bundle with immutable revisions, branches/refs, hashes, audit, artifact binding, export/import / Git 독립 `.musica` Project Bundle
- strict Director Provider Capability, Request, Proposal, Trace contracts / 엄격한 Director provider/request/proposal/trace 계약
- provider-neutral create path: user language → typed proposal → validated Music Intent → M1 Blueprint / provider-neutral 생성 경로
- provider-neutral edit path: language + exact revision context → typed proposal → Semantic Control → lock-aware candidate / provider-neutral 수정 경로
- explicit user-hint precedence over AI inference / 명시 사용자 hint의 AI 추론 대비 우선권
- exact Blueprint SHA/context binding for edits / 수정 시 정확한 Blueprint SHA/context 결속
- provider capability and identity enforcement / provider 역량·식별자 검증
- provider resolution side-effect freedom before explicit M2 commit / 명시 M2 commit 전 provider resolution side-effect 차단
- request/proposal/capability/accepted-contract SHA-256 provenance trace / SHA-256 provenance trace
- fail-closed rejection of canonical-state injection, arbitrary patch injection, stale context, metadata spoofing, undeclared capability use, and unsupported semantic axes / 권한 우회 시도 실패 폐쇄

## Canonical authority rule / 공식 권한 규칙

**AI providers may propose; they do not own canonical state.**

**AI provider는 제안할 수 있지만 공식 상태를 소유하지 않습니다.**

```text
User language
→ Director Request
→ AI Provider (proposal only)
→ typed proposal validation
→ trusted Music Intent / Semantic Control
→ deterministic MUSICA core
→ HARD lock / constraint validation
→ explicit M2 commit
→ Accepted Blueprint Revision
```

Accepted explicit user intent and constraints outrank provider inference. HARD locks outrank semantic optimization. A provider cannot directly overwrite an accepted Blueprint or mutate `.musica` refs.

승인된 명시 사용자 의도·제약은 provider 추론보다 우선하고 HARD lock은 semantic 최적화보다 우선합니다. Provider는 승인 Blueprint를 직접 덮어쓰거나 `.musica` ref를 변경할 수 없습니다.

## Claim boundaries / 주장 경계

M3-R1 does **not** validate or imply:

M3-R1은 다음을 검증하거나 암시하지 않습니다.

- live OpenAI or other external-network provider execution / 실제 OpenAI·외부 네트워크 provider 실행,
- arbitrary free-form natural-language understanding / 임의 자유형 자연어 이해,
- deterministic external LLM output / 외부 LLM 출력 결정론성,
- autonomous long-running agent behavior / 장기 자율 에이전트,
- AI authority over accepted state / 승인 상태에 대한 AI 권위,
- production/mastering audio quality / 상용 제작·마스터링 음질,
- polished application/chat UI / 완성형 앱·채팅 UI,
- professional renderer/VST/sampler interoperability / 전문 renderer·VST·sampler 상호운용.

`FixtureMusicDirectorProvider` validates the provider contract/authority architecture only; it is not evidence of general AI music-direction quality.

`FixtureMusicDirectorProvider`는 provider 계약·권한 아키텍처만 검증하며 범용 AI 음악 디렉팅 품질의 근거가 아닙니다.

## Evidence status / 근거 상태

- Core product proposition: **ACCEPTED**
- Foundation design package v0.1: **ACCEPTED**
- Repository SoT contract: **IMPLEMENTED**
- M0 milestone: **VALIDATED**
- M1 milestone: **VALIDATED**
- M2 milestone: **VALIDATED**
- M3-R1 provider-neutral Director boundary: **IMPLEMENTED + TESTED + MERGED + VALIDATED**
- Live OpenAI provider adapter: **NOT IMPLEMENTED**
- User application/UI: **NOT IMPLEMENTED**
- Production renderer adapters: **NOT IMPLEMENTED**

## Resume authority / 재개 권위

Before substantive work inspect, in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. normative design specifications / 규범 설계 명세
5. M0/M1/M2 acceptance + durable evidence
6. `docs/M3_R1_ACCEPTANCE.md`
7. `evidence/M3_R1_VALIDATION.md`
8. this file / 본 파일
9. `memory/NEXT_ACTION.md`
10. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

Repository evidence remains authoritative over conversation or model memory.

레포 근거는 계속해서 대화 또는 모델 기억보다 우선합니다.
