# M6-R1 Runtime / M6-R1 런타임

**Milestone / 마일스톤:** `M6-R1 — Typed Exact-Note Material + Edit Engine`

**Governing Issue / 지배 Issue:** `#54`

**Implementation PR / 구현 PR:** `#55`

M6-R0 is ratified as a contract/design milestone. M6-R1 implements that authority model in the trusted MUSICA core. This document describes only the implemented R1 backend boundary; Browser Studio piano-roll work remains M6-R2.

M6-R0는 계약·설계 마일스톤으로 비준되었습니다. M6-R1은 해당 권한 모델을 MUSICA trusted core에 구현합니다. 본 문서는 R1 backend 경계만 설명하며 Browser Studio piano-roll은 M6-R2 범위입니다.

## 1. Canonical authority / 공식 권한

```text
Accepted Blueprint
→ trusted compiler
→ Music IR

NoteEditCandidate
→ exact source binding
→ stable-ID edit operations
→ Blueprint candidate
→ stable-ID HARD note locks
→ existing Blueprint locks/constraints
→ READY_FOR_PREVIEW — non-canonical
→ explicit Accept only
→ existing M2 commit_revision
→ new accepted Blueprint
→ trusted compiler
→ new Music IR
```

Music IR remains derived and cannot be selected as an edit authority target.

## 2. Exact-note material / exact-note material

The optional canonical material lives at:

```text
/materials/melody/exact_timeline
```

and is validated against:

```text
schemas/exact-note-material-v0.schema.json
```

R1 additionally enforces cross-field invariants that JSON Schema alone does not safely express:

- unique stable `note_id`;
- canonical storage order `(start_beat, part_id, pitch, note_id)`;
- known `part_id`;
- known optional `section_id`;
- fixed-tempo bounded runtime;
- note end not beyond project duration;
- section-bound notes remain inside their declared section;
- current R1 implementation is deliberately bounded to the canonical motif/lead part.

Existing Blueprint projects without `exact_timeline` retain the legacy `motif_notes` compiler path.

## 3. Faithful lowering / 충실한 lowering

When `exact_timeline` exists, the compiler selects it as the note source for the motif/lead track.

For every accepted exact note:

```text
start_beat     → round(start_beat × PPQ)
duration_beats → round(duration_beats × PPQ)
pitch          → exact integer pitch
velocity       → exact integer velocity
```

`PPQ=480` remains a derived compiler detail, not creative authority.

Semantic energy/density/motion may continue to affect other bounded derived mechanisms and control events, but must not silently rescale exact-note pitch/start/duration/velocity.

## 4. Stable-ID edit engine / Stable-ID 편집 엔진

Public core module:

```text
src/musica/note_edit.py
```

Primary resolution boundary:

```python
build_note_edit_preview(parent_blueprint, candidate, revision_id=None)
```

Supported primitive operations:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

Existing-note targets use:

```text
part_id + note_id
```

Array indices are never edit identity.

The returned `NoteEditPreview` contains:

- authority result;
- candidate Blueprint only when READY;
- stable-ID-oriented note diff;
- source/candidate Blueprint SHA-256;
- changed stable note IDs;
- revision conflicts.

A blocked result contains no Blueprint candidate.

## 5. Exact source binding / 정확한 source binding

Every candidate is bound to all three values:

```text
project_id
revision_id
canonical Blueprint SHA-256
```

Any mismatch produces:

```text
BLOCKED / STALE_SOURCE
preview_generation_allowed = false
```

There is no silent rebase.

## 6. Stable-ID HARD note lock / Stable-ID HARD note lock

R1 adds:

```text
schemas/exact-note-lock-v0.schema.json
```

Locks are stored additively under:

```text
/materials/melody/exact_note_locks
```

A lock selector is:

```json
{
  "part_id": "P-SYNTH",
  "note_id": "N-MOTIF-001",
  "property": "pitch"
}
```

Supported protected properties are:

```text
pitch
start_beat
duration_beats
velocity
```

The lock is enforced twice:

1. during Preview resolution for a structured `HARD_LOCK_VIOLATION` result;
2. inside `validate_revision()` so direct use of `MusicaProject.commit_revision()` cannot bypass the lock.

Existing top-level JSON-pointer locks continue unchanged. M6 stable-ID note locks are additive; they do not reinterpret existing lock semantics.

## 7. Preview and Accept / Preview와 Accept

Preview resolution is side-effect free with respect to project refs.

```text
head = rev-A
build_note_edit_preview(...)
head = rev-A
```

Acceptance is explicit:

```python
accept_note_edit_preview(project, preview)
```

This helper delegates to the existing M2 `commit_revision()` boundary. It does not create a second persistence/version-control system.

Blocked previews cannot be accepted.

## 8. Deterministic audit surface / 결정론 감사 표면

`stable_note_diff()` compares notes by stable `(part_id, note_id)` identity and emits deterministic insert/delete/update records independent of storage indices.

The candidate Blueprint provenance records:

- source revision;
- candidate ID;
- operation IDs;
- actor;
- change reason.

The accepted M2 revision still stores the normal canonical Blueprint diff and immutable revision/audit records.

## 9. Canonical evidence runner / 공식 근거 runner

```bash
python -m musica.m6_r1_demo --out artifacts/m6-r1-exact-note-edit
```

The runner proves in one bounded flow:

- legacy motif path remains deterministic;
- exact source notes lower faithfully;
- all six edit operation kinds are exercised;
- Preview is deterministic and non-authoritative;
- project ref does not advance before Accept;
- explicit Accept creates one child revision;
- project integrity passes;
- candidate and accepted compile deterministically;
- stale source is blocked;
- stable-ID HARD note lock violation is blocked;
- exact source/candidate/accepted hashes are recorded.

Dedicated workflow:

```text
.github/workflows/m6-r1-evidence.yml
```

## 10. Claim boundary / 주장 경계

Successful M6-R1 evidence may support:

> **MUSICA can represent, validate, preview, accept, version and deterministically compile bounded exact note-level edits through stable identities while preserving Blueprint/M2 authority above Music IR.**

M6-R1 does **not** validate:

- browser piano-roll usability;
- real-browser note dragging/resizing UX;
- arbitrary polyphonic/instrument-part editing beyond the bounded motif/lead implementation;
- arbitrary tempo-map editing;
- arbitrary DAW reverse mapping;
- live MIDI recording;
- mixer/automation/plugin editing;
- human-subject usability or perceptual quality.

Those require later evidence.
