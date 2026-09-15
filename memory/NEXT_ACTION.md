# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M7-R4 — REFERENCE RENDERER AUTOMATION MAPPING & AUDIBLE EVIDENCE**

M7-R3 is `VALIDATED — BOUNDED DERIVED EXECUTION`. The next mission is to prove one explicit canonical automation parameter can be applied audibly by one explicit renderer policy **without granting renderer state canonical authority or silently reusing MIDI CC semantics**.

## Canonical starting point / 공식 시작점

- M7-R3 Issue `#77` — **COMPLETED**
- M7-R3 PR `#78` — **MERGED**
- implementation merge/main: `f4dbbf78c1556815228ef1446192a1308707eec9`
- pre-durable exact head: `09eaa538128a302f82374764becf1ddfc87eafda`
- final evidence-bearing successor head: `43d4568362cc26c23e9747da2a15b29c0cf4fe4d`
- successor M7-R3 workflow `34822272947` — **SUCCESS**
- successor MUSICA CI `34822272980` — **SUCCESS**
- successor M7-R2/R1/R0, M6-R4/R3/R2/R1, M5-R3/R4 — **ALL SUCCESS**
- successor artifact ID `10338193487`
- packaging SHA-256 `48b157aefb9bd6067aa7a2d4b187693294a2b7417869c35a4daa56bea5d1f61c`
- internal manifest SHA-256 `864135b90e650496e89d1e6f9b293e709f2fd187a3ddb639e155136c028207db`
- derived execution SHA-256 `2874fc72e78fd817a53ad2c20348cf56403af53fa24fdfc57f7f2aa1ac2444c7`
- manifest integrity: **10/10 exact**
- pre-durable vs successor extracted evidence: **11 files / 0 differences**
- durable evidence: `evidence/M7_R3_VALIDATION.md`

## Architecture facts R4 must respect / R4가 지켜야 할 구조 사실

### Canonical automation remains backend-independent

Canonical automation identity is:

```text
parameter_id
scope
owner_id
unit
lane_id
point_id
beat
value
interpolation
```

R3 derived execution adds deterministic ticks/segments but deliberately records:

```text
backend_mapping.status = UNMAPPED
renderer_mapping_authorized = false
audible_automation_validated = false
```

R4 must not mutate R3 execution to pretend the renderer mapping was canonical all along.

### Existing semantic CC path is unrelated authority

Current Music IR semantic controls use CC11 / CC74 / CC71 and the current reference WAV renderer interprets those values. They are existing preview semantics, not canonical M7 automation mapping authority.

Therefore this is forbidden:

```text
mix.gain == CC11 merely because CC11 already changes expression
```

R4 must create an explicit renderer-specific mapping layer instead.

## Bounded mapping selected for R4 / R4 제한 매핑

Exactly one canonical parameter family is eligible:

```text
parameter_id = mix.gain
scope        = project
owner_id     = null
unit         = normalized
minimum      = 0.0
maximum      = 1.0
renderer_id  = musica-reference-local
```

No `synth.cutoff`, part-scope automation, decibel/hertz/semitone/ratio mapping or arbitrary parameter registry expansion is required for R4.

## Required R4 design / 필수 설계

### 1. Renderer-specific derived plan

Introduce a versioned non-canonical renderer plan, recommended working name:

```text
automation-render-plan-v0
```

The plan must bind at minimum:

```text
plan_version
classification = derived_noncanonical
source.music_ir_sha256
source.automation_execution_sha256
source.project_id
source.revision_id
renderer.renderer_id
renderer.renderer_version
mapping.policy_id
mapped_lanes[]
unmapped_lanes[]
authority.*
```

The plan is generated from already-validated Music IR + already-validated R3 execution. It may not accept arbitrary free-form mappings supplied by Browser or renderer state.

### 2. Exact cross-source validation

Before mapping, fail closed unless:

```text
music_ir.source_blueprint_revision == execution.source.revision_id
music_ir.timing.ppq == execution.lowering.ppq
execution.classification == derived_noncanonical
```

Bind exact SHA-256 of both supplied objects. Recompute rather than trust caller strings.

### 3. Mapping registry

R4 registry contains one rule only:

```text
mix.gain / project / normalized
→ reference renderer post-synthesis gain envelope
```

Every other R3 lane must be carried as typed `UNMAPPED` / `UNSUPPORTED_BY_REFERENCE_RENDERER` and must never be guessed into MIDI CC or another DSP control.

### 4. Gain-envelope semantics

Use R3 point/segment semantics directly.

Recommended deterministic policy:

```text
before first point: first point value
hold segment: start value until end point tick
linear segment: linear interpolation start→end over exact tick interval
after last point: last point value
```

The envelope should be evaluated against renderer sample time using the exact fixed tempo and PPQ already present in Music IR.

### 5. Additive renderer path

Preserve existing `render_wav()` / `wav_bytes()` unchanged.

Prefer a new additive module or function, for example:

```text
src/musica/automation_renderer.py
```

or an explicit automation-aware renderer adapter path.

The new path should synthesize the same reference mix and apply the mapped gain envelope as a deterministic post-synthesis multiplier. It must not change MIDI bytes or semantic CC interpretation.

### 6. Normalization boundary

Avoid a design where final peak normalization erases the audible gain proof. The automation-aware path should make the order explicit and testable.

Recommended policy:

```text
existing deterministic synthesis/mix
→ existing safety normalization if needed
→ R4 mix.gain envelope
→ final PCM clipping guard only
```

Do not renormalize after automation gain, because that could erase the mapped amplitude relationship.

### 7. Objective audio evidence

Do not claim perceptual quality. Prove machine-observable behavior:

- baseline/no-automation WAV SHA-256;
- automated WAV SHA-256;
- repeated automated render byte identity;
- PCM sample difference count > 0 for non-unity automation;
- whole-file RMS/peak comparison;
- bounded segment/window RMS comparisons aligned to hold/linear envelope phases;
- envelope samples at deterministic probe ticks/samples;
- WAV container/QA remains valid.

Use an evidence fixture whose gain curve makes the expected direction unambiguous and avoids silence-only windows.

## Required tests / 필수 테스트

At minimum prove:

1. exact Music IR hash binding;
2. exact R3 execution hash binding;
3. revision and PPQ cross-binding;
4. only `mix.gain/project/normalized` maps;
5. `synth.cutoff` remains typed unmapped;
6. wrong scope fails mapping eligibility;
7. wrong unit fails mapping eligibility;
8. forged/tampered execution fails validation/hash binding;
9. `hold` envelope values are exact at boundary probes;
10. `linear` envelope interpolation is deterministic;
11. before-first and after-last policies are deterministic;
12. automation-aware WAV differs from baseline for non-unity curve;
13. repeated automation-aware WAV is byte-identical;
14. measurable RMS/peak windows move in expected direction;
15. source Music IR object remains unchanged;
16. source R3 execution object remains unchanged;
17. legacy/no-automation produces no mapped lane and baseline-equivalent audio;
18. existing `render_wav()` output remains unchanged;
19. existing MIDI bytes remain unchanged;
20. no Project/Blueprint mutation or reverse promotion authority;
21. R3/R2/R1/R0 remain green;
22. M6-R4/R3/R2/R1 and M5-R3/R4 remain green;
23. Python 3.11/3.12 full suite remains green.

## Expected implementation direction / 예상 구현 방향

Likely bounded package:

```text
schemas/automation-render-plan-v0.schema.json
src/musica/automation_renderer.py
tests/test_m7_r4_automation_renderer.py
src/musica/m7_r4_demo.py
.github/workflows/m7-r4-audible-automation-evidence.yml
```

Exact naming may change only when repository inspection reveals a better existing contract pattern.

## Evidence target / 공식 근거 목표

Dedicated deterministic artifact should include at minimum:

```text
source-blueprint.json or bound source hashes
music-ir.json
automation-execution.json
automation-render-plan.json
envelope-proof.json
baseline.wav
automated-a.wav
automated-b.wav
audio-difference-proof.json
authority-boundary-proof.json
manifest.json
```

The dedicated workflow should render twice and require byte-identical automated WAV/evidence where intended.

## Scope control / 범위 통제

Do **not** add or claim in M7-R4:

- canonical MIDI CC mapping for automation;
- `synth.cutoff` or arbitrary parameter mappings;
- arbitrary part-scope automation mapping;
- plug-in/device mapping or VST/AU/CLAP hosting;
- external DAW automation import/export/reconciliation;
- MIDI/OSC real-time control;
- lane creation/deletion or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential interpolation;
- Browser UI expansion;
- mastering quality or human/perceptual superiority.

## Maximum intended R4 claim / 성공 시 최대 주장

> **MUSICA can take validated source-bound automation execution for canonical `mix.gain` and, through one explicit reference-renderer mapping policy, deterministically produce audibly different WAV output whose gain-envelope effect is objectively measurable and byte-reproducible, without changing canonical authority or reusing MIDI CC as implicit automation semantics.**

## Execution discipline / 실행 규율

```text
M7-R3 state closure
→ create M7-R4 Issue
→ fresh branch from closure main
→ ratify renderer-plan contract
→ bounded mix.gain mapping implementation
→ deterministic envelope/audio tests
→ dedicated audible evidence workflow
→ PR
→ exact-head full regressions
→ artifact inspection
→ durable M7_R4 validation
→ successor rerun
→ expected-head merge
→ Issue completed
→ state-only closure
```

**Repository evidence remains authoritative over conversation/model memory.**