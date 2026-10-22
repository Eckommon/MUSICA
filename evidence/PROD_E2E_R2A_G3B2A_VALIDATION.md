# PROD-E2E-R2A-G3B2A validation / 3분 2트랙 고정 블록 믹싱 공식 검증

## Verified exact implementation / 검증된 정확한 커밋
- Parent #201/#195/#192, implementation Draft PR [#202](https://github.com/Eckommon/MUSICA/pull/202).
- Prior canonical main G3B1B: `77e49d41d6cbc5f2385a5855fd432a5676958a32`.
- **Exact G3B2A implementation SHA `56528810ba2eef5bbdc70b7a8c9d030569b5ed91`**.
- Permanent GitHub Actions **53/53 distinct workflow runs SUCCESS**, **57/57 check runs SUCCESS** at this exact SHA; the previous workflow G2B Chromium initially failed at a stale projection / 35-second timeout, and a prior intermittent HTTP 404. The G2B regression was improved to explicitly refresh *read-only* accepted routing projection and verify the *exact* accepted HEAD and -6dB bus gain within a bounded 90s window. G1 error diagnostics capture actual 4xx URLs without disabling checks. This full exact-head run has **no skipped failed gate**.
- Dedicated `PROD-E2E R2A G3B2A Streamed Native PCM Mix` run [#39700617677](https://github.com/Eckommon/MUSICA/actions/runs/39700617677), SUCCESS; test includes short ATCM-R2 byte parity and two separately accepted 180s PCM WAV sources. Previous focused CI /usr/bin/time reported 9 passed, 69.39s, maximum RSS 197,268 KiB. Exact-head downloaded proof records max RSS **197,576 KiB**.

## Independent audio inspection / 독립적인 WAV 검사
- Dedicated artifact ID `12392244241`, ZIP SHA-256 **`7d64443c7a0fa475388b256c2c155b18b606fad9c04e9fa9d1abb99c6456159d`**, contains original A/B, mixed WAV, and `proof.json`.
- Both input WAVs: 48,000Hz, stereo PCM16, 180s, 8,640,000 frames, 34,560,044 bytes each. A is channel-separated `(4000,0)`, SHA `8ab1c0a43ac895ef3dc1ec9b4afa4348726eb396784a878953f122bae4672165`; B is `(0,-2500)`, SHA `f8910ab88b00d52bb19fabb31e8d9ed10419ed0a615945e24253baa2fd32b2a8`. Assets are independently imported to **two separate explicitly accepted tracks/clips**, and accepted creative HEAD does not change during subsequent derived rendering.
- Rendered output `accepted-mixed-180s.wav`: 48,000Hz stereo PCM16, exactly 180s/8,640,000 frames/34,560,044 bytes. SHA-256 **`c681b3948b9be00ec18908f2f8ab9bab2a8d71dbb779b18efcf96ef1327d6a89`** matches `proof.json`. Independently decoded PCM samples at start/middle/final frame each `(4000,-2500)`; 0 clipped samples, `peak_pre_clip=0.1220703125`.
- After project reopening and a second render with a different block size, the derived output SHA is identical; original accepted project HEAD is unchanged. No full WAV is decoded into a Python per-frame list in the newly opt-in renderer.
- A process peak RSS of 197,576 KiB includes source setup, import and render and **does not** prove every unrelated Project operation is memory-bounded. Numeric proof uses synthetic constant-valued PCM, not music-production quality evidence.

## Engine features and limitations / 범위와 미완료
- `render_native_mix_streamed`: current accepted HEAD only; 4,096 frame blocks by default (max 16,384), project-local temporary derived WAV output capped at 256MiB; source CAS SHA / WAV header checks, cancellation and failure cleanup, deterministic PCM16 gain/pan/mute/solo/clip summing and clipping. Legacy ATCM-R2 renderer stays unchanged, short output is byte-identical.
- **G3B2A only covers native unrouted static accepted mixing**. Accepted routing buses/return and per-frame automation are G3B2B Draft PR #204, NOT merged here. First-party Browser long-song audition and file export are G3B2C Issue #205; complete two-track 3-minute Browser creation, WAV export and archive reopen is G3B3.
- Native legacy `project.verify_integrity` may still load whole CAS objects; crash-journal atomicity and real microphone/audio interface/third-party plugin binary/realtime low-latency evidence remain unproven.

## Mandatory successor promotion / 후속 커밋 검증
This validation record is **not itself approval**. Require this document's exact HEAD **53/53 full permanent workflows SUCCESS** plus review of main and PR head, then mark ready and perform **expected-head guarded squash merge**; keep parent #201, #195 and #192 OPEN until all G3B2B/C/G3B3 requirements are satisfied.
