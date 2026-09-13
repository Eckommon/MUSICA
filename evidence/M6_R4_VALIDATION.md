# M6-R4 Validation / M6-R4 검증 기록

**Milestone / 마일스톤:** `M6-R4 — Bounded Interchange Reconciliation for Representable Exact-Note Edits`  
**Governing Issue / 지배 Issue:** `#65`  
**Implementation PR / 구현 PR:** `#66`  
**Validation class / 검증 분류:** `BOUNDED_INTERCHANGE_NOTE_RECONCILIATION_EVIDENCE`

## 1. Verdict / 판정

M6-R4 has reached an evidence-backed pre-durable implementation candidate for bounded reconciliation of representable MUSICA-origin DAWproject exact-note changes into the existing M6 note authority.

M6-R4는 MUSICA-origin DAWproject의 표현 가능한 exact-note 변경을 기존 M6 note authority로 환원하는 제한적 reconciliation에 대해 근거가 결박된 pre-durable 구현 후보 상태에 도달했습니다.

Final promotion is authorized only if the exact successor head containing this durable record passes the same required CI/evidence gates and its new M6-R4 artifact is independently inspected. This file does not authorize merge by itself.

## 2. Canonical starting point / 공식 시작점

- canonical main after M6-R3 state closure: `f0f1e1cc5fdcf1e65208147da3bbb4e67d4fac1f`
- M6-R3 implementation merge: `327939e71bd63611f747bac147c4ba6591052b93`
- M6-R3 state closure merge: `f0f1e1cc5fdcf1e65208147da3bbb4e67d4fac1f`
- M6-R4 branch: `m6-r4-interchange-note-reconciliation`
- strengthened pre-durable implementation/evidence head: `71a86dd5d98ee1d7040ca3dbe8a9b0d74cbdfe32`
- acceptance contract: `docs/M6_R4_ACCEPTANCE.md`

## 3. Implemented bounded authority path / 구현된 제한 권한 경로

```text
Accepted exact-note Blueprint
→ deterministic Music IR
→ deterministic MUSICA DAWproject export
→ source-bound identity map + normalized export baseline
→ returned DAWproject
→ inherited M5-R3 ZIP/XML/XSD-safe parse + normalization
→ exact baseline-versus-returned comparison
→ one uniquely provable M6 primitive note delta only
→ normal note-edit-candidate-v0
→ existing M6-R1 source/lock/constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ non-canonical Preview
→ explicit Accept only
→ existing M2 commit authority
```

Forbidden:

```text
returned artifact alone → MUSICA note identity
DAW note array index/order → stable identity
nearest-note heuristic → identity
ambiguous delta → guessed candidate
external interchange state → accepted Blueprint
Music IR mutation → accepted Blueprint
external artifact → HARD-lock/constraint bypass
```

## 4. Historical M5-R3 boundary preserved / M5-R3 역사적 경계 보존

M5-R3 historical evidence remains unchanged. Its arbitrary external note-edit `UNSUPPORTED_BLOCKING` result was correct for the authority available at that time.

M6-R4 is additive evidence enabled by the canonical exact-note authority validated in M6-R1→R3. It does not retroactively rewrite M5-R3 evidence or broaden its historical claim.

## 5. Source-bound identity design / source-bound identity 설계

DAWproject 1.0 Note elements do not carry MUSICA stable note IDs. M6-R4 v0 therefore does not use DAW note array index/order as identity and does not use nearest-note or edit-distance heuristics.

The identity bundle binds:

- project ID;
- accepted revision ID;
- canonical Blueprint SHA-256;
- exact-timeline SHA-256;
- compiled Music-IR SHA-256;
- deterministic MUSICA export artifact SHA-256;
- normalized export baseline SHA-256;
- reconciliation policy/version;
- stable MUSICA note IDs against unique normalized lowered signatures.

If two source notes lower to an identical normalized signature, M6-R4 v0 fails closed as ambiguous rather than using order as identity.

The current runtime constructs this bundle through a trusted in-memory constructor. No external/persistent identity-bundle loader is exposed in M6-R4 v0; if such a loader is added later, persisted bundle schema/self-rehash validation becomes a required new boundary.

## 6. Reconciliation policy / reconciliation 정책

Policy ID:

`musica-m6-r4-single-primitive-v0`

The returned artifact is compared against the **exact normalized MUSICA export baseline**, not only against a newly compiled current IR.

M6-R4 v0 allows exactly one uniquely provable primitive delta:

```text
MOVE
RESIZE
REPITCH
SET_VELOCITY
DELETE
INSERT
```

For update operations, exactly one normalized musical field of exactly one source note may change. Channel/part changes are not treated as note primitives. DELETE is one identified source note disappearing. INSERT is one new returned note while all source notes remain unchanged; its MUSICA identity is deterministically source/artifact-bound and its part/section/timing is revalidated through the existing exact-note contract.

Multi-note, multi-field, transport+note, ambiguous or unsupported changes fail closed.

## 7. Evidence determinism strengthening / 근거 결정론 강화

An earlier M6-R4 evidence runner produced semantically correct evidence but rewrote modified DAWproject fixtures with wall-clock ZIP member timestamps. Because returned artifact SHA-256 values feed candidate/operation provenance, otherwise identical evidence runs could differ byte-for-byte.

This was treated as an evidence-quality defect rather than ignored.

The strengthened evidence entrypoint now pins rewritten fixture ZIP metadata:

```text
member order = sorted
ZIP timestamp = 1980-01-01 00:00:00
compression = ZIP_STORED
create_system = 3
regular-file mode = 0644
```

The dedicated M6-R4 workflow now generates canonical evidence **twice independently on the same exact head** and requires:

```text
diff -qr artifacts/m6-r4-a artifacts/m6-r4-b
```

The byte-reproducibility step on run `34789857709` completed **SUCCESS**, proving zero file differences between the two generated evidence trees before artifact upload.

This strengthening changes only canonical evidence-fixture serialization. It does not broaden production reconciliation authority or alter historical M5-R3 serialization/evidence.

## 8. Strengthened pre-durable exact-head CI / 강화된 pre-durable exact-head CI

Exact head:

`71a86dd5d98ee1d7040ca3dbe8a9b0d74cbdfe32`

| Workflow / 워크플로 | Run | Result |
|---|---:|---|
| MUSICA CI | `34789857677` | **SUCCESS** |
| M6-R4 Interchange Note Reconciliation | `34789857709` | **SUCCESS** |
| M6-R3 Real-Browser Exact-Note Evidence | `34789857724` | **SUCCESS** |
| M6-R2 Piano-Roll Evidence | `34789857657` | **SUCCESS** |
| M6-R1 Exact-Note Edit Evidence | `34789857772` | **SUCCESS** |
| M5-R3 DAWproject Evidence | `34789857778` | **SUCCESS** |
| M5-R4 Paired Audio Evidence | `34789857659` | **SUCCESS** |

MUSICA CI exact-head jobs:

- Python 3.11 contracts/runtime: job `103811961676` — **SUCCESS**;
- Python 3.12 contracts/runtime + canonical evidence regeneration: job `103811961761` — **SUCCESS**;
- M4-R3 real Chromium browser E2E: job `103811961743` — **SUCCESS**;
- M5-R2 Windows FluidSynth evidence: job `103811961593` — **SUCCESS**.

Dedicated M6-R4 job `103811961581` passed:

1. M5-R3 + M6-R1/R2 + M6-R4 targeted regressions;
2. two independent canonical M6-R4 evidence generations;
3. byte-for-byte evidence-tree reproducibility via `diff -qr`;
4. canonical artifact upload.

## 9. Strengthened pre-durable M6-R4 evidence artifact / 강화된 pre-durable M6-R4 근거 artifact

- workflow run: `34789857709`
- head: `71a86dd5d98ee1d7040ca3dbe8a9b0d74cbdfe32`
- artifact name: `musica-m6-r4-interchange-note-reconciliation`
- artifact ID: `10328395422`
- GitHub packaging digest: `sha256:79729650a4cc23095dff8ff8bc6d70ab3ecbdf93255e211014d7358cedf7caa3`
- independently downloaded ZIP SHA-256: `79729650a4cc23095dff8ff8bc6d70ab3ecbdf93255e211014d7358cedf7caa3`
- internal `manifest.json` SHA-256: `4fd4ae72d9b3a77ab2c5ec4ab973af05d753a7c22aca21c523bd5e9862415d2c`
- manifest-bound file count: `33`
- independent manifest verification: **33/33 SHA-256 + byte-size matches**
- same-head independent evidence generation comparison: **0 file differences**

Source bindings recorded by `proof.json`:

- source revision: `rev-001`
- source Blueprint SHA-256: `b216c8772eb72de42160e0d104430307e9079d08dcc41af7be0e4832e5786aca`
- exact timeline SHA-256: `0d65010d53a57bd4a6589bb408c7c5acb98d2e2faa0143531648392d214ada21`
- source Music-IR SHA-256: `ff7778e6e233a3db87b4dea000ecfacc6bca85ebbbe5e0afe66d47d98395feba`
- source DAWproject export SHA-256: `729e84f4d22ed36c38f61e18918985b0671f87aba9d1df410a7ecf9a531f7501`
- normalized baseline SHA-256: `544f9391ef4d5eacd5ad0ac9bbcdf9b0a504e5e2482425f7af37c2e3d6821c0f`
- identity-map SHA-256: `45c6354a6fde4a064436cbad11e16219fb0c733eef8f9923e64fb626a3a7b86e`

## 10. Six primitive positive proof / 6개 primitive 양성 증명

`proof.json` records:

```text
all_six_primitives_reconciled = true
array_index_used_as_identity = false
heuristic_nearest_note_matching = false
external_state_canonical_authority = false
explicit_accept_required = true
```

Every primitive produced a normal M6 candidate and `READY_FOR_PREVIEW` authority result:

- MOVE;
- RESIZE;
- REPITCH;
- SET_VELOCITY;
- DELETE;
- INSERT.

Every candidate is bound to source project/revision/Blueprint identity, uses one typed M6 operation, has `preview_only=true`, and preserves `project_mutation_authorized=false` / `music_ir_mutation_authorized=false` until explicit acceptance.

## 11. Explicit M2 acceptance proof / 명시적 M2 승인 증명

The evidence separately exercised a reconciled REPITCH through the existing M6 Preview and M2 commit boundary.

Observed:

```text
before_ref = rev-001
after_ref  = rev-001-note-2b0c8563e5a8e6df
accepted_revision_id = rev-001-note-2b0c8563e5a8e6df
ref_advanced_exactly_to_commit = true
accepted_pitch = 64
accepted_pitch_expected = true
project integrity = PASS
revision_count = 2
```

This proves the external artifact itself does not advance accepted state; canonical state advances only after explicit acceptance through the existing M2 engine.

## 12. Negative authority proof / 음성 권한 증명

### HARD stable-note lock

A source-bound external REPITCH was successfully reconciled into a typed candidate, then the existing M6 authority returned:

```text
status = BLOCKED
code = HARD_LOCK_VIOLATION
rule_id = L-M6-R4-EVIDENCE-PITCH
note_id = N-MOTIF-001
preview_generation_allowed = false
project_mutation_authorized = false
music_ir_mutation_authorized = false
```

### Multi-field ambiguity

One returned note changed both time and pitch. Reconciliation failed before candidate construction with:

`external note change is not one uniquely representable M6 primitive`

### Stale source

After source revision identity was changed relative to the export bundle, reconciliation failed before returned-artifact interpretation with:

`stale or tampered M6-R4 identity bundle: source_revision_id mismatch`

### Other automated fail-closed coverage

Targeted tests also cover:

- unchanged artifact as no edit candidate;
- two-note edits;
- transport change combined with note path;
- duplicate lowered exact-note signatures;
- deterministic INSERT identity;
- stable-ID DELETE mapping.

Inherited M5-R3 tests preserve malformed ZIP/XML/XSD/path/archive security failures.

## 13. Claim boundary / 주장 경계

If the evidence-bearing successor head passes the required gates, M6-R4 supports only this bounded claim:

> **MUSICA can reconcile one uniquely provable, representable exact-note change from an exact MUSICA-origin DAWproject export into the existing typed M6 note-edit authority without using DAW note order as identity or granting external interchange state canonical authority.**
>
> **MUSICA는 정확한 MUSICA-origin DAWproject export에서 유일하게 증명 가능한 하나의 표현 가능한 exact-note 변경을 DAW note 순서를 identity로 사용하지 않고, 외부 interchange 상태에 canonical authority를 부여하지 않은 채 기존 typed M6 note-edit authority로 환원할 수 있다.**

Not validated or implied:

- arbitrary DAWproject reverse mapping;
- non-MUSICA-origin project reconciliation;
- any specific real DAW compatibility or execution;
- multi-note/batch edit reconciliation;
- heuristic note matching;
- arbitrary polyphonic/every-part exact editing;
- tempo-map reconciliation;
- automation/mixer/plugin/device round-trip;
- external DAW state as canonical truth;
- externally supplied/persisted identity-bundle loading without an additional schema/self-rehash boundary.

## 14. Final promotion gate / 최종 승격 gate

The exact successor head containing this strengthened durable record must pass all of:

1. MUSICA CI;
2. M6-R4 Interchange Note Reconciliation, including same-head two-run byte-reproducibility proof;
3. M6-R3 Real-Browser Exact-Note Evidence;
4. M6-R2 Piano-Roll Evidence;
5. M6-R1 Exact-Note Edit Evidence;
6. M5-R3 DAWproject Evidence;
7. M5-R4 Paired Audio Evidence.

The successor M6-R4 artifact must then be independently downloaded and inspected. Because the only expected successor change is this durable Markdown record, the extracted successor evidence tree should remain byte-identical to the strengthened pre-durable evidence tree; GitHub's outer artifact packaging ZIP digest may independently vary and is verified separately.

Only after those checks may PR #66 be merged with expected-head protection, Issue #65 be completed, and canonical state be promoted to `M6-R4 — VALIDATED — BOUNDED INTERCHANGE NOTE RECONCILIATION`.

**Repository evidence remains authoritative over conversation/model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
