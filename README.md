# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation** built around one product promise:

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**
>
> **자연어로 지시할 만큼 쉽고, 전문 음악 시스템처럼 세밀하게 편집할 만큼 정밀해야 한다.**

MUSICA is not a text-to-song clone and is not designed around one renderer or one DAW. Natural-language intent is lowered into inspectable contracts, protected by locks/constraints, compiled into executable music, rendered or exchanged through replaceable adapters, and accepted into durable project revisions only through explicit authority boundaries.

MUSICA는 text-to-song 복제 제품도 특정 renderer/DAW 중심 시스템도 아닙니다. 자연어 의도는 검사 가능한 계약으로 구조화되고 lock/constraint로 보호되며 실행 가능한 음악으로 컴파일됩니다. Renderer와 interchange는 교체 가능한 adapter이고 공식 프로젝트 revision은 명시적인 권한 경계를 통과할 때만 승인됩니다.

## Current canonical status / 현재 공식 상태

**M0 → M6-R3 are validated within their explicitly bounded claims.**

**M0 → M6-R3는 각 명시적 제한 주장 범위에서 검증 완료되었습니다.**

M6-R0 ratified the canonical exact-note authority/data model. M6-R1 implemented the bounded trusted-core edit engine. M6-R2 exposed it through the Browser Studio Inspect piano roll. M6-R3 proved that exact-note path through real Chromium, including all six primitive operations, explicit Preview/Accept/Discard, restart/reopen persistence, and visible fail-closed HARD-lock/stale-source conflict UX.

M6-R0는 canonical exact-note 권한/데이터 모델을 비준했고, M6-R1은 제한된 trusted-core edit engine을 구현했습니다. M6-R2는 이를 Browser Studio Inspect piano roll에 연결했으며, M6-R3는 실제 Chromium에서 6개 primitive operation, 명시적 Preview/Accept/Discard, 재시작·재오픈 보존, HARD-lock/stale-source fail-closed conflict UX까지 검증했습니다.

The next bounded milestone is **M6-R4 — bounded interchange reconciliation for representable exact-note edits**.

다음 제한 마일스톤은 **M6-R4 — 표현 가능한 exact-note 편집의 제한된 interchange reconciliation**입니다.

R4 will not grant a DAW or DAWproject artifact canonical authority. It may only convert provably source-bound, stable-identity, representable note differences from a MUSICA-origin bounded DAWproject artifact into the existing typed M6 `NoteEditCandidate` primitives, which still require normal M6 validation and explicit M2 acceptance.

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

## One state, four depths / 하나의 상태, 네 가지 깊이

The Browser Studio exposes progressively deeper control over the same canonical `.musica` project state:

- **Direct / 간편 디렉팅** — natural-language creation/refinement and audition
- **Shape / 의미·구조 편집** — semantic axes, sections and scoped Preview
- **Inspect / 전문 편집·검사** — locks, exact diff, accepted/preview state, branches/history and exact-note piano roll
- **Code / 코드·근거** — read-only validated JSON and authority evidence

These are views over one project state, not separate databases or incompatible modes.

## Canonical authority / 공식 권한 구조

```text
User / 사용자
  ↓
Browser Studio / API / bounded interchange proposal
  ↓
M4 Application Service + typed candidate boundaries
  ↓
M0/M1 contracts + HARD locks + M6 exact-note authority
  ↓
PREVIEW — non-canonical
  ↓ explicit Accept only
M2 Project & Version Engine
  ↓
Accepted Blueprint Revision
  ↓ trusted lowering
Music IR — derived executable state
  ↓
M5 replaceable renderer / interchange / evaluation adapters
```

M6 exact-note editing preserves the same ownership rule:

```text
Accepted exact-note Blueprint
→ deterministic source-bound projection
→ Browser or future bounded interchange input
→ typed NoteEditCandidate
→ source + stable-ID lock + constraint validation
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept / Discard
→ existing M2 revision authority
→ trusted deterministic Music IR
```

**AI output is not accepted state. Preview audio is not accepted state. Browser memory/DOM/canvas state is not accepted state. Direct Music IR edits are not accepted state. Renderer output is not accepted state. Comparison output is not accepted state. Imported DAW/interchange state is not accepted state.**

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

> **Music Blueprint = canonical human/AI creative state.**
>
> **Music IR = lower-level executable representation produced by compilation.**
>
> **External renderer/interchange/comparison artifact = non-canonical output, candidate carrier or evidence.**

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
| M6-R2 Browser Studio Piano-Roll / Inspect Surface | **VALIDATED — BOUNDED BROWSER INTEGRATION** | `evidence/M6_R2_VALIDATION.md` |
| M6-R3 Real-browser Exact-Note E2E + Lock/Conflict UX | **VALIDATED — BOUNDED REAL-BROWSER EXACT-NOTE E2E** | `evidence/M6_R3_VALIDATION.md` |
| M6-R4 Bounded interchange exact-note reconciliation | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| Human-subject usability/perceptual evidence | **NOT VALIDATED** | separate controlled study required |

## M6-R3 validated boundary / M6-R3 검증 경계

M6-R3 validates the real-browser path over the already trusted M6 authority:

```text
Accepted exact-note Blueprint
→ deterministic Studio note view
→ real Chromium Browser Studio Inspect piano roll
→ browser exact-note input
→ typed stable-ID NoteEditCandidate
→ M6-R1 authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept / Discard
→ existing M2 commit only
→ accepted Blueprint
→ restart/reopen persistence
```

Validated bounded properties include:

- all six primitive operations browser-exercised: `INSERT / DELETE / MOVE / RESIZE / REPITCH / SET_VELOCITY`;
- exact project/revision/Blueprint SHA-256 source binding;
- accepted ref unchanged before explicit Accept;
- Discard preserves accepted state;
- explicit Accept advances exactly once through M2;
- accepted REPITCH persists after service restart/browser reopen;
- real-browser HARD lock conflict is visibly `BLOCKED / HARD_LOCK_VIOLATION` with stable note/rule context and no pending Preview;
- real-browser stale source is visibly `BLOCKED / STALE_SOURCE` with no pending Preview or silent rebase;
- legacy motif-only projects expose exact editing unavailable and fabricate no canonical notes;
- browser console/page error counts are zero in canonical evidence;
- browser project mutation authority and Music IR mutation authority remain false.

Final M6-R3 evidence-bearing head: `c4b525a9083ff8a537b411789b8bbfbf39c04a7b`  
Implementation merge: `327939e71bd63611f747bac147c4ba6591052b93`  
Final artifact ID: `10305989929`  
Artifact SHA-256: `2e44021ddd2a2803379f2223b045463d1a81c334afdb695d10df9b8fc5d914c0`  
Internal manifest SHA-256: `825c5d69f55a40ba77deefe1bdb3bba4974f0ed26d0cf1696aa11718dcff58ec`

## M6-R4 boundary / M6-R4 경계

M5-R3 historical evidence correctly blocks arbitrary external note reverse mapping. M6-R4 may introduce a new bounded path only when all of the following are proven:

```text
MUSICA-origin export lineage
+ exact accepted source binding
+ deterministic baseline-versus-returned comparison
+ stable note identity/part mapping
+ exact representation as existing M6 primitives
+ normal M6 lock/constraint authority
```

A returned DAWproject is never accepted by itself. Unsupported, ambiguous, stale or provenance-broken changes must fail closed. Arbitrary external DAW reverse mapping remains outside the claim boundary.

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
3. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
4. `docs/M5_R3_ACCEPTANCE.md`
5. `docs/M5_R3_ROUNDTRIP_AUTHORITY.md`
6. `evidence/M5_R3_VALIDATION.md`
7. `evidence/M6_R1_VALIDATION.md`
8. `evidence/M6_R2_VALIDATION.md`
9. `evidence/M6_R3_VALIDATION.md`
10. `memory/CURRENT_STATE.md`
11. `memory/NEXT_ACTION.md`
12. relevant Issue / PR / exact-head CI evidence

## Current exact next point / 현재 정확한 다음 재개점

Start **M6-R4 — bounded interchange reconciliation for representable exact-note edits**.

Reuse the existing M5-R3 DAWproject parser/exporter and M6-R1 exact-note authority. Establish an exact export lineage and stable note identity mapping, compare returned artifacts against the exact MUSICA-exported normalized baseline, and convert only provably representable note changes into existing typed M6 primitives. Unsupported or ambiguous changes remain blocked; explicit M2 Accept remains the only canonical mutation path.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
