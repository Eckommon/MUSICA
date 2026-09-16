# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation**. The accepted Music Blueprint/project revision is creative authority. Music IR, Browser state, derived execution, renderer/plugin runtime state, audio artifacts, comparison projections and interchange/DAW state remain derived or non-canonical unless an explicit authority contract says otherwise.

## Long-term product direction / 장기 제품 방향

MUSICA's long-term scope includes becoming a **general-purpose, commercially usable music production workstation** while preserving its AI-native authority model.

This does not mean cloning every feature of every DAW. It means ordinary end-to-end production should eventually have first-class native workflows for arrangement, audio tracks/clips, mixing and signal flow, recording, supported instruments/effects/plugins, automation, interoperability, persistence/recovery and reliable commercial distribution.

The governing capability map is `docs/COMMERCIAL_WORKSTATION_TARGET.md`.

Foundation-stage statements that MUSICA did not need to replace every professional DAW or provide universal plugin hosting remain valid as **foundation acceptance boundaries**, not permanent product ceilings.

## Current canonical status / 현재 공식 상태

**M0 → M7-R6 and the post-M7 Accepted Revision A/B Compare & Human Decision Surface v0 are validated within their explicitly bounded repository claims.**

```text
M0      controllable core                                  VALIDATED
M1      creative core                                      VALIDATED
M2      project & version engine                           VALIDATED
M3      AI Music Director provider layer                   VALIDATED — BOUNDED
M4      Browser Studio / usable MVP                        VALIDATED
M5      rendering / interchange / evaluation               VALIDATED — BOUNDED
M6      precision editing R0→R4                            VALIDATED — BOUNDED
M7-R0   automation authority/data model                    VALIDATED — CONTRACT/DESIGN ONLY
M7-R1   canonical automation runtime                       VALIDATED — BOUNDED CORE RUNTIME
M7-R2   Browser automation inspect/edit                    VALIDATED — BOUNDED REAL-BROWSER SURFACE
M7-R3   deterministic derived automation execution         VALIDATED — BOUNDED DERIVED EXECUTION
M7-R4   reference-renderer audible mix.gain mapping        VALIDATED — BOUNDED AUDIBLE EXECUTION
M7-R5   Studio audible Preview / Accept / reopen            VALIDATED — BOUNDED STUDIO AUDITION
M7-R6   truthful audible automation inspection              VALIDATED — BOUNDED TRUTHFUL INSPECTION
Post-M7 accepted revision A/B Compare + human choice        VALIDATED — BOUNDED READ-ONLY DECISION SURFACE
```

No artificial `M8` identifier is inferred from the next product expansion.

## Canonical product loop / 공식 제품 루프

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

The repository contains bounded validated evidence for every stage of that loop:

- natural-language intent → typed Blueprint generation;
- deterministic compilation/rendering and Browser audition;
- locks/constraints and source-bound edit authority;
- semantic, exact-note and automation refinement through Preview → explicit Accept;
- immutable revision/history/branch/project persistence;
- accepted-revision A/B comparison with exact structured diff and media provenance;
- Browser-local human A/B decision state with no hidden canonical mutation;
- explicit Accept as the canonical acceptance transition.

This closes the core interaction-loop gap. It does **not** mean MUSICA is already a finished commercial DAW.

## Latest validated capability — Accepted Revision A/B Compare

Issue `#89` / PR `#91` validated:

```text
accepted revision A + accepted revision B
→ immutable revision/Blueprint verification
→ deterministic structured_diff(A, B)
→ exact bound/fallback WAV + MIDI provenance
→ read-only localhost comparison/media routes
→ independent Browser A/B audition
→ Browser-local Choose A / Choose B
→ no canonical mutation
```

Durable evidence: `evidence/POST_M7_REVISION_COMPARE_VALIDATION.md`.

Final state:

- Issue `#89` — **COMPLETED**
- implementation PR `#91` — **MERGED**
- implementation/validation main: `7314deb5aba93073f1f7750dc68f9f4d31cd3c06`
- state closure PR `#94` — **MERGED**
- state closure main: `f6128a8b5dcaae5f4cb4e05ad21da415b34afaa5`
- pre-durable exact head: `b22e41f690606aeedcffa11ef2ec5e915b34551d` — **15/15 SUCCESS**
- durable-record exact head: `de309c7f030d6c3f8085da312bc7c7bfaa94e19d` — **15/15 SUCCESS**

## Selected commercial-workstation successor / 선정된 상용 워크스테이션 후속 미션

The post-Compare successor review selected:

> **Issue #95 — Audio Track / Clip / Mixer Foundation v0 — RATIFIED TARGET, NOT YET VALIDATED**

Selection record: `docs/POST_COMPARE_SUCCESSOR_SELECTION.md`.

Why this comes before plugin hosting or recording:

- the repository has no native immutable audio-asset domain;
- no native audio clip model;
- no native audio track model;
- no internal multitrack mixer state;
- no deterministic project mixdown derived from accepted audio arrangement state.

Those are prerequisite primitives for recording, routing/buses, plugin hosting, latency compensation, waveform editing and deeper professional mixing.

### Issue #95 target path

```text
supported WAV/PCM bytes
→ immutable content-addressed audio asset
→ accepted audio track + clip state
→ source-bound Preview edit
→ explicit Accept
→ accepted mixer state
→ deterministic offline mix plan
→ deterministic stereo mixdown
→ Browser arrangement/mixer inspection + audition
```

Minimum target controls include stable tracks/clips, clip placement/source range/gain and track gain/pan/mute/solo.

Issue #95 explicitly does **not** yet claim microphone recording, low-latency device I/O, plugin hosting, latency compensation, arbitrary buses/sends, warp/time-stretch, destructive editing, comping or commercial release readiness.

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
Accepted project / Music Blueprint revision
        ↓ trusted deterministic lowering/execution
Music IR / automation / future native audio mix plan
        ↓
Renderer / Studio media artifacts
        ↓ read-only or bounded UI projection
Browser Studio
```

No renderer, Browser, decoded audio buffer, waveform cache, meter, Music IR, derived execution package, audio artifact, comparison result, local A/B choice, plugin runtime or external DAW state may silently promote itself into accepted project authority.

## Exact next bounded action / 정확한 다음 작업

> **After this planning decision is merged, implement Issue #95 contract-first: choose the least invasive accepted audio-material authority shape → define audio asset/material/edit/mix contracts → immutable project asset store → source-bound Preview/Accept audio editing → deterministic offline mixer → Studio/Browser arrangement+mixer → restart/reopen evidence → permanent CI → durable validation → expected-head implementation merge → separate state-only closure.**

See `memory/NEXT_ACTION.md` for the exact execution order.

## Important current non-claims / 주요 현재 비주장

MUSICA does not yet validate:

- native accepted audio track/clip/multitrack mixer workflow;
- microphone/line recording or low-latency real-time device engine;
- VST3/AU/CLAP hosting;
- generalized routing/buses/sends or latency compensation;
- arbitrary parameter → renderer/MIDI/plugin mapping;
- external DAW automation/native-audio reconciliation;
- live OpenAI provider execution;
- time-stretch/warp or destructive waveform editing;
- human preference/perceptual-superiority claims;
- cloud collaboration or multi-user authority;
- installer/signing/commercial release qualification or production SLA claims.

## Repository as source of truth / Repo 공식 근거

```text
accepted repository tests/artifacts/evidence
> merged specifications/current-state records
> Issue/PR/exact-head CI evidence
> conversation context
> model memory/inference
```

Resume from `memory/CURRENT_STATE.md` and `memory/NEXT_ACTION.md`.

**Repository evidence remains authoritative over conversation/model memory.**
