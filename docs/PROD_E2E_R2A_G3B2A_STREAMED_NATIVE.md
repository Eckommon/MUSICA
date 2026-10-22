# G3B2A — Fixed-block accepted native PCM output / 승인된 오디오의 고정 블록 WAV 출력

**DRAFT implementation / 초안 구현** · Issue #201 (parent #195/#192). Promotion pending CI/independent audio evidence.

## New engine / 새로운 렌더러
- `render_native_mix_streamed` builds a source-bound native mix plan from one exact **accepted** Project HEAD.
- Reads verified immutable CAS audio as fixed `wave.readframes` windows (default 4096, capped 16384 frames), preserving ATCM-R2 integer PCM mono/stereo decode, gain, pan, mute/solo, order, PCM16 clipping and sample-rate equality.
- Writes the derived WAV directly to project-private, temporary, **noncanonical** file and computes output SHA256 from the completed file. It never adds a canonical asset/clip or Accepts a revision.
- Fixed output size cap 256MiB and cancellation/stale/corrupt-source cleanup. Source CAS SHA and accepted HEAD are rechecked after file processing.
- The previous `render_native_mix` stays unchanged for all inherited short-song workflows.

## Required proof / 필수 근거
1. Short ATCM-R2 native WAV **byte equality**, frame/block-size independence and clipping parity.
2. **Two independently accepted 180s/48kHz/stereo PCM16 sources**, distinct SHA, 34,560,044 bytes each; actual 3min stereo PCM output with channel-resolved sample oracle, reopened Project source and deterministic WAV SHA.
3. Whole-process peak RSS < 512MiB on Linux CI (a generous fail-closed smoke ceiling), real `/usr/bin/time -v` wall+RSS log, cancel cleanup, mixed-rate error.
4. Dedicated permanent GitHub workflow plus inherited suite exact-head green; independent derived WAV artifact analysis, bilingual validation successor, another full suite green, guarded merge.

## Not yet proven / 현재 미완료
- **Routing graph, buses, gain/pan automation, realtime playback, Browser full-song audition and full song export/reopen** are separate G3B2B/C/G3B3. This implementation covers accepted **unrouted native** audio only.
- Full Project `verify_integrity` still contains whole-object `read_bytes` in legacy code; tests must not claim every Project operation is constant-RSS. A comprehensive Project integrity streaming refactor is follow-on.
- No physical microphone/interface or actual VST/CLAP plugin binary or commercial production quality.
