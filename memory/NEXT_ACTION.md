# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**REC-R2 — BOUNDED INPUT MONITORING & CAPTURE/DROPOUT INSTRUMENTATION v0**

Issue #149 — OPEN
Parent mission: Issue #142 — Recording & Monitoring Foundation v0 — OPEN

REC-R1 is validated, merged and completed. The next dependency-safe step is to add a bounded deterministic monitor path for the same provenance-bound simulated input used by REC-R0 capture, while proving that monitoring remains runtime-only and cannot alter recorded bytes or accepted creative state.

## Canonical base / 공식 기준점

- canonical main after REC-R1 merge: 284c823fa6b0e29a9abf78f3425054c2339e0bdb
- REC-R1 Issue #146 — COMPLETED
- REC-R1 PR #148 — MERGED
- implementation/evidence head 023db631c827ebbea6068f0709ce57d341fde8e3 — 30/30 SUCCESS
- validation-record successor c066136b79919eb28f40b9bddeddc489403f67c4 — 30/30 SUCCESS
- durable validation: evidence/REC_R1_VALIDATION.md
- dedicated artifact ID 11072283272
- artifact ZIP SHA-256 5b4047fb3471e7a082143f2b4098ec497a39bd3c89fa0729ce42673065d3699f
- permanent workflow count: 30

## Inherited authority / 상속 권한

REC-R0:
accepted revision + explicit simulated input config
→ deterministic capture plan/runtime
→ exact PCM payload + capture report
→ derived only

REC-R1:
clean completed capture
→ source-bound finalize candidate
→ Preview / HEAD unchanged
→ explicit Accept
→ immutable asset
→ accepted stable track/clip revision

RTIO:
accepted revision
→ deterministic realtime plan
→ simulated output/callback/transport runtime
→ derived only

REC-R2 must compose these boundaries without turning monitor runtime/output/metrics into accepted creative state.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground capture and output runtime contracts

Inspect recording_capture.py, REC-R0 schemas/tests/validation, recording_finalize.py, REC-R1 schemas/tests/validation, RTIO-R0/R1/R2/R3 plan/runtime/backend/transport modules, the simulated output sink representation and Project source/hash binding helpers.

Identify the smallest existing deterministic output/runtime boundary suitable for monitoring. Do not create a second unrelated realtime engine.

### 2. Freeze monitoring plan v0

Define a derived/non-canonical monitoring plan binding exact project/revision ID, Blueprint/audio/routing/automation hashes, input backend capability/config identity, sample rate, channels, block size, input generator identity, monitor enabled state, supported simulated monitor output backend, compatible output config, optional exact monitor gain, plan/compiler/version identity and self-hash.

Use exact-match only. No resampling.

### 3. Use one input block stream for capture and monitor

For every input block N, fork the same bytes to capture and monitor. Do not regenerate a separate pseudo-input for monitoring. Captured PCM must be taken before any monitor-only gain or processing.

### 4. Prove monitor OFF/ON capture equality

For the same source/config and clean input, monitor-OFF capture payload and monitor-ON capture payload must be byte-for-byte identical, with the same payload identity and exact frame count.

### 5. Deterministic monitor output

When enabled, derive deterministic monitor sink bytes/trace/metrics binding exact source block/frame ranges, sink frames, payload SHA where materialized, block/callback counts, lifecycle, enabled state and monitoring-plan SHA. Repeat execution must reproduce exact outputs.

### 6. Monitoring state is runtime-only

Monitor enable/disable/start/stop/reset must leave Project HEAD, Blueprint hash, accepted audio/routing/automation material and immutable asset inventory unchanged. Transient monitor cursors/counters are not creative state.

### 7. Optional monitor gain

Only implement if an existing exact gain law/range can be reused. If supported, prove the capture payload SHA remains identical while monitor output SHA changes. Never apply monitor gain to captured PCM.

### 8. Capture/dropout/error instrumentation

Preserve REC-R0 exact counters and add only explicitly defined monitor-side metrics. Exercise clean, SHORT_FILL, LATE, ERROR and a monitor-side dropped/underrun case only if separately modeled. No hidden padding, replay or repair.

### 9. REC-R1 finalize compatibility

A clean monitored capture must remain finalizable through the unchanged REC-R1 Preview→Accept authority. A failed/non-clean capture must remain non-finalizable. Monitoring state itself must not gain creative authority.

### 10. Fail-closed matrix

Reject stale accepted source, unsupported input or monitor backend/config, rate/channel mismatch, incompatible block size where required, malformed monitoring-plan/self-hash, corrupted validated trace, unsupported monitor gain/range and any attempt to treat monitor output as accepted audio without REC-R1 authority.

### 11. Runtime reconstruction

Reconstructing the derived monitor runtime from the same accepted revision/config should reproduce the same plan and deterministic scenario output while transient counters/state reset according to contract.

No Browser/UI claim is required in R2.

### 12. Dedicated evidence and permanent gate

Add one REC-R2 workflow without weakening the existing 30 gates. Expected total after R2: 31 permanent workflows.

Evidence must prove exact source/input/output binding, monitor OFF/ON capture equality, deterministic monitor output/metrics, runtime-only authority, exact failure instrumentation, REC-R1 clean-finalize compatibility, fail-closed incompatible/stale paths and reconstruction repeatability.

### 13. Promotion

Implementation/evidence complete → dedicated REC-R2 gate green → 31/31 exact-head green → independent artifact inspection → durable REC-R2 validation → validation successor 31/31 green → expected-head squash merge → Issue #149 completed → separate state-only closure to REC-R3.

## REC-R2 non-goals / 비목표

No Browser recording/monitoring UI, host-native microphone or speaker monitoring, measured host-native latency, zero-latency/hardware monitoring, take/comp, punch recording, effects/plugin monitoring, VST3/AU/CLAP hosting, PDC, sidechains, resampling, mastering or generalized commercial recording readiness.

## Successor after R2

If R2 validates cleanly: REC-R3 — truthful Studio/Browser recording + monitoring lifecycle surface with fresh restart/reopen proof, followed by parent Issue #142 bounded closure evaluation.

## Maximum intended REC-R2 outcome

> MUSICA can run a bounded deterministic input-monitoring path from the same provenance-bound simulated input used for capture, keep monitoring strictly runtime-only, prove monitoring does not alter captured recording bytes, and deterministically instrument capture/monitor failures while preserving REC-R1 finalize authority.

This remains a target claim until R2 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
