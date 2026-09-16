# Post-M7 Validation — Accepted Revision A/B Compare & Human Decision Surface v0

Status: **VALIDATED — BOUNDED ACCEPTED REVISION A/B COMPARE & HUMAN DECISION SURFACE**

This validation is intentionally bounded. Repository evidence is authoritative over conversation/model memory.

## 1. Validated claim

> MUSICA can compare two immutable accepted revisions without changing canonical project authority, expose an exact deterministic `A_TO_B` structured Blueprint diff, bind each side to verified revision/Blueprint/media provenance, audition revision-specific WAV/MIDI in the Browser, and let the human make a Browser-local A/B choice that has no server-side Accept, checkout, ranking, or reverse-promotion authority.

The validated user loop is therefore extended from the already validated creation/editing/audition path to a bounded Compare decision surface:

```text
accepted revision A + accepted revision B
→ verified immutable revision/Blueprint provenance
→ deterministic structured_diff(A, B)
→ exact A/B WAV + MIDI provenance
→ read-only localhost HTTP projection
→ independent Browser A/B audition
→ Browser-local human Choose A / Choose B
→ no canonical mutation
```

This milestone does **not** authorize MUSICA to decide which musical revision is better.

## 2. Authority boundary

The comparison contract explicitly preserves:

```text
canonical                       = false
browser_mutation_authorized     = false
project_mutation_authorized     = false
reverse_promotion_authorized    = false
creative_ranking_authorized     = false
implicit_accept_authorized      = false
```

No `winner`, `score`, `better`, or `preference_probability` field is admitted by the validated comparison projection.

The Browser-local `Choose A` / `Choose B` state is presentation/decision state only. It does not:

- move `refs/HEAD`;
- checkout a branch;
- create or Accept a revision;
- write a project record;
- alter revision history;
- call a preference/ranking model;
- reuse the M5-R4 renderer comparator as a cross-revision music-quality score.

M5-R4 remains limited to objective comparison of renders derived from the same Music IR and is not repurposed here.

## 3. Exact lineage

- Issue: `#89`
- implementation PR: `#91`
- branch: `feature/issue-89-accepted-revision-ab-compare-v0`
- canonical base/main: `bc656ef8cdc345df6a2504d5db8b67f336721670`
- exact pre-durable evidence head: `b22e41f690606aeedcffa11ef2ec5e915b34551d`

The implementation establishes a dedicated versioned schema and read-only projection rather than changing M2 project authority or retroactively changing earlier contracts.

Principal implementation/evidence paths before this durable record include:

```text
.github/workflows/post-m7-revision-compare-evidence.yml
e2e/test_post_m7_revision_compare_browser.py
e2e/test_post_m7_revision_compare_choice_browser.py
schemas/studio-revision-compare-v0.schema.json
src/musica/post_m7_revision_compare_demo.py
src/musica/post_m7_revision_compare_e2e.py
src/musica/studio_compare.py
src/musica/studio_http.py
src/musica/studio_web/revision_compare.css
src/musica/studio_web/revision_compare.js
tests/test_post_m7_revision_compare.py
tests/test_post_m7_revision_compare_provenance.py
```

The durable validation-record successor head must differ from the pre-durable head only by this validation record and must itself reproduce the complete permanent workflow set before expected-head merge.

## 4. Pre-durable exact-head permanent gates — 15/15 SUCCESS

Exact head: `b22e41f690606aeedcffa11ef2ec5e915b34551d`

| Workflow | Run | Result |
|---|---:|---|
| MUSICA CI | `35063187800` | SUCCESS |
| Post-M7 Accepted Revision Compare Evidence | `35063187699` | SUCCESS |
| M7-R6 Truthful Audition Inspection Evidence | `35063187774` | SUCCESS |
| M7-R5 Studio Audible Automation Evidence | `35063187778` | SUCCESS |
| M7-R4 Audible Automation Evidence | `35063187630` | SUCCESS |
| M7-R3 Automation Lowering Evidence | `35063187796` | SUCCESS |
| M7-R2 Real-Browser Automation Evidence | `35063187820` | SUCCESS |
| M7-R1 Automation Runtime Evidence | `35063187598` | SUCCESS |
| M7-R0 Automation Contract Evidence | `35063187675` | SUCCESS |
| M6-R4 Interchange Note Reconciliation | `35063187643` | SUCCESS |
| M6-R3 Real-Browser Exact-Note Evidence | `35063187686` | SUCCESS |
| M6-R2 Piano-Roll Evidence | `35063187764` | SUCCESS |
| M6-R1 Exact-Note Edit Evidence | `35063187748` | SUCCESS |
| M5-R4 Paired Audio Evidence | `35063187751` | SUCCESS |
| M5-R3 DAWproject Evidence | `35063187823` | SUCCESS |

The dedicated Compare workflow successfully completed all of the following:

1. accepted-revision comparison regression suite;
2. provenance regression suite;
3. real-Chromium A/B comparison lifecycle;
4. real-Chromium Browser-local human `Choose A` / `Choose B` isolation test;
5. deterministic evidence A generation;
6. deterministic evidence B generation;
7. `diff -qr` byte-tree reproducibility proof between deterministic A and B;
8. evidence artifact upload.

## 5. Pre-durable Compare artifact integrity

Dedicated workflow run: `35063187699`

Artifact:

- artifact ID: `10433182942`
- artifact name: `musica-post-m7-accepted-revision-compare-evidence`
- ZIP SHA-256: `43116ab6d75bb96a52cdadea8a299325480feb514b6a9e814955aa40ad59368c`
- archive size: `3,934,424` bytes
- archive entries: **42**

Independent inspection of the uploaded artifact confirms the GitHub artifact digest and local ZIP SHA-256 are identical.

### Deterministic comparison evidence

- deterministic manifest SHA-256: `acb42672339f18bb1e65c93c553e1c1b4e755ce6541d27a5931e2f0352de12dd`
- manifest records: **8/8 exact SHA-256 + byte-size matches**
- revision A: `rev-post-m7-compare-demo-r1`
- revision B: `rev-studio-cb5c81e69b23078f29517312`
- revision A WAV: `e049e83bdda5a1c5710bd4d09b3010ab414d27d5a6705398aae120ae9deac5b8`
- revision A MIDI: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- revision B WAV: `dd5908497157c2cd2aea022fcf2ab6358d8e303c3fc60b0414d5a6ce7ce41458`
- revision B MIDI: `9fb5ed1dcdb19af3e4a68b4afad4cfd74aa60839a3caa44baea19bc9df7bd549`

Deterministic proof confirms:

- mixed media provenance is truthful (`A = deterministic_fallback`, `B = bound_artifact`);
- forward diff equals exact `structured_diff(A, B)`;
- reverse diff equals exact `structured_diff(B, A)`;
- identity comparison `A == A` has zero diff;
- identity WAV/MIDI hashes are equal on both sides;
- exact served revision A/B WAV/MIDI bytes match declared SHA-256;
- canonical HEAD remains unchanged;
- forbidden creative verdict keys are absent;
- all mutation/ranking/implicit-Accept authority flags remain false.

### Real-Chromium comparison evidence

- Browser manifest SHA-256: `ead585e0af92d43b4a206f2296ef320ce42baf3fb4c001a8cf05e9636323afe7`
- Browser manifest records: **9/9 exact SHA-256 + byte-size matches**
- revision A: `rev-post-m7-compare-r1`
- revision B / canonical HEAD: `rev-studio-9bc96ab819e42eba41615375`
- revision A WAV: `e049e83bdda5a1c5710bd4d09b3010ab414d27d5a6705398aae120ae9deac5b8`
- revision A MIDI: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- revision B WAV: `dd5908497157c2cd2aea022fcf2ab6358d8e303c3fc60b0414d5a6ce7ce41458`
- revision B MIDI: `9fb5ed1dcdb19af3e4a68b4afad4cfd74aa60839a3caa44baea19bc9df7bd549`
- Browser screenshots: **2** stable comparison states

Browser proof confirms:

- real Chromium was used;
- two accepted revisions are visible;
- direction is explicitly `A_TO_B`;
- structured diff is visible;
- revision A fallback and revision B bound-artifact provenance are truthful;
- A/B have independent audio controls bound to exact revisions;
- Browser-computed WAV/MIDI hashes for both sides match the comparison contract;
- HEAD remains unchanged;
- refresh/reopen reproduces the same structured diff and media provenance;
- Browser console errors: `0`;
- Browser page errors: `0`;
- unexpected Browser request failures: `0`;
- all canonical mutation/ranking/implicit-Accept authority flags remain false.

The separate real-Chromium Browser-local choice test runs in the same permanent Compare workflow and proves that clicking `Choose A` and then `Choose B` changes only Browser-local decision state. The accepted revision count, current branch and canonical HEAD remain unchanged, and refresh clears the local choice rather than persisting it into project authority.

## 6. Exact provenance boundary

For each accepted revision side, the validated projection binds the comparison to:

- exact `revision_id`;
- revision-record SHA-256;
- Blueprint SHA-256;
- exact WAV/MIDI SHA-256 and byte size;
- media source classification (`bound_artifact` or `deterministic_fallback`);
- bound artifact filename when applicable;
- immutable artifact-manifest SHA-256 when applicable.

Project integrity is verified fail-closed before comparison/media access. Unknown revision IDs fail closed. Tampered revision/artifact state fails closed rather than being compared or auditioned.

Fallback rendering does not create accepted project authority; it is a deterministic read-only media projection for an already accepted revision that lacks a bound media artifact.

## 7. Exact Compare semantics

The validated diff direction is always explicit:

```text
direction = A_TO_B
```

`structured_diff(A, B)` is descriptive, not evaluative. It reports what changed in canonical Blueprint structure. It does not infer musical quality or preference.

The following are validated:

- A→B structured diff;
- B→A structured diff;
- A→A zero-diff identity;
- arbitrary accepted revision media retrieval;
- exact bound/fallback source reporting;
- pending Preview isolation from accepted-revision comparison;
- read-only HTTP projection;
- independent A/B Browser audition;
- Browser-local human decision state;
- refresh/reopen stability;
- HEAD immutability.

## 8. Explicit non-claims

This milestone does **not** validate or claim:

- MUSICA-selected creative winner or preference;
- quality scoring or preference probability;
- implicit Accept or automatic checkout after a Browser choice;
- cross-revision use of M5-R4 renderer metrics as a music-quality metric;
- human-subject perceptual superiority or usability evidence;
- a second canonical automation renderer mapping family;
- arbitrary canonical parameter → renderer/MIDI/plugin mapping;
- VST/AU/CLAP hosting or device automation;
- DAW automation import/export/reconciliation;
- real-time MIDI/OSC automation;
- arbitrary tempo maps or spline/bezier curves;
- lane creation/deletion or parameter reassignment;
- live OpenAI provider execution;
- cloud collaboration, desktop signing or destructive waveform/audio editing.

## 9. Promotion verdict

The pre-durable implementation satisfies the promotion requirements available before adding this durable record:

1. machine-valid dedicated comparison contract exists;
2. immutable accepted revision A/B read projection is implemented;
3. deterministic `A_TO_B` structured diff is exact;
4. revision-record and Blueprint SHA provenance is explicit;
5. bound/fallback media provenance and exact WAV/MIDI bytes are verified;
6. artifact filename and immutable manifest SHA are exposed for bound artifacts;
7. comparison and media access do not move canonical HEAD;
8. unknown/tampered state fails closed;
9. real Chromium proves independent A/B audition and refresh/reopen stability;
10. real Chromium proves Browser-local human A/B choice cannot mutate canonical project state;
11. no creative winner/ranking/score authority exists;
12. deterministic evidence A/B is byte-tree reproducible;
13. uploaded artifact was independently inspected and its declared records are exact;
14. **15/15 permanent workflows SUCCESS** on the pre-durable exact head.

Therefore the bounded capability is eligible for the verdict:

> **VALIDATED — BOUNDED ACCEPTED REVISION A/B COMPARE & HUMAN DECISION SURFACE**

This durable-record-containing successor head must itself reproduce the permanent **15-workflow** set before PR #91 is eligible for expected-head squash merge.
