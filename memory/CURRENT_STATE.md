# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M6-R0 — PRECISION EDITING AUTHORITY & CANONICAL NOTE MODEL v0: VALIDATED — CONTRACT/DESIGN ONLY / M6-R0 — 정밀 편집 권한 및 공식 Note Model v0: 계약·설계 범위 검증 완료**

M0→M6-R0 are validated within their explicitly bounded claims. M6-R0 adds an accepted authority/data contract for exact note-level creative decisions without promoting Music IR to canonical project authority.

M0→M6-R0는 각 명시적 제한 주장 범위에서 검증 완료되었습니다. M6-R0는 Music IR을 공식 프로젝트 권한으로 승격하지 않으면서 exact note-level 창작 결정을 표현·편집하기 위한 승인된 권한/데이터 계약을 추가했습니다.

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
| M6-R1 Typed Exact-Note Material + Edit Engine | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| Human-subject usability / perceptual evidence | **NOT VALIDATED** | separate controlled study required |

## M6-R0 final evidence / M6-R0 최종 근거

- Issue `#51` — **COMPLETED**
- PR `#52` — **MERGED**
- governing docs: `docs/M6_PRECISION_EDITING_AUTHORITY.md`, `docs/M6_ACCEPTANCE.md`
- machine contracts:
  - `schemas/exact-note-material-v0.schema.json`
  - `schemas/note-edit-candidate-v0.schema.json`
  - `schemas/note-edit-authority-result-v0.schema.json`
- contract tests: `tests/test_m6_r0_contract.py`
- first final-design exact head: `3e37e8eda72c6dadd3663915a4010e2899f8fff4`
- durable-evidence exact head: `7bd51827913bd9dec62b8f452ac37f508bd54dfe`
- final full MUSICA CI: `34688992955` — **SUCCESS**
- final M5-R3 regression: `34688993005` — **SUCCESS**
- final M5-R4 paired regression: `34688992941` — **SUCCESS**
- merge: `9a7beb133c4094d16a58466e97baec831ea98a01`
- durable evidence: `evidence/M6_R0_VALIDATION.md`

M6-R0 validates the contract/design boundary only. It does **not** claim that the exact-note edit engine, stable-ID note-lock runtime, or piano-roll UI is implemented.

## M6-R0 authority invariant / M6-R0 권한 불변식

```text
Accepted Blueprint revision
→ trusted lowering
→ Music IR

User exact-note edit
→ typed NoteEditCandidate
→ source revision/hash validation
→ Blueprint-representable candidate
→ HARD lock / constraint validation
→ PREVIEW — non-canonical
→ explicit Accept only
→ new M2 revision
→ trusted lowering
→ new Music IR
```

Forbidden / 금지:

```text
Music IR direct mutation → accepted project state
```

R0 also fixes these design decisions:

- legacy `motif_notes` remains backward compatible;
- exact-note material is additive via `explicit_timeline`;
- canonical exact-note time uses quarter-note beat coordinates; ticks/seconds are derived;
- notes use stable `note_id + part_id` addressing, never array-index authority;
- candidates bind to exact project/revision/Blueprint hash and stale sources fail closed;
- exact pitch/start/duration/velocity must lower faithfully rather than being silently semantic-scaled;
- project mutation and Music IR mutation are never authorized by a note-edit candidate itself;
- note-specific stable HARD-lock runtime remains unimplemented until M6-R1 adds an ID-aware selector.

## Validated capability stack / 검증된 기능 스택

### Music authority core
Typed Intent / Blueprint / Semantic Control / Music IR contracts, deterministic lowering, bounded semantic control, fail-closed locks/constraints, immutable accepted revisions, branches and audit chain.

### AI Director
Provider-neutral typed proposal boundary with user-intent precedence and no direct accepted-state mutation. OpenAI adapter contract is validated offline; live execution remains **NOT VALIDATED**.

### Studio
Local-first Browser Studio with `Direct → Shape → Inspect → Code`, explicit Preview/Accept/Discard, visible locks/diff/history/export, and real Chromium E2E evidence.

### Renderer / Interchange / Evaluation
Reference renderer, bounded FluidSynth renderer evidence, bounded DAWproject interchange, and exact-source objective audio comparison. These remain non-canonical output/evidence boundaries.

### Precision editing contract
M6-R0 now defines exact-note material, typed edit candidates, authority results, stable-ID addressing, stale-source failure, and explicit-accept authority. Runtime implementation begins in M6-R1.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- successful live OpenAI API execution;
- human-subject usability/perceptual evidence;
- perceptual superiority or professional/mastering audio quality;
- VST/AU/CLAP hosting;
- successful real external DAW smoke or universal DAW compatibility;
- implemented exact-note edit runtime;
- implemented stable-ID note-specific HARD-lock selector;
- implemented piano-roll professional editing UI;
- arbitrary automation/mixer fidelity;
- cloud collaboration or desktop installer/signing.

## Next phase / 다음 단계

The exact next bounded mission is **M6-R1 — Typed Exact-Note Material + Edit Engine**.

정확한 다음 제한 mission은 **M6-R1 — Typed Exact-Note Material + Edit Engine**입니다.

M6-R1 must turn the accepted R0 contracts into executable runtime behavior without changing authority semantics:

```text
R0 schemas
→ Blueprint exact-note validation
→ candidate preflight
→ stable-ID operation application
→ HARD lock/constraint conflict evaluation
→ non-canonical preview candidate
→ explicit M2 accept
→ exact deterministic compile
```

The first implementation target is the backend/core engine. Piano-roll UI work belongs to M6-R2 after R1 proves the authority path.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
4. `docs/M6_ACCEPTANCE.md`
5. `schemas/exact-note-material-v0.schema.json`
6. `schemas/note-edit-candidate-v0.schema.json`
7. `schemas/note-edit-authority-result-v0.schema.json`
8. `evidence/M6_R0_VALIDATION.md`
9. this file / 본 파일
10. `memory/NEXT_ACTION.md`
11. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
