# M6 Precision Editing Authority & Canonical Note Model v0 / M6 정밀 편집 권한 및 공식 Note Model v0

**Status / 상태:** `RATIFIED — M6-R0 CONTRACT; M6-R1 BOUNDED CORE RUNTIME VALIDATED; M6-R2 BOUNDED BROWSER INTEGRATION VALIDATED`

**Governing Issue / 지배 Issue:** `#51`

**Runtime implementation / 런타임 구현:** `M6-R1 / Issue #54 / PR #55 / evidence/M6_R1_VALIDATION.md`

**Browser integration / Browser 통합:** `M6-R2 / Issue #57 / PR #58 / evidence/M6_R2_VALIDATION.md`

## 1. Purpose / 목적

M6 introduces exact note-level editing without weakening MUSICA's existing authority model.

M6는 MUSICA의 기존 권한 모델을 약화시키지 않고 exact note-level 편집을 도입합니다.

The central rule is:

> **A user may edit exact notes, but the edit must become a Blueprint-representable candidate before it can become accepted project state. Music IR remains derived execution state.**
>
> **사용자는 exact note를 편집할 수 있지만, 승인 프로젝트 상태가 되기 전에 반드시 Blueprint로 표현 가능한 candidate가 되어야 한다. Music IR은 파생 실행 상태로 남는다.**

A piano roll is therefore a view/editor over Blueprint-authoritative note material, never an editor that promotes mutated Music IR into canonical state.

## 2. Why M6 exists / M6가 필요한 이유

Repository evidence before M6 had a deliberate gap:

- the conceptual Blueprint permits explicit notes when needed;
- `music-blueprint-v0.schema.json` leaves `materials.melody` structurally open;
- the legacy compiler lowers a repeating `motif_notes` pattern to Music IR;
- M5-R3 exports note events but correctly refuses arbitrary note edits when no Blueprint reverse mapping exists;
- Browser Studio originally exposed Inspect without a validated piano-roll exact-note path.

M6-R0 closed the authority/data-contract gap, M6-R1 validated the bounded trusted-core runtime, and M6-R2 validated the bounded Browser Studio service/UI integration over that runtime. Full real-browser exact-note end-to-end interaction and conflict UX remain an M6-R3 concern.

## 3. Authority model / 권한 모델

```text
Accepted Blueprint revision
        │
        ├─ legacy motif material
        └─ exact-note material (when present)
                │
                ↓ trusted lowering
             Music IR
                ↓
       renderer / interchange

User note edit
        ↓
NoteEditCandidate — NON-CANONICAL
        ↓ source/revision/hash preflight
        ↓ stable note-id resolution
        ↓ HARD lock / constraint checks
        ↓ exact Blueprint delta
      PREVIEW — NON-CANONICAL
        ↓ explicit Accept only
      M2 commit
        ↓
new Accepted Blueprint revision
        ↓ trusted lowering
new Music IR
```

Forbidden path:

```text
mutated Music IR
→ accepted Blueprint or project revision
```

No renderer, DAW, browser, AI provider or note editor gains project mutation authority merely because it can display or modify executable events.

## 4. Canonical exact-note material / 공식 exact-note material

Normative machine contract:

- `schemas/exact-note-material-v0.schema.json`

The first canonical exact-note material mode is:

```json
{
  "material_version": "0",
  "mode": "explicit_timeline",
  "time_base": {
    "unit": "quarter_note_beat",
    "origin_beat": 0.0
  },
  "notes": []
}
```

### 4.1 Why quarter-note beats / quarter-note beat를 사용하는 이유

Canonical exact-note timing uses **quarter-note beat coordinates**, not seconds and not Music-IR ticks.

Reasons:

1. ticks are an implementation/lowering detail (`PPQ=480` today) and must not become creative authority;
2. seconds couple note identity to one tempo realization;
3. beat coordinates survive deterministic re-lowering and align with DAWproject's bounded beat representation;
4. future tempo-map support can map musical position to seconds without rewriting accepted note identity.

The validated M6-R1/M6-R2 runtime and Browser integration remain bounded to the currently supported fixed-tempo context. Adaptive/multi-event tempo-map editing remains outside the validated boundary.

### 4.2 Exact note fields / exact note 필드

Each exact note carries at minimum:

- `note_id` — stable logical identity;
- `part_id` — Blueprint part ownership;
- `section_id` — optional structural association;
- `start_beat` — absolute musical start position;
- `duration_beats` — musical duration;
- `pitch` — bounded MIDI-note integer `0..127` for v0;
- `velocity` — bounded integer `1..127` for v0.

Optional v0 attributes are deliberately small: bounded articulation and identity tags.

The note contract is renderer-independent. A MIDI-like integer pitch/velocity vocabulary is used as a compact interoperable musical representation, not as authority granted to MIDI or Music IR.

## 5. Stable identity and ordering / 안정적 식별자와 정렬

`note_id` is the addressable identity of one exact-note object across a revision lineage.

Rules:

- edit operations target `note_id` + `part_id`, never array indices;
- `note_id` values must be unique inside the exact-note material of one accepted revision;
- an INSERT creates a new identity;
- DELETE retires that identity in the child revision;
- MOVE, RESIZE, REPITCH and SET_VELOCITY preserve the same identity;
- reorder of JSON array storage is not itself a musical edit;
- canonical presentation order is `(start_beat, part_id, pitch, note_id)`.

M6-R1 enforces the cross-field uniqueness/order and ownership invariants in trusted runtime validation; JSON Schema alone is not treated as sufficient evidence for those invariants. M6-R2 exposes the resulting stable identity through the Browser Studio note-view contract without transferring authority to browser array order.

## 6. Backward compatibility / 하위 호환

M6 does **not** invalidate existing Blueprint v0 projects.

Existing material remains valid:

```json
"melody": {
  "main_motif_id": "motif-A",
  "motif_length_beats": 4.0,
  "motif_notes": [...]
}
```

M6 adds an explicit timeline as an additive Blueprint-facing sub-contract:

```json
"melody": {
  "main_motif_id": "motif-A",
  "motif_length_beats": 4.0,
  "motif_notes": [...],
  "exact_timeline": {
    "material_version": "0",
    "mode": "explicit_timeline",
    "time_base": {"unit": "quarter_note_beat", "origin_beat": 0.0},
    "notes": [...]
  }
}
```

Because Blueprint v0 already permits structured material extension under `materials.melody`, M6 does not silently change `blueprint_version`.

- existing projects without `exact_timeline` retain legacy compiler behavior;
- when `exact_timeline` exists, M6-R1 validates it against `exact-note-material-v0.schema.json` plus trusted cross-field invariants;
- M6-R2 reports exact-note editing unavailable for legacy motif-only Browser Studio projects and does not fabricate canonical notes from Music IR;
- any future change that makes exact-note material mandatory or changes incompatible semantics requires an explicit Blueprint schema/version decision.

## 7. Material mode and precedence / material mode와 우선순위

The legacy compiler repeats `motif_notes` and applies bounded semantic energy scaling to motif velocity. That behavior remains valid for the **legacy motif path**.

For the **explicit timeline path**:

> Exact note `pitch`, `start_beat`, `duration_beats` and `velocity` are accepted creative decisions and MUST lower faithfully. The compiler must not silently alter them because a semantic control suggests different energy, density or motion.

Therefore:

```text
legacy motif material
→ existing generative/semantic lowering allowed

explicit exact-note material
→ faithful exact-note lowering
→ semantic change affecting those notes must first become a new explicit Blueprint candidate/diff
```

M6-R1 implements and validates this bounded precedence rule. M6-R2 reuses it unchanged through the Studio note Preview boundary.

## 8. Note edit candidate / Note Edit Candidate

Normative machine contract:

- `schemas/note-edit-candidate-v0.schema.json`

A candidate is always non-canonical and contains:

- stable `candidate_id`;
- `authority_target = blueprint_exact_note_material`;
- source `project_id`;
- source accepted `revision_id`;
- source canonical Blueprint SHA-256;
- actor and reason;
- one or more typed operations;
- `preview_only = true`.

Allowed v0 operation vocabulary:

- `INSERT`
- `DELETE`
- `MOVE`
- `RESIZE`
- `REPITCH`
- `SET_VELOCITY`

Quantize, transpose ranges, humanize, legato transforms and other batch operations remain deferred unless later lowered into these primitives or separately contracted after evidence.

## 9. Source binding and stale protection / source binding과 stale 보호

Every candidate is bound to an exact accepted source:

```text
project_id
+ revision_id
+ canonical Blueprint SHA-256
```

M6-R1 fails closed when any source binding no longer matches the active accepted project state. M6-R2 preserves that exact binding through the Browser Studio note-view and Preview service boundary.

A stale edit is not rebased silently. A fresh candidate must be produced against the new accepted revision.

## 10. Lock and constraint authority / Lock·Constraint 권한

Existing precedence remains:

```text
project integrity
> explicit HARD locks
> explicit hard constraints
> accepted project invariants
> user soft preferences
> AI inference
> optimization heuristics
```

A note editor does not bypass top-level Blueprint locks simply because it operates visually.

### 10.1 Existing JSON-pointer locks

Existing Blueprint locks continue to use JSON Pointer targets. Any inherited HARD lock whose protected target changes remains blocking under `validate_revision` semantics.

### 10.2 Stable note-specific locks

Array-index pointers are not accepted as the identity mechanism for note-specific locks because note array order is not musical identity.

M6-R1 implements the additive stable-ID-aware note-lock contract:

- `schemas/exact-note-lock-v0.schema.json`

The trusted runtime resolves note locks by stable note identity/property and also enforces them inside `validate_revision()` so direct M2 commit cannot bypass the note-edit preflight.

M6-R2 exposes stable-ID lock state to the Browser Studio view and proves `HARD_LOCK_VIOLATION` remains fail-closed with no pending Preview. Rich real-browser conflict presentation is deferred to M6-R3.

Unsupported future lock semantics must continue to fail closed rather than degrade into advisory behavior.

## 11. Authority result / 권한 판정 결과

Normative machine contract:

- `schemas/note-edit-authority-result-v0.schema.json`

Result states:

- `READY_FOR_PREVIEW`
- `BLOCKED`

A valid result always enforces:

```text
explicit_accept_required        = true
project_mutation_authorized     = false
music_ir_mutation_authorized    = false
```

`READY_FOR_PREVIEW` means only that the candidate may be materialized as a non-canonical Preview. It does not mean the edit is accepted.

`BLOCKED` requires at least one explicit conflict and prohibits preview generation under the v0 authority result.

Bounded conflict codes:

- `STALE_SOURCE`
- `HARD_LOCK_VIOLATION`
- `CONSTRAINT_VIOLATION`
- `INVALID_NOTE`
- `UNKNOWN_NOTE`
- `PART_MISMATCH`
- `UNREPRESENTABLE_EDIT`

M6-R2 preserves these results through the Studio service and validates that stale/HARD-lock blocked results install no pending Preview.

## 12. Part and section ownership / Part·Section 소유권

`part_id` is mandatory for every exact note and targeted edit.

The validated M6-R1 semantic boundary proves that:

- `part_id` exists in `roles.instruments_or_parts`;
- bounded exact editing is restricted to supported motif/lead material;
- target operations do not silently move a note to another part;
- supplied `section_id` references a known section;
- note timing remains inside project bounds;
- section/time consistency is checked under the accepted fixed-tempo context.

M6-R2 projects this bounded ownership into Browser Studio without expanding the supported exact-edit part/tempo scope.

Expanding exact editing to arbitrary parts or tempo maps requires new evidence.

## 13. Diff and provenance / Diff·provenance

Every accepted exact-note edit is explainable as:

1. the original `NoteEditCandidate` operations, and
2. the resulting structured/stable-note Blueprint diff.

Accepted revision provenance remains bound to the source revision, actor, reason and exact accepted Blueprint. M2 acceptance remains the only project-state commit boundary.

M6-R2 presents stable-note edit/diff context at the Browser Studio boundary without granting display state revision authority.

## 14. Compiler impact / Compiler 영향

### Legacy path

Current `motif_notes` repeating compiler behavior remains unchanged for existing fixtures.

### Exact timeline path

M6-R1 validates and implements a lowering path that:

- validates exact-note material;
- maps quarter-note beats to PPQ ticks deterministically;
- preserves pitch/start/duration/velocity within deterministic numeric conversion policy;
- binds notes to the supported exact-edited part/track;
- sorts output deterministically;
- records exact-note lowering provenance;
- avoids silent semantic velocity scaling.

M6-R2 does not introduce a separate compiler path; accepted Browser Studio edits return to the same M2/Blueprint authority and trusted lowering.

Music IR remains derived and non-canonical.

## 15. Interchange impact / 상호운용성 영향

M5-R3 historical evidence remains unchanged. Its arbitrary note-edit `UNSUPPORTED_BLOCKING` behavior was correct for the authority available at that time.

A later M6-R4 may allow a bounded DAWproject note edit to become a `NoteEditCandidate` only when mapping/source/lock constraints are provable. That capability requires new evidence and may not rewrite M5-R3 evidence retroactively.

## 16. Browser Studio impact / Browser Studio 영향

M6-R0 defined the exact-note authority contract and M6-R1 validated the trusted-core runtime. M6-R2 now validates the bounded Browser Studio integration:

```text
accepted exact-note material
→ deterministic Studio note-view projection
→ Browser Studio Inspect piano roll
→ bounded browser edit control
→ typed NoteEditCandidate
→ M6-R1 authority result
→ PREVIEW · NOT ACCEPTED or BLOCKED
→ explicit Accept / Discard
→ existing M2 authority only
```

M6-R2 validates:

- schema-validated browser-facing note view;
- stable note identity and lock visibility;
- six primitive operation controls;
- non-canonical Preview installation only after `READY_FOR_PREVIEW`;
- stale and HARD-lock cases blocked with no Preview;
- explicit existing M2 acceptance;
- accepted exact-note persistence after reopen;
- legacy motif-only `exact_note_editing_available=false` without fabricated notes;
- same-origin/local-first security boundaries;
- browser and Music IR mutation authority remain false.

The browser must never directly persist mutated Music IR or browser-local note arrays as project truth.

M6-R3 is responsible for proving this already validated integration through a real Chromium exact-note E2E journey and for validating visible lock/stale conflict UX. R3 must not create new canonical authority semantics.

## 17. Non-goals / 비목표

The currently validated M6 boundary does not claim:

- full professional DAW piano-roll parity;
- real-browser six-operation exact-note E2E acceptance evidence;
- real-browser pointer drag/move/resize behavior as a validated capability;
- validated real-browser HARD-lock/stale-source conflict UX;
- waveform/destructive audio editing;
- arbitrary automation lanes;
- mixer/device/plugin editing;
- VST/AU/CLAP hosting;
- live MIDI recording;
- score engraving;
- collaboration;
- arbitrary tempo-map editing;
- humanization/quantize algorithms;
- direct Music IR mutation authority;
- arbitrary DAW note round-trip acceptance;
- human-subject usability or perceptual superiority.

## 18. Planned sequence / 예정 순서

```text
M6-R0 — Precision Editing Authority & Canonical Note Model       VALIDATED
M6-R1 — Typed Exact-Note Material + Edit Engine                  VALIDATED — BOUNDED CORE RUNTIME
M6-R2 — Browser Studio Piano-Roll / Inspect Surface              VALIDATED — BOUNDED BROWSER INTEGRATION
M6-R3 — Real-browser exact-note E2E + lock/conflict UX           NEXT
M6-R4 — bounded interchange reconciliation for note edits         PLANNED
```

## 19. Ratified claims / 비준 주장

M6-R0 contract claim:

> **MUSICA has an accepted authority and machine-readable data contract for representing exact note-level creative decisions and turning user note edits into Blueprint-bound non-canonical candidates without promoting Music IR to canonical state.**

M6-R1 bounded runtime claim:

> **MUSICA can represent, validate, preview, accept, version and deterministically compile bounded exact note-level edits through stable identities while preserving Blueprint/M2 authority above Music IR.**

M6-R2 bounded Browser integration claim:

> **MUSICA can expose accepted exact-note material through a local Browser Studio piano-roll / Inspect surface, construct bounded stable-ID exact-note edits, preview them through the trusted M6-R1 authority path, and accept them only through existing M2 project authority.**

Real-browser exact-note E2E interaction and lock/conflict UX remain unvalidated until M6-R3 evidence.
