# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M4-R1 — STUDIO APPLICATION SERVICE & SESSION BOUNDARY v0: VALIDATED / M4-R1 — Studio 애플리케이션 서비스·세션 경계 v0: 검증 완료**

M0→M3 remain validated within their bounded claims. M4-R1 adds the first validated user-application boundary: local Studio sessions, non-canonical previews, explicit acceptance, project/version operations, deterministic export, workspace confinement, and a loopback-only HTTP bridge.

M0→M3는 제한된 주장 범위에서 계속 검증 상태입니다. M4-R1은 local Studio session, 비공식 preview, 명시적 승인, project/version 작업, 결정론 export, workspace 제한, loopback-only HTTP bridge를 포함하는 첫 검증된 사용자 애플리케이션 경계를 추가했습니다.

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
| M4-R2 Browser Studio UI | **NOT IMPLEMENTED** | next exact resume point |
| M4-R3 Usable MVP | **NOT VALIDATED** | future acceptance |
| Live OpenAI provider execution | **NOT VALIDATED** | requires separate `LIVE_PROVIDER_EVIDENCE` |
| Production renderer/DAW adapters | **NOT IMPLEMENTED** | future M5 |

## M4-R1 final evidence / M4-R1 최종 근거

- implementation Issue: `#23`
- implementation PR: `#24`
- exact final head: `cba73433c5e83315472c0305b20f436672d1fb0d`
- exact-head CI run: `34549868112`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- M0→M4-R1 evidence generation/upload: **SUCCESS**
- final artifact: `musica-m4-r1-studio-service`, ID `10180408128`
- final artifact digest: `sha256:3640aebebb156f975a9faea58026604f419aa5ecc471174f7da6cb28f1d4c81e`
- implementation merge: `4ebe2e0590b17f5e659dd48bed5b0331af7fac9b`
- durable evidence: `evidence/M4_R1_VALIDATION.md`
- acceptance: `docs/M4_R1_ACCEPTANCE.md`
- runtime: `docs/M4_R1_RUNTIME.md`

## Validated capability stack / 검증된 기능 스택

### Music core / 음악 코어

- strict Music Intent / Blueprint / Semantic Control / Music IR contracts,
- deterministic Intent → Blueprint composition,
- bounded style profiles and six semantic axes,
- HARD-lock/constraint fail-closed revision validation,
- deterministic MIDI and bounded local WAV preview.

### Project/version / 프로젝트·버전

- Git-independent `.musica` Project Bundle,
- immutable accepted revisions, branches/refs and structured diffs,
- SHA-256 object/artifact binding and audit chain,
- integrity verification and deterministic export/import.

### AI Director / AI 디렉터

- provider-neutral Request/Proposal/Trace authority boundary,
- explicit user intent outranks provider inference,
- exact revision/context binding,
- OpenAI Responses adapter contract with strict structured output,
- external provider output cannot directly mutate canonical state,
- offline adapter evidence is distinct from live provider evidence.

### Studio application boundary / Studio 애플리케이션 경계

- create/open Studio sessions and `.musica` projects,
- inspect branch/head/sections/semantic state/HARD locks,
- semantic or Director edit → audible non-canonical preview,
- branch ref remains unchanged until explicit Accept,
- Accept → M2 commit + MIDI/WAV binding,
- Discard → exact ref preservation,
- branch create/checkout + revision history,
- deterministic project export,
- workspace/path/symlink confinement,
- loopback-only HTTP and local WAV/MIDI retrieval,
- restart/reopen of durable project state.

## Canonical authority rule / 공식 권한 규칙

```text
User
 ↓
Browser/Studio client
 ↓
M4 application service
 ↓
M3 AI proposal boundary or validated semantic command
 ↓
M1/M0 trusted music core + HARD locks
 ↓
PREVIEW — non-canonical
 ↓ explicit user Accept only
M2 Project Engine
 ↓
Accepted Blueprint Revision + bound render artifacts
```

**UI state, AI provider state, and preview state never outrank the accepted `.musica` Project Bundle.**

**UI 상태, AI provider 상태, preview 상태는 승인된 `.musica` Project Bundle보다 우선할 수 없습니다.**

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- polished Browser Studio UI or browser E2E workflow,
- successful live OpenAI API execution,
- universal free-form music understanding,
- production/mastering audio quality,
- professional DAW/VST/sampler interoperability,
- cloud collaboration or multi-user security,
- desktop installer/signing,
- remote HTTP serving,
- crash-atomic recovery across revision commit and artifact binding.

레포는 아직 완성형 Browser Studio UI, 실제 OpenAI live 호출, 보편 음악 이해, 상용 음질, 전문 DAW/VST 상호운용, cloud collaboration, desktop installer, remote HTTP, commit/artifact-binding crash-atomic recovery를 검증하지 않습니다.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. normative design specs / 규범 설계 명세
5. M0→M3 durable evidence
6. `docs/M4_R1_ACCEPTANCE.md`
7. `docs/M4_R1_RUNTIME.md`
8. `evidence/M4_R1_VALIDATION.md`
9. this file / 본 파일
10. `memory/NEXT_ACTION.md`
11. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
