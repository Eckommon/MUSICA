# M7 Automation & Continuous-Control Authority v0 / M7 자동화·연속제어 권한 v0

**Status / 상태:** `PROPOSED — M7-R0 CONTRACT/DESIGN ONLY`  
**Governing Issue / 지배 Issue:** `#68`

## 1. Purpose / 목적

M7 defines how time-varying continuous musical decisions can become inspectable, lockable, editable, reproducible and programmable without allowing Browser points, Music IR control events, renderer state, plug-in state or DAW automation to become canonical by accident.

M7은 시간에 따라 변하는 연속적 음악 결정을 검사·잠금·편집·재현·프로그래밍할 수 있게 하되 Browser point, Music IR control event, renderer/plug-in state, DAW automation이 우연히 canonical authority가 되는 것을 금지합니다.

M7-R0 is **contract/design only**. It does not implement accepted-project mutation, Studio lanes, rendering, plug-in hosting, real-time MIDI/OSC control or DAW automation round-trip.

## 2. Authority invariant / 권한 불변식

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

## 3. Canonical ownership decision / 공식 소유권 결정

The canonical creative representation is `automation-material-v0`, not execution events. R0 validates this contract as a standalone authority model. The exact Blueprint storage/migration path is intentionally **not implemented in R0**; R1 must add an explicit Blueprint integration path and prove backward compatibility before any accepted revision may contain or mutate this material.

공식 창작 표현은 실행 event가 아니라 `automation-material-v0`입니다. R0는 이를 standalone authority contract로 검증합니다. 정확한 Blueprint 저장/migration 경로는 R0에서 구현하지 않으며, R1이 명시적으로 통합하고 하위 호환성을 증명해야 합니다.

## 4. Stable identities / 안정 ID

### Lane identity

Each lane owns a stable `lane_id`. Lane identity is not array position and is not a renderer/DAW lane index.

### Point identity

Each point owns a stable `point_id`. Point identity is not beat position: moving a point changes `beat`, not `point_id`.

### Parameter identity

`parameter_id` is a backend-independent lowercase dotted namespace such as:

```text
mix.gain
mix.pan
space.send
synth.cutoff
synth.resonance
```

These identifiers describe MUSICA creative parameters. They are **not** VST parameter IDs, MIDI CC numbers, DAW automation IDs or renderer-specific addresses. Backend mappings require later explicit adapter contracts/evidence.

## 5. Scope model / 범위 모델

M7-R0 v0 permits only:

```text
scope = project | part
```

`track` is deliberately excluded because the currently validated Blueprint has canonical `part_id` identity while Music IR `track_id` is derived execution state.

- `project` scope requires `owner_id = null`;
- `part` scope requires a stable canonical `part_id` once R1 integrates with Blueprint context.

## 6. Time domain / 시간 영역

Canonical time is:

```text
unit = quarter_note_beat
origin_beat = 0.0
```

The material does not store renderer ticks, sample positions or wall-clock milliseconds as canonical identity.

M7-R0 does not ratify arbitrary tempo-map automation. R1 must define the allowed Blueprint tempo assumptions when it integrates automation with accepted projects.

## 7. Value domain / 값 영역

Each lane declares:

```text
unit
minimum
maximum
```

Allowed v0 units:

```text
normalized | decibel | hertz | semitone | ratio
```

The executable R0 contract validator requires `minimum < maximum` and every point value to remain inside the declared inclusive range.

Units must remain explicit. A normalized value cannot be silently reinterpreted as dB/Hz or a renderer-native value.

## 8. Curve model / 곡선 모델

R0 intentionally ratifies only the smallest deterministic interpolation vocabulary:

```text
hold | linear
```

A point's `interpolation` describes the segment leaving that point toward the next point. Curved/spline/bezier/exponential interpolation is not validated in R0 and must not be silently approximated into an accepted canonical curve.

Within one lane:

- point IDs are unique;
- beats are unique;
- points use canonical order `(beat, point_id)`;
- lane IDs are unique;
- lane target signatures are unique;
- lane list uses canonical order by `lane_id`.

R0 also requires point IDs to be globally unique within one automation material so future conflict/lock reporting cannot become lane-order dependent.

## 9. Primitive edit vocabulary / 기본 편집 어휘

`automation-edit-candidate-v0` supports only:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
```

All operations are non-canonical proposals. Except `INSERT_POINT`, point operations require both stable `lane_id` and stable `point_id`.

R0 does not define lane creation/deletion, parameter reassignment, bulk quantization, curve simplification, humanization or arbitrary transform languages.

## 10. Source binding / 소스 결박

Every future edit candidate must bind:

```text
project_id
revision_id
blueprint_sha256
automation_material_sha256
```

A stale or mismatched source must fail closed before Preview generation. R0 defines the typed result code `STALE_SOURCE`; runtime enforcement belongs to R1.

## 11. Lock model / 잠금 모델

`automation-lock-v0` is stable-ID aware and supports:

```text
HARD | SOFT
exact | range | presence
```

Lock selectors may protect a lane, point, beat, value, interpolation or parameter identity. Exact/range/presence modes are structurally disjoint in the schema:

- `exact` requires `value`;
- `range` requires `minimum` and `maximum`;
- `presence` carries no value/range payload.

The executable R0 validator additionally checks lane/point references, parameter selector consistency and `minimum <= maximum` for range locks.

A future HARD-lock violation must yield `BLOCKED / HARD_LOCK_VIOLATION` with no canonical mutation.

## 12. Semantic-controls precedence / 의미 제어와의 우선순위

Existing semantic controls and future exact automation are different abstraction depths.

R0 establishes this rule:

> **Accepted explicit automation, once introduced by a later runtime milestone, is a stronger exact creative commitment than a newly proposed semantic transform over the same parameter/time scope. A semantic proposal may not silently overwrite or regenerate locked explicit automation.**

The actual semantic-to-automation conflict resolver is not implemented or validated in R0.

## 13. Derived lowering boundary / 파생 lowering 경계

Future lowering may translate canonical automation into renderer/Music IR events, but derived events do not own identity and cannot be reverse-promoted without a separately proven source-bound reconciliation contract.

Therefore:

```text
canonical lane/point/parameter IDs
→ deterministic adapter mapping
→ execution events
```

is allowed in a later milestone, while:

```text
execution events
→ guessed canonical lane/point IDs
```

is forbidden.

## 14. R0 executable validation / R0 실행형 검증

`src/musica/automation_contracts.py` is permitted in R0 only as an executable contract checker. It must not:

- mutate Project bundles;
- generate Preview state;
- commit revisions;
- lower to Music IR;
- render audio;
- communicate with plug-ins/DAWs.

It validates schema plus cross-field invariants that JSON Schema does not express clearly.

## 15. Backward compatibility / 하위 호환성

Existing M0→M6 projects contain no canonical M7 automation material and remain valid. R0 does not migrate them or fabricate automation from semantic curves, Music IR, renderer output or historical DAW artifacts.

## 16. Explicit non-claims / 명시적 비주장

M7-R0 does **not** validate:

- runtime automation edit authority;
- accepted Blueprint automation storage/migration;
- Browser automation lanes;
- audible automation rendering;
- VST/AU/CLAP parameter mapping or hosting;
- MIDI CC / OSC / real-time control;
- DAW automation import/export round-trip;
- arbitrary tempo-map automation;
- bezier/spline/exponential curves;
- mixer implementation;
- synthesis/DSP runtime implementation;
- human-subject usability or perceptual benefit.

Repository evidence remains authoritative over conversation/model memory.
