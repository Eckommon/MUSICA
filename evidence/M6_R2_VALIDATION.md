# M6-R2 Validation / M6-R2 검증 기록

**Milestone / 마일스톤:** `M6-R2 — Browser Studio Piano-Roll / Inspect Surface`

**Governing Issue / 지배 Issue:** `#57`

**Implementation PR / 구현 PR:** `#58`

**Validation class / 검증 분류:** `BOUNDED_BROWSER_INTEGRATION_EVIDENCE`

## 1. Verdict / 판정

M6-R2 has reached an evidence-backed implementation candidate for the bounded Browser Studio exact-note piano-roll / Inspect integration.

M6-R2는 제한된 Browser Studio exact-note piano-roll / Inspect 통합에 대해 근거가 결박된 구현 후보 상태에 도달했습니다.

Promotion to final `VALIDATED — BOUNDED BROWSER INTEGRATION` is effective only when the exact successor head containing this durable record passes the same required CI/evidence gates. Until that evidence-bearing rerun succeeds, this file records the validated pre-durable implementation evidence rather than authorizing merge by itself.

본 durable record를 포함한 exact successor head가 동일한 필수 CI/evidence gate를 통과한 경우에만 최종 `VALIDATED — BOUNDED BROWSER INTEGRATION` 승격이 유효합니다. 그 전까지 본 문서는 merge 권한 자체가 아니라 pre-durable 구현 검증 근거를 기록합니다.

## 2. Canonical starting point / 공식 시작점

- canonical main at M6-R2 start: `5e71afbf822dc4076c1821cc5cc2fe52cc944525`
- M6-R1 implementation merge: `7adf507630334021459e89055e98627d184f5354`
- M6-R1 state closure merge/main: `5e71afbf822dc4076c1821cc5cc2fe52cc944525`
- M6-R2 branch: `m6-r2-browser-piano-roll`
- pre-durable final implementation/evidence head: `1760076770757e53da47fd5e198765bc729df1f0`

## 3. Implemented browser integration boundary / 구현된 browser 통합 경계

M6-R2 exposes the already validated M6-R1 exact-note authority through the existing local-first Browser Studio without granting the browser, DOM, canvas, local arrays, or Music IR canonical mutation authority.

Implemented:

1. dedicated `studio-note-view-v0` browser-facing exact-note read contract;
2. `GET /v0/sessions/{id}/notes` deterministic accepted-note projection;
3. `POST /v0/sessions/{id}/preview/notes` delegation to the existing M6-R1 trusted authority;
4. additive `note_edit` support inside the existing Studio Preview contract;
5. explicit legacy `exact_note_editing_available=false` without reverse-mapping Music IR into canonical notes;
6. stable note identity and stable-ID note-lock visibility;
7. Inspect piano-roll presentation with accepted vs `PREVIEW · NOT ACCEPTED` distinction;
8. bounded UI controls for `INSERT / DELETE / MOVE / RESIZE / REPITCH / SET_VELOCITY`;
9. exact project/revision/Blueprint-hash source binding;
10. existing Studio Accept/Discard and M2 acceptance reused unchanged;
11. same-origin packaged JavaScript/CSS with prior loopback/CSP/no-upload/no-telemetry boundaries preserved;
12. dedicated service/HTTP/UI tests and canonical M6-R2 evidence workflow.

Primary implementation files are the M6-R2 changes in the Studio service, HTTP boundary, Browser Studio assets, schemas, tests, evidence runner and workflow attached to PR #58.

## 4. Authority proof / 권한 증명

Validated bounded path:

```text
Accepted exact-note Blueprint
→ Studio exact-note read projection
→ Browser Inspect piano-roll interaction/form input
→ typed NoteEditCandidate
→ M6-R1 exact source/lock/constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW — non-canonical
→ explicit Accept / Discard
→ existing M2 authority only
→ accepted exact-note Blueprint revision
```

Forbidden:

```text
DOM/canvas/browser-local note state → canonical project
Music IR direct mutation → canonical project
```

The canonical evidence proves:

```text
browser_project_mutation_authorized = false
music_ir_mutation_authorized = false
explicit_accept_required = true
```

## 5. Pre-durable exact-head CI / pre-durable exact-head CI

Exact head:

`1760076770757e53da47fd5e198765bc729df1f0`

Required workflows:

| Workflow / 워크플로 | Run | Result |
|---|---:|---|
| MUSICA CI | `34693409072` | **SUCCESS** |
| M6-R2 Piano-Roll Evidence | `34693409110` | **SUCCESS** |
| M6-R1 Exact-Note Edit Evidence | `34693409083` | **SUCCESS** |
| M5-R3 DAWproject Evidence | `34693409097` | **SUCCESS** |
| M5-R4 Paired Audio Evidence | `34693409080` | **SUCCESS** |

MUSICA CI also passed the required regression jobs on the exact head:

- Python 3.11 contracts/runtime job: `103552619830` — **SUCCESS**;
- Python 3.12 contracts/runtime + prior M0→M5-R1 evidence regeneration: `103552619918` — **SUCCESS**;
- M4-R3 real Chromium browser E2E job: `103552619907` — **SUCCESS**;
- M5-R2 Windows FluidSynth evidence job: `103552619928` — **SUCCESS**.

The dedicated M6-R2 evidence job `103552619855` also passed M6-R1/R2 precision tests, canonical evidence generation and artifact upload.

## 6. Final pre-durable M6-R2 artifact / 최종 pre-durable M6-R2 artifact

Canonical strengthened evidence run:

- workflow run: `34693409110`
- head: `1760076770757e53da47fd5e198765bc729df1f0`
- artifact name: `musica-m6-r2-piano-roll`
- artifact ID: `10297532769`
- artifact size: `1076246` bytes
- GitHub packaging digest: `sha256:abcb9011157a7dc0ad29722ea75b5b85250f0e5800acd61d1723e1df6bb47663`
- independently downloaded ZIP SHA-256: `abcb9011157a7dc0ad29722ea75b5b85250f0e5800acd61d1723e1df6bb47663`
- internal `manifest.json` SHA-256: `6e97d79b19248b03d2fe705223fb5f3c5de7ff95a2d80ef279e7fd86a8b27b7e`
- exact source Blueprint SHA-256: `b216c8772eb72de42160e0d104430307e9079d08dcc41af7be0e4832e5786aca`
- accepted Blueprint SHA-256: `74c10e3e72d160d70b2a4ae3c02cffc9eef9aa38287bd2053a205341918c5e73`
- accepted revision: `rev-studio-b8741a45061c15dde7738cc9`

All 13 files declared by the internal manifest were independently rehashed after download; every declared SHA-256 and byte size matched the extracted artifact exactly.

## 7. Evidence strengthening and reproducibility / 근거 강화 및 재현성

An earlier successful M6-R2 evidence run existed before the final determinism-strengthening commit:

### Earlier successful run

- run: `34693311732`
- head: `2bc5dc2fcdb413f20b46f4c21cd7431a23df5a42`
- artifact ID: `10298091979`
- GitHub packaging digest: `sha256:5223e372ac2c2c247b2efb23a90f9e7ce0769a46164d3f4e2d03a943b999fd57`
- internal manifest SHA-256: `283d2eeca16e8a757cdc70752dca05ad83d699f9f7974e8fbde87ca9e470ca12`

The final strengthening changed `source_view_deterministic` from a claim that could be satisfied without two independent reads into a proof that performs two independent `note_view()` calls and compares their actual outputs.

The extracted evidence trees were compared recursively:

- earlier file count: `58`;
- strengthened file count: `59`;
- differing paths: exactly `2`;
- `source-note-view-repeat.json` exists only in the strengthened artifact;
- `manifest.json` changed only to bind the new independent repeat file;
- all other evidence/workspace files are byte-identical across the two runs;
- `proof.json` is byte-identical across the two runs.

In the strengthened artifact:

- `source-note-view.json` SHA-256 = `fbeb40af823865f99f388c2af1578f1c40e2b2b511d38fc411f0763905df3df0`;
- `source-note-view-repeat.json` SHA-256 = `fbeb40af823865f99f388c2af1578f1c40e2b2b511d38fc411f0763905df3df0`;
- the two files are byte-identical.

This converts source-view determinism from an assumed/constant proof bit into independently materialized evidence while preserving every other canonical proof output.

## 8. Positive exact-note browser-integration proof / 양성 exact-note browser 통합 증명

The canonical evidence exercises all six M6-R1 operation types through the Studio note Preview boundary:

```text
INSERT
DELETE
MOVE
RESIZE
REPITCH
SET_VELOCITY
```

The proof records:

- `all_six_operations_exercised = true`;
- `preview_authority_status = READY_FOR_PREVIEW`;
- `preview_installed = true`;
- accepted ref unchanged before explicit Accept;
- stable-note diff present in Preview;
- inserted stable-ID note present;
- deleted stable-ID note absent;
- move/resize/repitch/velocity changes preserved after Accept;
- explicit Accept advances exactly to the validated candidate;
- accepted revision count = `2`;
- accepted project integrity = **PASS**;
- reopen preserves the accepted exact-note state.

`accepted-note-view.json` and `reopened-note-view.json` are byte-identical with SHA-256:

`c26ec5b54ef9a80f466f80f45149846cd99aa06b4b007c48b4d6d3dbaf6e100d`

## 9. Negative authority proofs / 음성 권한 증명

### Stale source

The canonical stale-source evidence records:

```text
status = BLOCKED
code = STALE_SOURCE
preview_installed = false
project_mutation_authorized = false
music_ir_mutation_authorized = false
```

### Stable-ID HARD note lock

The canonical HARD-lock evidence records:

```text
status = BLOCKED
code = HARD_LOCK_VIOLATION
preview_installed = false
```

These blocked cases do not install a pending Preview and do not advance canonical project authority.

## 10. Legacy compatibility / legacy 호환

For a motif-only legacy project without canonical exact-note material, M6-R2 proves:

```text
exact_note_editing_available = false
legacy_has_no_fabricated_notes = true
```

The Browser Studio does not reverse-map Music IR or rendered output into invented canonical note state.

## 11. Browser/local-first security boundary / browser·local-first 보안 경계

M6-R2 preserves the existing Browser Studio trust boundary:

- loopback-only service boundary;
- same-origin packaged browser assets;
- no third-party CDN dependency;
- no wildcard CORS authority;
- no upload endpoint added by M6-R2;
- no remote telemetry added by M6-R2;
- existing CSP remains applicable;
- browser route does not receive direct Music IR or filesystem mutation authority.

Canonical UI proof records:

```text
same_origin_assets_only = true
note_preview_route_present = true
piano_roll_style_present = true
precision_global_present = true
```

## 12. Claim boundary / 주장 경계

If the evidence-bearing successor head passes the required gates, M6-R2 supports the bounded claim:

> **MUSICA can expose accepted exact-note material through a local Browser Studio piano-roll / Inspect surface, construct bounded stable-ID exact-note edits, preview them through the trusted M6-R1 authority path, and accept them only through existing M2 project authority.**
>
> **MUSICA는 accepted exact-note material을 local Browser Studio piano-roll / Inspect surface에 노출하고, stable-ID 기반의 제한된 exact-note 편집을 구성하며, trusted M6-R1 권한 경로로 Preview하고, 기존 M2 프로젝트 권한을 통해서만 Accept할 수 있다.**

M6-R2 does **not** validate or imply:

- real-browser pointer gesture acceptance for exact-note editing;
- full DAW piano-roll parity;
- arbitrary polyphonic/every-part exact editing;
- arbitrary tempo-map editing;
- quantize/humanize/advanced batch transforms;
- arbitrary DAW reverse mapping;
- live MIDI recording;
- waveform/destructive audio editing;
- mixer/automation/plugin hosting;
- human-subject usability evidence;
- perceptual, production or mastering superiority.

These remain separately bounded future work.

## 13. Final promotion gate / 최종 승격 gate

The exact successor head containing this document must pass all of:

1. MUSICA CI — Python 3.11/3.12 plus existing Browser Studio and M5-R2 regression jobs;
2. M6-R2 Piano-Roll Evidence;
3. M6-R1 Exact-Note Edit Evidence regression;
4. M5-R3 DAWproject Evidence regression;
5. M5-R4 Paired Audio Evidence regression.

After those exact-head gates pass, the successor M6-R2 artifact must be downloaded and inspected to confirm the strengthened independent source-view proof remains intact. Only then may PR #58 be merged with expected-head protection, Issue #57 be closed, and canonical state advance to:

> **M6-R2 — VALIDATED — BOUNDED BROWSER INTEGRATION**

The next bounded milestone is:

> **M6-R3 — Real-browser exact-note E2E + lock/conflict UX**
