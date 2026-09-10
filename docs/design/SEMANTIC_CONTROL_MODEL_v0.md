# Semantic Control Model v0 / 의미 제어 모델 v0

**Status / 상태:** ACCEPTED-FOUNDATION / 기반 승인

## 1. Purpose / 목적

The Semantic Control Model translates human musical intent into structured, inspectable control targets without pretending that subjective language has one universally correct acoustic mapping.

Semantic Control Model은 인간의 음악적 의도를 구조화되고 검사 가능한 제어 목표로 변환하되, 주관적 언어가 하나의 보편적으로 옳은 음향 매핑을 가진다고 가정하지 않습니다.

Its purpose is not to reduce music to a few sliders. Its purpose is to create a traceable bridge between language and musical change.

목적은 음악을 몇 개의 슬라이더로 환원하는 것이 아니라, 자연어와 음악적 변화 사이에 추적 가능한 다리를 만드는 것입니다.

## 2. Control domains / 제어 도메인

v0 defines semantic controls in six domains.

v0는 의미 제어를 여섯 도메인으로 정의합니다.

### A. Energy / 에너지
Examples: calm ↔ intense, restrained ↔ explosive.

예: 차분함 ↔ 강렬함, 절제 ↔ 폭발.

### B. Tension / 긴장
Examples: stable ↔ unresolved, relaxed ↔ urgent.

예: 안정 ↔ 미해결, 여유 ↔ 긴박.

### C. Density / 밀도
Examples: sparse ↔ layered, exposed ↔ crowded.

예: 희소 ↔ 중층, 비어 있음 ↔ 촘촘함.

### D. Motion / 움직임
Examples: static ↔ driving, floating ↔ propulsive.

예: 정적 ↔ 추진적, 부유 ↔ 전진.

### E. Timbre / 음색
Examples: warm, bright, dark, metallic, airy, organic, synthetic, brittle, smooth.

예: 따뜻함, 밝음, 어두움, 금속성, 공기감, 유기적, 합성적, 거침, 부드러움.

### F. Space & Focus / 공간·초점
Examples: intimate ↔ expansive, dry ↔ distant, narrow ↔ wide, foreground ↔ background.

예: 친밀 ↔ 광활, 건조 ↔ 원거리, 좁음 ↔ 넓음, 전경 ↔ 배경.

These domains are not assumed to be orthogonal. Correlations and conflicts MUST be representable.

이 도메인들은 서로 완전히 독립적이라고 가정하지 않습니다. 상관관계와 충돌을 표현할 수 있어야 합니다.

## 3. Semantic control value / 의미 제어 값

A semantic value SHOULD include more than a scalar when appropriate.

의미 값은 필요한 경우 단순 숫자 하나보다 더 많은 정보를 포함해야 합니다.

Example / 예:

```yaml
semantic_control:
  name: tension
  target: 0.68
  scope: section:S03
  confidence: 0.82
  source: user_language
  phrase: "make the second half more urgent"
  interpretation_notes:
    - "increase harmonic instability moderately"
    - "increase rhythmic forward motion"
  protected_dimensions:
    - melody.identity
```

## 4. Resolution pipeline / 해석 파이프라인

Semantic edits SHALL follow this conceptual pipeline:

의미 기반 수정은 다음 개념 파이프라인을 따라야 합니다.

```text
User phrase / 사용자 표현
      ↓
Intent parse / 의도 파싱
      ↓
Scope resolution / 적용 범위 결정
      ↓
Semantic target candidates / 의미 목표 후보
      ↓
Musical mechanism candidates / 음악 메커니즘 후보
      ↓
Lock & constraint check / 잠금·제약 검사
      ↓
Ranked Blueprint deltas / 우선순위 Blueprint 변경안
      ↓
Accept / branch / reject
```

The AI Music Director MAY propose multiple musically valid interpretations when language is ambiguous.

자연어가 모호하면 AI Music Director는 복수의 음악적으로 타당한 해석을 제안할 수 있습니다.

## 5. Semantic-to-musical mapping / 의미→음악 매핑

Mappings MUST be many-to-many, not hardcoded one-to-one rules.

매핑은 일대일 고정 규칙이 아니라 다대다 구조여야 합니다.

Example: increasing `tension` MAY involve any supported combination of:

`tension` 증가는 상황에 따라 다음 중 일부 조합으로 구현될 수 있습니다.

- harmonic instability / 화성 불안정성 증가,
- unresolved cadence / 미해결 종지,
- dissonance or suspension / 불협·서스펜션,
- rhythmic anticipation / 리듬 선행,
- register expansion or compression / 음역 확장·압축,
- textural accumulation / 텍스처 축적,
- dynamics / 다이내믹 변화,
- timbral roughness / 음색 거칠기,
- spatial narrowing or widening depending on context / 맥락에 따른 공간 폭 변화.

The resolver MUST record which mechanisms were selected for an accepted change.

승인된 변경에 어떤 메커니즘이 선택되었는지 기록해야 합니다.

## 6. Context sensitivity / 맥락 민감성

Semantic resolution SHOULD consider:

- genre/context / 장르·맥락,
- current Blueprint state / 현재 Blueprint 상태,
- section purpose / 구간 목적,
- instrument roles / 악기 역할,
- references and exclusions / 참고·배제 조건,
- user locks / 사용자 잠금,
- previous accepted revisions / 이전 승인 리비전,
- renderer capabilities / 렌더러 역량.

For example, “more powerful” in a solo piano cue and in an industrial electronic track SHOULD NOT map to the same parameter recipe by default.

예를 들어 솔로 피아노와 인더스트리얼 전자음악에서 “더 강하게”는 기본적으로 동일 파라미터 조합으로 해석되어서는 안 됩니다.

## 7. Scope / 적용 범위

A semantic command MUST resolve its scope explicitly.

의미 명령은 적용 범위를 명시적으로 해석해야 합니다.

Supported conceptual scopes include:

- global project / 전체 프로젝트,
- section / 구간,
- time range / 시간 범위,
- part or role / 파트·역할,
- material dimension / 화성·리듬·멜로디 등 재료 차원,
- mix/sound dimension / 믹스·사운드 차원,
- revision comparison target / 리비전 비교 대상.

## 8. Relative vs absolute edits / 상대·절대 수정

MUSICA SHOULD distinguish:

- **relative:** “more urgent”, “slightly warmer”, “less busy”
- **absolute/target:** “energy 0.70”, “keep under 110 BPM”, “stereo width 65% where supported”

MUSICA는 “더 긴박하게” 같은 상대 수정과 “energy 0.70” 같은 목표값 지정을 구분해야 합니다.

Relative edits require comparison to the current Blueprint state.

상대 수정은 현재 Blueprint 상태와의 비교를 필요로 합니다.

## 9. Uncertainty protocol / 불확실성 규약

If a semantic request is ambiguous, MUSICA SHOULD choose among these strategies:

의미 요청이 모호하면 MUSICA는 다음 중 하나를 선택해야 합니다.

1. resolve automatically when ambiguity is low and change is reversible / 모호성이 낮고 가역적이면 자동 해석,
2. produce ranked variants / 우선순위 대안 생성,
3. preserve uncertainty in the Blueprint / Blueprint에 불확실성 보존,
4. ask for clarification only when necessary to avoid violating important constraints or wasting expensive renders / 중요한 제약 위반 또는 고비용 렌더 낭비 방지에 필요할 때만 확인 요청.

The system MUST NOT fabricate precision. A confidence score is evidence about interpretation confidence, not musical quality.

시스템은 정밀도를 가장해서는 안 됩니다. confidence는 해석 확신도이지 음악 품질 점수가 아닙니다.

## 10. Initial semantic vocabulary / 초기 의미 어휘

The v0 core vocabulary SHOULD remain intentionally small and composable:

v0 코어 어휘는 의도적으로 작고 조합 가능하게 유지합니다.

- energy / 에너지
- tension / 긴장
- density / 밀도
- motion / 움직임
- brightness / 밝기
- warmth / 따뜻함
- roughness / 거칠기
- intimacy / 친밀감
- width / 폭
- depth / 깊이
- clarity / 명료도
- punch / 임팩트
- complexity / 복잡도
- stability / 안정감
- organicity / 유기성
- syntheticity / 합성성

This list is provisional and MAY evolve based on user studies and implementation evidence.

이 목록은 잠정적이며 사용자 테스트와 구현 근거에 따라 변경될 수 있습니다.

## 11. Semantic diff / 의미 diff

Each accepted semantic edit SHOULD generate an explanation record.

각 승인 의미 수정은 설명 기록을 생성해야 합니다.

Example / 예:

```yaml
request: "make the last 8 seconds more urgent, keep the melody"
scope: "time:22.0-30.0"
protected:
  - melody.identity
semantic_delta:
  tension: +0.18
  motion: +0.12
selected_mechanisms:
  - harmonic_rhythm: "faster"
  - bass_pattern_density: "+10%"
  - percussion_anticipation: "increased"
rejected_mechanisms:
  - melody_contour_change: "blocked by hard lock"
```

This explanation is part of MUSICA's inspectability promise.

이 설명은 MUSICA의 검사 가능성 약속의 일부입니다.

## 12. v0 non-goals / v0 비목표

- universal objective definition of emotion,
- perfect prediction of perceived emotion,
- one fixed mapping per adjective,
- replacing detailed musical editing with sliders,
- claiming subjective semantic scores as scientific ground truth.

v0는 감정을 객관적 절대값으로 정의하거나, 형용사마다 하나의 고정 음향 규칙을 정하거나, 의미 슬라이더로 세밀한 편집을 대체하는 것을 목표로 하지 않습니다.
