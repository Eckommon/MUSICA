# PROD-E2E-R1B-G2C — User-created first audible native automation / 첫 자동화 레인

Status: **implementation draft, not yet validated**. Parent #190, #187, #181, #178.

## Function / 기능
The Browser M7 canonical-automation panel supports a new **First native gain automation** tool, including selecting one of two already accepted audio tracks, start/end dB and end beat. It appears before the legacy "no canonical automation" notice; G1/G2B projects therefore no longer require an existing automation lane to reach trusted `ADD_LANE`.

Preconditions: accepted source revision and session identity match across native audio/routing/automation projections; two accepted tracks have source clips and the supported 2-bus routing graph is accepted; no Preview is pending; no other lane exists. This is UI convenience only: the existing trusted server checks every source SHA/revision, target, point geometry and lock. The Browser uses Preview; only the **separate user Accept** commits the new lane.

## Target audio proof / 오디오 검증
Playwright actual Chromium creates G1 two WAVs and G2B bus routed song using the existing exact user-controlled runs, reopens it and clicks the first gain-lane Preview. Assertions: accepted HEAD remains unchanged, download disabled, explicit Accept advances HEAD, first-channel amplitude decreases as gain changes from -3 to -9 dB, untouched second-channel PCM remains sample-identical, 12-second stereo 8kHz PCM16 WAV SHA and exact reopened WAV, screenshots and no errors.

Not a human usability study, professional-length/44.1/48kHz master, hardware callback, or actual VST3/CLAP/AU binary. PR must remain Draft until complete 48/48 exact-head implementation CI, independent artifacts, durable successor 48/48, expected-head merge.
