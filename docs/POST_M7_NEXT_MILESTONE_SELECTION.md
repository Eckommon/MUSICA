# Post-M7 Next-Milestone Selection / Post-M7 다음 마일스톤 선정

## Status / 상태

**RATIFIED TARGET — ACCEPTED REVISION A/B COMPARE & DECISION SURFACE v0**

This record closes the planning gate opened after M7-R6. It selects exactly one bounded successor capability from repository evidence. It does **not** claim that the selected capability is implemented or validated.

- canonical review base: `2bfc8ffbe707c06f016d820cc47d901ed862be92`
- selected implementation Issue: `#89`
- predecessor: `M7-R6 — VALIDATED — BOUNDED TRUTHFUL AUDITION INSPECTION`
- selected capability: **Accepted Revision A/B Compare & Decision Surface v0**
- milestone numbering: **no inferred `M7-R7` or `M8`**

## 1. Product gap / 제품 공백

The canonical product loop is:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

M4-R3 already validates in real Chromium:

```text
natural-language create
→ audition
→ semantic Preview
→ explicit Accept
→ branch/history/export
→ restart/reopen
```

Therefore another generic natural-language end-to-end milestone would duplicate validated work.

The explicit unresolved product-loop gap is **Compare** at the accepted-revision level: Browser Studio cannot yet select two immutable accepted revisions, show their exact structured Blueprint difference, and audition their exact revision-specific media side by side.

## 2. Repository readiness / 저장소 준비도

The selected capability mostly reuses validated infrastructure:

- `MusicaProject.read_revision_record(revision_id)` reads immutable accepted revision records;
- `MusicaProject.read_revision(revision_id)` validates the Blueprint contract and bound SHA-256;
- `structured_diff(before, after)` returns deterministic JSON-Pointer-oriented change lists;
- accepted artifacts are revision-bound with immutable manifests and SHA-256 identities;
- Studio already uses artifact-first / deterministic-render-fallback media for current accepted HEAD;
- Browser Studio already serves same-origin audition media;
- real-Chromium product evidence infrastructure already exists.

The concrete gap is narrow: Studio's current public media path resolves only pending Preview or current accepted HEAD. Its internal artifact helper already accepts an arbitrary revision ID, but no bounded public arbitrary-accepted-revision comparison/media surface exists.

## 3. Serious candidate comparison / 주요 후보 비교

### A. Accepted Revision A/B Compare & Decision Surface — **SELECTED**

- **User leverage:** closes the explicit `Compare` stage and turns version history into a real decision workflow.
- **Dependency readiness:** high; M2 revision authority, structured diff, artifacts, rendering, Studio media and Browser E2E already exist.
- **Authority risk:** low if implemented as a read-only projection with no reverse promotion.
- **Evidence feasibility:** high and deterministic; no network or secret is required.
- **Regression surface:** bounded; mostly additive read-only projection/media/UI work.
- **Sequencing value:** directly closes a canonical product-loop gap before expanding adjacent technical surfaces.

### B. Live OpenAI Provider Evidence — **DEFERRED, NOT REJECTED**

- M3-R2 already implements a live-ready HTTPS Responses transport behind the provider-neutral authority boundary.
- M3-R2 explicitly classifies a future authorized live smoke separately as `LIVE_PROVIDER_EVIDENCE`.
- Live evidence depends on external credentials, endpoint/model behavior and network availability.
- It would validate real provider execution but would not add the missing Compare workflow.
- It is not a prerequisite for accepted-revision comparison.

## 4. Adjacent domains reviewed and deferred / 인접 영역 보류

Not selected now:

- additional automation renderer mappings;
- lane creation/deletion, tempo or curve-family expansion;
- automation-aware DAW reconciliation;
- real-time MIDI/OSC control;
- packaging/installer/cloud collaboration.

None has stronger repository evidence of blocking the canonical product loop than accepted-revision Compare, and several would enlarge derived/external authority surfaces first.

## 5. Ratified mission / 비준 미션

> **Given two immutable accepted revisions in the same MUSICA project, expose a read-only, provenance-bearing comparison that shows deterministic Blueprint differences and exact A/B audition media, while leaving all creative preference and canonical navigation/acceptance decisions to the user.**

Implementation authority is Issue `#89`.

## 6. Authority model / 권한 모델

Allowed:

```text
accepted revision A ─┐
                     ├→ read-only comparison projection → Browser inspection/audition
accepted revision B ─┘
```

Forbidden:

```text
Browser state / audio / comparison result / score
    ─X→ canonical Blueprint mutation
```

Comparison is a truthful projection over already accepted authority, not a new creative authority.

## 7. Required comparison semantics / 필수 비교 의미론

The v0 contract must expose:

- explicit revision A and B IDs;
- explicit diff direction `A_TO_B`;
- deterministic `structured_diff(A, B)`;
- revision-record identity and Blueprint SHA-256 for both sides;
- current branch/head identity;
- exact media provenance for both sides;
- no hidden acceptance or mutation.

The contract must contain **no creative `winner`, `score`, `better`, `preference_probability`, or equivalent field**.

M5-R4 remains semantically separate: it compares renderers for the **same Music IR**. It must not be reused to rank different musical revisions.

## 8. Media truth rule / 미디어 진실성 규칙

For each requested accepted revision and media kind:

```text
exact bound artifact, if present
else
explicit deterministic fallback render from that exact accepted Blueprint
```

Every result must expose:

- revision ID;
- provenance mode: `bound_artifact` or `deterministic_fallback`;
- SHA-256 of exact served bytes;
- media type;
- explicit failure/availability state.

Fallback media remains derived and disposable. It must not silently create or alter the immutable artifact manifest.

## 9. Same-revision policy / 동일 revision 정책

v0 will support A == B as a truthful identity case:

```text
A revision == B revision
diff = []
media SHA A == media SHA B for the same provenance path
head unchanged
```

This keeps the comparison contract total over any two existing accepted revision IDs and provides a useful deterministic negative/identity case.

## 10. Expected implementation surface / 예상 구현 표면

Expected bounded additions:

```text
schemas/studio-revision-compare-v0.schema.json
src/musica/studio_compare.py
src/musica/studio.py
src/musica/studio_http.py
src/musica/studio_web/revision_compare.js
src/musica/studio_web/revision_compare.css
src/musica/studio_web/index.html
tests/test_post_m7_revision_compare.py
e2e/test_post_m7_revision_compare_browser.py
.github/workflows/post-m7-revision-compare-evidence.yml
evidence/POST_M7_REVISION_COMPARE_VALIDATION.md
```

Exact file names may change for concrete repository reasons. Authority semantics may not drift.

## 11. Required test matrix / 필수 테스트 행렬

### Trusted comparison

- valid A/B accepted revisions → exact deterministic diff;
- explicit A→B direction and consistent reversal;
- A == B → zero-diff identity result;
- unknown revision → fail closed;
- tampered accepted revision → existing M2 integrity failure;
- compare leaves branch, HEAD and accepted state unchanged.

### Media

- bound/bound exact-byte and SHA proof;
- fallback/fallback deterministic exact-revision proof;
- mixed bound/fallback truthful provenance;
- fallback never silently becomes canonical bound media;
- arbitrary-revision media route accepts only existing accepted revisions and remains workspace-confined.

### Browser

- history supplies selectable A/B accepted revisions;
- visible Compare action loads exact requested revisions;
- independent A/B audio controls;
- revision/provenance identity and structured changes are visible;
- opening, playing and comparing do not move HEAD;
- refresh/reopen preserves canonical project state;
- console/page/request failures are explicitly accounted for.

### Regression

- all permanent M0→M7-R6 workflows remain green;
- M5-R4 same-Music-IR renderer comparison semantics remain unchanged.

## 12. Promotion criteria / 승격 기준

Issue `#89` may be promoted only after:

1. machine-valid compare contract;
2. deterministic service/unit evidence;
3. exact bound/fallback media SHA proof;
4. real-Chromium A/B workflow evidence;
5. explicit pre/post HEAD non-mutation proof;
6. permanent regression set success on exact evidence-bearing head;
7. durable validation record;
8. expected-head implementation merge;
9. separate state-only closure.

## 13. Explicit non-goals / 명시적 비목표

- no system-selected creative winner;
- no creative quality/preference score;
- no perceptual-superiority or human-subject preference claim;
- no cross-revision use of M5-R4 scoring;
- no implicit Accept or automatic branch/head movement;
- no merge/rebase/cherry-pick semantics;
- no new automation renderer family;
- no live OpenAI requirement;
- no DAW automation reconciliation;
- no destructive waveform editing;
- no cloud/multi-user comparison.

## 14. Maximum intended claim / 최대 의도 주장

> **MUSICA can truthfully compare two immutable accepted creative revisions by showing their exact structured Blueprint differences and revision-bound/fallback audition media side by side, while leaving creative preference and any canonical navigation/acceptance decision to the user.**

This is a **target claim only** until Issue `#89` is implemented, independently evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**