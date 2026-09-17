# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → COMMERCIAL WORKSTATION EXPANSION IN PROGRESS**

Long-term governing target:

> **MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving its AI-native authority, inspectability, reproducibility and programmability.**

This is a product target, not a claim that MUSICA is already a complete commercial DAW.

## Canonical baseline / 공식 기준점

Parent mission:

- Issue `#95` — **Audio Track / Clip / Mixer Foundation v0 — OPEN**

Completed ATCM rungs:

- R0 Issue `#97` — **COMPLETED**
- R0 PR `#98` — **MERGED**
- R0 merge: `f3c5c5d9cc8289dcdb88a420dea8db29d14f74dc`
- R0 validation: `evidence/ATCM_R0_VALIDATION.md`
- R1 Issue `#99` — **COMPLETED**
- R1 PR `#101` — **MERGED**
- R1 merge: `f95268d8dba368e4d9ce01039848a06206e68fa7`
- R1 validation: `evidence/ATCM_R1_VALIDATION.md`
- R2 Issue `#102` — **COMPLETED**
- R2 PR `#104` — **MERGED**
- R2 implementation merge/main: `bada04778630004b3b199a8283bd883a7b07909d`
- R2 pre-validation exact head: `909300fa50692ca789ba39d7994bd5fa61e8b5ee` — **18/18 permanent workflows SUCCESS**
- R2 validation-record exact head: `bc68d74b764c1c657654fe0f20b5a3498ed4bc6e` — **18/18 permanent workflows SUCCESS**
- R2 durable validation: `evidence/ATCM_R2_VALIDATION.md`

Current next rung:

- Issue `#105` — **ATCM-R3 — Browser Native-Audio Arrangement & Mixer Surface v0 — OPEN**

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**

The commercial-workstation objective extends this proposition; it does not replace it.

## Validated native-audio foundation / 검증된 네이티브 오디오 기반

### ATCM-R0 — immutable asset boundary

Validated:

```text
bounded PCM WAV bytes
→ content-addressed immutable project object
→ SHA-256 asset identity
→ descriptor + audit binding
→ project-integrity validation
→ deterministic export/import
```

Imported resource bytes do not receive creative authority merely by being imported.

### ATCM-R1 — accepted arrangement authority

Validated:

```text
accepted source revision
+ immutable project audio asset
→ source-bound audio edit candidate
→ READY_FOR_PREVIEW or BLOCKED
→ Preview; accepted HEAD unchanged
→ explicit Accept
→ exactly one accepted revision advance
```

Validated operations include stable track/clip creation, clip placement, source trim and bounded clip gain, with stale/missing/corrupt/out-of-range references failing closed.

### ATCM-R2 — deterministic offline mixer

Validated:

```text
exact accepted native-audio revision
+ immutable project audio assets
+ versioned deterministic mixer policy
→ exact mix plan
→ deterministic offline stereo PCM mix
→ byte-reproducible WAV
≠ creative authority
```

Bounded R2 semantics now include:

- exact revision / Blueprint / audio-material / asset bindings;
- exact source-rate match with no hidden resampling;
- mono/stereo source to stereo output;
- deterministic seconds→frame round-half-up rule;
- clip and track dB gain lowering;
- linear-balance pan law;
- mute-wins then solo-isolates precedence;
- canonical track/clip summing order;
- float64 accumulation;
- hard clip before deterministic PCM16 little-endian WAV encoding;
- deterministic mix-plan SHA-256 and WAV SHA-256;
- byte-identical repeated rendering and reopen/re-render identity;
- R2 mixer field edits using the same R1 Preview/Accept authority family.

R2 dedicated evidence:

- workflow: `ATCM-R2 Native Mixer Evidence`
- successful pre-validation run: `35184486911`
- artifact: `10481497910`
- artifact ZIP digest: `sha256:403f04a307ea7cc6f73c74a7e24aa36414e4f0cf64a55184cb4aadddf04be5b2`
- before WAV SHA-256: `c30d8c450ee37ecae99aff96c00011b2dab0d2ece2c981484bed52912d9154a7`
- after WAV SHA-256: `aa9b9d6015f4f0d65d3390a659bcf306deb0e9fb9036d31fcef8e9c72c687db8`

### R2 maximum validated claim

> **MUSICA can deterministically lower an exact accepted native-audio arrangement and bounded mixer state into an exact project-bound mix plan and byte-reproducible offline stereo WAV, with explicit gain/pan/mute/solo/summing/clipping semantics and fail-closed unsupported inputs, while keeping rendered audio derived from accepted creative authority.**

## ATCM-R3 selected current rung / R3 현재 단계

Issue `#105` is now the exact implementation rung.

Its bounded authority loop is:

```text
exact accepted native-audio revision
→ Browser arrangement + mixer projection
→ source-bound Preview edit
→ accepted HEAD remains unchanged
→ truthful derived R2 audition
→ explicit Accept or discard
→ exactly one accepted revision advance only on Accept
```

R3 must expose accepted-vs-preview truth, stable track/clip IDs, asset identity, clip placement/range/gain and track gain/pan/mute/solo while reusing R1/R2 authority rather than inventing Browser authority.

## Parent Issue #95 remaining path / 상위 미션 잔여 경로

```text
ATCM-R0 immutable asset + authority contracts        VALIDATED
→ ATCM-R1 accepted track/clip Preview→Accept        VALIDATED
→ ATCM-R2 deterministic multitrack mixer            VALIDATED
→ ATCM-R3 Browser arrangement + mixer               CURRENT / Issue #105
→ ATCM-R4 restart/reopen + real-browser lifecycle
→ parent Issue #95 closure decision
```

## Current important non-claims / 현재 주요 비주장

Until separately validated, do not claim:

- R3 Browser native-audio arrangement/mixer workflow;
- microphone/line recording or monitoring;
- low-latency ASIO/CoreAudio/WASAPI device engine;
- VST3/AU/CLAP hosting;
- generalized buses/sends/sidechains or latency compensation;
- hidden sample-rate conversion, warp/time-stretch or destructive waveform editing;
- commercial release readiness or supported production SLA;
- cloud/multi-user authority;
- perceptual superiority.

## Exact next phase / 다음 단계

> **Issue #105 — ATCM-R3: expose the validated native-audio arrangement and bounded mixer through a truthful Browser/Studio surface, preserve Preview-vs-Accept authority, and audition exact derived R2 mixes without granting Browser/runtime state reverse authority.**

See `memory/NEXT_ACTION.md` for exact execution order.

## Resume authority / 재개 권위

Before R3 implementation inspect at minimum:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/COMMERCIAL_WORKSTATION_TARGET.md`
3. parent Issue `#95`
4. Issue `#105`
5. `evidence/ATCM_R0_VALIDATION.md`
6. `evidence/ATCM_R1_VALIDATION.md`
7. `evidence/ATCM_R2_VALIDATION.md`
8. `src/musica/audio_edit.py`
9. `src/musica/audio_mixer_edit.py`
10. `src/musica/native_mixer.py`
11. current Studio/Browser service and web-app modules/tests
12. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**
