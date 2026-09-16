# Post-M7 Next-Milestone Selection / Post-M7 다음 마일스톤 선정

## Status / 상태

**RATIFICATION PROPOSAL — ACCEPTED REVISION A/B COMPARE & DECISION SURFACE v0**

This record closes the planning gate opened after M7-R6. It selects exactly one bounded successor capability from repository evidence. It does **not** claim that the selected capability is implemented or validated.

이 기록은 M7-R6 이후 열린 planning gate를 종결하기 위한 선정 기록입니다. 저장소 근거를 바탕으로 정확히 하나의 제한된 후속 capability를 선정하며, 해당 capability가 구현·검증되었다고 주장하지 않습니다.

- canonical review base: `2bfc8ffbe707c06f016d820cc47d901ed862be92`
- selected implementation Issue: `#89`
- predecessor: `M7-R6 — VALIDATED — BOUNDED TRUTHFUL AUDITION INSPECTION`

## 1. Product gap / 제품 공백

The canonical product loop is:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

M4-R3 already validates, in real Chromium, natural-language create, audition, semantic Preview, explicit Accept, branch/history/export and restart/reopen. Rebuilding a generic natural-language end-to-end workflow would therefore duplicate a validated capability.

The remaining explicit loop gap is **Compare** at the accepted-revision product level. MUSICA already supports immutable revisions and branches, but Browser Studio does not yet provide a bounded surface where a user can select two accepted revisions, inspect their exact structured difference and audition the exact revision-specific media side by side.

## 2. Repository readiness finding / 저장소 준비도 발견

The selected milestone is enabled mostly by already validated infrastructure:

- `MusicaProject.read_revision_record(revision_id)` reads an immutable accepted revision record;
- `MusicaProject.read_revision(revision_id)` validates the Blueprint contract and its bound SHA-256;
- `structured_diff(before, after)` already provides deterministic JSON-Pointer-oriented Blueprint differences;
- accepted artifacts are bound under exact revision IDs with immutable manifests and SHA-256 identities;
- Studio already has a bounded artifact-first / deterministic-render-fallback media pattern for the current accepted HEAD;
- Browser Studio already serves same-origin audition media and has real-Chromium acceptance evidence.

The exact implementation gap is narrower than the product gap: Studio's public media path currently resolves only the pending Preview or current accepted HEAD. Its internal artifact helper already accepts an arbitrary revision ID, but there is no safe public arbitrary-accepted-revision projection/media route and no A/B Browser surface.

## 3. Serious candidate comparison / 주요 후보 비교

### Candidate A — Accepted Revision A/B Compare & Decision Surface

**User leverage**

Closes the explicit `Compare` stage and makes versionable music usable as a decision workflow rather than only as stored history.

**Dependency readiness**

High. Immutable revision reads, structured diff, revision artifacts, deterministic rendering, Studio media delivery and Browser E2E are already validated.

**Authority risk**

Low when implemented as a read-only projection. Comparison must never promote Browser/audio state or a computed preference back into Blueprint authority.

**Evidence feasibility**

High and deterministic. Unit/service/browser tests can prove exact revision IDs, hashes, media provenance, diff direction and no HEAD mutation without network or secrets.

**Regression surface**

Bounded. Additive comparison projection + read-only media routes + Browser panel, with narrow extensions to existing Studio media helpers.

**Strategic sequencing**

Strong. It completes the product loop's missing decision step and provides a reusable revision-inspection surface for later AI-assisted alternatives without giving AI acceptance authority.

### Candidate B — Live OpenAI Provider Evidence

**User leverage**

Would prove that the existing provider adapter can complete at least one authorized real network exchange, but it would not by itself add the missing Compare product workflow.

**Dependency readiness**

Technically high. M3-R2 already implements a live-ready HTTPS Responses transport behind the provider-neutral authority boundary.

**Authority risk**

Low at the canonical layer because the M3 boundary is already fail-closed, but live evidence introduces operational dependency on external credentials, endpoint behavior and model availability.

**Evidence feasibility**

Lower determinism than Candidate A. The repository explicitly requires any future live smoke to be separately recorded as `LIVE_PROVIDER_EVIDENCE`; network/model responses cannot serve as byte-reproducible permanent regression evidence.

**Regression surface**

Small in code but externally dependent in evidence operation.

**Strategic sequencing**

Useful later, but not prerequisite to the accepted-revision Compare workflow. M4 product flows already operate through the validated fixture/provider-neutral path.

## 4. Adjacent domains reviewed and deferred / 인접 영역 검토 및 보류

The closure review also preserves, but does not select:

- second/additional automation renderer mappings;
- lane creation/deletion, tempo or curve-family expansion;
- automation-aware DAW reconciliation;
- real-time MIDI/OSC control;
- packaging/installer/cloud collaboration work.

None currently has stronger repository evidence of blocking the canonical product loop than accepted-revision Compare. Several would also enlarge derived execution or external-system authority boundaries before a direct product-loop gap is closed.

## 5. Decision / 결정

> **SELECT — Accepted Revision A/B Compare & Decision Surface v0**

Implementation authority is Issue `#89`.

The selection does **not** assign an artificial `M7-R7` or `M8` number. Numbering may be ratified only if a later repository-level program decision requires it.

`LIVE_PROVIDER_EVIDENCE` remains explicitly deferred rather than rejected.

## 6. Selected mission statement / 선정 미션

> Given two immutable accepted revisions in the same MUSICA project, expose a read-only, provenance-bearing comparison that shows deterministic Blueprint differences and exact A/B audition media, while leaving all creative preference and canonical navigation/acceptance decisions to the user.

## 7. Authority model / 권한 모델

Allowed direction:

```text
accepted revision A ─┐
                     ├→ read-only comparison projection → Browser inspection/audition
accepted revision B ─┘
```

Forbidden reverse direction:

```text
Browser state / audio / comparison result / score
    ─X→ canonical Blueprint mutation
```

Comparison is not a new creative authority. It is a truthful projection over already accepted authority.

## 8. Media semantics / 미디어 의미론

For each requested accepted revision and each supported media kind:

```text
exact bound artifact, if present
else
explicit deterministic fallback render from that exact accepted Blueprint
```

Every served media result must expose:

- revision ID;
- provenance mode: `bound_artifact` or `deterministic_fallback`;
- SHA-256 of exact served bytes;
- media type;
- availability/failure state.

Fallback media remains derived and non-canonical. It must not silently create or alter the revision's immutable artifact manifest.

## 9. Comparison semantics / 비교 의미론

Required:

- explicit A and B revision IDs;
- explicit diff direction `A_TO_B`;
- deterministic `structured_diff(A, B)`;
- revision record and Blueprint hash provenance;
- independent A/B WAV audition;
- MIDI retrieval for both sides where supported;
- current branch/head identity shown and proven unchanged;
- zero hidden acceptance.

The contract must contain **no creative `winner`, `score`, `better`, `preference_probability`, or equivalent field**.

M5-R4 remains semantically separate: it compares renderers for the **same Music IR**. It must not be repurposed to rank different accepted musical revisions.

## 10. Same-revision policy / 동일 revision 정책

v0 should **support** A == B as a truthful zero-diff comparison rather than fail solely because the IDs match. This gives a deterministic identity case and makes the contract total over any two existing accepted revision IDs.

Expected result:

```text
A revision == B revision
diff = []
media SHA A == media SHA B for the same provenance path
head unchanged
```

## 11. Expected implementation surface / 예상 구현 표면

Bounded expected additions:

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

File naming may change only for a concrete repository reason. Authority semantics may not drift.

## 12. Required test matrix / 필수 테스트 행렬

### Trusted core / service

- valid A/B accepted revisions produce exact deterministic diff;
- A→B direction is explicit and reversal behaves consistently;
- A == B returns a zero-diff identity comparison;
- unknown revision fails closed;
- tampered accepted revision fails through M2 integrity checks;
- comparison does not mutate current branch, HEAD, accepted revisions or acceptance audit state.

### Media

- bound/bound pair returns exact bound bytes and hashes;
- fallback/fallback pair returns deterministic exact-revision renders and labels them fallback;
- mixed bound/fallback pair remains truthful;
- no fallback render is silently persisted as canonical bound artifact;
- arbitrary-revision media route serves only accepted project revisions and remains workspace-confined.

### Contract truthfulness

- no winner/ranking/preference field exists;
- revision-record/Blueprint hashes are explicit;
- media provenance is explicit;
- failures are structured and fail closed.

### Browser

- history supplies selectable accepted A/B revisions;
- visible Compare action loads exact requested revisions;
- A and B have independent audio controls;
- structured change list is visible;
- revision/provenance identity is visible;
- opening/playing/comparing does not move HEAD;
- refresh/reopen preserves canonical project state;
- no console/page errors beyond narrowly documented expected media abort behavior.

### Regression

All permanent M0→M7-R6 workflows remain green. M5-R4 same-Music-IR comparison meaning remains unchanged.

## 13. Promotion criteria / 승격 기준

Implementation may be promoted only after:

1. machine-valid compare contract;
2. unit/service deterministic evidence;
3. exact bound/fallback media SHA proof;
4. real-Chromium A/B evidence;
5. explicit pre/post HEAD non-mutation proof;
6. permanent regression set succeeds on exact evidence-bearing head;
7. durable validation record is committed;
8. expected-head merge succeeds;
9. a separate state-only closure records the final canonical status.

## 14. Explicit non-goals / 명시적 비목표

- no system-selected creative winner;
- no perceptual-superiority or human-preference claim;
- no cross-revision use of M5-R4 scoring;
- no implicit Accept or branch-head movement;
- no revision merge/rebase/cherry-pick system;
- no new renderer automation family;
- no live OpenAI dependency;
- no DAW automation reconciliation;
- no destructive waveform editing;
- no cloud/multi-user comparison.

## 15. Maximum intended claim / 최대 의도 주장

> **MUSICA can truthfully compare two immutable accepted creative revisions by showing their exact structured Blueprint differences and revision-bound/fallback audition media side by side, while leaving creative preference and any canonical navigation/acceptance decision to the user.**

Until implementation evidence is promoted, this sentence is a **target claim, not a validated claim**.

**Repository evidence remains authoritative over conversation/model memory.**