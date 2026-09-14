# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation**. The accepted Music Blueprint/project revision is creative authority; Music IR, Browser state, renderer/plugin state and interchange/DAW state are derived or non-canonical.

## Current canonical status / 현재 공식 상태

**M0 → M7-R1 are validated within their explicitly bounded repository claims.**

```text
M6-R0  exact-note authority/data model                 VALIDATED — DESIGN
M6-R1  typed exact-note runtime                        VALIDATED — BOUNDED
M6-R2  Browser Studio piano roll                       VALIDATED — BOUNDED
M6-R3  real Chromium exact-note E2E/conflict UX        VALIDATED — BOUNDED
M6-R4  source-bound DAWproject note reconciliation     VALIDATED — BOUNDED
M7-R0  automation authority/data model                 VALIDATED — CONTRACT/DESIGN ONLY
M7-R1  canonical automation trusted-core runtime       VALIDATED — BOUNDED CORE RUNTIME
```

### M7-R1 validated boundary

M7-R1 integrates the R0 automation contract into accepted Blueprint/project authority without granting derived state authority:

```text
accepted Blueprint
→ optional canonical materials.automation
→ source-bound AutomationEditCandidate
→ stable lane/point identity + time/range + inherited lock authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit M2 Accept only
→ immutable accepted revision
```

Validated properties include:

- legacy Blueprints remain valid and do not acquire fabricated automation;
- deterministic empty automation material/hash for legacy source binding;
- exactly five primitives: `INSERT_POINT / DELETE_POINT / MOVE_POINT / SET_VALUE / SET_INTERPOLATION`;
- stable lane/point identity independent of array order;
- stale source, unknown identity, duplicate point ID/beat, out-of-range value and unsupported interpolation fail closed;
- inherited HARD exact/presence automation locks block conflicting edits;
- direct M2 commit cannot bypass inherited HARD automation authority;
- Preview has no Project or Music IR mutation authority;
- explicit M2 Accept advances exactly one accepted revision.

Durable evidence: `evidence/M7_R1_VALIDATION.md`.

## Exact next bounded milestone / 정확한 다음 마일스톤

> **M7-R2 — Browser Studio Automation Lane / Inspect Surface**

R2 may expose the already-validated M7-R1 authority through Browser Studio Inspect only. The Browser must remain a proposal surface, not canonical state.

Required bounded path:

```text
accepted M7-R1 automation material
→ Browser Inspect projection
→ stable lane/point DOM mapping
→ user point edit gesture
→ typed AutomationEditCandidate
→ existing M7-R1 authority
→ READY_FOR_PREVIEW or BLOCKED
→ Preview / Accept / Discard
```

R2 must not yet claim automation-to-audio lowering/rendering, plug-in/device mapping, DAW automation reconciliation, real-time MIDI/OSC or arbitrary tempo maps.

## One state, four depths / 하나의 상태, 네 가지 깊이

- **Direct** — natural-language creation/refinement and audition
- **Shape** — semantic axes, sections, structure and locks
- **Inspect** — exact notes plus bounded explicit automation editing after M7-R2 validation
- **Code** — validated JSON, API/CLI, programmable transforms and evidence

These remain views over one canonical project state, not separate products.

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
Music IR — derived execution state
        ↓
Renderer / Interchange / Evaluation adapters
```

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
| M7-R2 Browser Studio Automation Lane / Inspect Surface | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |

## M7-R1 final evidence / M7-R1 최종 근거

- Issue `#71` — **COMPLETED**
- PR `#72` — **MERGED**
- implementation merge/main: `877ed9b7e7f90101ffcdb6891bd75631807053e2`
- final evidence-bearing exact head: `abe1f9c92751e0cdde935b34f4a17f1e1fc20548`
- M7-R1 workflow `34795684053` — **SUCCESS**
- MUSICA CI `34795683991` — **SUCCESS**
- M7-R0 regression `34795684183` — **SUCCESS**
- M6-R4 `34795684200` — **SUCCESS**
- M6-R3 `34795683988` — **SUCCESS**
- M6-R2 `34795683981` — **SUCCESS**
- M6-R1 `34795684023` — **SUCCESS**
- M5-R3 `34795684054` — **SUCCESS**
- M5-R4 `34795683984` — **SUCCESS**
- final artifact ID `10330005742`
- packaging SHA-256 `178d86faf11bfd859b84fc0c60363a493f9ffa8530dab27567ccd0b2e03ea638`
- internal manifest SHA-256 `b21dfd8e6b7c61ceee8b5613f8c65bb4857209a050cffe92eb8cabe33232ed5e`
- pre-durable vs successor evidence tree: **15 files / 0 differences**

## Current non-claims / 현재 비주장

MUSICA does not yet validate:

- Browser automation-lane UI or real-browser automation editing;
- automation lowering into Music IR or audible renderer control;
- arbitrary plug-in/mixer/device automation or VST/AU/CLAP hosting;
- DAW automation import/export/reconciliation;
- real-time MIDI/OSC automation;
- arbitrary tempo-map automation;
- lane creation/deletion or parameter reassignment in automation runtime;
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

Before substantive M7-R2 work read `governance/SOURCE_OF_TRUTH.md`, `docs/PRODUCT_THESIS.md`, `docs/M7_AUTOMATION_AUTHORITY.md`, `evidence/M7_R0_VALIDATION.md`, `evidence/M7_R1_VALIDATION.md`, M7 schemas/runtime, Browser Studio precedent, `memory/CURRENT_STATE.md`, and `memory/NEXT_ACTION.md`.

**Repository evidence remains authoritative over conversation/model memory.**
