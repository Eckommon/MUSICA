# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**RTIO-R3 — STUDIO/BROWSER RUNTIME INSPECTION + RESTART/REOPEN LIFECYCLE v0**

Issue `#139` — **OPEN**

Parent mission: Issue `#129` — **Real-Time Audio Engine & Device Foundation v0 — OPEN**

RTIO-R2 Issue `#136` is validated, merged and completed.

Do **not** add microphone input, recording, monitoring, plugin hosting, resampling, host-native device guarantees or Browser-originated creative authority in R3.

## Canonical base / 공식 기준점

- canonical main after RTIO-R2 implementation merge:
  `f01be3232459dec9e687c7c6b961b73f8ef6cbd5`
- parent Issue `#129` — **OPEN**
- RTIO-R2 Issue `#136` — **COMPLETED**
- RTIO-R2 PR `#138` — **MERGED**
- R2 implementation/evidence exact head:
  `cf4e9d3dba17d1ba130a66e5fd79b9a38d57db29` — **27/27 SUCCESS**
- R2 validation-record successor:
  `a79da14a30e9428e7fc7e88960b25f837e6c85fd` — **27/27 SUCCESS**
- durable validation: `evidence/RTIO_R2_VALIDATION.md`
- dedicated artifact ID: `11044417646`
- artifact ZIP SHA:
  `372829e4ca4abe4b953a603164bd8f19c9d08cdbc4615d7f07abd7b3f7ab0337`
- permanent workflow count at validated R2 state: **27**

## Exact implementation order / 정확한 구현 순서

1. Re-ground `studio_service.py`, `studio_http.py`, `studio_web/*`, existing real-browser patterns, and RTIO-R0/R1/R2 runtime modules/tests/evidence.
2. Freeze a typed non-canonical runtime inspection payload binding exact accepted revision/source hashes, realtime-plan SHA, backend/config, transport state, exact playhead, latency provenance and error/short-fill/late/xrun counters.
3. Add an explicit StudioService runtime-session boundary bound to one accepted source revision and one exact realtime plan.
4. Add inspection-first read-only API/UI; visibly mark runtime/transport/metrics as derived/non-canonical.
5. Only if needed for complete evidence, add bounded runtime-only play/stop/seek commands that delegate to existing RTIO-R2 transport and never mutate Project creative state.
6. Reject stale project/runtime handles, mismatched plan SHA and unknown IDs.
7. Prove accepted HEAD equality across all runtime inspection/commands.
8. Prove fresh service/process restart + project reopen reconstructs the same accepted source/realtime-plan binding and deterministic scenario identities while runtime playhead is not persisted as creative state.
9. Add real Chromium E2E proving exact displayed source/plan/state/playhead/config/metrics, derived authority labels, restart/reopen exactness and fail-closed stale/unknown paths.
10. Add dedicated RTIO-R3 evidence + permanent workflow; expected total **28** workflows.
11. Promote through exact-head full CI → independent artifact inspection → durable validation → validation-successor full CI → expected-head squash merge → Issue #139 completion.
12. After R3 validation, evaluate every required capability of parent Issue #129 before deciding closure.

## RTIO-R3 non-goals

No microphone/line input, recording/monitoring, host-native latency guarantees, VST3/AU/CLAP hosting, plugin-delay compensation, resampling, sidechains, mastering or generalized commercial realtime readiness.

## Maximum intended R3 outcome

> **MUSICA can truthfully inspect its provenance-bound realtime transport/runtime state through Studio/Browser, expose exact frame/configuration/latency/dropout provenance, and reconstruct the same accepted source/realtime-plan binding after fresh restart/reopen while Browser/runtime state remains derived and cannot reverse-author accepted creative state.**

This remains a target claim until R3 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
