# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M5-R1 — RENDERER ADAPTER CONTRACT & AUDIO QUALITY BASELINE v0: VALIDATED / M5-R1 — 렌더러 어댑터 계약 및 오디오 품질 기준선 v0: 검증 완료**

M0→M5-R1 are validated within their bounded claims. MUSICA now separates canonical musical authority from renderer execution through machine-valid renderer contracts, exact Music IR binding, bounded artifact production, objective PCM WAV QA, and explicit reproducibility evidence.

M0→M5-R1은 각 제한된 주장 범위에서 검증 완료되었습니다. MUSICA는 이제 machine-valid renderer 계약, 정확한 Music IR 바인딩, 제한된 artifact 생성, 객관적 PCM WAV QA, 명시적 재현성 근거를 통해 공식 음악 권한과 renderer 실행을 분리합니다.

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
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| M5-R2 First higher-fidelity local renderer | **NOT IMPLEMENTED** | next bounded mission |
| M5-R3 DAW/interchange interoperability | **NOT IMPLEMENTED** | later phase |
| M5-R4 Comparative music/audio quality evaluation | **NOT IMPLEMENTED** | later phase |

## M5-R1 final evidence / M5-R1 최종 근거

- implementation Issue: `#35` — **CLOSED / completed**
- implementation PR: `#36` — **MERGED**
- exact evidence-bearing head: `15668312e731f4d53fbaf633e8fa874c124eb1e7`
- exact-head CI: `34568008405`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- pytest: **92 passed**
- M0→M5 evidence generation/upload chain: **SUCCESS**
- Playwright Chromium M4-R3 regression: **SUCCESS**
- exact-head M5 artifact: `musica-m5-r1-renderer`
- artifact ID: `10186752409`
- artifact digest: `sha256:a1d0e61df96824bff375bb446a127ca2e3f07e703e19f59dff0db140d29c6ed9`
- independent downloaded ZIP digest: **MATCH**
- implementation merge: `5d9809984996b1b4c8b23605ac25134bfcc88b50`
- durable evidence: `evidence/M5_R1_VALIDATION.md`

### Exact renderer proof / 정확한 renderer 증명

- canonical Music IR SHA-256: `f28fd7f9268f1ff043f90988bb33800d95fce494cd0cc68c4265a6d8e0abc83d`
- request bound to exact Music IR: **true**
- Music IR unchanged after render: **true**
- renderer has project authority: **false**
- reference renderer: `musica-reference-local`
- renderer classification: `deterministic`
- independent run A/B MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- independent run A/B WAV SHA-256: `e049e83bdda5a1c5710bd4d09b3010ab414d27d5a6705398aae120ae9deac5b8`
- cross-run byte-exact reproducibility: **true**
- individual RendererResult reproducibility: `claim=byte_exact`, `verified=false`; verification belongs to independent cross-run evidence, not self-assertion.

### Objective PCM WAV baseline / 객관적 PCM WAV 기준선

- WAV container: **valid**
- sample rate: `22050 Hz`
- channels: `1 mono`
- bit depth: `16-bit PCM`
- duration: `20.0 s` / target `20.0 s`
- tolerance: `0.1 s`
- non-zero samples: `361028`
- peak normalized amplitude: approximately `0.130527665`
- hard clipping samples: `0`
- normalized DC offset: approximately `-0.000008868`
- AudioQualityReport: **PASS**
- integrated loudness: **UNKNOWN** — intentionally unmeasured in R1.

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

### Studio / Studio
- local-first Browser Studio with `Direct → Shape → Inspect → Code`,
- natural-language create/refine plus semantic controls,
- visible Tempo / Melody identity / Rhythm identity HARD locks,
- audible non-canonical Preview separated from accepted state,
- explicit Accept/Discard,
- branch/history/export and read-only Code/session JSON,
- loopback-only HTTP and same-origin security policy,
- real Chromium create → preview → accept → branch/history/export → Code → restart/reopen path validated.

### Renderer boundary / Renderer 경계
- machine-valid `RendererRequest v0`, `RendererCapability v0`, `RendererResult v0`, `AudioQualityReport v0`,
- exact canonical Music IR SHA-256 binding,
- bounded registry and capability checks,
- deterministic workspace-confined artifact paths,
- artifact path/hash/size verification,
- existing MIDI/WAV engine wrapped as reference adapter rather than rewritten,
- objective WAV container/signal validation,
- fail-closed negative coverage for IR hash mismatch, unknown renderer, capability mismatch, tamper, traversal, corrupt/silent/clipped/duration-mismatched audio,
- explicit separation of reproducibility claim from reproducibility verification.

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
 ↓ explicit user Accept only
M2 Project Engine
 ↓
Accepted Blueprint Revision
 ↓ trusted lowering
Canonical Music IR
 ↓ exact hash-bound RendererRequest
M5 Renderer Adapter
 ↓
Renderer artifacts + objective QA evidence
```

**Browser state, AI provider state, preview state, renderer state, and renderer artifacts never outrank the accepted `.musica` Project Bundle and canonical Music IR derived from its accepted revision.**

**Browser 상태, AI provider 상태, preview 상태, renderer 상태, renderer artifact는 승인된 `.musica` Project Bundle 및 그 승인 revision에서 파생된 canonical Music IR보다 우선할 수 없습니다.**

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- human-subject usability-study evidence,
- successful live OpenAI API execution,
- professional/mastering or perceptually superior audio quality,
- stereo high-fidelity production renderer,
- waveform/piano-roll/note-level professional editing UI,
- VST/AU plugin hosting,
- professional DAW automation/interoperability,
- a selected/validated higher-fidelity local synth/SoundFont/sampler backend,
- cloud collaboration or multi-user security,
- desktop installer/signing,
- remote HTTP serving,
- crash-atomic recovery across every possible process/filesystem failure.

레포는 아직 사람 대상 usability evidence, OpenAI live 호출, 전문/mastering 또는 지각적으로 우수한 음질, stereo 고음질 production renderer, 전문 note-level UI, VST/AU host, DAW 상호운용, 선정·검증된 고품질 local backend, cloud collaboration, desktop installer, remote HTTP를 검증하지 않습니다.

## Next phase / 다음 단계

The exact next bounded mission is **M5-R2 — First Higher-Fidelity Local Renderer Adapter v0**, beginning with evidence-driven backend selection rather than assuming a technology in advance.

정확한 다음 제한 mission은 **M5-R2 — First Higher-Fidelity Local Renderer Adapter v0 / 첫 고음질 로컬 렌더러 어댑터 v0**입니다. 특정 기술을 미리 채택하지 않고 근거 기반 backend selection부터 시작합니다.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. normative design specs / 규범 설계 명세
5. M0→M3 durable evidence
6. M4 acceptance/runtime/evidence documents
7. `docs/M5_R1_ACCEPTANCE.md`
8. `docs/M5_R1_RUNTIME.md`
9. `evidence/M5_R1_VALIDATION.md`
10. this file / 본 파일
11. `memory/NEXT_ACTION.md`
12. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
