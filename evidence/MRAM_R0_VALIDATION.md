# MRAM-R0 Validation — Routing Graph Contracts & Deterministic Signal-Flow Plan v0

## Scope

Issue #118 under parent Issue #115.

MRAM-R0 defines a bounded explicit native-audio routing graph contract and deterministic derived signal-flow lowering while deliberately keeping non-empty accepted routing authority closed.

## Evidence-bearing implementation head

- exact head: `1d7c310ba02ef651927ad65cc58f782b1f1b34b6`
- permanent workflow count: **21**
- exact-head result: **21/21 SUCCESS**
- dedicated workflow: **MRAM-R0 Routing Graph Evidence**
- dedicated run: `35283452173` — **SUCCESS**
- artifact ID: `10522966682`
- artifact name: `musica-mram-r0-routing-evidence`
- artifact ZIP SHA-256: `bfe38c8d8794e98a904155ee2f31353fe585fddeef3faeeaae2b98a17224b923`
- artifact size: 2,845 bytes

The first Post-M7 Accepted Revision Compare attempt on this same exact head failed during real Chromium with a transient HTTP/BrokenPipe path (`compare fetch failed: 400`) after its regression step had already passed. The failed job was rerun without changing the head. The rerun passed regression, real Chromium Compare, deterministic evidence A/B and artifact upload. No MRAM code or contract was changed to obtain the green result.

## Independent artifact inspection

The downloaded artifact ZIP digest matched the GitHub artifact digest exactly.

Manifest payload verification passed for all **4/4** declared payload files:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `contract-hashes.json` | `ab5d06ecdc9e6183adc8ccf7356cf74f407a961dee9473d8da7ee78a05174fb1` | 1,124 |
| `proof.json` | `b4b5a6df1ef16ca59a0f64d315a51d943293aa2f0118a83ebe79dbcf9bf1fcfa` | 863 |
| `routing-material.json` | `aac46ac0238c4eea3c1c434f3c362bdd7ea6e3ac6998b1a424e6f10088bf5cf4` | 772 |
| `routing-plan.json` | `5a58d29051f47e7eaf21c34dff09e84470ad21ea2122cac357387be1a971e822` | 1,269 |

The routing-plan self-hash was independently recomputed using MUSICA canonical JSON bytes and matched exactly:

- declared: `4d756500bb806be98b25f3c7f2e21cb3b08b36ea652795002a89edcdedbe46e8`
- recomputed: `4d756500bb806be98b25f3c7f2e21cb3b08b36ea652795002a89edcdedbe46e8`

## Proven bounded behavior

The evidence proves:

- explicit stable bus/group/return/master routing-node identities;
- one unique master sink for a non-empty graph;
- exact per-track output mapping;
- explicit bounded post-fader sends;
- deterministic canonical ordering;
- deterministic topological signal-flow lowering;
- repeat-exact routing plan and plan SHA;
- cycle rejection;
- missing route-target rejection;
- missing known-track output rejection;
- master-as-send-source rejection;
- optional absent/empty Blueprint routing compatibility;
- structurally valid non-empty routing when validation is explicitly invoked for analysis;
- canonical non-empty accepted Blueprint routing remains fail-closed under MRAM-R0.

## Authority boundary

MRAM-R0 does **not** grant an accepted routing mutation path.

```text
routing material contract
→ deterministic topology validation
→ derived signal-flow plan
≠ accepted routing mutation authority
≠ routed audio render authority
≠ Browser/runtime reverse authority
```

A later MRAM rung must introduce a source-bound Preview → explicit Accept path before non-empty routing may become accepted project state.

## Explicit non-claims

This validation does not claim:

- accepted routing Preview→Accept authority;
- routed native-audio rendering;
- track/bus automation mapping;
- Browser routing editing;
- sidechain semantics;
- real-time audio device I/O;
- recording/monitoring;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- generalized commercial release readiness.

## Validation verdict

> **VALIDATED — BOUNDED EXPLICIT ROUTING GRAPH CONTRACTS & DETERMINISTIC SIGNAL-FLOW PLAN v0**

Maximum supported claim:

> **MUSICA can validate a bounded explicit acyclic routing graph and deterministically lower it into an exact provenance-bearing signal-flow plan while non-empty accepted routing remains fail-closed and no routing runtime/rendered output gains reverse creative authority.**

Promotion remains conditional on all **21** permanent workflows succeeding again on the exact successor head containing this durable record, followed by expected-head merge and separate state-only closure.

Repository evidence remains authoritative over conversation/model memory.
