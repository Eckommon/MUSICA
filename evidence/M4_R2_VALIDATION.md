# M4-R2 Validation Evidence / Browser Studio UI 검증 근거

**Milestone / 마일스톤:** M4-R2 — Browser Studio UI Vertical Slice v0  
**Evidence status / 근거 상태:** **VALIDATED / 검증 완료**  
**Evidence class / 근거 등급:** LOCAL BROWSER STUDIO EVIDENCE / 로컬 Browser Studio 근거

## 1. Scope / 범위

M4-R2 validates that MUSICA has a real browser-deliverable, local-first Studio surface connected to the validated M4-R1 service. The Browser UI implements progressive disclosure `Direct → Shape → Inspect → Code` while preserving the canonical Preview → explicit Accept authority boundary.

M4-R2는 검증된 M4-R1 service에 연결된 실제 browser-deliverable local-first Studio 화면이 존재함을 검증합니다. Browser UI는 `Direct → Shape → Inspect → Code` 단계적 복잡성 노출을 구현하면서 Preview → 명시적 Accept 공식 권한 경계를 유지합니다.

## 2. Final validation identity / 최종 검증 식별자

- implementation Issue: `#27`
- implementation PR: `#28`
- implementation branch: `m4-r2-browser-studio-ui-v0`
- exact final PR head: `6ee200606dbf99419fa67e9aec3ad4e288a8c66d`
- exact-head PR CI: `34551205586`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- M0→M4-R2 regression/evidence generation/upload: **SUCCESS**
- implementation merge: `16707e25bf78b4141c44da24bf8e82f375d7c465`

Only the exact evidence-bearing PR head above was accepted for merge.

위 evidence-bearing PR exact head만 병합 대상으로 수용되었습니다.

## 3. Final canonical artifact / 최종 공식 artifact

- artifact: `musica-m4-r2-browser-studio`
- final artifact ID: `10180901528`
- final artifact digest: `sha256:5c55c2f61ed53a1638479d1383cabb042d97be41599b36e04d65dea90cf57d5b`
- external network used: **NO**
- live OpenAI call performed: **NO**
- telemetry enabled: **NO**
- third-party CDN/remote asset dependency: **NO**

A prior branch-validation artifact also existed, but this exact-head PR artifact is the final promotion evidence.

이전 branch 검증 artifact도 존재하지만 본 exact-head PR artifact가 최종 승격 근거입니다.

## 4. Browser surface proof / Browser 화면 증명

The validated package contains the Studio UI assets served by MUSICA:

```text
browser-assets/index.html
browser-assets/app.css
browser-assets/app.js
```

Validated HTTP surface:

```text
GET /                 → 200 text/html
GET /assets/app.css   → 200 text/css
GET /assets/app.js    → 200 text/javascript
```

The UI exposes all four progressive-disclosure surfaces:

```text
Direct
Shape
Inspect
Code
```

Canonical source contains no third-party runtime asset dependency or telemetry integration.

공식 source에는 third-party runtime asset 의존성이나 telemetry 통합이 없습니다.

## 5. Same-origin security proof / 동일-origin 보안 증명

Validated UI responses include a strict local policy:

```text
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self';
  connect-src 'self';
  media-src 'self';
  img-src 'self' data:;
  font-src 'self';
  object-src 'none';
  base-uri 'none';
  frame-ancestors 'none';
  form-action 'self'

Referrer-Policy: no-referrer
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

The validated M4-R1 loopback-only bind policy remains authoritative.

검증된 M4-R1 loopback-only bind 정책은 계속 공식 규칙입니다.

## 6. Browser-visible workflow proof / Browser-visible workflow 증명

The canonical HTTP workflow exercised:

```text
Browser-visible create request
  ↓
accepted root revision rev-001
  ↓
accepted WAV retrieval
  ↓
semantic tension preview
  ↓
assert canonical head unchanged
  ↓
pending preview WAV retrieval
  ↓
explicit Accept
  ↓
accepted revision advances
  ↓
create + checkout browser-variation branch
  ↓
history
  ↓
canonical export
  ↓
final project integrity PASS
```

Observed proof values:

```text
preview_ref_unchanged_before_accept = true
preview_diff_count                  = 9
preview_audio_wav                   = true
accept_advanced_revision            = true
accepted_pending_preview_cleared    = true
branch_created_and_checked_out      = true
history_revision_count              = 2
final_integrity_status              = PASS
hard_lock_count                     = 3
six_semantic_axes_visible           = true
```

This validates the R2 authority invariant: listening to a preview does not promote it; only explicit Accept may advance canonical state.

이는 R2 권한 불변식을 검증합니다. preview 청취는 승격을 의미하지 않으며 명시적 Accept만 공식 상태를 전진시킬 수 있습니다.

## 7. Product surface / 제품 화면

### Direct / 간편 디렉팅
- natural-language project creation,
- explicit provider selection with offline fixture default,
- duration/use-case/style essentials,
- accepted/preview audio player,
- natural-language refinement preview.

### Shape / 의미·구조 편집
- six semantic controls: `energy`, `tension`, `density`, `motion`, `brightness`, `warmth`,
- whole/final/selected-section scope,
- section timeline,
- HARD-lock summary,
- explicit Preview Changes action.

### Inspect / 전문 검사
- Accepted vs `PREVIEW · NOT ACCEPTED` state,
- exact preview diff returned by preview,
- HARD locks,
- current branch/head/integrity,
- explicit Accept / Discard,
- branch create/checkout,
- accepted revision history,
- canonical export status.

### Code / 코드·근거
- read-only session JSON,
- explicit authority-chain explanation,
- no raw canonical-state mutation surface.

## 8. Launcher/package proof / 실행기·패키지 증명

M4-R2 packages `musica.studio_web` assets and provides:

```text
musica-studio
```

Default runtime intent:

```text
workspace = ~/MUSICA-Workspace
host      = 127.0.0.1
port      = 8765
browser   = auto-open unless --no-browser
```

The server host remains constrained by M4-R1 loopback validation.

## 9. Authority verdict / 권한 판정

**PASS — browser state did not become canonical authority.**

```text
Browser UI
  ↓ same-origin API
M4-R1 Studio Service
  ↓
M3/M1/M0 trusted core
  ↓
PREVIEW — non-canonical
  ↓ explicit Accept only
M2 Project Engine
  ↓
Accepted Revision
```

## 10. Claim boundary / 주장 경계

M4-R2 validates a **packaged Browser Studio surface and same-origin HTTP integration**. It does **not** validate:

- Playwright/Selenium real-browser automation,
- complete browser restart/session recovery through UI,
- human usability-study evidence,
- production/mastering audio quality,
- waveform/piano-roll/note-level professional UI,
- simultaneous multi-axis preview transaction,
- desktop installer/signing,
- cloud collaboration,
- remote HTTP serving,
- live OpenAI execution,
- DAW/VST/sampler interoperability.

이 근거는 **패키징된 Browser Studio 화면과 same-origin HTTP 통합**을 검증합니다. 실제 browser automation, 사람 대상 usability evidence, 전문 음질/UI, desktop packaging, cloud collaboration, live OpenAI, DAW/VST 상호운용은 검증하지 않습니다.

## 11. Promotion verdict / 승격 판정

The promotion rule is satisfied:

1. durable evidence existed before final PR validation,
2. exact PR head `6ee200606dbf99419fa67e9aec3ad4e288a8c66d` passed Python 3.11/3.12,
3. the complete M0→M4-R2 evidence chain regenerated/uploaded successfully,
4. final artifact identity is recorded above,
5. only that exact head was merged as `16707e25bf78b4141c44da24bf8e82f375d7c465`.

Therefore M4-R2 is **VALIDATED** within the bounded claim above.

따라서 M4-R2는 위 제한된 주장 범위에서 **VALIDATED / 검증 완료**입니다.
