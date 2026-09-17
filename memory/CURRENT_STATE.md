# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → COMMERCIAL WORKSTATION EXPANSION IN PROGRESS**

MUSICA's long-term governing target remains:

> **MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving its AI-native authority, inspectability, reproducibility and programmability.**

This is a product target, not a claim that MUSICA is already a complete commercial DAW.

## Canonical baseline / 공식 기준점

- parent Issue `#95` — **Audio Track / Clip / Mixer Foundation v0 — OPEN**
- ATCM-R0 Issue `#97` — **COMPLETED**
- ATCM-R0 implementation PR `#98` — **MERGED**
- ATCM-R0 implementation merge: `f3c5c5d9cc8289dcdb88a420dea8db29d14f74dc`
- ATCM-R0 durable validation: `evidence/ATCM_R0_VALIDATION.md`
- ATCM-R1 Issue `#99` — **COMPLETED**
- ATCM-R1 implementation PR `#101` — **MERGED**
- ATCM-R1 implementation merge/main: `f95268d8dba368e4d9ce01039848a06206e68fa7`
- ATCM-R1 pre-validation exact head: `0bc066b2960e3d2500e5fc5688da612fe233887e` — **17/17 permanent workflows SUCCESS**
- ATCM-R1 validation-record exact head: `242316843acad58fe2181b93634cbe036ac59627` — **17/17 permanent workflows SUCCESS**
- ATCM-R1 durable validation: `evidence/ATCM_R1_VALIDATION.md`
- next bounded implementation Issue `#102` — **ATCM-R2 — Deterministic Multitrack Mixer Semantics & Offline Mixdown v0 — OPEN**

No artificial numeric milestone is assigned beyond the ATCM rung names.

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**

The commercial-workstation objective extends this proposition; it does not replace it.

## Validated product-loop coverage / 검증된 제품 루프

The bounded interaction thesis remains validated:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

Validated coverage includes typed intent/Blueprint generation, deterministic audition, locks/constraints, semantic/exact-note/automation Preview edits, explicit Accept, immutable revisions, restart/reopen, and accepted-revision A/B Compare with Browser-local human choice.

## ATCM-R0 validated capability / R0 검증 기능

R0 established the immutable native-source boundary:

```text
bounded PCM WAV bytes
→ content-addressed immutable project object
→ SHA-256 audio asset identity
→ descriptor + audit binding
→ project-integrity validation
→ deterministic export/import
```

R0 deliberately did not grant imported bytes or arbitrary non-empty `materials.audio` reverse authority into accepted creative state.

## ATCM-R1 validated capability / R1 검증 기능

R1 opened the first trusted native-audio acceptance path:

```text
accepted source revision
+ immutable in-project audio asset
→ source-bound audio edit candidate
→ project-bound asset/range/material validation
→ READY_FOR_PREVIEW or BLOCKED
→ Preview; accepted HEAD unchanged
→ explicit Accept
→ source/hash/asset revalidation
→ exactly one accepted revision advance
```

Validated R1 operations:

- add stable audio track;
- add/reference immutable project audio clip;
- move clip on the project timeline;
- trim source in/out;
- set bounded clip gain;
- discard Preview without accepted-state mutation;
- reject stale source, cross-project/missing/corrupt assets, source-range overrun and direct public commit bypass;
- persist/reopen exact accepted track/clip/asset state through deterministic project export/import.

R1 dedicated evidence:

- workflow: `ATCM-R1 Accepted Audio Authority Evidence`
- run: `35167647013`
- artifact: `10475436146`
- artifact ZIP SHA-256: `7f2d3d945bae31d3ba1ede32068bb65e893cbe48b962dca7863a1155fc3a93bd`

### R1 maximum validated claim

> **MUSICA can bind immutable in-project audio assets into stable accepted audio tracks/clips through source-bound Preview/Accept authority, preserve exact source ranges and clip gain, reject stale/missing/corrupt/out-of-range references, and reopen the accepted arrangement without granting rendered audio or runtime state reverse authority.**

R1 still does **not** validate deterministic native multitrack mixing or audible track gain/pan/mute/solo semantics.

## ATCM-R2 selected next rung / R2 다음 단계

Issue `#102` is the exact next implementation rung.

Its bounded signal path is:

```text
exact accepted R1 revision
+ exact immutable project audio assets
+ explicit versioned mixer policy
→ canonical deterministic mix plan
→ deterministic offline PCM mix
→ deterministic stereo WAV bytes
≠ creative authority
```

R2 must explicitly define and prove:

- exact revision/Blueprint/audio-material/asset bindings;
- sample-rate and channel support policy;
- seconds→sample/frame quantization;
- clip gain and track gain mapping;
- pan law;
- mute/solo precedence;
- deterministic summing order and numeric precision;
- clipping/headroom/output PCM/WAV encoding policy;
- stable mix-plan SHA and output SHA;
- fail-closed unsupported/missing/corrupt/mismatched inputs;
- byte-reproducible plan and WAV evidence.

R2 must keep mixed/rendered output derived and non-canonical.

## Parent Issue #95 remaining path / 상위 미션 잔여 경로

```text
ATCM-R0 immutable asset + authority contracts        VALIDATED
→ ATCM-R1 accepted track/clip Preview→Accept        VALIDATED
→ ATCM-R2 deterministic multitrack mixer            CURRENT / Issue #102
→ ATCM-R3 Studio/Browser arrangement + mixer
→ ATCM-R4 restart/reopen + real-browser lifecycle
→ parent Issue #95 closure
```

The boundaries may narrow if repository evidence requires it; they must not silently widen.

## Long-term commercial workstation target / 장기 상용 워크스테이션 목표

`docs/COMMERCIAL_WORKSTATION_TARGET.md` remains governing. Eventual credible coverage includes native arrangement, audio assets/recording, mixer/signal flow, instruments/effects/plugin hosting, real-time audio/device operation, non-destructive editing, AI/composition control, interoperability, persistence/recovery/performance, commercial distribution, and later collaboration as a separate distributed-authority domain.

## Current important non-claims / 현재 주요 비주장

Until separately validated, do not claim:

- deterministic native multitrack mixer execution beyond R2 once implemented;
- Browser native-audio arrangement/mixer workflow;
- recording or low-latency real-time device engine;
- VST3/AU/CLAP or other third-party plugin hosting;
- generalized buses/sends/sidechains or latency compensation;
- sample-rate conversion, warp/time-stretch or destructive waveform editing;
- external DAW native-audio round-trip reconciliation;
- generalized automation mapping;
- commercial release readiness or supported production SLA;
- cloud/multi-user authority;
- perceptual superiority.

## Exact next phase / 다음 단계

> **Issue #102 — ATCM-R2: define and implement an exact project-bound deterministic offline multitrack mixer from accepted R1 native-audio state, with explicit gain/pan/mute/solo/summing/clipping semantics, byte-reproducible mix plans and WAV outputs, and fail-closed unsupported inputs.**

See `memory/NEXT_ACTION.md` for the exact execution order.

## Resume authority / 재개 권위

Before ATCM-R2 implementation, inspect at minimum:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/COMMERCIAL_WORKSTATION_TARGET.md`
3. parent Issue `#95`
4. Issue `#102`
5. `evidence/ATCM_R0_VALIDATION.md`
6. `evidence/ATCM_R1_VALIDATION.md`
7. `schemas/audio-asset-v0.schema.json`
8. `schemas/audio-material-v0.schema.json`
9. `src/musica/audio_assets.py`
10. `src/musica/audio_contracts.py`
11. `src/musica/audio_edit.py`
12. `src/musica/project.py`
13. `tests/test_atcm_r1_audio_authority.py`
14. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**
