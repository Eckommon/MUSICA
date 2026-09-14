# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M7-R2 — BROWSER STUDIO AUTOMATION LANE / INSPECT SURFACE**

M7-R1 is `VALIDATED — BOUNDED CORE RUNTIME`. The exact next mission is to expose the already-validated canonical automation authority through Browser Studio Inspect while keeping Browser state non-canonical.

## Canonical starting point / 공식 시작점

- M7-R1 Issue `#71` — **COMPLETED**
- M7-R1 PR `#72` — **MERGED**
- implementation merge/main: `877ed9b7e7f90101ffcdb6891bd75631807053e2`
- final evidence-bearing head: `abe1f9c92751e0cdde935b34f4a17f1e1fc20548`
- M7-R1 workflow `34795684053` — **SUCCESS**
- MUSICA CI `34795683991` — **SUCCESS**
- M7-R0 `34795684183` — **SUCCESS**
- M6-R4 `34795684200` — **SUCCESS**
- M6-R3 `34795683988` — **SUCCESS**
- M6-R2 `34795683981` — **SUCCESS**
- M6-R1 `34795684023` — **SUCCESS**
- M5-R3 `34795684054` — **SUCCESS**
- M5-R4 `34795683984` — **SUCCESS**
- final M7-R1 artifact ID `10330005742`
- packaging SHA-256 `178d86faf11bfd859b84fc0c60363a493f9ffa8530dab27567ccd0b2e03ea638`
- internal manifest SHA-256 `b21dfd8e6b7c61ceee8b5613f8c65bb4857209a050cffe92eb8cabe33232ed5e`
- pre-durable vs successor evidence: **15 files / 0 differences**
- durable evidence: `evidence/M7_R1_VALIDATION.md`

## R1 authority R2 must reuse / R2가 재사용해야 할 R1 권한

```text
canonical storage     = optional materials.automation
stable identity       = lane_id + point_id + parameter_id
canonical time        = quarter_note_beat
interpolation         = hold | linear
runtime primitives    = INSERT_POINT / DELETE_POINT / MOVE_POINT / SET_VALUE / SET_INTERPOLATION
candidate source      = project_id + revision_id + Blueprint SHA + automation-material SHA
candidate authority   = preview_only / non-canonical
result states         = READY_FOR_PREVIEW | BLOCKED
acceptance             = explicit existing M2 commit only
```

Browser code must not duplicate or weaken this authority.

## Required M7-R2 implementation / 필수 구현

### 1. Inspect projection

Add a bounded Automation section/lane surface to Browser Studio Inspect.

Required properties:

- projection originates from the accepted Blueprint's `materials.automation` only;
- legacy/no-automation project shows an explicit empty/no-automation state rather than inventing a lane;
- visible lane rows bind stable `lane_id`;
- visible control points bind stable `point_id`;
- labels show backend-independent `parameter_id`, scope/unit and explicit value/time;
- DOM ordering or canvas coordinate is never identity.

### 2. Bounded edit surface

R2 may expose exactly the R1 five point primitives through Browser controls:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
```

No lane create/delete, parameter reassignment, arbitrary spline editing, plug-in automation browser or free-form transform language.

### 3. Candidate construction

Every Browser edit must construct the same `automation-edit-candidate-v0` contract used by R1. Client-side code may gather input, but authority belongs to the server/runtime boundary.

At minimum bind:

```text
accepted project_id
accepted revision_id
accepted Blueprint SHA-256
accepted automation material SHA-256
stable lane_id / point_id
```

No client-generated array position may be substituted for stable identity.

### 4. Preview / Accept / Discard

Required UX state machine:

```text
accepted automation projection
→ edit gesture/form
→ typed candidate
→ server R1 authority
→ BLOCKED or READY_FOR_PREVIEW
```

For READY:

```text
Preview clearly marked NOT ACCEPTED
→ accepted project remains unchanged
→ explicit Accept advances via existing M2 authority
→ Discard restores accepted projection with no revision
```

For BLOCKED:

- no candidate Blueprint accepted;
- no hidden local acceptance;
- conflict code/reason shown;
- HARD lock conflict visually distinguishable;
- stale-source response forces refresh/reprojection rather than silent rebase.

### 5. Stable coordinate mapping

Browser visualization may map beat/value to pixels, but conversion must be explicit and reversible within the supported bounded UI.

Required invariant:

```text
DOM/canvas x,y
→ presentation only
stable lane_id + point_id + typed beat/value
→ candidate identity/data
```

Dragging a point changes beat/value, never point ID.

### 6. Accessibility and non-canvas fallback

Do not make the only editing path dependent on pointer geometry. Provide inspectable form/table controls for stable lane/point values so keyboard-driven editing and deterministic browser tests can use the same authority.

### 7. Browser/service API boundary

Prefer reusing existing Browser Studio service/Preview patterns from M4/M6. Do not create a parallel project store or client-only accepted state.

Potential minimal service operations:

```text
GET accepted automation projection
POST automation preview candidate
POST explicit accept existing preview/revision
POST discard/local preview clear
```

Exact routes should follow existing Studio conventions after code inspection.

### 8. Negative UX paths

At minimum surface and test:

- stale source;
- unknown lane/point;
- duplicate point ID;
- occupied beat;
- value outside declared range;
- HARD exact lock conflict;
- HARD presence lock deletion conflict;
- malformed/unsupported interpolation;
- legacy project with no automation lane.

### 9. No hidden renderer authority

R2 must not claim that moving an automation point audibly changes rendered output. Until a later lowering milestone proves it, Browser R2 edits only canonical project automation material.

## Required tests / 필수 테스트

At minimum prove:

1. existing Browser Studio still opens legacy project;
2. no-automation legacy project shows explicit empty automation state;
3. automation-capable project projects stable lane/point IDs;
4. parameter/scope/unit/time/value/interpolation are inspectable;
5. each five primitive Browser interaction constructs a correct typed candidate;
6. point drag preserves `point_id`;
7. Browser array/DOM order cannot change target identity;
8. valid edit gives Preview but accepted ref stays unchanged;
9. explicit Accept advances one M2 revision;
10. Discard leaves accepted ref unchanged;
11. HARD exact/presence conflicts are visible and non-previewable;
12. stale source is visible and not silently rebased;
13. range/time/identity errors are visible fail-closed states;
14. refresh after Accept shows accepted updated automation;
15. existing exact-note piano-roll behavior remains green;
16. M7-R1/R0 tests remain green;
17. Python 3.11/3.12 full suite remains green;
18. M6-R4/R3/R2/R1 and M5-R3/R4 regressions remain green.

## Evidence target / 공식 근거 목표

R2 dedicated evidence should capture machine-readable Browser/service proof and, if consistent with M6-R3 precedent, a real Chromium evidence artifact proving actual DOM interaction rather than only service-unit tests.

Target evidence:

```text
accepted source IDs/hashes
Browser projection snapshot
stable DOM identity mapping
five candidate constructions
READY Preview screenshot/state
BLOCKED HARD lock state
stale-source state
accepted ref before/after Preview
explicit Accept revision
Discard proof
real-browser execution metadata
manifest/hash bindings
```

## Scope control / 범위 통제

Do **not** add or claim in M7-R2:

- automation lowering into Music IR;
- audible automation rendering;
- plug-in/device parameter mapping or VST/AU/CLAP hosting;
- external DAW automation reconciliation;
- MIDI CC / OSC / real-time control;
- lane creation/deletion or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential interpolation;
- human-subject/perceptual superiority.

## Maximum intended R2 claim / 성공 시 최대 주장

> **Browser Studio Inspect can project and edit the already-validated canonical automation material through stable lane/point identities and the existing source-bound M7-R1 Preview/Accept authority, while Browser presentation state remains non-canonical.**

## Execution discipline / 실행 규율

```text
M7-R1 state closure
→ create M7-R2 Issue
→ fresh implementation branch from canonical closure main
→ inspect M4/M6 Browser service + real-browser evidence precedent
→ bounded automation Inspect projection/editing
→ service/browser tests
→ dedicated real-browser evidence
→ PR
→ exact-head full regressions
→ artifact inspection
→ durable M7_R2 validation
→ successor rerun
→ expected-head merge
→ Issue completed
→ state-only closure to next bounded mission
```

**Repository evidence remains authoritative over conversation/model memory.**
