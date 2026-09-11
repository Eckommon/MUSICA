# M4-R3 Validation Evidence / Usable MVP Real-Browser E2E 검증 근거

**Milestone / 마일스톤:** M4-R3 — Usable MVP / Real-Browser E2E Acceptance v0  
**Evidence status / 근거 상태:** **VALIDATED — EXACT-HEAD REAL_BROWSER_E2E_EVIDENCE / 검증 완료**  
**Evidence class / 근거 등급:** `REAL_BROWSER_E2E_EVIDENCE`

## 1. Verdict / 판정

**PASS — M4-R3 is validated within its bounded claim. / PASS — M4-R3는 제한된 주장 범위에서 검증 완료되었습니다.**

MUSICA Studio was exercised through an actual Playwright Chromium browser against the packaged local application. The evidence proves browser-driven create, audition, progressive disclosure, semantic Preview, HARD-lock inspection, explicit Accept, branch/history/export, read-only Code inspection, and service restart/reopen while preserving the canonical `.musica` authority model.

MUSICA Studio는 실제 Playwright Chromium browser에서 packaged local application을 대상으로 검증되었습니다. Browser 기반 생성·청취·단계별 UI·semantic Preview·HARD lock 검사·명시적 Accept·branch/history/export·read-only Code·service restart/reopen이 공식 `.musica` 권한 모델을 보존한 상태에서 동작함을 증명했습니다.

This evidence validates **automated real-browser operability**, not human-subject usability or production audio quality.

## 2. Implementation identity / 구현 식별자

- implementation Issue: `#31` — **CLOSED / completed**
- implementation PR: `#32` — **MERGED**
- validated evidence-bearing PR head: `0bfc3e7475c20e4891c629ee736237bbc72a958c`
- exact-head PR CI: `34553248432`
- implementation merge commit: `2c64fe69a5472d5aa7eef5d077e5c30fdfe704d2`

### Exact-head gates / exact-head 게이트

| Gate | Result |
|---|---|
| Python 3.11 core regression | **SUCCESS** |
| Python 3.12 core + M0→M4-R2 evidence chain | **SUCCESS** |
| Playwright Chromium `browser-e2e` | **SUCCESS** |
| M4-R3 artifact upload | **SUCCESS** |

## 3. Final exact-head artifact / 최종 exact-head artifact

- artifact: `musica-m4-r3-real-browser-e2e`
- artifact ID: `10181576753`
- digest: `sha256:b38c510939c7d6869ad446cd79ed8fd0777ed09e636e9f7aa95d053be65a206b`
- workflow run: `34553248432`
- exact head: `0bfc3e7475c20e4891c629ee736237bbc72a958c`
- browser: Chromium via Playwright
- provider mode: `fixture`
- live OpenAI call: **NO**
- external provider network required for the product workflow: **NO**

The earlier successful branch artifact (`10181507410`, digest `sha256:0df4f74ac8ae6af74168f2592d027fbc1811b3355267017f65c1e295124ee2e3`) remains developmental evidence only. Promotion is based on the exact-head PR artifact above.

## 4. Real-browser canonical proof / 실제 Browser 공식 증명

The final E2E path proves:

```text
real_chromium_used                         = true
project_created_via_visible_browser_controls = true
accepted_audio_browser_retrieval_valid    = true
progressive_disclosure_tabs_exercised     = Direct, Shape, Inspect, Code
preview_not_accepted_visible              = true
preview_ref_unchanged_before_accept       = true
preview_candidate_differs_from_parent     = true
preview_diff_count                        = 9
hard_lock_count                           = 3
preview_conflict_controls_disabled        = true
explicit_accept_advanced_to_candidate     = true
branch_created_and_checked_out            = true
history_visible                           = true
export_visible_with_hash                  = true
code_view_read_only                       = true
restart_reopen_preserved_branch           = true
restart_reopen_preserved_head             = true
restart_reopen_integrity                  = PASS
reopened_audio_browser_retrieval_valid    = true
browser_console_error_count               = 0
browser_page_error_count                  = 0
```

## 5. Visible workflow / 화면 상호작용 경로

```text
open Studio
  ↓
enter project name + natural-language intent
  ↓
Generate
  ↓
ACCEPTED + integrity PASS + accepted WAV
  ↓
Direct → Shape → Inspect → Code
  ↓
change Tension + final-section scope
  ↓
Preview selected change
  ↓
PREVIEW · NOT ACCEPTED
  ↓
canonical head remains parent revision
  ↓
preview WAV + structured diff + three HARD locks
  ↓
branch/checkout/export blocked during pending preview
  ↓
explicit Accept
  ↓
head advances to candidate revision
  ↓
Preview decision disappears
  ↓
create/checkout browser-variation
  ↓
history + canonical export
  ↓
read-only Code/session JSON
  ↓
stop first Studio service
  ↓
start fresh service on same workspace
  ↓
Open existing project in Browser
  ↓
branch/head/integrity/audio restored
```

## 6. Screenshot evidence / Screenshot 근거

The real-browser artifact contains six Chromium screenshots:

```text
01-created-accepted.png
02-preview-not-accepted.png
03-accepted-revision.png
04-branch-history-export.png
05-code-view.png
06-reopened-after-restart.png
```

Visual inspection confirmed the Direct identity-lock controls, accepted audio state, visible `PREVIEW · NOT ACCEPTED`, structured diff, three HARD locks, disappearance of the preview decision after Accept, branch/history/export state, read-only Code/session JSON, and durable reopen after service restart.

## 7. Product defects discovered by R3 / R3가 발견한 제품 결함

Real-browser validation found defects not exposed by static/direct HTTP evidence and fixed them before promotion.

### R3-F01 — Invalid `networkidle` readiness assumption

HTML5 media activity made `networkidle` unsuitable as a Studio-ready condition. R3 changed the browser gate to `DOMContentLoaded` plus explicit visible Studio-ready assertion.

### R3-F02 — Browser create could not express core HARD identity locks

The core already supported `preserve_on_edit`, but Browser create sent an empty policy. R3 added visible **Tempo / Melody identity / Rhythm identity** controls and wired them to the existing trusted contract.

### R3-F03 — Preview decision remained visually visible after Accept

Canonical promotion succeeded, but CSS `display:flex` overrode semantic `hidden`. R3 added explicit hidden-state rendering so the decision card disappears after Accept.

### R3-F04 — Modern Chromium project-name pattern incompatibility

Modern HTML `v` regular-expression semantics rejected an unescaped hyphen in the input pattern. Browser delivery now normalizes the pattern without changing the accepted character set. The final exact-head run reports zero browser console/page errors.

## 8. Authority proof / 권한 증명

```text
Chromium Browser
  ↓ visible UI actions
Browser Studio
  ↓ same-origin loopback HTTP
M4-R1 application service
  ↓
M3/M1/M0 trusted core + HARD locks
  ↓
PREVIEW — non-canonical
  ↓ explicit Accept only
M2 Project Engine
  ↓
Accepted .musica revision + bound artifacts
```

Browser and server evidence agree that Preview did not advance the canonical head and that only explicit Accept promoted the candidate revision.

## 9. Claim boundary / 주장 경계

M4-R3 does **not** validate or imply:

- human-subject usability-study results,
- production/mastering audio quality,
- waveform/piano-roll/note-level professional editing,
- desktop installer/signing,
- cloud collaboration or multi-user security,
- remote HTTP serving,
- live OpenAI provider execution,
- professional DAW/VST/sampler interoperability,
- crash-atomic recovery across every possible process/filesystem failure.

M4-R3는 사람 대상 usability, 상용 mastering 음질, 전문 note-level editing, desktop packaging, cloud collaboration, live OpenAI, DAW/VST/sampler 상호운용을 아직 주장하지 않습니다.

## 10. Promotion record / 승격 기록

The evidence-bearing PR head passed all required gates and was merged exactly. Therefore M4-R3 may be promoted to **VALIDATED** through the accompanying state-only closure.

근거 포함 PR exact head가 모든 필수 gate를 통과하고 정확히 병합되었으므로, 본 state-only closure에서 M4-R3를 **VALIDATED**로 승격합니다.
