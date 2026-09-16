# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation**. The accepted Music Blueprint/project revision is creative authority. Music IR, Browser state, derived automation execution, renderer/plugin state, audio artifacts and interchange/DAW state are derived or non-canonical.

## Current canonical status / 현재 공식 상태

**M0 → M7-R5 are validated within their explicitly bounded repository claims.**

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
```

## M7-R5 validated boundary

```text
accepted Blueprint automation
→ source-bound automation edit candidate
→ trusted Preview authority
→ candidate Music IR
→ M7-R3 automation-execution-v0
→ M7-R4 automation-render-plan-v0
→ bounded reference-renderer mix.gain WAV
→ Studio PREVIEW · NOT ACCEPTED
→ Discard OR explicit Accept
→ existing M2 immutable revision + bound WAV/MIDI artifacts
→ reopen serves accepted artifact bytes unchanged
```

Validated properties include:

- only `mix.gain / project / normalized` is audibly mapped by the current reference renderer;
- `synth.cutoff` and unsupported lanes remain typed unmapped;
- Studio Preview audio now consumes the validated R3→R4 audible path;
- Preview remains non-canonical and cannot advance the accepted project ref;
- Discard removes pending audition media and preserves accepted state/artifacts;
- explicit Accept advances exactly one revision and binds the exact Preview WAV/MIDI;
- reopening serves byte-identical accepted WAV/MIDI artifacts;
- accepted audio cannot reverse-promote itself into Blueprint automation authority;
- existing MIDI semantics remain unchanged;
- R4 performance optimization is byte-preserving;
- no arbitrary MIDI CC/plugin/DAW mapping or perceptual-quality claim is made.

Durable evidence: `evidence/M7_R5_VALIDATION.md`.

## M7-R5 final evidence / 최종 근거

- Issue `#84` — **COMPLETED**
- PR `#83` — **MERGED**
- implementation merge/main: `43488fe85bb6c2fde19dc27d0dabfdb7587d7f1f`
- pre-durable head: `298a46a4de360d697c2fe55006cd17966c3bf1e8`
- successor evidence head: `87dd85cb2ff2f0a576db24c6b87c7ad16a32bb29`
- final validation-record head: `41f98e882e62cf638370c998447e754398c63284`
- pre-durable regression set: **13/13 SUCCESS**
- successor regression set: **13/13 SUCCESS**
- final record-head regression set: **13/13 SUCCESS**
- final record-head M7-R5 workflow: `35039890451` — **SUCCESS**
- final record-head MUSICA CI: `35039890429` — **SUCCESS**
- pre-durable artifact: `10411768231`
- successor artifact: `10412286568`
- R5 internal manifest SHA-256: `ab5c99c4ab474eccac17b727cf0a502061f2691ffae5bbfab734572a90e5c772`
- pre-durable vs successor R5 evidence: **16 files / 0 differences**
- Preview = accepted = reopened WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- Preview = accepted = reopened MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- R4 byte-preservation recheck: **14 files / 0 differences**

## Exact next bounded milestone / 정확한 다음 마일스톤

> **M7-R6 — Truthful Audible Automation Capability & Browser Lifecycle Inspection**

R5 deliberately preserved the historical R2 `studio-automation-view-v0` contract. Consequently the product now has a truthfulness gap:

- the R5 Studio Preview is audibly automation-aware;
- `pending.detail.studio_audition` contains mapped/unmapped lanes and render evidence;
- but the R2 Browser automation view still declares `audible_automation_validated=false`;
- the Browser surface does not formally expose which lane is audibly mapped, which is unmapped, whether automation changed the Preview WAV, or the accepted artifact lineage after Accept/reopen.

R6 closes that gap **without rewriting the historical R2 contract and without adding a second renderer mapping family**.

Preferred direction:

```text
R5 validated studio_audition proof
→ new bounded Browser/inspection contract
→ explicit renderer policy identity
→ mapped lane IDs + unmapped lane IDs
→ automation-applied / baseline-different state
→ render-plan / Preview media hashes
→ PREVIEW · NOT ACCEPTED lifecycle visibility
→ accepted artifact identity after Accept/reopen
```

R6 should introduce a new versioned audition/capability contract rather than silently changing the meaning of `studio-automation-view-v0`.

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

- a versioned Browser capability contract that truthfully exposes R5 audible mapping/audition evidence;
- accepted automation-artifact lineage inspection in the Browser UI;
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

Before substantive M7-R6 work read `governance/SOURCE_OF_TRUTH.md`, `docs/PRODUCT_THESIS.md`, `docs/M7_AUTOMATION_AUTHORITY.md`, `evidence/M7_R5_VALIDATION.md`, `schemas/studio-automation-view-v0.schema.json`, `src/musica/studio_automation.py`, `src/musica/studio.py`, `memory/CURRENT_STATE.md`, and `memory/NEXT_ACTION.md`.

**Repository evidence remains authoritative over conversation/model memory.**