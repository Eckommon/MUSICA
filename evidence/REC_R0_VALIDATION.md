# REC-R0 Validation — Deterministic Simulated Input Capture Substrate v0

## Scope

Issue #143 under parent Issue #142.

REC-R0 defines the first bounded input/capture substrate for MUSICA. It introduces an explicit deterministic simulated input capability, provenance-bound capture plan, strict capture lifecycle, exact frame cursor, deterministic block scheduling, derived PCM payload/report, and fail-closed configuration/lifecycle semantics while preserving the core authority invariant that capture runtime and capture bytes are non-canonical and cannot directly become accepted creative state.

## Evidence-bearing implementation head

- exact implementation/evidence head: `f8b0f90a852aeb8ba48f361c5ba1844ecb8325ac`
- permanent workflow count: **29**
- exact-head final result: **29/29 SUCCESS**
- one initial Post-M7 Accepted Revision Compare run observed a single Browser 400 resource-load console error in the human-choice E2E; the failed workflow alone was rerun on the same exact head and completed SUCCESS through real Chromium, deterministic A/B evidence generation and artifact upload
- dedicated workflow: **REC-R0 Input Capture Evidence**
- dedicated run: `36629133385` — **SUCCESS**
- artifact ID: `11062015980`
- artifact name: `musica-rec-r0-input-capture-evidence`
- artifact ZIP SHA-256: `04a9a49aee2a3d719e4de5f97b72e2d3aa9f3607456f984f6c3d3d9049f0f203`
- artifact ZIP size: **21,948 bytes**

All 29 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The downloaded GitHub artifact matched the declared digest and byte size exactly:

- SHA-256: `04a9a49aee2a3d719e4de5f97b72e2d3aa9f3607456f984f6c3d3d9049f0f203`
- bytes: **21,948**

The artifact contains **12 manifest-declared payload files plus `manifest.json`**. All **12/12** payloads independently matched the manifest SHA-256 and byte size.

The artifact payload inventory is:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `capture-plan.json` | `40df64d5c51070120a21f529957202f0d0e85c2b531b1f2a459fd0af99f5f05f` | 1,331 |
| `contract-hashes.json` | `e93973f35e2ef491002859da56e63c91d4643a96cced5a4e0f86e91058e0a84c` | 1,031 |
| `failure-block-trace.json` | `56c82c60418809ae61ccd311ddf6bd7686c684c308d954899b527a8388e5c6d7` | 2,041 |
| `failure-capture.pcm` | `f929ab7e47e82806ba63ca5659962a30579d774761f56e16c8bebfaa386eef0b` | 3,328 |
| `failure-run-report.json` | `050ea9ec5e2f565a9ce544b809928da00c2e084ac2832e2b55cb65d68e33f256` | 907 |
| `input-capability.json` | `1ba3cfefe3907e05293ac48df8ab85519311af6a3c98b6175e225a6a35f6153b` | 413 |
| `invalid-results.json` | `971145aa85ee59c9a0a1f9679fd33dade296934dd0fc817759ba4c488795416f` | 1,103 |
| `normal-block-trace.json` | `6f16ee6b568ca2f5d8455ca6284a9871baff155c34da85d5426c25bdb05b43a3` | 2,290 |
| `normal-capture.pcm` | `6ffa39de383519a535837d6cea0b9118339f7e29cfaff1354e98c2616bc51f71` | 8,200 |
| `normal-run-report.json` | `1cbb791586f18c9d19d514688f473ae651e5307130bc35735c98b63fb0b712f8` | 907 |
| `project.musica.zip` | `2a8b404c9c1fdedd085d8e7b0aac2db98374060d73ebc305db1e37f885e533b0` | 6,435 |
| `proof.json` | `e1f7a2081af37ff599d39c69233ad9fed314c1d282f6b1142158a7448e335706` | 935 |

The evidence contract inventory was independently checked against the exact GitHub implementation head. All **7/7** schema, implementation, test and workflow files matched both the recorded SHA-256 and byte size.

## Capability contract

The validated input capability is explicitly bounded:

```text
backend_id: musica-simulated-input-v0
classification: simulated_test_input_backend
deterministic: true
sample format: pcm16_little_endian
supported sample rates: 8000, 44100, 48000 Hz
supported input channels: 1, 2
supported block sizes: 64, 128, 256, 512, 1024 frames
host-native-input-claimed: false
nominal simulated input latency: 0 frames
```

No ASIO/CoreAudio/WASAPI microphone or line-input claim is made.

## Capture-plan provenance and self-hash

The evidence capture plan binds exact accepted project provenance:

- project ID: `MUSICA-M1-DARK-001`
- accepted revision: `rev-001`
- Blueprint SHA: `f9bf87d00e5c1c102e8161662b3e13c60c72a0775f03243509d807c8f06d3855`
- audio material SHA: `06786e35abb823002ac8e2c60fe11f7e3a64a95c69119ba5c23d2ceec55340c3`
- routing material SHA: `1ad118d97e8b733c526e5f33ce454ec6a936a6c9e7d447991d9f502c2b8019f2`
- automation material SHA: `5109269edbac5a98dac3e075f9f3f89fc2a1621733642a130e29bbc1c3323776`
- input capability SHA: `1ba3cfefe3907e05293ac48df8ab85519311af6a3c98b6175e225a6a35f6153b`

The plan freezes:

```text
sample rate: 8,000 Hz
channels: 2
block size: 256 frames
capture length: 2,050 frames
cursor authority: exact zero-based capture frame
scheduler: sequential fixed blocks
final block: partial block without padding
source-rate policy: exact match required / no resampling
runtime state canonical: false
captured payload canonical: false
```

The plan self-hash independently recomputed exactly:

> `c73dabfe63dd60f521ffb29d1cddcdf36f2f877c950a1ae7480b4b76d15d79d7`

## Normal capture proof

Normal deterministic capture produces:

- requested frames: **2,050**
- captured frames: **2,050**
- block requests: **9**
- captured blocks: **9**
- final capture cursor: **2,050**
- ERROR: **0**
- SHORT_FILL: **0**
- LATE: **0**
- dropout-equivalent count: **0**
- channels: **2**
- sample rate: **8,000 Hz**
- payload bytes: **8,200**
- payload SHA-256:
  `6ffa39de383519a535837d6cea0b9118339f7e29cfaff1354e98c2616bc51f71`

The first eight blocks contain 256 frames each and the final block contains exactly 2 frames, proving the declared partial-final-block/no-padding policy.

The normal run-report self-hash independently recomputed exactly:

> `42823ffa6aa21b21ee46c841a9b2bef4a2f284e364182ee9210f25a90d86fcc4`

The PCM payload was independently regenerated from the declared deterministic integer input pattern and matched **byte-for-byte**.

## Controlled capture-failure proof

The deterministic failure scenario injects:

```text
block 1 → ERROR
block 2 → SHORT_FILL
block 3 → LATE
```

The exact resulting metrics are:

- frames requested: **2,048**
- frames captured: **1,664**
- final capture cursor: **2,048**
- blocks requested: **8**
- blocks captured: **7**
- ERROR count: **1**
- SHORT_FILL count: **1**
- LATE count: **1**
- dropout-equivalent count: **3**
- channels: **1**
- payload bytes: **3,328**
- payload SHA-256:
  `f929ab7e47e82806ba63ca5659962a30579d774761f56e16c8bebfaa386eef0b`

The ERROR block contributes zero captured frames, the SHORT_FILL block captures exactly 128 of 256 requested frames, and the LATE block captures all 256 frames while marking late status.

The failure run-report self-hash independently recomputed exactly:

> `f2579e5232031346fe96ff1fb8475502af0310e17c6a42020eb550d6b62ae89b`

The failure PCM payload was also independently reconstructed from the exact selected deterministic source-frame ranges and matched **byte-for-byte**.

## Lifecycle and fail-closed behavior

The validated lifecycle is:

```text
CLOSED
→ OPEN
→ READY
→ CAPTURING
→ STOPPED
→ FINALIZED
→ CLOSED
```

The artifact proves fail-closed handling for:

- unsupported sample rate;
- unsupported input channel count;
- unsupported block size;
- invalid capture frame limit;
- forced failure index outside the capture trace;
- overlapping ERROR and SHORT_FILL injection;
- capture before open/start;
- start before open;
- requested range outside the capture plan;
- double close.

## Authority boundary

REC-R0 proves:

```text
accepted Project revision
+ explicit simulated input capability/config
→ derived non-canonical capture plan
→ strict simulated input runtime
→ deterministic block trace
→ derived captured PCM
→ derived capture report
≠ accepted audio asset
≠ accepted track/clip state
```

The evidence explicitly confirms:

- accepted Project HEAD remains unchanged;
- accepted audio material remains unchanged;
- captured payload is not canonical;
- capture runtime is not canonical;
- captured bytes are not imported as an asset;
- no trusted recording Accept authority is claimed;
- no monitoring authority is claimed.

## Repeat and reopen exactness

Independent evidence A/B generation is byte-reproducible.

Fresh export/import reopen reproduces:

- capture plan exactly;
- normal block trace exactly;
- normal captured payload exactly;
- normal run report exactly;
- accepted source binding exactly;
- Project integrity PASS.

The nested `project.musica.zip` independently matched its manifest digest:

- SHA-256: `2a8b404c9c1fdedd085d8e7b0aac2db98374060d73ebc305db1e37f885e533b0`
- bytes: **6,435**

Its content-addressed object store contains **3** object files, and all **3/3** object contents independently matched their SHA-256 filenames. Persisted HEAD/main refs are present.

## Explicit non-claims

REC-R0 does not claim:

- accepted recording placement;
- direct capture-to-track mutation;
- trusted captured-asset finalization;
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

## Validation verdict

> **VALIDATED — DETERMINISTIC SIMULATED INPUT CAPTURE SUBSTRATE v0**

Maximum supported claim:

> **MUSICA can deterministically capture a bounded simulated input source through an explicit provenance-bearing capture plan/runtime with exact frame progression, deterministic failure instrumentation and fail-closed configuration/lifecycle semantics while capture bytes and runtime state remain derived and cannot directly become accepted creative state.**

Promotion remains conditional on all **29** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #143 completion and separate state-only closure to REC-R1.

Repository evidence remains authoritative over conversation/model memory.
