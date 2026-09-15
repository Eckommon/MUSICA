# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M7-R4 — REFERENCE RENDERER AUTOMATION MAPPING & AUDIBLE EVIDENCE: VALIDATED — BOUNDED AUDIBLE EXECUTION**

M0→M7-R4 are validated only within their durable repository claims. Accepted Music Blueprint remains canonical creative authority. Browser, Music IR, automation execution, renderer/plugin and external DAW state remain derived or non-authoritative.

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
| M7-R5 Studio Automation Audition & Accepted Artifact Persistence | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |

## M7-R4 final evidence / M7-R4 최종 근거

- Issue `#80` — **COMPLETED**
- PR `#81` — **MERGED**
- implementation merge/main: `6f862dea15eea394f3e29ad7c91ef3e8b2cd767a`
- pre-durable exact head: `0166eb193f3df1269f3f8260753faed99de97e2d`
- final evidence-bearing successor head: `cae504d4582eb234b6bcb121fa4b96370c08069f`
- successor regression set: **12/12 SUCCESS**
- M7-R4 workflow `35002276837` — **SUCCESS**
- MUSICA CI `35002276941` — **SUCCESS**
- artifact ID `10410595918`
- packaging SHA-256 `ab47508dbdd8e7f8b14ada2dad792d0b5ea07339fe09cc744e23a6f05efcf585`
- internal manifest SHA-256 `532b225c9a40db44565fd617d5b5481049efcd9b337c022e6ab0b9af2a8110a4`
- render-plan SHA-256 `3821d05b18b55b81836bfcd271134bac3245fd3324bacb401647329d43049296`
- baseline WAV `efb3dfecd8b72545563a24617eaafaeea8ea22738103fa7703cb7efcfa0429c3`
- automated WAV `3137a946772c80286e9ba57df3081e3574be6cd4489d036359857ab75a2248a0`
- PCM differences: **146,461 samples**
- RMS ratios: linear `0.707450205`, hold `0.820013328`, after-last `0.750111392`
- pre-durable vs successor artifact: **14 files / 0 differences**

## M7-R4 validated authority invariant

```text
accepted automation
→ R3 automation-execution-v0
→ exact Music IR/execution hash binding
→ automation-render-plan-v0
→ only mix.gain/project/normalized maps
→ deterministic hold/linear reference-WAV gain
→ objective audible evidence
```

Validated R4 properties:

- `automation-render-plan-v0` is derived/non-canonical;
- only `mix.gain/project/normalized` maps in the current reference renderer;
- unsupported parameter domains remain typed unmapped;
- canonical `mix.gain` is not MIDI CC11;
- renderer/audio output cannot mutate or reverse-promote canonical state;
- automation-aware A/B render is byte-identical;
- automated output differs measurably from baseline;
- source Blueprint, Music IR and R3 execution remain unchanged;
- existing MIDI and baseline reference render paths remain regression-stable.

## Current capability stack / 현재 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material and accepted explicit automation material.

### Precision editing
M6 exact-note editing and M7-R1/R2 automation point editing use source-bound Preview/Accept authority patterns.

### Studio
Browser Studio Direct → Shape → Inspect → Code, exact-note piano roll and bounded automation Inspect/edit surface are validated. Studio audio Preview, however, still uses the legacy render cache path and is not yet integrated with R4 audible automation.

### Derived execution
R3 deterministically lowers accepted canonical automation to `automation-execution-v0` without guessing backend addresses.

### Renderer
R4 can map exactly one canonical automation family — `mix.gain/project/normalized` — through an explicit reference-renderer plan to byte-reproducible audible WAV output.

### Interchange
Existing bounded DAWproject interchange/evaluation and exact-note reconciliation remain validated. Automation interchange remains unvalidated.

## Current architecture finding for R5

`StudioService._render_to_cache()` currently executes:

```text
compile_blueprint
→ render_midi
→ render_wav
```

`StudioAutomationSurface.preview_automation_edit()` installs its validated candidate through `StudioService._install_preview()`, which calls this same cache renderer. Thus a Browser automation Preview can be valid and accepted while its Studio Preview WAV still ignores R4 audible automation.

The correct next mission is therefore **product integration**, not mapping expansion.

## Next phase / 다음 단계

> **M7-R5 — Studio Automation Audition & Accepted Artifact Persistence**

Required path:

```text
validated Studio candidate Blueprint
→ compile Music IR
→ R3 automation execution
→ R4 render plan / bounded mix.gain mapping
→ automation-aware Studio Preview WAV
→ explicit Accept or Discard

Accept → exact Preview WAV bound to accepted revision artifact
Discard → pending Preview/media removed, accepted state unchanged
Reopen → accepted revision artifact served unchanged
```

R5 must keep MIDI bytes stable, keep unsupported lanes unmapped, preserve Preview-not-authority semantics and prove artifact persistence across reopen.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate:

- Studio Preview/Accept/reopen integration of audible automation;
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

Before R5 substantive work inspect:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M7_AUTOMATION_AUTHORITY.md`
4. `evidence/M7_R4_VALIDATION.md`
5. `src/musica/automation_renderer.py`
6. `src/musica/automation_lowering.py`
7. `src/musica/studio.py`
8. `src/musica/studio_automation.py`
9. `memory/CURRENT_STATE.md`
10. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**