# M5-R4 Evaluation Contract v0 / M5-R4 비교 오디오 평가 계약 v0

**Status / 상태:** `PROPOSED — M5-R4A CONTRACT`

## 1. Purpose / 목적

M5-R4 defines how MUSICA may compare two rendered audio artifacts without confusing **technical validity**, **objective signal difference**, and **human perceptual/music quality**.

M5-R4는 두 렌더 오디오를 비교할 때 **기술적 유효성**, **객관적 신호 차이**, **인간 청감·음악 품질**을 혼동하지 않도록 평가 권한을 정의합니다.

This contract does not select a new renderer and does not assert that the higher sample rate, stereo output, a larger SoundFont, or any machine metric means “better music.”

이 계약은 새 renderer를 선정하지 않으며, 더 높은 sample rate, stereo 출력, 더 큰 SoundFont 또는 기계 지표가 곧 “더 좋은 음악”이라는 뜻이라고 주장하지 않습니다.

## 2. Governing authority / 지배 권한

A comparison is downstream evidence only.

```text
Accepted Blueprint revision
  ↓ trusted compiler
Canonical Music IR
  ↓ exact SHA-256 source binding
  ├─ Renderer A → Result A → AudioQualityReport A
  └─ Renderer B → Result B → AudioQualityReport B
                    ↓
              Comparability Gate
                    ↓
        Objective Descriptor Analysis
                    ↓
              Paired Deltas
                    ↓
              Claim Boundary
```

A comparison result SHALL NOT mutate or outrank accepted Blueprint, canonical Music IR, renderer result provenance, or M2 project authority.

## 3. Evidence layers / 근거 계층

### Layer 1 — Technical validity / 기술 유효성

The pair SHALL bind and verify:

- accepted Blueprint revision ID and Blueprint SHA-256;
- one exact canonical Music IR SHA-256;
- each renderer request/result bound to that exact Music IR;
- renderer adapter ID/version;
- runtime/executable identity where applicable;
- external content identity/hash where applicable;
- exact renderer configuration or canonical configuration hash;
- raw output artifact SHA-256 and size;
- AudioQualityReport status and report hash;
- requested/final duration and any renderer-level normalization provenance.

If either path does not prove the same source authority, the pair is `NOT_COMPARABLE`.

### Layer 2 — Objective comparative descriptors / 객관 비교 지표

M5-R4-v0 freezes the following dependency-bounded descriptor set. These are signal descriptors, **not quality scores**.

| Metric | Unit | v0 definition / v0 정의 | Interpretation limit / 해석 한계 |
|---|---|---|---|
| `rms_dbfs` | dBFS | `20*log10(sqrt(mean(x^2)))` over all normalized channel samples | level/energy proxy only |
| `peak_dbfs` | dBFS | `20*log10(max(abs(x)))` | peak level only |
| `crest_factor_db` | dB | `peak_dbfs - rms_dbfs` | dynamic peak-to-average proxy only |
| `silence_ratio` | ratio `0..1` | fraction of frames where every channel is at/below `-80 dBFS` amplitude | threshold-dependent silence proxy |
| `dc_offset_normalized` | normalized | mean normalized sample value over all channels | signal bias only |
| `stereo_correlation` | correlation `-1..1` | Pearson L/R correlation after per-channel mean removal; 2-channel only | stereo relationship, not width preference |
| `stereo_difference_rms_dbfs` | dBFS | RMS of `(L-R)/2`; 2-channel only | side-energy proxy only |
| `spectral_centroid_hz` | Hz | centroid of average windowed power spectrum within the common physical frequency range | brightness-related descriptor, not timbre quality |
| `spectral_rolloff_95_hz` | Hz | frequency below which 95% of in-band power lies | spectral distribution only |
| `band_energy_low_ratio` | ratio | `20–250 Hz` energy / common-band energy | coarse spectral balance only |
| `band_energy_mid_ratio` | ratio | `250–4000 Hz` energy / common-band energy | coarse spectral balance only |
| `band_energy_high_ratio` | ratio | `4000 Hz–ceiling` energy / common-band energy | coarse spectral balance only |

Integrated LUFS is intentionally **not required in v0**. M5-R1 left it `UNKNOWN`, and R4A does not add a new loudness standard merely to manufacture a ranking.

### Layer 3 — Perceptual/music-quality claims / 청감·음악 품질 주장

For M5-R4-v0:

```text
HUMAN_SUBJECT_EVIDENCE = NOT_VALIDATED
PERCEPTUAL_SUPERIORITY = UNKNOWN
HUMAN_PREFERENCE_CLAIM_ALLOWED = false
```

No RMS, spectral, stereo, machine heuristic, or LLM output can promote these values.

A later human-study schema/version may change that boundary only under a separate protocol.

## 4. Normalized sample domain / 정규화 샘플 영역

PCM samples are converted to full-scale-normalized floating values in `[-1, 1]` using the source bit depth. The original artifacts remain immutable.

All time-domain metrics except stereo-specific metrics are computed over **all channel samples**, not after hidden downmixing. This allows mono and stereo artifacts to retain their native channel topology while sharing a defined energy convention.

## 5. Spectral analysis policy / 스펙트럼 분석 정책

M5-R4-v0 SHALL NOT resample audio merely to compare it.

For each artifact:

1. derive a spectral analysis signal by arithmetic channel mean; mono remains unchanged;
2. use a Hann window with a nominal duration of `50 ms`;
3. use `50%` overlap;
4. compute one-sided power spectra;
5. average frame power spectra before aggregate descriptor calculation;
6. ignore frequencies below `20 Hz`;
7. use one pair-level common ceiling:

```text
min(10000 Hz, 0.45 * min(sample_rate_a, sample_rate_b))
```

The same physical frequency range is therefore used for both outputs without silently resampling either artifact.

If the common ceiling is not high enough to support a defined band, the affected metric becomes `NOT_APPLICABLE` or the pair becomes `NOT_COMPARABLE` where the missing band is required by the acceptance gate.

A numerical FFT implementation may use NumPy in M5-R4B. M5-R4A does not require SciPy, librosa, a psychoacoustic model, or any ML dependency.

## 6. Analysis window / 분석 구간

The initial M5-R4 pair SHALL compare the same requested canonical duration.

- raw renderer artifacts and renderer-level normalization evidence remain preserved;
- the final artifacts used for comparison SHALL each satisfy the same target duration under their validated renderer policy;
- comparison-time trimming, padding, time stretching, resampling, or loudness normalization is forbidden in the initial pair;
- if a common analysis window cannot be proven without an additional transform, the pair is `NOT_COMPARABLE` until that transform is separately specified and recorded.

## 7. Gain/loudness policy / gain·loudness 정책

M5-R4-v0 performs **no comparison-time gain or loudness matching**.

Output level is part of the renderer/content/config behavior and must be measured rather than normalized away. Any later loudness-matched perceptual study must create a separate derived artifact and preserve both raw and normalized hashes.

## 8. Treatment vs confound / 비교 대상과 교란

The comparison treatment is the complete renderer bundle:

```text
renderer adapter + runtime + external content + exact config
```

The following MUST be recorded when different or unknown:

- `CHANNEL_LAYOUT_DIFFERENCE`
- `SAMPLE_RATE_DIFFERENCE`
- `BIT_DEPTH_DIFFERENCE`
- `RENDERER_LEVEL_DURATION_NORMALIZATION`
- `RUNTIME_OS_DIFFERENCE`
- `DEFAULT_EFFECT_OR_REVERB_DIFFERENCE`
- `NONDETERMINISM`
- `MISSING_PROVENANCE`
- `UNKNOWN_RENDERER_BEHAVIOR`

A recorded difference does not automatically invalidate comparison. It limits interpretation. Missing required provenance, ambiguous normalization, source mismatch, or failed technical QA does invalidate comparison.

## 9. Initial pair / 초기 pair

The first implementation pair SHALL reuse the existing deterministic dark-electronic fixture and exact canonical Music IR already proven by M5-R1/M5-R2/M5-R3.

Known starting conditions:

```text
same accepted Blueprint / same canonical Music IR
├─ musica-reference-local      → 22,050 Hz / mono / 16-bit PCM
└─ musica-fluidsynth-local     → 48,000 Hz / stereo / 16-bit PCM / FluidR3_GM 3.1
```

The sample-rate and channel-layout differences are explicit observed treatment outputs, not hidden preprocessing targets.

For the first execution, M5-R4B SHOULD render both paths in the **same Windows CI job** from the same checked-out source and same serialized Music IR. If that proves impractical, a hash-bound cross-job handoff must be specified and the environment difference recorded.

## 10. Comparability gate / 비교 가능성 gate

`COMPARABLE` requires all of the following:

1. source Blueprint binding is present;
2. renderer A and B each bind the exact same canonical Music IR SHA-256;
3. each required RendererResult and AudioQualityReport provenance is present;
4. neither required AudioQualityReport is `FAIL`;
5. target durations match and final comparison windows are unambiguous;
6. no comparison-time transform is hidden or unrecorded;
7. runtime/content/config identities required by each adapter are present;
8. objective metric method/version is pinned;
9. raw artifact hashes remain preserved.

Otherwise the result is `NOT_COMPARABLE` with machine-readable reasons.

## 11. Paired deltas / 쌍대 차이

For every metric measured on both sides with the same method and unit:

```text
delta_b_minus_a = metric_b - metric_a
```

A delta is descriptive only. Positive or negative sign SHALL NOT be mapped to `BETTER` or `WORSE` in v0.

Metrics unavailable on one side, such as stereo-only metrics for a mono renderer, use `NOT_APPLICABLE` and have no paired delta.

## 12. Machine result / 기계 결과

`schemas/audio-comparison-result-v0.schema.json` is the machine contract for M5-R4. It separates:

- source binding;
- renderer identities and raw artifacts;
- technical validity;
- analysis policy;
- objective metrics;
- paired deltas;
- normalizations;
- confounds;
- comparability;
- claim boundary.

M5-R4B may add semantic validation beyond JSON Schema but SHALL NOT weaken this contract.

## 13. Reproducibility / 재현성

The comparison report SHALL record enough provenance to reproduce or explain the pair:

- source hashes;
- adapter/runtime/content/config identities;
- analyzer ID/version;
- metric policy version;
- raw artifact hashes;
- comparison report canonical hash;
- CI/run provenance where evidence is produced.

## 14. Non-goals / 비목표

M5-R4-v0 does not establish:

- a universal music quality score;
- human preference;
- mastering quality;
- psychoacoustic equivalence;
- perceptual transparency of any normalization;
- renderer ranking across all music;
- model-generated aesthetic truth;
- a reason to optimize composition merely to improve selected metrics.
