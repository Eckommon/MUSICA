# M4-R3 Acceptance / Usable MVP Real-Browser E2E 수용 기준

**Status / 상태:** ACTIVE GATE / 활성 게이트

## Objective / 목표

M4-R3 SHALL prove that the validated MUSICA Browser Studio can be operated through an actual Chromium browser as a local usable workflow while preserving the same canonical `.musica` authority and Preview → explicit Accept boundary validated below the UI.

M4-R3는 검증된 MUSICA Browser Studio가 실제 Chromium browser를 통해 로컬 사용 흐름으로 조작 가능하며, UI 아래에서 검증된 동일한 공식 `.musica` 권한과 Preview → 명시적 Accept 경계를 보존함을 증명해야 합니다.

## Evidence classes / 근거 등급

```text
STATIC_UI_EVIDENCE          — M4-R2 validated
HTTP_INTEGRATION_EVIDENCE   — M4-R2 validated
REAL_BROWSER_E2E_EVIDENCE   — M4-R3 required
HUMAN_USABILITY_EVIDENCE    — not required for R3 v0
```

R3 SHALL NOT relabel static or direct HTTP tests as real-browser evidence.

R3는 정적 또는 직접 HTTP 테스트를 실제 browser evidence로 재표기해서는 안 됩니다.

## Acceptance criteria / 수용 기준

1. **Real Chromium / 실제 Chromium** — CI launches Playwright Chromium and navigates to the packaged Studio served by the loopback server.
2. **Visible create / 화면 생성** — browser fills visible project/prompt controls and creates an accepted project through the UI.
3. **Accepted audio surface / 승인 오디오 화면** — the audio element receives the accepted WAV source; browser-driven retrieval proves valid `audio/wav`/RIFF media.
4. **Progressive disclosure / 단계적 복잡성 노출** — Direct, Shape, Inspect and Code tabs are exercised through visible navigation.
5. **Visible semantic edit / 화면 의미 수정** — browser changes a semantic slider and requests Preview from the Shape surface.
6. **Preview authority / Preview 권한** — `PREVIEW · NOT ACCEPTED` is visible and the displayed/server-backed canonical head remains the parent revision.
7. **Preview media / Preview 미디어** — pending preview WAV is browser-accessible and valid while canonical head is unchanged.
8. **Inspect proof / 검사 증명** — exact diff entries and HARD locks are visible in Inspect.
9. **Conflict surface / 충돌 화면** — branch/checkout/export controls are disabled while preview is pending.
10. **Explicit Accept / 명시 승인** — browser clicks Accept; pending preview clears and head advances to the candidate revision.
11. **Branch/history / branch·history** — browser creates+checks out a branch and sees accepted history.
12. **Export / 내보내기** — browser invokes canonical export and receives visible path/hash/size feedback.
13. **Code read-only / Code 읽기 전용** — browser opens Code, sees server-backed session JSON, and no raw canonical-state mutation control exists.
14. **Restart/reopen / 재시작·재열기** — first server is stopped; a fresh StudioService/server on the same workspace reopens the project through visible browser controls and restores durable branch/head/integrity/media.
15. **No external runtime dependency / 외부 런타임 의존 없음** — fixture mode requires no external network/API; browser console/page errors are captured as evidence.
16. **Evidence capture / 근거 캡처** — canonical R3 artifact contains browser screenshots plus structured proof/manifest files with hashes.
17. **Dependency isolation / 의존성 격리** — Playwright is test/evidence-only; MUSICA runtime dependencies remain unchanged.
18. **Core regression / 코어 회귀** — existing Python 3.11/3.12 M0→M4-R2 regression/evidence chain remains green.
19. **Dedicated browser gate / 별도 browser gate** — a Python 3.12 + Chromium CI job independently gates real-browser acceptance.
20. **Exact-head promotion / exact-head 승격** — only an evidence-bearing PR exact head that passes core + browser gates may be merged and later promoted.

## Canonical browser workflow / 공식 Browser 흐름

```text
Chromium → /
  ↓ visible controls
Create from natural-language intent
  ↓
ACCEPTED + WAV
  ↓
Shape → semantic slider → Preview Changes
  ↓
PREVIEW · NOT ACCEPTED
  ↓
Inspect diff + HARD locks
  ↓
explicit Accept
  ↓
new accepted revision
  ↓
branch + history + export
  ↓
Code read-only JSON
  ↓
server restart
  ↓
Open existing project through browser
  ↓
durable branch/head/integrity/audio restored
```

## Authority invariants / 권한 불변식

```text
Browser DOM ≠ canonical authority
Browser JavaScript state ≠ canonical authority
Preview audio ≠ accepted state
AI proposal ≠ accepted state
Only explicit Accept → M2 commit → accepted revision
```

## Claim boundary / 주장 경계

M4-R3 v0 validates **automated real-browser operability**, not human-subject usability research. It also does not validate production/mastering audio quality, waveform/piano-roll editing, desktop installer/signing, cloud collaboration, remote serving, live OpenAI execution, or professional DAW/VST/sampler interoperability.

M4-R3 v0는 **자동화된 실제 browser 조작성**을 검증하며 사람 대상 usability research를 검증하지 않습니다. 상용 음질, waveform/piano-roll, desktop packaging, cloud collaboration, remote serving, OpenAI live 실행, DAW/VST 상호운용도 범위 밖입니다.
