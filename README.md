# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation**. The accepted Music Blueprint/project revision is creative authority; Music IR, Browser state, renderer/plugin state and interchange/DAW state are derived or non-canonical.

## Current canonical status / 현재 공식 상태

**M0 → M7-R2 are validated within their explicitly bounded repository claims.**

```text
M6-R0  exact-note authority/data model                 VALIDATED — DESIGN
M6-R1  typed exact-note runtime                        VALIDATED — BOUNDED
M6-R2  Browser Studio piano roll                       VALIDATED — BOUNDED
M6-R3  real Chromium exact-note E2E/conflict UX        VALIDATED — BOUNDED
M6-R4  source-bound DAWproject note reconciliation     VALIDATED — BOUNDED
M7-R0  automation authority/data model                 VALIDATED — CONTRACT/DESIGN ONLY
M7-R1  canonical automation trusted-core runtime       VALIDATED — BOUNDED CORE RUNTIME
M7-R2  Browser Studio automation Inspect/edit surface  VALIDATED — BOUNDED REAL-BROWSER SURFACE
```

### M7-R2 validated boundary

```text
accepted Blueprint materials.automation
→ Browser Studio Inspect projection
→ stable lane_id / point_id / parameter_id
→ keyboard/form/table bounded point editing
→ source-bound automation-edit-candidate-v0
→ existing M7-R1 authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit existing M2 Accept or Discard
```

Validated properties include:

- legacy/no-automation projects show an explicit empty state and fabricate no lanes;
- Browser source binds project/revision/Blueprint hash/automation-material hash;
- exactly five point primitives are exercised through real Chromium;
- Browser geometry and DOM order remain presentation only;
- Preview leaves the accepted ref unchanged;
- explicit Accept advances the accepted M2 revision and restart/reopen preserves it;
- Discard preserves accepted state;
- HARD exact and HARD presence conflicts fail closed with visible rule context;
- stale Browser source fails closed and reprojects current accepted authority;
- cross-surface pending Preview replacement is blocked;
- Browser console/page errors are zero in dedicated evidence;
- `audible_automation_validated=false` remains explicit.

Durable evidence: `evidence/M7_R2_VALIDATION.md`.

## M7-R2 final evidence / M7-R2 최종 근거

- Issue `#74` — **COMPLETED**
- PR `#75` — **MERGED**
- implementation merge/main: `b5f73ac8ebf83b0bfdcca277924af9b7c0fcc263`
- pre-durable exact head: `5396d38dad12247d8c55a40d677738fc51357569`
- final evidence-bearing successor head: `90b6d3eec6621cd2d666c544863d1c8e28fd145f`
- successor M7-R2 workflow `34798196898` — **SUCCESS**
- successor MUSICA CI `34798196910` — **SUCCESS**
- successor M7-R1 `34798196888` — **SUCCESS**
- successor M7-R0 `34798196884` — **SUCCESS**
- successor M6-R4 `34798196893` — **SUCCESS**
- successor M6-R3 `34798196887` — **SUCCESS**
- successor M6-R2 `34798196909` — **SUCCESS**
- successor M6-R1 `34798196960` — **SUCCESS**
- successor M5-R3 `34798196949` — **SUCCESS**
- successor M5-R4 `34798196938` — **SUCCESS**
- successor artifact ID `10330402763`
- successor packaging SHA-256 `dd192e04c12ce9d8f7e474717ac365acc0d2fb00ba2b8d9e5e4ea4cbe9d67ef2`
- successor internal manifest SHA-256 `c3a4026394408b266943d3f9aca15393112780cf13114efd8f8a56b3e520f133`
- successor manifest records: **19/19 exact SHA-256 + size matches**
- pre-durable vs successor `proof.json`: **identical**

## Exact next bounded milestone / 정확한 다음 마일스톤

> **M7-R3 — Deterministic Automation Lowering & Derived Execution Boundary**

R3 must establish a backend-independent **derived automation execution representation** before any audible renderer claim. Existing Music IR `controlEvent` is MIDI-controller-specific, so canonical `parameter_id` must not be silently collapsed into CC numbers or plug-in addresses.

Required direction:

```text
accepted canonical automation material
→ source-bound deterministic lowering
→ derived automation execution representation
→ stable source/lane/point/parameter provenance
→ deterministic beat/time/interpolation expansion
→ explicit supported/unsupported parameter mapping result
```

R3 must remain one-way and non-authoritative:

```text
canonical Blueprint automation → derived execution
NOT derived execution → canonical automation
```

R3 does **not** yet claim audible automation rendering. Actual renderer application/audio-difference evidence is reserved for a later bounded milestone after the derived execution contract is validated.

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
Derived execution state / Music IR
        ↓
Renderer / Interchange / Evaluation adapters
```

## One state, four depths / 하나의 상태, 네 가지 깊이

- **Direct** — natural-language creation/refinement and audition
- **Shape** — semantic axes, sections, structure and locks
- **Inspect** — exact notes plus validated bounded automation editing
- **Code** — validated JSON, API/CLI, programmable transforms and evidence

These remain views over one canonical project state, not separate products.

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
| M7-R3 Deterministic Automation Lowering & Derived Execution Boundary | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |

## Current non-claims / 현재 비주장

MUSICA does not yet validate:

- canonical automation lowering into a backend-independent derived execution contract;
- audible renderer application of canonical automation;
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

Before substantive M7-R3 work read `governance/SOURCE_OF_TRUTH.md`, `docs/PRODUCT_THESIS.md`, `docs/M7_AUTOMATION_AUTHORITY.md`, `evidence/M7_R2_VALIDATION.md`, `schemas/music-ir-v0.schema.json`, `src/musica/compiler.py`, `src/musica/render.py`, `src/musica/renderer.py`, `memory/CURRENT_STATE.md`, and `memory/NEXT_ACTION.md`.

**Repository evidence remains authoritative over conversation/model memory.**
