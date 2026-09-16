# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**POST-M7 CLOSURE REVIEW — EVIDENCE-BASED NEXT-MILESTONE SELECTION**

M7-R6 is `VALIDATED — BOUNDED TRUTHFUL AUDITION INSPECTION`. The repository does not currently ratify an `M7-R7` or `M8`. Do not infer a new milestone from numbering, implementation momentum or adjacent technical possibility.

The next mission is a **bounded planning gate** that selects exactly one successor milestone from evidence.

## Canonical starting point / 공식 시작점

- M7-R6 Issue `#86` — **COMPLETED**
- M7-R6 PR `#87` — **MERGED**
- implementation/validation merge main: `1de099e8d3e489c818ae561ddfb0c43c4ffdcbfc`
- pre-durable head: `af11315c777f761179ca3d94bfed1a6e472dd315`
- successor evidence head: `93129768ff4b33c663eeeccda22c1d07faea0872`
- final validation-record head: `0ea3fd976a8b63293d434bb427f7dfeffb68fcfd`
- pre-durable / successor / final-record permanent gates: **14/14 SUCCESS** each
- deterministic manifest SHA-256: `926c0608c5998ceaa1ac0f49c19dbf4f293acc180d0e2433d067b369d32b953a`
- deterministic pre-durable vs successor evidence: **14 files / 0 differences**
- accepted/reopened WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- accepted/reopened MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- durable evidence: `evidence/M7_R6_VALIDATION.md`

## Why a planning gate is required / 왜 계획 게이트가 필요한가

M0→M7 now validates a broad vertical slice:

```text
intent / Blueprint authority
→ immutable project/version authority
→ AI Director/provider boundary
→ Browser Studio workflow
→ rendering/interchange/evaluation
→ exact-note precision editing
→ canonical automation editing
→ deterministic automation lowering
→ one bounded audible renderer mapping
→ Studio audible Preview / Accept / reopen
→ truthful Browser audition inspection
```

At this point, several legitimate directions remain, but the repository contains no evidence that any one of them should automatically become the next milestone. Continuing the M7 numbering by inertia would blur product priority with implementation convenience.

## Review objective / 검토 목표

Select **one and only one** bounded next milestone that maximizes product leverage while preserving MUSICA authority discipline.

The review must answer:

1. What is the highest-value user workflow still blocked by the validated stack?
2. Which missing capability is prerequisite-like rather than merely adjacent?
3. Which candidate can be specified with a narrow authority boundary and deterministic evidence?
4. Which candidate reuses the greatest amount of already validated infrastructure?
5. Which candidate has the lowest risk of silently expanding canonical authority?
6. What should explicitly remain deferred after the selection?

## Candidate domains to inspect / 검토할 후보 영역

These are **candidate domains, not approved milestones and not a ranking**:

### A. Intent-to-music product workflow
Close gaps between user intent, AI Director proposals, Preview, bounded editing and accepted project revisions so a normal user can complete a coherent end-to-end creation session with less low-level intervention.

### B. AI provider execution
Revisit the currently bounded provider layer and determine whether live provider execution, reproducible prompt/model provenance or provider failover is now the highest-leverage missing layer.

### C. Automation expressiveness
Consider whether another automation mapping, lane management, tempo behavior or curve family is actually required by product workflows. Do **not** expand this merely because M7 validated one mapping.

### D. Interchange / external workflow
Assess whether automation-aware DAW interchange/reconciliation is now more valuable than additional internal editing capability.

### E. Real-time interaction
Assess MIDI/OSC/live control only if an actual user workflow justifies introducing a new derived control adapter and latency evidence boundary.

### F. Distribution / usability hardening
Assess project packaging, installer/desktop delivery, recovery, performance, accessibility or user-facing workflow reliability if product usability is now the bottleneck rather than musical expressiveness.

## Required evidence inputs / 필수 입력

At minimum inspect:

```text
governance/SOURCE_OF_TRUTH.md
docs/PRODUCT_THESIS.md
memory/CURRENT_STATE.md
docs/M7_AUTOMATION_AUTHORITY.md
evidence/M4_R3_VALIDATION.md
evidence/M5_R4_VALIDATION.md
evidence/M6_R4_VALIDATION.md
evidence/M7_R6_VALIDATION.md
schemas + runtime boundaries implicated by each candidate
current Browser Studio workflow
current Director/provider workflow
current explicit non-claims
```

Do not base the decision only on conversation memory.

## Selection criteria / 선정 기준

For every serious candidate, record at least:

- **User leverage:** which concrete workflow becomes possible or materially easier;
- **Dependency readiness:** how much of the prerequisite stack is already validated;
- **Authority risk:** probability of creating an ambiguous canonical/derived boundary;
- **Evidence feasibility:** whether success can be proven deterministically and independently;
- **Regression surface:** number and criticality of existing validated layers touched;
- **Implementation boundedness:** whether one mission can close the capability without scope creep;
- **Strategic sequencing:** whether later high-value capabilities depend on this one.

Do not select by a single numeric score alone. Record factual trade-offs and an explicit decision rationale.

## Required planning outputs / 필수 산출물

The planning mission should produce a durable package such as:

```text
one next-milestone Issue
one explicit mission statement
problem / user workflow blocked
canonical vs derived authority decision
bounded scope + explicit non-goals
expected implementation surface
test matrix
evidence package target
permanent-regression set
promotion criteria
updated memory/NEXT_ACTION.md
```

If the review cannot identify a sufficiently bounded, high-leverage successor, record `HOLD — NEXT MILESTONE NOT YET RATIFIED` rather than inventing work.

## Guardrails / 가드레일

The review must not silently authorize:

- new canonical authority from Browser/audio/renderer/DAW state;
- another renderer mapping merely to extend coverage;
- MIDI CC or plugin addresses as canonical parameter identities;
- implicit AI acceptance;
- unbounded “complete DAW” scope;
- perceptual superiority claims without appropriate evidence;
- destructive mutation of accepted project history.

## Maximum intended outcome / 최대 의도 결과

> **MUSICA selects one evidence-backed, bounded successor milestone after M7-R6, with its user value, authority boundary, dependencies, non-goals, tests and promotion evidence ratified before implementation begins.**

## Execution discipline / 실행 규율

```text
M7-R6 state-only closure
→ inspect M0→M7 validated stack + product thesis + non-claims
→ enumerate serious successor candidates
→ compare user leverage / dependency readiness / authority risk / evidence feasibility
→ select exactly one bounded successor OR HOLD
→ create Issue
→ update canonical NEXT_ACTION
→ only then create implementation branch
```

**Repository evidence remains authoritative over conversation/model memory.**