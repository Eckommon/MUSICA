# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M7-R3 — DETERMINISTIC AUTOMATION LOWERING & DERIVED EXECUTION BOUNDARY: VALIDATED — BOUNDED DERIVED EXECUTION**

M0→M7-R3 are validated only within their durable repository claims. Accepted Music Blueprint remains canonical creative authority. Browser, Music IR, automation execution, renderer/plugin and external DAW state remain derived or non-authoritative.

## Canonical proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**

## Canonical milestone ledger / 공식 마일스톤 원장

| Milestone | Status | Durable evidence |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | `evidence/M3_R1_VALIDATION.md`, `evidence/M3_R2_VALIDATION.md` |
| M4 Browser Studio / Usable MVP | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` → `evidence/M4_R3_VALIDATION.md` |
| M5 Rendering / Interchange / Evaluation | **VALIDATED — BOUNDED** | `evidence/M5_R1_VALIDATION.md` → `evidence/M5_R4_VALIDATION.md` |
| M6 Precision Editing R0→R4 | **VALIDATED — BOUNDED** | `evidence/M6_R0_VALIDATION.md` → `evidence/M6_R4_VALIDATION.md` |
| M7-R0 Automation Authority & Canonical Model | **VALIDATED — CONTRACT/DESIGN ONLY** | `evidence/M7_R0_VALIDATION.md` |
| M7-R1 Canonical Automation Runtime & Blueprint Integration | **VALIDATED — BOUNDED CORE RUNTIME** | `evidence/M7_R1_VALIDATION.md` |
| M7-R2 Browser Studio Automation Lane / Inspect Surface | **VALIDATED — BOUNDED REAL-BROWSER SURFACE** | `evidence/M7_R2_VALIDATION.md` |
| M7-R3 Deterministic Automation Lowering & Derived Execution Boundary | **VALIDATED — BOUNDED DERIVED EXECUTION** | `evidence/M7_R3_VALIDATION.md` |
| M7-R4 Reference Renderer Automation Mapping & Audible Evidence | **NOT IMPLEMENTED — NEXT** | `memory/NEXT_ACTION.md` |

## M7-R3 final evidence / M7-R3 최종 근거

- Issue `#77` — **COMPLETED**
- PR `#78` — **MERGED**
- implementation merge/main: `f4dbbf78c1556815228ef1446192a1308707eec9`
- pre-durable exact head: `09eaa538128a302f82374764becf1ddfc87eafda`
- final evidence-bearing successor head: `43d4568362cc26c23e9747da2a15b29c0cf4fe4d`
- successor M7-R3 `34822272947` — **SUCCESS**
- successor MUSICA CI `34822272980` — **SUCCESS**
- successor M7-R2 `34822272949` — **SUCCESS**
- successor M7-R1 `34822272975` — **SUCCESS**
- successor M7-R0 `34822272967` — **SUCCESS**
- successor M6-R4 `34822272955` — **SUCCESS**
- successor M6-R3 `34822272953` — **SUCCESS**
- successor M6-R2 `34822272968` — **SUCCESS**
- successor M6-R1 `34822272956` — **SUCCESS**
- successor M5-R3 `34822273054` — **SUCCESS**
- successor M5-R4 `34822272987` — **SUCCESS**
- successor artifact ID `10338193487`
- packaging SHA-256 `48b157aefb9bd6067aa7a2d4b187693294a2b7417869c35a4daa56bea5d1f61c`
- internal manifest SHA-256 `864135b90e650496e89d1e6f9b293e709f2fd187a3ddb639e155136c028207db`
- derived execution SHA-256 `2874fc72e78fd817a53ad2c20348cf56403af53fa24fdfc57f7f2aa1ac2444c7`
- manifest records: **10/10 exact hash + size matches**
- pre-durable vs successor extracted evidence: **11 files / 0 differences**

## M7-R3 validated authority invariant

```text
accepted optional materials.automation
→ exact source hashes
→ deterministic automation-execution-v0
→ stable lane/parameter/point provenance
→ deterministic PPQ 480 tick representation
→ typed hold / linear segments
→ backend mapping remains UNMAPPED
```

Validated R3 properties:

- no automation is fabricated for legacy projects;
- source binding includes project/revision/Blueprint/material hashes;
- `lane_id`, `point_id`, `parameter_id` remain source authority identities;
- execution state is explicitly derived/non-canonical;
- Decimal `ROUND_HALF_UP` beat→tick policy is explicit;
- source beat/value/interpolation survive lowering;
- distinct source beats collapsing to one tick fail closed;
- backend mapping remains typed `UNMAPPED`;
- backend-address/MIDI-CC injection is schema-rejected;
- source Blueprint and automation material remain unchanged;
- existing Music IR compiler output remains byte-identical before/after lowering;
- no Project/Blueprint/reverse/renderer authority is granted;
- `audible_automation_validated=false` remains explicit.

## Current capability stack / 현재 기능 스택

### Authority & project core
Typed Intent/Blueprint, semantic controls, locks/constraints, immutable revisions/branches/audit, exact-note material and accepted explicit automation material.

### Precision editing
M6 exact-note editing and M7-R1/R2 automation point editing share source-bound Preview/Accept authority patterns.

### Studio
Browser Studio Direct → Shape → Inspect → Code, exact-note piano roll and bounded canonical automation Inspect editing are validated.

### Derived execution
R3 can deterministically lower accepted canonical automation to `automation-execution-v0` without guessing backend addresses.

### Renderer / interchange
Existing bounded rendering, DAWproject interchange/evaluation and exact-note reconciliation remain validated. Canonical automation is **not yet validated as audible renderer control**.

## Current architecture finding for R4

Current semantic Music IR controls are MIDI-like and the reference WAV renderer interprets CC11/74/71. Canonical automation must not inherit those meanings implicitly.

The safest next step is a renderer-specific derived plan that consumes both exact Music IR and exact R3 execution hashes, maps only one explicit canonical parameter domain, and leaves all others unmapped.

Chosen bounded R4 mapping:

```text
parameter_id = mix.gain
scope        = project
unit         = normalized
renderer     = musica-reference-local
```

Recommended renderer semantics: evaluate R3 `hold|linear` segments as a deterministic gain envelope and apply it as a post-synthesis reference-WAV multiplier through a new additive automation-aware render path. Existing `render_wav()` and MIDI semantics remain unchanged.

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate:

- audible renderer execution of canonical automation;
- arbitrary canonical parameter → renderer/MIDI/plugin mapping;
- plug-in/device mapping or VST/AU/CLAP hosting;
- external DAW automation reconciliation;
- arbitrary tempo maps or spline/bezier curves;
- lane creation/deletion or parameter reassignment;
- real-time MIDI/OSC automation;
- live OpenAI provider execution;
- human-subject usability/preference or perceptual superiority;
- waveform/destructive audio editing, cloud collaboration or desktop signing.

## Next phase / 다음 단계

> **M7-R4 — Reference Renderer Automation Mapping & Audible Evidence**

Required path:

```text
validated Music IR
+
validated R3 automation execution
→ exact hash-bound reference-render plan
→ explicit mix.gain mapping only
→ deterministic hold/linear gain envelope
→ automation-aware reference WAV
→ byte reproducibility + objective audio-difference evidence
```

No arbitrary mapping expansion is allowed in R4. Unsupported lane domains remain typed unsupported/unmapped rather than guessed.

## Resume authority / 재개 권위

Before R4 substantive work inspect:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. `docs/M7_AUTOMATION_AUTHORITY.md`
4. `evidence/M7_R3_VALIDATION.md`
5. `schemas/automation-execution-v0.schema.json`
6. `src/musica/automation_lowering.py`
7. `src/musica/compiler.py`
8. `src/musica/render.py`
9. `src/musica/renderer.py`
10. `memory/CURRENT_STATE.md`
11. `memory/NEXT_ACTION.md`

**Repository evidence remains authoritative over conversation/model memory.**