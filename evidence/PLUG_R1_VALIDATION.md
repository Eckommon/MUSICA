# PLUG-R1 Validation — Trusted Accepted Plugin Preview→Accept & Deterministic Offline Execution v0

## Scope

Issue #159 under parent Issue #155.

PLUG-R1 promotes the validated PLUG-R0 detached simulated plugin descriptor/instance/state model into bounded accepted Blueprint plugin authority. Accepted plugin state may change only through exact source-bound Preview → explicit Accept, while runtime processor objects, derived processing plans and processed WAV output remain non-canonical.

Real VST3/AU/CLAP binary loading remains explicitly out of scope.

## Evidence-bearing implementation head

- exact implementation/evidence head: `2130960e572b0e22b2618450add8a803b34d331d`
- permanent workflow count: **34**
- exact-head result: **34/34 SUCCESS**
- dedicated workflow: **PLUG-R1 Accepted Plugin Authority Evidence**
- dedicated run: `38428999804` — **SUCCESS**
- artifact ID: `11828934691`
- artifact name: `musica-plug-r1-accepted-plugin-authority-evidence`
- artifact ZIP SHA-256: `90a6032126eb3fc9b7eeeb8ce71e504d90f428fc5ddf77ec1b7d1c2624312170`
- artifact ZIP size: **32,544 bytes**

All 34 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The GitHub artifact declared digest and size matched the independently downloaded ZIP exactly:

- SHA-256: `90a6032126eb3fc9b7eeeb8ce71e504d90f428fc5ddf77ec1b7d1c2624312170`
- bytes: **32,544**

The artifact contains **16 manifest-declared payload files plus `manifest.json`**. All **16/16** declared payloads matched their recorded SHA-256 and byte size.

Key payload identities:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `accepted-plugin-a.json` | `cdb21e4b882c5293135f46d1d88f32ed69893953ae341043ed88a0a20ef88105` | 856 |
| `accepted-plugin-b.json` | `73a89347903a6d08f47062ba4fbda0d02e3b0abf6552c406f49baef9c4c4a15a` | 857 |
| `accepted-plugin-bypass.json` | `94a660f57b3caf6313f2d7c8aa187d487c2e414c072b9f55fe0627cb9e617c7f` | 856 |
| `accepted-plugin-removed.json` | `708404c39db2cb21433538c6827d5c753eda5deb1eab7ed763adc88dd71011af` | 101 |
| `baseline-routed.wav` | `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4` | 384,044 |
| `plugin-a.wav` | `1a813b90fdb38ab79c24f383e58167d8480f347ce6a04c8233ca5ef493a3c627` | 384,044 |
| `plugin-b.wav` | `7bebd2f8b2867214e0c7516427c2e20a90dac16a58508e3cc00d01f9132c0305` | 384,044 |
| `plugin-bypass.wav` | `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4` | 384,044 |
| `plugin-removed.wav` | `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4` | 384,044 |
| `project.musica.zip` | `e16be4d0ca5dced3694367ff716a71e01fce5cc7a6546a55cc7d87bee8475c09` | 42,009 |
| `proof.json` | `1b984a780a06b65607287568110207238e29caaab6ee17bf2969ce84f1d844d5` | 1,545 |

The exact Git contract/source/test/workflow inventory embedded in the evidence was independently checked against GitHub at the exact implementation head. All **11/11** entries matched their recorded SHA-256 and byte size.

## Accepted material identity

The accepted PLUG-R1 material uses a distinct canonical classification:

```text
classification = accepted_plugin_material
```

The initial accepted instance is bounded exactly to the validated PLUG-R0 semantics:

```text
plugin_id      PLUG-REF-001
instance_id    PI-001
format         simulated_reference_v0
processor_id   musica-simulated-gain-delay-v0
owner          routing_node / MASTER-001
slot           0
bypass         false
gain_db        -6.0
delay_frames   4
```

The controlled accepted state change modifies only:

```text
PI-001 / gain_db: -6.0 dB → -12.0 dB
```

The delay remains exactly **4 frames**.

The bounded edit primitives are:

- `ADD_INSTANCE`
- `REMOVE_INSTANCE`
- `SET_STATE`
- `SET_BYPASS`

No wildcard, display-name or positional identity is accepted.

## Source-bound authority proof

PLUG-R1 candidate source binding covers:

- project ID;
- accepted revision ID;
- Blueprint SHA-256;
- audio-material SHA-256;
- routing-material SHA-256;
- automation-material SHA-256;
- accepted plugin-material SHA-256.

The evidence proves:

- Preview is generated from an exact accepted source;
- Preview leaves accepted HEAD unchanged;
- generic `commit_revision()` cannot introduce/change/remove accepted plugin material;
- explicit plugin Accept is the only path that opens the Project Engine plugin delta gate;
- Accept advances exactly one accepted revision;
- the same Preview cannot be accepted twice;
- a stale Preview after another HEAD advance fails closed;
- a forged Blueprint object carrying the same accepted revision ID fails persisted-source hash binding;
- missing instance IDs fail closed;
- invalid/non-master owner placement fails closed;
- descriptor/instance identity and canonical owner/slot ordering remain exact.

Runtime processor state, processing plans and processed audio do not have reverse mutation authority.

## Deterministic accepted execution

PLUG-R1 reuses the PLUG-R0 deterministic processor and processing-plan contract rather than introducing a second execution model.

The insertion policy remains:

```text
accepted routed master PCM16 reference stage
→ accepted simulated plugin chain
→ deterministic gain
→ deterministic fixed-frame delay
→ hard clip before PCM16 output
```

Exact plan self-hashes were independently recomputed using MUSICA canonical JSON encoding:

- accepted plugin A:
  `17e8e9a942f54aca86e183db42ebaf0c9c319b95f2a7f6bae4bd489ec40e338c`
- accepted controlled plugin B:
  `3cb4a89b11a3b0f0e2d0fa161135ab43f6fe5e1237149f79e8a6c03cd00b34a8`
- accepted bypass:
  `28000489e0963ce6af9da0aaf83150331dc6188de6ec11185e0d761444aa2087`
- accepted removed/empty state:
  `86b8962ac6ac70dafeb342004bdc88a8f67ce0c5e69f4f3f86daa639288d50c2`

All **4/4** declared/recomputed self-hashes matched exactly.

Effective latency is:

- active A: **4 frames**
- active B: **4 frames**
- bypass: **0 frames**
- removed/empty: **0 frames**

## Numerical DSP proof

All evidence WAV files independently parse as:

- stereo: **2 channels**
- sample width: **2 bytes**
- sample rate: **8,000 Hz**
- frame count: **96,000**
- compression: **NONE / PCM**
- byte size: **384,044**

For active A and B, the first **4 frames are exactly zero**, proving the declared fixed 4-frame delay appears in the actual output.

The controlled gain change is also numerically observable:

- active A maximum PCM magnitude: approximately **13,778**
- active B maximum PCM magnitude: approximately **6,905**
- B/A peak ratio: approximately **0.501**

This is consistent with the accepted -6 dB additional gain reduction and proves the output difference is not merely a hash change.

## Bypass and remove proof

Accepted bypass produces:

- effective plugin latency: **0 frames**
- WAV bytes exactly equal to the underlying routed baseline
- SHA-256 exactly equal to baseline:
  `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4`

Removing the last accepted instance also prunes its now-unreferenced descriptor and returns the accepted plugin material to the deterministic empty identity:

```json
{"classification":"accepted_plugin_material","descriptors":[],"instances":[],"material_version":"0"}
```

The removed/empty output is again byte-exact to the underlying routed baseline.

## Processor failure authority proof

A deterministic forced processor error is rejected during derived execution.

The evidence proves that such a processor failure:

- does not advance Project HEAD;
- does not mutate accepted plugin material;
- does not silently repair or substitute plugin output;
- cannot reverse-author creative state.

## Reopen integrity

The nested `project.musica.zip` independently matched its manifest digest:

- SHA-256: `e16be4d0ca5dced3694367ff716a71e01fce5cc7a6546a55cc7d87bee8475c09`
- bytes: **42,009**

Independent archive inspection found **19** content-addressed object files, and all **19/19** contents matched their SHA-256 object names.

The persisted accepted lineage contains the expected sequence:

```text
root
→ accepted audio
→ accepted routing
→ accepted plugin insertion
→ accepted plugin controlled state change
```

The archive intentionally captures the non-empty accepted controlled state before later bypass/remove evidence. Fresh import/reopen reproduces exactly:

- accepted plugin material;
- plugin-material SHA;
- processing plan;
- processing-plan SHA;
- processed WAV bytes/SHA;
- Project integrity PASS.

## Compatibility

PLUG-R1 preserves:

- legacy projects with no `materials.plugins`;
- deterministic empty accepted plugin identity;
- PLUG-R0 detached proposal API as a non-canonical testing/reference helper;
- existing routed rendering when accepted plugin material is empty;
- MRAM, RTIO and REC authority boundaries.

A PLUG-R0 `noncanonical_proposal` object cannot simply be inserted into accepted Blueprint state because the accepted Blueprint path requires the distinct `accepted_plugin_material` contract.

## Explicit non-claims

This validation does not claim:

- real VST3/AU/CLAP binary loading;
- plugin discovery/scanning/installation;
- arbitrary third-party plugin UI/editor embedding;
- third-party opaque state chunks;
- untrusted-binary sandboxing or crash containment;
- generalized plugin parameter automation;
- sidechain or arbitrary plugin bus negotiation;
- arbitrary-graph latency compensation;
- sample-rate conversion;
- commercial third-party plugin compatibility;
- generalized commercial release readiness.

Latency compensation beyond the current deterministic serial fixed-delay identity remains a later rung.

## Validation verdict

> **VALIDATED — TRUSTED ACCEPTED PLUGIN PREVIEW→ACCEPT & DETERMINISTIC OFFLINE EXECUTION v0**

Maximum supported claim:

> **MUSICA can accept and persist bounded simulated plugin instances/state only through source-bound Preview→Accept authority, deterministically execute the exact accepted plugin state over its accepted routed source, and reproduce accepted plugin identity plus derived plan/output after reopen while generic commit, stale/forged source, processor runtime and processed-output paths remain non-authoritative.**

Promotion remains conditional on all **34** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #159 completion and separate state-only closure to PLUG-R2.

Repository evidence remains authoritative over conversation/model memory.
