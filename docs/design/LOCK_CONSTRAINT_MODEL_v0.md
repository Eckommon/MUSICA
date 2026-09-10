# Lock & Constraint Model v0 / 잠금·제약 모델 v0

**Status / 상태:** ACCEPTED-FOUNDATION / 기반 승인

## 1. Purpose / 목적

Locks and constraints make MUSICA controllable. They define what MUST remain unchanged, what MAY vary, and what conditions any accepted revision must satisfy.

Lock과 constraint는 MUSICA를 통제 가능한 시스템으로 만드는 핵심입니다. 무엇을 반드시 유지하고, 무엇을 바꿀 수 있으며, 승인 리비전이 어떤 조건을 만족해야 하는지 정의합니다.

## 2. Core distinction / 핵심 구분

### Lock / 잠금
A lock protects an existing accepted property or musical identity from mutation.

Lock은 기존에 승인된 속성 또는 음악적 정체성을 변경으로부터 보호합니다.

### Constraint / 제약
A constraint specifies a condition that a candidate state must satisfy. It may limit ranges, relationships, capabilities, timing, style, or rendering behavior.

Constraint는 후보 상태가 만족해야 하는 조건을 정의하며 범위, 관계, 기능, 시간, 스타일, 렌더 동작 등을 제한할 수 있습니다.

## 3. Lock strengths / 잠금 강도

### HARD
Must not be violated. Candidate mutation fails closed or branches into an explicit conflict-resolution path.

위반 불가. 후보 변경은 실패 폐쇄하거나 명시적 충돌 해결 분기로 이동합니다.

### SOFT
Prefer preservation, but the resolver may propose a violation if it explains the reason and obtains explicit acceptance before commit.

보존이 우선이지만, 사유를 설명하고 승인받는 경우에 한해 위반안을 제안할 수 있습니다.

### ADVISORY
A preference, not a preservation guarantee. Used mainly for ranking alternatives.

보존 보장이 아닌 선호이며 대안 순위 결정에 주로 사용합니다.

## 4. Lock targets / 잠금 대상

Locks MAY target:

- whole project revision / 전체 프로젝트 리비전,
- section / 구간,
- time range / 시간 범위,
- part / 파트,
- instrument assignment / 악기 배정,
- role / 역할,
- melody identity / 멜로디 정체성,
- explicit notes / 명시 음표,
- harmony / 화성,
- chord progression / 코드 진행,
- rhythm or groove / 리듬·그루브,
- tempo/meter / 템포·박자,
- lyrics / 가사,
- arrangement / 편곡,
- semantic property / 의미 속성,
- sound/timbre intent / 사운드·음색 의도,
- mix intent / 믹스 의도,
- renderer target/configuration where reproducibility requires it / 재현성에 필요한 렌더러 대상·설정.

## 5. Identity locks vs value locks / 정체성 잠금과 값 잠금

MUSICA MUST distinguish at least two important lock semantics.

MUSICA는 최소 다음 두 잠금 의미를 구분해야 합니다.

### Value lock / 값 잠금
Exact or tolerance-bounded value preservation.

정확한 값 또는 허용 오차 범위 내 값 보존.

Example:

```yaml
lock:
  strength: HARD
  target: tempo.bpm
  mode: exact
  value: 112
```

### Identity lock / 정체성 잠금
Preserve recognizable musical identity while allowing implementation-level changes that do not materially alter that identity.

인식 가능한 음악적 정체성을 보존하되, 정체성을 실질적으로 바꾸지 않는 구현 수준 변화는 허용합니다.

Example:

```yaml
lock:
  strength: HARD
  target: melody.main_motif
  mode: identity
  identity_basis:
    pitch_contour: preserve
    anchor_intervals: preserve
    rhythmic_signature: preserve
    octave_displacement: allowed
    ornamentation: bounded
```

Identity locks require explicit policy because “same melody” is not equivalent to byte-identical notes.

정체성 잠금은 “같은 멜로디”가 음표 바이트 동일성과 같지 않기 때문에 명시 정책이 필요합니다.

## 6. Constraint classes / 제약 종류

### Range constraints / 범위 제약
```yaml
constraint:
  target: tempo.bpm
  op: between
  value: [105, 115]
```

### Equality/inequality constraints / 등가·부등 제약
Examples: section duration = 8 bars; peak energy > intro energy.

예: 구간 길이 = 8마디, peak energy > intro energy.

### Structural constraints / 구조 제약
Examples: chorus must begin by 0:40; no section overlap; motif appears at least twice.

예: 40초 이전 chorus 시작, 구간 겹침 금지, 모티프 최소 2회 등장.

### Preservation constraints / 보존 제약
Examples: maintain vocal phrasing; preserve beat grid; retain cadence type.

예: 보컬 프레이징 유지, beat grid 유지, 종지 유형 유지.

### Capability constraints / 기능 제약
Examples: selected renderer must support microtonal pitch bends; MIDI-only path cannot satisfy a required acoustic articulation without approximation policy.

예: 선택 렌더러가 미세음 pitch bend를 지원해야 함, MIDI-only 경로에서 필수 어쿠스틱 아티큘레이션을 근사 정책 없이 충족할 수 없음.

### Budget/performance constraints / 비용·성능 제약
Examples: render under local CPU-only profile; avoid paid backend; preview under specified latency budget.

예: 로컬 CPU-only 렌더, 유료 백엔드 금지, 지정 preview latency 이내.

## 7. Scope and precedence / 범위와 우선순위

A lock/constraint SHOULD declare scope and priority.

Lock/constraint는 적용 범위와 우선순위를 선언해야 합니다.

Default precedence / 기본 우선순위:

1. safety/legal/project integrity constraints / 안전·법적·프로젝트 무결성 제약
2. explicit user HARD locks / 사용자 명시 HARD lock
3. explicit user hard constraints / 사용자 명시 hard constraint
4. accepted project-level invariants / 승인 프로젝트 불변조건
5. section/part constraints / 구간·파트 제약
6. user SOFT locks/preferences / 사용자 SOFT 잠금·선호
7. AI inferred preferences / AI 추론 선호
8. optimization heuristics / 최적화 휴리스틱

Lower-ranked rules MUST NOT silently override higher-ranked rules.

하위 규칙은 상위 규칙을 몰래 덮어쓸 수 없습니다.

## 8. Mutation protocol / 변경 프로토콜

Every candidate mutation SHALL conceptually execute:

모든 후보 변경은 개념적으로 다음 절차를 수행합니다.

```text
1. Resolve requested scope
2. Enumerate affected Blueprint fields
3. Expand applicable locks/constraints
4. Compute candidate delta
5. Detect violations
6. Classify conflicts
7. If HARD conflict → reject or branch explicit alternatives
8. If SOFT conflict → annotate and require acceptance when violated
9. Validate resulting Blueprint
10. Emit structured diff + provenance
```

## 9. Conflict record / 충돌 기록

Conflicts SHOULD be machine-readable.

충돌은 기계 판독 가능해야 합니다.

```yaml
conflict_id: "C-001"
request: "make the chorus much faster"
affected_scope: section:chorus
violated_rule:
  type: lock
  strength: HARD
  target: tempo.bpm
  value: 112
status: BLOCKED
alternatives:
  - "increase rhythmic subdivision while preserving BPM"
  - "increase percussion anticipation"
  - "unlock tempo explicitly"
```

## 10. Lock inheritance / 잠금 상속

A lock on a parent scope applies to descendants unless explicitly declared non-inheriting.

상위 범위의 lock은 명시적으로 비상속으로 지정하지 않는 한 하위 범위에 적용됩니다.

Example: a HARD melody lock at project scope applies to all sections containing that melody identity.

예: 프로젝트 범위의 HARD melody lock은 해당 멜로디 정체성이 나타나는 모든 구간에 적용됩니다.

## 11. Renderer approximation policy / 렌더러 근사 정책

Renderer limitations MUST NOT silently weaken locks or constraints.

렌더러 한계가 lock/constraint를 몰래 약화해서는 안 됩니다.

Each compiled target should classify unsupported requirements as:

- `SUPPORTED`
- `APPROXIMATED_ACCEPTABLE`
- `APPROXIMATED_REQUIRES_ACCEPTANCE`
- `UNSUPPORTED_BLOCKING`

각 컴파일 대상은 미지원 요구를 위 상태 중 하나로 분류해야 합니다.

## 12. Reproducibility locks / 재현성 잠금

For workflows claiming repeatability, MUSICA MAY lock:

- Blueprint revision,
- compiler version,
- adapter version,
- seed,
- preset/sample identity,
- execution configuration,
- dependency manifest,
- artifact hash.

재현성을 주장하는 워크플로에서는 위 실행 환경과 산출물 정보를 잠글 수 있습니다.

## 13. User experience principle / 사용자 경험 원칙

The UI SHOULD present locks simply first (“Keep melody”, “Keep drums”, “Keep timing”), while allowing advanced users to inspect exact scope and lock semantics.

UI는 우선 “멜로디 유지”, “드럼 유지”, “타이밍 유지”처럼 간단하게 보여주되, 전문 사용자는 정확한 범위와 잠금 의미를 검사할 수 있어야 합니다.

## 14. M0 lock/constraint minimum / M0 최소 범위

M0 MUST prove:

1. one HARD value lock,
2. one HARD identity-like musical lock with a simplified policy,
3. one numeric constraint,
4. one semantic edit that would have violated a lock without the constraint engine,
5. fail-closed behavior,
6. an alternative valid mutation,
7. structured conflict and diff evidence.

M0는 위 최소 사례를 실행 근거로 증명해야 합니다.
