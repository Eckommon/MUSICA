# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M4-R2 — BROWSER STUDIO UI VERTICAL SLICE v0 / M4-R2 — Browser Studio UI Vertical Slice v0**

M4-R1 is validated. The next task is to turn the validated local application service into an actual user-facing Studio without creating a second/shadow music state.

M4-R1은 검증 완료되었습니다. 다음 작업은 별도의 shadow music state를 만들지 않고 검증된 local application service를 실제 사용자-facing Studio로 전환하는 것입니다.

## Product principle / 제품 원칙

M4-R2 MUST operationalize the accepted product promise:

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**
>
> **자연어로 지시할 만큼 쉽고, 전문 음악 시스템처럼 세밀하게 편집할 만큼 정밀해야 한다.**

The UI SHALL use progressive disclosure over one canonical M4-R1/M2 project state:

하나의 공식 M4-R1/M2 project state 위에 단계적 복잡성 노출을 적용합니다.

```text
Direct  → natural-language creation and refinement
Shape   → six semantic controls + sections
Inspect → locks, exact change preview, versions/history
Code    → read-only validated JSON/evidence surface
```

## R2 architecture / R2 아키텍처

```text
Browser UI (static HTML/CSS/JS)
        ↓ localhost only
validated M4-R1 HTTP bridge
        ↓
StudioApplication / StudioService
        ↓
M3 / M1 / M0 trusted core
        ↓
PREVIEW — non-canonical
        ↓ explicit Accept only
M2 Project Engine
```

R2 SHOULD remain dependency-light. Prefer static HTML/CSS/JavaScript served by the existing Python loopback server before introducing a frontend framework. A framework may be adopted later only if it materially improves the validated interaction model.

R2는 dependency-light를 유지합니다. frontend framework를 먼저 도입하지 말고 기존 Python loopback server가 제공하는 static HTML/CSS/JavaScript를 우선합니다. interaction model이 검증된 뒤 실질적 이점이 있을 때만 framework 도입을 고려합니다.

## Required user workflow / 필수 사용자 workflow

A non-developer user must be able to perform through visible controls:

1. create a new project from natural-language intent,
2. open an existing `.musica` project by safe workspace project name/path,
3. play/pause the current accepted WAV,
4. see project title/branch/head/integrity status,
5. see sections and their time boundaries,
6. adjust all six implemented semantic axes,
7. select global or bounded section scope where supported,
8. request an edit preview without changing canonical state,
9. hear the pending preview,
10. inspect what changed and which HARD locks remain protected,
11. explicitly Accept or Discard the preview,
12. create/switch branches when no preview is pending,
13. inspect accepted revision history,
14. export the canonical `.musica` project,
15. access/download current MIDI/WAV through local endpoints,
16. inspect raw validated session/metadata in Code view without unsafe direct mutation.

비개발 사용자가 visible control만으로 프로젝트 생성·열기 → 청취 → 6축 조정 → preview → 변경/lock 확인 → Accept/Discard → branch/history → export를 수행할 수 있어야 합니다.

## UX layout / UX 레이아웃

### Direct / 간편 디렉팅

- primary natural-language prompt,
- provider indicator (`Offline Fixture` by default; `OpenAI` only when explicitly selected/configured),
- project name and duration/use-case essentials,
- Generate / Refine action,
- accepted audio player.

### Shape / 구조·의미 편집

- six semantic sliders: `energy`, `tension`, `density`, `motion`, `brightness`, `warmth`,
- section strip/timeline summary,
- axis value labels and keyboard-accessible controls,
- Preview Changes action rather than implicit commit.

### Inspect / 전문 검사

- accepted vs pending state badge,
- HARD-lock list,
- preview diff summary/count,
- branch selector and history,
- exact revision IDs and integrity state,
- Accept / Discard separated from ordinary edit controls.

### Code / 코드·근거

- read-only JSON session view,
- current accepted revision metadata,
- evidence/authority explanation,
- no direct raw mutation in R2.

## Non-negotiable safety/authority rules / 변경 불가 규칙

1. Browser state is a view cache, never canonical authority. / browser state는 view cache이며 공식 권위가 아닙니다.
2. Every mutating action must go through M4-R1 endpoints. / 모든 변경은 M4-R1 endpoint를 통과합니다.
3. Preview must be visually distinct from Accepted. / Preview와 Accepted를 시각적으로 명확히 구분합니다.
4. Audio preview does not imply acceptance. / preview 청취는 승인을 의미하지 않습니다.
5. Accept and Discard operate only on the server-reported pending preview. / Accept·Discard는 server가 보고한 pending preview에만 적용합니다.
6. Branch/history/export controls are disabled or fail visibly while R1 reports a preview conflict. / preview 충돌 상태에서는 branch/history/export 관련 불가 작업을 명확히 처리합니다.
7. OpenAI is never an implicit network requirement. / OpenAI는 암묵적 network 필수가 아닙니다.
8. UI must not expose arbitrary filesystem paths outside the configured workspace. / workspace 밖 임의 파일 경로를 노출하지 않습니다.
9. No telemetry or third-party frontend CDN dependency in R2 canonical evidence. / R2 공식 근거에는 telemetry·third-party CDN 의존성을 두지 않습니다.
10. Bilingual product copy follows Korean/English repository principle where practical. / 제품 copy도 가능한 범위에서 한영문 병기를 적용합니다.

## Implementation sequence / 구현 순서

```text
Issue + branch
→ UI information architecture
→ static asset serving from loopback HTTP
→ Direct project create/open flow
→ accepted/preview audio player switching
→ Shape six-axis controls
→ preview diff + lock inspection
→ Accept/Discard
→ branch/history/export
→ Code read-only state view
→ accessibility/responsive states
→ UI contract/static tests
→ loopback HTTP integration tests
→ canonical M4-R2 evidence
→ PR + exact-head CI
→ merge
→ M4-R2 closure
→ M4-R3 browser E2E usable-MVP acceptance
```

## R2 acceptance boundary / R2 수용 경계

R2 is accepted when the repository contains and CI verifies a real browser-deliverable Studio surface connected to M4-R1, with all primary controls present and HTTP integration proven. R2 does not yet claim a human usability study or full browser-automation E2E; those belong to M4-R3.

R2는 M4-R1에 연결된 실제 browser-deliverable Studio 화면과 핵심 control, HTTP integration이 레포와 CI로 검증되면 수용합니다. 실제 사람 대상 usability study나 전체 browser automation E2E는 M4-R3에서 검증합니다.

## Product sequence / 제품 순서

```text
M4-R1 Application Service                 ✅ VALIDATED
→ M4-R2 Browser Studio UI                 ← NOW
→ M4-R3 Usable MVP / browser E2E
→ M5 Renderer/DAW interoperability & quality
→ M6 hardening / desktop packaging / release candidate
```

Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.
