# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M6-R3 — REAL-BROWSER EXACT-NOTE E2E + LOCK/CONFLICT UX: VALIDATED — BOUNDED REAL-BROWSER EXACT-NOTE E2E / M6-R3 — 실제 Browser Exact-Note E2E + Lock/Conflict UX: 제한된 real-browser exact-note E2E 검증 완료**

M0→M6-R3 are validated within their explicitly bounded claims. M6-R3 proves the M6-R2 exact-note Browser Studio path through real Chromium while preserving Blueprint/M2 authority above browser state, DAW/interchange state and Music IR.

M0→M6-R3는 각 명시적 제한 주장 범위에서 검증 완료되었습니다. M6-R3는 M6-R2 exact-note Browser Studio 경로를 실제 Chromium에서 증명했으며 browser state, DAW/interchange state, Music IR보다 상위에 있는 Blueprint/M2 권한을 유지합니다.

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
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4-R1 Studio Application Service | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` |
| M4-R2 Browser Studio UI | **VALIDATED** | `evidence/M4_R2_VALIDATION.md` |
| M4-R3 Usable MVP / real-browser E2E | **VALIDATED** | `evidence/M4_R3_VALIDATION.md` |
| M5-R1 Renderer Adapter Contract + Audio QA Baseline | **VALIDATED** | `evidence/M5_R1_VALIDATION.md` |
| M5-R2 First Higher-Fidelity Local Renderer | **VALIDATED — BOUNDED** | `evidence/M5_R2_VALIDATION.md` |
| M5-R3 DAW / Interchange Interoperability | **VALIDATED — BOUNDED** | `evidence/M5_R3_VALIDATION.md` |
| M5-R4 Comparative Music/Audio Quality Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R4_VALIDATION.md` |
| M6-R0 Precision Editing Authority & Canonical Note Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M6_R0_VALIDATION.md` |
| M6-R1 Typed Exact-Note Material + Edit Engine | **VALIDATED — BOUNDED CORE RUNTIME** | `evidence/M6_R1_VALIDATION.md` |
| M6-R2 Browser Studio Piano-Roll / Inspect Surface | **VALIDATED — BOUNDED BROWSER INTEGRATION** | `evidence/M6_R2_VALIDATION.md` |
| M6-R3 Real-browser Exact-Note E2E + Lock/Conflict UX | **VALIDATED — BOUNDED REAL-BROWSER EXACT-NOTE E2E** | `evidence/M6_R3_VALIDATION.md` |
| M6-R4 Bounded interchange reconciliation for representable exact-note edits | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| Human-subject usability/perceptual evidence | **NOT VALIDATED** | separate controlled study required |

## M6-R3 final evidence / M6-R3 최종 근거

- Issue `#60` — **COMPLETED**
- PR `#61` — **MERGED**
- final evidence-bearing exact head: `c4b525a9083ff8a537b411789b8bbfbf39c04a7b`
- final MUSICA CI: `34720643018` — **SUCCESS**
- final M6-R3 real-browser evidence: `34720643011` — **SUCCESS**
- final M6-R2 regression: `34720643012` — **SUCCESS**
- final M6-R1 regression: `34720642999` — **SUCCESS**
- final M5-R3 regression: `34720643007` — **SUCCESS**
- final M5-R4 regression: `34720643001` — **SUCCESS**
- Python 3.11 contracts/runtime job: `103625731654` — **SUCCESS**
- Python 3.12 contracts/runtime + prior evidence chain job: `103625731656` — **SUCCESS**
- M4-R3 real Chromium regression job: `103625731545` — **SUCCESS**
- M5-R2 Windows FluidSynth regression job: `103625731661` — **SUCCESS**
- final M6-R3 artifact: `musica-m6-r3-real-browser-note-e2e`
- final artifact ID: `10305989929`
- GitHub packaging digest: `sha256:2e44021ddd2a2803379f2223b045463d1a81c334afdb695d10df9b8fc5d914c0`
- internal `manifest.json` SHA-256: `825c5d69f55a40ba77deefe1bdb3bba4974f0ed26d0cf1696aa11718dcff58ec`
- 18/18 top-level manifest records independently rehashed with exact hash/size match
- pre-durable and evidence-bearing `proof.json` objects: **semantically identical**
- implementation merge/main: `327939e71bd63611f747bac147c4ba6591052b93`
- durable evidence: `evidence/M6_R3_VALIDATION.md`

## M6-R3 validated authority invariant / M6-R3 검증 권한 불변식

```text
Accepted exact-note Blueprint
→ deterministic Studio note view
→ real Chromium Browser Studio Inspect piano roll
→ visible browser interaction / exact numeric input
→ typed source-bound NoteEditCandidate
→ M6-R1 source + stable-ID lock + constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept / Discard
→ existing M2 authority only
→ accepted exact-note Blueprint revision
→ restart/reopen persistence
```

Forbidden / 금지:

```text
DOM/canvas/browser-local state → accepted project
Music IR mutation → accepted project
blocked authority result → pending Preview
browser edit gesture → implicit Accept
stale candidate → silent rebase/accept
```

Validated M6-R3 properties:

- real Chromium/Playwright Browser Studio execution;
- exact source binding to project/revision/Blueprint SHA-256;
- all six operations exercised through browser-accessible controls: `INSERT / DELETE / MOVE / RESIZE / REPITCH / SET_VELOCITY`;
- valid operations produce non-canonical `READY_FOR_PREVIEW` state;
- accepted ref remains unchanged before explicit Accept;
- Discard preserves accepted state;
- explicit Accept advances exactly once through existing M2 authority;
- accepted REPITCH survives service restart and browser reopen;
- stable-ID HARD lock is visibly `BLOCKED / HARD_LOCK_VIOLATION` with note/rule context and no pending Preview;
- stale Browser source is visibly `BLOCKED / STALE_SOURCE` with no pending Preview or silent rebase;
- legacy motif-only projects remain read-only for exact editing and fabricate no canonical notes;
- browser console error count = `0` and page error count = `0` in canonical evidence;
- browser and Music IR direct project mutation authority remain `false`.

## M6-R3 defect closure / M6-R3 결함 종결

The first real-browser gate exposed a latent Browser Studio integration defect: `app.js` requested `GET /v0/sessions/{id}/preview`, but the HTTP bridge had no read route, producing six browser-console `404` errors.

M6-R3 did not suppress those errors. It implemented the missing read-only Preview-detail endpoint and permanent regression coverage:

```text
existing session + pending Preview → 200 descriptor/diff/detail
existing session + no pending Preview → 200 explicit empty state
unknown session → 404 fail-closed
```

Post-fix diagnostic evidence recorded zero HTTP errors and zero browser console errors; the temporary diagnostic harness was removed before the clean implementation head.

## Validated capability stack / 검증된 기능 스택

### Music authority core
Typed Intent / Blueprint / Semantic Control / exact-note material / Music IR contracts, deterministic lowering, bounded semantic control, fail-closed locks/constraints, immutable accepted revisions, branches and audit chain.

### AI Director
Provider-neutral typed proposal boundary with user-intent precedence and no direct accepted-state mutation. OpenAI adapter contract is validated offline; live provider execution remains **NOT VALIDATED**.

### Studio
Local-first Browser Studio with `Direct → Shape → Inspect → Code`, explicit Preview/Accept/Discard, locks/diff/history/export, real-browser E2E, and a validated exact-note piano-roll path through the trusted M6 authority engine.

### Renderer / Interchange / Evaluation
Reference renderer, bounded FluidSynth renderer, bounded DAWproject 1.0 interchange, and exact-source objective audio comparison. External interchange artifacts remain non-canonical candidate carriers/evidence.

### Precision editing
M6-R1 validates exact-note core authority, M6-R2 validates Browser Studio integration, and M6-R3 validates the bounded real-browser six-operation journey, conflict UX and restart/reopen persistence.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- successful live OpenAI API execution;
- human-subject usability/perceptual evidence;
- perceptual superiority or professional/mastering audio quality;
- VST/AU/CLAP hosting;
- successful real external DAW smoke or universal DAW compatibility;
- full professional DAW piano-roll parity;
- arbitrary polyphonic/every-instrument-part exact editing;
- arbitrary tempo-map editing;
- general quantize/humanize/batch transformations;
- arbitrary DAW reverse mapping into accepted exact-note state;
- arbitrary external note edits becoming canonical;
- live MIDI recording;
- waveform/destructive audio editing;
- arbitrary automation/mixer fidelity;
- cloud collaboration or desktop installer/signing.

## Next phase / 다음 단계

The exact next bounded mission is **M6-R4 — bounded interchange reconciliation for representable exact-note edits**.

정확한 다음 제한 mission은 **M6-R4 — 표현 가능한 exact-note 편집의 제한된 interchange reconciliation**입니다.

R4 must reconcile the historically correct M5-R3 external-note `UNSUPPORTED_BLOCKING` boundary with the exact-note authority introduced by M6 without granting DAW/interchange state canonical authority:

```text
MUSICA accepted exact-note Blueprint
→ deterministic M5-R3 bounded DAWproject export
→ exact source/provenance + stable identity mapping
→ bounded external note change
→ parse + compare against exact exported source
→ representability/identity/source preflight
→ typed NoteEditCandidate primitives only
→ M6-R1 authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept / Discard
→ existing M2 authority only
```

R4 is **not** arbitrary DAW reverse mapping. Only changes whose source lineage, stable identity mapping, supported part/timing semantics and primitive M6 operation representation are provable may become a NoteEditCandidate. Unsupported, ambiguous, stale, lock-conflicting or provenance-broken changes must fail closed.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
4. `docs/M6_ACCEPTANCE.md`
5. `docs/M6_R1_RUNTIME.md`
6. `docs/M5_R3_ACCEPTANCE.md`
7. `docs/M5_R3_ROUNDTRIP_AUTHORITY.md`
8. `evidence/M5_R3_VALIDATION.md`
9. `schemas/exact-note-material-v0.schema.json`
10. `schemas/note-edit-candidate-v0.schema.json`
11. `schemas/note-edit-authority-result-v0.schema.json`
12. `schemas/exact-note-lock-v0.schema.json`
13. `schemas/studio-note-view-v0.schema.json`
14. `src/musica/note_edit.py`
15. M5-R3 DAWproject exporter/importer implementation
16. `evidence/M6_R1_VALIDATION.md`
17. `evidence/M6_R2_VALIDATION.md`
18. `evidence/M6_R3_VALIDATION.md`
19. this file / 본 파일
20. `memory/NEXT_ACTION.md`
21. relevant Issue/PR/exact-head CI evidence / 관련 Issue·PR·exact-head CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
