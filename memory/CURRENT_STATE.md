# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M1 — CREATIVE CORE v0: VALIDATED / M1 — 창작 코어 v0: 검증 완료**

M0 remains validated. M1 now adds a bounded, deterministic Intent → Music Blueprint creative path, three explicit style profiles, and a six-axis semantic runtime. The implementation is merged and exact-head repository CI satisfies the M1 acceptance gate.

M0는 계속 검증 상태입니다. M1은 제한형·결정론적 Intent → Music Blueprint 창작 경로, 세 개의 명시적 스타일 프로필, 6축 semantic 런타임을 추가했습니다. 구현은 병합되었고 exact-head 레포 CI가 M1 수용 게이트를 충족합니다.

## Canonical core proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

## Canonical milestone evidence / 공식 마일스톤 근거

### M0

- M0-R1 merge / 병합: `5260f29c62a39bd0912532ca99e54c79f40046a6`
- M0-R2 merge / 병합: `b8132d8524fec5fc9f22214a9fa4aee21849379b`
- Durable evidence / 영속 근거: `evidence/M0_R2_VALIDATION.md`
- Acceptance / 수용 계약: `docs/M0_ACCEPTANCE.md`
- Status / 상태: **VALIDATED**

### M1

- Implementation PR / 구현 PR: `#8`
- M1 implementation merge / 구현 병합: `a189f34e9c6d6843fecba03a8086c907c445c18d`
- Exact pre-merge head / 정확한 병합 전 HEAD: `7243a9f127dedde42fa384793cc0d7df0b754f44`
- Exact-head CI run: **34508569414**
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- M0 regression evidence generation: **SUCCESS**
- M1 evidence generation/upload: **SUCCESS**
- Final-run M1 artifact: `musica-m1-creative-core`, ID **10164873827**
- Final-run artifact digest: `sha256:d3b9d93ded835b0b5a03a4fa1cf4b06cf8bb0ce47ba61beb516573757ed710b8`
- Durable evidence / 영속 근거: `evidence/M1_VALIDATION.md`
- Acceptance / 수용 계약: `docs/M1_ACCEPTANCE.md`
- Runtime description / 런타임 설명: `docs/M1_RUNTIME.md`
- Status / 상태: **VALIDATED**

## Validated capabilities / 검증된 기능

The following claims are evidence-backed only within the bounded M0/M1 contracts.

다음 주장은 제한된 M0/M1 계약 범위에서만 근거로 검증되었습니다.

- strict Music Blueprint v0 and Music Intent v0 machine contracts / 엄격한 Music Blueprint v0 및 Music Intent v0 기계 계약
- deterministic Intent → Creative Plan → Blueprint composition / 결정론적 Intent → Creative Plan → Blueprint 작곡
- SHA-256-derived seed material selection / SHA-256 파생 seed 기반 음악 재료 선택
- three bounded style profiles: `dark_electronic`, `warm_ambient`, `kinetic_minimal` / 세 제한형 스타일 프로필
- six implemented semantic axes: `energy`, `tension`, `density`, `motion`, `brightness`, `warmth` / 6개 구현 semantic 축
- explicit semantic mechanism registry and structured revision diffs / 명시적 semantic 메커니즘 registry 및 구조화 리비전 diff
- HARD tempo, melody-identity-token, and rhythm-identity-token fail-closed preservation / HARD tempo·멜로디 identity token·리듬 identity token 실패 폐쇄 보존
- profile-aware Blueprint → Music IR compilation / 프로필 인지 Blueprint → Music IR 컴파일
- deterministic Standard MIDI output / 결정론 Standard MIDI 출력
- deterministic local audible WAV preview with bounded timbre controls / 제한형 음색 제어를 포함한 결정론 로컬 청취 WAV 프리뷰
- reproducible SHA-256 evidence bundles / 재현 가능한 SHA-256 근거 번들
- M0 regression preservation under M1 / M1에서 M0 회귀 보존

## Claim boundaries / 주장 경계

M1 does **not** validate or imply:

M1은 다음을 검증하거나 암시하지 않습니다.

- arbitrary free-form natural-language music understanding / 임의 자유형 자연어 음악 이해
- universal genre or emotion modeling / 보편적 장르·감정 모델링
- general composition intelligence / 범용 작곡 지능
- production/mastering audio quality / 상용 제작·마스터링 음질
- perceptual melody identity / 지각적 멜로디 동일성
- persistent user project/version storage / 사용자 프로젝트·버전 영속 저장
- AI Music Director provider integration / AI Music Director provider 통합
- full DAW functionality or polished application UI / 완전한 DAW 기능 또는 완성형 앱 UI
- professional renderer/VST/sampler interoperability / 전문 renderer·VST·sampler 상호운용

## Evidence status / 근거 상태

- Core product proposition: **ACCEPTED**
- Foundation design package v0.1: **ACCEPTED**
- Repository SoT contract: **IMPLEMENTED**
- M0 milestone: **VALIDATED**
- Music Intent v0 contract: **IMPLEMENTED + TESTED + MERGED**
- Creative Planner / Blueprint Composer: **IMPLEMENTED + TESTED + MERGED**
- Three bounded style profiles: **IMPLEMENTED + TESTED + MERGED**
- Six-axis semantic runtime: **IMPLEMENTED + TESTED + MERGED**
- Profile-aware compiler and semantic preview rendering: **IMPLEMENTED + TESTED + MERGED**
- M1 milestone: **VALIDATED**
- Persistent project/version store: **NOT IMPLEMENTED**
- Revision branching/refs/user project integrity engine: **NOT IMPLEMENTED**
- AI Music Director provider integration: **NOT IMPLEMENTED**
- User application/UI: **NOT IMPLEMENTED**
- Production renderer adapters: **NOT IMPLEMENTED**

## Resume authority / 재개 권위

Before substantive work inspect, in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. normative design specifications / 규범 설계 명세
5. `docs/M0_ACCEPTANCE.md`
6. `evidence/M0_R2_VALIDATION.md`
7. `docs/M1_ACCEPTANCE.md`
8. `evidence/M1_VALIDATION.md`
9. this file / 본 파일
10. `memory/NEXT_ACTION.md`
11. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

Repository evidence remains authoritative over conversation or model memory.

레포 근거는 계속해서 대화 또는 모델 기억보다 우선합니다.
