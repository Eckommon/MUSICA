# M7-R0 Validation / M7-R0 검증 기록

**Milestone / 마일스톤:** `M7-R0 — Canonical Automation & Continuous-Control Authority`  
**Governing Issue / 지배 Issue:** `#68`  
**Implementation PR / 구현 PR:** `#69`  
**Validation class / 검증 분류:** `CONTRACT_DESIGN_ONLY`

## 1. Verdict / 판정

M7-R0 has reached an evidence-backed pre-promotion state for a bounded canonical automation and continuous-control authority/data model.

M7-R0는 제한된 canonical automation 및 continuous-control 권한/데이터 모델에 대해 근거가 결박된 pre-promotion 상태에 도달했습니다.

This record validates **contracts and design only**. It does not validate runtime automation editing, accepted Blueprint storage/migration, Browser automation lanes, audible automation rendering, plug-in/renderer parameter mapping, DAW automation reconciliation or real-time control.

Final promotion is authorized only if the exact successor head containing this durable record passes the same required CI/evidence gates and its new M7-R0 artifact is independently inspected. This file does not authorize merge by itself.

## 2. Canonical starting point / 공식 시작점

- canonical main after M6-R4 state closure: `3524e2ca19fe41ff4b50e73eac9d68d310f8369b`
- M6-R4 implementation merge: `66637f7977782ad01e8060d3c4810095c7b44d19`
- M7-R0 Issue: `#68`
- M7-R0 PR: `#69`
- design branch: `m7-r0-automation-authority`
- pre-durable exact head: `3e0a14676916cb5769271ff1151fb34df5fe23ac`

## 3. Ratified authority boundary / 비준 권한 경계

```text
future accepted Blueprint automation material
→ trusted deterministic lowering
→ derived Music IR / renderer automation events

user / AI / future bounded import proposal
→ source-bound AutomationEditCandidate
→ stable lane / point / parameter identity
→ lock + constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ PREVIEW · NOT ACCEPTED
→ explicit Accept only
→ existing M2 revision authority
```

Forbidden:

```text
Music IR control events → fabricated canonical automation
renderer / plug-in state → accepted Blueprint directly
Browser DOM/canvas point → canonical state
AI-generated curve → implicit acceptance
DAW lane order/index → MUSICA stable identity
external automation state → accepted state without separately validated reconciliation
```

R0 intentionally keeps accepted-project storage and mutation outside its claim. The standalone automation contract is the authority design precursor; a later runtime milestone must prove Blueprint integration and backward compatibility.

## 4. Ratified bounded data model / 비준된 제한 데이터 모델

M7-R0 ratifies:

- stable `lane_id`;
- stable `point_id`;
- backend-independent lowercase dotted `parameter_id`;
- canonical scope `project | part` only;
- derived `track_id` excluded from canonical target identity;
- canonical time base `quarter_note_beat`, origin `0.0`;
- explicit units: `normalized | decibel | hertz | semitone | ratio`;
- deterministic bounded interpolation: `hold | linear` only;
- source-bound non-canonical candidates;
- stable-ID-aware automation locks;
- fail-closed authority results.

Primitive edit vocabulary is exactly:

```text
INSERT_POINT
DELETE_POINT
MOVE_POINT
SET_VALUE
SET_INTERPOLATION
```

R0 does not ratify lane creation/deletion, arbitrary parameter reassignment, bulk transforms, quantize/humanize, bezier/spline/exponential interpolation or arbitrary external parameter identities.

## 5. Executable contract boundary / 실행형 계약 경계

`src/musica/automation_contracts.py` is an executable **contract checker only**. It does not mutate Projects, create Preview state, commit revisions, lower Music IR, render audio or access external applications.

It fail-closes on cross-field conditions that are not safely expressed by JSON Schema alone, including:

- duplicate lane IDs;
- non-canonical lane order;
- duplicate target signatures;
- invalid lane bounds (`minimum >= maximum`);
- duplicate point IDs within a lane or across material;
- non-canonical point order;
- duplicate beat positions within a lane;
- point values outside declared lane range;
- lock reference to unknown lane/point;
- parameter selector mismatch;
- invalid lock mode/property combinations;
- invalid exact/range lock values.

## 6. Pre-durable exact-head CI / pre-durable exact-head CI

Exact head:

`3e0a14676916cb5769271ff1151fb34df5fe23ac`

| Workflow / 워크플로 | Run | Result |
|---|---:|---|
| MUSICA CI | `34791354798` | **SUCCESS** |
| M7-R0 Automation Contract Evidence | `34791354793` | **SUCCESS** |
| M6-R4 Interchange Note Reconciliation | `34791354781` | **SUCCESS** |
| M6-R3 Real-Browser Exact-Note Evidence | `34791354775` | **SUCCESS** |
| M6-R2 Piano-Roll Evidence | `34791354806` | **SUCCESS** |
| M6-R1 Exact-Note Edit Evidence | `34791354776` | **SUCCESS** |
| M5-R3 DAWproject Evidence | `34791354811` | **SUCCESS** |
| M5-R4 Paired Audio Evidence | `34791354763` | **SUCCESS** |

MUSICA CI jobs:

- Python 3.11 contracts/runtime: job `103816056835` — **SUCCESS**;
- Python 3.12 contracts/runtime + canonical evidence regeneration: job `103816056793` — **SUCCESS**;
- M4-R3 real Chromium browser E2E: job `103816056760` — **SUCCESS**;
- M5-R2 Windows FluidSynth evidence: job `103816056649` — **SUCCESS**.

The dedicated M7-R0 workflow additionally passed:

```text
M7-R0 contract tests
→ evidence generation A
→ evidence generation B
→ byte-identical recursive diff
→ artifact upload
```

## 7. Pre-durable M7-R0 evidence artifact / pre-durable M7-R0 근거 artifact

- workflow run: `34791354793`
- head: `3e0a14676916cb5769271ff1151fb34df5fe23ac`
- artifact name: `musica-m7-r0-automation-contract-evidence`
- artifact ID: `10328502200`
- GitHub packaging digest: `sha256:396e7b84b20fc8614b833b32800a02fb480118083530f984fcad7e404162adec`
- independently downloaded ZIP SHA-256: `396e7b84b20fc8614b833b32800a02fb480118083530f984fcad7e404162adec`
- internal `manifest.json` SHA-256: `aab674c3953abcbca94d659da4d3627d65a682b4039510f6f6e255e08efee5`
- manifest-bound output record count: `2`
- independent manifest verification: **2/2 SHA-256 + byte-size matches**
- `contract-hashes.json`: **21 source/contract files hash-bound**
- same-head evidence A/B: **byte-identical**

The source hash ledger binds the authority docs, acceptance/decision/scope/traceability/precheck docs, all four M7 schemas, executable checker, evidence generator, contract tests, dedicated workflow and all automation example fixtures.

## 8. Machine proof / 기계 판독 proof

The canonical `proof.json` records:

```text
automation_material_valid = true
edit_candidate_valid = true
automation_lock_valid = true
ready_authority_result_valid = true
blocked_authority_result_valid = true
canonical_scope_enum = [project, part]
derived_track_scope_excluded = true
primitive_vocabulary_exact = true
candidate_preview_only = true
ready_project_mutation_authorized = false
ready_music_ir_mutation_authorized = false
track_scope_fails_closed = true
out_of_range_value_fails_closed = true
duplicate_beat_fixture_fails_closed = true
point_operation_without_point_id_fails_closed = true
direct_project_mutation_authority_fails_closed = true
runtime_automation_editing_claimed = false
blueprint_storage_integration_claimed = false
audible_automation_rendering_claimed = false
external_daw_automation_reconciliation_claimed = false
```

This evidence validates the contract boundary and its fail-closed properties; it does not exercise runtime automation mutation.

## 9. Lock and authority result contracts / 잠금 및 권한 결과 계약

`automation-lock-v0` supports:

```text
HARD | SOFT
exact | range | presence
```

The payload modes are structurally disjoint:

- exact requires `value`;
- range requires `minimum` + `maximum`;
- presence carries neither exact nor range payload.

The executable checker additionally validates stable lane/point references, parameter consistency and selected values/ranges.

`automation-authority-result-v0` permits only:

```text
READY_FOR_PREVIEW
BLOCKED
```

READY requires zero conflicts and allows Preview generation. BLOCKED requires at least one conflict and forbids Preview generation. Both keep:

```text
explicit_accept_required = true
project_mutation_authorized = false
music_ir_mutation_authorized = false
```

## 10. Backward compatibility / 하위 호환성

M7-R0 changes no existing accepted Blueprint schema and performs no migration. Existing M0→M6 projects remain unchanged and no automation is fabricated from semantic curves, Music IR, renderer output or historical interchange artifacts.

This is intentional. Blueprint storage/migration for canonical automation is a separate runtime acceptance problem for a successor milestone.

## 11. Claim boundary / 주장 경계

If the evidence-bearing successor head passes the final promotion gate, M7-R0 supports only this bounded claim:

> **MUSICA has a validated contract/design authority model for explicit continuous automation with stable backend-independent lane/point/parameter identity, source-bound non-canonical edit candidates, deterministic bounded curve semantics, and fail-closed lock/result contracts.**
>
> **MUSICA는 안정적인 backend-independent lane/point/parameter identity, source-bound 비공식 편집 candidate, 결정론적 제한 곡선 의미, fail-closed lock/result 계약을 갖는 명시적 continuous automation의 contract/design 권한 모델을 검증했다.**

Not validated or implied:

- accepted Blueprint automation storage/migration;
- runtime automation edit authority;
- Preview/Accept execution for automation;
- Browser automation lanes;
- audible automation rendering;
- Music IR automation lowering;
- VST/AU/CLAP hosting or parameter mapping;
- DAW automation round-trip/reconciliation;
- arbitrary tempo-map automation;
- real-time MIDI/OSC control;
- human-subject usability/perceptual evidence.

## 12. Final promotion gate / 최종 승격 gate

The exact successor head containing this document must pass all of:

1. MUSICA CI;
2. M7-R0 Automation Contract Evidence;
3. M6-R4 Interchange Note Reconciliation;
4. M6-R3 Real-Browser Exact-Note Evidence;
5. M6-R2 Piano-Roll Evidence;
6. M6-R1 Exact-Note Edit Evidence;
7. M5-R3 DAWproject Evidence;
8. M5-R4 Paired Audio Evidence.

The successor M7-R0 artifact must then be independently downloaded and inspected for packaging digest, manifest hash, complete manifest hash/size binding and equivalent proof semantics. Because this validation record is deliberately outside the source list hashed by the evidence generator, the successor's extracted M7-R0 evidence tree is expected to remain byte-identical to the pre-durable artifact if no contract-bearing file changes.

Only after those checks may PR #69 be merged with expected-head protection, Issue #68 be completed, and canonical state be promoted to `M7-R0 — VALIDATED — CONTRACT/DESIGN ONLY`.

**Repository evidence remains authoritative over conversation/model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
