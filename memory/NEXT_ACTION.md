# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M7-R1 — BOUNDED CANONICAL AUTOMATION RUNTIME & BLUEPRINT INTEGRATION / M7-R1 — 제한된 Canonical Automation Runtime 및 Blueprint 통합**

M7-R0 is `VALIDATED — CONTRACT/DESIGN ONLY`. The exact next task is to implement the smallest trusted-core runtime that makes the ratified standalone automation contract safely usable inside accepted MUSICA project authority.

M7-R0는 `VALIDATED — CONTRACT/DESIGN ONLY`입니다. 정확한 다음 작업은 비준된 standalone automation contract를 accepted MUSICA project authority 안에서 안전하게 사용할 수 있게 하는 최소 trusted-core runtime을 구현하는 것입니다.

## Canonical starting point / 공식 시작점

- M7-R0 Issue `#68` — **COMPLETED**
- M7-R0 PR `#69` — **MERGED**
- M7-R0 implementation merge/main: `672ce33ee8b8fe05717ad1a5a0c416714de88d2d`
- final evidence-bearing head: `5b5aeb8c6bee3f8e2d48f41543b5bd5cd33e43ef`
- final MUSICA CI `34791538725` — **SUCCESS**
- final M7-R0 workflow `34791538703` — **SUCCESS**
- final M6-R4 `34791538853` — **SUCCESS**
- final M6-R3 `34791538669` — **SUCCESS**
- final M6-R2 `34791538762` — **SUCCESS**
- final M6-R1 `34791538672` — **SUCCESS**
- final M5-R3 `34791538695` — **SUCCESS**
- final M5-R4 `34791538743` — **SUCCESS**
- final M7 artifact ID `10328327862`
- outer artifact SHA-256 `1360f29d6568a75e7bcf740e605e37fd1f97df9715bdb7326133047afd2753a5`
- internal manifest SHA-256 `aab674c3953abcbca94d659da4d3627d65a682b4039510f6f6e255e08efee5`
- contract/source hash ledger: **21 files**
- pre-durable vs successor internal evidence tree: **3 files / 0 differences**
- durable evidence: `evidence/M7_R0_VALIDATION.md`

## R0 facts R1 must preserve / R1이 보존해야 할 R0 사실

```text
canonical scope       = project | part
canonical time        = quarter_note_beat / origin 0.0
units                 = normalized | decibel | hertz | semitone | ratio
interpolation         = hold | linear
stable identity       = lane_id + point_id + parameter_id
primitive operations  = INSERT_POINT / DELETE_POINT / MOVE_POINT / SET_VALUE / SET_INTERPOLATION
candidate authority   = non-canonical, source-bound, preview_only=true
result states         = READY_FOR_PREVIEW | BLOCKED
```

Forbidden authority remains:

```text
Music IR event → canonical automation
renderer/plugin state → accepted Blueprint
Browser point/order → accepted identity
external DAW automation → accepted state
AI curve → implicit Accept
```

## Required M7-R1 implementation / 필수 구현

### 1. Backward-compatible Blueprint integration

Integrate canonical automation material into the accepted Blueprint/project model without invalidating existing projects.

Required properties:

- old projects with no automation remain valid and semantically unchanged;
- no migration may fabricate canonical automation from semantic curves, Music IR, renderer state or DAW artifacts;
- new automation material must validate against `automation-material-v0` plus executable R0 cross-field invariants;
- storage location and schema versioning must be explicit and deterministic;
- canonical serialization/hash behavior must be stable.

A missing automation block means **no accepted explicit automation**, not an inferred curve.

### 2. Source-bound automation material hash

For every candidate bind:

```text
project_id
accepted revision_id
canonical Blueprint SHA-256
canonical automation-material SHA-256
```

If accepted source differs, fail closed as `STALE_SOURCE` or a stronger typed source conflict. No silent rebase.

For a valid legacy project with no accepted explicit automation, R1 must define one deterministic empty-material/source-hash policy rather than using null/implicit inference inconsistently.

### 3. Core edit engine

Implement exactly the ratified five point operations:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
```

Do not add lane creation/deletion or parameter reassignment unless a later contract ratifies them.

Operation semantics must preserve:

- stable lane/point IDs;
- canonical ordering;
- unique point beat within lane;
- unique IDs and target signatures;
- declared unit/range;
- `hold | linear` only.

### 4. Candidate authority and Preview

Reuse MUSICA's existing authority pattern rather than create a parallel project mutation engine:

```text
accepted Blueprint
→ source-bound AutomationEditCandidate
→ validate source + identities + ranges + locks + invariants
→ READY_FOR_PREVIEW or BLOCKED
→ candidate Blueprint / diff as non-canonical Preview
→ accepted ref unchanged
```

No edit call may implicitly commit.

### 5. Explicit Accept / Discard through M2

Required positive path:

```text
READY_FOR_PREVIEW
→ Preview exists, accepted ref unchanged
→ explicit Accept
→ exactly one M2 revision advance
→ accepted canonical automation material persists
```

Required Discard path:

```text
READY_FOR_PREVIEW
→ explicit Discard
→ accepted ref unchanged
```

Use existing M2 integrity/audit/version authority.

### 6. Stable identity checks

R1 must never use array position as lane/point identity.

At minimum fail closed on:

- unknown lane ID;
- unknown point ID;
- duplicate inserted point ID;
- move into an occupied beat;
- identity mismatch after source changed;
- attempts to mutate `parameter_id` through a point primitive.

### 7. Range/unit/interpolation authority

For every result candidate, revalidate the whole resulting automation material.

At minimum fail closed on:

- value outside lane min/max;
- unsupported unit;
- unsupported interpolation;
- invalid min/max;
- non-canonical ordering;
- duplicate beats/IDs/targets.

No renderer-side clamping or implicit normalization may rescue an invalid canonical edit.

### 8. HARD/SOFT lock runtime enforcement

R1 must implement runtime lock checks using `automation-lock-v0`.

Minimum HARD behavior:

```text
protected lane/point/property
→ conflicting operation
→ BLOCKED / HARD_LOCK_VIOLATION
→ conflict carries lane_id / point_id / lock rule_id when applicable
→ preview_generation_allowed = false
→ accepted ref unchanged
```

SOFT behavior must remain explicitly non-authoritative relative to user choice and hard constraints. R1 may keep SOFT behavior minimal, but it must not accidentally block as HARD or disappear silently from evidence.

### 9. Semantic-control coexistence boundary

R1 must preserve the R0 precedence rule but should avoid implementing a broad semantic-to-automation transform engine.

Required minimum:

- accepted explicit automation is not silently regenerated by unrelated semantic refinement;
- when existing semantic runtime touches a scope that contains explicit protected automation, behavior must either preserve it or fail closed under an explicit rule;
- no hidden lowering from semantic control into canonical automation.

If a full overlap resolver is not needed for the minimal runtime, state it as a later milestone non-claim and test non-fabrication.

### 10. No derived-state authority

R1 must not add reverse authority from:

- Music IR;
- Browser DOM/canvas;
- renderer controls;
- plug-in parameters;
- DAW automation;
- MIDI CC/OSC.

Those remain future adapter/UI/reconciliation milestones.

## Required tests / 필수 테스트

At minimum prove:

1. legacy Blueprint/project with no automation remains valid and unchanged;
2. automation-capable Blueprint stores valid canonical material;
3. deterministic empty-material/source-hash policy;
4. material survives project create/read/restart path;
5. all five primitive operations build valid non-canonical candidates;
6. INSERT adds a stable point and preserves canonical order;
7. DELETE removes exactly the targeted stable point;
8. MOVE preserves point identity;
9. SET_VALUE preserves lane/point identity and obeys range;
10. SET_INTERPOLATION permits only hold/linear;
11. Preview leaves accepted ref unchanged;
12. explicit Accept advances exactly once through M2;
13. Discard leaves accepted ref unchanged;
14. stale revision/hash blocks;
15. unknown lane/point blocks;
16. duplicate ID/beat blocks;
17. out-of-range value blocks;
18. HARD exact value lock blocks a conflicting SET_VALUE;
19. HARD presence lock blocks protected lane/point deletion as applicable;
20. blocked candidate produces no Preview;
21. derived Music IR/browser/renderer state cannot directly mutate canonical automation;
22. old M0→M7-R0 contract tests remain green;
23. Python 3.11/3.12 full suite remains green;
24. M6-R4/R3/R2/R1 and M5-R3/R4 regressions remain green.

## Recommended implementation shape / 권장 구현 구조

Reuse existing authority patterns, but do not couple automation identity to the exact-note engine.

Likely minimal components:

```text
Blueprint schema integration / migration-safe optional automation material
src/musica/automation_edit.py
  - material projection/hash
  - candidate application to a copy
  - source/stale checks
  - stable identity resolution
  - lock/range/invariant authority
  - Preview construction
  - explicit M2 Accept wrapper

tests/test_m7_r1_automation_edit.py
M7-R1 dedicated evidence generator/workflow
```

`src/musica/automation_contracts.py` remains the R0 cross-field contract checker and should be reused rather than duplicated.

## Canonical evidence target / 공식 근거 목표

A later R1 artifact should include machine-readable proof of:

```text
source Blueprint + automation hashes
all five primitive candidates/results
accepted ref before/after Preview
explicit Accept revision
Discard proof
stale-source negative
unknown-identity negative
range negative
HARD-lock negative
legacy no-fabrication proof
project integrity
manifest/hash bindings
```

## Scope control / 범위 통제

Do **not** add or claim in M7-R1:

- Browser automation lane UI;
- real-browser automation E2E;
- audible automation rendering;
- Music IR/renderer automation execution unless separately contracted;
- VST/AU/CLAP hosting or mapping;
- external DAW automation reconciliation;
- real-time MIDI/OSC;
- lane creation/deletion/parameter reassignment beyond the R0 primitive vocabulary;
- arbitrary curve interpolation;
- arbitrary tempo-map automation;
- human-subject/perceptual claims.

## Promotion claim if successful / 성공 시 허용 주장

The maximum intended R1 claim is:

> **MUSICA can store bounded canonical explicit automation in accepted project authority and apply the five ratified stable-ID point-edit primitives through source-bound fail-closed Preview/Accept semantics, while legacy projects and derived execution state remain non-authoritative.**

## Execution discipline / 실행 규율

```text
M7-R0 state closure
→ create M7-R1 Issue
→ fresh implementation branch from canonical state-closure main
→ inspect Blueprint/M2/M6 precedent
→ optional backward-compatible Blueprint integration
→ trusted automation edit engine
→ targeted tests + dedicated evidence
→ PR
→ exact-head full regressions
→ artifact inspection
→ durable M7_R1 validation
→ evidence-bearing successor rerun
→ expected-head merge
→ Issue completed
→ state-only closure to next bounded mission
```

**Repository evidence remains authoritative over conversation/model memory.**
