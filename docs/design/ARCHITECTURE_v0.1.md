# MUSICA Architecture v0.1 / MUSICA 아키텍처 v0.1

**Status / 상태:** ACCEPTED-FOUNDATION / 기반 승인

## 1. Architectural goal / 아키텍처 목표

MUSICA SHALL convert user intent into inspectable, constrained, reproducible musical state and renderable artifacts without making any single renderer or user interface the source of truth.

MUSICA는 특정 렌더러나 UI를 공식 기준정보로 삼지 않고, 사용자 의도를 검사 가능하고 제약되며 재현 가능한 음악 상태와 렌더 가능한 산출물로 변환해야 합니다.

## 2. System layers / 시스템 계층

### L0 — Experience Layer / 경험 계층
Surfaces: Direct, Shape, Inspect, Code. Accepts natural language, semantic controls, timeline edits, note edits, and explicit technical parameters.

표면: Direct, Shape, Inspect, Code. 자연어, 의미 제어, 타임라인 수정, 음표 수정, 명시적 기술 파라미터를 받습니다.

### L1 — Intent & Direction Layer / 의도·디렉션 계층
Components: Intent Recorder, AI Music Director, Reference Interpreter, Clarification/Alternative Generator.

역할: 사용자의 요구를 기록하고 창작 목표, 범위, 보존 조건, 불확실성을 구조화합니다.

### L2 — Canonical Creative State / 공식 창작 상태
Primary object: `Music Blueprint`.

Contains project identity, timeline/sections, musical roles, harmonic/rhythmic/melodic intent, semantic state, locks, constraints, provenance, revision metadata, and render intent.

프로젝트 정체성, 구간/시간축, 음악 역할, 화성·리듬·멜로디 의도, 의미 상태, lock, constraint, provenance, 리비전 정보, 렌더 의도를 포함합니다.

### L3 — Resolution & Validation Layer / 해석·검증 계층
Components: Semantic Resolver, Constraint Engine, Diff Engine, Blueprint Validator, Conflict Resolver.

Natural-language edits are resolved into candidate deltas, checked against locks/constraints, validated, diffed, and only then accepted as a new Blueprint revision.

자연어 수정은 후보 delta로 해석되고 lock/constraint 검사를 거쳐 검증·diff 후 새로운 Blueprint 리비전으로 승인됩니다.

### L4 — Compilation Layer / 컴파일 계층
Components: Music Compiler, target profiles, lowering passes.

Transforms validated Blueprint state into a lower-level `Music IR`. Compilation SHOULD be deterministic where the selected target permits it. Any probabilistic lowering MUST record seed/configuration/provenance when available.

검증된 Blueprint를 저수준 `Music IR`로 변환합니다. 대상이 허용하는 경우 결정론적이어야 하며, 확률적 lowering은 가능한 경우 seed/configuration/provenance를 기록해야 합니다.

### L5 — Adapter & Rendering Layer / 어댑터·렌더 계층
Potential adapters: MIDI, MusicXML/score, synth, sampler, DSP, DAW bridge, generative-audio backend.

The adapter contract receives a versioned Music IR or compiled target package and emits artifacts plus evidence.

어댑터는 버전된 Music IR 또는 컴파일된 대상 패키지를 받아 산출물과 실행 근거를 출력합니다.

### L6 — Analysis & Evaluation Layer / 분석·평가 계층
Components: technical audio analyzer, structural verifier, AI evaluator, optional human acceptance.

Evaluation SHALL distinguish measurable evidence from subjective interpretation.

평가는 측정 가능한 근거와 주관적 해석을 구분해야 합니다.

### L7 — Persistence & Evidence Layer / 영속화·근거 계층
Stores project revisions, diffs, intents, constraints, render manifests, hashes, test evidence, and accepted decisions.

프로젝트 리비전, diff, 의도, 제약, 렌더 manifest, hash, 테스트 근거, 승인 결정을 저장합니다.

## 3. Core runtime flow / 핵심 실행 흐름

```text
INPUT
  ↓
Intent Record
  ↓
AI Music Director
  ↓
Blueprint candidate
  ↓
Semantic Resolver
  ↓
Constraint/Lock Check
  ├─ conflict → fail closed / branch alternatives / request resolution
  ↓ pass
Blueprint Validator
  ↓
Accepted Blueprint Revision
  ↓
Compiler
  ↓
Music IR
  ↓
Renderer Adapter
  ↓
Artifact + Render Manifest
  ↓
Analysis / Evaluation
  ↓
Evidence + Diff + Provenance
```

## 4. Canonical authority / 공식 권위 관계

Within a MUSICA project:

1. Accepted user intent and explicit constraints outrank inferred preferences.
2. Hard locks outrank semantic optimization.
3. Accepted Blueprint revision is the canonical creative state.
4. Music IR is canonical only for a specific compilation target/revision.
5. Rendered audio is an output artifact, not the canonical project state.
6. AI evaluation does not mutate accepted state without a new revision.

MUSICA 프로젝트 내부에서는:

1. 승인된 사용자 의도·명시적 제약이 추론된 선호보다 우선합니다.
2. Hard lock이 의미 최적화보다 우선합니다.
3. 승인된 Blueprint 리비전이 공식 창작 상태입니다.
4. Music IR은 특정 컴파일 대상/리비전에 한해 공식 실행 상태입니다.
5. 렌더 오디오는 출력 산출물이지 프로젝트 공식 상태가 아닙니다.
6. AI 평가는 새 리비전 없이 승인 상태를 변경하지 않습니다.

## 5. Progressive disclosure contract / 단계적 복잡성 노출 계약

All four interaction depths MUST resolve to the same underlying project state:

- **Direct / 디렉팅:** intent, references, high-level semantic edits.
- **Shape / 구조:** sections, roles, emotion curves, harmony/rhythm shape, locks.
- **Inspect / 전문:** notes, MIDI-like events, automation, synthesis/mix parameters where supported.
- **Code / 코드:** Blueprint/IR/API/CLI and programmable transforms.

No depth may maintain an incompatible shadow state.

어떤 깊이도 별도의 비호환 shadow state를 유지해서는 안 됩니다.

## 6. Module boundaries / 모듈 경계

Proposed core packages / 제안 코어 패키지:

```text
musica/
  intent/
  blueprint/
  semantics/
  constraints/
  diff/
  compiler/
  ir/
  adapters/
  analysis/
  evaluation/
  evidence/
```

UI, cloud collaboration, model-provider integration, and DAW-specific bridges SHOULD depend on core contracts rather than define them.

UI, 클라우드 협업, 모델 제공자 통합, DAW 전용 브리지는 코어 계약을 정의하기보다 이에 의존해야 합니다.

## 7. Renderer adapter minimum contract / 렌더러 어댑터 최소 계약

Each adapter SHOULD declare:

- adapter id and version,
- supported Music IR target profile,
- deterministic/probabilistic behavior,
- supported capabilities,
- unsupported/approximated fields,
- execution configuration,
- artifact outputs,
- manifest/hash/provenance,
- warnings and failures.

각 어댑터는 ID/버전, 지원 IR 프로파일, 결정론 여부, 지원 기능, 근사·미지원 필드, 실행 설정, 산출물, manifest/hash/provenance, 경고·실패를 선언해야 합니다.

## 8. Fail-closed cases / 실패 폐쇄 조건

The core SHALL reject or explicitly branch resolution when:

- a hard lock would be violated,
- a required Blueprint field is invalid,
- a requested renderer cannot satisfy a required non-approximable constraint,
- a semantic edit has no sufficiently supported mapping and no user-approved fallback,
- provenance required for a reproducibility claim is missing.

다음 경우 코어는 요청을 거부하거나 명시적 대안 분기로 전환해야 합니다: hard lock 위반, 필수 Blueprint 무효, 렌더러의 필수 제약 미지원, 의미 매핑 근거 부족, 재현성 주장에 필요한 provenance 누락.

## 9. v0.1 architectural non-goals / v0.1 아키텍처 비목표

- full DAW replacement,
- proprietary audio model training,
- real-time collaborative editing,
- universal plugin hosting,
- mastering-grade universal DSP,
- perfect semantic-to-acoustic prediction.

위 기능들은 v0.1 기반 아키텍처의 승인 조건이 아닙니다.
