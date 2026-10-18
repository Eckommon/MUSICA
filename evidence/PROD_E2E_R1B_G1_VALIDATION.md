# PROD-E2E-R1B-G1 validation / 두 실제 오디오 소스의 Browser 믹싱 실증

**Exact validated implementation head:** `7bedf3f939bbe28d307b89d065fded4df73df2bc`. **Implementation 45/45 GitHub Actions workflows SUCCESS.** This document creates a **new evidence-successor head; successor CI and merge are still mandatory.** Issue #185 / PR #186; parents #181/#178 remain OPEN.

## Product operation verified / 실제 검증한 사용자 조작

- Automated **real Playwright Chromium**, first-party Studio Create → choose/import two **different user-supplied local PCM WAV bytes** → separate two track Previews and explicit Accepts → separate two clip Previews and explicit Accepts → two native mixer Pan Previews and explicit Accepts → accepted WAV download / `.musica` export → browser/server restart and exact project reopen.
- **Six distinct manual Accept operations** observed through browser controls. Resource imports and all Preview operations **did not advance accepted HEAD**. No hidden auto-Accept. Accepted state: **two tracks, two separate immutable SHA-256 resources, two clips, pan -1 and +1**.
- Browser user-triggered next-unused track/clip ID suggestions and clip destination preservation do not commit creative state. Product guide counts **2 TRACKS / 2 CLIPS ACCEPTED**.
- The real Chromium flow is an automated exercise, **not a human usability study**.

## Exact CI + independently reviewed evidence / 독립 아티팩트 분석

- Dedicated new **45th workflow** run `39126696591`, job `117673215727` **SUCCESS**. All **45/45** workflows succeeded at the exact implementation commit above, with no waiver.
- Artifact `12136303700` (`musica-prod-e2e-r1b-g1-two-track`) **8,078,158 bytes**, GitHub digest and independent downloaded ZIP SHA-256 both `454c1300093c482edf88877491bcd559e3736c9dce738302a45c061ef06a7e4c`. ZIP contains **four real Chromium PNG screenshots, proof.json, two WAVs**.
- Downloaded stereo WAV and reopened WAV are **byte-exact**; both SHA-256 `bd44323e86dc8480327cef00d7c51c35df7507bc9254cb83e83c7850fd1f4b79`, **384,044 bytes each**, actual format **8kHz stereo 16-bit PCM, 96,000 frames = 12 seconds**.
- Independent Python `wave` + `struct` oracle: first **16,000 left PCM frames exactly equal original first mono WAV** (+/-3000); first **16,000 right PCM frames exactly equal original second mono WAV** (+/-6200); all later left/right frames zero. **32,000 nonzero scalar samples, peak 6200, clipping 0**. This proves actual two-source contribution, unlike single nonzero-WAV checks.
- Browser console errors **0**, page errors **0**, network errors **0**. Source/reopen accepted HEAD and final WAV hash identical.

## Genuine repeated-edit defect discovered and fixed / 반복 편집 결함 종결 범위

An initial real-Chromium run passed two-source import, two-track and two-clip acceptance, then failed the **second mixer Preview** because the prior algorithm recursively concatenated full parent revision IDs until a candidate revision exceeded the unchanged `studio-audio-view-v0.schema.json` 128-character ID constraint. The trusted mixer candidate was otherwise READY_FOR_PREVIEW; this was **not** a transient environment failure.

- Corrected `audio_edit.py` and `audio_mixer_edit.py` to use **fixed-length deterministic SHA-256 of exact parent revision + candidate**, preserving project source authority and parent history (not weakening any schema).
- Permanent 30-consecutive-edit unit test checks deterministic replay, bounded IDs, unique parent-bound identities. The actual corrected 6-Accept Chromium flow now succeeds; inherited CI 45/45 is green.

## Limits and product next / 비지원 및 다음 목표

One 12-second project driven by two short synthetic 8kHz WAV fixtures, not a professionally mastered or full-length production, a usability study or an original AI-created commercial song. No real audio interface, microphone, actual 44.1/48kHz hardware, real third-party plugin binary, or integrated user-operated routing/automation effects were demonstrated. Continue with guided routing/automation, higher quality sample rates and longer multitrack workflows after safe G1 promotion.

**Promotion requirement:** run full permanent **45/45** on this exact new durable-validation successor SHA; independently assess failures if any, then mark PR #186 ready and expected-head squash merge. Only after merge close G1 issue #185; keep #181/#178 open. No waived tests.
