# Current State / 현재 상태

## Project phase / 프로젝트 단계

**FOUNDATION — PRODUCT DEFINITION / 기반 설계 — 제품 정의**

Implementation has not started. The repository currently records the accepted initial product direction and governance rules.

구현은 아직 시작하지 않았습니다. 현재 레포는 승인된 초기 제품 방향과 거버넌스 규칙을 기록하는 단계입니다.

## Accepted direction / 승인된 방향

- MUSICA is an **AI-native programmable music creation system**, not merely a text-to-song generator.
- MUSICA는 단순 text-to-song 생성기가 아니라 **AI-native 프로그래머블 음악 제작 시스템**입니다.

- Primary product promise: **easy natural-language creation + professional, inspectable precision**.
- 핵심 제품 약속: **쉬운 자연어 제작 + 전문가급의 검사 가능한 정밀 제어**.

- The user experience should use **progressive disclosure** rather than forcing users to choose between a simple app and a professional tool.
- 사용자 경험은 간편 앱과 전문 도구를 분리하기보다 **단계적 복잡성 노출**을 사용합니다.

- A structured **Music Blueprint / Music IR** is the canonical bridge between intent and execution.
- 구조화된 **Music Blueprint / Music IR**이 의도와 실행을 연결하는 공식 중간 계층입니다.

- **Locks and constraints** are first-class concepts so users can preserve selected musical elements while modifying others.
- 특정 요소를 보존한 채 다른 요소만 수정할 수 있도록 **잠금과 제약**을 핵심 개념으로 둡니다.

- Rendering should be **backend-independent** where practical: MIDI, synth, sampler, DAW, DSP, or external generative audio systems may be adapters.
- 가능한 범위에서 렌더링은 **백엔드 독립적**이어야 하며 MIDI, synth, sampler, DAW, DSP, 외부 생성형 오디오 시스템을 어댑터로 연결할 수 있습니다.

## Evidence status / 근거 상태

- Product thesis: **ACCEPTED-INITIAL / 초기 승인**
- Repository SoT contract: **IMPLEMENTED**
- Music IR schema: **NOT IMPLEMENTED**
- Compiler: **NOT IMPLEMENTED**
- Renderer adapters: **NOT IMPLEMENTED**
- Application/UI: **NOT IMPLEMENTED**
- Audio generation pipeline: **NOT IMPLEMENTED**
- Automated tests: **NOT IMPLEMENTED**

## Competitive note / 경쟁 관점

MUSICA should not depend on a claim that competing AI music tools lack MIDI, automation, effects, or conversational editing. The product must differentiate on the combination of semantic control, inspectability, locks/constraints, reproducibility, structured diffs, and renderer independence.

MUSICA는 경쟁 AI 음악 도구에 MIDI, 오토메이션, 이펙트 또는 대화형 편집 기능이 없다는 전제에 의존해서는 안 됩니다. 의미 기반 제어, 검사 가능성, 잠금/제약, 재현성, 구조화 diff, 렌더러 독립성의 결합으로 차별화해야 합니다.
