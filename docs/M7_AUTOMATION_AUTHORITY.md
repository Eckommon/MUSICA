# M7 Automation & Continuous-Control Authority v0 / M7 자동화·연속제어 권한 v0

**Status:** `RATIFIED — M7-R0 CONTRACT + R1 CORE RUNTIME + R2 BROWSER SURFACE + R3 DERIVED EXECUTION + R4 BOUNDED AUDIBLE EXECUTION + R5 STUDIO AUDITION/PERSISTENCE VALIDATED`  
**R0 Issue/PR:** `#68 / #69`  
**R1 Issue/PR:** `#71 / #72`  
**R2 Issue/PR:** `#74 / #75`  
**R3 Issue/PR:** `#77 / #78`  
**R4 Issue/PR:** `#80 / #81`  
**R5 Issue/PR:** `#84 / #83`  
**Durable evidence:** `evidence/M7_R0_VALIDATION.md` → `evidence/M7_R5_VALIDATION.md`  
**Next bounded extension:** `M7-R6 — Truthful Audible Automation Capability & Browser Lifecycle Inspection`

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
DAW lane/index → stable MUSICA identity
AI-generated curve → implicit acceptance
backend address / MIDI CC → canonical parameter identity
renderer mapping → reverse canonical promotion
accepted audio artifact → canonical automation inference
```

## 2. Canonical representation

`automation-material-v0` remains the canonical explicit continuous-control representation under accepted Blueprint `materials.automation`; `materials.automation_locks` carries optional stable-ID automation locks.

A legacy Blueprint with no automation remains valid and unchanged. Missing automation means **no accepted explicit automation**. Deterministic empty material/execution may be used for source binding only; it is not written into legacy Blueprint authority and is not inferred from semantic controls, Music IR, renderer, audio or interchange state.

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

Validated through R5:

```text
Preview construction → accepted ref unchanged
R5 audible audition install → accepted ref unchanged
Discard → pending audition removed, accepted ref/artifacts unchanged
explicit Accept → exactly one immutable M2 revision advance
Accept → exact pending WAV/MIDI bound to accepted revision
reopen → accepted artifact bytes served unchanged
blocked/failing candidate → no accepted mutation
```

Audio availability never implies acceptance.

## 5. M7-R3 derived execution authority

`automation-execution-v0` is an L4 derived sidecar. It binds exact accepted project/revision/Blueprint/material identity and lowers canonical beats to deterministic PPQ 480 ticks using Decimal `ROUND_HALF_UP` while preserving source beats, values, point IDs and `hold|linear` segment semantics.

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

R5 integrates the already validated R3→R4 path into the actual Studio pending Preview lifecycle without changing M2 authority.

`StudioAutomationSurface._install_audible_preview()`:

1. requires an existing trusted pending `automation_edit` Preview;
2. reads the candidate Blueprint only from that pending trusted Preview;
3. compiles candidate Music IR;
4. derives R3 execution;
5. builds the R4 reference-renderer plan;
6. replaces only the pending Preview WAV;
7. records `studio_audition` proof as non-canonical detail;
8. verifies the accepted project ref is unchanged;
9. clears the pending Preview fail-closed on any audible-installation failure.

R5 does not create a new acceptance path. Existing `StudioService.accept_preview()` remains the only transition that can commit the candidate revision and bind its exact pending WAV/MIDI artifacts.

Validated R5 lifecycle:

```text
Preview WAV ≠ unautomated baseline WAV
Preview WAV = accepted WAV = reopened WAV
Preview MIDI = accepted MIDI = reopened MIDI
```

Reference evidence hashes:

- R5 manifest: `ab5c99c4ab474eccac17b727cf0a502061f2691ffae5bbfab734572a90e5c772`
- Preview/accepted/reopened WAV: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- Preview/accepted/reopened MIDI: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- pre-durable vs successor R5 evidence: **16 files / 0 differences**
- R4 preservation recheck: **14 files / 0 differences**

Implementation merge/main: `43488fe85bb6c2fde19dc27d0dabfdb7587d7f1f`.

## 9. Historical R2 Browser contract remains historical

R5 intentionally does **not** silently rewrite `studio-automation-view-v0`. That schema still contains:

```text
audible_automation_validated = false
```

This field describes the bounded R2 view contract as ratified at R2. R5 proof is currently carried separately under pending `studio_audition` detail.

After R5 this creates a product truthfulness gap: the Studio can perform a validated audible audition, but the versioned Browser automation view does not yet formally expose the renderer policy, mapped/unmapped lanes, automation-applied status, Preview media hashes or accepted-artifact lineage.

## 10. M7-R6 authority decision

R6 must close the truthfulness/inspection gap **without mutating the historical meaning of v0 and without expanding renderer mapping coverage**.

Preferred design:

```text
R5 studio_audition proof
→ new versioned Browser audition/capability contract
→ explicit renderer_policy_id
→ supported/mapped lane IDs
→ unsupported/unmapped lane IDs
→ automation_applied + output_differs_from_baseline
→ render-plan + media hashes
→ pending PREVIEW lifecycle visibility
→ accepted artifact identity after Accept/reopen
```

R6 must preserve:

- accepted Blueprint as canonical authority;
- Preview as non-canonical;
- explicit Accept as the only project-state transition;
- current R4 mapping set exactly as-is;
- no inference from audio back into automation;
- no mutation of the old R2 contract by reinterpretation.

## 11. Explicit non-claims

M7-R0→R5 do **not** validate:

- a truthful versioned Browser contract for R5 audible capabilities/artifact lineage;
- a second canonical parameter mapping family;
- arbitrary parameter → renderer/MIDI/plugin mappings;
- arbitrary VST/AU/CLAP mapping/hosting;
- external DAW automation import/export/reconciliation;
- MIDI CC / OSC / real-time control as canonical automation authority;
- lane create/delete or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential curves;
- human-subject usability/perceptual benefit.

**Repository evidence remains authoritative over conversation/model memory.**