# PLUG-R2 latency decision record — v0 (design gate)

Status: **DESIGN ONLY — NOT IMPLEMENTED / NOT VALIDATED**. Parent #155, rung #162. Canonical prerequisite: R1 state closure merge `cf3def72aa982fa953264db93e5965d59f9e54e4`.

## Grounded semantics

The R1 reference processor is a **post-routed-master PCM16 stereo stage**. Its supported `delay_frames` parameter creates actual audible fixed-frame displacement (leading zeros, with output length held fixed). It is an accepted **creative/reference signal delay parameter**, not evidence of a real plugin's intrinsic algorithmic processing latency. No discovered VST3/AU/CLAP latency reporting exists.

The current accepted plugin placement is only `routing_node` at the exact master node. An ordered serial chain therefore has one audible route, and its total delay is the sum of active instance delays (bypassed instance contributes zero). A ledger of this total is not multi-path plugin delay compensation (PDC).

## Decision: stage the bounded claim, do not fabricate PDC

1. **R2-A — exact latency ledger and failure containment:** derive a read-only, deterministic and source-bound latency plan over the R1 serial master scope. Call it *latency accounting*, not compensated audio. Preserve R1 playback semantics byte-for-byte. Reject overflow, unsupported shapes and forged/tampered plan hashes. Include absent-plugin / single / multi / bypass / removed / reopen and error proof. Separate this from a PDC success verdict.
2. **R2-B — optional genuinely audible reference-path alignment:** only after a narrowly extended two-path topology has been explicitly specified and independently tested. Under an offline causal reference model, the faster path may be delayed to the slower path; never advance the delayed path or delete user-intended creative delay. Define which routing graph nodes, input streams, ownership/slot identity and output clock are supported, with no implicit master-only compatibility change. If no such bounded extension is feasible, close R2 strictly as *ledger/failure containment* and return PDC to a follow-up issue; do **not** promote compensation language.
3. **No hidden split of the parameter:** `delay_frames` remains a signal delay in R2-A. If a distinct `algorithmic_latency_frames` is introduced later, version the descriptor/plan contract explicitly and provide a measured/reported provenance and separate semantics. Do not repurpose an existing accepted field.

## R2-A derived ledger contract — proposed fields

- `plan_version`, `engine_id`, `classification=derived_noncanonical`, `stage=post_routed_master_pcm16_reference_stage`;
- exact accepted project ID/revision ID/Blueprint SHA-256, audio/routing/automation/accepted-plugin-material SHA-256;
- sample rate, stereo channel count and PCM16 identity; no resampling;
- ordered active/bypassed `instance_id`, `plugin_id`, `owner_kind`, `owner_id`, `slot`, `declared_signal_delay_frames`, `effective_signal_delay_frames`, `bypass`;
- `serial_effective_signal_delay_frames` = sum of active effective delays, within an explicit integer maximum; `compensation_applied_frames=0` and `compensation_claim=NONE_SERIAL_ONLY`;
- deterministic canonical JSON serialization and plan self-SHA calculated with the self-hash field excluded.

Plan generation MUST revalidate the exact accepted source and plugin material, reject duplicate slot/identity, wrong master owner, stale source, unsupported rates/channels, noninteger/negative/out-of-bounds values and plan self-hash mismatch. Derived plans, runtime buffers and WAV never authorize a Project commit.

## Failure and bypass contract

- All-bypassed / empty chain: zero ledger effective delay and byte-exact existing routed PCM/WAV output.
- A changed or removed instance regenerates ledger from accepted source; no persistent compensation buffer survives.
- An injected processor failure aborts derived rendering (no partial artifact promotion, no silent bypass, no accepted revision mutation).
- Export/import/reopen recomputes the same ledger bytes/hash and same derived audio output for the same accepted revision.

## Evidence and promotion gate

Independent test oracles must inspect actual first-nonzero frame position and PCM samples for impulse/reference fixtures; hash equality alone is inadequate. For a serial chain, numerical displacement supports *delay accounting only*. For claimed two-path PDC, verify the two independently distinguishable paths align at exact output frame indices and preserve intentional delay under bypass and failure. Dedicated permanent R2 gate is expected to raise count from 34 to 35. Require exact-head 35/35 success, independent evidence inspection, durable validation, successor 35/35, expected-head squash merge, then Issue #162 completion.

Non-claims: real plugin binary loading, unknown host latency reporting, general graph PDC, real-time compensated hosting, plugin editors, sidechains, commercial compatibility.
