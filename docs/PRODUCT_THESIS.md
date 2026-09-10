# MUSICA Product Thesis / 제품 명제

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

MUSICA does not win by generating one-shot songs faster than dedicated generative models. It wins by making musical intent explicit, editable, lockable, reproducible, and backend-independent.

MUSICA는 전용 생성 모델보다 원샷 음악을 더 빨리 만드는 것으로 승부하지 않습니다. 음악적 의도를 명시적이고 편집 가능하며 잠글 수 있고 재현 가능하며 특정 렌더러에 종속되지 않게 만드는 것이 차별점입니다.

Core differentiators / 핵심 차별점:

1. **Progressive disclosure / 단계적 복잡성 노출** — beginner controls first, professional detail on demand.
2. **Semantic controls / 의미 기반 제어** — users edit concepts such as tension, energy, groove, density, brightness, intimacy, scale, and motion.
3. **Structured Music Blueprint / 구조화 음악 설계도** — every generation has an inspectable representation.
4. **Locks and constraints / 잠금과 제약** — preserve selected melody, harmony, rhythm, instrumentation, timing, lyrics, sound, or mix while changing other parts.
5. **Reversible editing / 가역 편집** — move from intent to sections to notes/automation and back without losing structure.
6. **Versionable music / 버전 가능한 음악** — branch, compare, and explain changes as structured musical diffs.
7. **Renderer independence / 렌더러 독립성** — MIDI, synths, samplers, DAWs, DSP, and external generative audio systems can be adapters rather than the product core.
8. **Evidence-backed AI / 증거 기반 AI** — the system records what is decided, generated, rendered, evaluated, and accepted.

## 4. UX principle / UX 원칙

The user interface should expose three depths without forcing three separate products.

사용자 인터페이스는 세 개의 별도 제품이 아니라 하나의 경험 안에서 세 단계 깊이를 제공해야 합니다.

### Direct / 간편 디렉팅
Natural language + references + high-level semantic controls.

자연어 + 참고자료 + 상위 의미 제어.

### Shape / 구조 편집
Sections, instruments, roles, harmony, rhythm, emotion curves, and locks.

구간, 악기, 역할, 화성, 리듬, 감정 곡선, 잠금.

### Inspect / 전문 편집
Notes, MIDI, automation, synthesis, DSP, mix parameters, rendering details, and structured Music IR.

음표, MIDI, 오토메이션, 신시시스, DSP, 믹스 파라미터, 렌더링 세부정보, 구조화된 Music IR.

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

## 6. Non-goals / 비목표

At foundation stage MUSICA is not defined as:

- a clone of Suno or another text-to-song service,
- a full replacement for every professional DAW,
- a proprietary audio foundation model project,
- a system that hides all musical decisions behind opaque generation.

기반 단계에서 MUSICA는 Suno 복제, 모든 DAW 대체, 독자 오디오 파운데이션 모델 구축, 불투명한 생성 결과만 제공하는 시스템을 목표로 하지 않습니다.

## 7. Product test / 제품 판단 기준

A feature belongs in MUSICA when it improves at least one of these without materially harming the others:

1. ease of creation / 제작 편의성,
2. depth of control / 제어 깊이,
3. reproducibility / 재현성,
4. inspectability / 검사 가능성,
5. interoperability / 상호운용성,
6. trustworthy AI operation / 신뢰 가능한 AI 작업.
