# ATCM-R2 Validation — Deterministic Native Multitrack Mixer v0

## Verdict

**VALIDATED — BOUNDED DETERMINISTIC NATIVE MULTITRACK MIXER & OFFLINE MIXDOWN v0**

This record validates only the bounded ATCM-R2 capability described by Issue #102. It does **not** claim real-time audio I/O, recording, Browser mixer UI, buses/sends/sidechains, latency compensation, resampling, warp/time-stretch, plugin hosting, mastering-grade DSP, or commercial-release readiness.

## Exact implementation head

Pre-validation exact head:

`909300fa50692ca789ba39d7994bd5fa61e8b5ee`

All **18/18 permanent pull-request workflows completed SUCCESS** on this exact head.

The first R2 implementation head `32fd269d2711b7bff765ddf139d64049ed0ded6d` correctly failed closed in the dedicated R2 regression gate because a 16 kHz test fixture contained only 800 frames while requesting a 0.1 s accepted clip. The fixture was corrected to preserve a real 0.1 s source duration at each sample rate, and rate-mismatch and corruption checks were separated so each failure mode is independently evidenced. Mixer/runtime semantics were not weakened.

## Dedicated evidence

Workflow: `ATCM-R2 Native Mixer Evidence`

Successful run:

`35184486911`

Artifact:

- ID: `10481497910`
- Name: `musica-atcm-r2-native-mixer-evidence`
- GitHub artifact ZIP digest: `sha256:403f04a307ea7cc6f73c74a7e24aa36414e4f0cf64a55184cb4aadddf04be5b2`

The workflow independently generated evidence A and B and required `diff -qr` equality before upload.

## Independent artifact inspection

The downloaded artifact manifest contained seven evidence files and every declared SHA-256 and byte size matched the actual file bytes:

- `contract-hashes.json`
- `mix-after.wav`
- `mix-before.wav`
- `mix-plan-after.json`
- `mix-plan-before.json`
- `project.musica.zip`
- `proof.json`

Key derived artifacts:

- before WAV SHA-256: `c30d8c450ee37ecae99aff96c00011b2dab0d2ece2c981484bed52912d9154a7`
- after WAV SHA-256: `aa9b9d6015f4f0d65d3390a659bcf306deb0e9fb9036d31fcef8e9c72c687db8`
- before mix-plan SHA-256: `2cbce344bb5be36776ce178cad18b148690496787fb0fcb1964eda608fe4af8a`
- after mix-plan SHA-256: `495b0f1eda0259fcef1d467c836aaa22b8017dda85a7b9a34fe236107c6bfaef`

Both mix-plan SHA values were independently recomputed from canonical JSON after removing the self-hash field and matched exactly.

## Validated semantics

The evidence and permanent regressions establish the following bounded v0 behavior:

1. one exact accepted revision is the mixer authority source;
2. Blueprint SHA, audio-material SHA, asset/object SHA and descriptor SHA are bound into the derived plan;
3. source sample rates must exactly equal the explicit mix sample rate — no hidden resampling;
4. bounded mono/stereo integer PCM WAV sources lower to stereo output;
5. non-negative seconds are quantized by deterministic round-half-up-to-frame semantics;
6. clip and track dB gains lower deterministically to linear gain;
7. pan uses the declared linear-balance law;
8. mute wins, then solo isolates eligible tracks;
9. summing order follows canonical track and clip ordering;
10. accumulation uses float64 semantics;
11. over-range samples are hard-clipped to the unit range before PCM16 encoding;
12. output is deterministic stereo PCM16 little-endian WAV;
13. repeat plan generation is exact;
14. repeat WAV rendering is byte-identical;
15. controlled accepted mixer-state changes alter both mix-plan SHA and WAV SHA;
16. overlapping sources exercised the clipping path;
17. export/reopen preserves exact plan and WAV identity;
18. mixer Preview does not advance accepted HEAD before explicit Accept;
19. mixer-field edits reuse the existing R1 `AudioEditPreview` / `accept_audio_edit_preview()` acceptance path rather than creating a second authority system;
20. rendered/mixed audio remains derived and non-canonical.

## Evidence proof flags

The durable proof recorded all of the following as true:

- `asset_import_did_not_advance_head`
- `arrangement_preview_did_not_advance_head`
- `mixer_preview_did_not_advance_head`
- `plan_repeat_exact`
- `wav_before_repeat_exact`
- `wav_after_repeat_exact`
- `controlled_mixer_state_changes_plan`
- `controlled_mixer_state_changes_wav`
- `overlap_clipping_observed_before`
- `reopen_plan_exact`
- `reopen_wav_exact`
- `reopen_wav_sha256_exact`

And it explicitly records:

- `rendered_audio_is_canonical = false`
- `realtime_audio_claimed = false`
- `browser_mixer_claimed = false`
- `recording_claimed = false`
- `plugin_hosting_claimed = false`

## Promotion rule

This document records the pre-validation exact-head evidence. Because adding this durable record creates a successor head, ATCM-R2 is eligible for merge only after **all 18 permanent workflows succeed again on the exact validation-record head**, followed by expected-head merge.
