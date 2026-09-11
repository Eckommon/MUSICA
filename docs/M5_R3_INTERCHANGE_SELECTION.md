# M5-R3 Interchange Selection / M5-R3 교환 형식 선정

**Decision ID / 결정 ID:** `M5R3-SEL-001`  
**Evidence date / 근거 기준일:** 2026-09-11  
**Status / 상태:** `ACCEPTED_FOR_IMPLEMENTATION — NOT YET VALIDATED` / `구현 대상으로 승인 — 아직 검증 완료 아님`

## 1. Decision / 결정

MUSICA SHALL implement **DAWproject 1.0** as the first bounded DAW/project interchange target behind a MUSICA-owned interchange boundary.

MUSICA는 MUSICA가 소유하는 interchange boundary 뒤의 첫 제한 DAW/project 교환 대상으로 **DAWproject 1.0**을 채택합니다.

This decision selects an **implementation target**, not a claim of complete DAW fidelity or real external-application compatibility. Real DAW import/export execution remains `NOT VALIDATED` until separately evidenced.

이 결정은 **구현 대상**을 선정하는 것이며 완전한 DAW fidelity 또는 실제 외부 애플리케이션 호환성을 선언하지 않습니다. 실제 DAW import/export 실행은 별도 근거 확보 전까지 `NOT VALIDATED`입니다.

DAWproject is **replaceable infrastructure**. It does not replace Music Blueprint, Music IR, `.musica`, M2 Project Engine authority, HARD locks, or explicit user Accept.

DAWproject는 **교체 가능한 infrastructure**입니다. Music Blueprint, Music IR, `.musica`, M2 Project Engine 권한, HARD lock, 명시적 사용자 Accept를 대체하지 않습니다.

---

## 2. Selection gate / 선정 게이트

Candidates were scored 1–5 against the twelve criteria defined by `memory/NEXT_ACTION.md`.

후보는 `memory/NEXT_ACTION.md`의 12개 기준에 대해 1–5점으로 평가했습니다.

```text
weighted score = Σ(weight × candidate_score / 5)
maximum = 100
selection threshold = 85
```

For the **first project interchange target**, a candidate also fails selection regardless of total score if any of these is true:

첫 **project interchange target**은 총점과 무관하게 다음 조건 중 하나라도 해당하면 선정하지 않습니다.

- production-semantic coverage score `< 3`;
- accepted MUSICA state must be replaced directly by imported external state;
- no inspectable open specification or stable machine-readable representation is available;
- deterministic/normalizable artifact hashing is not practical;
- the tested use has an unresolved specification/library licensing blocker.

### Weights / 가중치

| Criterion / 기준 | Weight |
|---|---:|
| Musical semantic coverage / 음악 의미 보존 | 15 |
| Production semantic coverage / 제작 의미 보존 | 12 |
| Round-trip inspectability / 왕복 검사 가능성 | 12 |
| Authority fit / 권한 적합성 | 10 |
| Open specification / 공개 명세 | 10 |
| Cross-DAW reach / DAW 범용성 | 10 |
| Deterministic/normalizable serialization / 결정론·정규화 직렬화 | 8 |
| Automation/tooling surface / 자동화·도구 표면 | 8 |
| Licensing / 라이선스 | 5 |
| Windows practicality / Windows 실용성 | 4 |
| Repository hygiene / 레포 위생 | 3 |
| Future extensibility / 향후 확장성 | 3 |
| **Total** | **100** |

---

## 3. Candidate matrix / 후보 비교표

| Candidate / 후보 | Musical | Production | Round-trip | Authority | Open spec | Reach | Serialize | Tooling | License | Windows | Hygiene | Extend | Weighted /100 | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **DAWproject 1.0** | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 4 | 5 | 5 | **97.2** | **SELECT** |
| MusicXML 4.0 | 5 | 1 | 4 | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 3 | **85.8** | HOLD — production blocker |
| Standard MIDI File | 4 | 1 | 4 | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 3 | **82.8** | HOLD |
| AAF | 2 | 5 | 3 | 5 | 5 | 4 | 3 | 3 | 4 | 4 | 3 | 4 | **74.2** | HOLD |

Scores measure suitability for MUSICA's **first bounded project-interchange bridge**, not general standard quality or industry importance.

점수는 각 표준의 일반적 우수성이 아니라 MUSICA의 **첫 제한 project-interchange bridge 적합성**을 평가합니다.

---

## 4. Why DAWproject 1.0 clears the gate / DAWproject 1.0 선정 이유

### 4.1 Purpose fit / 목적 적합성

The upstream project explicitly defines DAWproject as a **vendor-agnostic exchange format between DAWs** and states that its goal is to transfer project/song user data across music applications.

Upstream 프로젝트는 DAWproject를 **DAW 간 vendor-agnostic 교환 형식**으로 명시하며 음악 애플리케이션 간 project/song user data 전송을 목표로 합니다.

Its published comparison identifies:

- music production as the intended use;
- combined beats/seconds time representation;
- audio clips/events/fades/warping;
- notes and note expressions;
- tempo, time-signature, mixer and plug-in automation;
- plug-in state;
- track/channel structure and clip/scenes.

### 4.2 Stable, inspectable container / 안정적·검사 가능한 컨테이너

Upstream documentation declares DAWproject **version 1.0 stable**. The format is a `.dawproject` ZIP containing UTF-8 XML including `project.xml` and `metadata.xml`, with published XSDs.

Upstream 문서는 DAWproject **1.0을 stable**로 선언합니다. 형식은 `project.xml`, `metadata.xml` 등 UTF-8 XML을 담는 `.dawproject` ZIP이며 공개 XSD를 제공합니다.

This supports MUSICA's requirements for:

- schema validation;
- deterministic normalization policy;
- exact SHA-256 artifact binding;
- structured import rather than opaque binary overwrite;
- small text fixtures in Git.

### 4.3 Entity fit / 엔티티 적합성

The published `Project.xsd` includes first-class entities for `Project`, `Transport`, `Arrangement`, `Track`, `Channel`, `Note`, `Notes`, `Clip`, `Audio`, `Points`, tempo/time-signature parameters, devices, VST2/VST3/CLAP/AU plug-ins, built-in EQ/compressor/gate/limiter and references.

공개 `Project.xsd`에는 `Project`, `Transport`, `Arrangement`, `Track`, `Channel`, `Note`, `Notes`, `Clip`, `Audio`, `Points`, tempo/time-signature parameter, device, VST2/VST3/CLAP/AU plug-in, built-in EQ/compressor/gate/limiter, reference 등이 일급 엔티티로 존재합니다.

This is materially closer to MUSICA's planned professional project-interchange boundary than note-only or notation-only interchange.

### 4.4 Current cross-DAW evidence / 현재 cross-DAW 근거

The upstream README currently lists DAWproject 1.0 support for multiple applications including Bitwig Studio, PreSonus Studio One, Steinberg Cubase, Steinberg Cubasis, Steinberg VST Live and n-Track Studio. This is **published support evidence**, not MUSICA-tested compatibility.

Upstream README는 현재 Bitwig Studio, PreSonus Studio One, Steinberg Cubase, Steinberg Cubasis, Steinberg VST Live, n-Track Studio 등 여러 애플리케이션의 DAWproject 1.0 지원을 기재합니다. 이는 **공개 지원 근거**이며 MUSICA가 직접 검증한 호환성은 아닙니다.

### 4.5 Licensing / 라이선스

The upstream `bitwig/dawproject` repository is published under the **MIT License**. MUSICA SHALL still record the exact schema/spec source revision used by implementation evidence.

Upstream `bitwig/dawproject` 저장소는 **MIT License**로 공개되어 있습니다. 구현 근거에서는 사용한 schema/spec source revision을 별도로 고정해야 합니다.

---

## 5. Why the other candidates remain complements / 다른 후보를 보완재로 유지하는 이유

### 5.1 Standard MIDI File — HOLD / 보류

The MIDI Association defines SMF as a way to interchange **time-stamped MIDI data** between programs. It supports one or more streams, event time, tracks/sequences, tempo, time signature and descriptive metadata.

MIDI Association은 SMF를 프로그램 간 **time-stamped MIDI data** 교환 형식으로 정의합니다. stream, event time, track/sequence, tempo, time signature, 기술 메타데이터를 지원합니다.

For MUSICA this remains valuable as:

- a stable low-level note/event interchange target;
- a renderer-input and compatibility baseline;
- a possible side export.

But it does not natively provide the rich audio-clip/project/mixer/device structure required for the first project bridge. Therefore it remains **COMPLEMENTARY**, not the M5-R3 primary target.

### 5.2 MusicXML 4.0 — HOLD / 보류

The W3C Music Notation Community Group defines MusicXML 4.0 as an open format for **digital sheet music exchange and archival**, with professional notation semantics and XSD-based validation.

W3C Music Notation Community Group는 MusicXML 4.0을 **digital sheet music 교환·보관**을 위한 공개 형식으로 정의하며 전문 notation 의미와 XSD 검증을 제공합니다.

It is an excellent future notation adapter candidate, but it fails M5-R3's critical production-semantic gate because mixer/audio-clip/device/project-production state is outside its primary purpose.

따라서 향후 notation adapter로는 강력하지만 mixer/audio clip/device/project-production state가 핵심 목적이 아니므로 M5-R3의 production-semantic 필수 gate를 통과하지 못합니다.

### 5.3 AAF — HOLD / 보류

AAF is an open, cross-platform multimedia authoring interchange model with rich essence/compositional metadata and strong audio/video post-production use.

AAF는 풍부한 essence/compositional metadata를 가진 공개 cross-platform multimedia authoring interchange model이며 audio/video post-production에 강합니다.

However, for MUSICA's first bridge it is a poorer fit than DAWproject because its center of gravity is multimedia/post-production rather than musical-time composition and note-level DAW project exchange. Its structured binary/container ecosystem also makes a minimal deterministic Python implementation heavier.

MUSICA 첫 bridge 관점에서는 중심이 musical-time composition과 note-level DAW project 교환보다 multimedia/post-production에 있고, structured binary/container 생태계 때문에 최소 Python 구현 부담도 더 큽니다.

---

## 6. Selected bounded R3 profile / 선정된 제한 R3 프로파일

The first implementation SHALL target only a **bounded DAWproject 1.0 subset**.

첫 구현은 **제한된 DAWproject 1.0 subset**만 대상으로 합니다.

### Required v0 export preservation / v0 export 필수 보존

- project/application identity sufficient for provenance;
- constant or event-based tempo representable from canonical Music IR;
- 4/4 or other currently representable meter where available from Blueprint context;
- track ordering and stable generated IDs;
- track names/part IDs through an explicit mapping policy;
- note start, duration, pitch and velocity;
- MIDI-channel/program information where a standards-compliant DAWproject representation exists, otherwise explicit `TRANSFORMED`/`UNSUPPORTED` reporting;
- deterministic ZIP/XML normalization owned by MUSICA;
- exact source Music IR and output artifact SHA-256.

### Explicitly not promised in v0 / v0에서 보장하지 않음

- proprietary DAW device state;
- third-party plug-in state fidelity;
- audio warp algorithms;
- clip-launcher semantics;
- arbitrary DAW automation;
- full mixer topology;
- every Music Blueprint semantic axis;
- Blueprint HARD lock encoding inside DAWproject;
- perfect round-trip identity after arbitrary external DAW edits.

Unsupported MUSICA semantics MUST be surfaced in a loss report rather than silently omitted.

지원하지 않는 MUSICA 의미는 조용히 삭제하지 말고 loss report에 반드시 표면화해야 합니다.

---

## 7. Source-to-target mapping seed / 초기 매핑

| MUSICA source | DAWproject target | v0 status |
|---|---|---|
| Music IR `tempo_events` | `Transport/Tempo` and/or `Arrangement/TempoAutomation` | `PRESERVED` or `TRANSFORMED`, exact policy to implement |
| Blueprint `musical_context.meter` | `Transport/TimeSignature` | `PRESERVED` for bounded supported meters |
| Music IR `tracks[]` | `Structure/Track` + `Channel`; arrangement lanes | `PRESERVED` structurally |
| `track_id` / `part_id` | generated DAWproject IDs + name/comment mapping manifest | `TRANSFORMED` |
| note `tick` | beat-time derived from IR `ppq` | `TRANSFORMED` with reversible bounded mapping |
| note `duration` | `Note@duration` | `TRANSFORMED` with reversible bounded mapping |
| note `note` | `Note@key` | `PRESERVED` |
| note `velocity` | `Note@vel` normalized value | `TRANSFORMED` with bounded inverse policy |
| control events | `Points`/parameter or MIDI-message-compatible representation | `UNKNOWN` until implementation mapping proof |
| Blueprint semantics | no primary DAWproject authority mapping | `UNSUPPORTED` in R3-v0 unless explicitly added |
| Blueprint locks/constraints | remain MUSICA-only authority | `UNSUPPORTED` for interchange encoding; always enforced on import |
| revision/provenance | MUSICA evidence manifest + input/output hashes | `PRESERVED` outside external authority |

`UNKNOWN` entries MUST NOT be silently upgraded during implementation. A code/test/evidence change is required before promotion.

`UNKNOWN` 항목은 구현 중 근거 없이 상향할 수 없습니다. 승격에는 코드·테스트·근거 변경이 필요합니다.

---

## 8. Normalization and evidence policy / 정규화·근거 정책

MUSICA SHALL own a deterministic serialization profile rather than assume that arbitrary DAW-generated ZIP/XML bytes are byte-identical.

MUSICA는 임의 DAW가 생성한 ZIP/XML byte가 동일하다고 가정하지 않고 자체 deterministic serialization profile을 소유합니다.

Implementation SHALL distinguish:

```text
semantic equivalence
≠ normalized MUSICA serialization equality
≠ arbitrary external-DAW byte equality
```

At minimum record:

- DAWproject spec version;
- exporter/importer adapter ID + version;
- source accepted revision ID;
- source Blueprint/Music IR hashes as applicable;
- generated `.dawproject` SHA-256;
- normalized `project.xml` / metadata hashes;
- imported artifact SHA-256;
- source application metadata from imported project when present;
- loss report;
- structured candidate diff;
- acceptance actor/action if a candidate is committed.

---

## 9. Repository hygiene / 레포 위생

Allowed in normal Git:

- XSD snapshots only when license/source revision is recorded and inclusion is necessary;
- tiny generated `.dawproject` fixtures;
- tiny XML/JSON fixtures;
- manifests, hashes, mappings, loss reports and tests.

Not allowed in normal Git:

- large DAW project media;
- commercial sample libraries;
- proprietary plug-in state binaries when redistribution is unclear;
- large audio stems solely for interoperability tests;
- installed DAW binaries.

Large or proprietary assets SHALL be externally provisioned and hash-bound, consistent with the M5-R2 content-provenance pattern.

---

## 10. Reopen / NO_SELECTION conditions / 재선정 조건

Selection SHALL be reopened or changed to `NO_SELECTION` if implementation discovers any of the following:

- published DAWproject 1.0 XSD cannot represent the bounded required note/timing/project subset without non-standard mutation;
- deterministic/normalized generation cannot be made inspectable and hashable;
- safe ZIP/path validation cannot fail closed;
- import cannot remain non-canonical until explicit user Accept;
- critical bounded semantics cannot round-trip without silent loss;
- specification/license/source provenance becomes unresolved;
- external application evidence contradicts the selected mapping in a way that breaks the bounded contract.

---

## 11. Next exact action / 다음 정확한 작업

After this selection package is merged:

```text
create M5-R3 implementation branch from selection-merge main
→ implement DAWproject 1.0 bounded exporter
→ deterministic ZIP/XML normalization + hash manifest
→ schema/structural validation
→ bounded importer to NON-CANONICAL candidate
→ loss report + structured diff
→ HARD lock/constraint validation
→ explicit Accept → M2 revision only
→ malformed/tampered/traversal negative tests
→ round-trip fixture tests
→ real external DAW/tool smoke test if practical
→ durable evidence
→ evidence-bearing exact-head CI
→ merge
→ state-only closure
```

No full-DAW-fidelity or real-DAW compatibility claim is authorized by this selection document.

이 선정 문서는 full-DAW-fidelity 또는 실제 DAW 호환성 주장을 승인하지 않습니다.

---

## 12. Evidence sources / 근거 출처

Primary sources consulted on 2026-09-11:

### DAWproject
- https://github.com/bitwig/dawproject
- https://github.com/bitwig/dawproject/blob/main/README.md
- https://github.com/bitwig/dawproject/blob/main/Project.xsd
- https://github.com/bitwig/dawproject/blob/main/MetaData.xsd
- https://github.com/bitwig/dawproject/blob/main/LICENSE

### Standard MIDI File
- https://midi.org/standard-midi-files
- https://midi.org/standard-midi-files-specification
- https://midi.org/specs

### MusicXML 4.0
- https://www.w3.org/2021/06/musicxml40/
- https://www.w3.org/2021/06/musicxml40/listings/musicxml.xsd/
- https://www.w3.org/2021/06/musicxml40/version-history/40/

### AAF
- https://aafassociation.org/specs/object_spec.html
- https://aafassociation.org/downloads.html

**Repository evidence remains authoritative over conversational memory or model inference. / 레포 근거는 대화·모델 추론보다 우선합니다.**
