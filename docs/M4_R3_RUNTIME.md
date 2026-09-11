# M4-R3 Runtime / Real-Browser E2E 검증 런타임

## 1. Role / 역할

M4-R3 adds a browser-automation validation layer above the already validated M4-R2 Studio. It does not add a second product runtime or a second music-state store.

M4-R3는 이미 검증된 M4-R2 Studio 위에 browser automation 검증 계층을 추가합니다. 별도 제품 runtime이나 별도 음악 상태 저장소를 추가하지 않습니다.

## 2. Architecture / 아키텍처

```text
Playwright Chromium
        │ test/evidence only
        ▼
Browser Studio HTML/CSS/JS
        │ same-origin loopback
        ▼
M4-R1 Studio HTTP/Application Service
        ▼
M3/M1/M0 trusted music core
        ▼
PREVIEW — non-canonical
        │ explicit Accept only
        ▼
M2 Project Engine
        ▼
Accepted .musica state
```

## 3. Dependency boundary / 의존성 경계

Playwright belongs only to the optional `e2e` dependency group and dedicated CI job. Importing or running normal MUSICA does not require Playwright or Chromium.

Playwright는 선택적 `e2e` dependency group과 전용 CI job에만 속합니다. 일반 MUSICA import·실행에는 Playwright나 Chromium이 필요하지 않습니다.

## 4. Evidence runner / 근거 runner

`musica.m4_r3_e2e` starts a loopback Studio server, launches Chromium, drives visible controls, captures screenshots and structured assertions, restarts the server on the same workspace, reopens the durable project, and writes a canonical evidence manifest.

`musica.m4_r3_e2e`는 loopback Studio server를 시작하고 Chromium을 실행해 visible control을 조작하며 screenshot과 구조화 assertion을 기록합니다. 이후 동일 workspace에서 server를 재시작하고 durable project를 다시 열어 공식 evidence manifest를 생성합니다.

## 5. Screenshot policy / Screenshot 정책

Screenshots are local Studio evidence only. The canonical fixture workflow uses no account credentials, secrets, personal files or live-provider data.

Screenshot은 local Studio evidence 전용입니다. 공식 fixture workflow는 계정 credential, secret, 개인 파일, live-provider 데이터를 사용하지 않습니다.

Expected captures / 예상 캡처:

```text
01-created-accepted.png
02-preview-not-accepted.png
03-accepted-revision.png
04-branch-history-export.png
05-code-view.png
06-reopened-after-restart.png
```

## 6. Media proof / 미디어 증명

Automated evidence cannot prove human auditory perception. R3 therefore proves that Chromium receives a playable media source, reaches a loaded media state where supported, and browser-managed retrieval returns a valid `audio/wav` RIFF payload.

자동화 근거는 인간이 실제로 들었다는 사실을 증명할 수 없습니다. 따라서 R3는 Chromium audio element에 playable source가 연결되고 지원되는 loaded media state에 도달하며 browser-managed retrieval이 유효한 `audio/wav` RIFF payload를 반환함을 증명합니다.

## 7. Restart semantics / 재시작 의미

The first application service/session is intentionally ephemeral. Restart proof shuts down the first HTTP server, creates a fresh `StudioService` on the same workspace, opens a new browser page, and reopens the project through the visible Open form. Durable branch/head state must come from the `.musica` bundle, not serialized browser/session memory.

첫 application service/session은 의도적으로 일시적입니다. restart proof는 첫 HTTP server를 종료하고 동일 workspace에 새로운 `StudioService`를 생성한 뒤 새 browser page에서 visible Open form을 통해 project를 재개합니다. Durable branch/head는 browser/session memory가 아니라 `.musica` bundle에서 복원되어야 합니다.

## 8. CI separation / CI 분리

The existing Python 3.11/3.12 matrix remains authoritative for core regression. A separate Python 3.12 browser job installs Chromium and runs only the R3 E2E scenario. Browser tooling therefore cannot silently become a normal runtime prerequisite.

기존 Python 3.11/3.12 matrix는 core regression의 공식 gate로 유지됩니다. 별도 Python 3.12 browser job만 Chromium을 설치하고 R3 E2E를 실행합니다.

## 9. Known boundary / 알려진 경계

M4-R3 does not attempt pixel-perfect visual regression, cross-browser compatibility, human usability scoring, accessibility certification, professional audio QA, desktop packaging, cloud deployment, live OpenAI calls, or DAW interoperability.
