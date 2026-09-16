# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M7-R5 — STUDIO AUTOMATION AUDITION & ACCEPTED ARTIFACT PERSISTENCE: VALIDATED — BOUNDED STUDIO AUDITION & ARTIFACT PERSISTENCE**

M0→M7-R5 are validated only within their durable repository claims. Accepted Music Blueprint remains canonical creative authority. Browser, Music IR, automation execution, renderer/plugin and external DAW state remain derived or non-authoritative.

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**

## Canonical milestone ledger / 공식 마일스톤 원장

| Milestone | Status | Durable evidence |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4 Browser Studio / Usable MVP | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` → `evidence/M4_R3_VALIDATION.md` |
| M5 Rendering / Interchange / Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R1_VALIDATION.md` → `evidence/M5_R4_VALIDATION.md` |
| M6 Precision Editing R0→R4 | **VALIDATED — BOUNDED** | `evidence/M6_R0_VALIDATION.md` → `evidence/M6_R4_VALIDATION.md` |
| M7-R0 Automation Authority & Canonical Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M7_R0_VALIDATION.md` |
| M7-R1 Canonical Automation Runtime & Blueprint Integration | **VALIDATED — BOUNDED CORE RUNTIME** | `evidence/M7_R1_VALIDATION.md` |
| M7-R2 Browser Studio Automation Lane / Inspect Surface | **VALIDATED — BOUNDED REAL-BROWSER SURFACE** | `evidence/M7_R2_VALIDATION.md` |
| M7-R3 Deterministic Automation Lowering & Derived Execution Boundary | **VALIDATED — BOUNDED DERIVED EXECUTION** | `evidence/M7_R3_VALIDATION.md` |
| M7-R4 Reference Renderer Automation Mapping & Audible Evidence | **VALIDATED — BOUNDED AUDIBLE EXECUTION** | `evidence/M7_R4_VALIDATION.md` |
| M7-R5 Studio Automation Audition & Accepted Artifact Persistence | **VALIDATED — BOUNDED STUDIO AUDITION & ARTIFACT PERSISTENCE** | `evidence/M7_R5_VALIDATION.md` |
| M7-R6 Truthful Audible Automation Capability & Browser Lifecycle Inspection | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |

## M7-R5 final evidence / M7-R5 최종 근거

- Issue `#84` — **COMPLETED**
- PR `#83` — **MERGED**
- implementation merge/main: `43488fe85bb6c2fde19dc27d0dabfdb7587d7f1f`
- pre-durable exact head: `298a46a4de360d697c2fe55006cd17966c3bf1e8`
- successor evidence head: `87dd85cb2ff2f0a576db24c6b87c7ad16a32bb29`
- final validation-record head: `41f98e882e62cf638370c998447e754398c63284`
- pre-durable, successor and final-record regression sets: **13/13 SUCCESS**
- final M7-R5 workflow `35039890451` — **SUCCESS**
- final MUSICA CI `35039890429` — **SUCCESS**
- pre-durable artifact `10411768231`
- successor artifact `10412286568`
- manifest SHA-256 `ab5c99c4ab474eccac17b727cf0a502061f2691ffae5bbfab734572a90e5c772`
- pre-durable vs successor R5 evidence: **16 files / 0 differences**
- Preview/accepted/reopened WAV `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- Preview/accepted/reopened MIDI `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- R4 preservation recheck: **14 files / 0 differences**

## M7-R5 validated lifecycle

```text
accepted automation edit candidate
→ trusted pending Preview
→ candidate Music IR
→ R3 automation-execution-v0
→ R4 bounded render plan
→ automation-aware pending WAV
→ PREVIEW · NOT ACCEPTED
→ Discard OR explicit Accept
→ exact pending WAV/MIDI bound to accepted revision
→ reopen serves accepted bytes unchanged
```

Validated properties:

- accepted branch head never changes during Preview rendering;
- only `mix.gain/project/normalized` is mapped;
- `synth.cutoff` and unsupported lanes remain unmapped;
- Preview WAV differs from its unautomated baseline;
- Preview WAV = accepted WAV = reopened WAV;
- Preview MIDI = accepted MIDI = reopened MIDI;
- Discard clears pending media and restores accepted-media resolution;
- audible-install failures clear pending Preview fail-closed;
- accepted audio/renderer state gains no reverse canonical authority;
- R4 performance refactor preserves prior R4 evidence bytes exactly.

## Current capability stack / 현재 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material and accepted explicit automation material.

### Precision editing
M6 exact-note editing and M7 automation point editing use source-bound Preview/Accept authority patterns.

### Studio
Browser Studio Direct → Shape → Inspect → Code, exact-note piano roll and bounded automation Inspect/edit surface are validated. R5 now makes trusted automation Preview audio consume the validated R3→R4 path and persist exact Preview media on Accept/reopen.

### Derived execution
R3 deterministically lowers accepted/candidate canonical automation to `automation-execution-v0` without guessing backend addresses.

### Renderer
R4 maps exactly one automation family — `mix.gain/project/normalized` — through an explicit reference-renderer plan to byte-reproducible audible WAV output. R5 integrates that output into Studio Preview lifecycle.

### Interchange
Existing bounded DAWproject interchange/evaluation and exact-note reconciliation remain validated. Automation interchange remains unvalidated.

## Current architecture finding for R6

R5 deliberately preserved the historical R2 Browser automation contract. Current code therefore has a truthfulness mismatch:

```text
actual Studio capability:
  R5 audible audition is validated
  pending.detail.studio_audition carries proof

historical Browser view v0:
  capabilities.audible_automation_validated = false
  no formal mapped/unmapped lane audition state
  no render-plan/media hash inspection
  no accepted artifact lineage inspection
```

The correct next mission is to expose the already validated capability truthfully and versionedly, not to broaden renderer mapping.

## Next phase / 다음 단계

> **M7-R6 — Truthful Audible Automation Capability & Browser Lifecycle Inspection**

Required direction:

```text
R5 studio_audition proof
→ new versioned audition/capability contract
→ renderer policy identity
→ mapped + unmapped lane IDs
→ automation-applied / output-different status
→ render-plan + Preview media hashes
→ visible PREVIEW · NOT ACCEPTED lifecycle
→ accepted artifact identity after Accept/reopen
```

Do not reinterpret `studio-automation-view-v0` in place. Prefer a new versioned contract or separate audition-inspection object so R2 evidence remains historically truthful.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate:

- a new versioned Browser contract that truthfully exposes R5 audible capability;
- Browser inspection of accepted automation-artifact lineage;
- arbitrary canonical parameter → renderer/MIDI/plugin mapping;
- plug-in/device mapping or VST/AU/CLAP hosting;
- external DAW automation reconciliation;
- arbitrary tempo maps or spline/bezier curves;
- lane creation/deletion or parameter reassignment;
- real-time MIDI/OSC automation;
- live OpenAI provider execution;
- human-subject usability/preference or perceptual superiority;
- waveform/destructive audio editing, cloud collaboration or desktop signing.

## Resume authority / 재개 권위

Before R6 substantive work inspect:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M7_AUTOMATION_AUTHORITY.md`
4. `evidence/M7_R5_VALIDATION.md`
5. `schemas/studio-automation-view-v0.schema.json`
6. `src/musica/studio_automation.py`
7. `src/musica/studio.py`
8. Browser Studio JS/HTTP automation surfaces
9. `memory/CURRENT_STATE.md`
10. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**