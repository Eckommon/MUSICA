# M7 Automation & Continuous-Control Authority v0 / M7 자동화·연속제어 권한 v0

**Status:** `RATIFIED — M7-R0 CONTRACT + M7-R1 BOUNDED CORE RUNTIME VALIDATED`  
**R0 Issue/PR:** `#68 / #69`  
**R1 Issue/PR:** `#71 / #72`  
**Durable evidence:** `evidence/M7_R0_VALIDATION.md`, `evidence/M7_R1_VALIDATION.md`  
**Next bounded extension:** `M7-R2 — Browser Studio Automation Lane / Inspect Surface`

## 1. Authority invariant

```text
accepted Blueprint automation material
→ trusted deterministic lowering in a later milestone
→ derived Music IR / renderer automation events

user / AI / bounded proposal
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
Music IR control event → fabricated canonical automation
renderer / plug-in state → accepted Blueprint
Browser DOM/canvas coordinate → canonical identity
DAW lane/index → stable MUSICA identity
AI curve → implicit acceptance
```

## 2. Canonical representation

`automation-material-v0` is the canonical explicit continuous-control representation. M7-R1 integrates it backward-compatibly as optional `materials.automation` in accepted Blueprint authority. `materials.automation_locks` carries optional stable-ID automation locks.

A legacy Blueprint with no automation remains valid and unchanged. Missing automation means **no accepted explicit automation**. For source binding only, M7-R1 defines one deterministic canonical empty material; it is not written into the legacy Blueprint and is not inferred from semantics, Music IR, renderer or interchange state.

## 3. Ratified identity, scope and domains

- lane identity: stable `lane_id`, never array position;
- point identity: stable `point_id`, never beat position;
- parameter identity: backend-independent dotted `parameter_id`;
- scope: `project | part` only;
- canonical time: `quarter_note_beat`, origin `0.0`;
- units: `normalized | decibel | hertz | semitone | ratio`;
- interpolation: `hold | linear` only;
- fixed-tempo project bound in M7-R1;
- derived `track_id`, renderer addresses, MIDI CCs and plug-in IDs are not canonical identity.

## 4. M7-R1 runtime vocabulary

Exactly five stable-ID point primitives are validated:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
```

R1 does not implement lane create/delete or parameter reassignment.

Each candidate binds:

```text
project_id
revision_id
blueprint_sha256
automation_material_sha256
```

Stale source fails closed. The resulting complete material is revalidated for stable IDs, canonical order, unique beats/target signatures, declared range, project time bound and Blueprint ownership.

## 5. Preview / Accept authority

`src/musica/automation_edit.py` implements the bounded trusted-core path. A valid candidate creates a non-canonical `AutomationEditPreview`; it cannot mutate Project refs or Music IR. Only `accept_automation_edit_preview()` may pass a READY candidate to the existing M2 `commit_revision()` authority.

Validated invariant:

```text
Preview construction → accepted ref unchanged
explicit Accept → exactly one immutable M2 revision advance
blocked candidate → no candidate Blueprint / no accepted mutation
```

## 6. Automation lock authority

`automation-lock-v0` supports:

```text
HARD | SOFT
exact | range | presence
```

M7-R1 validates stable lane/point/parameter references. Root revisions require lock declarations to be self-consistent with their selected values. Child revisions carry inherited lock structure, while parent→candidate authority in `validate_revision()` determines violations.

This separation is intentional: a child HARD-lock conflict must remain a typed `automation_lock` authority conflict rather than being collapsed into a generic structural validation error.

Inherited HARD locks cannot be removed, semantically changed, or violated. Directly calling M2 `project.commit_revision()` does not bypass automation authority because `validate_revision()` includes `automation_revision_conflicts()`.

## 7. Semantic-control coexistence

Accepted explicit automation is a stronger exact creative commitment than a later high-level semantic proposal over the same protected scope. M7-R1 does not implement a broad semantic-to-automation overlap resolver, but it does not fabricate or silently regenerate canonical automation from semantic curves.

A future semantic overlap resolver must preserve this precedence and fail closed where necessary.

## 8. Derived lowering boundary

M7-R1 deliberately stops before renderer execution:

```text
accepted canonical automation
≠ Music IR automation execution
≠ renderer parameter automation
≠ plug-in automation
```

Future lowering may deterministically map canonical automation into derived execution events. Reverse promotion from derived events remains forbidden unless a separate source-bound reconciliation milestone proves it.

## 9. M7-R1 final evidence

Implementation merge/main:

`877ed9b7e7f90101ffcdb6891bd75631807053e2`

Final evidence-bearing head:

`abe1f9c92751e0cdde935b34f4a17f1e1fc20548`

Final successful gates:

- M7-R1 `34795684053`;
- M7-R0 `34795684183`;
- MUSICA CI `34795683991`;
- M6-R4 `34795684200`;
- M6-R3 `34795683988`;
- M6-R2 `34795683981`;
- M6-R1 `34795684023`;
- M5-R3 `34795684054`;
- M5-R4 `34795683984`.

Final M7-R1 artifact:

- artifact ID `10330005742`;
- packaging SHA-256 `178d86faf11bfd859b84fc0c60363a493f9ffa8530dab27567ccd0b2e03ea638`;
- internal manifest SHA-256 `b21dfd8e6b7c61ceee8b5613f8c65bb4857209a050cffe92eb8cabe33232ed5e`;
- pre-durable vs successor extracted evidence: **15 files / 0 differences**;
- pre-durable manifest: **14/14 exact SHA-256 + byte-size matches**.

The machine proof establishes legacy no-fabrication, deterministic source hashing, all five primitives, Preview non-authority, explicit M2 acceptance, stale-source blocking, HARD exact/presence lock blocking, direct-M2 bypass prevention and project integrity `PASS`.

## 10. Next bounded extension — M7-R2

M7-R2 may expose the existing R1 authority in Browser Studio Inspect:

```text
accepted automation material
→ Browser projection with stable lane/point mapping
→ bounded point gesture/edit form
→ typed AutomationEditCandidate
→ existing R1 Preview authority
→ Preview / Accept / Discard
```

Browser state must remain a projection/proposal surface. R2 must not implement or claim automation-to-audio lowering, plug-in/device mapping, DAW automation reconciliation or real-time MIDI/OSC.

## 11. Explicit non-claims

M7-R0/R1 do **not** validate:

- Browser automation-lane UI or real-browser automation editing;
- Music IR/renderer automation execution or audible automation;
- VST/AU/CLAP mapping/hosting;
- external DAW automation import/export/reconciliation;
- MIDI CC / OSC / real-time control;
- lane create/delete or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential curves;
- human-subject usability/perceptual benefit.

**Repository evidence remains authoritative over conversation/model memory.**
