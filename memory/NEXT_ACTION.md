# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M7-R6 — TRUTHFUL AUDIBLE AUTOMATION CAPABILITY & BROWSER LIFECYCLE INSPECTION**

M7-R5 is `VALIDATED — BOUNDED STUDIO AUDITION & ARTIFACT PERSISTENCE`. The next mission is to make the Browser/Studio inspection surface truthfully describe the audible automation capability that R5 now actually provides, **without rewriting the historical R2 contract, without adding a second renderer mapping family, and without changing M2 authority**.

## Canonical starting point / 공식 시작점

- M7-R5 Issue `#84` — **COMPLETED**
- M7-R5 PR `#83` — **MERGED**
- implementation merge/main: `43488fe85bb6c2fde19dc27d0dabfdb7587d7f1f`
- pre-durable head: `298a46a4de360d697c2fe55006cd17966c3bf1e8`
- successor evidence head: `87dd85cb2ff2f0a576db24c6b87c7ad16a32bb29`
- final validation-record head: `41f98e882e62cf638370c998447e754398c63284`
- final exact-head regression set: **13/13 SUCCESS**
- final M7-R5 workflow: `35039890451` — **SUCCESS**
- final MUSICA CI: `35039890429` — **SUCCESS**
- R5 manifest SHA-256: `ab5c99c4ab474eccac17b727cf0a502061f2691ffae5bbfab734572a90e5c772`
- Preview/accepted/reopened WAV SHA-256: `4f26a08636726945205c97575885f9966f67245dc086eb30fd4af198c71d21b7`
- Preview/accepted/reopened MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- durable evidence: `evidence/M7_R5_VALIDATION.md`

## Architecture fact R6 must close / R6가 닫아야 할 구조 사실

R5 now creates trusted pending audition proof in `pending.detail.studio_audition`, including:

```text
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

However the historical R2 `studio-automation-view-v0` schema still requires:

```text
capabilities.audible_automation_validated = false
```

and the Browser automation view does not formally expose R5 `studio_audition` proof or accepted artifact lineage. This is intentional historical preservation, but it is now a product truthfulness gap.

The system can perform the audible audition, yet the versioned Browser inspection contract cannot truthfully say which lanes are audible, which are unmapped, whether automation changed the Preview WAV, or which exact WAV/MIDI artifacts were accepted and served after reopen.

## Bounded R6 mission / 제한 미션

R6 adds a **new versioned inspection/capability surface** for the already validated R5 lifecycle.

Preferred architecture:

```text
accepted automation view v0        # unchanged historical R2 contract
        +
R5 pending studio_audition proof
        +
accepted artifact metadata
        ↓
new audition/capability contract
        ↓
Browser Inspect presentation
```

Do not silently change the meaning of `studio-automation-view-v0`.

## Required contract / 필수 계약

Create a new schema/object with bounded fields equivalent to:

```text
contract_version
renderer_policy_id = musica-reference-local
validated_mapping_families = [mix.gain/project/normalized]
pending_audition:
  present
  preview_id / candidate_revision_id
  automation_applied
  output_differs_from_baseline
  mapped_lane_ids
  unmapped_lane_ids
  render_plan_sha256
  baseline_wav_sha256
  preview_wav_sha256
  preview_midi_sha256
  canonical = false
  reverse_promotion_authorized = false
accepted_media:
  revision_id
  wav artifact presence/hash
  midi artifact presence/hash
  source = bound_artifact | fallback_render
```

Exact field names may differ after implementation inspection, but every claim must be source-bound and schema-validated.

## Required implementation direction / 필수 구현 방향

### 1. Preserve v0

`schemas/studio-automation-view-v0.schema.json` and the historical R2 meaning of `audible_automation_validated=false` should remain unchanged unless evidence proves a versioned replacement is impossible.

### 2. Add a new inspection boundary

Prefer one of:

- `studio-automation-audition-v0`, or
- `studio-automation-view-v1` that explicitly supersedes rather than mutates v0.

A separate audition contract is preferred if it keeps R2 evidence maximally stable.

### 3. Derive only from trusted state

Pending audition fields must come from the trusted R5 pending Preview detail plus exact media bytes, not from DOM state or inferred audio analysis.

Accepted media fields must come from Project/Studio artifact binding and accepted revision identity. Do not infer accepted automation from WAV content.

### 4. Browser truthfulness

The Browser must distinguish at least:

```text
accepted automation material
pending non-canonical automation Preview
mapped audible lanes
unmapped/non-audible lanes
accepted bound media artifact
fallback-rendered media when no bound artifact exists
```

The UI must not label the entire automation system “audible” merely because one mapping family exists.

### 5. Lifecycle preservation

R6 presentation/inspection must not alter:

- Preview authority;
- Discard behavior;
- Accept revision count;
- accepted artifact bytes;
- renderer mapping policy;
- MIDI bytes.

## Required tests / 필수 테스트

At minimum prove:

1. historical `studio-automation-view-v0` remains byte/schema compatible with R2 expectations;
2. new audition contract validates for accepted state with no pending Preview;
3. new audition contract validates during an R5 eligible `mix.gain` Preview;
4. mapped lane IDs expose exactly `A-MIX-GAIN` for the canonical fixture;
5. `B-SYNTH-CUTOFF` is explicitly exposed as unmapped;
6. `automation_applied=true` only when mapped lanes exist;
7. Preview WAV/MIDI/render-plan hashes equal the actual pending files/proof;
8. `canonical=false` and `reverse_promotion_authorized=false` are explicit;
9. Discard removes pending audition inspection state;
10. accepted project ref remains unchanged on Preview/Discard;
11. explicit Accept produces exactly one revision;
12. accepted media inspection identifies the accepted revision and exact bound WAV/MIDI hashes;
13. close/reopen exposes the same accepted artifact hashes;
14. fallback render is distinguishable from a bound accepted artifact;
15. unsupported-only automation does not claim audible application;
16. stale/cross-surface Preview conflicts remain fail-closed;
17. real Chromium shows mapped/unmapped/audition status truthfully;
18. R5/R4/R3/R2/R1/R0 remain green;
19. M6-R4/R3/R2/R1 and M5-R3/R4 remain green;
20. Python 3.11/3.12 full suite remains green.

## Expected implementation package / 예상 구현 패키지

Likely bounded changes:

```text
schemas/studio-automation-audition-v0.schema.json
src/musica/studio_automation.py
src/musica/studio_http.py                # only if a dedicated endpoint is cleaner
src/musica/studio_web/app.js              # exact path after repository inspection
src/musica/studio_web/...                 # minimal UI presentation only
tests/test_m7_r6_studio_audition_view.py
e2e/test_m7_r6_browser.py
src/musica/m7_r6_demo.py
.github/workflows/m7-r6-audition-inspection-evidence.yml
```

Avoid modifying R4 mapping registry, compiler, Music IR, M2 authority or the historical R2 schema.

## Evidence target / 공식 근거 목표

Dedicated evidence should include at minimum:

```text
accepted-before-audition.json
pending-audition-view.json
pending-preview-descriptor.json
accepted-after.json
accepted-media-view.json
reopened-media-view.json
browser-proof.json
authority-proof.json
schema-compatibility-proof.json
manifest.json
```

Real-browser evidence should visibly prove:

- `mix.gain` is mapped/audible under `musica-reference-local`;
- `synth.cutoff` is unmapped;
- pending audition is `PREVIEW · NOT ACCEPTED`;
- Discard clears pending audition state;
- Accept/reopen show the exact accepted media identity;
- no UI state is treated as canonical authority.

## Scope control / 범위 통제

Do **not** add or claim in M7-R6:

- a second renderer mapping family;
- canonical MIDI CC mapping;
- arbitrary part-scope renderer automation;
- plug-in/device/VST/AU/CLAP hosting;
- external DAW automation import/export/reconciliation;
- MIDI/OSC real-time control;
- lane creation/deletion or parameter reassignment;
- arbitrary tempo maps;
- spline/bezier/exponential interpolation;
- mastering quality or human/perceptual superiority.

## Maximum intended R6 claim / 성공 시 최대 주장

> **MUSICA Browser Studio can truthfully inspect the already validated bounded audible automation lifecycle: it can distinguish accepted automation from a non-canonical audible Preview, show which canonical lanes are mapped or unmapped by the current reference renderer, and after explicit Accept/reopen identify the exact accepted WAV/MIDI artifacts without granting Browser/audio state canonical authority.**

## Execution discipline / 실행 규율

```text
M7-R5 state-only closure
→ create M7-R6 Issue
→ fresh branch from closure main
→ ratify new versioned audition-inspection contract
→ bounded trusted-state projection
→ Browser presentation
→ unit + real-browser lifecycle tests
→ dedicated deterministic evidence workflow
→ PR
→ exact-head full regressions
→ artifact inspection
→ durable M7_R6 validation
→ successor rerun
→ expected-head merge
→ Issue completed
→ state-only closure
```

**Repository evidence remains authoritative over conversation/model memory.**