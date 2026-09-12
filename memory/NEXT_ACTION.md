# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M6-R2 — BROWSER STUDIO PIANO-ROLL / INSPECT SURFACE / M6-R2 — Browser Studio Piano-Roll / Inspect Surface**

M6-R1 is `VALIDATED — BOUNDED CORE RUNTIME`. The next task is to expose the already validated exact-note authority path through the existing local-first Browser Studio without giving the browser, DOM, canvas or Music IR direct project authority.

M6-R1은 `VALIDATED — BOUNDED CORE RUNTIME`입니다. 다음 작업은 이미 검증된 exact-note 권한 경로를 기존 local-first Browser Studio에 노출하되 browser/DOM/canvas/Music IR에 직접 프로젝트 권한을 부여하지 않는 것입니다.

## Canonical starting point / 공식 시작점

- M6-R1 implementation merge: `7adf507630334021459e89055e98627d184f5354`
- Issue #54: **COMPLETED**
- PR #55: **MERGED**
- final evidence-bearing M6-R1 exact head: `4cff9ae28bcaa49ac4c96019d4d0d4e47b773857`
- final MUSICA CI: `34691729996` — **SUCCESS**
- final M6-R1 evidence: `34691730003` — **SUCCESS**
- final M5-R3 regression: `34691730001` — **SUCCESS**
- final M5-R4 regression: `34691730000` — **SUCCESS**
- final M6-R1 artifact ID: `10297550295`
- final artifact packaging digest: `sha256:585df28c91652d7965de898c32ba568ddb0eb5c0b9abb164a4f45387378f7020`
- internal M6-R1 manifest SHA-256: `4f00c0da286c0b62d00a9bfe98e0ea33a8f8cfdb0945803fe1574b21daf66bcc`
- durable evidence: `evidence/M6_R1_VALIDATION.md`

## Governing contracts / 지배 계약

Read and obey:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
4. `docs/M6_ACCEPTANCE.md`
5. `docs/M6_R1_RUNTIME.md`
6. `schemas/exact-note-material-v0.schema.json`
7. `schemas/note-edit-candidate-v0.schema.json`
8. `schemas/note-edit-authority-result-v0.schema.json`
9. `schemas/exact-note-lock-v0.schema.json`
10. `src/musica/note_edit.py`
11. `src/musica/studio.py`
12. `src/musica/studio_http.py`
13. `src/musica/studio_web/index.html`
14. `src/musica/studio_web/app.js`
15. `src/musica/studio_web/app.css`
16. `evidence/M6_R1_VALIDATION.md`

## Core invariant / 핵심 불변식

```text
Accepted exact-note Blueprint
→ Studio read projection
→ Browser piano-roll projection
→ user edit gesture/form input
→ typed NoteEditCandidate
→ M6-R1 source/lock/constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW — non-canonical
→ audible + diff inspection
→ explicit Accept or Discard
→ existing M2 authority only
```

Forbidden:

```text
DOM/canvas state → canonical project
Music IR event mutation → canonical project
browser-local note array → canonical project
```

## Required M6-R2 implementation / 필수 구현

### 1. Studio service exact-note read projection

Add a stable read-only service boundary that exposes the accepted exact-note material required by the piano roll without leaking direct filesystem authority.

Recommended operation:

```text
GET /v0/sessions/{session_id}/notes
```

Response should include at minimum:

- exact accepted `project_id`;
- accepted `revision_id`;
- canonical Blueprint SHA-256;
- current branch;
- fixed tempo and PPQ projection metadata;
- editable part metadata;
- section ranges;
- stable exact notes sorted canonically;
- stable-ID HARD note locks relevant to visible notes;
- capability flags describing the bounded R2 editing surface.

If the accepted Blueprint has no `exact_timeline`, R2 must fail closed or expose an explicit `exact_note_editing_available=false` state. It must not silently reverse-map Music IR into canonical exact notes.

### 2. Studio service note-edit Preview boundary

Add a Studio operation that receives a typed `NoteEditCandidate` payload or safely constructs one from a bounded browser command, then delegates to the M6-R1 engine.

Recommended operation:

```text
POST /v0/sessions/{session_id}/preview/notes
```

Required behavior:

- bind candidate to the current accepted project/revision/Blueprint hash;
- use stable `note_id + part_id` only;
- call the trusted M6-R1 note-edit authority path;
- map `BLOCKED` to a visible Studio conflict without installing a pending Preview;
- on `READY_FOR_PREVIEW`, install the candidate through existing `_install_preview()`;
- preserve the canonical branch ref before explicit Accept;
- reuse existing `accept_preview` and `discard_preview` paths;
- never create a second acceptance/versioning system.

### 3. Inspect piano-roll projection

Extend the existing **Inspect** depth rather than creating a disconnected editor mode.

The first bounded piano roll must provide:

- pitch rows and beat/time grid;
- section boundary overlays;
- accepted notes with stable identity;
- selected-note detail;
- visible locked-note/property state;
- preview notes visually distinct from accepted state;
- no dependence on third-party CDN/framework.

The visual surface may use plain DOM/SVG/Canvas, but authority must remain in the Studio service. Browser coordinates are merely interaction data.

### 4. Bounded R2 edit interactions

R2 must expose the M6-R1 primitive operations without inventing new authority semantics:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

A minimal professional-enough interaction set for R2 may use:

- click/select note;
- numeric/property controls for exact pitch/start/duration/velocity;
- move/resize controls or bounded drag where deterministically mapped;
- insert/delete actions;
- keyboard-accessible alternatives for any pointer interaction.

R2 does not need advanced multi-select, quantize, humanize or automation.

### 5. Preview authority UX

The existing Preview/Accept/Discard semantics must be reused.

When a note edit is ready:

- show `PREVIEW · NOT ACCEPTED`;
- render/play preview audio via the existing pending-preview media path;
- show stable-note diff rather than only generic JSON pointer noise where possible;
- show changed note IDs and operation summary;
- keep `Accept` explicit and separate from the edit gesture.

When blocked:

- do not install Preview;
- show bounded conflict code (`STALE_SOURCE`, `HARD_LOCK_VIOLATION`, etc.);
- show stable `note_id`, operation ID and rule ID where available;
- keep project ref unchanged.

### 6. Session/read model changes

Extend Studio session data only where necessary. Do not overload `studio-session-v0` with a huge note list if a dedicated note-view contract is cleaner.

Prefer additive machine contracts such as:

```text
schemas/studio-note-view-v0.schema.json
schemas/studio-note-preview-v0.schema.json   # only if existing response contracts are insufficient
```

All browser-facing JSON must remain schema validated.

### 7. Security/local-first constraints

Preserve all M4 boundaries:

- loopback-only server;
- no wildcard CORS;
- no directory listing;
- no upload endpoint;
- no third-party CDN dependency;
- no remote telemetry;
- existing CSP remains valid;
- bounded JSON request sizes;
- project paths remain workspace-confined.

### 8. Backward compatibility

Projects without exact-note material must continue to open, play, Shape, Inspect history/locks and export as before.

The piano roll should clearly explain that exact-note editing is unavailable for legacy motif-only material rather than fabricating canonical notes from Music IR.

## Required tests / 필수 테스트

At minimum prove:

1. accepted exact-note project returns deterministic note-view payload;
2. note view binds exact project/revision/Blueprint hash;
3. legacy motif-only project reports exact editing unavailable without failure;
4. read endpoint never mutates project refs;
5. browser-facing note payload is canonically ordered;
6. INSERT Preview through Studio leaves ref unchanged;
7. DELETE Preview through Studio leaves ref unchanged;
8. MOVE Preview through Studio leaves ref unchanged;
9. RESIZE Preview through Studio leaves ref unchanged;
10. REPITCH Preview through Studio leaves ref unchanged;
11. SET_VELOCITY Preview through Studio leaves ref unchanged;
12. blocked stable-ID HARD lock produces no pending Preview;
13. stale source produces no pending Preview;
14. explicit Accept advances exactly once through M2;
15. Discard preserves accepted ref;
16. accepted note state reloads after browser/session refresh;
17. existing semantic/director Preview behavior remains valid;
18. existing M4 Browser Studio tests remain green;
19. CSP/same-origin/local-only guarantees remain green;
20. no browser route can mutate Music IR directly.

## Browser evidence target / Browser 근거 목표

M6-R2 should add deterministic service/UI evidence but reserve full real-browser gesture acceptance for M6-R3.

Recommended bounded R2 evidence:

```text
python -m musica.m6_r2_demo --out artifacts/m6-r2-piano-roll
```

It should prove:

- exact-note project exposed through Studio note view;
- stable note identity visible;
- Browser assets include the Inspect piano-roll surface;
- valid note edit becomes a non-canonical pending Preview;
- accepted ref unchanged before Accept;
- blocked lock/stale cases create no Preview;
- explicit Accept uses the existing Studio/M2 path;
- accepted exact notes survive reopen;
- manifest binds source/view/candidate/accepted hashes.

## M6-R2 merge discipline / 병합 규율

```text
Issue
→ fresh branch from canonical main after M6-R1 state closure
→ machine contracts + Studio service integration
→ Browser Inspect piano-roll surface
→ service/UI tests
→ PR
→ exact-head full CI + prior evidence regressions
→ inspect M6-R2 evidence artifact
→ durable evidence/M6_R2_VALIDATION.md
→ exact evidence-bearing rerun
→ merge
→ state-only closure to M6-R3
```

## Scope control / 범위 통제

Do **not** claim or add in M6-R2:

- full DAW piano-roll parity;
- arbitrary polyphonic/every-part editing;
- arbitrary tempo-map editing;
- quantize/humanize/batch transforms unless separately contracted;
- waveform/destructive audio editing;
- automation lanes or mixer console;
- live MIDI recording;
- VST/AU/CLAP hosting;
- arbitrary DAW reverse mapping;
- collaborative editing;
- human-subject usability evidence;
- perceptual-quality superiority claims.

## Expected next after R2 / R2 이후 예상

If M6-R2 is validated:

```text
M6-R3 — Real-browser exact-note E2E + lock/conflict UX
M6-R4 — bounded interchange reconciliation for representable note edits
```

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
