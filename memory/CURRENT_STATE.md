# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → NATIVE AUDIO FOUNDATION VALIDATED → MIXER ROUTING & AUTOMATION EXPANSION IN PROGRESS**

Long-term governing target:

> **MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving its AI-native authority, inspectability, reproducibility and programmability.**

This remains a product target, not a claim that MUSICA is already a complete commercial DAW.

## Canonical baseline / 공식 기준점

### Audio Track / Clip / Mixer Foundation v0

Parent Issue `#95` — **COMPLETED — BOUNDED FOUNDATION ONLY**

Validated ATCM rungs:

- R0 Issue `#97` / PR `#98` — **COMPLETED / MERGED / VALIDATED**
- R1 Issue `#99` / PR `#101` — **COMPLETED / MERGED / VALIDATED**
- R2 Issue `#102` / PR `#104` — **COMPLETED / MERGED / VALIDATED**
- R3 Issue `#105` / PR `#107` — **COMPLETED / MERGED / VALIDATED**
- R4 Issue `#111` / PR `#114` — **COMPLETED / MERGED / VALIDATED**
- R4 implementation merge: `e19c8ebf81b1dc37a03493458abb180adf48e9c7`
- R4 state-only closure PR `#117` — **MERGED**
- R4/native-audio foundation state merge: `712769f2ec469083d5c08fca8006a4b6e419a4d0`

The bounded native-audio foundation has durable end-to-end evidence for immutable assets, accepted track/clip authority, deterministic multitrack mix, truthful Browser interaction and restart/reopen persistence/integrity.

## Current commercial-workstation mission

Parent Issue `#115` — **Mixer Routing & Automation Foundation v0 — OPEN**

Selected bounded rung sequence:

```text
MRAM-R0 routing contracts + deterministic graph lowering      VALIDATED
→ MRAM-R1 trusted routing Preview→Accept + routed mixer       CURRENT
→ MRAM-R2 track/bus gain/pan automation mapping
→ MRAM-R3 Browser routing/automation + reopen lifecycle
→ Issue #115 bounded closure evaluation
```

## MRAM-R0 — validated routing substrate

Issue `#118` — **COMPLETED**

Implementation PR `#119` — **MERGED**

Canonical implementation merge/main:

> **`7e5da8b558c0c4b980f7b6e3061eca9873e65513`**

Durable validation:

- `evidence/MRAM_R0_VALIDATION.md`
- implementation/pre-validation exact head:
  `1d7c310ba02ef651927ad65cc58f782b1f1b34b6` — **21/21 permanent workflows SUCCESS**
- validation-record successor exact head:
  `50701b45fd4c2cb9f95a01c8ec9a8b7d8ccb9956` — **21/21 SUCCESS**
- dedicated workflow: **MRAM-R0 Routing Graph Evidence**
- dedicated pre-validation run: `35283452173` — **SUCCESS**
- artifact ID: `10522966682`
- artifact ZIP SHA-256:
  `bfe38c8d8794e98a904155ee2f31353fe585fddeef3faeeaae2b98a17224b923`
- independently verified manifest payloads: **4/4 exact SHA-256 + byte size PASS**
- routing plan self-hash independently recomputed:
  `4d756500bb806be98b25f3c7f2e21cb3b08b36ea652795002a89edcdedbe46e8`

One pre-validation Compare browser run encountered a transient BrokenPipe / HTTP 400 after its regression stage passed. The same failed job was rerun on the same exact head without code changes and passed regression, real Chromium Compare, deterministic evidence A/B and upload. The successor validation head completed all 21 workflows successfully.

### Validated MRAM-R0 behavior

MRAM-R0 establishes:

- optional additive `materials.routing` Blueprint shape;
- stable `bus / group / return / master` routing-node identities;
- exact per-track output targets;
- bounded stable post-fader sends;
- exactly one master sink for non-empty graphs;
- canonical node/output/send ordering;
- fail-closed missing node/track references;
- fail-closed cycles;
- deterministic topological signal-flow lowering;
- exact derived routing-plan SHA;
- absent/empty routing backward compatibility.

The central R0 authority boundary remains:

```text
routing contract
→ structural validation
→ deterministic derived signal-flow plan
≠ accepted non-empty routing mutation authority
≠ routed-audio render authority
≠ Browser/runtime reverse authority
```

Non-empty routing may be structurally inspected with an explicit analysis allowance, but generic Blueprint validation still rejects it as accepted creative state. A later trusted routing accept boundary must explicitly authorize it.

### Maximum validated MRAM-R0 claim

> **MUSICA can validate a bounded explicit acyclic routing graph and deterministically lower it into an exact provenance-bearing signal-flow plan while non-empty accepted routing remains fail-closed and no routing runtime/rendered output gains reverse creative authority.**

## Exact current rung / 현재 정확한 단계

The next rung is **MRAM-R1 — trusted routing Preview→Accept + deterministic routed offline mixer**.

R1 must reuse the existing authority architecture rather than trusting a provenance marker alone.

Required authority invariant:

```text
exact accepted revision
→ source-bound routing edit candidate
→ validate project + exact source + routing DAG
→ Preview only; accepted HEAD unchanged
→ explicit trusted Accept
→ source/head/graph/assets revalidated
→ exactly one accepted revision advance
```

The Project Engine must gain a narrow internal routing-authorized commit boundary analogous in spirit to the existing protected native-audio acceptance path. Generic `commit_revision` must remain unable to accept routing changes.

R1 must then derive and render exact accepted routing through the native offline mixer without allowing the plan or rendered WAV to become canonical authority.

## Current important non-claims / 현재 주요 비주장

Until separately validated, do not claim:

- accepted routing edits or routed audio rendering beyond MRAM-R0;
- mixer automation mapped to native track/bus parameters;
- Browser routing editing;
- generalized sidechains;
- low-latency ASIO/CoreAudio/WASAPI device operation;
- microphone/line recording or monitoring;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- implicit sample-rate conversion;
- warp/time-stretch/pitch shift or destructive waveform editing;
- mastering-grade processing;
- generalized commercial release readiness or production SLA;
- cloud/multi-user creative authority;
- perceptual superiority.

## Exact next phase / 다음 단계

> **Open and implement MRAM-R1 from canonical main `7e5da8b558c0c4b980f7b6e3061eca9873e65513`: create a source-bound routing candidate/Preview/Accept authority path with a protected Project Engine routing commit boundary, then extend the deterministic native mixer to execute exact accepted DAG routing and prove byte-reproducible routed mix output.**

See `memory/NEXT_ACTION.md` for the exact execution order.

**Repository evidence remains authoritative over conversation/model memory.**
