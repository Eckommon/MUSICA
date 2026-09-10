# M2 Project & Version Engine Validation Evidence / M2 프로젝트·버전 엔진 검증 근거

**Evidence status / 근거 상태:** PASS — PRE-MERGE VALIDATION / 통과 — 병합 전 검증

## Source / 출처

- Pull Request / PR: `#12`
- Validated head: `580e4d6ce6314020a49cc3d2a63c0617f4ef1f6f`
- GitHub Actions workflow: `MUSICA CI`
- Workflow run: **34509874074**
- Python 3.11 full suite: **SUCCESS**
- Python 3.12 full suite: **SUCCESS**
- M0 evidence regeneration/upload: **SUCCESS**
- M1 evidence regeneration/upload: **SUCCESS**
- M2 evidence generation/upload: **SUCCESS**

## M2 workflow artifact / M2 workflow 산출물

- Artifact name: `musica-m2-project-version`
- Artifact ID: **10165359233**
- Archive size: **1,034,653 bytes**
- GitHub artifact digest: `sha256:609496e735469dab81a61964e3c6878f0e8df111555124e2509e02c96952242d`
- Evidence ZIP entries: **33**
- Manifest-bound evidence files: **32**

## Canonical Project Bundle proof / 공식 Project Bundle 증명

```text
main        → rev-001
variation-a → rev-m2-variation-a-001
```

- root revision / 루트 리비전: `rev-001`
- variation parent / variation parent: `rev-001`
- structured variation diff entries / 구조화 variation diff 항목: **9**
- current symbolic branch / 현재 symbolic branch: `main`
- accepted revisions / 승인 리비전: **2**
- branch refs / branch ref: **2**
- content-addressed objects / content-addressed object: **9**
- revision-bound artifacts / 리비전 결속 artifact: **2**
- logical audit events / 논리 audit event: **4**
- integrity verification / 무결성 검증: **PASS**

The `main` ref remained on R1 while `variation-a` advanced independently to R2.

`main` ref는 R1에 유지되고 `variation-a`만 독립적으로 R2로 전진했습니다.

## Artifact binding / 산출물 결속

The canonical R2 render produced MIDI and WAV files that were copied into the Project Bundle and bound through the immutable artifact manifest to the exact R2 revision-record SHA-256.

공식 R2 렌더의 MIDI와 WAV가 Project Bundle로 복사되고, 불변 artifact manifest를 통해 정확한 R2 revision-record SHA-256에 결속되었습니다.

Artifact binding count / 결속 산출물 수: **2**.

## Export/import reproducibility / export·import 재현성

- canonical project export SHA-256: `91016c94848de6c2a8ecc7e8d73b886ff94e2ad49fc28f4c84544d4f044ad642`
- imported integrity verification: **PASS**
- imported revisions: **2**
- imported refs: **2**
- imported objects: **9**
- imported artifacts: **2**
- imported audit events: **4**
- re-export byte-identical to original export: **TRUE**

## Tamper fail-closed evidence / 변조 실패 폐쇄 근거

The canonical proof copied the verified Project Bundle, appended an unauthorized byte to:

공식 증명은 검증된 Project Bundle 복사본에서 다음 파일에 비인가 바이트를 추가했습니다.

`revisions/rev-m2-variation-a-001/blueprint.json`

Result / 결과: **BLOCKED_AS_EXPECTED**.

The failure included a hash-mismatch signal. / 실패 결과에 hash mismatch 신호가 포함되었습니다.

## Acceptance interpretation / 수용 해석

The pre-merge evidence satisfies the executable requirements in `docs/M2_ACCEPTANCE.md` for the bounded M2 Project & Version Engine implementation. Final `M2 = VALIDATED` status must wait until this exact implementation/evidence head passes CI again and is merged to `main`, followed by a state-only closure update.

본 병합 전 근거는 제한형 M2 Project & Version Engine 구현에 대한 `docs/M2_ACCEPTANCE.md`의 실행 요구를 충족합니다. 최종 `M2 = VALIDATED` 상태는 이 정확한 구현·근거 HEAD가 다시 CI를 통과하고 `main`에 병합된 뒤 상태-only 종결 업데이트까지 완료된 후 선언합니다.

## Claim boundary / 주장 경계

M2 proves Git-independent local project persistence and content integrity within the v0 threat model. It does not prove signer authenticity, cloud collaboration, CRDT editing, Git-compatible user projects, a production database, polished GUI history, or AI-provider integration.

M2는 v0 위협 모델 내에서 Git 독립 로컬 프로젝트 영속성과 콘텐츠 무결성을 증명합니다. 서명자 authenticity, 클라우드 협업, CRDT 편집, Git 호환 사용자 프로젝트, 상용 DB, 완성형 GUI 히스토리, AI provider 통합은 증명하지 않습니다.
