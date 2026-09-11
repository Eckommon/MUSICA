# M5-R3 Round-Trip Authority & Loss Contract / M5-R3 왕복 권한·손실 계약

**Contract ID / 계약 ID:** `M5R3-AUTH-001`  
**Target / 대상:** `DAWproject 1.0 bounded profile`  
**Status / 상태:** `ACCEPTED_FOR_IMPLEMENTATION — NOT YET VALIDATED` / `구현 대상으로 승인 — 아직 검증 완료 아님`

## 1. Purpose / 목적

This contract defines how MUSICA may exchange project data with an external interchange artifact while preserving MUSICA's canonical authority model.

이 계약은 MUSICA가 외부 interchange artifact와 project data를 교환하면서도 MUSICA의 canonical authority model을 보존하는 방식을 정의합니다.

The governing rule is:

지배 규칙:

> **External project data can propose changes, but it cannot directly become accepted MUSICA state.**
>
> **외부 프로젝트 데이터는 변경을 제안할 수 있지만 MUSICA의 승인 상태가 직접 될 수 없다.**

---

## 2. Authority chain / 권한 체인

```text
Accepted .musica Revision
        ↓
Accepted Music Blueprint
        ↓ trusted lowering
Canonical Music IR
        ↓ exact source hash
M5-R3 Export Adapter
        ↓
DAWproject Artifact
        ↓ optional external DAW/tool modification
Imported DAWproject Artifact
        ↓ exact artifact hash
M5-R3 Import Parser
        ↓
NON-CANONICAL Import Candidate
  + source provenance
  + normalized representation
  + semantic preservation/loss report
  + structured diff
        ↓
M0/M1 HARD Lock + Constraint Validation
        ↓
PREVIEW / REVIEW ONLY
        ↓ explicit user Accept only
M2 Project Engine
        ↓
New Accepted .musica Revision
```

No step before explicit Accept may advance the accepted branch ref or replace the accepted Blueprint revision.

명시적 Accept 이전에는 어떤 단계도 accepted branch ref를 전진시키거나 accepted Blueprint revision을 대체할 수 없습니다.

---

## 3. Authority precedence / 권한 우선순위

For an imported candidate, authority SHALL be:

외부 import candidate에 대한 권한 우선순위:

```text
1. explicit user intent / 명시적 사용자 의도
2. existing HARD locks / 기존 HARD lock
3. hard project constraints / hard project constraint
4. accepted MUSICA project invariants / 승인 MUSICA project invariant
5. accepted Blueprint state / 승인 Blueprint 상태
6. imported mapped values / import된 매핑 값
7. inferred external metadata / 추론된 외부 metadata
8. adapter heuristics / adapter heuristic
```

Imported data cannot override items 1–5 silently.

Import 데이터는 1–5번을 암묵적으로 덮어쓸 수 없습니다.

---

## 4. Export authority / export 권한

Export is a **projection**, not a transfer of authority.

Export는 권한 이전이 아니라 **projection / 투영**입니다.

The exporter SHALL:

- read an exact accepted revision and exact derived Music IR;
- record source revision and hash bindings;
- emit only explicitly mapped semantics;
- classify every relevant source field as preserved/transformed/dropped/unsupported/unknown;
- never mutate accepted project state as a side effect of export;
- never claim that the external artifact can reconstruct unsupported MUSICA semantics.

Exporter는 exact accepted revision과 derived Music IR만 읽고, 명시적으로 매핑된 의미만 내보내며, export의 부수효과로 승인 프로젝트 상태를 변경해서는 안 됩니다.

---

## 5. Import authority / import 권한

Import creates a **candidate**, never an accepted revision.

Import는 항상 **candidate**를 생성하며 accepted revision을 직접 생성하지 않습니다.

A valid import result SHALL minimally contain:

```text
ImportCandidate
- candidate_id
- source_artifact_sha256
- source_format = dawproject
- source_format_version = 1.0
- source_application_name? / UNKNOWN
- source_application_version? / UNKNOWN
- importer_id
- importer_version
- normalized_source_hashes
- mapped_candidate_state
- structured_diff
- loss_report
- lock_constraint_validation
- acceptance_status = PENDING | REJECTED | ACCEPTED
```

`acceptance_status=ACCEPTED` may only be produced by an explicit MUSICA acceptance action that delegates revision creation to M2.

`acceptance_status=ACCEPTED`는 MUSICA의 명시적 승인 action이 M2에 revision 생성을 위임한 경우에만 가능합니다.

---

## 6. Loss taxonomy / 손실 분류

Every mapped or relevant source/target semantic SHALL use exactly one primary classification:

모든 관련 의미는 다음 5개 중 하나의 primary classification을 사용해야 합니다.

### `PRESERVED`

Meaning survives export/import without material semantic change within the bounded contract.

제한 계약 내에서 의미가 실질적으로 변하지 않고 유지됩니다.

Examples / 예:
- MIDI note pitch `60` → DAWproject key `60` → MUSICA note `60`;
- constant 4/4 meter when represented exactly.

### `TRANSFORMED`

Meaning is intentionally represented in another domain or scale with a defined reversible or bounded conversion rule.

정의된 변환 규칙에 따라 다른 domain/scale로 표현됩니다.

Examples / 예:
- IR ticks ↔ DAWproject beat positions using explicit PPQ;
- velocity integer `1..127` ↔ normalized float;
- MUSICA stable track identifiers ↔ generated XML IDs plus mapping manifest.

### `DROPPED`

The implementation intentionally omits data that could theoretically be represented, and the omission is declared.

이론상 표현 가능하지만 현재 구현 범위에서 의도적으로 제외하고 이를 명시합니다.

`DROPPED` MUST include a reason.

### `UNSUPPORTED`

The bounded adapter has no supported mapping for the semantic.

현재 bounded adapter가 해당 의미의 매핑을 지원하지 않습니다.

Examples / 예:
- MUSICA HARD lock encoded as DAWproject project authority;
- proprietary DAW plug-in state in the initial v0 import path.

### `UNKNOWN`

Available evidence is insufficient to determine whether semantics are preserved or how they should map.

근거가 부족해 보존 여부 또는 매핑 방식을 결정할 수 없습니다.

`UNKNOWN` MUST remain unknown until implementation/test evidence promotes it.

---

## 7. Loss-report invariants / 손실 보고 불변식

A loss report SHALL:

- be machine-readable;
- identify semantic path/domain;
- state classification;
- state direction: `EXPORT`, `IMPORT`, or `ROUND_TRIP`;
- include transformation policy when `TRANSFORMED`;
- include reason when `DROPPED`, `UNSUPPORTED`, or `UNKNOWN`;
- distinguish source absence from adapter loss;
- be bound to exact source/output artifact hashes;
- never suppress a known loss merely because the generated artifact is schema-valid.

Loss report는 machine-readable이어야 하며 syntactic validity와 semantic preservation을 혼동해서는 안 됩니다.

---

## 8. Initial bounded preservation set / 초기 제한 보존 집합

M5-R3 implementation SHALL attempt to prove the following bounded set:

| Semantic / 의미 | Export | Import | Round-trip target |
|---|---|---|---|
| tempo event(s) | required | required | preserved/transformed with exact policy |
| meter | required where source exists | required | preserved for supported values |
| track ordering | required | required | preserved |
| note pitch | required | required | preserved |
| note start | required | required | reversible transformed |
| note duration | required | required | reversible transformed |
| note velocity | required | required | bounded transformed |
| source track/part identity | required manifest mapping | required mapping | transformed, traceable |
| project/revision provenance | external evidence binding | import provenance | preserved in MUSICA evidence, not external authority |

The following begin as `UNSUPPORTED` or `UNKNOWN` until evidence says otherwise:

- semantic-control vectors;
- section intent/purpose;
- locks/constraints as interchange-controlled semantics;
- arbitrary MIDI CC automation mapping;
- plug-in state fidelity;
- arbitrary mixer routing;
- audio warp state;
- clip launcher/scenes;
- proprietary DAW metadata.

---

## 9. HARD lock behavior / HARD lock 동작

External edits are lower authority than existing HARD locks.

외부 수정은 기존 HARD lock보다 낮은 권한입니다.

If an imported candidate conflicts with a HARD lock:

```text
candidate mapping succeeds
→ diff detects affected locked target
→ constraint/lock validator returns BLOCKED
→ candidate remains non-canonical
→ explicit conflict record emitted
→ no accepted revision is created
```

The adapter MUST NOT resolve the conflict by silently deleting or weakening the lock.

Adapter는 lock을 삭제·완화하여 충돌을 자동 해소해서는 안 됩니다.

---

## 10. Normalization and reproducibility / 정규화·재현성

M5-R3 SHALL distinguish:

```text
A. canonical MUSICA source identity
B. deterministic MUSICA-export serialization
C. semantic equivalence of imported DAWproject
D. arbitrary external DAW byte serialization
```

Only B is expected to be byte-reproducible under a pinned MUSICA exporter version. D is explicitly **not** assumed byte-exact.

고정된 MUSICA exporter version에서 B만 byte reproducibility를 목표로 합니다. 외부 DAW가 다시 저장한 artifact의 byte identity(D)는 가정하지 않습니다.

The importer SHALL normalize the bounded parsed model before semantic comparison so irrelevant XML ordering/ZIP metadata differences do not masquerade as musical changes where the format permits normalization.

Importer는 bounded parsed model을 semantic comparison 전에 정규화해야 하며, 형식상 의미 없는 XML/ZIP 차이가 음악 변경으로 오인되지 않게 해야 합니다.

---

## 11. ZIP/container security / ZIP·컨테이너 보안

DAWproject is ZIP-based. Import SHALL fail closed on at least:

- absolute paths;
- `..` traversal;
- path normalization escaping the extraction root;
- duplicate critical files with ambiguous authority;
- missing required `project.xml` for the bounded profile;
- malformed XML;
- schema-invalid project XML when schema validation is required;
- external references that violate configured policy;
- unexpectedly huge or decompression-bomb-like content beyond bounded limits.

Initial implementation SHOULD parse from the ZIP without trusting archive extraction paths whenever practical.

초기 구현은 가능하면 archive path를 신뢰한 실제 추출보다 ZIP 내부 stream parsing을 우선합니다.

---

## 12. External application compatibility / 외부 애플리케이션 호환성

Three evidence states are distinct:

```text
FORMAT_VALIDATED
SEMANTIC_ROUNDTRIP_VALIDATED
EXTERNAL_APP_SMOKE_VALIDATED
```

A DAWproject artifact that passes XSD validation is not automatically proven importable by every DAW. A real external application smoke test must identify application name/version, operation, artifact hash and observed result.

XSD를 통과한 artifact가 모든 DAW에서 import 가능하다고 간주해서는 안 됩니다. 실제 외부 앱 smoke test는 앱 이름/버전, 수행 operation, artifact hash, 관측 결과를 기록해야 합니다.

If no real DAW can be executed in CI, the repository SHALL say `EXTERNAL_APP_SMOKE = NOT VALIDATED`, not infer success from upstream support lists.

---

## 13. Acceptance transition / 승인 전이

The only valid transition from imported data to accepted project state is:

```text
IMPORTED
→ PARSED
→ NORMALIZED
→ DIFFED
→ LOSS_CLASSIFIED
→ LOCK_VALIDATED
→ PREVIEWABLE/REVIEWABLE
→ USER_ACCEPTED
→ M2_COMMITTED
```

Invalid transitions include:

```text
IMPORTED → M2_COMMITTED
SCHEMA_VALID → ACCEPTED
EXTERNAL_DAW_SAVED → ACCEPTED
```

---

## 14. Claim boundary / 주장 경계

Acceptance of this contract does **not** validate:

- DAWproject exporter/importer implementation;
- XSD validation code;
- real DAW compatibility;
- perfect project fidelity;
- arbitrary plug-in state round-trip;
- preservation of every Blueprint field;
- semantic equality across all DAWproject producers;
- M5-R3 milestone completion.

Those claims require implementation and executable evidence.

위 주장은 모두 구현과 실행 근거가 필요합니다.

**Repository evidence remains authoritative over conversational memory or model inference. / 레포 근거는 대화·모델 추론보다 우선합니다.**
