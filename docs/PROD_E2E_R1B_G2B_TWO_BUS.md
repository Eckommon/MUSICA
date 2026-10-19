# PROD-E2E-R1B-G2B — Two user tracks into two buses / 두 트랙과 두 버스의 실제 믹싱

**Implementation under review / 구현 검증 중**. Parent #187 and #181/#178.

## Product capability / 실제 기능

Previously, the trusted MRAM engine supported ADD_NODE and SET_TRACK_OUTPUT, but the first-party Browser could not construct an initial routing graph. G2B adds a **user-clicked, source-bound two-bus Preview** for exactly two already accepted native audio tracks with clips, an empty graph, and matching accepted revision/session. The candidate builds BUS-UI-001, BUS-UI-002, MASTER-UI-001 with neutral mixer values, one output per accepted track. Only existing **explicit Accept** advances the project. / 사용자가 두 트랙의 버스 구성을 직접 Preview하고 승인해야 정식 라우팅이 생성됩니다.

User can separately Preview a bus gain change, explicitly Accept, audition the derived WAV, export `.musica` and reopen. / 버스 게인 조정과 재열기도 개별 승인합니다.

## CI oracle / 검증

Real Chromium reopens a G1 two-source Browser-produced project, clicks two-bus Preview/Accept, separately changes first-bus gain to -6dB via Preview/Accept, downloads accepted WAV, verifies stereo PCM 8kHz 96,000 frames, lower left-channel peak and exactly preserved right PCM, exports project, restarts Browser/Studio and verifies identical output WAV. No auto-Accept and no inferred audio result based on UI-only state.

## Strict limits / 주의

This **does not** yet create, audition or accept canonical automation lanes through Browser; G2C must close that gap. It does not prove real third-party plugin binaries, microphone, physical I/O, commercial production length/quality or actual human usability.

Promotion requires new CI on exact implementation SHA, independent ZIP/PCM review, durable evidence and successor full CI, guarded squash merge; keep parent #187 open.
