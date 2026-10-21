# PROD-E2E-R2A-G3B1A validation / 3분 WAV 스트리밍 CAS 검증

## Exact source and CI / 정확한 검증 기준
- Parent issue: #195 (parent #192); implementation PR: #198.
- Canonical predecessor: G3B-0 PR #197 merged to main `61626524556802b62a5ed08d69017cc3dde812b3`.
- Exact implementation head: **`813bf43f98f32ee685d30284d3e80c8e8169eac7`**.
- All **51/51 distinct permanent GitHub Actions workflows completed SUCCESS** for that exact implementation SHA (51 workflow runs, no failures). GitHub check-runs endpoint additionally reports 55/55 successful check runs; these are *checks*, not 55 distinct workflows.
- Dedicated `PROD-E2E R2A G3B1A Streaming CAS WAV Intake` run [39579126088](https://github.com/Eckommon/MUSICA/actions/runs/39579126088), job `119152037049`, concluded SUCCESS. Job log shows **14 focused tests passed** across G3B1A, inherited G3B0 staging, and R1A Browser import authority.
- The dedicated job produces no media ZIP/artifact and is *not* a real Chromium 3-minute performance run. A separate downloaded media SHA/PCM artifact audit is therefore **not claimed**.

## Verified behavior / 검증된 사실
- Real Studio project; test generates a fixed **180-second**, **48kHz**, two-channel, 16-bit PCM WAV: **8,640,000 audio frames** and **34,560,044 file bytes**.
- Trusted G3B0 private stage receives WAV through strict ordered **1MiB** chunks, per-chunk SHA-256 and complete content digest verification.
- `import_audio_asset_verified_path` computes a streaming SHA-256, validates declared WAV PCM frames with at most 65,536 frames per inspection iteration, and streams CAS object construction in at most 1MiB blocks.
- New CAS objects are published through no-overwrite hard-link creation, followed by source-hash-bound asset descriptor and audit. Corrupt existing object refuses instead of being silently repaired.
- Idempotent re-import returns matching descriptor. Cancelled private stage path disappears. Invalid WAV or incorrect whole-file digest rejects; asset descriptor and accepted creative HEAD do not change.
- `read_audio_asset` source verification no longer reads whole WAV files to memory; the **audio decoding/mixer remains distinct and is not bounded by this patch**.

## Scope and risks / 범위 및 미검증
- **Trusted internal bridge only. No HTTP staged session routes, no Browser File.slice transport or live user upload.** Callers must obtain stage paths internally; never accept a client-supplied filesystem path.
- No crash-recovery transaction/journal spanning object, descriptor and audit; unexpected interruption can leave an orphan intermediate object or metadata that requires recovery work.
- No 3-minute dual-track mixing, no bounded mixer RSS/CPU measurement, no 3-minute export/reopen, no physical device or third-party plugin binary evidence.
- Older 16MiB Browser direct-upload contract is retained. Creative track/clip revisions remain subject to separate explicit Preview → Accept.
- Fixture audio consists of constant PCM values. Test is **format/storage/integrity evidence**, not audio quality, musical content or user acceptance.

## Promotion / 병합 전 추가 요구
- This document is the **durable evidence successor**, not automatic approval.
- Require a fresh **51/51 full permanent workflow SUCCESS on this exact successor SHA**, recheck base main and PR head, then mark ready and perform **expected-head guarded squash merge**.
- Keep #195 / #192 OPEN. Prioritize G3B1B secure session-scoped HTTP staged transfer and user-selected Browser File.slice, then G3B2 memory-bounded decoding, then G3B3 actual 3-minute two-track Chromium production.

## Korean summary / 한국어 요약
3분 48kHz 스테레오 WAV의 사설 청크 수신→무결성 확인→불변 CAS 오디오 자산 등록이 내부 테스트에서 성공했습니다. 이는 실제 브라우저 대용량 파일 가져오기나 3분 음악 믹싱의 완성이 아닙니다. 문서 커밋의 독립적인 전체 CI 재통과 후에만 병합합니다.
