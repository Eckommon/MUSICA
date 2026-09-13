# MUSICA

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

MUSICA is an **AI-native programmable music workstation** built around one product promise:

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**

It is not a text-to-song clone and is not organized around one renderer or one DAW. Natural-language intent becomes inspectable contracts; accepted creative state lives in the Music Blueprint/project revision model; derived execution state lives in Music IR; renderer/interchange/evaluation systems remain adapters.

## Current canonical status / 현재 공식 상태

**M0 → M6-R4 are validated within their explicitly bounded repository claims.**

The first M6 precision-editing tranche is complete:

```text
M6-R0  exact-note authority/data model                 VALIDATED — DESIGN
M6-R1  typed exact-note runtime                        VALIDATED — BOUNDED
M6-R2  Browser Studio piano roll                       VALIDATED — BOUNDED
M6-R3  real Chromium exact-note E2E/conflict UX        VALIDATED — BOUNDED
M6-R4  source-bound DAWproject note reconciliation     VALIDATED — BOUNDED
```

M6-R4 does **not** grant DAW/interchange state authority. It translates only one uniquely provable representable note change from an exact MUSICA-origin bounded DAWproject export into the same existing M6 `NoteEditCandidate` authority. Ambiguous, stale, multi-note, multi-field and lock-conflicting cases fail closed.

Durable M6-R4 evidence: `evidence/M6_R4_VALIDATION.md`.

The next phase is deliberately **contract/design first**:

> **M7-R0 — Canonical Automation & Continuous-Control Authority**

No prior M6-R5/M7 roadmap existed after M6-R4. M7-R0 is introduced to close a product-thesis gap: Inspect-level professional control explicitly includes automation, synthesis, DSP and mix parameters, but the repository does not yet have a canonical editable continuous-control authority model.

## Try the local Studio / 로컬 Studio 실행

```bash
python -m pip install -e '.[dev]'
musica-studio
```

Default:

```text
Workspace: ~/MUSICA-Workspace
URL: http://127.0.0.1:8765/
```

Useful options:

```bash
musica-studio --workspace ./my-musica-workspace
musica-studio --port 8877
musica-studio --no-browser
```

The Studio is loopback-only by design. It requires no cloud account, telemetry, remote asset CDN or live OpenAI credential to start. The offline fixture Director is the default; OpenAI is an explicit optional provider mode.

## One state, four depths / 하나의 상태, 네 가지 깊이

The Browser Studio exposes progressively deeper control over the same canonical `.musica` project state:

- **Direct** — natural-language creation/refinement and audition
- **Shape** — semantic axes, sections, structure and locks
- **Inspect** — exact notes, diffs, locks, history, piano roll and future explicit automation controls
- **Code** — validated JSON, API/CLI, programmable transforms and evidence

These are views over one project state, not separate databases or incompatible modes.

## Canonical authority / 공식 권한 구조

```text
User / AI / bounded external proposal
        ↓
typed non-canonical candidate
        ↓
source binding + locks + constraints + project invariants
        ↓
READY_FOR_PREVIEW or BLOCKED
        ↓
PREVIEW · NOT ACCEPTED
        ↓ explicit Accept only
M2 Project & Version Engine
        ↓
Accepted Music Blueprint revision
        ↓ trusted deterministic lowering
Music IR — derived executable state
        ↓
Renderer / Interchange / Evaluation adapters
```

**AI output is not accepted state. Preview audio is not accepted state. Browser DOM/canvas state is not accepted state. Direct Music IR edits are not accepted state. Renderer output is not accepted state. Imported DAW/interchange state is not accepted state.**

The accepted `.musica` project remains canonical.

## System model / 시스템 모델

```text
Intent
  ↓
AI Music Director
  ↓
Music Blueprint
  ├─ semantic material
  ├─ exact-note material
  └─ future canonical automation material only after M7 ratification
  ↓
Locks + Constraints + Version Authority
  ↓
Music Compiler
  ↓
Music IR
  ↓
Renderer / Interchange / Evaluation
```

Important distinction:

> **Music Blueprint = canonical human/AI creative state.**
>
> **Music IR = derived executable representation.**
>
> **External renderer/interchange/comparison artifact = non-canonical output, proposal carrier or evidence.**

## Validated milestone stack / 검증 마일스톤

| Milestone | Status | Evidence |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4 Browser Studio / Usable MVP | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` → `M4_R3_VALIDATION.md` |
| M5 Rendering / Interchange / Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R1_VALIDATION.md` → `M5_R4_VALIDATION.md` |
| M6-R0 Exact-Note Authority | **VALIDATED — DESIGN** | `evidence/M6_R0_VALIDATION.md` |
| M6-R1 Exact-Note Runtime | **VALIDATED — BOUNDED** | `evidence/M6_R1_VALIDATION.md` |
| M6-R2 Browser Piano Roll | **VALIDATED — BOUNDED** | `evidence/M6_R2_VALIDATION.md` |
| M6-R3 Real-Browser Exact-Note E2E | **VALIDATED — BOUNDED** | `evidence/M6_R3_VALIDATION.md` |
| M6-R4 Interchange Note Reconciliation | **VALIDATED — BOUNDED** | `evidence/M6_R4_VALIDATION.md` |
| M7-R0 Automation Authority & Canonical Model | **NOT IMPLEMENTED — NEXT DESIGN MILESTONE** | `memory/NEXT_ACTION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate live-provider evidence required |
| Human-subject usability/perceptual evidence | **NOT VALIDATED** | separate study required |

## M6-R4 bounded claim / M6-R4 제한 주장

The maximum authorized R4 claim is:

> **A MUSICA-origin bounded DAWproject artifact can carry one uniquely provable representable exact-note change back as a source-bound stable-identity `NoteEditCandidate`, which remains non-canonical and is accepted only after normal M6 authority and explicit M2 acceptance.**

R4 evidence additionally proves deterministic evidence generation itself: the dedicated workflow generates the canonical evidence tree twice and requires byte-identical output before upload.

## Current non-claims / 현재 비주장

MUSICA does not yet validate:

- live OpenAI API execution;
- human preference/usability evidence;
- perceptual/mastering superiority;
- arbitrary external DAW compatibility;
- arbitrary DAW reverse mapping;
- non-MUSICA-origin reconciliation;
- multi-note/batch interchange reconciliation;
- arbitrary tempo maps;
- canonical automation/mixer/plugin editing;
- VST/AU/CLAP hosting;
- waveform/destructive audio editing;
- live MIDI recording;
- cloud collaboration;
- installer/signing.

## Repository as source of truth / Repo를 공식 근거로 사용

Authority order:

```text
accepted repository tests/artifacts/evidence
> merged specifications/current-state records
> Issue/PR/exact-head CI evidence
> conversation context
> model memory/inference
```

Before substantive work read:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/design/MUSICA_DESIGN_PACKAGE_v0.1.md`
4. `docs/M6_PRECISION_EDITING_AUTHORITY.md`
5. `docs/M6_R4_ACCEPTANCE.md`
6. `evidence/M6_R4_VALIDATION.md`
7. `memory/CURRENT_STATE.md`
8. `memory/NEXT_ACTION.md`

## Exact next point / 정확한 다음 재개점

Start **M7-R0 — Canonical Automation & Continuous-Control Authority** as a contract/design-only milestone. Ratify canonical ownership, stable parameter/lane/point identity, time/value domains, interpolation, edit primitives, lock semantics, source binding, semantic-control coexistence and deterministic lowering **before** implementing automation lanes or runtime editing.

**Repository evidence remains authoritative over conversation/model memory.**
