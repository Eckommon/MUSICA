# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M7-R5 — STUDIO AUTOMATION AUDITION & ACCEPTED ARTIFACT PERSISTENCE**

M7-R4 is `VALIDATED — BOUNDED AUDIBLE EXECUTION`. The next mission is to connect that validated audible automation path to the actual Studio Preview/Accept/reopen lifecycle **without expanding canonical parameter coverage and without changing M2 authority**.

## Canonical starting point / 공식 시작점

- M7-R4 Issue `#80` — **COMPLETED**
- M7-R4 PR `#81` — **MERGED**
- implementation merge/main: `6f862dea15eea394f3e29ad7c91ef3e8b2cd767a`
- pre-durable exact head: `0166eb193f3df1269f3f8260753faed99de97e2d`
- final evidence-bearing successor head: `cae504d4582eb234b6bcb121fa4b96370c08069f`
- successor regression set: **12/12 SUCCESS**
- successor artifact ID: `10410595918`
- internal manifest SHA-256: `532b225c9a40db44565fd617d5b5481049efcd9b337c022e6ab0b9af2a8110a4`
- render-plan SHA-256: `3821d05b18b55b81836bfcd271134bac3245fd3324bacb401647329d43049296`
- automated WAV SHA-256: `3137a946772c80286e9ba57df3081e3574be6cd4489d036359857ab75a2248a0`
- durable evidence: `evidence/M7_R4_VALIDATION.md`

## Architecture fact R5 must close / R5가 닫아야 할 구조 사실

Current `StudioService._render_to_cache()` still renders all Studio Preview/initial/fallback audio through:

```text
compile_blueprint
→ render_midi
→ render_wav
```

Current `StudioAutomationSurface.preview_automation_edit()` builds a trusted R1 automation Preview, then calls `StudioService._install_preview()`. `_install_preview()` delegates to `_render_to_cache()`. Therefore the Browser automation Preview can contain a valid `mix.gain` curve while the actual Studio Preview WAV does not yet consume R3 lowering or the R4 automation renderer.

Current `accept_preview()` binds the exact pending MIDI/WAV paths to the accepted revision. This is useful: once the Preview WAV is correctly automation-aware, existing M2 acceptance can persist that exact audible artifact without inventing new authority.

## Bounded R5 mission / 제한 미션

R5 implements one product integration path only:

```text
validated candidate Blueprint
→ compile_blueprint(candidate)
→ lower canonical automation through R3
→ build R4 automation-render-plan-v0
→ if eligible mix.gain is mapped:
     render automation-aware WAV
  else:
     preserve baseline WAV behavior
→ install Studio Preview
→ explicit Accept or Discard
```

MIDI remains on the existing path.

## Required implementation direction / 필수 구현 방향

### 1. Centralize Studio cache render decision

Modify the internal Studio render-cache boundary rather than duplicating rendering logic in Browser code.

Recommended shape:

```text
StudioService._render_to_cache(...)
  compile Music IR
  render existing MIDI
  derive R3 automation execution from the same Blueprint
  build R4 reference render plan
  select WAV path:
    eligible mapped mix.gain → automation-aware WAV
    no canonical automation / no mapped lane → existing baseline WAV
```

The exact helper name may vary after implementation inspection, but the decision belongs in the trusted Studio service, not DOM/JavaScript.

### 2. Preserve legacy byte compatibility

For a Blueprint with no explicit canonical automation, Studio WAV bytes must remain byte-identical to the existing `render_wav()` path.

Unsupported lanes alone must not silently change audio. In particular `synth.cutoff` remains unmapped under the current R4 policy.

### 3. Preview authority remains unchanged

Before and after creating an audible Preview:

```text
accepted branch head is unchanged
Preview artifact is non-canonical
```

Audio availability does not imply acceptance.

### 4. Discard semantics

Discard must prove:

- pending Preview state removed;
- Preview cache media removed;
- accepted branch head unchanged;
- accepted artifact manifest unchanged;
- subsequent accepted media resolves to accepted revision media, not discarded Preview bytes.

### 5. Accept semantics

Accept must prove:

- exactly one new immutable revision is committed;
- the exact pending automation-aware WAV is bound to that revision;
- the accepted artifact WAV bytes equal the Preview WAV bytes;
- canonical authority comes from the accepted Blueprint revision, not from the audio artifact;
- MIDI remains the existing deterministic MIDI for that candidate.

### 6. Reopen / persistence semantics

After closing and reopening the project/session:

- accepted head is the accepted automation revision;
- `media_bytes(..., "audio")` returns the accepted artifact bytes;
- returned WAV equals the previously accepted Preview WAV;
- no re-render/reverse-inference is required when the artifact already exists.

### 7. Browser / Studio capability truthfulness

If R5 exposes an audible automation capability flag, update it only after the Studio lifecycle is actually validated. Existing R2 capability fields that say `audible_automation_validated=false` must not be changed speculatively before evidence.

## Required tests / 필수 테스트

At minimum prove:

1. Studio automation Preview with eligible `mix.gain` produces a WAV different from the same candidate's baseline `render_wav()`;
2. Preview WAV is deterministic across repeated equivalent sessions/operations where IDs are controlled;
3. Preview MIDI remains equal to the existing MIDI path;
4. accepted branch head does not change during Preview;
5. R4 mapped lane remains exactly `mix.gain/project/normalized`;
6. `synth.cutoff` remains unmapped and does not gain implicit audible control;
7. no-automation Studio render remains baseline-byte-identical;
8. unsupported-only automation remains baseline-equivalent or explicitly non-mapped according to current R4 policy;
9. Discard removes pending media and leaves accepted state/artifacts unchanged;
10. Accept advances exactly one revision;
11. accepted WAV bytes equal pending Preview WAV bytes;
12. accepted artifact manifest contains the correct WAV/MIDI hashes;
13. close/reopen serves the same accepted WAV bytes;
14. stale Preview conflict remains fail-closed;
15. cross-surface pending Preview isolation remains fail-closed;
16. source Blueprint/automation identities remain stable;
17. audio/renderer state cannot mutate or reverse-promote canonical automation;
18. R4/R3/R2/R1/R0 remain green;
19. M6-R4/R3/R2/R1 and M5-R3/R4 remain green;
20. Python 3.11/3.12 full suite remains green.

## Expected implementation package / 예상 구현 패키지

Likely bounded changes:

```text
src/musica/studio.py
src/musica/studio_automation.py        # only if truthful capability/detail plumbing is needed
tests/test_m7_r5_studio_audible_automation.py
src/musica/m7_r5_demo.py
.github/workflows/m7-r5-studio-audible-automation-evidence.yml
```

Avoid modifying `render.py`, `renderer.py` or `compiler.py` unless repository evidence proves integration is impossible without it. Prefer reusing the already validated R3/R4 modules.

## Evidence target / 공식 근거 목표

Dedicated evidence should include at minimum:

```text
accepted-before.json
candidate-blueprint.json
automation-execution.json
automation-render-plan.json
preview-descriptor.json
preview-audio-proof.json
preview.wav
preview.mid
discard-proof.json
accept-proof.json
accepted-artifact-manifest.json
reopen-proof.json
authority-boundary-proof.json
manifest.json
```

A strong fixture should exercise:

- eligible `mix.gain` audible Preview;
- an unsupported `synth.cutoff` lane remaining unmapped;
- Discard on one Preview;
- a second equivalent Preview followed by Accept;
- reopen/persistence verification.

## Scope control / 범위 통제

Do **not** add or claim in M7-R5:

- a second canonical parameter mapping family;
- canonical MIDI CC mapping for automation;
- arbitrary part-scope renderer automation;
- plug-in/device/VST/AU/CLAP hosting;
- external DAW automation import/export/reconciliation;
- MIDI/OSC real-time control;
- lane creation/deletion or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential interpolation;
- mastering quality or human/perceptual superiority.

## Maximum intended R5 claim / 성공 시 최대 주장

> **MUSICA Studio can audition a validated canonical `mix.gain` automation edit through the already validated R3→R4 derived execution path, keep that audition non-canonical until explicit Accept, discard it without changing accepted state, and on Accept persist the exact audible Preview artifact with the accepted immutable revision so the same audio is served after reopening.**

## Execution discipline / 실행 규율

```text
M7-R4 state-only closure
→ create M7-R5 Issue
→ fresh branch from closure main
→ bounded Studio render-cache integration
→ Preview/Discard/Accept/reopen tests
→ dedicated evidence workflow
→ PR
→ exact-head full regressions
→ artifact inspection
→ durable M7_R5 validation
→ successor rerun
→ expected-head merge
→ Issue completed
→ state-only closure
```

**Repository evidence remains authoritative over conversation/model memory.**