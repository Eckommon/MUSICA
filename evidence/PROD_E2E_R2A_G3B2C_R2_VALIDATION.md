# PROD-E2E-R2A-G3B2C-R2 validated 180s WAV Range cache / 3분 WAV 재사용 검증

## Exact implementation and promotion dependency / 검증 기준
- R1 baseline is stacked Draft PR [#206](https://github.com/Eckommon/MUSICA/pull/206), original head `e47cb856341de42d1525ed084a2b7dd1d630afcf`. R2 Draft [#208](https://github.com/Eckommon/MUSICA/pull/208), six R2-only files, original implementation head **`5b9d73f47383ac9d4473d68e9ea2935c9a4269b8`**. Canonical main has G3B2B `1668c1256c35539e51815631a715917aedaa3f8c`. **R2 cannot merge until R1 has independently completed its evidence successor and merged**.
- On this exact original R2 implementation HEAD: **56/56 independent GitHub Actions workflows SUCCESS; 60/60 individual checks SUCCESS**. Dedicated permanent 56th workflow [#39838530595](https://github.com/Eckommon/MUSICA/actions/runs/39838530595) SUCCESS, including real source/Range, TTL, corruption, symlink safety and restart cleanup tests. No inherited workflow waived.

## Independent WAV+proof archive audit / 파일 단위 독립 검증
- GitHub Actions artifact ID **`12454037676`**, independently downloaded ZIP `MUSICA-G3B2C-R2-180s-cached-range-audit.zip`, ZIP SHA-256 **`4d89cb3e6a085fbfb6e7286cc1a08d94cfa9f31c87f4d8663fd7d8bbf2fa94a9`**. Members: `accepted-range-cached-180s.wav`, `proof.json`.
- Independently parsed actual WAV with Python `wave`: 48,000Hz, stereo, signed 16-bit PCM, exactly **8,640,000 frames / 180 seconds / 34,560,044 bytes**. WAV SHA-256 **`c681b3948b9be00ec18908f2f8ab9bab2a8d71dbb779b18efcf96ef1327d6a89`**, exactly matches `proof.json` and earlier G3B2A full-length native two-track output.
- Independent decoded WAV PCM first frame, frame 1, frame 4,320,000 and frame 8,639,999 all `(4000, -2500)`. Two distinct accepted source CAS hashes: A `8ab1c0a43ac895ef3dc1ec9b4afa4348726eb396784a878953f122bae4672165`, B `f8910ab88b00d52bb19fabb31e8d9ed10419ed0a615945e24253baa2fd32b2a8`.
- `proof.json`: three independent HTTP Range requests `bytes=44-51`, `bytes=17280044-17280051`, `bytes=-8`; **render_count_for_three_distinct_ranges = 1**, **cache_file_count = 1**, original accepted HEAD unchanged. Linux whole-test-process maximum RSS **196,768 KiB** (about 192.16MiB), inclusive of source assets and tests.
- Synthetic constant PCM demonstrates numerical exactness and memory-bound behavior, **not listening quality or real-world music mixing latency**.

## Implemented resource and trust boundary / 보안과 실제 기능
- The accepted-only derived WAV file cache binds exact Studio session, project root, branch, accepted revision, trusted mix/route plan SHA, immutable source object SHA and sample rate. It never writes an accepted creative revision or changes CAS data.
- At most **two 256MiB derived WAV files**, 300-second idle TTL, stale/changed revision invalidation, source+output SHA recheck, per-session active lease guard, symlink root denial and process-restart derived orphan cleanup. Source WAV remains immutable.
- HTTP accepted-wave byte-range transfer reuses derived file without re-running costly PCM DSP on each seek, while still reading bounded transfer chunks.

## Evidence successor and exclusions / 종결 전 검증
This document is **not itself a merge authorization**. Full **56/56 and all 60 checks** must pass on this documentation-bearing successor. After R1 official main promotion, **rebase the exact six R2-only files plus this evidence** on the new canonical main and repeat implementation+evidence checks before guarded expected-head squash. R3 #210, R4 #212 and end-to-end G3B3 must not be merged before prerequisites.
- Legacy Studio 180s accepted/Preview metadata can still render a whole song in Python; R3 resolves the read-only view, R4 addresses Pending Preview. No professional real-time audio device, VST/CLAP real plugin or commercial DAW claim.
