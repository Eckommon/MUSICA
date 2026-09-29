# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**RTIO-R2 — EXACT-FRAME TRANSPORT & LATENCY/DROPOUT INSTRUMENTATION v0**

Issue `#136` — **OPEN**

Parent mission: Issue `#129` — **Real-Time Audio Engine & Device Foundation v0 — OPEN**

RTIO-R1 Issue `#133` is validated, merged and completed.

Do **not** add microphone input, recording, monitoring, plugin hosting, resampling, platform-native latency claims or realtime Browser control in R2.

## Canonical base / 공식 기준점

- canonical main after RTIO-R1 implementation merge:
  `310112b4d458f0a7cf120c7dcee1aab34bbbbdea`
- parent Issue `#129` — **OPEN**
- RTIO-R1 Issue `#133` — **COMPLETED**
- RTIO-R1 PR `#135` — **MERGED**
- R1 implementation/evidence head:
  `c0ce95fef4ec1990311dc3dd0305e24fe793eb43` — **26/26 SUCCESS**
- R1 validation-record successor:
  `80e30249891715144ee0d84d9c8a269e48351bfe` — **26/26 SUCCESS**
- durable validation: `evidence/RTIO_R1_VALIDATION.md`
- dedicated artifact ID: `11030046866`
- artifact ZIP SHA:
  `14c58c4eb9f68bdadb189d6c59c61b1951f89a2055327ccc5bd699b8177c0077`
- permanent workflow count at validated R1 state: **26**

## Inherited authority / 상속 권한

R2 inherits:

```text
M2 Project Engine:
accepted revision is creative authority

MRAM:
accepted routed + automated audio
→ deterministic routed PCM semantics

RTIO-R0:
provenance-bound realtime execution plan
→ exact frame/block source semantics

RTIO-R1:
callback engine
→ exact callback request/response frame ranges
→ deterministic backend-adapter boundary
→ callback lifecycle/error metrics
```

R2 must add transport and observability without creating a second source model or runtime write-back path.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground R0/R1 execution contracts

Inspect at minimum:

- `src/musica/realtime_engine.py`;
- `src/musica/realtime_callback.py`;
- RTIO-R0/R1 schemas/tests/evidence;
- `evidence/RTIO_R0_VALIDATION.md`;
- `evidence/RTIO_R1_VALIDATION.md`.

Freeze which state belongs to accepted plan, callback engine, transport and metrics.

### 2. Define transport contract v0

At minimum define:

- transport state;
- exact zero-based playhead frame;
- command sequence/index;
- command kind;
- requested target frame where applicable;
- before/after playhead;
- source realtime-plan SHA;
- status/error code;
- derived/non-canonical authority flag.

Prefer a small state model such as:

```text
STOPPED
→ PLAYING
→ STOPPED
→ END_OF_STREAM
```

with exact legal transitions.

### 3. Freeze play semantics

Play must:

- start from the current exact playhead;
- bind the callback engine to that frame;
- preserve exact source plan identity;
- define whether callback index resets per play segment;
- never infer position from wall-clock time.

### 4. Freeze stop semantics

Prove explicit stop:

- before first callback if allowed or fail closed;
- mid-stream;
- at EOS;
- repeated stop behavior;
- exact final playhead/cursor.

### 5. Freeze seek semantics

Define exact seek behavior:

- valid frame range;
- whether seek is legal only while stopped;
- whether seek while playing fails closed in v0;
- callback cursor/index reset policy;
- exact first callback range after seek;
- seek-to-EOS behavior;
- out-of-range/negative seek fail closed.

Do not implement ambiguous async seek behavior.

### 6. Transport ↔ callback cursor invariant

At every callback boundary, prove the relationship among:

- transport playhead;
- callback requested start frame;
- callback end frame;
- engine frame cursor;
- next transport playhead.

Any mismatch must fail closed.

### 7. Latency metadata contract

Expose deterministic metadata that clearly separates:

- configured block/buffer size;
- adapter nominal output latency frames;
- reported runtime latency fields, if any;
- whether values are simulated, configured or host-observed;
- no wall-clock guarantee flag.

Do not label simulated/configured latency as measured device latency.

### 8. Dropout/xrun instrumentation

Carry forward R0/R1 error semantics and expose at least:

- callback count;
- requested frames;
- delivered frames;
- error count;
- short-fill count;
- late count;
- xrun/dropout-equivalent count;
- transport discontinuity/seek count;
- final playhead;
- final callback cursor.

Provide deterministic forced paths.

### 9. Deterministic transport scenarios

Evidence should cover at minimum:

1. play from frame 0 to EOS;
2. stop before EOS;
3. seek to exact middle frame then play to EOS;
4. multiple stop/seek/play segments if contract supports them;
5. forced ERROR/SHORT_FILL/LATE/dropout accounting;
6. invalid transition/seek paths blocked;
7. exact repeated trace/sink/metrics equality.

### 10. Authority invariant

Prove accepted HEAD equality across all transport operations:

```text
open
→ seek
→ play
→ callbacks
→ stop
→ seek
→ play
→ EOS
→ close
```

Transport, playhead, adapter and metrics remain derived/non-canonical.

### 11. Fresh reopen proof

Export/import or fresh reopen must regenerate the same:

- source realtime plan;
- valid transport behavior;
- transport trace;
- callback ranges;
- sink;
- latency/dropout metrics.

### 12. Dedicated evidence and permanent gate

Add a dedicated RTIO-R2 workflow without weakening the existing **26** gates.

Expected total after R2: **27 permanent workflows**.

Evidence should include transport contract/trace, callback trace, latency metadata, normal/failure sink, metrics, invalid transition results, accepted HEAD invariant, reopen exactness and contract hash inventory.

### 13. Promotion

RTIO-R2 promotion requires:

- implementation/evidence complete;
- dedicated RTIO-R2 gate green;
- all 27 workflows green on exact evidence head;
- independent artifact inspection;
- durable validation;
- all 27 workflows green again on validation successor;
- expected-head squash merge;
- Issue #136 completed;
- separate state-only closure to RTIO-R3.

## RTIO-R2 non-goals

Do not implement or claim:

- microphone/line input;
- recording/monitoring;
- host-native ASIO/CoreAudio/WASAPI latency guarantees;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- resampling;
- realtime Browser control;
- mastering;
- commercial realtime readiness.

## Successor after R2

If R2 validates cleanly, exact next rung:

> **RTIO-R3 — Studio/Browser runtime inspection + restart/reopen lifecycle over the validated realtime/transport substrate, followed by parent Issue #129 bounded closure evaluation.**

## Maximum intended R2 outcome

> **MUSICA can control its provenance-bound callback engine through a bounded exact-frame transport and report deterministic latency/xrun/dropout instrumentation while transport/runtime state remains derived and accepted creative state remains unchanged.**

This remains a target claim until R2 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
