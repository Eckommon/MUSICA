# Current State / 현재 상태

## Project phase / 프로젝트 단계

**POST-M7 NEXT-MILESTONE SELECTION — ACCEPTED REVISION A/B COMPARE & DECISION SURFACE v0 RATIFIED FOR IMPLEMENTATION**

M0→M7-R6 remain validated only within their durable repository claims. Accepted Music Blueprint remains canonical creative authority. Browser, Music IR, automation execution, renderer/plugin, audio artifact, comparison projection and external DAW state remain derived or non-authoritative.

The post-M7 planning gate has now selected exactly one successor capability: **Issue #89 — Accepted Revision A/B Compare & Decision Surface v0**. It is ratified for implementation but is **not yet a validated capability**.

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
| Post-M7 Accepted Revision A/B Compare & Decision Surface v0 | **RATIFIED FOR IMPLEMENTATION — NOT YET VALIDATED** | Issue `#89`, `docs/POST_M7_NEXT_MILESTONE_SELECTION.md` |

No artificial `M7-R7` or `M8` identifier is assigned by this planning decision.

## M7-R6 final evidence / M7-R6 최종 근거

- Issue `#86` — **COMPLETED**
- PR `#87` — **MERGED**
- implementation/validation merge main: `1de099e8d3e489c818ae561ddfb0c43c4ffdcbfc`
- pre-durable exact head: `af11315c777f761179ca3d94bfed1a6e472dd315`
- successor evidence head: `93129768ff4b33c663eeeccda22c1d07faea0872`
- final validation-record head: `0ea3fd976a8b63293d434bb427f7dfeffb68fcfd`
- pre-durable, successor and final-record permanent workflow sets: **14/14 SUCCESS** each
- pre-durable R6 artifact: `10426461920`
- successor R6 artifact: `10426332617`
- deterministic manifest SHA-256: `926c0608c5998ceaa1ac0f49c19dbf4f293acc180d0e2433d067b369d32b953a`
- deterministic pre-durable vs successor evidence: **14 files / 0 differences**
- accepted/reopened WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- accepted/reopened MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- Browser proof on pre-durable/successor: console errors `0`, page errors `0`, unexpected request failures `0`, expected superseded-audio aborts `2`

## M7-R6 validated lifecycle / 검증된 수명주기

```text
accepted automation material
→ historical R2 view remains unchanged
→ trusted R5 audible Preview
→ studio-automation-audition-v0 read-only inspection
→ Browser verifies mapped/unmapped lanes + exact media hashes
→ PREVIEW · NOT ACCEPTED
→ Discard OR explicit Accept
→ exact pending WAV/MIDI bound to accepted revision
→ restart/reopen serves accepted bytes unchanged
```

Validated properties remain unchanged:

- historical `studio-automation-view-v0` remains unchanged with `audible_automation_validated=false`;
- `studio-automation-audition-v0` truthfully reports current bounded audible capability;
- current mapped lane set is exactly `A-MIX-GAIN` under `mix.gain/project/normalized`;
- `B-SYNTH-CUTOFF` remains explicitly unmapped;
- pending Browser inspection is non-canonical and does not mutate Project authority;
- Browser-computed Preview WAV/MIDI hashes equal trusted pending hashes;
- Discard restores accepted identity;
- explicit Accept advances exactly one revision;
- accepted/reopened WAV/MIDI equal exact Preview bytes;
- unsupported-only automation cannot claim audible application;
- Browser/audio/renderer state has no reverse-promotion authority.

## Current capability stack / 현재 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material and accepted explicit automation material.

### Precision editing
M6 exact-note editing and M7 automation point editing use source-bound Preview/Accept authority patterns.

### Studio
Browser Studio Direct → Shape → Inspect → Code, exact-note piano roll, bounded automation editing, audible automation Preview and truthful audition inspection are validated within their stated boundaries.

### Version foundation
M2 can read arbitrary immutable accepted revision records and Blueprints with hash verification, stores deterministic per-revision structured diffs, and binds artifacts to exact revisions. This foundation is validated; an A/B user-facing comparison surface is not yet validated.

### Derived execution
R3 deterministically lowers accepted/candidate canonical automation to `automation-execution-v0` without guessing backend addresses.

### Renderer
R4 maps exactly one automation family — `mix.gain/project/normalized` — through an explicit reference-renderer plan to byte-reproducible audible WAV output. R5 integrates it into Studio Preview; R6 exposes the resulting lifecycle truthfully without granting new authority.

### Interchange
Existing bounded DAWproject interchange/evaluation and exact-note reconciliation remain validated. Automation interchange remains unvalidated.

### AI provider
M3-R2 validates the OpenAI adapter contract and offline integration path. The adapter is live-ready, but **live OpenAI provider execution remains unvalidated** and any future live smoke must be separate `LIVE_PROVIDER_EVIDENCE`.

## Post-M7 closure review finding / Post-M7 종결 검토 결과

The product thesis explicitly requires:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

M4-R3 already validates natural-language create, audition, semantic Preview, explicit Accept, branch/history/export and restart/reopen in real Chromium. A generic end-to-end natural-language milestone would therefore duplicate existing evidence.

The strongest unresolved product-loop gap is **Compare**. The repository already contains nearly all prerequisites: arbitrary accepted revision reads, immutable revision records, `structured_diff()`, revision-bound artifacts, deterministic rendering, Studio same-origin media delivery and real-browser evidence infrastructure.

The concrete missing boundary is that Studio currently serves media for pending Preview or current accepted HEAD; it does not yet expose a bounded read-only projection/media surface for arbitrary accepted revisions A and B at once.

The closure review therefore selected:

> **Issue #89 — Accepted Revision A/B Compare & Decision Surface v0**

See `docs/POST_M7_NEXT_MILESTONE_SELECTION.md`.

## Issue #89 target authority / Issue #89 목표 권한

```text
accepted revision A ─┐
                     ├→ read-only comparison projection
accepted revision B ─┘
                              ↓
                    Browser inspection/audition
```

The comparison projection has **no write authority**.

It may expose:

- exact revision IDs and revision-record/Blueprint hashes;
- deterministic `A_TO_B` Blueprint diff;
- exact per-revision media provenance;
- bound artifact bytes when present;
- explicit deterministic fallback render otherwise;
- independent A/B audition;
- existing user-controlled project navigation only.

It may not expose or perform:

- system-selected creative winner;
- creative quality/preference score;
- implicit Accept;
- automatic branch/head movement;
- cross-revision reuse of M5-R4's same-Music-IR renderer comparison semantics;
- reverse promotion from Browser/audio/comparison state into Blueprint authority.

## Exact next phase / 다음 단계

> **Implement Issue #89 contract-first, then trusted comparison projection → arbitrary accepted-revision media → read-only HTTP routes → Browser A/B surface → deterministic tests → real-Chromium evidence → permanent CI/evidence → expected-head merge → state-only closure.**

See `memory/NEXT_ACTION.md` for the exact execution order and promotion gate.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate:

- accepted-revision A/B Browser comparison or arbitrary-revision Studio audition;
- a system-selected creative preference/winner between revisions;
- a second automation renderer mapping family;
- arbitrary canonical parameter → renderer/MIDI/plugin mapping;
- plug-in/device mapping or VST/AU/CLAP hosting;
- external DAW automation reconciliation;
- arbitrary tempo maps or spline/bezier curves;
- lane creation/deletion or parameter reassignment;
- real-time MIDI/OSC automation;
- live OpenAI provider execution;
- human-subject usability/preference or perceptual superiority;
- waveform/destructive audio editing, cloud collaboration or desktop signing.

## Resume authority / 재개 권위

Before implementing Issue `#89`, inspect:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/POST_M7_NEXT_MILESTONE_SELECTION.md`
4. Issue `#89`
5. `src/musica/project.py`
6. `src/musica/diff.py`
7. `src/musica/studio.py`
8. `src/musica/studio_http.py`
9. `evidence/M4_R3_VALIDATION.md`
10. `evidence/M3_R2_VALIDATION.md`
11. `evidence/M7_R6_VALIDATION.md`
12. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**