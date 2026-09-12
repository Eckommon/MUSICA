# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M5-R4 — COMPARATIVE MUSIC / AUDIO QUALITY EVALUATION v0: VALIDATED — BOUNDED / M5-R4 — 비교 음악·오디오 품질 평가 v0: 제한 범위 검증 완료**

M0→M5-R4 are validated within their explicitly bounded claims. MUSICA now has a controllable/versioned creative core, provider-neutral AI Director boundary, usable Browser Studio, replaceable renderer adapters, bounded DAWproject interchange, and reproducible exact-source renderer comparison for objective signal descriptors.

M0→M5-R4는 각 명시적 제한 주장 범위에서 검증 완료되었습니다. MUSICA는 제어·버전 가능한 창작 코어, provider-neutral AI Director 경계, 사용 가능한 Browser Studio, 교체 가능한 renderer adapter, 제한적 DAWproject 상호운용성, 동일 source renderer 출력의 재현 가능한 객관 신호 비교를 보유합니다.

## Canonical core proposition / 공식 핵심 명제

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
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| Human-subject usability / perceptual evidence | **NOT VALIDATED** | separate controlled study required |
| Professional note-level editing authority/UI | **NOT IMPLEMENTED — NEXT** | M6-R0 selected |

## M5-R4 final evidence / M5-R4 최종 근거

### Contract / 계약

- Issue `#46` — **COMPLETED**
- PR `#47` — **MERGED**
- contract exact head: `7aaedd273ef2d9b4908324537889da29e8f4a9eb`
- contract CI: `34672590806` — **SUCCESS**
- contract merge: `fa8244009fde4c7a8968f775a000bfe1596b8b83`

### Implementation / 구현

- Issue `#48`
- PR `#49` — **MERGED**
- first evidence-bearing head: `3f4f6bb31bc077ae7f018ad128353896b02ba6ad`
- durable-evidence exact head: `818886a2834285dabdb5874a58f62606af0d2df7`
- final M5-R4 paired evidence run: `34673317029` — **SUCCESS**
- final M5-R3 regression run: `34673317011` — **SUCCESS**
- final full MUSICA CI run: `34673317078` — **SUCCESS**
- final M5-R4 artifact ID: `10291277918`
- final artifact ZIP digest: `sha256:3dd97cc99907ce8bba460981be9530e4983cd5d1899a835208b45e0f9316b111`
- implementation merge: `34b54ce2cd30347a4d82868dde7ccbf886f51432`
- durable evidence: `evidence/M5_R4_VALIDATION.md`

### Exact controlled-pair proof / 정확한 통제 pair 증명

- accepted Blueprint revision: `rev-001`
- Blueprint SHA-256: `085d44ac294631e0816b6cb3e58bc5d616b29dec408f867633506e83a2f7222b`
- canonical Music IR SHA-256: `f28fd7f9268f1ff043f90988bb33800d95fce494cd0cc68c4265a6d8e0abc83d`
- reference WAV SHA-256: `e049e83bdda5a1c5710bd4d09b3010ab414d27d5a6705398aae120ae9deac5b8`
- FluidSynth WAV SHA-256: `e054ad9cb7d938f50f75d222c1522e71cc7a7f163e8ea7bf3f8dceec628bcfa3`
- canonical comparison A/B SHA-256: `cb480c03fef734148592d6aeb60049836837371880bfe2e978f03b69493c3343`
- repeated comparison identity: **true**
- comparison-time resampling/gain matching/time stretching: **NONE**
- result: **`COMPARABLE_OBJECTIVE_ONLY`**

Claim boundary remains:

```text
HUMAN_SUBJECT_EVIDENCE = NOT_VALIDATED
PERCEPTUAL_SUPERIORITY = UNKNOWN
HUMAN_PREFERENCE_CLAIM_ALLOWED = false
```

M5-R4 does not prove that either renderer sounds better to humans.

## Validated capability stack / 검증된 기능 스택

### Music authority core / 음악 권한 코어
- typed Intent / Blueprint / Semantic Control / Music IR contracts;
- deterministic composition/lowering paths;
- bounded semantic controls;
- HARD-lock/constraint fail-closed validation;
- immutable accepted revisions/branches and audit chain.

### AI Director / AI 디렉터
- provider-neutral typed proposal boundary;
- explicit user intent outranks provider inference;
- provider output cannot directly mutate accepted state;
- OpenAI adapter contract validated offline;
- live OpenAI execution remains **NOT VALIDATED**.

### Studio / Studio
- local-first Browser Studio with `Direct → Shape → Inspect → Code`;
- non-canonical Preview separated from accepted state;
- explicit Accept/Discard;
- visible locks/diff/history/export;
- real Chromium E2E regression remains green.

### Renderer / Renderer
- renderer-neutral Request/Capability/Result/QA boundary;
- deterministic reference renderer;
- real Windows FluidSynth 2.6.0 + exact-hash-bound FluidR3_GM 3.1 bounded renderer evidence;
- renderer has no accepted-project mutation authority.

### Interchange / 교환
- deterministic bounded DAWproject 1.0 export;
- safe ZIP/XML/XSD validation;
- non-canonical import candidate;
- structured loss report;
- HARD-lock/stale-candidate fail-closed protection;
- explicit M2 acceptance boundary.

### Objective comparison / 객관 비교
- exact-source comparability gate;
- fixed objective PCM/spectral descriptors;
- explicit native-format/confound preservation;
- reproducibility proof;
- fail-closed prohibition on perceptual-superiority inference.

## Canonical authority rule / 공식 권한 규칙

```text
User
 ↓
Browser Studio / API
 ↓
M4 application service
 ↓
M3 proposal boundary or validated semantic command
 ↓
M1/M0 trusted core + HARD locks
 ↓
PREVIEW — non-canonical
 ↓ explicit Accept only
M2 Project Engine
 ↓
Accepted Blueprint Revision
 ↓ trusted lowering
Canonical Music IR
 ↓
M5 adapters / analysis
 ├─ Renderer → artifacts + QA + provenance
 ├─ Interchange → external artifact → NON-CANONICAL candidate
 └─ Comparison → objective evidence only
```

**AI output, preview, browser memory, Music IR edits, renderer output, comparison output and external DAW/interchange state never outrank accepted `.musica` project state.**

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- successful live OpenAI API execution;
- human-subject usability-study evidence;
- perceptual superiority of one renderer/audio path over another;
- professional/mastering audio quality;
- VST/AU/CLAP hosting;
- successful real external DAW smoke;
- compatibility with every DAW;
- arbitrary note-edit reverse mapping into Blueprint v0;
- plug-in/device fidelity;
- arbitrary automation/mixer fidelity;
- waveform/piano-roll/note-level professional editing UI;
- cloud collaboration/multi-user security;
- desktop installer/signing;
- remote HTTP serving.

## Next phase / 다음 단계

The exact next bounded mission is **M6-R0 — Precision Editing Authority & Canonical Note Model v0**.

정확한 다음 제한 mission은 **M6-R0 — 정밀 편집 권한 및 공식 Note Model v0**입니다.

M6-R0 exists because the conceptual Blueprint permits explicit notes when needed, but the concrete Blueprint v0 currently leaves `materials.melody` structurally open and M5-R3 correctly blocks arbitrary note edits from silently reverse-mapping into canonical Blueprint state. M6-R0 must define the authority contract before any piano-roll UI is allowed to mutate project state.

Core invariant:

```text
user note edit
→ typed edit candidate
→ canonical Blueprint-representable delta
→ HARD lock / constraint validation
→ PREVIEW
→ explicit Accept only
→ new M2 revision
```

Direct mutation of canonical Music IR is forbidden.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. normative design package/specs
4. `docs/design/MUSIC_BLUEPRINT_v0.md`
5. `schemas/music-blueprint-v0.schema.json`
6. `evidence/M5_R3_VALIDATION.md`
7. `evidence/M5_R4_VALIDATION.md`
8. this file / 본 파일
9. `memory/NEXT_ACTION.md`
10. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
