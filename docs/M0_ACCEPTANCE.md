# M0 Acceptance / M0 수용 기준

## Purpose / 목적

M0 proves MUSICA's smallest end-to-end controllability claim without pretending to be a full DAW or a proprietary foundation audio model.

M0는 MUSICA가 완전한 DAW 또는 독자 파운데이션 오디오 모델이라고 가장하지 않고, 최소한의 end-to-end 제어 가능성을 증명합니다.

## M0-R1 — Executable Blueprint Contract / 실행 가능한 Blueprint 계약

**Acceptance criteria / 수용 기준**

- All JSON Schemas validate under Draft 2020-12. / 모든 JSON Schema가 Draft 2020-12 기준으로 유효해야 함.
- The canonical root Blueprint validates. / 공식 루트 Blueprint가 검증을 통과해야 함.
- Explicit invalid examples fail closed. / 명시적 비정상 예제는 실패 폐쇄해야 함.
- Semantic controls are restricted to the accepted v0 vocabulary and normalized ranges. / 의미 제어는 승인된 v0 어휘와 정규화 범위로 제한됨.
- Blueprint and Music IR remain separate machine contracts. / Blueprint와 Music IR은 별도 기계 계약으로 유지됨.
- HARD locks survive inheritance and cannot be silently removed or weakened. / HARD lock은 상속되며 몰래 제거·약화할 수 없음.
- A hard constraint can block an otherwise schema-valid candidate. / hard constraint가 형식상 유효한 후보를 차단할 수 있어야 함.
- Ordered, non-overlapping v0 sections and references are cross-field validated. / v0 구간 순서·비중첩과 참조 무결성을 교차 필드 검증함.
- Tests run on Python 3.11 and 3.12 in repository CI. / 레포 CI에서 Python 3.11 및 3.12 테스트를 실행함.

## M0-R2 — Minimal Deterministic Music Loop / 최소 결정론 음악 루프

M0-R2 is accepted only when repository evidence proves the following:

M0-R2는 레포 근거가 다음을 증명할 때만 승인됩니다.

1. A validated Blueprint compiles to validated Music IR. / 검증된 Blueprint가 검증된 Music IR로 컴파일됨.
2. Music IR renders through at least one free/local deterministic path to MIDI and audible WAV. / Music IR이 최소 하나의 무료·로컬 결정론 경로로 MIDI와 청취 가능한 WAV를 생성함.
3. One semantic edit produces an explicit candidate revision. / 하나의 의미 수정이 명시적 후보 리비전을 생성함.
4. Melody/drum/tempo HARD locks block prohibited mutations. / 멜로디·드럼·템포 HARD lock이 금지 변경을 차단함.
5. The resolver can choose at least one alternative allowed mechanism. / resolver가 허용된 대체 메커니즘 하나 이상을 선택할 수 있음.
6. A structured diff explains the accepted revision. / 구조화 diff가 승인 리비전을 설명함.
7. Re-rendering identical accepted inputs produces reproducible contract-level artifacts. / 동일 승인 입력 재렌더가 계약 수준에서 재현 가능한 산출물을 생성함.

## Evidence rule / 근거 규칙

A passing design review is not executable evidence. A code file without a passing test is not `TESTED`. A workflow definition without a successful run is not CI evidence.

설계 리뷰 통과는 실행 근거가 아닙니다. 코드 파일만 존재하고 테스트가 통과하지 않았다면 `TESTED`가 아닙니다. workflow 정의만 있고 성공 실행이 없다면 CI 근거가 아닙니다.
