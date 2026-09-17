# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → COMMERCIAL WORKSTATION EXPANSION IN PROGRESS**

Long-term governing target:

> **MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving its AI-native authority, inspectability, reproducibility and programmability.**

This remains a product target, not a claim that MUSICA is already a complete commercial DAW.

## Canonical baseline / 공식 기준점

Parent mission:

- Issue `#95` — **Audio Track / Clip / Mixer Foundation v0 — OPEN**

Completed / validated ATCM rungs:

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
- R2 merge: `bada04778630004b3b199a8283bd883a7b07909d`
- R2 validation: `evidence/ATCM_R2_VALIDATION.md`
- R3 Issue `#105` — **COMPLETED**
- R3 PR `#107` — **MERGED**
- R3 implementation merge/main: `fe6c53b41bb98762110001a61e715478464a5760`
- R3 pre-validation exact head: `8db2c3cc0e85d416c84ee2106df4bbb5c64ceeef` — **19/19 permanent workflows SUCCESS**
- R3 validation-record exact head: `cc5c3111563d2c18015c1d66b110643aa3a20f30` — **19/19 permanent workflows SUCCESS**
- R3 durable validation: `evidence/ATCM_R3_VALIDATION.md`

Current exact rung:

- Issue `#111` — **ATCM-R4 — Restart/Reopen Native-Audio Lifecycle & Parent Closure Evaluation v0 — OPEN**

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**

The commercial-workstation objective extends this proposition; it does not replace it.

## Validated native-audio foundation / 검증된 네이티브 오디오 기반

### ATCM-R0 — immutable asset boundary

Validated immutable bounded PCM WAV import, content-addressed object identity, descriptor/audit binding, project-integrity checks and deterministic export/import. Imported bytes do not gain creative authority by import alone.

### ATCM-R1 — accepted track/clip authority

Validated source-bound native-audio Preview → explicit Accept authority for stable tracks/clips, move/trim/clip-gain editing, exact asset/range binding, stale-source rejection and deterministic reopen.

### ATCM-R2 — deterministic offline mixer

Validated exact accepted arrangement/mixer → deterministic mix plan → byte-reproducible stereo PCM16 WAV, including explicit sample-rate/channel, gain, pan, mute/solo, summing, clipping and output semantics. Mixed audio remains derived/non-canonical.

### ATCM-R3 — truthful Browser arrangement/mixer surface

Validated:

```text
exact accepted native-audio revision
→ Browser arrangement/mixer projection
→ source-bound native-audio Preview
→ accepted HEAD unchanged
→ derived R2 native-mix audition
→ explicit trusted Accept
→ exactly one accepted revision advance
```

R3 real-Chromium evidence proved:

- accepted track/clip/mixer projection;
- arrangement Preview with accepted HEAD unchanged;
- preview-derived audition distinct from accepted audition;
- discard with accepted HEAD unchanged;
- mixer Preview with accepted HEAD unchanged;
- explicit trusted Accept advancing exactly once;
- service restart + fresh Browser reopen restoring accepted mixer state;
- stale Preview rejection after an independent accepted HEAD advance;
- zero page errors, console errors and non-ignored request failures in final evidence.

R3 dedicated evidence:

- workflow: `ATCM-R3 Browser Native Audio Evidence`
- pre-validation run: `35192996006` — **SUCCESS**
- artifact ID: `10484249087`
- artifact ZIP SHA-256: `ebe04df259bdb8948446533096f8061acdd21cdafdf4cca9f443d258abf07bdd`

### R3 maximum validated claim

> **MUSICA can truthfully project exact accepted native-audio tracks/clips and bounded mixer state into a Browser arrangement/mixer surface, create source-bound arrangement or mixer Previews without mutating accepted state, audition exact derived R2 mixes, explicitly Accept through the existing trusted native-audio authority path, restore accepted state after restart/reopen, and fail closed on stale Preview acceptance.**

## ATCM-R4 selected current rung / R4 현재 단계

Issue `#111` is the exact next implementation/evidence rung.

Its bounded lifecycle is:

```text
accepted project revision + immutable audio assets
→ deterministic persistence/export
→ process/service stop
→ fresh process + reopen/import
→ exact accepted revision/arrangement/mixer restored
→ fresh Browser projection
→ same deterministic R2 mix-plan SHA + WAV SHA
→ pending/orphaned Preview not promoted
→ corrupted persistence fails closed
```

R4 must use actual process/service restart and fresh Chromium evidence, not only in-process object re-instantiation.

## Parent Issue #95 closure rule / 상위 미션 종결 규칙

R4 must evaluate parent `#95` only against its bounded foundation scope:

- immutable native audio asset boundary;
- accepted audio track/clip authority;
- deterministic bounded multitrack mixer;
- truthful Browser arrangement/mixer interaction;
- restart/reopen persistence lifecycle with fail-closed integrity.

If these are fully evidenced, a later state-only closure may close `#95` with bounded wording. If not, keep `#95` open and create the smallest evidence-backed missing rung. Closing `#95` must not imply completion of recording, real-time device I/O, plugins, buses/sends, latency compensation, resampling, warp/time-stretch, destructive editing, mastering, collaboration or commercial release hardening.

## Current important non-claims / 현재 주요 비주장

Until separately validated, do not claim:

- microphone/line recording or monitoring;
- low-latency ASIO/CoreAudio/WASAPI device operation;
- VST3/AU/CLAP hosting;
- generalized buses/sends/sidechains or latency compensation;
- implicit sample-rate conversion;
- warp/time-stretch/pitch shift or destructive waveform editing;
- mastering-grade processing;
- commercial release readiness or supported production SLA;
- cloud/multi-user creative authority;
- perceptual superiority.

## Exact next phase / 다음 단계

> **Issue #111 — ATCM-R4: prove exact native-audio persistence across real process/service restart and fresh Browser reopen, reproduce the same accepted-state derived mix, fail closed on orphaned Preview/corrupted persistence, then perform a bounded evidence-based parent #95 closure evaluation.**

See `memory/NEXT_ACTION.md` for exact execution order.

## Resume authority / 재개 권위

Before R4 implementation inspect at minimum:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/COMMERCIAL_WORKSTATION_TARGET.md`
3. parent Issue `#95`
4. Issue `#111`
5. `evidence/ATCM_R0_VALIDATION.md`
6. `evidence/ATCM_R1_VALIDATION.md`
7. `evidence/ATCM_R2_VALIDATION.md`
8. `evidence/ATCM_R3_VALIDATION.md`
9. `src/musica/project.py`
10. `src/musica/audio_assets.py`
11. `src/musica/audio_edit.py`
12. `src/musica/native_mixer.py`
13. `src/musica/studio_audio.py`
14. R3 Browser/HTTP/E2E modules and tests
15. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**