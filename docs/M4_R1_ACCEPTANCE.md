# M4-R1 Acceptance / Studio Application Service 수용 기준

**Status / 상태:** ACTIVE GATE / 활성 게이트

## Objective / 목표

M4-R1 SHALL expose validated MUSICA M0→M3 capabilities through a local-first application/session boundary without allowing UI convenience to bypass AI authority, preview/accept, lock, project-integrity, or workspace-security rules.

M4-R1은 검증된 M0→M3 기능을 local-first 애플리케이션·세션 경계로 노출하되 UI 편의성이 AI 권한, preview/accept, lock, project integrity, workspace 보안 규칙을 우회하지 못하게 해야 합니다.

## Acceptance criteria / 수용 기준

1. **Workspace confinement / workspace 제한** — every project, cache, preview and export path stays inside the configured Studio workspace; traversal and symlink escape fail closed.
2. **Create/open / 생성·열기** — a user-facing service operation can create and reopen `.musica` projects without Git knowledge.
3. **Natural-language create / 자연어 생성** — create flows through M3 Director Request/Proposal authority and M1 Blueprint generation; fixture/offline provider is the default so the app never requires network to start.
4. **Optional OpenAI / 선택적 OpenAI** — `openai` provider mode is wired, but missing runtime credentials fail before project creation and do not create a partial project.
5. **Inspection / 검사** — current branch/head, sections, six semantic values, HARD locks, branches, media availability and pending preview status are machine-readable.
6. **Non-canonical preview / 비공식 preview** — semantic or Director edits render an audible candidate but MUST NOT advance the current branch ref.
7. **Explicit acceptance / 명시 승인** — only `accept_preview` may commit the pending candidate and bind its MIDI/WAV to that accepted revision.
8. **Discard / 폐기** — discard deletes pending preview state/cache and preserves the branch head exactly.
9. **Preview conflict policy / preview 충돌 규칙** — branch creation, checkout and canonical export are blocked while a preview is pending.
10. **Branch/history / branch·이력** — create/checkout branches and inspect accepted revision records through the application boundary.
11. **Deterministic export / 결정론 export** — unchanged canonical project state produces the same `.musica.zip` bytes/hash.
12. **Media / 미디어** — current accepted or pending preview MIDI/WAV may be retrieved through the service and local HTTP bridge.
13. **Local HTTP / 로컬 HTTP** — bridge defaults to loopback and refuses non-loopback binding in M4-R1.
14. **Machine contracts / 기계 계약** — Studio session, preview, response and error objects validate against versioned JSON Schemas.
15. **Restart/open proof / 재개 증명** — a second service instance can reopen the exact durable project and read its media.
16. **Regression / 회귀** — M0→M3 tests/evidence remain green on Python 3.11 and 3.12.
17. **Canonical evidence / 공식 근거** — Python 3.12 CI generates/uploads `musica-m4-r1-studio-service` evidence.

## Canonical proof / 공식 증명

```text
local workspace
  ↓
Studio create project
  ↓
M3 Director create
  ↓
M1 Blueprint
  ↓
M2 .musica project + accepted root MIDI/WAV
  ↓
Studio semantic edit
  ↓
PREVIEW candidate + audible MIDI/WAV
  ↓
assert branch ref unchanged
  ↓
explicit Accept
  ↓
M2 accepted revision + bound artifacts
  ↓
create/checkout branch
  ↓
preview another edit → Discard
  ↓
assert branch ref unchanged
  ↓
history + deterministic export
  ↓
close/reopen with a new Studio service instance
  ↓
local HTTP inspect + WAV retrieval
```

A path traversal attempt MUST be rejected as an explicit negative proof.

경로 탈출 시도는 명시적인 부정 증명으로 차단되어야 합니다.

## Claim boundary / 주장 경계

M4-R1 is an **application-service boundary**, not the final polished Studio UI. It does not validate production mastering, cloud collaboration, desktop packaging, arbitrary remote HTTP serving, multi-user security, or live OpenAI execution.

M4-R1은 **애플리케이션 서비스 경계**이며 최종 Studio UI가 아닙니다. 상용 마스터링, cloud collaboration, desktop packaging, 임의 원격 HTTP 제공, 다중 사용자 보안, 실제 OpenAI live 실행을 검증하지 않습니다.
