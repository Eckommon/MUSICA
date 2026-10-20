# PROD-E2E-R2A-G3A — Standard-Resolution Browser Production Validation / 44.1·48kHz 실제 음악 제작 검증

## Source of truth and gate / 정본·검증 범위
- PR **#194**, Issue **#192**. Source main `72c528eaf61894252348fdf6f63066969d2f8258` after accepted G2C #193.
- **Exact tested implementation HEAD: `f68661b34148c36995a4d603365dbd4b84e8d9ec`**.
- **49/49 GitHub Actions completed SUCCESS** on that SHA including real Chromium dual-rate matrix run **`39451442626`** and all inherited 48 CI workflows. No waived checks. This document is an evidence **successor** and requires a **second 49/49 exact-head validation** before guarded promotion.
- Parameterized trusted preexisting G1 Browser two-WAV file-picker import / two-track Preview→Accept, G2B two-bus/master Preview→Accept, G2C user-created first mixer gain automation lane Preview→Accept, accepted WAV download, `.musica` export, Chromium/Studio restart and byte-exact reopened output. / 사용자가 각 단계를 별도로 승인해야만 창작 상태가 변경됩니다.
- Backward 8kHz default remains unchanged. Exact source matching is required: mixing 44.1kHz and 48kHz source rates is explicitly rejected with no silent resampling, independently checked by unit contract. / 암묵적 리샘플링 불허.

## First-party Browser 44,100 Hz / 44.1kHz 실증
- Dedicated run `39451442626` matrix 44100 **SUCCESS**, artifact ID **`12278032567`**, name `musica-prod-e2e-r2a-g3a-44100`; ZIP SHA-256 **`2c8f3e54eb98f3fabd6d3d7f7bd9ddc2c7dca20b1658936bd5b3d7fc122fc41c`** (independently downloaded and matched provider digest), archive size **7,339,480 B**.
- WAV `standard-accepted.wav`: SHA-256 **`f61c9b0e5f5f7c6e93feeca53f6395ef73f6d4a2d98a68779637d704be5c0c75`**, size **2,116,844 B**, stereo **PCM16 44,100 Hz**, 12 seconds, **529,200 frames**. `standard-reopened.wav` **byte-exact identical**.
- Left-channel gain automation window peaks **[1064, 836, 656, 515, 425]** decrease through the source; untouched right channel **[6200,6200,6200,6200,6200]**. Peak 6200, clipped scalar samples **0**. Three actual Chromium PNG screenshots + JSON provenance proof.
- End-to-end automated Browser proof wall time ~**77.995 sec** (CI runner timing, **not measured local DAW latency or realtime performance**).

## First-party Browser 48,000 Hz / 48kHz 실증
- Dedicated run `39451442626` matrix 48000 **SUCCESS**, artifact ID **`12277788200`**, name `musica-prod-e2e-r2a-g3a-48000`; ZIP SHA-256 **`aa5033f2c4184340ec4dac7ee7c2b12fbaac3daa79496d6b29bc1c0392a9f4d0`** (independently downloaded and matched provider digest), archive size **7,337,820 B**.
- Accepted WAV SHA-256 **`ba0c3f29bad7235345f62181600f2e61002d8e24a372ed3446ce2c369194d280`**, size **2,304,044 B**, stereo **PCM16 48,000 Hz**, 12 seconds, **576,000 frames**. Reopened WAV **byte-exact identical**.
- Left-channel gain peaks **[1064,836,656,515,425]**, right constant **6200** in all five windows, absolute peak 6200, clipped scalar samples **0**. Three real Chromium PNGs + JSON proof. Automated CI workflow time **81.21 sec**; not a realtime audio-device latency measurement.
- Both tested two distinct imported **2-second mono user-picker WAV fixtures**, accepted into separate tracks with stereo pan and bus + gain automation. The song timeline lasts 12 seconds, not two 12-second recordings.

## CI-discovered lifecycle issues and corrections / 발견·수정한 결함
- Original dual-rate CI blocked 44.1k gain-lane Preview and 48k bus Preview under short default 5-second assertions. Added **bounded 90-second** Preview/Accept gates for standard-rate heavy CPU projections only; retained original 8k thresholds.
- 48k new-lane eligibility could remain disabled when accepted automation and native audio state loaded before routed view. The trusted routing surface now dispatches read-only `musica:routing-view-ready` **after accepted routing GET projection**, and automation editor reacts only for matching session, re-evaluating exact accepted routing/audio/automation revision eligibility. **No auto Accept, no fabricated graph or lanes**.
- The latest test explicitly awaits matching accepted native audio/routing/automation **same session/revision**, no pending Preview and an accepted routed clip before judging the first-lane button. Failure path saves source snapshot and screenshot; tests do **not** bypass the button or change canonical authority.
- 49/49 CI final implementation SHA green including both actual Chromium matrix jobs and full Python 3.11/3.12 MUSICA CI.

## Product limits and next implementation / 제품화 한계·후속 과제
- **Not full-song ready:** two 2-second synthetic PCM sources within 12-second project; no real human or studio recording, no mastered multi-minute material.
- Native mixer and importer reject unlike sample-rate combinations; no SRC implemented. Browser import remains **16MiB total** per WAV, so 3-minute 48kHz stereo PCM16 exceeds capacity. Native and routed mixer currently decode full source and construct in-memory PCM frames; CPU/memory are not yet proven for >=3 min.
- G3B on #192 must provide **bounded streamed/chunked content-addressed import, partial failure cleanup, memory/CPU proof at >=3 min and >=2 tracks**. Preserve exact source hash, immutable CAS, Preview≠Accept. Audio-device ASIO/WASAPI callbacks, external plugin binaries, Windows install, AI creative quality and real-user study remain separately unproven.

## Promotion conditions / 병합 게이트
**This evidence commit must pass all 49 workflows anew at its exact SHA.** Only then mark PR #194 ready and squash merge guarded by exact expected head, verify new canonical main, and leave Issue #192 OPEN for G3B. No premature claims about full-length DAW readiness.
