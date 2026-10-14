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
→ PLUG-R1 trusted plugin state Preview→Accept + accepted execution   VALIDATED
→ PLUG-R2 latency compensation + bypass/failure containment         CURRENT
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

## PLUG-R1 — validated accepted plugin state and deterministic execution

Issue #159 — **COMPLETED**; implementation PR #161 — **MERGED**.

Canonical implementation merge/main:

> **d509406c49f423c5a53825a66aff0b4f0b922ecb**

Durable validation:

- `evidence/PLUG_R1_VALIDATION.md`
- implementation/evidence exact head:
  `2130960e572b0e22b2618450add8a803b34d331d` — **34/34 SUCCESS**
- final validation-successor head including Browser Compare concurrency repair:
  `276187c8bffda4fb72616043945ae4c2c31423d1` — **34/34 SUCCESS**
- dedicated workflow: **PLUG-R1 Accepted Plugin Authority Evidence**
- original independently inspected run/artifact: `38428999804` / `11828934691`
- validated original artifact ZIP SHA-256:
  `90a6032126eb3fc9b7eeeb8ce71e504d90f428fc5ddf77ec1b7d1c2624312170`
- original artifact payloads **16/16** exact, source inventory **11/11**, archive content-addressed objects **19/19**, plugin plan self-hashes **4/4**.
- final successor Browser Compare regression on the same exact head: **SUCCESS**; concurrent fallback-media requests reuse stable render state without modifying accepted HEAD.

### Validated R1 authority

~~~text
exact accepted project/revision/Blueprint/audio/routing/automation/plugin hashes
→ source-bound plugin edit candidate (ADD/REMOVE/SET_STATE/SET_BYPASS)
→ Preview / accepted HEAD unchanged
→ explicit Accept with persisted-source revalidation
→ protected plugin-authorized Project commit
→ immutable accepted plugin material
→ deterministic R0-derived plan and processed WAV
→ export/import/reopen reproduces accepted material, plan and WAV
~~~

Accepted plugin material is classified `accepted_plugin_material`; legacy projects and absent/empty plugin material remain valid. The initial scope is the R0 reference plugin (`simulated_reference_v0`, `musica-simulated-gain-delay-v0`) on the exact accepted master node only.

Numerical proof: the controlled `gain_db` state change `-6 → -12 dB` yields approximately **0.501** peak-amplitude ratio, and active instances provide exactly **4 latency frames**. Both accepted bypass and last-instance removal return **byte-exact** routed baseline WAV with zero effective plugin latency. Generic commits, stale/forged previews, runtime plans and processor failures do not gain accepted-authority write access.

### Maximum validated PLUG-R1 claim

> **MUSICA can accept and persist bounded simulated plugin instances/state only through source-bound Preview→Accept authority, deterministically execute the exact accepted plugin state over its accepted routed source, and reproduce accepted plugin identity plus derived plan/output after reopen while generic commit, stale/forged source, processor runtime and processed-output paths remain non-authoritative.**

## Exact current rung / 현재 정확한 단계

> **Issue #162 — PLUG-R2: bounded latency planning, compensation and bypass/failure containment v0 — OPEN.**

PLUG-R2 must first separate algorithmic processing latency, audible creative delay and presentation/reference alignment. R1's master-only serial plugin chain proves latency **accounting**, not nontrivial multi-path delay **compensation**. Do not promote an audible compensation claim without an independently checked, numerically aligned nontrivial reference-path or bounded multi-path proof.

Required direction:

~~~text
accepted plugin/routing source and stable instance/slot identities
→ exact source-bound, self-hashed derived latency plan
→ explicit causal/bypass/error policy
→ minimal supported alignment topology
→ numerical frame-alignment proof (if compensation claimed)
→ accepted-state/HEAD invariants and reopen exactness
~~~

## Current important non-claims

Until separately validated, do not claim:

- real VST3/AU/CLAP binary hosting, scanning/installation or third-party state chunks;
- arbitrary plugin UI embedding or production-grade untrusted-binary sandboxing;
- generalized plugin automation, arbitrary sidechains/bus negotiation or arbitrary-graph PDC;
- sample-rate conversion, commercial third-party plugin compatibility or mastering-grade processing;
- generalized commercial release readiness, cloud or multi-user creative authority.

## Exact next phase / 다음 단계

> **Start Issue #162 from canonical main `d509406c49f423c5a53825a66aff0b4f0b922ecb`: freeze the precise latency taxonomy and minimal compensatable topology, implement bounded deterministic derived latency planning with explicit bypass/failure semantics, and prove actual frame alignment before claiming compensation. Maintain all 34 existing permanent workflows and add the 35th PLUG-R2 evidence gate.**

See `memory/NEXT_ACTION.md` for execution order. Repository evidence remains authoritative over conversation/model memory.
