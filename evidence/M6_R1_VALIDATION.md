# M6-R1 Validation / M6-R1 검증 기록

**Milestone / 마일스톤:** `M6-R1 — Typed Exact-Note Material + Edit Engine`

**Governing Issue / 지배 Issue:** `#54`

**Implementation PR / 구현 PR:** `#55`

**Validation class / 검증 분류:** `BOUNDED_CORE_RUNTIME_EVIDENCE`

## 1. Verdict / 판정

M6-R1 has reached an evidence-backed implementation candidate for the bounded trusted-core exact-note authority path.

M6-R1은 제한된 trusted-core exact-note 권한 경로에 대해 근거가 결박된 구현 후보 상태에 도달했습니다.

Promotion to final `VALIDATED — BOUNDED CORE RUNTIME` is effective only when the exact successor head containing this durable record passes the same required CI/evidence gates. Until that evidence-bearing rerun succeeds, this file records the validated pre-durable implementation evidence rather than authorizing merge by itself.

본 durable record를 포함한 exact successor head가 동일한 필수 CI/evidence gate를 통과한 경우에만 최종 `VALIDATED — BOUNDED CORE RUNTIME` 승격이 유효합니다. 그 전까지 본 문서는 merge 권한 자체가 아니라 pre-durable 구현 검증 근거를 기록합니다.

## 2. Canonical starting point / 공식 시작점

- canonical main at M6-R1 start: `f3aa58096f860fece59935bd9bbff69d0c3e848b`
- M6-R0 design merge: `9a7beb133c4094d16a58466e97baec831ea98a01`
- M6-R0 state closure merge: `f3aa58096f860fece59935bd9bbff69d0c3e848b`
- M6-R1 branch: `m6-r1-exact-note-edit-engine`
- pre-durable implementation/evidence head: `74ab3b4872230957a36aaad5f3a856b530e60ded`

## 3. Implemented runtime boundary / 구현된 런타임 경계

M6-R1 implements the M6-R0 authority model in the core without adding Browser Studio piano-roll authority.

Implemented:

1. optional `materials.melody.exact_timeline` Blueprint validation;
2. legacy `motif_notes` backward-compatible compiler path;
3. fixed-tempo, motif/lead-part-bounded exact-note runtime;
4. deterministic exact beat-to-tick lowering;
5. faithful exact pitch/start/duration/velocity lowering without hidden semantic rescaling;
6. stable-ID operations `INSERT / DELETE / MOVE / RESIZE / REPITCH / SET_VELOCITY`;
7. exact `project_id + revision_id + Blueprint SHA-256` source binding;
8. deterministic stable `(part_id, note_id)` note diff;
9. additive stable-ID HARD exact-note lock contract and runtime enforcement;
10. stable-ID lock enforcement inside `validate_revision()` so direct M2 commit cannot bypass it;
11. side-effect-free non-canonical Preview;
12. explicit Accept through existing M2 `commit_revision()` only;
13. deterministic candidate/accepted compilation and M2 integrity verification;
14. canonical evidence runner and dedicated CI workflow.

Primary files:

- `schemas/exact-note-lock-v0.schema.json`
- `src/musica/contracts.py`
- `src/musica/compiler.py`
- `src/musica/note_edit.py`
- `tests/test_m6_r1_note_edit.py`
- `src/musica/m6_r1_demo.py`
- `.github/workflows/m6-r1-evidence.yml`
- `docs/M6_R1_RUNTIME.md`

## 4. Authority proof / 권한 증명

Validated path:

```text
Accepted Blueprint
→ typed NoteEditCandidate
→ exact source binding
→ stable-ID operations
→ Blueprint candidate
→ stable-ID HARD note lock + existing revision validation
→ READY_FOR_PREVIEW — non-canonical
→ explicit Accept only
→ existing M2 commit_revision
→ new accepted Blueprint
→ deterministic Music IR
```

Still forbidden:

```text
Music IR direct mutation → accepted project state
```

The M6-R1 authority result continues to require:

```text
explicit_accept_required = true
project_mutation_authorized = false
music_ir_mutation_authorized = false
```

## 5. Pre-durable exact-head CI / pre-durable exact-head CI

Exact head:

`74ab3b4872230957a36aaad5f3a856b530e60ded`

Required workflows:

| Workflow / 워크플로 | Run | Result |
|---|---:|---|
| MUSICA CI | `34691539628` | **SUCCESS** |
| M6-R1 Exact-Note Edit Evidence | `34691539629` | **SUCCESS** |
| M5-R3 DAWproject Evidence | `34691539650` | **SUCCESS** |
| M5-R4 Paired Audio Evidence | `34691539635` | **SUCCESS** |

The full suite passed on Python 3.11 and Python 3.12; the Python 3.12 job also regenerated the prior M0→M5-R1 evidence chain successfully. Existing Browser Studio Chromium E2E and Windows FluidSynth evidence also remained green.

## 6. M6-R1 artifact / M6-R1 artifact

Second canonical M6-R1 evidence run:

- workflow run: `34691539629`
- head: `74ab3b4872230957a36aaad5f3a856b530e60ded`
- artifact name: `musica-m6-r1-exact-note-edit`
- artifact ID: `10296394258`
- GitHub ZIP packaging digest: `sha256:f74f041686a4e2b34dd7d453025f29cac734f60eb9fc005cb411545ba1bf245f`
- artifact size: `42011` bytes
- internal `manifest.json` SHA-256: `4f00c0da286c0b62d00a9bfe98e0ea33a8f8cfdb0945803fe1574b21daf66bcc`

Canonical Blueprint hash bindings recorded inside the evidence:

- exact source Blueprint SHA-256: `b216c8772eb72de42160e0d104430307e9079d08dcc41af7be0e4832e5786aca`
- candidate Blueprint SHA-256: `b3e7e4fa7c2b881f11350f61cd185e0fe147f60e8a61ca14ef192b45914e0042`
- accepted Blueprint SHA-256: `b3e7e4fa7c2b881f11350f61cd185e0fe147f60e8a61ca14ef192b45914e0042`

Candidate and accepted Blueprint hashes are equal because acceptance persists the exact validated Preview Blueprint rather than reinterpreting or relowering the creative state.

## 7. Evidence reproducibility / 근거 재현성

Two independent M6-R1 evidence workflow executions were inspected:

### Run 1

- run: `34691419521`
- head: `700236ba5bceee16229dda32239fc2446822bee0`
- artifact ID: `10296299327`
- GitHub ZIP digest: `sha256:f866fd3c07109651f6d9623752a1c21d204eb1d5bfa66e0600d029b572821356`

### Run 2

- run: `34691539629`
- head: `74ab3b4872230957a36aaad5f3a856b530e60ded`
- artifact ID: `10296394258`
- GitHub ZIP digest: `sha256:f74f041686a4e2b34dd7d453025f29cac734f60eb9fc005cb411545ba1bf245f`

GitHub ZIP container digests differ because artifact packaging metadata is external to the MUSICA evidence contract. The extracted internal evidence was compared directly:

- file lists: identical;
- `manifest.json`: byte-identical;
- `proof.json`: byte-identical;
- all tracked internal files: byte-identical;
- internal manifest SHA-256 in both runs: `4f00c0da286c0b62d00a9bfe98e0ea33a8f8cfdb0945803fe1574b21daf66bcc`;
- internal file differences: **0**.

This demonstrates deterministic M6-R1 evidence content across the two runs despite different GitHub packaging digests.

## 8. Positive exact-note proof / 양성 exact-note 증명

The canonical evidence executes all six operation types in one source-bound Preview:

- `MOVE` — `N-MOTIF-001` start `0.0 → 0.25` beat;
- `REPITCH` — `N-MOTIF-001` pitch `62 → 64`;
- `SET_VELOCITY` — `N-MOTIF-001` velocity `82 → 90`;
- `DELETE` — removes `N-MOTIF-002`;
- `RESIZE` — `N-MOTIF-003` duration `1.5 → 1.25` beats;
- `INSERT` — adds `N-MOTIF-004` at beat `4.0`, pitch `67`, velocity `74`.

Stable IDs changed:

```text
N-MOTIF-001
N-MOTIF-002
N-MOTIF-003
N-MOTIF-004
```

Accepted motif note events in Music IR were inspected as:

```text
note 64 / tick 120  / duration 360 / velocity 90
note 69 / tick 960  / duration 600 / velocity 80
note 67 / tick 1920 / duration 240 / velocity 74
```

These events correspond directly to the accepted exact-note Blueprint state under `PPQ=480`.

## 9. Preview / Accept / M2 integrity proof

Canonical evidence proves:

- source revision remains current before Preview;
- resolving and compiling Preview does not advance the project ref;
- Preview is non-canonical;
- explicit Accept creates child revision `rev-m6-r1-evidence-001`;
- accepted Blueprint equals the validated Preview Blueprint;
- accepted revision count = `2`;
- project object count = `6`;
- audit event count = `2`;
- project integrity status = **PASS**;
- repeated candidate compilation is deterministic;
- repeated accepted compilation is deterministic.

## 10. Negative authority proofs / 음성 권한 증명

### Stale source

A candidate with a mismatched Blueprint SHA-256 is rejected as:

```text
status = BLOCKED
code = STALE_SOURCE
preview Blueprint = none
project_mutation_authorized = false
music_ir_mutation_authorized = false
```

### Stable-ID HARD note lock

A repitch operation against a stable-ID HARD pitch lock is rejected as:

```text
status = BLOCKED
code = HARD_LOCK_VIOLATION
rule_id = L-M6-R1-EVIDENCE-PITCH
preview Blueprint = none
```

The same lock is also enforced through `validate_revision()`, preventing direct `MusicaProject.commit_revision()` from bypassing Preview authority.

### Direct Music IR authority

The R0 candidate schema still cannot represent Music IR as an authority target. M6-R1 does not add any Music IR mutation or acceptance path.

## 11. Backward compatibility / 하위 호환

Legacy Blueprint projects without `materials.melody.exact_timeline` continue through the previous `motif_notes` compiler path.

Evidence/tests prove:

- legacy Blueprint remains valid;
- repeated legacy compilation remains deterministic;
- exact-note material remains optional;
- exact-note lowering is selected only when `exact_timeline` is present.

## 12. Claim boundary / 주장 경계

If the evidence-bearing successor head passes the required gates, M6-R1 supports the bounded claim:

> **MUSICA can represent, validate, preview, accept, version and deterministically compile bounded exact note-level edits through stable identities while preserving Blueprint/M2 authority above Music IR.**
>
> **MUSICA는 stable identity를 통해 제한된 exact note-level 편집을 표현·검증·Preview·Accept·버전화·결정론적으로 컴파일하면서 Blueprint/M2의 Music IR 상위 권한을 유지할 수 있다.**

M6-R1 does **not** validate or imply:

- Browser Studio piano-roll editing;
- real-browser drag/resize/repitch interaction;
- arbitrary polyphonic or every-instrument-part editing;
- arbitrary tempo-map editing;
- arbitrary DAW reverse mapping;
- live MIDI recording;
- waveform/destructive audio editing;
- mixer/automation/plugin hosting;
- human-subject usability evidence;
- perceptual, production or mastering superiority.

These remain future milestones and require separate evidence.

## 13. Final promotion gate / 최종 승격 gate

The exact successor head containing this document must pass all of:

1. MUSICA CI — Python 3.11/3.12 + prior evidence chain;
2. M6-R1 Exact-Note Edit Evidence;
3. M5-R3 DAWproject Evidence regression;
4. M5-R4 Paired Audio Evidence regression.

After those exact-head gates pass, PR #55 may be merged with expected-head protection, Issue #54 may be closed, and canonical state may advance to:

> **M6-R1 — VALIDATED — BOUNDED CORE RUNTIME**

The next bounded milestone is then:

> **M6-R2 — Browser Studio Piano-Roll / Inspect Surface**
