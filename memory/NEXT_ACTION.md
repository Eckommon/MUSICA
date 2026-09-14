# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M7-R3 — DETERMINISTIC AUTOMATION LOWERING & DERIVED EXECUTION BOUNDARY**

M7-R2 is `VALIDATED — BOUNDED REAL-BROWSER SURFACE`. The next mission is to make accepted canonical automation executable **without collapsing backend-independent canonical parameter identity into MIDI CC, renderer or plug-in addresses**.

## Canonical starting point / 공식 시작점

- M7-R2 Issue `#74` — **COMPLETED**
- M7-R2 PR `#75` — **MERGED**
- implementation merge/main: `b5f73ac8ebf83b0bfdcca277924af9b7c0fcc263`
- final evidence-bearing successor head: `90b6d3eec6621cd2d666c544863d1c8e28fd145f`
- successor M7-R2 workflow `34798196898` — **SUCCESS**
- successor MUSICA CI `34798196910` — **SUCCESS**
- successor regressions M7-R1/R0, M6-R4/R3/R2/R1, M5-R3/R4 — **ALL SUCCESS**
- successor artifact ID `10330402763`
- packaging SHA-256 `dd192e04c12ce9d8f7e474717ac365acc0d2fb00ba2b8d9e5e4ea4cbe9d67ef2`
- internal manifest SHA-256 `c3a4026394408b266943d3f9aca15393112780cf13114efd8f8a56b3e520f133`
- manifest integrity: **19/19 exact**
- pre-durable vs successor `proof.json`: **identical**
- durable evidence: `evidence/M7_R2_VALIDATION.md`

## Architecture fact R3 must respect / R3가 지켜야 할 구조 사실

Current `music-ir-v0` control events are MIDI-like:

```text
controlEvent = { type, tick, controller: 0..127, value: 0..127 }
```

Current compiler uses CC11 / CC74 / CC71 for semantic preview controls. The local WAV renderer interprets those CCs directly for expression / brightness / warmth.

Canonical automation instead uses:

```text
lane_id
point_id
parameter_id          # backend-independent dotted identity
scope                 # project | part
unit                  # normalized | decibel | hertz | semitone | ratio
beat
value
interpolation         # hold | linear
```

Therefore this is forbidden:

```text
canonical parameter_id == arbitrary MIDI CC / plug-in address
```

A typed derived execution layer must sit between canonical authority and backend-specific rendering.

## Required M7-R3 design / 필수 설계

### 1. Derived execution contract

Introduce a versioned contract, recommended working name:

```text
automation-execution-v0
```

It is **derived, non-canonical, deterministic** and must bind the accepted source exactly.

Required top-level provenance at minimum:

```text
execution_version
source.project_id
source.revision_id
source.blueprint_sha256
source.automation_material_sha256
lowering.compiler_id
lowering.compiler_version
lowering.policy_id
lanes[]
unsupported[]
```

### 2. Preserve canonical identity

Every derived lane/event must preserve enough provenance to trace back to:

```text
lane_id
parameter_id
scope
part_id? / section_id?
point_id or source point pair
unit
```

Backend-specific address is **not** canonical identity and should not be required in R3.

### 3. Time model

Canonical time is `quarter_note_beat`. R3 may derive integer tick time using the repository's current PPQ only if the conversion is explicit and deterministic.

Required proof:

```text
beat 0.0 → tick 0
beat N → deterministic round/quantization rule
same source → same derived ticks
```

No arbitrary tempo map support is added. Fixed-tempo bound remains.

### 4. Interpolation semantics

R3 must represent both:

```text
hold
linear
```

without pretending that all renderers can execute them identically.

Recommended design:

- retain source points exactly;
- derive explicit segments between stable source points;
- segment references stable source `point_id` endpoints;
- `hold` and `linear` remain typed execution semantics;
- do not densify to arbitrary sampled MIDI values unless a separate renderer adapter requests it.

This prevents resolution/sampling policy from becoming hidden authority.

### 5. Supported vs unsupported parameter mapping

R3 should define an explicit registry or policy for which canonical parameter domains are understood by the derived layer. The derived layer may carry a generic parameter unchanged even when no renderer mapping exists.

If a lane cannot be lowered safely, report typed unsupported status rather than guessing.

At minimum distinguish:

```text
DERIVED_GENERIC       # valid canonical lane represented in execution contract
UNSUPPORTED_SCOPE
UNSUPPORTED_UNIT
UNSUPPORTED_PARAMETER
INVALID_SOURCE
```

Exact vocabulary may be refined after implementation inspection, but all failures must be deterministic and machine-readable.

### 6. Legacy/no-automation behavior

For accepted Blueprint with no canonical automation:

```text
lowering result = valid empty derived automation execution
```

No semantic/Music-IR/renderer reverse inference is allowed.

### 7. Determinism

The same accepted source must produce byte-identical derived execution JSON where no timestamp/random identifier is present.

Recommended evidence:

```text
run A execution.json
run B execution.json
SHA-256(A) == SHA-256(B)
```

### 8. Authority boundary

R3 lowering must be a pure derived operation:

```text
accepted Blueprint → execution
```

It must not:

- create a new accepted revision;
- mutate automation material;
- create Browser Preview;
- back-propagate Music IR / renderer changes;
- infer canonical automation from existing semantic CC events.

## Required implementation direction / 구현 방향

Prefer a new isolated module such as:

```text
src/musica/automation_lowering.py
```

Do not modify the current semantic `controlEvent` path until the R3 derived contract is validated. This keeps existing M0→M7-R2 renderer behavior regression-stable.

Likely new assets:

```text
schemas/automation-execution-v0.schema.json
src/musica/automation_lowering.py
tests/test_m7_r3_automation_lowering.py
src/musica/m7_r3_demo.py
.github/workflows/m7-r3-automation-lowering-evidence.yml
```

Naming may change only if repository inspection reveals a better existing pattern.

## Required tests / 필수 테스트

At minimum prove:

1. legacy/no-automation → valid empty derived execution;
2. automation-capable accepted Blueprint → source-bound derived execution;
3. source Blueprint/material hashes are exact;
4. stable lane/parameter/point provenance is retained;
5. deterministic beat→tick mapping;
6. hold segment semantics preserved;
7. linear segment semantics preserved;
8. lane/point array reordering cannot change canonical identity/output ordering rules;
9. invalid/missing source identity fails closed;
10. unsupported unit/scope/parameter status is explicit, not guessed;
11. lowering causes no accepted project mutation;
12. lowering causes no canonical automation mutation;
13. derived execution cannot be promoted back into Blueprint authority;
14. same source produces byte-identical canonical execution JSON;
15. existing compiler output is unchanged for legacy and exact-note fixtures unless explicitly tested otherwise;
16. M7-R2/R1/R0 remain green;
17. M6-R4/R3/R2/R1 and M5-R3/R4 remain green;
18. Python 3.11/3.12 full suite remains green.

## Evidence target / 공식 근거 목표

Dedicated deterministic artifact should include at minimum:

```text
source-blueprint.json or source hashes
source-automation-material.json
execution-a.json
execution-b.json
execution-determinism.json
legacy-empty-execution.json
hold-linear-proof.json
unsupported-proof.json
authority-boundary-proof.json
manifest.json
```

Evidence must bind exact-head workflow execution and artifact hashes.

## Scope control / 범위 통제

Do **not** add or claim in M7-R3:

- audible automation rendering;
- arbitrary MIDI CC mapping as canonical semantics;
- plug-in/device mapping or VST/AU/CLAP hosting;
- external DAW automation import/export/reconciliation;
- MIDI CC / OSC / real-time control;
- lane creation/deletion or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential interpolation;
- Browser UI expansion beyond R2;
- human-subject/perceptual superiority.

## Maximum intended R3 claim / 성공 시 최대 주장

> **MUSICA can deterministically lower accepted canonical automation into a source-bound, backend-independent, non-authoritative derived execution representation that preserves stable parameter/lane/point provenance and explicit hold/linear semantics without silently equating canonical parameters with MIDI CC or renderer-specific addresses.**

## Expected successor after R3 / R3 이후 예상 후속

Only after R3 validation should the project consider a bounded renderer milestone such as:

> **M7-R4 — Renderer Automation Mapping & Audible Evidence**

R4 would choose one explicit renderer/backend mapping policy and prove audible application without expanding canonical authority.

## Execution discipline / 실행 규율

```text
M7-R2 state closure
→ create M7-R3 Issue
→ fresh branch from closure main
→ ratify derived execution contract
→ deterministic lowering implementation
→ unit/contract/determinism tests
→ dedicated evidence workflow
→ PR
→ exact-head full regressions
→ artifact inspection
→ durable M7_R3 validation
→ successor rerun
→ expected-head merge
→ Issue completed
→ state-only closure to renderer mapping milestone
```

**Repository evidence remains authoritative over conversation/model memory.**
