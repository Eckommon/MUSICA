# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation**. The accepted Music Blueprint/project revision is creative authority. Music IR, Browser state, derived automation execution, renderer/plugin state, audio artifacts and interchange/DAW state are derived or non-canonical.

## Current canonical status / 현재 공식 상태

**M0 → M7-R6 are validated within their explicitly bounded repository claims.**

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
M7-R5  Studio audible Preview / Accept / reopen lifecycle VALIDATED — BOUNDED STUDIO AUDITION & ARTIFACT PERSISTENCE
M7-R6  truthful audible automation lifecycle inspection   VALIDATED — BOUNDED TRUTHFUL AUDITION INSPECTION
```

## M7-R6 validated boundary

R6 closes the truthfulness gap between the already validated R5 audible audition and the historical R2 Browser automation view **without rewriting the historical R2 contract**.

```text
historical studio-automation-view-v0           # unchanged; audible_automation_validated=false
+ trusted R5 pending.detail.studio_audition
+ exact accepted/fallback media identity
        ↓
studio-automation-audition-v0                  # read-only, versioned
        ↓
localhost inspection endpoint
        ↓
non-authoritative Browser inspector
```

Validated properties include:

- the only audible renderer mapping remains `mix.gain / project / normalized` under `musica-reference-local`;
- `synth.cutoff` remains explicitly unmapped;
- Browser inspection distinguishes accepted media, pending `PREVIEW · NOT ACCEPTED`, mapped lanes and unmapped lanes;
- Browser-computed WAV/MIDI SHA-256 values match trusted pending inspection hashes;
- Discard removes pending audition state without changing accepted identity;
- explicit Accept advances exactly one revision and binds the exact Preview WAV/MIDI;
- restart/reopen preserves the exact accepted artifact identity and bytes;
- unsupported-only automation reports `automation_applied=false` and does not invent audible mapping;
- Browser/audio/renderer inspection remains non-canonical and cannot reverse-promote into Blueprint authority;
- historical `studio-automation-view-v0` remains truthful and unchanged.

Durable evidence: `evidence/M7_R6_VALIDATION.md`.

## M7-R6 final evidence / 최종 근거

- Issue `#86` — **COMPLETED**
- PR `#87` — **MERGED**
- implementation + validation merge/main: `1de099e8d3e489c818ae561ddfb0c43c4ffdcbfc`
- pre-durable head: `af11315c777f761179ca3d94bfed1a6e472dd315`
- successor evidence head: `93129768ff4b33c663eeeccda22c1d07faea0872`
- final validation-record head: `0ea3fd976a8b63293d434bb427f7dfeffb68fcfd`
- pre-durable / successor / final-record permanent gates: **14/14 SUCCESS** each
- pre-durable deterministic manifest SHA-256: `926c0608c5998ceaa1ac0f49c19dbf4f293acc180d0e2433d067b369d32b953a`
- deterministic pre-durable vs successor evidence: **14 files / 0 differences**
- accepted/reopened WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- accepted/reopened MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- Browser proof: console errors `0`, page errors `0`, unexpected request failures `0`; exactly `2` narrowly classified superseded-audio `ERR_ABORTED` events

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
        ↓ read-only inspection only
Browser audition inspector
```

No renderer, Browser, Music IR, derived execution package, audio artifact or DAW/plugin state may promote itself back into canonical Blueprint authority.

## Exact next bounded action / 정확한 다음 작업

The repository does **not** currently ratify an `M7-R7` or `M8` milestone. The next action is therefore not feature implementation by inertia.

> **Post-M7 closure review → evidence-based next-milestone selection**

The review must inspect the validated M0→M7 stack, product thesis, remaining non-claims, dependency readiness and user-value leverage, then ratify exactly one bounded next milestone before implementation begins. See `memory/NEXT_ACTION.md`.

## Current non-claims / 현재 비주장

MUSICA does not yet validate, unless a future milestone explicitly does so:

- a second canonical automation renderer mapping family;
- arbitrary parameter → renderer/MIDI/plugin mapping;
- plug-in/mixer/device mapping or VST/AU/CLAP hosting;
- DAW automation import/export/reconciliation;
- real-time MIDI/OSC automation;
- arbitrary tempo-map automation;
- lane creation/deletion or parameter reassignment;
- spline/bezier/exponential interpolation;
- live OpenAI provider execution;
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

Before substantive next-milestone work read `governance/SOURCE_OF_TRUTH.md`, `docs/PRODUCT_THESIS.md`, `docs/M7_AUTOMATION_AUTHORITY.md`, `evidence/M7_R6_VALIDATION.md`, `memory/CURRENT_STATE.md`, and `memory/NEXT_ACTION.md`.

**Repository evidence remains authoritative over conversation/model memory.**