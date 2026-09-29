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

Validated MRAM rungs:

```text
MRAM-R0 routing contracts + deterministic graph lowering      VALIDATED
MRAM-R1 trusted routing Preview→Accept + routed mixer         VALIDATED
MRAM-R2 track/routing-node gain/pan automation mapping        VALIDATED
MRAM-R3 Browser routing/automation + restart/reopen           VALIDATED
```

Canonical MRAM-R3 merge/main:

> **`5fb3796160d95cd11ad0332b23c67e65bd948e08`**

## Current commercial-workstation mission

Parent Issue `#129` — **Real-Time Audio Engine & Device Foundation v0 — OPEN**

Current rung sequence:

```text
RTIO-R0 realtime execution contracts + simulated backend      VALIDATED
→ RTIO-R1 bounded callback engine + backend adapter           CURRENT
→ RTIO-R2 transport + latency/dropout instrumentation
→ RTIO-R3 Studio/Browser runtime inspection + restart
→ parent #129 bounded closure evaluation
```

## RTIO-R0 — validated realtime contract/simulated backend substrate

Issue `#130` — **COMPLETED**

Implementation PR `#132` — **MERGED**

Canonical implementation merge/main:

> **`c6857700eb599a453ef3e99619c0f4ef8243a783`**

Durable validation:

- `evidence/RTIO_R0_VALIDATION.md`
- implementation/evidence exact head:
  `f597c441e0b2586789b7c5f06d802ed0c9298f17` — **25/25 permanent workflows SUCCESS**
- validation-record successor exact head:
  `6cd85303a17bed6f10bb200e6074e991f415a77c` — **25/25 SUCCESS**
- dedicated workflow: **RTIO-R0 Realtime Simulated Backend Evidence**
- dedicated run: `36548047238` — **SUCCESS**
- artifact ID: `11023801193`
- artifact ZIP SHA-256:
  `8765ec2e24c9fb081f1aadd74e7861aeccffea00194b638b9d0a5204f7920456`
- artifact ZIP size: **31,187 bytes**
- manifest payloads: **11/11 exact SHA-256 + byte size PASS**
- exact Git contract/source/test/workflow inventory: **9/9 PASS**
- persisted project object store: **16/16 object hashes PASS**
- realtime plan self-hash:
  `29566a48c8e8a9c20ac03c45ca0b499747975aa88d386ab3a3956d0510d0b203`
- normal run report self-hash:
  `4ec3fd23d6c0f96fb67b52907559095f8daf5a1cfc1746fd3226a8d8316bb642`
- forced-xrun report self-hash:
  `5d5b2d4c4376e43660d34929d8e29febda4e6af341f907f60fa03f402d2eddc5`

### Validated RTIO-R0 behavior

RTIO-R0 establishes:

- explicit simulated backend capability contract;
- exact accepted revision/Blueprint/audio/routing/automation source binding;
- explicit sample rate, stereo channel and block-size configuration;
- inherited exact source-rate match / no-resampling policy;
- derived/non-canonical realtime execution plan;
- strict `CLOSED → OPEN → RUNNING → STOPPED → CLOSED` lifecycle;
- deterministic fixed-block scheduling;
- zero-based monotonic frame cursor;
- exact normal sink equivalence to routed mixer PCM payload;
- deterministic run report and block trace;
- runtime counters for blocks, frames, cursor, xrun count and simulated latency metadata;
- deterministic forced-xrun/dropout injection;
- fail-closed unsupported sample rate, source-rate mismatch, unsupported block size and invalid xrun index;
- accepted Project HEAD unchanged across realtime execution;
- export/import reopen exactness for plan, block trace, sink and run report.

Evidence fixture:

```text
sample rate       = 8,000 Hz
channels          = 2
block size        = 256 frames
duration          = 96,000 frames
normal blocks     = 375 / 375
normal xrun count = 0
forced xrun       = block index 1
xrun blocks       = 374 / 375
xrun frames       = 95,744 / 96,000
```

Normal sink SHA-256:

`08aefbaf4a918446584245d2c7f4a79feede21c769cb8f2cacc510eeaece3c03`

Forced-xrun sink SHA-256:

`2180084d3a8b09fe229a259d8c2a9bc3a79d814136a1be82ef8cf5129ae659ac`

### Maximum validated RTIO-R0 claim

> **MUSICA can deterministically lower an accepted routed/automated project into an explicit realtime execution plan and execute it through a bounded simulated fixed-block backend with exact frame progression, lifecycle and runtime metrics while realtime state remains derived and accepted creative state remains unchanged.**

## Exact current rung / 현재 정확한 단계

> **Issue #133 — RTIO-R1: Bounded Callback Engine & Host-Backend Adapter Boundary v0**

RTIO-R1 must consume the validated RTIO-R0 plan and introduce callback-driven execution semantics without creating a second audio source model or unsupported platform-device claim.

Required direction:

```text
accepted routed+automated revision
→ RTIO-R0 realtime plan
→ callback engine / exact frame cursor
→ backend adapter callback
→ output buffer + callback metrics
≠ Project authority
```

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
- sidechains;
- generalized commercial realtime readiness.

## Exact next phase / 다음 단계

> **Implement Issue #133 from canonical main `c6857700eb599a453ef3e99619c0f4ef8243a783`: define callback request/response and backend-adapter contracts, make the callback engine consume the existing RTIO-R0 plan with exact cursor/final-block/error semantics, prove deterministic callback-harness execution and accepted-HEAD invariance, then promote through a dedicated RTIO-R1 permanent gate.**

See `memory/NEXT_ACTION.md` for exact execution order.

**Repository evidence remains authoritative over conversation/model memory.**
