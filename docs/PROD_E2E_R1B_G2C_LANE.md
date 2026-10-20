# PROD-E2E-R1B-G2C — User-created native gain automation lane / 트랙 게인 자동화 레인 생성

Status: DRAFT / 검증 중. Parent issue #187.

MUSICA already has trusted native mixer automation ADD_LANE but the canonical Browser editor exposes only selected-point modification or point insertion in existing lanes. This change adds a first-party **user-operated native track gain automation lane** creation form to the Browser.

The UI requires matching accepted session/revision across Browser automation, routing and native audio, a real routed accepted track with at least one accepted clip and an accepted nonempty graph. User chooses a track, stable lane ID and start/end dB values (-60..12). A two-point audio-track `mixer.gain_db` lane is submitted through the pre-existing trusted `sendPreview` method. Only a separate explicit user Accept creates the canonical lane. The Browser does not auto-commit audio, routing or automation state.

## Honest proof scope / 한계

Initial G2C implementation regression checks actual served same-origin first-party Browser JavaScript, parsed JavaScript syntax, source guards, ADD_LANE payload and inherited automation tests. **This alone is NOT real Chromium automated click or independently audible lane effect proof**. A further required G2C real Chromium test should start from G2B routed WAV, click lane Preview and explicit Accept, compare accepted vs unautomated PCM, block stale downloads, export/reopen SHA and include screenshots/ZIP evidence. Do not declare full G2C completion or merge until this evidence and exact-head full CI gate are satisfied.

Physical I/O, real licensed plugin binaries, commercial-length mastered audio and genuine human usability remain unproven.
