# M6-R3 Validation / M6-R3 검증 기록

**Milestone / 마일스톤:** `M6-R3 — Real-browser Exact-Note E2E + Lock/Conflict UX`

**Governing Issue / 지배 Issue:** `#60`

**Implementation PR / 구현 PR:** `#61`

**Validation class / 검증 분류:** `REAL_BROWSER_EXACT_NOTE_E2E_EVIDENCE`

## 1. Verdict / 판정

M6-R3 has reached an evidence-backed implementation candidate for the bounded real-browser exact-note E2E and visible lock/conflict UX mission.

M6-R3는 제한된 real-browser exact-note E2E 및 가시적 lock/conflict UX 미션에 대해 근거가 결박된 구현 후보 상태에 도달했습니다.

Promotion to final `VALIDATED — BOUNDED REAL-BROWSER EXACT-NOTE E2E` is effective only when the exact successor head containing this durable record passes the same required CI/evidence gates and its successor M6-R3 artifact is independently inspected. Until that rerun succeeds, this file records the validated pre-durable implementation evidence and does not authorize merge by itself.

본 durable record를 포함한 exact successor head가 동일한 필수 CI/evidence gate를 통과하고 successor M6-R3 artifact를 독립 검사한 경우에만 최종 `VALIDATED — BOUNDED REAL-BROWSER EXACT-NOTE E2E` 승격이 유효합니다. 그 전까지 본 문서는 pre-durable 구현 검증 근거를 기록할 뿐 merge 권한 자체를 부여하지 않습니다.

## 2. Canonical starting point / 공식 시작점

- M6-R2 implementation merge: `4fc186168a2c6d6b91ed0d842476f9fed9586ba6`
- M6-R2 state closure/main: `aa435725e62a4cebcdf1247fb311424fdd8cafa5`
- M6-R3 branch: `m6-r3-real-browser-note-e2e`
- Issue `#60`
- PR `#61`
- clean pre-durable implementation/evidence head: `f60731019bb9dae8f8b80189a938c771dadb7f6e`

## 3. Implemented bounded real-browser boundary / 구현된 제한 real-browser 경계

M6-R3 does not introduce a new project authority model. It proves the M6-R2 Browser Studio integration through real Chromium while preserving M6-R1 trusted note authority and existing M2 acceptance authority.

Implemented and exercised:

1. dedicated Playwright Chromium M6-R3 evidence runner;
2. real Browser Studio open/render of canonical exact-note material;
3. browser-visible source binding to exact `project_id / revision_id / Blueprint SHA-256`;
4. real-browser access to all six existing M6 primitive operations: `INSERT / DELETE / MOVE / RESIZE / REPITCH / SET_VELOCITY`;
5. non-canonical `PREVIEW · NOT ACCEPTED` behavior before explicit acceptance;
6. explicit existing Studio/M2 `Accept` and `Discard` reuse;
7. accepted exact-note persistence across service restart and browser reopen;
8. stable-ID HARD-lock proposal path reaching trusted M6-R1 authority and visibly failing closed;
9. stale-source browser proposal visibly failing closed without silent rebase or pending Preview;
10. stable note/rule conflict context exposed where available;
11. legacy motif-only project remains explicit read-only with no fabricated canonical notes;
12. machine-readable browser candidate and authority-result evidence;
13. permanent M6-R3 real-browser CI/evidence workflow;
14. permanent HTTP regression for the Browser Studio Preview-detail read model.

## 4. Authority invariant / 권한 불변식

Validated path:

```text
Accepted exact-note Blueprint
→ deterministic Studio note view
→ real Chromium Browser Studio Inspect piano roll
→ visible browser interaction / exact numeric input
→ typed source-bound NoteEditCandidate
→ M6-R1 source + lock + constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept / Discard
→ existing M2 authority only
→ accepted exact-note Blueprint revision
→ restart/reopen persistence proof
```

Forbidden:

```text
DOM/canvas/browser-local state → canonical project
Music IR mutation → canonical project
blocked result → pending Preview
browser edit gesture → implicit Accept
stale candidate → silent rebase/accept
```

Canonical proof records:

```text
browser_project_mutation_authorized = false
music_ir_mutation_authorized = false
accepted_ref_unchanged_before_accept = true
explicit_accept_advanced_once_to_candidate = true
discard_preserved_accepted_ref = true
```

## 5. Defect discovered by the first real-browser gate / 첫 real-browser gate가 발견한 결함

The first dedicated M6-R3 Chromium run was intentionally treated as a real quality gate rather than having browser console errors ignored.

Initial run:

- workflow run: `34695065569`
- initial implementation head: `ed507c90bb96ebe61e38adad5a6f44efd5d583bf`
- M6-R1/R2 precision regressions: **PASS** (`39 passed`)
- M6-R3 functional browser journey: reached all positive/negative scenarios
- final result: **FAIL** because Chromium reported six HTTP `404` console errors.

A dedicated diagnostic captured the concrete failing request as:

```text
GET /v0/sessions/{session_id}/preview
HTTP 404
resource_type = fetch
```

Root cause:

- Browser Studio `app.js` already called the read-only `GET /v0/sessions/{id}/preview` endpoint to refresh pending Preview detail;
- the HTTP bridge had never implemented that GET route;
- the UI catch path hid the missing route during earlier milestones;
- real-browser console evidence exposed the latent integration defect.

The fix did **not** suppress browser console failures. The missing read model was implemented:

- existing session + pending Preview → `200` with Preview descriptor/diff/detail;
- existing session + no pending Preview → normal `200` empty read state (`pending=false`), which is race-safe across Accept/Discard;
- unknown session → remains fail-closed `404`.

Permanent regression coverage was added in `tests/test_m4_browser_ui.py`, and the M6-R3 workflow permanently runs that Browser HTTP suite together with M6-R1/R2 precision tests.

A post-fix diagnostic recorded:

```json
{
  "console_errors": [],
  "http_errors": []
}
```

The temporary diagnostic harness was then removed before the clean pre-durable head.

## 6. Clean pre-durable exact-head CI / clean pre-durable exact-head CI

Exact head:

`f60731019bb9dae8f8b80189a938c771dadb7f6e`

Required workflows:

| Workflow / 워크플로 | Run | Result |
|---|---:|---|
| MUSICA CI | `34720489913` | **SUCCESS** |
| M6-R3 Real-Browser Exact-Note Evidence | `34720490000` | **SUCCESS** |
| M6-R2 Piano-Roll Evidence | `34720489980` | **SUCCESS** |
| M6-R1 Exact-Note Edit Evidence | `34720489983` | **SUCCESS** |
| M5-R3 DAWproject Evidence | `34720489911` | **SUCCESS** |
| M5-R4 Paired Audio Evidence | `34720489945` | **SUCCESS** |

MUSICA CI exact-head jobs:

- Python 3.11 contracts/runtime: job `103625332032` — **SUCCESS**;
- Python 3.12 contracts/runtime + M0→M5-R1 evidence regeneration: job `103625332007` — **SUCCESS**;
- M4-R3 real Chromium browser E2E: job `103625332003` — **SUCCESS**;
- M5-R2 Windows FluidSynth evidence: job `103625331891` — **SUCCESS**.

Dedicated M6-R3 job:

- job `103625332062` — **SUCCESS**;
- Browser + M6 permanent regressions — **SUCCESS**;
- M6-R3 real-browser exact-note E2E — **SUCCESS**;
- canonical artifact upload — **SUCCESS**.

## 7. Clean pre-durable M6-R3 artifact / clean pre-durable M6-R3 artifact

Canonical evidence run:

- workflow run: `34720490000`
- head: `f60731019bb9dae8f8b80189a938c771dadb7f6e`
- artifact name: `musica-m6-r3-real-browser-note-e2e`
- artifact ID: `10306033112`
- artifact size: `5791493` bytes
- GitHub packaging digest: `sha256:4d6f563b31dd49cb1e73cbe246fb8fb85730a20fbde3ea3a3c0abc9ab807a270`
- independently downloaded ZIP SHA-256: `4d6f563b31dd49cb1e73cbe246fb8fb85730a20fbde3ea3a3c0abc9ab807a270`
- internal `manifest.json` SHA-256: `4bc0d29f64d9d855ce567bdd5d0b897e0e483a093717c393bb813db4167b12b7`
- source Blueprint SHA-256: `8503af57b42b91f7c77330ace3587fe60d255fb19c8d5eba8721627c825f7ed2`
- accepted Blueprint SHA-256: `e8b6418da362b43217d6572a094dda814bbf080ed2fb302c4a947e38f96ae3ba`
- accepted revision: `rev-studio-75a7282ef134c0b31e68a50f`
- ZIP members: `87`
- manifest-declared evidence records: `18`

All 18 files declared by the top-level evidence manifest were independently rehashed after download. Every declared SHA-256 and byte size matched the extracted artifact exactly.

## 8. Six-operation real-browser proof / 6개 연산 real-browser 증명

`operation-outcomes.json` independently records all six primitive operation outcomes:

| Operation | Authority | Resolution |
|---|---|---|
| `MOVE` | `READY_FOR_PREVIEW` | `DISCARD` |
| `RESIZE` | `READY_FOR_PREVIEW` | `DISCARD` |
| `SET_VELOCITY` | `READY_FOR_PREVIEW` | `DISCARD` |
| `DELETE` | `READY_FOR_PREVIEW` | `DISCARD` |
| `INSERT` | `READY_FOR_PREVIEW` | `DISCARD` |
| `REPITCH` | `READY_FOR_PREVIEW` | `ACCEPT` |

The canonical proof records:

```text
real_chromium_used = true
exact_note_project_opened_in_real_browser = true
browser_source_bound_to_project_revision_blueprint_hash = true
all_six_operations_browser_exercised = true
preview_not_accepted_visible = true
accepted_ref_unchanged_before_accept = true
discard_preserved_accepted_ref = true
explicit_accept_advanced_once_to_candidate = true
accepted_repitch_preserved = true
accepted_state_survives_restart_reopen = true
browser_console_error_count = 0
browser_page_error_count = 0
```

## 9. HARD-lock fail-closed proof / HARD-lock fail-closed 증명

The real-browser HARD-lock scenario proposes a pitch change against stable note `N-MOTIF-001` protected by rule `L-M6-R3-PITCH`.

Extracted canonical conflict:

```text
status = BLOCKED
code = HARD_LOCK_VIOLATION
note_id = N-MOTIF-001
rule_id = L-M6-R3-PITCH
reason = HARD exact-note lock L-M6-R3-PITCH protects pitch: 62 -> 65
preview_installed = false
```

The Browser UI visibly exposes the stable note/rule context while the trusted M6-R1 engine remains the blocking authority.

## 10. Stale-source fail-closed proof / stale-source fail-closed 증명

A concurrent accepted revision is created after the Browser has loaded its source-bound note view. The stale Browser proposal is then submitted without silently rebasing its candidate.

Extracted conflict:

```text
status = BLOCKED
code = STALE_SOURCE
reason = revision_id mismatch; blueprint_sha256 mismatch
preview_installed = false
```

The proof also records:

```text
stale_response_rebound_to_current_accepted_source = true
```

This means the rejected stale candidate is not promoted; the read projection is rebound to the actual current accepted source after the conflict.

## 11. Legacy no-fabrication proof / legacy 비조작 증명

For a motif-only project without canonical exact-note material, the real Browser Studio proves:

```text
legacy_reports_exact_editing_unavailable = true
legacy_has_no_fabricated_notes = true
```

MUSICA does not reverse-map Music IR or rendered output into invented accepted exact-note state.

## 12. Browser runtime observations / Browser runtime 관찰

Canonical runtime evidence records:

```text
console_errors = []
page_errors = []
```

The run also records six `audio.wav` requests aborted by Chromium with `net::ERR_ABORTED` while media sources are rapidly replaced during Preview/Accept/Discard state transitions. These are captured as browser request-lifecycle evidence, not HTTP error responses, and they do not represent canonical authority or project-state failures. M6-R3 does not claim zero browser request cancellations.

This bounded observation is retained rather than silently discarded.

## 13. Local-first and security boundary / local-first 및 보안 경계

M6-R3 preserves the previously validated Studio boundary:

- loopback-only HTTP server;
- same-origin packaged browser assets;
- no wildcard CORS authority;
- no upload endpoint introduced;
- no remote telemetry introduced;
- no external provider network required by canonical M6-R3 evidence;
- Browser, DOM and canvas remain non-authoritative;
- Music IR direct mutation remains unauthorized;
- unknown-session Preview-detail read remains fail-closed `404`.

Canonical proof records:

```text
external_provider_network_required = false
browser_project_mutation_authorized = false
music_ir_mutation_authorized = false
```

## 14. Claim boundary / 주장 경계

If the evidence-bearing successor head passes the required gates and its successor artifact is inspected, M6-R3 supports the bounded claim:

> **MUSICA can perform bounded stable-ID exact-note editing through a real Chromium Browser Studio, keep every browser edit non-canonical until explicit existing M2 acceptance, visibly fail closed on HARD-lock and stale-source conflicts, and preserve accepted exact-note state across restart/reopen.**
>
> **MUSICA는 실제 Chromium Browser Studio에서 stable-ID 기반의 제한된 exact-note 편집을 수행하고, 모든 browser 편집을 기존 M2의 명시적 Accept 전까지 비공식 상태로 유지하며, HARD-lock 및 stale-source 충돌을 가시적으로 fail-closed 처리하고, 승인된 exact-note 상태를 재시작·재오픈 후에도 보존할 수 있다.**

M6-R3 does **not** validate or imply:

- full DAW piano-roll parity;
- arbitrary polyphonic/every-instrument-part exact editing;
- arbitrary tempo-map editing;
- general quantize/humanize/batch transformations;
- waveform/destructive audio editing;
- mixer/automation/plugin hosting;
- live MIDI recording;
- arbitrary DAW reverse mapping;
- cloud/collaborative authority;
- human-subject usability evidence;
- perceptual, production or mastering superiority.

## 15. Final promotion gate / 최종 승격 gate

The exact successor head containing this document must pass all of:

1. MUSICA CI — Python 3.11/3.12 plus M4-R3 Chromium and M5-R2 Windows FluidSynth jobs;
2. M6-R3 Real-Browser Exact-Note Evidence;
3. M6-R2 Piano-Roll Evidence regression;
4. M6-R1 Exact-Note Edit Evidence regression;
5. M5-R3 DAWproject Evidence regression;
6. M5-R4 Paired Audio Evidence regression.

The successor M6-R3 artifact must then be independently downloaded and checked for:

- GitHub packaging digest equality;
- top-level manifest hash/size integrity;
- all six Browser operations;
- explicit Accept/Discard authority proof;
- zero Browser console/page errors;
- HARD-lock and stale-source fail-closed proof;
- legacy no-fabrication proof;
- restart/reopen persistence proof.

Only after those checks may PR #61 be merged with expected-head protection, Issue #60 be closed, and canonical state advance to:

> **M6-R3 — VALIDATED — BOUNDED REAL-BROWSER EXACT-NOTE E2E**

The expected next bounded milestone is:

> **M6-R4 — bounded interchange reconciliation for representable exact-note edits**
