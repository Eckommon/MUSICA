# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M5-R4 — COMPARATIVE MUSIC / AUDIO QUALITY EVALUATION v0 / M5-R4 — 비교 음악·오디오 품질 평가 v0**

M5-R3 is closed as `VALIDATED — BOUNDED` once this state-only closure reaches main. The next mission is not another renderer implementation and not an immediate claim that FluidSynth/FluidR3 sounds better. The next mission is to design and execute a controlled evaluation that separates **technical audio validity, renderer capability and perceived/music quality**.

이 state-only closure가 main에 병합되면 M5-R3는 `VALIDATED — BOUNDED`로 종결됩니다. 다음 작업은 새 renderer 추가나 FluidSynth/FluidR3가 더 좋게 들린다는 즉시 주장이 아닙니다. **기술적 오디오 유효성, renderer capability, 청감·음악 품질**을 분리하는 통제 평가를 설계·실행하는 것이 다음 mission입니다.

## Governing prior evidence / 선행 권위

Read before work:

- `evidence/M5_R1_VALIDATION.md`
- `evidence/M5_R2_VALIDATION.md`
- `evidence/M5_R3_VALIDATION.md`
- `docs/M5_R2_RUNTIME.md`
- `docs/M5_R3_RUNTIME.md`
- `memory/CURRENT_STATE.md`

M5-R2 explicitly proved 48 kHz stereo renderer capability but **did not prove perceptual superiority**. M5-R4 exists to address that unknown without overstating evidence.

## Mission objective / mission 목표

Create an evidence-backed comparison framework capable of answering, for controlled paired renders:

1. Are both outputs technically valid under the same musical source authority?
2. Are differences caused by renderer/content/config rather than different composition state?
3. Which objective audio descriptors differ, and by how much?
4. What can and cannot be inferred about perceptual/music quality without human-subject evidence?
5. Can MUSICA record comparison evidence reproducibly enough to support future renderer selection or quality optimization?

## Required phase order / 필수 단계 순서

Do not start with subjective scoring. Proceed in this order:

```text
M5-R4A Evaluation Contract
→ exact source/paired-render binding
→ objective descriptor design
→ confound controls
→ deterministic/reproducible evidence format
→ paired reference-vs-FluidSynth execution
→ objective report + waveform/spectral evidence
→ optional bounded machine heuristic analysis
→ claim-boundary review
→ durable evidence
→ exact-head CI
→ merge/state closure
```

## M5-R4A — Evaluation contract first / 평가 계약 우선

Create a normative acceptance/evaluation specification before implementation. It SHALL distinguish at least three evidence layers:

### Layer 1 — Technical validity / 기술 유효성

Examples:

- exact source Music IR hash equality;
- requested/final duration;
- sample rate/channels/sample width;
- clipping/silence/DC offset/invalid samples;
- renderer/runtime/content/config provenance;
- artifact SHA-256;
- render success/failure and normalization policy.

### Layer 2 — Objective comparative descriptors / 객관 비교 지표

Select bounded, reproducible descriptors with explicit units and interpretation limits, for example:

- integrated/RMS-like level descriptors where implementation is dependency-safe;
- peak/crest factor;
- stereo correlation or channel-difference evidence where applicable;
- spectral centroid/band-energy descriptors;
- spectral flatness/rolloff or similarly bounded timbral descriptors;
- transient/onset density if reliably implementable;
- silence ratio/dynamic-range proxies.

Exact metric set must be selected and documented before coding. Avoid introducing a heavy ML dependency merely to create a score.

### Layer 3 — Perceptual/music-quality claims / 청감·음악 품질 주장

Default state:

```text
PERCEPTUAL_SUPERIORITY = UNKNOWN
HUMAN_SUBJECT_EVIDENCE = NOT VALIDATED
```

Machine metrics or an LLM judgment SHALL NOT be presented as proof that one renderer sounds better to humans. If no controlled listening study is executed, the milestone may validate the **comparison framework and objective differences**, not perceptual superiority.

## Paired-source authority / paired source 권한

Every A/B comparison SHALL prove both paths render the **same exact canonical Music IR** or another explicitly equivalent frozen source representation.

Required bindings:

- accepted Blueprint revision ID/hash;
- canonical Music IR SHA-256;
- renderer adapter ID/version;
- renderer executable/runtime identity where external;
- external content identity/hash where applicable;
- exact renderer config;
- output artifact hashes.

A pair with different composition state is invalid for renderer-quality comparison.

## Confound policy / 교란 통제 정책

The evaluation contract SHALL define how to handle at least:

- mono vs stereo capability difference;
- sample-rate difference;
- duration/release-tail normalization;
- gain/loudness differences;
- different instrument/sample content;
- renderer effects/reverb defaults;
- nondeterminism or environment differences.

Do not silently normalize away a difference that is itself part of the renderer behavior. Record raw and comparison-normalized evidence separately when normalization is necessary.

## Comparison result model / 비교 결과 모델

Prefer a machine-readable result with at least:

```text
source_binding
renderer_a
renderer_b
raw_artifacts
technical_validity
objective_metrics_a
objective_metrics_b
paired_deltas
normalizations_applied
confounds
interpretations
claim_boundary
verdict
```

Possible bounded verdict vocabulary should separate evidence quality from preference, e.g.:

```text
COMPARABLE
NOT_COMPARABLE
OBJECTIVE_DIFFERENCE_OBSERVED
NO_MATERIAL_OBJECTIVE_DIFFERENCE_OBSERVED
PERCEPTUAL_PREFERENCE_UNKNOWN
```

Do not use `BETTER`/`WORSE` without an explicitly defined, validated preference criterion.

## Initial fixture / 초기 fixture

Begin with the existing deterministic dark-electronic canonical fixture used in M5-R1/M5-R2/M5-R3 so prior source hashes and renderer evidence remain reusable.

First pair:

```text
same accepted Blueprint
→ same exact canonical Music IR
├─ musica-reference-local
└─ musica-fluidsynth-local + pinned FluidR3_GM 3.1
```

If CI cannot practically execute both paths in one comparable environment, the acceptance contract must define a hash-bound artifact handoff rather than pretending the runs are directly paired.

## Human listening study / 인간 청취 평가

A formal human study is **not required** for the first M5-R4 bounded closure unless practical and ethically/operationally sound. If absent, record:

```text
HUMAN_SUBJECT_EVIDENCE = NOT VALIDATED
PERCEPTUAL_SUPERIORITY = UNKNOWN
```

A later phase may add blinded AB/ABX or preference testing with a separate protocol.

## Required negative cases / 필수 음성 케이스

At minimum prove that comparison fails closed or becomes `NOT_COMPARABLE` when:

- source Music IR hashes differ;
- one artifact fails technical QA;
- required provenance is missing;
- renderer/content identity is missing where required;
- duration normalization is ambiguous or unrecorded;
- an attempted comparison silently substitutes a different Blueprint/revision.

## Repository discipline / 레포 규율

Use normal workflow:

```text
Issue
→ evaluation/acceptance specification branch
→ PR + exact-head CI
→ merge
→ fresh implementation branch
→ tests + paired evidence
→ durable validation
→ exact-head CI
→ merge
→ state closure
```

Do not combine renderer selection, subjective product claims and evaluation implementation into one opaque change.

## Non-goals / 비목표

M5-R4-v0 does not require or claim:

- universal audio-quality scoring;
- scientific proof of human preference without human evidence;
- mastering-grade evaluation;
- training a proprietary perceptual model;
- adding another renderer before comparison discipline exists;
- replacing professional listening tests;
- optimizing music generation merely to improve selected metrics.

## Exit condition / 종료 조건

M5-R4 may close only when repository evidence can truthfully state what was technically compared, what objective differences were observed, what confounds were controlled, and what perceptual conclusions remain unknown.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
