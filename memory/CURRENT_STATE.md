# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M7-R2 — BROWSER STUDIO AUTOMATION INSPECT/EDIT SURFACE: VALIDATED — BOUNDED REAL-BROWSER SURFACE**

M0→M7-R2 are validated only within their durable repository claims. M7-R2 exposes accepted canonical automation through Browser Studio without creating a second authority model. Browser, Music IR, renderer/plugin and external DAW state remain non-authoritative.

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
| M7-R3 Deterministic Automation Lowering & Derived Execution Boundary | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |

## M7-R2 final evidence / M7-R2 최종 근거

- Issue `#74` — **COMPLETED**
- PR `#75` — **MERGED**
- implementation merge/main: `b5f73ac8ebf83b0bfdcca277924af9b7c0fcc263`
- pre-durable exact head: `5396d38dad12247d8c55a40d677738fc51357569`
- final evidence-bearing successor head: `90b6d3eec6621cd2d666c544863d1c8e28fd145f`
- successor M7-R2 `34798196898` — **SUCCESS**
- successor MUSICA CI `34798196910` — **SUCCESS**
- successor M7-R1 `34798196888` — **SUCCESS**
- successor M7-R0 `34798196884` — **SUCCESS**
- successor M6-R4 `34798196893` — **SUCCESS**
- successor M6-R3 `34798196887` — **SUCCESS**
- successor M6-R2 `34798196909` — **SUCCESS**
- successor M6-R1 `34798196960` — **SUCCESS**
- successor M5-R3 `34798196949` — **SUCCESS**
- successor M5-R4 `34798196938` — **SUCCESS**
- successor artifact ID `10330402763`
- packaging SHA-256 `dd192e04c12ce9d8f7e474717ac365acc0d2fb00ba2b8d9e5e4ea4cbe9d67ef2`
- internal manifest SHA-256 `c3a4026394408b266943d3f9aca15393112780cf13114efd8f8a56b3e520f133`
- manifest records: **19/19 exact hash + size matches**
- pre-durable vs successor `proof.json`: **identical**

## M7-R2 validated authority invariant

```text
accepted optional materials.automation
→ deterministic source/material hashes
→ Browser Inspect stable-ID projection
→ bounded keyboard/form/table point proposal
→ automation-edit-candidate-v0
→ existing M7-R1 authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit M2 Accept or Discard
```

Validated R2 properties:

- no automation is fabricated for legacy projects;
- source binding includes project/revision/Blueprint/material hashes;
- `lane_id`, `point_id`, `parameter_id` remain authority identities;
- all five point primitives are exercised in real Chromium;
- Browser geometry/DOM ordering is not canonical identity;
- Preview does not advance accepted project state;
- explicit Accept advances once and survives restart/reopen;
- Discard preserves accepted ref;
- HARD exact and HARD presence conflicts visibly fail closed;
- stale Browser source visibly fails closed and reprojects current accepted source;
- cross-surface Preview replacement is blocked;
- Browser console/page errors are zero;
- Browser/project/Music IR mutation capability flags remain false until explicit authority boundary;
- `audible_automation_validated=false` remains explicit.

## Current capability stack / 현재 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material and accepted explicit automation material.

### Precision editing
M6 exact-note editing and M7-R1/R2 automation point editing share source-bound Preview/Accept authority patterns.

### Studio
Browser Studio Direct → Shape → Inspect → Code, exact-note piano roll and bounded canonical automation Inspect editing are validated.

### Renderer / interchange
Existing bounded rendering, DAWproject interchange/evaluation and exact-note reconciliation remain validated. Canonical automation is **not yet lowered through a backend-independent derived execution contract and is not yet validated as audible renderer control**.

## Important post-R2 architecture finding

Current `music-ir-v0` control events are MIDI-controller-specific (`controller` + 7-bit `value`). Existing semantic preview lowering uses CC11/74/71, and the local WAV renderer interprets those specific CCs.

Canonical automation, however, uses backend-independent `parameter_id` + explicit unit/scope. Therefore the next phase must not directly map every canonical lane to arbitrary MIDI CC or renderer address. Doing so would collapse canonical identity into a backend implementation detail.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate:

- backend-independent deterministic lowering of canonical automation;
- audible renderer execution of canonical automation;
- plug-in/device mapping or VST/AU/CLAP hosting;
- external DAW automation reconciliation;
- arbitrary tempo maps or spline/bezier curves;
- lane creation/deletion or parameter reassignment;
- real-time MIDI/OSC automation;
- live OpenAI provider execution;
- human-subject usability/preference or perceptual superiority;
- waveform/destructive audio editing, cloud collaboration or desktop signing.

## Next phase / 다음 단계

> **M7-R3 — Deterministic Automation Lowering & Derived Execution Boundary**

R3 must introduce a derived, non-authoritative execution representation that preserves canonical source identity while separating backend-independent `parameter_id` from backend-specific MIDI CC/plugin/renderer addresses.

Required path:

```text
accepted automation material
→ exact source binding
→ deterministic derived automation execution representation
→ explicit point/lane/parameter provenance
→ deterministic beat/time/interpolation representation
→ explicit supported/unsupported mapping state
```

No audible renderer claim is required in R3. Renderer-specific application and audio-difference evidence should be a subsequent bounded milestone after R3 is validated.

## Resume authority / 재개 권위

Before R3 substantive work inspect:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M7_AUTOMATION_AUTHORITY.md`
4. `evidence/M7_R2_VALIDATION.md`
5. `schemas/automation-material-v0.schema.json`
6. `schemas/music-ir-v0.schema.json`
7. `src/musica/automation_contracts.py`
8. `src/musica/compiler.py`
9. `src/musica/render.py`
10. `src/musica/renderer.py`
11. `memory/CURRENT_STATE.md`
12. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**
