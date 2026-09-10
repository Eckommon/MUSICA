# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M4-R1 — MUSICA STUDIO APPLICATION SERVICE & SESSION BOUNDARY v0 / M4-R1 — MUSICA Studio 애플리케이션 서비스·세션 경계 v0**

M0→M3 are validated within their bounded claims. The next priority is product usability: expose the existing creative, Director, project/version, render and evidence core through a stable local application boundary so a non-developer user can operate MUSICA without editing JSON or invoking Python modules directly.

M0→M3는 제한된 주장 범위에서 검증되었습니다. 다음 우선순위는 제품 사용성입니다. 기존 창작·Director·프로젝트/버전·렌더·근거 코어를 안정적인 로컬 애플리케이션 경계로 노출하여 비개발 사용자가 JSON을 직접 편집하거나 Python 모듈을 호출하지 않고 MUSICA를 사용할 수 있게 해야 합니다.

## Product architecture decision / 제품 아키텍처 결정

M4 will begin as a **local-first Studio with a Python application service and browser UI**, while preserving the option to wrap the same local service/UI in a desktop shell during product hardening.

M4는 **Python 애플리케이션 서비스 + 브라우저 UI의 local-first Studio**로 시작합니다. 이후 제품 hardening 단계에서 동일한 로컬 service/UI를 desktop shell로 감쌀 수 있도록 경계를 유지합니다.

Why / 이유:

- current validated core is Python-native / 현재 검증 코어가 Python 기반,
- browser UI provides a usable PC surface without forcing a large desktop framework into the trusted core / 큰 desktop framework를 신뢰 코어에 강제하지 않고 PC 사용 화면 제공,
- service/UI separation keeps Direct/Shape/Inspect/Code surfaces compatible with one canonical project state / 서비스·UI 분리로 Direct/Shape/Inspect/Code가 하나의 공식 상태를 공유,
- future desktop packaging remains possible without rewriting the music core / 음악 코어 재작성 없이 향후 desktop packaging 가능.

M4 MUST remain local-first by default. No cloud account, telemetry, remote file upload, or background network behavior is required for the MVP.

M4 MVP는 기본 local-first여야 하며 cloud account, telemetry, remote file upload, background network 동작을 요구하지 않습니다.

## M4 staged sequence / M4 단계 순서

### M4-R1 — Application Service & Session Boundary

Build a narrow application API above the validated core. Required / 검증된 core 위에 좁은 app API 구축:

1. create/open a Studio session backed by a `.musica` Project Bundle / `.musica` Project Bundle 기반 session 생성·열기,
2. create music from a structured/director request using fixture/offline provider by default / 기본 offline provider로 음악 생성,
3. optional OpenAI provider selection only when runtime credential is available / credential이 있을 때만 선택적 OpenAI provider,
4. inspect current project/revision/sections/semantic state/locks/branches / 프로젝트·리비전·구간·semantic state·lock·branch 조회,
5. apply one validated semantic edit and preview the candidate before commit / semantic 수정 후 commit 전 preview,
6. explicit accept/commit and discard boundaries / 명시적 승인·commit·discard,
7. create/checkout branches and inspect revision history / branch·history,
8. deterministic preview render and local artifact retrieval / 결정론 preview·local artifact,
9. export `.musica` project archive / 프로젝트 export,
10. path confinement: a Studio session MUST NOT escape its configured workspace / workspace 경로 탈출 차단,
11. no implicit AI acceptance or project mutation / AI의 암묵적 승인·프로젝트 변경 금지,
12. machine-valid app response/error contracts and Python 3.11/3.12 tests / app 응답·오류 계약 및 테스트.

### M4-R2 — Studio UI Vertical Slice

Expose R1 through an actual user-facing local browser Studio. Required / 실제 사용자 UI:

```text
Create / Open Project
        ↓
Direct prompt
        ↓
Generate proposal / music
        ↓
Audio preview
        ↓
Shape controls
  energy / tension / density
  motion / brightness / warmth
        ↓
Locks + current section view
        ↓
Preview edit diff
        ↓
Accept / Discard
        ↓
Versions / Branches
        ↓
Export Project + MIDI/WAV
```

The first UI SHOULD use progressive disclosure:

- **Direct:** prompt + Generate / 자연어 지시,
- **Shape:** six semantic controls + section scope / 6축·구간,
- **Inspect:** locks, exact diff, Blueprint/revision metadata / lock·diff·메타데이터,
- **Code:** raw validated JSON view/download, not direct unsafe mutation by default / 검증 JSON 조회·다운로드.

### M4-R3 — Usable MVP acceptance

M4 becomes validated only after a clean local workflow proves that a user can create a project, hear a preview, make a semantic edit, inspect what changed and what stayed locked, accept a version, switch branches/history, and export the project without using developer commands.

사용자가 개발자 명령 없이 프로젝트 생성 → 청취 → 의미 수정 → 변경/보존 확인 → 버전 승인 → branch/history → export를 수행할 수 있어야 M4를 검증 완료로 승격합니다.

## M4-R1 authority boundary / M4-R1 권한 경계

```text
Studio UI / client
       ↓
Application Service
       ↓
Director Request / semantic command
       ↓
M3 AI proposal boundary
       ↓
M1 trusted creative/semantic core
       ↓
M0 contracts + locks
       ↓
[PREVIEW — not canonical]
       ↓ explicit accept only
M2 Project Engine commit
       ↓
Accepted revision + render artifacts
```

A preview candidate MUST NOT silently advance a branch ref. / preview candidate는 branch ref를 암묵적으로 전진시켜서는 안 됩니다.

## Technology direction / 기술 방향

For R1, prefer a minimal local HTTP/application-service boundary with explicit JSON contracts and no cloud dependency. Keep framework-specific code outside the music core. R2 may add a static/browser frontend over those endpoints. Avoid Electron/Tauri/PySide commitment until the interaction model is validated; desktop wrapping belongs after the local Studio workflow is proven.

R1에서는 명시적 JSON 계약을 가진 최소 로컬 HTTP/application-service 경계를 우선합니다. framework-specific 코드는 음악 코어 바깥에 둡니다. R2에서는 그 endpoint 위에 static/browser frontend를 추가할 수 있습니다. interaction model이 검증되기 전 Electron/Tauri/PySide에 조기 종속하지 않으며 desktop wrapping은 로컬 Studio workflow 증명 이후에 진행합니다.

## M4-R1 non-goals / M4-R1 비목표

- production cloud backend / 상용 cloud backend,
- user accounts/sync / 계정·동기화,
- multi-user collaboration / 다중 사용자 협업,
- DAW replacement / DAW 대체,
- professional renderer quality / 전문 렌더 음질,
- arbitrary plugin hosting / 임의 plugin hosting,
- automatic live OpenAI requirement / OpenAI live 호출 필수화,
- installer/signing / 설치 프로그램·코드 서명.

## Product sequence / 제품 순서

```text
M4-R1 Application Service & Session Boundary
→ M4-R2 Studio UI Vertical Slice
→ M4-R3 Usable MVP acceptance
→ M5 Renderer/DAW interoperability & quality expansion
→ M6 Product hardening / desktop packaging / release candidate
```

## Development discipline / 개발 규율

```text
Issue → Branch → Contracts → Application boundary → Tests
→ PR → exact-head CI → Evidence → Merge → State update
```

Repository-backed contracts and executable evidence remain authoritative over conversation or model memory. / 레포 기반 계약과 실행 근거는 계속해서 대화·모델 기억보다 우선합니다.
