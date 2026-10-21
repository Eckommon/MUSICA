# PROD-E2E-R2A-G3B1B — Bounded Browser WAV intake validation / 분할 WAV 브라우저 가져오기 검증

## Evidence chain / 정확한 증거 체계
- Issue [#199](https://github.com/Eckommon/MUSICA/issues/199), parent #195/#192; implementation PR [#200](https://github.com/Eckommon/MUSICA/pull/200).
- Canonical predecessor: PR #198 G3B1A merge `6b55f293aa334d6084c219460cefa0dc27380756`, itself validated 51/51 on implementation and documentation successor.
- **Exact G3B1B implementation HEAD: `c8258593cacbf337376b65e7a4bac4fa90381ea9`**.
- All **52/52 distinct GitHub Actions workflows SUCCESS** on this SHA; 51 inherited gates preserved. Dedicated real-Chromium + HTTP [run #39643598944](https://github.com/Eckommon/MUSICA/actions/runs/39643598944), job `119373260138`, SUCCESS, including Node crypto-vs-incremental-JS SHA-256 oracle.
- Downloaded dedicated artifact **`12366128879`** `musica-prod-e2e-r2a-g3b1b-3min`, independently read ZIP files, `proof.json`, original WAV and captured screenshot. **ZIP SHA256 `7956119a26808cef1e508dfe098c7df8ac5d349285aca679fcc735f8a0684f77`**. The screenshot visibly shows user-file WAV resource import and track/clip controls; its long full-page image is not direct user usability evidence.

## Numerically verified / 독립 수치 검증
- Real Playwright Chromium uses the existing first-party local Browser file picker with a generated deterministic fixture (no human subject).
- Captured original `three-minute-source.wav`: **34,560,044 bytes**, RIFF/WAV PCM16, **48,000 Hz**, **2 channels**, **8,640,000 frames**, exactly **180 seconds**; first stereo frame `(42,0)`.
- Independent WAV hash `30f07d654d27057d491eca105b7965d0f7c7c6846e2e62fe603cc0ea14bb0f32` matches JSON proof `source_sha256`.
- Proof records resource-only immutable CAS registration, unchanged accepted creative HEAD, no automatically accepted track or clip, staged temp files remaining zero, and no assertion of two-track long-song mix.
- Separate localhost HTTP adversarial tests exercise wrong session, oversize, wrong offset, chunk SHA, whole-file SHA, pending Preview, cancel and aborted transmission. Browser 1MiB `File.slice()` hashing avoids `file.arrayBuffer()` for the whole 34.56MB file; chunk WebCrypto digest and SHA validation are distinct.
- The existing <=16MiB direct import endpoint remains unchanged. A 3-minute WAV imported as a resource does **not** become a track/clip without source-bound user Preview and explicit Accept.

## Product/safety limits / 한계
- **G3B1B verifies Browser-to-CAS intake only**; G3B2 still must prove 3min dual-track bounded-RSS/CPU deterministic mixing and 3min WAV export. G3B3 must prove complete accepted 2-track Browser production and project/archive reopen.
- Browser proof uses deterministic constant-tone fixture, not professional music, actual microphone/Windows device/physical latency, or human study.
- G3B1A resource descriptor/object/audit publication lacks a transactional crash-recovery journal. The new upload store clears dedicated stage remnants on startup but cannot claim atomic multi-file CAS crash recovery.
- Project-wide `verify_integrity` may still inspect full objects in memory; bounded upload/staging and streaming CAS do **not** prove end-to-end bounded memory for arbitrary projects or renders. This must be addressed before long-song commercial claims.
- Stated maximum is 64MiB per WAV input, not arbitrary length/bit depth/samplerate.

## Promotion gate / 공식 병합 관문
This document is the durable validation successor. Require **52/52 workflows SUCCESS on this document-bearing exact successor SHA**; reconfirm main and PR head, mark ready, then guarded expected-head squash merge. Keep parent #195 and #192 OPEN for G3B2/G3B3. Do not waive failed/pending checks.
