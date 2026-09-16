# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation**. The accepted Music Blueprint/project revision is creative authority. Music IR, Browser state, derived automation execution, renderer/plugin state, audio artifacts, comparison projections and interchange/DAW state are derived or non-canonical unless an explicit authority contract says otherwise.

## Current canonical status / 현재 공식 상태

**M0 → M7-R6 and the post-M7 Accepted Revision A/B Compare & Human Decision Surface v0 are validated within their explicitly bounded repository claims.**

```text
M0      controllable core                                  VALIDATED
M1      creative core                                      VALIDATED
M2      project & version engine                           VALIDATED
M3      AI Music Director provider layer                   VALIDATED — BOUNDED
M4      Browser Studio / usable MVP                        VALIDATED
M5      rendering / interchange / evaluation               VALIDATED — BOUNDED
M6      precision editing R0→R4                            VALIDATED — BOUNDED
M7-R0   automation authority/data model                    VALIDATED — CONTRACT/DESIGN ONLY
M7-R1   canonical automation runtime                       VALIDATED — BOUNDED CORE RUNTIME
M7-R2   Browser automation inspect/edit                    VALIDATED — BOUNDED REAL-BROWSER SURFACE
M7-R3   deterministic derived automation execution         VALIDATED — BOUNDED DERIVED EXECUTION
M7-R4   reference-renderer audible mix.gain mapping        VALIDATED — BOUNDED AUDIBLE EXECUTION
M7-R5   Studio audible Preview / Accept / reopen            VALIDATED — BOUNDED STUDIO AUDITION
M7-R6   truthful audible automation inspection              VALIDATED — BOUNDED TRUTHFUL INSPECTION
Post-M7 accepted revision A/B Compare + human choice        VALIDATED — BOUNDED READ-ONLY DECISION SURFACE
```

No artificial `M7-R7` or `M8` identifier is inferred from this closure.

## Canonical product loop / 공식 제품 루프

The thesis-level loop is:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

The repository now contains bounded validated evidence for every stage of that loop:

- natural-language intent → typed Blueprint generation;
- deterministic compilation/rendering and Browser audition;
- locks/constraints and source-bound edit authority;
- semantic, exact-note and automation refinement through Preview → explicit Accept;
- immutable revision/history/branch/project persistence;
- accepted-revision A/B comparison with exact structured diff and exact media provenance;
- human A/B decision state that remains Browser-local and cannot silently mutate project authority;
- explicit Accept as the only canonical acceptance transition.

This does **not** mean MUSICA is a finished production DAW. It means the canonical product thesis is now demonstrably implemented across a bounded local workstation path.

## Accepted Revision A/B Compare — validated boundary

Issue `#89` / PR `#91` closes the explicit Compare gap.

```text
accepted revision A + accepted revision B
→ immutable revision/Blueprint verification
→ deterministic structured_diff(A, B)
→ exact bound/fallback WAV + MIDI provenance
→ read-only localhost comparison/media routes
→ independent Browser A/B audition
→ Browser-local Choose A / Choose B
→ no canonical mutation
```

Validated properties include:

- explicit `A_TO_B` diff direction;
- A→B and B→A deterministic structured diffs;
- A==B zero-diff identity behavior;
- exact revision-record and Blueprint SHA-256 provenance;
- exact WAV/MIDI SHA-256 and byte-size provenance;
- bound artifact filename + immutable artifact-manifest SHA when bound media exists;
- explicit `deterministic_fallback` when an accepted revision lacks bound media;
- fail-closed unknown/tampered revision or artifact state;
- arbitrary accepted-revision media access without checkout/HEAD mutation;
- independent real-Chromium A/B audition;
- refresh/reopen preservation of diff/media provenance;
- Browser-local human choice without Accept, checkout, revision creation or HEAD movement;
- no creative winner, score, preference probability or cross-revision M5-R4 ranking authority.

Durable evidence: `evidence/POST_M7_REVISION_COMPARE_VALIDATION.md`.

### Final Compare evidence

- Issue `#89` — **COMPLETED**
- PR `#91` — **MERGED**
- implementation/validation merge main: `7314deb5aba93073f1f7750dc68f9f4d31cd3c06`
- pre-durable exact head: `b22e41f690606aeedcffa11ef2ec5e915b34551d`
- durable-record exact head: `de309c7f030d6c3f8085da312bc7c7bfaa94e19d`
- pre-durable permanent gates: **15/15 SUCCESS**
- durable-record permanent gates: **15/15 SUCCESS**
- dedicated pre-durable Compare run: `35063187699` — **SUCCESS**
- evidence artifact: `10433182942`
- artifact ZIP SHA-256: `43116ab6d75bb96a52cdadea8a299325480feb514b6a9e814955aa40ad59368c`
- deterministic manifest: **8/8 exact records**
- Browser manifest: **9/9 exact records**
- real Chromium + Browser-local human choice: **SUCCESS**
- deterministic evidence A/B byte-tree reproduction: **SUCCESS**

## Canonical authority / 공식 권한 구조

```text
User / AI / bounded proposal
        ↓
typed non-canonical candidate
        ↓
source binding + locks + constraints + invariants
        ↓
READY_FOR_PREVIEW or BLOCKED
        ↓
PREVIEW · NOT ACCEPTED
        ↓ explicit Accept only
M2 Project & Version Engine
        ↓
Accepted Music Blueprint revision
        ↓ trusted deterministic lowering
Music IR + automation execution
        ↓ explicit renderer mapping policy
Renderer / Studio media artifacts
        ↓ read-only projection
Browser audition / accepted-revision Compare
        ↓
Browser-local human decision state
```

No renderer, Browser, Music IR, derived execution package, audio artifact, comparison result, local A/B choice or DAW/plugin state may promote itself back into canonical Blueprint authority.

## Exact next bounded action / 정확한 다음 작업

The explicit Compare gap is closed. The next repository action is therefore **not another implementation by assumption**.

> **Run a post-Compare successor review against `docs/PRODUCT_THESIS.md`, validated evidence, current non-claims and user leverage; compare the strongest remaining candidates and ratify exactly one bounded successor before implementation.**

Candidate families that must be evaluated rather than automatically selected include:

- `LIVE_PROVIDER_EVIDENCE` for actual OpenAI execution;
- expansion beyond the single validated `mix.gain/project/normalized` automation renderer mapping;
- automation-aware DAW/interchange reconciliation;
- richer automation authoring/tempo/curve operations;
- plug-in/device or real-time MIDI/OSC integration;
- production distribution/collaboration surfaces;
- human usability/perceptual evaluation where claims require it.

See `memory/NEXT_ACTION.md`.

## Current non-claims / 현재 비주장

MUSICA does not yet validate, unless a future milestone explicitly does so:

- a system-selected creative winner/preference between different revisions;
- a second canonical automation renderer mapping family;
- arbitrary canonical parameter → renderer/MIDI/plugin mapping;
- VST/AU/CLAP hosting or generalized plug-in/device automation;
- external DAW automation reconciliation;
- arbitrary tempo maps or spline/bezier/exponential automation curves;
- lane creation/deletion or parameter reassignment;
- real-time MIDI/OSC automation;
- live OpenAI provider execution;
- human-subject usability/preference or perceptual-superiority claims;
- waveform/destructive audio editing;
- cloud collaboration, multi-user authority, installer/signing or production SLA claims.

## Repository as source of truth / Repo 공식 근거

```text
accepted repository tests/artifacts/evidence
> merged specifications/current-state records
> Issue/PR/exact-head CI evidence
> conversation context
> model memory/inference
```

Resume from `memory/CURRENT_STATE.md` and `memory/NEXT_ACTION.md`.

**Repository evidence remains authoritative over conversation/model memory.**
