# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M5-R3 — DAW / INTERCHANGE INTEROPERABILITY v0: VALIDATED — BOUNDED / M5-R3 — DAW·교환 상호운용성 v0: 제한 범위 검증 완료**

M0→M5-R3 are validated within their explicitly bounded claims. MUSICA now has both replaceable renderer adapters and a bounded deterministic DAWproject 1.0 interchange bridge while keeping accepted `.musica` Blueprint revisions and derived canonical Music IR above every renderer/interchange artifact in authority.

M0→M5-R3는 각 명시적 제한 주장 범위에서 검증 완료되었습니다. MUSICA는 교체 가능한 renderer adapter와 제한적 결정론 DAWproject 1.0 interchange bridge를 갖추었으며, 모든 renderer/interchange artifact보다 accepted `.musica` Blueprint revision 및 그로부터 파생된 canonical Music IR의 권한이 우선합니다.

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
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| M5-R4 Comparative music/audio quality evaluation | **NOT IMPLEMENTED** | exact next bounded mission |

## M5-R3 final evidence / M5-R3 최종 근거

### Selection / 선정

- governing Issue: `#42`
- selection PR: `#43` — **MERGED**
- selection exact head: `ef57f08cd42f3f323b6cc67fefc13b09c08e1b5a`
- selection CI: `34577168697` — **SUCCESS**
- selection merge: `16d859b4bb5652fb681ba20471927cdb3694b8e9`
- selected format/profile: `DAWproject 1.0 bounded profile`

### Implementation / 구현

- implementation PR: `#44` — **MERGED**
- initial executable head: `d653feadeea9fa3a6205af82a2e4072409fcc8e0`
- evidence-bearing exact head: `21b7e7315ff80b994f091a274a19c467eeca4bae`
- dedicated M5-R3 evidence run: `34581150840` — **SUCCESS**
- final full MUSICA CI run: `34581150808` — **SUCCESS**
- Python 3.11 full suite: **SUCCESS**
- Python 3.12 full suite + prior evidence chain: **SUCCESS**
- M4-R3 Chromium regression: **SUCCESS**
- M5-R2 Windows FluidSynth regression: **SUCCESS**
- implementation merge: `5c874b62b1df0abe0ce58077f7dae0f37303aa5d`
- durable evidence: `evidence/M5_R3_VALIDATION.md`

## Exact M5-R3 proof / 정확한 M5-R3 증명

Source authority:

- source revision: `rev-001`
- source Blueprint SHA-256: `085d44ac294631e0816b6cb3e58bc5d616b29dec408f867633506e83a2f7222b`
- canonical Music IR SHA-256: `f28fd7f9268f1ff043f90988bb33800d95fce494cd0cc68c4265a6d8e0abc83d`

Deterministic export:

- A/B DAWproject SHA-256: `2575713e0b3345a8a9c3553ace990f60650f9ed73877330193ae2906483e4b0d`
- A/B byte identity: **true**
- `project.xml` SHA-256: `816d7fac3c4789d750de57f6bbf9480867fe0015bca523775216f000419b03e4`
- `metadata.xml` SHA-256: `73dafa6d8db0afc2bb92b9bb257290f5eefa1de8761f040e9992644dbecab9b7`
- export mutates accepted M2 state: **false**

Round-trip authority:

- unedited import → `PENDING / PASS`
- external `130 BPM` edit → **BLOCKED** by existing HARD tempo authority
- arbitrary note edit → **UNSUPPORTED_BLOCKING** for Blueprint v0 reverse mapping
- external `3/4` meter edit → `PENDING / PASS`
- branch ref before explicit Accept: **unchanged**
- explicit Accept only → M2 commit `import-cade96e92cea8682`
- accepted provenance actor: `import`
- post-accept project integrity: **PASS**

Normative loss taxonomy:

`PRESERVED | TRANSFORMED | DROPPED | UNSUPPORTED | UNKNOWN`

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
- machine-readable loss report;
- traceable tempo/meter/track/note subset;
- HARD-lock and stale-candidate fail-closed protection;
- explicit M2 acceptance boundary.

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
M5 adapters
 ├─ Renderer → artifacts + QA + provenance
 └─ Interchange → external artifact → NON-CANONICAL candidate
                                      ↓ explicit Accept only
                                     M2 commit
```

**AI output, preview, browser memory, renderer output and external DAW/interchange state never outrank accepted `.musica` project state.**

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- successful live OpenAI API execution;
- human-subject usability-study evidence;
- perceptual superiority of one renderer/audio path over another;
- professional/mastering audio quality;
- VST/AU/CLAP hosting;
- successful real external DAW smoke (`EXTERNAL_APP_SMOKE = NOT VALIDATED`);
- compatibility with every DAW or any named DAW through MUSICA execution;
- arbitrary note-edit reverse mapping into Blueprint v0;
- plug-in/device fidelity;
- arbitrary automation/mixer fidelity;
- perfect project interchange;
- waveform/piano-roll/note-level professional editing UI;
- cloud collaboration/multi-user security;
- desktop installer/signing;
- remote HTTP serving.

## Next phase / 다음 단계

The exact next bounded mission is **M5-R4 — Comparative Music / Audio Quality Evaluation v0**.

정확한 다음 제한 mission은 **M5-R4 — 비교 음악·오디오 품질 평가 v0**입니다.

M5-R4 must evaluate actual rendered outputs without confusing technical signal validity with perceptual/music quality. It shall begin with an acceptance/evaluation contract and controlled paired evidence rather than claiming the higher-fidelity renderer is perceptually superior because it has higher sample rate/stereo capability.

M5-R4는 실제 렌더 결과를 평가하되 기술적 signal validity와 청감·음악 품질을 혼동하지 않아야 합니다. 높은 sample rate/stereo capability만으로 청감상 우월성을 주장하지 않고, acceptance/evaluation 계약과 통제된 paired evidence 설계부터 시작합니다.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. normative design package/specs
4. `evidence/M5_R2_VALIDATION.md`
5. `docs/M5_R3_INTERCHANGE_SELECTION.md`
6. `docs/M5_R3_ROUNDTRIP_AUTHORITY.md`
7. `docs/M5_R3_ACCEPTANCE.md`
8. `docs/M5_R3_RUNTIME.md`
9. `evidence/M5_R3_VALIDATION.md`
10. this file / 본 파일
11. `memory/NEXT_ACTION.md`
12. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
