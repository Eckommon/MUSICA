# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**REC-R3 — STUDIO/BROWSER RECORDING & MONITORING SURFACE + RESTART/REOPEN LIFECYCLE v0**

Issue `#152` — **OPEN**  
Parent mission: Issue `#142` — **Recording & Monitoring Foundation v0 — OPEN**

REC-R2 is validated, merged and completed. The next dependency-safe step is to expose the already validated capture, monitoring and recording-finalize authority through a truthful real Studio/Browser surface, then prove fresh service/process restart + project reopen lifecycle exactness.

## Canonical base / 공식 기준점

- canonical main after REC-R2 merge: `4d0e7988b979c05ee7f5a04ed7fb4cb043a2b60e`
- REC-R2 Issue `#149` — **COMPLETED**
- REC-R2 PR `#151` — **MERGED**
- implementation/evidence exact head `ec338120a61e1796a2cecd99aa66126fe6eebe29` — **31/31 SUCCESS**
- validation-record successor `af2a23e120123546a33791b902e685bd9da10738` — **31/31 SUCCESS**
- durable validation: `evidence/REC_R2_VALIDATION.md`
- dedicated artifact ID `11083583035`
- artifact ZIP SHA-256 `fa586bf0239901273eb4dcd77c3839b7a074a5bfd94dea569df96791d8404665`
- permanent workflow count: **31**

## Inherited authority / 상속 권한

```text
REC-R0:
accepted revision + explicit simulated input config
→ deterministic capture plan/runtime
→ exact PCM/report
→ derived only

REC-R1:
clean capture
→ source-bound recording-finalize candidate
→ Preview / HEAD + asset store unchanged
→ explicit Accept
→ immutable asset + accepted track/clip

REC-R2:
same capture blocks
→ copy-only direct monitor tap
→ deterministic simulated monitor sink/metrics
→ derived/runtime-only
```

REC-R3 must connect Studio/Browser to these existing authorities. It must not create a Browser-only recording store, direct asset import authority or direct audio-material commit endpoint.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground Studio/Browser lifecycle and existing authority surfaces

Inspect at minimum:

- `src/musica/studio_service.py`;
- `src/musica/studio_http.py`;
- `src/musica/studio_web/*`;
- current RTIO-R3 Studio runtime projection/restart implementation;
- MRAM-R3 Browser Preview/Accept patterns;
- `src/musica/recording_capture.py`;
- `src/musica/recording_monitor.py`;
- `src/musica/recording_finalize.py`;
- REC-R0/R1/R2 tests and durable validations.

Prefer extension of existing typed service/session projections rather than parallel state.

### 2. Freeze a typed recording/monitoring Browser projection

Bind exact:

- session/project identity;
- accepted revision ID;
- Blueprint/audio/routing/automation hashes;
- input backend/config identity;
- capture-plan/report SHA;
- capture clean/dirty/finalizable status;
- monitor enabled state;
- monitor-plan/report SHA;
- exact capture/monitor counters;
- prospective destination track/clip IDs where applicable;
- explicit authority flags showing runtime/Browser state is non-canonical.

Do not infer IDs from display labels or array positions.

### 3. Inspection-first capture and monitoring surface

Expose truthful derived values for:

- input sample rate/channels/block size/capture frames;
- capture cursor and frames captured;
- ERROR/SHORT_FILL/LATE/dropout-equivalent counts;
- monitor enabled state;
- monitor frames/blocks written;
- monitor-side output xrun count;
- source/report self-hashes;
- clean vs dirty capture status.

No Browser interaction may directly mutate accepted creative state.

### 4. Bounded Browser capture/monitor runtime actions

If runtime actions are exposed, delegate only to the existing REC-R0/R2 runtime semantics.

Preferred bounded actions:

- start one deterministic capture scenario;
- enable/disable bounded monitoring;
- stop/finalize runtime capture;
- discard/reset transient capture/monitor state.

Runtime actions must preserve accepted Project HEAD and asset/audio material.

### 5. Reuse REC-R1 finalize authority unchanged

A clean completed capture may produce a typed Browser recording-finalize proposal.

Required invariant:

```text
clean capture + accepted revision
→ Browser typed finalize proposal
→ existing build_recording_finalize_preview()
→ PREVIEW / HEAD and asset store unchanged
→ explicit Browser Accept
→ existing accept_recording_finalize_preview()
→ exactly one accepted recording revision
```

Do not create a second Browser recording Accept implementation.

### 6. Dirty capture truthfulness

A capture with ERROR/SHORT_FILL/LATE/dropout-equivalent failure must remain visibly non-finalizable under the unchanged REC-R1 rules.

The UI must not imply that monitored/dirty runtime bytes are accepted media.

### 7. Stale and unknown-handle fail-closed matrix

Reject at minimum:

- stale session ID;
- stale accepted revision;
- stale capture/monitor plan/report binding;
- stale recording Preview after HEAD advance;
- unknown destination track ID;
- duplicate/unknown clip identity;
- direct asset/audio mutation request;
- runtime action against an invalid lifecycle state.

### 8. Audition/accepted-state truthfulness

After explicit recording Accept:

- accepted Browser projection must show the exact new asset/track/clip identity;
- any routed/native audition must use accepted project state;
- transient capture/monitor sink bytes must never masquerade as accepted project media.

### 9. Fresh restart/reopen lifecycle

Use a genuinely fresh service/process boundary.

Prove:

```text
accepted recording revision
→ stop Studio/service
→ start fresh Studio/service
→ reopen project
→ same accepted revision
→ same immutable recording asset
→ same track/clip identity
→ same accepted audio material
→ same deterministic downstream plan/WAV where applicable
→ transient capture/monitor runtime absent/reset
```

Runtime reset is expected; accepted creative state persistence is required.

### 10. Real Chromium evidence

At minimum:

1. open source project;
2. inspect exact recording/monitoring projection;
3. run a deterministic clean monitored capture;
4. inspect clean status and exact metrics;
5. build recording Preview;
6. verify HEAD unchanged;
7. explicitly Accept;
8. verify accepted recording identity;
9. exercise a dirty capture and verify finalize blocked;
10. discard/reset without accepted mutation;
11. restart service/process;
12. reopen and verify accepted recording persists while runtime resets;
13. verify no unexpected console/page/request errors.

### 11. Dedicated evidence and permanent gate

Add a dedicated REC-R3 permanent workflow without weakening the existing **31** gates.

Expected total after R3: **32** permanent workflows.

Evidence should combine deterministic API/runtime evidence with real-browser screenshots/interactions and fresh restart/reopen proof.

### 12. Parent Issue #142 bounded closure evaluation

After R3 validates, evaluate every required capability in Issue #142 requirement-by-requirement.

Do not close the parent merely because R3 merged. Open the smallest missing rung if a material v0 requirement remains unproved.

### 13. Promotion

Implementation/evidence → dedicated REC-R3 gate → all workflows green on exact evidence head → independent artifact inspection → durable REC-R3 validation → successor exact-head full rerun → expected-head squash merge → Issue #152 completed → separate state-only parent #142 closure evaluation.

## REC-R3 non-goals / 비목표

No host-native microphone/line input, host-native speaker monitoring, measured host-native latency, hardware/zero-latency monitoring, take/comp, punch-in/out, effects/plugin monitoring, VST3/AU/CLAP hosting, PDC, resampling, sidechains, mastering or generalized commercial recording readiness.

## Maximum intended REC-R3 outcome

> **MUSICA can truthfully inspect bounded capture/monitoring runtime in Studio/Browser, finalize a clean capture through the existing REC-R1 Preview→explicit Accept authority, and recover the accepted recording exactly after fresh restart/reopen while transient Browser/runtime state remains derived and non-canonical.**

This remains a target claim until REC-R3 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
