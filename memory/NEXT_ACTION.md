# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**PLUG-R2 — BOUNDED LATENCY PLANNING, COMPENSATION AND BYPASS/FAILURE CONTAINMENT v0**

- Issue #162 — **OPEN**
- Parent #155 — Plugin Hosting & Latency Compensation Foundation v0 — **OPEN**
- PLUG-R1 Issue #159 — **COMPLETED**
- PLUG-R1 implementation PR #161 — **MERGED**
- canonical main after PLUG-R1: `d509406c49f423c5a53825a66aff0b4f0b922ecb`
- R1 evidence head: `2130960e572b0e22b2618450add8a803b34d331d` — **34/34 SUCCESS**
- validation successor: `276187c8bffda4fb72616043945ae4c2c31423d1` — **34/34 SUCCESS**
- durable validation: `evidence/PLUG_R1_VALIDATION.md`
- independent original artifact ID: `11828934691`
- original artifact SHA-256:
  `90a6032126eb3fc9b7eeeb8ce71e504d90f428fc5ddf77ec1b7d1c2624312170`
- permanent workflows today: **34**, expected after R2: **35**.

## Inherited invariants

PLUG-R1 accepts only a stable, bounded simulated reference plugin chain on the accepted master node through source-bound Preview→explicit Accept. Plugin execution plan and processed audio are derived only. Generic commits cannot mutate accepted plugin state. Bypass/empty results are byte-exact to routed baseline; an injected processor failure never changes accepted HEAD or plugin material. MRAM accepted routing, RTIO derived realtime runtime and REC accepted recording remain authoritative in their own validated scopes.

## Critical R2 design gate: latency is not automatically compensation

The R1 simulated `delay_frames` contributes a real effective serial processing delay. A single post-master serial chain has no parallel dry branch requiring path equalization. Consequently, measuring this latency is **not** proof of multi-path PDC.

Before writing code, settle and document:

1. Which frames represent algorithmic processing latency versus a deliberate creative signal delay?
2. For each supported topology, which path/clock is the reference, and is the proposed correction causal?
3. Is a bound-reference presentation/alignment policy enough for v0, or must owner/topology scope extend to the smallest provable two-path signal flow?
4. Which states make compensation impossible or unsupported and must fail closed?

Do not claim nontrivial compensation unless numerical audio output demonstrates it. Never erase intentional creative delay or look ahead to nonexistent live input.

## Dependency-safe implementation order

1. **Inspect source contracts.** Read `plugin_reference.py`, `plugin_edit.py`, `routed_mixer.py`, `project.py`, accepted routing and plugin schemas plus R1 durable proof.
2. **Decide bounded topology.** Freeze exactly which serial/path forms can be aligned. Document ledger-only cases separately from actual compensation.
3. **Schema + provenance.** Specify a versioned derived plan with stable instance/slot IDs, accepted Blueprint/audio/routing/automation/plugin hashes, exact sample rate/channel, explicit latency components, compensation offsets and recomputable plan self-hash.
4. **Deterministic planner.** Reject unknown owners/instances, duplicate slots, malformed or unsupported latency, overflow, incompatible routing and ambiguous paths.
5. **Causal execution.** Realize only documented supported offline/reference alignment, retaining deterministic sample counts and frame identities. No hidden resampling/channel conversion.
6. **Bypass/remove and failure.** Bypassed/removed instances provide no residual plugin latency or stale buffers. Processor failure reports a hard derived error; no implicit fallback or accepted Project mutation.
7. **Authority.** Preserve exact-source R1 Preview→Accept, generic plugin delta gate and HEAD non-mutation from derived runtime/output.
8. **Regression matrix.** Baseline, active chain, distinct latency, controlled state change, bypass/remove, forced error, invalid plan/tampering, reopen and the first nontrivial aligned reference-path case if PDC is claimed.
9. **Independent numeric evidence.** Verify exact PCM frames and latency offsets against a separately calculated reference, not hashes alone.
10. **Permanent workflow.** Add `PLUG-R2` evidence workflow as 35th gate with deterministic dual-run payload comparison, independent manifest and audio inspection.
11. **Promotion.** Exact implementation/evidence head **35/35 SUCCESS** → independent artifact verification → durable `evidence/PLUG_R2_VALIDATION.md` → exact successor **35/35 SUCCESS** → expected-head squash merge → Issue #162 completed → separate state-only closure to PLUG-R3.

## R2 prohibited shortcuts

- No unproven generic arbitrary-graph PDC claim from single serial delay metadata.
- No silent auto-bypass or accepted-state mutation after errors.
- No real VST3/CLAP/AU host or sandbox claim.
- No false portability, resampling or third-party compatibility claim.
- No relaxation of existing 34 workflows to obtain a green status.

## Maximum intended R2 outcome

> **MUSICA derives exact bounded latency and causal compensation decisions from accepted plugin/routing authority, applies and numerically proves alignment only for supported topologies, maintains explicit bypass and fail-closed processing semantics, and preserves byte-exact accepted-source/reopen identity without allowing runtime or processed audio to reverse-author creative state.**

This remains a target, not a validated R2 claim, until evidence and promotion complete.

**Repository evidence remains authoritative over conversation/model memory.**
