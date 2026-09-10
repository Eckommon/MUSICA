# M2 Project & Version Engine Acceptance / M2 프로젝트·버전 엔진 수용 기준

**Status / 상태:** NORMATIVE GATE / 규범 게이트

## Objective / 목표

M2 proves that M1 creative state can become a durable, inspectable, branchable, integrity-checked user project without requiring Git.

M2는 M1 창작 상태가 Git을 요구하지 않으면서 영속적·검사 가능·분기 가능하고 무결성 검사가 가능한 사용자 프로젝트가 될 수 있음을 증명합니다.

## Required evidence / 필수 근거

M2 is `VALIDATED` only when repository evidence proves all of the following.

M2는 레포 근거가 아래 항목을 모두 증명한 경우에만 `VALIDATED`입니다.

1. Project metadata, refs, revision records, and artifact manifests are machine-valid. / 프로젝트 메타데이터·ref·revision record·artifact manifest가 기계 검증됩니다.
2. A validated M1 Blueprint can initialize and reopen an exact `.musica` Project Bundle. / 검증된 M1 Blueprint로 `.musica` Project Bundle을 생성하고 정확히 다시 열 수 있습니다.
3. Accepted revisions are immutable and content-addressed with SHA-256. / 승인 리비전이 불변이며 SHA-256 content-addressed입니다.
4. A branch can be created from an accepted revision and only the selected branch advances on commit. / 승인 리비전에서 branch를 만들고 commit 시 선택한 branch만 전진합니다.
5. Parent lineage, structured diff, actor, reason, and logical sequence remain inspectable. / parent 계보·구조화 diff·actor·reason·논리 sequence가 검사 가능합니다.
6. HARD tempo, melody-identity-token, and rhythm-identity-token rules remain fail-closed after save/reload/branching. / 저장·재로드·분기 후에도 HARD tempo·melody identity token·rhythm identity token 규칙이 실패 폐쇄로 유지됩니다.
7. Rendered MIDI/WAV artifacts can be SHA-256 bound to the exact revision that produced them. / 렌더 MIDI/WAV 산출물을 생성한 정확한 리비전에 SHA-256으로 결속할 수 있습니다.
8. Blueprint, object, artifact, and audit-chain tampering is detected by integrity verification within the implemented v0 threat model. / 구현된 v0 위협 모델 내에서 Blueprint·object·artifact·audit chain 변조를 무결성 검증이 탐지합니다.
9. Deterministic export/import preserves refs, revisions, hashes, and semantic state; re-export is byte-identical under the tested environment. / 결정론 export/import가 ref·revision·hash·semantic state를 보존하며 테스트 환경에서 재-export가 바이트 동일합니다.
10. The canonical M2 branch scenario produces a durable evidence artifact and manifest. / 공식 M2 branch 시나리오가 영속 evidence artifact와 manifest를 생성합니다.
11. Python 3.11 and 3.12 CI pass. / Python 3.11·3.12 CI가 통과합니다.
12. M0 and M1 regression suites continue to pass. / M0·M1 회귀 suite가 계속 통과합니다.

## Integrity boundary / 무결성 경계

M2 v0 provides **content integrity**, not signer identity or hostile-rewriter authenticity. A party capable of rewriting every file and recomputing every hash is outside the v0 authenticity claim.

M2 v0는 **콘텐츠 무결성**을 제공하며 서명자 신원 또는 적대적 전체 재작성에 대한 authenticity를 제공하지 않습니다. 모든 파일과 해시를 다시 작성할 수 있는 공격자는 v0 authenticity 주장 범위 밖입니다.

## Non-goals / 비목표

M2 does not prove cloud collaboration, account synchronization, CRDT editing, Git compatibility for user projects, a production database, polished visual history tools, or AI-provider integration.

M2는 클라우드 협업·계정 동기화·CRDT 편집·사용자 프로젝트의 Git 호환·상용 데이터베이스·완성형 시각 히스토리 도구·AI provider 통합을 증명하지 않습니다.
