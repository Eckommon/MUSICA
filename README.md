# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation** designed to make music creation easy through natural-language direction while preserving deep, professional, inspectable control when the user wants it.

MUSICA는 자연어 디렉팅으로 음악 제작을 쉽게 만들면서도, 사용자가 원할 때 전문가 수준의 깊고 검사 가능한 제어를 제공하는 **AI-native 프로그래머블 음악 워크스테이션**입니다.

## Product model / 제품 모델

MUSICA is not defined as a text-to-song clone or a renderer-specific DAW. Its core workflow is:

MUSICA는 text-to-song 복제 제품이나 특정 렌더러 전용 DAW로 정의하지 않습니다. 핵심 흐름은 다음과 같습니다.

```text
Intent / 의도
  ↓
AI Music Director / AI 음악 디렉터
  ↓
Music Blueprint / 음악 설계도
  ↓
Semantic Resolver + Locks + Constraints
의미 해석기 + 잠금 + 제약
  ↓
Validated Blueprint Revision + Diff
검증된 Blueprint 리비전 + Diff
  ↓
Music Compiler / 음악 컴파일러
  ↓
Music IR
  ↓
Renderer Adapters / 렌더러 어댑터
  ↓
MIDI / Synth / Sampler / DAW / DSP / Generative Audio
  ↓
Analyze → Evaluate → Revise
분석 → 평가 → 수정
```

## One state, four depths / 하나의 상태, 네 가지 깊이

- **Direct / 디렉팅** — natural language, references, semantic intent / 자연어, 참고자료, 의미 의도
- **Shape / 구조** — sections, roles, harmony, rhythm, semantic curves, locks / 구간, 역할, 화성, 리듬, 의미 곡선, 잠금
- **Inspect / 전문** — notes, events, automation, synthesis/mix details where supported / 음표, 이벤트, 오토메이션, 신시시스·믹스 세부
- **Code / 코드** — Blueprint, Music IR, API, CLI, programmable transforms / Blueprint, Music IR, API, CLI, 프로그래머블 변환

These are views over one canonical project state, not incompatible modes.

이는 서로 다른 비호환 모드가 아니라 하나의 공식 프로젝트 상태를 보는 네 가지 깊이입니다.

## Accepted foundation design / 승인된 기반 설계

The canonical foundation design package is:

공식 기반 설계 패키지는 다음과 같습니다.

- `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
- `docs/design/ARCHITECTURE_v0.1.md`
- `docs/design/MUSIC_BLUEPRINT_v0.md`
- `docs/design/SEMANTIC_CONTROL_MODEL_v0.md`
- `docs/design/LOCK_CONSTRAINT_MODEL_v0.md`

Important distinction / 중요 구분:

> **Music Blueprint = canonical human/AI creative state. / 인간·AI가 공유하는 공식 창작 상태.**
>
> **Music IR = lower-level executable representation produced by compilation. / 컴파일로 생성되는 저수준 실행 표현.**

## Repository role / 저장소 역할

This repository is both the implementation workspace and the canonical project memory/evidence layer.

이 저장소는 구현 작업 공간인 동시에 프로젝트의 공식 기억·근거 계층입니다.

Authority rule / 권위 규칙:

```text
Accepted repository artifacts/tests
> merged specs/current-state records
> issue/PR evidence
> conversation context
> model memory
> model inference
```

No AI agent may claim that a feature, test, milestone, artifact, or integration exists without repository evidence.

어떤 AI 에이전트도 레포 근거 없이 기능, 테스트, 마일스톤, 산출물 또는 통합이 존재한다고 주장해서는 안 됩니다.

Before substantive work, read:

실질 작업 전 다음을 읽습니다.

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. `memory/CURRENT_STATE.md`
5. `memory/NEXT_ACTION.md`

## Current status / 현재 상태

**FOUNDATION DESIGN ACCEPTED / 기반 설계 승인**

The product thesis and design package are accepted. Software implementation is **not yet implemented**.

제품 명제와 설계 패키지는 승인되었습니다. 소프트웨어 구현은 **아직 시작되지 않았습니다**.

### Exact next point / 정확한 다음 재개점

**M0-R1 — Executable Blueprint Contract / 실행 가능한 Blueprint 계약**

The next step is to implement machine-valid schemas, fixtures, and acceptance tests for Blueprint, minimal Music IR, semantic controls, and locks/constraints before building the renderer/compiler pipeline.

다음 단계는 렌더러·컴파일러 파이프라인 구축에 앞서 Blueprint, 최소 Music IR, 의미 제어, lock/constraint의 기계 검증 가능한 스키마·fixture·수용 테스트를 구현하는 것입니다.
