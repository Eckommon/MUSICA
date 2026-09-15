# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation**. The accepted Music Blueprint/project revision is creative authority. Music IR, Browser state, derived automation execution, renderer/plugin state, audio artifacts and interchange/DAW state are derived or non-canonical.

## Current canonical status / 현재 공식 상태

**M0 → M7-R4 are validated within their explicitly bounded repository claims.**

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
M7-R4  reference-renderer audible mix.gain mapping        VALIDATED — BOUNDED AUDIBLE EXECUTION
```

## M7-R4 validated boundary

```text
accepted Blueprint materials.automation
→ M7-R3 automation-execution-v0
→ exact Music IR + execution hash binding
→ automation-render-plan-v0
→ explicit mix.gain / project / normalized mapping
→ post-normalization deterministic gain envelope
→ reference WAV + objective audio evidence
```

Validated properties include:

- exactly one renderer mapping family is supported: `mix.gain / project / normalized`;
- `synth.cutoff` and every other unsupported lane remain typed unmapped;
- canonical `mix.gain` is **not** equated with semantic MIDI CC11;
- renderer plan is `derived_noncanonical` and cannot mutate Project/Blueprint authority or reverse-promote itself;
- `hold` and `linear` envelopes are deterministic;
- existing `compile_blueprint()`, MIDI behavior, `wav_bytes()` and `render_wav()` remain regression-stable;
- automation-aware output starts from the existing deterministic reference WAV and applies gain after existing safety normalization;
- repeated automated WAV output is byte-identical;
- objective RMS/peak/window evidence follows the mapped gain envelope;
- legacy/no-automation remains baseline-byte-equivalent;
- no perceptual-quality or mastering claim is made.

Durable evidence: `evidence/M7_R4_VALIDATION.md`.

## M7-R4 final evidence / 최종 근거

- Issue `#80` — **COMPLETED**
- PR `#81` — **MERGED**
- implementation merge/main: `6f862dea15eea394f3e29ad7c91ef3e8b2cd767a`
- pre-durable exact head: `0166eb193f3df1269f3f8260753faed99de97e2d`
- final evidence-bearing successor head: `cae504d4582eb234b6bcb121fa4b96370c08069f`
- successor regression set: **12/12 SUCCESS**
- successor M7-R4 workflow: `35002276837` — **SUCCESS**
- successor MUSICA CI: `35002276941` — **SUCCESS**
- successor artifact ID: `10410595918`
- successor packaging SHA-256: `ab47508dbdd8e7f8b14ada2dad792d0b5ea07339fe09cc744e23a6f05efcf585`
- internal manifest SHA-256: `532b225c9a40db44565fd617d5b5481049efcd9b337c022e6ab0b9af2a8110a4`
- render-plan SHA-256: `3821d05b18b55b81836bfcd271134bac3245fd3324bacb401647329d43049296`
- baseline WAV SHA-256: `efb3dfecd8b72545563a24617eaafaeea8ea22738103fa7703cb7efcfa0429c3`
- automated WAV SHA-256: `3137a946772c80286e9ba57df3081e3574be6cd4489d036359857ab75a2248a0`
- baseline-different PCM samples: **146,461**
- RMS ratios: linear `0.707450205`, hold `0.820013328`, after-last `0.750111392`
- pre-durable vs successor extracted artifact: **14 files / 0 differences**

## Exact next bounded milestone / 정확한 다음 마일스톤

> **M7-R5 — Studio Automation Audition & Accepted Artifact Persistence**

Repository inspection after R4 found a product-level gap: `StudioService._render_to_cache()` still renders every Preview and accepted-cache fallback through the legacy `compile_blueprint → render_midi/render_wav` path. Therefore Browser automation editing can create and accept canonical automation, but the Studio audio Preview does not yet consume the validated R3→R4 audible automation path.

R5 closes that gap without expanding the parameter registry:

```text
Browser automation edit
→ validated Preview candidate
→ Music IR + R3 automation execution
→ R4 automation render plan
→ automation-aware Studio Preview WAV
→ explicit Accept or Discard

Accept → bind the exact audible Preview WAV as the accepted revision artifact
Discard → remove Preview media without changing canonical state
Reopen → serve the accepted artifact for the accepted revision
```

R5 must keep MIDI unchanged, keep unsupported automation lanes unmapped, preserve explicit Accept authority, and prove Preview/Discard/Accept/reopen lifecycle behavior. It does **not** add another automation parameter family.

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
Renderer / Studio media artifacts
```

No renderer, Browser, Music IR, derived execution package, audio artifact or DAW/plugin state may promote itself back into canonical Blueprint authority.

## Current non-claims / 현재 비주장

MUSICA does not yet validate:

- Studio Preview/Accept/reopen lifecycle use of audible canonical automation;
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

Before substantive M7-R5 work read `governance/SOURCE_OF_TRUTH.md`, `docs/PRODUCT_THESIS.md`, `docs/M7_AUTOMATION_AUTHORITY.md`, `evidence/M7_R4_VALIDATION.md`, `src/musica/automation_renderer.py`, `src/musica/automation_lowering.py`, `src/musica/studio.py`, `src/musica/studio_automation.py`, `memory/CURRENT_STATE.md`, and `memory/NEXT_ACTION.md`.

**Repository evidence remains authoritative over conversation/model memory.**