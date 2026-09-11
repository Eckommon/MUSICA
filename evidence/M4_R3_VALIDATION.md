# M4-R3 Validation Evidence / Usable MVP Real-Browser E2E 검증 근거

**Milestone / 마일스톤:** M4-R3 — Usable MVP / Real-Browser E2E Acceptance v0  
**Evidence status / 근거 상태:** BRANCH VALIDATION PASSED; PR exact-head validation pending / branch 검증 통과, PR exact-head 검증 대기  
**Evidence class / 근거 등급:** `REAL_BROWSER_E2E_EVIDENCE`

## 1. Scope / 범위

M4-R3 validates automated operation of the packaged MUSICA Studio through an actual Chromium browser. It extends M4-R2 static/HTTP evidence with visible browser interaction, screenshots, browser/server authority cross-checks, and restart/reopen proof.

M4-R3는 실제 Chromium browser를 통해 packaged MUSICA Studio가 자동화된 실제 사용자 흐름으로 조작 가능함을 검증합니다. M4-R2의 static/HTTP evidence에 visible browser interaction, screenshot, browser/server 권한 교차검증, restart/reopen 증명을 추가합니다.

This is **not** a human-subject usability study and does not claim that automated media validity proves human auditory perception.

이는 사람 대상 usability study가 아니며 자동화된 media 유효성 검증이 인간의 실제 청취 경험을 증명한다고 주장하지 않습니다.

## 2. Successful branch validation identity / 성공 branch 검증 식별자

- branch: `m4-r3-real-browser-e2e-v0`
- validated branch head: `b97db1074596ff5e7a0f2fc413ab8aed4fa3c182`
- GitHub Actions run: `34553014255`
- Python 3.11 core job: **SUCCESS**
- Python 3.12 core/evidence job: **SUCCESS**
- dedicated `browser-e2e` job: **SUCCESS**
- Playwright Chromium install: **SUCCESS**
- real-browser E2E execution: **SUCCESS**
- M4-R3 evidence upload: **SUCCESS**
- M0→M4-R2 regression/evidence generation/upload: **SUCCESS**

## 3. Canonical branch artifact / 공식 branch artifact

- artifact: `musica-m4-r3-real-browser-e2e`
- artifact ID: `10181507410`
- artifact digest: `sha256:0df4f74ac8ae6af74168f2592d027fbc1811b3355267017f65c1e295124ee2e3`
- evidence class: `REAL_BROWSER_E2E_EVIDENCE`
- browser: Chromium via Playwright
- provider mode: `fixture`
- external provider network required: **NO**
- live OpenAI call performed: **NO**

This artifact was downloaded and inspected after the successful branch run.

성공 branch run 이후 artifact를 직접 다운로드하여 manifest, proof, screenshot을 검사했습니다.

## 4. Real-browser canonical proof / 실제 Browser 공식 증명

Structured proof records:

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

The artifact records three browser `requestfailed` events for superseded/aborted audio element loads. Each corresponding canonical audio URL was independently fetched through the browser context as HTTP 200 `audio/wav` with valid RIFF bytes. These teardown/source-replacement cancellations are retained as evidence and are not treated as content retrieval failures.

artifact에는 audio element source 교체·종료 과정의 `requestfailed` 3건이 기록됩니다. 각 canonical audio URL은 browser context에서 별도 HTTP 200 `audio/wav` + RIFF로 검증되었으며, 이 취소 이벤트는 숨기지 않고 근거로 보존합니다.

## 5. Visible workflow proof / 화면 상호작용 증명

Actual Chromium interaction path:

```text
open Studio /
  ↓
fill visible project name + natural-language prompt
  ↓
Generate project
  ↓
ACCEPTED + integrity PASS + accepted WAV
  ↓
Direct → Shape → Inspect → Code → Direct → Shape
  ↓
change Tension + final-section scope
  ↓
Preview selected change
  ↓
PREVIEW · NOT ACCEPTED
  ↓
assert displayed/server canonical head remains rev-001
  ↓
valid preview WAV + 9 diff entries + 3 HARD locks
  ↓
assert branch/checkout/export controls disabled
  ↓
explicit Accept
  ↓
head advances to preview candidate
  ↓
preview decision disappears
  ↓
create+checkout browser-variation
  ↓
history count = 2
  ↓
canonical export path/hash visible
  ↓
Code view read-only session JSON
  ↓
stop first Studio service
  ↓
start fresh StudioService on same workspace
  ↓
Open existing project through visible Browser form
  ↓
browser-variation + accepted head + integrity PASS restored
  ↓
accepted WAV valid after restart
```

## 6. Screenshot evidence / Screenshot 근거

The inspected artifact contains six non-empty Chromium screenshots:

```text
01-created-accepted.png
02-preview-not-accepted.png
03-accepted-revision.png
04-branch-history-export.png
05-code-view.png
06-reopened-after-restart.png
```

Visual inspection confirmed:

- Identity Locks visible on Direct create,
- accepted project/audio state,
- pending `PREVIEW · NOT ACCEPTED`, exact diff and three HARD locks,
- preview decision removed after Accept,
- branch/history/export state,
- read-only Code/session JSON,
- reopened durable project after service restart.

## 7. Durable state values / 영속 상태 값

Branch evidence observed:

```text
accepted root head       = rev-001
preview/accepted revision = rev-studio-14650350d4db8b05a4b2eeb6
accepted project branch  = browser-variation
history revision count   = 2
project integrity         = PASS
export size               = 543579 bytes
export sha256             = b8e975883b2764559ecdea14a4a71ac965b42ce964bb157c27bb715c6f6a545f
WAV size                  = 352844 bytes
```

After a fresh service restart, the browser reopened the project and restored `browser-variation`, the exact accepted revision above, integrity `PASS`, and valid accepted WAV media.

새 service restart 이후 Browser가 project를 다시 열어 동일 branch, 동일 accepted revision, integrity `PASS`, accepted WAV를 복원했습니다.

## 8. Defects found by real-browser validation / 실제 Browser 검증으로 발견된 결함

R3 did not merely confirm R2. It found and fixed browser-specific defects that static/direct HTTP validation had not exposed.

### R3-F01 — Network-idle readiness assumption / readiness 오판

Initial real-browser run `34552145025` timed out on `networkidle` because HTML5 media connections are not a reliable Studio-ready signal.

Resolution: use `DOMContentLoaded` plus explicit visible `#connectionBadge = READY` assertion.

### R3-F02 — Browser could not create HARD identity locks / Browser lock 생성 기능 누락

Run `34552387283` reached Preview/Inspect but found zero HARD locks. Core support existed, but Browser create requests always sent `preserve_on_edit: []`.

Resolution: add visible **Identity Locks / 정체성 잠금** controls for:

- Tempo,
- Melody identity,
- Rhythm identity.

Selected values flow through the existing M4-R1 `preserve_on_edit` contract. The successful run proves three HARD locks are visible in Inspect.

### R3-F03 — Hidden Preview decision remained visually rendered / Accept 후 Preview 카드 잔존

Run `34552685197` proved Accept advanced canonical state, but the decision card remained visible because author CSS `display:flex` overrode semantic `hidden` behavior.

Resolution: `.decision-card[hidden] { display: none; }`.

### R3-F04 — Modern Chromium HTML pattern incompatibility / 최신 Chromium pattern 호환성

Run `34552844695` completed the full product workflow but browser console validation detected that the project-name pattern used an unescaped `-` under modern HTML `v` regular-expression semantics.

Resolution: Browser delivery normalizes the pattern to the same allowed character set with escaped hyphen. Final successful run reports zero browser console/page errors.

## 9. Authority verdict / 권한 판정

**PASS — real browser interaction did not bypass canonical MUSICA authority.**

```text
Chromium Browser
  ↓ visible UI actions
Browser Studio
  ↓ same-origin loopback HTTP
M4-R1 service
  ↓
M3/M1/M0 trusted core + HARD locks
  ↓
PREVIEW — non-canonical
  ↓ explicit Accept only
M2 Project Engine
  ↓
Accepted .musica revision
```

The browser and server independently agreed that the canonical head remained the parent during Preview and advanced only after explicit Accept.

Browser와 server가 독립적으로 Preview 동안 canonical head가 parent에 유지되고 명시적 Accept 이후에만 전진했음을 확인했습니다.

## 10. Claim boundary / 주장 경계

This branch evidence validates **automated real-browser operability** only. It does not validate:

- human-subject usability-study results,
- production/mastering audio quality,
- waveform/piano-roll/note-level professional editing,
- desktop installer/signing,
- cloud accounts/collaboration,
- remote HTTP serving,
- live OpenAI execution,
- DAW/VST/sampler interoperability.

본 branch 근거는 **자동화된 실제 browser 조작성**을 검증합니다. 사람 대상 usability study, 상용 음질, 전문 편집 UI, desktop packaging, cloud collaboration, live OpenAI, DAW/VST 상호운용을 검증하지 않습니다.

## 11. Promotion rule / 승격 규칙

M4-R3 SHALL NOT be promoted from the branch run alone. This durable evidence must be included in a pull request whose exact head passes:

1. Python 3.11 core regression,
2. Python 3.12 complete M0→M4-R2 evidence chain,
3. dedicated Playwright Chromium `browser-e2e`,
4. M4-R3 artifact upload.

Only that exact evidence-bearing PR head may be merged and then promoted through a state-only closure.

M4-R3는 branch run만으로 승격하지 않습니다. 본 durable evidence를 포함한 PR exact head가 core + browser gate 전체를 통과한 뒤 그 exact head만 병합하고 state-only closure로 승격해야 합니다.
