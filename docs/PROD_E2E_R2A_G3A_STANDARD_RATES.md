# PROD-E2E-R2A-G3A — Standard-resolution Browser production / 44.1·48kHz 제작 실증

**DRAFT / 검증 중.** Issue #192. Parent G2C #190 and PR #193 closed and merged to `main` `72c528eaf61894252348fdf6f63066969d2f8258` after implementation and successor **48/48 GitHub Actions** and independently audited PCM evidence.

## Problem / 해결 목표

Previous real Chromium multi-track/routing/gain automation proof used only 8,000 Hz synthetic 12-second source WAVs. The existing trusted WAV importer and native mixer already support 8,000–192,000 Hz exact-source integer PCM; there is **no need to create a duplicate audio engine or pretend a resampler exists**.

G3A makes the existing **real Browser user-operated** G1 → G2B → G2C production suites accept one bounded explicit source sample rate, preserving 8k as the unchanged default. New 49th permanent CI matrix exercises **44,100 Hz AND 48,000 Hz** independently, each with two distinct user-uploaded mono PCM16 source WAVs, two accepted tracks/clips, two buses and master, accepted bus gain, and user-created native gain automation Preview → explicit Accept. The accepted-derived stereo PCM16 WAV must have exact 12 s × rate frames, reproducible source contribution and gain curve, no clipped samples, `.musica` export and server/Browser restart plus exact byte-for-byte WAV reopen. Independent SHA and screenshot ZIP checks are required before promotion.

## Explicit limits / 비지원 사항

- 2 seconds of distinct deterministic source audio in a 12-second project; this is **not** a full-length mastered professional song.
- Local first-party Browser WAV importer retains its **16 MiB** cap. At 48 kHz stereo PCM16, a three-minute take exceeds that; G3B must design chunked bounded upload, streaming PCM and cleanup before a genuine full-song session claim.
- Exact matching sample rates across accepted tracks are **required**. A mixed 44.1/48k project must report an explicit unsupported error; no silent resampling. This is checked with a unit authority invariant; mixed-source real Browser negative remains separately to prove.
- No physical 44.1/48kHz microphone/audio interface callback, ASIO/WASAPI latency, real third-party plugin binaries, authentic human usability or commercial AI song quality are proven by this CI.

## Gate / 검증과 병합

New 49th workflow + all inherited 48 must pass at exact implementation HEAD; inspect WAV/PCM/SHA/screenshots for both rates; commit bilingual durable evidence; full 49/49 successor CI; guarded expected-head squash merge. Do not close #192 until G3B larger-source/long-session acceptance separately proven.
