# RTIO-R0 Validation — Realtime Execution Contracts & Deterministic Simulated Backend v0

## Scope

Issue #130 under parent Issue #129.

RTIO-R0 defines the first bounded real-time execution/device contract without claiming host-native realtime hardware. It binds one exact accepted routed/native-automation revision to a provenance-bearing derived realtime plan, deterministically schedules fixed PCM blocks through a strict simulated output backend, reports lifecycle/runtime/xrun metrics, and proves that realtime state cannot mutate accepted creative authority.

## Evidence-bearing implementation head

- exact implementation/evidence head: **`f597c441e0b2586789b7c5f06d802ed0c9298f17`**
- permanent workflow count: **25**
- exact-head result: **25/25 SUCCESS**
- dedicated workflow: **RTIO-R0 Realtime Simulated Backend Evidence**
- dedicated run: **`36548047238` — SUCCESS**
- artifact ID: **`11023801193`**
- artifact name: **`musica-rtio-r0-realtime-simulated-backend-evidence`**
- artifact ZIP SHA-256: **`8765ec2e24c9fb081f1aadd74e7861aeccffea00194b638b9d0a5204f7920456`**
- artifact ZIP size: **31,187 bytes**

All 25 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The GitHub artifact-declared digest and size matched the independently downloaded ZIP exactly.

The manifest declares **11 payload files**. All **11/11** matched their recorded SHA-256 and byte size.

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `backend-capability.json` | `b88e8ea024a145d33fe2eda9ed0c1cc3f69add2485045dee32b4363dc99c5ffc` | 336 |
| `block-trace.json` | `8cc211a06bd68bc7796152a4f6382df07dc3944af2f12c888e564d8a76537a54` | 73,304 |
| `contract-hashes.json` | `569509d5e0c87689e1cdd2e8e15a9b541e2c5f6cef5f5f4187b3e15cf68d3bba` | 1,333 |
| `invalid-config-results.json` | `6898e514427ceaf22e205bfc4ebacdc04462b8eed7c1289fb42d8b3068afd042` | 526 |
| `project.musica.zip` | `c54829307c987a18e7b9b2df83870bb52016a7ce7896bf2be56077333f274d9c` | 33,446 |
| `proof.json` | `3c58e3a5071c7655f9d395fef08b387bc86e63c3bdd511dadac95b4bf7d90af7` | 793 |
| `realtime-plan.json` | `3973659026bbd7a2ea6e98b943d85f050eee31c5a2d28fff7a09c842e38bc23b` | 1,573 |
| `run-report.json` | `d9f6b4bbfc82d4b819aafdfc4d4187a0f28be4ef363390ed3989524983dd29ee` | 856 |
| `sink.pcm` | `08aefbaf4a918446584245d2c7f4a79feede21c769cb8f2cacc510eeaece3c03` | 384,000 |
| `xrun-report.json` | `7998fc6f0eaab3bc88d792aded315be0bfc4a91fe9b88b4cbcf9710fbd63b5db` | 856 |
| `xrun-sink.pcm` | `2180084d3a8b09fe229a259d8c2a9bc3a79d814136a1be82ef8cf5129ae659ac` | 382,976 |

The artifact contract inventory was independently compared against exact GitHub head `f597c441e0b2586789b7c5f06d802ed0c9298f17`. All **9/9** schema, implementation, existing execution dependency, test and workflow files matched recorded SHA-256 and byte size.

The nested persisted project archive contains **16** content-addressed objects. All **16/16** independently matched the SHA-256 encoded in their object filename.

## Realtime plan self-hash

Using MUSICA canonical JSON encoding, the realtime execution plan self-hash independently recomputed exactly:

- declared:
  `29566a48c8e8a9c20ac03c45ca0b499747975aa88d386ab3a3956d0510d0b203`
- recomputed:
  `29566a48c8e8a9c20ac03c45ca0b499747975aa88d386ab3a3956d0510d0b203`

The plan is explicitly `derived_noncanonical` and binds:

- exact project ID and accepted revision ID;
- Blueprint SHA;
- audio material SHA;
- routing material SHA;
- automation material SHA;
- routed mix plan SHA;
- routed WAV SHA;
- backend capability SHA;
- sample rate;
- output channel count;
- block size;
- duration frames;
- transport start/end;
- no-resampling and scheduler policy.

## Backend capability boundary

RTIO-R0 validates exactly one backend identity:

```text
musica-simulated-output-v0
classification = simulated_test_backend
deterministic = true
```

The backend contract explicitly advertises supported sample rates, output channel counts, block sizes and latency metadata.

RTIO-R0 does **not** infer or claim ASIO, CoreAudio, WASAPI or any other host-native device semantics.

## Deterministic block scheduling proof

The evidence plan uses:

- sample rate: **8,000 Hz**
- output channels: **2**
- PCM width: **16-bit**
- block size: **256 frames**
- duration: **96,000 frames**

The independently inspected trace contains:

- **375 blocks**
- contiguous zero-based frame ranges;
- first block starts at frame **0**;
- every block begins exactly at the previous block end;
- final block ends exactly at frame **96,000**;
- summed block frame count is exactly **96,000**.

For this fixture the duration is exactly divisible by 256, so no partial final block is required. The contract nevertheless freezes the general final-block policy as `partial_block_without_padding`.

## Exact routed source equivalence

The simulated backend normal-run sink is byte-identical to the PCM16 stereo payload of the validated routed mixer WAV for the same exact accepted revision.

Normal sink:

- bytes: **384,000**
- frames: **96,000**
- SHA-256:
  `08aefbaf4a918446584245d2c7f4a79feede21c769cb8f2cacc510eeaece3c03`

This proves RTIO-R0 does not introduce a second DSP/mixer interpretation. It schedules the already validated routed output through explicit realtime blocks.

## Lifecycle proof

The strict simulated backend lifecycle is:

```text
CLOSED
→ OPEN
→ RUNNING
→ STOPPED
→ CLOSED
```

Writes outside `RUNNING`, malformed block payloads, and illegal lifecycle transitions fail closed.

The normal run report independently recomputed its self-hash exactly:

`4ec3fd23d6c0f96fb67b52907559095f8daf5a1cfc1746fd3226a8d8316bb642`

Normal metrics:

```text
blocks requested = 375
blocks written   = 375
frames requested = 96,000
frames written   = 96,000
final cursor     = 96,000
xrun count       = 0
nominal latency  = 0 frames (simulated metadata)
```

## Forced xrun/dropout proof

A deterministic test-only xrun is injected at block index **1**.

The xrun report self-hash independently recomputed exactly:

`5d5b2d4c4376e43660d34929d8e29febda4e6af341f907f60fa03f402d2eddc5`

Result:

```text
blocks requested = 375
blocks written   = 374
frames requested = 96,000
frames written   = 95,744
final cursor     = 96,000
xrun count       = 1
```

Exactly one 256-frame block is omitted from the simulated sink.

Xrun sink:

- bytes: **382,976**
- SHA-256:
  `2180084d3a8b09fe229a259d8c2a9bc3a79d814136a1be82ef8cf5129ae659ac`

Independent repeated xrun runs reproduce the same report and sink bytes exactly.

## Fail-closed configuration proof

The evidence independently records all of these as blocked:

- unsupported backend sample rate: **16,000 Hz**;
- supported-backend rate **44,100 Hz** against 8,000 Hz source assets under no-resampling policy;
- unsupported block size: **333 frames**;
- forced xrun index outside the execution trace.

The source-rate mismatch is rejected by the inherited native/routed mixer exact-source-rate rule rather than silently resampling.

## Accepted authority boundary

The evidence proves accepted Project `main` HEAD is identical before and after realtime plan construction and simulated execution.

The following remain derived/non-canonical:

```text
realtime execution plan
backend lifecycle state
block cursor / block trace
simulated sink bytes
xrun/dropout counters
runtime report
latency metadata
```

None may write back into accepted creative state.

## Repeat and reopen exactness

Independent identical runs reproduce exactly:

- realtime execution plan;
- block trace;
- normal sink bytes;
- normal run report;
- forced-xrun sink;
- forced-xrun run report.

After export/import reopen, evidence reproduces exactly:

- plan;
- block trace;
- sink bytes;
- run report;
- accepted source binding.

Project integrity verification is PASS after reopen.

## Explicit non-claims

RTIO-R0 does not claim:

- real ASIO/CoreAudio/WASAPI output;
- wall-clock realtime or low-latency guarantees;
- microphone/line input;
- recording/monitoring;
- take/comp workflows;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- sample-rate conversion;
- realtime Browser device control;
- sidechains;
- commercial realtime readiness.

## Validation verdict

> **VALIDATED — REALTIME EXECUTION CONTRACTS & DETERMINISTIC SIMULATED BACKEND v0**

Maximum supported claim:

> **MUSICA can deterministically lower an accepted routed/automated project into an explicit realtime execution plan and execute it through a bounded simulated fixed-block backend with exact frame progression, lifecycle and runtime metrics while realtime state remains derived and accepted creative state remains unchanged.**

Promotion remains conditional on all **25** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #130 completion and separate state-only closure to RTIO-R1.

Repository evidence remains authoritative over conversation/model memory.
