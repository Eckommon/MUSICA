# M7 Automation & Continuous-Control Authority v0 / M7 자동화·연속제어 권한 v0

**Status:** `RATIFIED — M7-R0 CONTRACT + R1 CORE RUNTIME + R2 BROWSER SURFACE + R3 DERIVED EXECUTION + R4 BOUNDED AUDIBLE EXECUTION + R5 STUDIO AUDITION/PERSISTENCE + R6 TRUTHFUL AUDITION INSPECTION VALIDATED`  
**R0 Issue/PR:** `#68 / #69`  
**R1 Issue/PR:** `#71 / #72`  
**R2 Issue/PR:** `#74 / #75`  
**R3 Issue/PR:** `#77 / #78`  
**R4 Issue/PR:** `#80 / #81`  
**R5 Issue/PR:** `#84 / #83`  
**R6 Issue/PR:** `#86 / #87`  
**Durable evidence:** `evidence/M7_R0_VALIDATION.md` → `evidence/M7_R6_VALIDATION.md`  
**Next bounded action:** `Post-M7 closure review & next-milestone selection`

## 1. Authority invariant

```text
accepted Blueprint automation material
→ trusted deterministic R3 lowering
→ automation-execution-v0 (derived / non-canonical)
→ explicit R4 renderer-specific mapping policy
→ bounded audible renderer artifact/evidence
→ R5 Studio pending audition artifact
→ explicit Accept only
→ existing M2 revision + bound artifact authority
→ R6 read-only truthful audition inspection

user / AI / bounded Browser proposal
→ source-bound AutomationEditCandidate
→ stable lane / point / parameter identity
→ lock + invariant authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept only
→ existing M2 revision authority
```

Forbidden authority remains:

```text
derived execution → fabricated canonical automation
Music IR / renderer / plug-in / audio state → accepted Blueprint
Browser DOM/canvas coordinate → canonical identity
Browser inspection state → canonical identity or acceptance
DAW lane/index → stable MUSICA identity
AI-generated curve → implicit acceptance
backend address / MIDI CC → canonical parameter identity
renderer mapping → reverse canonical promotion
accepted audio artifact → canonical automation inference
```

## 2. Canonical representation

`automation-material-v0` remains the canonical explicit continuous-control representation under accepted Blueprint `materials.automation`; `materials.automation_locks` carries optional stable-ID automation locks.

A legacy Blueprint with no automation remains valid and unchanged. Missing automation means **no accepted explicit automation**. Deterministic empty material/execution may be used for source binding only; it is not written into legacy Blueprint authority and is not inferred from semantic controls, Music IR, renderer, audio, Browser inspection or interchange state.

## 3. Ratified identity, scope and domains

- stable `lane_id` and `point_id` are canonical identities;
- `parameter_id` is backend-independent and dotted;
- scope is `project | part`;
- canonical time is quarter-note beat, origin 0;
- units are `normalized | decibel | hertz | semitone | ratio`;
- interpolation is `hold | linear` only;
- derived track IDs, renderer addresses, MIDI CCs and plug-in IDs are not canonical identity.

Validated point primitives remain exactly:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
```

Lane creation/deletion and parameter reassignment remain out of scope.

## 4. Preview / Accept authority

`src/musica/automation_edit.py` implements trusted-core edit authority. A valid candidate creates a non-canonical Preview and cannot mutate Project refs or Music IR directly. Only explicit existing M2 acceptance may advance canonical project authority.

Validated through R6:

```text
Preview construction → accepted ref unchanged
R5 audible audition install → accepted ref unchanged
R6 Browser inspection → read-only, accepted ref unchanged
Discard → pending audition removed, accepted ref/artifacts unchanged
explicit Accept → exactly one immutable M2 revision advance
Accept → exact pending WAV/MIDI bound to accepted revision
reopen → accepted artifact bytes served unchanged
blocked/failing candidate → no accepted mutation
```

Audio availability or Browser visibility never implies acceptance.

## 5. M7-R3 derived execution authority

`automation-execution-v0` is a derived sidecar. It binds exact accepted project/revision/Blueprint/material identity and lowers canonical beats to deterministic PPQ 480 ticks using Decimal `ROUND_HALF_UP` while preserving source beats, values, point IDs and `hold|linear` segment semantics.

Every lane remains `DERIVED_GENERIC` with typed backend mapping `UNMAPPED`. R3 grants no Project, Blueprint, renderer or reverse-promotion authority.

## 6. M7-R4 renderer authority

R4 adds `automation-render-plan-v0`, a renderer-specific derived object with exact Music IR and R3 execution SHA-256 binding.

The only validated mapping remains:

```text
parameter_id = mix.gain
scope        = project
owner_id     = null
unit         = normalized
range        = [0.0, 1.0]
renderer     = musica-reference-local
```

Everything else, including `synth.cutoff`, remains typed unmapped/unsupported by the current reference-renderer policy.

R4 application order remains:

```text
existing deterministic reference synthesis/mix
→ existing safety normalization
→ mapped mix.gain envelope
→ clipping guard only
→ PCM WAV
```

There is no post-automation renormalization. Existing MIDI semantic-control bytes remain regression-stable.

## 7. MIDI/CC non-equivalence

Existing Music IR semantic preview controls may use CC11/74/71. These are **not** canonical M7 automation identities.

The following remains forbidden:

```text
canonical mix.gain == MIDI CC11 by implication
```

Any future MIDI/plugin mapping requires its own explicit derived adapter contract and evidence.

## 8. M7-R5 Studio audition authority

R5 integrates the validated R3→R4 path into the Studio pending Preview lifecycle without changing M2 authority.

Validated R5 lifecycle:

```text
Preview WAV ≠ unautomated baseline WAV
Preview WAV = accepted WAV = reopened WAV
Preview MIDI = accepted MIDI = reopened MIDI
```

Reference evidence hashes remain:

- Preview/accepted/reopened WAV: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- Preview/accepted/reopened MIDI: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`

R5 creates no new acceptance path. Existing `StudioService.accept_preview()` remains the transition that can commit the candidate revision and bind its exact pending WAV/MIDI artifacts.

## 9. Historical R2 Browser contract remains historical

`studio-automation-view-v0` remains frozen and still contains:

```text
audible_automation_validated = false
```

This is historically truthful for the bounded R2 contract. R6 does not reinterpret or mutate that field.

## 10. M7-R6 truthful audition-inspection authority

R6 closes the post-R5 truthfulness gap with a **separate versioned read-only contract**, `studio-automation-audition-v0`.

```text
historical accepted automation state
+ trusted R5 pending.detail.studio_audition
+ exact accepted/fallback media identity
→ studio-automation-audition-v0
→ localhost GET inspection endpoint
→ non-authoritative Browser inspector
```

R6 truthfully exposes:

- renderer policy identity;
- mapped lane IDs and unmapped lane IDs;
- pending `PREVIEW · NOT ACCEPTED` state;
- `automation_applied` and baseline-difference status;
- render-plan and Preview media hashes;
- exact accepted revision and WAV/MIDI source (`bound_artifact | fallback_render`);
- Discard restoration;
- explicit Accept lineage;
- restart/reopen artifact identity.

The Browser computes served media SHA-256 during real-Chromium evidence and verifies it against trusted inspection hashes. This remains verification only, not authority.

Validated R6 boundaries:

```text
mapped_lane_ids   = [A-MIX-GAIN]
unmapped_lane_ids = [B-SYNTH-CUTOFF]
canonical = false
browser_mutation_authorized = false
project_mutation_authorized = false
reverse_promotion_authorized = false
explicit_accept_required = true
```

Unsupported-only `synth.cutoff` audition reports `automation_applied=false` and `output_differs_from_baseline=false`.

Durable evidence: `evidence/M7_R6_VALIDATION.md`.

R6 exact lineage:

- pre-durable head: `af11315c777f761179ca3d94bfed1a6e472dd315`
- successor head: `93129768ff4b33c663eeeccda22c1d07faea0872`
- final validation-record head: `0ea3fd976a8b63293d434bb427f7dfeffb68fcfd`
- implementation/validation merge main: `1de099e8d3e489c818ae561ddfb0c43c4ffdcbfc`
- pre-durable, successor and final-record permanent gates: **14/14 SUCCESS** each
- deterministic manifest: `926c0608c5998ceaa1ac0f49c19dbf4f293acc180d0e2433d067b369d32b953a`
- deterministic pre-durable vs successor: **14 files / 0 differences**

## 11. Post-M7 decision boundary

No `M7-R7` or `M8` is currently ratified in the repository. M7-R6 therefore closes the currently planned M7 sequence.

The next action is an evidence-based architecture/product closure review. It must select exactly one bounded next milestone from the remaining product gaps before implementation begins. Renderer mapping expansion is **not** the default continuation merely because R4→R6 validated one family.

## 12. Explicit non-claims

M7-R0→R6 do **not** validate:

- a second canonical parameter mapping family;
- arbitrary parameter → renderer/MIDI/plugin mappings;
- arbitrary VST/AU/CLAP mapping/hosting;
- external DAW automation import/export/reconciliation;
- MIDI CC / OSC / real-time control as canonical automation authority;
- lane create/delete or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential curves;
- live OpenAI provider execution;
- human-subject usability/perceptual benefit;
- destructive waveform editing, cloud collaboration or production installer/signing.

**Repository evidence remains authoritative over conversation/model memory.**