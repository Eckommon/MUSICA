# PROD-E2E-R1B-G1 — Two-source Browser Mix / 두 개 오디오 소스의 Browser 믹싱

**Status / 상태:** DRAFT, new real-Chromium CI not yet accepted. Issue #185 under #181/#178. Base: G0 validated main \`508163cdc1c727742d1adee560e8e672ec205b08\`.

## Product UX / 사용자 제작 흐름
1. Open/create project in Browser, Inspect → Native Audio. Import one mono/stereo PCM WAV as immutable resource.
2. Click **Next unused track ID**, rename source track, Preview → separate trusted **Accept**. Click **Next unused clip ID**, select a track, Preview → separate **Accept**.
3. Import a **different** WAV. Both IDs are suggested **from accepted material only**. Repeat for another track/clip; preserve chosen clip destination across view updates. No silent Accept, renumbering of accepted IDs or generated track from file import.
4. Adjust per-track gain/pan/mute/solo with existing trusted mixer Preview/Accept. Exact accepted mix WAV can be downloaded separately from \`.musica\` export; delivery blocked while Preview pending.
5. Reopen and confirm two exact asset SHA-256 identities, two tracks/clips, mixer settings, derived PCM and accepted HEAD.

## Executable proof / 검증 설계
The G1 fixture imports two distinct **8kHz mono PCM16, 2 seconds** user WAVs, makes two accepted tracks and two accepted clips, then pans each track hard left/right via individually accepted mixer edits. Independently compare every source-active PCM frame of final stereo WAV to the two source sample streams in their isolated channels; check 12-second exact frame count, peak, clipped sample count, SHA and reopen byte identity. Run true Playwright Chromium user controls and permanent 45th CI.

## Nonclaims / 제한
No proof of original creative sound quality, commercial-length song, physical audio devices, microphone, VST/CLAP/AU plugin execution or human usability. G1 does **not** imply completion of accepted routing, canonical automation and plugin bus processing in a fully guided song workflow. Follow-on R1B stages remain OPEN.

## Promotion / 승격
Exact G1 implementation SHA **45/45 workflow SUCCESS**, independent artifact download SHA/PCM inspection, durable validation evidence committed, successor exact SHA **45/45 SUCCESS**, guarded expected-head squash merge. No inherited gate waived or missing hardware capability misrepresented.
