# PROD-E2E-R1A — User WAV Import to Trusted Preview / 사용자 WAV 가져오기

**State / 상태:** DRAFT implementation and CI under [#181](https://github.com/Eckommon/MUSICA/issues/181); this is not yet a validated real-Chromium or production-quality user journey.

## Goal / 목표

Allow the user to choose a real local WAV in MUSICA Studio, preserving the distinction between an immutable **imported resource** and an **accepted creative audio track/clip**. This closes a known gap in ATCM-R3 Browser where the Add Clip UI demanded an already-imported content-addressed Asset ID.

## UX / 사용자 조작

1. Open/create a local Studio project; navigate to Inspect → Native Audio.
2. Under **Import WAV / WAV 가져오기**, select a mono/stereo uncompressed integer-PCM WAV (8–192 kHz; 1–4 bytes per sample) with a positive frame count and a file size between 44 bytes and 16 MiB. The file bytes are sent via direct same-origin `audio/wav` POST; arbitrary server filesystem paths are not accepted. Other formats fail visibly; no hidden transcoding/resampling is performed.
3. Read the returned exact content-addressed `sha256:...` Asset ID, sample rate, channels and duration. The Import control pre-fills **Add clip → Asset ID** and Source out fields.
4. **Preview add track** (no audio yet) → **Accept native Preview**, then **Preview add clip** on that track → audition → **Accept native Preview**. Each accepted revision advances only through trusted source-bound R1/R2 audio edit authority. Import itself never advances the accepted creative revision. Existing native-audio controls allow mixer/clip edits, while other product stages are separate.
5. Export/reopen the project after Accept; accepted asset metadata and bytes remain content-addressed and verifiable.

## Exact API / 검증 범위

- `POST /v0/sessions/{session_id}/audio/import-wav`, request: `Content-Type: audio/wav`, direct bounded binary body and Content-Length. Response contains `classification=IMMUTABLE_AUDIO_ASSET_NOT_ACCEPTED_CLIP`, `asset`, exact accepted revision, `accepted_revision_unchanged=true` and the separate Preview/Accept requirement.
- Reject unknown sessions, malformed/unsupported WAV, unsupported content type, chunked/no Content-Length, body lengths below 44 bytes or exceeding 16 MiB, and import during a pending Preview. No client-supplied local path field. Re-importing exact same bytes is idempotent.
- Empty-track Preview is allowed as *not audible* rather than failing or pretending to render media. Any candidate with actual clips still requires real render; render errors do not silently fall back to silence.

## Explicit limits / 비지원

**No claim of actual Chromium validation until that run exists.** HTTP authority/packaged JavaScript smoke tests are not user-click proof; a real browser test must actually choose a file, observe the asset, Preview, click Accept, export and reopen. This is a resource ingest feature, not physical microphone recording, actual third-party VST/CLAP/AU hosting, full 48kHz hardware output, time-stretch or mastering-grade sound quality. There is no server filesystem browse/upload path. The 16 MiB v0 cap is intentional; large sessions need a separate streamed ingestion design.

## Release gate / 승격

- Dedicated R1A tests, inherited ATCM-R3/R2/R1, project integrity and real Browser Chromium evidence, then full 43/43 workflow promotion on a head that includes R0. Bilingual durable proof and successor 43/43 before expected-head merge.
- Parent #178 and follow-on R1B remain OPEN until a genuine user-operated end-to-end song workflow is validated.
