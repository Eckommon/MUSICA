# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M6-R0 — PRECISION EDITING AUTHORITY & CANONICAL NOTE MODEL v0 / M6-R0 — 정밀 편집 권한 및 공식 Note Model v0**

M0→M5-R4 are `VALIDATED` within bounded claims. The next task is not another renderer, another audio metric, or a piano-roll UI built directly on Music IR. The next task is to define the **canonical authority contract for exact note-level user edits**.

M0→M5-R4는 제한 주장 범위에서 검증 완료되었습니다. 다음 작업은 새 renderer·새 품질 점수·Music IR 직접 조작 piano-roll이 아닙니다. **정확한 note-level 사용자 편집을 공식 프로젝트 상태로 수용하는 권한 계약**을 먼저 정의해야 합니다.

## Why this is next / 왜 다음 단계인가

The product promise requires professional precision, but the repository currently has a deliberate boundary:

- conceptual `Music Blueprint v0` says melody may contain explicit notes when needed;
- concrete `music-blueprint-v0.schema.json` leaves `materials.melody` structurally open;
- canonical Music IR contains executable events, but Music IR is derived state and cannot become project authority;
- M5-R3 correctly classified arbitrary external note edits as `UNSUPPORTED_BLOCKING` because reverse mapping into Blueprint v0 was not defined;
- Browser Studio has Direct/Shape/Inspect/Code views but does not yet validate a professional note-level editing surface.

Therefore MUSICA must type and govern exact-note edits before implementing a piano roll.

## Core invariant / 핵심 불변식

```text
Accepted Blueprint revision
→ trusted lowering
→ Music IR

User exact-note edit
→ typed NoteEditCandidate
→ Blueprint-representable delta
→ HARD lock + constraint validation
→ PREVIEW — non-canonical
→ explicit Accept only
→ new accepted M2 revision
→ trusted lowering
→ new Music IR
```

Forbidden:

```text
Music IR event mutation → accepted project state
```

Music IR remains executable derived representation, never the canonical creative authority.

## M6-R0 contract questions / 계약 질문

M6-R0 must answer explicitly:

1. **Canonical note representation** — what exact note properties may live in Blueprint v0/v0.x?
2. **Ownership** — how notes bind to part/role/section/motif identity.
3. **Time representation** — musical time vs seconds/ticks; deterministic conversion rules.
4. **Identity** — stable note/event IDs across edits and revisions.
5. **Edit vocabulary** — insert, delete, move, resize, repitch, velocity/dynamic change, bounded batch transform.
6. **Authority** — how an edit becomes a Blueprint candidate instead of mutating IR.
7. **Lock interaction** — exact and identity locks over melody/rhythm/section/part.
8. **Constraint interaction** — register, section bounds, duration, tonal/harmonic constraints where applicable.
9. **Semantic coexistence** — how explicit notes coexist with motif/contour/semantic intent without silently discarding one layer.
10. **Diff/provenance** — exact machine-readable before/after note changes and user reason.
11. **Compilation** — deterministic lowering from typed note material to Music IR.
12. **Interchange** — what previously unsupported DAWproject note edits could become representable later without changing M5-R3 historical evidence.

## Required M6-R0 deliverables / 필수 산출물

Create a fresh governing Issue and branch from canonical main.

Recommended branch:

```text
m6-r0-precision-editing-authority-v0
```

Required package:

1. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
2. `docs/M6_ACCEPTANCE.md`
3. machine-readable note/edit contract draft, preferably under `schemas/`
4. canonical examples for exact note material and edit candidates
5. explicit authority/precedence rules
6. hard-lock/constraint conflict examples
7. migration/backward-compatibility rule for existing Blueprint v0 fixtures
8. compiler impact analysis
9. M2 revision/diff/provenance impact analysis
10. Browser Studio implementation handoff for M6-R1+

## Strong design default / 강한 설계 기본값

Unless repository evidence forces a different choice, use these defaults:

- exact notes belong in **Blueprint musical material**, not directly in Music IR;
- each exact note has a stable `note_id` within its accepted revision lineage;
- note time is represented in musical coordinates sufficient for deterministic compile, with derived seconds/ticks lower in the stack;
- every edit is a typed candidate with source revision binding;
- stale source revision → fail closed;
- exact lock violation → fail closed;
- identity lock violation → fail closed or emit explicit alternatives;
- edits remain PREVIEW until explicit Accept;
- accepted edits create a new M2 revision and provenance event;
- existing Blueprints without exact-note material remain valid unless an explicit schema-version migration is accepted.

## Scope control / 범위 통제

M6-R0 is a contract/design milestone. Do **not** implement the full piano roll yet.

Do not add in R0:

- waveform editor;
- audio destructive editing;
- arbitrary automation lanes;
- mixer console;
- VST/AU/CLAP hosting;
- full score engraving;
- live MIDI recording;
- collaborative editing;
- direct Music IR authority;
- silent schema-breaking migration.

## Planned implementation sequence after R0 / R0 이후 예정 순서

If R0 is accepted, the preferred sequence is:

```text
M6-R1 — Typed Exact-Note Material + Edit Engine
M6-R2 — Browser Studio Piano-Roll / Inspect Surface
M6-R3 — Real-browser exact-note E2E + lock/conflict UX
M6-R4 — bounded interchange reconciliation for representable note edits
```

This sequence is provisional until M6-R0 contracts are ratified.

## Deferred independent evidence tracks / 독립 보류 근거 트랙

The following remain important but should not displace M6-R0:

### Live OpenAI provider smoke
- current status: `NOT VALIDATED`;
- requires authorized live credential/network execution;
- must be recorded separately as `LIVE_PROVIDER_EVIDENCE`;
- must not rewrite M3-R2 offline evidence.

### Human-subject usability / perceptual study
- current status: `NOT VALIDATED`;
- requires actual participant evidence and a separate protocol;
- machine objective metrics cannot substitute for it.

## M6-R0 acceptance gate / 수용 gate

R0 may be accepted only if the design package proves that:

- Blueprint remains canonical;
- Music IR remains derived;
- note edits are exactly diffable and provenance-carrying;
- stale edits fail closed;
- HARD locks remain authoritative;
- existing accepted projects have an explicit compatibility policy;
- compiler and M2 impacts are bounded and implementable;
- the next implementation milestone can be tested without inventing hidden reverse mapping.

## Completion claim / 완료 주장

Successful M6-R0 may claim only:

> MUSICA has an accepted authority and data contract for representing exact note-level creative decisions and turning user note edits into validated Blueprint candidates without promoting Music IR to canonical state.

It may not yet claim that a professional piano-roll editor is implemented or usable.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
