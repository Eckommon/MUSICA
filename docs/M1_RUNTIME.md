# M1 Creative Core Runtime / M1 Creative Core 런타임

## What M1 implements / M1 구현 범위

M1 accepts a validated `Music Intent v0`, creates a deterministic Creative Plan and Music Blueprint, compiles the Blueprint to Music IR, and renders deterministic MIDI plus a local audible WAV preview.

M1은 검증된 `Music Intent v0`를 입력받아 결정론적 Creative Plan과 Music Blueprint를 만들고, Blueprint를 Music IR로 컴파일한 뒤 결정론적 MIDI와 로컬 청취용 WAV 프리뷰를 렌더링합니다.

```text
Music Intent v0
    ↓
Creative Planner
    ↓
Blueprint Composer
    ↓
Validated Music Blueprint
    ↓
6-axis Semantic Runtime + Locks
    ↓
Music IR Compiler
    ↓
MIDI / Local WAV Preview
    ↓
SHA-256 Evidence
```

## Supported creative profiles / 지원 창작 프로필

- `dark_electronic` / 다크 일렉트로닉
- `warm_ambient` / 웜 앰비언트
- `kinetic_minimal` / 키네틱 미니멀

Profiles are explicit bounded implementation data. They are not universal genre definitions.

프로필은 제한된 명시적 구현 데이터이며 보편적인 장르 정의가 아닙니다.

## Supported semantic runtime / 지원 semantic 런타임

M1 runtime implements exactly six axes:

M1 런타임은 정확히 다음 6개 축을 구현합니다.

- `energy`: note velocity + CC11 expression / 음표 강도 + CC11 expression
- `tension`: deterministic bass pressure + bounded motion coupling / 결정론적 베이스 압력 + 제한된 motion 결합
- `density`: supporting bass-event density / 보조 베이스 이벤트 밀도
- `motion`: forward support-event density / 전진형 보조 이벤트 밀도
- `brightness`: CC74 + local preview harmonic balance / CC74 + 로컬 프리뷰 고조파 균형
- `warmth`: CC71 + local preview fundamental/sub-harmonic balance / CC71 + 로컬 프리뷰 기음·저역 고조파 균형

Other schema vocabulary remains future-facing and fails closed at runtime until implemented.

스키마에 존재하는 다른 미래 semantic 어휘는 실제 구현 전까지 런타임에서 실패 폐쇄합니다.

## Determinism / 결정론

Creative material selection uses SHA-256-derived selection from `seed + label`, rather than process-global random state. Identical validated Intent + profile + seed is therefore expected to produce identical Blueprint and executable output under the pinned implementation.

창작 재료 선택은 프로세스 전역 난수 상태 대신 `seed + label`에서 파생한 SHA-256 선택을 사용합니다. 따라서 고정 구현에서 동일한 검증 Intent + profile + seed는 동일 Blueprint와 실행 결과를 생성해야 합니다.

## Claim boundary / 주장 경계

The local WAV renderer exists to make contract behavior audible and testable. It is not a production synthesizer, mastering engine, or claim of commercial audio quality.

로컬 WAV renderer는 계약 동작을 청취·검증하기 위한 것으로, 상용 신시사이저·마스터링 엔진 또는 상업적 음질 주장이 아닙니다.
