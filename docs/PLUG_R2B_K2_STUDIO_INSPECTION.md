# PLUG-R2B K2 — Truthful Studio Accepted Bus-Processor Inspection & Opt-in Offline Audition

Status: **DRAFT IMPLEMENTATION — NOT VALIDATED / NOT PROMOTED**. Under open #166 / #162 / #155. Prerequisite is K1-B verified accepted simulated bus processor authority and offline causal PDC, not real third-party plugin binaries.

## Motivation

MUSICA is an AI-native music production workstation: accepted creative intent and durable user state must remain distinguishable from noncanonical Preview, offline listening and runtime buffers. Currently the legacy Studio media route is *not* an integrated K1-B compensated bus-host playback path. Silently replacing it would mislead creators and threaten previous Studio/RTIO regression.

K2 therefore introduces **explicit, read-only Studio inspection and opt-in WAV playback**, not generic Studio transport integration.

## Grounded endpoints

- `GET /v0/sessions/{session_id}/bus-plugins`: exact accepted HEAD revision ID, project/Blueprint/routing/bus-host material hashes, accepted instance list and bypass/algorithmic/creative delay state, plus truthful availability and output WAV SHA/derived-plan SHA. A pending unrelated Preview is not accepted and never replaces canonical state.
- `GET /v0/sessions/{session_id}/bus-plugins/media/accepted.wav`: explicitly rendered derived **offline** PCM16 WAV solely from the same accepted source; owner ID never supplied by caller; no alternate rate/config/WAV injection and no accepted Project mutation.
- Existing Studio `/media/audio.wav`, `/mixer-routing/media/*`, Browser JS, recording monitoring and realtime callbacks remain **unchanged** in this stage.
- Unsupported/empty-routing sessions retain inspectable state with `offline_audition.available=false` and a bounded reason; media call fails closed with structured Studio error.
- Report `native_vst3_clap_au_host=false`, `realtime_pdc=false`, `default_studio_media_overridden=false`, `render_is_derived=true` and `preview_mutation_supported_here=false`.

## Verification

- A session over a real accepted K1-B two-bus Project returns exact committed instances and playback SHA matching independent `render_accepted_simulated_bus_host` output.
- PCM at sample rate 8 kHz, stereo, 96,000 frames: first aligned sample at frame 9 equals (24576,24576); legacy case frame 3 equals (24576,24576).
- GET JSON/media routes return only authenticated-to-local-session accepted state, accepted preview is not confused with immutable revision, invalid session produces 404.
- No Project HEAD mutation from read-only Studio inspection/audition, and no changes to legacy Studio endpoints.
- New **39th permanent** CI with inherited K1-B, K1-A, K0, R1 contracts; double evidence byte comparison and independent manifest/WAV oracle.

This is not a browser UI editor or native plugin host. Before such a claim, an explicit Studio editing Preview→Accept and browser interaction validation must be implemented and independently proven, along with source-aware media cache invalidation and any realtime engine change.
