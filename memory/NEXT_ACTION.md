# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M6-R3 — REAL-BROWSER EXACT-NOTE E2E + LOCK/CONFLICT UX / M6-R3 — 실제 Browser Exact-Note E2E + Lock/Conflict UX**

M6-R2 is `VALIDATED — BOUNDED BROWSER INTEGRATION`. The exact next task is to prove the already implemented Browser Studio piano-roll path through a real Chromium browser and to make authority conflicts observable and actionable without weakening the M6-R1/M6-R2 authority model.

M6-R2는 `VALIDATED — BOUNDED BROWSER INTEGRATION`입니다. 정확한 다음 작업은 이미 구현된 Browser Studio piano-roll 경로를 실제 Chromium browser에서 end-to-end로 증명하고, M6-R1/M6-R2 권한 모델을 약화하지 않으면서 authority conflict를 사용자에게 명확하게 노출·처리하는 것입니다.

## Canonical starting point / 공식 시작점

- M6-R2 implementation merge: `4fc186168a2c6d6b91ed0d842476f9fed9586ba6`
- Issue #57: **COMPLETED**
- PR #58: **MERGED**
- final evidence-bearing M6-R2 exact head: `546ce59f6264d36af18064e2b2f1b522a969dda1`
- final MUSICA CI: `34694194134` — **SUCCESS**
- final M6-R2 evidence: `34694193980` — **SUCCESS**
- final M6-R1 regression: `34694193939` — **SUCCESS**
- final M5-R3 regression: `34694193938` — **SUCCESS**
- final M5-R4 regression: `34694194059` — **SUCCESS**
- final M6-R2 artifact: `musica-m6-r2-piano-roll`
- final artifact ID: `10298037150`
- final artifact packaging digest: `sha256:8fcb32ca8dc7718199e5fb0092617967446509a3793b7d00585880fd1c042cc9`
- internal M6-R2 manifest SHA-256: `6e97d79b19248b03d2fe705223fb5f3c5de7ff95a2d80ef279e7fd86a8b27b7e`
- final artifact tree comparison against the strengthened pre-durable artifact: **59 files / 0 differences**
- durable evidence: `evidence/M6_R2_VALIDATION.md`

## Governing contracts / 지배 계약

Read and obey before implementation:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
4. `docs/M6_ACCEPTANCE.md`
5. `docs/M6_R1_RUNTIME.md`
6. `schemas/exact-note-material-v0.schema.json`
7. `schemas/note-edit-candidate-v0.schema.json`
8. `schemas/note-edit-authority-result-v0.schema.json`
9. `schemas/exact-note-lock-v0.schema.json`
10. `schemas/studio-note-view-v0.schema.json`
11. `src/musica/note_edit.py`
12. `src/musica/studio.py`
13. `src/musica/studio_http.py`
14. `src/musica/studio_web/index.html`
15. `src/musica/studio_web/app.js`
16. `src/musica/studio_web/app.css`
17. `evidence/M6_R1_VALIDATION.md`
18. `evidence/M6_R2_VALIDATION.md`
19. existing M4-R3 browser E2E harness and evidence

## Core invariant / 핵심 불변식

```text
Accepted exact-note Blueprint
→ deterministic Studio note view
→ real Browser Studio Inspect piano roll
→ user browser interaction / exact form input
→ typed NoteEditCandidate
→ M6-R1 source + lock + constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW — NOT ACCEPTED
→ visible/audible inspection
→ explicit Accept or Discard
→ existing M2 authority only
→ browser refresh/reopen
→ accepted exact-note state preserved
```

Forbidden:

```text
DOM/canvas/browser-local arrays → canonical project
pointer coordinates → canonical project without typed deterministic mapping
Music IR event mutation → canonical project
blocked conflict → pending Preview
edit gesture → implicit Accept
```

M6-R3 is an evidence/UX milestone over the validated R2 integration. It must not create a second note-edit engine, second project authority path, or browser-owned canonical state.

## Required M6-R3 implementation / 필수 구현

### 1. Real-browser exact-note happy-path E2E

Extend the existing Playwright/Chromium harness so a real browser proves the exact-note path rather than only the pre-M6 Browser Studio path.

At minimum the browser must:

1. open an exact-note-capable `.musica` project through the normal Studio flow;
2. enter Inspect and load the piano-roll projection from the service;
3. observe stable note IDs and accepted-state metadata;
4. select a note and produce at least one real note-edit Preview through browser controls;
5. observe `PREVIEW · NOT ACCEPTED` before acceptance;
6. prove the canonical accepted ref is unchanged before Accept;
7. explicitly Accept through the existing Studio path;
8. refresh/reopen and observe the accepted exact-note state unchanged;
9. separately prove Discard leaves accepted state unchanged.

### 2. Six-operation browser coverage

The real-browser suite must prove browser-accessible execution of the existing primitive vocabulary:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

This does not require every operation to be implemented as free-form drag. Numeric/button/keyboard controls remain valid where they map deterministically to the same typed operation contract.

Each operation must be attributable to a stable `operation_id` and stable `note_id + part_id` target where applicable.

### 3. Pointer/keyboard interaction discipline

Where pointer interaction exists, browser coordinates are interaction inputs only. Mapping must be deterministic and bounded before a typed candidate is submitted.

Required properties:

- no raw DOM position becomes canonical state;
- drag/move/resize, if exercised, resolves to exact bounded musical values before Preview;
- keyboard/numeric alternatives remain available for precision and accessibility;
- browser-side rounding/quantization policy, if any, must be explicit and tested rather than implicit.

M6-R3 must not add general quantize/humanize semantics unless separately contracted.

### 4. HARD-lock conflict UX

A real browser must encounter a stable-ID HARD note lock and prove:

- the attempted operation returns `BLOCKED`;
- conflict code `HARD_LOCK_VIOLATION` is visible;
- stable note identity is visible;
- rule ID and affected property are visible when supplied by authority result;
- no pending Preview is installed;
- accepted ref remains unchanged;
- Accept is unavailable or cannot commit the blocked edit.

The UX may explain the conflict but must not silently weaken/remove a HARD lock.

### 5. Stale-source conflict UX

A deterministic real-browser scenario must prove stale protection across the service/browser boundary.

Required outcome:

```text
BLOCKED / STALE_SOURCE
preview_installed = false
accepted ref unchanged
```

The UI must present enough context for the user to understand that the visible/edit source is no longer current. Recovery should reload/rebind to the current accepted note view; it must not silently rebase and accept the stale candidate.

### 6. Preview authority UX

For a valid edit, the real browser must make the authority state explicit:

- `PREVIEW · NOT ACCEPTED` visible before acceptance;
- changed stable note IDs / operation summary visible;
- Preview note state visually distinguishable from accepted note state;
- existing Preview audio path remains bounded and non-canonical;
- Accept and Discard remain explicit separate actions;
- no edit gesture alone advances the accepted project ref.

### 7. Legacy project browser behavior

A motif-only project without canonical exact-note material must still open normally in the real browser.

Prove:

- `exact_note_editing_available=false` is represented to the UI;
- no fabricated canonical notes appear;
- existing Direct/Shape/Inspect history/locks/export behavior remains usable;
- the UI does not suggest that Music IR-derived notes can be accepted as canonical exact-note material.

### 8. Real-browser security/local-first regression

Preserve and prove the M4/M6 boundaries:

- loopback-only Studio server;
- CSP-compatible packaged assets;
- same-origin JS/CSS only;
- no wildcard CORS authority;
- no upload endpoint introduced;
- no third-party CDN/framework dependency;
- no remote telemetry;
- bounded request bodies;
- workspace-confined project access;
- browser cannot mutate Music IR/project files directly.

## Required tests / 필수 테스트

At minimum add automated evidence for:

1. exact-note-capable project opens in Chromium and piano roll renders;
2. accepted note view displayed in browser matches service-bound project/revision/Blueprint hash;
3. stable note selection works without array-index authority;
4. INSERT can create a non-canonical browser Preview;
5. DELETE can create a non-canonical browser Preview;
6. MOVE can create a non-canonical browser Preview;
7. RESIZE can create a non-canonical browser Preview;
8. REPITCH can create a non-canonical browser Preview;
9. SET_VELOCITY can create a non-canonical browser Preview;
10. canonical ref remains unchanged before each Preview Accept;
11. explicit Accept advances exactly once through M2;
12. refresh/reopen preserves the accepted exact-note result;
13. Discard leaves accepted state unchanged;
14. HARD note lock is visibly `BLOCKED` with no Preview;
15. stale source is visibly `BLOCKED` with no Preview;
16. conflict UX exposes stable note/rule context where available;
17. legacy motif-only project exposes exact editing unavailable with no fabricated notes;
18. existing M4-R3 browser journey remains green;
19. Python 3.11 / 3.12 full suite remains green;
20. M5-R2 / M5-R3 / M5-R4 and M6-R1 / M6-R2 evidence regressions remain green.

## Canonical evidence target / 공식 근거 목표

M6-R3 should add a dedicated real-browser evidence workflow rather than treating screenshots alone as proof.

Recommended evidence package:

```text
artifacts/m6-r3-real-browser-note-e2e/
  manifest.json
  proof.json
  browser-actions.json
  source-note-view.json
  preview-note-view.json
  accepted-note-view.json
  reopened-note-view.json
  blocked-hard-lock.json
  blocked-stale-source.json
  browser-console.json
  screenshots/...        # supporting evidence only
```

The manifest must bind relevant source/project/revision/Blueprint hashes and SHA-256 each proof-bearing file. Screenshots may support UX evidence but machine-readable authority/result artifacts remain primary.

The evidence should prove at minimum:

```text
real_browser = Chromium/Playwright
all_six_operations_browser_exercised = true
accepted_ref_unchanged_before_accept = true
explicit_accept_required = true
hard_lock_blocked = true
stale_source_blocked = true
blocked_preview_installed = false
accepted_state_survives_refresh = true
legacy_has_no_fabricated_notes = true
browser_project_mutation_authorized = false
music_ir_mutation_authorized = false
```

## M6-R3 merge discipline / 병합 규율

```text
Issue
→ fresh implementation branch from canonical main after M6-R2 state closure
→ extend real-browser harness + bounded UX only
→ targeted browser tests
→ PR
→ exact-head full CI + M4/M5/M6 regressions
→ inspect M6-R3 real-browser evidence artifact
→ durable evidence/M6_R3_VALIDATION.md
→ exact evidence-bearing rerun
→ expected-head merge
→ Issue completed
→ state-only closure to M6-R4
```

## Scope control / 범위 통제

Do **not** claim or add in M6-R3:

- full professional DAW piano-roll parity;
- arbitrary polyphonic/every-part editing;
- arbitrary tempo-map editing;
- general quantize/humanize/batch transforms unless separately contracted;
- score engraving;
- waveform/destructive audio editing;
- automation lanes or mixer console;
- live MIDI recording;
- VST/AU/CLAP hosting;
- arbitrary DAW reverse mapping;
- cloud/collaborative editing;
- human-subject usability validation;
- perceptual or mastering superiority claims.

## Expected next after R3 / R3 이후 예상

If M6-R3 is validated:

```text
M6-R4 — bounded interchange reconciliation for representable exact-note edits
```

M6-R4 may then evaluate whether representable DAW/interchange note changes can be mapped into typed `NoteEditCandidate` objects under exact source/identity/lock proof. It must not retroactively rewrite M5-R3 evidence or grant external DAW state canonical authority.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
