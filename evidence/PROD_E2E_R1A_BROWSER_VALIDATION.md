# PROD-E2E-R1A Validation / 사용자 WAV 가져오기 검증

**Status / 상태:** Validated implementation evidence at exact Git head `0374b36bade81ed7d993e791330ac04145eb033b`; **successor CI and merge pending**. Date / 기준일: 2026-10-18.

## Source and full CI / 검증 근거

- PR: https://github.com/Eckommon/MUSICA/pull/182; issue https://github.com/Eckommon/MUSICA/issues/181; canonical predecessor R0 main `d9f929e4e7a4a7abde09d20522d1990b438677b2`.
- All **43/43 GitHub Actions workflow runs** associated with the exact implementation head completed with `success`, including inherited suites. This means only the exercised contracts passed.
- Dedicated real Chromium workflow: https://github.com/Eckommon/MUSICA/actions/runs/39024491858 ; job `117372685565` passed: dependency setup, JS syntax, HTTP/authority and inherited ATCM tests, Python compilation, Playwright Chromium installation and browser click-through.
- Run artifact `12098650495` (`musica-prod-e2e-r1a-user-operated-wav`), archive SHA-256 `fa32a87cb251cdfcd397fec0098a7f64af3061e8c86dd05db913641f38a270c2`. GitHub digest agrees; independently downloaded/inspected artifact as recorded at https://github.com/Eckommon/MUSICA/issues/181#issuecomment-6232846222. Five Chromium screenshots and `proof.json`; browser console errors=0, page errors=0, failed network requests=0.
- Imported resource `sha256:a6f58eba0333393812718520db4a65cdfabeab09e7449ab01a2b608ba373b013`; accepted and reopened WAV hash `8cdd36cab6a0b6b6969a8adaed461a53b77d5c245daa566826315156f2beb99b`.

## Actual operator-control path / 실제 Browser 제어 경로

1. Create Studio song project and select `my-melody.wav` through Chromium file picker.
2. Import bounded same-origin WAV bytes to an immutable content-addressed project resource. Verify accepted creative revision **does not change**; this is not an accepted track or clip.
3. Make empty-track **Preview**; no fabricated playable audio and no accepted revision change. Click separate native **Accept**.
4. Make clip **Preview** using imported asset; check playable audition without accepted revision change. Click separate native **Accept**.
5. Export; restart browser/server and reopen same project; verify exact accepted revision, content-addressed resource and derived WAV hash.

## Explicit boundaries / 비지원 및 제한

- Automated Playwright interactions with actual Chromium are **not a human usability study**.
- The imported fixture is a short mono 8 kHz PCM WAV. No proof of long-form musical quality, 48 kHz physical sound-card operation or live microphone recording.
- No genuine VST3/CLAP/AU plugin binary executed. Browser import has a 16 MiB cap; no arbitrary server file path, silent resampling or automatic Accept.
- R0's 12-second two-track scripted offline project and R1A's browser WAV import are **separate proof scenarios**; neither alone proves a complete user-created multitrack song in the Browser. R1B remains next.

## Promotion rule / 병합 기준

This document is an evidence-successor change and causes new workflow runs. **Do not merge based on the predecessor's 43/43.** Require all 43 workflows to succeed on the exact document-successor head; inspect any failure rather than waive it; then mark PR ready and expected-head squash merge. Keep parent issue #178 open for guided R1B. After merge, update canonical README/working memory independently with fresh verified SHA.
