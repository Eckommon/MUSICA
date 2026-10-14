# PLUG-R2B K0 Validation — Detached Causal Two-Path Audio Alignment Reference

## Verdict / scoped claim

**PASS — audible, deterministic, causal, two-path PCM reference kernel. NOT accepted MUSICA DAW plugin PDC.**

Issue #166 under #162 and parent #155. Implementation PR #167. Predecessor PLUG-R2-A validated canonical main `14833ef0a56ca23fd9a447f2019d049424547163`.

The K0 kernel **actually delays the faster processing path**, verifies both separable PCM impulse channels at the output, and preserves an independent intentional creative delay. Its algorithmic latency comes from **explicit simulated detached reference configuration**, not third-party plugin binaries nor accepted non-master plugin state. No accepted Project revision or native routed host signal flow is modified.

## Exact implementation/evidence head

- PR #167, `feature/plug-r2b-two-path-pdc-kernel`
- implementation/evidence head: `76a93f2e5f6222773f9acb0458ffece34f159fd5`
- total permanent workflows: **36** (35 inherited + dedicated R2B K0)
- exact-head CI: **36/36 SUCCESS**
- dedicated workflow: **PLUG-R2B Detached Two-Path Causal Alignment Reference Evidence**
- dedicated run: `38566833211` — **SUCCESS**
- artifact ID: `11896700309`
- ZIP SHA-256 (GitHub declared and independently recomputed): `2a8d4f39e8350a2cbadb0309ef0f6d388e549fa8004936aca509e16c0e9b6300`
- artifact ZIP size: **4,953 bytes**

## Independent numerical and integrity proof

Downloaded the artifact ZIP independently and inspected:

- manifest `PLUG_R2B_DETACHED_REFERENCE_NO_HOST_PDC_CLAIM`;
- **10/10** manifest payload byte sizes + SHA-256 hashes recomputed successfully;
- **3/3** derived plan self-hashes recomputed using MUSICA canonical JSON with newline;
- dedicated CI verified all **6** Git source contract/test/workflow inventory hash/size entries against the checked out implementation head;
- WAVs are **stereo, PCM16, 8,000 Hz, 128 frames**;
- two distinguishable impulses originate at frame **4**: +8000 in left/path A and -6000 in right/path B;
- uncompensated simulated processing latency (A=3, B=9): output **left frame 7 / right frame 13**;
- real causal compensation offsets (A=6, B=0): output **left frame 13 / right frame 13** with exact simultaneous stereo sample **(8000,-6000)**;
- intentionally inserted creative delay on A=5: output **left frame 18 / right frame 13**; artistic delay was NOT erased;
- bypass A drops its algorithmic latency to zero and recomputes compensation A=9; output **13/13**;
- deterministic repeated plan and WAV bytes MATCH;
- stale/forged WAV source, tampered self-hash/offset/order, invalid rate/duration/identity and active processor failure fail closed;
- entirely truncated branch is rejected, not silently replaced with zero output.

The last check proves a genuine **sample-level reference signal alignment**, not merely a plan number. It does **not** establish accepted-source/plugin placement authority, bounded native routing plugin insert, realtime PDC or general graph compensation.

## Authority and remaining K1 gate

The plan is `detached_derived_reference_only`; source algorithmic latency provenance is `simulated_explicit_reference_only`; `host_pdc_integrated=false`. It holds no permission to update Project HEAD, Blueprint, accepted plugin state, or routed mixer inputs.

**K1 (still open):** freeze versioned accepted latency material independent of creative `delay_frames`; establish trusted Preview→explicit Accept for precisely scoped non-master plugin placement on two paths converging on master, process and compensate these paths in accepted routed offline execution, preserve legacy R1, prove independent PCM alignment/bypass/reopen/failure and exact-source hashes. Do not close Issue #162 or parent #155 at K0.

## Promotion discipline

This durable validation record follows exact-head 36/36. The PR may merge only after a **fresh exact-head 36/36 successor CI** on this validation commit and expected-head squash merge. Any new code change invalidates the gate and requires renewed verification.
