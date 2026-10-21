# PROD-E2E-R2A-G3B0 — Private bounded WAV staging / 대용량 WAV 안전 수신 기반

**DRAFT / 구현 검증 중** · issue #195, parent #192 · predecessor G3A PR #194 verified merged at `7c74296fa63319c7d301d22c1589b5a53b091502`.

## What exists / 구현된 부분

A private host-side `BoundedWavStaging` component enforces a fixed directory under Studio control (not user-provided paths), 64MiB maximum declared upload, 1MiB chunk maximum, at most two simultaneous active transfers, random opaque transfer tokens, exact per-chunk SHA-256, exact byte offset, total size and final streamed SHA-256. Temporary files are owner-only and can be cancelled/cleaned by trusted callers.

**No session HTTP endpoint, Browser UI wiring, immutable CAS finalize or canonical audio asset descriptor/audit has been implemented yet.** A verified private temporary path is *not* an imported WAV asset. No accepted creative revision changes, no automatic Preview or Accept, and no 3-minute rendered music claim.

## Mandatory subsequent gates / 후속 필수 작업

- Validate actual Studio session and pending-preview authority before allocation and every transfer action; secure HTTP session-bound begin/append/finalize/cancel with Content-Length/Content-Type checks, no Transfer-Encoding chunked confusion, resource quotas, expiry and aborted-transfer cleanup.
- Validate actual PCM WAV header and exact RIFF payload, stream into verified immutable CAS object and descriptor with correct audit; reimport idempotently. Test mismatched SHA, session, order, truncation, corruption, unexpected bytes and restart.
- Link first-party Browser File.slice upload without reading full files in JS, preserve explicit track/clip Preview→Accept.
- Rework Python per-frame full-length decoder/mixer and prove at least **two independent 3-minute 48kHz WAV sources**, bounded RSS/CPU, WAV SHA, project reopen and accepted audio lineage.
- New 50th workflow plus all 49 inherited at exact implementation and separate validation successor HEAD before expected-head merge.

**This step only provides a lower-level, non-user-facing safety primitive.** / 실제 사용 가능한 대용량 업로드 기능이나 범용 DAW 완성으로 표시하지 않습니다.
