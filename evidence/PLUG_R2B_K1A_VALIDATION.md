# PLUG-R2B K1-A Validation — Accepted-Source Two-Bus / Detached Latency Reference

## Verdict / strictly bounded claim

**PASS — K1-A accepted-source, immutable two-bus PCM bridge into detached simulated causal alignment. NOT accepted plugin-host PDC.**

Parent Issue #155; Issue #162; implementation mission Issue #166 remain **OPEN**. PR #168 adds no accepted non-master plugin material, does not approve latency settings, and does not modify the existing legacy master plugin/Project authority.

## Exact evidence-bound implementation

- PR #168: `feature/plug-r2b-k1-accepted-host-contract`
- pre-durable implementation/evidence head: `413afe766f89e336eff12ab0b1de65f35b96a07a`
- permanent workflows: **37/37 SUCCESS** at the above exact commit, including permanent `PLUG-R2B K1 Accepted Two-Bus Detached Reference Evidence`
- dedicated workflow run: `38579986235` — **SUCCESS**
- independent artifact ID: `11902966235`
- ZIP SHA-256 (GitHub declared and independently recomputed): `36c1d62d3f2919d85070b2b3f1e5e821a73bd5efbc3a07299ec1bcf2df897d66`
- artifact ZIP size: **6,488 bytes**
- 8/8 payload hashes and sizes independently recomputed and matched; 8 contract inventory entries verified by the dedicated CI gate.
- The ZIP contains a derived reference record, proof, two source WAVs, uncompensated, compensated, creative-preserved, and bypass-recomputed WAVs.

## Independent numeric audio proof

An actual accepted MUSICA Project revision (audio tracks and trusted routed Preview→Accept) is reopened through the canonical Project object store. Its two separately accepted tracks route to distinct buses, both ending in a neutral master. The bridge reuses native track and bus gain/pan/automation, and quantizes *post-bus/pre-master* float64 into stereo PCM16 at an explicit, nontransparent boundary.

- Both source bus WAVs: **8,000 Hz, stereo PCM16, 96,000 frames**.
- BUS-001 first sample (L/R): **(16384,16384)**; BUS-002 first sample: **(8192,8192)**.
- Detached synthetic algorithmic latency BUS-001 **3** frames and BUS-002 **9** frames.
- Without compensation: first BUS-001 output at frame **3**; at frame **9** the accumulated signal is **(24576,24576)**.
- With causal compensation: prior frames **0–8 zero** and first combined output at frame **9** with **(24576,24576)**. Independently inspected the actual PCM samples, not just planner offsets/hashes.
- Explicit creative delay of **5** on BUS-001: frame **9** contains only BUS-002 **(8192,8192)** and frame **14** contains both **(24576,24576)**.
- BUS-001 bypass recalculates its simulated algorithmic latency to **0** and still produces combined frame **9**.
- Accepted Project HEAD remains unchanged by all derived rendering; negative input owner/rate/error tests reject unsupported execution.
- The permanent workflow compared two separately generated evidence trees byte for byte; reopen validation is covered by the dedicated regression test.

## Explicit remaining gaps

This is **not K1-B**. Synthetic algorithmic latency/creative-delay configurations remain detached inputs, not approved in the canonical Blueprint. The R1 master-only accepted plugin contract remains unchanged. There is no accepted bus plugin Preview→Accept or integrated native routed plugin processing. This work does not demonstrate VST3/AU/CLAP, real plugin latency discovery, sample-accurate native realtime PDC, arbitrary graph processing, UI/editor integration or commercial-grade hosting.

## Promotion condition

The durable validation record is an additional commit, so it is not itself covered by the pre-durable 37/37. Before expected-head squash merging PR #168, require **37/37 SUCCESS on the exact durable-record successor commit**. Independently inspect the successor's workflow identities and retain the artifact evidence provenance. Then merge PR #168, keeping #166/#162/#155 OPEN and start a new branch for K1-B accepted host authority.

**Project evidence is authoritative over claims in a conversation.**
