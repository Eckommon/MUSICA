# RTIO-R2 Validation — Exact-Frame Transport & Latency/Dropout Instrumentation v0

## Scope

Issue #136 under parent Issue #129.

RTIO-R2 advances the validated RTIO-R0/R1 realtime plan and callback boundary with a bounded exact-frame transport state machine. It adds explicit play/stop/seek/end-of-stream behavior, callback/transport cursor invariants, deterministic latency metadata and dropout/xrun-equivalent instrumentation while keeping transport, wall-clock state, sink bytes and metrics derived/non-canonical.

## Evidence-bearing implementation head

- exact implementation/evidence head: `cf4e9d3dba17d1ba130a66e5fd79b9a38d57db29`
- permanent workflow count: **27**
- exact-head result: **27/27 SUCCESS**
- dedicated workflow: **RTIO-R2 Exact-Frame Transport Evidence**
- dedicated run: `36592465888` — **SUCCESS**
- artifact ID: `11044417646`
- artifact name: `musica-rtio-r2-exact-frame-transport-evidence`
- artifact ZIP SHA-256: `372829e4ca4abe4b953a603164bd8f19c9d08cdbc4615d7f07abd7b3f7ab0337`
- artifact ZIP size: **60,025 bytes**

All 27 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The GitHub artifact-declared digest and byte size matched the independently downloaded ZIP exactly.

The artifact contains **18 manifest-declared payload files plus `manifest.json`**. All **18/18** payloads matched their declared SHA-256 and byte size.

Selected payload identities:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `realtime-plan.json` | `b706eeb04d8365d04c395534c7e004495529f53b21ad2eda4564598d81c4bd30` | 1,574 |
| `normal-transport-events.json` | `a330123c5c32a165151021fab0d767f08edf9602e7d3d14bd33f308f38478890` | 45,197 |
| `normal-callback-trace.json` | `3d8155f0534021134fc67fbbd4f48f9eb8856ea6d6ffa0f335e8acb0f4d2ffe9` | 62,351 |
| `normal-transport-report.json` | `f6840723137f632247fbde405d74e9f9daaa3a268f1a2d2541cfb0c72a8bae39` | 1,371 |
| `normal-sink.pcm` | `08aefbaf4a918446584245d2c7f4a79feede21c769cb8f2cacc510eeaece3c03` | 384,000 |
| `segmented-transport-events.json` | `4640f96f80b6cfe94413691a788503861cf82857682711c70afce0ec79551baf` | 92,517 |
| `segmented-callback-trace.json` | `d6e1a13c09ada2194338544084a9d645b9ab5bd97a4feeda2aba724cf5e7cf16` | 126,374 |
| `segmented-transport-report.json` | `51e8123b932bd3c334d34aad4fcac6f9cc355219e0578c7c8f5eb57663734e93` | 1,371 |
| `segmented-sink.pcm` | `76292fa4de6deb81c79992130a28dcfb00211da06e5ccbc79386b26e1797b087` | 195,072 |
| `failure-transport-events.json` | `cd4fdcf0e3cdb9b38a6fd3d8be0dd136a91f7af157e4367cc12962e7808ad70c` | 178,079 |
| `failure-callback-trace.json` | `c8958d20d2e49f10d4b7b7bcc8e6ceb9df6e240606237533c4857773909f09d3` | 248,269 |
| `failure-transport-report.json` | `14c08ac7a67be520222acb920883c19ba412003b790d225caf7a6ee1695aa718` | 1,371 |
| `failure-sink.pcm` | `97cbe0a93c0092c939ff9f25a86e93ad4ef740354f124803509a02671685f8bd` | 382,464 |
| `latency-metadata.json` | `fcc6c80a2eb5e237a3908cf9b246c642d60de39602f4acc643379ef636924985` | 197 |
| `invalid-transport-results.json` | `2e220f20d30d756743d181c77210d85050cfbcec0383334983fa40a37423726a` | 998 |
| `project.musica.zip` | `eacee8672fac3c3f1b6143ebd29abc33715f126cf253160cc130149a275481c2` | 33,455 |
| `proof.json` | `5efafb14be7c40aea28968e0a5e7a575905ce5034e305e141f32e9188041a3ef` | 1,047 |

The evidence contract/source/test/workflow inventory was independently compared with exact GitHub head `cf4e9d3...`. All **11/11** files matched both recorded SHA-256 and byte size.

The nested persisted project archive contains **16** content-addressed object files. All **16/16** independently matched the SHA-256 encoded in their object filename, and `refs/heads/main.json` points to the exact routed/native-automation evidence revision.

## Self-hash verification

Using MUSICA canonical JSON bytes, all self-hashed derived records independently recomputed exactly:

- realtime execution plan:
  `042a3c6e144025d89c7668496d8371c60a8000a19764f7868d2e2e1afcfa9fc0`
- normal transport report:
  `a912027823fc515467979c8cec4d270fa2cb781bb8fce0a1c1c7517ca020e963`
- segmented stop/seek/play transport report:
  `327a951629655238ce38957c1172156272cab973532f47b6c38adbb77b04f13a`
- failure-injection transport report:
  `d9895547a358e7b1d0c4d60293c890ff6d1d770baf0037bf084030083cc46470`

All declared hashes matched independent recomputation.

## Exact transport state model

The bounded validated runtime states are:

```text
STOPPED
→ PLAYING
→ STOPPED
→ PLAYING
→ END_OF_STREAM
```

with these frozen rules:

- `PLAY` is legal only from `STOPPED`;
- `STOP` is legal only from `PLAYING`;
- `SEEK` is legal only from `STOPPED` or `END_OF_STREAM`;
- seek while playing fails closed;
- EOS is terminal until an explicit seek;
- play at frame `duration_frames` fails closed until seeking away from EOS;
- playhead authority is the exact zero-based frame cursor, never wall-clock time;
- callback index resets to zero for every new play segment;
- frame identity does not reset: a segment begins at the exact current playhead.

Transport events and reports are explicitly runtime/derived and non-canonical.

## Normal play-to-EOS proof

Normal evidence uses:

```text
sample rate       = 8,000 Hz
channels          = 2
duration          = 96,000 frames
block size        = 1,024 frames
callbacks         = 94
transport events  = 96
final callback    = 768 frames
final playhead    = 96,000
final state       = END_OF_STREAM
```

The **96** transport events are exactly:

- 1 `PLAY`;
- 94 `CALLBACK`;
- 1 `EOS`.

The sink is byte-identical to the already validated RTIO-R1 normal callback sink:

- frames: **96,000**
- bytes: **384,000**
- SHA-256:
  `08aefbaf4a918446584245d2c7f4a79feede21c769cb8f2cacc510eeaece3c03`

This proves the transport does not introduce another audio/DSP interpretation.

## Stop → seek → play proof

The segmented evidence freezes an explicit discontinuity:

```text
PLAY from frame 0
→ callback 0:   0 → 256
→ callback 1: 256 → 512
→ callback 2: 512 → 768
→ STOP at frame 768
→ SEEK to frame 48,000
→ PLAY from frame 48,000
→ first new callback_index = 0
→ first new callback range = 48,000 → 48,256
→ play to EOS at 96,000
```

Metrics:

```text
play_count                      = 2
stop_count                      = 1
seek_count                      = 1
transport_discontinuity_count   = 1
callbacks_requested             = 191
frames_requested                = 48,768
frames_delivered                = 48,768
final_playhead                  = 96,000
final_state                     = END_OF_STREAM
```

The segmented trace contains **191 callback transactions** and **196 transport events**.

The output sink contains exactly the first 768 frames followed by source frames 48,000→96,000:

- delivered frames: **48,768**
- bytes: **195,072**
- SHA-256:
  `76292fa4de6deb81c79992130a28dcfb00211da06e5ccbc79386b26e1797b087`

This proves seek changes runtime source position explicitly without mutating or rewriting accepted creative state.

## Transport ↔ callback cursor invariant

For every callback, the transport verifies:

```text
transport playhead before callback
= callback requested start frame

callback requested end frame
= callback engine frame cursor after callback
= transport playhead after callback
```

Any mismatch fails closed.

After seek, a new RTIO-R1 callback engine segment is created from the exact playhead. The new callback index resets to **0**, while the requested start frame remains **48,000**, proving callback ordinal and timeline identity are separate explicit concepts.

## Latency metadata boundary

The validated latency payload is:

```text
configured_block_size_frames       = 1,024
nominal_output_latency_frames      = 0
nominal_source                     = simulated_backend_capability
host_observed_latency_available    = false
wall_clock_guarantee_claimed       = false
```

The nominal value is contract/configuration metadata from the deterministic simulated backend. It is **not** measured ASIO/CoreAudio/WASAPI device latency and does not support a low-latency wall-clock claim.

## Dropout/xrun-equivalent instrumentation proof

Failure evidence uses 256-frame callbacks and injects:

- ERROR at callback index **1**;
- SHORT_FILL at callback index **2**;
- LATE at callback index **3**.

Metrics are:

```text
callbacks_requested             = 375
frames_requested                = 96,000
frames_delivered                = 95,616
error_count                     = 1
short_fill_count                = 1
late_count                      = 1
xrun_dropout_equivalent_count   = 3
final_playhead                  = 96,000
final_callback_cursor           = 96,000
final_state                     = END_OF_STREAM
```

Timeline progression follows exact requested frame ranges even when delivered audio is empty/short. The sink therefore records delivered payload reality while the transport playhead preserves exact source-timeline progression.

Failure sink:

- frames: **95,616**
- bytes: **382,464**
- SHA-256:
  `97cbe0a93c0092c939ff9f25a86e93ad4ef740354f124803509a02671685f8bd`

This exactly matches the validated RTIO-R1 failure sink for the same injections.

## Fail-closed transition and input matrix

Independent evidence records all of the following as blocked:

- callback while stopped;
- stop while stopped;
- negative seek;
- seek beyond EOS;
- double play;
- seek while playing;
- finalize while playing;
- double stop;
- play at EOS without seeking away;
- failure-injection index outside the current play segment.

The R1 callback engine also gains only one backward-compatible extension:

> `initial_frame=0` default, with explicit range validation.

Existing R1 callers therefore preserve zero-frame behavior while R2 may construct a new segment at an exact stopped-state seek frame.

## Accepted authority invariant

Across normal, segmented, failure and reopen execution:

> **accepted Project HEAD remains unchanged**

The following remain derived/non-canonical:

```text
transport state
playhead
callback index
transport event trace
callback transactions
latency metadata
dropout/xrun metrics
sink payload
transport report
```

No runtime result may reverse-author accepted creative state.

## Repeat and reopen exactness

The dedicated evidence workflow independently generates evidence A and B and requires byte-level directory equality before upload.

Repeated execution reproduces exactly:

- normal plan/events/callback trace/sink/report;
- segmented events/callback trace/sink/report;
- failure events/callback trace/sink/report.

After fresh export/import reopen, the segmented scenario reproduces exactly:

- realtime plan;
- transport events;
- callback transactions;
- sink bytes;
- transport report;
- accepted source binding.

Project integrity is PASS after reopen.

## Proven bounded execution model

The maximum validated chain is:

```text
accepted routed+automated revision
→ RTIO-R0 provenance-bound realtime plan
→ RTIO-R2 exact-frame transport
→ RTIO-R1 callback engine per play segment
→ exact callback request/response ranges
→ derived output sink
→ deterministic latency/dropout metrics
```

The transport never derives frame identity from elapsed wall-clock time.

## Explicit non-claims

RTIO-R2 does not claim:

- host-native ASIO output;
- host-native CoreAudio output;
- host-native WASAPI output;
- measured or guaranteed wall-clock low latency;
- microphone/line input;
- recording/monitoring;
- take/comp workflows;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- sample-rate conversion;
- realtime Browser control;
- mastering;
- generalized commercial realtime readiness.

## Validation verdict

> **VALIDATED — EXACT-FRAME TRANSPORT & LATENCY/DROPOUT INSTRUMENTATION v0**

Maximum supported claim:

> **MUSICA can control its provenance-bound callback engine through a bounded exact-frame play/stop/seek/EOS transport and report deterministic configured latency plus xrun/dropout-equivalent instrumentation while runtime state remains derived and accepted creative state remains unchanged.**

Promotion remains conditional on all **27** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #136 completion and separate state-only closure to RTIO-R3.

Repository evidence remains authoritative over conversation/model memory.
