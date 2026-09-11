# M4-R2 Runtime / Browser Studio UI 런타임

## 1. Role / 역할

M4-R2 is a thin browser client over the validated M4-R1 local application service. It introduces a usable visual surface, not a second music engine or state database.

M4-R2는 검증된 M4-R1 local application service 위의 얇은 browser client입니다. 사용 가능한 시각적 화면을 추가하지만 두 번째 음악 엔진이나 상태 데이터베이스를 만들지 않습니다.

## 2. Runtime architecture / 런타임 아키텍처

```text
musica-studio
  ↓
StudioService(workspace)
  ↓
loopback ThreadingHTTPServer
  ├─ /                  → packaged index.html
  ├─ /assets/app.css    → packaged CSS
  ├─ /assets/app.js     → packaged JS
  ├─ /v0/...            → validated M4-R1 JSON API
  └─ /v0/.../media/...  → local WAV/MIDI
```

All UI assets and API/media requests are same-origin. Canonical R2 contains no remote script, stylesheet, font, image, telemetry or CDN dependency.

모든 UI asset과 API/media 요청은 same-origin입니다. 공식 R2는 remote script, stylesheet, font, image, telemetry, CDN 의존성을 포함하지 않습니다.

## 3. Progressive disclosure / 단계적 복잡성 노출

The same M4-R1 session is rendered at four depths:

### Direct / 간편 디렉팅
- new/open project,
- natural-language musical intent,
- explicit provider choice,
- duration/use case/style essentials,
- accepted or preview audio player,
- natural-language refinement preview.

### Shape / 의미·구조 편집
- six semantic sliders (`energy`, `tension`, `density`, `motion`, `brightness`, `warmth`),
- whole/final/section scope,
- section timeline,
- HARD-lock summary,
- explicit Preview action.

R2 intentionally previews one selected semantic axis per action because the validated M4-R1 service accepts one semantic control at a time. Multi-axis batch preview must be introduced later through an explicit service contract rather than simulated as browser-only state.

R2는 검증된 M4-R1 service가 한 번에 하나의 semantic control을 받기 때문에 한 action에 선택된 한 축을 preview합니다. 여러 축 동시 preview는 browser-only 상태로 흉내 내지 않고 향후 명시적인 service 계약으로 도입해야 합니다.

### Inspect / 전문 검사
- Accepted vs Preview state,
- preview ID/parent/diff count,
- exact diff returned from the preview operation,
- HARD locks,
- branch/current head/integrity,
- accepted revision history,
- explicit Accept / Discard,
- branch and export operations.

### Code / 코드·근거
- read-only current Studio session JSON,
- canonical authority explanation,
- copy convenience only,
- no direct raw-state mutation.

## 4. Browser state rule / Browser 상태 규칙

The JavaScript keeps only view/session convenience data such as current `session_id`, last preview response for display, active tab and selected semantic axis. It does not write `.musica` files or synthesize accepted revisions.

JavaScript는 현재 `session_id`, 표시용 최근 preview 응답, 활성 tab, 선택 semantic axis 같은 view/session 편의 상태만 보유합니다. `.musica` 파일을 쓰거나 승인 리비전을 생성하지 않습니다.

A page refresh may lose transient UI-only detail such as a locally retained exact diff while the server session still reports the pending preview descriptor. This is acceptable in R2; M4-R3 or later may add an explicit read-only pending-preview detail endpoint if browser restart continuity becomes an MVP requirement.

페이지 새로고침 시 server session의 pending preview descriptor는 남아 있어도 브라우저에만 있던 exact diff 표시 정보는 사라질 수 있습니다. 이는 R2 경계에서 허용되며, browser restart continuity가 MVP 요구가 되면 M4-R3 이후 명시적 read-only pending-preview detail endpoint를 추가합니다.

## 5. Audio behavior / 오디오 동작

The `<audio>` element always points to the M4-R1 media endpoint. M4-R1 decides whether that endpoint resolves to pending-preview WAV or current accepted WAV. Therefore the browser never selects files by filesystem path.

`<audio>` element는 항상 M4-R1 media endpoint를 사용합니다. 해당 endpoint가 pending-preview WAV인지 current accepted WAV인지 M4-R1이 결정하므로 browser는 filesystem path를 직접 선택하지 않습니다.

The UI labels the player `Preview audio / 미승인 미리듣기` whenever the server reports `pending_preview != null`.

## 6. Security headers / 보안 헤더

Static UI responses include:

- `Content-Security-Policy` with `default-src 'self'`, local-only script/style/connect/media and `frame-ancestors 'none'`,
- `Referrer-Policy: no-referrer`,
- `X-Frame-Options: DENY`,
- `X-Content-Type-Options: nosniff`,
- `Cross-Origin-Resource-Policy: same-origin`,
- `Cache-Control: no-store`.

The server remains loopback-only by the validated M4-R1 host policy.

## 7. Packaging and launcher / 패키징·실행기

`pyproject.toml` packages `musica.studio_web` HTML/CSS/JS assets and exposes:

```text
musica-studio
```

Default workspace:

```text
~/MUSICA-Workspace
```

Default local URL:

```text
http://127.0.0.1:8765/
```

The launcher opens the system browser unless `--no-browser` is supplied. Host validation still happens inside the loopback server factory.

## 8. Known R2 boundaries / 알려진 R2 경계

R2 does not claim:

- Playwright/Selenium-level browser automation,
- human usability-study evidence,
- persistent browser session recovery after process restart,
- simultaneous multi-axis preview transaction,
- drag/drop references,
- waveform/note/piano-roll editing,
- desktop shell/installer/signing,
- cloud account/sync/collaboration,
- production renderer/mastering quality,
- live OpenAI validation,
- DAW/VST/sampler hosting.

These boundaries prevent the existence of a browser page from being misrepresented as a finished production workstation.

이 경계는 browser page가 존재한다는 사실을 완성된 production workstation으로 과장하지 않기 위한 것입니다.
