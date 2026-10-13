# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → NATIVE AUDIO FOUNDATION COMPLETED → MIXER ROUTING & AUTOMATION FOUNDATION COMPLETED → REAL-TIME AUDIO ENGINE & DEVICE FOUNDATION COMPLETED → RECORDING & MONITORING FOUNDATION COMPLETED → PLUGIN HOSTING & LATENCY COMPENSATION FOUNDATION IN PROGRESS**

Long-term governing target:

> **MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving AI-native authority, inspectability, reproducibility and programmability.**

This remains a product target, not a claim that MUSICA is already a complete commercial DAW.

## Completed bounded foundations

- Issue #95 — Audio Track / Clip / Mixer Foundation v0 — **COMPLETED**
- Issue #115 — Mixer Routing & Automation Foundation v0 — **COMPLETED**
- Issue #129 — Real-Time Audio Engine & Device Foundation v0 — **COMPLETED**
- Issue #142 — Recording & Monitoring Foundation v0 — **COMPLETED**

These completed foundations establish accepted native audio assets/tracks/clips, bounded routing and native mixer automation, deterministic routed execution, bounded realtime transport/runtime inspection, deterministic simulated capture/monitoring, trusted recording-finalize Preview→Accept authority and truthful Browser lifecycle surfaces.

## Current commercial-workstation mission

Parent Issue #155 — **Plugin Hosting & Latency Compensation Foundation v0 — OPEN**

Selected rung sequence:

~~~text
PLUG-R0 plugin contracts + deterministic simulated processor        VALIDATED
→ PLUG-R1 trusted plugin state Preview→Accept + accepted execution   CURRENT
→ PLUG-R2 latency compensation + bypass/failure containment
→ PLUG-R3 Studio/Browser plugin inspection + restart/reopen
→ bounded format adapter rung(s) only after host contract validation
→ parent #155 bounded closure evaluation
~~~

## PLUG-R0 — validated detached plugin contract + simulated processor

Issue #156 — **COMPLETED**

Implementation PR #158 — **MERGED**

Canonical implementation merge/main:

> **d978d6fd8faa6885de2e492874ce38e992b58ef2**

Durable validation:

- `evidence/PLUG_R0_VALIDATION.md`
- implementation/evidence exact head:
  `1d3866354bc6f9d30461c4ab73a190f4ca6c473d` — **33/33 permanent workflows SUCCESS**
- validation-record successor:
  `7a98f638306f96959d06879c3a7bb0d65f230f7b` — **33/33 SUCCESS**
- dedicated workflow: **PLUG-R0 Simulated Plugin Processor Evidence**
- dedicated run: `36869366855` — **SUCCESS**
- artifact ID: `11166403201`
- artifact ZIP SHA-256:
  `5fe99e09246747ac4e8a8b2e45d4ef0e82313aa44c01f1a0e4ea88bd040bf018`
- artifact ZIP size: **23,124 bytes**
- manifest payloads: **14/14 exact SHA-256 + byte size PASS**
- exact Git contract/source/test/workflow inventory: **8/8 PASS**
- nested Project object store: **13/13 content-addressed object hashes PASS**
- plugin plan self-hashes independently recomputed:
  - A: `2b8044b02c9349f7fe703f061ac23b3000e5b9e17db652ef4bd8d95f6486b57f`
  - B: `f9bdcce6efc1a3b7b11546fc9919f56aff9f7f138bde3bc0194bdb77f501f221`
  - bypass: `62933f7221ed4d55ab89c8d6c8e10f1788fdd86561c53137f8dcf2a76697d89f`

### Validated PLUG-R0 boundary

R0 intentionally keeps plugin material detached from accepted Blueprint authority:

~~~text
exact accepted routed revision
+ detached non-canonical plugin proposal
→ structural/source validation
→ deterministic plugin processing plan
→ deterministic simulated gain+delay processor
→ derived processed WAV
≠ accepted creative authority
~~~

Validated R0 descriptor/runtime scope:

- format: `simulated_reference_v0`;
- processor: `musica-simulated-gain-delay-v0`;
- stereo input/output;
- exact sample-rate match; no resampling;
- stable plugin and instance IDs;
- owner kind `routing_node`;
- exact accepted master node only;
- deterministic serial slot ordering;
- `gain_db` range -60 dB to +12 dB;
- `delay_frames` range 0 to 4096;
- explicit bypass;
- effective latency equals non-bypassed fixed delay frames.

The R0 execution stage is explicitly:

> `post_routed_master_pcm16_reference_stage`

This is a bounded deterministic reference stage, not a production third-party insert claim.

### Controlled deterministic proof

Material A and B differ in exactly one state field:

~~~text
PI-001 / gain_db: -6.0 dB → -12.0 dB
~~~

with both using `delay_frames = 4`.

Derived identities change exactly as required:

- material A:
  `cae2d837fa10aebb65a1e16f50e3f128c8316ca68e060b04cb98c066ead79021`
- material B:
  `ada37eb1c3c7df7fb77d3bb8adcb1f6785b6ae8a7d0d4a16b5b03bb89af6868a`
- plugin A WAV:
  `1a813b90fdb38ab79c24f383e58167d8480f347ce6a04c8233ca5ef493a3c627`
- plugin B WAV:
  `7bebd2f8b2867214e0c7516427c2e20a90dac16a58508e3cc00d01f9132c0305`

Independent numeric inspection confirms the -12 dB output is approximately 0.50116× the -6 dB output at corresponding nonzero PCM16 samples, matching the theoretical 6 dB amplitude ratio within quantization error.

The bypass fixture deliberately uses non-neutral state:

~~~text
gain_db = +12 dB
delay_frames = 128
bypass = true
~~~

but produces byte-exact baseline routed WAV:

`49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4`

with zero effective plugin latency.

### R0 authority and fail-closed behavior

Validated behavior includes:

- accepted Project HEAD remains unchanged by detached plugin processing;
- direct non-empty plugin insertion into accepted Blueprint fails schema/authority validation;
- unknown plugin IDs fail closed;
- duplicate insertion slots fail closed;
- non-master owner placement fails closed;
- non-canonical descriptor parameters fail closed;
- sample-rate mismatch fails closed under no-resampling policy;
- invalid parameter/state shapes fail schema validation;
- forced processor error fails closed without accepted Project mutation;
- processing-plan tampering fails self-hash validation;
- export/import reopen of the exact accepted source reproduces exact plan/output when supplied the same detached validated material.

R0 does **not** claim persistence of plugin material as accepted project state. That authority is the purpose of PLUG-R1.

### Maximum validated PLUG-R0 claim

> **MUSICA can describe stable bounded plugin instances and state as a detached non-canonical proposal, lower them against an exact accepted routed source into a provenance-bearing deterministic simulated processing plan with explicit latency and capability constraints, and reproduce derived processed output exactly while accepted plugin mutation remains closed and runtime/output state remains non-canonical.**

## Exact current rung / 현재 정확한 단계

The current rung is:

> **Issue #159 — PLUG-R1: Trusted Plugin State Preview→Accept & Accepted Offline Execution v0**

R1 must promote the proven R0 plugin representation into accepted project authority without opening generic commit or runtime write-back paths.

Required direction:

~~~text
legacy/no-plugin accepted project
→ optional accepted plugin material
→ source-bound plugin edit candidate
→ Preview / accepted HEAD unchanged
→ explicit Accept
→ protected Project Engine plugin commit
→ accepted plugin revision
→ deterministic R0 processing plan/output
→ export/import/reopen exactness
~~~

Initial accepted scope must stay identical to R0: simulated reference gain+delay processor on the exact accepted master routing node only.

## Current important non-claims

Until separately validated, do not claim:

- real VST3/AU/CLAP binary hosting;
- plugin scanning/installation;
- third-party state chunks;
- arbitrary plugin UI embedding;
- production-grade untrusted-binary sandboxing;
- generalized plugin automation;
- arbitrary sidechains/bus negotiation;
- arbitrary-graph latency compensation;
- implicit sample-rate conversion;
- commercial third-party plugin compatibility;
- mastering-grade processing;
- generalized commercial release readiness;
- cloud/multi-user creative authority.

## Exact next phase / 다음 단계

> **Implement Issue #159 from canonical main `d978d6fd8faa6885de2e492874ce38e992b58ef2`: add a backward-compatible accepted plugin-material shape, freeze deterministic empty-material/source hashing, implement source-bound typed plugin edit Preview→Accept with a protected Project Engine plugin delta gate, preserve the exact R0 master-only gain+delay semantics, and prove accepted plugin insertion/state/bypass/remove plus deterministic offline output and reopen exactness before moving to latency compensation.**

See `memory/NEXT_ACTION.md` for the exact execution order.

**Repository evidence remains authoritative over conversation/model memory.**
