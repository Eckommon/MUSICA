# Current State / 현재 상태

## Project phase / 프로젝트 단계

**POST-COMPARE CORE PRODUCT LOOP — BOUNDEDLY VALIDATED; SUCCESSOR REVIEW REQUIRED**

M0→M7-R6 and the post-M7 Accepted Revision A/B Compare & Human Decision Surface v0 are validated only within their durable repository claims. Accepted Music Blueprint remains canonical creative authority. Browser, Music IR, automation execution, renderer/plugin, audio artifact, comparison projection, Browser-local A/B choice and external DAW state remain derived or non-authoritative.

The previous post-M7 planning gate and Issue `#89` are complete. No successor implementation is currently ratified. Do not infer `M7-R7`, `M8`, or another milestone number without a new repository selection decision.

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**

## Canonical milestone ledger / 공식 마일스톤 원장

| Milestone | Status | Durable evidence |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4 Browser Studio / Usable MVP | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` → `evidence/M4_R3_VALIDATION.md` |
| M5 Rendering / Interchange / Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R1_VALIDATION.md` → `evidence/M5_R4_VALIDATION.md` |
| M6 Precision Editing R0→R4 | **VALIDATED — BOUNDED** | `evidence/M6_R0_VALIDATION.md` → `evidence/M6_R4_VALIDATION.md` |
| M7-R0 Automation Authority & Canonical Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M7_R0_VALIDATION.md` |
| M7-R1 Canonical Automation Runtime & Blueprint Integration | **VALIDATED — BOUNDED CORE RUNTIME** | `evidence/M7_R1_VALIDATION.md` |
| M7-R2 Browser Studio Automation Lane / Inspect Surface | **VALIDATED — BOUNDED REAL-BROWSER SURFACE** | `evidence/M7_R2_VALIDATION.md` |
| M7-R3 Deterministic Automation Lowering & Derived Execution Boundary | **VALIDATED — BOUNDED DERIVED EXECUTION** | `evidence/M7_R3_VALIDATION.md` |
| M7-R4 Reference Renderer Automation Mapping & Audible Evidence | **VALIDATED — BOUNDED AUDIBLE EXECUTION** | `evidence/M7_R4_VALIDATION.md` |
| M7-R5 Studio Automation Audition & Accepted Artifact Persistence | **VALIDATED — BOUNDED STUDIO AUDITION & ARTIFACT PERSISTENCE** | `evidence/M7_R5_VALIDATION.md` |
| M7-R6 Truthful Audible Automation Capability & Browser Lifecycle Inspection | **VALIDATED — BOUNDED TRUTHFUL AUDITION INSPECTION** | `evidence/M7_R6_VALIDATION.md` |
| Post-M7 Accepted Revision A/B Compare & Human Decision Surface v0 | **VALIDATED — BOUNDED READ-ONLY DECISION SURFACE** | `evidence/POST_M7_REVISION_COMPARE_VALIDATION.md` |

## Latest canonical completion / 최신 공식 완료

### Accepted Revision A/B Compare & Human Decision Surface v0

- Issue `#89` — **COMPLETED**
- PR `#91` — **MERGED**
- implementation/validation main: `7314deb5aba93073f1f7750dc68f9f4d31cd3c06`
- pre-durable exact head: `b22e41f690606aeedcffa11ef2ec5e915b34551d`
- durable-record exact head: `de309c7f030d6c3f8085da312bc7c7bfaa94e19d`
- pre-durable permanent workflows: **15/15 SUCCESS**
- durable-record permanent workflows: **15/15 SUCCESS**
- dedicated pre-durable Compare run: `35063187699` — **SUCCESS**
- evidence artifact: `10433182942`
- artifact ZIP SHA-256: `43116ab6d75bb96a52cdadea8a299325480feb514b6a9e814955aa40ad59368c`
- deterministic manifest: **8/8 exact SHA-256 + size records**
- Browser manifest: **9/9 exact SHA-256 + size records**
- deterministic evidence A/B byte-tree reproduction: **SUCCESS**
- real-Chromium A/B comparison: **SUCCESS**
- real-Chromium Browser-local `Choose A` / `Choose B` isolation: **SUCCESS**

## Canonical product-loop coverage / 공식 제품 루프 커버리지

The thesis loop is:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

Within the current bounded local workstation scope, repository evidence now covers the full loop:

1. **Describe / Generate Blueprint** — intent/provider-neutral Director path produces typed Blueprint candidates.
2. **Audition** — deterministic rendering and Browser Studio media paths are validated.
3. **Lock** — hard locks/constraints and exact-note/automation source binding protect canonical decisions.
4. **Refine** — semantic, exact-note and automation edits use Preview → explicit Accept.
5. **Compare** — two immutable accepted revisions can be compared by exact structured diff and exact revision-specific media provenance.
6. **Human decision** — Browser-local A/B choice is available but remains non-canonical.
7. **Accept** — M2 explicit Accept remains the only canonical acceptance transition.
8. **Reproduce/version** — immutable revisions, branches, audit, artifact binding and restart/reopen persistence are validated.

This closes the explicit thesis-loop gap. It does **not** imply production-DAW completeness or validation of every external integration.

## Compare validated authority / Compare 검증 권한

```text
accepted revision A ─┐
                     ├→ read-only comparison projection
accepted revision B ─┘
                              ↓
                 independent Browser A/B audition
                              ↓
                 Browser-local human choice
```

The comparison/choice path has no canonical write authority.

Validated truth includes:

- explicit `A_TO_B` direction;
- deterministic forward/reverse diff and A==B identity;
- exact revision-record + Blueprint SHA provenance;
- exact bound/fallback WAV/MIDI provenance and served-byte SHA;
- bound artifact filename + immutable manifest SHA where applicable;
- arbitrary accepted-revision media without checkout/HEAD mutation;
- fail-closed unknown/tampered state;
- independent Browser A/B audition;
- refresh/reopen diff/media stability;
- local human choice does not Accept, checkout, create revisions or move HEAD;
- no winner/score/preference-probability authority;
- M5-R4 same-Music-IR renderer comparison remains semantically unchanged.

## Current capability stack / 현재 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material, accepted explicit automation material, revision-bound artifacts and explicit Accept authority.

### Browser Studio
Natural-language create/edit workflow, Direct/Shape/Inspect/Code surfaces, exact-note piano roll, bounded automation editing, audible Preview, truthful audition inspection and accepted-revision A/B Compare with independent audition.

### Precision & automation
Exact-note editing and bounded automation point editing are canonical through source-bound Preview/Accept. Derived automation execution is deterministic.

### Renderer
Exactly one canonical automation renderer mapping family is validated: `mix.gain / project / normalized` through `musica-reference-local`. Unsupported parameters remain explicitly unmapped rather than guessed.

### Version & Compare
M2 arbitrary immutable revision reads + `structured_diff()` + revision-bound artifacts now feed a validated read-only A/B decision surface.

### Interchange
Bounded DAWproject interchange/evaluation and exact-note reconciliation are validated. Automation interchange/reconciliation is not.

### AI provider
The OpenAI adapter contract and offline integration path are validated. The adapter is live-ready, but actual live OpenAI execution remains unvalidated and separately classified `LIVE_PROVIDER_EVIDENCE`.

## Remaining claim boundaries / 남은 주장 경계

The repository does **not** yet validate:

- system-selected creative preference/winner across revisions;
- a second automation renderer mapping family;
- arbitrary canonical parameter → renderer/MIDI/plugin mapping;
- VST/AU/CLAP hosting or generalized device/plugin automation;
- external DAW automation reconciliation;
- arbitrary tempo maps, lane lifecycle or spline/bezier/exponential automation curves;
- real-time MIDI/OSC automation;
- live OpenAI provider execution;
- human-subject usability/preference or perceptual-superiority claims;
- destructive waveform/audio editing;
- cloud collaboration or multi-user authority;
- installer/signing/distribution hardening or production SLA guarantees.

These are candidates or future scope, not automatically required milestones.

## Exact next phase / 다음 단계

> **POST-COMPARE SUCCESSOR REVIEW — reassess the product thesis, current validated stack, remaining claim gaps, user leverage, authority risk and evidence cost; compare serious candidates and ratify exactly one bounded successor before implementation.**

The review must include at minimum:

- `LIVE_PROVIDER_EVIDENCE`;
- automation renderer/mapping expansion;
- automation-aware DAW/interchange reconciliation;
- richer authoring/tempo/curve operations;
- plug-in/device and real-time control integration;
- production/distribution/collaboration hardening;
- human usability/perceptual evaluation where it is necessary to support a claim.

Do not implement one by default merely because it is listed.

## Resume authority / 재개 권위

Before selecting the next successor, inspect:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `README.md`
4. `docs/POST_M7_NEXT_MILESTONE_SELECTION.md`
5. `evidence/POST_M7_REVISION_COMPARE_VALIDATION.md`
6. `evidence/M7_R6_VALIDATION.md`
7. `evidence/M3_R2_VALIDATION.md`
8. `memory/NEXT_ACTION.md`
9. open Issues/PRs and current permanent workflows

**Repository evidence remains authoritative over conversation/model memory.**
