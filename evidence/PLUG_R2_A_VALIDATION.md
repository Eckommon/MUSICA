# PLUG-R2-A Validation — Accepted Serial Signal-Delay Ledger & Failure Boundary

## Verified scope and decision

Parent mission #155; R2 mission #162; implementation PR #165.

**Verdict: PASS — PLUG-R2-A SERIAL LEDGER ONLY. NOT genuine cross-path plugin-delay compensation (PDC).**

PLUG-R2-A derives a schema-validated deterministic offline/reference-only serial latency ledger from *persisted accepted R1 project state*, without a caller-supplied routed render. It binds exact project/revision/Blueprint/audio/routing/automation/plugin material, R1 processing-plan and routed-source identities. R1's `delay_frames` is a user-controlled audible reference signal delay, **not independently reported/measured algorithmic plugin latency**.

One serial post-master chain has no competing dry/other path. The ledger explicitly fixes `compensation_applied_frames=0`, `compensation=NONE_SERIAL_ONLY`, and `algorithmic_latency=UNMEASURED_NOT_INFERRED`. It neither modifies routed rendering nor commits derived plans or WAV to accepted creative state. Genuine two-path PDC remains blocked pending an independently evidenced separate latency source and narrowly supported merge topology.

## Exact implementation/evidence head

- PR: #165 `feature/plug-r2-latency-contract`
- implementation/evidence head: `e92ef05498dbade47c9c56f0cdd1e5238bbe477d`
- CI: **35/35 permanent workflows SUCCESS** on that exact head (34 inherited + dedicated PLUG-R2)
- dedicated workflow: **PLUG-R2 Accepted Serial Latency Ledger Evidence**
- dedicated run: `38560356337`, conclusion **SUCCESS**
- artifact ID: `11891639511`
- artifact: `musica-plug-r2-serial-latency-ledger-evidence`
- ZIP SHA-256 (GitHub declared; independently downloaded and hashed): `810230cdc3f179dfb33ce60dd99c899578d0a06e1458122826a82d651ec357fb`
- ZIP bytes: **25,791**

## Independent artifact inspection (beyond CI verdict)

Downloaded exact-head archive and independently inspected:
- manifest classification: `PLUG_R2_LEDGER_ONLY_NO_PDC_CLAIM`;
- **11/11** manifest payload SHA-256 and byte sizes MATCH;
- **5/5** latency-plan self-SHA256 values independently recomputed using MUSICA canonical JSON (sorted, compact UTF-8, terminal newline);
- **16/16** nested Project content-addressed object hashes MATCH filenames;
- WAV: **stereo PCM16 / 8,000 Hz / 96,000 frames**;
- independently decoded PCM samples prove `wet[0:4] == (0,0)` and **every** frame `wet[4:] == dry[:-4]` (exact 4-frame displacement at unity gain, not merely a hash change);
- bypass and removed outputs are **byte-for-byte equal** to corresponding routed baseline WAV;
- accepted state change `delay_frames=4→9` updates ledger frames `4→9`; bypass and remove each return effective frames to **0**;
- deterministic forced processor failure leaves HEAD unchanged; forged material source hash is rejected even when ledger hash is recomputed;
- export/import/reopen reproduces exact accepted-source ledger and processed WAV.

The dedicated CI also independently verified the recorded hashes/byte sizes of the **7 source contract/test/workflow files** in the artifact inventory on the evidence head and ran duplicate A/B evidence generation with recursive exact byte comparison.

## Fail-closed invariants

- Exact R1 plan schema/self-hash and ledger self-hash; ordered stable instance/slot IDs, no duplicates.
- Master-only owner and stereo PCM16 exact-rate contract; no hidden resampling or channel conversion.
- Bypassed effective signal delay equals zero; maximum per instance `4096` frames and bounded serial sum.
- Rehashed or stale/forged ledger cannot bind to accepted persisted source.
- Processor failure is a hard derived execution error, not implicit bypass or accepted-state mutation.
- Existing accepted Preview→explicit Accept, generic commit protection, and R1 routed/recording/automation authority are preserved.

## Scope discipline and remaining gates

This document is durable evidence of **R2-A only**. Do not label the entire #162 or plugin latency compensation completed on this basis.

For genuine R2-B, implement a separate explicit algorithmic-latency authority/measurement representation and minimal two-path convergence topology (if feasible), with causal `max(path arrival) - arrival_i` correction by delaying shorter paths only. Prove two distinguishable input impulses align at identical sample indices and that creative delay is not erased, with bypass, failure, accepted revision, and reopen tests. If not feasible in this rung, split PDC into an explicit follow-up and keep parent #155 OPEN.

Promotion for this partial stage: durable validation record on successor head → all **35/35** exact-head CI again → expected-head squash merge PR #165. Leave Issue #162 OPEN until disposition of actual PDC, or explicitly narrow/split it with recorded governance.

**No claims** of VST3/AU/CLAP binary hosting, scanning, unsafe plugin sandbox isolation, real-time plugin host PDC, arbitrary graph PDC, or commercial third-party compatibility.
