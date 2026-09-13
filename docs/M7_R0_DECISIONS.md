# M7-R0 Ratification Decisions / M7-R0 비준 결정

## Decision set

1. **Authority owner:** canonical automation is future Blueprint creative material, never Music IR/renderer/DAW state.
2. **R0 storage boundary:** standalone `automation-material-v0` only; accepted Blueprint storage/migration is deferred to R1 and is not claimed here.
3. **Stable identity:** explicit `lane_id`, `point_id`, namespaced `parameter_id`.
4. **Canonical scope:** `project | part`; derived `track_id` is excluded from canonical target identity.
5. **Canonical time:** quarter-note beat with origin `0.0`.
6. **Units:** normalized, decibel, hertz, semitone, ratio.
7. **Curves:** hold and linear only.
8. **Primitive proposals:** INSERT_POINT, DELETE_POINT, MOVE_POINT, SET_VALUE, SET_INTERPOLATION.
9. **Source binding:** project/revision/Blueprint SHA/automation-material SHA.
10. **Locks:** stable-ID exact/range/presence contracts; HARD conflicts must fail closed in future runtime authority.
11. **Semantic precedence:** future accepted explicit automation cannot be silently overwritten by a higher-level semantic proposal over the same protected scope.
12. **Backward compatibility:** existing projects are unchanged; R0 fabricates no automation from semantic curves or derived execution artifacts.

## Deferred to R1 or later

- Blueprint schema/storage integration and migration;
- candidate execution/Preview generation;
- M2 Accept/Discard integration;
- Browser automation lanes;
- deterministic lowering into Music IR/renderer control events;
- renderer/plug-in parameter maps;
- DAW automation reconciliation;
- real-time MIDI/OSC control;
- curved interpolation beyond hold/linear.

These deferrals are scope controls, not implied failures or implemented capabilities.
