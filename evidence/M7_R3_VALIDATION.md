# M7-R3 Validation — Deterministic Automation Lowering & Derived Execution Boundary

Status: **VALIDATION CANDIDATE — SUCCESSOR RERUN REQUIRED**

This record durably binds the pre-durable M7-R3 evidence-bearing head. It does **not** by itself promote M7-R3; promotion requires the same full regression set and byte-reproducible R3 evidence to succeed again on the successor exact head containing this record.

## 1. Validated claim boundary

The maximum evidence-supported claim at this point is:

> MUSICA can deterministically lower accepted canonical automation into a source-bound, backend-independent, non-authoritative derived execution package that preserves stable lane/parameter/point provenance and explicit hold/linear segment semantics without silently equating canonical parameters with MIDI CC or renderer-specific addresses.

`automation-execution-v0` is an L4 compiled target package / sidecar for one exact accepted source revision. It is derived and regenerable. The accepted Music Blueprint remains canonical creative authority.

M7-R3 does **not** claim:

- audible automation rendering or audio-difference validation;
- MIDI CC mapping as canonical automation semantics;
- plug-in/device parameter mapping or VST/AU/CLAP hosting;
- DAW automation import/export/reconciliation;
- MIDI/OSC real-time control;
- lane creation/deletion or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential interpolation;
- reverse promotion from derived execution into canonical Blueprint authority;
- human-subject/perceptual evidence.

## 2. Pre-durable exact head

- branch: `m7-r3-automation-lowering`
- exact head: `09eaa538128a302f82374764becf1ddfc87eafda`
- base canonical closure main: `34d13e496e1524194bf34f82df360bb3d936165e`
- Issue: #77
- draft implementation PR: #78

## 3. Exact-head workflow evidence — 11/11 SUCCESS

All required pull-request workflows for the exact pre-durable head completed successfully:

| Workflow | Run | Result |
|---|---:|---|
| MUSICA CI | `34821937309` | SUCCESS |
| M7-R3 Automation Lowering Evidence | `34821937387` | SUCCESS |
| M7-R2 Real-Browser Automation Evidence | `34821937366` | SUCCESS |
| M7-R1 Automation Runtime Evidence | `34821937421` | SUCCESS |
| M7-R0 Automation Contract Evidence | `34821937356` | SUCCESS |
| M6-R4 Interchange Note Reconciliation | `34821937364` | SUCCESS |
| M6-R3 Real-Browser Exact-Note Evidence | `34821937312` | SUCCESS |
| M6-R2 Piano-Roll Evidence | `34821937308` | SUCCESS |
| M6-R1 Exact-Note Edit Evidence | `34821937384` | SUCCESS |
| M5-R3 DAWproject Evidence | `34821937326` | SUCCESS |
| M5-R4 Paired Audio Evidence | `34821937304` | SUCCESS |

The dedicated R3 gate first ran the M7-R0/R1/R2/R3 automation regression set, then generated evidence twice, then required `diff -qr` to report no differences before artifact upload.

The repository-wide CI also passed its Python 3.11 and Python 3.12 contract/runtime suites, Browser E2E, FluidSynth evidence and canonical prior-milestone evidence regeneration.

## 4. Deterministic artifact lineage

Artifact:

- name: `musica-m7-r3-automation-lowering-evidence`
- artifact ID: `10338124923`
- GitHub/ZIP SHA-256: `689c6a955198057328e1d631d857b4ce9c18a3cc140917c1a40b5d1befb5f816`
- internal `manifest.json` SHA-256: `864135b90e650496e89d1e6f9b293e709f2fd187a3ddb639e155136c028207db`
- manifest evidence records: **10 / 10 hash + size exact**
- source Blueprint SHA-256: `6251f252047840f32ccc41c1a821c836aadb172aafdd557af07ac09763667dd0`
- source automation-material SHA-256: `b7caa66d4d93a1e10383e579dd5966d2969e7b88d4841d31da65d302b1415c44`
- derived execution SHA-256: `2874fc72e78fd817a53ad2c20348cf56403af53fa24fdfc57f7f2aa1ac2444c7`
- `execution-a.json` SHA-256 = `execution-b.json` SHA-256 = `2874fc72e78fd817a53ad2c20348cf56403af53fa24fdfc57f7f2aa1ac2444c7`

Independent artifact inspection confirmed the GitHub digest equals the downloaded ZIP digest and every manifest record matches its extracted bytes.

## 5. Ratified derived execution model

R3 introduces:

- schema: `schemas/automation-execution-v0.schema.json`;
- lowering implementation: `src/musica/automation_lowering.py`;
- deterministic evidence generator: `src/musica/m7_r3_demo.py`;
- contract/runtime tests: `tests/test_m7_r3_automation_lowering.py`;
- dedicated workflow: `.github/workflows/m7-r3-automation-lowering-evidence.yml`.

The derived package binds:

```text
project_id
revision_id
blueprint_sha256
automation_material_sha256
explicit_automation_present
```

It records a deterministic lowering policy:

```text
compiler_id      = musica-automation-lowering
compiler_version = 0.1.0
policy_id        = automation-execution-v0-generic-segments
ppq              = 480
tick_rounding    = decimal_nearest_half_up_nonnegative
```

Beat-to-tick conversion uses Decimal arithmetic with explicit `ROUND_HALF_UP`, avoiding implicit language/runtime banker-rounding authority.

## 6. Stable provenance and interpolation proof

Every derived lane retains canonical source identity and domain metadata:

```text
lane_id
parameter_id
scope
owner_id
section_id
unit
minimum / maximum
```

Every derived point retains:

```text
point_id
beat
tick
value
interpolation
```

Each outgoing segment references the exact adjacent stable point IDs and records:

```text
start_point_id
end_point_id
start_tick / end_tick
start_value / end_value
interpolation
```

The segment interpolation is exactly the **start source point's outgoing interpolation**. Evidence includes both a `linear` segment and a `hold` segment.

Distinct canonical beats that collapse to one 480-PPQ tick fail closed rather than silently losing timing resolution.

## 7. Backend and authority boundary

Every valid canonical R3 lane is carried generically as:

```text
derivation_status = DERIVED_GENERIC
backend_mapping.status = UNMAPPED
```

R3 does not guess whether `mix.gain`, `synth.cutoff`, or any future canonical `parameter_id` should be MIDI CC, plug-in parameter, renderer address or DAW lane.

The schema uses `additionalProperties: false` at the backend mapping boundary. Independent machine proof injected `midi_cc = 11` and validation failed with an additional-property error.

The derived package explicitly records:

```text
canonical                    = false
project_mutation_authorized  = false
blueprint_mutation_authorized = false
reverse_promotion_authorized = false
renderer_mapping_authorized  = false
audible_automation_validated = false
```

## 8. Legacy and non-mutation proof

For a validated accepted Blueprint with no `materials.automation`:

- source binding uses the deterministic empty automation-material hash;
- `explicit_automation_present = false`;
- derived `lanes = []`;
- no semantic, Music IR or renderer state is reverse-inferred into canonical automation.

Evidence also confirms both explicit-automation and legacy source Blueprint bytes remain unchanged after lowering.

## 9. Existing compiler non-regression

R3 deliberately does not modify `src/musica/compiler.py`, `src/musica/render.py` or `src/musica/renderer.py`.

Machine proof compiles the same explicit-automation Blueprint before and after R3 lowering and confirms byte-identical existing Music IR. Existing semantic control events remain limited to the prior CC set `{11, 71, 74}`; R3 injects no canonical automation into that MIDI-like path.

This is intentional. A later renderer-mapping milestone must explicitly choose and validate one adapter policy rather than inheriting accidental CC semantics.

## 10. Machine proof summary

Required positive proof values are true:

- exact source binding;
- explicit-vs-legacy source distinction;
- legacy empty derived execution;
- canonical stable lane order;
- stable point provenance;
- `linear` semantics preserved;
- `hold` semantics preserved;
- deterministic tick policy recorded;
- execution bytes deterministic;
- backend mapping remains UNMAPPED;
- backend address injection rejected;
- derived state classified non-canonical;
- explicit and legacy source Blueprints unchanged;
- existing Music IR compiler output byte-identical.

Required authority/non-claim values remain false:

- legacy explicit automation present;
- project mutation authorized;
- Blueprint mutation authorized;
- reverse promotion authorized;
- renderer mapping authorized;
- audible automation validated;
- canonical automation injected into existing Music IR.

## 11. Promotion gate

M7-R3 may be promoted only after the successor exact head containing this file satisfies all of the following:

1. the same **11 workflows** complete with SUCCESS;
2. successor R3 artifact is independently inspected;
3. every manifest record remains hash/size exact;
4. repeated evidence generation remains byte-identical;
5. successor extracted R3 evidence tree is byte-identical to the pre-durable evidence tree;
6. source hashes and derived execution SHA-256 remain identical;
7. all required positive proof booleans remain true;
8. all authority/non-claim booleans remain false as designed;
9. existing compiler/renderer regressions remain green;
10. no excluded renderer/audio/backend capability is newly claimed.

Until then, M7-R3 remains **not yet promoted**.
