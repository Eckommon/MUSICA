# PROD-E2E-R2A-G3B1A — Verified streamed WAV asset CAS / 3분 오디오 자산 저장

**Dependent DRAFT implementation** after G3B0 PR #197; issue #195, parent #192. Use final merged G3B0 main as canonical base before promotion.

## Added / 구현
- `audio_assets.import_audio_asset_verified_path` accepts a **trusted server-private verified staging path only**, never a user-submitted filesystem path. It streams SHA-256, validates WAV PCM with at most 65,536 frames in each inspection step, and copies into a private CAS temporary file in 1MiB chunks. An atomic no-overwrite link publishes the immutable object only if the full copy matches the declared digest. Existing CAS object corruption is an error, not silently healed. An asset descriptor and existing audit binding follow the object, with idempotent verified reimport.
- `read_audio_asset` now verifies source objects with streaming file hashes and bounded WAV reads rather than `Path.read_bytes()` and whole-frame decode. This improves repeated asset listing and integrity verification for long recordings.
- New integration test creates a real **3-minute 48kHz stereo PCM16 WAV (~34.56MB)**, stages it through G3B0 1MiB chunks, verifies full content SHA-256, registers as a noncreative audio resource in a real Studio project, checks asset metadata and immutable object, retries idempotently, cleans staging and confirms accepted creative HEAD remains unchanged. Bad digest / invalid WAV imports must not create asset descriptors.

## Not yet provided / 미완료
- **No Browser or HTTP staged upload route yet.** This is a trusted internal file-to-CAS bridge only; a verified staged path is never accepted from a client.
- Asset metadata/audit are written using existing trusted primitives but there is not yet a recovery-journal transaction for unexpected disk failure midway through object+descriptor+audit publication; add crash-recovery and orphan cleanup before user-facing finalize.
- Mixer native/routed rendering still materializes full PCM frames and is **not proven memory-safe for 3-minute two-track songs**. No actual 3-minute Browser song or hardware recording proof.
- Next: session-scoped bounded HTTP begin/append/finalize/cancel, user File.slice() transport, expiry and cleanup, then bounded PCM mixer/long-song real Chromium proof. Preserve explicit Preview→Accept creative authority throughout.

## Safety promotion / 검증
New 51st permanent dedicated workflow plus all prior 50 workflows must succeed at exact implementation head; evidence successor 51/51 and guarded merge. Do not close #195.
