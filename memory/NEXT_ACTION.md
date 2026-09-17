# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**ISSUE #102 — ATCM-R2 — DETERMINISTIC MULTITRACK MIXER SEMANTICS & OFFLINE MIXDOWN v0**

ATCM-R1 is validated and merged. The exact next rung is to make the accepted native-audio arrangement deterministically audible through a bounded offline multitrack mixer.

Do **not** widen this rung into Browser mixer UI, recording, real-time device playback, plugin hosting, buses/sends, hidden resampling, or mastering DSP.

## Canonical base / 공식 기준점

- ATCM-R1 implementation merge/main: `f95268d8dba368e4d9ce01039848a06206e68fa7`
- ATCM-R1 Issue `#99` — **COMPLETED**
- ATCM-R1 PR `#101` — **MERGED**
- ATCM-R1 pre-validation exact head `0bc066b2960e3d2500e5fc5688da612fe233887e` — **17/17 SUCCESS**
- ATCM-R1 validation-record exact head `242316843acad58fe2181b93634cbe036ac59627` — **17/17 SUCCESS**
- ATCM-R1 durable validation: `evidence/ATCM_R1_VALIDATION.md`
- parent Issue `#95` — **OPEN**
- exact next Issue `#102` — **OPEN**

## Inherited authority / 상속 권한

R0 validates immutable bounded PCM WAV assets and deterministic project persistence.

R1 validates accepted native-audio track/clip authority through source-bound Preview → explicit Accept. R2 must consume only exact accepted R1 state and immutable in-project assets.

The signal path is:

```text
accepted R1 revision
+ exact project assets
+ versioned deterministic mixer policy
→ exact mix plan
→ deterministic offline mix
→ deterministic stereo WAV
≠ accepted creative authority
```

Mix plans and WAVs are derived outputs. They may be hash-bound to an accepted revision, but they have no reverse-promotion authority.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground R1 accepted audio state

Inspect:

- `evidence/ATCM_R1_VALIDATION.md`
- `schemas/audio-material-v0.schema.json`
- `src/musica/audio_assets.py`
- `src/musica/audio_contracts.py`
- `src/musica/audio_edit.py`
- `src/musica/project.py`
- `tests/test_atcm_r1_audio_authority.py`

Do not create a second creative-state authority model.

### 2. Freeze a bounded v0 mixer policy

Define a versioned policy before implementing DSP. It must state exactly:

- required mix sample rate;
- supported source sample formats;
- supported source channel counts;
- mono→stereo mapping if mono is supported;
- seconds→sample-index quantization;
- source in/out→frame-range quantization;
- clip gain dB→linear mapping;
- track gain dB→linear mapping;
- pan law and exact coefficients;
- mute behavior;
- solo behavior;
- mute/solo precedence;
- track and clip summing order;
- accumulation precision;
- clipping/headroom policy;
- output channel count;
- PCM sample width / signedness / endianness;
- deterministic WAV encoding policy.

Prefer a narrow fail-closed policy over implicit conversion.

### 3. Sample-rate policy

For v0, prefer **no hidden resampler**.

Recommended boundary:

- one explicit mix sample rate;
- every referenced source asset must have that exact sample rate;
- mismatch fails closed;
- a future resampler requires its own versioned contract/evidence.

### 4. Define canonical mix-plan contract

The plan must bind at least:

- project ID;
- exact accepted revision ID;
- accepted Blueprint SHA-256;
- accepted audio-material SHA-256;
- mixer policy/version;
- output sample rate/channels/sample format;
- ordered tracks;
- ordered clips;
- exact asset IDs/object hashes;
- exact source frame ranges;
- exact destination sample ranges;
- resolved gain/pan/mute/solo values;
- deterministic plan SHA-256.

Plan construction must be deterministic and project-bound.

### 5. Implement deterministic source decoding

Use only the bounded R0 WAV/PCM domain in R2.

Fail closed on:

- missing/corrupt descriptor/object;
- unsupported compression/format;
- unsupported channel count;
- unsupported sample width;
- sample-rate mismatch;
- source range outside exact asset duration;
- stale/mismatched revision or material binding.

### 6. Implement clip placement and gain

For each clip:

- slice exact source frames;
- map exact destination sample index;
- apply clip gain;
- preserve silence before/between/after clips;
- overlap using deterministic summing order.

Tests must include boundary sample positions and overlapping clips.

### 7. Implement bounded track mixer semantics

R2 is the first rung allowed to claim audible semantics for existing track mixer fields.

Prove exact behavior for:

- track gain;
- pan;
- mute;
- solo;
- multiple solos;
- mute + solo precedence;
- interaction with clip gain.

If editing track mixer fields is needed, extend the existing source-bound audio Preview/Accept authority family explicitly. Do not mutate accepted Blueprint state directly.

### 8. Define deterministic summing/output policy

At minimum specify and test:

- float64 accumulation or another explicit precision;
- deterministic track/clip processing order;
- handling of values outside output range;
- clipping/saturation policy;
- float→integer PCM quantization/rounding;
- RIFF/WAVE chunk order and absence of nondeterministic metadata.

Do not claim dither/limiter/mastering unless separately implemented and evidenced.

### 9. Build offline renderer

Required APIs should conceptually separate:

```text
accepted revision → mix plan
mix plan + immutable assets → PCM buffer
PCM buffer → deterministic WAV bytes
```

Keep planning, execution and encoding inspectable rather than one opaque renderer call.

### 10. Deterministic test matrix

At minimum prove:

- identical accepted state → identical plan SHA;
- identical plan/assets → byte-identical WAV;
- exact timeline placement;
- exact source slicing;
- mono/stereo supported behavior;
- clip gain effect;
- track gain effect;
- left/center/right pan coefficients;
- mute semantics;
- single/multiple solo semantics;
- mute/solo precedence;
- overlap summing;
- silence/gaps;
- clipping/output conversion policy;
- reopen project → same plan and WAV hashes;
- sample-rate mismatch FAIL;
- missing/corrupt asset FAIL;
- unsupported channels/format FAIL;
- out-of-range source FAIL;
- mismatched revision/material binding FAIL.

### 11. Dedicated deterministic evidence

Construct an evidence fixture with multiple accepted clips/assets, including overlap and silence.

Required flow:

```text
create deterministic project/assets
→ accept exact R1 arrangement
→ build mix plan A
→ render WAV A
→ independently build mix plan B
→ render WAV B
→ plan A == B byte-for-byte
→ WAV A == B byte-for-byte
→ reopen project
→ same plan SHA / WAV SHA
→ controlled mixer-state change through authority path
→ exact documented output difference
→ negative cases fail closed
```

The evidence package must record exact source revision, asset IDs, plan SHA, WAV SHA, sample counts, peak/output facts relevant to the claim, and a manifest.

### 12. Permanent CI and promotion

Add one dedicated permanent ATCM-R2 workflow without weakening the existing 17 gates.

Promotion requires:

- R2 tests/evidence green;
- all permanent workflows green on exact evidence-bearing head;
- deterministic evidence A/B byte equality;
- independently inspectable artifact manifest;
- durable `evidence/ATCM_R2_VALIDATION.md`;
- successor exact-head full rerun;
- expected-head squash merge;
- Issue `#102` completed;
- separate state-only closure.

## Explicit R2 non-goals / R2 비목표

Do not implement in R2:

- Browser native-audio arrangement/mixer UI;
- microphone/line recording;
- ASIO/CoreAudio/WASAPI callback engine;
- low-latency playback guarantees;
- VST3/AU/CLAP hosting;
- arbitrary buses/sends/sidechains;
- plugin delay compensation;
- implicit sample-rate conversion;
- warp/time-stretch/pitch shift;
- destructive waveform editing;
- mastering-grade limiter/dither claims;
- commercial release qualification.

## Parent Issue #95 rung sequence / 상위 미션 순서

```text
ATCM-R0 immutable asset + authority contracts        VALIDATED
→ ATCM-R1 accepted track/clip Preview→Accept        VALIDATED
→ ATCM-R2 deterministic multitrack mixer            CURRENT / Issue #102
→ ATCM-R3 Studio/Browser arrangement + mixer
→ ATCM-R4 restart/reopen + real-browser lifecycle
→ Issue #95 closure
```

## R2 maximum intended outcome / R2 최대 의도 결과

> **MUSICA can deterministically lower an exact accepted native-audio arrangement and bounded mixer state into an exact project-bound mix plan and byte-reproducible offline stereo WAV, with explicit gain/pan/mute/solo/summing/clipping semantics and fail-closed unsupported inputs, while keeping rendered audio derived from accepted creative authority.**

This remains a target claim until Issue `#102` is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
