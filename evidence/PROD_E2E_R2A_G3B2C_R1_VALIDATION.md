# PROD-E2E R2A G3B2C-R1 validation / 승인 WAV HTTP Range 및 실제 브라우저 다운로드

## Canonical predecessor and exact implementation / 공식 기반 및 구현 커밋
- Official prior `main`: `1668c1256c35539e51815631a715917aedaa3f8c` (G3B2B merged). Scope: [Draft PR #206](https://github.com/Eckommon/MUSICA/pull/206), parent #205/#201/#195/#192.
- Exact implementation HEAD **`4f9a8b21dd1e0a1fa9b4ebba54e127a84f9b4f8d`**, rebased to canonical main with **seven R1-only changed files**.
- **55/55 GitHub Actions workflow runs SUCCESS and 59/59 check runs SUCCESS at the exact implementation HEAD**. Dedicated permanent workflow [#39838148473](https://github.com/Eckommon/MUSICA/actions/runs/39838148473) SUCCESS, including real localhost byte-Range and Playwright Chromium click/download test. No inherited test skipped or failed gate waived.

## Independently inspected downloadable artifact / 독립 산출물 검증
- Downloaded dedicated artifact ID `12452757904`, archive filename `MUSICA-G3B2C-R1-verified-55-workflow-artifact.zip`, **ZIP SHA-256 `0931132b01d098a66e31f171307a0384008f45972396210705f2d6382f821b25`**. Actual members: `clicked-accepted.wav`, `01-accepted-bounded-download.png`, `proof.json`.
- Independently parsed actual WAV header with Python `wave`: 8,000 Hz, stereo (2 channels), 16-bit signed PCM, 96,000 frames = exactly **12 seconds**, **384,044 bytes**. Actual downloaded WAV SHA-256 **`bd44323e86dc8480327cef00d7c51c35df7507bc9254cb83e83c7850fd1f4b79`**. This matches independent `proof.json` expected and downloaded SHA; no implicit creative Accept or accepted revision HEAD mutation.
- The Browser action was **a real Chromium user-clicked first-party Studio download**, not a synthetic Python HTTP request. Screenshot and JSON are preserved in the ZIP. Separate real localhost HTTP tests check one byte range, suffix range, invalid/multiple-range 416, correct Content-Range/Content-Length, session quota, source HEAD and temporary output cleanup; 180-second accepted two-source 48kHz Range PCM test also passes on this implementation head.
- A local process peak RSS or end-to-end **180-second Browser edit/play/export** is **not** established by this 12-second browser download artifact. A future study with actual human end-users is not implied.

## R1 functional scope and limits / 구현 범위·남은 사항
- Additive accepted-only session-scoped `GET /v0/sessions/{id}/audio/stream/accepted.wav` with explicit user-triggered `?download=1`, accurate `200/206/416`, ETag SHA, <=1MiB output writes, one active stream per session/two total, private derived WAV cleanup; no client filesystem path, no Pending Preview, no automatic Accept.
- **R1 rerenders the entire WAV for each byte-Range request** and existing Studio accepted/Preview metadata views still use full-buffer render: these are specifically deferred to R2 [#208] and R3 [#210]. Bounded, source/HEAD validated reusable cache and real 180s player/Preview are not R1 production claims.
- No real audio device, realtime low-latency driver, third-party VST/CLAP binaries, or mature DAW claim.

## Mandatory evidence successor gate / 영구 검증 후속 단계
This evidence file is **not itself promotion approval**. It must be included in the next successor commit that independently passes **55/55 workflows and all 59 checks**, with unchanged canonical main and exact PR head guarded squash. Parent #205/#201/#195/#192 remains open; R2/R3 require separate implementation and evidence successor proof.
