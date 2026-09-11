# M4-R1 Validation Evidence / Studio Application Service 검증 근거

**Milestone / 마일스톤:** M4-R1 — Studio Application Service & Session Boundary v0  
**Evidence status / 근거 상태:** **VALIDATED** / **검증 완료**  
**Evidence class / 근거 등급:** LOCAL APPLICATION SERVICE EVIDENCE / 로컬 애플리케이션 서비스 근거

## 1. Scope / 범위

M4-R1 validates the first user-application boundary above the validated M0→M3 core. MUSICA can be operated through a local Studio service and loopback HTTP bridge while preserving AI authority, HARD locks, Project Engine integrity, workspace confinement, and the rule that Preview is never an accepted revision until explicit user acceptance.

M4-R1은 검증된 M0→M3 코어 위의 첫 사용자 애플리케이션 경계를 검증합니다. AI 권한, HARD lock, Project Engine 무결성, workspace 제한, 그리고 명시적 사용자 승인 전에는 Preview가 승인 리비전이 될 수 없다는 규칙을 유지한 채 local Studio service와 loopback HTTP bridge로 MUSICA를 조작할 수 있음을 증명합니다.

## 2. Final exact-head validation / 최종 exact-head 검증

- implementation PR: `#24`
- exact final head: `cba73433c5e83315472c0305b20f436672d1fb0d`
- exact-head PR CI run: `34549868112`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- M0 evidence generation/upload: **SUCCESS**
- M1 evidence generation/upload: **SUCCESS**
- M2 evidence generation/upload: **SUCCESS**
- M3-R1 evidence generation/upload: **SUCCESS**
- M3-R2 evidence generation/upload: **SUCCESS**
- M4-R1 evidence generation/upload: **SUCCESS**
- implementation merge: `4ebe2e0590b17f5e659dd48bed5b0331af7fac9b`

Earlier branch validation run `34540200139` also passed and was used to inspect the first canonical M4-R1 artifact before PR promotion.

이전 branch validation run `34540200139`도 성공했으며 PR 승격 전 첫 공식 M4-R1 artifact를 직접 검사하는 데 사용했습니다.

## 3. Final canonical artifact / 최종 공식 artifact

- artifact name: `musica-m4-r1-studio-service`
- artifact ID: `10180408128`
- artifact digest: `sha256:3640aebebb156f975a9faea58026604f419aa5ecc471174f7da6cb28f1d4c81e`
- external network required: **NO**
- live OpenAI call performed: **NO**
- loopback HTTP exercised: **YES**
- default provider evidence mode: `fixture`

The inspected pre-PR canonical artifact contained 52 evidence files. The exact-head PR run regenerated the same M4-R1 evidence class and uploaded it successfully.

검사한 pre-PR 공식 artifact는 52개 근거 파일을 포함했고, PR exact-head run은 동일 M4-R1 evidence class를 다시 생성·업로드하는 데 성공했습니다.

## 4. Acceptance proof / 수용 증명

Canonical proof flags / 공식 증명 플래그:

```text
preview_ref_unchanged_before_accept = true
accept_advanced_to_preview_candidate = true
discard_ref_unchanged                = true
branch_created_and_checked_out       = true
deterministic_export_byte_identical  = true
reopen_preserved_head                = true
loopback_http_status                 = PASS
negative_cases_blocked               = true
project_integrity_status             = PASS
```

Canonical Project Engine verification / 공식 Project Engine 검증:

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

The accepted revision is recorded with `actor = user`, parent `rev-001`, and reason `Accept Studio semantic edit: tension increase 0.18.`

승인 리비전은 `actor = user`, parent `rev-001`, reason `Accept Studio semantic edit: tension increase 0.18.`로 기록됩니다.

## 6. Discard, branching, history / Discard·branch·history

`variation-a` was created from the accepted revision. A later preview was discarded and the branch head remained unchanged.

```text
main        → rev-studio-b470e6cf61c9f6dc04a5feea
variation-a → rev-studio-b470e6cf61c9f6dc04a5feea
Discard      → head unchanged
```

Revision history remains a durable M2 record rather than ephemeral UI state.

리비전 이력은 일시적인 UI 상태가 아니라 M2 영속 기록으로 유지됩니다.

## 7. Deterministic export / 결정론 export

Two exports of unchanged canonical state were byte-identical:

```text
sha256 = 35ba8f85a7918465a7678b16bd8ba11e1a4d81861322c07db193c1b299fd8454
size   = 770850 bytes
byte_identical = true
```

## 8. Loopback HTTP and workspace security / Loopback HTTP·workspace 보안

Canonical evidence verifies:

- health endpoint: HTTP `200`,
- session inspection: HTTP `200`,
- accepted WAV retrieval: HTTP `200`, `audio/wav`,
- loopback-only policy: **true**,
- project path traversal: `BLOCKED_AS_EXPECTED`,
- non-loopback HTTP bind: `BLOCKED_AS_EXPECTED`.

Automated tests additionally cover symlink/workspace escape, preview conflict rules, missing live credentials before project creation, restart/open, media retrieval, branch/history, and deterministic export.

자동 테스트는 symlink/workspace 탈출, preview 충돌 규칙, 프로젝트 생성 전 live credential 부재, restart/open, media retrieval, branch/history, 결정론 export도 검증합니다.

## 9. Claim boundary / 주장 경계

M4-R1 validates **application/session service behavior**, not final product UX. It does **not** validate:

- polished browser Studio UX,
- browser-level end-to-end user interaction,
- production mastering or professional render quality,
- cloud collaboration or multi-user security,
- desktop installer/shell packaging,
- remote HTTP serving,
- live OpenAI execution,
- DAW/VST/sampler interoperability,
- crash-atomic recovery across revision commit and artifact binding.

M4-R1은 **애플리케이션·세션 서비스 동작**만 검증합니다. 완성형 browser Studio UX, browser E2E, 상용 음질, cloud collaboration, desktop packaging, remote HTTP, 실제 OpenAI 실행, DAW/VST 상호운용, commit/artifact-binding crash-atomic recovery는 검증하지 않습니다.

## 10. Verdict / 판정

**M4-R1 = IMPLEMENTED + TESTED + EVIDENCE-BACKED + MERGED + VALIDATED.**

The exact next product step is M4-R2 Browser Studio UI, which MUST consume this validated service and MUST NOT create a second shadow canonical music state.

정확한 다음 제품 단계는 M4-R2 Browser Studio UI이며, 반드시 이 검증된 service를 사용하고 별도의 shadow canonical music state를 만들어서는 안 됩니다.
