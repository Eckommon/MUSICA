# G3B3-R1A — first real editable 180-second Browser song / 실제 브라우저 믹서 A/B 편집 검증

**STACKED DRAFT** on G3B3-R0 PR #216 evidence successor `f4c9f94cb29629c4507e1e0ae5c5a23da817c2c5`. Parent Issue #217 / product loop PR #218. R1A must not merge until #216 has guarded-promoted, the product-goal ledger has been reconciled and this PR is clean-rebased onto the new canonical main.

## Why this slice / 격차
G3B3-R0 proves that the user can import two independent 180s WAVs in first-party Chromium, Preview→Accept tracks and clips, download the resulting accepted WAV and reproduce its SHA after restarting Studio. **It does not show that the user can actually edit the 180s mix, hear an alternative before Accept, compare and discard it.** R1A closes that distinct P0 user-workflow gap without pretending to solve routed automation or archive roundtrip.

## Real first-party Browser steps / 구현
1. Call the already verified G3B3-R0 Browser scenario to create and reopen two independently user-file-selected 180s 48k stereo 16-bit PCM WAV sources (A `2000,-1000`, B `1200,-400`) with four explicit track/clip Accept actions. Original output SHA is recorded.
2. Reopen the same project in **actual Chromium Studio inspector**, select track A mixer gain using its visible input and click `Preview mixer` (first -3 dB). The accepted HEAD remains unchanged. Browser HTMLAudioElement must compute **180 seconds** for the genuine source-bound candidate `/audio/stream/preview.wav?preview_id=...`. A real HTTP 206 range reads a sample different from the accepted `(3200,-1400)`.
3. Click visible `Discard native Preview` and prove original accepted HEAD is preserved and the discarded Preview URL returns HTTP 404.
4. Use the same first-party `Preview mixer` control with track A -6 dB. Sample the actual candidate HTTP 206 Range output at 0, 90 and 179.999 seconds; expected stereo PCM **`(2202,-901)`**, and all three Range requests must have the same SHA-derived ETag. Assert parent HEAD unchanged while `PREVIEW · NOT ACCEPTED` is visible.
5. Click visible `Accept native Preview` exactly once. Now and only now accepted HEAD may advance. The first-party user-clicked accepted WAV download **must** equal the earlier candidate ETag SHA, be 34,560,044 bytes with 8,640,000 frames and PCM `(2202,-901)` at all three positions.
6. Restart both Browser and Studio, reopen the same edited project via first-party UI, download again and compare exact SHA and accepted revision. Upload full WAVs, screenshot(s), browser errors and proof.json for independent audit.

## Strict exclusions / 미완료·다음 단계
- Synthetic PCM test inputs in real UI are **not** human musical composition or human listening evaluation.
- This is **native mixer** A/B only. Routed bus/automation UI Preview→Accept and **real .musica archive export/import** remain Issue #217 follow-up R1B/R1C; source workspace restart is not archive roundtrip.
- No actual AI generation quality, physical sound interface latency, native VST3/CLAP, Windows installer or commercial usability claim.
- Dedicated full-workflow CI is newly added and **has not yet passed**; do not merge with failed/incomplete inherited gates. Require independent WAV/SHA/PCM audit, bilingual evidence successor full CI and expected-head guarded squash after all dependencies officially merged.
