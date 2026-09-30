# REC-R1 Validation — Trusted Captured-Asset Finalize & Recording Preview/Accept Authority v0

## Scope

Issue #146 under parent Issue #142.

REC-R1 crosses the authority boundary intentionally left open by REC-R0. A completed derived capture may become accepted project media only through a typed source-bound recording-finalize candidate, non-mutating Preview and explicit trusted Accept.

The accepted creative state remains the Project/Blueprint revision. Capture runtime, raw captured PCM, capture reports, Preview objects, immutable asset resources by themselves and rendered audio remain non-canonical.

## Evidence-bearing implementation head

- exact implementation/evidence head: `023db631c827ebbea6068f0709ce57d341fde8e3`
- permanent workflow count: **30**
- exact-head result: **30/30 SUCCESS**
- dedicated workflow: **REC-R1 Recording Finalize Evidence**
- dedicated run: `36657402543` — **SUCCESS**
- artifact ID: `11072283272`
- artifact name: `musica-rec-r1-recording-finalize-evidence`
- artifact ZIP SHA-256: `5b4047fb3471e7a082143f2b4098ec497a39bd3c89fa0729ce42673065d3699f`
- artifact ZIP size: **36,363 bytes**

All 30 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The GitHub artifact declared digest and byte size matched the independently downloaded ZIP exactly.

The artifact contains **15 manifest-declared payload files plus `manifest.json`**. Every declared payload matched its manifest SHA-256 and byte size:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `accepted-audio-material.json` | `7f80f890554fc78d2e642edec26a07f7bedc9fa7d14a07177a5e40ff93f16d37` | 898 |
| `accepted-recording-asset.json` | `375339186089f78d8ba5c4a79cefbe70bcae2f18fb1a29026fc1e02e5ab86780` | 383 |
| `accepted-routed-plan.json` | `8633b6e8985b2eb486c88bce6d15c1044b79185c67db81699ae682712134fe48` | 4,107 |
| `accepted-routed.wav` | `3f4b3a4580a812da6e1b719a58d33a8e0fd0e69550215d08fb18be1ce9e09807` | 384,044 |
| `baseline-routed-plan.json` | `722a0be89f3b792cca3b869f2bb24df45932ae0431bb9b3a16ee4a4c37d7c29f` | 3,634 |
| `baseline-routed.wav` | `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4` | 384,044 |
| `capture-plan.json` | `7bbbbab44b0269c0f505cd16dc5089056ee5efc0656784d6a312c572e5f7d812` | 1,378 |
| `capture-report.json` | `6b160b2e6dabffd90a679f54370f53f3386cce8b75dbc6a5144115f6ce274100` | 951 |
| `captured-input.pcm` | `1bd57886e1faa51df981377c11be2217157c3fa4e93c7c29c356bee6faac0347` | 1,600 |
| `contract-hashes.json` | `396af5d801633618dd4477a3e901bfaf2c71875f873c2e4364850e3f3f64cdf7` | 1,177 |
| `finalized-recording.wav` | `3b66cbc7e7b4ee7af3a16c10562e0bd3b9a6cdf2208f8b5afd979eff6d6c3cc7` | 1,644 |
| `project.musica.zip` | `1b60e808b0797ef4f34908cea8b1bf5d1d96df2e2a4e410027d27e6b6867f4f2` | 36,480 |
| `proof.json` | `922bf9972e4cd62b0b3f36c39aedba2cf4bade2f527c902a530e2a97ea6c7ce1` | 1,152 |
| `recording-candidate.json` | `e1664e04a7bb9bab9aa89684071b72f7b9c5dc7925d61a84228b9546496a3c1f` | 1,225 |
| `recording-preview.json` | `1a1095db20bda9ac9b178a58a21ea220863691eed1fd8679414e0699c162348f` | 1,482 |

The evidence contract inventory was independently compared against the exact GitHub implementation head. All **8/8** schema, implementation, test and workflow files matched both recorded SHA-256 and byte size.

## Capture plan/report self-hash verification

Using MUSICA canonical JSON encoding, including the canonical trailing newline, the derived capture identities independently recomputed exactly:

- capture plan:
  `8257993ce4166dbc18ddd9878a88ba2f1d192291648b86e134a97f55344aeb95`
- capture run report:
  `3ff0dd8f4d9ac72332b4d6a9810d7b1d31f45e15075c2fa0604cc935212a7215`

The evidence fixture is:

- sample format: **PCM16 little-endian**
- channels: **1**
- sample rate: **8,000 Hz**
- captured frames: **800**
- captured duration: **0.1 seconds**
- raw payload bytes: **1,600**
- raw payload SHA-256:
  `1bd57886e1faa51df981377c11be2217157c3fa4e93c7c29c356bee6faac0347`

## Deterministic PCM → WAV finalize proof

REC-R1 wraps the exact captured PCM16 payload into one deterministic WAV container.

Independent WAV parsing proved:

- channels: **1**
- sample width: **2 bytes**
- sample rate: **8,000 Hz**
- frames: **800**
- compression: **NONE / PCM**
- WAV SHA-256:
  `3b66cbc7e7b4ee7af3a16c10562e0bd3b9a6cdf2208f8b5afd979eff6d6c3cc7`
- WAV PCM frame payload equals `captured-input.pcm` **byte-for-byte**

Therefore the finalize path performs containerization only. It does not resample, gain-process, pad, truncate or reinterpret channels.

The accepted immutable asset identity is exactly:

```text
sha256:3b66cbc7e7b4ee7af3a16c10562e0bd3b9a6cdf2208f8b5afd979eff6d6c3cc7
```

with descriptor:

- media type: `audio/wav`
- mono PCM integer
- sample width: 2 bytes
- rate: 8,000 Hz
- frames: 800
- duration: 0.1 s
- asset bytes: 1,644

## Source-bound Preview authority

The evidence candidate binds the exact accepted source:

- project ID;
- revision ID;
- Blueprint SHA;
- audio-material SHA;
- routing-material SHA;
- automation-material SHA;
- capture-plan SHA;
- capture-report SHA;
- captured payload SHA/size/rate/channels/frame count/format;
- destination track ID;
- new clip ID;
- timeline placement;
- actor/reason;
- `preview_only=true`.

The Preview proves:

- authority status `READY_FOR_PREVIEW`;
- accepted HEAD unchanged;
- project asset store unchanged;
- asset mutation not authorized by Preview;
- project mutation not authorized by Preview;
- explicit Accept required;
- prospective WAV SHA and prospective immutable asset ID are known deterministically before mutation.

## Explicit Accept and accepted recording identity

Only after exact source/capture/candidate revalidation does Accept write or reuse the immutable asset and commit accepted audio material.

The accepted recording is exactly:

```text
track_id: AT-001
clip_id: REC-CLIP-001
asset_id: sha256:3b66cbc7e7b4ee7af3a16c10562e0bd3b9a6cdf2208f8b5afd979eff6d6c3cc7
timeline_start_seconds: 0.2
source_in_seconds: 0.0
source_out_seconds: 0.1
gain_db: 0.0
```

The accepted revision advances exactly once from:

```text
rev-001-audio-c3fe9eab5b5cad96-routing-aedc233a8ba23101
```

to:

```text
rev-001-audio-c3fe9eab5b5cad96-routing-aedc233a8ba23101-recording-e1664e04a7bb9bab
```

A second Accept of the same Preview fails closed.

## Generic bypass and resource/authority separation

REC-R1 proves two independent boundaries:

1. before the prospective asset exists, generic commit fails because the referenced audio asset is missing;
2. even if the same deterministic WAV bytes are independently imported into the project object/asset store, generic `commit_revision()` still cannot introduce the recording clip because accepted audio-material changes require trusted audio/recording Preview→Accept authority.

Therefore:

```text
asset resource presence ≠ accepted creative authority
capture report ≠ accepted creative authority
runtime buffer ≠ accepted creative authority
Preview object ≠ accepted creative authority
```

## Fail-closed matrix

Dedicated regressions and evidence prove rejection of:

- captured payload byte tamper;
- capture-plan tamper / self-hash mismatch;
- capture-report tamper / self-hash mismatch;
- failed/short-fill capture;
- candidate capture-binding mismatch;
- stale Preview after another accepted HEAD advance;
- same Preview second Accept;
- missing destination track;
- duplicate clip ID;
- destination track/capture sample-rate mismatch under the no-resampling policy;
- generic commit bypass.

Discarding an otherwise READY candidate is a no-op: accepted HEAD and accepted asset inventory remain unchanged.

## Downstream audible/render proof

The recording is placed on an already audible routed track, so accepted creative state changes deterministic downstream output.

Independent routed-plan self-hashes recomputed exactly:

- baseline routed plan:
  `011c9f08350a4abd1999ac261b0c51498033eeabb8125b4c9e101f22d0d0bc0a`
- accepted-recording routed plan:
  `4e41f2bb443d95da2cced5e681bdb36a11e30e4df6d52863342355a94a729f8a`

Routed WAV identities change:

- baseline:
  `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4`
- after accepted recording:
  `3f4b3a4580a812da6e1b719a58d33a8e0fd0e69550215d08fb18be1ce9e09807`

Both are valid deterministic stereo PCM16, 8,000 Hz, 96,000-frame routed renders.

## Project archive and reopen integrity

The nested `project.musica.zip` independently matched its manifest digest:

- SHA-256:
  `1b60e808b0797ef4f34908cea8b1bf5d1d96df2e2a4e410027d27e6b6867f4f2`
- bytes: **36,480**

Independent archive inspection found **18** content-addressed object files and all **18/18** object contents matched their SHA-256 object names.

The persisted main ref points to the accepted recording revision.

Export/import reopen proves exact preservation of:

- accepted audio material;
- immutable audio asset inventory;
- destination track/clip/asset identities;
- routed plan;
- routed WAV;
- full Project integrity.

## Authority boundary

The validated REC-R1 authority chain is:

```text
accepted Project revision
+ completed validated REC-R0 capture
→ typed source-bound recording-finalize candidate
→ Preview
→ accepted HEAD + asset store unchanged
→ explicit trusted Accept
→ revalidate accepted source + capture plan/report/payload + destination
→ deterministic immutable WAV asset
→ trusted audio-material commit
→ exactly one accepted recording revision
→ deterministic routed execution
```

The following remain non-canonical:

```text
capture runtime
captured PCM by itself
capture plan/report
immutable asset resource by itself
Preview object
routed plan
rendered WAV
```

None can reverse-author accepted creative state.

## Compatibility

REC-R1 reuses rather than replaces the existing ATCM immutable audio-asset and accepted audio-material authority.

Existing audio tracks/clips/routing remain intact, and the complete repository regression set remained green on the exact evidence-bearing head.

## Explicit non-claims

This validation does not claim:

- Browser recording UI;
- live input monitoring;
- take/comp management;
- punch-in/out recording;
- host-native microphone/line input;
- measured host-native input or monitoring latency;
- automatic resampling;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- sidechains;
- generalized commercial recording readiness.

## Validation verdict

> **VALIDATED — TRUSTED CAPTURED-ASSET FINALIZE & RECORDING PREVIEW/ACCEPT AUTHORITY v0**

Maximum supported claim:

> **MUSICA can finalize a validated derived capture into immutable content-addressed project media and place it into stable accepted track/clip state only through a source-bound Preview→explicit Accept recording authority, while stale, tampered, bypass, incompatible and discard paths remain fail-closed.**

Promotion remains conditional on all **30** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #146 completion and separate state-only closure pointing to REC-R2.

Repository evidence remains authoritative over conversation/model memory.
