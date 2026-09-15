# M7-R4 Validation — Reference Renderer Automation Mapping & Audible Evidence

Status: **VALIDATION CANDIDATE — SUCCESSOR RERUN REQUIRED**

This record durably binds the pre-durable M7-R4 evidence-bearing head. It does **not** by itself promote M7-R4; promotion requires the same full regression set to succeed again on the successor exact head containing this record, plus independent successor artifact inspection.

## 1. Validated claim boundary

The maximum evidence-supported claim at the pre-durable head is:

> MUSICA can take validated source-bound automation execution for canonical `mix.gain` and, through one explicit reference-renderer mapping policy, deterministically produce audibly different WAV output whose gain-envelope effect is objectively measurable and byte-reproducible, without changing canonical authority or reusing MIDI CC as implicit automation semantics.

The bounded mapping is exactly:

```text
parameter_id = mix.gain
scope        = project
owner_id     = null
unit         = normalized
range        = [0.0, 1.0]
renderer     = musica-reference-local
```

M7-R4 does **not** claim arbitrary parameter mappings, canonical MIDI-CC automation semantics, plug-in/device/VST/AU/CLAP hosting, external DAW automation, real-time MIDI/OSC control, arbitrary tempo maps, Browser UI expansion, mastering quality, human preference or perceptual superiority.

## 2. Architecture and authority boundary

R4 preserves this one-way path:

```text
accepted Blueprint automation
→ M7-R3 automation-execution-v0
→ automation-render-plan-v0
→ bounded reference-renderer PCM gain application
→ WAV artifact + objective evidence
```

The renderer plan is `derived_noncanonical` and binds exact Music IR and R3 execution SHA-256 values. It grants no project/Blueprint mutation or reverse promotion authority. `midi_cc_semantics_authorized=false`; R4 does not equate canonical `mix.gain` with existing semantic CC11.

Existing `src/musica/render.py`, `src/musica/renderer.py` and `src/musica/compiler.py` are unchanged. The automation-aware path is additive and starts from the existing deterministic `wav_bytes()` baseline. Gain is applied after the existing safety normalization, followed only by a PCM clipping guard; no post-automation renormalization can erase the gain relationship.

## 3. Pre-durable exact head

- Issue: `#80`
- draft implementation PR: `#81`
- branch: `m7-r4-reference-renderer-automation`
- base canonical closure main: `2215650cb8cd6ba9396016a086a10c5b1103717f`
- exact pre-durable head: `0166eb193f3df1269f3f8260753faed99de97e2d`

The implementation diff at this head adds exactly five files and changes no existing runtime file:

```text
.github/workflows/m7-r4-audible-automation-evidence.yml
schemas/automation-render-plan-v0.schema.json
src/musica/automation_renderer.py
src/musica/m7_r4_demo.py
tests/test_m7_r4_automation_renderer.py
```

## 4. Exact-head workflow evidence — 12/12 SUCCESS

| Workflow | Run | Result |
|---|---:|---|
| MUSICA CI | `35001882834` | SUCCESS |
| M7-R4 Audible Automation Evidence | `35001883011` | SUCCESS |
| M7-R3 Automation Lowering Evidence | `35001882828` | SUCCESS |
| M7-R2 Real-Browser Automation Evidence | `35001883018` | SUCCESS |
| M7-R1 Automation Runtime Evidence | `35001882904` | SUCCESS |
| M7-R0 Automation Contract Evidence | `35001882812` | SUCCESS |
| M6-R4 Interchange Note Reconciliation | `35001882801` | SUCCESS |
| M6-R3 Real-Browser Exact-Note Evidence | `35001882895` | SUCCESS |
| M6-R2 Piano-Roll Evidence | `35001882796` | SUCCESS |
| M6-R1 Exact-Note Edit Evidence | `35001882900` | SUCCESS |
| M5-R3 DAWproject Evidence | `35001882773` | SUCCESS |
| M5-R4 Paired Audio Evidence | `35001882980` | SUCCESS |

The dedicated M7-R4 job ran M7-R0/R1/R2/R3/R4 automation tests, generated evidence twice, required `diff -qr` byte-tree identity, and uploaded the first evidence tree.

## 5. Pre-durable artifact lineage

Artifact:

- name: `musica-m7-r4-audible-automation-evidence`
- artifact ID: `10410595243`
- GitHub packaging digest / downloaded ZIP SHA-256: `03f77cc0e0b539f67c4bc5cd617de71d0cb42434456c18776d7d9897feab24dc`
- internal `manifest.json` SHA-256: `532b225c9a40db44565fd617d5b5481049efcd9b337c022e6ab0b9af2a8110a4`
- manifest records: **13 / 13 exact SHA-256 + byte-size matches**
- archive contents: **14 files including `manifest.json`**
- automation render plan SHA-256: `3821d05b18b55b81836bfcd271134bac3245fd3324bacb401647329d43049296`

Audio bytes:

- baseline WAV SHA-256: `efb3dfecd8b72545563a24617eaafaeea8ea22738103fa7703cb7efcfa0429c3`
- automated A WAV SHA-256: `3137a946772c80286e9ba57df3081e3574be6cd4489d036359857ab75a2248a0`
- automated B WAV SHA-256: `3137a946772c80286e9ba57df3081e3574be6cd4489d036359857ab75a2248a0`
- automated A/B byte identity: **TRUE**
- baseline differs from automated WAV: **TRUE**
- different PCM samples: **146,461**

## 6. Objective envelope and audio evidence

Exact gain probes from the mapped R3 lane:

| Tick | Expected / observed gain |
|---:|---:|
| `0` | `0.65` |
| `1920` | `0.735` |
| `3840` | `0.82` |
| `5000` | `0.82` |
| `5760` | `0.75` |
| `7000` | `0.75` |

The evidence uses an 8-second reference render at 112 BPM, covering the initial linear segment, the subsequent hold segment, and the post-last-point interval.

Whole-render metrics:

- baseline RMS: `612.776996313`
- automated RMS: `461.657364748`
- baseline peak integer: `3287`
- automated peak integer: `2477`

Window RMS ratios relative to the unchanged baseline:

- linear window 1.0–2.0 s: `0.707450205`
- hold window 5.0–6.0 s: `0.820013328`
- after-last window 7.0–7.8 s: `0.750111392`

Absolute-amplitude ratios independently track the same relationship:

- linear: `0.707804694`
- hold: `0.820007431`
- after-last: `0.750159436`

These measurements establish deterministic amplitude application only; they are not evidence of perceptual quality.

## 7. Mapping and negative-boundary proof

The artifact independently shows:

- mapped parameter IDs: exactly `["mix.gain"]`;
- unmapped parameter IDs include `synth.cutoff`;
- tampered plan source hash is rejected;
- source revision and PPQ are cross-bound;
- Music IR hash and automation execution hash are recomputed and bound;
- legacy/no-canonical-automation rendering is byte-identical to baseline;
- source Blueprint, Music IR and R3 execution remain unchanged;
- existing baseline `wav_bytes()` remains byte-identical before/after R4 use;
- existing MIDI bytes remain byte-identical;
- baseline and automated WAV both pass objective WAV QA;
- `canonical=false`;
- `project_mutation_authorized=false`;
- `blueprint_mutation_authorized=false`;
- `reverse_promotion_authorized=false`;
- `midi_cc_semantics_authorized=false`;
- `renderer_application_authorized=true` only inside the bounded derived renderer plan;
- `cc11_used_as_canonical_mix_gain=false`.

All 25 intended positive proof booleans are true and all six intended negative authority booleans remain false.

## 8. Promotion gate

M7-R4 may be promoted only after the successor exact head containing this durable record satisfies all of the following:

1. the same 12 workflows complete with SUCCESS;
2. the successor M7-R4 artifact is independently inspected;
3. all 13 manifest records match exact SHA-256 and byte size;
4. the extracted successor evidence tree is byte-identical to the pre-durable evidence tree unless a documented evidence-only nondeterministic field exists (none is currently expected);
5. automated A/B WAV remain byte-identical and differ from baseline;
6. exact gain probes and objective RMS/peak/window relationships remain unchanged;
7. source/mapping authority boundaries remain unchanged;
8. no excluded capability is newly claimed.

Until then, M7-R4 remains **not yet promoted**.

**Repository evidence remains authoritative over conversation/model memory.**
