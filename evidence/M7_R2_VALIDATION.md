# M7-R2 Validation — Browser Studio Automation Lane / Inspect Surface

Status: **VALIDATION CANDIDATE — SUCCESSOR RERUN REQUIRED**

This record durably binds the pre-durable M7-R2 evidence-bearing head. It does **not** by itself promote M7-R2; promotion requires the same full regression set to succeed again on the successor exact head containing this record.

## 1. Validated claim boundary

The maximum evidence-supported claim at this point is:

> Browser Studio Inspect can project and edit already-accepted canonical `materials.automation` through stable `lane_id` / `point_id` identities and the existing source-bound M7-R1 Preview/Accept authority, while Browser presentation state remains non-canonical.

The real-browser evidence uses the keyboard-accessible stable-ID point table as the authority interaction path. Plot coordinates remain presentation data only.

M7-R2 does **not** claim:

- automation lowering into Music IR;
- audible automation rendering/effect validation;
- plug-in/device parameter mapping or VST/AU/CLAP hosting;
- DAW automation import/export/reconciliation;
- MIDI CC / OSC / real-time control;
- lane creation/deletion or parameter reassignment;
- arbitrary tempo maps or spline/bezier/exponential interpolation;
- human-subject usability or perceptual evidence.

## 2. Pre-durable exact head

- branch: `m7-r2-browser-automation`
- exact head: `5396d38dad12247d8c55a40d677738fc51357569`
- base canonical main: `2a041c11545566ea3812e861f035b13b83d50257`
- Issue: #74
- draft implementation PR: #75

## 3. Exact-head workflow evidence — 10/10 SUCCESS

All required pull-request workflows for the exact pre-durable head completed successfully:

| Workflow | Run | Result |
|---|---:|---|
| MUSICA CI | `34797990443` | SUCCESS |
| M7-R2 Real-Browser Automation Evidence | `34797990458` | SUCCESS |
| M7-R1 Automation Runtime Evidence | `34797990423` | SUCCESS |
| M7-R0 Automation Contract Evidence | `34797990434` | SUCCESS |
| M6-R4 Interchange Note Reconciliation | `34797990418` | SUCCESS |
| M6-R3 Real-Browser Exact-Note Evidence | `34797990435` | SUCCESS |
| M6-R2 Piano-Roll Evidence | `34797990430` | SUCCESS |
| M6-R1 Exact-Note Edit Evidence | `34797990447` | SUCCESS |
| M5-R3 DAWproject Evidence | `34797990460` | SUCCESS |
| M5-R4 Paired Audio Evidence | `34797990461` | SUCCESS |

The M7-R2 dedicated job also ran the M7-R0/R1/R2 service/runtime regression set before real Chromium and both stages succeeded.

## 4. Real-browser artifact lineage

Artifact:

- name: `musica-m7-r2-real-browser-automation-e2e`
- artifact ID: `10330267731`
- GitHub/ZIP SHA-256: `775cfe8b225e6ed08607cad2412357b1a3b89c7fb37af1fa952eac38981be46f`
- internal evidence `manifest.json` SHA-256: `519ccd24235b96159fcd0e0830eb998ba00ec614a0a1c3f9b821606d30ee1542`
- manifest evidence records: **19 / 19 hash + size exact**
- browser: Playwright Chromium
- Browser console errors: **0**
- Browser page errors: **0**

Source binding recorded by the manifest:

- source Blueprint SHA-256: `a0a9d616420d02013de63114112899821f4ae80a620e587be0357e9b8eddd359`
- source automation-material SHA-256: `c613af24e1ff00a5b7a0544f8ffa4b0a1b98365e8acadccd2c895a1915cc49db`
- accepted revision: `rev-studio-969835931bcb47fd7aec6257`
- accepted Blueprint SHA-256: `60bad22205464f48648d9617e971cd04263def5e6b21ba7470fc7570954b2782`
- accepted automation-material SHA-256: `3efd78f45d49c1ae9f72a4a12b0bdd61f1c577c5ce2040a4b6b35423c8f09472`

## 5. Machine proof results

The dedicated real-Chromium proof establishes:

- accepted Browser projection is bound to project ID, accepted revision ID, Blueprint SHA-256 and automation-material SHA-256;
- stable lane/point DOM identities are present;
- all five canonical M7-R1 point primitives are exercised through visible Browser controls:
  - `INSERT_POINT`
  - `DELETE_POINT`
  - `MOVE_POINT`
  - `SET_VALUE`
  - `SET_INTERPOLATION`;
- Preview leaves the accepted ref unchanged;
- Browser visibly marks automation Preview as **NOT ACCEPTED**;
- Discard preserves the accepted ref;
- explicit Accept advances once to the candidate revision through the existing Studio/M2 boundary;
- accepted automation survives service/browser restart and reopen;
- HARD exact-value lock conflict is visible, BLOCKED, and installs no Preview;
- HARD point-presence deletion conflict is visible, BLOCKED, and installs no Preview;
- stale-source conflict is visible, BLOCKED, installs no Preview, and refreshes/rebinds the Browser projection to the current accepted source;
- legacy/no-automation accepted revisions expose no canonical automation and fabricate no lanes;
- Browser has no direct project mutation authority;
- Browser has no Music IR mutation authority;
- `audible_automation_validated = false`;
- no external provider network is required for this evidence.

The service-level regression also proves automation Preview cannot silently displace an already-pending Studio Preview from another surface; existing pending state and the accepted ref remain intact.

## 6. Evidence interpretation

The uploaded archive contains workspace objects and preview MIDI/WAV generated by the existing generic Studio Preview infrastructure. Those files are **not evidence of audible automation behavior** because M7-R2 does not lower canonical automation into Music IR. The authoritative R2 proof is canonical automation state, source binding, Browser stable identity mapping, trusted M7-R1 authority resolution, Preview/Accept/Discard behavior, conflict UX, persistence and repository integrity.

Browser screenshots are visual evidence and may vary at the byte level between runs. Browser-generated candidate IDs may also vary. Therefore successor promotion requires semantic proof/manifest integrity and exact-head workflow success, not whole-archive byte identity.

## 7. Promotion gate

M7-R2 may be promoted only after the successor exact head containing this file satisfies all of the following:

1. the same 10 workflows complete with SUCCESS;
2. the successor M7-R2 artifact is independently inspected;
3. all required positive proof booleans remain true;
4. blocked-preview and direct-authority booleans remain false as designed;
5. Browser console/page errors remain zero;
6. source/accepted hash bindings and manifest record integrity remain valid;
7. no excluded capability is newly claimed by documentation, UI or evidence.

Until then, M7-R2 remains **not yet promoted**.
