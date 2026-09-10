# M3-R1 Runtime — AI Music Director Provider Boundary / M3-R1 런타임 — AI Music Director Provider 경계

## 1. Runtime role / 런타임 역할

M3-R1 adds a provider-neutral boundary between user language and MUSICA's already validated M1/M2 core. The provider is intentionally not allowed to own, persist, or directly mutate canonical musical state.

M3-R1은 사용자 자연어와 이미 검증된 M1/M2 코어 사이에 provider-neutral 경계를 추가합니다. Provider는 의도적으로 공식 음악 상태를 소유·저장·직접 변경할 수 없습니다.

## 2. Authority boundary / 권한 경계

```text
UNTRUSTED / NON-AUTHORITATIVE
User language → Provider → Director Proposal
                         │
                         ▼
TRUST BOUNDARY
Schema + request binding + capability + user-authority validation
                         │
                         ▼
TRUSTED MUSICA CORE
Music Intent / Semantic Control
→ deterministic M1 transform
→ HARD lock + constraint validation
→ candidate Blueprint
→ explicit M2 commit
→ accepted revision
```

A provider never receives a `MusicaProject` object. Provider invocation is data-in/data-out only.

Provider는 `MusicaProject` 객체를 전달받지 않습니다. Provider 호출은 데이터 입력/출력으로만 구성됩니다.

## 3. Contracts / 계약

### `Director Provider Capability v0`

Declares provider/model identity, whether it is deterministic or networked, supported request modes, style profiles, semantic axes, and explicit claim boundaries.

Provider/model 식별자, 결정론·네트워크 여부, 지원 request mode, style profile, semantic axis, 주장 경계를 선언합니다.

### `Director Request v0`

Records the original user language plus optional explicit user hints. Edit requests additionally contain an exact read-only snapshot of the current canonical revision: project/revision IDs, Blueprint SHA-256, duration, sections, HARD-lock summaries, semantic state, and supported axes.

원본 사용자 자연어와 선택적 명시 사용자 hint를 기록합니다. Edit request에는 현재 공식 revision의 project/revision ID, Blueprint SHA-256, duration, section, HARD-lock 요약, semantic 상태, 지원 axis를 포함하는 정확한 read-only snapshot이 추가됩니다.

### `Director Proposal v0`

Permits only two bounded proposal kinds in R1:

R1에서는 다음 두 제한형 proposal만 허용합니다.

- `create_intent`: fields sufficient to lower into `Music Intent v0`,
- `semantic_edit`: fields sufficient to lower into `Semantic Control v0`.

It cannot contain a direct Music Blueprint, arbitrary JSON Patch, Project Bundle operation, acceptance flag, or unrestricted file/path mutation.

직접 Music Blueprint, 임의 JSON Patch, Project Bundle operation, 승인 flag, 무제한 파일/path 변경을 포함할 수 없습니다.

### `Director Trace v0`

Records SHA-256 digests for the exact request, proposal, provider capability declaration, and accepted lowered contract. It also records provider/model identity and the authority state `PROPOSAL_ONLY_MUSICA_CORE_ACCEPTED`.

정확한 request, proposal, provider capability 선언, 승인된 lowering 계약의 SHA-256 digest와 provider/model 식별자 및 권한 상태를 기록합니다.

## 4. User authority / 사용자 권위

Explicit create hints are authoritative over provider inference. If the user explicitly supplied duration, use case, style profile, or seed, the proposal MUST preserve it. `preserve_on_edit` and exclusions are also exact user policy in M3-R1 and a provider may not silently add or remove them.

명시된 duration, use case, style profile, seed는 provider 추론보다 우선하며 proposal이 그대로 보존해야 합니다. `preserve_on_edit`와 exclusion도 M3-R1에서는 정확한 사용자 정책이며 provider가 조용히 추가·삭제할 수 없습니다.

## 5. Edit context binding / 수정 context 결속

`build_edit_request()` derives the request context from a validated Blueprint and hashes its canonical JSON bytes. `direct_edit()` independently re-derives the context from the supplied parent and requires exact equality before calling or accepting provider output.

`build_edit_request()`는 검증된 Blueprint에서 request context를 파생하고 canonical JSON byte를 해시합니다. `direct_edit()`는 전달받은 parent에서 context를 독립적으로 다시 계산하여 provider 출력을 호출·수용하기 전에 완전 일치를 요구합니다.

This prevents a stale or substituted request from being applied to a different revision.

따라서 오래되거나 대체된 request가 다른 revision에 적용되는 것을 차단합니다.

## 6. Reference provider / 참조 provider

`FixtureMusicDirectorProvider` is a deterministic, transparent, deliberately narrow provider used only to validate the provider boundary in CI. It supports the three M1 style profiles and six M1 semantic axes through a documented bounded keyword/rule vocabulary.

`FixtureMusicDirectorProvider`는 CI에서 provider 경계를 검증하기 위한 결정론적·투명·의도적으로 좁은 provider입니다. 문서화된 제한형 keyword/rule vocabulary로 M1의 세 style profile과 6개 semantic axis를 지원합니다.

It is **not** evidence of general natural-language intelligence.

이는 범용 자연어 지능의 근거가 아닙니다.

## 7. Create runtime / 생성 런타임

```text
build_create_request()
→ request_provider_proposal()
→ validate_director_proposal()
→ lower_create_proposal()
→ validate Music Intent v0
→ compose_blueprint()
→ validated Blueprint
```

No project is mutated by `direct_create()`. Project creation/commit is an explicit M2 operation after the returned Blueprint has passed trusted validation.

`direct_create()`는 프로젝트를 변경하지 않습니다. 반환 Blueprint가 신뢰 검증을 통과한 뒤 M2의 명시적 project 생성/commit이 수행됩니다.

## 8. Edit runtime / 수정 런타임

```text
build_edit_request(parent)
→ verify exact context against parent
→ request_provider_proposal()
→ validate_director_proposal()
→ lower_edit_proposal()
→ validate Semantic Control v0
→ apply_semantic_control(parent)
→ validate inherited HARD locks/constraints
→ candidate + structured diff
```

`direct_edit()` remains side-effect free with respect to Project Bundle refs. The caller must explicitly commit the candidate through M2.

`direct_edit()`는 Project Bundle ref에 대해 side-effect free입니다. 호출자가 M2를 통해 candidate를 명시적으로 commit해야 합니다.

## 9. Provenance / 출처 추적

Provider output is not treated as reproducible merely because it has a model name. M3 traces bind:

Provider 출력은 model 이름이 있다는 이유만으로 재현 가능하다고 간주하지 않습니다. M3 trace는 다음을 결속합니다.

- exact Director Request digest,
- exact Director Proposal digest,
- provider capability declaration digest,
- provider/model identifiers,
- accepted Music Intent or Semantic Control digest,
- explicit non-authoritative authority status.

Live-provider transport/configuration provenance is deferred to M3-R2.

실제 provider의 transport/configuration provenance는 M3-R2에서 추가합니다.

## 10. Fail-closed cases / 실패 폐쇄 조건

M3-R1 rejects at least:

M3-R1은 최소 다음 경우를 거부합니다.

- schema-invalid provider output,
- request/proposal ID or mode mismatch,
- provider/model metadata mismatch,
- undeclared provider capability use,
- explicit user-hint policy conflict,
- invalid tempo envelope,
- unsupported semantic axis,
- non-explicit/out-of-range edit scope,
- stale/substituted Blueprint context,
- arbitrary Blueprint/patch/canonical-state injection,
- downstream HARD-lock or constraint conflict.

## 11. M3-R2 handoff / M3-R2 인계

Once this boundary is validated, M3-R2 may add a real OpenAI provider adapter behind the same protocol. Network transport, credentials, retry/error policy, structured output transport, and live-provider provenance must remain adapter concerns; they must not weaken this authority model.

본 경계가 검증된 뒤 M3-R2에서 동일 protocol 뒤에 실제 OpenAI provider adapter를 추가할 수 있습니다. 네트워크 transport, credential, retry/error policy, structured output transport, 실제 provider provenance는 adapter 관심사로 유지하며 본 권한 모델을 약화해서는 안 됩니다.
