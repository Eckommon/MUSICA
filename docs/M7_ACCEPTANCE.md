# M7-R0 Acceptance / M7-R0 수용 기준

**Milestone:** `M7-R0 — Canonical Automation & Continuous-Control Authority`  
**Class:** `CONTRACT/DESIGN ONLY`  
**Issue:** `#68`

## Required outcome / 필수 결과

R0 succeeds only if the repository ratifies a bounded, machine-checkable authority/data model for future canonical automation while preserving the rule that Browser, Music IR, renderer, plug-in and DAW state remain non-canonical.

## Required artifacts / 필수 산출물

- `docs/M7_AUTOMATION_AUTHORITY.md`
- `docs/M7_ACCEPTANCE.md`
- `schemas/automation-material-v0.schema.json`
- `schemas/automation-edit-candidate-v0.schema.json`
- `schemas/automation-authority-result-v0.schema.json`
- `schemas/automation-lock-v0.schema.json`
- `src/musica/automation_contracts.py`
- valid/invalid automation fixtures
- `tests/test_m7_r0_automation_contracts.py`
- dedicated M7-R0 CI
- `evidence/M7_R0_VALIDATION.md`

## Contract acceptance / 계약 수용 기준

The accepted v0 design must prove all of the following:

1. automation creative state is distinct from Music IR/renderer/DAW execution state;
2. stable `lane_id`, `point_id` and namespaced `parameter_id` are explicit;
3. v0 scope is `project | part` only; derived `track_id` is not canonical target identity;
4. time base is `quarter_note_beat` with origin `0.0`;
5. units are explicit and bounded;
6. `minimum < maximum` is executable cross-field validation;
7. point values are inside lane bounds;
8. `hold | linear` is the complete R0 interpolation vocabulary;
9. lanes and points use deterministic canonical order;
10. duplicate lane IDs, duplicate point IDs, duplicate beats and duplicate target signatures fail closed;
11. point-edit operations require stable point identity;
12. edit candidates are source-bound and `preview_only=true`;
13. authority result distinguishes `READY_FOR_PREVIEW` and `BLOCKED` and never authorizes project/Music-IR mutation;
14. automation locks are stable-ID aware and exact/range/presence payloads are structurally disjoint;
15. invalid/unknown source or identity classes have typed fail-closed result vocabulary;
16. legacy projects are not migrated and no automation is fabricated from derived state.

## Required valid fixtures / 필수 유효 fixture

At minimum:

- one canonical automation material containing a project-scoped normalized lane and a part-scoped Hz lane;
- one source-bound edit candidate;
- one HARD automation lock;
- one `READY_FOR_PREVIEW` authority result;
- one `BLOCKED / HARD_LOCK_VIOLATION` authority result.

## Required negative fixtures/tests / 필수 음성 fixture·테스트

At minimum fail closed on:

- `track` scope;
- project scope with non-null owner;
- point operation without `point_id`;
- duplicate lane ID;
- duplicate point ID;
- duplicate beat in one lane;
- duplicate target signature;
- non-canonical lane ordering;
- non-canonical point ordering;
- `minimum >= maximum`;
- point value outside declared range;
- malformed parameter namespace;
- unsupported interpolation;
- automation lock with contradictory mode payload;
- range lock with `minimum > maximum`;
- lock referencing an unknown lane/point;
- invalid authority result where READY carries conflicts or BLOCKED permits Preview.

## Regression gate / 회귀 gate

Before promotion, exact-head evidence must show:

1. dedicated M7-R0 contract workflow — SUCCESS;
2. MUSICA CI — SUCCESS;
3. M6-R4 Interchange Note Reconciliation — SUCCESS;
4. M6-R3 Real-Browser Exact-Note Evidence — SUCCESS;
5. M6-R2 Piano-Roll Evidence — SUCCESS;
6. M6-R1 Exact-Note Edit Evidence — SUCCESS;
7. M5-R3 DAWproject Evidence — SUCCESS;
8. M5-R4 Paired Audio Evidence — SUCCESS.

## Promotion discipline / 승격 규율

```text
Issue #68
→ fresh design branch
→ docs + schemas + executable contract checker
→ fixtures + tests
→ dedicated CI
→ PR
→ exact-head regression gates
→ durable evidence/M7_R0_VALIDATION.md
→ evidence-bearing successor rerun
→ expected-head merge
→ Issue completed
→ state-only handoff to bounded runtime milestone
```

## Maximum allowed claim / 최대 허용 주장

If all gates pass, the maximum claim is:

> **MUSICA has a validated contract/design authority model for explicit continuous automation with stable backend-independent lane/point/parameter identity, source-bound non-canonical edit candidates, deterministic bounded curve semantics, and fail-closed lock/result contracts. Runtime automation editing, accepted-project integration, rendering and external automation reconciliation remain unvalidated.**

Repository evidence remains authoritative over conversation/model memory.
