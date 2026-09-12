# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M5-R4B — CONTROLLED PAIRED RENDER EVALUATION v0 / M5-R4B — 통제된 쌍대 렌더 평가 v0**

M5-R3 is `VALIDATED — BOUNDED`. M5-R4A defines the comparison authority, objective metric vocabulary, normalization limits, comparability gate and claim boundary. Once the M5-R4A contract PR is merged, the next task is **implementation and evidence**, not another broad metric brainstorm.

M5-R3는 `VALIDATED — BOUNDED`입니다. M5-R4A는 비교 권한, 객관 지표 어휘, normalization 한계, comparability gate, claim boundary를 정의합니다. M5-R4A 계약 PR이 병합되면 다음 작업은 추가 지표 브레인스토밍이 아니라 **구현과 근거 생성**입니다.

Governing Issue / 지배 Issue:

- `#46 — M5-R4A — Comparative Audio Evaluation Contract v0`

Normative M5-R4 contract / 규범 계약:

- `docs/M5_R4_EVALUATION_CONTRACT.md`
- `docs/M5_R4_ACCEPTANCE.md`
- `schemas/audio-comparison-result-v0.schema.json`

## Do not reopen the contract casually / 계약을 임의 재개하지 말 것

The following are frozen for the first bounded implementation unless contradictory execution evidence requires a contract amendment:

- objective metric set;
- no comparison-time resampling;
- no gain/loudness matching;
- no time stretching;
- raw artifact preservation;
- common physical spectral frequency support;
- same-source Music IR authority;
- no human-preference inference from machine metrics.

## Initial controlled pair / 초기 통제 pair

Use the existing dark-electronic canonical fixture:

```text
same accepted Blueprint revision
→ same exact canonical Music IR SHA-256
├─ A: musica-reference-local
│    22,050 Hz / mono / 16-bit PCM
└─ B: musica-fluidsynth-local
     FluidSynth 2.6.0 + exact-hash FluidR3_GM 3.1
     48,000 Hz / stereo / 16-bit PCM
```

The first implementation SHOULD render both A and B in the same Windows CI job from the same checkout and serialized Music IR. This avoids turning environment drift into an untracked confound.

## M5-R4B implementation package / 구현 패키지

Create a fresh branch from the merged M5-R4A main, preferably:

```text
m5-r4b-paired-audio-evaluation-v0
```

Implement responsibility boundaries along these lines:

```text
src/musica/audio_compare.py
  - normalized PCM loading
  - time-domain metrics
  - spectral metrics
  - pair comparability validation
  - paired delta construction
  - machine result generation

src/musica/m5_r4_demo.py
  - exact-source compile/render orchestration
  - reference + FluidSynth paired execution
  - evidence manifest/report generation

tests/test_m5_r4_audio_compare.py
  - metric unit tests
  - source mismatch negative
  - QA FAIL negative
  - missing provenance negative
  - normalization-policy negative
  - perceptual-claim tamper negative
  - deterministic/reproducibility checks

.github/workflows/m5-r4-evidence.yml
  - Windows paired execution
  - exact FluidSynth/SoundFont provisioning reused from M5-R2
  - both renderers in one job
  - upload bounded evidence artifact
```

Exact filenames may change if a cleaner structure is justified, but the responsibility split must stay inspectable.

## Dependency policy / 의존성 정책

M5-R4B may add **NumPy only if needed for deterministic FFT/vector analysis**.

Do not introduce SciPy, librosa, a perceptual foundation model, or a heavy ML stack merely to produce a quality score.

If NumPy is added:

- pin a bounded compatible version range;
- record the observed version in evidence;
- keep formulas/policies in MUSICA-owned code;
- do not outsource claim semantics to library defaults.

## Frozen objective metric set / 고정 객관 지표

Implement exactly the v0 set from `docs/M5_R4_EVALUATION_CONTRACT.md`:

1. RMS dBFS;
2. peak dBFS;
3. crest factor dB;
4. silence ratio at `-80 dBFS` frame threshold;
5. normalized DC offset;
6. stereo correlation when applicable;
7. stereo difference RMS dBFS when applicable;
8. spectral centroid Hz;
9. spectral rolloff 95% Hz;
10. low-band energy ratio `20–250 Hz`;
11. mid-band energy ratio `250–4000 Hz`;
12. high-band energy ratio `4000 Hz–pair ceiling`.

Spectral policy:

```text
channel projection = arithmetic channel mean
window             = Hann
window duration    = 50 ms
hop                 = 50% overlap
frequency floor     = 20 Hz
pair ceiling        = min(10000 Hz, 0.45 * min(sr_a, sr_b))
comparison resample = NONE
```

## Comparability authority / 비교 가능성 권한

A pair can become `COMPARABLE` only when all required source/QA/provenance/duration gates pass.

At minimum fail closed to `NOT_COMPARABLE` when:

- Music IR hashes differ;
- Blueprint/source binding differs unexpectedly;
- required AudioQualityReport is `FAIL`;
- required runtime/content/config provenance is absent;
- target duration or analysis window is ambiguous;
- a hidden comparison transform is attempted;
- raw artifacts are replaced by normalized artifacts;
- result contract is tampered to claim perceptual superiority.

## Claim boundary / 주장 경계

Every M5-R4-v0 report SHALL retain:

```text
HUMAN_SUBJECT_EVIDENCE = NOT_VALIDATED
PERCEPTUAL_SUPERIORITY = UNKNOWN
HUMAN_PREFERENCE_CLAIM_ALLOWED = false
```

Do not use `BETTER`, `WORSE`, `SUPERIOR`, or an equivalent preference verdict.

## Evidence target / 근거 목표

M5-R4B should produce an artifact package containing at least:

- frozen canonical Music IR bytes/hash;
- renderer A request/result/QA and raw WAV;
- renderer B request/result/QA and raw WAV;
- comparison JSON validated by `audio-comparison-result-v0.schema.json`;
- analyzer policy/version;
- objective metric values and deltas;
- confound records;
- negative-case results;
- reproducibility result;
- top-level evidence manifest with SHA-256 for every included artifact.

Large external SoundFont content remains outside normal Git.

## Required merge gate / 필수 병합 gate

M5-R4B cannot merge until the evidence-bearing exact head passes:

- Python 3.11 full suite;
- Python 3.12 full suite and prior evidence chain;
- M4-R3 Chromium regression;
- M5-R2 Windows FluidSynth evidence;
- M5-R3 DAWproject evidence;
- M5-R4 paired Windows evidence workflow;
- durable `evidence/M5_R4_VALIDATION.md` on the exact PR head.

## Completion claim / 완료 주장

Without human-subject evidence, successful M5-R4 may claim only:

> MUSICA can reproducibly compare two exact-source renderer outputs for technical validity and bounded objective signal descriptors while preserving provenance, confounds and perceptual-claim boundaries.

It may not claim one renderer sounds better to humans.

## Non-goals / 비목표

Do not add in M5-R4B:

- a new renderer backend;
- a universal quality score;
- LUFS just to force a ranking;
- subjective LLM scoring presented as listening evidence;
- ABX significance without an actual study;
- optimization of music generation to game selected metrics;
- product marketing claims from a single fixture.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
