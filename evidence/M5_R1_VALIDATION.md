# M5-R1 Validation Evidence / M5-R1 검증 근거

## Status / 상태

**VALIDATED-BRANCH / BRANCH 검증 완료**

This document records branch-level validation evidence only. M5-R1 becomes repository-canonical `VALIDATED` only after the evidence-bearing exact PR head passes CI, PR #36 is merged, and state-only closure updates canonical state.

이 문서는 branch 수준 검증 근거만 기록합니다. M5-R1은 evidence-bearing exact PR head CI 통과, PR #36 병합, state-only closure 이후에만 repository 공식 `VALIDATED`가 됩니다.

## Scope / 범위

- Issue: #35 — `M5-R1: Renderer Adapter Contract & Audio Quality Baseline v0`
- Implementation PR: #36
- Validated implementation head before this durable evidence commit: `83ca3092b87db9f3a88cfceeb4a78f00e7050568`
- Validation workflow run: `34567768168`

M5-R1 establishes a renderer-neutral authority boundary around the existing deterministic local renderer and an objective PCM WAV signal-validity baseline. It does not claim production/mastering quality or DAW/VST interoperability.

M5-R1은 기존 결정론 local renderer 주위에 renderer-neutral 권한 경계와 객관적 PCM WAV 신호 유효성 기준선을 확립합니다. Production/mastering 음질이나 DAW/VST 상호운용성은 주장하지 않습니다.

## CI validation / CI 검증

Run `34567768168` completed successfully on the implementation head.

| Gate / 게이트 | Result / 결과 |
|---|---|
| Python 3.11 contracts/runtime | SUCCESS |
| Python 3.12 contracts/runtime | SUCCESS |
| Pytest | **92 passed in 52.18s** |
| M0 evidence generation | SUCCESS |
| M1 evidence generation | SUCCESS |
| M2 evidence generation | SUCCESS |
| M3-R1 evidence generation | SUCCESS |
| M3-R2 evidence generation | SUCCESS |
| M4-R1 evidence generation | SUCCESS |
| M4-R2 evidence generation | SUCCESS |
| M5-R1 renderer evidence generation | SUCCESS |
| M4-R3 Playwright Chromium regression | SUCCESS |
| M5-R1 artifact upload | SUCCESS |

## M5-R1 artifact / M5-R1 아티팩트

- Artifact name: `musica-m5-r1-renderer`
- Artifact ID: `10186660849`
- GitHub artifact digest: `sha256:2af43c347a1e802c846eb1df81e2db6f0f05e1ef58acf069ba9225fe20a611e4`
- Independent downloaded ZIP SHA-256: `2af43c347a1e802c846eb1df81e2db6f0f05e1ef58acf069ba9225fe20a611e4`
- Digest comparison: **MATCH**

## Exact Music IR binding / 정확한 Music IR 바인딩

Canonical Music IR SHA-256 used by the reference render:

`f28fd7f9268f1ff043f90988bb33800d95fce494cd0cc68c4265a6d8e0abc83d`

Evidence proves:

- `RendererRequest.music_ir_sha256` matches the exact canonical Music IR;
- renderer receives no Project authority;
- Music IR canonical bytes remain unchanged after rendering;
- renderer output is artifact/evidence only.

근거는 RendererRequest가 정확한 Music IR hash에 결합되고, renderer가 Project 권한을 받지 않으며, render 이후 Music IR canonical bytes가 불변임을 증명합니다.

## Reproducibility semantics / 재현성 의미

The reference renderer capability declares `byte_exact` reproducibility, but an individual `RendererResult` deliberately records:

```text
claim    = byte_exact
verified = false
```

A single render cannot prove its own reproducibility. Verification is established only by comparing two independent runs.

단일 render는 스스로 재현성을 증명할 수 없으므로 개별 RendererResult는 claim만 기록하고 `verified=false`로 유지합니다. 실제 검증은 독립된 두 render 비교에서 수행됩니다.

Cross-run proof:

| Artifact | Run A SHA-256 | Run B SHA-256 | Result |
|---|---|---|---|
| MIDI | `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f` | same | BYTE-EXACT |
| WAV | `e049e83bdda5a1c5710bd4d09b3010ab414d27d5a6705398aae120ae9deac5b8` | same | BYTE-EXACT |

Therefore branch evidence establishes `byte_exact_reproducibility = true` for this bounded reference renderer execution.

## Objective audio QA / 객관적 오디오 QA

The generated reference WAV passed the R1 signal-validity baseline:

| Metric / 지표 | Observed / 관측값 |
|---|---:|
| Container | valid WAV |
| Sample rate | 22,050 Hz |
| Channels | 1 mono |
| Bit depth | 16-bit PCM |
| Frame count | 441,000 |
| Duration | 20.0 s |
| Target duration | 20.0 s |
| Duration tolerance | 0.1 s |
| Non-zero sample count | 361,028 |
| Peak normalized amplitude | ~0.130527665 |
| Hard clipping samples | 0 |
| Normalized DC offset | ~-0.000008868 |
| Audio QA status | **PASS** |
| Integrated loudness | **UNKNOWN** |

`UNKNOWN` loudness is intentional. M5-R1 does not introduce a LUFS dependency and does not infer unmeasured perceptual/mastering quality.

LUFS는 R1에서 측정 dependency를 도입하지 않았으므로 의도적으로 `UNKNOWN`입니다. 측정하지 않은 perceptual/mastering 품질을 추론하지 않습니다.

## Fail-closed negative coverage / Fail-closed 부정 검증

Automated tests cover and reject at least:

- Music IR SHA-256 mismatch;
- unknown renderer ID;
- renderer capability mismatch;
- artifact byte/size tampering;
- result path traversal outside workspace;
- corrupt WAV container;
- silent WAV;
- hard-clipped WAV;
- duration-mismatched WAV.

The renderer boundary also rejects an internally inconsistent stochastic renderer claiming `byte_exact` reproducibility.

Renderer 경계는 `stochastic` renderer가 `byte_exact` 재현성을 주장하는 내부 모순도 거부합니다.

## Authority result / 권한 결과

```text
Accepted Blueprint
  ↓ trusted compiler
Canonical Music IR
  ↓ exact hash
RendererRequest
  ↓ capability-checked adapter
Renderer artifacts + AudioQualityReport
  ↓
RendererResult
```

**Renderer artifacts never become canonical musical authority.**

Renderer artifact는 공식 음악 권한으로 승격되지 않습니다.

## Claim boundary / 주장 경계

Validated here:

- renderer-neutral request/capability/result/QA contracts;
- exact Music IR binding;
- bounded renderer registry;
- workspace confinement and artifact hash verification;
- deterministic reference adapter using the existing MIDI/WAV renderer;
- reproducible objective PCM WAV signal-validity QA;
- cross-run byte-exact reference-render proof;
- preservation of M0→M4-R3 behavior.

Not validated here:

- professional or mastering audio quality;
- perceptual listener quality;
- stereo production rendering;
- VST/AU hosting;
- DAW automation/interoperability;
- higher-fidelity SoundFont/sampler/synth backend;
- cloud rendering;
- live OpenAI execution;
- waveform/piano-roll editing;
- stem separation.

## Promotion rule / 승격 규칙

This branch evidence SHALL NOT by itself promote M5-R1 to canonical `VALIDATED`.

Promotion requires:

1. this evidence file committed to the PR branch;
2. exact evidence-bearing PR head passes Python 3.11, Python 3.12, M0→M5 evidence generation/upload, and M4-R3 Chromium regression;
3. final M5 artifact digest/proof is rechecked;
4. PR #36 merges with exact-head protection;
5. state-only closure updates `memory/CURRENT_STATE.md` and `memory/NEXT_ACTION.md`.
