# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**ISSUE #105 — ATCM-R3 — BROWSER NATIVE-AUDIO ARRANGEMENT & MIXER SURFACE v0**

ATCM-R2 is validated and merged. The exact next rung is to project the accepted native-audio arrangement and bounded mixer into the Browser/Studio while preserving the same Preview → explicit Accept authority model.

Do **not** widen this rung into recording, a low-latency device engine, plugin hosting, buses/sends, hidden resampling, warp/time-stretch or mastering DSP.

## Canonical base / 공식 기준점

- parent Issue `#95` — **OPEN**
- ATCM-R0 `#97` — **COMPLETED / VALIDATED**
- ATCM-R1 `#99` — **COMPLETED / VALIDATED**
- ATCM-R2 Issue `#102` — **COMPLETED**
- ATCM-R2 PR `#104` — **MERGED**
- ATCM-R2 merge/main: `bada04778630004b3b199a8283bd883a7b07909d`
- R2 pre-validation exact head `909300fa50692ca789ba39d7994bd5fa61e8b5ee` — **18/18 SUCCESS**
- R2 validation-record exact head `bc68d74b764c1c657654fe0f20b5a3498ed4bc6e` — **18/18 SUCCESS**
- durable R2 validation: `evidence/ATCM_R2_VALIDATION.md`
- exact next Issue `#105` — **OPEN**

## Inherited authority / 상속 권한

R3 inherits three already validated layers:

```text
R0: immutable bounded PCM WAV resource authority
R1: accepted native-audio track/clip Preview→Accept authority
R2: exact accepted arrangement/mixer → deterministic derived mix plan/WAV
```

R3 may expose and operate these layers through Browser/Studio, but may not create a second authority system.

The intended Browser loop is:

```text
accepted revision
→ Browser accepted projection
→ user Browser edit intent
→ source-bound R1/R2 candidate
→ Preview projection; accepted HEAD unchanged
→ optional derived R2 audition
→ explicit Accept or discard
→ accepted revision changes only on Accept
```

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground existing Browser/Studio architecture

Inspect before writing R3 code:

- current Studio service/API module(s);
- Browser app/static JS/CSS/HTML modules;
- existing Browser E2E tests and Playwright evidence generators;
- M6 exact-note Browser editing paths;
- M7 automation Browser editing/audition paths;
- accepted-revision Compare surface;
- `src/musica/audio_edit.py`;
- `src/musica/audio_mixer_edit.py`;
- `src/musica/native_mixer.py`.

Reuse proven patterns rather than creating a parallel UI/runtime architecture.

### 2. Freeze truthful Browser state model

The Browser model must distinguish at least:

- accepted source revision ID;
- currently displayed accepted audio material;
- optional Preview candidate ID;
- Preview source revision/hash binding;
- Preview material;
- accepted vs Preview labels;
- whether explicit Accept is currently legal;
- any derived audition mix-plan/WAV identity.

Browser-local state must never be mistaken for accepted creative state.

### 3. Expose accepted arrangement projection

Browser/Studio should project, without mutation:

- stable track ID and order;
- track name;
- mixer gain/pan/mute/solo;
- stable clip ID;
- asset ID/reference;
- timeline start;
- source in/out;
- clip gain.

Prefer one normalized JSON projection from the service over duplicating domain logic in JavaScript.

### 4. Arrangement Preview operations

Wire Browser actions through the existing R1 candidate/Preview authority for at minimum:

- add track;
- add clip from an existing immutable project asset;
- move clip;
- trim source range;
- set clip gain.

Preview creation must not advance project HEAD.

### 5. Mixer Preview operations

Wire Browser controls through the R2 mixer candidate builder for:

- track gain;
- pan;
- mute;
- solo.

The Browser must not recalculate R2 DSP semantics independently. It edits accepted mixer fields through authority; `native_mixer.py` remains the audible semantics source of truth.

### 6. Explicit Accept / discard

Use the existing `AudioEditPreview` + `accept_audio_edit_preview()` authority path.

Required behavior:

- Accept revalidates exact source/head/assets;
- accepted revision advances exactly once;
- discard removes Browser Preview without accepted-state mutation;
- a Preview becomes stale after another accepted revision advances HEAD and must fail closed.

### 7. Truthful derived audition

Expose a bounded audition path using the R2 native mixer.

Audition metadata must identify:

- whether the source is accepted or Preview-derived;
- source revision ID;
- candidate ID where applicable;
- mix sample rate;
- mix-plan SHA;
- WAV SHA.

Rendered WAV remains derived/non-canonical.

If Preview audition requires a temporary noncanonical render path, implement it explicitly; never commit the Preview merely to hear it.

### 8. Browser usability boundary

Provide a minimally coherent arrangement/mixer surface rather than disconnected raw forms.

At minimum the user should be able to identify:

- which track/clip is being edited;
- accepted vs Preview values;
- mixer controls and their current values;
- whether a Preview exists;
- Accept / discard controls;
- audition identity/status/error.

Do not claim broad DAW usability yet. R3 validates a bounded workflow surface.

### 9. Fail-closed service/API matrix

Test at minimum:

- unknown track ID;
- unknown clip ID;
- missing/corrupt/cross-project asset;
- source-range overrun;
- invalid gain/pan;
- stale source hash/revision;
- stale Preview after HEAD change;
- direct accepted-state mutation request;
- Accept without valid Preview;
- unsupported R2 audition source rate/state.

Errors must be visible and typed enough for the Browser to tell the truth rather than silently substituting behavior.

### 10. Real-browser lifecycle evidence

Use actual Chromium/Playwright.

Minimum evidence flow:

```text
open accepted native-audio project
→ inspect exact accepted tracks/clips/mixer
→ create arrangement Preview
→ prove accepted HEAD unchanged
→ inspect accepted-vs-Preview difference
→ audition derived state truthfully
→ discard or Accept
→ create mixer Preview
→ prove accepted HEAD unchanged
→ explicit Accept
→ prove exactly one revision advance
→ reopen Browser/project
→ accepted arrangement/mixer restored exactly
→ attempt stale Preview after HEAD change
→ fail closed
```

Record machine-readable observations, revision/candidate IDs, key DOM truth labels, mix-plan/WAV hashes and evidence manifest.

### 11. Permanent R3 gate

Add a dedicated ATCM-R3 Browser evidence workflow without weakening the existing **18** permanent workflows.

Expected permanent workflow count after R3 gate: **19**.

The R3 gate should include:

- service/unit regressions;
- Browser E2E with real Chromium;
- deterministic evidence where the non-browser portion is deterministic;
- uploaded evidence package;
- no ignored console/server errors unless a specific proven exception exists.

### 12. Promotion

R3 promotion requires:

- bounded implementation complete;
- dedicated R3 evidence green;
- all 19 permanent workflows green on exact implementation/evidence head;
- evidence independently inspected;
- durable `evidence/ATCM_R3_VALIDATION.md`;
- all 19 workflows green again on exact validation-record head;
- expected-head squash merge;
- Issue `#105` completed;
- separate state-only closure;
- then open/execute ATCM-R4.

## Explicit R3 non-goals / R3 비목표

Do not implement in R3:

- microphone/line recording;
- ASIO/CoreAudio/WASAPI callback engine;
- low-latency monitoring guarantees;
- VST3/AU/CLAP hosting;
- arbitrary buses/sends/sidechains;
- plugin delay compensation;
- implicit sample-rate conversion;
- warp/time-stretch/pitch shift;
- destructive waveform editing;
- mastering-grade limiter/dither claims;
- generalized commercial-release qualification.

## Parent Issue #95 rung sequence / 상위 미션 순서

```text
ATCM-R0 immutable asset + authority contracts        VALIDATED
→ ATCM-R1 accepted track/clip Preview→Accept        VALIDATED
→ ATCM-R2 deterministic multitrack mixer            VALIDATED
→ ATCM-R3 Browser arrangement + mixer               CURRENT / Issue #105
→ ATCM-R4 restart/reopen + real-browser lifecycle
→ Issue #95 closure decision
```

## R3 maximum intended outcome / R3 최대 의도 결과

> **MUSICA can truthfully project accepted native-audio tracks/clips and bounded mixer state into a Browser arrangement/mixer surface, create source-bound arrangement or mixer Previews without mutating accepted state, audition exact derived R2 mixes, and advance accepted authority only through explicit Accept, with real-browser evidence and fail-closed stale/bypass behavior.**

This remains a target claim until Issue `#105` is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
