# M7-R6 Validation — Truthful Audible Automation Capability & Browser Lifecycle Inspection

Status: **VALIDATED — BOUNDED TRUTHFUL AUDITION INSPECTION**

M7-R6 is validated only for the bounded truthful-inspection lifecycle described here. Repository evidence remains authoritative over conversation/model memory.

## 1. Validated claim

> MUSICA can expose a separate, versioned, read-only Studio automation audition inspection contract that truthfully reports the already validated bounded `mix.gain / project / normalized` renderer mapping, pending audible Preview state, exact Preview WAV/MIDI hashes, accepted artifact identity and source, Discard restoration, explicit Accept lineage, and restart/reopen persistence, without rewriting the historical R2 automation view or granting Browser/audio/renderer reverse authority.

The validated renderer mapping family remains exactly:

```text
parameter_id = mix.gain
scope        = project
owner_id     = null
unit         = normalized
renderer     = musica-reference-local
```

`synth.cutoff` remains explicitly unmapped. M7-R6 does not add another renderer mapping family, canonical MIDI-CC semantics, plug-in/DAW automation authority, real-time control, arbitrary tempo maps, spline curves or perceptual/mastering claims.

## 2. Truthfulness boundary

M7-R6 preserves the historical `studio-automation-view-v0` contract unchanged, including:

```text
capabilities.audible_automation_validated = false
```

That historical value is not reinterpreted or retroactively upgraded.

R6 adds a separate `studio-automation-audition-v0` inspection surface derived from trusted Studio state:

```text
historical accepted automation state
+ trusted R5 pending.detail.studio_audition
+ exact accepted artifact/fallback media identity
→ studio-automation-audition-v0 projection
→ localhost read-only HTTP inspection
→ non-authoritative Browser inspector
```

The Browser inspector does not create authority. Canonical transitions still occur only through the existing explicit M2 Accept path.

## 3. Exact lineage

- Issue: `#86`
- implementation PR: `#87`
- branch: `m7-r6-truthful-audition-inspection`
- canonical base/main: `4c2960e7e10329c34fda05e6ae146e9cb382fb5f`
- exact pre-durable head: `af11315c777f761179ca3d94bfed1a6e472dd315`
- exact successor evidence head: `93129768ff4b33c663eeeccda22c1d07faea0872`

The implementation changes exactly these ten paths before the durable validation record:

```text
.github/workflows/m7-r6-truthful-audition-inspection-evidence.yml
e2e/test_m7_r6_browser.py
schemas/studio-automation-audition-v0.schema.json
src/musica/m7_r6_demo.py
src/musica/m7_r6_e2e.py
src/musica/studio_automation_audition.py
src/musica/studio_http.py
src/musica/studio_web/automation_audition.css
src/musica/studio_web/automation_audition.js
tests/test_m7_r6_studio_audition_inspection.py
```

The successor head differs from the pre-durable head by exactly one file:

```text
evidence/M7_R6_VALIDATION.md
```

No runtime, schema, test or workflow file changed between pre-durable and successor evidence heads.

M7-R6 does not modify the canonical Blueprint schema, canonical automation schema, Music IR schema, R3 execution schema, R4 renderer mapping family, M2 project authority, MIDI renderer semantics, or the frozen R2 automation-view schema.

## 4. Pre-durable exact-head permanent gates — 14/14 SUCCESS

Exact head: `af11315c777f761179ca3d94bfed1a6e472dd315`

| Workflow | Run | Result |
|---|---:|---|
| MUSICA CI | `35043531087` | SUCCESS |
| M7-R6 Truthful Audition Inspection Evidence | `35043531200` | SUCCESS |
| M7-R5 Studio Audible Automation Evidence | `35043531150` | SUCCESS |
| M7-R4 Audible Automation Evidence | `35043531174` | SUCCESS |
| M7-R3 Automation Lowering Evidence | `35043531186` | SUCCESS |
| M7-R2 Real-Browser Automation Evidence | `35043531292` | SUCCESS |
| M7-R1 Automation Runtime Evidence | `35043531147` | SUCCESS |
| M7-R0 Automation Contract Evidence | `35043531190` | SUCCESS |
| M6-R4 Interchange Note Reconciliation | `35043531154` | SUCCESS |
| M6-R3 Real-Browser Exact-Note Evidence | `35043531172` | SUCCESS |
| M6-R2 Piano-Roll Evidence | `35043531042` | SUCCESS |
| M6-R1 Exact-Note Edit Evidence | `35043531047` | SUCCESS |
| M5-R4 Paired Audio Evidence | `35043531157` | SUCCESS |
| M5-R3 DAWproject Evidence | `35043531103` | SUCCESS |

## 5. Successor exact-head permanent gates — 14/14 SUCCESS

Exact successor head: `93129768ff4b33c663eeeccda22c1d07faea0872`

| Workflow | Run | Result |
|---|---:|---|
| MUSICA CI | `35044535273` | SUCCESS |
| M7-R6 Truthful Audition Inspection Evidence | `35044535253` | SUCCESS |
| M7-R5 Studio Audible Automation Evidence | `35044535247` | SUCCESS |
| M7-R4 Audible Automation Evidence | `35044535284` | SUCCESS |
| M7-R3 Automation Lowering Evidence | `35044535269` | SUCCESS |
| M7-R2 Real-Browser Automation Evidence | `35044535228` | SUCCESS |
| M7-R1 Automation Runtime Evidence | `35044535289` | SUCCESS |
| M7-R0 Automation Contract Evidence | `35044535227` | SUCCESS |
| M6-R4 Interchange Note Reconciliation | `35044535237` | SUCCESS |
| M6-R3 Real-Browser Exact-Note Evidence | `35044535226` | SUCCESS |
| M6-R2 Piano-Roll Evidence | `35044535209` | SUCCESS |
| M6-R1 Exact-Note Edit Evidence | `35044535233` | SUCCESS |
| M5-R4 Paired Audio Evidence | `35044535219` | SUCCESS |
| M5-R3 DAWproject Evidence | `35044535224` | SUCCESS |

On both heads the R6 workflow itself completed all of the following successfully:

1. bounded Studio automation regression suite;
2. real-Chromium accepted → Preview → Discard → Preview → explicit Accept → restart/reopen lifecycle;
3. deterministic evidence A generation;
4. deterministic evidence B generation;
5. `diff -qr artifacts/m7-r6-a artifacts/m7-r6-b` byte-tree reproducibility proof;
6. evidence artifact upload.

## 6. Pre-durable R6 artifact integrity

Artifact:

- artifact ID: `10426461920`
- artifact name: `musica-m7-r6-truthful-audition-inspection-evidence`
- packaging ZIP SHA-256: `cb808f29c166eb373d1feb2d64010bb44663c882d454c49608195bf544376ae3`
- archive size: `5,651,185` bytes
- archive files: **55**

The workflow intentionally uploads deterministic evidence A and the real-browser evidence tree after proving A/B equality; deterministic evidence B is generated and compared in CI but is not retained in the uploaded artifact.

### Deterministic evidence A

- internal manifest SHA-256: `926c0608c5998ceaa1ac0f49c19dbf4f293acc180d0e2433d067b369d32b953a`
- files including manifest: **14**
- manifest records: **13/13 exact SHA-256 + byte-size matches**
- accepted revision: `rev-studio-25899a82ea1f87628cc0f71c`
- accepted WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- accepted MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`

### Real-Chromium evidence

- internal manifest SHA-256: `8c937ee986866eebcec693f88eba80e9da202b5dc42b1c7ddf0faf89c7eddb9d`
- files including manifest: **18**
- manifest records: **17/17 exact SHA-256 + byte-size matches**
- accepted revision: `rev-studio-936e0b5dd40975266c59606e`
- accepted WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- accepted MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- real Browser screenshots: **5** lifecycle states

## 7. Successor R6 artifact integrity and reproducibility

Successor artifact:

- artifact ID: `10426332617`
- artifact name: `musica-m7-r6-truthful-audition-inspection-evidence`
- packaging ZIP SHA-256: `dff062e068a73c5a6e134913327576e32cfc5aa7e7761b80a3d6b650a980d7dd`
- archive size: `5,648,182` bytes
- archive files: **55**

### Deterministic evidence

- successor deterministic manifest SHA-256: `926c0608c5998ceaa1ac0f49c19dbf4f293acc180d0e2433d067b369d32b953a`
- successor manifest records: **13/13 exact SHA-256 + byte-size matches**
- extracted pre-durable vs successor deterministic evidence: **14 files / 0 differences**
- accepted revision remains `rev-studio-25899a82ea1f87628cc0f71c`
- accepted WAV remains `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- accepted MIDI remains `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`

### Real-Chromium evidence

- successor Browser manifest SHA-256: `b1ca6fbf9cfb72b344dde0eb9ffc81710e935292b1ec7d6bf2ab2e458c95cb1c`
- successor Browser manifest records: **17/17 exact SHA-256 + byte-size matches**
- accepted WAV remains `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- accepted MIDI remains `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- `proof.json` is byte/semantic identical between pre-durable and successor Browser evidence;
- historical R2 view, initial accepted state and discarded state are byte/semantic identical;
- mapped/unmapped lane sets remain exactly `["A-MIX-GAIN"]` / `["B-SYNTH-CUTOFF"]`;
- expected superseded-audio abort count remains exactly `2`;
- accepted/reopened media identity is exact within each run and converges on the same WAV/MIDI bytes across runs.

The real-browser tree is intentionally not required to be byte-identical across independent runs because session IDs, generated candidate revision IDs, cache-bust URL values and screenshots contain run-local identity. Those values carry no canonical authority. The stable semantic proof and exact media bytes are the promotion criteria.

The ZIP packaging digest is also not expected to be byte-stable.

## 8. Exact lifecycle proof

Independent artifact inspection proves:

- root accepted media is truthfully reported as `fallback_render` before an accepted artifact exists;
- accepted mapping is exactly `["A-MIX-GAIN"]`;
- unsupported mapping is exactly `["B-SYNTH-CUTOFF"]`;
- historical R2 `audible_automation_validated=false` remains unchanged;
- pending audible Preview reports `canonical=false`;
- pending Preview reports `project_ref_unchanged=true`;
- pending Preview reports `reverse_promotion_authorized=false`;
- Browser-computed SHA-256 of served Preview WAV equals the trusted pending inspection hash;
- Browser-computed SHA-256 of served Preview MIDI equals the trusted pending inspection hash;
- accepted media identity is not contaminated while Preview is pending;
- Discard removes pending audition state and restores the original accepted identity;
- repeating the same deterministic edit produces byte-identical WAV/MIDI and identical deterministic inspection evidence;
- explicit Accept advances exactly one accepted revision;
- accepted WAV source becomes `bound_artifact` and equals the exact Preview WAV;
- accepted MIDI source becomes `bound_artifact` and equals the exact Preview MIDI;
- restart/reopen preserves the exact accepted artifact identity and served bytes;
- unsupported-only `synth.cutoff` Preview reports `automation_applied=false` and `output_differs_from_baseline=false`;
- `canonical=false`;
- `browser_mutation_authorized=false`;
- `project_mutation_authorized=false`;
- `reverse_promotion_authorized=false`;
- `explicit_accept_required=true`.

The stable Browser proof is identical on pre-durable and successor runs, including:

- Browser console errors: `0`;
- Browser page errors: `0`;
- unexpected Browser request failures: `0`;
- expected superseded audio aborts: `2`;
- `real_chromium_used=true`;
- `historical_r2_view_preserved=true`;
- `accepted_mapping_mix_gain_only=true`;
- `unsupported_cutoff_truthfully_unmapped=true`;
- `browser_audio_hash_matches_pending_inspection=true`;
- `browser_midi_hash_matches_pending_inspection=true`;
- `explicit_accept_advanced_exactly_once=true`;
- `reopen_preserves_exact_bound_artifacts=true`.

## 9. Browser request-cancellation classification

During source changes, Chromium may abort a superseded `<audio>` request when the Studio replaces the cache-busted media URL during Preview/Discard/Accept transitions.

The R6 evidence driver allows only the narrow expected case:

```text
GET .../media/audio.wav?v=...: net::ERR_ABORTED
```

and records it separately in `expected-media-aborts.json`.

Both pre-durable and successor Browser runs recorded exactly **2** expected media aborts. All other request failures remain fail-closed. This classification does not weaken transport or API failure detection outside the exact superseded-audio case.

## 10. Explicit non-claims

M7-R6 does **not** validate or claim:

- a second canonical automation parameter mapping;
- canonical MIDI CC semantics for `mix.gain`;
- arbitrary part-scope renderer automation;
- VST/AU/CLAP hosting or device automation;
- DAW automation import/export/reconciliation;
- real-time MIDI/OSC automation;
- lane creation/deletion or parameter reassignment;
- arbitrary tempo-map automation;
- spline/bezier/exponential interpolation;
- Browser, audio, renderer or inspection-state reverse authority;
- perceptual quality, mastering quality or human preference;
- production latency/SLA guarantees.

## 11. Promotion verdict

All successor promotion conditions are satisfied:

1. **14/14 permanent workflows SUCCESS** on the pre-durable head;
2. **14/14 permanent workflows SUCCESS** on the successor head;
3. pre-durable and successor R6 artifacts independently inspected;
4. deterministic manifest integrity is **13/13** on both artifacts;
5. Browser manifest integrity is **17/17** on both artifacts;
6. deterministic evidence is **14 files / 0 differences** across pre-durable and successor runs;
7. Browser semantic `proof.json` is identical across runs;
8. accepted WAV/MIDI hashes are unchanged across deterministic and Browser paths;
9. mapped/unmapped boundary remains exactly `A-MIX-GAIN` / `B-SYNTH-CUTOFF`;
10. historical R2 contract remains unchanged and truthful;
11. authority remains non-canonical with no reverse promotion;
12. no excluded capability is newly claimed.

Therefore M7-R6 is **VALIDATED — BOUNDED TRUTHFUL AUDITION INSPECTION**.

The final validation-record head containing this verdict must itself reproduce the permanent 14-workflow set before PR #87 is eligible for expected-head merge.
