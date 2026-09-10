# MUSICA Design Package v0.1 / MUSICA 설계 패키지 v0.1

**Status / 상태:** ACCEPTED-FOUNDATION / 기반 승인  
**Package version / 패키지 버전:** 0.1  
**Date / 날짜:** 2026-09-11

## 1. Core proposition / 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

This proposition is the primary product and architecture constraint. Any major feature that makes the system easier but materially weakens inspectability, locks, editability, reproducibility, or programmability requires an explicit design decision.

이 명제는 최상위 제품·아키텍처 제약입니다. 사용 편의성을 높이더라도 검사 가능성, 잠금, 편집 가능성, 재현성, 프로그래밍 가능성을 실질적으로 훼손하는 기능은 별도 설계 결정을 거쳐야 합니다.

## 2. Package contents / 패키지 구성

This package consists of four normative specifications:

이 패키지는 다음 네 개의 규범 명세로 구성됩니다.

1. [`ARCHITECTURE_v0.1.md`](./ARCHITECTURE_v0.1.md) — system boundaries, layers, execution flow, invariants / 시스템 경계·계층·실행 흐름·불변조건
2. [`MUSIC_BLUEPRINT_v0.md`](./MUSIC_BLUEPRINT_v0.md) — human/AI-facing canonical creative contract / 인간·AI가 공유하는 공식 창작 계약
3. [`SEMANTIC_CONTROL_MODEL_v0.md`](./SEMANTIC_CONTROL_MODEL_v0.md) — semantic intent vocabulary and resolution protocol / 의미 의도 어휘와 해석 규약
4. [`LOCK_CONSTRAINT_MODEL_v0.md`](./LOCK_CONSTRAINT_MODEL_v0.md) — preservation, constraint, conflict, and mutation rules / 보존·제약·충돌·변경 규칙

## 3. Foundational decisions / 기반 결정

### D-001 — Intent-first, not prompt-only / 의도 우선, 프롬프트 종속 금지
Natural language is an input surface, not the canonical project state. User intent must be translated into an inspectable structured representation before authoritative mutation.

자연어는 입력 인터페이스이지 프로젝트의 공식 상태가 아닙니다. 사용자의 의도는 공식 변경 전에 검사 가능한 구조화 표현으로 변환되어야 합니다.

### D-002 — Blueprint and IR are distinct / Blueprint와 IR 분리
`Music Blueprint` is the human/AI-facing creative contract. `Music IR` is the lower-level executable representation emitted by compilation. The Blueprint MUST NOT require users to understand renderer-specific events.

`Music Blueprint`는 인간/AI가 공유하는 창작 계약이고, `Music IR`은 컴파일 결과로 생성되는 저수준 실행 표현입니다. Blueprint는 사용자가 렌더러별 이벤트를 이해할 것을 요구해서는 안 됩니다.

### D-003 — Locks are invariants / Lock은 불변조건
A lock is not a suggestion. Any transformation that violates a hard lock MUST fail closed or explicitly request a conflict resolution path; it MUST NOT silently mutate the locked target.

Lock은 권고가 아닙니다. hard lock을 위반하는 변환은 반드시 실패 폐쇄하거나 명시적 충돌 해결 경로를 요구해야 하며, 잠긴 대상을 몰래 변경해서는 안 됩니다.

### D-004 — Semantic edits compile to explicit deltas / 의미 편집은 명시적 변경량으로 컴파일
Commands such as “more urgent” or “wider” are not direct audio mutations. They resolve into candidate structured deltas, are checked against constraints, then become Blueprint changes and eventually Music IR/render operations.

“더 긴박하게”, “더 넓게” 같은 명령은 오디오를 직접 수정하지 않습니다. 구조화된 후보 변경량으로 해석되고 제약 검사를 거친 뒤 Blueprint 변경 및 Music IR/렌더 작업으로 이어집니다.

### D-005 — Renderer independence / 렌더러 독립성
The MUSICA core owns intent, Blueprint state, semantics, constraints, provenance, diff, and compilation contracts. MIDI, synth, sampler, DAW, DSP, and generative-audio systems are adapters unless explicitly promoted by a later decision.

MUSICA Core는 의도, Blueprint 상태, 의미, 제약, provenance, diff, 컴파일 계약을 소유합니다. MIDI, synth, sampler, DAW, DSP, 생성형 오디오 시스템은 추후 명시적 결정이 없는 한 어댑터입니다.

### D-006 — Progressive disclosure / 단계적 복잡성 노출
One project state serves Direct, Shape, Inspect, and Code depths. These are views over the same canonical state, not separate incompatible modes.

하나의 프로젝트 상태를 Direct, Shape, Inspect, Code 깊이에서 다르게 보여줍니다. 서로 다른 비호환 모드가 아니라 동일한 공식 상태의 뷰입니다.

### D-007 — Provenance before trust / 신뢰보다 provenance 우선
Every accepted mutation should be attributable to user intent, AI resolution, deterministic transformation, renderer result, or explicit manual edit. MUSICA must be able to explain what changed and why.

모든 승인된 변경은 사용자 의도, AI 해석, 결정론적 변환, 렌더 결과 또는 명시적 수동 편집으로 추적 가능해야 합니다. MUSICA는 무엇이 왜 바뀌었는지 설명할 수 있어야 합니다.

## 4. Canonical object flow / 공식 객체 흐름

```text
User Intent / 사용자 의도
        ↓
Intent Record / 의도 기록
        ↓
AI Music Director / AI 음악 디렉터
        ↓
Music Blueprint / 음악 설계도
        ↓
Semantic Resolver + Constraint Engine
        ↓
Validated Blueprint Revision
        ↓
Music Compiler
        ↓
Music IR
        ↓
Renderer Adapter(s)
        ↓
Audio/MIDI/Score Artifacts
        ↓
Analysis + Evaluation
        ↓
Evidence / Diff / Provenance
        └──────────────→ next revision / 다음 리비전
```

## 5. Non-negotiable invariants / 필수 불변조건

1. **No silent mutation / 무음 변경 금지** — accepted state changes are diffable.
2. **Hard locks fail closed / Hard lock 실패 폐쇄** — locked targets cannot be silently modified.
3. **No unsupported completion claims / 근거 없는 완료 주장 금지** — repository evidence governs implementation status.
4. **Canonical state is structured / 공식 상태 구조화** — generated audio alone is never sufficient project state.
5. **Revisions preserve provenance / 리비전 provenance 보존** — accepted revisions link parent, intent, change set, and evidence.
6. **Renderer output is not semantic truth / 렌더 결과는 의미적 진실이 아님** — renderers execute or approximate a specification; they do not redefine user intent without acceptance.
7. **Unknown stays unknown / 미확인은 미확인으로 유지** — uncertain semantic interpretation must retain uncertainty or branch candidates rather than fabricate certainty.

## 6. Foundation acceptance / 기반 승인 기준

This package is accepted when:

- the four normative specifications exist in the repository,
- terminology and authority relationships are internally consistent,
- `docs/PRODUCT_THESIS.md` adopts the core proposition,
- `memory/CURRENT_STATE.md` records the package as accepted design rather than implemented software,
- `memory/NEXT_ACTION.md` advances to executable M0 specification and implementation preparation.

다음 조건을 충족하면 본 설계 패키지는 승인됩니다.

- 네 규범 명세가 레포에 존재,
- 용어 및 권위 관계가 상호 일관,
- `docs/PRODUCT_THESIS.md`가 핵심 명제를 채택,
- `memory/CURRENT_STATE.md`가 구현 완료가 아닌 승인된 설계로 기록,
- `memory/NEXT_ACTION.md`가 실행 가능한 M0 명세·구현 준비 단계로 전환.

## 7. Deferred decisions / 유보 결정

The following are intentionally NOT fixed by v0.1:

- final desktop/web/mobile application shell,
- proprietary audio foundation model,
- exact DAW/VST integration strategy,
- final semantic vocabulary size,
- final persistence database,
- collaboration/cloud architecture,
- commercial licensing model.

다음 항목은 v0.1에서 의도적으로 확정하지 않습니다.

- 최종 desktop/web/mobile 앱 셸,
- 독자 오디오 파운데이션 모델,
- 구체적인 DAW/VST 통합 방식,
- 최종 의미 어휘 규모,
- 최종 영속화 데이터베이스,
- 협업/클라우드 아키텍처,
- 상용 라이선스 모델.
