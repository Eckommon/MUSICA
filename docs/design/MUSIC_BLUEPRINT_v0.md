# Music Blueprint v0 / 음악 설계도 v0

**Status / 상태:** ACCEPTED-FOUNDATION / 기반 승인

## 1. Purpose / 목적

`Music Blueprint` is the canonical human/AI-facing creative state of a MUSICA project revision.

`Music Blueprint`는 MUSICA 프로젝트 리비전의 인간/AI 대상 공식 창작 상태입니다.

It is intentionally higher-level than executable Music IR. It captures what the music is intended to be, what is preserved, what may change, and why.

이는 실행용 Music IR보다 의도적으로 상위 수준이며, 음악이 무엇이어야 하는지, 무엇을 보존하고 무엇을 변경할 수 있는지, 그 이유를 기록합니다.

## 2. Design requirements / 설계 요구사항

A Blueprint MUST be:

- inspectable / 검사 가능,
- serializable / 직렬화 가능,
- versioned / 버전 가능,
- diffable / diff 가능,
- constraint-aware / 제약 인지,
- renderer-independent / 렌더러 독립,
- provenance-carrying / provenance 포함,
- partially specified when uncertainty exists / 불확실성이 있으면 부분 명세 허용.

## 3. Canonical top-level model / 공식 최상위 모델

```yaml
blueprint_version: "0"
project:
  project_id: "..."
  title: "..."
  revision_id: "..."
  parent_revision_id: "..."
  duration_seconds: 30.0

intent:
  summary: "..."
  use_case: "advertisement | song | score | game | ambient | other"
  references: []
  exclusions: []
  uncertainties: []

musical_context:
  tempo:
    bpm: 112
    policy: "fixed | range | adaptive"
  meter: "4/4"
  tonal_center: "D"
  mode: "minor"

form:
  sections: []

roles:
  instruments_or_parts: []

semantics:
  global: {}
  curves: []
  section_overrides: []

materials:
  harmony: {}
  melody: {}
  rhythm: {}
  texture: {}
  sound_design: {}
  mix_intent: {}

locks: []
constraints: []

render_intent:
  targets: []
  quality_preferences: []

provenance:
  created_from_intent_id: "..."
  actor: "user | ai | deterministic_transform | import"
  change_reason: "..."
  source_revision: "..."
```

The concrete JSON Schema will be implemented after this conceptual model is accepted and refined through M0 implementation needs.

실제 JSON Schema는 이 개념 모델을 기반으로 M0 구현 요구를 반영하여 작성합니다.

## 4. Section model / 구간 모델

Each section SHOULD include:

```yaml
section_id: "S01"
label: "build"
start: 4.0
end: 12.0
purpose: "increase momentum without revealing peak motif"
semantic_targets:
  energy: 0.55
  tension: 0.48
locks: []
constraints: []
```

Sections MAY overlap only if the later schema explicitly supports layered structural regions. v0 default is non-overlapping ordered sections.

구간은 향후 스키마에서 중첩 구조를 명시적으로 지원하지 않는 한 기본적으로 겹치지 않는 순차 구간으로 취급합니다.

## 5. Role model / 역할 모델

MUSICA SHOULD model musical parts by role, not only by instrument name.

MUSICA는 악기명만이 아니라 음악적 역할을 모델링해야 합니다.

Example / 예:

```yaml
part_id: "P_BASS_01"
instrument_family: "bass_synth"
role: "propulsion"
register: "low"
presence: 0.7
importance: 0.8
mutable: true
```

Typical roles MAY include:

- pulse / 박동,
- propulsion / 추진,
- foundation / 기반,
- harmonic support / 화성 지지,
- tension / 긴장,
- motif / 모티프,
- lead / 리드,
- counterline / 대선율,
- atmosphere / 분위기,
- transition / 전환,
- impact / 임팩트,
- spatial bed / 공간 배경.

## 6. Musical materials / 음악 재료

Blueprint v0 distinguishes intent-level material from renderer-level realization.

Blueprint v0는 의도 수준의 음악 재료와 렌더러 수준의 실현을 구분합니다.

### Harmony / 화성
May include key/mode, progression intent, chord symbols, harmonic rhythm, tension targets, voicing constraints.

조성/모드, 코드 진행 의도, 코드 기호, 화성 리듬, 긴장 목표, 보이싱 제약을 포함할 수 있습니다.

### Melody / 멜로디
May include motif identity, contour, range, cadence behavior, anchor notes, explicit notes when needed.

모티프 정체성, 윤곽, 음역, 종지 성향, 기준음, 필요 시 명시적 음표를 포함할 수 있습니다.

### Rhythm / 리듬
May include pulse, subdivision, syncopation, density, groove profile, explicit events when needed.

박, subdivision, 당김음, 밀도, groove profile, 필요 시 명시 이벤트를 포함할 수 있습니다.

### Texture / 텍스처
May include layer count, register spread, call/response, foreground/background balance, sparsity.

레이어 수, 음역 분포, call/response, 전경/배경 균형, 희소성을 포함할 수 있습니다.

### Sound design / 사운드 디자인
May express timbral intent such as warm, brittle, metallic, airy, saturated, acoustic, synthetic. Renderer-specific oscillator or plugin parameters belong lower unless explicitly exposed by the user.

따뜻함, 금속성, 공기감, 포화, 어쿠스틱/합성 등 음색 의도를 표현할 수 있으며, 렌더러별 오실레이터/플러그인 파라미터는 사용자가 명시적으로 노출하지 않는 한 하위 계층에 둡니다.

### Mix intent / 믹스 의도
May express relative focus, width, depth, clarity, punch, loudness policy, and separation goals without pretending that a Blueprint itself is DSP.

상대적 초점, 폭, 깊이, 명료도, punch, loudness 정책, 분리 목표를 표현하되 Blueprint 자체가 DSP인 것처럼 취급하지 않습니다.

## 7. Revision semantics / 리비전 의미론

Every accepted Blueprint revision MUST have:

- a unique revision id,
- a parent revision id unless it is the root,
- a reason or intent reference,
- a structured change set or derivable diff,
- provenance.

모든 승인 Blueprint 리비전은 고유 ID, 루트가 아닌 경우 부모 리비전 ID, 변경 이유/의도 참조, 구조화 change set 또는 계산 가능한 diff, provenance를 가져야 합니다.

## 8. Partial specification / 부분 명세

A Blueprint MAY contain unresolved values such as:

```yaml
tonal_center: null
mode_candidates: ["dorian", "minor"]
confidence: 0.58
```

Unknown information MUST NOT be silently invented merely to make the object look complete.

객체를 완성된 것처럼 보이게 하려고 미확인 값을 임의 생성해서는 안 됩니다.

## 9. Blueprint vs Music IR / Blueprint와 Music IR

Blueprint answers:

- What should this music feel and function like?
- What structure and musical decisions are accepted?
- What must remain unchanged?
- What may vary?

Blueprint가 답하는 질문:

- 음악이 어떤 느낌과 기능을 가져야 하는가?
- 어떤 구조와 음악 결정이 승인되었는가?
- 무엇이 반드시 유지되어야 하는가?
- 무엇이 변할 수 있는가?

Music IR answers:

- What executable events/parameters must a target backend receive?
- Which values were lowered or approximated from Blueprint intent?

Music IR이 답하는 질문:

- 대상 백엔드가 어떤 실행 이벤트/파라미터를 받아야 하는가?
- Blueprint 의도 중 무엇이 구체화 또는 근사되었는가?

## 10. M0 minimum viable Blueprint / M0 최소 Blueprint

M0 implementation needs only enough fields to prove the core loop:

1. project/revision identity,
2. duration,
3. tempo/meter/tonal context,
4. ordered sections,
5. at least three musical parts/roles,
6. basic harmony/rhythm/melody representation,
7. global + section semantic controls,
8. hard locks,
9. constraints,
10. provenance,
11. deterministic render target metadata.

M0는 위 최소 필드만으로 핵심 루프를 증명하며, 완전한 DAW 데이터 모델을 선행 구축하지 않습니다.
