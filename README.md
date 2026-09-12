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

**M0 → M6-R0 are validated within their explicitly bounded claims.**

**M0 → M6-R0는 각 명시적 제한 주장 범위에서 검증 완료되었습니다.**

Validated external-output/evaluation boundaries include:

- `musica-reference-local` — deterministic bounded reference renderer;
- `musica-fluidsynth-local` — bounded real Windows FluidSynth 2.6.0 + exact-hash-bound external FluidR3_GM 3.1 renderer path;
- `DAWproject 1.0 bounded profile` — deterministic export + safe non-canonical import-candidate bridge with explicit loss reporting and M2 acceptance authority;
- `musica-objective-audio-comparison-v0` — exact-source objective renderer comparison with explicit confounds and no perceptual-superiority inference.

M6-R0 has now ratified the exact-note authority/data contract: stable note identity, beat-domain exact-note material, source-bound edit candidates, fail-closed authority results, and the rule that Music IR may never become accepted project authority.

M6-R0는 stable note identity, beat-domain exact-note material, source-bound edit candidate, fail-closed authority result와 Music IR 직접 승격 금지를 공식 계약으로 비준했습니다.

The next bounded milestone is **M6-R1 — Typed Exact-Note Material + Edit Engine**.

다음 제한 마일스톤은 **M6-R1 — Typed Exact-Note Material + Edit Engine**입니다.

M6-R1 implements the R0 contracts in the trusted core before any piano-roll UI is allowed to mutate project state.

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

M6 deepens **Inspect** from inspection into bounded exact-note editing while preserving the same authority model. R0 defines that authority; R1 implements the trusted backend path; R2 will expose it through the browser surface.

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
  ↓
trusted lowering
  ↓
Canonical Music IR
  ↓
M5 replaceable adapters / evaluation
  ├─ Renderer → audio/artifacts + QA + provenance
  ├─ Interchange → external artifact → NON-CANONICAL candidate
  └─ Comparison → objective evidence only
```

M6 exact-note editing follows the same ownership rule:

```text
NoteEditCandidate
→ Blueprint candidate
→ validation
→ PREVIEW
→ explicit Accept
→ M2 revision
→ Music IR
```

**AI output is not accepted state. Preview audio is not accepted state. Browser memory is not accepted state. Direct Music IR edits are not accepted state. Renderer output is not accepted state. Comparison output is not accepted state. Imported DAW/interchange state is not accepted state.**

**AI 출력, Preview 오디오, Browser memory, Music IR 직접 편집, Renderer output, 비교 결과, 외부 DAW/interchange import 상태는 승인 상태가 아닙니다.**

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
Renderer / Interchange / Evaluation Adapters
  ↓
MIDI / local synth / DAWproject / objective analysis / future sampler·DAW·DSP·generative audio
```

Important distinction / 중요 구분:

> **Music Blueprint = canonical human/AI creative state. / 인간·AI가 공유하는 공식 창작 상태.**
>
> **Music IR = lower-level executable representation produced by compilation. / 컴파일로 생성되는 저수준 실행 표현.**
>
> **External renderer/interchange/comparison artifact = non-canonical output, candidate carrier or evidence. / 외부 renderer/interchange/comparison artifact는 비공식 출력·candidate 운반체·근거이다.**

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
| M5-R4 Comparative Music/Audio Quality Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R4_VALIDATION.md` |
| M6-R0 Precision Editing Authority & Canonical Note Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M6_R0_VALIDATION.md` |
| M6-R1 Typed Exact-Note Material + Edit Engine | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| Human-subject usability/perceptual evidence | **NOT VALIDATED** | separate controlled study required |

## M6-R0 validated boundary / M6-R0 검증 경계

M6-R0 validates the authority/data contract for exact-note creative decisions:

```text
Accepted Blueprint revision
→ trusted lowering
→ Music IR

User exact-note edit
→ typed NoteEditCandidate
→ source revision/hash validation
→ Blueprint-representable delta
→ HARD lock / constraint validation
→ PREVIEW — non-canonical
→ explicit Accept only
→ new M2 revision
→ trusted lowering
→ new Music IR
```

Validated design properties include stable `note_id + part_id` addressing, quarter-note-beat canonical timing, additive `explicit_timeline` material, stale-source fail-closed behavior, explicit acceptance, and prohibition of direct Music IR authority.

M6-R0 does **not** yet prove that the runtime edit engine, stable-ID note-lock selector or piano-roll UI exists. Those claims begin only after M6-R1/M6-R2 evidence.

## M5-R4 validated boundary / M5-R4 검증 경계

M5-R4 can reproducibly compare two renderer outputs derived from the same exact canonical Music IR for technical validity and a frozen objective signal-descriptor set.

Validated boundary:

```text
same accepted Blueprint revision
→ same exact canonical Music IR
├─ reference renderer
└─ FluidSynth renderer
→ exact provenance + QA gate
→ native-format objective analysis
→ explicit confounds
→ paired descriptive deltas
→ COMPARABLE_OBJECTIVE_ONLY
```

M5-R4 does **not** prove listener preference or renderer superiority:

```text
HUMAN_SUBJECT_EVIDENCE = NOT_VALIDATED
PERCEPTUAL_SUPERIORITY = UNKNOWN
HUMAN_PREFERENCE_CLAIM_ALLOWED = false
```

## Repository as Source of Truth / GitHub를 공식 근거로 사용

This repository is the implementation workspace, project memory, decision ledger and anti-hallucination evidence boundary.

Authority rule / 권위 규칙:

```text
Accepted repository artifacts/tests/evidence
> merged specs/current-state records
> Issue/PR/CI evidence
> conversation context
> model memory
> model inference
```

No AI agent may claim that a feature, test, milestone, artifact or integration exists without repository evidence.

Before substantive work read / 실질 작업 전 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
5. `docs/M6_ACCEPTANCE.md`
6. `memory/CURRENT_STATE.md`
7. `memory/NEXT_ACTION.md`
8. relevant milestone acceptance/evidence documents
9. relevant Issue / PR / exact-head CI evidence

## Current exact next point / 현재 정확한 다음 재개점

Start **M6-R1 — Typed Exact-Note Material + Edit Engine**.

Implement the accepted M6-R0 contracts in the trusted core: optional exact-note Blueprint validation, exact deterministic lowering, stable-ID note operations, source-hash stale protection, additive stable-ID note-lock handling, side-effect-free preview, exact diff/provenance and explicit M2 acceptance. Do not implement the browser piano roll until this core path is validated.

**M6-R1 — Typed Exact-Note Material + Edit Engine**부터 시작합니다. M6-R0 계약을 core runtime에 구현하고, 이 경로가 검증되기 전에는 browser piano roll을 구현하지 않습니다.
