# M5-R4 Acceptance / M5-R4 수용 계약

**Status / 상태:** `PROPOSED — M5-R4A CONTRACT`

## 1. Mission / 미션

M5-R4 validates a bounded renderer-comparison framework that can truthfully describe technical validity and objective signal differences while keeping unsupported perceptual claims `UNKNOWN`.

M5-R4는 renderer 간 기술 유효성과 객관적 신호 차이를 진실하게 기술할 수 있는 제한 비교 프레임워크를 검증하되, 근거 없는 청감 우월성 주장은 `UNKNOWN`으로 유지합니다.

## 2. Required phase discipline / 필수 단계 규율

```text
M5-R4A contract/specification
→ exact-head CI
→ merge
→ fresh M5-R4B implementation branch
→ paired render/analyzer implementation
→ tests + evidence
→ durable validation
→ exact-head CI
→ merge
→ state-only closure
```

R4A does not validate comparison execution. It freezes the authority, metric, normalization, comparability and claim contracts that R4B must satisfy.

## 3. R4A acceptance / R4A 수용 조건

M5-R4A may merge only when repository evidence shows:

1. a normative evaluation contract exists;
2. a normative acceptance contract exists;
3. a machine-readable comparison-result schema exists and is Draft 2020-12 valid;
4. the schema cannot encode a v0 human-preference/superiority claim;
5. a valid contract fixture passes schema validation;
6. an invalid perceptual-superiority fixture fails closed;
7. a comparison marked `COMPARABLE` cannot simultaneously declare source-hash mismatch or failed required QA in the schema contract;
8. the exact objective metric vocabulary, units and formulas are frozen;
9. raw artifacts are explicitly separated from any comparison-time transform;
10. v0 explicitly performs no hidden resampling, gain matching, time stretching or loudness normalization;
11. mono/stereo and sample-rate differences are recorded rather than erased;
12. M5-R1/M5-R2/M5-R3 claim boundaries remain intact;
13. all existing repository CI remains green on the exact R4A PR head.

## 4. M5-R4B executable acceptance / M5-R4B 실행 수용 조건

After R4A is merged, M5-R4B must prove at least the following before M5-R4 can close.

### Gate A — exact source binding

- one accepted Blueprint revision/hash;
- one canonical Music IR SHA-256;
- both renderer requests/results bind that exact Music IR;
- a deliberate different-source negative case yields `NOT_COMPARABLE`.

### Gate B — renderer provenance

Each side records:

- adapter ID/version;
- runtime/executable identity where applicable;
- external content identity/hash where applicable;
- canonical renderer config/hash;
- raw artifact hash/size;
- AudioQualityReport identity/status.

Missing required provenance must fail closed to `NOT_COMPARABLE`.

### Gate C — same controlled execution origin

For the initial pair, both render paths should execute in the same Windows CI job from the same checked-out repository state and same serialized Music IR whenever technically practical.

If not, a hash-bound handoff and explicit environment confound are required.

### Gate D — technical QA

- each artifact is valid PCM WAV under M5-R1 QA;
- neither required QA status is `FAIL`;
- target duration and final analysis window are equivalent and unambiguous;
- raw artifact hashes remain immutable.

### Gate E — no hidden comparison normalization

Initial v0 comparison performs no:

- resampling;
- gain/loudness matching;
- padding;
- time stretching;
- undocumented trimming;
- channel-count conversion of the raw evidence artifact.

Any renderer-level normalization already used by a validated renderer remains visible in provenance.

### Gate F — objective analyzer

The implementation measures the frozen v0 metric set:

- `rms_dbfs`;
- `peak_dbfs`;
- `crest_factor_db`;
- `silence_ratio`;
- `dc_offset_normalized`;
- `stereo_correlation` where applicable;
- `stereo_difference_rms_dbfs` where applicable;
- `spectral_centroid_hz`;
- `spectral_rolloff_95_hz`;
- low/mid/high band-energy ratios.

Metrics must use the methods in `docs/M5_R4_EVALUATION_CONTRACT.md`.

### Gate G — common spectral support

Both artifacts use the same pair-level physical frequency ceiling:

```text
min(10000 Hz, 0.45 * min(sample_rate_a, sample_rate_b))
```

No claim may compare spectral descriptors calculated over different frequency support.

### Gate H — metric provenance

The report records:

- analyzer ID/version;
- metric policy version;
- analysis window policy;
- silence threshold;
- spectral window/overlap/window function;
- frequency floor/ceiling;
- metric status and unit.

### Gate I — paired deltas

For metrics measured on both sides using the same method/unit, record:

```text
delta_b_minus_a = B - A
```

Unavailable stereo-only metrics for the mono side must remain `NOT_APPLICABLE` rather than fabricated.

### Gate J — confound visibility

At minimum classify relevant:

- sample-rate difference;
- channel-layout difference;
- bit-depth difference;
- renderer-level duration normalization;
- runtime OS difference;
- default effect/reverb difference if known;
- nondeterminism;
- missing/unknown renderer behavior.

### Gate K — claim boundary

Every v0 execution report must state:

```text
HUMAN_SUBJECT_EVIDENCE = NOT_VALIDATED
PERCEPTUAL_SUPERIORITY = UNKNOWN
HUMAN_PREFERENCE_CLAIM_ALLOWED = false
```

No machine-derived field may contain `BETTER`, `WORSE`, `SUPERIOR`, or equivalent renderer preference semantics as a verdict.

### Gate L — negative cases

Tests must prove `NOT_COMPARABLE` or fail closed when:

- Music IR hashes differ;
- one required QA report is `FAIL`;
- source/revision identity is missing;
- required runtime/content/config provenance is missing;
- target duration/window differs ambiguously;
- comparison transform is applied but not recorded;
- source Blueprint/revision is silently substituted;
- result schema is tampered into a perceptual superiority claim.

### Gate M — reproducibility

At least one exact M5-R4 execution shall be independently repeated under the pinned environment and comparison-result canonical hashes/metric values shall be checked under a documented tolerance/reproducibility policy.

### Gate N — regressions

The evidence-bearing exact PR head must keep green:

- Python 3.11 full repository suite;
- Python 3.12 full repository suite and prior evidence chain;
- M4-R3 Chromium regression;
- M5-R2 Windows FluidSynth evidence;
- M5-R3 DAWproject evidence;
- new M5-R4 paired-comparison evidence job.

## 5. Initial pair acceptance / 초기 pair 수용

Initial evidence target:

```text
source: dark-electronic canonical fixture
canonical Music IR: exact hash-bound source
A: musica-reference-local
B: musica-fluidsynth-local + pinned FluidR3_GM 3.1
```

Known raw-format differences are expected:

- A: 22,050 Hz, mono, 16-bit PCM;
- B: 48,000 Hz, stereo, 16-bit PCM.

Those differences do not authorize preprocessing them away. They must be measured and recorded under the R4 contract.

## 6. Allowed M5-R4 closure claim / 허용 종결 주장

If all gates pass without human listening evidence, M5-R4 may claim only:

> MUSICA can reproducibly compare two exact-source renderer outputs for technical validity and bounded objective signal descriptors while preserving provenance, confounds and perceptual-claim boundaries.

It may **not** claim one renderer sounds better to humans.

## 7. Non-goals / 비목표

M5-R4-v0 does not validate:

- universal audio quality;
- mastering quality;
- listener preference;
- ABX significance;
- psychoacoustic transparency;
- generalization from one fixture to all music;
- renderer ranking for product marketing;
- live OpenAI execution;
- a new renderer backend.
