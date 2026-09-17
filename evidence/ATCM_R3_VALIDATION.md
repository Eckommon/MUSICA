# ATCM-R3 Validation — Browser Native-Audio Arrangement & Mixer Surface v0

## Verdict

> **VALIDATED — BOUNDED BROWSER NATIVE-AUDIO ARRANGEMENT & MIXER SURFACE**

ATCM-R3 validates a truthful Browser/Studio projection of exact accepted native-audio arrangement and bounded mixer state while preserving the existing R1/R2 creative-authority boundary.

## Authority boundary

```text
exact accepted native-audio revision
→ Browser arrangement/mixer projection
→ source-bound native-audio Preview
→ accepted HEAD unchanged
→ derived R2 native-mix audition
→ explicit trusted Accept
→ exactly one accepted revision advance
```

Browser-local state, controls, transport state, screenshots, mix plans and WAV bytes remain derived/non-canonical. Accepted project revisions / Blueprints remain creative authority.

R3 does not introduce a second edit authority system:

- arrangement edits reuse the R1 audio-edit authority path;
- mixer edits reuse the R2 mixer-candidate builder while still producing the same `AudioEditPreview` authority type;
- explicit Accept uses the existing trusted `accept_audio_edit_preview()` path;
- generic Browser/Studio direct Blueprint mutation is not granted native-audio authority.

## Exact pre-validation head

- PR: `#107 — Implement ATCM-R3 Browser native-audio arrangement and mixer`
- exact evidence-bearing head: `8db2c3cc0e85d416c84ee2106df4bbb5c64ceeef`
- permanent workflows at this head: **19/19 SUCCESS**
- dedicated workflow: `ATCM-R3 Browser Native Audio Evidence`
- dedicated run: `35192996006` — **SUCCESS**
- dedicated artifact ID: `10484249087`
- artifact name: `musica-atcm-r3-browser-native-audio-evidence`
- artifact ZIP SHA-256: `ebe04df259bdb8948446533096f8061acdd21cdafdf4cca9f443d258abf07bdd`

## Independent artifact verification

The downloaded artifact ZIP SHA-256 independently matched the GitHub artifact digest above.

The artifact manifest was independently checked against the actual payload bytes. All listed SHA-256 values and byte sizes matched:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `01-accepted-native-audio.png` | `a7b92af49035251179dfe2cbe78901ec0ff474dae983f0d75de3489844cee357` | 950010 |
| `02-arrangement-preview.png` | `bac91a8dc2f7874cd3a64a8eddce2207af6eac6201695704d742170bb7f91d24` | 1067579 |
| `03-mixer-accepted.png` | `fd945281a31be1f20b8e1bb84b637920551a8c38afc73ff72feecfc84961c92f` | 1162575 |
| `04-stale-preview-rejected.png` | `406d507dc352f04351055cafb9482b7a67eabc2b5f5d07354c7b441dcf8946d1` | 1238820 |
| `proof.json` | `d5b6c9f9a5c5de1cdced31b80e78a51ebf09cc03eb4558d34ee86461d8da6d6b` | 1586 |

`manifest.json` SHA-256: `eb68d68616a465478a9e946ffdfe2dbb485215d84be0e14ddf9e07cd446320fa`.

## Real-Chromium evidence

The dedicated workflow runs the same bounded lifecycle twice in real Chromium and proves the machine-readable `proof.json` output is byte-identical across the two independent executions.

The validated lifecycle is:

```text
open accepted project
→ inspect accepted native-audio track/clip/mixer projection
→ arrangement Preview (move clip)
→ accepted HEAD unchanged
→ preview-derived R2 audition differs from accepted audition
→ discard Preview
→ accepted HEAD unchanged
→ mixer Preview (gain/pan)
→ accepted HEAD unchanged
→ explicit native-audio Accept
→ accepted revision advances exactly once
→ restart service + reopen in a fresh Browser process
→ accepted mixer state restored exactly
→ create another Preview
→ advance accepted HEAD independently
→ stale Browser Preview Accept rejected
→ concurrent accepted HEAD preserved
```

The screenshots independently show:

- accepted Browser native-audio surface;
- `PREVIEW · NOT ACCEPTED` arrangement state with the accepted project HEAD explicitly unchanged;
- mixer state after explicit Accept;
- stale Preview rejection after HEAD changed.

## Machine-readable proof

`proof.json` records:

- project ID: `PRJ-ATCM-R3-E2E`
- asset ID: `sha256:dd7b50dee138ea1eea989db24cfdbe6e15e05805fb7dbd11e72461718235bc66`
- source head: `rev-atcm-r3-root-audio-1d926f83a6c83844`
- accepted head after mixer Accept: `rev-atcm-r3-root-audio-1d926f83a6c83844-mixer-d7dbc9ca4bc2ad3b`
- reopened head: exactly the same accepted mixer revision
- concurrent head used for stale-Preview rejection: `rev-atcm-r3-root-audio-1d926f83a6c83844-mixer-d7dbc9ca4bc2ad3b-audio-4ba84102705d0156`

The proof records all of the following as `true`:

- `arrangement_preview_head_unchanged`
- `discard_head_unchanged`
- `mixer_preview_head_unchanged`
- `explicit_audio_accept_advanced_once`
- `reopen_preserved_mixer_state`
- `stale_preview_accept_rejected`

Derived audition bindings:

- accepted mix-plan SHA-256: `50427b5bb9d08747268bfe6954e168a4ed4b516d5458c0889c9d2e402613e417`
- accepted WAV SHA-256: `cdfca6f5c750e5d61e5336d8f4c2ae406bb6ab1114376ee103f5f145460bba79`
- arrangement Preview WAV SHA-256: `b1fe553cb8b3a57533c3ee8077c8f3fb2a82aaa7035c0ba5acea92d7c67db7da`
- mixer Preview plan SHA-256: `9f42b5f87f2a198ee38250ffd1b189ce39bebc485ae0352e23eb5a8dc831360e`
- final accepted WAV SHA-256: `d5a190023088865cfb4e60640c3db484483e6304e702ca2657218bbd5e89da26`

The proof also records:

- `rendered_audio_is_canonical = false`
- `browser_state_is_canonical = false`
- `recording_claimed = false`
- `realtime_device_engine_claimed = false`
- `plugin_hosting_claimed = false`
- `console_error_count = 0`
- `page_error_count = 0`
- `request_failure_count = 0`

## Fail-closed corrections discovered during validation

Validation found and corrected three bounded integration/evidence defects before promotion:

1. the Studio-session pending-Preview contract initially did not include the additive `native_audio_edit` Preview kind;
2. the first dedicated workflow referenced obsolete/nonexistent Studio test paths;
3. the real-Browser evidence runner initially classified Chromium's normal media-source cancellation (`net::ERR_ABORTED`) as a network failure when an `<audio>` source was replaced or closed.

The final runner ignores **only** `net::ERR_ABORTED`; any other failed request remains promotion-blocking and is recorded with its failure reason. Final validated evidence contains zero non-ignored request failures, zero page errors and zero console errors.

## Maximum validated claim

> **MUSICA can truthfully project exact accepted native-audio tracks/clips and bounded mixer state into a Browser arrangement/mixer surface, create source-bound arrangement or mixer Previews without mutating accepted state, audition exact derived R2 mixes, explicitly Accept through the existing trusted native-audio authority path, restore accepted state after restart/reopen, and fail closed on stale Preview acceptance.**

## Explicit non-claims

ATCM-R3 does **not** validate or claim:

- microphone/line recording;
- ASIO/CoreAudio/WASAPI or other low-latency real-time device callbacks;
- monitoring guarantees;
- VST3/AU/CLAP or other third-party plugin hosting;
- generalized buses/sends/sidechains;
- latency compensation;
- implicit sample-rate conversion;
- warp/time-stretch/pitch shift;
- destructive waveform editing;
- mastering-grade processing;
- overall commercial-release readiness;
- cloud/multi-user creative authority.

## Promotion rule

This record does not itself authorize merge. Because adding it creates a successor exact head, **all 19 permanent workflows must succeed again on that successor head**. Only then may PR #107 be expected-head merged and Issue #105 completed. A separate state-only closure must follow before ATCM-R4 / parent Issue #95 closure evaluation.

**Repository evidence remains authoritative over conversation/model memory.**
