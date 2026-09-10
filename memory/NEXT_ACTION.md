# Next Action / 다음 작업

## Immediate objective / 즉시 목표

Convert the accepted product thesis into an executable foundation **without prematurely building a full DAW or training a proprietary audio model**.

승인된 제품 명제를 실행 가능한 기반 구조로 전환하되, 초기 단계에서 완전한 DAW나 독자 오디오 모델을 성급히 구축하지 않습니다.

## Proposed next milestone / 제안 다음 마일스톤

### M0 — Controllable Music Blueprint / 제어 가능한 음악 설계도

Acceptance target / 수용 목표:

1. A user can describe a short instrumental piece in natural language.
2. The system converts that request into a validated structured Music Blueprint.
3. The Blueprint contains sections, tempo, meter, tonal information, instrument roles, notes/events or generative constraints, semantic attributes, and locks.
4. The same accepted Blueprint can be rendered repeatedly through at least one deterministic path to MIDI and audible audio.
5. A user can issue one semantic edit while locking at least one other musical element.
6. The system can show a structured diff between the pre-edit and post-edit Blueprint.
7. Repository tests and artifacts prove the above claims.

1. 사용자가 짧은 기악곡을 자연어로 설명할 수 있어야 합니다.
2. 시스템은 요청을 검증된 구조화 Music Blueprint로 변환해야 합니다.
3. Blueprint는 구간, 템포, 박자, 조성 정보, 악기 역할, 음표/이벤트 또는 생성 제약, 의미 속성, 잠금을 포함해야 합니다.
4. 승인된 동일 Blueprint를 최소 하나의 결정론적 경로를 통해 반복적으로 MIDI와 청취 가능한 오디오로 렌더링할 수 있어야 합니다.
5. 사용자가 최소 하나의 음악 요소를 잠근 상태에서 하나의 의미 기반 수정 지시를 내릴 수 있어야 합니다.
6. 수정 전후 Blueprint의 구조화 diff를 보여줄 수 있어야 합니다.
7. 위 주장은 레포 테스트와 산출물로 증명되어야 합니다.

## Before implementation / 구현 전

Create and accept:

- architecture specification / 아키텍처 명세
- Music Blueprint / Music IR v0 schema / Music IR v0 스키마
- semantic control vocabulary / 의미 제어 어휘
- lock/constraint model / 잠금·제약 모델
- renderer adapter contract / 렌더러 어댑터 계약
- M0 acceptance tests / M0 수용 테스트

Normal implementation should proceed through issue → branch → PR → tests → merge → state update.

본격 구현은 Issue → Branch → PR → Tests → Merge → State Update 순으로 진행합니다.
