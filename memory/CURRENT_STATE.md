# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → COMMERCIAL WORKSTATION EXPANSION SELECTED**

M0→M7-R6 and the post-M7 Accepted Revision A/B Compare & Human Decision Surface v0 remain validated only within their durable repository claims.

The post-Compare successor review now adds an explicit long-term product direction:

> **MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving its AI-native authority, inspectability, reproducibility and programmability.**

This is a governing product target, not a claim that MUSICA is already a finished commercial DAW.

## Canonical baseline / 공식 기준점

- canonical main before this planning decision: `f6128a8b5dcaae5f4cb4e05ad21da415b34afaa5`
- Compare Issue `#89` — **COMPLETED**
- Compare implementation PR `#91` — **MERGED**
- Compare state closure PR `#94` — **MERGED**
- Compare state closure main: `f6128a8b5dcaae5f4cb4e05ad21da415b34afaa5`
- latest validated capability: **Accepted Revision A/B Compare & Human Decision Surface v0 — VALIDATED — BOUNDED READ-ONLY DECISION SURFACE**
- new selected implementation Issue: `#95` — **Audio Track / Clip / Mixer Foundation v0**
- Issue `#95` status: **OPEN / TARGET ONLY — NOT IMPLEMENTED OR VALIDATED**

No artificial `M8` or other numeric milestone is assigned by this selection.

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**

The commercial-workstation objective extends this proposition; it does not replace it.

## Canonical milestone ledger / 공식 마일스톤 원장

| Milestone / capability | Status | Durable evidence |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4 Browser Studio / Usable MVP | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` → `evidence/M4_R3_VALIDATION.md` |
| M5 Rendering / Interchange / Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R1_VALIDATION.md` → `evidence/M5_R4_VALIDATION.md` |
| M6 Precision Editing R0→R4 | **VALIDATED — BOUNDED** | `evidence/M6_R0_VALIDATION.md` → `evidence/M6_R4_VALIDATION.md` |
| M7-R0→R6 Automation authority/runtime/Browser/lowering/audition/inspection | **VALIDATED — BOUNDED BY EACH RECORD** | `evidence/M7_R0_VALIDATION.md` → `evidence/M7_R6_VALIDATION.md` |
| Post-M7 Accepted Revision A/B Compare & Human Decision Surface v0 | **VALIDATED — BOUNDED READ-ONLY DECISION SURFACE** | `evidence/POST_M7_REVISION_COMPARE_VALIDATION.md` |
| Audio Track / Clip / Mixer Foundation v0 | **RATIFIED TARGET — NOT YET VALIDATED** | Issue `#95`, `docs/POST_COMPARE_SUCCESSOR_SELECTION.md` |

## Product-loop coverage / 제품 루프 커버리지

The thesis loop is boundedly validated:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

Validated coverage includes typed intent/Blueprint generation, deterministic audition, locks/constraints, semantic/exact-note/automation Preview edits, explicit Accept, immutable project revisions, restart/reopen, and accepted-revision A/B Compare with Browser-local human choice.

This proves the core interaction thesis. It does **not** prove general-purpose DAW completeness.

## Long-term commercial workstation target / 장기 상용 워크스테이션 목표

The long-term capability map is governed by `docs/COMMERCIAL_WORKSTATION_TARGET.md`.

The target includes credible eventual coverage for:

- native arrangement and track/clip workflows;
- audio assets and recording;
- mixer/signal flow and automation;
- supported instruments/effects and third-party plugin hosting;
- real-time audio/device operation and latency handling;
- non-destructive audio editing depth;
- composition/programming/AI direction;
- interoperability;
- persistence, migration, recovery, performance and commercial distribution;
- later collaboration as a separate distributed-authority domain.

Foundation-stage statements that MUSICA did not need to be a full DAW replacement or universal plugin host remain historically valid. They were acceptance boundaries for v0.1, not permanent product ceilings.

## Post-Compare successor review / Compare 이후 후속 선정

Serious candidate families were compared:

- Audio Track / Clip / Mixer Foundation;
- automation renderer mapping expansion;
- `LIVE_PROVIDER_EVIDENCE`;
- automation-aware DAW reconciliation;
- plugin hosting;
- real-time device/recording engine;
- release hardening;
- human usability/perceptual evaluation.

The selected successor is:

> **Issue #95 — Audio Track / Clip / Mixer Foundation v0**

Selection record: `docs/POST_COMPARE_SUCCESSOR_SELECTION.md`.

### Why selected

The repository has strong intent, note, automation, rendering, versioning, Browser and interchange foundations but no native internal domain for:

- immutable imported audio assets;
- audio clips;
- audio tracks;
- multitrack mixer state;
- deterministic project mixdown from accepted audio arrangement state.

Those are prerequisite primitives for later recording, plugin hosting, routing/buses, latency compensation, waveform editing and deeper professional mixing.

## Issue #95 target authority / Issue #95 목표 권한

Accepted project state may eventually reference typed native audio material:

```text
immutable content-addressed audio asset
        ↓
accepted audio track + clip state
        ↓
track/clip mixer parameters
        ↓
trusted deterministic mix plan
        ↓
derived stereo render / Browser audition
```

Target accepted state includes only explicit typed references and parameters. Decoded buffers, waveform caches, meters, renderer output and Browser state remain derived/non-canonical.

Minimum Issue #95 target:

- bounded WAV/PCM asset import with exact SHA-256 provenance;
- stable audio track IDs;
- stable audio clip IDs referencing exact asset identity;
- clip placement/source in-out/non-destructive gain;
- track gain/pan/mute/solo;
- source-bound Preview edits;
- explicit Accept only;
- deterministic offline multitrack mixdown;
- Browser arrangement/mixer surface;
- persistence/reopen evidence;
- real-Chromium evidence;
- fail-closed corrupt/missing media behavior.

## Explicit Issue #95 non-goals / Issue #95 비목표

The first audio foundation does not claim:

- microphone/line recording;
- ASIO/CoreAudio/WASAPI device engine;
- low-latency real-time guarantees;
- latency compensation;
- VST3/AU/CLAP hosting;
- arbitrary buses/sends/sidechains;
- time-stretch/warp/pitch shift;
- destructive waveform editing;
- comping/take lanes;
- mastering-grade DSP;
- cloud collaboration;
- commercial-release readiness.

These remain later workstation domains.

## Current validated capability stack / 현재 검증 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material, explicit automation material, revision-bound artifacts and explicit Accept authority.

### Browser Studio
Natural-language create/edit, Direct/Shape/Inspect/Code, piano-roll precision editing, automation editing/audition/inspection and accepted-revision A/B Compare.

### Renderer / automation
Deterministic reference rendering exists. Exactly one automation renderer mapping family is validated: `mix.gain / project / normalized`.

### Interchange
Bounded DAWproject interchange/evaluation and exact-note reconciliation are validated. DAW automation and native-audio round-trip are not.

### AI provider
Provider-neutral and OpenAI adapter/offline integration boundaries are validated; actual live OpenAI execution remains unvalidated `LIVE_PROVIDER_EVIDENCE`.

## Remaining important non-claims / 주요 비주장

Until separately validated, do not claim:

- native accepted audio track/clip/multitrack mixer workflow;
- recording or real-time low-latency audio engine;
- third-party plugin hosting;
- generalized mixer routing/buses/sends;
- generalized automation parameter mapping;
- external DAW automation/native-audio reconciliation;
- live OpenAI execution;
- waveform/warp/destructive editing;
- commercial release readiness, installer/signing or supported production SLA;
- cloud/multi-user authority;
- human preference/perceptual superiority.

## Exact next phase / 다음 단계

> **Issue #95 implementation must proceed contract-first from a ratified planning merge: inspect current Blueprint/project/render/DAWproject/Studio contracts → decide additive audio-material authority shape → define asset/material/edit/mix schemas → implement immutable asset store → trusted audio edit authority → deterministic offline mixer → Studio/Browser arrangement + mixer → persistence/evidence → permanent CI → durable validation → expected-head merge → state-only closure.**

See `memory/NEXT_ACTION.md` for exact execution order.

## Resume authority / 재개 권위

Before Issue `#95` implementation, inspect at minimum:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/COMMERCIAL_WORKSTATION_TARGET.md`
4. `docs/POST_COMPARE_SUCCESSOR_SELECTION.md`
5. Issue `#95`
6. `schemas/music-blueprint-v0.schema.json`
7. `src/musica/project.py`
8. `src/musica/render.py`
9. `src/musica/renderer.py`
10. `src/musica/dawproject.py`
11. `src/musica/studio.py`
12. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**
