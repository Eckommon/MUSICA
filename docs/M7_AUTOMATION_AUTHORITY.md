# M7 Automation & Continuous-Control Authority v0 / M7 자동화·연속제어 권한 v0

**Status / 상태:** `RATIFIED — M7-R0 CONTRACT/DESIGN VALIDATED`  
**Governing R0 Issue / 지배 R0 Issue:** `#68`  
**R0 implementation PR / 구현 PR:** `#69`  
**Durable evidence / 영속 근거:** `evidence/M7_R0_VALIDATION.md`  
**Next bounded extension / 다음 제한 확장:** `M7-R1 — Bounded Canonical Automation Runtime & Blueprint Integration`

## 1. Purpose / 목적

M7 defines how time-varying continuous musical decisions can become inspectable, lockable, editable, reproducible and programmable without allowing Browser points, Music IR control events, renderer state, plug-in state or DAW automation to become canonical by accident.

M7-R0 validates this authority/data model as **CONTRACT/DESIGN ONLY**. It does not itself implement accepted-project automation storage, runtime editing, rendering or external automation reconciliation.

## 2. Ratified authority invariant / 비준 권한 불변식

```text
future accepted Blueprint automation material
→ trusted deterministic lowering
→ derived Music IR / renderer automation events

user / AI / future bounded import proposal
→ source-bound AutomationEditCandidate
→ stable lane / point / parameter identity
→ lock + constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept only
→ existing M2 revision authority
```

Forbidden:

```text
Music IR control event → fabricated canonical automation
renderer / plug-in state → accepted Blueprint
Browser DOM/canvas coordinates → canonical state
AI-generated curve → implicit acceptance
DAW lane order/index → stable MUSICA identity
external automation artifact → accepted state without separately validated reconciliation
```

## 3. Canonical ownership / 공식 소유권

The ratified creative representation is `automation-material-v0`, not execution events.

R0 intentionally validates this as a standalone authority contract. Accepted Blueprint storage/migration is **not part of the R0 claim**. M7-R1 must integrate the contract into project authority with explicit backward compatibility before accepted revisions may store or mutate automation material.

A missing automation block means no accepted explicit automation. It must never trigger reverse inference from semantic curves, Music IR, renderer state or historical interchange artifacts.

## 4. Stable identities / 안정 ID

### Lane
Each lane owns stable `lane_id`. Array position, renderer lane order and DAW lane order are not identity.

### Point
Each point owns stable `point_id`. Moving a point changes beat, not identity.

### Parameter
`parameter_id` is backend-independent lowercase dotted namespace, for example:

```text
mix.gain
mix.pan
space.send
synth.cutoff
synth.resonance
```

These are MUSICA creative parameter identities, not VST parameter IDs, MIDI CC numbers or DAW-specific addresses.

## 5. Scope / 범위

M7-R0 v0 permits only:

```text
scope = project | part
```

`track` is excluded because current canonical Blueprint owns `part_id`, while Music IR `track_id` is derived execution identity.

- project scope → `owner_id = null`;
- part scope → stable canonical `part_id` once M7-R1 integrates Blueprint context.

## 6. Time / 시간

Canonical time:

```text
unit = quarter_note_beat
origin_beat = 0.0
```

Renderer ticks, samples and wall-clock milliseconds are not canonical creative identity in v0.

Arbitrary tempo-map automation remains outside the ratified R0 claim.

## 7. Value domain / 값 영역

Every lane declares explicit unit/range:

```text
normalized | decibel | hertz | semitone | ratio
minimum < maximum
```

Every point must lie within inclusive lane range. Backend-specific clamping or hidden conversion cannot rescue an invalid canonical value.

## 8. Curve model / 곡선 모델

The complete ratified R0 interpolation vocabulary is:

```text
hold | linear
```

Spline/bezier/exponential curves are not validated and must not be silently approximated into accepted canonical material.

Executable invariants include:

- unique lane IDs;
- unique lane target signatures;
- lane canonical order by `lane_id`;
- globally unique point IDs within material;
- unique beat per lane;
- point canonical order `(beat, point_id)`;
- valid declared range;
- every point within range.

## 9. Primitive edit vocabulary / 기본 편집 어휘

The exact ratified primitive set is:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
```

All are non-canonical proposals. Point-targeting operations require stable `lane_id + point_id`; INSERT targets a stable lane and introduces an explicit new stable point ID.

Not ratified in R0:

- lane create/delete;
- parameter reassignment;
- bulk quantization/humanization;
- arbitrary free-form transforms;
- curve simplification.

## 10. Source binding / 소스 결박

Every runtime candidate must bind:

```text
project_id
revision_id
blueprint_sha256
automation_material_sha256
```

Stale or mismatched source must fail closed before Preview generation. No silent rebase.

## 11. Lock model / 잠금 모델

`automation-lock-v0` is stable-ID aware and supports:

```text
HARD | SOFT
exact | range | presence
```

Modes are structurally disjoint:

- exact → `value`;
- range → `minimum + maximum`;
- presence → no exact/range payload.

The R0 executable checker validates stable lane/point reference integrity, matching parameter selectors, valid range order and selected-value consistency.

A future HARD conflict must produce:

```text
BLOCKED / HARD_LOCK_VIOLATION
preview_generation_allowed = false
project_mutation_authorized = false
music_ir_mutation_authorized = false
```

## 12. Semantic-control precedence / 의미 제어 우선순위

Once explicit automation is accepted by a later runtime milestone, it becomes a stronger exact creative commitment than a newly proposed high-level semantic transform over the same protected parameter/time scope.

A semantic proposal may not silently overwrite or regenerate accepted protected automation. R0 ratifies this precedence principle; the broad overlap resolver is not implemented in R0.

## 13. Derived lowering boundary / 파생 lowering 경계

Future valid direction:

```text
canonical lane/point/parameter IDs
→ deterministic adapter mapping
→ derived execution events
```

Forbidden reverse authority:

```text
execution events
→ guessed canonical lane/point identity
```

Renderer/Music IR events remain derived even after later automation runtime implementation.

## 14. Executable R0 validation / 실행형 R0 검증

`src/musica/automation_contracts.py` validates schema plus cross-field invariants only. It does not:

- mutate Project bundles;
- create Preview;
- commit M2 revisions;
- lower to Music IR;
- render audio;
- communicate with DAWs or plug-ins.

M7-R0 final evidence proves deterministic contract evidence generation and hash-binds the ratification path.

## 15. R0 validation evidence / R0 검증 근거

Final evidence-bearing head:

`5b5aeb8c6bee3f8e2d48f41543b5bd5cd33e43ef`

Final successful gates:

- MUSICA CI `34791538725`;
- M7-R0 `34791538703`;
- M6-R4 `34791538853`;
- M6-R3 `34791538669`;
- M6-R2 `34791538762`;
- M6-R1 `34791538672`;
- M5-R3 `34791538695`;
- M5-R4 `34791538743`.

Artifact:

- ID `10328327862`;
- packaging SHA-256 `1360f29d6568a75e7bcf740e605e37fd1f97df9715bdb7326133047afd2753a5`;
- internal manifest SHA-256 `aab674c3953abcbca94d659da4d3627d65a682b4039510f6f6e255e08efee5`;
- 2/2 internal manifest records verified;
- 21 source/contract files hash-bound;
- pre-durable and successor internal trees: 3 files / 0 differences.

## 16. Backward compatibility / 하위 호환성

Existing M0→M6 projects remain valid. R0 changes no accepted Blueprint storage contract and fabricates no canonical automation.

M7-R1 must preserve this property while adding optional automation-capable accepted storage.

## 17. Next bounded extension: M7-R1 / 다음 제한 확장

M7-R1 may implement only the trusted-core runtime necessary to make the R0 contract operational in accepted project authority:

```text
backward-compatible optional Blueprint automation storage
→ deterministic automation material hash
→ source-bound AutomationEditCandidate
→ stable identity/range/lock/stale checks
→ READY_FOR_PREVIEW or BLOCKED
→ non-canonical Preview
→ explicit Accept / Discard
→ existing M2 revision authority
```

M7-R1 must support only the five ratified point primitives and must revalidate the resulting full material.

M7-R1 remains outside Browser UI, renderer automation, plug-in mapping and DAW automation reconciliation.

## 18. Explicit non-claims / 명시적 비주장

Neither M7-R0 nor this state record validates:

- runtime automation editing (until R1 evidence exists);
- accepted Blueprint automation storage/migration (until R1 evidence exists);
- Browser automation lanes;
- audible automation rendering;
- Music IR automation execution;
- VST/AU/CLAP mapping/hosting;
- MIDI CC / OSC / real-time control;
- DAW automation import/export/reconciliation;
- arbitrary tempo-map automation;
- spline/bezier/exponential curves;
- mixer or synthesis/DSP runtime implementation;
- human-subject usability/perceptual benefit.

**Repository evidence remains authoritative over conversation/model memory.**
