# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M4-R3 — USABLE MVP / REAL-BROWSER E2E ACCEPTANCE v0: VALIDATED / M4-R3 — 사용 가능한 MVP / 실제 Browser E2E 수용 v0: 검증 완료**

M0→M4-R3 are validated within their bounded claims. MUSICA now has a local-first Browser Studio that can be operated through a real Chromium interaction path while preserving the accepted `.musica` Project Bundle as canonical authority.

M0→M4-R3는 각 제한된 주장 범위에서 검증 완료되었습니다. MUSICA는 이제 실제 Chromium interaction 경로로 조작 가능한 local-first Browser Studio를 가지며, 승인된 `.musica` Project Bundle을 공식 권한으로 유지합니다.

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
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| M5 Renderer/Audio Quality/DAW interoperability | **NOT IMPLEMENTED** | next phase |

## M4-R3 final evidence / M4-R3 최종 근거

- implementation Issue: `#31` — **CLOSED / completed**
- implementation PR: `#32` — **MERGED**
- exact evidence-bearing head: `0bfc3e7475c20e4891c629ee736237bbc72a958c`
- exact-head CI: `34553248432`
- Python 3.11: **SUCCESS**
- Python 3.12 + M0→M4-R2 evidence chain: **SUCCESS**
- Playwright Chromium `browser-e2e`: **SUCCESS**
- exact-head artifact: `musica-m4-r3-real-browser-e2e`
- artifact ID: `10181576753`
- artifact digest: `sha256:b38c510939c7d6869ad446cd79ed8fd0777ed09e636e9f7aa95d053be65a206b`
- implementation merge: `2c64fe69a5472d5aa7eef5d077e5c30fdfe704d2`
- durable evidence: `evidence/M4_R3_VALIDATION.md`

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
- offline adapter evidence remains distinct from live-provider evidence.

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
- visible identity locks for Tempo / Melody identity / Rhythm identity,
- six semantic controls with supported scopes,
- accepted/pending WAV playback and MIDI access,
- visible `PREVIEW · NOT ACCEPTED`, structured diff and HARD locks,
- explicit Accept/Discard,
- branch create/checkout, history and export,
- read-only Code/session JSON,
- strict same-origin CSP and no third-party runtime asset dependency,
- packaged `musica-studio` launcher.

### Real-browser acceptance / 실제 Browser 수용
- Playwright Chromium E2E is isolated as test/evidence infrastructure,
- Browser-driven create → preview → accept → branch/history/export → Code workflow validated,
- Preview cannot silently advance canonical head,
- conflicting branch/checkout/export controls are blocked while Preview is pending,
- fresh Studio service restart + Browser reopen restores durable branch/head/integrity/audio,
- final exact-head run records zero browser console/page errors.

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

**Browser state, AI provider state, renderer state, and preview state never outrank the accepted `.musica` Project Bundle.**

**Browser 상태, AI provider 상태, renderer 상태, preview 상태는 승인된 `.musica` Project Bundle보다 우선할 수 없습니다.**

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- human-subject usability-study evidence,
- successful live OpenAI API execution,
- production/mastering audio quality,
- waveform/piano-roll/note-level professional editing UI,
- production-grade renderer adapter architecture,
- professional DAW/VST/sampler interoperability,
- cloud collaboration or multi-user security,
- desktop installer/signing,
- remote HTTP serving,
- crash-atomic recovery across every possible process/filesystem failure.

레포는 아직 사람 대상 usability evidence, OpenAI live 호출, 상용 mastering 음질, 전문 note-level UI, production renderer adapter, DAW/VST/sampler 상호운용, cloud collaboration, desktop installer, remote HTTP를 검증하지 않습니다.

## Next phase / 다음 단계

The next phase is **M5 — Renderer / Audio Quality / DAW Interoperability**. The exact next bounded mission is defined in `memory/NEXT_ACTION.md` as **M5-R1 Renderer Adapter Contract & Audio Quality Baseline v0**.

다음 단계는 **M5 — Renderer / Audio Quality / DAW 상호운용**이며, 정확한 다음 제한 mission은 `memory/NEXT_ACTION.md`의 **M5-R1 Renderer Adapter Contract & Audio Quality Baseline v0**입니다.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. normative design specs / 규범 설계 명세
5. M0→M3 durable evidence
6. `docs/M4_R1_ACCEPTANCE.md` + `evidence/M4_R1_VALIDATION.md`
7. `docs/M4_R2_ACCEPTANCE.md` + `docs/M4_R2_RUNTIME.md` + `evidence/M4_R2_VALIDATION.md`
8. `docs/M4_R3_ACCEPTANCE.md` + `docs/M4_R3_RUNTIME.md` + `evidence/M4_R3_VALIDATION.md`
9. this file / 본 파일
10. `memory/NEXT_ACTION.md`
11. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
