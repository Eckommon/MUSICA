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

**M0 → M6-R1 are validated within their explicitly bounded claims.**

**M0 → M6-R1은 각 명시적 제한 주장 범위에서 검증 완료되었습니다.**

M6-R0 ratified the exact-note authority/data model. M6-R1 then implemented and validated the bounded trusted-core runtime for exact-note material, stable-ID note editing, fail-closed stale/lock handling, non-canonical Preview, explicit M2 acceptance and deterministic lowering.

M6-R0는 exact-note 권한/데이터 모델을 비준했고, M6-R1은 exact-note material, stable-ID note editing, stale/lock fail-closed 처리, non-canonical Preview, 명시적 M2 Accept, 결정론 lowering을 trusted core에 구현·검증했습니다.

The next bounded milestone is **M6-R2 — Browser Studio Piano-Roll / Inspect Surface**.

다음 제한 마일스톤은 **M6-R2 — Browser Studio Piano-Roll / Inspect Surface**입니다.

R2 exposes the already validated M6-R1 authority path through Browser Studio Inspect. It does **not** grant browser DOM/canvas state or Music IR direct project authority.

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
- **Inspect / 전문 편집·검사** — locks, exact diff, accepted/preview state, branches/history and the M6 precision-editing surface / lock·정확 diff·상태·버전 이력·M6 정밀 편집
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
  ↓
trusted lowering
  ↓
Music IR — derived executable state
  ↓
M5 replaceable adapters / evaluation
```

M6 exact-note editing preserves the same ownership rule:

```text
Accepted exact-note Blueprint
→ read projection
→ typed NoteEditCandidate
→ source + lock + constraint validation
→ PREVIEW — non-canonical
→ explicit Accept
→ M2 revision
→ trusted deterministic Music IR
```

**AI output is not accepted state. Preview audio is not accepted state. Browser memory/DOM/canvas state is not accepted state. Direct Music IR edits are not accepted state. Renderer output is not accepted state. Comparison output is not accepted state. Imported DAW/interchange state is not accepted state.**

**AI 출력, Preview 오디오, Browser memory/DOM/canvas 상태, Music IR 직접 편집, Renderer output, 비교 결과, 외부 DAW/interchange import 상태는 승인 상태가 아닙니다.**

The accepted `.musica` Project Bundle remains canonical.

## System model / 시스템 모델

```text
Intent / 의도
  ↓
AI Music Director / AI 음악 디렉터
  ↓
Music Blueprint / 음악 설계도
  ├─ semantic material
  └─ exact-note material when explicitly present
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
| M6-R1 Typed Exact-Note Material + Edit Engine | **VALIDATED — BOUNDED CORE RUNTIME** | `evidence/M6_R1_VALIDATION.md` |
| M6-R2 Browser Studio Piano-Roll / Inspect Surface | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| Human-subject usability/perceptual evidence | **NOT VALIDATED** | separate controlled study required |

## M6-R1 validated boundary / M6-R1 검증 경계

M6-R1 validates the trusted-core exact-note authority/runtime path:

```text
Accepted Blueprint revision
→ exact source binding
→ stable-ID NoteEditCandidate
→ exact-note invariants
→ stable-ID HARD note lock + existing lock/constraint validation
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW — non-canonical
→ explicit Accept only
→ existing M2 commit
→ accepted Blueprint
→ deterministic exact-note lowering
→ Music IR
```

Validated bounded properties include:

- optional `materials.melody.exact_timeline`;
- legacy `motif_notes` compatibility;
- stable `note_id + part_id` addressing;
- operations `INSERT / DELETE / MOVE / RESIZE / REPITCH / SET_VELOCITY`;
- exact project/revision/Blueprint SHA-256 stale protection;
- stable-ID HARD note locks that cannot be bypassed by direct M2 commit;
- faithful pitch/start/duration/velocity lowering;
- side-effect-free Preview and explicit M2 acceptance;
- deterministic evidence and project integrity after acceptance.

M6-R1 does **not** validate Browser Studio piano-roll interaction. That claim begins only after M6-R2/M6-R3 evidence.

## M5-R4 validated boundary / M5-R4 검증 경계

M5-R4 can reproducibly compare two renderer outputs derived from the same exact canonical Music IR for technical validity and a frozen objective signal-descriptor set. It does not prove listener preference or renderer superiority.

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
6. `docs/M6_R1_RUNTIME.md`
7. `evidence/M6_R1_VALIDATION.md`
8. `memory/CURRENT_STATE.md`
9. `memory/NEXT_ACTION.md`
10. relevant Issue / PR / exact-head CI evidence

## Current exact next point / 현재 정확한 다음 재개점

Start **M6-R2 — Browser Studio Piano-Roll / Inspect Surface**.

Integrate the validated M6-R1 exact-note engine into the existing Studio service and Inspect UI: deterministic accepted-note read projection, typed note-edit Preview endpoint, stable-ID/lock visibility, audible Preview, explicit Accept/Discard, and bounded piano-roll interaction. Do not create browser-side canonical state or direct Music IR mutation authority.

**M6-R2 — Browser Studio Piano-Roll / Inspect Surface**부터 시작합니다. 검증된 M6-R1 exact-note engine을 기존 Studio service/Inspect UI에 통합하되 browser-side canonical state나 Music IR 직접 수정 권한을 만들지 않습니다.
