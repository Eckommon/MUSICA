# Source of Truth / 공식 기준정보

## Authority precedence / 권위 우선순위

When sources conflict, use this order:

출처가 충돌할 경우 다음 순서를 적용합니다.

1. **Accepted repository artifacts and tests / 승인된 레포 산출물 및 테스트**
2. **Merged decisions, specifications, and current-state records / 병합된 결정·명세·현재상태 기록**
3. **Open issue or PR evidence / 열린 Issue·PR의 근거**
4. **Conversation context / 대화 맥락**
5. **Model memory / 모델 기억**
6. **Model inference or assumption / 모델 추론 또는 가정**

Repository evidence prevails over conversational recollection.

레포의 근거는 대화상의 회상보다 우선합니다.

## Claim discipline / 주장 규율

An AI agent MUST NOT claim that a feature, implementation, test, milestone, artifact, integration, or decision exists unless supported by repository evidence.

AI 에이전트는 레포 근거 없이 기능, 구현, 테스트, 마일스톤, 산출물, 통합 또는 결정이 존재한다고 주장해서는 안 됩니다.

Use these evidence states where relevant:

- **PROPOSED / 제안됨** — discussed but not accepted.
- **ACCEPTED / 승인됨** — explicitly recorded as an accepted decision.
- **IMPLEMENTED / 구현됨** — implementation exists in repository.
- **TESTED / 테스트됨** — executable evidence supports the claim.
- **VALIDATED / 검증됨** — acceptance criteria have passed.
- **UNKNOWN / 미확인** — evidence is insufficient.

Never silently upgrade one state to another.

어떤 상태도 근거 없이 상위 상태로 변경해서는 안 됩니다.

## Required resumption protocol / 작업 재개 필수 절차

Before substantive work, an AI agent should inspect at minimum:

실질 작업 전 AI 에이전트는 최소한 다음을 확인해야 합니다.

1. `README.md`
2. `docs/PRODUCT_THESIS.md`
3. `governance/SOURCE_OF_TRUTH.md`
4. `memory/CURRENT_STATE.md`
5. `memory/NEXT_ACTION.md`
6. relevant open issues / 관련 열린 Issue
7. relevant recent commits and tests / 관련 최근 커밋 및 테스트

If repository evidence is missing or contradictory, report `UNKNOWN` or the conflict rather than filling the gap from memory.

레포 근거가 없거나 상충하면 기억으로 빈칸을 채우지 말고 `UNKNOWN` 또는 충돌 상태를 보고합니다.

## Bilingual documentation rule / 한영문 병기 원칙

Canonical project-facing documentation should be bilingual Korean/English unless a file is machine-oriented and bilingual text would damage executability or schema validity.

프로젝트의 공식 문서는 원칙적으로 한영문 병기를 사용합니다. 단, 스키마·코드·기계 판독용 파일처럼 병기가 실행 가능성이나 유효성을 해치는 경우 예외로 합니다.

## Change discipline / 변경 규율

Material product, architecture, specification, governance, or acceptance changes should be traceable through commits and, once normal development begins, preferably through issues and pull requests.

제품·아키텍처·명세·거버넌스·수용기준의 중요한 변경은 커밋으로 추적 가능해야 하며, 본격 개발 이후에는 원칙적으로 Issue와 Pull Request를 통해 진행합니다.
