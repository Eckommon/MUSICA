# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M5-R3 — DAW / INTERCHANGE INTEROPERABILITY v0 / M5-R3 — DAW·교환 상호운용성 v0**

M5-R2 is validated within its bounded claim after real Windows FluidSynth 2.6.0 + externally provisioned FluidR3_GM 3.1 evidence. MUSICA now has a renderer-neutral execution boundary and two renderer paths, but it still lacks a validated project/interchange bridge to external professional music-production tools.

M5-R2는 실제 Windows FluidSynth 2.6.0 + 외부 provision FluidR3_GM 3.1 근거를 통해 제한 범위에서 검증되었습니다. MUSICA는 renderer-neutral 실행 경계와 두 renderer 경로를 갖췄지만 외부 전문 음악 제작 도구와 연결하는 검증된 project/interchange bridge는 아직 없습니다.

## First action is interchange selection, not DAW coupling / 첫 작업은 교환 형식 선정이며 DAW 직접 결합이 아님

M5-R3 SHALL NOT pre-commit MUSICA Core to Ableton Live, REAPER, Cubase, Studio One, Bitwig, Logic, Pro Tools, or another specific DAW merely because an application-specific file/API is convenient.

M5-R3는 특정 DAW의 파일/API가 편리하다는 이유만으로 MUSICA Core를 Ableton Live, REAPER, Cubase, Studio One, Bitwig, Logic, Pro Tools 등에 사전 결합하지 않습니다.

The first R3 deliverable is an evidence-backed interchange-target selection and a round-trip authority contract.

첫 R3 산출물은 **근거 기반 interchange target 선정 + round-trip 권한 계약**입니다.

## Current candidate landscape / 현재 후보 지형

The following are **PROPOSED candidates, not accepted dependencies**:

1. **DAWproject 1.0** — leading project-interchange candidate because its published purpose is open DAW-to-DAW user-data exchange and its schema can represent musical time, tracks/channels, notes, audio, automation and plug-in state. Current upstream documentation lists support across multiple DAWs. It must still be validated against MUSICA's exact bounded round-trip needs.
2. **Standard MIDI File (SMF)** — established sequencing interchange and already close to MUSICA's note/event lowering, but insufficient by itself for rich project/audio/automation interchange.
3. **MusicXML 4.0** — open digital sheet-music interchange with broad notation semantics, useful as a possible notation-focused complementary target rather than an assumed DAW-project format.
4. **AAF** — rich cross-platform multimedia/post-production interchange, but its center of gravity is audio/video authoring rather than musical-time composition; evaluate as a contrast or later audio-post bridge rather than assume it is the first music-production target.
5. **Application-specific adapters** such as REAPER project/ReaScript or another DAW API/file format — may be useful later, but only behind a generic interchange boundary and only if a concrete gap cannot be solved cleanly by the selected open format.

위 후보는 현재 조사 대상일 뿐 승인 dependency가 아닙니다. 특히 **DAWproject가 선두 후보라는 사실과 M5-R3의 공식 선정은 동일하지 않습니다.**

## Selection criteria / 선정 기준

Candidate interchange targets SHALL be compared on at least:

1. **Musical semantic coverage / 음악 의미 보존** — tempo, meter, musical time, tracks, notes/events, velocity/expression and section/timeline semantics as applicable.
2. **Production semantic coverage / 제작 의미 보존** — audio clips, automation, mixer/channel information, devices/plugins or clearly declared unsupported areas.
3. **Round-trip inspectability / 왕복 검사 가능성** — export → external/editable representation → import can be parsed into a structured candidate and diff rather than opaque overwrite.
4. **Authority fit / 권한 적합성** — imported external data cannot directly mutate accepted `.musica`; it must enter as candidate state subject to lock/constraint validation and explicit Accept.
5. **Open specification / 공개 명세** — stable, inspectable specification/schema preferred over proprietary reverse engineering.
6. **Cross-DAW reach / DAW 범용성** — multiple actively supported applications preferred to one-vendor lock-in.
7. **Deterministic serialization / 결정론 직렬화** — canonical or normalizable representation suitable for hashing, diffing and evidence.
8. **Automation/tooling surface / 자동화·도구 표면** — feasible Python/native parsing and generation without GUI automation as the only interface.
9. **Licensing / 라이선스** — specification/library use compatible with MUSICA and clearly documented.
10. **Windows practicality / Windows 실용성** — testable in the user's primary environment and CI where feasible.
11. **Repository hygiene / 레포 위생** — no large DAW projects/media/plugin binaries in normal Git; small fixtures and manifests only.
12. **Future extensibility / 향후 확장성** — supports M5-R3 without making the interchange format itself canonical MUSICA authority.

## Round-trip authority target / 왕복 권한 목표

```text
Accepted .musica Revision
        ↓
Canonical Music IR / Blueprint-derived state
        ↓
Interchange Export Adapter
        ↓
External Interchange Artifact
        ↓ optional external DAW/tool editing
Imported External Artifact
        ↓
Interchange Parser / Import Adapter
        ↓
NON-CANONICAL Candidate
  + provenance
  + structured diff
  + unsupported/loss report
        ↓
HARD lock / constraint validation
        ↓ explicit user Accept only
New accepted .musica Revision
```

**No imported DAW/interchange file may directly replace the current accepted revision, branch ref, Blueprint, locks or canonical Music IR.**

**외부 DAW/interchange 파일은 현재 accepted revision, branch ref, Blueprint, lock 또는 canonical Music IR을 직접 대체할 수 없습니다.**

## Required R3 design proof / R3 필수 설계 증명

Before implementation, M5-R3 SHALL create and accept:

- a bilingual selection matrix with explicit source evidence and UNKNOWNs;
- one selected bounded first interchange target or `NO_SELECTION`;
- an interchange authority/round-trip contract;
- a loss model distinguishing `PRESERVED`, `TRANSFORMED`, `DROPPED`, `UNSUPPORTED`, and `UNKNOWN` semantics;
- provenance requirements for source artifact, exporter/importer versions, hashes and normalization;
- an explicit map between selected interchange entities and MUSICA Blueprint/Music IR entities;
- fixture policy that keeps large audio/plugin/project content out of normal Git.

## Required implementation proof / 구현 필수 증명

If one target clears the selection gate, M5-R3 SHALL prove at least:

1. machine-readable export from one accepted MUSICA revision;
2. deterministic or explicitly normalized serialization with artifact SHA-256;
3. selected format/schema validation where an authoritative schema exists;
4. preservation of the selected bounded set of tempo/meter/timeline/track/note/event semantics;
5. import produces a **non-canonical candidate**, never an accepted revision directly;
6. structured diff between current accepted MUSICA state and imported candidate;
7. explicit loss/unsupported report for fields outside the bounded mapping;
8. HARD locks/constraints remain authoritative over imported changes;
9. explicit Accept is required before M2 creates a new accepted revision;
10. tampered, malformed, traversal-containing or structurally invalid interchange artifacts fail closed;
11. provenance records exact input/output hashes and adapter/spec version;
12. round-trip test for the selected bounded fixture set;
13. at least one real external-tool/DAW interoperability smoke test if practical and legally/test-environment feasible; otherwise mark external-application execution `NOT VALIDATED` rather than infer it;
14. M0→M5-R2 regressions and M4-R3 real-browser regression remain green;
15. durable evidence, evidence-bearing exact-head CI, merge and state-only closure.

## Fidelity rule / fidelity 규칙

R3 must distinguish:

1. **Syntactic validity** — the artifact conforms to the selected format/container/schema.
2. **Semantic preservation** — mapped musical/production concepts survive export/import according to explicit comparison.
3. **External application compatibility** — a real DAW/tool successfully imports/exports the bounded artifact.
4. **Perfect project fidelity** — every DAW-specific device/plugin/state survives unchanged.

Passing #1 does not prove #2; passing #2 does not automatically prove #3; M5-R3 does **not** require or claim #4.

#1 통과는 #2를 자동 증명하지 않으며 #2 통과도 #3을 자동 증명하지 않습니다. M5-R3는 모든 DAW 고유 상태의 완전 왕복 보존(#4)을 요구하거나 주장하지 않습니다.

## Recommended development sequence / 권장 개발 순서

```text
repo/state preflight
→ current official spec/support research
→ candidate selection matrix
→ selection decision / NO_SELECTION
→ round-trip authority + loss model
→ bounded export schema/mapping
→ import-as-candidate path
→ structured diff + lock validation
→ deterministic normalization/hashes
→ round-trip fixtures/tests
→ optional real external-DAW smoke evidence
→ durable evidence
→ exact-head CI
→ merge
→ state-only closure
```

## Non-goals / 비목표

M5-R3 does not require or claim:

- direct in-process hosting of a DAW;
- VST/AU/CLAP plugin hosting inside MUSICA;
- support for every DAW or every interchange format;
- perfect preservation of proprietary plug-in/device state;
- bypassing user Accept after external edits;
- cloud collaboration;
- perceptual audio-quality superiority;
- replacement of MUSICA's Blueprint/Music IR with a third-party interchange schema.

## Planned follow-on / 후속 예정

After M5-R3, the intended next bounded phase remains **M5-R4 — Comparative Music/Audio Quality Evaluation**. M5-R4 should measure the perceptual and use-case quality gap between renderers without conflating format capability with listener preference.

M5-R3 이후 예정된 제한 단계는 **M5-R4 — Comparative Music/Audio Quality Evaluation / 음악·오디오 품질 비교 평가**입니다. M5-R4는 format capability와 청감 선호를 혼동하지 않고 renderer 간 지각적/use-case 품질 차이를 평가해야 합니다.

## Development discipline / 개발 규율

```text
Issue
→ selection branch from M5-R2 closure main
→ evidence-backed interchange selection
→ bounded implementation branch
→ tests + evidence
→ PR
→ exact-head CI
→ merge
→ state-only closure
```

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
