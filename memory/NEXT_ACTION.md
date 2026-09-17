# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**ISSUE #99 — ATCM-R1 — ACCEPTED AUDIO TRACK / CLIP AUTHORITY & ASSET BINDING v0**

ATCM-R0 is validated and merged. The exact next rung is to open a trusted canonical path from immutable in-project audio assets into accepted audio track/clip state through source-bound Preview → explicit Accept authority.

Do **not** widen this rung into deterministic multitrack mixing, Browser arrangement, recording, real-time audio or plugin hosting.

## Canonical base / 공식 기준점

- ATCM-R0 implementation merge/main: `f3c5c5d9cc8289dcdb88a420dea8db29d14f74dc`
- ATCM-R0 Issue `#97` — **COMPLETED**
- ATCM-R0 PR `#98` — **MERGED**
- ATCM-R0 durable validation: `evidence/ATCM_R0_VALIDATION.md`
- R0 validation-record exact head: `dfb8e9cce1d4044fc249d5dba80583eff678b12b` — **16/16 permanent workflows SUCCESS**
- parent Issue `#95` — **OPEN**
- exact next Issue `#99` — **OPEN**

## R0 authority inherited by R1 / R1이 상속하는 R0 권한

R0 validates:

```text
bounded PCM WAV bytes
→ immutable SHA-256 project object
→ exact audio asset descriptor
→ descriptor/object/audit integrity
→ deterministic project export/import
```

R0 deliberately blocks non-empty native audio material from canonical acceptance because no trusted audio edit authority existed yet.

R1 must preserve that fail-closed property except through its own explicitly source-bound acceptance path.

## R1 exact authority model / R1 정확한 권한 모델

```text
accepted source revision
+ immutable in-project audio asset
→ source-bound audio edit candidate
→ project-bound asset/material validation
→ READY_FOR_PREVIEW or BLOCKED
→ install Preview only
→ accepted HEAD unchanged
→ explicit Accept only
→ revalidate source + asset integrity + material
→ exactly one accepted revision advance
```

Derived buffers, waveform state, rendered audio, Browser/runtime state and future mixer state have no reverse-promotion authority.

## Exact implementation order / 정확한 구현 순서

Proceed in this order unless repository evidence proves a narrower correction is required.

### 1. Re-ground exact authority primitives

Inspect and reuse the existing Preview/Accept lifecycle rather than creating a second acceptance subsystem.

At minimum inspect:

- `src/musica/audio_assets.py`
- `src/musica/audio_contracts.py`
- `src/musica/project.py`
- `src/musica/contracts.py`
- current semantic/exact-note/automation Preview/Accept implementation
- source-bound stale-revision tests
- `schemas/audio-material-v0.schema.json`
- `evidence/ATCM_R0_VALIDATION.md`

### 2. Add project-bound audio material validation

Generic structural validation is not sufficient for accepted audio references.

Add a project-aware validator that proves for every clip:

- `asset_id` is syntactically valid;
- descriptor exists in this exact project;
- underlying immutable object exists and matches exact SHA/size;
- descriptor audit binding remains valid;
- `source_in_seconds >= 0`;
- `source_out_seconds > source_in_seconds`;
- `source_out_seconds <= exact referenced asset duration`;
- project timeline end stays within project duration;
- stable track/clip IDs and canonical ordering remain valid.

Unknown, cross-project, missing, corrupt or out-of-range references must fail closed.

### 3. Define source-bound audio edit candidate/result contracts

Add versioned contracts for the minimum trusted R1 edit authority.

Candidate must bind at least:

- project ID;
- source revision ID;
- operation type;
- stable target IDs;
- exact requested parameters;
- referenced asset ID where applicable;
- deterministic candidate/result identity if repository patterns support it.

Result must distinguish bounded states such as:

```text
READY_FOR_PREVIEW
BLOCKED
```

Do not claim acceptance at candidate-generation time.

### 4. Implement minimum R1 operations

Trusted operations:

- add audio track;
- add/reference imported clip;
- move clip;
- trim source in/out;
- set bounded clip gain.

The material schema already contains track mixer fields for the parent mission, but R1 should keep them at canonical defaults and must not expose track gain/pan/mute/solo as validated audible edits yet.

### 5. Preview lifecycle

For every supported operation:

```text
accepted source revision
→ generate candidate
→ validate candidate/material/project-bound assets
→ install Preview
→ accepted HEAD remains unchanged
```

Preview must be disposable and non-canonical.

### 6. Explicit Accept lifecycle

Accept must:

- bind to the exact preview/source revision;
- reject stale source HEAD;
- revalidate all referenced audio assets and source ranges;
- produce one valid candidate Blueprint revision;
- remove the temporary R0 non-empty-audio acceptance block only through the trusted R1 authorization path;
- commit exactly one immutable accepted revision;
- leave no hidden secondary authority state.

Direct `commit_revision()` or equivalent bypass with non-empty audio material must remain blocked unless the call is carrying the explicit trusted R1 authorization mechanism.

### 7. Discard and stale-source behavior

Prove:

- Discard leaves accepted HEAD unchanged;
- stale candidate Preview/Accept fails closed;
- asset mutation/corruption between Preview and Accept blocks Accept;
- importing a new asset alone never advances accepted HEAD.

### 8. Persistence / reopen

Accepted R1 state must survive project export/import and reopen with:

- same accepted revision identity semantics;
- exact `asset_id` references;
- stable track IDs;
- stable clip IDs;
- exact timeline/source ranges;
- exact clip gain;
- project-bound asset validation still PASS.

### 9. Deterministic test matrix

At minimum:

- valid in-project asset reference PASS;
- unknown asset FAIL;
- cross-project asset FAIL;
- corrupt/missing asset FAIL;
- source overrun FAIL;
- duplicate/canonical-order violations FAIL;
- add-track Preview leaves HEAD unchanged;
- add-clip Preview leaves HEAD unchanged;
- move/trim/clip-gain Preview leaves HEAD unchanged;
- Discard leaves HEAD unchanged;
- explicit Accept advances exactly once;
- direct-commit bypass remains blocked;
- stale source FAIL;
- corruption after Preview blocks Accept;
- reopen preserves accepted material + exact asset binding;
- R0 import/export tests remain green;
- previous note/automation/Compare semantics remain green.

### 10. Dedicated deterministic evidence

Generate a deterministic R1 evidence package using a generated bounded PCM WAV fixture.

Required evidence path:

```text
create project
→ import exact audio asset
→ prove HEAD unchanged
→ create add-track/add-clip candidate
→ Preview
→ prove HEAD unchanged
→ Accept
→ prove exactly one revision advance
→ create move/trim/clip-gain candidate
→ Preview
→ Accept or Discard
→ export/import or reopen
→ verify accepted track/clip + exact asset identity
→ prove stale/out-of-range/cross-project/corrupt cases fail closed
```

Run evidence independently at least twice and compare all claimed deterministic outputs byte-for-byte where appropriate.

### 11. Permanent CI and promotion

Add one dedicated permanent R1 workflow without weakening prior gates.

Promotion requires:

- dedicated R1 tests/evidence green;
- all existing permanent workflows green on the exact evidence-bearing head;
- deterministic evidence package + manifest;
- durable R1 validation record;
- successor exact-head full rerun after validation-record commit;
- expected-head squash merge;
- Issue `#99` completed;
- separate state-only closure.

## Explicit R1 non-goals / R1 비목표

Do not implement in R1:

- deterministic multitrack summing or stereo mixdown;
- trusted track gain/pan/mute/solo audible semantics;
- Browser arrangement/mixer UI;
- microphone/line recording;
- ASIO/CoreAudio/WASAPI device engine;
- low-latency guarantees;
- plugin hosting;
- buses/sends/sidechains;
- warp/time-stretch/pitch shift;
- destructive waveform editing;
- DAW audio round-trip reconciliation;
- commercial release qualification.

## Parent Issue #95 rung sequence / 상위 미션 순서

```text
ATCM-R0 immutable asset + authority contracts        VALIDATED
→ ATCM-R1 accepted track/clip Preview→Accept        CURRENT / Issue #99
→ ATCM-R2 deterministic multitrack mixer semantics
→ ATCM-R3 Studio/Browser arrangement + mixer
→ ATCM-R4 restart/reopen + real-browser lifecycle
→ Issue #95 closure
```

## R1 maximum intended outcome / R1 최대 의도 결과

> **MUSICA can bind immutable in-project audio assets into stable accepted audio tracks/clips through source-bound Preview/Accept authority, preserve exact source ranges and clip gain, reject stale/missing/corrupt/out-of-range references, and reopen the accepted arrangement without granting derived audio or runtime state reverse authority.**

This remains a target claim until Issue `#99` is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
