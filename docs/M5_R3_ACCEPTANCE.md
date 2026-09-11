# M5-R3 Acceptance Contract / M5-R3 수용 계약

**Milestone / 마일스톤:** `M5-R3 — DAW / Interchange Interoperability v0`  
**Selected target / 선정 대상:** `DAWproject 1.0 bounded profile`  
**Status / 상태:** `ACCEPTED SPECIFICATION — IMPLEMENTATION NOT YET VALIDATED` / `수용 명세 승인 — 구현은 아직 검증되지 않음`

## 1. Acceptance verdict rule / 수용 판정 규칙

M5-R3 may be promoted to `VALIDATED — BOUNDED` only when **all REQUIRED gates** below pass on an evidence-bearing exact PR head.

M5-R3는 아래의 **모든 REQUIRED gate**가 evidence-bearing exact PR head에서 통과해야만 `VALIDATED — BOUNDED`로 승격할 수 있습니다.

A missing or inferred result is not a pass. It is `NOT VALIDATED` or `UNKNOWN`.

누락되거나 추론된 결과는 PASS가 아니며 `NOT VALIDATED` 또는 `UNKNOWN`입니다.

---

## 2. Selected contract / 선정 계약

Implementation SHALL follow:

- `docs/M5_R3_INTERCHANGE_SELECTION.md`
- `docs/M5_R3_ROUNDTRIP_AUTHORITY.md`
- DAWproject 1.0 upstream specification/XSD source pinned by implementation evidence.

Implementation may narrow the bounded mapping if evidence demands it, but SHALL NOT silently broaden claims.

구현은 근거에 따라 bounded mapping을 축소할 수 있으나 주장을 암묵적으로 확대해서는 안 됩니다.

---

## 3. REQUIRED Gate A — source/spec provenance / 소스·명세 provenance

Evidence SHALL record:

- DAWproject format version `1.0`;
- exact upstream repository/source revision used for XSD/reference evidence;
- upstream license identity;
- exporter adapter ID/version;
- importer adapter ID/version;
- normalization policy ID/version.

### Pass condition / 통과 조건

All exact identities are inspectable in durable evidence and no critical source/license field is `UNKNOWN`.

---

## 4. REQUIRED Gate B — deterministic bounded export / 결정론적 제한 export

From one accepted MUSICA revision and exact canonical Music IR, the exporter SHALL generate a `.dawproject` artifact without mutating accepted state.

하나의 accepted MUSICA revision과 exact canonical Music IR로부터 exporter가 accepted state를 변경하지 않고 `.dawproject` artifact를 생성해야 합니다.

### Required proof / 필수 증명

- exact source accepted revision ID;
- exact source Blueprint hash where used;
- exact source Music IR SHA-256;
- generated DAWproject SHA-256;
- bounded normalized XML hashes;
- two independent MUSICA exports under the same pinned implementation/config produce the same normalized/declared deterministic result;
- export does not advance any M2 ref or revision.

### Minimum bounded semantic set / 최소 제한 의미 집합

Export evidence SHALL cover at least:

- tempo;
- supported meter;
- ordered tracks;
- note pitch;
- note start;
- note duration;
- note velocity;
- traceable source track/part identity mapping.

---

## 5. REQUIRED Gate C — format/container validity / 형식·컨테이너 유효성

Generated artifacts SHALL satisfy the selected bounded DAWproject 1.0 structural contract.

### Required proof / 필수 증명

- valid ZIP container;
- required `project.xml` present;
- XML parses safely;
- upstream XSD validation passes for files covered by authoritative schemas;
- no untracked critical file controls MUSICA authority;
- deterministic path/layout policy is documented.

Schema validity alone does not satisfy semantic gates.

Schema validity만으로 semantic gate를 통과한 것으로 간주하지 않습니다.

---

## 6. REQUIRED Gate D — import is non-canonical / import 비공식 상태 보장

Importing a valid `.dawproject` SHALL create a **NON-CANONICAL candidate**.

### Required proof / 필수 증명

Before explicit Accept:

- current accepted revision remains unchanged;
- current branch/head ref remains unchanged;
- current canonical Blueprint remains unchanged;
- imported candidate has its own candidate ID;
- source artifact hash and source application metadata are captured when present;
- acceptance status is `PENDING` or equivalent, never implicitly accepted.

---

## 7. REQUIRED Gate E — semantic round-trip / 의미 왕복

For the bounded fixture set:

```text
MUSICA accepted state
→ DAWproject export
→ DAWproject import
→ normalized candidate
```

SHALL produce an explicit semantic comparison.

### Required comparison / 필수 비교

Each bounded semantic MUST be classified as:

- `PRESERVED`, or
- `TRANSFORMED` with a tested bounded inverse/comparison policy.

Any other source semantic relevant to the fixture MUST appear as `DROPPED`, `UNSUPPORTED`, or `UNKNOWN` rather than disappear silently.

### Required numeric/identity checks / 필수 수치·동일성 검사

- note pitches identical;
- track order identical;
- note timing equivalent under PPQ↔beat conversion policy;
- durations equivalent under the same policy;
- velocity round-trip within explicitly declared bounded tolerance if normalized float conversion is used;
- tempo/meter equivalent within explicit representation rules;
- source track/part mapping remains traceable.

---

## 8. REQUIRED Gate F — loss report / 손실 보고

Every export/import/round-trip evidence bundle SHALL include a machine-readable loss report.

### Pass condition / 통과 조건

- every classification uses the normative five-state taxonomy;
- transformed fields include conversion policy;
- dropped/unsupported/unknown fields include reasons;
- report is hash-bound to exact source and interchange artifact;
- known losses are not hidden by schema-valid status.

---

## 9. REQUIRED Gate G — HARD lock/constraint authority / HARD lock·constraint 권한

At least one imported external change SHALL intentionally conflict with an existing HARD lock or hard constraint.

### Pass condition / 통과 조건

The system SHALL:

- parse and map the external change;
- detect the protected target;
- block acceptance fail-closed;
- emit a structured conflict result;
- preserve the existing accepted revision/ref;
- not weaken/delete the lock automatically.

A second case SHALL demonstrate a valid imported candidate that preserves locks and can proceed to explicit Accept.

---

## 10. REQUIRED Gate H — explicit Accept → M2 commit only / 명시 승인 후 M2 commit

A valid imported candidate may become canonical only through explicit acceptance.

### Pass condition / 통과 조건

```text
candidate PENDING
→ validation PASS
→ explicit Accept action
→ M2 creates new revision
→ branch/ref advances to exactly that accepted revision
```

The new revision SHALL preserve provenance indicating `actor=import` or the canonical equivalent and exact source artifact binding.

---

## 11. REQUIRED Gate I — security and fail-closed negatives / 보안·실패 폐쇄

Automated tests SHALL fail closed for at least:

- malformed ZIP;
- malformed XML;
- missing `project.xml`;
- XSD-invalid bounded project;
- absolute archive path;
- `../` traversal;
- duplicate/ambiguous critical project entries;
- tampered artifact/hash mismatch where hash binding is expected;
- unsupported format version;
- candidate that violates HARD lock;
- extraction/size policy violation for bounded limits.

No negative case may mutate accepted project state.

---

## 12. REQUIRED Gate J — provenance and artifact observability / provenance·artifact 관측성

Durable evidence SHALL include exact hashes for relevant:

- source Blueprint;
- source Music IR;
- generated `.dawproject`;
- normalized `project.xml`;
- metadata XML if used;
- imported external artifact;
- candidate normalized representation;
- diff;
- loss report.

Adapter/spec versions and source revision SHALL also be recorded.

---

## 13. REQUIRED Gate K — repository hygiene / 레포 위생

Normal Git SHALL NOT contain:

- installed DAW binaries;
- large proprietary project/media assets;
- commercial sample libraries;
- redistributability-unclear plug-in states;
- large arbitrary audio stems.

Tiny fixtures required for tests are permitted when source/license is explicit.

---

## 14. REQUIRED Gate L — regressions / 회귀

Evidence-bearing exact PR head SHALL keep green at least:

- full Python 3.11 test suite;
- full Python 3.12 test suite;
- M0→M5-R2 applicable evidence/regression chain;
- M4-R3 real Chromium browser E2E;
- M5-R2 Windows real FluidSynth evidence unless CI architecture is explicitly revised with equivalent or stronger evidence.

Regression weakening requires a separate explicit repository decision; it cannot be hidden inside M5-R3.

---

## 15. CONDITIONAL Gate M — real external DAW/tool smoke / 실제 외부 DAW·도구 smoke

A real external application smoke test is **strongly preferred but conditional on practical/test-environment availability**.

If executed, durable evidence SHALL record:

- application name and exact version;
- operation (`IMPORT`, `OPEN`, `EXPORT`, or bounded round-trip);
- exact artifact hashes;
- observed success/failure;
- any warnings or losses;
- whether the application modified serialization while preserving bounded semantics.

If not executed:

```text
EXTERNAL_APP_SMOKE = NOT VALIDATED
```

The milestone may still be `VALIDATED — BOUNDED` for MUSICA's format/semantic round-trip contract, but repository claims MUST NOT state real-DAW compatibility as tested.

실제 DAW 실행이 없으면 format/semantic bounded validation은 가능하지만 실제 DAW 호환성을 테스트했다고 주장할 수 없습니다.

---

## 16. Non-acceptance conditions / 수용 불가 조건

M5-R3 SHALL NOT be promoted if any of the following is true:

- imported file directly mutates accepted state;
- semantic loss occurs silently;
- schema validity is used as a substitute for semantic preservation proof;
- HARD locks can be bypassed by import;
- deterministic/normalized export evidence is absent;
- critical provenance/hash binding is missing;
- path/archive handling is fail-open;
- unsupported DAWproject version is accepted without an explicit compatibility policy;
- selection/source/license evidence is materially contradicted and not reconciled;
- required regression gates fail.

---

## 17. Claim boundary after successful M5-R3 / 성공 후 주장 경계

Even after all REQUIRED gates pass, MUSICA may claim only:

> A bounded DAWproject 1.0 export/import bridge preserves the explicitly tested subset of musical/project semantics, imports external state as a non-canonical candidate, surfaces known losses, preserves HARD-lock authority, and commits changes only after explicit user acceptance.

성공 이후에도 MUSICA는 **명시적으로 테스트한 제한 의미 집합에 대한 DAWproject 1.0 왕복 bridge**만 주장할 수 있습니다.

It SHALL NOT imply:

- perfect DAW project interchange;
- compatibility with every DAW;
- arbitrary plug-in/device fidelity;
- arbitrary automation/mixer fidelity;
- external DAW byte-exact reproducibility;
- VST/AU/CLAP hosting;
- professional workflow validation beyond tested evidence.

**Repository evidence remains authoritative over conversational memory or model inference. / 레포 근거는 대화·모델 추론보다 우선합니다.**
