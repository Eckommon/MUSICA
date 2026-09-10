# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M2 — PROJECT & VERSION ENGINE v0: VALIDATED / M2 — 프로젝트·버전 엔진 v0: 검증 완료**

M0 and M1 remain validated. M2 adds a Git-independent user Project Bundle with immutable accepted revisions, branch refs, content-addressed objects, exact-revision artifact binding, deterministic export/import, and fail-closed integrity verification.

M0와 M1은 계속 검증 상태입니다. M2는 Git과 독립된 사용자 Project Bundle을 추가하며, 불변 승인 리비전, branch ref, content-addressed object, 정확한 리비전별 산출물 결속, 결정론 export/import, 실패 폐쇄 무결성 검증을 제공합니다.

## Canonical core proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

## Canonical milestone evidence / 공식 마일스톤 근거

### M0

- M0-R1 merge / 병합: `5260f29c62a39bd0912532ca99e54c79f40046a6`
- M0-R2 merge / 병합: `b8132d8524fec5fc9f22214a9fa4aee21849379b`
- Durable evidence / 영속 근거: `evidence/M0_R2_VALIDATION.md`
- Status / 상태: **VALIDATED**

### M1

- Implementation PR / 구현 PR: `#8`
- Implementation merge / 구현 병합: `a189f34e9c6d6843fecba03a8086c907c445c18d`
- Exact pre-merge head / 정확한 병합 전 HEAD: `7243a9f127dedde42fa384793cc0d7df0b754f44`
- Exact-head CI run: `34508569414`
- Final M1 artifact / 최종 M1 산출물: `musica-m1-creative-core`, ID `10164873827`
- Durable evidence / 영속 근거: `evidence/M1_VALIDATION.md`
- Status / 상태: **VALIDATED**

### M2

- Implementation PR / 구현 PR: `#12`
- Exact pre-merge head / 정확한 병합 전 HEAD: `6c22bb11ee6fc49c09e8c155907b95a3c0158cac`
- Exact-head CI run: `34510135960`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- M0 regression evidence: **SUCCESS**
- M1 regression evidence: **SUCCESS**
- M2 evidence generation/upload: **SUCCESS**
- Final M2 artifact / 최종 M2 산출물: `musica-m2-project-version`, ID `10165479188`
- Final M2 artifact digest / 최종 M2 산출물 digest: `sha256:8b59cbe3f2233cfe0d381089867180c7c1495e4ad333ca3fb88f7fec89a53e66`
- Implementation merge / 구현 병합: `e439d884f53ed9f36b6e8b62232c07e0d4cfed4c`
- Durable evidence / 영속 근거: `evidence/M2_VALIDATION.md`
- Acceptance / 수용 계약: `docs/M2_ACCEPTANCE.md`
- Runtime description / 런타임 설명: `docs/M2_RUNTIME.md`
- Status / 상태: **VALIDATED**

## Validated capabilities / 검증된 기능

The following claims are evidence-backed only within the bounded M0/M1/M2 contracts.

다음 주장은 제한된 M0/M1/M2 계약 범위에서만 레포 근거로 검증되었습니다.

- strict Music Blueprint v0 and Music Intent v0 machine contracts / 엄격한 Music Blueprint v0·Music Intent v0 기계 계약
- deterministic Intent → Creative Plan → Blueprint composition / 결정론 Intent → Creative Plan → Blueprint 작곡
- three bounded style profiles and six-axis semantic runtime / 세 제한형 스타일 프로필 및 6축 semantic 런타임
- HARD tempo, melody-identity-token, rhythm-identity-token fail-closed preservation / HARD tempo·멜로디 identity token·리듬 identity token 실패 폐쇄 보존
- profile-aware Blueprint → Music IR compilation / 프로필 인지 Blueprint → Music IR 컴파일
- deterministic MIDI and bounded local WAV preview / 결정론 MIDI 및 제한형 로컬 WAV 프리뷰
- Git-independent `.musica` Project Bundle / Git 독립 `.musica` Project Bundle
- immutable accepted Blueprint revisions / 불변 승인 Blueprint 리비전
- content-addressed SHA-256 object storage / SHA-256 content-addressed object 저장
- lightweight branches/refs with explicit advancement / 명시적 전진을 갖는 경량 branch·ref
- stored lineage, structured diff, actor/reason, and logical audit sequence / 저장된 계보·구조화 diff·actor/reason·논리 audit sequence
- exact-revision MIDI/WAV artifact hash binding / 정확한 리비전별 MIDI/WAV 해시 결속
- hash-chained audit history / 해시 체인 audit history
- full-project integrity verification and tamper fail-closed behavior / 전체 프로젝트 무결성 검증 및 변조 실패 폐쇄
- deterministic ZIP export/import with byte-identical re-export under canonical M2 evidence / 공식 M2 근거에서 결정론 ZIP export/import 및 byte-identical 재-export
- M0/M1 regression preservation under M2 / M2에서 M0/M1 회귀 보존

## Claim boundaries / 주장 경계

M2 does **not** validate or imply:

M2는 다음을 검증하거나 암시하지 않습니다.

- arbitrary free-form natural-language music understanding / 임의 자유형 자연어 음악 이해
- live LLM/provider integration / 실제 LLM/provider 통합
- AI-generated proposals being authoritative without validation / 검증 없는 AI 제안의 권위
- universal genre or emotion modeling / 보편적 장르·감정 모델링
- production/mastering audio quality / 상용 제작·마스터링 음질
- cryptographic signer authenticity or non-repudiation / 암호학적 서명자 진위·부인방지
- cloud collaboration, account sync, or CRDT editing / 클라우드 협업·계정 동기화·CRDT 편집
- full DAW functionality or polished application UI / 완전한 DAW 기능·완성형 앱 UI
- professional renderer/VST/sampler interoperability / 전문 renderer·VST·sampler 상호운용

## Evidence status / 근거 상태

- Core product proposition: **ACCEPTED**
- Foundation design package v0.1: **ACCEPTED**
- Repository SoT contract: **IMPLEMENTED**
- M0 milestone: **VALIDATED**
- M1 milestone: **VALIDATED**
- M2 Project & Version Engine: **IMPLEMENTED + TESTED + MERGED + VALIDATED**
- Persistent project/version store: **IMPLEMENTED + TESTED + MERGED**
- Revision branching/refs/user project integrity engine: **IMPLEMENTED + TESTED + MERGED**
- Deterministic project export/import: **IMPLEMENTED + TESTED + MERGED**
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
9. `docs/M2_ACCEPTANCE.md`
10. `evidence/M2_VALIDATION.md`
11. this file / 본 파일
12. `memory/NEXT_ACTION.md`
13. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

Repository evidence remains authoritative over conversation or model memory.

레포 근거는 계속해서 대화 또는 모델 기억보다 우선합니다.
