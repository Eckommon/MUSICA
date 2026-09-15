# M7-R5 Implementation Contract — Studio Automation Audition & Artifact Persistence

Status: **DESIGN READY / CODE WRITE BLOCKED BY CURRENT CONNECTOR POLICY**

Canonical base: `0e9d8cec4b9fb8ad476cd4460741b470b6c02baf`  
Branch: `m7-r5-studio-audible-automation`

This document is a durable implementation handoff for the exact next bounded milestone. It does not claim M7-R5 implementation or validation.

## 1. Product gap confirmed from repository code

`StudioAutomationSurface.preview_automation_edit()` correctly creates a trusted, source-bound automation Preview and installs it through `StudioService._install_preview()`.

However, `_install_preview()` ultimately calls `StudioService._render_to_cache()`, which currently renders:

```text
compile_blueprint
→ render_midi
→ render_wav
```

Therefore the Browser automation Preview can contain valid canonical automation while its Studio WAV still ignores the validated M7-R3→M7-R4 audible path.

## 2. Bounded implementation decision

Do **not** expand the renderer mapping registry in R5. Reuse the already validated R4 mapping only:

```text
parameter_id = mix.gain
scope        = project
owner_id     = null
unit         = normalized
range        = [0, 1]
```

The lowest-risk first implementation is to keep the existing `_install_preview()` call unchanged so MIDI and Preview authority remain stable, then replace **only the pending automation Preview WAV** through the validated R3→R4 path.

Target sequence:

```text
build_automation_edit_preview
→ READY_FOR_PREVIEW
→ existing StudioService._install_preview()
   → existing candidate MIDI
   → existing baseline candidate WAV
→ compile_blueprint(candidate)
→ lower_automation_execution(candidate)
→ build_automation_render_plan(music_ir, execution)
→ render_automation_wav(..., pending.wav_path)
→ pending automation Preview now carries bounded audible WAV
```

If any R3/R4 step fails, clear the pending Preview fail-closed. The accepted project ref must remain byte-for-byte unchanged throughout Preview construction/audition.

## 3. Exact code touchpoint

Primary implementation file:

```text
src/musica/studio_automation.py
```

Recommended imports:

```text
hashlib
compile_blueprint
lower_automation_execution
build_automation_render_plan
automation_render_plan_sha256
render_automation_wav
DEFAULT_SAMPLE_RATE
```

Recommended private helper on `StudioAutomationSurface`:

```text
_install_audible_preview(session, candidate_blueprint) -> audition_proof
```

The helper should:

1. require `session.pending.kind == automation_edit`;
2. capture accepted head before rendering;
3. hash baseline pending WAV and pending MIDI;
4. compile candidate Music IR;
5. lower candidate automation through R3;
6. build exact R4 render plan;
7. render through `render_automation_wav` into the existing pending WAV path;
8. verify accepted head is unchanged;
9. return/store a typed proof payload;
10. clear pending Preview and re-raise on any failure.

Recommended proof fields:

```text
audition_version
candidate_revision_id
path = m7-r3-to-m7-r4-reference-renderer
automation_applied
output_differs_from_baseline
mapped_lane_ids
unmapped_lane_ids
render_plan_sha256
baseline_wav_sha256
preview_wav_sha256
preview_midi_sha256
project_ref_unchanged
canonical = false
reverse_promotion_authorized = false
```

`mapped_lane_ids` must be exactly `A-MIX-GAIN` for the canonical fixture; `B-SYNTH-CUTOFF` must remain in `unmapped_lane_ids`.

## 4. Preserve the existing R2 view contract

`studio-automation-view-v0` currently fixes:

```text
audible_automation_validated = false
```

Do not silently rewrite that older R2 contract during the first R5 implementation. R5 may return/store a separate `studio_audition` proof in the Preview result/detail. A later explicitly versioned Studio automation view may advertise the new capability after R5 is fully validated.

## 5. Existing M2 lifecycle is intentionally reused

No new accept authority is required.

Current `StudioService.accept_preview()` already:

```text
commit_revision(pending.candidate)
→ bind_artifacts(revision_id, [pending.midi_path, pending.wav_path])
→ clear pending
→ verify project integrity
```

Therefore once the pending WAV is correctly replaced by the R4 output, explicit Accept will persist the **exact audible Preview WAV** with the immutable accepted revision.

Current `close_session()` removes session cache only. Accepted artifacts are copied into the project bundle, so reopening the project should serve the accepted artifact bytes unchanged.

## 6. Required R5 tests

Create:

```text
tests/test_m7_r5_studio_audition.py
```

Use the existing fixtures:

```text
examples/blueprints/valid/dark-electronic-20s-r1.json
examples/automation/valid/automation-material-v0.json
```

Bind the reusable cutoff fixture section to `S01`, as existing R2 tests already do.

### Test A — eligible mix.gain Preview is audible and non-canonical

- open an automation project;
- submit a source-bound `SET_VALUE` edit for `A-MIX-GAIN/P-GAIN-001`;
- assert Preview installed;
- accepted head unchanged;
- audition proof maps only `A-MIX-GAIN`;
- `B-SYNTH-CUTOFF` remains unmapped;
- Preview WAV SHA differs from the legacy baseline candidate WAV SHA;
- Preview MIDI SHA equals the existing candidate MIDI path;
- `canonical=false` and `reverse_promotion_authorized=false`.

### Test B — discard restores accepted media/state

- capture accepted head/media before Preview;
- install audible automation Preview;
- capture pending path;
- discard;
- assert pending path/cache removed;
- assert accepted head unchanged;
- assert accepted media resolves to accepted revision media, not discarded Preview bytes.

### Test C — accept persists exact audible Preview

- install Preview;
- capture Preview WAV and MIDI bytes;
- explicit Accept;
- assert one revision advance;
- assert artifact manifest has exactly MIDI + WAV;
- assert accepted `media_bytes(audio)` equals captured Preview WAV;
- assert accepted `media_bytes(midi)` equals captured Preview MIDI.

### Test D — reopen serves exact accepted artifact

- after Test C close session;
- create a new `StudioService` over the same workspace;
- reopen project;
- assert accepted head is unchanged;
- assert reopened audio bytes equal the previously accepted Preview bytes.

### Test E — unsupported-only automation does not invent mapping

- create a valid material containing only `B-SYNTH-CUTOFF`;
- edit that lane within range;
- assert render plan has no mapped lane;
- Preview WAV equals existing baseline candidate WAV;
- no MIDI/DSP mapping is guessed.

### Test F — legacy/no-automation compatibility

- existing M4 Studio create/render path stays byte-compatible;
- existing M4/M6/M7 regression suites remain green.

## 7. Deterministic evidence generator

Create:

```text
src/musica/m7_r5_demo.py
```

The generator should run in a temporary workspace and produce a deterministic package with at least:

```text
accepted-before.json
candidate-blueprint.json
automation-execution.json
automation-render-plan.json
preview-descriptor.json
preview-audition-proof.json
preview.wav
preview.mid
discard-proof.json
accept-proof.json
accepted-artifact-manifest.json
reopen-proof.json
authority-boundary-proof.json
manifest.json
```

Suggested lifecycle:

```text
open accepted automation project
→ Preview candidate A
→ prove audible Preview + unchanged accepted ref
→ Discard
→ prove accepted state/media unchanged
→ install the same deterministic candidate again
→ capture Preview WAV/MIDI
→ Accept
→ prove accepted artifact hashes equal Preview hashes
→ close session
→ reopen in a new service instance
→ prove reopened audio hash equals accepted Preview hash
```

Avoid timestamps, absolute temp paths and random session IDs in evidence output.

## 8. Dedicated workflow

Create:

```text
.github/workflows/m7-r5-studio-audible-automation-evidence.yml
```

Required steps:

```text
install dev dependencies
run R0→R5 automation/Studio regression tests
generate R5 evidence A
generate R5 evidence B
diff -qr A B
upload one evidence tree
```

Permanent gate set after R5 should include the existing 12 workflows plus the new R5 workflow.

## 9. Promotion discipline

```text
bounded implementation
→ draft PR
→ exact pre-durable head
→ 13 permanent workflows SUCCESS
→ independent artifact inspection
→ durable evidence/M7_R5_VALIDATION.md
→ successor exact head
→ same 13 workflows SUCCESS
→ successor artifact inspection
→ expected-head squash merge
→ Issue completed
→ state-only closure
```

Do not claim R5 implemented or validated before this sequence is complete.

## 10. Scope exclusions

R5 does not implement:

- a second canonical automation parameter family;
- canonical MIDI CC automation mapping;
- arbitrary part-scope renderer mapping;
- VST/AU/CLAP/device hosting;
- DAW automation interchange;
- real-time MIDI/OSC control;
- arbitrary tempo maps;
- spline/bezier/exponential interpolation;
- mastering/perceptual-quality claims.

## 11. Current tool constraint

In the current chat execution environment, GitHub Markdown writes succeed, while attempts to create or replace `.py` source files are blocked by the connector's safety inspection, including a two-line probe function. This constraint must not be bypassed. Continue implementation only in an environment where code-file writes are permitted.

**Repository evidence remains authoritative over conversation/model memory.**
