# M7 Automation & Continuous-Control Authority v0 / M7 자동화·연속제어 권한 v0

**Status:** `RATIFIED — M7-R0 CONTRACT + R1 CORE RUNTIME + R2 BROWSER SURFACE + R3 DERIVED EXECUTION + R4 BOUNDED AUDIBLE EXECUTION VALIDATED`  
**R0 Issue/PR:** `#68 / #69`  
**R1 Issue/PR:** `#71 / #72`  
**R2 Issue/PR:** `#74 / #75`  
**R3 Issue/PR:** `#77 / #78`  
**R4 Issue/PR:** `#80 / #81`  
**Durable evidence:** `evidence/M7_R0_VALIDATION.md` → `evidence/M7_R4_VALIDATION.md`  
**Next bounded extension:** `M7-R5 — Studio Automation Audition & Accepted Artifact Persistence`

## 1. Authority invariant

```text
accepted Blueprint automation material
→ trusted deterministic R3 lowering
→ automation-execution-v0 (derived / non-canonical)
→ explicit R4 renderer-specific mapping policy
→ bounded audible renderer artifact/evidence
→ optional Studio audition/persistence integration in R5

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

Validated invariant through R2:

```text
Preview construction → accepted ref unchanged
explicit Accept → exactly one immutable M2 revision advance
Discard → accepted ref unchanged
blocked candidate → no pending automation Preview / no accepted mutation
```

R5 may change the audio produced for a validated Preview, but must not change this authority relationship.

## 5. M7-R3 derived execution authority

`automation-execution-v0` is an L4 derived sidecar. It binds exact accepted project/revision/Blueprint/material identity and lowers canonical beats to deterministic PPQ 480 ticks using Decimal `ROUND_HALF_UP` while preserving source beats, values, point IDs and `hold|linear` segment semantics.

Every lane remains `DERIVED_GENERIC` with typed backend mapping `UNMAPPED`. R3 grants no Project, Blueprint, renderer or reverse-promotion authority.

## 6. M7-R4 renderer authority

R4 adds `automation-render-plan-v0`, a renderer-specific derived object with exact Music IR and R3 execution SHA-256 binding.

The only validated mapping is:

```text
parameter_id = mix.gain
scope        = project
owner_id     = null
unit         = normalized
range        = [0.0, 1.0]
renderer     = musica-reference-local
```

Everything else, including `synth.cutoff`, remains typed unmapped/unsupported by the R4 reference renderer policy.

R4 application order is explicitly:

```text
existing deterministic reference synthesis/mix
→ existing safety normalization
→ mapped mix.gain envelope
→ clipping guard only
→ PCM WAV
```

There is no post-automation renormalization. Existing `render_wav()` / `wav_bytes()` and MIDI semantic-control bytes remain regression-stable.

## 7. MIDI/CC non-equivalence

Existing Music IR semantic preview controls may use CC11/74/71. These are **not** canonical M7 automation identities.

R4 explicitly proves:

```text
midi_cc_semantics_authorized = false
cc11_used_as_canonical_mix_gain = false
```

Therefore this remains forbidden:

```text
canonical mix.gain == MIDI CC11 by implication
```

Any future MIDI/plugin mapping requires its own explicit derived adapter contract and evidence.

## 8. M7-R4 final evidence

- implementation merge/main: `6f862dea15eea394f3e29ad7c91ef3e8b2cd767a`
- pre-durable exact head: `0166eb193f3df1269f3f8260753faed99de97e2d`
- final evidence-bearing successor head: `cae504d4582eb234b6bcb121fa4b96370c08069f`
- successor regression set: **12/12 SUCCESS**
- M7-R4 workflow `35002276837` — **SUCCESS**
- MUSICA CI `35002276941` — **SUCCESS**
- successor artifact `10410595918`
- internal manifest SHA-256 `532b225c9a40db44565fd617d5b5481049efcd9b337c022e6ab0b9af2a8110a4`
- render-plan SHA-256 `3821d05b18b55b81836bfcd271134bac3245fd3324bacb401647329d43049296`
- baseline WAV SHA-256 `efb3dfecd8b72545563a24617eaafaeea8ea22738103fa7703cb7efcfa0429c3`
- automated WAV SHA-256 `3137a946772c80286e9ba57df3081e3574be6cd4489d036359857ab75a2248a0`
- different PCM samples: **146,461**
- RMS ratios: linear `0.707450205`, hold `0.820013328`, after-last `0.750111392`
- pre-durable vs successor extracted artifact: **14 files / 0 differences**

## 9. R5 product boundary decision

Repository inspection after R4 shows `StudioService._render_to_cache()` still uses:

```text
compile_blueprint
→ render_midi
→ render_wav
```

for Preview, initial render and accepted-cache fallback. `StudioAutomationSurface.preview_automation_edit()` routes a trusted candidate into `_install_preview()`, which calls that same legacy cache renderer. Consequently the Browser automation Preview can be structurally correct while its Studio audio does not yet consume R3→R4 audible automation.

R5 therefore targets **Studio audition and accepted artifact persistence**, not a second automation mapping family.

Required one-way path:

```text
validated candidate Blueprint
→ compile_blueprint
→ R3 lower_automation
→ R4 build automation render plan
→ automation-aware Preview WAV
→ explicit Accept or Discard
```

Acceptance may bind the exact Preview WAV as the accepted revision artifact. Discard must remove Preview media without changing canonical state. Reopening the accepted project must serve the accepted revision artifact, not reverse-infer automation from audio.

## 10. R5 invariants

R5 must prove:

1. automation Preview audio uses R4 only when an eligible `mix.gain` lane exists;
2. legacy/no-automation Studio audio remains byte-compatible with the old path;
3. unsupported lanes stay unmapped and never become implicit MIDI/DSP mappings;
4. MIDI Preview bytes remain unchanged;
5. Preview audio cannot mutate the accepted branch ref;
6. Discard removes pending media and leaves accepted revision/artifacts unchanged;
7. Accept commits exactly one revision and binds the exact audible Preview artifact;
8. reopening/serving accepted media yields the accepted artifact bytes;
9. stale-preview and pending-preview conflict behavior remains fail-closed;
10. no audio/renderer artifact gains reverse canonical authority.

## 11. Explicit non-claims

M7-R0→R4 do **not** validate:

- Studio lifecycle integration of audible canonical automation;
- arbitrary parameter → renderer/MIDI/plugin mappings;
- arbitrary VST/AU/CLAP mapping/hosting;
- external DAW automation import/export/reconciliation;
- MIDI CC / OSC / real-time control as canonical automation authority;
- lane create/delete or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential curves;
- human-subject usability/perceptual benefit.

**Repository evidence remains authoritative over conversation/model memory.**