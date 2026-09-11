# M4-R2 Acceptance / Browser Studio UI 수용 기준

**Status / 상태:** ACTIVE GATE / 활성 게이트

## Objective / 목표

M4-R2 SHALL expose the validated M4-R1 application service through a real browser-deliverable local Studio while preserving one canonical `.musica` project state and the Preview → explicit Accept authority boundary.

M4-R2는 검증된 M4-R1 application service를 실제 browser-deliverable local Studio로 노출하되 하나의 공식 `.musica` project state와 Preview → 명시적 Accept 권한 경계를 유지해야 합니다.

## Acceptance criteria / 수용 기준

1. **Real browser surface / 실제 브라우저 화면** — packaged HTML/CSS/JavaScript is served from the loopback Studio server at `/`.
2. **No shadow authority / shadow 권한 금지** — browser state is display/cache only; every canonical mutation uses M4-R1 operations.
3. **Progressive disclosure / 단계적 복잡성 노출** — Direct, Shape, Inspect and Code surfaces are visible over the same session.
4. **Create/open / 생성·열기** — visible controls create and open safe workspace projects.
5. **Direct / 간편 디렉팅** — natural-language create and Director refinement controls are wired to M4-R1/M3.
6. **Audition / 청취** — the current accepted or pending-preview WAV is playable through the same-origin local media endpoint; MIDI is locally accessible.
7. **Shape / 의미 편집** — all six implemented semantic axes are visible and editable, with whole/final/selected-section scope.
8. **Preview separation / Preview 분리** — UI visibly distinguishes `PREVIEW · NOT ACCEPTED` from `ACCEPTED`; generating/listening to preview does not imply acceptance.
9. **Inspect / 검사** — exact preview diff, HARD locks, branch/head/integrity and accepted history are visible.
10. **Accept/Discard / 승인·폐기** — explicit visible controls invoke only server-reported pending-preview acceptance/discard paths.
11. **Branches / 브랜치** — create and checkout controls are available and conflict-disabled while a preview is pending.
12. **Export / 내보내기** — canonical project export is available through the validated service and reports path/hash/size.
13. **Code / 코드·근거** — read-only validated session JSON is visible; direct unsafe JSON mutation is not offered.
14. **Local-first / 로컬 우선** — fixture/offline provider is default; OpenAI is opt-in and no cloud account is required.
15. **No third-party runtime dependency / 외부 런타임 의존 금지** — canonical UI uses no third-party CDN, telemetry, remote font, remote script or image asset.
16. **Same-origin security / 동일-origin 보안** — strict CSP limits script/style/connect/media to local self and prevents framing/object embedding.
17. **Package/launcher / 패키징·실행 진입점** — static assets are included in the Python package and `musica-studio` launches the local Studio.
18. **Responsive/accessibility basics / 반응형·접근성 기본** — semantic labels, keyboard-focusable controls, status live region, reduced-motion handling and responsive layouts are present.
19. **HTTP integration proof / HTTP 통합 증명** — automated tests exercise static delivery plus create → preview → audio → Accept → history → export through HTTP.
20. **Regression / 회귀** — M0→M4-R1 regressions remain green on Python 3.11/3.12.
21. **Canonical evidence / 공식 근거** — Python 3.12 CI generates/uploads `musica-m4-r2-browser-studio` evidence.

## Canonical product loop / 공식 제품 루프

```text
Open localhost Studio
  ↓
Direct: describe or open project
  ↓
Accepted audio + project status
  ↓
Shape: adjust one semantic axis and scope
  ↓
Preview Changes
  ↓
PREVIEW · NOT ACCEPTED + preview audio
  ↓
Inspect: exact diff + HARD locks
  ↓
Discard OR explicit Accept
  ↓
Accepted revision
  ↓
Branches / History / Export
  ↓
Code: read-only canonical session state
```

## Authority invariants / 권한 불변식

```text
Browser view state ≠ canonical state
AI output ≠ accepted state
Preview audio ≠ accepted state
Only M4-R1 explicit Accept → M2 commit → accepted revision
```

## Evidence boundary / 근거 경계

M4-R2 validates a **browser-deliverable UI and same-origin HTTP integration**, not yet full browser automation or a human usability study. Those are M4-R3 Usable MVP acceptance concerns.

M4-R2는 **browser-deliverable UI와 same-origin HTTP 통합**을 검증합니다. 전체 브라우저 자동화 또는 사람 대상 usability 검증은 M4-R3 Usable MVP 수용 범위입니다.

M4-R2 also does not validate production mastering, desktop installer/signing, cloud collaboration, live OpenAI execution, remote HTTP serving, or professional DAW/VST/sampler interoperability.
