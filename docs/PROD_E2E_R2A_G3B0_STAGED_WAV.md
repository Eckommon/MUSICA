# PROD-E2E-R2A-G3B0 — Bounded staged WAV ingress / 검증형 WAV 분할 업로드

**Draft implementation / 구현 검증 중.** Issue #195 under R2A #192; predecessor 44.1/48kHz G3A #194 merged after 49/49 implementation and successor gates to main `7c74296fa63319c7d301d22c1589b5a53b091502`.

## User-facing workflow / 사용자 이용
First-party Browser keeps the existing 44-byte to 16MiB direct `import-wav` unchanged. A selected 16–64MiB source now uses **same-origin staged start → ordered 1MiB chunks → SHA-256 check → finish**, with an explicit Cancel button. The server stages only a randomized opaque ID under its own configured workspace; the user supplies **no filesystem path**. Each request is local-session-bound and checks pending Preview and exact accepted HEAD. Start must declare the expected SHA-256 and bounded length; every chunk declares its offset and SHA and is individually verified, with wrong-order/hash upload discarded. A failed full digest or explicit cancellation removes temporary data without any imported asset/audit/clip. A successful finalize delegates to the **existing** CAS/audit importer; the imported WAV remains a resource-only immutable asset, **not** a project track or clip. The user must still explicitly Preview and Accept track/clip edits.

## Security bounds / 보안·리소스 상한
- 64 MiB per staged source, 1 MiB per chunk, 1 concurrent active upload per session, up to 4 active per server, 15-minute idle expiry and deletion; obsolete orphan temp files cleaned on subsequent startup/access.
- No arbitrary URL-path filename, no `Transfer-Encoding: chunked` and no ability for one Studio session to finalize another session's random upload ID; strict Content-Type, Content-Length and per-chunk digest requirements. The old 16MiB direct endpoint remains independently guarded.
- Browser SHA-256 currently computes from `File.arrayBuffer()` (up to 64MiB) and finalization currently uses a **whole-file bounded 64MiB `read_bytes`** into existing `import_audio_asset_bytes`. This is **not memory-bounded streaming CAS** or zero-copy; the G3B-1 milestone must refactor hash/descriptor/CAS validation to streaming and improve crash-atomicity.
- No claim of three-minute two-track rendered WAV. At 48kHz stereo PCM16, a three-minute WAV source is ~34.56MB; G3B-0 only solves transport, not efficient accepted rendering or physical I/O. In-memory decoder/routed mixer remain the key G3B-2 blockers.

## Evidence and promotion / 승격 기준
A new **50th** permanent GitHub Actions CI checks original direct import regressions, HTTP staged SHA/size/wrong session/wrong offset/cancel/audit invariants, real Chromium user File picker of >16MiB PCM16 source, accepted HEAD unchanged and temporary cleanup. After exact implementation 50/50 SUCCESS, inspect artifact proof, commit durable bilingual validation successor and demand second exact-head 50/50 before expected-head guarded merge. G3B parent #195 remains OPEN for G3B-1 to G3B-3.
