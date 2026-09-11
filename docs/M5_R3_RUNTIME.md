# M5-R3 Runtime Mapping / M5-R3 런타임 매핑

**Status / 상태:** `VALIDATED — BOUNDED / 제한 범위 검증 완료`

This document records the executable bounded mapping validated for the M5-R3 DAWproject bridge. It narrows, but does not broaden, `docs/M5_R3_ACCEPTANCE.md`. Durable proof is recorded in `evidence/M5_R3_VALIDATION.md`.

본 문서는 M5-R3 DAWproject bridge에서 실제 검증된 제한 매핑을 기록합니다. `docs/M5_R3_ACCEPTANCE.md`를 확대하지 않으며, 영속 검증 근거는 `evidence/M5_R3_VALIDATION.md`에 있습니다.

## 1. Canonical authority / 공식 권한

`DAWproject` is never canonical MUSICA state.

```text
Accepted Blueprint revision
→ trusted compile
→ canonical Music IR
→ DAWproject export
→ external state
→ safe import
→ NON-CANONICAL candidate
→ diff/loss/conflict validation
→ explicit Accept
→ M2 commit
```

External interchange state can propose changes but cannot directly advance an accepted M2 ref.

외부 interchange 상태는 변경을 제안할 수 있지만 accepted M2 ref를 직접 전진시킬 수 없습니다.

## 2. Validated bounded export mapping / 검증된 제한 export 매핑

| MUSICA source | DAWproject 1.0 | Validated state |
|---|---|---|
| fixed BPM at tick 0 | `Transport/Tempo` | `PRESERVED` |
| fixed Blueprint meter | `Transport/TimeSignature` | `PRESERVED` |
| Music IR track order | `Structure/Track` + `Arrangement/Lanes` order | `PRESERVED` |
| `track_id`, `part_id` | `Track@comment` MUSICA trace token | `PRESERVED` |
| note pitch | `Note@key` | `PRESERVED` |
| note start tick | `Note@time` beats | `TRANSFORMED`, `tick / 480` |
| note duration tick | `Note@duration` beats | `TRANSFORMED`, `duration / 480` |
| note velocity integer | `Note@vel` normalized float | `TRANSFORMED`, bounded round-back |
| Music IR control events | not projected in v0 | `UNSUPPORTED` |
| program/timbre hints | not projected in v0 | `UNSUPPORTED` |
| Blueprint semantic vectors | not DAWproject authority | `UNSUPPORTED` |
| MUSICA locks/constraints | not serialized as external authority | `UNSUPPORTED` |

The loss report uses exactly:

`PRESERVED | TRANSFORMED | DROPPED | UNSUPPORTED | UNKNOWN`.

## 3. Import authority / import 권한

The importer validates ZIP policy, safe XML parsing, DAWproject 1.0 XSD and the bounded profile before building a candidate.

- Import itself does not advance an M2 ref.
- Imported tempo/meter may become Blueprint candidate deltas.
- Existing HARD locks and hard constraints are checked by the normal MUSICA revision validator.
- Imported note edits are inspectable but **cannot be reverse-mapped into Blueprint v0 safely**, because Blueprint v0 owns generative material while exact note timelines are compiler output.
- External note edits are therefore `UNSUPPORTED_BLOCKING` for canonical acceptance in M5-R3 v0.
- Unproven track/part mapping is blocking.
- A stale candidate is blocked if the branch head moved before Accept.

## 4. Determinism / 결정론

MUSICA v0 emits a deterministic `ZIP_STORED` container with:

- sorted member names;
- fixed ZIP timestamp `1980-01-01 00:00:00`;
- fixed Unix regular-file mode;
- deterministic XML element/attribute construction;
- deterministic numeric formatting;
- exact source Blueprint/Music IR and generated artifact hashes.

Validated A/B export SHA-256:

`2575713e0b3345a8a9c3553ace990f60650f9ed73877330193ae2906483e4b0d`

## 5. Security limits / 보안 한계

The bounded importer fails closed for:

- malformed ZIP/XML;
- DTD/entity declarations;
- missing `project.xml`;
- XSD-invalid project/metadata XML;
- absolute, traversal or backslash archive paths;
- duplicate/case-ambiguous entries;
- unsupported format version;
- excessive entry/member/total archive size;
- excessive compression ratio;
- expected artifact hash mismatch;
- stale candidate;
- HARD-lock/constraint conflicts;
- unsupported arbitrary note reverse mapping.

## 6. Validation lineage / 검증 계보

- selection PR `#43`, merge `16d859b4bb5652fb681ba20471927cdb3694b8e9`
- implementation PR `#44`
- evidence-bearing exact head `21b7e7315ff80b994f091a274a19c467eeca4bae`
- final M5-R3 evidence run `34581150840` — **SUCCESS**
- final full MUSICA CI run `34581150808` — **SUCCESS**
- implementation merge `5c874b62b1df0abe0ce58077f7dae0f37303aa5d`
- durable evidence: `evidence/M5_R3_VALIDATION.md`

## 7. Claim boundary / 주장 경계

Validated claim:

> MUSICA has a bounded deterministic DAWproject 1.0 export/import bridge for the explicitly tested semantic subset, with non-canonical candidate import, explicit loss reporting, HARD-lock preservation and explicit M2 acceptance.

Not validated or implied:

- a successful real external DAW smoke test (`EXTERNAL_APP_SMOKE = NOT VALIDATED`);
- compatibility with every DAW or any named DAW through MUSICA execution;
- arbitrary note-edit reverse mapping into Blueprint v0;
- plug-in/device fidelity;
- arbitrary automation/mixer fidelity;
- VST/AU/CLAP hosting;
- perfect project interchange;
- external-DAW byte-exact reproducibility.
