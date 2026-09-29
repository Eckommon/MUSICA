# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**REC-R0 — INPUT/CAPTURE CONTRACTS & DETERMINISTIC SIMULATED INPUT BACKEND v0**

Issue `#143` — **OPEN**

Parent mission: Issue `#142` — **Recording & Monitoring Foundation v0 — OPEN**

The bounded Real-Time Audio Engine & Device Foundation v0 (Issue `#129`) is validated and completed. The next dependency-safe step is to define an input/capture substrate before adding trusted recording acceptance, monitoring UX, take management or host-native microphone claims.

## Canonical base / 공식 기준점

- canonical main after RTIO-R3 implementation merge:
  `a7ed3f1fcf545fd01dcda020d808fd0f4b9d4294`
- RTIO parent Issue `#129` — **COMPLETED**
- RTIO-R3 Issue `#139` — **COMPLETED**
- RTIO-R3 PR `#141` — **MERGED**
- R3 implementation/evidence exact head:
  `1b1e4031bfc6df727afaaf7e5fc432e6379b5a32` — **28/28 SUCCESS**
- R3 validation-record successor:
  `eb353f074c92568fa5ec3a218cf522b3562ec2bd` — **28/28 SUCCESS**
- durable validation: `evidence/RTIO_R3_VALIDATION.md`
- dedicated artifact ID: `11060346157`
- artifact ZIP SHA:
  `26c5f34f9d95ab874895ba2ac68ff67e84d46054b477c950ce096c7a5225b7d1`
- permanent workflow count at validated RTIO state: **28**

## Inherited authority / 상속 권한

REC-R0 inherits:

```text
ATCM:
immutable content-addressed audio assets
→ accepted audio tracks/clips
→ source-bound audio Preview / explicit Accept

MRAM:
accepted routing + native mixer automation
→ deterministic routed audio

RTIO:
accepted routed revision
→ provenance-bound realtime execution plan
→ deterministic backend/callback/transport lifecycle
→ exact frame cursors + latency/dropout metrics
→ Browser runtime truth
```

REC-R0 must introduce the **input direction** without bypassing those authority boundaries.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground existing output and asset contracts

Inspect at minimum:

- `src/musica/realtime_engine.py`;
- `src/musica/realtime_callback.py`;
- `src/musica/realtime_transport.py`;
- RTIO R0/R1/R2/R3 schemas, tests and validation records;
- `src/musica/audio_assets.py`;
- native audio asset/material/edit contracts;
- Project object store and export/import integrity logic;
- existing source-rate/no-resampling validation.

Identify which RTIO concepts can be reused generically and which must remain output-specific.

### 2. Freeze input backend capability v0

Define one explicit deterministic input capability, e.g. a simulated test input backend, binding:

- backend/input-device ID;
- classification = deterministic/simulated test input;
- supported sample rates;
- supported channel counts;
- supported block sizes;
- sample format;
- nominal/configured latency metadata if applicable;
- deterministic flag;
- host-native-input-claimed = false.

Do not infer microphone semantics from output backend capability.

### 3. Freeze capture plan v0

A derived, non-canonical capture plan should bind:

- exact Project ID and accepted revision ID;
- exact input backend capability SHA;
- explicit sample rate/channels/block size/sample format;
- requested capture duration/frame limit where bounded;
- start frame = zero-based capture cursor;
- block/final-block policy;
- no-resampling policy;
- capture-plan version + self-hash;
- authority flags showing capture runtime/payload are not canonical.

### 4. Freeze capture lifecycle

Prefer an explicit lifecycle such as:

```text
CLOSED
→ OPEN
→ READY
→ CAPTURING
→ STOPPED
→ FINALIZED
→ CLOSED
```

or a smaller equivalent if every transition is unambiguous.

Illegal transitions must fail closed.

`FINALIZED` in R0 may mean only a completed derived capture payload/report; it must **not** mean accepted Project media.

### 5. Exact capture frame progression

Capture cursor authority must be exact frames, not wall clock.

For each block/callback record:

- callback/block index;
- requested start frame;
- requested frame count;
- captured frame count;
- end frame;
- status;
- optional failure flag.

Contiguous normal capture must prove exact cursor progression.

### 6. Deterministic simulated input source

Use a source whose PCM bytes are deterministic and independently inspectable.

Prefer either:

- deterministic generated PCM fixture; or
- immutable fixture bytes with declared SHA.

The capture engine must not silently reinterpret channel/rate/sample-format semantics.

### 7. Failure and dropout instrumentation

If the callback/input contract supports fault injection, freeze bounded deterministic cases such as:

- ERROR;
- SHORT_FILL;
- LATE/dropout-equivalent.

Report requested vs captured frames and failure counters explicitly.

Do not infer physical-device xruns from simulated failures.

### 8. Fail-closed configuration matrix

Reject at minimum:

- unsupported sample rate;
- unsupported channel count;
- unsupported block size;
- invalid frame limit;
- malformed capability/plan hash;
- source-rate mismatch under no-resampling policy where applicable;
- illegal lifecycle transition;
- callback index/frame cursor mismatch;
- invalid failure-injection index.

### 9. Preserve accepted authority

Across all R0 capture runs:

> **accepted Project HEAD must remain unchanged.**

Explicitly prove captured PCM bytes, capture plan, callbacks, metrics and report are derived/non-canonical.

Do not call audio-asset import or audio edit Accept as part of R0 capture authority.

### 10. Repeat/reopen evidence

Generate independent evidence A/B and require byte equality where deterministic.

Fresh project reopen/rebuild should reproduce:

- capture plan;
- deterministic input source identity;
- callback/block trace;
- captured payload;
- capture report;
- accepted source binding.

Runtime lifecycle state itself should not be persisted as creative state.

### 11. Dedicated evidence and permanent gate

Add a dedicated REC-R0 workflow without weakening the existing **28** permanent gates.

Expected total: **29** permanent workflows.

Evidence artifact should include at minimum:

- input capability;
- capture plan;
- normal capture trace/payload/report;
- bounded failure trace/payload/report if supported;
- invalid-config/lifecycle results;
- project archive or source-binding proof where needed;
- proof record;
- contract hash inventory;
- deterministic manifest.

### 12. Promotion

REC-R0 promotion requires:

- implementation/evidence complete;
- dedicated REC-R0 gate green;
- all 29 workflows green on exact implementation/evidence head;
- independent artifact digest/manifest/hash inspection;
- durable `evidence/REC_R0_VALIDATION.md`;
- all 29 workflows green again on validation successor;
- expected-head squash merge;
- Issue #143 completed;
- separate state-only closure to REC-R1.

## REC-R0 non-goals / 비목표

Do not implement or claim in REC-R0:

- accepted recording placement;
- direct capture-to-track mutation;
- Browser recording UI;
- live input monitoring;
- take/comp management;
- punch recording;
- host-native microphone/line input;
- measured host-native input latency;
- resampling;
- plugin hosting/PDC;
- sidechains;
- generalized commercial recording readiness.

## Maximum intended REC-R0 outcome

> **MUSICA can deterministically capture a bounded simulated input source through an explicit provenance-bearing capture plan/runtime with exact frame progression and fail-closed configuration/lifecycle semantics while capture bytes and runtime state remain derived and cannot directly become accepted creative state.**

This remains a target claim until REC-R0 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
