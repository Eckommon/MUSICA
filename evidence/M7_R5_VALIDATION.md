# M7-R5 Validation — Studio Automation Audition & Accepted Artifact Persistence

Status: **VALIDATED — BOUNDED STUDIO AUDITION & ARTIFACT PERSISTENCE**

M7-R5 is validated only for the bounded lifecycle and renderer mapping described here. Repository evidence remains authoritative over conversation/model memory.

## 1. Validated claim

> MUSICA can route an already trusted Studio automation Preview through the validated M7-R3 automation execution boundary and the validated M7-R4 bounded reference-renderer `mix.gain` mapping, expose the resulting audible WAV as a non-canonical Preview, discard it without changing accepted authority, explicitly Accept the exact Preview WAV/MIDI as immutable revision artifacts, and reopen the project with byte-identical accepted media.

The bounded audible mapping remains exactly:

```text
parameter_id = mix.gain
scope        = project
owner_id     = null
unit         = normalized
renderer     = musica-reference-local
```

`synth.cutoff` remains explicitly unmapped. M7-R5 does not add arbitrary parameter mappings, MIDI-CC canonical semantics, plug-in hosting, DAW automation, real-time control, arbitrary tempo maps or human/perceptual quality claims.

## 2. Authority and lifecycle boundary

```text
accepted Blueprint revision
→ source-bound automation edit candidate
→ R1 trusted automation authority
→ READY_FOR_PREVIEW
→ existing Studio pending Preview
→ candidate Music IR
→ M7-R3 automation-execution-v0
→ M7-R4 automation-render-plan-v0
→ bounded automation-aware pending WAV
→ PREVIEW · NOT ACCEPTED
→ Discard OR explicit Accept
→ existing M2 immutable revision/artifact authority
```

The R5 audible installation path:

- does not advance the accepted project ref while Preview is pending;
- keeps Browser/renderer state non-canonical;
- preserves existing Preview MIDI generation;
- replaces only the pending automation Preview WAV through R3→R4;
- clears the pending Preview on any audible-installation failure;
- relies on existing M2 `accept_preview()` / `bind_artifacts()` for the only canonical transition;
- grants no reverse-promotion authority from audio, Music IR, execution or render plan.

The pre-existing R2 view capability `audible_automation_validated=false` deliberately remains unchanged. R5 proof is recorded separately as `studio_audition`; the older R2 contract is not silently rewritten.

## 3. Exact lineage

- Issue: `#84`
- implementation PR: `#83`
- branch: `m7-r5-studio-audible-automation`
- canonical base/main: `0e9d8cec4b9fb8ad476cd4460741b470b6c02baf`
- exact pre-durable head: `298a46a4de360d697c2fe55006cd17966c3bf1e8`
- exact successor evidence head: `87dd85cb2ff2f0a576db24c6b87c7ad16a32bb29`

The implementation changes only these eight implementation/test/workflow paths, plus this durable evidence record:

```text
.github/workflows/m7-r5-studio-audible-automation-evidence.yml   added
docs/M7_R5_IMPLEMENTATION_NOTE.md                               added
e2e/test_m7_r2_browser.py                                       modified
src/musica/automation_renderer.py                               modified
src/musica/m7_r5_demo.py                                        added
src/musica/studio_automation.py                                 modified
tests/test_m7_r2_studio_automation.py                           modified
tests/test_m7_r5_studio_audition.py                             added
evidence/M7_R5_VALIDATION.md                                    added
```

The implementation does not modify Project/M2 authority, the Blueprint schema, Music IR schema, MIDI renderer semantics or the canonical automation schema.

## 4. Pre-durable exact-head evidence — 13/13 SUCCESS

| Workflow | Run | Result |
|---|---:|---|
| MUSICA CI | `35006549861` | SUCCESS |
| M7-R5 Studio Audible Automation Evidence | `35006549735` | SUCCESS |
| M7-R4 Audible Automation Evidence | `35006549800` | SUCCESS |
| M7-R3 Automation Lowering Evidence | `35006549730` | SUCCESS |
| M7-R2 Real-Browser Automation Evidence | `35006549777` | SUCCESS |
| M7-R1 Automation Runtime Evidence | `35006549766` | SUCCESS |
| M7-R0 Automation Contract Evidence | `35006549928` | SUCCESS |
| M6-R4 Interchange Note Reconciliation | `35006549898` | SUCCESS |
| M6-R3 Real-Browser Exact-Note Evidence | `35006549760` | SUCCESS |
| M6-R2 Piano-Roll Evidence | `35006549734` | SUCCESS |
| M6-R1 Exact-Note Edit Evidence | `35006549736` | SUCCESS |
| M5-R4 Paired Audio Evidence | `35006549749` | SUCCESS |
| M5-R3 DAWproject Evidence | `35006549888` | SUCCESS |

MUSICA CI passed Python 3.11 and Python 3.12 full tests, Browser E2E and existing renderer/evidence regeneration paths.

## 5. Successor exact-head evidence — 13/13 SUCCESS

The successor head containing the initial durable record reproduced the full permanent set:

| Workflow | Run | Result |
|---|---:|---|
| MUSICA CI | `35007183799` | SUCCESS |
| M7-R5 Studio Audible Automation Evidence | `35007183694` | SUCCESS |
| M7-R4 Audible Automation Evidence | `35007183618` | SUCCESS |
| M7-R3 Automation Lowering Evidence | `35007183747` | SUCCESS |
| M7-R2 Real-Browser Automation Evidence | `35007183921` | SUCCESS |
| M7-R1 Automation Runtime Evidence | `35007183858` | SUCCESS |
| M7-R0 Automation Contract Evidence | `35007183812` | SUCCESS |
| M6-R4 Interchange Note Reconciliation | `35007183616` | SUCCESS |
| M6-R3 Real-Browser Exact-Note Evidence | `35007183671` | SUCCESS |
| M6-R2 Piano-Roll Evidence | `35007183701` | SUCCESS |
| M6-R1 Exact-Note Edit Evidence | `35007183912` | SUCCESS |
| M5-R4 Paired Audio Evidence | `35007183662` | SUCCESS |
| M5-R3 DAWproject Evidence | `35007183746` | SUCCESS |

## 6. M7-R5 artifact reproducibility

Pre-durable artifact:

- artifact ID: `10411768231`
- packaging ZIP SHA-256: `17d8dcca3afb9092362ebf12fc1664b227e70ff6c81fbf1bfa87c6b1b0b1ef63`
- internal `manifest.json` SHA-256: `ab5c99c4ab474eccac17b727cf0a502061f2691ffae5bbfab734572a90e5c772`
- archive contents: **16 files including `manifest.json`**
- manifest records: **15/15 exact SHA-256 + byte-size matches**

Successor artifact:

- artifact ID: `10412286568`
- packaging ZIP SHA-256: `8b594f39209324545b179c7d005aae6ad132d99ca4ed0678bfeedcb82d385b6b`
- internal `manifest.json` SHA-256: `ab5c99c4ab474eccac17b727cf0a502061f2691ffae5bbfab734572a90e5c772`
- archive contents: **16 files including `manifest.json`**
- extracted pre-durable vs successor evidence: **16 files / 0 differences**

The ZIP packaging digest is not expected to be byte-stable; the extracted evidence tree is byte-identical.

## 7. Exact Preview / Accept / reopen media lineage

Candidate revision:

`rev-studio-b7d60fa218d4bfb951654b44`

Reference hashes are identical in pre-durable and successor artifacts:

- baseline pending Studio WAV SHA-256: `e049e83bdda5a1c5710bd4d09b3010ab414d27d5a6705398aae120ae9deac5b8`
- automation-aware Preview WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- accepted revision WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- reopened accepted WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- Preview / accepted / reopened MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- renderer plan SHA-256: `f65952c4cefba8970939a6f9e6bfb1cbc0e3565987519996d9c087195922b6c8`

The Preview WAV differs from the unautomated pending baseline while Preview/accepted/reopened media are byte-identical where required.

## 8. Lifecycle, mapping and fail-closed proof

Independent artifact inspection proves:

- mapped lane IDs are exactly `["A-MIX-GAIN"]`;
- unmapped lane IDs are exactly `["B-SYNTH-CUTOFF"]`;
- `mix.gain` produces an audibly different Preview WAV;
- unsupported `synth.cutoff` remains typed unmapped and is not guessed into CC/DSP control;
- Preview remains non-canonical and accepted project head is unchanged before Accept;
- Discard removes the pending Preview cache and restores previously accepted audio/MIDI bytes;
- repeating the same source-bound Preview produces deterministic descriptor/proof/WAV/MIDI evidence;
- explicit Accept advances exactly to the candidate revision;
- Accept binds exactly two artifacts, WAV and MIDI;
- accepted WAV/MIDI equal the exact Preview WAV/MIDI;
- project integrity remains `PASS` after Accept;
- reopening through a new `StudioService` returns the same accepted revision and byte-identical WAV/MIDI;
- `canonical=false`;
- `reverse_promotion_authorized=false`;
- the R2 view capability remains `audible_automation_validated=false`.

`StudioAutomationSurface._install_audible_preview()` clears the pending non-canonical Preview on any failure after the pending automation Preview exists, including pending media-read, compilation/lowering, render-plan, automation-render or project-ref integrity failure. No failure in this path may advance or mutate accepted M2 authority.

## 9. R4 performance refactor is byte-preserving

R5 exposed shared-runner latency in the R4 Decimal PCM gain loop. The implementation precompiles invariant Decimal point/segment values once and advances the active segment monotonically rather than rebuilding constants and rescanning all segments per sample. Interpolation formulas, tick/sample positions, Decimal arithmetic, segment boundaries and `ROUND_HALF_UP` PCM quantization remain unchanged.

R4 evidence at the pre-durable R5 head and successor R5 head is internally byte-identical:

- pre-durable R4 artifact ID: `10412200698`
- successor R4 artifact ID: `10411844041`
- extracted R4 evidence: **14 files / 0 differences**
- successor R4 packaging ZIP SHA-256: `d160a98d582d2a8dfe888f68da1e42b84c354e9b96efc0e3e0b6984516dc39ff`
- R4 internal manifest SHA-256: `532b225c9a40db44565fd617d5b5481049efcd9b337c022e6ab0b9af2a8110a4`
- R4 render plan SHA-256: `3821d05b18b55b81836bfcd271134bac3245fd3324bacb401647329d43049296`
- R4 baseline WAV SHA-256: `efb3dfecd8b72545563a24617eaafaeea8ea22738103fa7703cb7efcfa0429c3`
- R4 automated A/B WAV SHA-256: `3137a946772c80286e9ba57df3081e3574be6cd4489d036359857ab75a2248a0`

Thus the R4 optimization changes latency only, not evidence bytes or automation semantics.

## 10. Test-only observation-window hardening

R5 performs deterministic local audio rendering before the HTTP response and Browser Preview state become visible. Shared CI runners can exceed the old five-second test observation windows.

Two test-only changes increase observation windows without changing product/API semantics:

- `tests/test_m7_r2_studio_automation.py`: loopback HTTP client timeout `5s → 30s`;
- `e2e/test_m7_r2_browser.py`: Playwright `expect` assertion timeout set to `30s`.

These are not product latency guarantees, server deadlines or acceptance-policy changes. The real-browser R2 workflow succeeds with the same Preview/Discard/Accept authority assertions on both pre-durable and successor heads.

## 11. Explicit non-claims

M7-R5 does **not** validate or claim:

- arbitrary canonical parameter → renderer/MIDI/plugin mapping;
- canonical automation as MIDI CC semantics;
- arbitrary part-scope renderer automation;
- VST/AU/CLAP hosting or device automation;
- external DAW automation import/export/reconciliation;
- real-time MIDI/OSC automation;
- arbitrary tempo-map automation;
- spline/bezier/exponential curves;
- asynchronous/background rendering architecture;
- production latency/SLA guarantees;
- mastering quality, human preference or perceptual superiority.

## 12. Promotion verdict

All successor promotion conditions are satisfied:

1. **13/13 permanent workflows SUCCESS** on the successor head;
2. successor M7-R5 artifact independently inspected;
3. manifest integrity preserved;
4. **16 files / 0 differences** between extracted pre-durable and successor R5 evidence;
5. Preview/accepted/reopened WAV and MIDI hashes unchanged;
6. mapped/unmapped lane boundaries unchanged;
7. durable R4 lineage preserved with **14 files / 0 differences**;
8. authority remains non-canonical with no reverse promotion;
9. no excluded capability newly claimed.

Therefore M7-R5 is **VALIDATED — BOUNDED STUDIO AUDITION & ARTIFACT PERSISTENCE**.
