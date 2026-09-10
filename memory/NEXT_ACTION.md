# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M1 — CREATIVE CORE v0: INTENT → MUSIC BLUEPRINT / M1 — 창작 코어 v0: 의도 → 음악 설계도**

M0 is validated. The next problem is no longer whether MUSICA can preserve constraints and deterministically render a known Blueprint. The next problem is whether a user can provide a compact musical intention and receive a useful, editable Blueprint without manually authoring notes and events.

M0는 검증되었습니다. 다음 문제는 알려진 Blueprint를 제약 보존하며 결정론적으로 렌더링할 수 있는지가 아닙니다. 이제 사용자가 간결한 음악 의도를 제공했을 때 음표·이벤트를 직접 작성하지 않고 유용하고 편집 가능한 Blueprint를 받을 수 있는지를 증명해야 합니다.

## M1 product objective / M1 제품 목표

```text
User musical intent / 사용자 음악 의도
        ↓
Intent Contract / 의도 계약
        ↓
Creative Planner / 창작 플래너
        ↓
Blueprint Composer / Blueprint 작곡기
        ↓
Validated Music Blueprint
        ↓
Semantic edit + locks
        ↓
M0 compiler/render path
        ↓
Audible result + explainable revision
```

## M1 required scope / M1 필수 범위

1. **Music Intent v0 contract / 음악 의도 v0 계약** — duration, use case, mood/semantic targets, style family, tonal/tempo preferences, exclusions, seed, confidence/provenance.
2. **Deterministic Creative Planner / 결정론 창작 플래너** — transforms a bounded Intent into form, tempo/key/mode, roles, harmony strategy, motif/rhythm plan, semantic curves, and default locks/constraints.
3. **Blueprint Composer / Blueprint 작곡기** — generates explicit motif/rhythm/harmony material from the plan under a reproducible seed.
4. **Multi-axis semantic runtime / 다축 의미 런타임** — implement a useful M1 subset beyond `tension`, prioritized around `energy`, `tension`, `density`, `motion`, `brightness`, and `warmth` with explicit mechanism registry and claim boundaries.
5. **Style profiles / 스타일 프로필** — at least three materially different bounded profiles sufficient to prove the architecture is not hard-coded to one dark-electronic demo.
6. **Intent→Blueprint evidence / 의도→Blueprint 근거** — at least three different canonical intents compile and render successfully through the existing M0 path.
7. **Lock-aware revision / lock 인지 리비전** — at least two different semantic edits preserve protected material and produce explainable diffs.
8. **Determinism / 결정론성** — same intent + profile + seed yields identical canonical Blueprint and compiled artifacts under the tested path.
9. **Bilingual docs and CI evidence / 한영문 문서 및 CI 근거**.

## Explicit boundary / 명시적 경계

M1 does not yet need to claim arbitrary free-form natural-language understanding. The Intent Contract is the canonical boundary. A deterministic local parser may support a limited convenience subset, while a later AI Music Director provider can populate the same contract.

M1은 아직 임의 자유형 자연어의 범용 이해를 주장할 필요가 없습니다. Intent Contract가 공식 경계입니다. 결정론 로컬 parser는 제한된 편의 입력을 지원할 수 있으며, 이후 AI Music Director provider도 동일한 계약을 생성하도록 연결합니다.

## Product sequence after M1 / M1 이후 제품 순서

The preferred sequence remains:

권장 순서는 다음과 같습니다.

```text
M1 Creative Core
→ M2 Project & Version Engine
→ M3 AI Music Director Provider Layer
→ M4 MUSICA Studio usable application MVP
→ M5 Renderer/DAW interoperability & quality expansion
→ M6 Product hardening / packaging / release candidate
```

Each milestone must preserve the repository evidence discipline and may be revised only through repository-backed decisions.

각 마일스톤은 레포 근거 규율을 유지해야 하며, 변경 시 레포 기반 결정으로만 수정합니다.
