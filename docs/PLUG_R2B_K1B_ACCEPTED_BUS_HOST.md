# PLUG-R2B K1-B — Accepted Simulated Bus Processor Authority & Offline PDC

**Status: IMPLEMENTATION CANDIDATE, NOT VALIDATED OR PROMOTED.** Issues #166, #162, #155 remain OPEN. Predecessor K1-A PR #168 merged to canonical `58c7c6ebe8be6f990ecd21125293c61c815939d1`.

## Creative authority: new distinct canonical material

The optional `materials.bus_plugins` is a **separate** accepted versioned material, not a relaxation of legacy R1 `materials.plugins` (master-only). The existing `delay_frames` remains creative reference signal delay, unchanged.

Each K1-B bus instance declares:
- stable `instance_id`, stable exact `owner_bus_id`, fixed `owner_kind=routing_node` and `slot=0`;
- fixed simulated processor identity/version `musica-simulated-bus-latency-v0` / `0`, with `latency_provenance=accepted_explicit_simulated_reference`;
- **separate** accepted `algorithmic_latency_frames` (simulated processor delay, **not** discovered from any VST3/CLAP/AU binary), `creative_delay_frames` (intentional independent path delay), and `bypass` (disables algorithmic processing delay but does not erase independently accepted creative path delay).

Exactly two accepted tracks must route to distinct named bus nodes -> one neutral master with no sends/sidechains for the supported K1-B execution. Optional host instances are at most one per bus; empty materials are valid on legacy projects. Nonempty legacy master plugin chain and K1-B bus inserts cannot be combined in this bounded version.

## Trust and acceptance

- `bus_host_edit.build_bus_host_edit_preview` requires an exact persisted Project revision, matching HEAD and exact project/revision/Blueprint/audio/routing/automation/R1 legacy plugin/current bus material hashes. It validates the complete proposed host material, stable owner slots, accepted two-bus topology and inherited revision locks without writing Project state.
- **Only** `accept_bus_host_edit_preview` performs explicit source-bound Accept through a new independently denied `allow_bus_plugin_material_change` Project gate. Generic commits are blocked for changes to this material. A forged/stale/tampered preview, unknown bus or unsupported processor fails closed.
- Changing/removing/bypassing an instance creates a new accepted immutable revision; derived runtime plans and WAV never write back into that canonical material.

## Bounded offline audio execution

`render_accepted_simulated_bus_host` reads the exact persisted accepted bus processor state and calls the accepted-source K1-A bridge with derived internal configuration. The caller **cannot inject** an arbitrary latency profile or unaccepted WAV at the host execution entrypoint.

For nonempty supported states, the reference processes each post-bus, pre-master stereo PCM16 path through a simulated causal processor and computes `C_i=max(L_A,L_B)-L_i` using accepted simulated algorithmic processing latency (bypass => `L_i=0`). Creative path delay is preserved independently. Fixed output duration and tail truncation are intentional. Intermediate float64 -> PCM16 quantization occurs before mixing and differs from legacy float64 master behavior; it is not hidden.

For **empty** accepted bus processor state, the host bypasses K1-A quantization and returns the **exact legacy routed WAV bytes**. Unsupported topology, stale source, unsupported rate/channel, unknown owner or injected active processor failure aborts derived rendering. There is no silent fallback after errors.

## Test and promotion gates

Permanent CI #38 must include K1-B trusted Preview/Accept/Project-gate regressions, accepted-source paired actual PCM, creative delay, bypass/removal, forced processor failure, source rehash forgery, export/import/reopen and existing R1/R2/MRAM regressions. The evidence generator must run twice with byte-identical artifact trees and an independently verifiable manifest.

Before merge: exact implementation/evidence head **38/38 SUCCESS**, independently inspect uploaded artifact and recompute ZIP/member hashes plus numeric WAV PCM frames, durable validation, exact successor **38/38 SUCCESS**, expected-head squash merge. None of these steps is inferred or claimed until separately confirmed.

**Nonclaims**: generic graph PDC, arbitrary track/bus plug-ins, native VST3/CLAP/AU latency discovery, untrusted binary sandboxing, realtime compensation, Studio plug-in/editor UI, live monitoring latency handling, mastering-grade production readiness. These remain future explicit rungs under #166/#162/#155.
