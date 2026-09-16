# Post-M7 Next-Milestone Selection / Post-M7 다음 마일스톤 선정

## Status / 상태

**COMPLETED — SELECTED CAPABILITY VALIDATED AND MERGED**

This record originally selected exactly one bounded post-M7 successor from repository evidence: **Accepted Revision A/B Compare & Decision Surface v0**. That selected capability is now implemented, independently evidenced, merged and ready for state closure.

- original review base: `2bfc8ffbe707c06f016d820cc47d901ed862be92`
- selected Issue: `#89` — **COMPLETED**
- implementation PR: `#91` — **MERGED**
- implementation/validation merge main: `7314deb5aba93073f1f7750dc68f9f4d31cd3c06`
- durable evidence: `evidence/POST_M7_REVISION_COMPARE_VALIDATION.md`
- milestone numbering: **no inferred `M7-R7` or `M8`**

## 1. Original selection rationale / 최초 선정 근거

The product thesis defines:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

M4-R3 had already validated natural-language create → audition → semantic Preview → explicit Accept → branch/history/export → restart/reopen in real Chromium. M2 had already validated immutable accepted revisions, arbitrary revision reads, deterministic structured diffs and revision-bound artifacts.

The strongest explicit product-loop gap was therefore accepted-revision **Compare**, not another duplicate end-to-end create/edit milestone.

The selection review compared that gap with live OpenAI provider evidence and adjacent automation/interchange candidates. Compare was selected because it directly closed a user-facing thesis gap, reused validated authority infrastructure, remained read-only, and could be proven deterministically without external credentials/network dependencies.

## 2. Validated outcome / 검증 결과

The selected mission is now validated as:

> **VALIDATED — BOUNDED ACCEPTED REVISION A/B COMPARE & HUMAN DECISION SURFACE**

The final bounded path is:

```text
accepted revision A + accepted revision B
→ immutable revision records + Blueprint SHA-256 verification
→ deterministic structured diff A_TO_B
→ exact revision media provenance
   ├─ bound artifact when present
   └─ deterministic fallback render when not bound
→ read-only localhost HTTP projection
→ independent Browser A/B audition
→ Browser-local human Choose A / Choose B
→ no canonical mutation
```

Validated properties include:

- explicit A/B accepted revision IDs;
- deterministic A→B and B→A structured diff;
- A==B zero-diff identity case;
- revision-record and Blueprint SHA-256 provenance;
- exact revision-specific WAV/MIDI hashes and byte sizes;
- explicit bound/fallback provenance;
- bound artifact filename and immutable artifact-manifest SHA;
- arbitrary accepted-revision media serving without checkout/HEAD mutation;
- real-Chromium A/B presentation and audition;
- Browser-local user choice that cannot Accept, checkout, create revisions or move HEAD;
- refresh/reopen stability;
- fail-closed unknown/tampered state;
- no creative winner/score/preference authority.

## 3. Promotion evidence / 승격 근거

- pre-durable exact head: `b22e41f690606aeedcffa11ef2ec5e915b34551d`
- pre-durable permanent workflows: **15/15 SUCCESS**
- durable-record exact head: `de309c7f030d6c3f8085da312bc7c7bfaa94e19d`
- durable-record permanent workflows: **15/15 SUCCESS**
- dedicated Compare run: `35063187699` — **SUCCESS**
- evidence artifact: `10433182942`
- artifact ZIP SHA-256: `43116ab6d75bb96a52cdadea8a299325480feb514b6a9e814955aa40ad59368c`
- deterministic manifest records: **8/8 exact**
- Browser manifest records: **9/9 exact**
- deterministic evidence A/B `diff -qr`: **SUCCESS**
- real Chromium Compare: **SUCCESS**
- real Chromium Browser-local Choose A/B isolation: **SUCCESS**

## 4. Authority result / 권한 결과

The validated comparison projection preserves:

```text
canonical                    = false
browser_mutation_authorized  = false
project_mutation_authorized  = false
reverse_promotion_authorized = false
creative_ranking_authorized  = false
implicit_accept_authorized   = false
```

Forbidden paths remain forbidden:

```text
comparison result ─X→ accepted Blueprint mutation
Browser choice    ─X→ implicit Accept / checkout / HEAD movement
A/B audio         ─X→ inferred canonical Blueprint
metric            ─X→ creative winner
M5-R4 comparator  ─X→ cross-revision preference score
```

M5-R4 remains semantically separate: it compares renderer outputs for the **same Music IR**, not different musical revisions.

## 5. Deferred candidates remain deferred, not invalidated / 보류 후보

The Compare milestone does not select the next implementation automatically. Previously reviewed candidates remain legitimate inputs to a new successor review, including:

- `LIVE_PROVIDER_EVIDENCE` — actual authorized OpenAI execution behind the already validated M3-R2 provider boundary;
- additional automation renderer mappings beyond `mix.gain/project/normalized`;
- automation-aware DAW/interchange reconciliation;
- richer automation authoring, tempo and curve families;
- real-time MIDI/OSC or plug-in/device integration;
- production packaging/collaboration surfaces;
- human usability/perceptual evaluation when product claims require it.

## 6. Closed selection gate / 종료된 선정 게이트

The original post-M7 planning gate is closed. The selected target claim is no longer hypothetical:

> **MUSICA can truthfully compare two immutable accepted creative revisions by showing their exact structured Blueprint differences and revision-bound/fallback audition media side by side, while leaving creative preference and canonical acceptance/navigation authority to the user.**

The next action is a **new post-Compare successor review**, not an extension of Issue #89 and not an inferred `M7-R7`/`M8`.

**Repository evidence remains authoritative over conversation/model memory.**
