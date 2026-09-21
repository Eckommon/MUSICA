# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**MRAM-R2 — NATIVE MIXER AUTOMATION TARGET MAPPING v0**

Parent mission: Issue `#115` — **Mixer Routing & Automation Foundation v0 — OPEN**

MRAM-R1 Issue `#121` is validated, merged and completed. The next dependency-safe step is to extend MUSICA's existing typed automation authority/lowering model to stable native mixer targets without introducing a second automation authority model.

Do **not** add Browser routing/automation UI, realtime device I/O, recording, plugin hosting, sidechains or generalized parameter automation in R2.

## Canonical base / 공식 기준점

- canonical main after MRAM-R1 implementation merge:
  `422f30f78b39b333dd970bf3a20e94e1ba64e7fb`
- parent Issue `#115` — **OPEN**
- MRAM-R1 Issue `#121` — **COMPLETED**
- MRAM-R1 PR `#122` — **MERGED**
- R1 pre-validation exact head:
  `91d9629b4b017a70f30bb53d273890e22cd87734` — **22/22 SUCCESS**
- R1 validation-record successor:
  `009db978aab242525e20db4677083201c7af645f` — **22/22 SUCCESS**
- durable validation: `evidence/MRAM_R1_VALIDATION.md`
- dedicated artifact ID: `10532212394`
- dedicated artifact ZIP SHA:
  `4a59898baf16af1d7f26d14a3f31868fc573ee028d996f5c62ba5a8881be6da0`
- accepted routed-mix plan SHA:
  `a4a67b79a2a402b08280b7f9c39d291f7b669800be39d558e9a1bc9fed2bb74e`
- accepted routed WAV SHA:
  `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4`

Permanent workflow count at the R1 validated state: **22**.

## Inherited authority / 상속 권한

R2 inherits:

```text
ATCM:
immutable audio assets
→ accepted audio tracks/clips
→ accepted static per-track mixer
→ deterministic native mix
→ Browser truth + reopen

M7 automation:
typed automation material
→ source-bound edit candidate / Preview / explicit Accept
→ deterministic lowering/runtime evidence
→ accepted automation as creative state

MRAM-R0/R1:
explicit routing DAG
→ trusted routing Preview / Accept
→ accepted routing state
→ deterministic routed offline mixer
```

R2 must connect the already accepted automation state to the already accepted native mixer/routing identities. It must not create a parallel automation store, generic runtime write-back path or Browser-only authority.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground the existing automation stack before changing schemas

Inspect at minimum:

- automation schemas and target identity fields;
- `src/musica/automation_edit.py`;
- automation validation/lowering/runtime modules;
- M7-R0/R1/R2/R3/R4/R5/R6 tests and durable validation records;
- `src/musica/audio_mixer_edit.py`;
- `src/musica/routing_contracts.py`;
- `src/musica/routed_mixer.py`;
- `evidence/MRAM_R1_VALIDATION.md`.

Determine exactly how current `project|part` target scope is represented, hashed, previewed, accepted, lowered and consumed.

Do not retrofit native mixer targets until backward compatibility and authority boundaries are explicit.

### 2. Freeze native mixer automation target identity v0

Prefer a versioned target shape that can distinguish legacy targets from native mixer targets without changing the meaning of existing accepted automation.

Initial supported target identities:

```text
audio_track:<track_id>:gain_db
audio_track:<track_id>:pan
routing_node:<node_id>:gain_db
routing_node:<node_id>:pan
```

Equivalent structured fields are acceptable if they are schema-versioned and canonical.

Each target must bind:

- target kind;
- stable target ID;
- parameter ID;
- unit;
- numeric range;
- interpolation policy;
- exact source accepted revision/Blueprint;
- exact referenced audio/routing identity where needed.

Do not support wildcard, name-only or position-only addressing.

### 3. Freeze bounded parameter semantics

For R2, prefer only:

- gain in dB with the already validated native mixer gain rule;
- pan with the already validated native mixer pan range/law.

Explicitly define:

- accepted min/max range;
- value normalization policy;
- interpolation mode;
- time domain and conversion to sample/frame positions;
- endpoint behavior;
- duplicate-time-point policy;
- out-of-range behavior;
- missing target behavior.

Keep mute/solo/send-gain automation out unless they can be specified without ambiguous event semantics.

### 4. Preserve source-bound Preview→Accept authority

Native mixer automation edits must continue through the existing trusted automation candidate path.

Required invariant:

```text
exact accepted revision
→ source-bound automation candidate
→ validate target identity + source hashes
→ Preview only; accepted HEAD unchanged
→ explicit trusted Accept
→ revalidate source/head/target/routing/audio
→ exactly one accepted revision advance
```

Generic project commit and runtime objects must remain unable to introduce or change accepted automation.

### 5. Extend validation for current native identities

Preview and Accept must reject:

- missing track ID;
- missing routing-node ID;
- target kind/ID mismatch;
- unsupported parameter;
- out-of-range value;
- stale source revision;
- stale Blueprint/audio/routing/automation hashes;
- target removed after Preview;
- routing change that invalidates target identity before Accept;
- duplicate/ambiguous target identity;
- unsupported interpolation or unit.

Validation must use exact stable IDs, not UI names.

### 6. Deterministic automation lowering for native mixer targets

Lower accepted automation into a deterministic derived representation that binds:

- exact accepted revision;
- automation material SHA;
- audio material SHA;
- routing material SHA;
- exact target identity;
- parameter/unit/range;
- ordered automation points;
- interpolation;
- deterministic frame/sample positions;
- lowering policy/version;
- derived lowering SHA.

The lowering representation remains derived/non-canonical.

### 7. Apply lowered automation inside the routed mixer

Integrate automation without replacing MRAM-R1 routing or ATCM-R2 numeric semantics.

Recommended execution model:

```text
accepted automation
→ deterministic per-target lowering
→ per-frame/per-segment gain/pan value resolution
→ track processing
→ primary output + post-fader sends
→ node input sum
→ node gain/pan automation
→ node output/sends
→ master
→ inherited hard clip
→ PCM16 stereo WAV
```

Freeze the exact point at which track and node automation is sampled/applied.

### 8. Controlled audible/output proof

Build evidence with a small accepted routed project.

At minimum prove independently:

1. accepted static routed baseline → plan/WAV A;
2. Preview track gain automation → HEAD unchanged;
3. explicit Accept → exactly one revision advance;
4. routed plan/WAV B changes exactly as documented;
5. track pan automation produces deterministic stereo change;
6. routing-node gain automation produces deterministic downstream change;
7. routing-node pan automation produces deterministic stereo change;
8. independent rerun reproduces exact lowering/plan/WAV hashes.

Use at least one change where the output difference is numerically inspectable, not only hash-different.

### 9. Reopen and compatibility proof

Export/import or reopen must preserve:

- accepted automation target kind/ID/parameter;
- accepted points/interpolation;
- accepted audio/routing state;
- deterministic lowering SHA;
- deterministic routed plan SHA;
- deterministic routed WAV SHA.

Also prove legacy existing `project|part` automation examples remain valid and deterministic.

### 10. Fail-closed negative matrix

Reject at least:

- unsupported native target kind;
- missing target ID;
- removed track/node;
- stale Preview;
- generic commit bypass;
- invalid parameter/unit/range;
- malformed/non-canonical target identity;
- unsupported interpolation;
- duplicate/conflicting identity where the contract forbids it;
- missing/corrupt audio asset;
- invalid routing DAG;
- source sample-rate mismatch under the existing no-resampling policy.

### 11. Dedicated evidence and permanent gate

Add a dedicated MRAM-R2 workflow without weakening the existing **22** gates.

Expected total after R2: **23** permanent workflows.

Evidence should bind exact source hashes and prove:

```text
accepted routed source
→ native mixer automation candidate
→ Preview
→ HEAD unchanged
→ explicit Accept
→ exact accepted target identity
→ deterministic lowering A/B
→ deterministic routed plan/WAV A/B
→ controlled audible/output change
→ reopen exactness
→ legacy automation compatibility
→ stale/missing/unsupported/bypass paths fail closed
```

### 12. Promotion

R2 promotion requires:

- implementation/evidence complete;
- dedicated MRAM-R2 gate green;
- all 23 permanent workflows green on exact evidence-bearing head;
- independent artifact digest/manifest/hash inspection;
- durable `evidence/MRAM_R2_VALIDATION.md`;
- all 23 workflows green again on exact validation-record successor head;
- expected-head squash merge;
- R2 Issue completed;
- separate state-only closure pointing to MRAM-R3.

## MRAM-R2 non-goals / 비목표

Do not implement or claim in R2:

- Browser routing/automation editing;
- send-gain automation unless separately frozen;
- mute/solo event automation unless separately frozen;
- sidechains;
- realtime callbacks/device transport;
- recording/monitoring;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- resampling;
- warp/time-stretch/pitch shift;
- mastering;
- generalized commercial release readiness.

## Successor after R2

If R2 validates cleanly, exact next rung:

> **MRAM-R3 — truthful Browser editing/inspection for accepted routing and native mixer automation, plus fresh restart/reopen lifecycle proof without Browser/runtime reverse authority.**

## Maximum intended R2 outcome

> **MUSICA can bind accepted typed automation to stable native audio-track and routing-node gain/pan targets, lower that automation deterministically into routed mixer execution, and reproduce the resulting routed plan/WAV exactly while stale, unsupported, missing-target and bypass paths remain fail-closed.**

This remains a target claim until R2 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
