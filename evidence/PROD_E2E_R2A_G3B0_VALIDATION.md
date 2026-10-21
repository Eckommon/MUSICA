# PROD-E2E-R2A-G3B0 Validation / 대용량 WAV 안전 업로드 검증

## Exact canonical context / 정본
- Source canonical main after G3A #194: `7c74296fa63319c7d301d22c1589b5a53b091502`.
- Draft PR **#196**, parent G3B Issue **#195**, R2A Issue **#192**. This is a staged transport product increment, not the entire G3B acceptance.
- Verified **implementation exact HEAD `f21c4f166a7ed49ad514562ca05e9690b64e6ebb`**: **50/50 permanent GitHub Actions workflows completed SUCCESS**, including all 49 inherited tests, dedicated new G3B-0 workflow `39547516065`, existing G3A real 44.1/48kHz Chromium, and Python 3.11/3.12 `MUSICA CI`.
- This durable document creates an evidence **successor commit that must independently achieve another 50/50** before guarded expected-head squash merge. No bypass or skip.

## Real first-party Chromium integration / Browser 실제 조작
- Dedicated run `39547516065` concluded **SUCCESS**, permanent 50th CI checks old 16MiB direct import compatibility, new staged HTTP resource authority, typed Browser JavaScript syntax and actual Chromium user WAV file selection.
- Real chosen WAV source: **17,200,044 bytes** (>16MiB), **48,000 Hz stereo uncompressed PCM16**, **4,300,000 frames = 89.583333 seconds**. Source SHA-256 **`64e5adf6f846a73d890899b57ef19a11b43aaf5297791fb2c597fd6d34576fa3`** independently recomputed from the exact deterministic source bytes. This is a test source, not a user-composed commercial song.
- Upload route validates whole-file SHA-256 and 1MiB chunk SHA-256/offset/order; Browser receives asset ID `sha256:64e5adf6f846a73d890899b57ef19a11b43aaf5297791fb2c597fd6d34576fa3` from trusted CAS and displays **NOT A CLIP**. Accepted project HEAD stays identical; no track or clip is created automatically; existing audit chain receives exactly one imported-resource event. No remaining staging temp files and project integrity reports PASS.
- Independently fetched artifact `12322820616` (`musica-prod-e2e-g3b0-17mib-staging`). ZIP SHA-256 **`a8947ea8ab70012ed8f860c24d8e42506979e7dd1f8b9039c49080fc8db19271`** matches GitHub artifact digest. Archive contains actual full-page Chromium screenshot `01-user-picked-17MiB-wav-resource.png` (2,062,909 B) and `proof.json`; proof confirms source bytes/hash/rate, 64MiB ceiling, original accepted HEAD unchanged, immutable resource, no accepted clips or track, no residual temporary files. The 17MiB source WAV is reproducible from recorded deterministic fixture rather than duplicated as workflow artifact.

## Adversarial and failure checks / 실패·보안 검증
- 1MiB maximum chunk request size, 64MiB per source, one live upload per local Studio session, four live uploads per server, opaque random server-side temp token and server-owned paths (no user-selected host path). 15-minute idle timeout cleanup and old orphan expiry handling.
- Tests fail closed on wrong or stale session, concurrent uploads, incorrect offset, incorrect per-chunk SHA, incomplete/mismatched declared whole-file SHA, oversize, and explicit cancellation. No imported asset, audit or accepted clip appears from these failures.
- An additional *real HTTP half-close* test sends a chunk declaring 100 bytes but delivering 10 bytes, verifies HTTP 400 and **immediate staged file deletion** rather than leaving partial untrusted data until TTL. Legacy direct import remains independently capped at 16MiB; it is not silently widened.
- User's Browser first-party File.slice upload checks per-chunk server next_offset and accepted_revision_unchanged. Separate Preview and explicit Accept are still mandatory for any creative track/clip change. AI/browser transport cannot auto-accept music.

## Honest product limits / 제품화 한계
- **G3B-0 is bounded staged transport, NOT memory-safe end-to-end streaming storage**. Browser still computes overall SHA through bounded whole-file `File.arrayBuffer()`; final server step reads up to 64MiB via `read_bytes()` and existing `import_audio_asset_bytes`. The G3B-1 milestone must replace this with streaming hash + content-addressed atomic finalize/rollback.
- Existing `native_mixer.py` and `routed_mixer.py` use full-frame Python memory materialization. Neither two **three-minute 48kHz recorded sources** mixed into a ≥3-minute song nor CPU/RSS targets, physical interface latency, external plugin binary, original AI music quality, or human usability has been demonstrated. G3B-2 and G3B-3 remain OPEN under Issue #195.
- The test used a **12-second empty song project only to verify resource import**, with one 89.58-second source WAV; this is expressly **not** a 89.58-second accepted musical arrangement.

## Promotion gate / 병합 조건
Complete all **50/50** on the evidence-successor exact HEAD. Only then mark PR #196 ready and expected-head squash merge. Verify canonical main and keep #195 / #192 open for G3B-1 staged streaming CAS and G3B-2 memory-bounded three-minute production.
