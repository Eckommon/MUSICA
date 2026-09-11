# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M5-R1 — RENDERER ADAPTER CONTRACT & AUDIO QUALITY BASELINE v0 / M5-R1 — 렌더러 어댑터 계약 및 오디오 품질 기준선 v0**

M4-R3 is validated. The next problem is no longer whether MUSICA can be operated as a Browser Studio. The next bounded problem is to separate musical authority from rendering implementation and establish a measurable audio-quality baseline before integrating higher-fidelity or DAW-oriented backends.

M4-R3는 검증 완료되었습니다. 이제 핵심 문제는 Browser Studio 조작 가능 여부가 아닙니다. 다음 제한 문제는 음악적 권한과 renderer 구현을 분리하고, 고품질 renderer 또는 DAW backend를 통합하기 전에 측정 가능한 오디오 품질 기준선을 확립하는 것입니다.

## Why M5-R1 comes first / 왜 M5-R1이 먼저인가

MUSICA must not become coupled to one synth, DAW, VST host, generative-audio provider, or operating system. Renderer backends may transform validated Music IR into MIDI/audio artifacts, but they must never gain authority to mutate accepted Blueprint/IR/project state.

MUSICA는 특정 synth, DAW, VST host, generative-audio provider, 운영체제에 종속되어서는 안 됩니다. Renderer backend는 검증된 Music IR을 MIDI/audio artifact로 변환할 수 있지만, 승인된 Blueprint/IR/project state를 변경할 권한을 가져서는 안 됩니다.

M5-R1 therefore establishes the renderer trust boundary and objective audio QA before M5-R2 adds a higher-fidelity backend.

## M5 phase decomposition / M5 단계 분해

```text
M5-R1 Renderer Adapter Contract + Audio QA Baseline
  ↓
M5-R2 First Higher-Fidelity Local Renderer Adapter
  ↓
M5-R3 DAW / interchange interoperability
  ↓
M5-R4 Comparative music/audio quality evaluation
```

This sequence is intentionally incremental. M5-R1 does **not** attempt a full DAW, VST host, or proprietary audio foundation model.

## R1 architecture target / R1 아키텍처 목표

```text
Accepted Blueprint Revision
        ↓ trusted lowering
Canonical Music IR
        ↓
Renderer Request
        ↓
Renderer Adapter Boundary
  ├─ builtin deterministic reference renderer
  └─ future external/high-fidelity adapters
        ↓
Renderer Result Manifest
  ├─ MIDI/audio artifacts
  ├─ backend identity/version
  ├─ settings + seed
  ├─ hashes
  ├─ warnings/errors
  └─ objective audio QA metrics
        ↓
Artifact binding
        ↓
.musica Project Bundle
```

**Renderer output is evidence/artifact, never canonical musical authority. / Renderer 출력은 근거·artifact이며 공식 음악적 권한이 아닙니다.**

## Required contracts / 필수 계약

M5-R1 SHALL define machine-valid contracts for at least:

1. `RendererRequest v0`
   - exact Music IR identity/hash,
   - requested output formats,
   - renderer ID/configuration,
   - seed where applicable,
   - target audio format,
   - bounded render intent/hints that cannot mutate core music state.

2. `RendererCapability v0`
   - renderer identity/version,
   - deterministic/stochastic classification,
   - supported input/output types,
   - supported sample rates/channels/bit depth where relevant,
   - external binary/plugin/network requirements,
   - reproducibility guarantees.

3. `RendererResult v0`
   - exact input binding,
   - artifact paths/roles,
   - SHA-256 hashes and sizes,
   - renderer identity/version/settings,
   - warnings,
   - deterministic/reproducibility status,
   - objective QA result.

4. `AudioQualityReport v0`
   - format validity,
   - sample rate,
   - channels,
   - sample/bit depth where observable,
   - duration and target tolerance,
   - peak level / clipping count or equivalent bounded metric,
   - silence/non-empty signal check,
   - DC offset or comparable sanity metric,
   - loudness metric only if implemented with a reproducible dependency,
   - PASS/WARN/FAIL policy with explicit thresholds.

## Reference renderer / 기준 renderer

The existing bounded deterministic local WAV/MIDI path SHALL be adapted behind the new renderer interface rather than rewritten as a new music engine.

기존 제한적 deterministic local WAV/MIDI 경로를 새 renderer interface 뒤에 배치하며, 별도의 음악 엔진처럼 재작성하지 않습니다.

R1 must prove that the same canonical Music IR passed through the reference adapter still produces valid artifacts and preserves current M0→M4 behavior.

## Trust and authority invariants / 신뢰·권한 불변식

M5-R1 SHALL fail closed if any adapter:

- returns artifacts bound to a different Music IR hash,
- attempts to replace accepted Blueprint/Music IR state,
- returns undeclared output formats or unsupported capability claims,
- omits required artifact hashes/metadata,
- violates workspace/path confinement,
- reports success when required audio QA fails,
- claims deterministic reproducibility without evidence.

Adapters may fail or produce warnings; they may not silently upgrade their authority.

## Audio quality baseline / 오디오 품질 기준선

R1 is a **measurement and contract milestone**, not a claim of professional mastering quality.

At minimum the reference renderer SHALL produce a durable QA report proving:

```text
valid audio container
sample rate / channels recorded
non-empty signal
expected duration within explicit tolerance
no hard digital clipping under the defined baseline policy
artifact SHA-256 and byte size recorded
same deterministic request → reproducible result where promised
```

If a metric cannot be measured reliably with the selected dependencies, it must be `UNKNOWN` rather than inferred.

## Required tests / 필수 테스트

At minimum:

- schema validation for request/capability/result/QA,
- deterministic reference render reproducibility,
- exact Music IR hash binding,
- renderer capability mismatch rejection,
- unknown renderer rejection,
- undeclared output rejection,
- tampered artifact/hash detection,
- workspace traversal rejection,
- invalid/corrupt audio detection,
- clipping/empty-audio negative fixtures,
- current M0→M4 regression remains green.

## M5-R1 acceptance gate / M5-R1 수용 게이트

M5-R1 may be promoted only when:

1. renderer-neutral contracts are machine-valid,
2. current deterministic render path is reachable only through the bounded reference adapter in the tested R1 path,
3. Renderer Result binds exact Music IR + exact artifact hashes,
4. objective AudioQualityReport is generated and tested,
5. negative/tamper tests fail closed,
6. no renderer can mutate canonical Blueprint/IR/project authority,
7. existing M0→M4-R3 regression remains green,
8. dedicated durable evidence is generated,
9. evidence-bearing PR exact head passes required CI and is merged,
10. state-only closure promotes R1.

## Non-goals / 비목표

M5-R1 does not require or claim:

- professional/mastering audio quality,
- actual VST/AU plugin hosting,
- Ableton/Logic/Cubase/FL Studio automation,
- proprietary foundation audio model training,
- cloud rendering,
- live OpenAI provider evidence,
- human listener preference studies,
- stem separation,
- waveform/piano-roll editor implementation.

## Planned follow-on / 후속 예정

After M5-R1 closure, M5-R2 should select the first higher-fidelity local backend based on reproducibility, licensing, Windows compatibility, automation surface, audio quality, install burden and renderer isolation. Candidate technologies may include a SoundFont/FluidSynth-class backend or another locally automatable synth path, but no candidate is accepted until evaluated against the R1 contract.

M5-R1 종료 후 M5-R2에서 재현성, 라이선스, Windows 호환성, 자동화 인터페이스, 음질, 설치 부담, renderer 격리 기준으로 첫 고품질 local backend를 선정합니다. 후보 기술은 R1 계약에 대한 평가 전까지 승인된 것으로 간주하지 않습니다.

## Development discipline / 개발 규율

```text
Issue
→ branch from M4-R3 closure main
→ R1 acceptance contract
→ renderer schemas + adapter boundary
→ reference adapter migration
→ audio QA analyzer
→ negative/tamper tests
→ durable evidence
→ PR
→ exact-head CI
→ merge
→ M5-R1 state-only closure
```

Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.
