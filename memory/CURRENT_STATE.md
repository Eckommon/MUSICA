# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M0 — CONTROLLABLE MUSIC BLUEPRINT / M0 — 제어 가능한 음악 설계도**

Foundation design is accepted. M0-R1 executable contracts are implemented and tested; compiler/rendering work belongs to M0-R2.

기반 설계는 승인되었습니다. M0-R1 실행 계약은 구현 및 테스트되었으며, 컴파일·렌더링 작업은 M0-R2 범위입니다.

## Canonical core proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

## Accepted foundation package / 승인 기반 패키지

- `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
- `docs/design/ARCHITECTURE_v0.1.md`
- `docs/design/MUSIC_BLUEPRINT_v0.md`
- `docs/design/SEMANTIC_CONTROL_MODEL_v0.md`
- `docs/design/LOCK_CONSTRAINT_MODEL_v0.md`

Status / 상태: **ACCEPTED-FOUNDATION**.

## M0-R1 evidence / M0-R1 근거

Implemented / 구현됨:

- `schemas/music-blueprint-v0.schema.json`
- `schemas/semantic-control-v0.schema.json`
- `schemas/lock-constraint-v0.schema.json`
- `schemas/music-ir-v0.schema.json`
- `src/musica/contracts.py`
- canonical valid/invalid examples / 공식 정상·비정상 예제
- `tests/test_contracts.py`
- `.github/workflows/contracts.yml`
- `docs/M0_ACCEPTANCE.md`

Validated CI evidence / 검증된 CI 근거:

- GitHub Actions workflow: `MUSICA Contracts`
- Run: **34504587688**
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**

## Accepted architectural decisions / 승인 아키텍처 결정

1. Natural language is an input surface, not canonical state. / 자연어는 입력 인터페이스이며 공식 상태 자체가 아님.
2. `Music Blueprint` is the human/AI-facing canonical creative state. / `Music Blueprint`는 인간·AI 대상 공식 창작 상태.
3. `Music IR` is a separate lower-level executable representation. / `Music IR`은 별도의 하위 실행 표현.
4. Semantic v0 vocabulary is bounded and normalized; subjective values are controls, not scientific ground truth. / 의미 v0 어휘는 제한·정규화되며 주관 값은 과학적 절대값이 아니라 제어값.
5. Lock and constraint targets use JSON Pointer paths in M0. / M0 lock·constraint target은 JSON Pointer 경로를 사용.
6. HARD locks fail closed and inherited HARD lock semantics cannot be silently removed or weakened. / HARD lock은 실패 폐쇄하며 상속 의미를 몰래 제거·약화할 수 없음.
7. v0 identity lock proves explicit identity-token preservation only; perceptual melody equivalence is not yet claimed. / v0 identity lock은 명시 identity-token 보존만 증명하며 지각적 멜로디 동일성은 아직 주장하지 않음.
8. Renderer backends remain adapters to the core. / 렌더러 백엔드는 코어의 어댑터로 유지.

## Evidence status / 근거 상태

- Core product proposition: **ACCEPTED**
- Foundation design package v0.1: **ACCEPTED**
- Repository SoT contract: **IMPLEMENTED**
- Blueprint JSON Schema v0: **IMPLEMENTED + TESTED**
- Semantic Control contract v0: **IMPLEMENTED + TESTED**
- Lock/Constraint contract v0: **IMPLEMENTED + TESTED**
- Music IR schema v0: **IMPLEMENTED + TESTED (schema only)**
- Cross-field/revision contract validator: **IMPLEMENTED + TESTED**
- HARD lock/constraint fail-closed behavior: **TESTED at contract level**
- Compiler Blueprint → Music IR: **NOT IMPLEMENTED**
- Semantic resolver: **NOT IMPLEMENTED**
- Structured diff/provenance engine: **NOT IMPLEMENTED**
- MIDI renderer: **NOT IMPLEMENTED**
- WAV renderer: **NOT IMPLEMENTED**
- Application/UI: **NOT IMPLEMENTED**

## Resume authority / 재개 권위

Before substantive work inspect, in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. normative design specifications / 규범 설계 명세
5. `docs/M0_ACCEPTANCE.md`
6. this file / 본 파일
7. `memory/NEXT_ACTION.md`
8. relevant Issue/PR/workflow evidence / 관련 Issue·PR·workflow 근거

Never infer runtime capability from schema/design acceptance alone.

스키마·설계 승인만으로 런타임 기능을 추론하지 않습니다.
