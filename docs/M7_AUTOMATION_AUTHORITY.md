# M7 Automation & Continuous-Control Authority v0 / M7 자동화·연속제어 권한 v0

**Status:** `RATIFIED — M7-R0 CONTRACT + M7-R1 CORE RUNTIME + M7-R2 BROWSER SURFACE + M7-R3 DERIVED EXECUTION VALIDATED`  
**R0 Issue/PR:** `#68 / #69`  
**R1 Issue/PR:** `#71 / #72`  
**R2 Issue/PR:** `#74 / #75`  
**R3 Issue/PR:** `#77 / #78`  
**Durable evidence:** `evidence/M7_R0_VALIDATION.md`, `evidence/M7_R1_VALIDATION.md`, `evidence/M7_R2_VALIDATION.md`, `evidence/M7_R3_VALIDATION.md`  
**Next bounded extension:** `M7-R4 — Reference Renderer Automation Mapping & Audible Evidence`

## 1. Authority invariant

```text
accepted Blueprint automation material
→ trusted deterministic R3 lowering
→ automation-execution-v0 (derived / non-canonical)
→ explicit renderer-specific mapping policy in later bounded milestones
→ renderer artifact + evidence

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
Music IR / renderer / plug-in state → accepted Blueprint
Browser DOM/canvas coordinate → canonical identity
DAW lane/index → stable MUSICA identity
AI-generated curve → implicit acceptance
backend address / MIDI CC → canonical parameter identity
renderer mapping → reverse canonical promotion
```

## 2. Canonical representation

`automation-material-v0` is the canonical explicit continuous-control representation. It lives optionally under accepted Blueprint `materials.automation`; `materials.automation_locks` carries optional stable-ID automation locks.

A legacy Blueprint with no automation remains valid and unchanged. Missing automation means **no accepted explicit automation**. A deterministic empty material may be used for source binding only; it is not written into legacy Blueprint authority and is not inferred from semantic controls, Music IR, renderer or interchange state.

## 3. Ratified identity, scope and domains

- lane identity: stable `lane_id`, never array position;
- point identity: stable `point_id`, never beat position;
- parameter identity: backend-independent dotted `parameter_id`;
- scope: `project | part` only;
- canonical time: `quarter_note_beat`, origin `0.0`;
- units: `normalized | decibel | hertz | semitone | ratio`;
- interpolation: `hold | linear` only;
- fixed-tempo project bound through R3;
- derived `track_id`, renderer addresses, MIDI CCs and plug-in IDs are not canonical identity.

Exactly five stable-ID point primitives remain validated:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
```

Lane create/delete and parameter reassignment remain out of scope.

## 4. Preview / Accept authority

`src/musica/automation_edit.py` implements the trusted-core edit path. A valid candidate creates a non-canonical automation Preview and cannot mutate Project refs or Music IR directly. Only explicit existing M2 acceptance may advance canonical project authority.

Validated invariant:

```text
Preview construction → accepted ref unchanged
explicit Accept → exactly one immutable M2 revision advance
Discard → accepted ref unchanged
blocked candidate → no pending automation Preview / no accepted mutation
```

M7-R2 additionally blocks automation Preview installation when another Studio Preview is already pending, preventing cross-surface displacement.

## 5. M7-R2 Browser authority

Browser Studio Inspect is validated as a non-canonical projection/proposal surface:

```text
accepted materials.automation
→ source-bound Inspect projection
→ stable lane_id / point_id DOM data
→ keyboard/table/form editing
→ automation-edit-candidate-v0
→ existing R1 authority
→ READY_FOR_PREVIEW or BLOCKED
→ Preview / explicit Accept / Discard
```

Browser geometry remains presentation only. Legacy projects show `NO CANONICAL AUTOMATION`; they do not reverse-infer automation from semantics, audio, Music IR or renderer state.

## 6. M7-R3 derived execution authority

R3 introduces the versioned L4 compiled target sidecar:

```text
automation-execution-v0
```

It is explicitly:

```text
classification = derived_noncanonical
canonical = false
project_mutation_authorized = false
blueprint_mutation_authorized = false
reverse_promotion_authorized = false
renderer_mapping_authorized = false
audible_automation_validated = false
```

R3 binds exact accepted source identity:

```text
project_id
revision_id
blueprint_sha256
automation_material_sha256
explicit_automation_present
```

and records deterministic lowering policy:

```text
compiler_id      = musica-automation-lowering
compiler_version = 0.1.0
policy_id        = automation-execution-v0-generic-segments
ppq              = 480
tick_rounding    = decimal_nearest_half_up_nonnegative
```

Every lane preserves canonical provenance and remains:

```text
derivation_status = DERIVED_GENERIC
backend_mapping.status = UNMAPPED
```

No MIDI CC, plug-in address, renderer address or DAW lane is guessed.

## 7. R3 interpolation/time boundary

Canonical source points remain authoritative. Derived execution retains `point_id`, beat, value and interpolation while adding deterministic integer tick.

Each adjacent source pair becomes one explicit segment:

```text
start_point_id
end_point_id
start_tick / end_tick
start_value / end_value
interpolation = start source point outgoing interpolation
```

Beat→tick conversion uses Decimal `ROUND_HALF_UP` at PPQ 480. Distinct canonical beats that collapse to the same integer tick fail closed rather than silently losing timing resolution.

## 8. M7-R3 final evidence

Implementation merge/main:

`f4dbbf78c1556815228ef1446192a1308707eec9`

Pre-durable exact head:

`09eaa538128a302f82374764becf1ddfc87eafda`

Final evidence-bearing successor head:

`43d4568362cc26c23e9747da2a15b29c0cf4fe4d`

Successor successful gates:

- M7-R3 `34822272947`;
- MUSICA CI `34822272980`;
- M7-R2 `34822272949`;
- M7-R1 `34822272975`;
- M7-R0 `34822272967`;
- M6-R4 `34822272955`;
- M6-R3 `34822272953`;
- M6-R2 `34822272968`;
- M6-R1 `34822272956`;
- M5-R3 `34822273054`;
- M5-R4 `34822272987`.

Successor R3 artifact:

- artifact ID `10338193487`;
- packaging SHA-256 `48b157aefb9bd6067aa7a2d4b187693294a2b7417869c35a4daa56bea5d1f61c`;
- internal manifest SHA-256 `864135b90e650496e89d1e6f9b293e709f2fd187a3ddb639e155136c028207db`;
- derived execution SHA-256 `2874fc72e78fd817a53ad2c20348cf56403af53fa24fdfc57f7f2aa1ac2444c7`;
- manifest: **10/10 exact SHA-256 + byte-size matches**;
- pre-durable vs successor extracted evidence: **11 files / 0 differences**.

## 9. R4 renderer boundary decision

Existing Music IR `controlEvent` is MIDI-like and current semantic preview uses CC11/74/71. R4 must **not** equate canonical `mix.gain` with CC11.

The bounded R4 design is:

```text
validated Music IR
+
validated automation-execution-v0
↓ exact hashes
reference-renderer automation render plan
↓ explicit mapping registry
mix.gain / project / normalized
↓
deterministic reference-WAV gain envelope
↓
WAV + audio-difference evidence
```

The render plan should be a renderer-specific derived object that binds at minimum:

```text
music_ir_sha256
automation_execution_sha256
renderer_id
renderer_version
mapping_policy_id
```

Only `mix.gain` with `scope=project`, `unit=normalized` is eligible in R4. All other canonical lanes remain explicitly unmapped/unsupported by this renderer policy rather than guessed.

Recommended application semantics: evaluate the typed R3 `hold|linear` envelope over renderer time and apply it as a deterministic post-synthesis gain multiplier to the reference WAV mix. Keep existing `render_wav()` unchanged; add a separate automation-aware path so prior byte/regression claims remain stable.

## 10. R4 required audible evidence

R4 must prove at least:

1. exact Music IR hash and R3 execution hash binding;
2. renderer identity/version and mapping policy binding;
3. only `mix.gain/project/normalized` maps successfully;
4. unsupported parameter/scope/unit fails closed or remains typed unmapped;
5. `hold` produces the expected piecewise constant envelope;
6. `linear` produces the expected deterministic ramp;
7. automation-aware WAV differs from the no-automation baseline when the envelope is non-unity;
8. repeated automation-aware render is byte-identical;
9. measurable segment RMS/peak behavior tracks the gain envelope direction;
10. source Music IR/execution/Blueprint remain unchanged;
11. old MIDI and `render_wav()` bytes remain regression-stable;
12. no reverse authority from rendered audio to canonical automation.

R4 should not claim perceptual quality from these objective measurements.

## 11. Explicit non-claims

M7-R0→R3 do **not** validate:

- audible automation rendering;
- arbitrary parameter → renderer/MIDI/plugin mappings;
- arbitrary VST/AU/CLAP mapping/hosting;
- external DAW automation import/export/reconciliation;
- MIDI CC / OSC / real-time control as canonical automation authority;
- lane create/delete or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential curves;
- human-subject usability/perceptual benefit.

**Repository evidence remains authoritative over conversation/model memory.**