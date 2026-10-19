# PROD-E2E-R1B-G2C validation / Browser 첫 자동화 레인과 실제 시간별 음량 검증

## Exact scope and implementation gate / 정확한 증거 커밋

- PR #191, scoped issue #190; parents #187/#181/#178 remain OPEN.
- Predecessor G2B PR #189: exact durable successor `991ea4b0f5ba3c10942d6debef0927d460d8592d` achieved **47/47 SUCCESS**, expected-head squash canonical main `053b4f15ba8c7e6c2c4caa5bdcb9d0a1210389d9`.
- **Exact G2C implementation HEAD** `2abb69d85564268c95c0434d5cacb870fd9b700b` succeeded **48/48 GitHub Actions workflows** including new real Chromium G2C dedicated run **39185798279**. No inherited workflow waived.
- **This validation document creates a successor HEAD**; **the entire 48/48 must pass AGAIN on that exact successor commit** before ready-for-review and guarded expected-head squash merge. The G2C source branch was regenerated directly from the official G2B-merged main to avoid stacked duplicate changes.

## Actual user-operated flow and trusted authority / 실제 Browser 사용 흐름

- First-party Browser M7 Automation exposes first native gain lane for a G2B **two accepted WAV tracks + two buses + master** project, with user-selected track, start/end dB and end beat, fixed-tempo validation. Previously M7 could only edit a lane that already existed.
- Uses existing trusted typed `ADD_LANE` Preview and separate explicit user **Accept**. UI checks exact native-audio/routing/automation **session and accepted revision**, accepted clips/graph and absence of pending Preview. No AI/device/Browser state can auto-commit.
- Real Playwright Chromium exercise starts from **two independently imported distinct user-supplied WAV resources**, six G1 Previews/Accepts and two G2B routed bus Previews/Accepts. Then **clicks first native gain automation Preview**, confirms accepted HEAD unchanged, clicks generic Accept separately, downloads accepted WAV and exports/reopens the project. Neither importing WAV nor Preview changes accepted HEAD.
- Dedicated test includes actual Browser screenshots of Preview state, approved automation and reopened output. This is **automated real Browser operation**, not a real human usability study.

## Independent artifact and PCM numerical verification / 독립 수치 검사

- Dedicated artifact ID **12158505310**, archive **7,783,814 bytes**, GitHub digest and independently verified ZIP SHA-256 both `47da0ad47076c08785a786740fdbc6f4d3cc63be06c845aac174dc904b62ea2c`.
- Archive contains **3 real Chromium PNG screenshots, proof.json, automated-accepted.wav and automated-reopened.wav**, WAVs **384,044 bytes** and byte-identical.
- Baseline separately downloaded from G2B evidence: stereo WAV SHA-256 `dd16529019d259a39a64a2b97b11fa10a7edda198379d253eee3a5f1492cbad0`.
- Accepted G2C native automation WAV SHA-256 `42b6fcb45e8ba3626355405e07a1cff0ff9aca7ef8c550230fcd7b9b72eaa23a`. Format **8kHz, stereo PCM16, 96,000 frames = 12 seconds**, independently decoded with Python `wave` + `struct`: left peak **1,064**, right peak **6,200**, **0 clipped**.
- **All 96,000 right-channel PCM frames are exactly identical** to independently retrieved G2B baseline; left channel audibly changes over time: amplitude ratio vs G2B baseline at 0.1s **0.62234**, 0.2s **0.54654**, 0.3s **0.48072**, 0.5s **0.37168**, 1.2s **0.35439**. This proves native track gain envelope affects the actual routed output, not just a UI label.
- Browser console/page/network errors **0**. Project reopen produces identical accepted WAV bytes and accepted HEAD.

## Proven limitations / 제한

- Two *short synthetic* 8kHz WAV source fixtures in a 12-second timeline, not a finished user-composed song, 44.1/48kHz physical callback/mic, actual VST3/CLAP/AU plugin binary or human usability test. No professional mastering claim.
- 16MiB first-party Browser import cap is insufficient for a whole stereo 48kHz 3-minute WAV take; distinct longer/higher-resolution import/performance validation is tracked in issue #192.
- Subsequent scope: G2D Browser accepted simulated bus plugin/A/B integration if topology supports; #192 quality-rate offline and streaming source; real physical hardware/plugin ABI separately. Keep #187/#181/#178 OPEN.

## Strict promotion / 승격 기준

1. First implementation exact 48/48 SUCCESS and independently inspected ZIP/PCM: **satisfied**.
2. This durable-validation successor exact **48/48 SUCCESS**: **pending at document authoring**.
3. Re-check PR HEAD/mergeability and canonical main; mark PR ready and expected-head squash merge only when #2 complete. Never waive CI or replace missing physical/user evidence with simulation.
