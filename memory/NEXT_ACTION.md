# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M6-R1 — TYPED EXACT-NOTE MATERIAL + EDIT ENGINE / M6-R1 — Typed Exact-Note Material + Edit Engine**

M6-R0 is `VALIDATED — CONTRACT/DESIGN ONLY`. The next task is to implement the accepted exact-note authority path in the MUSICA core. Do not build the piano roll first and do not mutate Music IR directly.

M6-R0는 `VALIDATED — CONTRACT/DESIGN ONLY`입니다. 다음 작업은 승인된 exact-note 권한 경로를 MUSICA core에 실제 구현하는 것입니다. Piano-roll UI를 먼저 만들거나 Music IR을 직접 수정하지 않습니다.

## Canonical starting point / 공식 시작점

- M6-R0 implementation/design merge: `9a7beb133c4094d16a58466e97baec831ea98a01`
- Issue #51: **COMPLETED**
- PR #52: **MERGED**
- final validated M6-R0 exact head: `7bd51827913bd9dec62b8f452ac37f508bd54dfe`
- final MUSICA CI: `34688992955` — **SUCCESS**
- final M5-R3 regression: `34688993005` — **SUCCESS**
- final M5-R4 regression: `34688992941` — **SUCCESS**
- durable evidence: `evidence/M6_R0_VALIDATION.md`

## Governing contracts / 지배 계약

Read and obey:

1. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
2. `docs/M6_ACCEPTANCE.md`
3. `schemas/exact-note-material-v0.schema.json`
4. `schemas/note-edit-candidate-v0.schema.json`
5. `schemas/note-edit-authority-result-v0.schema.json`
6. `src/musica/contracts.py`
7. `src/musica/compiler.py`
8. `src/musica/project.py`
9. `src/musica/diff.py`

## Core invariant / 핵심 불변식

```text
Accepted Blueprint revision
→ trusted lowering
→ Music IR

NoteEditCandidate
→ validate exact source revision + Blueprint SHA-256
→ validate exact-note material
→ apply stable-ID operations to Blueprint candidate
→ HARD lock / constraint evaluation
→ authority result
→ PREVIEW — non-canonical
→ explicit Accept only
→ new M2 revision
→ trusted lowering
→ new Music IR
```

Forbidden:

```text
Music IR direct mutation → accepted project state
```

## Required M6-R1 implementation / 필수 구현

### 1. Exact-note Blueprint integration

Add executable validation/invariants for optional `materials.melody.explicit_timeline` while preserving existing `motif_notes` projects unchanged.

Required invariants:

- `note_id` unique within the exact-note material;
- every note `part_id` resolves to a Blueprint part;
- every optional `section_id` resolves to a Blueprint section;
- `start_beat >= 0` and `duration_beats > 0`;
- pitch/velocity remain schema bounded;
- deterministic ordering is defined independently of input array order;
- legacy motif-only fixtures remain valid.

### 2. Exact deterministic lowering

Extend compiler behavior so `explicit_timeline` notes lower exactly to Music IR note events.

Rules:

- beat → tick uses the existing canonical PPQ policy;
- pitch/start/duration/velocity lower faithfully;
- semantic energy/density/motion logic must not silently rescale explicit exact-note event properties;
- derived Music IR remains non-canonical;
- deterministic compile must produce byte/logically identical IR for identical Blueprint state.

### 3. Note edit engine

Recommended module:

```text
src/musica/note_edit.py
```

Implement the R0 vocabulary:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

Operations must use stable `note_id + part_id`, never array indices.

Recommended public boundary:

```text
build_note_edit_preview(parent_blueprint, candidate) -> NoteEditPreview
```

The preview result should expose:

- validated authority result;
- candidate Blueprint;
- exact structured diff;
- source/candidate hashes;
- changed stable note IDs;
- compile preview metadata where useful;
- no project-ref mutation.

### 4. Source binding / stale protection

Before applying operations verify all candidate source bindings against the supplied accepted parent:

- `project_id` exact match;
- `source_revision_id` exact match;
- `source_blueprint_sha256` exact canonical hash.

Any mismatch → `BLOCKED / STALE_SOURCE` and no preview candidate.

### 5. Stable-ID note lock selector

Implement an ID-aware M6 note-lock rule rather than array-index JSON Pointer identity.

The minimum R1 mechanism must support exact locks over stable note properties such as:

```text
part_id + note_id + property(pitch/start_beat/duration_beats/velocity)
```

Do not silently reinterpret existing M0 JSON-pointer locks. Existing locks continue to work unchanged; M6 note-lock behavior is additive and explicitly typed.

If a requested operation violates an inherited HARD note lock:

```text
BLOCKED / HARD_LOCK_VIOLATION
```

### 6. Constraints

Reuse existing Blueprint `validate_revision()` for current top-level locks/constraints after candidate construction. M6-specific exact-note invariants must run before acceptance.

Do not invent unsupported tonal/harmonic intelligence in R1. Structural exact-note constraints are in scope; perceptual/musical-quality judgement is not.

### 7. Preview vs Accept

Candidate resolution must be side-effect free with respect to `MusicaProject`.

Required proof:

```text
before preview: ref = X
resolve candidate
compile candidate
ref still = X
explicit commit_revision(...)
ref advances only after explicit acceptance
```

Use existing M2 commit/revision/audit mechanisms instead of creating a second version-control path.

### 8. Diff and provenance

Ensure exact-note edits appear in deterministic structured diff/provenance with stable note identity visible enough for audit.

Do not use Music IR diffs as project authority evidence.

## Required tests / 필수 테스트

At minimum add tests proving:

1. legacy motif Blueprint still validates and compiles identically;
2. valid explicit timeline validates;
3. duplicate `note_id` blocked;
4. unknown `part_id` blocked;
5. unknown `section_id` blocked;
6. exact timeline compiles deterministically;
7. explicit note pitch/start/duration/velocity survive compile faithfully;
8. semantic scaling does not silently rewrite exact note properties;
9. each of INSERT/DELETE/MOVE/RESIZE/REPITCH/SET_VELOCITY works by stable ID;
10. stale project/revision/hash blocks;
11. missing target note blocks;
12. duplicate operation IDs block;
13. HARD stable-note lock conflict blocks;
14. existing top-level HARD locks/constraints still block where applicable;
15. preview is side-effect free;
16. explicit M2 accept creates a new accepted revision;
17. direct Music IR authority remains impossible;
18. deterministic diff/provenance is stable across repeat execution.

## Evidence target / 근거 목표

Add a canonical M6-R1 demo/evidence runner, preferably:

```text
python -m musica.m6_r1_demo --out artifacts/m6-r1-exact-note-edit
```

It should prove at least:

- motif-only backward compatibility;
- exact-note Blueprint compile;
- valid multi-operation edit preview;
- stable-ID authority;
- stale-source block;
- HARD note-lock block;
- project ref unchanged before Accept;
- explicit Accept creates exactly one new accepted revision;
- accepted exact notes compile deterministically;
- evidence manifest binds exact source/candidate/IR hashes.

## M6-R1 merge discipline / 병합 규율

```text
Issue
→ fresh branch from canonical main
→ implementation + tests
→ PR
→ exact-head full CI + previous evidence regressions
→ inspect evidence artifact
→ durable evidence/M6_R1_VALIDATION.md
→ exact evidence-bearing head rerun
→ merge
→ state-only closure to M6-R2
```

## Scope control / 범위 통제

Do **not** add in M6-R1:

- piano-roll browser UI;
- waveform/destructive audio editing;
- automation lanes;
- mixer console;
- live MIDI recording;
- VST/AU/CLAP hosting;
- arbitrary DAW reverse mapping;
- new perceptual-quality claims;
- live OpenAI evidence;
- collaborative editing.

These can follow only after the core authority/runtime path is proven.

## Expected next after R1 / R1 이후 예상

If M6-R1 is validated:

```text
M6-R2 — Browser Studio Piano-Roll / Inspect Surface
M6-R3 — Real-browser exact-note E2E + lock/conflict UX
M6-R4 — bounded interchange reconciliation for representable note edits
```

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
