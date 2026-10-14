# PLUG-R2-B K0 — Detached Causal Two-Path Alignment Reference

Status: **IMPLEMENTED IN DRAFT BRANCH; VALIDATION PENDING**. Track Issue #166 under still-open R2 #162 and parent #155. Predecessor: validated R2-A ledger on main `14833ef0a56ca23fd9a447f2019d049424547163`.

## Why the implementation is deliberately split

R1/R2-A accepts only a post-master simulated reference gain/creative-delay chain. R1's `delay_frames` creates a *user-intended audible displacement* and is **not** an independent real plugin's reported processing latency. The accepted routing engine can handle multiple buses but has no validated non-master plugin insertion authority. Inventing a PDC claim by altering master-chain delay numbers would be technically false.

This K0 introduces a **genuine PCM-level, offline and causal two-path compensation kernel** while leaving creative ownership detached. Its declared algorithmic latency fields are synthetic/simulated test input only: **not read from VST3/AU/CLAP binaries and not yet accepted canonical plugin state**. This proves signal processing mechanics, not product-level DAW PDC integration.

## Exactly supported topology

Two independent stereo PCM16 WAV input paths, **equal sample rate and frame count**, with unique stable IDs, one deterministic stereo summed output. No sample-rate conversion, channel conversion, sends, feedback loops, sidechain, external plugins or arbitrary graphs.

Every path separately declares:

- `declared_algorithmic_latency_frames`: simulated plugin processing latency, 0–4096 integer;
- `creative_delay_frames`: optional intentional artistic delay, 0–4096 integer, NEVER eliminated by PDC;
- `bypass`: true means zero **algorithmic** plugin latency;
- `input_wav_sha256`: exact immutable source input binding;
- computed `effective_algorithmic_latency_frames` and `compensation_frames`.

For effective path latencies `L_A, L_B`, choose `L_ref=max(L_A,L_B)`. Compensation for path i is `C_i=L_ref-L_i`. A source frame at index t is rendered at `t + L_i + creative_i + C_i`; this is always **at least t** and never reads future input to advance the slower path.

Output length remains the input length. Trailing frames can be truncated and this is explicit; a branch whose entire output would be truncated fails closed. The first version is **offline reference-only** and not suitable for realtime device hosting.

## Fixed oracle — independent impulse channels

At frame 4, path A has left sample +8000; path B has right sample -6000. Simulated algorithmic latency is 3 frames for A and 9 for B, with no creative delay:

| Case | Left arrival | Right arrival | Interpretation |
| --- | ---: | ---: | --- |
| Without compensation | 7 | 13 | Different arrival indexes |
| With compensation A=6, B=0 | 13 | 13 | Both independently detectable samples coincide |
| Accepted-intent creative delay A=5 | 18 | 13 | Creative delay preserved, intentionally unaligned |
| Bypass A latency=0 | 13 | 13 | Compensation recalculated A=9; no stale offset |

The reference kernel must confirm complete waveform bytes and exact nonzero positions, not only plan hashes. Forced active-processor failures must abort output without silent bypass or mutated plan; tampered source WAV fails hash binding.

## Trust boundaries / next genuine host-integration gate

K0 plans are `classification=detached_derived_reference_only`; `host_authority=none_detached_not_accepted`, and require `simulated_explicit_reference_only` provenance. A kernel input cannot authorize a Project commit, plugin state mutation or routing reconfiguration. No accepted source guarantee is claimed.

**Next K1 gate:** version a separate, authenticated simulated processing-latency declaration in accepted plugin material and source-bound Preview→Accept. Explicitly allow only two non-master routing paths converging at master, inject bounded plugin processing before merge and revalidate the source, exact plan, numerical audio and reopen. Reject unsupported routes/owners, stale revisions and plugin failures. The existing 35 workflows must remain green; new K0 evidence gate adds one without weakening prior ones.

No claim of production plugin-host PDC, realtime scheduling, commercial VST/AU/CLAP hosting or arbitrary graph compensation.
