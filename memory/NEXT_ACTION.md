# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**RTIO-R0 — REALTIME EXECUTION CONTRACTS & DETERMINISTIC SIMULATED BACKEND v0**

Issue `#130` — **OPEN**

Parent mission: Issue `#129` — **Real-Time Audio Engine & Device Foundation v0 — OPEN**

Mixer Routing & Automation Foundation Issue `#115` is now **COMPLETED** after MRAM-R0→R3 validation and explicit parent closure evaluation.

Do **not** start recording, microphone input, monitoring, plugin hosting, platform-native backend claims or resampling in R0.

## Canonical base / 공식 기준점

- canonical main after MRAM-R3 implementation merge:
  `5fb3796160d95cd11ad0332b23c67e65bd948e08`
- MRAM parent Issue `#115` — **COMPLETED**
- MRAM-R3 Issue `#126` — **COMPLETED**
- MRAM-R3 PR `#128` — **MERGED**
- R3 implementation/evidence head:
  `68250b792ea8ecf773bfd92a16c8866efb4ef2b5` — **24/24 SUCCESS**
- R3 validation-record successor:
  `a68b16531df6b8ecca61d7504c6977ca88e5408f` — **24/24 SUCCESS**
- durable validation: `evidence/MRAM_R3_VALIDATION.md`
- dedicated artifact ID: `11016528257`
- artifact ZIP SHA:
  `e56c11505cf50b410b74461bdf0bc9a2fb88de31d13a04dbe4b4ad3c54d58938`
- permanent workflow count at validated R3 state: **24**

## Inherited authority / 상속 권한

RTIO-R0 inherits:

```text
ATCM:
accepted audio assets/tracks/clips/static mixer

MRAM:
accepted routing DAG + sends
accepted native track/node gain/pan automation
deterministic routed mixer
truthful Browser/Studio projection
restart/reopen exactness

M2 Project Engine:
accepted revision is creative authority
```

The realtime execution plan, block scheduler, backend instance, sink bytes, clocks/cursors and metrics must remain derived/non-canonical.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground existing render/signal-flow contracts

Inspect at minimum:

- `src/musica/routed_mixer.py`;
- `src/musica/native_mixer_automation.py`;
- `src/musica/routing_contracts.py`;
- accepted project/revision/hash utilities;
- Studio audio/audition paths;
- MRAM-R1/R2/R3 durable validation records;
- current sample-rate/no-resampling assumptions.

Freeze what can be reused and what must be a new realtime-only derived layer.

### 2. Define realtime execution plan v0

The plan must bind at least:

- plan version/compiler/runtime ID;
- exact project ID and accepted revision ID;
- Blueprint SHA;
- audio material SHA;
- routing material SHA;
- automation material SHA;
- backend ID/capability version;
- sample rate;
- output channel count;
- block size in frames;
- project duration/total frame count;
- transport start frame;
- no-resampling policy;
- exact execution/scheduling policy;
- self-hash.

The plan is **derived_noncanonical**.

### 3. Define backend capability/configuration contracts

Create explicit typed contracts for:

- backend identity;
- supported sample rates;
- supported channel counts;
- supported block-size range/set;
- latency metadata availability;
- deterministic/simulated vs host-native classification.

Reject unsupported configurations rather than coercing them silently.

### 4. Implement deterministic simulated output backend

Implement an in-process backend whose behavior is fully controllable in tests.

Required lifecycle:

```text
CLOSED
→ OPEN
→ RUNNING
→ STOPPED
→ CLOSED
```

Define exact allowed/blocked transitions.

The backend should accept fixed-size stereo float/PCM blocks or another explicitly frozen representation and persist/accumulate deterministic sink output for evidence.

### 5. Implement fixed-block scheduler and frame cursor

Freeze:

- zero-based frame cursor;
- block start/end semantics;
- final partial-block policy;
- transport start/stop behavior;
- exact total frames rendered;
- behavior after end-of-project;
- no hidden wall-clock authority.

For the simulated backend, block scheduling should be deterministic.

### 6. Connect accepted routed audio to block execution

Reuse accepted routed/native automation semantics instead of implementing a second mix engine.

Preferred bounded strategy:

- derive exact routed PCM/float source from the accepted revision;
- expose it through the realtime block scheduler;
- prove block concatenation corresponds exactly to the declared source/render policy.

If a streaming implementation is introduced, it must be mathematically/evidentially equivalent to the existing validated routed mixer semantics.

### 7. Runtime metrics and xrun/dropout instrumentation

Expose at least:

- blocks requested/written;
- frames requested/written;
- current frame cursor;
- underrun/dropout/xrun count;
- configured/backend latency metadata;
- lifecycle state;
- last error/failure reason.

Provide a deterministic test-only mechanism to force an xrun/dropout condition and prove it increments/reporting exactly without mutating creative state.

### 8. No-resampling and invalid-config fail closed

Reject at minimum:

- unsupported sample rate;
- unsupported output channel count;
- unsupported block size;
- source/backend sample-rate mismatch under v0 no-resampling;
- missing/corrupt source asset;
- invalid routing/native automation source state;
- stale/nonexistent revision;
- illegal lifecycle transition.

Do not silently convert sample rates or channel topology.

### 9. Authority boundary proof

Prove:

```text
accepted HEAD before realtime run
== accepted HEAD during open/start/run/stop
== accepted HEAD after close
```

No runtime metric, sink buffer or transport cursor may write back into the accepted Blueprint/project revision.

### 10. Deterministic repeat and reopen proof

For the simulated backend, prove independent runs over exact source/config produce:

- identical realtime plan;
- identical block sequence/frame ranges;
- identical sink output hash;
- identical deterministic metrics except explicitly excluded runtime-only identifiers.

Then fresh reopen of the project must produce the same exact source binding and plan.

### 11. Dedicated evidence and permanent gate

Add a dedicated RTIO-R0 workflow without weakening the existing **24** gates.

Expected total after R0: **25 permanent workflows**.

Evidence should include:

- source/plan/config hashes;
- block trace;
- sink output hash/bytes;
- lifecycle trace;
- runtime metrics;
- forced xrun/dropout proof;
- invalid configuration results;
- accepted HEAD invariant;
- reopen exactness;
- contract/source/test/workflow hash inventory.

### 12. Promotion

RTIO-R0 promotion requires:

- implementation/evidence complete;
- dedicated RTIO-R0 gate green;
- all 25 workflows green on exact evidence-bearing head;
- independent artifact digest/manifest/hash inspection;
- durable RTIO-R0 validation record;
- all 25 workflows green again on validation-record successor head;
- expected-head squash merge;
- Issue #130 completed;
- separate state-only closure to RTIO-R1.

## RTIO-R0 non-goals / 비목표

Do not implement or claim in R0:

- real ASIO/CoreAudio/WASAPI output;
- low-latency wall-clock guarantees;
- microphone/line input;
- recording/monitoring;
- plugin hosting;
- plugin-delay compensation;
- realtime Browser control;
- sample-rate conversion;
- sidechains;
- commercial realtime readiness.

## Maximum intended R0 outcome

> **MUSICA can deterministically lower an accepted routed/automated project into an explicit realtime execution plan and execute it through a bounded simulated fixed-block backend with exact frame progression, lifecycle and runtime metrics while realtime state remains derived and accepted creative state remains unchanged.**

This remains a target claim until RTIO-R0 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
