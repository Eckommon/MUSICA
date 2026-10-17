# PROD-E2E-R0 — First Audible Song Vertical Slice / 첫 실제 청취 가능 곡 제작 연결 검증

**Status / 검증 단계:** Exact corrected implementation head `556d4c0d52bf0c0dfa020e9865842470bafedcb7` completed **42/42 workflows** and **45/45 individual check runs** on 2026-10-17. Durable-evidence successor must independently go green before expected-head PR #180 merge. State-closure PR #179 is already merged; Issue #178 stays open. This is the **first audibly musical**, bounded integration exercise after the isolated technical foundation milestones; it is not a commercial-grade DAW release or complete everyday production proof.

## Contract / 지원되는 정확한 실험

- A user-defined, pinned local `examples/intents/dark-electronic-12s.json` composition Blueprint via the existing deterministic Director. This is **not a live external AI provider**.
- Generate exactly two musically structured 12-second **mono 8kHz PCM16** source assets (synth melody motif, kick/hat rhythmic pulse), with real changing pitches, amplitude envelopes and repeatable sample timing. Unlike prior PLUG-R2 impulse fixtures, both sources contain intentionally musical nonconstant PCM and are independently audible.
- Import both sources into immutable project audio assets, add two accepted named tracks and exactly two non-destructive 12-second clips using typed source-bound Audio Preview→Accept.
- Accept exactly `AT-001→BUS-001` and `AT-002→BUS-002` to one neutral `MASTER-001` using trusted Routing Preview→Accept.
- Accept one native `AT-001 mixer.gain_db` automation lane via the trusted Automation Preview→Accept path; no plugin-param automation is inferred.
- Accept exactly two bounded simulated bus processors with algorithmic latency 3 and 9 frames, no creative delay, on the exact accepted source using K1B source-bound Preview→Accept; render true derived offline causal PDC.
- Deliver reproducible final stereo PCM16 WAV, source WAVs, pre-plugin stereo WAV, portable `.musica.zip` accepted project bundle, typed evidence `proof.json` and source-hashed `manifest.json`.
- Independently verify nonzero actual musical audio, 12.0s length at 8000 Hz, PCM16 2-ch, first possible causally aligned audio from frame >=9, peak under 32767, no reported clipping; no Project HEAD mutation during render, exact accepted archive/reopen and byte-for-byte equality of output and plan.
- Expose a CLI: `python -m musica.prod_e2e_r0 --out <empty-output-dir>`. Existing output is not silently overwritten.

## Hard limitations / 비지원

- This does **not** claim a polished 3-minute 48 kHz song, comprehensive instruments, real microphone recording, real VST3/AU/CLAP DSP, realtime plugin PDC or mastering-grade audio.
- The example uses a local deterministic music-generator and no external copyrighted audio; it does not prove real OpenAI Director provider execution, human musical satisfaction, commercial licensing, or large-project stability.
- The exact two-bus neutral-master plugin host cannot simultaneously process the unrelated legacy R1 master plugin chain in this experimental topology. Arbitrary sends, sidechains and plugin format adapters remain unsupported.
- Initial demo is user-runnable via CLI and can be inspected/reopened in MUSICA; full end-to-end Browser UX *across every* production function needs separate real UI evidence. **The reference Python script itself calls the trusted Accept methods; that is not evidence of a human clicking Browser Accept.** Genuine user-operated Browser production begins in [#181](https://github.com/Eckommon/MUSICA/issues/181). PLUG-R3B Browser plugin editing already has its own exact 41-gate evidence.

## Promotion gates / 승격

1. Work on the already-merged **post-#179 canonical main** and preserve the isolated PROD-E2E files (plus two targeted Browser audition-regression fixes).
2. New **42nd permanent** workflow exercises normal accepted state transitions + original PLUG-R3B, MRAM and ATCM regressions, twice-generates A/B musical output evidence, byte-compares directories and independently decodes the actual output WAV and checks manifest/hashes.
3. Exact implementation head 42/42 green, independent artifact WAV/Project archive inspection, durable validation file, successor head 42/42 green and expected-head squash merge.
4. Product gate progression continues with a full user Browser production loop, physical device evidence and real licensed plug-in binary fixture; no green synthetic test upgrades those claims.

**Product goal:** improve *end-to-end production power* without sacrificing deterministic, inspectable, explicit user creative authority.


## Corrected-head qualification / 수정 HEAD 추가 검증 (2026-10-17)

- Corrected implementation `556d4c0d52bf0c0dfa020e9865842470bafedcb7`: 42/42 workflow conclusions **SUCCESS**, 45/45 check runs **SUCCESS**. The extra check-run entries are the MUSICA CI job matrix, not extra workflows.
- Browser audition refresh regressions covered by inherited M7-R2 and M7-R6 workflows; inherited PLUG-R3B also passed. No test waivers.
- Artifact run `39023040828`, ZIP ID `12096914867`, downloaded ZIP SHA-256 `ae4316b372673d71c67a84e85c10b0cee6abb3738c137d1a1d74f58873116948`; matched GitHub artifact digest. Independent archive manifest 6/6 member size/hash matches; actual stereo WAV: 8000 Hz, PCM16, 96,000 frames, peak 9390, 191,882 nonzero interleaved scalar samples, clipping 0, WAV SHA-256 `f3a199c452c214d2a4bf4c7e321ff8d06e1bbeed0bc0b96fcbf0b96babaa8bff`.
- **Scope honesty:** accepted revisions advance through scripted explicit calls, not demonstrated human Browser clicks. The shipped WAV is intentionally an 8kHz reference, not a professional-quality 48kHz release. User-operated imported-audio workflow is issue #181.
