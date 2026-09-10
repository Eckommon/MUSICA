# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M0 — CONTROLLABLE MUSIC BLUEPRINT: VALIDATED / M0 — 제어 가능한 음악 설계도: 검증 완료**

M0-R1 executable contracts and M0-R2 minimal deterministic runtime are merged and repository-backed evidence satisfies the M0 acceptance gate.

M0-R1 실행 계약과 M0-R2 최소 결정론 런타임이 병합되었고, 레포 기반 근거가 M0 수용 게이트를 충족합니다.

## Canonical core proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

## M0 canonical evidence / M0 공식 근거

- M0-R1 merge / 병합: `5260f29c62a39bd0912532ca99e54c79f40046a6`
- M0-R2 merge / 병합: `b8132d8524fec5fc9f22214a9fa4aee21849379b`
- M0-R2 validated PR CI / 검증 PR CI: `34505670926` — Python 3.11 **SUCCESS**, Python 3.12 **SUCCESS**, evidence generation/upload **SUCCESS**
- Durable record / 영속 근거: `evidence/M0_R2_VALIDATION.md`
- M0 acceptance contract / 수용 계약: `docs/M0_ACCEPTANCE.md`

## Validated capabilities / 검증된 기능

The following are repository-evidenced at M0 scope only.

다음 항목은 M0 범위에서만 레포 근거로 검증되었습니다.

- strict Music Blueprint v0 machine contract / 엄격한 Music Blueprint v0 기계 계약
- bounded Semantic Control v0 contract / 제한된 Semantic Control v0 계약
- HARD lock and constraint fail-closed validation / HARD lock·constraint 실패 폐쇄 검증
- separate Music IR v0 contract / 분리된 Music IR v0 계약
- deterministic structured Blueprint diff / 결정론 구조화 Blueprint diff
- bounded runtime `tension` semantic edit / 제한된 런타임 `tension` 의미 수정
- deterministic Blueprint → Music IR compiler / 결정론 Blueprint → Music IR 컴파일러
- deterministic Standard MIDI File output / 결정론 Standard MIDI File 출력
- deterministic free/local audible PCM WAV preview / 결정론 무료·로컬 청취 PCM WAV 프리뷰
- SHA-256 evidence manifest and reproducibility tests / SHA-256 근거 manifest 및 재현성 테스트

## Claim boundaries / 주장 경계

M0 does **not** validate or imply:

M0는 다음을 검증하거나 암시하지 않습니다.

- production-quality audio generation / 상용 수준 오디오 생성
- arbitrary natural-language music understanding / 임의 자연어 음악 이해
- general composition intelligence / 범용 작곡 지능
- perceptual melody identity / 지각적 멜로디 동일성
- full DAW functionality / 완전한 DAW 기능
- VST hosting or professional sampler integration / VST hosting 또는 전문 sampler 통합
- external generative-audio backend integration / 외부 생성형 오디오 백엔드 통합
- polished application UI / 완성형 앱 UI

## Evidence status / 근거 상태

- Core product proposition: **ACCEPTED**
- Foundation design package v0.1: **ACCEPTED**
- Repository SoT contract: **IMPLEMENTED**
- M0-R1 executable contracts: **IMPLEMENTED + TESTED + MERGED**
- M0-R2 deterministic runtime loop: **IMPLEMENTED + TESTED + MERGED**
- M0 milestone: **VALIDATED**
- General intent → Blueprint generation: **NOT IMPLEMENTED**
- Multi-axis semantic runtime: **NOT IMPLEMENTED**
- Persistent project/version store: **NOT IMPLEMENTED**
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
7. this file / 본 파일
8. `memory/NEXT_ACTION.md`
9. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

Repository evidence remains authoritative over conversation or model memory.

레포 근거는 계속해서 대화 또는 모델 기억보다 우선합니다.
