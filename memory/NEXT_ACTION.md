# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M6-R4 — BOUNDED INTERCHANGE RECONCILIATION FOR REPRESENTABLE EXACT-NOTE EDITS / M6-R4 — 표현 가능한 exact-note 편집의 제한된 interchange reconciliation**

M6-R3 is `VALIDATED — BOUNDED REAL-BROWSER EXACT-NOTE E2E`. The exact next task is to connect the historically bounded M5-R3 DAWproject bridge to the M6 exact-note authority **without granting external interchange state canonical authority**.

M6-R3는 `VALIDATED — BOUNDED REAL-BROWSER EXACT-NOTE E2E`입니다. 정확한 다음 작업은 M5-R3의 제한된 DAWproject bridge를 M6 exact-note authority와 연결하되 **외부 interchange 상태에 canonical authority를 부여하지 않는 것**입니다.

## Canonical starting point / 공식 시작점

- M6-R3 implementation merge/main: `327939e71bd63611f747bac147c4ba6591052b93`
- Issue #60: **COMPLETED**
- PR #61: **MERGED**
- final evidence-bearing M6-R3 exact head: `c4b525a9083ff8a537b411789b8bbfbf39c04a7b`
- final MUSICA CI: `34720643018` — **SUCCESS**
- final M6-R3 real-browser evidence: `34720643011` — **SUCCESS**
- final M6-R2 regression: `34720643012` — **SUCCESS**
- final M6-R1 regression: `34720642999` — **SUCCESS**
- final M5-R3 regression: `34720643007` — **SUCCESS**
- final M5-R4 regression: `34720643001` — **SUCCESS**
- final M6-R3 artifact ID: `10305989929`
- final artifact packaging digest: `sha256:2e44021ddd2a2803379f2223b045463d1a81c334afdb695d10df9b8fc5d914c0`
- internal M6-R3 manifest SHA-256: `825c5d69f55a40ba77deefe1bdb3bba4974f0ed26d0cf1696aa11718dcff58ec`
- 18/18 manifest records independently rehashed with exact size/hash match
- durable evidence: `evidence/M6_R3_VALIDATION.md`

## Why M6-R4 exists / M6-R4가 필요한 이유

M5-R3 deliberately blocked arbitrary external note reverse mapping. That decision was correct at M5-R3 because the then-accepted Blueprint did not own a validated canonical exact-note timeline.

M6-R1→R3 changed the authority facts:

- accepted Blueprint may now contain canonical `exact_timeline` note material;
- notes have stable `note_id + part_id` identity;
- exact source binding uses project/revision/Blueprint SHA-256;
- six primitive note edits have a typed `NoteEditCandidate` contract;
- stale source, HARD locks and constraints fail closed;
- Browser Studio proves Preview/Accept/Discard through real Chromium.

Therefore R4 may safely revisit **only the representable subset** of interchange note changes. It may not reinterpret M5-R3 as having validated arbitrary reverse mapping and must not rewrite its historical evidence.

## Governing contracts / 지배 계약

Read and obey before implementation:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
4. `docs/M6_ACCEPTANCE.md`
5. `docs/M6_R1_RUNTIME.md`
6. `docs/M5_R3_ACCEPTANCE.md`
7. `docs/M5_R3_ROUNDTRIP_AUTHORITY.md`
8. `evidence/M5_R3_VALIDATION.md`
9. `schemas/exact-note-material-v0.schema.json`
10. `schemas/note-edit-candidate-v0.schema.json`
11. `schemas/note-edit-authority-result-v0.schema.json`
12. `schemas/exact-note-lock-v0.schema.json`
13. M5-R3 DAWproject export/import contracts and implementation
14. `src/musica/note_edit.py`
15. `src/musica/studio_notes.py`
16. `evidence/M6_R1_VALIDATION.md`
17. `evidence/M6_R2_VALIDATION.md`
18. `evidence/M6_R3_VALIDATION.md`

## Core invariant / 핵심 불변식

```text
Accepted exact-note Blueprint revision
→ exact source project/revision/Blueprint hash
→ deterministic bounded M5-R3 DAWproject export
→ export provenance + source identity mapping
→ optional external note modification
→ safe DAWproject parse + normalization
→ compare against exact exported baseline
→ reconcile only provably representable note changes
→ typed NoteEditCandidate primitives
→ M6-R1 source/identity/lock/constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept / Discard
→ existing M2 authority only
```

Forbidden:

```text
external DAWproject state → accepted Blueprint directly
external DAW note index/order → MUSICA note identity
Music IR event diff → accepted Blueprint directly
ambiguous mapping → guessed NoteEditCandidate
stale export lineage → silent rebase
unsupported DAW semantics → silent drop then Accept
external application metadata → project authority
```

## Required M6-R4 implementation / 필수 구현

### 1. Exact source-bound interchange envelope

R4 must bind a reconciliation attempt to the exact MUSICA source that produced the exported interchange artifact.

At minimum bind:

```text
project_id
accepted revision_id
canonical Blueprint SHA-256
canonical exact-note source hash or equivalent material binding
export artifact SHA-256
M5-R3 exporter/importer + normalization policy identity
DAWproject version
track/part mapping provenance
```

A DAWproject artifact whose MUSICA lineage cannot be proven must not enter the exact-note reconciliation path.

### 2. Baseline-versus-returned comparison

Do **not** infer edits from the returned DAWproject in isolation.

R4 must compare:

```text
A = exact normalized bounded DAWproject model originally exported by MUSICA
B = normalized returned/modified bounded DAWproject model
```

Only semantic differences between A and B that can be traced back to the accepted exact-note source may be candidates for M6 reconciliation.

ZIP metadata, XML ordering or other non-semantic serialization differences must not masquerade as note edits after normalization.

### 3. Stable note identity reconciliation

DAWproject representation must not be assumed to provide MUSICA-native `note_id` authority.

R4 must prove a deterministic identity bridge from each representable exported note back to `part_id + note_id`. Acceptable implementation may use a source-bound export mapping manifest/sidecar or another deterministic mapping proven by tests.

Requirements:

- no array-index identity;
- no nearest-note heuristic when multiple matches are possible;
- no guessed identity after note reorder;
- duplicate/ambiguous correspondence fails closed;
- source note deletions and returned note insertions are handled only when identity semantics are explicit;
- the mapping itself is hash-bound to the exact export/source.

### 4. Representable edit vocabulary

A returned interchange change may reconcile only if it can be expressed exactly as the existing M6 primitive vocabulary:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

R4 must not introduce a second DAW-specific note-edit authority engine.

For each reconciled difference, construct the same typed `NoteEditCandidate` contract used by Browser Studio.

Examples of potentially representable bounded changes:

- one known note pitch changed → `REPITCH`;
- one known note start changed within supported bounds → `MOVE`;
- one known note duration changed → `RESIZE`;
- one known note velocity changed under the explicit M5-R3 normalization inverse → `SET_VELOCITY`;
- one known source note absent → `DELETE`;
- one new note with provable part/section/timing identity → `INSERT`.

### 5. Mixed/unsupported semantic changes

R4 must fail closed when the returned artifact contains note changes mixed with unsupported or authority-changing semantics that make safe reconciliation ambiguous.

At minimum distinguish:

- `REPRESENTABLE_NOTE_EDIT`
- `UNSUPPORTED_SEMANTIC_CHANGE`
- `AMBIGUOUS_IDENTITY`
- `SOURCE_BINDING_MISMATCH`
- `STALE_SOURCE`
- `MAPPING_INTEGRITY_FAILURE`
- existing M6 lock/constraint conflict codes after candidate construction.

The implementation may use a new reconciliation result contract, but final note authority must still be delegated to the existing M6-R1 engine.

### 6. Tempo/meter and note-edit boundary

M6-R4 is a note-reconciliation milestone, not a broad interchange-authority expansion.

- arbitrary tempo maps remain outside scope;
- M5-R3's existing supported bounded meter behavior remains historically valid but must not be conflated with M6 exact-note reconciliation;
- a returned artifact that changes unsupported tempo/meter semantics alongside notes must fail closed for R4 rather than partially accepting notes silently;
- fixed-tempo exact-note assumptions remain in force unless a separate contract expands them.

### 7. HARD lock / constraint enforcement

Once a DAWproject note delta becomes a typed `NoteEditCandidate`, all normal M6 authority applies unchanged.

Required negative proof:

```text
representable DAW note change
→ correct stable note mapping
→ typed NoteEditCandidate
→ HARD lock conflict
→ BLOCKED / HARD_LOCK_VIOLATION
→ no pending Preview
→ accepted ref unchanged
```

Interchange provenance never weakens or deletes a lock.

### 8. Stale export protection

A DAWproject exported from revision A must not be silently reconciled after MUSICA has accepted revision B.

Required outcome:

```text
source revision/hash mismatch
→ BLOCKED / STALE_SOURCE or stronger reconciliation-source failure
→ no silent rebase
→ no pending Preview
→ accepted ref unchanged
```

If the user wants to apply the external changes, a fresh reconciliation must be explicitly produced against current accepted state under a separately proven mapping policy.

### 9. Preview/Accept reuse

A valid reconciled note candidate remains non-canonical:

```text
RECONCILED
→ READY_FOR_PREVIEW
→ PREVIEW · NOT ACCEPTED
→ explicit Accept / Discard
→ existing M2 commit only
```

No import/reconcile action may implicitly commit the candidate.

### 10. Loss/provenance reporting

Preserve the M5-R3 five-state loss taxonomy:

```text
PRESERVED | TRANSFORMED | DROPPED | UNSUPPORTED | UNKNOWN
```

R4 evidence must additionally bind:

- original export artifact hash;
- returned artifact hash;
- normalized baseline hash;
- normalized returned hash;
- identity mapping hash;
- exact source Blueprint hash;
- reconciliation result hash;
- resulting `NoteEditCandidate` hash;
- authority result;
- stable-note diff;
- Preview/accepted revision when applicable.

### 11. Security/fail-closed inheritance

All M5-R3 ZIP/XML security boundaries remain mandatory. R4 must not create a less strict import path.

Malformed, traversal, duplicate-critical-entry, XSD-invalid, unsupported-version, oversized or provenance-tampered artifacts remain blocked before note reconciliation.

### 12. Backward compatibility

M5-R3's historical arbitrary-note-edit test and evidence remain unchanged and correct for its milestone context.

R4 should add a **new explicit reconciliation path** that is only available when canonical exact-note material plus required source/mapping evidence exist.

Legacy motif-only projects must not gain reverse-mapped canonical notes from DAWproject or Music IR.

## Required tests / 필수 테스트

At minimum prove:

1. exact-note project exports through the existing bounded M5-R3 DAWproject adapter without accepted-state mutation;
2. export evidence binds source project/revision/Blueprint/exact-note material;
3. unmodified export reconciles to zero note operations;
4. XML/ZIP serialization-only changes reconcile to zero musical operations;
5. one representable `REPITCH` maps to the correct stable note ID;
6. one representable `MOVE` maps correctly;
7. one representable `RESIZE` maps correctly;
8. one representable `SET_VELOCITY` maps correctly under declared conversion tolerance/policy;
9. one representable `DELETE` maps correctly;
10. one representable `INSERT` maps correctly only with explicit supported identity/ownership semantics;
11. each positive case becomes a typed source-bound `NoteEditCandidate`;
12. Preview leaves accepted ref unchanged;
13. explicit Accept advances exactly once through M2;
14. Discard preserves accepted state;
15. HARD note lock blocks a mapped external change;
16. stale exported source blocks reconciliation;
17. ambiguous stable-note mapping blocks reconciliation;
18. unsupported/mixed semantic edits block or remain explicitly non-acceptable;
19. provenance/mapping hash tamper blocks reconciliation;
20. legacy motif-only project cannot fabricate exact-note authority;
21. M5-R3 ZIP/XML security negatives remain green;
22. Python 3.11 / 3.12 full suite remains green;
23. M4-R3, M5-R2/R3/R4-quality and M6-R1/R2/R3 regressions remain green.

## Canonical evidence target / 공식 근거 목표

Recommended dedicated artifact:

```text
artifacts/m6-r4-interchange-note-reconciliation/
  manifest.json
  proof.json
  source-blueprint.json
  source-note-view.json
  source-export.dawproject
  source-export-manifest.json
  source-note-identity-map.json
  returned-artifact.dawproject
  normalized-source.json
  normalized-returned.json
  reconciliation-result.json
  note-edit-candidate.json
  authority-result.json
  preview-note-view.json
  accepted-note-view.json
  loss-report.json
  negative-stale.json
  negative-hard-lock.json
  negative-ambiguous-map.json
  negative-unsupported-change.json
```

Machine-readable evidence, not screenshots, is primary for R4.

## M6-R4 merge discipline / 병합 규율

```text
Issue
→ fresh implementation branch from canonical main after M6-R3 state closure
→ inspect/reuse M5-R3 adapter rather than duplicate it
→ add source-bound note identity/reconciliation contract
→ targeted reconciliation tests + M5/M6 regressions
→ PR
→ exact-head full CI
→ inspect M6-R4 artifact
→ durable evidence/M6_R4_VALIDATION.md
→ exact evidence-bearing rerun
→ expected-head merge
→ Issue completed
→ state-only closure to next bounded mission
```

## Scope control / 범위 통제

Do **not** claim or add in M6-R4:

- arbitrary DAW reverse mapping;
- external DAW state as canonical authority;
- compatibility with every DAW or tested real-DAW execution;
- arbitrary tempo-map reconciliation;
- arbitrary polyphonic/every-part editing beyond the supported exact-note scope;
- plug-in/device state round-trip;
- mixer/automation fidelity;
- waveform/destructive audio editing;
- general quantize/humanize/batch transforms unless separately contracted;
- live MIDI recording;
- VST/AU/CLAP hosting;
- cloud/collaborative authority;
- human-subject usability or perceptual-superiority claims.

## Promotion claim if successful / 성공 시 허용 주장

If all M6-R4 gates pass, the maximum intended bounded claim is:

> **A MUSICA-origin bounded DAWproject artifact can carry representable exact-note changes back as source-bound stable-identity `NoteEditCandidate` operations, which remain non-canonical and are accepted only after normal M6 authority and explicit M2 acceptance.**
>
> **MUSICA-origin 제한 DAWproject artifact의 표현 가능한 exact-note 변경은 source-bound stable-identity `NoteEditCandidate` 연산으로 환원될 수 있으며, 일반 M6 권한 검증과 명시적 M2 Accept를 통과하기 전까지 비공식 상태로 유지된다.**

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
