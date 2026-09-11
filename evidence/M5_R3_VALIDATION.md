# M5-R3 Validation Evidence / M5-R3 검증 근거

**Milestone / 마일스톤:** `M5-R3 — DAW / Interchange Interoperability v0`  
**Evidence status / 근거 상태:** `DURABLE EVIDENCE RECORDED — FINAL EXACT-HEAD PR REVALIDATION REQUIRED`  
**Implementation PR:** `#44`  
**Evidence date:** `2026-09-11`

This document records executable evidence for the bounded DAWproject 1.0 interchange bridge defined by `docs/M5_R3_ACCEPTANCE.md`. Milestone promotion to `VALIDATED — BOUNDED` is authorized only after the PR head containing this document passes the required exact-head CI gates.

본 문서는 `docs/M5_R3_ACCEPTANCE.md`에 정의된 제한 DAWproject 1.0 교환 bridge의 실행 근거를 기록합니다. 이 문서를 포함한 PR exact head가 필수 CI gate를 다시 통과한 뒤에만 `VALIDATED — BOUNDED` 승격이 허용됩니다.

## 1. Selection and implementation lineage / 선정·구현 계보

- governing Issue: `#42`
- selection PR: `#43`
- selection exact head: `ef57f08cd42f3f323b6cc67fefc13b09c08e1b5a`
- selection CI: `34577168697` — SUCCESS
- selection merge: `16d859b4bb5652fb681ba20471927cdb3694b8e9`
- selected target: **DAWproject 1.0 bounded profile**
- implementation branch: `m5-r3-dawproject-roundtrip-v0`
- initial executable implementation head: `d653feadeea9fa3a6205af82a2e4072409fcc8e0`
- implementation PR: `#44`

## 2. Source/spec provenance / 소스·명세 provenance

Pinned DAWproject source:

- upstream repository: `bitwig/dawproject`
- upstream commit: `ee4dcdde75940f30e14e55401a26955a58b8322b`
- format version: `1.0`
- upstream license: `MIT`
- exporter: `musica-dawproject-exporter 0.1.0`
- importer: `musica-dawproject-importer 0.1.0`
- normalization policy: `musica-dawproject-bounded-v0`

Vendored runtime XSD SHA-256 observed by the evidence run:

- `Project.xsd`: `5b33633a3abea83c9cee2e54bf9b555c60ee528dfd56e61c0f3bce448d9d1d4a`
- `MetaData.xsd`: `fb3ba378271770dddbcced8990aba537de3d36ff2d58573523460a699221c99f`

`MetaData.xsd` and `LICENSE` are byte-exact Git snapshots of the pinned upstream revision. The local `Project.xsd` XML/XSD snapshot differs from upstream only by the final EOF LF; this one-byte difference is explicitly recorded in `schemas/vendor/dawproject-1.0/SOURCE.md` and is not represented as byte-exact.

## 3. Initial PR exact-head execution / 초기 PR exact-head 실행

Exact implementation head tested: `d653feadeea9fa3a6205af82a2e4072409fcc8e0`

### Dedicated M5-R3 workflow

- workflow run: `34580738849`
- job: `m5-r3-dawproject-evidence`
- bounded M5-R3 tests: **18 passed**
- evidence generation: **SUCCESS**
- uploaded artifact: `musica-m5-r3-dawproject`
- artifact ID: `10191485092`
- artifact size: `42,508 bytes`
- artifact digest: `sha256:b4b1b456d63c34800fb0fc6b805cc777671a9915bf0e25f643bb237852001632`

### Full MUSICA regression workflow

Workflow run: `34580738896`

- Python 3.11 full contracts/runtime suite: **SUCCESS**
- Python 3.12 full contracts/runtime suite: **SUCCESS**
- M0→M5-R1 canonical evidence generation/upload chain: **SUCCESS**
- M4-R3 real Chromium browser E2E: **SUCCESS**
- M5-R2 real Windows FluidSynth evidence: **SUCCESS**

No required regression gate was weakened for M5-R3.

## 4. Exact source bindings / 정확한 source binding

The evidence run bound the interchange proof to:

- source accepted revision: `rev-001`
- source Blueprint SHA-256: `085d44ac294631e0816b6cb3e58bc5d616b29dec408f867633506e83a2f7222b`
- canonical Music IR SHA-256: `f28fd7f9268f1ff043f90988bb33800d95fce494cd0cc68c4265a6d8e0abc83d`

These identities are independent of the external interchange artifact and remain the MUSICA authority source.

## 5. Deterministic bounded export proof / 결정론적 제한 export 증명

Two independent exporter invocations from the same accepted Blueprint and canonical Music IR produced byte-identical DAWproject artifacts:

- `export-a.dawproject`: `2575713e0b3345a8a9c3553ace990f60650f9ed73877330193ae2906483e4b0d`
- `export-b.dawproject`: `2575713e0b3345a8a9c3553ace990f60650f9ed73877330193ae2906483e4b0d`
- equality: **true**
- normalized `project.xml` SHA-256: `816d7fac3c4789d750de57f6bbf9480867fe0015bca523775216f000419b03e4`
- `metadata.xml` SHA-256: `73dafa6d8db0afc2bb92b9bb257290f5eefa1de8761f040e9992644dbecab9b7`
- accepted branch head unchanged after export: **true**

Deterministic ZIP policy: sorted members, fixed ZIP timestamp, fixed regular-file metadata and deterministic XML/numeric construction.

## 6. Bounded semantic round-trip / 제한 의미 왕복

The unedited exported artifact imported as a **non-canonical PENDING candidate** with validation `PASS`.

Observed normalized proof:

- bounded track count: `3`
- original candidate status: `PENDING`
- original validation: `PASS`
- normalized candidate SHA-256: `4c08b83cdf04ef52f11790eadd42e7fb7df3654411f72b11760fde21c38c55fc`
- structured diff SHA-256: `8981c0e8cf0cec65ab17313695a05329db1f53b41fa2b1f9ca40c9ec08ca21fb`
- loss report SHA-256: `97ec863452d9f847c1ce9ece9d38c93892d60f385c3a87de1eff9f37f5afd8e0`

Bounded semantics proven by tests/evidence:

- fixed tempo;
- supported fixed meter;
- ordered tracks;
- note pitch;
- note start;
- note duration;
- note velocity through explicit normalization/round-back policy;
- traceable MUSICA `track_id` / `part_id` mapping.

The machine-readable loss taxonomy is exactly:

`PRESERVED | TRANSFORMED | DROPPED | UNSUPPORTED | UNKNOWN`.

Known unimplemented semantics are surfaced instead of silently discarded.

## 7. Authority negative proof / 권한 음성 증명

### Tempo edit versus HARD lock

An external DAWproject tempo edit to `130 BPM` produced:

- validation: **BLOCKED**
- existing `L-TEMPO` HARD lock observed as blocking: **true**
- accepted branch head unchanged: **true**

External artifact SHA-256: `f5a77243d2ebc8c1c19f690a304c2d3aa0b7c464245be522e4e0be2631b0983a`.

### Arbitrary note edit

A one-semitone external note edit produced:

- validation: **BLOCKED**
- reverse-mapping rule: `blueprint-v0-note-reverse-mapping`
- reason: Blueprint v0 owns generative musical material while exact note timeline is compiler output; arbitrary external note edits cannot be safely inferred back into canonical Blueprint material.

External artifact SHA-256: `588fc712e7dadbb0073eb58814c78e93b6201243f9f990419d249eb7c0e10752`.

This is intentionally `UNSUPPORTED_BLOCKING`, not silently approximated.

## 8. Explicit valid acceptance proof / 명시적 유효 승인 증명

A bounded external meter change from `4/4` to `3/4` produced a PENDING candidate with validation `PASS`.

- source external artifact SHA-256: `cade96e92cea86824688f09b445bc902f7dabfded9eef0450dc4b18cf6621eeb`
- branch head before explicit Accept remained source revision: **true**
- explicit Accept delegated to M2 only: **true**
- accepted revision: `import-cade96e92cea8682`
- accepted meter: `3/4`
- accepted Blueprint provenance actor: `import`
- head advanced exactly to accepted revision only after Accept: **true**
- resulting project integrity: **PASS**

## 9. Negative/security coverage / 음성·보안 coverage

Executable tests fail closed for at least:

- malformed ZIP;
- malformed XML;
- missing `project.xml`;
- XSD-invalid project XML;
- absolute path;
- `../` traversal;
- backslash archive path;
- duplicate/case-ambiguous critical entries;
- DTD/entity declaration;
- unsupported DAWproject version;
- artifact SHA-256 mismatch;
- stale candidate after branch movement;
- configured member/size-limit violation;
- HARD-lock conflict;
- unsupported external note reverse mapping.

No negative case is authorized to mutate accepted project state.

## 10. Evidence artifact hashes / 근거 artifact hash

Selected generated artifact records:

| Artifact | SHA-256 |
|---|---|
| `accepted-blueprint.json` | `c38e6076b13956ff9cb9c993a67df9cc3dd405d570c4bd1b0d4035aba3e3b997` |
| `accepted-import.json` | `a9a3aeccdc5778e67298cc1c6cd6558966965d41680650157322643ecd560859` |
| `candidate-original.json` | `e2556839674b5645b5903f00542a6ca163de5bb986be42a1e45ee8caddda0c8a` |
| `candidate-tempo-blocked.json` | `6387272c79d49ddca861acd340764b22284e1de7ff2b749af330c4de0f35054c` |
| `candidate-note-blocked.json` | `d58259fd3856571122c16b5847fc0dc5e29c6bd9c76df3da9759071177b64c75` |
| `candidate-meter-ready.json` | `e562320d8899107cc1ff40faa9f25ca074847c95ce24bc432dc29da254dc785d` |
| `export-loss-report.json` | `4f4a1368b6e4d0742668ec1f0b6f5c0923fc1b91817c69d657460f5fdccbfa7d` |
| `export-manifest.json` | `d4e42af4038502965d456f4aba364f6bb9df82e8083bcc55b15be878b9937ebc` |
| `project-integrity.json` | `e297995c61c52035a92f7f9734a558dee99a0a0a80e67551b9cac4a2c6b1b6fa` |

## 11. Conditional external-application gate / 조건부 외부 앱 gate

```text
EXTERNAL_APP_SMOKE = NOT VALIDATED
```

No real external DAW was executed in the available CI environment. Upstream DAW support statements are not represented as MUSICA-tested compatibility.

## 12. Claim boundary / 주장 경계

After the final evidence-bearing PR head passes all required gates, the authorized claim is limited to:

> A bounded DAWproject 1.0 export/import bridge preserves the explicitly tested subset of musical/project semantics, imports external state as a non-canonical candidate, surfaces known losses, preserves HARD-lock authority, and commits supported changes only after explicit user acceptance.

Not validated or implied:

- compatibility with every DAW or any specific real DAW execution;
- perfect DAW project interchange;
- arbitrary external note-edit reverse mapping into Blueprint v0;
- arbitrary plug-in/device fidelity;
- arbitrary mixer/automation fidelity;
- VST/AU/CLAP hosting;
- external-DAW byte-exact reproducibility.

## 13. Final promotion condition / 최종 승격 조건

This evidence file is intentionally committed **before** final promotion. The PR head containing this document must re-run and pass:

1. M5-R3 dedicated evidence workflow;
2. Python 3.11 full suite;
3. Python 3.12 full suite + prior canonical evidence chain;
4. M4-R3 Chromium E2E;
5. M5-R2 Windows FluidSynth evidence.

Only then may the merged repository state promote M5-R3 to `VALIDATED — BOUNDED` and advance `memory/NEXT_ACTION.md` to M5-R4.

**Repository evidence remains authoritative over conversation/model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
