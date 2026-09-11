# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M5-R3 IMPLEMENTATION — BOUNDED DAWPROJECT 1.0 ROUND-TRIP v0 / M5-R3 구현 — 제한 DAWproject 1.0 왕복 v0**

M5-R2 remains `VALIDATED — BOUNDED`. M5-R3 selection design has now selected **DAWproject 1.0** as the first bounded project-interchange implementation target, subject to merge of the selection package and subsequent executable proof.

M5-R2는 계속 `VALIDATED — BOUNDED`입니다. M5-R3 선정 설계는 **DAWproject 1.0**을 첫 제한 project-interchange 구현 대상으로 선정했습니다. 단, 이 선정 패키지의 병합과 이후 실행 검증이 필요합니다.

Selection authority / 선정 권위:

- `docs/M5_R3_INTERCHANGE_SELECTION.md`
- `docs/M5_R3_ROUNDTRIP_AUTHORITY.md`
- `docs/M5_R3_ACCEPTANCE.md`
- Issue `#42`

## Do not reopen selection without contradictory evidence / 반대 근거 없이는 선정 재개 금지

The next task is implementation, not another broad survey of DAWs or interchange formats.

다음 작업은 구현이며 DAW/교환 형식에 대한 광범위한 재조사가 아닙니다.

Reopen selection only if implementation evidence triggers one of the explicit `NO_SELECTION`/reopen conditions in `docs/M5_R3_INTERCHANGE_SELECTION.md`.

## Implementation architecture / 구현 아키텍처

```text
Accepted .musica Revision
        ↓
Accepted Blueprint
        ↓ trusted lowering
Canonical Music IR
        ↓ exact source hash
M5-R3 DAWproject Export Adapter
        ↓
.dawproject ZIP
  project.xml
  metadata.xml when used
  bounded files only
        ↓ optional external DAW/tool edit
Imported .dawproject
        ↓
Safe ZIP/XML Parser + XSD Validation
        ↓
Normalized Bounded DAWproject Model
        ↓
NON-CANONICAL Import Candidate
  + provenance
  + structured diff
  + loss report
        ↓
HARD Lock / Constraint Validation
        ↓ explicit user Accept only
M2 Project Engine
        ↓
New Accepted Revision
```

**Imported DAWproject state never directly advances an M2 ref or accepted revision.**

**Import된 DAWproject 상태는 M2 ref 또는 accepted revision을 직접 전진시키지 않습니다.**

## R3-v0 bounded semantic target / R3-v0 제한 의미 목표

Implementation SHALL prove at least:

1. tempo;
2. supported meter;
3. ordered tracks;
4. note pitch;
5. note start;
6. note duration;
7. note velocity;
8. traceable source `track_id` / `part_id` mapping;
9. exact source revision/Music IR and output artifact provenance.

Other semantics begin as `UNSUPPORTED` or `UNKNOWN` unless implementation evidence explicitly promotes them.

다른 의미는 구현 근거로 명시적으로 승격되기 전까지 `UNSUPPORTED` 또는 `UNKNOWN`입니다.

## Required implementation components / 필수 구현 구성요소

Create a fresh implementation branch from the merged M5-R3 selection main and add a bounded package, preferably along these responsibility lines:

```text
musica/interchange/
  __init__.py
  dawproject.py          # public bounded export/import surface
  dawproject_model.py    # normalized internal interchange model
  dawproject_xml.py      # deterministic XML lowering/parsing
  dawproject_zip.py      # deterministic/safe ZIP container handling
  loss.py                # five-state loss taxonomy/report
  candidate.py           # non-canonical import candidate
```

Exact filenames may change if repository structure gives a better fit, but responsibility boundaries SHALL remain inspectable.

### Machine contracts / 기계 계약

Add machine-readable contracts for at least:

- interchange provenance/result;
- import candidate;
- loss report;
- conflict/acceptance status if existing M0/M2 contracts cannot carry the evidence cleanly.

Prefer JSON Schema 2020-12 when a new repository contract is needed, consistent with existing MUSICA contracts.

### DAWproject source/XSD policy / source·XSD 정책

Implementation SHALL pin the exact upstream DAWproject source revision used for evidence.

If upstream XSD files are vendored:

- preserve their license/source notice;
- record source commit/hash;
- keep them under a clearly third-party/spec location;
- do not silently modify the authoritative XSD.

If not vendored, tests SHALL still have a reproducible authoritative validation path without network dependency during normal test execution.

## Deterministic export policy / 결정론 export 정책

MUSICA SHALL own deterministic output for its own exporter. At minimum define and test:

- stable generated XML IDs;
- stable element ordering;
- stable numeric formatting;
- UTF-8 encoding;
- stable ZIP member ordering;
- stable ZIP timestamps/metadata or another normalized ZIP policy;
- exact SHA-256 for `.dawproject` and normalized critical XML;
- repeated identical export equality under the pinned implementation.

Do **not** claim arbitrary external DAWs will serialize byte-identically.

## Tick ↔ beat policy / tick↔beat 정책

Music IR uses integer ticks + PPQ. DAWproject supports musical beat time.

Implementation SHALL define one explicit reversible bounded conversion policy, for example rational/decimal beat values derived from `tick / ppq`, with deterministic formatting and tested inverse comparison.

Do not use uncontrolled binary floating-point string output as authority.

## Velocity policy / velocity 정책

Music IR velocity is integer `1..127`; DAWproject note velocity uses a normalized value.

Implementation SHALL define:

- exact forward conversion;
- canonical numeric serialization;
- inverse/comparison tolerance;
- edge-case tests for minimum, middle and maximum values.

## Loss-report policy / 손실 보고 정책

Use exactly:

```text
PRESERVED
TRANSFORMED
DROPPED
UNSUPPORTED
UNKNOWN
```

Known unsupported Blueprint semantics, locks/constraints-as-interchange-data, proprietary plug-in/device state and any unimplemented automation must be visible in the report, not silently discarded.

## Import-as-candidate policy / candidate import 정책

A valid import SHALL return a non-canonical candidate containing:

- candidate ID;
- source artifact SHA-256;
- DAWproject version;
- source application name/version when present;
- importer version;
- normalized parsed state;
- structured diff against current accepted state;
- loss report;
- lock/constraint validation result;
- acceptance status initially `PENDING`.

Only an explicit Accept action may delegate a commit to M2.

## Security / 보안

Fail closed for at least:

- malformed ZIP;
- malformed XML;
- missing `project.xml`;
- schema-invalid bounded project;
- absolute archive paths;
- `../` traversal or normalized escape;
- duplicate critical entries;
- unsupported DAWproject version;
- artifact/hash tamper where binding applies;
- configured decompression/size-limit violations;
- imported changes conflicting with HARD locks.

No negative case may mutate accepted project state.

## Test fixture / 테스트 fixture

Use one small canonical MUSICA fixture first, preferably the existing deterministic dark-electronic fixture because its Music IR and hashes are already exercised by prior milestones.

The DAWproject fixture SHALL remain small and text-inspectable after unzip. Do not add large audio or proprietary assets.

## External DAW smoke / 실제 DAW smoke

After internal format + semantic round-trip passes, attempt at least one real external-tool/DAW smoke test **only if practical in the available environment**.

If unavailable:

```text
EXTERNAL_APP_SMOKE = NOT VALIDATED
```

Do not infer a MUSICA-tested compatibility result from DAWproject's upstream support list.

## M5-R3 acceptance gate / M5-R3 수용 게이트

`docs/M5_R3_ACCEPTANCE.md` is normative. In summary, M5-R3 cannot close until:

- exact source/spec provenance is pinned;
- deterministic bounded export is proven;
- DAWproject container/XSD validity is proven;
- import remains non-canonical;
- bounded semantic round-trip is proven;
- machine-readable loss report is complete;
- HARD-lock conflict fails closed;
- a valid candidate requires explicit Accept before M2 commit;
- malformed/tampered/traversal cases fail closed;
- exact hashes/provenance are durable;
- repository hygiene is preserved;
- Python 3.11/3.12, prior evidence chain, Chromium and Windows M5-R2 renderer regressions remain green;
- durable evidence exists on the evidence-bearing exact PR head.

## Recommended execution sequence / 권장 실행 순서

```text
selection PR exact-head CI
→ merge selection package
→ create M5-R3 implementation branch from new main
→ pin DAWproject upstream source/XSD
→ implement normalized bounded model
→ deterministic exporter
→ safe parser + XSD validation
→ non-canonical import candidate
→ structured diff + loss report
→ lock/constraint gate + explicit Accept path
→ negative/security tests
→ deterministic round-trip evidence
→ optional external DAW smoke
→ durable M5-R3 evidence
→ evidence-bearing exact-head CI
→ merge
→ close Issue #42
→ state-only closure
```

## Non-goals / 비목표

M5-R3-v0 does not require or claim:

- every DAW;
- every DAWproject entity;
- full mixer/device/plug-in fidelity;
- VST/AU/CLAP hosting;
- perfect arbitrary external-DAW byte reproducibility;
- cloud collaboration;
- perceptual audio-quality superiority;
- replacement of Music Blueprint/Music IR with DAWproject.

## Follow-on / 후속

After M5-R3 closure, the intended next bounded milestone remains **M5-R4 — Comparative Music/Audio Quality Evaluation** unless repository evidence explicitly changes the program order.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
