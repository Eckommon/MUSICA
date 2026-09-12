# M5-R4 Validation / M5-R4 검증 근거

**Status / 상태:** `VALIDATED — BOUNDED ON EVIDENCE-BEARING PR HEAD / 근거 포함 PR head에서 제한 범위 검증 완료`

**Date / 날짜:** 2026-09-12

## 1. Verdict / 판정

M5-R4 has executable evidence that MUSICA can compare two renderer outputs derived from the **same exact canonical Music IR** for technical validity and the frozen set of objective signal descriptors while preserving source/provenance authority, native-format differences, explicit confounds, reproducibility evidence and a fail-closed perceptual-claim boundary.

M5-R4는 **동일한 정확한 canonical Music IR**에서 파생된 두 renderer 출력을 기술 유효성과 고정된 객관 신호 지표 집합으로 비교할 수 있음을 실행 근거로 검증했습니다. 이 과정에서 source/provenance 권한, native format 차이, 명시적 confound, 재현성 근거, fail-closed 청감 주장 경계를 보존합니다.

The validated claim is deliberately limited to:

> **COMPARABLE_OBJECTIVE_ONLY**

The evidence does **not** establish that either renderer sounds better to humans.

검증된 주장은 의도적으로 `COMPARABLE_OBJECTIVE_ONLY`에 제한됩니다. 어느 renderer가 인간에게 더 좋게 들리는지는 검증하지 않았습니다.

## 2. Governing repository evidence / 지배 레포 근거

### Contract phase / 계약 단계

- Issue `#46` — M5-R4A Comparative Audio Evaluation Contract v0 — **COMPLETED**
- contract PR `#47`
- contract exact head: `7aaedd273ef2d9b4908324537889da29e8f4a9eb`
- contract MUSICA CI: `34672590806` — **SUCCESS**
- contract M5-R3 regression: `34672590824` — **SUCCESS**
- contract merge: `fa8244009fde4c7a8968f775a000bfe1596b8b83`
- normative contract: `docs/M5_R4_EVALUATION_CONTRACT.md`
- normative acceptance: `docs/M5_R4_ACCEPTANCE.md`
- machine contract: `schemas/audio-comparison-result-v0.schema.json`

### Implementation phase / 구현 단계

- Issue `#48` — M5-R4B Controlled Paired Render Evaluation v0 — **OPEN until merge/closure**
- implementation PR `#49`
- first evidence-bearing PR head: `3f4f6bb31bc077ae7f018ad128353896b02ba6ad`
- M5-R4 paired evidence run: `34673146578` — **SUCCESS**
- MUSICA full CI run: `34673146596` — **SUCCESS**
- M5-R3 DAWproject regression run: `34673146605` — **SUCCESS**

Full MUSICA CI on the evidence-bearing head kept green:

- Python 3.11 full repository suite — **SUCCESS**
- Python 3.12 full repository suite + prior evidence chain — **SUCCESS**
- M4-R3 real Chromium E2E — **SUCCESS**
- M5-R2 real Windows FluidSynth evidence — **SUCCESS**
- M5-R3 DAWproject evidence — **SUCCESS**

A final exact-head rerun after this durable evidence is committed remains required before merge. This document records the already-observed executable validation and does not pre-authorize merge if that final rerun regresses.

이 durable evidence가 포함된 새 exact head에서 최종 재실행을 한 번 더 통과해야 병합할 수 있습니다. 본 문서는 이미 관측된 실행 검증을 기록하며 최종 재검증 실패 시 병합을 허용하지 않습니다.

## 3. Initial controlled pair / 초기 통제 pair

Canonical source fixture:

- project: `MUSICA-M0-DEMO-001`
- accepted Blueprint revision: `rev-001`
- Blueprint SHA-256: `085d44ac294631e0816b6cb3e58bc5d616b29dec408f867633506e83a2f7222b`
- canonical Music IR SHA-256: `f28fd7f9268f1ff043f90988bb33800d95fce494cd0cc68c4265a6d8e0abc83d`
- target duration: `20.0 s`
- input Music IR unchanged after all renders: **true**

The exact same serialized Music IR was supplied to both existing renderer paths within one Windows evidence job.

동일하게 직렬화된 Music IR이 하나의 Windows evidence job 안에서 두 기존 renderer 경로 모두에 전달되었습니다.

## 4. Renderer A — reference / Renderer A — reference

- renderer: `musica-reference-local`
- output: PCM WAV
- sample rate: `22,050 Hz`
- channels: `1 / mono`
- bit depth: `16-bit`
- duration: `20.0 s`
- WAV SHA-256: `e049e83bdda5a1c5710bd4d09b3010ab414d27d5a6705398aae120ae9deac5b8`
- WAV size: `882,044 bytes`
- AudioQualityReport: accepted by comparability gate

## 5. Renderer B — FluidSynth / Renderer B — FluidSynth

- renderer: `musica-fluidsynth-local`
- FluidSynth observed version: `2.6.0`
- FluidSynth executable SHA-256: `08c72384a47f67b0c5be9ee8c88b1f0b6afe39a8217ed2adb83a88b41c051632`
- FluidSynth source archive SHA-256: `817262deacaa748edb3af6731dffe1766b00146790becfccc949a9f701e76681`
- external content: `FluidR3_GM-3.1`
- SoundFont SHA-256: `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`
- SoundFont source archive SHA-256: `2621acaa1c78e4abdb24bdd163230cc577e61276936d6aa6e3180582142f0343`
- SoundFont size: `148,398,306 bytes`
- SoundFont normal-Git inclusion: **false**
- output: PCM WAV
- sample rate: `48,000 Hz`
- channels: `2 / stereo`
- bit depth: `16-bit`
- duration: `20.0 s`
- WAV SHA-256: `e054ad9cb7d938f50f75d222c1522e71cc7a7f163e8ea7bf3f8dceec628bcfa3`
- WAV size: `3,840,044 bytes`
- renderer-level duration normalization: existing validated `trim_tail_to_requested_duration_v0` policy remains visible in provenance
- AudioQualityReport: accepted by comparability gate

## 6. Comparison policy / 비교 정책

Analyzer:

- ID: `musica-audio-compare`
- version: `0.1.0`
- observed NumPy: `2.5.3`
- policy: `musica-objective-audio-comparison-v0`

Frozen policy:

```text
sample domain             = native PCM → full-scale-normalized float64
comparison resampling     = NONE
comparison gain matching  = NONE
comparison time stretching= NONE
spectral channel policy   = arithmetic channel mean
spectral window           = Hann / 50 ms
spectral overlap          = 50%
frequency floor           = 20 Hz
common pair ceiling       = 9922.5 Hz
silence threshold         = -80 dBFS
```

No comparison-time audio artifact is synthesized or substituted for the raw evidence WAVs.

비교를 위해 raw evidence WAV를 대체하는 재샘플링·gain matching·time stretching 등의 새 오디오 artifact를 만들지 않습니다.

## 7. Objective result / 객관 결과

The initial controlled pair produced the following frozen objective descriptors.

초기 통제 pair의 고정 객관 지표 결과는 다음과 같습니다.

| Descriptor / 지표 | Reference A | FluidSynth B | B − A |
|---|---:|---:|---:|
| RMS | `-31.803804307 dBFS` | `-41.076115094 dBFS` | `-9.272310787` |
| Peak | `-17.686213694 dBFS` | `-21.443738950 dBFS` | `-3.757525256` |
| Crest factor | `14.117590613 dB` | `19.632376144 dB` | `+5.514785531` |
| Silence ratio | `0.183448980` | `0.013163542` | `-0.170285438` |
| DC offset | `-0.000008868` | `-0.000518537` | `-0.000509669` |
| Spectral centroid | `265.398918183 Hz` | `507.141072434 Hz` | `+241.742154251 Hz` |
| Spectral rolloff 95% | `460.208711434 Hz` | `2640.0 Hz` | `+2179.791288566 Hz` |
| Low-band ratio | `0.411622766` | `0.675357185` | `+0.263734419` |
| Mid-band ratio | `0.588218572` | `0.296053948` | `-0.292164624` |
| High-band ratio | `0.000158662` | `0.028588867` | `+0.028430205` |
| Stereo correlation | `NOT_APPLICABLE` | `0.141025982` | `NOT_APPLICABLE` |
| Stereo difference RMS | `NOT_APPLICABLE` | `-44.761599872 dBFS` | `NOT_APPLICABLE` |

**No sign, magnitude or metric is interpreted as `BETTER`, `WORSE` or human preference.**

**어떤 부호·크기·지표도 `BETTER`, `WORSE` 또는 인간 선호로 해석하지 않습니다.**

## 8. Explicit confounds / 명시적 confound

The comparison report preserves instead of hiding:

- `CHANNEL_LAYOUT_DIFFERENCE` — Reference mono vs FluidSynth stereo — `RECORDED`
- `SAMPLE_RATE_DIFFERENCE` — `22,050 Hz` vs `48,000 Hz` — `RECORDED`
- `RENDERER_LEVEL_DURATION_NORMALIZATION` — FluidSynth validated tail trim remains visible — `RECORDED`
- `DEFAULT_EFFECT_OR_REVERB_DIFFERENCE` — renderer-internal contribution not independently isolated — `UNKNOWN`

These facts limit interpretation. They are not silently removed by preprocessing.

이 요소들은 해석의 한계를 정의하며 전처리로 조용히 제거하지 않습니다.

## 9. Negative authority proof / 음성 권한 증명

The evidence suite proves fail-closed behavior for the bounded authority layer:

- different Music IR source → `NOT_COMPARABLE` — **PASS**
- Blueprint binding mismatch → `NOT_COMPARABLE` — **PASS in unit test**
- failed required AudioQualityReport → `NOT_COMPARABLE` — **PASS**
- missing required FluidSynth content provenance → `NOT_COMPARABLE` — **PASS**
- raw artifact hash tamper → `NOT_COMPARABLE` — **PASS in unit test**
- attempted perceptual-superiority schema tamper → **REJECTED**
- hidden comparison resampling/gain matching in v0 contract → **REJECTED by contract tests**

The M5-R4 dedicated workflow executed **16 bounded contract/analyzer tests successfully** on Windows.

## 10. Reproducibility / 재현성

The exact evidence job independently rendered and analyzed the pair twice.

Results:

- reference WAV A/B SHA-256 identity: **true**
- FluidSynth WAV A/B SHA-256 identity: **true**
- objective metric values and paired deltas identity: **true**
- canonical comparison JSON A/B identity: **true**
- comparison A SHA-256: `cb480c03fef734148592d6aeb60049836837371880bfe2e978f03b69493c3343`
- comparison B SHA-256: `cb480c03fef734148592d6aeb60049836837371880bfe2e978f03b69493c3343`

This proves reproducibility for the exact observed Windows/runtime/content/config/policy boundary. It does not claim universal cross-platform byte identity.

이는 관측된 정확한 Windows/runtime/content/config/policy 경계에서의 재현성을 증명합니다. 모든 OS·환경에서의 보편적 byte identity를 주장하지 않습니다.

## 11. PR evidence artifact / PR 근거 artifact

Evidence-bearing PR head:

- head: `3f4f6bb31bc077ae7f018ad128353896b02ba6ad`
- workflow run: `34673146578`
- artifact: `musica-m5-r4-paired-audio`
- artifact ID: `10291367529`
- artifact ZIP size: `6,189,149 bytes`
- GitHub artifact digest: `sha256:aa0ef19bc3f0ba1c453eab168c398a7d582bef2cbd3b2a781628de5f52fdbcba`
- `comparison-a.json` SHA-256: `cb480c03fef734148592d6aeb60049836837371880bfe2e978f03b69493c3343`
- `comparison-b.json` SHA-256: same
- `proof.json` SHA-256: `3047fe7de1f42ef0b6d766d11c29b8478dc80b1d636f05d517b0c697880cf158`

The ZIP container digest is packaging evidence; the canonical comparison and included artifact hashes are the semantic/reproducibility evidence.

## 12. Claim boundary / 주장 경계

Every accepted M5-R4-v0 result is constrained to:

```text
HUMAN_SUBJECT_EVIDENCE = NOT_VALIDATED
PERCEPTUAL_SUPERIORITY = UNKNOWN
HUMAN_PREFERENCE_CLAIM_ALLOWED = false
```

Therefore M5-R4 does **not** validate or imply:

- that FluidSynth sounds better than the reference renderer;
- that the reference renderer sounds better than FluidSynth;
- a universal audio-quality score;
- mastering/professional audio quality;
- listener preference;
- ABX significance;
- psychoacoustic transparency;
- generalization from the single dark-electronic fixture to all music;
- a renderer ranking suitable for marketing claims;
- that higher sample rate or stereo output alone means higher perceptual quality.

## 13. Bounded completion rule / 제한 완료 규칙

M5-R4 implementation may be merged only after this evidence-bearing head (or its exact successor containing only this durable evidence/runtime-status update) passes again:

- Python 3.11 full suite;
- Python 3.12 full suite and prior evidence chain;
- M4-R3 Chromium;
- M5-R2 Windows FluidSynth;
- M5-R3 DAWproject;
- M5-R4 paired Windows evidence.

After implementation merge, canonical `CURRENT_STATE`, README and `NEXT_ACTION` must be reconciled in a separate state-only closure before Issue #48 is closed.
