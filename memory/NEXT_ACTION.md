# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M0-R1 — Executable Blueprint Contract / 실행 가능한 Blueprint 계약**

The foundation design package is accepted. The next work is NOT another product brainstorm and NOT audio-quality optimization. The next work is to convert the conceptual Blueprint/semantic/lock models into executable contracts and tests.

기반 설계 패키지는 승인되었습니다. 다음 작업은 추가 제품 브레인스토밍도, 음질 최적화도 아닙니다. 다음 작업은 개념적 Blueprint/semantic/lock 모델을 실행 가능한 계약과 테스트로 전환하는 것입니다.

## Immediate objective / 즉시 목표

Create the minimum executable specification needed to prove MUSICA's core loop without prematurely building a full DAW or proprietary audio model.

완전한 DAW나 독자 오디오 모델을 성급히 구축하지 않고 MUSICA 핵심 루프를 증명할 최소 실행 명세를 만듭니다.

## M0 target / M0 목표

```text
Natural-language intent
        ↓
Validated Music Blueprint
        ↓
Semantic edit candidate
        ↓
Hard-lock / constraint check
        ↓
Accepted Blueprint revision + structured diff
        ↓
Deterministic compile target
        ↓
MIDI + audible audio
        ↓
Evidence manifest
```

## M0-R1 deliverables / M0-R1 산출물

1. `schemas/music-blueprint-v0.schema.json`
2. `schemas/music-ir-v0.schema.json` — minimal executable target, not a universal final IR
3. semantic-control machine vocabulary / 의미 제어 기계 어휘
4. lock/constraint machine schema / 잠금·제약 기계 스키마
5. canonical example Blueprint / 공식 예제 Blueprint
6. valid + invalid fixtures / 유효·무효 fixture
7. schema validation tests / 스키마 검증 테스트
8. M0 acceptance-test specification / M0 수용 테스트 명세

## M0-R2 target / M0-R2 목표

After M0-R1 passes:

M0-R1 통과 후:

- implement minimal semantic resolver,
- implement hard-lock fail-closed constraint check,
- implement structured Blueprint diff,
- compile one accepted Blueprint deterministically to MIDI,
- render one audible local audio artifact through a free/local path,
- record compiler/adapter/config/hash evidence.

최소 의미 해석기, hard-lock 실패 폐쇄 검사, Blueprint diff, 결정론적 MIDI 컴파일, 무료/로컬 경로의 청취 가능한 오디오 렌더, 실행 근거 기록을 구현합니다.

## M0 acceptance criteria / M0 수용 기준

M0 is VALIDATED only when repository evidence proves all of the following:

M0는 레포 근거로 다음을 모두 증명한 경우에만 VALIDATED입니다.

1. A user intent is represented as a valid structured Blueprint.
2. At least one section-scoped semantic edit is resolved into an explicit candidate delta.
3. At least one HARD value lock blocks an invalid mutation.
4. At least one simplified melody-identity HARD lock blocks an invalid mutation.
5. The system proposes or executes a valid alternative that preserves the locks.
6. Pre/post accepted Blueprints produce a structured diff.
7. The same accepted Blueprint compiles repeatedly to equivalent deterministic MIDI output under the pinned environment.
8. At least one free/local renderer produces audible audio from the compiled target.
9. Manifest/provenance records the Blueprint revision, compiler version/configuration, adapter/configuration, and artifact hash where applicable.
10. Automated tests support all implementation claims.

## Development discipline / 개발 규율

From M0-R1 onward, substantive implementation SHOULD proceed:

본격 구현은 M0-R1부터 다음 순서를 원칙으로 합니다.

```text
Issue → Branch → Implementation → Tests → PR → Review → Merge → State Update
```

No later session should skip directly to advanced UI, generative-audio integration, VST hosting, or proprietary model work unless M0 evidence justifies changing this sequence.

후속 세션은 M0 근거 없이 고급 UI, 생성형 오디오 통합, VST 호스팅, 독자 모델 작업으로 건너뛰지 않습니다.
