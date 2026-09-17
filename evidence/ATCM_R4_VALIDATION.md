# ATCM-R4 Validation — Restart/Reopen Native-Audio Lifecycle & Parent Closure Evaluation v0

## Verdict

> **VALIDATED — BOUNDED NATIVE-AUDIO RESTART/REOPEN LIFECYCLE**

ATCM-R4 validates that the accepted native-audio foundation established by R0→R3 survives deterministic project export/import, fresh Studio startup and a fresh real-Chromium session without granting runtime Preview state, Browser state or rendered audio any reverse authority.

## Authority boundary

```text
exact accepted native-audio revision
+ immutable project audio assets
→ deterministic Project Bundle export
→ fresh destination import
→ fresh Studio process
→ fresh Chromium session
→ same accepted revision / Blueprint / mixer state
→ same R2 mix-plan SHA / WAV SHA
```

The following remain derived/non-canonical and are deliberately not persisted as accepted authority:

- Browser-local state;
- Studio-session pending Preview state;
- last submitted candidate / authority-result runtime state;
- rendered WAV bytes and playback state.

Explicit Preview/Accept remains the only trusted native-audio creative-state transition. Generic public project commit remains unable to bypass that boundary after reopen.

## Exact pre-validation head

- Issue: `#111 — ATCM-R4 — Restart/Reopen Native-Audio Lifecycle & Parent Closure Evaluation v0`
- PR: `#114 — Implement ATCM-R4 restart/reopen native-audio lifecycle evidence`
- exact evidence-bearing head: `2062c6e778b4cd7c726644550ca3917e4c102275`
- permanent workflows at this head: **20/20 SUCCESS**
- dedicated workflow: `ATCM-R4 Restart Reopen Lifecycle Evidence`
- dedicated run: `35244846922` — **SUCCESS**
- dedicated artifact ID: `10506274908`
- artifact name: `musica-atcm-r4-restart-reopen-lifecycle-evidence`
- artifact ZIP SHA-256: `65423122a533f590f0462ed0d31dcf222106941e78ac76e64989cd4062d4ad03`
- artifact ZIP size: `3,069,846` bytes

## Independent artifact verification

The downloaded artifact ZIP SHA-256 independently matched the GitHub artifact digest above.

The artifact manifest was independently checked against the actual payload bytes. All **5/5** listed SHA-256 values and byte sizes matched:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `01-source-accepted.png` | `d430b09c8e38e0771a21767c8529f2f8b3ee106ed6fb4ab8eb1491f4aa0c4c2d` | 998,785 |
| `02-pending-preview-before-restart.png` | `6c5f5f6f8dc2dca0d7c9a4a4b2f4e1b7d83acd47ec30cf65e6ccda86eeb5b253` | 1,132,215 |
| `03-fresh-reopened-accepted.png` | `d430b09c8e38e0771a21767c8529f2f8b3ee106ed6fb4ab8eb1491f4aa0c4c2d` | 998,785 |
| `native-r4.musica.zip` | `f43e59200c34383c0248664d625bc3e16b5d17e5528dbfd2653d66c258bd9082` | 22,441 |
| `proof.json` | `47a239259673e68e04574ee8c7c4f40b5ac1e9f24143f358774c7e959da86c03` | 1,686 |

The identical accepted-state screenshot SHA before restart and after fresh reopen provides an additional visual check that the accepted Browser projection was restored exactly in this deterministic fixture.

## Real restart/reopen evidence

The dedicated workflow executes the lifecycle twice and proves `proof.json` is byte-identical across independent A/B executions.

The validated lifecycle is:

```text
create accepted native-audio project
→ explicitly Accept bounded mixer state
→ render exact R2 mix
→ open Studio + Chromium
→ verify accepted revision/mixer/audition hashes
→ create a new mixer Preview only
→ accepted HEAD remains unchanged
→ export deterministic project bundle while Preview is pending
→ stop Browser + Studio
→ import bundle into a different fresh workspace
→ verify project integrity and exact accepted Blueprint
→ reproduce exact R2 mix-plan and WAV bytes
→ start fresh Studio + fresh Chromium
→ verify same accepted revision/mixer/mix hashes
→ verify prior pending Preview/runtime authority state did not reappear
→ verify generic native-audio commit bypass remains blocked
→ corrupt persisted audio object in isolated imported copy
→ integrity fails closed
```

## Machine-readable proof

`proof.json` records:

- project ID: `PRJ-ATCM-R3-E2E`
- accepted head: `rev-atcm-r3-root-audio-1d926f83a6c83844-mixer-a9937c0e6a04a6a4`
- reopened head: exactly the same accepted revision
- asset ID: `sha256:dd7b50dee138ea1eea989db24cfdbe6e15e05805fb7dbd11e72461718235bc66`
- asset object SHA-256: `dd7b50dee138ea1eea989db24cfdbe6e15e05805fb7dbd11e72461718235bc66`
- deterministic project bundle SHA-256: `f43e59200c34383c0248664d625bc3e16b5d17e5528dbfd2653d66c258bd9082`
- accepted mix-plan SHA-256: `1902ef2c67b3dd07d97a7489a484f85a2134fa61d3f102280b7dacd4985eb6df`
- reopened mix-plan SHA-256: exactly the same
- accepted WAV SHA-256: `d5a190023088865cfb4e60640c3db484483e6304e702ca2657218bbd5e89da26`
- reopened WAV SHA-256: exactly the same

The proof records all of the following as `true`:

- `accepted_blueprint_equal_after_import`
- `project_integrity_before_export`
- `project_integrity_after_import`
- `pending_preview_head_unchanged`
- `pending_preview_not_promoted_across_restart`
- `fresh_browser_runtime_authority_state_empty`
- `fresh_browser_mixer_state_exact`
- `fresh_browser_mix_hashes_exact`
- `generic_commit_bypass_after_reopen_blocked`
- `corrupt_persisted_audio_fails_closed`

The proof also records:

- `rendered_audio_is_canonical = false`
- `browser_state_is_canonical = false`
- `runtime_preview_is_canonical = false`
- `recording_claimed = false`
- `realtime_device_engine_claimed = false`
- `plugin_hosting_claimed = false`
- `console_error_count = 0`
- `page_error_count = 0`
- `request_failure_count = 0`

## Parent Issue #95 closure evaluation

Issue `#95 — Audio Track / Clip / Mixer Foundation v0` defined a bounded native audio-production substrate rather than a complete commercial DAW.

Repository evidence now covers its required foundation end-to-end:

| Foundation requirement | Evidence status |
| --- | --- |
| immutable content-addressed audio assets + integrity | **R0 VALIDATED** |
| accepted stable audio tracks/clips through Preview→Accept | **R1 VALIDATED** |
| deterministic bounded multitrack mixer + reproducible stereo WAV | **R2 VALIDATED** |
| truthful Browser arrangement/mixer surface using the same authority path | **R3 VALIDATED** |
| persistence/export/import + fresh-process/browser reopen + exact mix reproduction | **R4 VALIDATED** |
| pending runtime state remains non-canonical after restart | **R4 VALIDATED** |
| tampered persisted audio fails closed after import | **R4 VALIDATED** |
| existing permanent regressions preserved | **20/20 SUCCESS on exact R4 pre-validation head** |

Therefore, **the evidence supports closing parent Issue #95 after ATCM-R4 itself is promoted to canonical main and the separate state-only closure is green**.

That future closure is strictly a bounded foundation closure. It must not be interpreted as completion of MUSICA's general-purpose/commercial workstation objective.

## Explicit non-claims

ATCM-R4 and the eventual bounded closure of Issue #95 do **not** validate or claim:

- microphone/line-input recording;
- ASIO/CoreAudio/WASAPI or another low-latency real-time device callback engine;
- low-latency monitoring guarantees;
- VST3/AU/CLAP or other third-party plugin hosting;
- generalized buses/sends/sidechains;
- plugin delay / latency compensation;
- sample-rate conversion;
- warp/time-stretch/pitch-shift;
- destructive waveform editing, comping or take lanes;
- mastering-grade processing;
- commercial release qualification, supported production SLA or migration guarantees;
- cloud/multi-user creative authority.

## Maximum validated claim

> **MUSICA can persist and deterministically reopen an exact accepted native-audio arrangement and bounded mixer state across Project Bundle export/import, a fresh Studio process and a fresh Browser session, reproduce the exact project-bound R2 mix plan and WAV bytes, discard non-canonical pending runtime Preview state across restart, and fail closed on generic authority bypass or corrupted persisted audio.**

## Promotion rule

This validation record creates a successor exact head and therefore does not itself authorize merge. **All 20 permanent workflows must succeed again on that successor head.** Only then may PR #114 be expected-head squash merged and Issue #111 completed.

After canonical R4 merge, perform a separate state-only closure that records R4 completion and closes parent Issue #95 only for its bounded `Audio Track / Clip / Mixer Foundation v0` scope. The next commercial-workstation mission must be selected independently from the governing product target rather than smuggled into #95.

**Repository evidence remains authoritative over conversation/model memory.**
