# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → COMMERCIAL WORKSTATION EXPANSION IN PROGRESS**

M0→M7-R6 and the post-M7 Accepted Revision A/B Compare & Human Decision Surface v0 remain validated only within their durable repository claims.

The long-term product direction remains:

> **MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving its AI-native authority, inspectability, reproducibility and programmability.**

This is a governing product target, not a claim that MUSICA is already a finished commercial DAW.

## Canonical baseline / 공식 기준점

- pre-audio planning main: `b26cacf92279aef8527c3372ceb89316e47dc7d8`
- parent Issue `#95` — **Audio Track / Clip / Mixer Foundation v0 — OPEN**
- ATCM-R0 Issue `#97` — **COMPLETED**
- ATCM-R0 implementation PR `#98` — **MERGED**
- ATCM-R0 implementation merge/main: `f3c5c5d9cc8289dcdb88a420dea8db29d14f74dc`
- ATCM-R0 durable record: `evidence/ATCM_R0_VALIDATION.md`
- ATCM-R0 validation-record exact head: `dfb8e9cce1d4044fc249d5dba80583eff678b12b` — **16/16 permanent workflows SUCCESS**
- next bounded implementation Issue `#99` — **ATCM-R1 — Accepted Audio Track / Clip Authority & Asset Binding v0 — OPEN**

No artificial `M8` or other numeric milestone is assigned.

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
| ATCM-R0 Native Audio Authority & Immutable Asset Store | **VALIDATED — BOUNDED** | `evidence/ATCM_R0_VALIDATION.md` |
| ATCM-R1 Accepted Audio Track / Clip Authority & Asset Binding v0 | **OPEN — NOT YET VALIDATED** | Issue `#99` |
| Audio Track / Clip / Mixer Foundation v0 parent mission | **IN PROGRESS** | Issue `#95` |

## Product-loop coverage / 제품 루프 커버리지

The thesis loop is boundedly validated:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

Validated coverage includes typed intent/Blueprint generation, deterministic audition, locks/constraints, semantic/exact-note/automation Preview edits, explicit Accept, immutable project revisions, restart/reopen, and accepted-revision A/B Compare with Browser-local human choice.

This proves the core interaction thesis. It does **not** prove general-purpose DAW completeness.

## ATCM-R0 validated capability / ATCM-R0 검증 기능

R0 establishes the first native source-audio persistence boundary:

```text
bounded PCM WAV bytes
→ validated immutable content-addressed object
→ SHA-256 audio asset identity
→ canonical descriptor + audit binding
→ deterministic project export/import
```

Validated R0 behavior includes:

- bounded RIFF/WAVE integer PCM import;
- mono/stereo source boundary;
- exact SHA-256 content identity and byte length;
- exact format metadata including channels/sample rate/sample width/frame count/duration;
- identical-byte idempotent import;
- project-confined paths independent of untrusted source filenames;
- descriptor/object/audit integrity verification;
- missing/tampered source or descriptor fail-closed behavior;
- project-level `verify_integrity()` coverage for audio assets;
- deterministic export/import/re-export preservation;
- machine-valid future native audio track/clip material shape;
- deliberate authority block preventing non-empty native audio material from becoming accepted creative state before R1 authority exists.

### R0 maximum validated claim

> **MUSICA can validate, import, content-address, persist, integrity-check, export and re-import a bounded PCM WAV source as an immutable project audio asset, and can machine-validate the typed native audio material structure that later accepted revisions will use, without treating imported bytes or non-authorized audio material as accepted creative state.**

R0 does **not** validate accepted audio track/clip edits, multitrack summing, Browser arrangement, recording or plugin hosting.

## ATCM-R1 selected next rung / ATCM-R1 다음 단계

Issue `#99` is the exact next implementation rung.

Its bounded authority path is:

```text
accepted source revision
+ immutable in-project R0 audio asset
→ project-bound source-bound audio edit candidate
→ validate exact asset / source range / stable IDs / material invariants
→ READY_FOR_PREVIEW or BLOCKED
→ Preview only; accepted HEAD unchanged
→ explicit Accept only
→ exactly one accepted revision advance
```

R1 is intentionally narrower than the full parent Issue #95.

### R1 intended trusted edits

- add audio track;
- add/reference imported clip;
- move clip;
- trim clip source in/out;
- set bounded clip gain.

### R1 mixer boundary

The existing audio material schema carries default track mixer fields for structural continuity, but R1 does **not** claim validated audible semantics for track gain/pan/mute/solo and should not expose them as trusted user edits.

Those semantics belong to the following deterministic mixer rung.

## Parent Issue #95 remaining path / 상위 미션 잔여 경로

Current evidence-driven rung order:

```text
ATCM-R0 immutable asset + authority contracts        VALIDATED
→ ATCM-R1 accepted track/clip Preview→Accept        NEXT / Issue #99
→ ATCM-R2 deterministic multitrack mixer semantics
→ ATCM-R3 Studio/Browser arrangement + mixer
→ ATCM-R4 restart/reopen + real-browser lifecycle
→ parent Issue #95 closure
```

The exact boundaries may narrow further if repository evidence requires it; they must not widen silently.

## Long-term commercial workstation target / 장기 상용 워크스테이션 목표

The target remains governed by `docs/COMMERCIAL_WORKSTATION_TARGET.md` and includes eventual credible coverage for:

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

Foundation-stage statements that MUSICA did not need to be a full DAW replacement or universal plugin host were acceptance boundaries for earlier stages, not permanent product ceilings.

## Current validated capability stack / 현재 검증 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material, explicit automation material, revision-bound artifacts and explicit Accept authority.

### Native source audio
Bounded immutable PCM WAV assets with exact identity, project-integrity coverage and deterministic bundle persistence are validated. Accepted track/clip use is not yet validated.

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

- accepted native audio track/clip edit authority;
- deterministic native multitrack mixer execution;
- Browser native-audio arrangement/mixer workflow;
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

> **Issue #99 — ATCM-R1: implement project-bound asset-reference validation and source-bound audio track/clip Preview→Accept authority while preserving R0's fail-closed direct-commit boundary until the trusted R1 path explicitly authorizes acceptance.**

See `memory/NEXT_ACTION.md` for the exact execution order.

## Resume authority / 재개 권위

Before ATCM-R1 implementation, inspect at minimum:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/COMMERCIAL_WORKSTATION_TARGET.md`
4. `docs/POST_COMPARE_SUCCESSOR_SELECTION.md`
5. Issue `#95`
6. Issue `#99`
7. `evidence/ATCM_R0_VALIDATION.md`
8. `schemas/audio-asset-v0.schema.json`
9. `schemas/audio-material-v0.schema.json`
10. `src/musica/audio_assets.py`
11. `src/musica/audio_contracts.py`
12. `src/musica/project.py`
13. existing Preview/Accept authority implementation and tests
14. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**
