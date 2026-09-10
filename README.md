# MUSICA

> **Music creation from intent to precision. / 의도에서 정밀 제어까지 이어지는 음악 제작 시스템.**

MUSICA is an AI-native programmable music creation system designed to make music creation **easy for non-experts** while preserving **deep, inspectable, professional control** for advanced users.

MUSICA는 비전문가도 쉽게 음악을 만들 수 있으면서, 전문가에게는 **검사 가능하고 정밀한 제어**를 제공하는 AI-native 프로그래머블 음악 제작 시스템입니다.

## Product thesis / 제품 명제

MUSICA is **not** defined as a text-to-song competitor. Its core is a reversible workflow:

MUSICA는 단순 text-to-song 경쟁 제품으로 정의하지 않습니다. 핵심은 다음의 **가역적(reversible) 제작 흐름**입니다.

```text
Intent / 의도
  ↓
AI Music Director / AI 음악 감독
  ↓
Editable Music Blueprint / 편집 가능한 음악 설계도
  ↓
Music IR + Constraints + Locks / 음악 중간표현 + 제약 + 잠금
  ↓
Compiler & Renderer Adapters / 컴파일러 및 렌더러 어댑터
  ↓
MIDI / Synth / DAW / Audio Backend
  ↓
Analyze → Compare → Revise / 분석 → 비교 → 수정
```

The user should not need to see code, YAML, MIDI events, or DSP parameters unless they want to. Complexity is progressively disclosed.

사용자는 원하지 않는 한 코드, YAML, MIDI 이벤트, DSP 파라미터를 볼 필요가 없습니다. 전문 제어는 필요할 때 단계적으로 노출됩니다.

## Core experience / 핵심 경험

- **Describe / 설명:** create from natural language, references, mood, scene, or timeline.
- **Direct / 디렉팅:** use semantic controls such as energy, tension, density, brightness, groove, intimacy, and scale.
- **Lock / 잠금:** preserve what must not change—melody, rhythm, harmony, instrument, section, timing, or mix decisions.
- **Inspect / 검사:** reveal the structured musical decisions behind the result.
- **Edit / 편집:** move seamlessly from high-level intent to notes, automation, MIDI, synthesis, and mix parameters.
- **Compare / 비교:** branch versions and compare musical changes as structured diffs rather than opaque regenerations.
- **Render / 렌더링:** support multiple rendering backends instead of binding the product to one generative model.

## Repository role / 저장소 역할

This repository is both the implementation workspace and the canonical project memory.

이 저장소는 구현 작업 공간인 동시에 프로젝트의 공식 기억장치입니다.

Authority rule / 권위 규칙:

> **Repository evidence > conversational memory > model inference.**
>
> **레포 증거 > 대화 기억 > 모델 추론.**

No AI agent may claim a feature, decision, test, milestone, or artifact exists unless repository evidence supports that claim.

어떤 AI 에이전트도 레포 근거 없이 기능, 결정, 테스트, 마일스톤 또는 산출물이 존재한다고 주장해서는 안 됩니다.

See `governance/SOURCE_OF_TRUTH.md` and `memory/CURRENT_STATE.md` before continuing work.

## Current status / 현재 상태

**FOUNDATION / PRODUCT DEFINITION** — architecture and product thesis are being established before implementation begins.

**기반 설계 / 제품 정의 단계** — 구현에 앞서 제품 명제와 아키텍처를 확정하는 단계입니다.
