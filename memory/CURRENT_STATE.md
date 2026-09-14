# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M7-R1 — BOUNDED CANONICAL AUTOMATION RUNTIME & BLUEPRINT INTEGRATION: VALIDATED — BOUNDED CORE RUNTIME**

M0→M7-R1 are validated only within their durable repository claims. M7-R1 operationalizes the M7-R0 authority contract inside accepted Blueprint/project authority while preserving legacy projects and keeping Browser, Music IR, renderer/plugin and external DAW state non-authoritative.

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**

## Canonical milestone ledger / 공식 마일스톤 원장

| Milestone | Status | Durable evidence |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4 Browser Studio / Usable MVP | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` → `M4_R3_VALIDATION.md` |
| M5 Rendering / Interchange / Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R1_VALIDATION.md` → `M5_R4_VALIDATION.md` |
| M6 Precision Editing R0→R4 | **VALIDATED — BOUNDED** | `evidence/M6_R0_VALIDATION.md` → `evidence/M6_R4_VALIDATION.md` |
| M7-R0 Automation Authority & Canonical Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M7_R0_VALIDATION.md` |
| M7-R1 Canonical Automation Runtime & Blueprint Integration | **VALIDATED — BOUNDED CORE RUNTIME** | `evidence/M7_R1_VALIDATION.md` |
| M7-R2 Browser Studio Automation Lane / Inspect Surface | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |

## M7-R1 final evidence / M7-R1 최종 근거

- Issue `#71` — **COMPLETED**
- PR `#72` — **MERGED**
- implementation merge/main: `877ed9b7e7f90101ffcdb6891bd75631807053e2`
- final evidence-bearing exact head: `abe1f9c92751e0cdde935b34f4a17f1e1fc20548`
- M7-R1 `34795684053` — **SUCCESS**
- M7-R0 `34795684183` — **SUCCESS**
- MUSICA CI `34795683991` — **SUCCESS**
- M6-R4 `34795684200` — **SUCCESS**
- M6-R3 `34795683988` — **SUCCESS**
- M6-R2 `34795683981` — **SUCCESS**
- M6-R1 `34795684023` — **SUCCESS**
- M5-R3 `34795684054` — **SUCCESS**
- M5-R4 `34795683984` — **SUCCESS**
- final artifact ID `10330005742`
- packaging SHA-256 `178d86faf11bfd859b84fc0c60363a493f9ffa8530dab27567ccd0b2e03ea638`
- internal manifest SHA-256 `b21dfd8e6b7c61ceee8b5613f8c65bb4857209a050cffe92eb8cabe33232ed5e`
- pre-durable vs successor extracted evidence tree: **15 files / 0 differences**
- pre-durable manifest: **14/14 exact SHA-256 + byte-size matches**

## M7-R1 validated authority invariant

```text
legacy or automation-capable accepted Blueprint
→ optional canonical automation material
→ deterministic material hash
→ source-bound AutomationEditCandidate
→ stable identity + time/range + inherited lock authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit M2 Accept only
→ immutable accepted revision
```

Validated R1 properties:

- legacy Blueprint bytes remain unchanged and no automation is fabricated;
- deterministic empty material hash exists for legacy source binding;
- accepted automation storage is optional under `materials.automation`;
- exactly five stable-ID point primitives are implemented;
- stale source, unknown lane/point, duplicate point ID/beat, invalid range/time and unsupported interpolation fail closed;
- HARD exact and presence locks produce typed blocking authority;
- child revision validation preserves inherited lock semantics;
- direct M2 commit cannot bypass HARD automation locks;
- Preview is side-effect-free and has no Project/Music IR mutation authority;
- explicit Accept advances exactly one M2 revision;
- evidence generation is byte-reproducible.

## Current capability stack / 현재 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material and now bounded accepted explicit automation material.

### Precision editing
M6 provides exact-note trusted editing. M7-R1 adds trusted-core automation point editing through the same source-bound Preview/Accept authority pattern.

### Studio
Browser Studio Direct → Shape → Inspect → Code and exact-note piano roll remain validated. Browser automation lanes are **not yet implemented**.

### Renderer / interchange
Existing bounded rendering, DAWproject interchange/evaluation and exact-note reconciliation remain validated. Canonical automation is **not yet lowered to audible renderer control**.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate:

- Browser automation-lane UI or real-browser automation editing;
- automation lowering into Music IR or audible renderer execution;
- plug-in/device mapping or VST/AU/CLAP hosting;
- external DAW automation reconciliation;
- arbitrary tempo maps or spline/bezier curves;
- lane creation/deletion or parameter reassignment in R1;
- real-time MIDI/OSC automation;
- live OpenAI provider execution;
- human-subject usability/preference or perceptual superiority;
- waveform/destructive audio editing, cloud collaboration or desktop signing.

## Next phase / 다음 단계

> **M7-R2 — Browser Studio Automation Lane / Inspect Surface**

R2 must expose accepted R1 automation through Browser Studio Inspect without creating a second authority model:

```text
accepted R1 automation material
→ stable Browser lane/point projection
→ bounded point editing gesture/form
→ typed AutomationEditCandidate
→ existing R1 authority
→ READY_FOR_PREVIEW or BLOCKED
→ Preview / Accept / Discard
```

The Browser must remain a projection/proposal surface. DOM/canvas location, array index and client-only state must never become canonical lane/point identity.

## Resume authority / 재개 권위

Before R2 substantive work inspect:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M7_AUTOMATION_AUTHORITY.md`
4. `evidence/M7_R0_VALIDATION.md`
5. `evidence/M7_R1_VALIDATION.md`
6. M7 automation schemas
7. `src/musica/automation_contracts.py`
8. `src/musica/automation_edit.py`
9. M4/M6 Browser Studio and Preview/Accept precedents
10. `memory/CURRENT_STATE.md`
11. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**
