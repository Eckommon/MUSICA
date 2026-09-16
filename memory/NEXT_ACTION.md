# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**ISSUE #89 — ACCEPTED REVISION A/B COMPARE & DECISION SURFACE v0**

The post-M7 closure review has selected exactly one bounded successor capability. Do not infer `M7-R7` or `M8`; the selected mission is identified by its descriptive product capability and Issue `#89` until repository governance explicitly decides otherwise.

M7-R6 remains `VALIDATED — BOUNDED TRUTHFUL AUDITION INSPECTION`. Issue `#89` is **RATIFIED FOR IMPLEMENTATION, NOT YET VALIDATED**.

## Canonical starting point / 공식 시작점

- predecessor canonical main: `2bfc8ffbe707c06f016d820cc47d901ed862be92`
- M7-R6 Issue `#86` — **COMPLETED**
- M7-R6 implementation PR `#87` — **MERGED**
- M7-R6 state closure PR `#88` — **MERGED**
- selected successor Issue `#89` — **OPEN**
- selection record: `docs/POST_M7_NEXT_MILESTONE_SELECTION.md`

## Why this mission / 선정 이유

The canonical product thesis defines:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

M4-R3 already validates natural-language create → audition → semantic Preview → explicit Accept → branch/history/export → restart/reopen in real Chromium. A generic natural-language end-to-end milestone would duplicate validated work.

M2 already validates arbitrary accepted revision reads, immutable revision records, deterministic Blueprint diffs and revision-bound artifacts. Studio already supports artifact-first / deterministic-render-fallback media for the accepted HEAD. The remaining user-level gap is therefore a truthful **accepted-revision Compare** surface.

Live OpenAI execution remains a valid later `LIVE_PROVIDER_EVIDENCE` mission, but it is not selected now: M3-R2 already implements the live-ready provider boundary, while the live smoke is externally dependent and does not close the explicit Compare stage.

## Ratified mission / 비준 미션

Given two immutable accepted revisions in the same MUSICA project:

```text
accepted revision A + accepted revision B
→ validated revision records + Blueprint SHA identities
→ deterministic structured_diff(A, B)
→ exact per-revision media provenance
   ├─ bound artifact when present
   └─ explicit deterministic fallback render otherwise
→ read-only Browser A/B comparison
→ independent A/B audition
→ user-controlled decision/navigation only
```

Comparison itself must not mutate accepted authority.

## Exact implementation order / 정확한 구현 순서

Proceed in this order unless repository evidence forces a narrower correction:

1. **Contract first**
   - add `studio-revision-compare-v0` schema;
   - encode A/B identities, `A_TO_B` direction, revision/Blueprint hashes, structured diff, media provenance and current HEAD identity;
   - prohibit winner/score/preference semantics by schema and tests.

2. **Trusted read-only comparison projection**
   - add a dedicated comparison surface/module;
   - resolve exactly two existing accepted revision IDs;
   - call existing M2 revision readers and `structured_diff()`;
   - verify project integrity before exposing comparison data;
   - support A == B as a zero-diff identity case.

3. **Arbitrary accepted-revision media**
   - generalize the current accepted-media helper narrowly from HEAD-only to an explicit accepted `revision_id`;
   - prefer exact bound artifacts;
   - otherwise render deterministically from the exact accepted Blueprint;
   - label provenance as `bound_artifact` or `deterministic_fallback`;
   - return SHA-256 of the exact served bytes;
   - never persist fallback media as canonical bound artifact.

4. **Read-only HTTP routes**
   - add bounded same-origin compare projection route;
   - add arbitrary accepted-revision WAV/MIDI retrieval route;
   - reject unknown/unaccepted/corrupt revision state fail-closed;
   - preserve loopback/workspace confinement.

5. **Browser Compare surface**
   - expose accepted revision history as A/B selectors;
   - visible Compare action;
   - independent A/B audio controls;
   - visible revision IDs, Blueprint/provenance hashes and structured diff;
   - no automatic winner, score, Accept or branch movement.

6. **Deterministic tests**
   - valid A/B and reversed direction;
   - A == B zero-diff case;
   - bound/bound, fallback/fallback and mixed media cases;
   - unknown/tampered revision failures;
   - compare/media access leaves HEAD and accepted state unchanged;
   - contract contains no creative ranking semantics;
   - M5-R4 comparison semantics unchanged.

7. **Real-browser evidence**
   - actual Chromium A/B selection and audition;
   - exact requested revision IDs in media requests;
   - structured diff visible;
   - pre/post HEAD identical;
   - refresh/reopen preserves canonical state;
   - console/page/request failure accounting.

8. **Permanent CI / evidence package**
   - dedicated evidence workflow;
   - all existing permanent M0→M7-R6 regressions remain green;
   - deterministic evidence manifest and exact hashes;
   - durable validation record only after exact-head success.

9. **Promotion**
   - expected-head implementation merge;
   - close Issue `#89` only after implementation/evidence merge;
   - separate state-only closure updates README/current state/next action.

## Authority invariant / 권한 불변식

Allowed:

```text
accepted revisions
→ read-only compare projection
→ Browser inspection / audition
→ explicit user navigation through existing project authority
```

Forbidden:

```text
comparison result → canonical mutation
Browser selection → implicit Accept
A/B audio → inferred Blueprint
metric → creative winner
M5-R4 same-IR renderer comparator → cross-revision preference score
```

## Media truth rule / 미디어 진실성 규칙

For each side and media kind:

```text
bound artifact exists
    → serve exact bound bytes + exact SHA-256 + bound_artifact provenance
else
    → deterministic render from exact accepted Blueprint
       + exact served SHA-256 + deterministic_fallback provenance
```

A fallback render is derived and disposable. It must not rewrite the immutable artifact record.

## Required evidence / 필수 근거

Promotion requires all of:

- machine-valid comparison contract;
- deterministic A/B structured diff proof;
- exact revision-record/Blueprint hash provenance;
- exact bound/fallback WAV/MIDI SHA proof;
- no-HEAD-mutation proof before/after compare and audition;
- real-Chromium A/B workflow evidence;
- full permanent regression set success on exact evidence-bearing head;
- durable evidence document;
- expected-head merge.

## Explicit non-goals / 명시적 비목표

Do not expand Issue `#89` into:

- creative winner/ranking/preference scoring;
- human-subject perceptual superiority claims;
- M5-R4 cross-revision audio scoring;
- revision merge/rebase/cherry-pick semantics;
- implicit branch-head movement;
- additional automation renderer mappings;
- live OpenAI provider execution;
- DAW automation reconciliation;
- real-time MIDI/OSC;
- destructive waveform editing;
- cloud/multi-user comparison.

## Deferred mission / 보류 미션

`LIVE_PROVIDER_EVIDENCE` remains deferred and separate. A future authorized live smoke must be recorded independently and must not reinterpret M3-R2's offline adapter evidence.

## Maximum intended outcome / 최대 의도 결과

> **MUSICA can truthfully compare two immutable accepted creative revisions by showing their exact structured Blueprint differences and revision-bound/fallback audition media side by side, while leaving creative preference and any canonical navigation/acceptance decision to the user.**

This remains a **target claim until Issue #89 is implemented, independently evidenced, merged and state-closed**.

**Repository evidence remains authoritative over conversation/model memory.**