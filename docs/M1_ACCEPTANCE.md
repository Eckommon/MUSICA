# M1 Creative Core Acceptance / M1 Creative Core 수용 기준

**Status / 상태:** NORMATIVE GATE / 규범 게이트

## Objective / 목표

M1 moves MUSICA from a hand-authored Blueprint proof to reproducible composition from a compact validated Music Intent contract.

M1은 수작업 Blueprint 증명에서 벗어나, 검증된 간결한 Music Intent 계약으로부터 재현 가능한 작곡을 수행하는 단계입니다.

## Required evidence / 필수 근거

M1 is `VALIDATED` only when repository evidence proves all of the following.

M1은 레포 근거가 아래 항목을 모두 증명한 경우에만 `VALIDATED`입니다.

1. `Music Intent v0` is machine-valid and rejects out-of-contract values. / `Music Intent v0`가 기계 검증되며 계약 외 값을 거부합니다.
2. Identical Intent + profile + seed produces an identical Creative Plan and Blueprint. / 동일 Intent+profile+seed가 동일 Creative Plan과 Blueprint를 생성합니다.
3. Changing the seed changes generated musical material without changing the contract shape. / seed 변경이 계약 형태는 유지한 채 음악 재료를 변경합니다.
4. `dark_electronic`, `warm_ambient`, and `kinetic_minimal` produce materially different tempo/timbre/material/render results. / 세 프로필이 템포·음색·재료·렌더 결과에서 실질적으로 구분됩니다.
5. Six semantic axes are runtime-supported: `energy`, `tension`, `density`, `motion`, `brightness`, `warmth`. / 6개 semantic 축이 런타임에서 지원됩니다.
6. Every supported semantic edit emits an explicit diff and selected mechanism record. / 모든 지원 semantic edit가 명시적 diff와 선택 메커니즘 기록을 생성합니다.
7. HARD tempo, melody-identity token, and rhythm-identity token locks remain fail-closed. / HARD tempo·melody identity token·rhythm identity token 잠금이 실패 폐쇄로 유지됩니다.
8. Every supported semantic axis changes executable MIDI and audible local WAV evidence under the canonical probe. / 모든 지원 축이 공식 probe에서 MIDI와 로컬 WAV 실행 결과를 변경합니다.
9. Compiler output uses profile-selected instrument programs instead of one hard-coded M0 profile. / 컴파일러가 M0 단일 고정 프로그램 대신 프로필별 악기 프로그램을 사용합니다.
10. The canonical three-case evidence bundle is reproducible and SHA-256 bound. / 공식 3-case 근거 번들이 재현 가능하며 SHA-256으로 결속됩니다.
11. Python 3.11 and 3.12 CI pass. / Python 3.11 및 3.12 CI가 통과합니다.
12. M0 regression tests continue to pass. / M0 회귀 테스트가 계속 통과합니다.

## Claim boundary / 주장 경계

M1 does **not** prove:

M1이 증명하지 않는 항목:

- arbitrary free-form natural-language understanding / 임의 자유형 자연어 이해,
- universal genre modeling / 보편 장르 모델링,
- objective or universal emotion mapping / 객관적·보편적 감정 매핑,
- production/mastering audio quality / 상용 제작·마스터링 음질,
- perceptual melody-identity equivalence / 지각적 멜로디 동일성,
- full DAW functionality / 완전한 DAW 기능.

Those claims require later milestones and separate evidence.

해당 주장은 이후 마일스톤과 별도 근거가 필요합니다.
