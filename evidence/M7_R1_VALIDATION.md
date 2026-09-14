# M7-R1 Validation — Bounded Canonical Automation Runtime & Blueprint Integration

**Status:** `PRE-MERGE DURABLE VALIDATION — BOUNDED CORE RUNTIME`  
**Issue:** `#71`  
**PR:** `#72`  
**Pre-durable exact head:** `8e472f01399100f7c1c0ccfe6a07c3a09c038a93`

## Validated claim

M7-R1 validates only the following bounded authority path:

```text
legacy or automation-capable accepted Blueprint
→ backward-compatible optional canonical automation material
→ deterministic automation-material SHA-256
→ source-bound AutomationEditCandidate
→ stable lane/point identity + time/range + inherited lock authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit M2 Accept only
→ accepted immutable revision
```

Exactly five point primitives are implemented and exercised:

- `INSERT_POINT`
- `DELETE_POINT`
- `MOVE_POINT`
- `SET_VALUE`
- `SET_INTERPOLATION`

No lane create/delete, parameter reassignment, Browser automation lane, automation-to-audio lowering, plug-in mapping/hosting, DAW automation reconciliation, MIDI/OSC real-time control or arbitrary tempo-map authority is claimed.

## Pre-durable exact-head CI

All repository gates completed successfully on `8e472f01399100f7c1c0ccfe6a07c3a09c038a93`:

| Gate | Run | Result |
|---|---:|---|
| M7-R1 Automation Runtime Evidence | `34795521288` | **SUCCESS** |
| M7-R0 Automation Contract Evidence | `34795521244` | **SUCCESS** |
| MUSICA CI | `34795521183` | **SUCCESS** |
| M6-R4 Interchange Note Reconciliation | `34795521173` | **SUCCESS** |
| M6-R3 Real-Browser Exact-Note Evidence | `34795521254` | **SUCCESS** |
| M6-R2 Piano-Roll Evidence | `34795521178` | **SUCCESS** |
| M6-R1 Exact-Note Edit Evidence | `34795521226` | **SUCCESS** |
| M5-R3 DAWproject Evidence | `34795521207` | **SUCCESS** |
| M5-R4 Paired Audio Evidence | `34795521222` | **SUCCESS** |

The integrated CI additionally completed Python 3.11/3.12 contract/runtime tests, Browser E2E and FluidSynth evidence successfully.

## Dedicated evidence reproducibility

Dedicated workflow `34795521288`:

1. ran M7-R0 + M7-R1 contract/runtime tests;
2. generated the M7-R1 canonical evidence tree twice;
3. required `diff -qr` byte identity between A/B trees;
4. uploaded the canonical A tree only after the equality gate passed.

Result: **SUCCESS**.

## Artifact inspection

- artifact name: `musica-m7-r1-automation-runtime-evidence`
- artifact ID: `10328788906`
- GitHub packaging SHA-256: `c9baf4699fcf36137c07c7b26691a129d2779635632d62f35c2d5ca380c5b9e4`
- independently downloaded ZIP SHA-256: **same as GitHub packaging digest**
- internal `manifest.json` SHA-256: `b21dfd8e6b7c61ceee8b5613f8c65bb4857209a050cffe92eb8cabe33232ed5e`
- manifest-declared files: **14/14 SHA-256 + byte-size exact matches**
- extracted artifact files: **15 total including `manifest.json`**

## Machine proof facts

The canonical `proof.json` establishes:

- legacy Blueprint bytes remain unchanged;
- legacy Blueprint contains no fabricated canonical automation;
- legacy/no-automation source uses a deterministic empty-material hash;
- positive Preview is `READY_FOR_PREVIEW`;
- Preview has no project mutation authority;
- Preview has no Music IR mutation authority;
- repeated positive Preview construction is deterministic;
- all five ratified point primitives are exercised;
- project ref remains unchanged before explicit Accept;
- explicit M2 Accept advances the ref exactly once;
- accepted project integrity is `PASS`;
- accepted revision count is `2`;
- accepted Blueprint equals the Preview Blueprint;
- stale automation-material source binding yields `BLOCKED / STALE_SOURCE`;
- HARD exact-value lock yields `BLOCKED / HARD_LOCK_VIOLATION` under `L-M7-R1-EVIDENCE-VALUE`;
- HARD point-presence lock yields `BLOCKED / HARD_LOCK_VIOLATION` under `L-M7-R1-EVIDENCE-PRESENCE`;
- direct M2 commit cannot bypass inherited HARD automation authority and the accepted ref is preserved.

Source bindings recorded by the proof:

- source Blueprint SHA-256: `27657c18cb03ea75c1403debd5a23c51cc4c9a4ee582048794ab1fc4aa9eae45`
- source Automation Material SHA-256: `f89e7a0842b38aabc7a859803b2d98b6568c549545ca249f594159203d32b056`
- accepted Blueprint SHA-256: `0b637f11802c600cc5d67f6523a2077bb9e343b64008184e61055a12699702bd`
- accepted Automation Material SHA-256: `173e3dfc12d3f8e46fe7f2ba29f643d1d8b84abed62006a3f13964fbb6469b3e`

## Fail-closed authority properties

R1 demonstrates that accepted automation authority does not depend on array index, Browser coordinates, renderer/plugin state or external DAW state. Stable `lane_id` and `point_id` remain the edit/lock identity boundary.

The Blueprint contract remains backward compatible because `materials.automation` and `materials.automation_locks` are optional. Legacy projects are not migrated or reverse-inferred into automation.

Inherited automation locks are enforced by `validate_revision`, so bypassing the dedicated Preview API and attempting a direct M2 commit does not bypass HARD authority.

## Corrected pre-ratification workflow wiring

An earlier dedicated workflow attempt on an earlier head failed before executing R1 tests because the R0 test filename was wired as singular instead of the repository's plural filename. The path was corrected before this pre-durable head. The successful exact-head evidence above is the ratification basis; the earlier workflow wiring error is not treated as runtime evidence.

## Explicit non-claims

M7-R1 does **not** validate:

- Browser Studio automation-lane UI;
- real-browser automation editing or conflict UX;
- automation lowering into Music IR or renderer control events;
- audible automation rendering;
- VST/AU/CLAP parameter mapping or hosting;
- external DAW automation import/export/reconciliation;
- MIDI CC / OSC / live control;
- lane creation/deletion or parameter reassignment;
- arbitrary tempo maps;
- human-subject usability or perceptual benefit.

## Promotion rule

This durable validation file does not promote M7-R1 by itself. The successor exact head containing this file must rerun the same dedicated M7-R1 gate and all existing regressions successfully. Its uploaded M7-R1 evidence must also be independently inspected and compared against the pre-durable evidence before expected-head merge.

**Repository evidence remains authoritative over conversation/model memory.**
