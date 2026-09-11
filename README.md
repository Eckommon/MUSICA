# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation** built around one product promise:

MUSICA는 하나의 제품 약속을 중심으로 구축하는 **AI-native 프로그래머블 음악 워크스테이션**입니다.

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**
>
> **자연어로 지시할 만큼 쉽고, 전문 음악 시스템처럼 세밀하게 편집할 만큼 정밀해야 한다.**

MUSICA is not a text-to-song clone and is not designed around one renderer or one DAW. Natural-language intent is lowered into inspectable contracts, protected by locks/constraints, compiled into executable music, rendered through replaceable adapters, and accepted into durable project revisions only through explicit authority boundaries.

MUSICA는 text-to-song 복제 제품도, 하나의 renderer나 DAW에 종속된 시스템도 아닙니다. 자연어 의도는 검사 가능한 계약으로 구조화되고 lock/constraint로 보호되며 실행 가능한 음악으로 컴파일됩니다. Renderer와 interchange는 교체 가능한 adapter이며 공식 프로젝트 revision은 명시적인 권한 경계를 통과할 때만 승인됩니다.

## Current canonical status / 현재 공식 상태

**M0 → M5-R2 are validated within their explicitly bounded claims.**

**M0 → M5-R2는 각 명시적 제한 주장 범위에서 검증 완료되었습니다.**

Current validated renderer paths:

- `musica-reference-local` — deterministic bounded reference renderer;
- `musica-fluidsynth-local` — real Windows FluidSynth 2.6.0 + externally provisioned, exact-hash-bound FluidR3_GM 3.1 evidence path.

M5-R2 proves a real replaceable 48 kHz stereo local renderer boundary; it does **not** prove perceptual superiority or professional/mastering quality.

M5-R2는 실제 교체 가능한 48 kHz stereo local renderer 경계를 증명하지만 청감상 우월성 또는 professional/mastering 품질을 증명하지 않습니다.

The next bounded milestone is **M5-R3 — DAW / Interchange Interoperability v0**. The current selection package chooses **DAWproject 1.0** as the first implementation target, subject to exact-head CI/merge and later executable evidence.

다음 제한 마일스톤은 **M5-R3 — DAW / Interchange Interoperability v0**입니다. 현재 selection package는 **DAWproject 1.0**을 첫 구현 대상으로 선정하며, exact-head CI/병합과 이후 실행 근거가 필요합니다.

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
- **Shape / 의미·구조 편집** — semantic axes, sections and scoped preview / 의미 제어·구간·범위 preview
- **Inspect / 전문 검사** — locks, exact diff, accepted/preview status, branches/history / lock·정확한 diff·상태·버전 이력
- **Code / 코드·근거** — read-only validated JSON and authority evidence / 읽기 전용 검증 JSON·권한 근거

These are views over one project state, not incompatible modes or separate databases.

이는 서로 다른 비호환 모드나 별도 데이터베이스가 아니라 하나의 프로젝트 상태를 보는 네 가지 깊이입니다.

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
PREVIEW — non-canonical / 비공식 상태
  ↓ explicit Accept only / 명시적 승인만
M2 Project & Version Engine
  ↓
Accepted Blueprint Revision
  ↓ trusted lowering
Canonical Music IR
  ↓
M5 replaceable Renderer / Interchange adapters
```

**AI output is not accepted state. Preview audio is not accepted state. Browser memory is not accepted state. Renderer output is not accepted state. Imported DAW/interchange state is not accepted state.**

**AI 출력, Preview 오디오, Browser memory, Renderer output, 외부 DAW/interchange import 상태는 승인 상태가 아닙니다.**

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
  ↓
Validated Blueprint Revision + Diff
  ↓
Music Compiler
  ↓
Music IR
  ↓
Renderer Adapters / Interchange Adapters
  ↓
MIDI / local synth / DAWproject / future sampler·DAW·DSP·generative audio
```

Important distinction / 중요 구분:

> **Music Blueprint = canonical human/AI creative state. / 인간·AI가 공유하는 공식 창작 상태.**
>
> **Music IR = lower-level executable representation produced by compilation. / 컴파일로 생성되는 저수준 실행 표현.**
>
> **External interchange artifact = non-canonical projection/candidate carrier. / 외부 교환 artifact는 비공식 투영·candidate 운반체.**

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
| M5-R3 DAW / Interchange Interoperability | **SELECTION: DAWproject 1.0 — IMPLEMENTATION NOT YET VALIDATED** | `docs/M5_R3_INTERCHANGE_SELECTION.md` |
| M5-R4 Comparative Music/Audio Quality Evaluation | **NOT IMPLEMENTED** | planned follow-on |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |

## M5-R3 selected boundary / M5-R3 선정 경계

Current design documents:

- `docs/M5_R3_INTERCHANGE_SELECTION.md`
- `docs/M5_R3_ROUNDTRIP_AUTHORITY.md`
- `docs/M5_R3_ACCEPTANCE.md`

Selected authority model:

```text
Accepted .musica revision
→ DAWproject export
→ optional external edit
→ DAWproject import
→ NON-CANONICAL candidate
→ diff + loss report
→ HARD lock / constraint validation
→ explicit user Accept
→ M2 commit
```

An external DAW file can propose changes but cannot silently overwrite MUSICA authority.

외부 DAW 파일은 변경을 제안할 수 있지만 MUSICA 권한을 조용히 덮어쓸 수 없습니다.

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
6. relevant milestone acceptance/evidence documents
7. relevant Issue / PR / exact-head CI evidence

## Current exact next point / 현재 정확한 다음 재개점

After the M5-R3 selection package passes exact-head CI and is merged, create a fresh implementation branch from the new main and implement the **bounded DAWproject 1.0 export → safe import-as-candidate → loss/diff → HARD-lock validation → explicit Accept → M2 commit** path defined by `memory/NEXT_ACTION.md` and `docs/M5_R3_ACCEPTANCE.md`.

M5-R3 selection package가 exact-head CI를 통과해 병합된 후 새 main에서 구현 branch를 생성하여 `memory/NEXT_ACTION.md` 및 `docs/M5_R3_ACCEPTANCE.md`에 정의된 **제한 DAWproject 1.0 export → 안전한 candidate import → loss/diff → HARD-lock 검증 → 명시적 Accept → M2 commit** 경로를 구현합니다.
