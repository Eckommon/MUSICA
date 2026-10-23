# G3B2C-R3 — bounded first-party Studio audio inspection / 장시간 음악 조회 메모리 보호

**STACKED Draft / 정식 병합 전 초안**. Depends on B2C-R1 PR #206 and R2 PR #208; R3 may not be promoted ahead of both.

## Why / 문제
Legacy `StudioAudioSurface._render_blueprint()` and `StudioRoutingSurface._audition()` calculate the entire stereo float buffers and `wav_bytes` merely to create an accepted or pending Preview metadata JSON view. At 180s/48k this can allocate massive Python objects even without a Browser play request.

## R3 bounded contract / 신규 설계
- For projected WAV larger than **16MiB** (duration × exact source sample rate × stereo PCM16 bytes + WAV header), accepted Native and Routed Studio views **skip the legacy full-buffer renderer**. Return a truthful unavailable metadata summary with null WAV SHA and the explicit `LONG_ACCEPTED_AUDIO_STREAM_REQUIRED` classification; never fabricate SHA or imply rendered Preview audio.
- Existing first-party Native/Routing Browser players recognize the accepted marker and use the accepted-only, file-backed `/v0/sessions/{session}/audio/stream/accepted.wav` 200/206 endpoint implemented in G3B2C-R1/R2. No changed creative HEAD, no auto Accept, no client-controlled file path.
- **Preview longer than 16MiB is explicitly unavailable**, classified as `LONG_PREVIEW_AUDITION_NOT_AVAILABLE`; the Browser does not play a stale accepted WAV as the pending Preview. This is temporary and MUST be resolved with source-bound long-duration pending-Preview streaming before claiming full 3-minute user editing.
- Small accepted and pending previews continue to use the legacy path with exact WAV hashes and byte-equivalent behavior; no change to short-track tests.
- Unit tests build two truly accepted, independent 180s/48k stereo PCM assets (native and 2-bus routing). They monkeypatch the long full-buffer render call to throw, then validate that read-only Studio views return truthful metadata without calling that renderer or advancing HEAD. Node syntax checks both Browser surfaces. A **real Playwright Chromium** test separately opens a persisted accepted two-track 180s project in the actual Studio, verifies the accepted `<audio>` element binds to the bounded HTTP Range endpoint, waits for browser-computed 180s WAV metadata, preserves exact HEAD, and uploads a screenshot+JSON. This is not a human-created 180s project or low-latency performance proof.

## Explicit limitations / 아직 미검증
- General Project `verify_integrity()` can still read whole source CAS objects; R3 prevents song-length **DSP** buffer and WAV-bytes materialization **during read-only Studio view**, but cannot claim all Project operations constant-RSS.
- Actual Browser 180s metadata, seek/export and Pending Preview->Accept full creative cycle requires separate G3B3 evidence; 180s Preview audition is presently **unavailable**, not implicitly accepted.
- Physical audio interface, real plugin binaries, practical low-latency playback, 100-track scale and mature commercial DAW usability have not been demonstrated.

## Promotion rule / 병합 관문
Require all inherited 56 CI plus dedicated **57th workflow** (including real Chromium 180s file-backed WAV metadata) on exact implementation head, independently inspect downloadable screenshot/JSON, create bilingual evidence successor and rerun all 57 workflows before guarded expected-head squash. B2C-R1 and R2 must merge first; maintain G3B3 parent issues open.
