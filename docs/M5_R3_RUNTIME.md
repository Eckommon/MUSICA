# M5-R3 Runtime Mapping / M5-R3 런타임 매핑

**Status / 상태:** `IMPLEMENTATION BRANCH — VALIDATION PENDING`

This document records the executable bounded mapping used by the M5-R3 DAWproject bridge. It narrows, but does not broaden, the accepted specification in `docs/M5_R3_ACCEPTANCE.md`.

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

## 2. Bounded export mapping / 제한 export 매핑

| MUSICA source | DAWproject 1.0 | State |
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

## 3. Import authority / import 권한

The importer validates ZIP policy, safe XML parsing, DAWproject 1.0 XSD and the bounded profile before building a candidate.

- Import itself does not advance an M2 ref.
- Imported tempo/meter may become Blueprint candidate deltas.
- Existing HARD locks and hard constraints are checked with the normal MUSICA revision validator.
- Imported note edits are inspectable but **cannot be reverse-mapped into Blueprint v0 safely**, because Blueprint v0 owns generative material while note timelines are compiler output.
- Therefore external note edits are `UNSUPPORTED_BLOCKING` for canonical acceptance in M5-R3 v0.
- Track/part mapping that cannot be proven is also blocking.

## 4. Determinism / 결정론

MUSICA v0 emits a deterministic `ZIP_STORED` container with:

- sorted member names;
- fixed ZIP timestamp `1980-01-01 00:00:00`;
- fixed Unix regular-file mode;
- deterministic XML element/attribute construction;
- exact source Blueprint/Music IR and generated artifact hashes in the evidence manifest.

## 5. Security limits / 보안 한계

The bounded importer rejects:

- malformed ZIP/XML;
- DTD/entity declarations;
- missing `project.xml`;
- XSD-invalid project/metadata XML;
- absolute, traversal or backslash archive paths;
- duplicate/case-ambiguous entries;
- unsupported format version;
- excessive entry/member/total archive size;
- excessive compression ratio;
- expected artifact hash mismatch.

## 6. Claim boundary / 주장 경계

M5-R3 v0 does not claim real-DAW compatibility until an actual external application smoke is recorded. It also does not claim arbitrary note-edit reverse mapping, plug-in/device fidelity, arbitrary automation/mixer fidelity, or perfect project interchange.
