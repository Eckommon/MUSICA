# M3-R1 Acceptance — AI Music Director Provider Boundary / M3-R1 수용 — AI Music Director Provider 경계

**Status / 상태:** PROPOSED UNTIL EXACT-HEAD CI PASSES / exact-head CI 통과 전 제안 상태

## 1. Objective / 목표

M3-R1 proves that a probabilistic or external AI provider can participate in MUSICA as a **non-authoritative proposal engine** while MUSICA contracts, deterministic transforms, HARD locks, constraints, and explicit revision acceptance remain authoritative.

M3-R1은 확률적 또는 외부 AI provider가 MUSICA에서 **비권위 제안 엔진**으로 참여할 수 있음을 증명하되, MUSICA 계약·결정론 transform·HARD lock·constraint·명시적 revision 승인이 계속 공식 권위를 갖도록 합니다.

## 2. Acceptance criteria / 수용 기준

M3-R1 is accepted only if repository evidence proves all of the following.

다음 항목을 레포 근거가 모두 증명할 때만 M3-R1을 수용합니다.

1. `Director Provider Capability v0`, `Director Request v0`, `Director Proposal v0`, and `Director Trace v0` are valid Draft 2020-12 JSON Schemas.
2. Provider output is schema-bounded to create-intent or semantic-edit proposals; arbitrary Blueprint state or patch injection is rejected.
3. Explicit user hints and exclusions outrank provider inference and cannot be silently changed.
4. Edit requests are bound to an exact Blueprint revision SHA-256 and stale/substituted context fails closed.
5. Provider-declared capabilities are checked before proposal lowering; undeclared modes, styles, and semantic axes are rejected.
6. Create path proves user language → typed proposal → validated Music Intent v0 → deterministic M1 Blueprint.
7. Edit path proves user language + exact revision context → typed proposal → validated Semantic Control v0 → M1 resolver → HARD-lock-preserving candidate revision.
8. Provider/director resolution has no `.musica` Project Bundle side effect before explicit project commit.
9. Accepted AI-origin revisions retain provider/request/proposal/accepted-contract digest provenance.
10. Malformed, over-authoritative, stale-context, and unsupported-axis negative cases are blocked before canonical mutation.
11. Canonical M3-R1 evidence includes create/edit contracts, traces, Blueprint/IR/MIDI/WAV artifacts, M2 project state, branch state, integrity verification, and negative authority proofs.
12. Python 3.11 and Python 3.12 CI pass with all M0/M1/M2 regressions preserved.

## 3. Canonical proof / 공식 증명

### Create / 생성

```text
User language
  ↓
Director Request v0
  ↓
Fixture Provider proposal
  ↓
Director Proposal v0 validation
  ↓
Music Intent v0
  ↓
M1 Blueprint Composer
  ↓
Blueprint R1
  ↓
M2 Project Bundle commit
  ↓
IR + MIDI/WAV evidence
```

### Edit / 수정

```text
User language + exact R1 SHA/context
  ↓
Director Request v0
  ↓
Fixture Provider proposal
  ↓
Director Proposal v0 validation
  ↓
Semantic Control v0
  ↓
M1 Semantic Resolver
  ↓
HARD lock / constraint validation
  ↓
Candidate R2
  ↓
explicit M2 branch commit
  ↓
diff + trace + IR + MIDI/WAV evidence
```

Before the explicit M2 commit, both project refs MUST remain unchanged.

명시적 M2 commit 전에는 모든 프로젝트 ref가 변경되지 않아야 합니다.

## 4. Negative authority proof / 부정 권한 증명

The canonical suite MUST deliberately attempt and reject at least these cases:

공식 suite는 최소 다음 경우를 의도적으로 시도하고 거부해야 합니다.

- direct canonical-state/Blueprint injection / 직접 공식 상태·Blueprint 주입,
- explicit user-hint override / 명시적 사용자 hint 변경,
- stale revision-context substitution / 오래되거나 대체된 revision context,
- unsupported semantic-axis output / 미지원 semantic axis 출력.

## 5. Reproducibility interpretation / 재현성 해석

The deterministic fixture/reference provider MUST be reproducible for CI. This does **not** imply that future live model providers are deterministic.

결정론 fixture/reference provider는 CI에서 재현 가능해야 합니다. 이는 향후 실제 모델 provider가 결정론적임을 의미하지 않습니다.

For a live provider, MUSICA reproducibility means preserving exact request contracts, provider/model identifiers, relevant configuration, proposal/response digests, accepted lowered contracts, and downstream deterministic state.

실제 provider에서 MUSICA의 재현성은 정확한 request 계약, provider/model 식별자, 관련 설정, proposal/response digest, 승인된 lowering 계약, 이후 결정론 상태를 보존하는 것을 의미합니다.

## 6. Non-goals / 비목표

M3-R1 does not claim:

M3-R1은 다음을 주장하지 않습니다.

- live OpenAI or other network-provider execution / 실제 OpenAI 또는 기타 네트워크 provider 실행,
- arbitrary natural-language understanding / 임의 자연어 이해,
- autonomous long-running agent behavior / 장기 자율 에이전트,
- AI authority over accepted Blueprint or Project Bundle state / 승인 Blueprint·Project Bundle에 대한 AI 권위,
- deterministic external LLM output / 외부 LLM 출력의 결정론성,
- production/mastering audio quality / 상용 제작·마스터링 음질,
- polished conversational UI / 완성형 대화 UI.

## 7. Closure rule / 종결 규칙

Implementation may merge only after exact-head CI satisfies this contract. M3-R1 becomes `VALIDATED` only after durable evidence is committed and that exact evidence-bearing head also passes CI.

구현은 exact-head CI가 본 계약을 충족한 뒤에만 병합할 수 있습니다. M3-R1은 durable evidence가 커밋되고 그 근거 포함 exact head까지 CI를 통과한 후에만 `VALIDATED`가 됩니다.
