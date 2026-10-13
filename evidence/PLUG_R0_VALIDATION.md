# PLUG-R0 Validation — Plugin Contracts & Deterministic Simulated Processor v0

## Scope

Issue #156 under parent Issue #155.

PLUG-R0 defines the first bounded plugin-host contract as a **detached non-canonical proposal plus deterministic simulated/reference processor**. It deliberately does not place non-empty plugin material into accepted Blueprint authority and does not claim third-party VST3/AU/CLAP binary hosting.

The validated execution boundary is:

```text
exact accepted routed revision
+ detached plugin descriptor/instance/state proposal
→ structural/source validation
→ deterministic derived plugin processing plan
→ deterministic post-routed-master reference processing
→ derived PCM16 WAV
≠ accepted creative authority
```

## Evidence-bearing implementation head

- canonical PR base main: `5c9150da4c7ff18f12797e87fea08a10c5e12ed0`
- implementation PR: #158
- exact implementation/evidence head:
  `1d3866354bc6f9d30461c4ab73a190f4ca6c473d`
- permanent workflow count: **33**
- exact-head result: **33/33 SUCCESS**
- dedicated workflow: **PLUG-R0 Simulated Plugin Processor Evidence**
- dedicated run: `36869366855` — **SUCCESS**
- artifact ID: `11166403201`
- artifact name: `musica-plug-r0-simulated-processor-evidence`
- artifact ZIP SHA-256:
  `5fe99e09246747ac4e8a8b2e45d4ef0e82313aa44c01f1a0e4ea88bd040bf018`
- artifact ZIP size: **23,124 bytes**

All 33 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The GitHub artifact declared digest and byte size matched the independently downloaded ZIP exactly:

- SHA-256:
  `5fe99e09246747ac4e8a8b2e45d4ef0e82313aa44c01f1a0e4ea88bd040bf018`
- bytes: **23,124**

The artifact contains **14 manifest-declared payload files plus `manifest.json`**. Every declared payload matched its manifest SHA-256 and byte size:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `baseline-routed-plan.json` | `52aa3806f6289c96ade6feb802d3fb51f42dca803e0f5661947b52e753101b7b` | 3,634 |
| `baseline-routed.wav` | `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4` | 384,044 |
| `contract-hashes.json` | `4f7bb5c03ff29c830ab74414384b2c50f930199bac410dcabc12af8b14e8601c` | 1,144 |
| `plugin-a.wav` | `1a813b90fdb38ab79c24f383e58167d8480f347ce6a04c8233ca5ef493a3c627` | 384,044 |
| `plugin-b.wav` | `7bebd2f8b2867214e0c7516427c2e20a90dac16a58508e3cc00d01f9132c0305` | 384,044 |
| `plugin-bypass.wav` | `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4` | 384,044 |
| `plugin-material-a.json` | `cae2d837fa10aebb65a1e16f50e3f128c8316ca68e060b04cb98c066ead79021` | 853 |
| `plugin-material-b.json` | `ada37eb1c3c7df7fb77d3bb8adcb1f6785b6ae8a7d0d4a16b5b03bb89af6868a` | 854 |
| `plugin-material-bypass.json` | `befabe7bd7a6cc881eeb0d00e208cffe0700b488d5bf7fa1b3bf79a61c11a861` | 854 |
| `plugin-plan-a.json` | `647e2573bf2726fff2d1b1c0f960cbf3c8cf602c9dafb34562fe7e00d1536ba1` | 1,628 |
| `plugin-plan-b.json` | `f263f19d17c9b505e7308581faff038b5f103cba0a5f2ed25fcac1bc9a476b79` | 1,628 |
| `plugin-plan-bypass.json` | `79ac0c2cbcabe67a9889bf1353700ba41ea227ecf5217c7d2502d3879ad08a04` | 1,629 |
| `project.musica.zip` | `e10d092e91795835fd166303aa2e238b86fc0524720bc6343495cce033041b87` | 24,697 |
| `proof.json` | `bee6b5880f52afb07ced56d6251a93f4ba90768fcf64a082d41cb63b4da85bc1` | 1,258 |

The evidence contract inventory was independently compared with exact GitHub head `1d386635...`. All **8/8** recorded schema/source/test/workflow files matched both recorded SHA-256 and byte size.

## Project archive inspection

The nested `project.musica.zip` matched its manifest digest exactly.

Independent archive inspection found **13** content-addressed files under `objects/sha256/`; all **13/13** object contents matched their SHA-256 object names.

The archive contains the accepted root → audio → routed revision lineage and references required to reconstruct the exact accepted source used by the detached plugin processor.

PLUG-R0 does **not** claim that detached plugin material is persisted as accepted project state. Rather, given the same validated detached material, reopening the exact accepted project source reproduces the same plugin plan and processed output. Accepted plugin persistence is reserved for PLUG-R1 authority.

## Plugin descriptor and instance contract

The validated descriptor is explicitly bounded:

```text
format: simulated_reference_v0
processor_id: musica-simulated-gain-delay-v0
I/O: stereo → stereo
internal sample format: float64
sample-rate policy: exact match required / no resampling
latency source: delay_frames state parameter
```

The exact canonical parameter descriptor set is:

```text
gain_db      decibel   [-60, 12]   default 0
delay_frames frames    [0, 4096]   default 0
```

The R0 instance scope is intentionally narrow:

- stable `instance_id`;
- stable `plugin_id`;
- owner kind `routing_node`;
- owner ID must equal the exact accepted master routing node;
- deterministic serial slot ordering;
- unique slot per owner;
- explicit bypass boolean;
- canonical gain/delay state.

Wildcard, display-name-only and position-only authority are not used.

## Processing plan provenance

The derived plugin processing plan binds exact:

- project ID;
- accepted revision ID;
- Blueprint SHA;
- audio material SHA;
- routing material SHA;
- automation material SHA;
- routed mix plan SHA;
- routed WAV SHA;
- detached plugin material SHA;
- processor identity;
- owner/slot/instance identity;
- gain state;
- delay/latency state;
- sample rate and channel contract.

The plan is explicitly classified:

> `derived_noncanonical`

and its insertion policy is explicitly:

> `post_routed_master_pcm16_reference_stage`

This is a bounded R0 reference stage, not a claim that real third-party plugins already execute at a production DAW insert point.

## Self-hash verification

Using MUSICA canonical JSON encoding, including the canonical trailing newline, all plugin processing plan self-hashes independently recomputed exactly:

- plugin A:
  `2b8044b02c9349f7fe703f061ac23b3000e5b9e17db652ef4bd8d95f6486b57f`
- plugin B:
  `f9bdcce6efc1a3b7b11546fc9919f56aff9f7f138bde3bc0194bdb77f501f221`
- bypass:
  `62933f7221ed4d55ab89c8d6c8e10f1788fdd86561c53137f8dcf2a76697d89f`

## Controlled state-change proof

Plugin material A and B differ in exactly one state field:

```text
PI-001 / gain_db: -6.0 dB → -12.0 dB
```

All descriptor identity, owner, slot, delay and bypass state remain unchanged.

The controlled change alters:

- plugin material SHA:
  `cae2d837...ead79021` → `ada37eb1...af6868a`;
- processing plan self-hash:
  `2b8044b0...6486b57f` → `f9bdcce6...501f221`;
- processed WAV:
  `1a813b90...93a3c627` → `7bebd2f8...32c0305`.

This proves deterministic parameter state materially controls the derived processor plan and output.

## Latency proof

Plugin A and B both declare:

```text
delay_frames = 4
effective_latency_frames = 4
total_effective_latency_frames = 4
```

Independent WAV inspection confirms the processed output begins with the expected four silent frames under the deterministic fixed-delay processor.

A serial two-instance regression separately proves deterministic slot order and summed latency:

```text
PI-001 delay 3 frames
→ PI-002 delay 4 frames
→ total effective latency 7 frames
```

Bypassed instances contribute zero effective latency.

PLUG-R0 does not yet claim arbitrary-graph latency compensation; that is a later rung.

## Bypass proof

The bypass proposal deliberately contains non-neutral state:

```text
gain_db = +12 dB
delay_frames = 128
bypass = true
```

Despite that state, the bypass result is byte-exact to the accepted routed baseline:

- baseline routed WAV:
  `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4`
- bypass WAV:
  `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4`
- effective latency: **0 frames**

This proves bypass semantics are execution-authoritative for the derived processor while remaining non-canonical.

## WAV inspection

All four evidence WAV files are valid deterministic uncompressed PCM:

- channels: **2**
- sample width: **2 bytes**
- sample rate: **8,000 Hz**
- frames: **96,000**
- byte size: **384,044**
- compression: **NONE / PCM**

The active processor changes output relative to baseline. Independent reruns reproduce the exact plugin plan and exact processed WAV bytes.

## Fail-closed behavior

The implementation/tests/evidence prove rejection of or protection against:

- unknown plugin ID;
- duplicate insertion slot;
- non-master owner placement in R0;
- non-canonical descriptor parameter contract;
- unsupported sample-rate/no-resampling path;
- schema-invalid parameter/state values;
- malformed/duplicate instance identity;
- processing-plan tampering through self-hash validation;
- deterministic forced processor error injection;
- accepted Blueprint plugin material insertion;
- generic accepted plugin mutation authority.

The forced processor error fails closed without changing accepted Project HEAD.

## Reopen and authority proof

The evidence proves:

- accepted HEAD remains unchanged throughout detached plugin execution;
- plugin material is non-canonical;
- plugin runtime is non-canonical;
- processed audio is non-canonical;
- accepted non-empty plugin mutation authority is **not open** in R0;
- the existing Blueprint contract rejects direct non-empty plugin material insertion;
- export/import reopen of the accepted source passes Project integrity;
- identical detached plugin material over the reopened exact source reproduces the exact plan and WAV.

No runtime processor object, processing plan or processed WAV can reverse-author accepted creative state.

## Compatibility

PLUG-R0 preserves the legacy/no-plugin accepted project path.

The baseline routed render remains the existing MRAM routed output, and an all-bypassed plugin chain is byte-exact to that baseline.

All **33** permanent workflows — including the prior ATCM, MRAM, RTIO, REC, M5/M6/M7 and full MUSICA CI gates — are green on the exact implementation/evidence head.

## Explicit non-claims

This validation does not claim:

- accepted plugin Preview→Accept authority;
- accepted plugin persistence inside Blueprint/project state;
- real VST3/AU/CLAP binary loading;
- host plugin scanning/installation;
- third-party state chunks;
- arbitrary plugin UI/editor embedding;
- production sandbox/crash containment for untrusted binaries;
- plugin parameter automation;
- arbitrary sidechain/bus negotiation;
- arbitrary-graph plugin-delay compensation;
- sample-rate conversion;
- commercial third-party plugin compatibility;
- generalized commercial release readiness.

## Validation verdict

> **VALIDATED — DETACHED PLUGIN CONTRACTS & DETERMINISTIC SIMULATED PROCESSOR v0**

Maximum supported claim:

> **MUSICA can describe stable bounded plugin instances and state as a detached non-canonical proposal, lower them against an exact accepted routed source into a provenance-bearing deterministic simulated processing plan with explicit latency and capability constraints, and reproduce derived processed output exactly while accepted plugin mutation remains closed and runtime/output state remains non-canonical.**

Promotion remains conditional on all **33** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #156 completion and separate state-only closure to PLUG-R1.

Repository evidence remains authoritative over conversation/model memory.
