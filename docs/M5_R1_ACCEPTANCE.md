# M5-R1 Acceptance / M5-R1 수용 계약

## Mission / 미션

M5-R1 establishes a renderer-neutral authority boundary and an objective audio-quality baseline. It does **not** claim professional mastering quality or add a higher-fidelity backend.

M5-R1은 renderer-neutral 권한 경계와 객관적 오디오 품질 기준선을 확립합니다. **전문 mastering 음질을 주장하지 않으며 고품질 backend를 추가하지 않습니다.**

## Authority model / 권한 모델

```text
Accepted Blueprint
  ↓ trusted compiler
Canonical Music IR
  ↓ exact hash binding
RendererRequest
  ↓ capability validation
Renderer Adapter
  ↓
Artifacts + AudioQualityReport
  ↓ exact artifact hashes
RendererResult
```

Renderer output is artifact/evidence only. A renderer SHALL NOT replace or mutate accepted Blueprint, Music IR, revision, branch, or project authority.

Renderer 출력은 artifact/evidence일 뿐입니다. Renderer는 승인된 Blueprint, Music IR, revision, branch, project 권한을 대체하거나 변경해서는 안 됩니다.

## Required machine contracts / 필수 기계 계약

- `renderer-request-v0.schema.json`
- `renderer-capability-v0.schema.json`
- `renderer-result-v0.schema.json`
- `audio-quality-report-v0.schema.json`

## Required proof / 필수 증명

M5-R1 is acceptable only when repository tests prove all of the following:

1. exact canonical Music IR SHA-256 is bound into the request and checked before rendering;
2. unknown renderer IDs and capability mismatches fail closed;
3. requested outputs must be declared by renderer capability;
4. output paths remain inside the supplied workspace;
5. artifact role/path/hash/size are returned in a validated RendererResult;
6. WAV output produces a validated AudioQualityReport;
7. corrupt, silent, clipped, duration-mismatched audio is rejected or reported FAIL under explicit policy;
8. deterministic reference rendering is byte reproducible for the same request;
9. artifact tampering is detectable by hash verification;
10. rendering leaves input Music IR byte-equivalent and cannot promote project authority;
11. all prior M0→M4-R3 regression remains green.

## Audio QA baseline / 오디오 QA 기준선

The R1 analyzer records only reproducible measurements available from the PCM WAV container:

- container validity;
- sample rate;
- channel count;
- sample width / bit depth;
- frame count;
- duration;
- expected-duration tolerance;
- non-zero sample count;
- peak normalized amplitude;
- hard clipping sample count;
- normalized DC offset;
- SHA-256 and byte size.

Integrated loudness is `UNKNOWN` in R1 because no reproducible loudness dependency is introduced here.

R1에서는 재현 가능한 loudness dependency를 추가하지 않으므로 integrated loudness는 `UNKNOWN`입니다.

## PASS/WARN/FAIL policy / 판정 정책

- `FAIL`: invalid container, empty/silent signal, duration outside tolerance, or hard digital clipping;
- `WARN`: valid signal but DC offset exceeds the bounded warning threshold;
- `PASS`: required validity, signal, duration and clipping checks pass without warning;
- `UNKNOWN`: reserved for individual unmeasured metrics and shall not be used to silently convert a failed required check into success.

## Non-goals / 비목표

M5-R1 does not validate VST/AU hosting, DAW automation, production mastering, cloud rendering, human listening quality, live OpenAI execution, waveform editing, stem separation, or a proprietary audio model.
