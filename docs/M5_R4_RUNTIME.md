# M5-R4 Runtime / M5-R4 실행 비교 런타임

**Status / 상태:** `IMPLEMENTATION BRANCH — VALIDATION PENDING`

This document records the executable implementation of the accepted M5-R4A contracts. It narrows but does not broaden `docs/M5_R4_EVALUATION_CONTRACT.md` and `docs/M5_R4_ACCEPTANCE.md`.

이 문서는 승인된 M5-R4A 계약의 실행 구현을 기록합니다. `docs/M5_R4_EVALUATION_CONTRACT.md`와 `docs/M5_R4_ACCEPTANCE.md`의 범위를 좁힐 수는 있으나 확장하지 않습니다.

## 1. Runtime flow / 실행 흐름

```text
accepted Blueprint fixture
→ one exact canonical Music IR
→ same Windows CI job
   ├─ musica-reference-local
   │    → native 22,050 Hz mono 16-bit PCM WAV
   └─ musica-fluidsynth-local
        → FluidSynth 2.6.0 + exact-hash FluidR3_GM 3.1
        → native 48,000 Hz stereo 16-bit PCM WAV
→ existing AudioQualityReport on each artifact
→ exact source/provenance/comparability gate
→ native-PCM time-domain analysis
→ common-physical-band spectral analysis
→ paired deltas + explicit confounds
→ `audio-comparison-result-v0`
```

No comparison step mutates Blueprint, Music IR, RendererResult or M2 project state.

## 2. Implementation ownership / 구현 소유권

- `src/musica/audio_compare.py`
  - native PCM loading;
  - full-scale sample normalization;
  - common physical frequency ceiling;
  - objective metric calculation;
  - paired deltas;
  - comparability and provenance gate;
  - confound construction;
  - comparison schema validation.
- `src/musica/m5_r4_demo.py`
  - exact-source compile/render orchestration;
  - two independent paired executions;
  - negative cases;
  - reproducibility proof;
  - evidence manifest.
- `tests/test_m5_r4_audio_compare.py`
  - bounded synthetic unit/negative tests.
- `.github/workflows/m5-r4-evidence.yml`
  - one Windows evidence job containing both renderer paths.

## 3. Dependency boundary / 의존성 경계

M5-R4 adds NumPy `>=2.0,<3` for deterministic vector/FFT analysis.

NumPy provides numerical primitives only. MUSICA owns:

- metric definitions;
- band boundaries;
- channel policy;
- frequency-support policy;
- comparability semantics;
- claim semantics.

No SciPy, librosa, ML model or externally defined quality score is introduced in v0.

## 4. PCM normalization / PCM 정규화

Supported PCM widths are 8/16/24/32-bit integer PCM. Samples are converted to float64 by the signed full-scale denominator for the source width:

```text
8-bit unsigned PCM → center at 128 → divide by 128
16-bit signed PCM  → divide by 32768
24-bit signed PCM  → divide by 2^23
32-bit signed PCM  → divide by 2^31
```

The native channel count and sample rate are preserved. No comparison audio file is generated.

## 5. Spectral implementation / 스펙트럼 구현

For each native artifact:

1. arithmetic channel mean for spectral analysis only;
2. `round(sample_rate * 0.050)`-sample Hann window;
3. 50% nominal overlap using rounded half-window hop;
4. one-sided `rfft` power;
5. average power across all complete windows;
6. common pair frequency range:

```text
20 Hz … min(10000 Hz, 0.45 * min(sr_A, sr_B))
```

Initial pair ceiling: **9922.5 Hz**.

No resampling is performed.

## 6. Initial branch evidence / 초기 branch 근거

Branch evidence run:

- branch: `m5-r4b-paired-audio-evaluation-v0`
- head: `d967e647116180f8550ebb3da32ddf929e93beed`
- workflow: `M5-R4 Paired Audio Evidence`
- run: `34672991324`
- result: **SUCCESS**
- bounded M5-R4 contract + analyzer tests: **16 passed**
- artifact: `musica-m5-r4-paired-audio`
- artifact ID: `10291317280`
- artifact ZIP digest: `sha256:39631d62d5a8a15b1f09f739862e7458d9ea75264fc6d91c4871277edb45c727`

This branch evidence is not yet the final M5-R4 durable validation; exact PR-head full regression and evidence-bearing revalidation remain required.

## 7. First observed objective descriptors / 최초 관측 객관 지표

The first branch run observed the following under the same canonical Music IR and the accepted v0 metric policy:

| Descriptor | Reference A | FluidSynth B | B − A |
|---|---:|---:|---:|
| RMS | `-31.803804307 dBFS` | `-41.076115094 dBFS` | `-9.272310787 dB` |
| Peak | `-17.686213694 dBFS` | `-21.443738950 dBFS` | `-3.757525256 dB` |
| Crest factor | `14.117590613 dB` | `19.632376144 dB` | `+5.514785531 dB` |
| Silence ratio | `0.183448980` | `0.013163542` | `-0.170285438` |
| Spectral centroid | `265.398918183 Hz` | `507.141072434 Hz` | `+241.742154251 Hz` |
| Spectral rolloff 95% | `460.208711434 Hz` | `2640.0 Hz` | `+2179.791288566 Hz` |
| Low-band ratio | `0.411622766` | `0.675357185` | `+0.263734419` |
| Mid-band ratio | `0.588218572` | `0.296053948` | `-0.292164624` |
| High-band ratio | `0.000158662` | `0.028588867` | `+0.028430205` |

Reference A is mono, therefore stereo correlation and stereo-difference RMS are `NOT_APPLICABLE` for paired delta. FluidSynth B alone measured stereo correlation `0.141025982` and stereo-difference RMS `-44.761599872 dBFS`.

**These values are descriptive signals only. They are not quality rankings.**

## 8. Initial reproducibility / 최초 재현성

Within the exact branch Windows run:

- reference pair A/B WAV SHA-256: identical;
- FluidSynth pair A/B WAV SHA-256: identical;
- objective metrics and paired deltas: identical;
- canonical comparison A/B SHA-256: identical;
- comparison SHA-256: `cb480c03fef734148592d6aeb60049836837371880bfe2e978f03b69493c3343`.

Observed final WAV hashes:

- reference: `e049e83bdda5a1c5710bd4d09b3010ab414d27d5a6705398aae120ae9deac5b8`;
- FluidSynth: `e054ad9cb7d938f50f75d222c1522e71cc7a7f163e8ea7bf3f8dceec628bcfa3`.

## 9. Negative authority proof / 음성 권한 증명

Initial branch evidence confirms:

- different Music IR source → `NOT_COMPARABLE`;
- failed required AudioQualityReport → `NOT_COMPARABLE`;
- missing required FluidSynth content provenance → `NOT_COMPARABLE`;
- attempted perceptual-superiority schema tamper → rejected.

Synthetic tests additionally cover Blueprint binding mismatch and artifact-hash tamper.

## 10. Explicit confounds / 명시적 교란

The initial pair records:

- `CHANNEL_LAYOUT_DIFFERENCE` — A mono, B stereo;
- `SAMPLE_RATE_DIFFERENCE` — A 22,050 Hz, B 48,000 Hz;
- `RENDERER_LEVEL_DURATION_NORMALIZATION` — FluidSynth final artifact uses the already validated tail-trim policy;
- `DEFAULT_EFFECT_OR_REVERB_DIFFERENCE` — `UNKNOWN`, not independently isolated.

The runtime does not erase these differences.

## 11. Claim boundary / 주장 경계

Every valid M5-R4-v0 result keeps:

```text
HUMAN_SUBJECT_EVIDENCE = NOT_VALIDATED
PERCEPTUAL_SUPERIORITY = UNKNOWN
HUMAN_PREFERENCE_CLAIM_ALLOWED = false
```

`COMPARABLE_OBJECTIVE_ONLY` means the pair is technically valid for the frozen objective descriptor contract. It does **not** mean either renderer sounds better.
