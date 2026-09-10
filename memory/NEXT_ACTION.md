# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M2 — PROJECT & VERSION ENGINE v0 / M2 — 프로젝트·버전 엔진 v0**

M1 Creative Core v0 is validated. The next problem is no longer whether MUSICA can deterministically create and semantically revise a bounded piece of music. The next problem is whether those creative states can become a durable user project with inspectable history, branches, immutable accepted revisions, provenance, and integrity checks.

M1 Creative Core v0는 검증되었습니다. 다음 문제는 MUSICA가 제한 범위에서 음악을 결정론적으로 생성하고 의미 기반으로 수정할 수 있는지가 아닙니다. 이제 그 창작 상태를 검사 가능한 이력, branch, 불변 승인 리비전, provenance, 무결성 검사를 갖춘 영속적인 사용자 프로젝트로 만들 수 있는지를 증명해야 합니다.

## Architectural decision / 아키텍처 결정

GitHub remains the development and evidence SoT for the MUSICA software project, but MUSICA end users MUST NOT need Git to save or version their music.

GitHub는 MUSICA 소프트웨어 개발·근거의 SoT로 유지하지만, MUSICA 최종 사용자가 자신의 음악을 저장·버전 관리하기 위해 Git을 알아야 해서는 안 됩니다.

M2 therefore builds a renderer-independent **MUSICA Project Bundle** with content-addressed immutable revisions and lightweight refs.

따라서 M2는 renderer 독립적인 **MUSICA Project Bundle**을 구축하며, content-addressed 불변 리비전과 경량 ref를 사용합니다.

Proposed v0 shape / 제안 v0 구조:

```text
<project>.musica/
├── project.json
├── refs/
│   ├── HEAD.json
│   └── heads/<branch>.json
├── revisions/<revision-id>/
│   ├── blueprint.json
│   ├── revision.json
│   └── diff.json
├── objects/sha256/<digest>
├── artifacts/<revision-id>/manifest.json
└── audit/history.jsonl
```

The exact storage details may be refined by implementation evidence, but user-facing project persistence MUST remain separate from Git internals.

구체 저장 세부는 구현 근거에 따라 조정할 수 있으나, 사용자 프로젝트 영속성은 Git 내부 구조와 분리되어야 합니다.

## M2 required scope / M2 필수 범위

1. **Project Bundle contract / Project Bundle 계약** — machine-valid project metadata, refs, revision metadata, and artifact bindings.
2. **Create/open/save / 생성·열기·저장** — initialize a project from a validated M1 Blueprint and reopen the exact canonical state.
3. **Immutable accepted revisions / 불변 승인 리비전** — committed Blueprint revisions are content-addressed and cannot be silently overwritten.
4. **Branches and refs / branch·ref** — branch from an accepted revision and advance only the selected ref after a valid commit.
5. **Structured revision lineage / 구조화 리비전 계보** — parent revision, reason, actor, diff, locks, and provenance remain inspectable.
6. **Lock inheritance across stored revisions / 저장 리비전 간 lock 상속** — M0/M1 fail-closed rules continue to apply after reload and branching.
7. **Artifact binding / 산출물 결속** — MIDI/WAV/evidence hashes may be attached to the exact revision that produced them.
8. **Integrity verification / 무결성 검증** — tampered Blueprint/object/manifest content is detected by hash or contract mismatch.
9. **Deterministic export/import / 결정론 export·import** — the same validated project state can be exported and re-imported without semantic drift.
10. **M0/M1 regression + Python 3.11/3.12 CI / M0·M1 회귀 + Python 3.11/3.12 CI**.

## M2 canonical proof / M2 공식 증명 시나리오

```text
M1 Intent
  ↓
Blueprint R1
  ↓
Create Project Bundle
  ↓
commit R1 → main
  ↓
branch "variation-a"
  ↓
semantic edit under HARD locks
  ↓
commit R2 → variation-a
  ↓
main still points to R1
variation-a points to R2
  ↓
render R2 → MIDI/WAV
  ↓
bind artifact hashes to R2
  ↓
close/reopen project
  ↓
verify refs + lineage + locks + hashes
  ↓
modify stored bytes deliberately
  ↓
integrity verification MUST fail closed
```

## M2 non-goals / M2 비목표

M2 does not yet need cloud collaboration, account sync, CRDT editing, a production database, arbitrary Git interoperability, polished GUI history views, or AI-provider integration.

M2는 아직 클라우드 협업, 계정 동기화, CRDT 편집, 상용 데이터베이스, 임의 Git 상호운용, 완성형 GUI 히스토리 화면, AI provider 통합을 요구하지 않습니다.

## Product sequence after M2 / M2 이후 제품 순서

```text
M2 Project & Version Engine
→ M3 AI Music Director Provider Layer
→ M4 MUSICA Studio usable application MVP
→ M5 Renderer/DAW interoperability & quality expansion
→ M6 Product hardening / packaging / release candidate
```

## Development discipline / 개발 규율

```text
Issue → Branch → Contract → Implementation → Tests → PR → exact-head CI → Evidence → Merge → State update
```

Do not infer M2 capability from this plan. M2 becomes validated only after repository-backed implementation and evidence pass its acceptance gate.

본 계획만으로 M2 기능을 추론하지 않습니다. M2는 레포 기반 구현과 근거가 수용 게이트를 통과한 후에만 검증 상태가 됩니다.
