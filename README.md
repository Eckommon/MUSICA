# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation**. The accepted Music Blueprint/project revision is creative authority. Music IR, Browser state, derived automation execution, renderer/plugin state and interchange/DAW state are derived or non-canonical.

## Current canonical status / 현재 공식 상태

**M0 → M7-R3 are validated within their explicitly bounded repository claims.**

```text
M6-R0  exact-note authority/data model                    VALIDATED — DESIGN
M6-R1  typed exact-note runtime                           VALIDATED — BOUNDED
M6-R2  Browser Studio piano roll                          VALIDATED — BOUNDED
M6-R3  real Chromium exact-note E2E/conflict UX           VALIDATED — BOUNDED
M6-R4  source-bound DAWproject note reconciliation        VALIDATED — BOUNDED
M7-R0  automation authority/data model                    VALIDATED — CONTRACT/DESIGN ONLY
M7-R1  canonical automation trusted-core runtime          VALIDATED — BOUNDED CORE RUNTIME
M7-R2  Browser Studio automation Inspect/edit surface     VALIDATED — BOUNDED REAL-BROWSER SURFACE
M7-R3  deterministic derived automation execution         VALIDATED — BOUNDED DERIVED EXECUTION
```

## M7-R3 validated boundary

```text
accepted Blueprint materials.automation
→ exact source binding
→ automation-execution-v0
→ stable lane / parameter / point provenance
→ deterministic beat → tick conversion (PPQ 480, Decimal ROUND_HALF_UP)
→ explicit hold / linear segments
→ backend_mapping = UNMAPPED
```

Validated properties include:

- derived execution is explicitly `derived_noncanonical`;
- exact project/revision/Blueprint/material hashes are retained;
- missing canonical automation yields an explicit empty derived execution, not reverse inference;
- stable lane/point/parameter identity is retained;
- canonical beat time is preserved while deterministic integer ticks are derived;
- `hold` and `linear` remain typed segment semantics;
- distinct source beats collapsing to one tick fail closed;
- backend/MIDI/plugin addresses are not guessed;
- backend-address injection is schema-rejected;
- no Project, Blueprint, Browser Preview, Music IR or renderer state is mutated;
- existing compiler semantic CC path remains regression-stable;
- repeated R3 evidence is byte-identical.

Durable evidence: `evidence/M7_R3_VALIDATION.md`.

## M7-R3 final evidence / M7-R3 최종 근거

- Issue `#77` — **COMPLETED**
- PR `#78` — **MERGED**
- implementation merge/main: `f4dbbf78c1556815228ef1446192a1308707eec9`
- pre-durable exact head: `09eaa538128a302f82374764becf1ddfc87eafda`
- final evidence-bearing successor head: `43d4568362cc26c23e9747da2a15b29c0cf4fe4d`
- successor M7-R3 workflow `34822272947` — **SUCCESS**
- successor MUSICA CI `34822272980` — **SUCCESS**
- successor M7-R2 `34822272949` — **SUCCESS**
- successor M7-R1 `34822272975` — **SUCCESS**
- successor M7-R0 `34822272967` — **SUCCESS**
- successor M6-R4 `34822272955` — **SUCCESS**
- successor M6-R3 `34822272953` — **SUCCESS**
- successor M6-R2 `34822272968` — **SUCCESS**
- successor M6-R1 `34822272956` — **SUCCESS**
- successor M5-R3 `34822273054` — **SUCCESS**
- successor M5-R4 `34822272987` — **SUCCESS**
- successor artifact ID `10338193487`
- successor packaging SHA-256 `48b157aefb9bd6067aa7a2d4b187693294a2b7417869c35a4daa56bea5d1f61c`
- internal manifest SHA-256 `864135b90e650496e89d1e6f9b293e709f2fd187a3ddb639e155136c028207db`
- derived execution SHA-256 `2874fc72e78fd817a53ad2c20348cf56403af53fa24fdfc57f7f2aa1ac2444c7`
- successor manifest records: **10/10 exact SHA-256 + size matches**
- pre-durable vs successor extracted evidence: **11 files / 0 differences**

## Exact next bounded milestone / 정확한 다음 마일스톤

> **M7-R4 — Reference Renderer Automation Mapping & Audible Evidence**

R4 must remain deliberately narrow. It will validate **one explicit renderer-specific mapping only**:

```text
canonical parameter: mix.gain
scope: project
unit: normalized
renderer: musica-reference-local only
```

The recommended one-way execution path is:

```text
accepted Blueprint automation
→ validated R3 automation-execution-v0
→ exact execution hash + exact Music IR hash
→ renderer-specific automation render plan
→ explicit mix.gain mapping
→ deterministic gain envelope
→ reference WAV output + machine audio evidence
```

R4 must **not** reuse CC11 as canonical `mix.gain`, mutate `automation-execution-v0`, or grant renderer state reverse authority. Existing `render_wav()` and semantic MIDI-CC behavior should remain regression-stable; the automation-aware renderer path should be additive and explicitly source/hash-bound.

## Canonical authority / 공식 권한 구조

```text
User / AI / bounded proposal
        ↓
typed non-canonical candidate
        ↓
source binding + locks + constraints + invariants
        ↓
READY_FOR_PREVIEW or BLOCKED
        ↓
PREVIEW · NOT ACCEPTED
        ↓ explicit Accept only
M2 Project & Version Engine
        ↓
Accepted Music Blueprint revision
        ↓ trusted deterministic lowering
Music IR + automation-execution-v0
        ↓ explicit renderer mapping policy
Renderer artifacts / evidence
```

No renderer, Browser, Music IR, derived execution package or DAW/plugin state may promote itself back into canonical Blueprint authority.

## Validated milestone stack / 검증 마일스톤

| Milestone | Status | Evidence |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4 Browser Studio / Usable MVP | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` → `M4_R3_VALIDATION.md` |
| M5 Rendering / Interchange / Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R1_VALIDATION.md` → `M5_R4_VALIDATION.md` |
| M6 Exact-Note Precision Editing R0→R4 | **VALIDATED — BOUNDED** | `evidence/M6_R0_VALIDATION.md` → `M6_R4_VALIDATION.md` |
| M7-R0 Automation Authority & Canonical Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M7_R0_VALIDATION.md` |
| M7-R1 Canonical Automation Runtime & Blueprint Integration | **VALIDATED — BOUNDED CORE RUNTIME** | `evidence/M7_R1_VALIDATION.md` |
| M7-R2 Browser Studio Automation Lane / Inspect Surface | **VALIDATED — BOUNDED REAL-BROWSER SURFACE** | `evidence/M7_R2_VALIDATION.md` |
| M7-R3 Deterministic Automation Lowering & Derived Execution Boundary | **VALIDATED — BOUNDED DERIVED EXECUTION** | `evidence/M7_R3_VALIDATION.md` |
| M7-R4 Reference Renderer Automation Mapping & Audible Evidence | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |

## Current non-claims / 현재 비주장

MUSICA does not yet validate:

- audible application of canonical automation;
- arbitrary canonical parameter → renderer/MIDI/plugin mapping;
- arbitrary plug-in/mixer/device mapping or VST/AU/CLAP hosting;
- DAW automation import/export/reconciliation;
- real-time MIDI/OSC automation;
- arbitrary tempo-map automation;
- lane creation/deletion or parameter reassignment;
- spline/bezier/exponential interpolation;
- live OpenAI API execution;
- human-subject usability/preference or perceptual superiority;
- waveform/destructive audio editing, cloud collaboration or installer/signing.

## Repository as source of truth / Repo 공식 근거

```text
accepted repository tests/artifacts/evidence
> merged specifications/current-state records
> Issue/PR/exact-head CI evidence
> conversation context
> model memory/inference
```

Before substantive M7-R4 work read `governance/SOURCE_OF_TRUTH.md`, `docs/PRODUCT_THESIS.md`, `docs/M7_AUTOMATION_AUTHORITY.md`, `evidence/M7_R3_VALIDATION.md`, `schemas/automation-execution-v0.schema.json`, `src/musica/automation_lowering.py`, `src/musica/compiler.py`, `src/musica/render.py`, `src/musica/renderer.py`, `memory/CURRENT_STATE.md`, and `memory/NEXT_ACTION.md`.

**Repository evidence remains authoritative over conversation/model memory.**