# M6-R0 Acceptance / M6-R0 수용 기준

**Milestone / 마일스톤:** `M6-R0 — Precision Editing Authority & Canonical Note Model v0`

**Governing Issue / 지배 Issue:** `#51`

## 1. Acceptance verdict / 수용 판정

M6-R0 is a **contract/design milestone**, not a piano-roll implementation milestone.

R0 may be accepted only when the repository contains coherent normative documents, machine-readable contracts, examples and tests that make the next implementation step unambiguous while preserving existing project authority.

## 2. Required artifacts / 필수 산출물

R0 requires all of the following on one evidence-bearing exact PR head:

- `docs/M6_PRECISION_EDITING_AUTHORITY.md`
- this acceptance document
- `schemas/exact-note-material-v0.schema.json`
- `schemas/note-edit-candidate-v0.schema.json`
- `schemas/note-edit-authority-result-v0.schema.json`
- valid exact-note material example
- valid edit-candidate example
- valid `READY_FOR_PREVIEW` authority-result example
- valid blocked stale-source authority-result example
- valid blocked HARD-lock authority-result example
- deliberately invalid direct-Music-IR candidate example
- contract tests covering the above
- explicit M6-R1 handoff

## 3. Authority invariants / 권한 불변식

The following must be normative and machine-visible where applicable:

| Invariant / 불변식 | Required result / 필수 결과 |
|---|---|
| Blueprint/M2 remains canonical | PASS |
| Music IR remains derived | PASS |
| edit candidate is non-canonical | PASS |
| `authority_target` cannot select Music IR | PASS |
| `preview_only` is true for candidate v0 | PASS |
| explicit Accept remains required | PASS |
| authority result cannot authorize project mutation | PASS |
| authority result cannot authorize direct Music IR mutation | PASS |
| stale source is a blocking conflict class | PASS |
| HARD lock violation is a blocking conflict class | PASS |

## 4. Exact-note contract / exact-note 계약

The exact-note material contract must define at least:

- stable `note_id`;
- `part_id` ownership;
- optional `section_id`;
- absolute musical `start_beat`;
- positive `duration_beats`;
- bounded pitch and velocity;
- explicit quarter-note-beat time base;
- renderer-independent semantics.

The design must state that uniqueness of note IDs and project/section bounds are semantic invariants requiring M6-R1 runtime validation when JSON Schema cannot express them safely.

## 5. Backward-compatibility gate / 하위 호환 gate

R0 must preserve the validity and semantics of existing Blueprint v0 projects that use legacy `motif_notes`.

Required policy:

```text
legacy project without exact_timeline
→ existing compiler behavior unchanged

project with exact_timeline
→ additional exact-note material validation required
→ explicit material-selection policy required
```

R0 must not silently make exact-note material mandatory and must not bump `blueprint_version` without a separate explicit version decision.

## 6. Exact lowering boundary / exact lowering 경계

The accepted design must distinguish:

- legacy motif generation/lowering, where existing bounded semantic mechanisms may apply; and
- explicit exact-note lowering, where accepted pitch/start/duration/velocity must be faithfully lowered rather than silently rescaled by semantic energy/density/motion.

If semantic intent is to change exact note content, it must produce a new explicit Blueprint candidate/diff first.

## 7. Candidate operation vocabulary / candidate 연산 어휘

R0 operation vocabulary is frozen to:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

Operations must address existing notes by stable `note_id` + `part_id`, not by array index.

Batch transforms remain deferred unless later lowered into these primitives or separately contracted.

## 8. Fail-closed authority cases / 실패 폐쇄 권한 사례

The R0 contract/examples/tests must preserve these classifications:

### Stale source

```text
source revision/hash no longer equals active accepted state
→ BLOCKED
→ conflict code = STALE_SOURCE
→ preview_generation_allowed = false
```

### HARD lock

```text
candidate would violate a protected HARD rule
→ BLOCKED
→ conflict code = HARD_LOCK_VIOLATION
→ preview_generation_allowed = false
```

### Direct Music IR authority attempt

```text
authority_target = music_ir or equivalent
→ schema/contract rejection
```

### Valid candidate

```text
source binding current
+ operation representable
+ no blocking rule
→ READY_FOR_PREVIEW
→ preview_generation_allowed = true
→ project_mutation_authorized = false
→ explicit_accept_required = true
```

## 9. Stable-lock limitation / stable lock 제한

R0 must not claim note-specific HARD locking through mutable array-index JSON pointers.

The design must explicitly require a stable-ID-aware note-lock selector in M6-R1 before note-specific locks are claimed as implemented.

Existing safely provable ancestor/current Blueprint HARD locks remain authoritative.

## 10. Regression gate / 회귀 gate

R0 cannot merge until its exact PR head passes:

- Python 3.11 full repository suite;
- Python 3.12 full repository suite + prior evidence chain;
- M4-R3 Chromium E2E;
- M5-R2 Windows FluidSynth evidence;
- M5-R3 DAWproject evidence;
- M5-R4 paired Windows evidence;
- M6-R0 contract tests.

R0 does not require a new audio-render artifact because it does not implement the note-edit engine.

## 11. Non-goals / 비목표

R0 acceptance does not prove:

- working piano-roll UI;
- end-to-end accepted note editing;
- stable note-specific lock runtime;
- arbitrary DAW note round-trip acceptance;
- arbitrary tempo-map editing;
- waveform/audio editing;
- automation/mixer/plugin editing;
- human usability evidence.

## 12. Completion claim / 완료 주장

If every R0 gate passes, the allowed claim is:

> **MUSICA has ratified a machine-readable authority/data contract for exact note-level creative state and non-canonical user edit candidates while preserving Blueprint/M2 authority above Music IR.**

The exact next implementation milestone becomes:

> **M6-R1 — Typed Exact-Note Material + Edit Engine**
