# M6 Precision Editing Authority & Canonical Note Model v0 / M6 정밀 편집 권한 및 공식 Note Model v0

**Status / 상태:** `PROPOSED — M6-R0 CONTRACT`

**Governing Issue / 지배 Issue:** `#51`

## 1. Purpose / 목적

M6 introduces exact note-level editing without weakening MUSICA's existing authority model.

M6는 MUSICA의 기존 권한 모델을 약화시키지 않고 exact note-level 편집을 도입합니다.

The central rule is:

> **A user may edit exact notes, but the edit must become a Blueprint-representable candidate before it can become accepted project state. Music IR remains derived execution state.**
>
> **사용자는 exact note를 편집할 수 있지만, 승인 프로젝트 상태가 되기 전에 반드시 Blueprint로 표현 가능한 candidate가 되어야 한다. Music IR은 파생 실행 상태로 남는다.**

A piano roll is therefore a view/editor over Blueprint-authoritative note material, never an editor that promotes mutated Music IR into canonical state.

## 2. Why M6 exists / M6가 필요한 이유

Repository evidence before M6 has a deliberate gap:

- the conceptual Blueprint permits explicit notes when needed;
- `music-blueprint-v0.schema.json` leaves `materials.melody` structurally open;
- the current compiler lowers a repeating `motif_notes` pattern to Music IR;
- M5-R3 exports note events but correctly refuses arbitrary note edits when no Blueprint reverse mapping exists;
- Browser Studio exposes Inspect but does not yet validate professional exact-note editing.

M6 closes this gap by adding a typed exact-note authority layer above Music IR.

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

For M6-R1 the bounded runtime may continue to require the currently supported fixed-tempo context. Adaptive/multi-event tempo-map editing is outside R0.

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

Cross-field uniqueness/order are semantic invariants and will be enforced by the M6-R1 runtime validator; JSON Schema alone is not treated as sufficient evidence for those invariants.

## 6. Backward compatibility / 하위 호환

M6-R0 does **not** invalidate existing Blueprint v0 projects.

Existing material remains valid:

```json
"melody": {
  "main_motif_id": "motif-A",
  "motif_length_beats": 4.0,
  "motif_notes": [...]
}
```

M6 adds an explicit timeline as an additive Blueprint-facing sub-contract, conceptually:

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

Because Blueprint v0 already permits structured material extension under `materials.melody`, M6-R0 does not silently change `blueprint_version`. Instead:

- existing projects without `exact_timeline` retain legacy compiler behavior;
- when `exact_timeline` exists, M6-R1 must validate it against `exact-note-material-v0.schema.json` in addition to the Blueprint schema;
- any future change that makes exact-note material mandatory or changes incompatible semantics requires an explicit Blueprint schema/version decision.

This is an additive compatibility policy, not an excuse to leave the new field unvalidated at runtime.

## 7. Material mode and precedence / material mode와 우선순위

The current compiler repeats `motif_notes` and applies bounded semantic energy scaling to motif velocity. That behavior remains valid for the **legacy motif path**.

For the future **explicit timeline path**, the authority rule changes:

> Exact note `pitch`, `start_beat`, `duration_beats` and `velocity` are accepted creative decisions and MUST lower faithfully. The compiler must not silently alter them because a semantic control suggests different energy, density or motion.

Therefore:

```text
legacy motif material
→ existing generative/semantic lowering allowed

explicit exact-note material
→ faithful exact-note lowering
→ semantic change affecting those notes must first become a new explicit Blueprint candidate/diff
```

This preserves the product promise: what the user precisely edited is what the trusted compiler executes.

If both legacy motif material and `exact_timeline` are present, M6-R1 must use an explicit material-selection policy; it may not merge both implicitly. R0 default is that `exact_timeline` becomes the authoritative source for the exact-edited part once explicitly activated by a validated revision.

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

Allowed R0 operation vocabulary:

- `INSERT`
- `DELETE`
- `MOVE`
- `RESIZE`
- `REPITCH`
- `SET_VELOCITY`

This set is intentionally small. Quantize, transpose ranges, humanize, legato transforms and other batch operations should later compile into these primitive deltas or receive their own bounded contract after evidence.

## 9. Source binding and stale protection / source binding과 stale 보호

Every candidate is bound to an exact accepted source:

```text
project_id
+ revision_id
+ canonical Blueprint SHA-256
```

M6-R1 must fail closed when any source binding no longer matches the active accepted project ref.

A stale edit is not rebased silently. The user/editor may request a fresh candidate against the new revision, but that is a new authority decision with a new diff.

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

Existing Blueprint locks use JSON Pointer targets. Any inherited HARD lock whose protected target is directly changed by an exact-note candidate remains blocking under the current `validate_revision` semantics.

### 10.2 Stable note-specific locks

Array-index pointers are not acceptable as the long-term identity mechanism for note-specific locks because note array order is not musical identity.

Therefore R0 records the following implementation requirement:

> M6-R1 must introduce or bind a stable-ID-aware note-lock selector before claiming note-specific HARD-lock support. It must not fake stable locking with mutable array indices.

Until that selector is implemented, a UI may expose only lock scopes that the runtime can prove safely (for example an existing ancestor/melody identity lock or a bounded whole-material lock). Unsupported note-specific lock requests must fail closed, not degrade into advisory behavior.

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

## 12. Part and section ownership / Part·Section 소유권

`part_id` is mandatory for every exact note and targeted edit.

M6-R1 semantic validation must prove that:

- `part_id` exists in `roles.instruments_or_parts`;
- the part is eligible for the bounded exact-editing implementation;
- target operations do not silently move a note to another part;
- if `section_id` is supplied it references a known section;
- note timing remains inside project bounds;
- any required section-time consistency is checked using the accepted fixed-tempo context.

R0 schema supports any part ID structurally. M6-R1 may deliberately validate only motif/lead parts first, but such narrowing must be explicit evidence, not an undocumented assumption.

## 13. Diff and provenance / Diff·provenance

Every accepted exact-note edit must be explainable as both:

1. the original `NoteEditCandidate` operations, and
2. the resulting structured Blueprint diff.

Accepted revision provenance must record at minimum:

- source revision;
- candidate ID;
- actor;
- user-visible reason;
- accepted operation IDs;
- conflicts resolved or alternatives selected if applicable.

M2 acceptance remains the only project-state commit boundary.

## 14. Compiler impact / Compiler 영향

M6-R1 compiler work must be additive and bounded:

### Legacy path

Current `motif_notes` repeating compiler behavior remains unchanged for existing fixtures.

### Exact timeline path

A new lowering path must:

- validate exact-note material;
- map quarter-note beats to PPQ ticks deterministically;
- preserve pitch/start/duration/velocity exactly within deterministic numeric conversion policy;
- bind each note to the correct part/track;
- sort output deterministically;
- record compiler provenance indicating exact-note lowering;
- avoid silent semantic velocity scaling.

The R0 contract does not implement that compiler path yet.

## 15. Interchange impact / 상호운용성 영향

M5-R3 historical evidence remains unchanged. Its arbitrary note-edit `UNSUPPORTED_BLOCKING` behavior was correct for the authority available at that time.

After M6-R1+ validates canonical exact-note material and edit candidates, a later M6-R4 may allow a bounded DAWproject note edit to become a `NoteEditCandidate` when all mapping/source/lock constraints are provable.

This future capability must be new evidence; it may not rewrite M5-R3 evidence retroactively.

## 16. Browser Studio impact / Browser Studio 영향

M6-R0 does not build the piano roll.

A future M6-R2 Inspect surface should operate as:

```text
accepted exact-note material
→ visual piano-roll projection
→ typed NoteEditCandidate
→ authority result
→ Preview
→ audible/diff inspection
→ explicit Accept / Discard
```

The browser must never directly persist mutated Music IR events as project truth.

## 17. Non-goals / 비목표

R0 does not claim or implement:

- a professional piano-roll UI;
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
- arbitrary DAW note round-trip acceptance.

## 18. Planned sequence / 예정 순서

Subject to R0 ratification:

```text
M6-R1 — Typed Exact-Note Material + Edit Engine
M6-R2 — Browser Studio Piano-Roll / Inspect Surface
M6-R3 — Real-browser exact-note E2E + lock/conflict UX
M6-R4 — bounded interchange reconciliation for representable note edits
```

## 19. R0 completion claim / R0 완료 주장

Successful M6-R0 may claim only:

> **MUSICA has an accepted authority and machine-readable data contract for representing exact note-level creative decisions and turning user note edits into Blueprint-bound non-canonical candidates without promoting Music IR to canonical state.**

It may not yet claim that exact-note editing is implemented end-to-end or that a piano-roll editor is usable.
