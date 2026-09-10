# M4-R1 Runtime / Studio Application Service 런타임

## 1. Product role / 제품 역할

M4-R1 is the first application-facing boundary above the validated MUSICA core. It turns internal Python modules into stable local operations that M4-R2 can expose through a browser Studio.

M4-R1은 검증된 MUSICA core 위의 첫 애플리케이션-facing 경계입니다. 내부 Python 모듈을 안정적인 local operation으로 바꾸며 M4-R2 browser Studio가 이를 사용합니다.

## 2. Authority flow / 권한 흐름

```text
Studio client
  ↓
StudioApplication / StudioService
  ↓
M3 Director or direct validated Semantic Control
  ↓
M1 creative/semantic core
  ↓
M0 schema + HARD locks
  ↓
PREVIEW cache (non-canonical)
  ↓ explicit Accept only
M2 Project Engine commit
  ↓
Accepted revision + MIDI/WAV binding
```

The application service never treats a preview as an accepted revision.

애플리케이션 service는 preview를 승인 리비전으로 취급하지 않습니다.

## 3. Local-first workspace / Local-first workspace

A `StudioService` receives one workspace root. Project bundles, Studio cache, preview renders and exports must resolve underneath that root.

`StudioService`는 하나의 workspace root를 받으며 project bundle, cache, preview render, export는 모두 그 root 아래로 resolve되어야 합니다.

```text
workspace/
├── <project>.musica/
├── .studio/
│   └── sessions/<session>/renders/...
└── exports/
    └── <project>.musica.zip
```

Project/session/branch identifiers are restricted to bounded safe names. Existing symlinks are resolved before a path is accepted, so a project path that resolves outside the workspace fails closed.

## 4. Session model / 세션 모델

M4-R1 sessions are intentionally ephemeral application state. Durable musical state remains in the `.musica` Project Bundle.

M4-R1 session은 의도적으로 일시적인 애플리케이션 상태이며 영속 음악 상태는 `.musica` Project Bundle에 남습니다.

A session records:

- session ID,
- selected provider mode (`fixture` or `openai`),
- project slug/path,
- current durable project handle,
- at most one pending preview.

Restarting the application creates a new session and reopens the durable bundle; it does not depend on serialized session memory.

## 5. Create/open / 생성·열기

`create_project_session()` builds a Director create request, resolves it through the selected M3 provider, generates a validated M1 Blueprint, creates the M2 bundle, renders MIDI/WAV and binds those artifacts to the accepted root revision.

Default provider mode is `fixture`, keeping first-run/offline Studio behavior independent of network credentials. Selecting `openai` uses M3-R2; absence of `OPENAI_API_KEY` fails before a project is created.

`open_project_session()` verifies M2 project integrity before exposing it as a Studio session.

## 6. Preview model / Preview 모델

A semantic or Director edit produces a candidate Blueprint with a deterministic candidate revision ID derived from parent+command content. The candidate is rendered only into `.studio` cache.

```text
current accepted head R1
       ↓
edit command
       ↓
candidate R2 + diff
       ↓
preview.mid / preview.wav
       ↓
branch still points to R1
```

While a preview is pending, M4-R1 blocks branch creation/checkout and canonical export to avoid ambiguous user intent.

## 7. Accept/discard / 승인·폐기

`accept_preview()` verifies that the preview parent still equals the current branch head, commits the candidate through M2, binds the already-rendered MIDI/WAV to that accepted revision, verifies project integrity and clears preview cache.

`discard_preview()` removes preview cache/state and asserts the branch head did not move.

## 8. Inspection surface / 검사 표면

The machine-valid session view exposes:

- current branch/head revision,
- project identity and relative path,
- all branch heads,
- section IDs/labels/time bounds,
- six implemented semantic global values,
- current HARD-lock IDs/targets/modes,
- pending preview descriptor,
- current MIDI/WAV availability,
- project-integrity status.

This gives M4-R2 enough state to implement Direct, Shape and Inspect views without maintaining a separate shadow music state.

## 9. Dispatch API / Dispatch API

`StudioApplication.dispatch()` currently supports:

```text
POST /v0/projects/create
POST /v0/projects/open
GET  /v0/sessions/{id}
POST /v0/sessions/{id}/preview/semantic
POST /v0/sessions/{id}/preview/direct
POST /v0/sessions/{id}/preview/accept
POST /v0/sessions/{id}/preview/discard
POST /v0/sessions/{id}/branches
POST /v0/sessions/{id}/checkout
GET  /v0/sessions/{id}/history
POST /v0/sessions/{id}/export
POST /v0/sessions/{id}/close
```

Success values use `studio-response-v0`; application errors use `studio-error-v0`.

## 10. HTTP bridge / HTTP bridge

`studio_http.create_local_server()` maps the same application surface to a standard-library `ThreadingHTTPServer` and additionally exposes:

```text
GET /v0/health
GET /v0/sessions/{id}/media/audio.wav
GET /v0/sessions/{id}/media/preview.mid
```

M4-R1 refuses non-loopback hosts. This is a local UI bridge, not a remotely exposed production web service.

M4-R1은 loopback이 아닌 host binding을 거부합니다. 이는 local UI bridge이며 외부 공개용 production web service가 아닙니다.

## 11. Provider behavior / Provider 동작

`fixture` is the default and is suitable for deterministic/offline application testing. `openai` is an optional M3-R2 provider mode and retains all M3 authority rules. The Studio service never hands a `MusicaProject` object to either provider.

## 12. Known R1 boundary / 알려진 R1 경계

M4-R1 validates the application/session boundary, not final UX. It does not yet include:

- the M4-R2 browser UI,
- waveform/timeline editing,
- drag/drop files,
- cloud accounts or sync,
- desktop installer/shell,
- professional renderer/DAW integration,
- multi-user network security,
- production transaction recovery for rare filesystem failure between revision commit and artifact binding.

The last point is intentionally explicit: normal acceptance pre-renders artifacts and tests the commit+binding path, but a future hardening milestone should introduce a transactional acceptance journal if product requirements demand crash-atomic recovery.
