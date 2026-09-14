# M7 Automation & Continuous-Control Authority v0 / M7 자동화·연속제어 권한 v0

**Status:** `RATIFIED — M7-R0 CONTRACT + M7-R1 CORE RUNTIME + M7-R2 BROWSER SURFACE VALIDATED`  
**R0 Issue/PR:** `#68 / #69`  
**R1 Issue/PR:** `#71 / #72`  
**R2 Issue/PR:** `#74 / #75`  
**Durable evidence:** `evidence/M7_R0_VALIDATION.md`, `evidence/M7_R1_VALIDATION.md`, `evidence/M7_R2_VALIDATION.md`  
**Next bounded extension:** `M7-R3 — Deterministic Automation Lowering & Derived Execution Boundary`

## 1. Authority invariant

```text
accepted Blueprint automation material
→ trusted deterministic lowering
→ derived execution state
→ renderer/interchange adapters in later bounded milestones

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
derived execution event → fabricated canonical automation
Music IR / renderer / plug-in state → accepted Blueprint
Browser DOM/canvas coordinate → canonical identity
DAW lane/index → stable MUSICA identity
AI-generated curve → implicit acceptance
backend address / MIDI CC → canonical parameter identity
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
- fixed-tempo project bound through R2;
- derived `track_id`, renderer addresses, MIDI CCs and plug-in IDs are not canonical identity.

## 4. Trusted automation edit vocabulary

Exactly five stable-ID point primitives are validated:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
```

Lane create/delete and parameter reassignment remain out of scope.

Every candidate binds:

```text
project_id
revision_id
blueprint_sha256
automation_material_sha256
```

Stale source fails closed. Complete resulting material is revalidated for stable IDs, canonical order, unique beats/target signatures, declared range, project time bound and Blueprint ownership.

## 5. Preview / Accept authority

`src/musica/automation_edit.py` implements the bounded trusted-core path. A valid candidate creates a non-canonical automation Preview and cannot mutate Project refs or Music IR directly. Only explicit existing M2 acceptance may advance canonical project authority.

Validated invariant:

```text
Preview construction → accepted ref unchanged
explicit Accept → exactly one immutable M2 revision advance
Discard → accepted ref unchanged
blocked candidate → no pending automation Preview / no accepted mutation
```

M7-R2 additionally blocks automation Preview installation when another Studio Preview is already pending, preventing cross-surface displacement.

## 6. Automation lock authority

`automation-lock-v0` supports:

```text
HARD | SOFT
exact | range | presence
```

Inherited HARD locks cannot be removed, semantically changed, or violated. Direct M2 `commit_revision()` does not bypass automation authority because revision validation includes inherited automation conflicts.

R2 proves HARD exact and HARD presence violations through real Browser controls. Conflict code and lock context remain visible while no pending Preview or accepted ref mutation occurs.

## 7. M7-R2 Browser authority

Browser Studio Inspect is now validated as a non-canonical projection/proposal surface:

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

Browser geometry remains presentation only. Point-table keyboard selection is deliberately part of the evidence path so authority does not depend on pointer hit-testing or pixel coordinates.

Legacy projects show `NO CANONICAL AUTOMATION`; they do not reverse-infer automation from semantics, audio, Music IR or renderer state.

## 8. M7-R2 final evidence

Implementation merge/main:

`b5f73ac8ebf83b0bfdcca277924af9b7c0fcc263`

Pre-durable exact head:

`5396d38dad12247d8c55a40d677738fc51357569`

Final evidence-bearing successor head:

`90b6d3eec6621cd2d666c544863d1c8e28fd145f`

Successor successful gates:

- M7-R2 `34798196898`;
- MUSICA CI `34798196910`;
- M7-R1 `34798196888`;
- M7-R0 `34798196884`;
- M6-R4 `34798196893`;
- M6-R3 `34798196887`;
- M6-R2 `34798196909`;
- M6-R1 `34798196960`;
- M5-R3 `34798196949`;
- M5-R4 `34798196938`.

Successor M7-R2 artifact:

- artifact ID `10330402763`;
- packaging SHA-256 `dd192e04c12ce9d8f7e474717ac365acc0d2fb00ba2b8d9e5e4ea4cbe9d67ef2`;
- internal manifest SHA-256 `c3a4026394408b266943d3f9aca15393112780cf13114efd8f8a56b3e520f133`;
- manifest: **19/19 exact SHA-256 + byte-size matches**;
- pre-durable vs successor `proof.json`: **identical**.

The real-Chromium proof covers all five point primitives, Preview non-authority, Discard, explicit Accept, restart/reopen persistence, HARD exact/presence conflicts, stale source, legacy no-fabrication, stable Browser identity mapping and zero Browser console/page errors.

## 9. Derived lowering boundary discovered after R2

Existing `music-ir-v0` `controlEvent` is explicitly MIDI-like:

```text
type = control
controller = 0..127
value = 0..127
```

Existing compiler uses CC11/74/71 for semantic preview controls, and the local WAV renderer interprets those CCs directly. Therefore a canonical automation `parameter_id` such as a backend-independent mix/filter parameter **must not be silently equated with a MIDI CC number**.

R3 must introduce and validate a deterministic backend-independent **derived automation execution contract** or equivalent typed layer before renderer-specific mapping.

Required one-way authority:

```text
accepted automation-material-v0
→ deterministic derived automation execution
→ later backend mapping
```

Forbidden:

```text
MIDI CC / plug-in address / renderer event
→ canonical parameter_id
```

## 10. Next bounded extension — M7-R3

R3 must prove:

1. accepted source binding to revision/Blueprint/material hash;
2. deterministic lane/point ordering and provenance retention;
3. quarter-note-beat → deterministic execution time/tick representation;
4. `hold` and `linear` semantics represented explicitly without renderer-dependent guesswork;
5. backend-independent `parameter_id` preserved in the derived layer;
6. unsupported parameter/unit/scope combinations fail closed or are explicitly marked unsupported;
7. no canonical mutation from lowering;
8. no reverse authority from derived execution;
9. legacy/no-automation input produces explicit empty derived automation, not fabricated controls;
10. same input yields byte-identical machine evidence where timestamps/random IDs are absent.

R3 does **not** need to prove audible output differences.

## 11. Explicit non-claims

M7-R0→R2 do **not** validate:

- backend-independent canonical-automation lowering contract;
- audible automation rendering;
- arbitrary VST/AU/CLAP mapping/hosting;
- external DAW automation import/export/reconciliation;
- MIDI CC / OSC / real-time control as canonical automation authority;
- lane create/delete or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential curves;
- human-subject usability/perceptual benefit.

**Repository evidence remains authoritative over conversation/model memory.**
