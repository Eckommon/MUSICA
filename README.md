# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation**. The accepted Music Blueprint/project revision is creative authority; Music IR and renderer/interchange state are derived or non-canonical.

## Current canonical status / 현재 공식 상태

**M0 → M7-R0 are validated within their explicitly bounded repository claims.**

M6 completed the first exact-note precision-editing tranche. M7-R0 now ratifies the contract/design authority model for explicit continuous automation without claiming runtime integration.

```text
M6-R0  exact-note authority/data model                 VALIDATED — DESIGN
M6-R1  typed exact-note runtime                        VALIDATED — BOUNDED
M6-R2  Browser Studio piano roll                       VALIDATED — BOUNDED
M6-R3  real Chromium exact-note E2E/conflict UX        VALIDATED — BOUNDED
M6-R4  source-bound DAWproject note reconciliation     VALIDATED — BOUNDED
M7-R0  automation authority/data model                 VALIDATED — CONTRACT/DESIGN ONLY
```

### M7-R0 ratified boundary

M7-R0 defines stable backend-independent automation identity and fail-closed proposal contracts:

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

Ratified v0 decisions:

- stable `lane_id` + `point_id` + dotted `parameter_id`;
- canonical scope `project | part`; derived `track_id` is excluded;
- quarter-note-beat time domain;
- explicit `normalized | decibel | hertz | semitone | ratio` units;
- `hold | linear` interpolation only;
- primitive proposals: `INSERT_POINT / DELETE_POINT / MOVE_POINT / SET_VALUE / SET_INTERPOLATION`;
- candidates remain source-bound and `preview_only=true`;
- Browser, Music IR, renderer/plugin and DAW state never gain direct canonical mutation authority.

Durable evidence: `evidence/M7_R0_VALIDATION.md`.

## Exact next bounded milestone / 정확한 다음 마일스톤

> **M7-R1 — Bounded Canonical Automation Runtime & Blueprint Integration**

R1 must implement the smallest safe runtime bridge from the ratified standalone R0 contracts into accepted Blueprint/project authority. It may add:

- backward-compatible Blueprint storage/integration for explicit automation material;
- deterministic canonical material hashing and source binding;
- the five ratified automation point primitives;
- stale-source, identity, range and HARD-lock enforcement;
- non-canonical Preview plus explicit M2 Accept/Discard;
- durable tests/evidence for the trusted core path.

R1 must **not** yet claim Browser automation lanes, audible automation rendering, plug-in/device mapping, DAW automation round-trip, real-time MIDI/OSC or human-subject evidence.

## One state, four depths / 하나의 상태, 네 가지 깊이

- **Direct** — natural-language creation/refinement and audition
- **Shape** — semantic axes, sections, structure and locks
- **Inspect** — exact notes and, after later M7 runtime/UI validation, explicit automation
- **Code** — validated JSON, API/CLI, programmable transforms and evidence

These remain views over one canonical project state, not separate products.

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
Music IR — derived execution state
        ↓
Renderer / Interchange / Evaluation adapters
```

**AI output, Browser state, Music IR mutation, renderer output and external interchange/DAW state are not accepted project state.**

## Validated milestone stack / 검증 마일스톤

| Milestone | Status | Evidence |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4 Browser Studio / Usable MVP | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` → `M4_R3_VALIDATION.md` |
| M5 Rendering / Interchange / Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R1_VALIDATION.md` → `M5_R4_VALIDATION.md` |
| M6 Exact-Note Precision Editing R0→R4 | **VALIDATED — BOUNDED** | `evidence/M6_R0_VALIDATION.md` → `M6_R4_VALIDATION.md` |
| M7-R0 Automation Authority & Canonical Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M7_R0_VALIDATION.md` |
| M7-R1 Canonical Automation Runtime & Blueprint Integration | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate live-provider evidence required |
| Human-subject usability/perceptual evidence | **NOT VALIDATED** | separate study required |

## M7-R0 final evidence / M7-R0 최종 근거

- Issue `#68` — **COMPLETED**
- PR `#69` — **MERGED**
- implementation merge/main: `672ce33ee8b8fe05717ad1a5a0c416714de88d2d`
- final evidence-bearing head: `5b5aeb8c6bee3f8e2d48f41543b5bd5cd33e43ef`
- final M7-R0 workflow: `34791538703` — **SUCCESS**
- final MUSICA CI: `34791538725` — **SUCCESS**
- final artifact ID: `10328327862`
- packaging SHA-256: `1360f29d6568a75e7bcf740e605e37fd1f97df9715bdb7326133047afd2753a5`
- internal manifest SHA-256: `aab674c3953abcbca94d659da4d3627d65a682b4039510f6f6e255e08efee5`
- manifest: **2/2 exact hash + size**
- source/contract hash bindings: **21**
- pre-durable vs successor internal evidence: **3 files / 0 differences**

## Current non-claims / 현재 비주장

MUSICA does not yet validate:

- runtime canonical automation editing or Blueprint integration;
- Browser automation lanes;
- audible automation rendering;
- arbitrary plug-in/mixer/device automation;
- VST/AU/CLAP hosting;
- DAW automation reconciliation;
- real-time MIDI/OSC control;
- arbitrary tempo-map automation;
- live OpenAI API execution;
- human preference/usability or perceptual superiority;
- arbitrary external DAW compatibility;
- waveform/destructive audio editing;
- cloud collaboration or installer/signing.

## Repository as source of truth / Repo 공식 근거

```text
accepted repository tests/artifacts/evidence
> merged specifications/current-state records
> Issue/PR/exact-head CI evidence
> conversation context
> model memory/inference
```

Before substantive M7-R1 work read:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M7_AUTOMATION_AUTHORITY.md`
4. `docs/M7_ACCEPTANCE.md`
5. `docs/M7_R0_DECISIONS.md`
6. `evidence/M7_R0_VALIDATION.md`
7. `schemas/automation-material-v0.schema.json`
8. `schemas/automation-edit-candidate-v0.schema.json`
9. `schemas/automation-authority-result-v0.schema.json`
10. `schemas/automation-lock-v0.schema.json`
11. `src/musica/automation_contracts.py`
12. `memory/CURRENT_STATE.md`
13. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**
