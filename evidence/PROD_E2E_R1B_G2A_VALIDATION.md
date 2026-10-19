# PROD-E2E-R1B-G2A verification / 라우팅·자동화 상태 표시 검증

## Exact implementation / 구현 검증 기준

- Implementation SHA: `42430346e882326caf29a280de74d0b103eec684` on PR #188 (issue #187).
- Verified first **46/46 GitHub Actions workflow runs completed SUCCESS** at exactly that SHA. The new dedicated workflow `PROD-E2E R1B G2A Source-Bound Routing Automation Status` also passed.
- Official predecessor G1 main: `7f4817aa2f9f0e110e96e13b4488b2d19c3b02aa` (PR #186 merged, issue #185 closed).

## What is proven / 실제로 검증된 기능

- Browser first-party `/assets/app.js` serves source-bound read-only one-song guide progress. UI checks session identity AND accepted revision identity against both routing and automation views; absent or outdated views return **UNAVAILABLE / UNKNOWN**, not reported success.
- Explicitly accepted routing graph/outputs, native mixer automation lane identities, and automation lanes appear as derived status only. Accepted audio/asset/track/clip and final WAV source lineage remain under their existing independent authority.
- JS parser and dedicated HTTP first-party asset regression passed; inherited 45 workflows were preserved and green.
- No UI automation, renderer output or AI content is granted creative Accept authority.

## Evidence limits / 증거의 한계

- G2A **does not** include a real Chromium scenario exercising live routing and automation edits or sound-altering outputs. It proves static syntax, first-party serving and source guard predicates, not actual two-track routed sound or audible automation.
- No human usability test, real microphone/interface callback, professionally mastered full song or actual external VST3/CLAP/AU plugin binary is proven.
- Issue #187 remains OPEN until an operator Browser routing/automation Preview → Accept → audible PCM → export/reopen roundtrip is independently evidenced.

## Promotion / 안전한 병합

This documentation commit is the **validation successor**, and must run all **46** permanent workflows again at the successor exact SHA. Do not merge until 46/46 SUCCESS on that successor, then mark PR #188 ready and guarded squash merge by expected HEAD. Never waive inherited CI.
