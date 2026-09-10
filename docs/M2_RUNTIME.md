# M2 Project & Version Runtime / M2 프로젝트·버전 런타임

## Product role / 제품 역할

M2 turns an accepted Music Blueprint into a durable MUSICA user project. GitHub remains the source of truth for developing MUSICA itself; end users do not need Git to save, branch, inspect, or verify their music projects.

M2는 승인 Music Blueprint를 영속 MUSICA 사용자 프로젝트로 전환합니다. GitHub는 MUSICA 자체 개발의 SoT로 유지되지만 최종 사용자는 음악 프로젝트를 저장·분기·검사·검증하기 위해 Git을 사용할 필요가 없습니다.

## Project Bundle v0 / Project Bundle v0

```text
song.musica/
├── project.json
├── refs/
│   ├── HEAD.json
│   └── heads/<branch>.json
├── revisions/<revision-id>/
│   ├── blueprint.json
│   ├── revision.json
│   └── diff.json
├── objects/sha256/<digest>
├── artifacts/<revision-id>/
│   ├── manifest.json
│   └── files/*
└── audit/
    ├── history.jsonl
    └── HEAD
```

## Revision model / 리비전 모델

An accepted revision is immutable. `revision.json` binds the Blueprint hash, structured diff hash, parent revision, parent record hash, actor, reason, and logical sequence. Human-readable revision files are duplicated from the content-addressed object store for inspectability; integrity verification cross-checks both forms.

승인 리비전은 불변입니다. `revision.json`은 Blueprint hash, 구조화 diff hash, parent revision, parent record hash, actor, reason, logical sequence를 결속합니다. 검사 편의를 위해 사람이 읽을 수 있는 리비전 파일을 content-addressed object store와 함께 보존하고, 무결성 검증에서 두 표현을 상호 대조합니다.

## Branch model / branch 모델

A branch is a lightweight MUSICA ref pointing to an accepted revision record hash. Committing on one branch does not advance other branches. `refs/HEAD.json` stores the current symbolic branch independently from Git semantics.

branch는 승인 revision record hash를 가리키는 경량 MUSICA ref입니다. 한 branch의 commit은 다른 branch를 전진시키지 않습니다. `refs/HEAD.json`은 Git 의미론과 독립적인 현재 symbolic branch를 저장합니다.

## Artifact binding / 산출물 결속

Generated MIDI/WAV or later renderer outputs can be copied into `artifacts/<revision-id>/files/` and bound through an immutable manifest containing SHA-256, size, media type, and exact revision-record hash.

생성 MIDI/WAV 또는 이후 renderer 산출물은 `artifacts/<revision-id>/files/`에 복사되고 SHA-256·크기·media type·정확한 revision-record hash를 포함하는 불변 manifest로 결속될 수 있습니다.

## Audit and integrity / 감사·무결성

M2 uses a logical-sequence audit JSONL chain. Each event includes the previous event SHA-256, and `audit/HEAD` anchors the current event-chain tip inside the bundle. Verification cross-checks object filenames, revision hashes, parent links, refs, artifacts, stored diffs, and audit chaining.

M2는 논리 sequence 기반 audit JSONL chain을 사용합니다. 각 이벤트는 이전 이벤트 SHA-256을 포함하고 `audit/HEAD`가 bundle 내부의 현재 chain tip을 고정합니다. 검증은 object 파일명, revision hash, parent link, ref, artifact, 저장 diff, audit chain을 상호 대조합니다.

## Deterministic export/import / 결정론 export·import

Export uses canonical file ordering, fixed ZIP metadata, canonical JSON, and no wall-clock timestamp in core project state. Under the tested runtime, exporting the same verified Project Bundle twice and re-exporting after import must be byte-identical.

Export는 canonical 파일 순서, 고정 ZIP metadata, canonical JSON을 사용하며 핵심 프로젝트 상태에 wall-clock timestamp를 넣지 않습니다. 테스트 런타임에서 동일한 검증 Project Bundle을 두 번 export하거나 import 후 재-export하면 바이트 동일해야 합니다.

## Security boundary / 보안 경계

M2 v0 detects ordinary corruption or unauthorized byte changes inside the bundle when hashes are not all maliciously recomputed. It is not a digital-signature/authenticity system and does not identify who authored a change.

M2 v0는 모든 해시까지 악의적으로 재계산하지 않는 일반 손상·비인가 바이트 변경을 탐지합니다. 디지털 서명·authenticity 시스템이 아니며 변경 작성자의 신원을 증명하지 않습니다.
