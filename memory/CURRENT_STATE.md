# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M7-R0 — CANONICAL AUTOMATION & CONTINUOUS-CONTROL AUTHORITY: VALIDATED — CONTRACT/DESIGN ONLY**

M0→M7-R0 are validated only within their durable repository claims. M7-R0 ratifies the bounded authority/data model for future canonical explicit automation while deliberately leaving accepted Blueprint storage/migration and runtime editing unimplemented.

M0→M7-R0는 영속 repo 근거가 허용하는 제한 범위에서만 검증되었습니다. M7-R0는 향후 canonical explicit automation을 위한 제한 권한/데이터 모델을 비준했지만 accepted Blueprint 저장·migration 및 runtime 편집은 의도적으로 구현하지 않았습니다.

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
| M7-R1 Canonical Automation Runtime & Blueprint Integration | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate live-provider evidence required |
| Human-subject usability/perceptual evidence | **NOT VALIDATED** | separate controlled study required |

## M7-R0 final evidence / M7-R0 최종 근거

- Issue `#68` — **COMPLETED**
- PR `#69` — **MERGED**
- implementation merge/main: `672ce33ee8b8fe05717ad1a5a0c416714de88d2d`
- final evidence-bearing exact head: `5b5aeb8c6bee3f8e2d48f41543b5bd5cd33e43ef`
- final MUSICA CI: `34791538725` — **SUCCESS**
- final M7-R0 contract evidence: `34791538703` — **SUCCESS**
- final M6-R4 regression: `34791538853` — **SUCCESS**
- final M6-R3 regression: `34791538669` — **SUCCESS**
- final M6-R2 regression: `34791538762` — **SUCCESS**
- final M6-R1 regression: `34791538672` — **SUCCESS**
- final M5-R3 regression: `34791538695` — **SUCCESS**
- final M5-R4 regression: `34791538743` — **SUCCESS**
- final artifact ID: `10328327862`
- final packaging SHA-256: `1360f29d6568a75e7bcf740e605e37fd1f97df9715bdb7326133047afd2753a5`
- internal manifest SHA-256: `aab674c3953abcbca94d659da4d3627d65a682b4039510f6f6e255e08efee5`
- manifest: **2/2 SHA-256 + byte-size matches**
- source/contract ledger: **21 files hash-bound**
- same-head evidence A/B: **byte-identical**
- pre-durable vs successor internal evidence: **3 files / 0 differences**

## M7-R0 validated authority invariant / M7-R0 검증 권한 불변식

```text
future accepted Blueprint automation material
→ trusted deterministic lowering
→ derived Music IR / renderer control events

source-bound AutomationEditCandidate
→ stable lane / point / parameter identity
→ lock + constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept only
→ M2 revision authority
```

Forbidden:

```text
Music IR control events → fabricated canonical automation
renderer/plugin state → accepted Blueprint directly
Browser point/order → canonical identity
AI curve → implicit acceptance
DAW lane/index → MUSICA stable identity
external automation → accepted state without later proven reconciliation
```

Ratified R0 properties:

- canonical stable `lane_id`, `point_id`, dotted `parameter_id` contract;
- canonical scope `project | part`, with derived `track_id` excluded;
- quarter-note-beat time domain;
- explicit units and range validation;
- `hold | linear` interpolation only;
- exactly five typed point-edit primitives;
- source-bound `preview_only=true` candidates;
- fail-closed READY/BLOCKED authority result model;
- stable-ID exact/range/presence automation lock contract;
- duplicate IDs, duplicate beats, duplicate targets, out-of-range values and invalid lock references fail closed;
- no Project or Music IR direct mutation authority;
- deterministic contract evidence generation.

## Current capability stack / 현재 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit and existing exact-note authority.

### Studio
Local-first Browser Studio with Direct → Shape → Inspect → Code, explicit Preview/Accept/Discard and exact-note piano-roll editing. Automation lane UI is **not yet implemented**.

### Renderer / interchange
Bounded local rendering, DAWproject interchange, comparative evaluation and bounded exact-note return reconciliation remain validated within M5/M6 claims.

### Automation authority
M7-R0 adds only the validated contract/design boundary. It does not yet add canonical automation material to accepted projects or execute automation edits.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate:

- accepted Blueprint automation storage/migration;
- runtime automation editing;
- automation Preview/Accept execution;
- Browser automation lanes;
- audible automation lowering/rendering;
- plug-in/device parameter mapping or VST/AU/CLAP hosting;
- external DAW automation reconciliation;
- arbitrary tempo-map automation;
- real-time MIDI/OSC control;
- live OpenAI provider execution;
- human-subject usability/preference or perceptual superiority;
- arbitrary external DAW compatibility;
- waveform/destructive audio editing;
- cloud collaboration or desktop signing.

## Next phase / 다음 단계

The exact next bounded mission is:

> **M7-R1 — Bounded Canonical Automation Runtime & Blueprint Integration**

R1 must implement only the trusted-core path needed to make the ratified R0 automation contract part of accepted project authority:

```text
legacy or automation-capable Blueprint
→ backward-compatible canonical automation storage
→ source-bound typed AutomationEditCandidate
→ stable identity + range + lock + stale validation
→ READY_FOR_PREVIEW or BLOCKED
→ non-canonical Preview
→ explicit Accept / Discard
→ existing M2 revision authority
```

R1 must not yet include Browser automation lanes, audible automation rendering, plug-in mappings or external DAW automation reconciliation.

## Resume authority / 재개 권위

Before R1 substantive work inspect:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M7_AUTOMATION_AUTHORITY.md`
4. `docs/M7_ACCEPTANCE.md`
5. `docs/M7_R0_DECISIONS.md`
6. `evidence/M7_R0_VALIDATION.md`
7. all four M7 automation schemas
8. `src/musica/automation_contracts.py`
9. existing M2 Project/Preview/Accept authority
10. existing M6-R1 source-binding/lock patterns as precedent only
11. `memory/CURRENT_STATE.md`
12. `memory/NEXT_ACTION.md`
13. relevant Issue/PR/exact-head evidence

**Repository evidence remains authoritative over conversation/model memory.**
