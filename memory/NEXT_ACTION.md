# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**RTIO-R1 — BOUNDED CALLBACK ENGINE & HOST-BACKEND ADAPTER BOUNDARY v0**

Issue `#133` — **OPEN**

Parent mission: Issue `#129` — **Real-Time Audio Engine & Device Foundation v0 — OPEN**

RTIO-R0 Issue `#130` is validated, merged and completed.

Do **not** add microphone input, recording, monitoring, plugin hosting, resampling, platform-specific low-latency claims or realtime Browser control in R1.

## Canonical base / 공식 기준점

- canonical main after RTIO-R0 implementation merge:
  `c6857700eb599a453ef3e99619c0f4ef8243a783`
- parent Issue `#129` — **OPEN**
- RTIO-R0 Issue `#130` — **COMPLETED**
- RTIO-R0 PR `#132` — **MERGED**
- R0 implementation/evidence head:
  `f597c441e0b2586789b7c5f06d802ed0c9298f17` — **25/25 SUCCESS**
- R0 validation-record successor:
  `6cd85303a17bed6f10bb200e6074e991f415a77c` — **25/25 SUCCESS**
- durable validation: `evidence/RTIO_R0_VALIDATION.md`
- dedicated artifact ID: `11023801193`
- artifact ZIP SHA:
  `8765ec2e24c9fb081f1aadd74e7861aeccffea00194b638b9d0a5204f7920456`
- permanent workflow count at validated R0 state: **25**

## Inherited authority / 상속 권한

R1 inherits:

```text
M2 Project Engine:
accepted revision is creative authority

MRAM:
accepted audio/routing/native automation
→ deterministic routed PCM semantics

RTIO-R0:
provenance-bound realtime execution plan
→ deterministic fixed-block scheduler
→ simulated output backend
→ lifecycle/runtime/xrun metrics
```

R1 must make execution callback-driven without replacing these source semantics.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground RTIO-R0 contracts and runtime

Inspect:

- `src/musica/realtime_engine.py`;
- RTIO-R0 schemas/tests/evidence;
- `src/musica/routed_mixer.py`;
- project revision/hash utilities;
- `evidence/RTIO_R0_VALIDATION.md`.

Freeze which state belongs to plan, callback engine, backend adapter and runtime metrics.

### 2. Define callback request/response contracts

At minimum define:

- callback sequence/index;
- requested start frame;
- requested frame count;
- end frame exclusive;
- source plan SHA;
- transport state;
- response frame count;
- response payload identity;
- callback status;
- error/short-fill condition.

No callback request may infer source identity from wall-clock time.

### 3. Define host-backend adapter boundary

The adapter should expose:

- backend/capability identity;
- open/close;
- callback registration;
- start/stop;
- callback buffer request;
- latency metadata access where available;
- error/xrun notification.

Provide a deterministic test adapter/harness. Host-native implementations remain optional and unclaimed unless directly evidenced.

### 4. Implement callback-driven engine

The callback engine must:

- consume the exact RTIO-R0 execution plan;
- own a monotonic frame cursor;
- answer callback requests with exact source frames;
- preserve the R0 no-resampling policy;
- define exact end-of-stream behavior;
- never mutate accepted Project state.

### 5. Freeze final-block and stop semantics

Prove:

- normal full-size callbacks;
- final partial callback when duration is not divisible by block size;
- callback after end-of-stream behavior;
- explicit stop before project end;
- restart policy if supported;
- illegal lifecycle calls fail closed.

### 6. Callback failure instrumentation

Provide deterministic test paths for:

- forced callback error;
- short-fill;
- late/xrun-equivalent notification;
- invalid frame request or cursor mismatch.

Metrics must distinguish requested vs delivered frames and error counts.

### 7. Deterministic callback-harness proof

For an identical plan/config, independent runs should reproduce:

- callback request sequence;
- frame ranges;
- response payload hashes;
- output sink bytes;
- deterministic metrics.

The concatenated successful callback payload must equal the RTIO-R0 normal source/sink bytes when no failure is injected.

### 8. Authority invariant

Prove accepted HEAD equality across:

```text
open
→ start
→ callback execution
→ stop
→ close
```

Callback buffers, adapter state and metrics remain derived/non-canonical.

### 9. Restart/reopen proof

Fresh project reopen should regenerate the same source binding and callback plan/harness result.

### 10. Dedicated evidence and permanent gate

Add a dedicated RTIO-R1 workflow without weakening the existing **25** gates.

Expected total after R1: **26 permanent workflows**.

Evidence should include callback contracts, callback trace, normal/failure sink, metrics, invalid lifecycle results, accepted HEAD invariant, reopen exactness and contract hash inventory.

### 11. Promotion

RTIO-R1 promotion requires:

- implementation/evidence complete;
- dedicated RTIO-R1 gate green;
- all 26 workflows green on exact evidence head;
- independent artifact inspection;
- durable validation;
- all 26 workflows green again on validation successor;
- expected-head squash merge;
- Issue #133 completed;
- separate state-only closure to RTIO-R2.

## RTIO-R1 non-goals

Do not implement or claim:

- microphone/line input;
- recording/monitoring;
- host-native low-latency performance;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- resampling;
- realtime Browser control;
- commercial realtime readiness.

## Maximum intended R1 outcome

> **MUSICA can execute its provenance-bound realtime plan through a bounded callback-driven output engine with exact frame cursor, lifecycle and error accounting while callback/backend runtime remains derived and cannot reverse-author accepted creative state.**

This remains a target claim until R1 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
