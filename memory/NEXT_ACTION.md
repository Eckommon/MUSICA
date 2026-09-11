# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M4-R3 — USABLE MVP / REAL-BROWSER E2E ACCEPTANCE v0 / M4-R3 — 사용 가능한 MVP / 실제 브라우저 E2E 수용 v0**

M4-R2 is validated. The next task is no longer to prove that HTML, HTTP endpoints, or packaged assets exist. M4-R3 must prove that the merged Studio can be operated through an actual browser interaction path as a usable local product while preserving all canonical authority rules.

M4-R2는 검증 완료되었습니다. 다음 작업은 HTML, HTTP endpoint, packaged asset의 존재를 다시 증명하는 것이 아닙니다. M4-R3는 병합된 Studio가 실제 browser interaction 경로에서 로컬 제품으로 조작 가능하며 모든 공식 권한 규칙을 보존함을 증명해야 합니다.

## Product acceptance objective / 제품 수용 목표

A clean browser-driven workflow SHALL prove that a user can:

1. launch/open the local Studio,
2. create a project from natural-language intent,
3. hear accepted audio,
4. move through `Direct → Shape → Inspect → Code`,
5. create a semantic preview from visible controls,
6. observe `PREVIEW · NOT ACCEPTED`,
7. hear pending preview audio while canonical head remains unchanged,
8. inspect exact diff and HARD locks,
9. explicitly Accept the preview and observe revision advancement,
10. create and checkout a branch,
11. inspect accepted revision history,
12. export canonical project state,
13. inspect read-only Code/session JSON,
14. restart/reopen the Studio and recover the durable accepted project state.

실제 browser-driven workflow에서 위 전체 경로가 개발자 명령을 사용하지 않는 UI interaction으로 증명되어야 합니다.

## R3 evidence classes / R3 근거 등급

M4-R3 SHALL distinguish evidence classes instead of collapsing them:

```text
STATIC_UI_EVIDENCE          — packaged HTML/CSS/JS contract
HTTP_INTEGRATION_EVIDENCE   — same-origin API/media path
REAL_BROWSER_E2E_EVIDENCE   — actual browser automation interactions
HUMAN_USABILITY_EVIDENCE    — future optional human study; not required for R3 v0
```

R2 already validates the first two. R3 must add `REAL_BROWSER_E2E_EVIDENCE`.

R2는 앞의 두 등급을 이미 검증했습니다. R3는 `REAL_BROWSER_E2E_EVIDENCE`를 추가해야 합니다.

## Automation direction / 자동화 방향

Prefer **Playwright + Chromium** for R3 because it can exercise the real packaged browser surface, media element state, visible controls, DOM states, accessibility-oriented selectors and restart/reopen flows in CI.

R3에서는 **Playwright + Chromium**을 우선합니다. 실제 packaged browser surface, media element, visible control, DOM state, accessibility selector, restart/reopen flow를 CI에서 검증하기 적합하기 때문입니다.

The browser automation layer MUST remain test/evidence infrastructure. It must not become a runtime dependency of MUSICA Studio.

Browser automation은 test/evidence infrastructure로만 유지하며 MUSICA Studio runtime dependency가 되어서는 안 됩니다.

## Required browser E2E scenarios / 필수 Browser E2E 시나리오

### E2E-01 Create and audition / 생성·청취

```text
open /
→ enter project name + natural-language prompt
→ Generate
→ Accepted state appears
→ audio element receives accepted WAV source
→ project/head/integrity visible
```

### E2E-02 Shape → Preview authority / Shape → Preview 권한

```text
open Shape
→ change tension control
→ choose supported scope
→ Preview Changes
→ PREVIEW · NOT ACCEPTED visible
→ preview diff visible
→ HARD locks visible
→ preview audio available
→ displayed accepted head remains parent revision
```

### E2E-03 Explicit Accept / 명시적 승인

```text
open Inspect
→ click Accept
→ pending preview disappears
→ state badge becomes ACCEPTED
→ head revision changes to candidate revision
→ accepted audio remains available
```

### E2E-04 Branch/history/export / branch·history·export

```text
create branch
→ checkout branch
→ history visible
→ export
→ export result includes canonical path/hash/size
```

### E2E-05 Code view / Code 화면

```text
open Code
→ validated read-only session JSON visible
→ current branch/head match server-backed UI state
→ no raw mutation control exists
```

### E2E-06 Restart/reopen / 재시작·재열기

```text
stop first Studio server/session
→ start a fresh Studio service on same workspace
→ browser opens Studio
→ Open existing project
→ durable branch/head/integrity restored
→ accepted audio available
```

### E2E-07 Negative UI authority / UI 권한 부정 증명

- preview must never silently become accepted,
- branch/export actions must not bypass pending-preview conflicts,
- invalid project/session inputs must produce visible errors rather than hidden mutation,
- external network must remain unnecessary in fixture mode.

## R3 architecture / R3 아키텍처

```text
Playwright Chromium  [test/evidence only]
        ↓ visible browser actions
Browser Studio       [runtime UI]
        ↓ same-origin loopback
validated M4-R1 service
        ↓
M3/M1/M0 trusted core
        ↓
PREVIEW — non-canonical
        ↓ explicit Accept only
M2 Project Engine
```

## CI strategy / CI 전략

R3 SHOULD add a dedicated browser-E2E job rather than forcing Chromium installation into both existing Python matrix jobs.

Recommended split / 권장 분리:

```text
contracts-and-runtime (Python 3.11)
contracts-and-runtime (Python 3.12)
        +
browser-e2e (Python 3.12 + Chromium)
```

The existing Python matrix remains the core regression gate. Browser-specific dependencies live only in the dedicated E2E job.

기존 Python matrix는 core regression gate로 유지하고 browser 전용 dependency는 별도 E2E job에만 둡니다.

## R3 acceptance gate / R3 수용 게이트

M4-R3 may be promoted only when:

1. real Chromium E2E scenarios pass in CI,
2. M0→M4-R2 core regression remains green,
3. R3 canonical evidence records screenshots/DOM assertions/session evidence without leaking secrets,
4. browser automation proves Preview ≠ Accepted and explicit Accept is required,
5. restart/reopen durability is proven,
6. exact evidence-bearing PR head passes all required jobs,
7. that exact head alone is merged and promoted through state-only closure.

## Non-goals / 비목표

M4-R3 v0 does not require:

- human usability-study recruitment,
- pixel-perfect visual-design validation,
- production/mastering audio quality,
- waveform/piano-roll editing,
- desktop installer/signing,
- cloud accounts/collaboration,
- live OpenAI evidence,
- professional DAW/VST/sampler interoperability.

## Product sequence / 제품 순서

```text
M4-R1 Application Service                ✅ VALIDATED
→ M4-R2 Browser Studio UI                ✅ VALIDATED
→ M4-R3 Usable MVP / real-browser E2E    ← NOW
→ M5 Renderer/DAW interoperability & quality
→ M6 Product hardening / desktop packaging / release candidate
```

## Development discipline / 개발 규율

```text
Issue
→ branch from closure main
→ R3 acceptance contract
→ dedicated browser-E2E infrastructure
→ real Chromium scenarios
→ canonical R3 evidence
→ PR
→ exact-head core CI + browser-E2E CI
→ artifact inspection
→ merge
→ R3 closure
```

Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.
