# PROD-E2E-R1B-G2B validation / 두 버스 실제 Browser 믹싱 검증

## Exact code and CI / 정확한 검증 대상

- First **implementation head**: `917e6683684f8628578537ed9e0c1199d6fc3864`, Draft PR #189, parent issue #187 (and #181/#178).
- **47/47 GitHub Actions workflows SUCCESS** on this exact implementation head, including dedicated real-Chromium run **39181940772**.
- Implementation was built from G1 main, and GitHub PR includes subsequent G2A state/status main `bb992cbc1c853963619185257f888c68d931595f` in its merge base. PR mergeable=true at inspection. Do not promote unless latest base and CI remain green.
- **This durable-validation commit creates a successor HEAD; all 47/47 inherited + new workflows must pass again at that exact successor SHA before expected-head squash merge.**

## Independently verified ZIP and WAV / 독립 실증

- Run artifact ID `12156652602`, name `musica-prod-e2e-r1b-g2b-two-bus`, **9,253,993 ZIP bytes**.
- Both GitHub artifact digest and independently downloaded ZIP SHA-256: `e18eb519b354d021d6c8f454550b4b70c8a639967b53a30c655853206fb5d463`.
- ZIP files: **four real Chromium screenshots**, `proof.json`, `routed-accepted.wav` and `routed-reopened.wav` (both **384,044 bytes**, identical bytes).
- Stereo PCM16 WAV: **8,000 Hz**, 96,000 frames = 12 s. Independent Python `wave` and `struct` reading: left peak **1,504**, right peak **6,200**, **32,000 nonzero scalar samples**, **0 clipped**. Reopened byte identity independently checked.
- Previous G1 accepted two-source WAV SHA-256: `bd44323e86dc8480327cef00d7c51c35df7507bc9254cb83e83c7850fd1f4b79`; current routed WAV SHA-256: `dd16529019d259a39a64a2b97b11fa10a7edda198379d253eee3a5f1492cbad0`.
- Browser runner asserts **Bus A at -6dB attenuates left-channel PCM** and **Bus B leaves all right-channel PCM exactly identical to G1**. Screenshots cover two-bus Preview, gain Preview, accepted output and reopened accepted output.
- 0 Browser console errors, 0 page errors, 0 network errors; real automated Playwright Chromium operation, *not* a human user study.
- Browser click creates source-bound, non-canonical two-bus + master routing Preview. Only the separate explicit Accept advances the accepted revision. Subsequent Bus A gain Preview similarly leaves accepted HEAD intact until separate Accept. No auto-Accept.

## Defects found and corrected / 실제 회귀에서 발견·수정한 문제

1. G1 fixture runner exports `suite` (not `run_suite`). Corrected.
2. An accepted source may arrive asynchronously after the routing view; fixed by source-bound `musica:native-audio-view-ready` and routing controls re-render, rather than timeouts or disabling checks.
3. The Browser accepted WAV download guard correctly refuses stale pre-routing audio revisions; final actual Chromium runner requires exact accepted audio/routing revision convergence before download, not a stale enabled button.
4. Older red and pending commits were never accepted as evidence. 47/47 success above is on exact latest implementation.

## Boundaries and next product work / 명확한 한계

G2B demonstrates *two short synthetic 8kHz WAV sources, two accepted buses/master, audible accepted bus attenuation, export and exact reopen*. **It does not yet demonstrate user-created canonical automation lanes, user-auditioned automation effects or simulated bus plugin choice in Browser.** G2C must address those. No real external VST3/CLAP/AU binary, live microphone/device, long/44.1kHz/48kHz professional track, human usability or commercial workstation acceptance is established. Keep #187/#181/#178 OPEN.

**Promotion:** After this evidence successor, require 47/47 CI, re-review exact HEAD, mark PR ready, then expected-head guarded squash merge. Never waive tests.
