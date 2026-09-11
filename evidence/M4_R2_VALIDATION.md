# M4-R2 Validation Evidence / Browser Studio UI 검증 근거

**Milestone / 마일스톤:** M4-R2 — Browser Studio UI Vertical Slice v0  
**Evidence status / 근거 상태:** BRANCH VALIDATION PASSED; PR exact-head validation pending / branch 검증 통과, PR exact-head 검증 대기  
**Evidence class / 근거 등급:** LOCAL BROWSER STUDIO EVIDENCE / 로컬 Browser Studio 근거

## 1. Scope / 범위

M4-R2 validates that MUSICA now has a real browser-deliverable, local-first Studio surface connected to the validated M4-R1 service. The Browser UI implements progressive disclosure `Direct → Shape → Inspect → Code` while preserving the canonical Preview → explicit Accept authority boundary.

M4-R2는 검증된 M4-R1 service에 연결된 실제 browser-deliverable local-first Studio 화면이 존재함을 검증합니다. Browser UI는 `Direct → Shape → Inspect → Code` 단계적 복잡성 노출을 구현하면서 Preview → 명시적 Accept 공식 권한 경계를 유지합니다.

## 2. Branch validation identity / Branch 검증 식별자

- branch: `m4-r2-browser-studio-ui-v0`
- validated branch head: `c6600263a4abaebd20e3f905a0dac730bffa0721`
- GitHub Actions run: `34550942907`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- M0→M4-R1 regression/evidence generation: **SUCCESS**
- M4-R2 Browser Studio evidence generation/upload: **SUCCESS**

## 3. Canonical artifact / 공식 artifact

- artifact: `musica-m4-r2-browser-studio`
- artifact ID: `10180808523`
- artifact digest: `sha256:05c428a5a5e3d2fa0620148d02a14dfbfed459e721122cf963765fb748cee7e2`
- inspected file count: **46**
- external network used: **NO**
- live OpenAI call performed: **NO**
- telemetry enabled: **NO**
- third-party CDN/remote asset dependency: **NO**

## 4. Browser surface proof / Browser 화면 증명

The canonical artifact contains the exact packaged UI assets served by MUSICA:

```text
browser-assets/index.html
browser-assets/app.css
browser-assets/app.js
```

HTTP proof:

```text
GET /                 → 200 text/html
GET /assets/app.css   → 200 text/css
GET /assets/app.js    → 200 text/javascript
```

The inspected UI records all four progressive-disclosure surfaces:

```text
Direct
Shape
Inspect
Code
```

The static source contains no `http://` or `https://` runtime asset dependency and no telemetry/CDN integration.

정적 UI source는 `http://`/`https://` 외부 런타임 asset 의존성과 telemetry/CDN 통합을 포함하지 않습니다.

## 5. Same-origin security proof / 동일-origin 보안 증명

Canonical UI responses include:

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

The validated M4-R1 loopback-only bind policy remains in force.

검증된 M4-R1 loopback-only bind 정책은 그대로 유지됩니다.

## 6. Browser-visible workflow proof / Browser-visible workflow 증명

The canonical HTTP workflow performed:

```text
Browser-visible create request
  ↓
accepted root revision rev-001
  ↓
accepted WAV retrieved
  ↓
semantic tension preview
  ↓
assert head still rev-001
  ↓
pending preview WAV retrieved
  ↓
explicit Accept
  ↓
accepted revision rev-studio-d609cb248b8ab5b3cd1133e3
  ↓
create + checkout browser-variation branch
  ↓
history
  ↓
canonical export
  ↓
final session integrity PASS
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

Canonical export:

```text
exports/browser-studio-proof.musica.zip
sha256:a4ce81b7b83ad734f39a69622ff16ae7466fb093d6c4720a2ead1459fd690dfc
```

## 7. Product surface / 제품 화면

The Browser Studio exposes:

### Direct / 간편 디렉팅
- natural-language project creation,
- explicit provider selection with offline fixture default,
- duration/use-case/style essentials,
- accepted/preview audio player,
- natural-language refinement preview.

### Shape / 의미·구조 편집
- six semantic controls: energy, tension, density, motion, brightness, warmth,
- whole/final/selected-section scope,
- section timeline,
- HARD-lock summary,
- explicit Preview Changes action.

### Inspect / 전문 검사
- Accepted vs `PREVIEW · NOT ACCEPTED` state,
- exact change diff returned by preview,
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

M4-R2 packages `musica.studio_web` assets and adds the local launcher:

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

The server host still passes through M4-R1 loopback validation.

## 9. Authority verdict / 권한 판정

**PASS:** The browser did not become canonical authority.

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

Audio playback of a pending preview did not advance the branch head. Only the explicit Accept operation did.

pending preview 오디오를 청취해도 branch head는 전진하지 않았고 명시적 Accept 작업만 head를 전진시켰습니다.

## 10. Claim boundary / 주장 경계

This evidence validates a **packaged Browser Studio surface and same-origin HTTP integration**. It does **not** validate:

- Playwright/Selenium browser automation,
- complete browser restart/session recovery,
- human usability-study evidence,
- production/mastering audio quality,
- waveform/piano-roll/note-level professional UI,
- simultaneous multi-axis preview transaction,
- desktop installer/signing,
- cloud collaboration,
- remote HTTP serving,
- live OpenAI execution,
- DAW/VST/sampler interoperability.

이 근거는 **패키징된 Browser Studio 화면과 same-origin HTTP 통합**을 검증합니다. 전체 browser automation, human usability study, 전문 음질/UI, desktop packaging, cloud collaboration, live OpenAI, DAW/VST 상호운용은 검증하지 않습니다.

## 11. Promotion rule / 승격 규칙

M4-R2 SHALL NOT be marked `VALIDATED` from this branch run alone. This evidence-bearing PR head must pass Python 3.11/3.12 plus the complete M0→M4-R2 evidence chain. Only that exact head may be merged and promoted through a state-only closure.

이 branch run만으로 M4-R2를 `VALIDATED`로 표시하지 않습니다. 본 durable evidence가 포함된 PR exact head가 Python 3.11/3.12와 M0→M4-R2 전체 evidence chain을 통과해야 하며, 그 exact head만 병합·state-only closure로 승격할 수 있습니다.
