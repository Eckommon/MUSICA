# G3B2C-R3 — bounded Studio 180s source projection validation / 장시간 조회 검증

## Canonical ancestry and CI / 정본·검증 이력
- Parents #209/#207/#205/#201/#195/#192. R1 guarded merge PR #206 `79d27e0d6ae79f053b25f5211e946ca0770c6c73`; R2 guarded merge PR #208 `fe8f842cdd7612d05f5d9cc843835f6d8d88f6bb`.
- Original stacked implementation `674dfd13268e782648958f0296415b0c39708353`: **57/57 GitHub Actions workflows SUCCESS, 61/61 check runs SUCCESS**. Earlier implementation `5c7cb445ee538b98291f67c9de338edebf77708a` had an inherited Python 3.11 missing-Playwright failure; corrected by using `pytest.importorskip("playwright.sync_api")` in generic matrix while permanent R3 workflow installs actual Playwright+Chromium and executes the real browser test. No gate skipped.
- R3-only 8-file rebase onto promoted R2 main: exact implementation `be7e6746f972832840bc77835d04876a0e7f45d5`. **This new rebase full 57-workflow CI is separate and must succeed before promotion; previous 57/57 does not substitute for it.**

## Independently inspected real Chromium artifact / 실제 화면 증거 독립 검사
- Dedicated original implementation workflow [#39857609352](https://github.com/Eckommon/MUSICA/actions/runs/39857609352): SUCCESS, artifact ID `12463988353`, ZIP SHA-256 **`5b1c33d3871391ef46a75a055f8bd6c2fe70a022947f9bef534e1a4bef3f2428`**. ZIP contains a 2,167,259-byte actual Browser screenshot `01-real-chromium-180s-native-stream.png` and `proof.json`. Independently opened and inspected screenshot and parsed JSON.
- JSON confirms browser reported **exact 180-second WAV metadata**, first-party accepted Range audio player active, two **distinct accepted** 180s stereo PCM source assets, accepted revision `rev-audio-bd68cb08f953bd30bbd7d7dd84412e79`, and **HEAD unchanged**. This is a real headless Chromium Studio UI check, **not** a full-length listen through physical speakers nor human-based user acceptance.
- Test executes a real `create_local_server` localhost HTTP source and waits for Chromium `HTMLAudioElement.duration` to be 180. Browser screenshot shows the native accepted player and its explicit streaming classification.

## Code scope and precise limits / 기능과 잔여 위험
- Studio Native/Routing **read-only** accepted and candidate metadata projections exceeding 16 MiB never call the legacy full-song Python float-array/`wav_bytes` renderer. They return truthful null WAV hash with accepted-only streaming classification, and Browser accepted-player binds to the file-backed R1+R2 Range endpoint.
- Pending long Preview in R3 is clearly marked unavailable: it is not falsely rendered as accepted audio and never advances canonical creative HEAD. Real pending long Preview streaming belongs to R4 Draft PR #212.
- Short-song accepted and pending Preview still use established legacy WAV parity and no silent Accept. Global Project verification can still read CAS assets; 180s user-operated source import/Preview/explicit Accept/export/reopen and full commercial DAW performance are **not proven**.
- External audio hardware, device low-latency, real VST/CLAP plugin binaries and human pilot remain unverified.

## Promotion barrier / 실제 병합 조건
This document-bearing successor is not approval. On its exact SHA require **57/57 distinct workflows and all 61 checks SUCCESS**, confirm canonical main remains R2 merged and exact PR HEAD, then mark ready and expected-head guarded squash; keep parent #209/#211/#205/#201/#195/#192 open pending full end-to-end G3B3.
