# MUSICA Product Thesis / 제품 명제

## 0. Core proposition / 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

This sentence is the canonical product proposition of MUSICA and governs downstream architecture and product decisions.

이 문장은 MUSICA의 공식 핵심 제품 명제이며 이후 아키텍처와 제품 결정을 지배합니다.

## 1. Problem / 문제 정의

Most AI music products optimize for fast generation. Traditional DAWs optimize for precision. Users are often forced to choose between convenience and control.

대부분의 AI 음악 제품은 빠른 생성을, 전통적 DAW는 정밀 제어를 최적화합니다. 사용자는 편의성과 통제력 사이에서 선택을 강요받는 경우가 많습니다.

MUSICA exists to remove that trade-off.

MUSICA의 목적은 이 양자택일을 없애는 것입니다.

## 2. Product promise / 제품 약속

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**
>
> **자연어로 지시할 만큼 쉽고, 전문 음악 시스템처럼 세밀하게 편집할 만큼 정밀해야 한다.**

## 3. Differentiation / 차별화

MUSICA does not win by generating one-shot songs faster than dedicated generative models. It wins by making musical intent explicit, editable, lockable, reproducible, explainable, versionable, and backend-independent.

MUSICA는 전용 생성 모델보다 원샷 음악을 더 빨리 만드는 것으로 승부하지 않습니다. 음악적 의도를 명시적이고 편집 가능하며 잠글 수 있고 재현·설명·버전 관리가 가능하며 특정 렌더러에 종속되지 않게 만드는 것이 차별점입니다.

Core differentiators / 핵심 차별점:

1. **Progressive disclosure / 단계적 복잡성 노출** — beginner controls first, professional detail on demand.
2. **Semantic controls / 의미 기반 제어** — users edit concepts such as tension, energy, density, motion, timbre, space, and focus.
3. **Structured Music Blueprint / 구조화 음악 설계도** — every accepted creative state has an inspectable representation.
4. **Locks and constraints / 잠금과 제약** — preserve selected musical identity or exact values while changing other parts.
5. **Reversible editing / 가역 편집** — move from intent to sections to notes/automation and back without losing canonical structure.
6. **Versionable music / 버전 가능한 음악** — branch, compare, and explain changes as structured musical diffs.
7. **Renderer independence / 렌더러 독립성** — MIDI, synths, samplers, DAWs, DSP, and external generative audio systems are adapters rather than the product core.
8. **Evidence-backed AI / 증거 기반 AI** — the system records what was requested, resolved, changed, rendered, evaluated, and accepted.

## 4. UX principle / UX 원칙

The user interface exposes four depths over the same canonical project state rather than four separate products.

사용자 인터페이스는 네 개의 별도 제품이 아니라 동일한 공식 프로젝트 상태를 네 깊이로 제공합니다.

### Direct / 간편 디렉팅
Natural language + references + high-level semantic controls.

자연어 + 참고자료 + 상위 의미 제어.

### Shape / 구조 편집
Sections, instruments, roles, harmony, rhythm, emotion curves, and locks.

구간, 악기, 역할, 화성, 리듬, 감정 곡선, 잠금.

### Inspect / 전문 편집
Notes, MIDI-like events, automation, synthesis, DSP, mix parameters, rendering details, and structured execution evidence.

음표, MIDI형 이벤트, 오토메이션, 신시시스, DSP, 믹스 파라미터, 렌더링 세부정보, 구조화 실행 근거.

### Code / 코드
Blueprint, Music IR, API, CLI, programmable transforms, and reproducible automation.

Blueprint, Music IR, API, CLI, 프로그래머블 변환, 재현 가능한 자동화.

## 5. Core interaction loop / 핵심 상호작용 루프

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
설명 → 설계도 생성 → 청취 → 잠금 → 정교화 → 비교 → 확정
```

The system should allow commands such as:

- “Keep the melody, but make the chorus 20% more urgent.”
- “Preserve the drums and timing; replace only the harmonic color.”
- “Make bars 17–24 feel wider without increasing loudness.”
- “Show me exactly what changed between version A and B.”

시스템은 위와 같은 자연어 지시를 구조화된 음악 수정으로 변환해야 합니다.

## 6. Canonical design package / 공식 설계 패키지

The accepted foundation design is defined by:

승인된 기반 설계는 다음 문서로 정의됩니다.

- `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
- `docs/design/ARCHITECTURE_v0.1.md`
- `docs/design/MUSIC_BLUEPRINT_v0.md`
- `docs/design/SEMANTIC_CONTROL_MODEL_v0.md`
- `docs/design/LOCK_CONSTRAINT_MODEL_v0.md`

The package establishes the distinction between human/AI-facing `Music Blueprint` and executable `Music IR`, semantic edit resolution, hard-lock fail-closed behavior, renderer independence, provenance, and progressive disclosure.

이 패키지는 인간/AI 대상 `Music Blueprint`와 실행용 `Music IR`의 분리, 의미 수정 해석, hard-lock 실패 폐쇄, 렌더러 독립성, provenance, 단계적 복잡성 노출을 확정합니다.

## 7. Non-goals / 비목표

At foundation stage MUSICA is not defined as:

- a clone of Suno or another text-to-song service,
- a full replacement for every professional DAW,
- a proprietary audio foundation model project,
- a system that hides all musical decisions behind opaque generation.

기반 단계에서 MUSICA는 Suno 복제, 모든 DAW 대체, 독자 오디오 파운데이션 모델 구축, 불투명한 생성 결과만 제공하는 시스템을 목표로 하지 않습니다.

## 8. Product test / 제품 판단 기준

A feature belongs in MUSICA when it improves at least one of these without materially harming the others:

1. ease of creation / 제작 편의성,
2. depth of control / 제어 깊이,
3. reproducibility / 재현성,
4. inspectability / 검사 가능성,
5. interoperability / 상호운용성,
6. trustworthy AI operation / 신뢰 가능한 AI 작업.
