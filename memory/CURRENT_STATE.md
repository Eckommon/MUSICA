# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → NATIVE AUDIO FOUNDATION COMPLETED → MIXER ROUTING & AUTOMATION FOUNDATION COMPLETED → REAL-TIME AUDIO ENGINE & DEVICE FOUNDATION COMPLETED → RECORDING & MONITORING FOUNDATION IN PROGRESS**

Long-term target: MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving AI-native authority, inspectability, reproducibility and programmability. This is a product target, not a claim of current full-DAW completeness.

## Completed bounded foundations

- Issue #95 — Audio Track / Clip / Mixer Foundation v0 — COMPLETED, ATCM R0→R4 validated.
- Issue #115 — Mixer Routing & Automation Foundation v0 — COMPLETED, MRAM R0→R3 validated.
- Issue #129 — Real-Time Audio Engine & Device Foundation v0 — COMPLETED, RTIO R0→R3 validated under the bounded simulated/test backend.

RTIO-R3 final implementation merge/main: a7ed3f1fcf545fd01dcda020d808fd0f4b9d4294
Durable validation: evidence/RTIO_R3_VALIDATION.md

## Current commercial-workstation mission

Parent Issue #142 — Recording & Monitoring Foundation v0 — OPEN

Selected rung sequence:

REC-R0 input/capture contracts + deterministic simulated input — VALIDATED
REC-R1 trusted captured-asset finalize + Preview/Accept — VALIDATED
REC-R2 bounded input monitoring + capture/dropout instrumentation — CURRENT
REC-R3 Studio/Browser recording + monitoring + restart/reopen
parent #142 bounded closure evaluation

## REC-R0 — validated deterministic input/capture substrate

Issue #143 — COMPLETED
PR #145 — MERGED
Canonical implementation merge/main: fce2797639258ec32418c13fb56bb9266f818b20
Durable validation: evidence/REC_R0_VALIDATION.md

Key facts:
- implementation/evidence head f8b0f90a852aeb8ba48f361c5ba1844ecb8325ac — 29/29 SUCCESS
- validation successor a4d80c9e5ad9d4038bc26cf87dd6f4abbff0c348 — 29/29 SUCCESS
- artifact ID 11062015980
- artifact ZIP SHA-256 04a9a49aee2a3d719e4de5f97b72e2d3aa9f3607456f984f6c3d3d9049f0f203

REC-R0 established exact simulated input capability/config identity, deterministic fixed-block capture, exact frame progression, derived PCM/report identities and deterministic ERROR/SHORT_FILL/LATE/dropout-equivalent instrumentation without granting capture runtime or payload accepted authority.

## REC-R1 — validated trusted recording-finalize authority

Issue #146 — COMPLETED
PR #148 — MERGED
Canonical implementation merge/main: 284c823fa6b0e29a9abf78f3425054c2339e0bdb
Durable validation: evidence/REC_R1_VALIDATION.md

Promotion facts:
- implementation/evidence exact head 023db631c827ebbea6068f0709ce57d341fde8e3 — 30/30 permanent workflows SUCCESS
- validation-record successor c066136b79919eb28f40b9bddeddc489403f67c4 — 30/30 SUCCESS
- dedicated workflow: REC-R1 Recording Finalize Evidence
- dedicated run 36657402543 — SUCCESS
- artifact ID 11072283272
- artifact ZIP SHA-256 5b4047fb3471e7a082143f2b4098ec497a39bd3c89fa0729ce42673065d3699f
- artifact ZIP size 36,363 bytes
- manifest payloads 15/15 exact SHA-256 + byte-size PASS
- exact Git schema/source/test/workflow inventory 8/8 PASS
- nested Project object store 18/18 content hashes PASS

Validated REC-R1 authority:

accepted Project revision + completed validated REC-R0 capture
→ typed source-bound recording-finalize candidate
→ Preview with accepted HEAD and asset store unchanged
→ explicit trusted Accept
→ exact source/capture/destination revalidation
→ deterministic immutable WAV asset
→ trusted audio-material commit
→ exactly one accepted recording revision
→ deterministic routed execution

Evidence capture:
- PCM16 little-endian, mono, 8,000 Hz, 800 frames, 0.1 seconds
- raw PCM 1,600 bytes, SHA-256 1bd57886e1faa51df981377c11be2217157c3fa4e93c7c29c356bee6faac0347
- finalized WAV 1,644 bytes, SHA-256 3b66cbc7e7b4ee7af3a16c10562e0bd3b9a6cdf2208f8b5afd979eff6d6c3cc7
- finalized WAV PCM payload equals raw capture byte-for-byte; no resampling, gain processing, hidden padding or channel reinterpretation

Accepted placement:
- track AT-001
- clip REC-CLIP-001
- asset sha256:3b66cbc7e7b4ee7af3a16c10562e0bd3b9a6cdf2208f8b5afd979eff6d6c3cc7
- timeline start 0.2 s
- source range 0.0→0.1 s
- gain 0 dB

Independent self-hash checks:
- capture plan 8257993ce4166dbc18ddd9878a88ba2f1d192291648b86e134a97f55344aeb95
- capture report 3ff0dd8f4d9ac72332b4d6a9810d7b1d31f45e15075c2fa0604cc935212a7215
- baseline routed plan 011c9f08350a4abd1999ac261b0c51498033eeabb8125b4c9e101f22d0d0bc0a
- accepted routed plan 4e41f2bb443d95da2cced5e681bdb36a11e30e4df6d52863342355a94a729f8a

Routed WAV changed from 49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4 to 3f4b3a4580a812da6e1b719a58d33a8e0fd0e69550215d08fb18be1ce9e09807 after recording became accepted creative state.

Validated fail-closed behavior:
- generic commit bypass
- same Preview second Accept
- stale Preview after HEAD advance
- captured payload tamper
- capture-plan tamper/self-hash mismatch
- capture-report tamper/self-hash mismatch
- failed/short-fill capture
- candidate capture-binding mismatch
- missing destination track
- duplicate clip ID
- sample-rate mismatch under no-resampling policy
- discard/cancel no mutation

Asset-resource presence alone is not creative authority; accepted audio-material mutation still requires trusted Preview→Accept.

Maximum validated REC-R1 claim:

> MUSICA can finalize a validated derived capture into immutable content-addressed project media and place it into stable accepted track/clip state only through a source-bound Preview→explicit Accept recording authority, while stale, tampered, bypass, incompatible and discard paths remain fail-closed.

## REC-R2 — validated bounded input monitoring + capture/dropout instrumentation

Issue #149 — **COMPLETED**  
PR #151 — **MERGED**  
Canonical implementation merge/main:

> **`4d0e7988b979c05ee7f5a04ed7fb4cb043a2b60e`**

Durable validation: `evidence/REC_R2_VALIDATION.md`

Promotion facts:

- implementation/evidence exact head `ec338120a61e1796a2cecd99aa66126fe6eebe29` — **31/31 permanent workflows SUCCESS**
- validation-record successor `af2a23e120123546a33791b902e685bd9da10738` — **31/31 SUCCESS**
- dedicated workflow: **REC-R2 Monitoring Evidence**
- dedicated run `36685344816` — **SUCCESS**
- artifact ID `11083583035`
- artifact ZIP SHA-256 `fa586bf0239901273eb4dcd77c3839b7a074a5bfd94dea569df96791d8404665`
- artifact ZIP size **40,001 bytes**
- manifest payloads **14/14 exact SHA-256 + byte-size PASS**
- exact Git schema/source/test/workflow inventory **9/9 PASS**
- nested Project object store **18/18 content hashes PASS**
- monitor plan/report self-hashes **6/6 independently recomputed PASS**

Validated REC-R2 execution boundary:

```text
accepted revision + exact simulated stereo input config
→ REC-R0 capture plan/runtime
→ exact captured PCM block
   ├→ capture backend records exact bytes
   └→ copy-only REC-R2 direct monitor tap
      → validated simulated stereo output backend
      → derived monitor sink/metrics
```

Key evidence:

- monitor OFF capture PCM = monitor ON capture PCM = clean monitor sink:
  `8bd5917d21004e7fe2143c04dfd2f20f9d546c993cd4cde41b4cb6be5b012aed`
- each clean payload is **3,200 bytes / 800 stereo frames**
- injected monitor-output xrun count **1** leaves capture PCM/report unchanged
- xrun monitor sink becomes **2,176 bytes**, SHA `137d1a6ff36272831d0a297e909b4078d515fe0373b72f92caac7fc2dc3daa35`
- injected input ERROR + SHORT_FILL + LATE produce exact capture dropout-equivalent count **3**
- monitor correlation counters are exactly **1 / 1 / 1**
- no hidden padding, replay or repair
- clean monitored capture reuses unchanged REC-R1 finalize Preview→explicit Accept authority
- reopen reproduces exact capture/monitor plan, trace, PCM, sink and report

Bounded v0 intentionally supports exact stereo/no-resampling/unity monitoring only because the validated simulated output backend is stereo-only. Mono monitor conversion, monitor DSP and host-native device claims remain outside the validated scope.

Maximum validated REC-R2 claim:

> **MUSICA can run a bounded deterministic input-monitoring path from the same provenance-bound simulated input used for capture, keep monitoring strictly runtime-only, prove monitoring does not alter captured recording bytes, and deterministically instrument capture/monitor failures while preserving REC-R1 finalize authority.**

## Exact current rung / 현재 정확한 단계

> **Issue #152 — REC-R3: Studio/Browser Recording & Monitoring Surface + Restart/Reopen Lifecycle v0 — CURRENT**

REC-R3 must project the already validated REC-R0/R1/R2 recording and monitoring truth into a real Studio/Browser surface without creating Browser-only recording authority.

Required direction:

```text
accepted project revision
→ derived capture/monitor runtime projection
→ Browser recording-finalize proposal
→ existing REC-R1 Preview / HEAD unchanged
→ explicit REC-R1 Accept
→ accepted immutable asset + track/clip
→ fresh service/process restart
→ project reopen
→ accepted recording persists exactly
→ transient capture/monitor state resets
```

The Browser must expose exact source/config/hash identity and runtime-only authority labels, reject stale/unknown handles, and delegate recording finalization to the existing REC-R1 authority rather than adding a direct asset/audio commit path.

## Current non-claims

No host-native microphone/line input, host-native speaker monitoring, measured host-native monitoring latency, zero-latency/hardware monitoring, take/comp, punch-in/out, plugin/effect monitoring, VST3/AU/CLAP hosting, PDC, resampling, sidechains, mastering or generalized commercial recording readiness is validated.

## Exact next phase / 다음 단계

> **Implement Issue #152 from canonical main `4d0e7988b979c05ee7f5a04ed7fb4cb043a2b60e`: re-ground Studio/Browser session and runtime projection patterns, expose truthful REC-R0/R2 capture+monitor inspection, connect a bounded recording-finalize Browser proposal to existing REC-R1 Preview→explicit Accept, prove dirty/stale/discard paths fail closed, then prove fresh service restart + project reopen preserves accepted recording while transient runtime resets.**

See `memory/NEXT_ACTION.md` for the exact execution order.

**Repository evidence remains authoritative over conversation/model memory.**
