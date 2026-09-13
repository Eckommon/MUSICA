# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M7-R0 — CANONICAL AUTOMATION & CONTINUOUS-CONTROL AUTHORITY / M7-R0 — 공식 Automation·연속 제어 권한 모델**

M6-R4 is `VALIDATED — BOUNDED INTERCHANGE NOTE RECONCILIATION`, and the first M6 Precision Editing tranche is complete within its bounded claims.

M6-R4는 `VALIDATED — BOUNDED INTERCHANGE NOTE RECONCILIATION`이며, 첫 M6 Precision Editing tranche는 제한된 주장 범위에서 완료되었습니다.

No pre-existing M6-R5 or M7 implementation roadmap was found in the repository. The next phase is intentionally a **contract/design-only milestone** derived from the canonical product thesis rather than an assumed runtime extension.

## Canonical starting point / 공식 시작점

- M6-R4 Issue `#65` — **COMPLETED**
- M6-R4 PR `#66` — **MERGED**
- M6-R4 implementation merge/main: `66637f7977782ad01e8060d3c4810095c7b44d19`
- final evidence-bearing head: `6927a69a84589da985c5ce37ec4bd80749767ea7`
- final MUSICA CI `34790028892` — **SUCCESS**
- final M6-R4 `34790028903` — **SUCCESS**
- final M6-R3 `34790028845` — **SUCCESS**
- final M6-R2 `34790028854` — **SUCCESS**
- final M6-R1 `34790028874` — **SUCCESS**
- final M5-R3 `34790028871` — **SUCCESS**
- final M5-R4 `34790028873` — **SUCCESS**
- final M6-R4 artifact ID `10328000726`
- outer artifact SHA-256 `26cd14c67d50023ce2c81cd8257b47dda2a4770ee1e3cc503efd02cf526ecf18`
- internal manifest SHA-256 `4fd4ae72d9b3a77ab2c5ec4ab973af05d753a7c22aca21c523bd5e9862415d2c`
- final evidence tree vs strengthened pre-durable tree: **34 files / 0 differences**
- durable evidence: `evidence/M6_R4_VALIDATION.md`

## Why M7-R0 / 왜 M7-R0인가

The canonical product thesis says Inspect-level professional control includes:

- notes / MIDI-like events;
- automation;
- synthesis;
- DSP;
- mix parameters;
- rendering details.

M6 established trusted exact-note authority. The repository still lacks a validated canonical model for time-varying/continuous control decisions such as volume, pan, filter cutoff, send level or other bounded automatable parameters.

Without an explicit authority model, adding visual automation lanes would risk repeating the pre-M6 mistake: a derived execution representation could accidentally become de facto canonical creative state.

Therefore M7-R0 must answer the authority/data questions **before** runtime/UI implementation.

## Governing invariant / 지배 불변식

Target authority principle:

```text
accepted creative automation decision
→ Blueprint-representable canonical automation material
→ trusted deterministic lowering
→ Music IR / renderer automation events
```

Potential edit path:

```text
user/AI automation edit
→ typed non-canonical AutomationEditCandidate
→ exact source binding
→ stable parameter/lane identity
→ HARD lock / constraint validation
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept only
→ M2 revision authority
```

Forbidden:

```text
raw renderer/plugin parameter state → accepted Blueprint
Music IR control events → canonical state by reverse inference
DOM/canvas points → canonical state without typed mapping
AI-generated curve → accepted state without Preview/Accept
external DAW automation → canonical state without explicit proven reconciliation contract
```

## Required M7-R0 design decisions / 필수 설계 결정

### 1. Canonical ownership

Define which automation decisions belong in Blueprint authority versus derived execution state.

At minimum distinguish:

- creative automation explicitly chosen by user/AI and accepted;
- semantic-control curves already represented at higher level;
- compiler-generated control events;
- renderer/device implementation parameters;
- external DAW/plugin automation.

No lower-authority representation may silently override a higher-level accepted decision.

### 2. Parameter identity

Define stable, backend-independent identity for automatable parameters.

Candidate identity must not depend solely on:

- array index;
- MIDI CC number;
- DAW lane order;
- plugin-specific opaque ID;
- DOM position.

A bounded registry/namespaced parameter reference should identify semantic/project parameters independently of one renderer.

### 3. Time domain

Decide canonical automation position units.

Strong default to evaluate:

- musical beat coordinates for musically aligned creative automation;
- explicit project-level domain and interpolation;
- no seconds-only authority that binds creative identity to one tempo realization.

Any exception must be explicit.

### 4. Curve model

Define the minimum canonical v0 representation:

- lane ID;
- target parameter identity;
- ordered stable point IDs;
- position;
- normalized or typed value;
- interpolation mode;
- optional scope/section ownership.

Do not overreach into arbitrary DAW spline fidelity in R0.

### 5. Value domain and units

Separate canonical creative value from backend-specific implementation value.

Examples to resolve:

- normalized `0..1` vs physical units;
- dB gain versus linear amplitude;
- pan domain;
- frequency/log-frequency representation;
- bounded discrete enum parameters.

Conversions must be explicit, deterministic and testable.

### 6. Locks and constraints

Define stable lane/point/parameter-specific lock targets, avoiding array-index authority.

Required precedence remains:

```text
project integrity
> HARD locks
> hard constraints
> accepted canonical state
> user soft preferences
> AI inference
> optimization heuristics
```

### 7. Edit vocabulary

Ratify a bounded primitive set before implementation. Candidate primitives to evaluate:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
REPLACE_BOUNDED_SEGMENT
```

R0 may narrow this set. It must not approve arbitrary free-form transformations without a typed/reproducible representation.

### 8. Source binding / stale protection

Automation candidates should bind to:

```text
project_id
accepted revision_id
canonical Blueprint SHA-256
canonical automation material hash
```

Stale edits must fail closed; no silent rebase.

### 9. Compiler/lowering boundary

Specify deterministic lowering from canonical automation material into derived execution events while preserving the distinction:

```text
Blueprint automation = creative authority
Music IR / renderer control events = derived execution
```

The compiler must not silently resample or alter accepted creative decisions without an explicit deterministic policy.

### 10. Semantic-control coexistence

The design must resolve overlap between existing semantic controls and explicit automation.

Required principle:

> Once a lower-level continuous control becomes an accepted explicit creative decision, higher-level semantic refinement may not silently rewrite it unless the user explicitly authorizes that scope.

This is analogous to M6 exact-note precedence.

### 11. Browser and interchange implications

R0 should define future integration contracts but not claim implementation:

- Inspect automation lane UI;
- real-browser point editing;
- DAWproject automation export/import;
- automation reconciliation;
- renderer/device adapter mapping.

Each requires later executable evidence.

### 12. Backward compatibility

Existing projects without canonical automation material must remain valid. Compiler-generated control events must not be reverse-mapped into fabricated canonical automation.

## Required M7-R0 deliverables / 필수 산출물

At minimum:

1. `docs/M7_AUTOMATION_AUTHORITY.md`
2. `docs/M7_ACCEPTANCE.md`
3. canonical automation-material schema proposal;
4. automation-edit-candidate schema proposal;
5. automation authority-result schema proposal;
6. stable automation-lock/target design if required;
7. valid/invalid fixtures;
8. contract/schema tests;
9. `evidence/M7_R0_VALIDATION.md` proving contract/design consistency only.

R0 must be labeled **CONTRACT/DESIGN ONLY**. It may not claim automation runtime, Browser lanes, real audio impact or DAW automation interoperability.

## Recommended M7 sequence / 권장 M7 순서

This is a proposed sequence to be ratified by R0, not an already validated roadmap:

```text
M7-R0 — Automation Authority & Canonical Model             CONTRACT/DESIGN
M7-R1 — Typed Automation Material + Edit Engine            future
M7-R2 — Browser Studio Automation Lane / Inspect Surface   future
M7-R3 — Real-browser Automation E2E + Conflict UX          future
M7-R4 — Bounded Renderer/Interchange Automation Mapping    future
```

R0 may revise later stages if repository evidence shows a better decomposition.

## Scope control / 범위 통제

Do not claim in M7-R0:

- runtime automation editing;
- arbitrary plugin automation;
- mixer console implementation;
- VST/AU/CLAP hosting;
- waveform/destructive audio editing;
- arbitrary external DAW automation reverse mapping;
- tempo-map authority unless separately contracted;
- real-time MIDI recording;
- human-subject usability/perceptual superiority.

## Execution discipline / 실행 규율

```text
M6-R4 state closure
→ create M7-R0 Issue
→ fresh design branch from canonical state-closure main
→ inspect thesis + M0/M1/M2/M6 authority precedents
→ draft schemas/contracts
→ fixtures + contract tests
→ PR
→ exact-head full CI/regressions
→ durable R0 validation
→ evidence-bearing rerun
→ expected-head merge
→ state closure to ratified next M7 stage
```

**Repository evidence remains authoritative over conversation/model memory.**
