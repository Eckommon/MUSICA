# PROD-E2E-R1B-G0 Validation / Browser 한 곡 제작 안내 실증

**Implementation validated at exact SHA:** `69d2f2d92a5e6cef0165f0f24a1abad1b6fe79be`. **Status: evidence successor CI and merge NOT YET completed.** Parent issues #183 / #181 / #178.

## Scope / 실제 검증 범위

First-party Studio Browser `One-song production guide` guides create/open, local immutable PCM WAV import, separately Preview/Accept track and clip, optional mixer/routing/automation navigation, accepted WAV delivery, `.musica` export, and project restart/reopen. Progress comes from accepted source projection, not file chooser presence or preview. This G0 is **navigation/delivery**, not a fully produced general-purpose song.

## Exact CI and independent artifact / 검증 이력

- All **44/44 GitHub Actions workflow runs SUCCESS** on exact implementation SHA, no waivers. New dedicated real-Chromium workflow run `39115725100`, job `117640993958`: **SUCCESS** (including JS syntax, HTTP authority, native tests, Chromium user controls).
- Generated artifact **12132755778**, `musica-prod-e2e-r1b-guide-browser`; GitHub-reported ZIP SHA-256 `0e4a027c462764d60ba788a9ba194556fe8a9d446dfe06efadbf635d199e1522`. Independently downloaded 7,815,668-byte archive, recomputed SHA-256 **matches**.
- ZIP includes **four actual Chromium PNG screenshots**, `proof.json`, two WAV files. Accepted WAV and reopened accepted WAV SHA-256 both `62949d9750e75892be3ca8acfe1ac47668870647c04b995844e4f0e81c4328dd`; **byte-for-byte equal**.
- Independently decoded actual WAV via Python `wave` and `struct`: **8,000 Hz, 2 channels, 16-bit PCM, 96,000 frames (12 seconds), peak |sample| 3500, 32,000 nonzero scalar samples, 0 clipped scalar samples**. 384,044 bytes each.
- Browser automation assertions: imported resource left accepted HEAD unchanged; track and clip Preview individually left HEAD unchanged; two explicit Browser Accept operations advanced HEAD; WAV delivery was blocked before Accept; same accepted-derived WAV downloaded after Accept; reopened project verified exact HEAD/bytes. Browser console, page and network failure counts **0**.
- Source limitations: one mono 8 kHz two-second test WAV and one accepted native track/clip (rendered 12-second stereo project WAV), not two musically independent tracks, professional mastering or sustained hardware.

## Nonclaims / 정확한 제한

Playwright-driven real Chromium controls are not a human usability study. The test does **not** establish an operator-composed full-length multitrack song, optional routing/automation actually used, physically captured microphone audio, 44.1/48 kHz real interface, VST3/CLAP/AU third-party binary execution, actual plugin latency or commercial production readiness.

## Promotion / 병합 기준

This evidence document itself creates the new **validation-successor** commit. Verify all **44/44 workflows SUCCESS at that exact successor SHA**, review new run evidence and reject failures without waiver, then mark PR #184 ready and expected-head squash merge. Only then update canonical project memory and close bounded G0 issue #183; parent #181/#178 remain OPEN for multitrack, routing/automation integration and product goals.
