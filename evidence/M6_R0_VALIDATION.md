# M6-R0 Validation / M6-R0 검증 근거

**Status / 상태:** `VALIDATED — CONTRACT ONLY / 계약 범위 검증 완료`

**Date / 날짜:** 2026-09-12

**Governing Issue / 지배 Issue:** `#51`

**Implementation PR / 구현 PR:** `#52`

## 1. Verdict / 판정

M6-R0 validates the **authority and machine-readable data contract** required for future exact note-level editing while preserving Blueprint/M2 as canonical project authority above derived Music IR.

M6-R0는 향후 exact note-level 편집에 필요한 **권한 및 기계판독 데이터 계약**을 검증하며, 파생 Music IR보다 Blueprint/M2의 공식 프로젝트 권한을 유지합니다.

Allowed completion claim:

> **MUSICA has a validated contract for representing exact note-level creative state and for expressing user note edits as source-bound, non-canonical Blueprint candidates that require explicit acceptance.**

R0 does **not** validate an edit engine or piano-roll UI.

## 2. Evidence-bearing design head / 근거 보유 설계 head

First fully green R0 contract head:

- head: `3e37e8eda72c6dadd3663915a4010e2899f8fff4`
- full MUSICA CI: `34688857283` — **SUCCESS**
- M5-R3 DAWproject regression: `34688857297` — **SUCCESS**
- M5-R4 paired-audio regression: `34688857295` — **SUCCESS**

The R0 contract will be rerun once more after this durable evidence file is present. Merge is prohibited until that successor exact head is also green.

## 3. Normative artifacts / 규범 산출물

- `docs/M6_PRECISION_EDITING_AUTHORITY.md`
- `docs/M6_ACCEPTANCE.md`
- `schemas/exact-note-material-v0.schema.json`
- `schemas/note-edit-candidate-v0.schema.json`
- `schemas/note-edit-authority-result-v0.schema.json`
- `tests/test_m6_r0_contract.py`

Examples:

- `examples/note-material/valid/dark-electronic-explicit-timeline-v0.json`
- `examples/note-edits/valid/repitch-and-move-candidate-v0.json`
- `examples/note-edits/valid/ready-for-preview-result-v0.json`
- `examples/note-edits/valid/blocked-stale-source-result-v0.json`
- `examples/note-edits/valid/blocked-hard-lock-result-v0.json`
- `examples/note-edits/invalid/direct-music-ir-authority-candidate.json`

## 4. Contract decisions proven / 검증된 계약 결정

### 4.1 Canonical authority

```text
Accepted Blueprint / M2 revision
> Preview / candidate
> Music IR
> renderer / interchange artifact
```

Music IR is executable derived state only.

The candidate schema permits only:

```text
authority_target = blueprint_exact_note_material
preview_only = true
```

A candidate cannot select Music IR as creative authority.

### 4.2 Exact note material

The R0 exact-note contract defines:

- stable `note_id`;
- explicit `part_id` ownership;
- optional `section_id`;
- absolute quarter-note `start_beat`;
- positive `duration_beats`;
- bounded pitch `0..127`;
- bounded velocity `1..127`;
- small renderer-independent articulation/identity metadata.

Quarter-note beat coordinates are canonical at the creative layer; ticks/seconds remain derived lowering/rendering coordinates.

### 4.3 Stable edit addressing

Primitive R0 edit vocabulary:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

Existing notes are addressed by `note_id + part_id`, never mutable array index.

### 4.4 Source binding

Every candidate is bound to:

```text
project_id
+ revision_id
+ canonical Blueprint SHA-256
```

The contract reserves `STALE_SOURCE` as a blocking authority conflict. Silent rebase is forbidden by the normative design.

### 4.5 Fail-closed authority result

Every authority result requires:

```text
explicit_accept_required     = true
project_mutation_authorized  = false
music_ir_mutation_authorized = false
```

`READY_FOR_PREVIEW`:

```text
conflicts = []
preview_generation_allowed = true
```

`BLOCKED`:

```text
conflicts >= 1
preview_generation_allowed = false
```

Bounded conflict codes include:

- `STALE_SOURCE`
- `HARD_LOCK_VIOLATION`
- `CONSTRAINT_VIOLATION`
- `INVALID_NOTE`
- `UNKNOWN_NOTE`
- `PART_MISMATCH`
- `UNREPRESENTABLE_EDIT`

## 5. Negative contract evidence / 음성 계약 근거

The dedicated R0 tests establish schema/contract rejection for:

- direct Music IR authority target;
- candidate claiming `preview_only = false`;
- note operation attempting array-index addressing;
- pitch outside the v0 bounded domain;
- non-positive duration;
- `READY_FOR_PREVIEW` carrying a hidden conflict;
- `BLOCKED` with no explicit conflict;
- authority result attempting `project_mutation_authorized = true`;
- authority result attempting `music_ir_mutation_authorized = true`.

The R0 examples also machine-validate explicit fail-closed result shapes for:

- `STALE_SOURCE`;
- `HARD_LOCK_VIOLATION`.

The HARD-lock example is deliberately identified as a **contract shape** for the future M6 stable-ID-aware selector. R0 does not claim that the current v0 JSON-pointer lock engine already implements note-specific stable locking.

## 6. Backward compatibility / 하위 호환

Existing Blueprint v0 fixtures remain valid.

R0 does not replace or invalidate current melody material:

```text
legacy motif_notes
→ existing compiler behavior remains valid
```

The new exact-note contract is additive:

```text
materials.melody.exact_timeline
→ additional exact-note validation in M6-R1
```

No incompatible Blueprint version change is claimed in R0.

## 7. Compiler boundary / Compiler 경계

Repository inspection established that the current compiler:

- uses `PPQ = 480` as a lowering detail;
- compiles `motif_notes` as a repeating motif;
- currently applies bounded semantic energy scaling to generated motif velocity.

R0 therefore freezes this future distinction:

```text
legacy motif path
→ existing semantic/generative lowering may remain

explicit exact-note path
→ pitch/start/duration/velocity lower faithfully
→ semantic change to those exact decisions requires a new explicit Blueprint candidate/diff first
```

The exact-note compiler path itself is **NOT IMPLEMENTED** in R0.

## 8. Lock boundary / Lock 경계

Existing Blueprint HARD locks remain authoritative wherever the current runtime can prove their protected target.

R0 explicitly rejects the idea of treating array index as stable note identity.

Before claiming note-specific HARD-lock runtime support, M6-R1 must implement a stable-ID-aware note-lock selector or equivalent provable mapping. Unsupported note-specific lock requests must fail closed.

## 9. Regression preservation / 회귀 보존

On exact head `3e37e8eda72c6dadd3663915a4010e2899f8fff4`:

- Python 3.11 full suite — **SUCCESS**
- Python 3.12 full suite — **SUCCESS**
- prior M0→M5 evidence regeneration chain — **SUCCESS**
- M4-R3 Chromium E2E — **SUCCESS**
- M5-R2 Windows FluidSynth evidence — **SUCCESS**
- M5-R3 DAWproject evidence — **SUCCESS**
- M5-R4 paired Windows evidence — **SUCCESS**
- M6-R0 dedicated contract tests — included in both full suites and **SUCCESS**

## 10. Explicit non-claims / 명시적 비주장

M6-R0 does not validate or imply:

- working note-edit engine;
- accepted exact-note revision mutation;
- exact-note compiler lowering;
- usable piano-roll UI;
- real-browser note-edit E2E;
- stable note-specific lock runtime;
- arbitrary DAW note round-trip acceptance;
- quantize/humanize/batch transforms;
- tempo-map editing;
- waveform/audio editing;
- plugin/mixer/automation editing;
- human-subject usability evidence.

## 11. Exact next implementation / 정확한 다음 구현

After this evidence-bearing head passes its final exact-head regression and PR #52 is merged, the next bounded milestone is:

> **M6-R1 — Typed Exact-Note Material + Edit Engine**

M6-R1 must implement the semantic/runtime invariants that JSON Schema alone cannot prove, including unique note IDs, project/section bounds, part resolution, stale source enforcement, exact candidate application, stable-ID lock handling, structured diff/provenance and faithful exact-note compilation.
