# REC-R2 Validation — Bounded Input Monitoring & Capture/Dropout Instrumentation v0

## Scope

Issue #149 under parent Issue #142.

REC-R2 adds one bounded deterministic input-monitoring path on top of the validated REC-R0 capture substrate and REC-R1 recording-finalize authority. Monitoring consumes an exact copy of each already-captured input block and writes only to the validated simulated output backend. Monitor runtime/sink state remains derived and non-canonical.

## Evidence-bearing implementation head

- exact implementation/evidence head: `ec338120a61e1796a2cecd99aa66126fe6eebe29`
- permanent workflow count: **31**
- exact-head result: **31/31 SUCCESS**
- one initial Post-M7 real-browser Compare run emitted a single HTTP 400 console resource error; that existing browser workflow alone was rerun on the same exact head and completed SUCCESS without code changes
- dedicated workflow: **REC-R2 Monitoring Evidence**
- dedicated run: `36685344816` — **SUCCESS**
- artifact ID: `11083583035`
- artifact name: `musica-rec-r2-monitoring-evidence`
- artifact ZIP SHA-256: `fa586bf0239901273eb4dcd77c3839b7a074a5bfd94dea569df96791d8404665`
- artifact ZIP size: **40,001 bytes**

## Independent artifact inspection

The independently downloaded GitHub artifact matched the declared digest and byte size exactly.

The archive contains **14 manifest-declared payloads plus `manifest.json`**. All **14/14** declared payloads matched manifest SHA-256 and byte size.

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `capture-failure-report.json` | `ba211602c94ee2c854de2e3fd1ed27711e66a78675533310d3da9d8715289e67` | 1,077 |
| `contract-hashes.json` | `618a56f345029dda89a7a4d4876757ab0711aa75196531d4093a4f737d3c5d3a` | 1,288 |
| `monitor-off-capture.pcm` | `8bd5917d21004e7fe2143c04dfd2f20f9d546c993cd4cde41b4cb6be5b012aed` | 3,200 |
| `monitor-off-plan.json` | `f9313762e78be1dfdf03acc018f0800f985a7ebee59cce95a040c3096a331870` | 1,486 |
| `monitor-off-report.json` | `e556a689b6e476639b5914ccfe4dcb3178e9c7e55ecf124dccd06e0bb2291749` | 1,073 |
| `monitor-on-capture.pcm` | `8bd5917d21004e7fe2143c04dfd2f20f9d546c993cd4cde41b4cb6be5b012aed` | 3,200 |
| `monitor-on-plan.json` | `f32c69ed0a583474bc3df19e1e1f7126055dcbf2df5e087815f5080094799503` | 1,485 |
| `monitor-on-report.json` | `5df0c3aba43536c3038a5c0f42f76070caaa6ab2c83a91724194666eb2624798` | 1,077 |
| `monitor-on-sink.pcm` | `8bd5917d21004e7fe2143c04dfd2f20f9d546c993cd4cde41b4cb6be5b012aed` | 3,200 |
| `monitor-xrun-report.json` | `10460d5991aaffd25bae7fe3ea63f7e6cdc5a0f6e25699b15d3540e3781e7b95` | 1,077 |
| `monitor-xrun-sink.pcm` | `137d1a6ff36272831d0a297e909b4078d515fe0373b72f92caac7fc2dc3daa35` | 2,176 |
| `project.musica.zip` | `86d60316909c102a814f5802fa92f9419fadb26323bc3ccc346fb75c0f2527b5` | 38,117 |
| `proof.json` | `c76b3b5d41316fee4ca00cfc22c038787147842c1c3a92119c4071697c7037c0` | 1,397 |
| `recording-finalize-preview.json` | `bc78815cad56150d3e39692cfc77543aa33018d1d3622ed69b237ca661d17771` | 1,491 |

The artifact contract inventory was independently checked against the exact GitHub implementation head. All **9/9** schema/source/test/workflow files matched recorded SHA-256 and byte size.

The nested `project.musica.zip` contains **18** content-addressed object files; all **18/18** object contents matched their SHA-256 object names. Project refs for HEAD and `main` were present.

## Monitoring plan/report self-hash verification

Using MUSICA canonical JSON encoding, all independently recomputed plan/report self-hashes matched exactly:

- monitor OFF plan: `a67ad2fb843ac70b358eeb45d557181150b2355be4b086399bec4657d1e336f0`
- monitor ON plan: `1b203d03a076afb94c24cc14d860f10342cf53f0f8764bef63692ac2ac9a6e83`
- monitor OFF report: `862cae22f0e3ab820b14db1bbb85fb684f45f5cda0b328eaee2075ecafa3409f`
- monitor ON report: `bce501c10e4f5c589641e7108afe36a77f88b55c2a9728c9e43fdf5ea6fab6bb`
- monitor xrun report: `c762c02f39ebed62210f599c2c6ba954c741d55ee0f8fb900e642a61d77d174a`
- capture-failure monitor report: `976484cb8fdee0569db7bbc2fb025410798a30c647dab0359dafb7735559332f`

## Frozen bounded monitoring semantics

REC-R2 v0 deliberately uses the narrowest exact-match path:

```text
REC-R0 simulated stereo input block
→ capture backend records exact PCM block
→ copy of returned captured block
→ REC-R2 direct monitor tap
→ validated RTIO simulated stereo output backend
```

The plan freezes:

- simulated input backend only;
- validated simulated output backend only;
- PCM16 little-endian;
- exact stereo only;
- exact sample-rate match;
- exact block-size compatibility;
- no resampling;
- direct post-capture-copy tap;
- unity-only monitoring in v0;
- no plugins/effects/latency compensation;
- monitor state and sink output non-canonical.

Stereo-only is intentional because the existing validated simulated output backend supports exactly two output channels. Mono monitoring therefore fails closed rather than inventing an unvalidated channel conversion.

## Capture isolation proof

For the same accepted revision and input configuration:

```text
monitor OFF capture SHA = 8bd5917d...12aed
monitor ON  capture SHA = 8bd5917d...12aed
clean monitor sink SHA  = 8bd5917d...12aed
```

All three payloads are **3,200 bytes**.

The OFF and ON runs also reproduce the exact same REC-R0 capture plan, capture block trace and capture report.

This proves that enabling monitoring does not modify captured recording bytes.

## Monitor-only xrun isolation proof

A deterministic monitor-output xrun was injected at exactly one block.

Capture state remained unchanged:

- capture PCM SHA stayed `8bd5917d...12aed`;
- capture report remained exact;
- captured frames stayed **800**;
- capture error/short-fill/late/dropout-equivalent counts remained zero.

Only monitor output changed:

- monitor output xrun count: **1**
- clean sink bytes: **3,200**
- xrun sink bytes: **2,176**
- clean sink SHA: `8bd5917d...12aed`
- xrun sink SHA: `137d1a6f...daa35`

This proves monitor-output failure cannot reverse-modify captured PCM.

## Capture failure correlation proof

One deterministic input ERROR, one SHORT_FILL and one LATE block were injected.

Exact capture metrics:

- error count: **1**
- short-fill count: **1**
- late count: **1**
- dropout-equivalent count: **3**
- captured frames: **416**
- payload bytes: **1,664**

Exact monitor correlation:

- input-error monitor drop count: **1**
- input-short-fill count: **1**
- input-late count: **1**
- monitor output xrun count: **0**
- monitored frames: **416**
- monitor payload equals the actually captured failure payload

No hidden padding, replay, repair or synthetic replacement is performed.

## REC-R1 authority compatibility

A clean monitored capture is passed to REC-R1 using its original `SimulatedCaptureRun`.

The existing REC-R1 finalize Preview reports:

- `READY_FOR_PREVIEW`;
- exact source Blueprint/audio/routing/automation hashes;
- exact capture-plan/report/payload hashes;
- prospective immutable asset identity;
- destination stable track/clip IDs;
- explicit Accept required;
- project/asset mutation unauthorized during Preview.

Explicit REC-R1 Accept alone advances accepted HEAD exactly once.

REC-R2 therefore does not create a second recording-accept authority. Monitoring remains runtime-only; capture promotion continues exclusively through REC-R1 Preview→Accept.

## Restart/reopen exactness

After the explicit recording Accept, the project was exported/imported and the original source revision was used to reconstruct the monitoring runtime.

Reopen reproduced exactly:

- monitoring plan;
- REC-R0 capture plan;
- capture trace;
- capture PCM;
- capture report;
- monitor trace;
- monitor sink PCM;
- monitoring report.

Project integrity passed after reopen.

Transient monitoring runtime itself is not persisted as creative state; it is deterministically reconstructed from accepted source + explicit configuration.

## Proven fail-closed behavior

The dedicated regression suite proves:

- mono monitoring is rejected because validated output is stereo-only;
- unsupported sample rate is rejected;
- monitor-xrun injection while monitoring is disabled is rejected;
- invalid REC-R0 input config remains fail-closed;
- monitor runtime never changes accepted Project HEAD;
- monitor output xrun cannot change capture bytes/report;
- dirty/incomplete capture remains subject to unchanged REC-R1 finalize validation.

## Authority boundary

```text
accepted revision
+ explicit REC-R0 input config
→ derived REC-R0 capture plan/runtime
→ exact captured PCM
   └→ copy-only REC-R2 monitor runtime → derived monitor sink/metrics

clean capture
→ unchanged REC-R1 finalize Preview
→ explicit REC-R1 Accept
→ accepted immutable recording asset + track/clip revision
```

The following remain non-canonical:

- monitor enabled/disabled state;
- monitor plan;
- monitor trace;
- monitor sink bytes;
- monitor xrun metrics;
- capture runtime counters;
- captured PCM before REC-R1 Accept.

## Explicit non-claims

This validation does not claim:

- Browser recording/monitoring UI;
- host-native microphone/line input;
- host-native speaker monitoring;
- measured host-native monitoring latency;
- zero-latency/hardware monitoring;
- monitor gain DSP beyond unity;
- plugin/effect monitoring;
- take/comp workflows;
- punch-in/out;
- plugin hosting or PDC;
- sidechains;
- resampling;
- generalized commercial recording readiness.

## Validation verdict

> **VALIDATED — BOUNDED DETERMINISTIC INPUT MONITORING & CAPTURE/DROPOUT INSTRUMENTATION v0**

Maximum supported claim:

> **MUSICA can run a bounded deterministic input-monitoring path from the same provenance-bound simulated input used for capture, keep monitoring strictly runtime-only, prove monitoring does not alter captured recording bytes, and deterministically instrument capture/monitor failures while preserving REC-R1 finalize authority.**

Promotion remains conditional on all **31** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #149 completion and separate state-only closure to REC-R3.

Repository evidence remains authoritative over conversation/model memory.
