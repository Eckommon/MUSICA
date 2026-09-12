# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M6-R1 — TYPED EXACT-NOTE MATERIAL + EDIT ENGINE: VALIDATED — BOUNDED CORE RUNTIME / M6-R1 — Typed Exact-Note Material + Edit Engine: 제한된 core runtime 검증 완료**

M0→M6-R1 are validated within their explicitly bounded claims. M6-R1 turns the ratified M6-R0 exact-note authority contract into executable trusted-core behavior while preserving Blueprint/M2 authority above Music IR.

M0→M6-R1은 각 명시적 제한 주장 범위에서 검증 완료되었습니다. M6-R1은 M6-R0의 exact-note 권한 계약을 trusted core 실행 동작으로 구현하면서 Blueprint/M2의 Music IR 상위 권한을 유지합니다.

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
| M6-R2 Browser Studio Piano-Roll / Inspect Surface | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| Human-subject usability / perceptual evidence | **NOT VALIDATED** | separate controlled study required |

## M6-R1 final evidence / M6-R1 최종 근거

- Issue `#54` — **COMPLETED**
- PR `#55` — **MERGED**
- final evidence-bearing exact head: `4cff9ae28bcaa49ac4c96019d4d0d4e47b773857`
- final MUSICA CI: `34691729996` — **SUCCESS**
- final M6-R1 evidence: `34691730003` — **SUCCESS**
- final M5-R3 regression: `34691730001` — **SUCCESS**
- final M5-R4 regression: `34691730000` — **SUCCESS**
- final M6-R1 artifact: `musica-m6-r1-exact-note-edit`
- final artifact ID: `10297550295`
- GitHub packaging digest: `sha256:585df28c91652d7965de898c32ba568ddb0eb5c0b9abb164a4f45387378f7020`
- internal `manifest.json` SHA-256: `4f00c0da286c0b62d00a9bfe98e0ea33a8f8cfdb0945803fe1574b21daf66bcc`
- final merge: `7adf507630334021459e89055e98627d184f5354`
- durable evidence: `evidence/M6_R1_VALIDATION.md`

The final evidence-bearing artifact was inspected after the durable validation record was added. Its internal manifest hash remained byte-identical to the prior independent evidence runs, and all positive/negative authority proofs remained unchanged.

Durable validation 문서를 포함한 최종 evidence-bearing artifact를 다시 검사했으며, 내부 manifest hash는 이전 독립 실행과 byte-identical하게 유지되었고 모든 양성/음성 권한 증명이 동일하게 유지되었습니다.

## M6-R1 validated authority invariant / M6-R1 검증 권한 불변식

```text
Accepted Blueprint revision
→ trusted lowering
→ Music IR

NoteEditCandidate
→ exact project/revision/Blueprint-hash binding
→ stable-ID operation application
→ exact-note invariant validation
→ stable-ID HARD note-lock + existing lock/constraint validation
→ READY_FOR_PREVIEW — non-canonical
→ explicit Accept only
→ existing M2 commit_revision
→ new accepted Blueprint revision
→ trusted deterministic lowering
→ new Music IR
```

Forbidden / 금지:

```text
Music IR direct mutation → accepted project state
```

Validated bounded runtime properties:

- optional `materials.melody.exact_timeline` with legacy `motif_notes` compatibility;
- stable `note_id + part_id` addressing;
- fixed-tempo bounded exact-note validation;
- deterministic beat→PPQ lowering;
- faithful exact pitch/start/duration/velocity lowering without hidden semantic scaling;
- typed operations `INSERT / DELETE / MOVE / RESIZE / REPITCH / SET_VELOCITY`;
- stale source fail-closed by exact project/revision/Blueprint SHA-256 binding;
- deterministic stable-note diff/provenance;
- stable-ID HARD note locks enforced both in note-edit preflight and `validate_revision()`;
- side-effect-free Preview;
- explicit M2 acceptance as the only canonical project mutation path;
- deterministic candidate and accepted compilation;
- M2 project integrity after acceptance.

## Validated capability stack / 검증된 기능 스택

### Music authority core
Typed Intent / Blueprint / Semantic Control / exact-note material / Music IR contracts, deterministic lowering, bounded semantic control, fail-closed locks/constraints, immutable accepted revisions, branches and audit chain.

### AI Director
Provider-neutral typed proposal boundary with user-intent precedence and no direct accepted-state mutation. OpenAI adapter contract is validated offline; live execution remains **NOT VALIDATED**.

### Studio
Local-first Browser Studio with `Direct → Shape → Inspect → Code`, explicit Preview/Accept/Discard, visible locks/diff/history/export, and real Chromium E2E evidence.

### Renderer / Interchange / Evaluation
Reference renderer, bounded FluidSynth renderer evidence, bounded DAWproject interchange, and exact-source objective audio comparison. These remain non-canonical output/evidence boundaries.

### Precision editing core
M6-R1 now validates bounded exact-note material, stable-ID edit candidates, note-specific HARD-lock enforcement, stale-source failure, non-canonical Preview and explicit M2 acceptance. Browser piano-roll interaction is not yet validated.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- successful live OpenAI API execution;
- human-subject usability/perceptual evidence;
- perceptual superiority or professional/mastering audio quality;
- VST/AU/CLAP hosting;
- successful real external DAW smoke or universal DAW compatibility;
- Browser Studio piano-roll editing;
- real-browser drag/move/resize/repitch/velocity note interaction;
- arbitrary polyphonic or every-instrument-part exact editing;
- arbitrary tempo-map editing;
- arbitrary DAW reverse mapping into accepted exact-note state;
- live MIDI recording;
- waveform/destructive audio editing;
- arbitrary automation/mixer fidelity;
- cloud collaboration or desktop installer/signing.

## Next phase / 다음 단계

The exact next bounded mission is **M6-R2 — Browser Studio Piano-Roll / Inspect Surface**.

정확한 다음 제한 mission은 **M6-R2 — Browser Studio Piano-Roll / Inspect Surface**입니다.

M6-R2 must expose the already validated M6-R1 authority path through the existing local-first Studio boundary without granting the browser direct canonical mutation authority:

```text
accepted exact-note material
→ Studio read projection
→ piano-roll Inspect view
→ typed NoteEditCandidate
→ M6-R1 authority result
→ PREVIEW — non-canonical
→ audible/diff inspection
→ explicit Accept / Discard
→ existing M2 authority
```

R2 is a Browser Studio integration/UI milestone, not a new authority model. Browser state, DOM state, canvas coordinates and Music IR remain non-canonical.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
4. `docs/M6_ACCEPTANCE.md`
5. `docs/M6_R1_RUNTIME.md`
6. `schemas/exact-note-material-v0.schema.json`
7. `schemas/note-edit-candidate-v0.schema.json`
8. `schemas/exact-note-lock-v0.schema.json`
9. `src/musica/note_edit.py`
10. `src/musica/studio.py`
11. `evidence/M6_R1_VALIDATION.md`
12. this file / 본 파일
13. `memory/NEXT_ACTION.md`
14. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
