# PROD-E2E-R1B-G2C validation / 실사용 자동화 레인 Browser·PCM 검증

**Validated exact implementation commit:** `362bf1600737472924b434643556df853322f1cb`
**Pull request:** #193; **parent issues:** #187, #181, #178.
**Implementation gate:** 48/48 GitHub Actions workflows **SUCCESS**, including dedicated real Chromium run `39413580318`, inherited G2B run `39413580227`, and the full MUSICA test matrix. This validation file creates a new successor HEAD which **must** independently achieve 48/48 before guarded merge.

## Validated user-operable scope / 직접 조작 흐름
- On a real automated Playwright **Chromium** Browser session, first-party controls load a previous G2B accepted 2-WAV/2-bus project, create a *new* audio-track gain automation lane on `AT-UI-001` with user-chosen `-3 dB` start and `-12 dB` end, Preview it without mutating accepted HEAD, then **explicitly Accept**.
- This fixes a genuine first-lane usability defect: the creation form had been nested inside a workspace hidden whenever `materials.automation` did not yet exist. The form now resides outside that hidden workspace; its eligibility is still restricted to matching accepted audio/routing/automation source revision and eligible routed clip tracks. An unaccepted first lane displays **PREVIEW · NOT ACCEPTED**.
- The trusted typed `ADD_LANE` authority remains the only candidate pathway; browser state, AI, rendering and media have **no implicit Accept authority**. A separate acceptance changes the canonical project revision.
- Export `.musica`; restart Chromium/Studio; reopen exact accepted HEAD and download byte-identical rendered WAV. Real Browser automation, not real-person usability study.

## Independent artifact and PCM audit / 독립 증거 분석
- Dedicated run `39413580318` SUCCESS, artifact ID **`12261035301`**, artifact `musica-prod-e2e-r1b-g2c-gain-automation`, ZIP **7,683,638 bytes**, independently downloaded ZIP SHA-256 exactly **`a2b9e748ed4dc8f3bc6ea4293f10b514a6013345996c915a9348e25d8931b42f`**, matching GitHub artifact digest.
- ZIP consists of **three actual Chromium PNG screenshots**, `proof.json`, `gain-automated.wav` and `gain-reopened.wav`.
- Independent Python `wave` / `struct` inspection: WAV SHA-256 **`e72eef3dd00fc4ce90d5b34375b224f8070afedcf4a0095ce5d928e854122b6c`**; both exports byte-identical, **384,044 bytes** each; stereo **PCM16 @ 8,000 Hz**, **96,000 frames = 12 seconds**; scalar samples nonzero **32,000**, absolute peak **6,200**, clipped **0**.
- First audio source left-channel localized frame-window peaks at frames [0, 3,900, 7,900, 11,900, 15,000] are **[1,064, 841, 660, 519, 430]**, decreasing with the automated gain envelope; right-source channel corresponding peaks remain **[6,200, 6,200, 6,200, 6,200, 6,200]**. Dedicated trusted Browser oracle additionally checks that the automated WAV differs from its pre-automation routed baseline and the other source's PCM remains exactly unchanged.
- All accepted HEAD / Preview non-mutation, exact sample format, user-selected lane and output/reopen assertions passed the dedicated Chromium test.

## Corrected inherited regression and CI environment / 추가 결함 정정
- Under the heavier G2C UI, inherited G2B Chromium sometimes observed the prior **accepted routing projection** immediately after Accept, before the latest accepted `-6dB` node mixer view finished refreshing. Corrected G2B regression to wait for the exact **server accepted revision ID AND the -6dB mixer value**; this strengthens the authority check, not relaxes it. Subsequent inherited G2B Chromium run passed.
- One inherited Post-M7 workflow initially stopped **before tests** while installing Chromium when a third-party Microsoft Ubuntu apt source returned **403 Forbidden**. Reran only this demonstrably transient failed job without changing code or waiving any checks; all Post-M7 tests subsequently completed SUCCESS. Final exact implementation SHA: **48/48 SUCCESS**, no skipped gates.

## Honest limits and next priorities / 실제 한계
- This is **12-second 8kHz deterministic bounded fixture sound**, not a complete user-produced song, measured musical quality or real-time 44.1/48kHz device callback. Source files are synthetic user-picker supplied PCM fixtures exercised through real automated Chromium controls, **not evidence of human usability, original AI music quality or live recording**.
- No third-party licensed CLAP/VST3/AU binary, microphone, native ASIO/WASAPI device latency, complex plugin graph, professional mastering or installer proven. Parent #187 remains OPEN until separately demonstrated remaining operator plugin integration and other requirements.
- Highest next practical product increment after G2C: user-selected standard-rate / longer-session production and robust multitrack audio editing, then real audio-device/plugin interoperability, while preserving explicitly accepted canonical authoring.

**Promotion:** commit this durable bilingual evidence, require **48/48 SUCCESS again at exact evidence-successor HEAD**, then mark PR #193 ready, expected-head squash merge, and record actual main. No premature promotion.
