# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**ISSUE #111 — ATCM-R4 — RESTART/REOPEN NATIVE-AUDIO LIFECYCLE & PARENT CLOSURE EVALUATION v0**

ATCM-R3 is validated and merged. The exact next rung is to prove the bounded native-audio foundation across real process/service restart and fresh Browser reopen, then evaluate parent Issue #95 against its intended foundation scope only.

Do **not** widen this rung into recording, low-latency device I/O, plugin hosting, buses/sends, resampling, warp/time-stretch, mastering or generalized release hardening.

## Canonical base / 공식 기준점

- parent Issue `#95` — **OPEN**
- ATCM-R0 `#97` — **COMPLETED / VALIDATED**
- ATCM-R1 `#99` — **COMPLETED / VALIDATED**
- ATCM-R2 `#102` — **COMPLETED / VALIDATED**
- ATCM-R3 Issue `#105` — **COMPLETED**
- ATCM-R3 PR `#107` — **MERGED**
- ATCM-R3 merge/main: `fe6c53b41bb98762110001a61e715478464a5760`
- R3 pre-validation exact head `8db2c3cc0e85d416c84ee2106df4bbb5c64ceeef` — **19/19 SUCCESS**
- R3 validation-record exact head `cc5c3111563d2c18015c1d66b110643aa3a20f30` — **19/19 SUCCESS**
- durable R3 validation: `evidence/ATCM_R3_VALIDATION.md`
- exact next Issue `#111` — **OPEN**

## Inherited authority / 상속 권한

R4 inherits four validated layers:

```text
R0: immutable bounded PCM WAV resource boundary
R1: accepted native-audio track/clip Preview→Accept authority
R2: deterministic accepted arrangement/mixer → derived mix plan/WAV
R3: truthful Browser arrangement/mixer projection + Preview/Audition/Accept
```

R4 must prove these survive restart/reopen without creating, inferring or repairing creative authority from derived state.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground persistence and R3 lifecycle code

Inspect before writing R4 code:

- `evidence/ATCM_R3_VALIDATION.md`;
- `src/musica/project.py` export/import/reopen/integrity paths;
- `src/musica/audio_assets.py`;
- `src/musica/audio_edit.py`;
- `src/musica/audio_mixer_edit.py`;
- `src/musica/native_mixer.py`;
- `src/musica/studio_audio.py`;
- `src/musica/studio_http_r3.py`;
- R3 Browser JS/CSS/server overlay;
- `src/musica/atcm_r3_e2e.py`;
- project persistence and Browser lifecycle tests.

Do not create a second persistence format or authority model if the existing project archive/store already carries the required truth.

### 2. Freeze the restart/reopen contract

Specify exactly what must survive:

- project ID;
- accepted HEAD revision ID;
- accepted Blueprint hash/content;
- immutable audio asset IDs/descriptors/object hashes;
- audio track IDs/order/names;
- clip IDs/assets/timeline/source ranges/clip gains;
- track gain/pan/mute/solo;
- project-integrity status;
- R2 mix-plan SHA and WAV SHA regenerated from accepted state.

Specify what must **not** survive as authority:

- Browser-local UI state;
- transport position;
- decoded PCM caches;
- rendered WAV authority;
- pending nonaccepted Preview as accepted state;
- transient service/session identifiers unless explicitly required for diagnostics.

### 3. Define real restart boundary

Evidence must include actual service/process termination and fresh startup, not only a new Python object inside the same process.

Prefer one deterministic harness that can:

```text
start service A
→ operate project through Browser/API
→ persist/export
→ stop service A
→ start fresh service B
→ reopen/import
→ launch fresh Chromium
```

Process identity should be recorded in evidence where practical so restart is independently inspectable.

### 4. Establish accepted baseline before restart

Create a deterministic native-audio project using only validated R0–R3 paths:

- immutable bounded audio asset import;
- accepted track/clip arrangement;
- accepted mixer state;
- exact accepted HEAD;
- accepted R2 mix plan + WAV.

Record all relevant hashes before persistence/restart.

### 5. Persist/export through existing canonical project boundary

Use the existing deterministic project export/archive or equivalent validated persistence boundary.

Verify before shutdown:

- aggregate project integrity passes;
- archive/object/descriptor hashes are known;
- accepted revision and native-audio material are present;
- no derived Browser/runtime state is being smuggled into creative authority.

### 6. Fresh-process reopen/import

After terminating the first service/process:

- start a fresh service/process;
- reopen/import the persisted project;
- run project integrity;
- verify exact accepted HEAD and accepted Blueprint identity;
- verify exact asset descriptors/objects;
- verify exact arrangement and mixer state.

Any mismatch must fail promotion.

### 7. Fresh Browser truth projection

Launch a fresh Chromium process/session against the reopened project.

Verify visible/machine-readable truth for:

- accepted revision identity;
- tracks/clips/assets;
- timeline/source ranges/clip gains;
- track gain/pan/mute/solo;
- accepted-vs-preview state;
- no phantom pending Preview created by restart.

### 8. Reproduce exact accepted derived mix

Rebuild the R2 mix plan and WAV from reopened accepted state.

Required equality:

```text
pre-restart accepted mix-plan SHA == post-restart mix-plan SHA
pre-restart accepted WAV SHA      == post-restart WAV SHA
```

This proves reproducible derived audition binding; it does not grant rendered audio authority.

### 9. Nonaccepted Preview restart test

Create a valid native-audio Preview but do **not** Accept it.

Then restart/reopen again and prove:

- accepted HEAD is unchanged;
- Preview candidate material was not promoted;
- Browser accepted projection remains the accepted revision;
- any orphaned Preview/session reference is rejected or discarded fail-closed;
- a stale/orphaned Preview cannot be accepted after restart by bypassing source/head validation.

### 10. Corruption/missing-resource negative fixture

In an isolated copy/fixture, corrupt or remove at least one persisted native-audio object or descriptor.

Required result:

- import/reopen or integrity check fails closed;
- no silent resource repair;
- no fallback to stale rendered audio;
- no accepted creative state fabricated from Browser/runtime caches.

### 11. Authority bypass regression after restart

Reprove after reopen that:

- generic Studio commit cannot directly mutate accepted native-audio material;
- Browser direct mutation requests cannot bypass Preview→Accept;
- Accept revalidates source/head/assets;
- stale source still fails closed.

### 12. Real-browser deterministic evidence package

Evidence should contain at minimum:

- machine-readable proof JSON;
- process/service restart observations;
- pre/post accepted revision IDs;
- asset IDs/object/descriptor hashes;
- pre/post mix-plan and WAV hashes;
- Browser observations/screenshots before and after restart;
- orphaned-Preview rejection result;
- corruption fail-closed result;
- manifest with exact SHA-256 and byte sizes.

Where deterministic payloads are generated twice, prove byte equality.

### 13. Permanent R4 gate

Add one dedicated permanent ATCM-R4 lifecycle evidence workflow without weakening the existing **19** permanent workflows.

Expected permanent workflow count after R4 gate: **20**.

### 14. Promotion

R4 promotion requires:

- bounded implementation/evidence complete;
- dedicated R4 evidence green;
- all 20 permanent workflows green on exact evidence-bearing head;
- evidence independently inspected;
- durable `evidence/ATCM_R4_VALIDATION.md`;
- all 20 workflows green again on exact validation-record head;
- expected-head squash merge;
- Issue `#111` completed;
- separate state-only closure / parent #95 evaluation.

### 15. Parent Issue #95 closure evaluation

After R4 merge, evaluate only these bounded foundation criteria:

```text
immutable audio assets
+ accepted track/clip authority
+ deterministic bounded mixer
+ truthful Browser arrangement/mixer
+ restart/reopen persistence/integrity lifecycle
```

If all are durably evidenced, close parent `#95` with explicit bounded wording.

If any criterion remains unsupported, keep `#95` open and open the smallest missing rung. Do **not** weaken the closure criterion merely to finish the mission.

## Explicit R4 non-goals / R4 비목표

Do not implement in R4:

- microphone/line recording;
- ASIO/CoreAudio/WASAPI callback engine;
- low-latency monitoring guarantees;
- VST3/AU/CLAP hosting;
- arbitrary buses/sends/sidechains;
- plugin delay compensation;
- implicit sample-rate conversion;
- warp/time-stretch/pitch shift;
- destructive waveform editing;
- mastering-grade processing;
- cloud/multi-user authority;
- generalized commercial release qualification.

## Parent Issue #95 rung sequence / 상위 미션 순서

```text
ATCM-R0 immutable asset + authority contracts        VALIDATED
→ ATCM-R1 accepted track/clip Preview→Accept        VALIDATED
→ ATCM-R2 deterministic multitrack mixer            VALIDATED
→ ATCM-R3 Browser arrangement + mixer               VALIDATED
→ ATCM-R4 restart/reopen + lifecycle closure        CURRENT / Issue #111
→ Issue #95 bounded closure evaluation
```

## R4 maximum intended outcome / R4 최대 의도 결과

> **MUSICA can persist, restart and reopen the bounded native-audio foundation without changing creative authority, restore exact accepted arrangement/mixer state and immutable asset bindings in a fresh Browser/Studio process, reproduce the same deterministic derived mix, reject orphaned/stale Preview state, and fail closed on corrupted persisted resources; this evidence then supports a bounded decision on closing the Audio Track / Clip / Mixer Foundation v0 parent mission.**

This remains a target claim until Issue `#111` is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**