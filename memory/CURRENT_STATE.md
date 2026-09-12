# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M6-R2 — BROWSER STUDIO PIANO-ROLL / INSPECT SURFACE: VALIDATED — BOUNDED BROWSER INTEGRATION / M6-R2 — Browser Studio Piano-Roll / Inspect Surface: 제한된 Browser 통합 검증 완료**

M0→M6-R2 are validated within their explicitly bounded claims. M6-R2 exposes the M6-R1 exact-note authority through the local-first Browser Studio Inspect surface while preserving Blueprint/M2 authority above browser state and Music IR.

M0→M6-R2는 각 명시적 제한 주장 범위에서 검증 완료되었습니다. M6-R2는 M6-R1 exact-note 권한을 local-first Browser Studio Inspect surface에 노출하면서 browser state와 Music IR보다 상위에 있는 Blueprint/M2 권한을 유지합니다.

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

Product promise / 제품 약속:

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**
>
> **자연어로 지시할 만큼 쉽고, 전문 음악 시스템처럼 세밀하게 편집할 만큼 정밀해야 한다.**

## Canonical milestone ledger / 공식 마일스톤 원장

| Milestone | Status | Durable evidence / 영속 근거 |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3-R1 Director authority boundary | **VALIDATED** | `evidence/M3_R1_VALIDATION.md` |
| M3-R2 OpenAI adapter contract | **VALIDATED — ADAPTER_CONTRACT_EVIDENCE** | `evidence/M3_R2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | R1 + R2 evidence |
| M4-R1 Studio Application Service | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` |
| M4-R2 Browser Studio UI | **VALIDATED** | `evidence/M4_R2_VALIDATION.md` |
| M4-R3 Usable MVP / real-browser E2E | **VALIDATED** | `evidence/M4_R3_VALIDATION.md` |
| M5-R1 Renderer Adapter Contract + Audio QA Baseline | **VALIDATED** | `evidence/M5_R1_VALIDATION.md` |
| M5-R2 First higher-fidelity local renderer | **VALIDATED — BOUNDED** | `evidence/M5_R2_VALIDATION.md` |
| M5-R3 DAW / interchange interoperability | **VALIDATED — BOUNDED** | `evidence/M5_R3_VALIDATION.md` |
| M5-R4 Comparative music/audio quality evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R4_VALIDATION.md` |
| M6-R0 Precision Editing Authority & Canonical Note Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M6_R0_VALIDATION.md` |
| M6-R1 Typed Exact-Note Material + Edit Engine | **VALIDATED — BOUNDED CORE RUNTIME** | `evidence/M6_R1_VALIDATION.md` |
| M6-R2 Browser Studio Piano-Roll / Inspect Surface | **VALIDATED — BOUNDED BROWSER INTEGRATION** | `evidence/M6_R2_VALIDATION.md` |
| M6-R3 Real-browser exact-note E2E + lock/conflict UX | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| Human-subject usability / perceptual evidence | **NOT VALIDATED** | separate controlled study required |

## M6-R2 final evidence / M6-R2 최종 근거

- Issue `#57` — **COMPLETED**
- PR `#58` — **MERGED**
- final evidence-bearing exact head: `546ce59f6264d36af18064e2b2f1b522a969dda1`
- final MUSICA CI: `34694194134` — **SUCCESS**
- final M6-R2 evidence: `34694193980` — **SUCCESS**
- final M6-R1 regression: `34694193939` — **SUCCESS**
- final M5-R3 regression: `34694193938` — **SUCCESS**
- final M5-R4 regression: `34694194059` — **SUCCESS**
- Python 3.11 contracts/runtime job: `103554723708` — **SUCCESS**
- Python 3.12 contracts/runtime + prior evidence chain job: `103554723673` — **SUCCESS**
- M4-R3 real Chromium browser regression job: `103554723704` — **SUCCESS**
- M5-R2 Windows FluidSynth regression job: `103554723690` — **SUCCESS**
- final M6-R2 artifact: `musica-m6-r2-piano-roll`
- final artifact ID: `10298037150`
- GitHub packaging digest: `sha256:8fcb32ca8dc7718199e5fb0092617967446509a3793b7d00585880fd1c042cc9`
- internal `manifest.json` SHA-256: `6e97d79b19248b03d2fe705223fb5f3c5de7ff95a2d80ef279e7fd86a8b27b7e`
- final evidence-bearing artifact vs strengthened pre-durable artifact: **59 files / 0 differences**
- implementation merge: `4fc186168a2c6d6b91ed0d842476f9fed9586ba6`
- durable evidence: `evidence/M6_R2_VALIDATION.md`

The final evidence-bearing artifact was independently downloaded and inspected after the durable validation record was added. Its complete 59-file evidence tree was byte-identical to the strengthened pre-durable artifact. All 13 manifest-bound files matched declared SHA-256 and byte size.

Durable validation 문서를 포함한 최종 evidence-bearing artifact를 독립 다운로드·검사했으며, 59개 전체 evidence tree가 강화된 pre-durable artifact와 byte-identical했습니다. Manifest가 결박한 13개 파일의 SHA-256과 byte size도 모두 일치했습니다.

The strengthened determinism proof contains two independently materialized Studio `note_view()` reads:

```text
source-note-view.json
source-note-view-repeat.json
```

Both are byte-identical with SHA-256:

`fbeb40af823865f99f388c2af1578f1c40e2b2b511d38fc411f0763905df3df0`

Accepted and reopened note views are also byte-identical with SHA-256:

`c26ec5b54ef9a80f466f80f45149846cd99aa06b4b007c48b4d6d3dbaf6e100d`

## M6-R2 validated authority invariant / M6-R2 검증 권한 불변식

```text
Accepted exact-note Blueprint revision
→ deterministic Studio note-view projection
→ Browser Studio Inspect piano roll
→ bounded browser edit controls
→ typed NoteEditCandidate
→ exact project/revision/Blueprint-hash binding
→ M6-R1 stable-ID lock/constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW — non-canonical
→ explicit Accept / Discard
→ existing M2 commit_revision only
→ accepted exact-note Blueprint revision
→ deterministic lowering
→ Music IR
```

Forbidden / 금지:

```text
DOM/canvas/browser-local note array → accepted project state
Music IR direct mutation → accepted project state
blocked authority result → pending Preview
browser edit gesture → implicit Accept
```

Validated bounded Browser integration properties:

- dedicated schema-validated `studio-note-view-v0` projection;
- deterministic `GET /v0/sessions/{id}/notes` accepted-note read boundary;
- `POST /v0/sessions/{id}/preview/notes` delegates to M6-R1 authority;
- stable note identity and stable-ID HARD-lock visibility;
- Inspect piano-roll surface with accepted vs `PREVIEW · NOT ACCEPTED` distinction;
- browser-accessible `INSERT / DELETE / MOVE / RESIZE / REPITCH / SET_VELOCITY` controls;
- exact project/revision/Blueprint SHA-256 source binding;
- stale source fail-closed as `BLOCKED / STALE_SOURCE` with no pending Preview;
- stable-ID HARD lock fail-closed as `BLOCKED / HARD_LOCK_VIOLATION` with no pending Preview;
- explicit Accept through existing Studio/M2 path only;
- accepted exact-note state survives reopen;
- legacy motif-only projects expose `exact_note_editing_available=false` and fabricate no canonical notes;
- same-origin packaged JS/CSS and existing loopback/CSP/no-upload/no-telemetry boundaries preserved;
- browser and Music IR canonical mutation authority remain false.

## Validated capability stack / 검증된 기능 스택

### Music authority core
Typed Intent / Blueprint / Semantic Control / exact-note material / Music IR contracts, deterministic lowering, bounded semantic control, fail-closed locks/constraints, immutable accepted revisions, branches and audit chain.

### AI Director
Provider-neutral typed proposal boundary with user-intent precedence and no direct accepted-state mutation. OpenAI adapter contract is validated offline; live execution remains **NOT VALIDATED**.

### Studio
Local-first Browser Studio with `Direct → Shape → Inspect → Code`, explicit Preview/Accept/Discard, visible locks/diff/history/export, existing real Chromium Studio E2E evidence, and now a bounded exact-note piano-roll / Inspect integration over the trusted M6-R1 engine.

### Renderer / Interchange / Evaluation
Reference renderer, bounded FluidSynth renderer evidence, bounded DAWproject interchange, and exact-source objective audio comparison. These remain non-canonical output/evidence boundaries.

### Precision editing
M6-R1 validates the core exact-note edit authority. M6-R2 validates the deterministic Browser Studio service/UI integration over that authority. Full real-browser exact-note interaction and conflict UX are intentionally reserved for M6-R3.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- successful live OpenAI API execution;
- human-subject usability/perceptual evidence;
- perceptual superiority or professional/mastering audio quality;
- VST/AU/CLAP hosting;
- successful real external DAW smoke or universal DAW compatibility;
- real-browser end-to-end exact-note edit acceptance across all six operations;
- real-browser pointer drag/move/resize behavior as an evidence-backed claim;
- real-browser HARD-lock/stale-source conflict UX as validated behavior;
- full professional DAW piano-roll parity;
- arbitrary polyphonic or every-instrument-part exact editing;
- arbitrary tempo-map editing;
- arbitrary DAW reverse mapping into accepted exact-note state;
- live MIDI recording;
- waveform/destructive audio editing;
- arbitrary automation/mixer fidelity;
- cloud collaboration or desktop installer/signing.

## Next phase / 다음 단계

The exact next bounded mission is **M6-R3 — Real-browser exact-note E2E + lock/conflict UX**.

정확한 다음 제한 mission은 **M6-R3 — 실제 Browser Exact-Note E2E + Lock/Conflict UX**입니다.

M6-R3 must prove the already implemented R2 path through a real Chromium browser and make fail-closed authority conflicts visible without moving canonical authority into the browser:

```text
accepted exact-note material
→ deterministic Studio note view
→ real Browser Studio Inspect piano roll
→ browser edit interaction
→ typed NoteEditCandidate
→ M6-R1 authority
→ PREVIEW · NOT ACCEPTED or BLOCKED
→ visible/audible inspection
→ explicit Accept / Discard
→ existing M2 authority
→ refresh/reopen persistence proof
```

R3 is an E2E/evidence and bounded UX milestone. It is not a new authority model and must not introduce browser-owned canonical state, implicit acceptance, or direct Music IR mutation.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
4. `docs/M6_ACCEPTANCE.md`
5. `docs/M6_R1_RUNTIME.md`
6. `schemas/exact-note-material-v0.schema.json`
7. `schemas/note-edit-candidate-v0.schema.json`
8. `schemas/note-edit-authority-result-v0.schema.json`
9. `schemas/exact-note-lock-v0.schema.json`
10. `schemas/studio-note-view-v0.schema.json`
11. `src/musica/note_edit.py`
12. `src/musica/studio.py`
13. `src/musica/studio_http.py`
14. `src/musica/studio_web/app.js`
15. `src/musica/studio_web/app.css`
16. `evidence/M6_R1_VALIDATION.md`
17. `evidence/M6_R2_VALIDATION.md`
18. existing M4-R3 browser E2E harness/evidence
19. this file / 본 파일
20. `memory/NEXT_ACTION.md`
21. relevant Issue/PR/exact-head CI evidence / 관련 Issue·PR·exact-head CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
