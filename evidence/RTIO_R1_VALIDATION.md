# RTIO-R1 Validation — Bounded Callback Engine & Host-Backend Adapter Boundary v0

## Scope

Issue #133 under parent Issue #129.

RTIO-R1 advances the validated RTIO-R0 realtime execution plan into a bounded callback-driven output boundary. It defines exact callback request/response transactions, a deterministic callback adapter lifecycle, monotonic frame-cursor semantics, partial-final-block handling, observable callback failures and reopen exactness while keeping callback/backend runtime derived and non-canonical.

## Evidence-bearing implementation head

- exact implementation/evidence head: `c0ce95fef4ec1990311dc3dd0305e24fe793eb43`
- permanent workflow count: **26**
- exact-head result: **26/26 SUCCESS**
- dedicated workflow: **RTIO-R1 Callback Engine Evidence**
- dedicated run: `36560788431` — **SUCCESS**
- artifact ID: `11030046866`
- artifact name: `musica-rtio-r1-callback-engine-evidence`
- artifact ZIP SHA-256: `14c58c4eb9f68bdadb189d6c59c61b1951f89a2055327ccc5bd699b8177c0077`
- artifact ZIP size: **40,275 bytes**

All 26 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The GitHub artifact declared digest and byte size matched the independently downloaded ZIP exactly:

- SHA-256: `14c58c4eb9f68bdadb189d6c59c61b1951f89a2055327ccc5bd699b8177c0077`
- bytes: **40,275**

The artifact contains **13 manifest-declared payload files plus `manifest.json`**. All **13/13** payloads matched their declared SHA-256 and byte size.

Selected payload identities:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `adapter-capability.json` | `71371bfe39a6bce62ad9288df35cf0cbf358369e010b36817aa0b657234eb6d4` | 289 |
| `callback-run-report.json` | `42619db244878cdaeb25b7be35fcd5d0507c01bfcb7b2e2291327d5342142002` | 1,106 |
| `callback-sink.pcm` | `08aefbaf4a918446584245d2c7f4a79feede21c769cb8f2cacc510eeaece3c03` | 384,000 |
| `callback-trace.json` | `3d8155f0534021134fc67fbbd4f48f9eb8856ea6d6ffa0f335e8acb0f4d2ffe9` | 62,351 |
| `failure-callback-run-report.json` | `0eb7802e2f6106cd1175c4578764c80577db4a37d7f86c2a6aee66878f70a4f1` | 1,108 |
| `failure-callback-sink.pcm` | `97cbe0a93c0092c939ff9f25a86e93ad4ef740354f124803509a02671685f8bd` | 382,464 |
| `failure-callback-trace.json` | `c8958d20d2e49f10d4b7b7bcc8e6ceb9df6e240606237533c4857773909f09d3` | 248,269 |
| `invalid-callback-results.json` | `75456139dc805c72ecb6cb577cc3aa3687994044102ca50bd752e44b8df51f0c` | 1,080 |
| `project.musica.zip` | `eacee8672fac3c3f1b6143ebd29abc33715f126cf253160cc130149a275481c2` | 33,455 |
| `proof.json` | `af0f10f4d9ed54dfa90fdc4f680ab42aeab4cd398894ddf1edfb0c32197d306a` | 1,026 |
| `realtime-plan.json` | `b706eeb04d8365d04c395534c7e004495529f53b21ad2eda4564598d81c4bd30` | 1,574 |

The evidence contract/source/test/workflow inventory was independently compared with exact GitHub head `c0ce95f...`. All **10/10** files matched both recorded SHA-256 and byte size.

## Self-hash verification

Using MUSICA canonical JSON bytes, all self-hashed derived records independently recomputed exactly:

- realtime execution plan:
  `042a3c6e144025d89c7668496d8371c60a8000a19764f7868d2e2e1afcfa9fc0`
- normal callback run report:
  `f44c4f74131dd43d2b0cf04bd5dd2473c61e0b77e3b5a9c78e0af6bf97b68d93`
- failure-injection callback run report:
  `2f67a2fa440757a0d0076b46798f0ec30a64f3158d46952e2bb10463957b884e`
- early-stop callback run report:
  `b2d18194402bb778833752de2f04e9f8e9745935f86338fee4ae7e900c3e9bfb`

All four declared hashes matched independent recomputation.

## Adapter capability boundary

The validated adapter capability is explicitly:

```text
adapter_id                 = musica-deterministic-callback-adapter-v0
classification             = deterministic_test_adapter
callback_model             = registered_pull_callback
deterministic              = true
supported failure modes    = ERROR, SHORT_FILL, LATE
host_native_device_claimed = false
```

This is a host-backend boundary contract and deterministic test adapter, not evidence of native ASIO/CoreAudio/WASAPI execution.

## Normal callback execution proof

Normal evidence uses:

```text
sample rate       = 8,000 Hz
channels          = 2
duration          = 96,000 frames
block size        = 1,024 frames
callback count    = 94
final callback    = 768 frames
final cursor      = 96,000
error count       = 0
short-fill count  = 0
late count        = 0
```

The first request is:

```text
callback_index = 0
start_frame    = 0
frame_count    = 1,024
end_exclusive  = 1,024
```

The final request is:

```text
callback_index = 93
start_frame    = 95,232
frame_count    = 768
end_exclusive  = 96,000
```

This proves explicit final partial callback semantics with no padding and exact end-of-stream closure.

The callback sink:

- payload SHA-256:
  `08aefbaf4a918446584245d2c7f4a79feede21c769cb8f2cacc510eeaece3c03`
- payload bytes: **384,000**
- delivered frames: **96,000**

matches the RTIO-R0 normal sink exactly, proving RTIO-R1 consumes the validated RTIO-R0 source semantics rather than inventing a second DSP/audio model.

## Callback lifecycle proof

The validated adapter lifecycle is exactly:

```text
CLOSED
→ OPEN
→ CALLBACK_REGISTERED
→ RUNNING
→ STOPPED
→ CLOSED
```

Illegal lifecycle requests fail closed.

Independently evidenced blocked paths include:

- request before RUNNING;
- start before callback registration;
- callback index mismatch;
- callback start-frame mismatch;
- callback requested-frame-count mismatch;
- callback after end-of-stream;
- invalid failure injection index;
- ERROR/SHORT_FILL overlap;
- invalid early-stop callback count;
- double close.

All invalid paths in `invalid-callback-results.json` report `blocked: true`.

## Failure instrumentation proof

Failure evidence uses 256-frame callbacks over the same 96,000-frame timeline:

- callback count: **375**
- ERROR injected at callback index 1;
- SHORT_FILL injected at callback index 2;
- LATE injected at callback index 3;
- error count: **1**
- short-fill count: **1**
- late count: **1**
- xrun-equivalent count: **3**
- requested frames: **96,000**
- delivered frames: **95,616**
- final frame cursor: **96,000**

The trace contains:

- **373** `OK` responses;
- **1** `ERROR`;
- **1** `SHORT_FILL`;
- exactly **1** callback marked late.

The timeline cursor still advances by requested timeline ranges, while delivered audio bytes reflect the forced failure/short-fill conditions. The failure sink is therefore intentionally different:

- SHA-256:
  `97cbe0a93c0092c939ff9f25a86e93ad4ef740354f124803509a02671685f8bd`
- bytes: **382,464**
- delivered frames: **95,616**

Repeated independent failure runs produce exact-equal transaction trace, sink and report.

## Early-stop proof

The explicit early-stop run stops after three 256-frame callbacks:

```text
completion_status = STOPPED_EARLY
callbacks         = 3
requested frames  = 768
delivered frames  = 768
final cursor      = 768
```

The early-stop sink is the exact prefix of the corresponding full callback run.

## Accepted authority invariant

Across normal, failure, early-stop and reopen execution:

> **accepted Project HEAD remains unchanged**

The callback engine, adapter lifecycle, callback transactions, sink payloads and metrics are all explicitly `derived_noncanonical` or runtime-only state.

No callback result can reverse-author accepted Project state.

## Project archive and reopen integrity

The nested `project.musica.zip` independently matched its manifest digest:

- SHA-256:
  `eacee8672fac3c3f1b6143ebd29abc33715f126cf253160cc130149a275481c2`
- bytes: **33,455**

Independent archive inspection found:

- **16** content-addressed object files;
- all **16/16** object contents matched their SHA-256 object names;
- persisted HEAD/main references were present.

Fresh import/reopen reproduces exactly:

- realtime execution plan;
- callback transaction trace;
- callback sink;
- callback run report;
- Project integrity PASS.

## Determinism

The evidence generator runs independently twice in the dedicated workflow and requires:

```text
diff -qr artifacts/rtio-r1-callback-engine-a artifacts/rtio-r1-callback-engine-b
```

to succeed before artifact upload.

The durable proof additionally confirms repeat-exact:

- normal plan;
- normal trace;
- normal sink;
- normal report;
- failure trace;
- failure sink;
- failure report;
- reopen plan/trace/sink/report.

## Proven bounded execution model

The maximum validated execution chain is:

```text
accepted routed+automated revision
→ RTIO-R0 provenance-bound realtime plan
→ CallbackEngine exact frame cursor
→ registered deterministic adapter callback
→ exact request/response transaction
→ derived PCM output payload
→ deterministic callback metrics/report
```

The callback request may not infer frame identity from wall-clock time. Source identity remains bound to exact accepted revision and RTIO-R0 plan SHA.

## Explicit non-claims

This validation does not claim:

- host-native ASIO device output;
- host-native CoreAudio device output;
- host-native WASAPI device output;
- wall-clock low-latency performance guarantees;
- microphone/line input;
- recording or monitoring;
- take/comp management;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- sample-rate conversion;
- realtime Browser control;
- generalized commercial realtime readiness.

## Validation verdict

> **VALIDATED — BOUNDED CALLBACK ENGINE & HOST-BACKEND ADAPTER BOUNDARY v0**

Maximum supported claim:

> **MUSICA can execute its provenance-bound realtime plan through a bounded callback-driven output engine with exact frame cursor, lifecycle, final-block behavior and deterministic failure accounting while callback/backend runtime remains derived and cannot reverse-author accepted creative state.**

Promotion remains conditional on all **26** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #133 completion and separate state-only closure to RTIO-R2.

Repository evidence remains authoritative over conversation/model memory.
