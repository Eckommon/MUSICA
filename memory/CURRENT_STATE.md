# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M4-R2 — BROWSER STUDIO UI VERTICAL SLICE v0: VALIDATED / M4-R2 — Browser Studio UI Vertical Slice v0: 검증 완료**

M0→M4-R2 are validated within their bounded claims. MUSICA now has a local-first browser-deliverable Studio over the validated application service, with progressive disclosure `Direct → Shape → Inspect → Code`, same-origin media/API access, explicit Preview/Accept authority separation, branches/history/export, and a packaged `musica-studio` launcher.

M0→M4-R2는 각 제한된 주장 범위에서 검증 완료되었습니다. MUSICA는 이제 검증된 application service 위에서 동작하는 local-first browser Studio를 가지며 `Direct → Shape → Inspect → Code`, same-origin media/API, Preview/Accept 권한 분리, branch/history/export, `musica-studio` 실행 진입점을 제공합니다.

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
| M4-R3 Usable MVP / real-browser E2E | **NOT VALIDATED** | next exact resume point |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| Production renderer/DAW adapters | **NOT IMPLEMENTED** | future M5 |

## M4-R2 final evidence / M4-R2 최종 근거

- implementation Issue: `#27`
- implementation PR: `#28`
- exact final head: `6ee200606dbf99419fa67e9aec3ad4e288a8c66d`
- exact-head CI: `34551205586`
- Python 3.11/3.12: **SUCCESS**
- M0→M4-R2 evidence generation/upload: **SUCCESS**
- final artifact: `musica-m4-r2-browser-studio`, ID `10180901528`
- final artifact digest: `sha256:5c55c2f61ed53a1638479d1383cabb042d97be41599b36e04d65dea90cf57d5b`
- implementation merge: `16707e25bf78b4141c44da24bf8e82f375d7c465`
- durable evidence: `evidence/M4_R2_VALIDATION.md`
- acceptance: `docs/M4_R2_ACCEPTANCE.md`
- runtime: `docs/M4_R2_RUNTIME.md`

## Validated capability stack / 검증된 기능 스택

### Music core / 음악 코어
- strict Intent / Blueprint / Semantic Control / Music IR contracts,
- deterministic Intent → Blueprint composition,
- six bounded semantic axes,
- HARD-lock/constraint fail-closed revision validation,
- deterministic MIDI and bounded local WAV preview.

### Project/version / 프로젝트·버전
- Git-independent `.musica` Project Bundle,
- immutable accepted revisions and branches/refs,
- structured diffs, SHA-256 artifact/object binding and audit chain,
- integrity verification and deterministic export/import.

### AI Director / AI 디렉터
- provider-neutral Request/Proposal/Trace authority boundary,
- explicit user intent outranks provider inference,
- exact revision/context binding,
- bounded OpenAI Responses adapter contract,
- external provider output cannot directly mutate canonical state,
- offline adapter evidence is distinct from live-provider evidence.

### Studio application service / Studio 애플리케이션 서비스
- create/open local Studio sessions and `.musica` projects,
- semantic/Director edit → audible non-canonical preview,
- explicit Accept → M2 commit + artifact binding,
- Discard → ref preservation,
- branch/history/export,
- workspace confinement,
- loopback-only HTTP and local media retrieval.

### Browser Studio / Browser Studio
- packaged local HTML/CSS/JavaScript UI,
- `Direct → Shape → Inspect → Code` progressive disclosure,
- natural-language create/refine controls,
- six semantic controls with supported scopes,
- accepted/pending WAV playback and MIDI access,
- visible `PREVIEW · NOT ACCEPTED`, exact diff and HARD locks,
- explicit Accept/Discard,
- branch create/checkout, history and export,
- read-only Code/session JSON,
- strict same-origin CSP and no third-party runtime asset dependency,
- packaged `musica-studio` launcher.

## Canonical authority rule / 공식 권한 규칙

```text
User
 ↓
Browser Studio
 ↓
M4 application service
 ↓
M3 proposal boundary or validated semantic command
 ↓
M1/M0 trusted core + HARD locks
 ↓
PREVIEW — non-canonical
 ↓ explicit user Accept only
M2 Project Engine
 ↓
Accepted Blueprint Revision + bound render artifacts
```

**Browser state, AI provider state, and preview state never outrank the accepted `.musica` Project Bundle.**

**Browser 상태, AI provider 상태, preview 상태는 승인된 `.musica` Project Bundle보다 우선할 수 없습니다.**

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- Playwright/Selenium real-browser end-to-end workflow,
- complete UI-level restart/reopen recovery,
- human usability-study evidence,
- successful live OpenAI API execution,
- production/mastering audio quality,
- waveform/piano-roll/note-level professional editing UI,
- professional DAW/VST/sampler interoperability,
- cloud collaboration or multi-user security,
- desktop installer/signing,
- remote HTTP serving,
- crash-atomic recovery across revision commit and artifact binding.

레포는 아직 실제 browser E2E, UI-level restart/reopen, 사람 대상 usability evidence, OpenAI live 호출, 상용 음질, 전문 note-level UI, DAW/VST 상호운용, cloud collaboration, desktop installer, remote HTTP, crash-atomic recovery를 검증하지 않습니다.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. normative design specs / 규범 설계 명세
5. M0→M3 durable evidence
6. `docs/M4_R1_ACCEPTANCE.md` + `evidence/M4_R1_VALIDATION.md`
7. `docs/M4_R2_ACCEPTANCE.md` + `docs/M4_R2_RUNTIME.md` + `evidence/M4_R2_VALIDATION.md`
8. this file / 본 파일
9. `memory/NEXT_ACTION.md`
10. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
