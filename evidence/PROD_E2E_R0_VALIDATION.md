# PROD-E2E-R0 Validation — First Real Audible Two-Track Song and Accepted Project Replay

## Bounded result

**PASS — the first deterministic *musically changing* two-source offline MUSICA vertical slice was actually generated through sequential trusted Project Preview→explicit Accept transitions, accepted two-bus routing, native mixer automation and accepted simulated bus-host processing, yielding a listenable 12-second stereo WAV. A fresh exported Project import reproduces the exact accepted revision, derived processing plan and WAV bytes.**

This is not an ordinary end-to-end commercial DAW production proof, a real recorded performer, an external AI provider call, a real VST3/CLAP/AU host, realtime plugin PDC, professional mastering quality, or 44.1/48kHz physical device performance. Scope report `docs/PROD_E2E_R0_MUSICAL_SLICE.md`. Parent product integration #178 stays OPEN for later product stages.

## Exact implementation / evidence identity

- PR #180, branch `feature/prod-e2e-r0-musical-vertical-slice-clean`, based on canonical state/documentation main `3f725f89d24ad67883ab801101aa0f5b5b7c8d4d`.
- Exact implementation/evidence head `c8a95603dd7a6d9657da4d6e27283bd98e2b88ba`: **42/42 GitHub Actions SUCCESS**. New permanent `PROD-E2E R0 First Musical Song Vertical Slice Evidence` workflow plus inherited ATCM/MRAM/RTIO/REC/K1B/R3B/Browser/M7 and full Python 3.11/3.12 MUSICA CI.
- New dedicated workflow run **38726031727 — SUCCESS**. Artifact ID **11968307645**, GitHub ZIP size **800,983 bytes**, declared and independently verified SHA-256 `b3761141acf57a7f6ba905474e3e14458f95cd6b23a413bc7cfa0d8687333edf`.
- The artifact independently extracted into real WAVs and an accepted Project zip; its outer manifest has **6/6 exact SHA-256 and byte-size matches**. The inner portable project has **41 entries**, **19/19** content-addressed SHA-256 objects matched their object names.
- Two clean musical generation runs were compared **byte-for-byte** by permanent CI (full output directories). New tests also independently generated twice and compared all emitted payload hashes.

## Actual musical audio proof

- Synthetic-but-musically changing **melodic synth motif** and **drum pulse** inputs, 12.000 s each, mono PCM16 8kHz; no constant-value impulses substituted. Independent SHA-256 input identities `6125f859eef51e74b2658eee56c694c09c4707db269cd102d2e657adf0a163fa` and `af6ea016fc9c5060ef2330537035a66014dd51fced9c642e9bd2125bf1293fb5`.
- Exact trusted chain: accepted Project Blueprint root `rev-001` → audio tracks/clips → two distinct bus routing with neutral master → `AT-001 mixer.gain_db` automation → accepted simulated plugins with distinct **3- and 9-frame algorithmic delays** → causal offline compensated stereo WAV.
- Accepted final HEAD `rev-001-audio-518ad26796519656-routing-4068c69ebe8ced39-auto-8054005a7aeb1144-bus-host-5025437f028d1337`, **not changed** by offline rendering.
- Actual `final-song.wav`: stereo PCM16, sample rate **8000 Hz**, **96,000 frames** (12 s), exact WAV SHA-256 `f3a199c452c214d2a4bf4c7e321ff8d06e1bbeed0bc0b96fcbf0b96babaa8bff`; peak absolute sample **9390**, **0 clipped PCM samples**, **191,882** nonzero interleaved scalar samples.
- Frames 0–8 are silent, as required by the bounded causal two-bus latency policy. Accepted reference mix *without* simulated plugin differs bytewise, SHA-256 `5470d866a2ea96f32ecd6ef48be251636bffef05c21664cfd75a5078c4a522f2`. Actual render plan SHA-256 `a46c7aba09b50e2870ce65f43a91559fe72e533148c543ff9f629871b068e638`.
- Portable `accepted-project.musica.zip` is **166,048 bytes**. Import to a fresh directory reproduces accepted HEAD, the full processing plan structure and exact final WAV bytes.
- CLI implementation: `python -m musica.prod_e2e_r0 --out <new-or-empty-dir>`; nonempty target is rejected rather than overwritten. No third-party copyrighted sample files are required for this test.

## Product gaps still open

The demonstration establishes a real, narrowly bounded audible musical output and export/reopen vertical slice, **not** a single fully integrated Browser workflow with live AI, externally imported recordings, arbitrary effects, actual plugins or simultaneous physical recording/monitoring. The 8kHz PCM fixture is an evidence-friendly format, not a commercial production recommendation. Naturalness, arrangement quality, mix quality, perceptual advantage, 48kHz physical-device operation and usability must be evaluated separately under #178. Future #177 must process a legitimate identified real plugin binary, never simply present the simulated K1B processor as a third-party plugin.

## Promotion / 승격 기준

This durable validation file creates a new PR head. **Only after that exact successor head independently passes 42/42** may PR #180 be marked ready and guarded expected-head squash merged. No test waivers, no missing workflows, no implicit Project authority upgrades. Keep #178 OPEN for follow-up longer/song/browser/hardware/quality product readiness work.

The exact repository commit and GitHub Actions artifact are the source of truth.


## Corrected implementation successor qualification — 2026-10-17 / 최신 검증

The original `c8a95603...` numerical/ZIP proof above remains accurate. PR #180's subsequent M7 Browser refresh fixes did **not** waive inherited tests. Its latest corrected implementation head `556d4c0d52bf0c0dfa020e9865842470bafedcb7` completed **42/42 GitHub Actions workflows, SUCCESS** and **45/45 individual check runs, SUCCESS** (MUSICA CI includes three separately reported jobs).

**Cross-workflow regression:** M7-R2 Browser automation run `39023040837`, M7-R6 truthful audition run `39023040928`, and PLUG-R3B Browser bus-plugin run `39023040773` all succeeded. The Preview-installed notification only invalidates the read-only audition inspection after a successful actual Preview install; unrelated GETs no longer trigger recurrent fallback renders.

**Latest actual artifact, independently downloaded and inspected:** PROD-E2E-R0 workflow run `39023040828`, artifact ID `12096914867`, ZIP size 800,983 bytes, downloaded archive SHA-256 `ae4316b372673d71c67a84e85c10b0cee6abb3738c137d1a1d74f58873116948` (matches GitHub's reported SHA-256 digest). The `manifest.json` inside independently verified **6/6** exact uncompressed member sizes and SHA-256 digests. Independently decoded final WAV: **8,000 Hz**, **2 channels**, **16-bit**, **96,000 frames / 12 s**, **9390** peak absolute scalar value, **191,882** nonzero scalar samples, **0** samples at |PCM| >= 32767. Actual WAV SHA-256 remains `f3a199c452c214d2a4bf4c7e321ff8d06e1bbeed0bc0b96fcbf0b96babaa8bff`. Independent archive bytes confirm the same artifacts as the prior green head.

**Critical limitation clarification / 중요:** The demo script's `_accept(...)` routine calls trusted explicit Accept handlers programmatically; this is **not** proof of real end-user Browser interaction or human approval. It validates the authority implementation, not the UX. Future end-user Browser WAV import, Preview and human-triggered Accept are tracked in issue [#181](https://github.com/Eckommon/MUSICA/issues/181). Parent #178 remains OPEN; no claims of external plugin ABI, physical recording, native 48kHz device path or release readiness.

**Promotion gate:** This document and scope-note refresh create one or more successor commits. Only the exact final successor head's independent 42/42 workflow pass permits guarded expected-head squash merge. Record the final promoted SHA and merge result in subsequent canonical state alignment.
