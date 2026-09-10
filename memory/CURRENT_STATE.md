# Current State / 현재 상태

## Project phase / 프로젝트 단계

**FOUNDATION DESIGN ACCEPTED / 기반 설계 승인**

The product thesis and foundation design package are accepted. Software implementation has not started.

제품 명제와 기반 설계 패키지는 승인되었습니다. 소프트웨어 구현은 아직 시작하지 않았습니다.

## Canonical core proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

## Accepted foundation package / 승인된 기반 패키지

The following are **ACCEPTED-FOUNDATION**, not implemented software:

다음 항목은 **기반 설계 승인** 상태이며 구현 완료를 의미하지 않습니다.

- `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
- `docs/design/ARCHITECTURE_v0.1.md`
- `docs/design/MUSIC_BLUEPRINT_v0.md`
- `docs/design/SEMANTIC_CONTROL_MODEL_v0.md`
- `docs/design/LOCK_CONSTRAINT_MODEL_v0.md`

## Accepted architectural decisions / 승인 아키텍처 결정

1. Natural language is an input surface, not canonical state. / 자연어는 입력 인터페이스이지 공식 상태가 아님.
2. `Music Blueprint` is the human/AI-facing canonical creative state. / `Music Blueprint`가 인간/AI 대상 공식 창작 상태.
3. `Music IR` is a lower-level executable representation produced by compilation. / `Music IR`은 컴파일로 생성되는 저수준 실행 표현.
4. Hard locks are invariants and fail closed on violation. / Hard lock은 불변조건이며 위반 시 실패 폐쇄.
5. Semantic edits resolve to explicit candidate deltas before mutation. / 의미 수정은 변경 전에 명시적 후보 delta로 해석.
6. Renderer backends are adapters to the core. / 렌더러 백엔드는 코어의 어댑터.
7. Direct, Shape, Inspect, and Code are views over one canonical project state. / Direct·Shape·Inspect·Code는 하나의 공식 상태를 공유.
8. Accepted revisions preserve diff and provenance. / 승인 리비전은 diff와 provenance를 보존.

## Evidence status / 근거 상태

- Core product proposition: **ACCEPTED**
- Product thesis: **ACCEPTED**
- Foundation design package v0.1: **ACCEPTED**
- Repository SoT contract: **IMPLEMENTED**
- Conceptual Music Blueprint v0: **ACCEPTED**
- Conceptual Semantic Control Model v0: **ACCEPTED**
- Conceptual Lock/Constraint Model v0: **ACCEPTED**
- Concrete Blueprint JSON Schema: **NOT IMPLEMENTED**
- Music IR schema: **NOT IMPLEMENTED**
- Compiler: **NOT IMPLEMENTED**
- Constraint engine: **NOT IMPLEMENTED**
- Semantic resolver: **NOT IMPLEMENTED**
- Diff/provenance engine: **NOT IMPLEMENTED**
- Renderer adapters: **NOT IMPLEMENTED**
- Application/UI: **NOT IMPLEMENTED**
- Audio generation pipeline: **NOT IMPLEMENTED**
- Automated tests: **NOT IMPLEMENTED**

## Product positioning / 제품 포지셔닝

MUSICA is an **AI-native programmable music workstation** centered on intent, structured creative state, semantic control, locks/constraints, explainable revisions, reproducibility, and renderer independence. It is not defined by matching another service feature-for-feature.

MUSICA는 의도, 구조화 창작 상태, 의미 제어, lock/constraint, 설명 가능한 리비전, 재현성, 렌더러 독립성을 중심으로 하는 **AI-native programmable music workstation**입니다. 타 서비스와의 기능 일대일 비교로 제품을 정의하지 않습니다.

## Resume authority / 재개 권위

For the next session, inspect in order:

다음 세션에서는 순서대로 확인합니다.

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. the four normative design specifications / 네 규범 설계 명세
5. this file / 본 파일
6. `memory/NEXT_ACTION.md`

Do not infer implementation from accepted design documentation.

승인된 설계 문서만으로 구현 상태를 추론하지 않습니다.
