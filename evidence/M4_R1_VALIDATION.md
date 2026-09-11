# M4-R1 Validation Evidence / Studio Application Service 검증 근거

**Milestone / 마일스톤:** M4-R1 — Studio Application Service & Session Boundary v0  
**Evidence status / 근거 상태:** BRANCH VALIDATION PASSED; PR exact-head validation pending / branch 검증 통과, PR exact-head 검증 대기  
**Evidence class / 근거 등급:** LOCAL APPLICATION SERVICE EVIDENCE / 로컬 애플리케이션 서비스 근거

## 1. Scope / 범위

M4-R1 validates the first user-application boundary above the already validated M0→M3 core. It proves that MUSICA can be operated through a local Studio service and loopback HTTP bridge while preserving the existing authority, lock, project-integrity, and preview/accept rules.

M4-R1은 이미 검증된 M0→M3 코어 위의 첫 사용자 애플리케이션 경계를 검증합니다. 기존 권한, lock, project integrity, preview/accept 규칙을 보존하면서 MUSICA를 local Studio service와 loopback HTTP bridge로 조작할 수 있음을 증명합니다.

## 2. Branch validation identity / Branch 검증 식별자

- branch: `m4-r1-studio-application-service-v0`
- validated branch head: `276299b24183279e035f86be0ae97b7b857834ae`
- GitHub Actions run: `34540200139`
- run conclusion: **SUCCESS**
- Python 3.11 test job: **SUCCESS**
- Python 3.12 test job: **SUCCESS**
- M0 evidence regeneration/upload: **SUCCESS**
- M1 evidence regeneration/upload: **SUCCESS**
- M2 evidence regeneration/upload: **SUCCESS**
- M3-R1 evidence regeneration/upload: **SUCCESS**
- M3-R2 evidence regeneration/upload: **SUCCESS**
- M4-R1 evidence generation/upload: **SUCCESS**

## 3. Canonical artifact / 공식 artifact

- artifact name: `musica-m4-r1-studio-service`
- artifact ID: `10176996635`
- artifact digest: `sha256:e12629cf1049f33679b7e5f180d48b49fd9ddfadaf7cdd236edec9ea9c0e07d4`
- artifact file count inspected: **52**
- external network used: **NO**
- live OpenAI call performed: **NO**
- loopback HTTP used: **YES**
- provider mode: `fixture`

## 4. Acceptance proof / 수용 증명

The inspected artifact records all of the following as true / 검사한 artifact는 다음을 모두 참으로 기록합니다.

- `preview_ref_unchanged_before_accept = true`
- `accept_advanced_to_preview_candidate = true`
- `discard_ref_unchanged = true`
- `branch_created_and_checked_out = true`
- `deterministic_export_byte_identical = true`
- `reopen_preserved_head = true`
- `loopback_http_status = PASS`
- `negative_cases_blocked = true`
- `project_integrity_status = PASS`

Canonical project verification / 공식 project verification:

```text
status              PASS
revision_count      2
ref_count           2
object_count        12
artifact_count      4
audit_event_count   6
```

## 5. Preview → Accept authority proof / Preview → Accept 권한 증명

Initial accepted state / 최초 승인 상태:

```text
main → rev-001
pending_preview = null
integrity = PASS
MIDI/WAV available = true
```

After semantic preview / semantic preview 후:

```text
main → rev-001                    # unchanged / 불변
pending preview candidate → rev-studio-b470e6cf61c9f6dc04a5feea
preview diff count = 9
preview MIDI/WAV available = true
```

Only after explicit acceptance / 명시적 Accept 후에만:

```text
main → rev-studio-b470e6cf61c9f6dc04a5feea
pending_preview = null
accepted MIDI/WAV bound to revision
project integrity = PASS
```

The accepted revision record explicitly states:

```text
actor = user
reason = "Accept Studio semantic edit: tension increase 0.18."
parent_revision_id = rev-001
```

This is direct evidence that an audible preview is not silently promoted into canonical state.

이는 청취 가능한 preview가 암묵적으로 canonical state로 승격되지 않는다는 직접 근거입니다.

## 6. Discard and branching proof / Discard 및 branch 증명

A `variation-a` branch was created from the accepted revision. A later preview was discarded and the branch head remained exactly unchanged.

`variation-a` branch를 승인 리비전에서 생성했고 이후 preview를 Discard한 뒤 branch head가 정확히 유지되었습니다.

```text
main        → rev-studio-b470e6cf61c9f6dc04a5feea
variation-a → rev-studio-b470e6cf61c9f6dc04a5feea
Discard      → head unchanged
```

## 7. Deterministic project export / 결정론 project export

Two exports of unchanged canonical state were byte-identical:

```text
sha256 = 35ba8f85a7918465a7678b16bd8ba11e1a4d81861322c07db193c1b299fd8454
size   = 770850 bytes
byte_identical = true
```

## 8. Loopback HTTP proof / Loopback HTTP 증명

The canonical run started the local bridge and verified:

- health request: HTTP `200`
- session inspect request: HTTP `200`
- accepted WAV request: HTTP `200`
- audio content type: `audio/wav`
- WAV size: `352844` bytes
- loopback-only policy: **true**

No remote-serving capability is claimed.

원격 서비스 능력은 주장하지 않습니다.

## 9. Negative proof / 부정 증명

The canonical artifact records explicit fail-closed cases:

```text
project_path_traversal  → BLOCKED_AS_EXPECTED
non_loopback_http_bind  → BLOCKED_AS_EXPECTED
```

The automated test suite additionally covers workspace/symlink confinement, pending-preview conflict rules, missing OpenAI credentials before project creation, restart/open behavior, and loopback HTTP media retrieval.

자동화 테스트는 workspace/symlink 제한, pending-preview 충돌 규칙, 프로젝트 생성 전 OpenAI credential 부재 차단, restart/open, loopback HTTP media retrieval도 함께 검증합니다.

## 10. Claim boundary / 주장 경계

This evidence validates **M4-R1 application/session service behavior only**. It does not validate:

- polished browser/end-user UX,
- production mastering or professional render quality,
- cloud collaboration or multi-user security,
- desktop installer/shell packaging,
- remote HTTP serving,
- live OpenAI execution,
- DAW/VST/sampler interoperability,
- crash-atomic recovery across the revision-commit/artifact-binding boundary.

이 근거는 **M4-R1 application/session service 동작만** 검증합니다. 완성형 브라우저 UX, 상용 음질, cloud collaboration, desktop packaging, 원격 HTTP, 실제 OpenAI 호출, DAW/VST 상호운용, commit/artifact-binding 사이의 crash-atomic recovery는 검증하지 않습니다.

## 11. Promotion rule / 승격 규칙

M4-R1 SHALL NOT be marked `VALIDATED` solely from this branch run. The evidence-bearing PR head must pass Python 3.11/3.12 plus the entire M0→M4-R1 evidence chain. Only that exact head may be merged and then promoted through a state-only closure.

이 branch run만으로 M4-R1을 `VALIDATED`로 표시하지 않습니다. 이 durable evidence를 포함한 PR exact head가 Python 3.11/3.12 및 M0→M4-R1 전체 evidence chain을 통과해야 하며, 그 exact head만 병합 후 state-only closure로 승격할 수 있습니다.
