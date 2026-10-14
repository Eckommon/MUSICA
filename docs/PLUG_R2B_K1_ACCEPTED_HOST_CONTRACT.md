# PLUG-R2B K1 — Accepted Two-Path Host Integration Contract Gate

Status: **PROPOSED, NOT IMPLEMENTED OR VALIDATED**. Issue #166 under #162 and #155. Base: validated detached K0 merge `ee1a4fee33124ca2fb97bde44af0930de7a7165e` (PR #167, 36/36 exact-head SUCCESS).

## Required architectural separation

- **Existing R1 state**: `delay_frames` is a creative audible signal delay in accepted master-only simulated plugin state. Preserve this field's exact identity, historical byte output and trusted Preview→Accept authority.
- **K0 reference**: detached `algorithmic_latency_frames` is a simulated test/configuration field. The K0 kernel proves causal PCM alignment but does **not** license injecting arbitrary caller-owned WAV or runtime plugin handles into an accepted host.
- **K1 authority**: never infer algorithmic latency from creative delay, runtime buffer, metadata label, or an untrusted caller. A separate, versioned accepted processor descriptor/state contract must explicitly state simulated algorithmic latency provenance, with exact accepted revision and owner IDs. No implicit upgrades or fallback.
- **Derived execution**: same approved Blueprint + routing + audio + automation + plugin material -> deterministic plan and aligned WAV. No reverse write-back from runtime, aligned WAV or detached K0 configuration.

## Minimum accepted topology: K1 v0

Exactly **two accepted, distinct audio tracks** with stable `track_id`, each routed to a distinct stable bus `node_id`. Both buses converge exactly once on one accepted master node. No direct-to-master side path, no sends, feedback, sidechain, multi-input branch or branching path supported for v0. Retain existing routed engine for every unsupported/legacy project without changing its output.

Canonical shape MUST be established by inspecting `routing_contracts.build_routing_plan` and the exact accepted routing material, NOT guessed from UI node names or array positions. Each source bus's input is the accepted audio/routing-derived **pre-merge** PCM (after documented track/bus gain/pan/automation stage). Reuse the current float64 mixer where possible to avoid PCM16 intermediate rounding artefacts. If K0's PCM16 inputs are used instead, explicitly prove and document the quantization boundary.

## New versioned accepted host policy (design constraints)

Do not extend R1 `accepted-plugin-material-v0` by loosening its master-only owner check. Add a separate versioned *simulated processing insert* contract, if accepted plugin inserts are introduced on buses. At minimum bind:
- immutable plugin descriptor identity, processor ID/version, simulated latency provenance/policy and stereo/exact sample rate;
- stable `instance_id`, exact `owner_kind=routing_node`, exact accepted **bus** `owner_id`, insertion `slot` and explicit bypass;
- distinct **algorithmic_latency_frames** nonnegative bounded integer and independent accepted **creative_delay_frames** (if supported, with a separately documented audible semantics);
- source binding of project ID, revision ID, Blueprint/audio/routing/automation/legacy-plugin material hashes and proposed new host-material hash;
- Preview on copy -> explicit Accept on exact persisted HEAD -> protected Project Engine gate -> exactly one revision advance;
- generic commit rejects any nonempty host material or changes to it without trusted host-specific Accept.

No duplicate instance/slot, ambiguous master, track, bus, sample-rate or owner. Missing/misreported latency provenance fails closed. Legacy no-host plugin projects are valid and render byte-identically.

## Derived plan and causal compensation

Only for two validated accepted paths, define `L_ref=max(L_A,L_B)`; the faster path receives `C_i=L_ref-L_i` frames. The output sum uses independent processing path samples at frame `t + algorithmic_i + creative_i + C_i`. A user-created `creative_i` delay is NOT subtracted. All offsets >= 0; never read future frames. Fixed-length truncation policy must be explicit; reject entirely truncated paths. Input source SHA, path topology SHA, accepted host material SHA, and every output plan's canonical JSON self-hash must be verified.

The `algorithmic_latency_frames` in K1 must remain clearly labeled **simulated/reference processor** metadata until measured/reported native plugin backend evidence exists.

## Fail-closed acceptance and execution

- stale/forged source revision/parent/Blueprint; malformed/duplicate bus or instance identity; unsupported graph; unknown descriptor/processor; sample-rate mismatch; > bounds; incorrect plan self-hash -> block;
- bypass and instance removal recalculates compensation from the **new accepted** source and discards old runtime offsets;
- forced processor error prevents derived WAV promotion; no implicit auto-bypass, no partial accepted commit;
- reopen accepted archive reproduces host material, derived alignment plan, and output bytes/sha exactly;
- detach-only K0 path is never accepted Project mutation authority.

## Numerical and integrity proof required before K1 promotion

1. Two independently distinguishable accepted audio-track impulses routed through separate accepted buses to one master.
2. Uncompensated arrivals at unequal sample indices; compensated output arrives at exactly same index, verifying both positive and negative sample magnitudes numerically.
3. A separate intentional creative delay survives compensation and is independently observable.
4. Bypass and remove recompute latency/offsets; zero-latency/no-plugin legacy output is byte-identical.
5. Accepted trusted Preview→Accept, stale/forged/generic commit blocked, forced error leaves HEAD intact.
6. A/B deterministic plan + PCM/WAV bytes and exported/reopened project identity.
7. New K1 permanent CI without weakening 36 existing workflows, independently inspected artifact/manifest and exact-head validations before any merge.

## Promotion discipline

This gate documents unresolved host authority design, **not** an accepted DAW PDC capability. Implement schema + protected Preview→Accept first; prove it on separate branch/PR as appropriate; only then couple the accepted two-bus mixer execution to the numerical K0 kernel. Keep #166/#162/#155 OPEN until product-level evidence exists. Do not claim real third-party plugin ABI, realtime hosting, arbitrary graph PDC or commercial DAW readiness.

## Current intermediate execution — K1 source bridge (not plugin authority)

The first K1 implementation is intentionally **read-only and not product-host PDC**:

- `plugin_host_topology.exact_two_bus_host_topology` checks two accepted track IDs -> two distinct `bus` nodes -> neutral master, with no sends, detours or extra nodes.
- `plugin_host_bridge.build_accepted_bus_reference_inputs` resolves actual immutable accepted audio asset bytes and canonical native track/bus gain/pan/automation through existing MRAM primitives, reusing the accepted source's deterministic routed plan.
- The bridge quantizes each **post-bus, pre-master float64 output to PCM16** independently before invoking the detached K0 PCM16 reference kernel. This is an explicit reference quantization boundary, **not** interchangeable with the existing float64-first final master mix. Legacy routing audio remains unchanged.
- It rejects non-neutral/muted master, master automation, accepted R1 master plugins, unsupported routing, sample-rate mismatch, duration overflow, owner-ID spoofing and unknown detached configuration fields.
- Synthetic per-bus algorithmic latency, intentional creative delay and bypass are supplied as explicit **detached experiment parameters**, not as accepted/authorized plugin processor state. K0 applies causal offsets to those accepted-audio-derived WAV paths without any Project writes.
- The permanent **37th** workflow must prove source-bound evidence A/B byte equality, actual accepted two-bus PCM values, nontrivial compensation offsets, creative delay preservation, bypass offset recalculation, fail-closed error, HEAD non-mutation and reopen identity.
- A green K1-source-bridge verdict will **not** close Issue #166/#162. Product-host PDC still requires an independent versioned and protected **accepted non-master plugin instance/latency material** and physically integrated signal processing over that accepted authority. The transient K0 parameters cannot be silently promoted as if they were approved by the user.
