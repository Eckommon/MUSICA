# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation** built around one product promise:

MUSICA는 하나의 제품 약속을 중심으로 구축하는 **AI-native 프로그래머블 음악 워크스테이션**입니다.

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**
>
> **자연어로 지시할 만큼 쉽고, 전문 음악 시스템처럼 세밀하게 편집할 만큼 정밀해야 한다.**

MUSICA is not a text-to-song clone and is not designed around one renderer. Natural-language intent is lowered into inspectable contracts, protected by locks/constraints, compiled into executable music, and accepted into durable project revisions only through explicit authority boundaries.

MUSICA는 text-to-song 복제 제품도, 특정 렌더러 중심 시스템도 아닙니다. 자연어 의도는 검사 가능한 계약으로 구조화되고 lock/constraint로 보호되며 실행 가능한 음악으로 컴파일됩니다. 공식 프로젝트 리비전은 명시적인 권한 경계를 통과할 때만 승인됩니다.

## Try the local Studio / 로컬 Studio 실행

Current M4 architecture provides a local-first browser Studio over the Python core.

현재 M4 아키텍처는 Python 코어 위에 local-first Browser Studio를 제공합니다.

```bash
python -m pip install -e '.[dev]'
musica-studio
```

Default / 기본값:

```text
Workspace / 작업공간: ~/MUSICA-Workspace
URL: http://127.0.0.1:8765/
```

Useful options / 주요 옵션:

```bash
musica-studio --workspace ./my-musica-workspace
musica-studio --port 8877
musica-studio --no-browser
```

The Studio is loopback-only by design. It requires no cloud account, telemetry, remote asset CDN, or live OpenAI credential to start. The offline fixture Director is the default; OpenAI is an explicit optional provider mode.

Studio는 설계상 loopback-only입니다. 시작에 cloud account, telemetry, remote asset CDN, live OpenAI credential이 필요하지 않습니다. Offline fixture Director가 기본이며 OpenAI는 명시적으로 선택하는 provider mode입니다.

## One state, four depths / 하나의 상태, 네 가지 깊이

The Browser Studio exposes progressively deeper control over the same canonical `.musica` project state.

Browser Studio는 동일한 공식 `.musica` project state를 단계적으로 더 깊게 제어합니다.

- **Direct / 간편 디렉팅** — natural-language creation/refinement and audition / 자연어 생성·수정·청취
- **Shape / 의미·구조 편집** — six semantic axes, sections and scoped preview / 6축 의미 제어·구간·범위 preview
- **Inspect / 전문 검사** — locks, exact diff, accepted/preview status, branches/history / lock·정확한 diff·상태·버전 이력
- **Code / 코드·근거** — read-only validated JSON and authority evidence / 읽기 전용 검증 JSON·권한 근거

These are views over one project state, not incompatible modes or separate databases.

이는 서로 다른 비호환 모드나 별도 데이터베이스가 아니라 하나의 프로젝트 상태를 보는 네 가지 깊이입니다.

## Canonical authority / 공식 권한 구조

```text
User / 사용자
  ↓
Browser Studio
  ↓
M4 Application Service
  ↓
M3 AI Music Director proposal boundary
  ↓
M1 Creative Core + M0 contracts / HARD locks
  ↓
PREVIEW — non-canonical / 비공식 상태
  ↓ explicit Accept only / 명시적 승인만
M2 Project & Version Engine
  ↓
Accepted Blueprint Revision + MIDI/WAV artifacts
```

**AI output is not accepted state. Preview audio is not accepted state. Browser memory is not accepted state.**

**AI 출력은 승인 상태가 아닙니다. Preview 오디오는 승인 상태가 아닙니다. Browser memory도 승인 상태가 아닙니다.**

The accepted `.musica` Project Bundle remains canonical.

승인된 `.musica` Project Bundle이 계속 공식 상태입니다.

## System model / 시스템 모델

```text
Intent / 의도
  ↓
AI Music Director / AI 음악 디렉터
  ↓
Music Blueprint / 음악 설계도
  ↓
Semantic Controls + Locks + Constraints
의미 제어 + 잠금 + 제약
  ↓
Validated Blueprint Revision + Diff
검증 Blueprint 리비전 + Diff
  ↓
Music Compiler
  ↓
Music IR
  ↓
Renderer Adapters
  ↓
MIDI / local Synth / future Sampler·DAW·DSP·Generative Audio
```

Important distinction / 중요 구분:

> **Music Blueprint = canonical human/AI creative state. / 인간·AI가 공유하는 공식 창작 상태.**
>
> **Music IR = lower-level executable representation produced by compilation. / 컴파일로 생성되는 저수준 실행 표현.**

## Validated milestone stack / 검증 마일스톤 스택

| Milestone | Status / 상태 | Evidence / 근거 |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4-R1 Studio Application Service | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` |
| M4-R2 Browser Studio UI | **BRANCH VALIDATION PASSED; exact-head PR gate pending** | `evidence/M4_R2_VALIDATION.md` |
| M4-R3 Usable MVP / Browser E2E | **NOT VALIDATED** | next product acceptance |

M3-R2 validates an OpenAI adapter contract with offline injected transport. A real authorized OpenAI network run is **not** currently validated evidence and must be recorded separately as `LIVE_PROVIDER_EVIDENCE` if performed.

M3-R2는 offline injected transport로 OpenAI adapter 계약을 검증합니다. 실제 승인된 OpenAI network 실행은 현재 검증 근거가 아니며 수행 시 반드시 별도 `LIVE_PROVIDER_EVIDENCE`로 기록해야 합니다.

## Repository as Source of Truth / GitHub를 공식 근거로 사용

This repository is the implementation workspace, project memory, decision ledger and anti-hallucination evidence boundary.

이 저장소는 구현 workspace, 프로젝트 기억, 의사결정 원장, AI 환각 방지 근거 경계입니다.

Authority rule / 권위 규칙:

```text
Accepted repository artifacts/tests/evidence
> merged specs/current-state records
> issue/PR/CI evidence
> conversation context
> model memory
> model inference
```

No AI agent may claim that a feature, test, milestone, artifact or integration exists without repository evidence.

어떤 AI 에이전트도 레포 근거 없이 기능, 테스트, 마일스톤, 산출물 또는 통합이 존재한다고 주장해서는 안 됩니다.

Before substantive work read / 실질 작업 전 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. `memory/CURRENT_STATE.md`
5. `memory/NEXT_ACTION.md`

## Current exact next point / 현재 정확한 다음 재개점

M4-R2 implementation has passed its first branch CI/evidence gate. It must still pass the **evidence-bearing exact-head PR CI** before merge and state promotion. After M4-R2 closure, the next milestone is **M4-R3 Usable MVP / browser E2E acceptance**.

M4-R2 구현은 첫 branch CI/evidence gate를 통과했습니다. 병합·상태 승격 전 **durable evidence 포함 exact-head PR CI**를 반드시 다시 통과해야 합니다. M4-R2 종결 후 다음 마일스톤은 **M4-R3 Usable MVP / browser E2E 수용**입니다.
