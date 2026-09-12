# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation** built around one product promise:

MUSICA는 하나의 제품 약속을 중심으로 구축하는 **AI-native 프로그래머블 음악 워크스테이션**입니다.

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**
>
> **자연어로 지시할 만큼 쉽고, 전문 음악 시스템처럼 세밀하게 편집할 만큼 정밀해야 한다.**

MUSICA is not a text-to-song clone and is not designed around one renderer or one DAW. Natural-language intent is lowered into inspectable contracts, protected by locks/constraints, compiled into executable music, rendered or exchanged through replaceable adapters, and accepted into durable project revisions only through explicit authority boundaries.

MUSICA는 text-to-song 복제 제품도 특정 renderer/DAW 중심 시스템도 아닙니다. 자연어 의도는 검사 가능한 계약으로 구조화되고 lock/constraint로 보호되며 실행 가능한 음악으로 컴파일됩니다. Renderer와 interchange는 교체 가능한 adapter이고 공식 프로젝트 revision은 명시적인 권한 경계를 통과할 때만 승인됩니다.

## Current canonical status / 현재 공식 상태

**M0 → M5-R3 are validated within their explicitly bounded claims.**

**M0 → M5-R3는 각 명시적 제한 주장 범위에서 검증 완료되었습니다.**

Validated external-output boundaries now include:

- `musica-reference-local` — deterministic bounded reference renderer;
- `musica-fluidsynth-local` — bounded real Windows FluidSynth 2.6.0 + exact-hash-bound external FluidR3_GM 3.1 renderer path;
- `DAWproject 1.0 bounded profile` — deterministic export + safe non-canonical import-candidate bridge with explicit loss reporting and M2 acceptance authority.

The next bounded milestone is **M5-R4 — Comparative Music / Audio Quality Evaluation v0**. It will compare controlled paired renders without converting technical capability into an unsupported perceptual-superiority claim.

다음 제한 마일스톤은 **M5-R4 — 비교 음악·오디오 품질 평가 v0**입니다. 기술 capability를 근거 없는 청감상 우월성 주장으로 바꾸지 않고 통제된 paired render를 비교하는 단계입니다.

## Try the local Studio / 로컬 Studio 실행

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

- **Direct / 간편 디렉팅** — natural-language creation/refinement and audition / 자연어 생성·수정·청취
- **Shape / 의미·구조 편집** — semantic axes, sections and scoped preview / 의미 제어·구간·범위 preview
- **Inspect / 전문 검사** — locks, exact diff, accepted/preview status, branches/history / lock·정확한 diff·상태·버전 이력
- **Code / 코드·근거** — read-only validated JSON and authority evidence / 읽기 전용 검증 JSON·권한 근거

These are views over one project state, not separate databases or incompatible modes.

## Canonical authority / 공식 권한 구조

```text
User / 사용자
  ↓
Browser Studio / API
  ↓
M4 Application Service
  ↓
M3 AI Music Director proposal boundary
  ↓
M1 Creative Core + M0 contracts / HARD locks
  ↓
PREVIEW — non-canonical
  ↓ explicit Accept only
M2 Project & Version Engine
  ↓
Accepted Blueprint Revision
  ↓ trusted lowering
Canonical Music IR
  ↓
M5 replaceable adapters
  ├─ Renderer → audio/artifacts + QA + provenance
  └─ Interchange → external artifact → NON-CANONICAL candidate
                                        ↓ explicit Accept only
                                       M2 commit
```

**AI output is not accepted state. Preview audio is not accepted state. Browser memory is not accepted state. Renderer output is not accepted state. Imported DAW/interchange state is not accepted state.**

**AI 출력, Preview 오디오, Browser memory, Renderer output, 외부 DAW/interchange import 상태는 승인 상태가 아닙니다.**

The accepted `.musica` Project Bundle remains canonical.

## System model / 시스템 모델

```text
Intent / 의도
  ↓
AI Music Director / AI 음악 디렉터
  ↓
Music Blueprint / 음악 설계도
  ↓
Semantic Controls + Locks + Constraints
  ↓
Validated Blueprint Revision + Diff
  ↓
Music Compiler
  ↓
Music IR
  ↓
Renderer / Interchange Adapters
  ↓
MIDI / local synth / DAWproject / future sampler·DAW·DSP·generative audio
```

Important distinction / 중요 구분:

> **Music Blueprint = canonical human/AI creative state. / 인간·AI가 공유하는 공식 창작 상태.**
>
> **Music IR = lower-level executable representation produced by compilation. / 컴파일로 생성되는 저수준 실행 표현.**
>
> **External renderer/interchange artifact = non-canonical output or candidate carrier. / 외부 renderer/interchange artifact는 비공식 출력 또는 candidate 운반체.**

## Validated milestone stack / 검증 마일스톤 스택

| Milestone | Status / 상태 | Evidence / 근거 |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4-R1 Studio Application Service | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` |
| M4-R2 Browser Studio UI | **VALIDATED** | `evidence/M4_R2_VALIDATION.md` |
| M4-R3 Usable MVP / real-browser E2E | **VALIDATED** | `evidence/M4_R3_VALIDATION.md` |
| M5-R1 Renderer Adapter Contract + Audio QA Baseline | **VALIDATED** | `evidence/M5_R1_VALIDATION.md` |
| M5-R2 First Higher-Fidelity Local Renderer | **VALIDATED — BOUNDED** | `evidence/M5_R2_VALIDATION.md` |
| M5-R3 DAW / Interchange Interoperability | **VALIDATED — BOUNDED** | `evidence/M5_R3_VALIDATION.md` |
| M5-R4 Comparative Music/Audio Quality Evaluation | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |

## M5-R3 validated boundary / M5-R3 검증 경계

M5-R3 selected and implemented **DAWproject 1.0** as the first bounded project-interchange target.

Validated authority model:

```text
Accepted .musica revision
→ canonical Music IR
→ deterministic DAWproject export
→ optional external edit
→ safe ZIP/XML/XSD import
→ NON-CANONICAL candidate
→ structured diff + five-state loss report
→ HARD lock / constraint validation
→ explicit user Accept
→ M2 commit
```

The evidence proves deterministic A/B export, bounded note/track/transport round-trip, fail-closed HARD-lock handling, unsupported arbitrary note reverse mapping, explicit meter-candidate acceptance and project-integrity preservation.

외부 DAW 파일은 변경을 제안할 수 있지만 MUSICA 권한을 조용히 덮어쓸 수 없습니다.

M5-R3 does **not** validate a real external DAW smoke, every-DAW compatibility, plug-in/device fidelity, arbitrary mixer/automation fidelity, or perfect interchange.

## Repository as Source of Truth / GitHub를 공식 근거로 사용

This repository is the implementation workspace, project memory, decision ledger and anti-hallucination evidence boundary.

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

Before substantive work read / 실질 작업 전 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. `memory/CURRENT_STATE.md`
5. `memory/NEXT_ACTION.md`
6. relevant milestone acceptance/evidence documents
7. relevant Issue / PR / exact-head CI evidence

## Current exact next point / 현재 정확한 다음 재개점

Start **M5-R4A Evaluation Contract**. Do not add another renderer or assert that FluidSynth/FluidR3 sounds better. First define the paired-source authority, objective descriptor set, confound controls, machine-readable comparison result and claim boundary described in `memory/NEXT_ACTION.md`.

**M5-R4A Evaluation Contract**부터 시작합니다. 새 renderer를 추가하거나 FluidSynth/FluidR3가 더 좋게 들린다고 먼저 주장하지 않습니다. `memory/NEXT_ACTION.md`에 정의된 paired-source 권한, 객관 descriptor 집합, 교란 통제, machine-readable comparison result 및 claim boundary를 먼저 확정합니다.
