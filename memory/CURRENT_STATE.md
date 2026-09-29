# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → NATIVE AUDIO FOUNDATION VALIDATED → MIXER ROUTING & AUTOMATION FOUNDATION COMPLETED → REAL-TIME AUDIO ENGINE & DEVICE FOUNDATION IN PROGRESS**

Long-term governing target:

> **MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving its AI-native authority, inspectability, reproducibility and programmability.**

This remains a product target, not a claim that MUSICA is already a complete commercial DAW.

## Completed bounded foundations

### Audio Track / Clip / Mixer Foundation v0

Parent Issue `#95` — **COMPLETED**

Validated ATCM rungs: R0→R4.

### Mixer Routing & Automation Foundation v0

Parent Issue `#115` — **COMPLETED**

Validated MRAM rungs: R0→R3.

Canonical MRAM-R3 merge/main:

> **`5fb3796160d95cd11ad0332b23c67e65bd948e08`**

## Current commercial-workstation mission

Parent Issue `#129` — **Real-Time Audio Engine & Device Foundation v0 — OPEN**

Current rung sequence:

```text
RTIO-R0 realtime execution contracts + simulated backend      VALIDATED
→ RTIO-R1 bounded callback engine + backend adapter           VALIDATED
→ RTIO-R2 exact-frame transport + latency/dropout metrics     CURRENT
→ RTIO-R3 Studio/Browser runtime inspection + restart
→ parent #129 bounded closure evaluation
```

## RTIO-R0 — validated realtime contract/simulated backend substrate

Issue `#130` — **COMPLETED**

Implementation PR `#132` — **MERGED**

Canonical implementation merge/main:

> **`c6857700eb599a453ef3e99619c0f4ef8243a783`**

Durable validation: `evidence/RTIO_R0_VALIDATION.md`.

RTIO-R0 established the provenance-bound realtime execution plan, deterministic fixed-block simulated backend, exact frame cursor, lifecycle, xrun/dropout simulation, sink equivalence to routed PCM, accepted-HEAD invariance and reopen exactness.

## RTIO-R1 — validated callback engine + host-backend adapter boundary

Issue `#133` — **COMPLETED**

Implementation PR `#135` — **MERGED**

Canonical implementation merge/main:

> **`310112b4d458f0a7cf120c7dcee1aab34bbbbdea`**

Durable validation:

- `evidence/RTIO_R1_VALIDATION.md`
- implementation/evidence exact head:
  `c0ce95fef4ec1990311dc3dd0305e24fe793eb43` — **26/26 permanent workflows SUCCESS**
- validation-record successor:
  `80e30249891715144ee0d84d9c8a269e48351bfe` — **26/26 SUCCESS**
- dedicated workflow: **RTIO-R1 Callback Engine Evidence**
- dedicated run: `36560788431` — **SUCCESS**
- artifact ID: `11030046866`
- artifact ZIP SHA-256:
  `14c58c4eb9f68bdadb189d6c59c61b1951f89a2055327ccc5bd699b8177c0077`
- artifact ZIP size: **40,275 bytes**
- manifest payloads: **13/13 exact SHA-256 + byte size PASS**
- exact Git contract/source/test/workflow inventory: **10/10 PASS**
- persisted project object store: **16/16 object hashes PASS**
- realtime plan self-hash:
  `042a3c6e144025d89c7668496d8371c60a8000a19764f7868d2e2e1afcfa9fc0`
- normal callback report self-hash:
  `f44c4f74131dd43d2b0cf04bd5dd2473c61e0b77e3b5a9c78e0af6bf97b68d93`
- failure callback report self-hash:
  `2f67a2fa440757a0d0076b46798f0ec30a64f3158d46952e2bb10463957b884e`
- early-stop report self-hash:
  `b2d18194402bb778833752de2f04e9f8e9745935f86338fee4ae7e900c3e9bfb`

### Validated RTIO-R1 behavior

RTIO-R1 establishes:

- explicit callback transaction contract over exact frame ranges;
- deterministic callback adapter capability and lifecycle;
- strict `CLOSED → OPEN → CALLBACK_REGISTERED → RUNNING → STOPPED → CLOSED`;
- exact monotonic frame cursor and callback index;
- final partial callback without padding;
- callback-after-EOS fail-closed behavior;
- fail-closed callback index/start-frame/frame-count mismatch;
- deterministic `ERROR`, `SHORT_FILL` and `LATE` instrumentation;
- exact requested vs delivered frame metrics;
- explicit early stop;
- deterministic repeat-exact callback trace, sink and run report;
- normal callback sink exact equality with RTIO-R0 source/sink;
- accepted Project HEAD unchanged across callback execution;
- fresh import/reopen exactness for plan, trace, sink and report;
- explicit non-claim of host-native ASIO/CoreAudio/WASAPI output.

Evidence fixture:

```text
sample rate       = 8,000 Hz
channels          = 2
duration          = 96,000 frames
normal block      = 1,024 frames
normal callbacks  = 94
final callback    = 768 frames
failure block     = 256 frames
failure callbacks = 375
ERROR             = 1
SHORT_FILL        = 1
LATE              = 1
```

Normal callback sink SHA-256:

`08aefbaf4a918446584245d2c7f4a79feede21c769cb8f2cacc510eeaece3c03`

Failure callback sink SHA-256:

`97cbe0a93c0092c939ff9f25a86e93ad4ef740354f124803509a02671685f8bd`

### Maximum validated RTIO-R1 claim

> **MUSICA can execute its provenance-bound realtime plan through a bounded callback-driven output engine with exact frame cursor, lifecycle, final-block behavior and deterministic failure accounting while callback/backend runtime remains derived and cannot reverse-author accepted creative state.**

## Exact current rung / 현재 정확한 단계

> **Issue #136 — RTIO-R2: Exact-Frame Transport & Latency/Dropout Instrumentation v0**

RTIO-R2 must add a bounded transport state machine and deterministic runtime observability on top of the validated RTIO-R0/R1 execution stack.

Required direction:

```text
accepted routed+automated revision
→ RTIO-R0 realtime plan
→ RTIO-R1 callback engine
→ exact-frame transport state
→ play / stop / seek / EOS
→ callback requests
→ latency/xrun/dropout metrics
≠ Project authority
```

The transport layer must not infer canonical creative state from wall-clock/runtime state.

## Current important non-claims

Until separately validated, do not claim:

- real ASIO/CoreAudio/WASAPI device output;
- wall-clock low-latency guarantees;
- microphone/line input;
- recording/monitoring;
- take/comp management;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- sample-rate conversion;
- realtime Browser control;
- sidechains;
- generalized commercial realtime readiness.

## Exact next phase / 다음 단계

> **Implement Issue #136 from canonical main `310112b4d458f0a7cf120c7dcee1aab34bbbbdea`: define exact-frame transport command/state contracts, freeze play/stop/seek/EOS behavior and callback-cursor interaction, add deterministic latency/xrun/dropout instrumentation, prove accepted-HEAD invariance and reopen exactness, then promote through a dedicated RTIO-R2 permanent gate.**

See `memory/NEXT_ACTION.md` for exact execution order.

**Repository evidence remains authoritative over conversation/model memory.**
