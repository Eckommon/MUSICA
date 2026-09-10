# M3-R2 Validation Evidence / M3-R2 검증 근거

**Evidence class / 근거 등급:** `ADAPTER_CONTRACT_EVIDENCE`

**Important / 중요:** This record does **not** claim that a live OpenAI network call was executed. Normal validation used a dependency-injected, no-network, no-secret Responses transport. / 본 기록은 실제 OpenAI 네트워크 호출을 수행했다고 주장하지 않습니다. 정상 검증은 network·secret이 없는 주입형 Responses transport를 사용했습니다.

## 1. Accepted implementation head / 수용 구현 HEAD

- Branch / 브랜치: `m3-r2-openai-provider-adapter-v0`
- Exact validated head / 정확한 검증 HEAD: `40a1f202042c722b3714c1c1279e74fd81661f53`
- Workflow / 워크플로: `MUSICA CI`
- Run / 실행: **34538788285**
- Python 3.11 full suite / 전체 테스트: **SUCCESS**
- Python 3.12 full suite / 전체 테스트: **SUCCESS**
- M0 evidence regeneration / M0 근거 재생성: **SUCCESS**
- M1 evidence regeneration / M1 근거 재생성: **SUCCESS**
- M2 evidence regeneration / M2 근거 재생성: **SUCCESS**
- M3-R1 evidence regeneration / M3-R1 근거 재생성: **SUCCESS**
- M3-R2 offline adapter evidence generation/upload / M3-R2 오프라인 adapter 근거 생성·업로드: **SUCCESS**

## 2. Canonical CI artifact / 공식 CI 산출물

- Artifact name / 산출물명: `musica-m3-r2-openai-adapter`
- Artifact ID: **10176475924**
- Archive size / 압축 크기: **833,104 bytes**
- Artifact digest: `sha256:7dc7ab298586466e5338db562aabef29473c0c1173d976a561769ac71661b3e4`

The downloaded artifact was inspected after CI completion rather than inferred from workflow configuration. / CI 완료 후 실제 artifact를 내려받아 검사했으며 workflow 정의만으로 결과를 추론하지 않았습니다.

## 3. Proven canonical proof / 검증된 공식 증명

The artifact manifest reports / artifact manifest 기록:

- `evidence_scope = M3-R2-OpenAI-Provider-Adapter-v0`
- `evidence_class = ADAPTER_CONTRACT_EVIDENCE`
- `live_openai_call_performed = false`
- `network_used = false`
- `secret_used = false`
- create OpenAI creative body lowered through the validated M3-R1 boundary / create OpenAI creative body가 검증된 M3-R1 경계를 통해 lowering됨: **true**
- explicit user hints preserved over model suggestions / 모델 제안보다 명시적 사용자 hint 우선 보존: **true**
- provider/director resolution left the project ref unchanged before explicit commit / 명시적 commit 전 provider/director 해석이 project ref를 변경하지 않음: **true**
- edit committed only after trusted validation / 신뢰 경계 검증 후에만 edit commit: **true**
- project integrity / 프로젝트 무결성: **PASS**
- negative cases blocked / 부정 사례 차단: **true**
- bound output artifacts / 결속 출력 산출물: **2** (`MIDI`, `WAV`)

Project verification additionally records / 프로젝트 검증 추가 기록:

- accepted revisions / 승인 리비전: **2**
- refs / ref: **2**
- content-addressed objects / content-addressed object: **9**
- audit events / audit event: **4**
- project integrity status / 프로젝트 무결성 상태: **PASS**

Canonical rendered files / 공식 렌더 파일:

- `openai-variation.mid`: **836 bytes**, SHA-256 `9792e88480257542f14bf27cd01cb89151d3de4731d958f7b471af9dea87537c`
- `openai-variation.wav`: **882,044 bytes**, SHA-256 `7f0225bc973abb68c57145989986ed44f719a4016726a1704f450841819f3c53`

## 4. Adapter exchange provenance / Adapter 교환 provenance

### Create exchange / 생성 교환

- requested model / 요청 모델: `gpt-5.6-sol`
- fixture response model / fixture 응답 모델: `gpt-5.6-sol-offline-fixture`
- response status / 응답 상태: `completed`
- attempt count / 시도 횟수: `1`
- maximum attempts / 최대 시도: `2`
- timeout / 제한시간: `45.0s`
- credential source / credential source: `injected-no-secret`
- request payload SHA-256: `a688ee43d376339ff08e3e68d54491cbfe528ccb68d0130fd04003688f2feac0`
- raw response SHA-256: `cb6208f81fecea3051917ab8c24fa46a97e126218f3ede5ada78baa3931b79c5`
- structured body SHA-256: `de920c5ebaa479f662cecb3e14080eeec0517260539de2dcd1825dd86e78abf9`
- reconstructed Director Proposal SHA-256: `8d3a1b14a167db5b9dca8a049647a7e313eac3e55d1aefe04087d68e2c51513c`

### Edit exchange / 수정 교환

- requested model / 요청 모델: `gpt-5.6-sol`
- fixture response model / fixture 응답 모델: `gpt-5.6-sol-offline-fixture`
- response status / 응답 상태: `completed`
- attempt count / 시도 횟수: `1`
- maximum attempts / 최대 시도: `2`
- timeout / 제한시간: `45.0s`
- credential source / credential source: `injected-no-secret`
- request payload SHA-256: `5f7cad773b5867d78697a2725813b5816d985a064e8d33d4c8dceb6201018984`
- raw response SHA-256: `c651776af9fe341690aa081812d0d18747eec3986eac4b5b2dc91b6cab80d9d8`
- structured body SHA-256: `32e471ea4f001e042f99a97700e13e0c2aca0c1b2933daa3f7dbe44e27a340ff`
- reconstructed Director Proposal SHA-256: `0079fd3577459cc1e770c75c204d8fd59356f3a608583e84bd99755906587521`

The response IDs and response model names above are explicit offline fixture identifiers and MUST NOT be interpreted as OpenAI-produced live metadata. / 위 response ID와 response model은 명시적인 offline fixture 식별자이며 실제 OpenAI live metadata로 해석해서는 안 됩니다.

## 5. Fail-closed negative evidence / 실패 폐쇄 부정 근거

The canonical bundle deliberately exercised and blocked / 공식 bundle에서 의도적으로 실행·차단:

| Case / 사례 | Classification / 분류 | Result / 결과 |
|---|---|---|
| model attempts direct `blueprint` injection / 모델의 직접 Blueprint 주입 | `invalid_output` | `BLOCKED_AS_EXPECTED` |
| model refusal / 모델 refusal | `refusal` | `BLOCKED_AS_EXPECTED` |
| incomplete response / 불완전 응답 | `incomplete` | `BLOCKED_AS_EXPECTED` |
| HTTP 429 fixture / rate limit | `rate_limit` | `BLOCKED_AS_EXPECTED` |
| transport timeout fixture / timeout | `timeout` | `BLOCKED_AS_EXPECTED` |

The unit suite also covers authentication, server, general transport, invalid JSON, unknown section targeting, bounded retry, missing live credentials before a network call, and prevention of API-key leakage into injected transports. / 단위 테스트는 인증, server, 일반 transport, invalid JSON, 알 수 없는 section 지정, 제한 재시도, 네트워크 호출 전 live credential 누락 차단, injected transport로의 API key 누출 방지도 검증합니다.

## 6. First-gate failure and correction / 최초 게이트 실패와 수정

The first branch CI run `34538681615` at head `9ac7d45b4c91be48c73e2c84362e91e6ef6a5d5b` failed with **68 passed / 1 failed**. The single failure was an over-specific test assertion that assumed `Blueprint.project.seed` existed. The M1/Music Blueprint contract stores deterministic seed authority at the Intent generation boundary rather than requiring a `project.seed` field. The assertion was corrected to test the actual Intent boundary, producing head `40a1f202...`, after which both Python versions and all evidence stages passed.

최초 branch CI run `34538681615`은 **68 passed / 1 failed**였습니다. 유일한 실패는 `Blueprint.project.seed`가 존재한다고 가정한 과도한 테스트 assertion이었습니다. 실제 계약에 맞춰 seed 검증을 Intent 경계로 수정한 뒤 head `40a1f202...`에서 Python 3.11/3.12 및 전체 evidence 단계가 성공했습니다.

This failed run is retained here intentionally so later agents do not erase or reinterpret the validation history. / 후속 AI가 검증 이력을 삭제하거나 잘못 해석하지 않도록 최초 실패 run도 의도적으로 기록합니다.

## 7. Claim boundary / 주장 경계

M3-R2 evidence validates **the OpenAI adapter contract and offline integration path**, including current request construction, strict schema-shaped model-body handling, transport/error classification, M3-R1 authority enforcement, and downstream deterministic MUSICA execution.

M3-R2 근거는 **OpenAI adapter 계약과 offline 통합 경로**를 검증합니다.

It does **not** validate or imply / 다음을 검증·암시하지 않습니다:

- that a live OpenAI API request succeeded / 실제 OpenAI API 호출 성공,
- that `gpt-5.6-sol` will always return the same output / 모델의 미래 동일 출력,
- universal natural-language music understanding / 보편적 자연어 음악 이해,
- autonomous acceptance of AI output / AI 출력의 자율 승인,
- production/mastering-grade audio / 상용·마스터링급 음질,
- direct DAW/VST/plugin control / 직접 DAW·VST·plugin 제어.

A future authorized live smoke test, if performed, MUST be recorded separately as `LIVE_PROVIDER_EVIDENCE` and MUST NOT retroactively change the meaning of this offline validation record. / 향후 승인된 live smoke가 실행되더라도 반드시 `LIVE_PROVIDER_EVIDENCE`로 별도 기록하며 본 offline 검증 기록의 의미를 소급 변경하지 않습니다.
