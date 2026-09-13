# M6 Precision Editing Authority & Canonical Note Model v0 / M6 정밀 편집 권한 및 공식 Note Model v0

**Status / 상태:** `RATIFIED — M6-R0→R4 VALIDATED WITHIN BOUNDED CLAIMS; FIRST PRECISION-EDITING TRANCHE COMPLETE`

**Governing design Issue:** `#51`

Durable validation chain:

- M6-R0 — `evidence/M6_R0_VALIDATION.md`
- M6-R1 — `evidence/M6_R1_VALIDATION.md`
- M6-R2 — `evidence/M6_R2_VALIDATION.md`
- M6-R3 — `evidence/M6_R3_VALIDATION.md`
- M6-R4 — `evidence/M6_R4_VALIDATION.md`

## 1. Governing rule / 지배 규칙

M6 introduced exact note-level editing without weakening MUSICA's canonical project authority:

> **Exact-note changes may be proposed by a user, browser, AI or bounded interchange carrier, but every accepted change must first become a source-bound Blueprint-representable typed candidate and pass trusted authority. Music IR, Browser state and DAW/interchange state remain non-canonical.**

```text
Accepted Blueprint exact-note material
→ trusted deterministic lowering
→ Music IR / renderer / interchange projections

note-edit proposal
→ typed NoteEditCandidate
→ exact source binding
→ stable note identity
→ HARD lock / constraint validation
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept only
→ existing M2 revision authority
```

Forbidden:

```text
mutated Music IR → accepted Blueprint
DOM/canvas state → accepted Blueprint
DAW/interchange artifact → accepted Blueprint
array index/order → stable note identity
blocked result → pending Preview
edit gesture/import → implicit Accept
```

## 2. Canonical exact-note material / 공식 exact-note material

Normative machine contract:

- `schemas/exact-note-material-v0.schema.json`

Canonical v0 exact-note timing uses quarter-note beat coordinates. Each note has stable logical identity and ownership, including:

- `note_id`;
- `part_id`;
- optional `section_id`;
- `start_beat`;
- `duration_beats`;
- `pitch`;
- `velocity`.

Accepted exact note properties are creative decisions. In the explicit timeline path the compiler must lower them faithfully rather than silently rescale them from semantic controls.

Legacy motif-only projects remain valid and are not reverse-mapped from Music IR into fabricated exact-note material.

## 3. Stable identity / 안정적 identity

Rules:

- operations address `part_id + note_id`, never array index;
- INSERT creates a new stable identity;
- DELETE retires identity in the child revision;
- MOVE/RESIZE/REPITCH/SET_VELOCITY preserve identity;
- JSON array reorder is not itself a musical edit;
- stable-ID locks are independent of array storage order.

## 4. Typed edit authority / typed 편집 권한

Normative contracts:

- `schemas/note-edit-candidate-v0.schema.json`
- `schemas/note-edit-authority-result-v0.schema.json`
- `schemas/exact-note-lock-v0.schema.json`

Bounded primitive vocabulary:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

Every candidate is non-canonical, binds exact source project/revision/Blueprint hash, and requires explicit acceptance.

Authority results remain:

```text
READY_FOR_PREVIEW
BLOCKED
```

with:

```text
explicit_accept_required = true
project_mutation_authorized = false
music_ir_mutation_authorized = false
```

## 5. Source and stale protection / 소스·stale 보호

Every exact-note candidate is bound to:

```text
project_id
revision_id
canonical Blueprint SHA-256
```

A stale edit is never silently rebased. The candidate must be reconstructed against current accepted state.

## 6. Lock and constraint authority / Lock·Constraint 권한

Authority precedence remains:

```text
project integrity
> HARD locks
> hard constraints
> accepted project invariants
> user soft preferences
> AI inference
> optimization heuristics
```

Stable note-specific locks use logical note identity rather than array-index JSON pointers. Direct M2 commit cannot bypass validated HARD note locks.

## 7. M6-R1 — trusted runtime / trusted runtime

M6-R1 validated:

- exact-note material validation;
- faithful deterministic lowering;
- typed primitive edit application;
- stable-ID lock/constraint checks;
- source binding and stale blocking;
- non-canonical Preview;
- explicit M2 acceptance;
- versioned accepted exact-note revisions.

## 8. M6-R2 — Browser Studio integration / Browser Studio 통합

M6-R2 validated:

- deterministic `studio-note-view-v0` projection;
- Browser Inspect piano roll;
- stable note/lock visibility;
- browser-accessible six primitive controls;
- `POST /v0/sessions/{id}/preview/notes` delegated to trusted M6 authority;
- blocked stale/HARD-lock cases install no Preview;
- Browser and Music IR mutation authority remain false.

## 9. M6-R3 — real-browser E2E / 실제 Browser E2E

M6-R3 validated in real Chromium:

- all six primitive operations through Browser controls;
- accepted ref unchanged before Accept;
- explicit Accept and Discard;
- restart/reopen persistence;
- visible `HARD_LOCK_VIOLATION` and `STALE_SOURCE` conflict UX;
- no fabricated notes for legacy projects;
- zero canonical browser console/page errors after fixing the missing Preview-detail read endpoint.

The Browser remains a proposal/view surface, not project authority.

## 10. M6-R4 — bounded interchange reconciliation / 제한 interchange reconciliation

M6-R4 validated one narrowly bounded return path from a **MUSICA-origin** DAWproject export:

```text
accepted exact-note Blueprint
→ deterministic MUSICA DAWproject export
→ source-bound identity map + exact normalized baseline
→ returned DAWproject
→ safe M5-R3 parse/normalize
→ compare against exact baseline
→ one uniquely provable primitive note delta
→ normal NoteEditCandidate
→ existing M6 authority
→ Preview / explicit M2 Accept
```

Validated R4 constraints:

- DAW Note has no MUSICA stable-ID authority;
- no DAW array order/index identity;
- no nearest-note heuristic;
- duplicate normalized signatures fail closed;
- only one uniquely provable primitive per v0 reconciliation;
- multi-note, multi-field, transport-mixed, stale and ambiguous cases fail closed;
- HARD stable-note lock remains final authority;
- external state remains non-canonical;
- evidence generation itself is byte-reproducible.

M5-R3 historical `UNSUPPORTED_BLOCKING` evidence remains correct for its milestone context and was not rewritten.

## 11. M6 final bounded claim / M6 최종 제한 주장

M6 supports this bounded claim:

> **MUSICA can represent exact-note creative decisions canonically in Blueprint state; validate, preview, edit and version them through stable identities; expose them through a real Browser Studio piano roll; and reconcile one uniquely provable representable note change from an exact MUSICA-origin bounded DAWproject export back into the same trusted candidate authority without promoting Music IR, browser state or external DAW state to canonical truth.**

## 12. Explicit non-claims / 명시적 비주장

M6 does not validate:

- full professional DAW parity;
- arbitrary DAW reverse mapping;
- non-MUSICA-origin interchange reconciliation;
- heuristic note correspondence;
- batch/multi-note interchange reconciliation;
- arbitrary polyphonic/every-part editing;
- arbitrary tempo-map editing;
- quantize/humanize systems;
- automation/mixer/plugin/device canonical editing;
- live MIDI recording;
- waveform/destructive audio editing;
- human-subject usability or perceptual superiority.

## 13. Next authority frontier / 다음 권한 경계

M6 is closed as the first exact-note precision tranche. The next proposed contract/design frontier is:

> **M7-R0 — Canonical Automation & Continuous-Control Authority**

M7 must not reuse derived Music IR control events, DAW automation or renderer/plugin parameter state as canonical creative truth by implication. As with M6-R0, authority/data/lock/source-binding rules must be ratified before runtime/UI work begins.

**Repository evidence remains authoritative over conversation/model memory.**
