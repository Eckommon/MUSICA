# M6 Precision Editing Authority & Canonical Note Model v0 / M6 정밀 편집 권한 및 공식 Note Model v0

**Status / 상태:** `RATIFIED — M6-R0 CONTRACT; M6-R1 BOUNDED CORE RUNTIME VALIDATED; M6-R2 BOUNDED BROWSER INTEGRATION VALIDATED; M6-R3 BOUNDED REAL-BROWSER E2E VALIDATED`

**Governing Issue / 지배 Issue:** `#51`

**Runtime implementation / 런타임 구현:** `M6-R1 / Issue #54 / PR #55 / evidence/M6_R1_VALIDATION.md`

**Browser integration / Browser 통합:** `M6-R2 / Issue #57 / PR #58 / evidence/M6_R2_VALIDATION.md`

**Real-browser validation / 실제 Browser 검증:** `M6-R3 / Issue #60 / PR #61 / evidence/M6_R3_VALIDATION.md`

**Next bounded extension / 다음 제한 확장:** `M6-R4 — bounded interchange reconciliation for representable exact-note edits`

## 1. Purpose / 목적

M6 introduces exact note-level editing without weakening MUSICA's existing authority model.

The central rule is:

> **A user or external bounded interchange artifact may propose exact-note changes, but every accepted change must first become a source-bound Blueprint-representable candidate and pass trusted authority. Music IR, Browser state and DAW/interchange state remain non-canonical.**
>
> **사용자 또는 제한된 외부 interchange artifact는 exact-note 변경을 제안할 수 있지만, 승인되기 전 모든 변경은 source-bound Blueprint 표현 candidate가 되어 trusted authority를 통과해야 한다. Music IR, Browser 상태, DAW/interchange 상태는 비공식 상태로 남는다.**

A piano roll, renderer or DAW is therefore a view/editor/proposal carrier over Blueprint-authoritative material, never an independent project authority.

## 2. Why M6 exists / M6가 필요한 이유

Before M6, repository evidence had a deliberate authority gap:

- the conceptual Blueprint permitted explicit notes but had no validated exact-note machine contract;
- the legacy compiler lowered repeating `motif_notes` to Music IR;
- M5-R3 exported/imported bounded DAWproject note semantics but correctly blocked arbitrary external note reverse mapping;
- Browser Studio had no validated exact-note piano-roll authority path.

M6 closed that gap incrementally:

- **M6-R0** ratified exact-note authority/data contracts;
- **M6-R1** validated bounded exact-note trusted-core runtime and six typed operations;
- **M6-R2** validated Browser Studio note projection and Preview integration;
- **M6-R3** validated the six-operation exact-note journey in real Chromium, including visible fail-closed conflicts and restart/reopen persistence;
- **M6-R4** may now evaluate a new bounded DAWproject note-reconciliation path without changing M5-R3's historical evidence or granting DAW state authority.

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
```

Valid proposal paths:

```text
Browser/User exact-note input
        ↓
source-bound NoteEditCandidate
        ↓
M6 authority
        ↓
PREVIEW — NON-CANONICAL
        ↓ explicit Accept only
M2 commit
        ↓
new Accepted Blueprint revision
```

Future R4 bounded interchange path:

```text
MUSICA-origin source-bound DAWproject export
        ↓ optional external bounded modification
returned DAWproject
        ↓ safe parse + normalized baseline comparison
stable identity / representability reconciliation
        ↓
source-bound NoteEditCandidate
        ↓
existing M6 authority
        ↓
PREVIEW — NON-CANONICAL
        ↓ explicit Accept only
M2 commit
```

Forbidden paths:

```text
mutated Music IR → accepted Blueprint
DOM/canvas/browser-local array → accepted Blueprint
returned DAWproject state → accepted Blueprint
ambiguous external note mapping → guessed NoteEditCandidate
```

No renderer, DAW, browser, AI provider or note editor gains project mutation authority merely because it can display, serialize or modify executable events.

## 4. Canonical exact-note material / 공식 exact-note material

Normative machine contract:

- `schemas/exact-note-material-v0.schema.json`

The first canonical mode is:

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

Canonical timing uses quarter-note beat coordinates rather than seconds or Music-IR ticks.

Reasons:

1. ticks are a lowering detail (`PPQ=480` today), not creative authority;
2. seconds bind note identity to one tempo realization;
3. beat coordinates survive deterministic re-lowering and align with the bounded DAWproject beat representation;
4. a later tempo-map design can map musical position without rewriting stable note identity.

The currently validated runtime remains bounded to fixed-tempo exact-note contexts.

Each exact note carries at minimum:

- `note_id` — stable logical identity;
- `part_id` — Blueprint part ownership;
- `section_id` — bounded structural association where present;
- `start_beat`;
- `duration_beats`;
- `pitch` — integer `0..127` in v0;
- `velocity` — integer `1..127` in v0.

The contract is renderer-independent. MIDI-like pitch/velocity vocabulary is an interoperable representation, not authority granted to MIDI or Music IR.

## 5. Stable identity and ordering / 안정적 식별자와 정렬

Rules:

- edit operations target `note_id + part_id`, never array indices;
- `note_id` must be unique inside one accepted exact-note material revision;
- `INSERT` creates a new identity;
- `DELETE` retires an identity in the child revision;
- `MOVE / RESIZE / REPITCH / SET_VELOCITY` preserve identity;
- JSON array reorder is not itself a musical edit;
- canonical presentation order is `(start_beat, part_id, pitch, note_id)`.

M6-R1 enforces cross-field identity/order/ownership invariants in trusted runtime validation. M6-R2/R3 expose and exercise stable identity without transferring authority to browser ordering.

For M6-R4, DAWproject/XML order must likewise never become MUSICA note identity. Any interchange identity bridge must be deterministic, source-bound and fail closed when ambiguous.

## 6. Backward compatibility / 하위 호환

M6 does not invalidate existing Blueprint v0 projects.

Legacy material remains valid:

```json
"melody": {
  "main_motif_id": "motif-A",
  "motif_length_beats": 4.0,
  "motif_notes": [...]
}
```

M6 adds an optional Blueprint-facing exact timeline:

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

- projects without `exact_timeline` retain legacy compiler behavior;
- projects with `exact_timeline` are validated by schema plus trusted cross-field invariants;
- Browser Studio reports exact editing unavailable for legacy motif-only material;
- Music IR or DAWproject must never fabricate canonical exact notes for a legacy project;
- incompatible future exact-note semantics require an explicit version decision.

## 7. Material precedence / material 우선순위

```text
legacy motif material
→ existing generative/semantic lowering allowed

explicit exact-note material
→ faithful exact-note lowering
→ semantic changes affecting exact notes must first become an explicit Blueprint candidate/diff
```

For explicit exact-note material, accepted `pitch / start_beat / duration_beats / velocity` are creative decisions. The compiler must not silently alter them because another semantic control suggests different energy, density or motion.

## 8. NoteEditCandidate / Note Edit Candidate

Normative machine contract:

- `schemas/note-edit-candidate-v0.schema.json`

Every candidate is non-canonical and contains:

- stable `candidate_id`;
- `authority_target = blueprint_exact_note_material`;
- exact source `project_id`;
- exact source accepted `revision_id`;
- exact source canonical Blueprint SHA-256;
- actor/reason;
- one or more typed operations;
- `preview_only = true`.

Allowed v0 primitive vocabulary:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

Quantize, transpose ranges, humanize, legato and other batch semantics remain deferred unless later lowered into these primitives or separately contracted.

M6-R4, if implemented, must produce this same candidate contract. It may not create a second DAW-specific note mutation authority.

## 9. Source binding and stale protection / source binding과 stale 보호

Every NoteEditCandidate binds:

```text
project_id
+ accepted revision_id
+ canonical Blueprint SHA-256
```

M6-R1 fails closed when the candidate no longer matches the current accepted project source. M6-R2/R3 preserve and validate that behavior through Browser Studio.

For R4, interchange reconciliation must additionally bind the exact MUSICA export lineage, including the original export artifact and deterministic source/mapping evidence. A returned artifact from an older accepted revision must not be silently rebased.

## 10. Lock and constraint authority / Lock·Constraint 권한

Authority precedence remains:

```text
project integrity
> explicit HARD locks
> explicit hard constraints
> accepted project invariants
> user soft preferences
> AI inference
> optimization heuristics
> external/interchange values and adapter heuristics
```

### 10.1 Existing JSON-pointer locks

Existing Blueprint locks continue to protect their canonical targets under `validate_revision` semantics.

### 10.2 Stable note-specific locks

Normative additive contract:

- `schemas/exact-note-lock-v0.schema.json`

Stable note locks resolve by note identity/property, not array index. M6-R1 enforces them both in note-edit preflight and revision validation so direct M2 commit cannot bypass the protection.

M6-R3 proves a real-browser attempted pitch edit against locked `N-MOTIF-001` is visibly blocked as `HARD_LOCK_VIOLATION` with stable note/rule context and no pending Preview.

Any R4 interchange candidate is subject to exactly the same lock authority.

## 11. Authority result / 권한 판정 결과

Normative contract:

- `schemas/note-edit-authority-result-v0.schema.json`

Result states:

- `READY_FOR_PREVIEW`
- `BLOCKED`

Invariant:

```text
explicit_accept_required        = true
project_mutation_authorized     = false
music_ir_mutation_authorized    = false
```

`READY_FOR_PREVIEW` authorizes only a non-canonical Preview. `BLOCKED` prohibits Preview generation and requires explicit conflict evidence.

Bounded codes include:

- `STALE_SOURCE`
- `HARD_LOCK_VIOLATION`
- `CONSTRAINT_VIOLATION`
- `INVALID_NOTE`
- `UNKNOWN_NOTE`
- `PART_MISMATCH`
- `UNREPRESENTABLE_EDIT`

R4 may require an outer reconciliation-result vocabulary for mapping/provenance failures, but final representable note authority must still delegate to this M6 result.

## 12. Part and section ownership / Part·Section 소유권

Validated bounded exact editing requires:

- `part_id` exists in `roles.instruments_or_parts`;
- exact editing is restricted to currently supported motif/lead material;
- target operations do not silently move notes between parts;
- supplied section identity is valid;
- note timing remains within supported project/section bounds;
- fixed-tempo context remains supported.

R4 must not expand these constraints merely because DAWproject can represent broader note or track structures.

## 13. Diff and provenance / Diff·provenance

Every accepted exact-note edit remains explainable as:

1. original typed operation(s);
2. resulting stable-note/Blueprint diff;
3. exact source revision/hash;
4. actor/reason;
5. explicit M2 acceptance.

For R4, durable provenance must additionally bind original MUSICA export artifact, returned artifact, normalized baseline/returned representations and note identity mapping evidence.

## 14. Compiler impact / Compiler 영향

### Legacy path

Existing `motif_notes` generative lowering remains unchanged.

### Exact timeline path

M6-R1 implements deterministic lowering that:

- validates exact-note material;
- maps quarter-note beats to PPQ ticks deterministically;
- preserves exact pitch/start/duration/velocity under declared numeric policy;
- binds notes to supported part/track ownership;
- sorts deterministically;
- records lowering provenance;
- avoids silent semantic velocity scaling.

M6-R2/R3 add no separate compiler authority. Accepted Browser edits return to the same M2/Blueprint → trusted lowering path.

Music IR remains derived and non-canonical.

## 15. Interchange impact / 상호운용성 영향

M5-R3 historical evidence remains valid and unchanged.

M5-R3 proved a bounded DAWproject 1.0 export/import bridge and intentionally blocked arbitrary external note reverse mapping because no validated canonical exact-note reverse authority existed at that milestone.

M6-R4 may introduce a **new bounded reconciliation path** only when all of the following are proven:

```text
MUSICA-origin exact export lineage
+ exact accepted source binding
+ deterministic normalized baseline-versus-returned comparison
+ stable note identity / part mapping
+ representability as existing M6 primitive operations
+ normal M6 lock/constraint validation
```

R4 must not:

- retroactively alter M5-R3 evidence;
- infer note identity from array/XML order;
- accept arbitrary external DAWproject state;
- guess ambiguous mappings;
- silently discard unsupported changes and accept a partial candidate;
- treat an external DAW application as project authority.

## 16. Browser Studio impact / Browser Studio 영향

Validated path through M6-R3:

```text
accepted exact-note material
→ deterministic Studio note view
→ real Chromium Browser Studio Inspect piano roll
→ browser exact-note controls
→ typed NoteEditCandidate
→ M6-R1 authority
→ PREVIEW · NOT ACCEPTED or BLOCKED
→ explicit Accept / Discard
→ existing M2 authority only
→ restart/reopen persistence
```

M6-R3 validates:

- all six primitive operations through browser-accessible controls;
- exact project/revision/Blueprint source binding;
- accepted ref unchanged before Accept;
- Discard preservation;
- explicit single M2 promotion;
- restart/reopen persistence;
- visible HARD-lock and stale-source fail-closed UX;
- legacy no-fabrication;
- zero browser console/page errors in canonical evidence;
- browser and Music IR mutation authority remain false.

M6-R3 also exposed and closed a missing Browser Preview-detail read route. Existing session with no Preview now returns an explicit empty 200 read state; unknown session remains fail-closed 404.

## 17. Non-goals / 비목표

The currently validated M6 boundary does not claim:

- full professional DAW piano-roll parity;
- arbitrary polyphonic/every-part exact editing;
- arbitrary tempo-map editing;
- general quantize/humanize/batch transforms;
- waveform/destructive audio editing;
- arbitrary automation/mixer/device/plugin fidelity;
- VST/AU/CLAP hosting;
- live MIDI recording;
- score engraving;
- cloud collaboration;
- direct Music IR mutation authority;
- arbitrary DAW note round-trip acceptance;
- universal/real-DAW compatibility;
- human-subject usability or perceptual superiority.

## 18. Planned sequence / 예정 순서

```text
M6-R0 — Precision Editing Authority & Canonical Note Model       VALIDATED
M6-R1 — Typed Exact-Note Material + Edit Engine                  VALIDATED — BOUNDED CORE RUNTIME
M6-R2 — Browser Studio Piano-Roll / Inspect Surface              VALIDATED — BOUNDED BROWSER INTEGRATION
M6-R3 — Real-browser exact-note E2E + lock/conflict UX           VALIDATED — BOUNDED REAL-BROWSER E2E
M6-R4 — bounded interchange reconciliation for note edits        NEXT
```

## 19. Ratified claims / 비준 주장

M6-R0 contract claim:

> **MUSICA has an accepted authority and machine-readable data contract for representing exact note-level creative decisions and turning note edits into Blueprint-bound non-canonical candidates without promoting Music IR to canonical state.**

M6-R1 bounded runtime claim:

> **MUSICA can represent, validate, preview, accept, version and deterministically compile bounded exact note-level edits through stable identities while preserving Blueprint/M2 authority above Music IR.**

M6-R2 bounded Browser integration claim:

> **MUSICA can expose accepted exact-note material through a local Browser Studio piano-roll / Inspect surface, construct bounded stable-ID exact-note edits, preview them through trusted M6 authority, and accept them only through existing M2 project authority.**

M6-R3 bounded real-browser claim:

> **MUSICA can exercise all six bounded stable-ID exact-note primitives through a real Chromium Browser Studio, keep edits non-canonical until explicit Accept, visibly fail closed on HARD-lock/stale-source conflicts, and preserve accepted exact-note state across restart/reopen.**

M6-R4 is not yet a ratified implementation claim. Its proposed maximum claim is limited to source-bound representable note reconciliation from a MUSICA-origin bounded DAWproject artifact into existing typed M6 candidates. New executable evidence is required before that claim may be promoted.

**Repository evidence remains authoritative over conversational memory or model inference. / 레포 근거는 대화·모델 추론보다 우선합니다.**
