# M5-R4 Validation / M5-R4 검증 근거

**Status / 상태:** `VALIDATED — BOUNDED / 제한 범위 검증 완료`

**Date / 날짜:** 2026-09-12

## 1. Verdict / 판정

M5-R4 has executable evidence that MUSICA can compare two renderer outputs derived from the **same exact canonical Music IR** for technical validity and a frozen objective signal-descriptor set while preserving source/provenance authority, native-format differences, explicit confounds, reproducibility evidence and a fail-closed perceptual-claim boundary.

M5-R4는 **동일한 정확한 canonical Music IR**에서 파생된 두 renderer 출력을 기술 유효성과 고정된 객관 신호 지표 집합으로 비교할 수 있음을 실행 근거로 검증했습니다. source/provenance 권한, native format 차이, 명시적 confound, 재현성 근거, fail-closed 청감 주장 경계를 보존합니다.

Validated result class / 검증 결과 등급:

```text
COMPARABLE_OBJECTIVE_ONLY
```

This does **not** establish that either renderer sounds better to humans.

## 2. Governing repository evidence / 지배 레포 근거

### Contract phase / 계약 단계

- Issue `#46` — M5-R4A Comparative Audio Evaluation Contract v0 — **COMPLETED**
- PR `#47` — **MERGED**
- contract exact head: `7aaedd273ef2d9b4908324537889da29e8f4a9eb`
- contract MUSICA CI run: `34672590806` — **SUCCESS**
- contract merge: `fa8244009fde4c7a8968f775a000bfe1596b8b83`
- normative contract: `docs/M5_R4_EVALUATION_CONTRACT.md`
- acceptance contract: `docs/M5_R4_ACCEPTANCE.md`
- machine contract: `schemas/audio-comparison-result-v0.schema.json`

### Implementation phase / 구현 단계

- Issue `#48` — M5-R4B Controlled Paired Render Evaluation v0
- PR `#49` — **MERGED**
- first evidence-bearing head: `3f4f6bb31bc077ae7f018ad128353896b02ba6ad`
- first PR M5-R4 evidence run: `34673146578` — **SUCCESS**
- first PR full MUSICA CI: `34673146596` — **SUCCESS**
- first PR M5-R3 regression: `34673146605` — **SUCCESS**
- durable-evidence exact head: `818886a2834285dabdb5874a58f62606af0d2df7`
- final M5-R3 regression run: `34673317011` — **SUCCESS**
- final M5-R4 paired evidence run: `34673317029` — **SUCCESS**
- final full MUSICA CI run: `34673317078` — **SUCCESS**
- implementation merge: `34b54ce2cd30347a4d82868dde7ccbf886f51432`

The final exact head includes this durable evidence and passed all required merge gates before merge.

최종 exact head에는 본 durable evidence가 포함되어 있으며 병합 전 모든 필수 gate를 통과했습니다.

## 3. Final regression gate / 최종 회귀 gate

The durable-evidence exact head kept green:

- Python 3.11 full repository suite — **SUCCESS**
- Python 3.12 full repository suite + prior evidence chain — **SUCCESS**
- M4-R3 real Chromium E2E — **SUCCESS**
- M5-R2 real Windows FluidSynth evidence — **SUCCESS**
- M5-R3 DAWproject evidence — **SUCCESS**
- M5-R4 paired Windows evidence — **SUCCESS**

No completion claim relies only on workflow configuration; the executable runs and uploaded evidence artifacts were inspected.

## 4. Initial controlled pair / 초기 통제 pair

Canonical source fixture:

- project: `MUSICA-M0-DEMO-001`
- accepted Blueprint revision: `rev-001`
- Blueprint SHA-256: `085d44ac294631e0816b6cb3e58bc5d616b29dec408f867633506e83a2f7222b`
- canonical Music IR SHA-256: `f28fd7f9268f1ff043f90988bb33800d95fce494cd0cc68c4265a6d8e0abc83d`
- target duration: `20.0 s`
- input Music IR unchanged after all renders: **true**

The same serialized Music IR was supplied to both renderer paths inside one Windows evidence job.

## 5. Renderer A — reference / Renderer A — reference

- renderer: `musica-reference-local`
- output: PCM WAV
- sample rate: `22,050 Hz`
- channels: `1 / mono`
- bit depth: `16-bit`
- duration: `20.0 s`
- WAV SHA-256: `e049e83bdda5a1c5710bd4d09b3010ab414d27d5a6705398aae120ae9deac5b8`
- WAV size: `882,044 bytes`
- required AudioQualityReport accepted by comparability gate

## 6. Renderer B — FluidSynth / Renderer B — FluidSynth

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
- renderer-level duration normalization: existing `trim_tail_to_requested_duration_v0`, recorded in provenance
- required AudioQualityReport accepted by comparability gate

## 7. Frozen comparison policy / 고정 비교 정책

Analyzer:

- ID: `musica-audio-compare`
- version: `0.1.0`
- observed NumPy: `2.5.3`
- policy: `musica-objective-audio-comparison-v0`

```text
sample domain              = native PCM → full-scale-normalized float64
comparison resampling      = NONE
comparison gain matching   = NONE
comparison time stretching = NONE
spectral channel policy    = arithmetic channel mean
spectral window            = Hann / 50 ms
spectral overlap           = 50%
frequency floor            = 20 Hz
common pair ceiling        = 9922.5 Hz
silence threshold          = -80 dBFS
```

No comparison-time audio artifact is synthesized or substituted for the raw evidence WAVs.

## 8. Objective result / 객관 결과

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

## 9. Explicit confounds / 명시적 confound

The report preserves instead of hiding:

- `CHANNEL_LAYOUT_DIFFERENCE` — mono vs stereo — `RECORDED`
- `SAMPLE_RATE_DIFFERENCE` — `22,050 Hz` vs `48,000 Hz` — `RECORDED`
- `RENDERER_LEVEL_DURATION_NORMALIZATION` — validated FluidSynth tail trim remains visible — `RECORDED`
- `DEFAULT_EFFECT_OR_REVERB_DIFFERENCE` — renderer-internal contribution not independently isolated — `UNKNOWN`

These facts constrain interpretation and are not silently removed by preprocessing.

## 10. Negative authority proof / 음성 권한 증명

The bounded authority layer proves fail-closed behavior:

- different Music IR source → `NOT_COMPARABLE` — **PASS**
- Blueprint binding mismatch → `NOT_COMPARABLE` — **PASS**
- failed required AudioQualityReport → `NOT_COMPARABLE` — **PASS**
- missing required FluidSynth content provenance → `NOT_COMPARABLE` — **PASS**
- raw artifact hash tamper → `NOT_COMPARABLE` — **PASS**
- attempted perceptual-superiority schema tamper → **REJECTED**
- hidden comparison resampling/gain matching under v0 contract → **REJECTED**

The dedicated workflow executed **16 bounded contract/analyzer tests successfully** on Windows.

## 11. Reproducibility / 재현성

The evidence job independently rendered and analyzed the pair twice.

- reference WAV A/B SHA-256 identity: **true**
- FluidSynth WAV A/B SHA-256 identity: **true**
- objective metrics and paired deltas identity: **true**
- canonical comparison JSON A/B identity: **true**
- comparison A SHA-256: `cb480c03fef734148592d6aeb60049836837371880bfe2e978f03b69493c3343`
- comparison B SHA-256: `cb480c03fef734148592d6aeb60049836837371880bfe2e978f03b69493c3343`

This proves reproducibility only for the exact observed Windows/runtime/content/config/policy boundary, not universal cross-platform byte identity.

## 12. Final exact-head evidence artifact / 최종 exact-head 근거 artifact

Durable-evidence exact head:

- head: `818886a2834285dabdb5874a58f62606af0d2df7`
- workflow run: `34673317029`
- artifact: `musica-m5-r4-paired-audio`
- artifact ID: `10291277918`
- artifact ZIP size: `6,189,149 bytes`
- GitHub artifact digest: `sha256:3dd97cc99907ce8bba460981be9530e4983cd5d1899a835208b45e0f9316b111`
- canonical comparison SHA-256: `cb480c03fef734148592d6aeb60049836837371880bfe2e978f03b69493c3343`
- implementation merge: `34b54ce2cd30347a4d82868dde7ccbf886f51432`

The ZIP digest is packaging evidence; canonical comparison/artifact hashes are the semantic and reproducibility evidence.

## 13. Claim boundary / 주장 경계

Every accepted M5-R4-v0 result remains constrained to:

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
- generalization from one dark-electronic fixture to all music;
- a renderer ranking suitable for marketing claims;
- that higher sample rate or stereo output alone means higher perceptual quality.

## 14. Closure / 종결

PR `#49` was merged only after the durable-evidence exact head passed all required regression and paired-evidence gates. M5-R4 is therefore **VALIDATED — BOUNDED** in canonical repository state. Any future human-listener study must be recorded separately and must not retroactively reinterpret this objective-only evidence as perceptual evidence.

PR `#49`는 durable-evidence exact head가 모든 필수 회귀 및 paired-evidence gate를 통과한 뒤에만 병합되었습니다. 따라서 M5-R4는 공식 레포 상태에서 **VALIDATED — BOUNDED**입니다. 향후 인간 청취자 연구는 별도 근거로 기록해야 하며 본 객관 근거를 청감 근거로 소급 해석해서는 안 됩니다.
