# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M6-R4 — BOUNDED INTERCHANGE NOTE RECONCILIATION: VALIDATED — BOUNDED**

**M6 Precision Editing tranche: COMPLETE within its explicit bounded claims.**

M0→M6-R4 are validated only within their durable repository claims. M6-R4 completes the first precision-editing tranche by proving that one uniquely representable note change from an exact MUSICA-origin DAWproject export can be translated into the existing M6 note authority without granting external interchange state canonical authority.

M0→M6-R4는 영속 repo 근거가 허용하는 제한 범위에서 검증되었습니다. M6-R4는 정확한 MUSICA-origin DAWproject export의 유일하게 표현 가능한 하나의 note 변경을 외부 interchange 상태에 canonical authority를 부여하지 않고 기존 M6 note authority로 환원할 수 있음을 증명하여 첫 precision-editing tranche를 종결합니다.

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

Product promise:

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**

## Canonical milestone ledger / 공식 마일스톤 원장

| Milestone | Status | Durable evidence |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4-R1 Studio Application Service | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` |
| M4-R2 Browser Studio UI | **VALIDATED** | `evidence/M4_R2_VALIDATION.md` |
| M4-R3 Usable MVP / real-browser E2E | **VALIDATED** | `evidence/M4_R3_VALIDATION.md` |
| M5-R1 Renderer Adapter + Audio QA | **VALIDATED** | `evidence/M5_R1_VALIDATION.md` |
| M5-R2 Higher-Fidelity Local Renderer | **VALIDATED — BOUNDED** | `evidence/M5_R2_VALIDATION.md` |
| M5-R3 DAW / Interchange | **VALIDATED — BOUNDED** | `evidence/M5_R3_VALIDATION.md` |
| M5-R4 Comparative Audio Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R4_VALIDATION.md` |
| M6-R0 Exact-Note Authority & Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M6_R0_VALIDATION.md` |
| M6-R1 Exact-Note Runtime | **VALIDATED — BOUNDED CORE RUNTIME** | `evidence/M6_R1_VALIDATION.md` |
| M6-R2 Browser Piano Roll | **VALIDATED — BOUNDED BROWSER INTEGRATION** | `evidence/M6_R2_VALIDATION.md` |
| M6-R3 Real-Browser Exact-Note E2E | **VALIDATED — BOUNDED** | `evidence/M6_R3_VALIDATION.md` |
| M6-R4 Interchange Note Reconciliation | **VALIDATED — BOUNDED** | `evidence/M6_R4_VALIDATION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate live-provider evidence required |
| Human-subject usability/perceptual evidence | **NOT VALIDATED** | separate controlled study required |

## M6-R4 final evidence / M6-R4 최종 근거

- Issue `#65` — **COMPLETED**
- PR `#66` — **MERGED**
- implementation merge/main: `66637f7977782ad01e8060d3c4810095c7b44d19`
- final evidence-bearing exact head: `6927a69a84589da985c5ce37ec4bd80749767ea7`
- final MUSICA CI: `34790028892` — **SUCCESS**
- final M6-R4 evidence: `34790028903` — **SUCCESS**
- final M6-R3 regression: `34790028845` — **SUCCESS**
- final M6-R2 regression: `34790028854` — **SUCCESS**
- final M6-R1 regression: `34790028874` — **SUCCESS**
- final M5-R3 regression: `34790028871` — **SUCCESS**
- final M5-R4 regression: `34790028873` — **SUCCESS**
- final M6-R4 artifact ID: `10328000726`
- final GitHub packaging digest: `sha256:26cd14c67d50023ce2c81cd8257b47dda2a4770ee1e3cc503efd02cf526ecf18`
- internal `manifest.json` SHA-256: `4fd4ae72d9b3a77ab2c5ec4ab973af05d753a7c22aca21c523bd5e9862415d2c`
- manifest binding: **33/33 SHA-256 + byte-size matches**
- strengthened pre-durable vs final extracted evidence tree: **34 files / 0 differences**
- same-head evidence generation A/B: **byte-identical** via permanent `diff -qr` CI gate

## M6-R4 validated authority invariant / M6-R4 검증 권한 불변식

```text
Accepted exact-note Blueprint
→ deterministic Music IR
→ deterministic MUSICA-origin DAWproject export
→ source-bound identity map + normalized baseline
→ optional returned DAWproject
→ inherited safe M5-R3 parse/normalize
→ exact baseline comparison
→ one uniquely provable M6 primitive only
→ typed note-edit-candidate-v0
→ existing M6 source/lock/constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept only
→ existing M2 revision authority
```

Forbidden:

```text
DAW note order/index → stable MUSICA identity
nearest-note heuristic → identity
ambiguous correspondence → guessed candidate
external state → accepted Blueprint
Music IR mutation → accepted Blueprint
interchange provenance → lock bypass
```

Validated R4 properties:

- exact project/revision/Blueprint/exact-timeline/Music-IR/export/baseline hash binding;
- no DAW note array-index authority;
- no nearest-note heuristic identity;
- duplicate lowered signatures fail closed;
- exact normalized exported baseline is authoritative comparison source;
- one primitive only: `MOVE / RESIZE / REPITCH / SET_VELOCITY / DELETE / INSERT`;
- transport, multi-note, multi-field, stale and ambiguous changes fail closed;
- resulting proposal reuses the existing M6 candidate and authority engine;
- HARD stable-note lock remains final authority;
- explicit M2 Accept is required to advance accepted state;
- canonical evidence generation is byte-reproducible.

## Validated capability stack / 검증 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material and deterministic lowering.

### AI Director
Provider-neutral typed proposal boundary is validated offline. Live OpenAI execution is still **NOT VALIDATED**.

### Studio
Local-first Browser Studio with `Direct → Shape → Inspect → Code`, explicit Preview/Accept/Discard, real-browser E2E and exact-note piano-roll editing.

### Renderer / Interchange / Evaluation
Reference and bounded higher-fidelity rendering, DAWproject bounded interchange, paired objective audio evaluation, and now bounded source-bound exact-note reconciliation.

### Precision editing
M6-R0→R4 establishes canonical exact-note authority from contract through runtime, Browser UI, real-browser E2E and narrowly bounded interchange return-path reconciliation.

## Current claim boundaries / 현재 주장 경계

The repository does **not** validate or imply:

- successful live OpenAI API execution;
- human-subject usability or preference evidence;
- perceptual/mastering superiority;
- full professional DAW parity;
- compatibility with every DAW or a tested real external DAW;
- arbitrary DAW reverse mapping;
- non-MUSICA-origin project reconciliation;
- heuristic note correspondence;
- multi-note/batch interchange reconciliation;
- arbitrary polyphonic/every-part exact editing;
- arbitrary tempo maps;
- automation/mixer/plugin/device canonical editing;
- live MIDI recording;
- waveform/destructive audio editing;
- cloud collaboration;
- desktop installer/signing.

## Next phase / 다음 단계

No pre-existing `M6-R5` or `M7` roadmap existed in the repository after M6-R4. The next phase is therefore deliberately opened as a **contract/design milestone**, not as an assumed runtime capability:

> **M7-R0 — Canonical Automation & Continuous-Control Authority / 공식 Automation·연속 제어 권한 모델**

Reason: the product thesis explicitly places automation, synthesis, DSP and mix parameters inside Inspect-level professional control, while current validated authority covers semantic controls and exact notes but not a canonical editable continuous-control timeline.

M7-R0 must first decide what becomes canonical Blueprint authority versus derived Music IR/renderer state, stable parameter identity, time domain, interpolation, lock semantics, source binding, Preview/Accept and backward compatibility. It must not implement automation lanes before these authority questions are ratified.

## Resume authority / 재개 권위

Before substantive work inspect:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
5. `docs/M6_R4_ACCEPTANCE.md`
6. `evidence/M6_R4_VALIDATION.md`
7. `memory/CURRENT_STATE.md`
8. `memory/NEXT_ACTION.md`
9. relevant Issue/PR/exact-head evidence

**Repository evidence remains authoritative over conversation/model memory.**
