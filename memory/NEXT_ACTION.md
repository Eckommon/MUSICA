# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M0-R2 — Minimal Deterministic Music Loop / 최소 결정론 음악 루프**

M0-R1 executable contracts have passed repository CI. The next work is runtime proof, not more schema brainstorming.

M0-R1 실행 계약은 레포 CI를 통과했습니다. 다음 작업은 추가 스키마 브레인스토밍이 아니라 런타임 증명입니다.

## Immediate objective / 즉시 목표

Prove the smallest end-to-end MUSICA loop using only deterministic, free/local components where practical.

가능한 범위에서 결정론적 무료·로컬 구성요소만 사용하여 MUSICA의 최소 end-to-end 루프를 증명합니다.

```text
Validated Blueprint A
        ↓
Deterministic semantic edit request
        ↓
Candidate Blueprint B
        ↓
Lock / constraint validation
        ↓
Accepted Blueprint B + structured diff
        ↓
Blueprint → Music IR compiler
        ↓
Validated Music IR
        ↓
MIDI renderer + simple local WAV renderer
        ↓
Artifact hashes + evidence manifest
```

## Required M0-R2 implementation / 필수 M0-R2 구현

1. Minimal semantic resolver for the canonical M0 command. / 공식 M0 명령용 최소 semantic resolver.
2. Explicit candidate delta and selected/rejected mechanism record. / 명시적 후보 delta 및 선택·거절 메커니즘 기록.
3. Structured Blueprint diff. / 구조화 Blueprint diff.
4. Deterministic Blueprint → Music IR compiler. / 결정론적 Blueprint → Music IR 컴파일러.
5. Standards-compliant deterministic MIDI file writer. / 표준 호환 결정론 MIDI 파일 writer.
6. Free/local audible WAV preview renderer with no proprietary service. / 독점 서비스 없는 무료·로컬 청취 WAV preview renderer.
7. SHA-256 evidence manifest binding revision, compiler, renderer, config, and output artifacts. / 리비전·컴파일러·렌더러·설정·산출물을 묶는 SHA-256 근거 manifest.
8. Automated tests proving lock preservation, invalid-edit blocking, deterministic compilation, MIDI/WAV validity, and hash reproducibility. / lock 보존·금지 수정 차단·결정론 컴파일·MIDI/WAV 유효성·hash 재현성을 증명하는 자동 테스트.

## M0 acceptance gate / M0 수용 게이트

Follow `docs/M0_ACCEPTANCE.md`. M0 may become **VALIDATED** only after all M0-R2 runtime criteria pass CI and the implementation is merged.

`docs/M0_ACCEPTANCE.md`를 따릅니다. M0-R2 런타임 기준이 CI를 모두 통과하고 구현이 병합된 후에만 M0를 **VALIDATED**로 승격할 수 있습니다.

## Explicit non-goals / 명시적 비목표

Do not yet build a full DAW, VST host, neural audio foundation model, collaborative cloud backend, or polished production UI.

아직 완전한 DAW, VST host, 신경망 오디오 파운데이션 모델, 협업 클라우드 백엔드, 완성형 production UI를 구축하지 않습니다.

## Development discipline / 개발 규율

```text
Issue → Branch → Implementation → Tests → PR → CI evidence → Merge → State update
```

No implementation claim may be inferred from design or schema existence alone.

설계 또는 스키마 존재만으로 구현 상태를 추론하지 않습니다.
