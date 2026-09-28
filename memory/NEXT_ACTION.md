# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**MRAM-R3 — BROWSER ROUTING & NATIVE AUTOMATION SURFACE + REOPEN LIFECYCLE v0**

Issue `#126` — **OPEN**

Parent mission: Issue `#115` — **Mixer Routing & Automation Foundation v0 — OPEN**

MRAM-R2 Issue `#124` is validated, merged and completed. The next dependency-safe step is to expose the already accepted routing graph and native mixer gain/pan automation through a truthful real-Browser/Studio inspection/edit surface, then prove fresh restart/reopen lifecycle exactness.

Do **not** add realtime device I/O, recording, plugin hosting, sidechains, generalized parameter automation, send automation, mute/solo automation or mastering scope in R3.

## Canonical base / 공식 기준점

- canonical main after MRAM-R2 implementation merge:
  `932b98e64f6e6d0b5464023b79973b1a5b33b65c`
- parent Issue `#115` — **OPEN**
- MRAM-R2 Issue `#124` — **COMPLETED**
- MRAM-R2 PR `#125` — **MERGED**
- R2 implementation/evidence exact head:
  `6fdc2a38b59886ebd41fe38d2f293363d3bbec77` — **23/23 SUCCESS**
- R2 validation-record successor:
  `7432b2a2c1ee3e4d6fe031ef36cbd8206ace6b11` — **23/23 SUCCESS**
- durable validation: `evidence/MRAM_R2_VALIDATION.md`
- dedicated artifact ID: `10646022648`
- artifact ZIP SHA:
  `03b13c8a2c1bc1c84ed248b8891ae3626532723197359509273de56967f2abb0`
- permanent workflow count at validated R2 state: **23**

## Inherited authority / 상속 권한

R3 inherits:

```text
ATCM:
immutable audio assets
→ accepted tracks/clips/static mixer
→ deterministic native mix
→ Browser native-audio truth + reopen

M7:
typed automation material
→ source-bound Preview / explicit Accept
→ deterministic generic lowering
→ Browser automation inspection/edit authority patterns

MRAM-R0/R1:
explicit routing DAG
→ trusted routing Preview / Accept
→ accepted routing state
→ deterministic routed mixer

MRAM-R2:
stable audio_track|routing_node gain/pan automation
→ trusted native automation Preview / Accept
→ deterministic beat→frame lowering
→ deterministic routed execution
```

R3 must connect the real Browser/Studio surface to these existing authorities. It must not create a parallel routing/automation store, direct Browser commit path or runtime write-back authority.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground Browser/Studio architecture before changing UI

Inspect at minimum:

- `src/musica/studio_service.py` and related session/project lifecycle code;
- `src/musica/studio_http.py` routes;
- `src/musica/studio_audio.py` routed audition path;
- `src/musica/studio_web/*` current Browser UI;
- existing M6/M7 real-browser edit/Preview/Accept implementations and tests;
- accepted revision Compare Browser projection;
- `src/musica/routing_edit.py`;
- `src/musica/automation_edit.py`;
- `src/musica/routing_contracts.py`;
- `src/musica/native_mixer_automation.py`;
- `src/musica/routed_mixer.py`;
- `evidence/MRAM_R1_VALIDATION.md`;
- `evidence/MRAM_R2_VALIDATION.md`.

Determine the narrowest existing service/API/UI extension that can project exact accepted routing + native automation and delegate edits to current authority engines.

### 2. Freeze the Browser projection contract

The Browser-visible derived projection should bind at least:

- session ID;
- accepted revision ID;
- Blueprint SHA;
- audio material SHA;
- routing material SHA;
- automation material SHA;
- exact stable track IDs;
- exact stable routing node/send IDs;
- exact native automation lane/point IDs;
- explicit authority flags showing Browser projection is non-canonical.

Prefer a typed projection object rather than reconstructing authority from DOM state.

### 3. Implement truthful routing inspection

At minimum make the Browser/Studio able to inspect:

- each accepted audio track's primary routing target;
- bus/group/return/master node identity and type;
- node output target;
- post-fader sends and send gain;
- node static gain/pan/mute;
- exact master sink;
- accepted revision/source hashes.

The Browser must never infer identity from display name or array position.

### 4. Implement truthful native automation inspection

Expose accepted R2 lanes with:

- lane ID;
- target kind;
- stable target ID;
- parameter ID;
- unit/range;
- points;
- interpolation;
- exact accepted revision/source hashes.

Do not display generic M7 `UNMAPPED` lowering as if it were separate canonical mixer authority.

### 5. Reuse existing typed edit engines

Browser routing edits must produce existing routing edit candidate operations.

Browser native automation edits must produce existing automation edit candidate operations.

Required invariant:

```text
Browser input
→ typed non-canonical candidate
→ existing source-bound Preview engine
→ READY_FOR_PREVIEW or BLOCKED
→ accepted HEAD unchanged
→ explicit Accept
→ existing trusted authority
→ exactly one accepted revision advance
```

Do not add a direct Project Engine commit endpoint for Browser edits.

### 6. Bound the first Browser edit surface

Prefer only operations already contracted and evidenced.

Routing candidates may include a small subset such as:

- change track primary output;
- adjust an existing send gain;
- adjust existing node static mixer values.

Native automation candidates may include:

- add one bounded gain/pan lane where absent;
- insert/move/delete automation point under existing rules;
- set point value;
- set interpolation.

Do not broaden the underlying authority model merely to make UI implementation easier.

### 7. Preview truthfulness and stale-state protection

Preview responses should bind exact source hashes and expose:

- candidate diff;
- changed stable IDs;
- authority status/conflicts;
- accepted HEAD unchanged;
- whether the audition is accepted or Preview state.

Reject at minimum:

- stale accepted revision;
- stale session/reopen source;
- stale Blueprint/audio/routing/automation hashes;
- missing track/node/lane/point IDs;
- malformed target identity;
- unsupported operation/parameter/unit/range;
- Browser request attempting direct accepted-state mutation.

### 8. Audition the exact routing + automation state

Accepted audition must use the MRAM-R1/R2 routed mixer path.

If Preview audition is exposed, it must render the exact candidate state without silently accepting it.

At minimum prove the Browser does not fall back to:

- flat native mix when accepted routing exists;
- static gain/pan when accepted native automation exists.

### 9. Fresh restart/reopen lifecycle

Use a real process/service restart, not merely a second object reference.

Prove:

```text
accepted routed+automated revision
→ export/persist
→ stop service/process
→ start fresh service/process
→ reopen project
→ same accepted revision
→ same routing identities
→ same automation lane/point identities
→ same derived native automation plan SHA
→ same routed mix plan SHA
→ same routed WAV SHA
```

Browser-local UI state must not be required to reconstruct accepted creative state.

### 10. Real Chromium evidence

Add a dedicated real-browser E2E covering at minimum:

1. open routed+automated project;
2. inspect exact routing graph;
3. inspect exact native automation;
4. propose one bounded Browser edit;
5. observe Preview and unchanged HEAD;
6. explicitly Accept;
7. observe one revision advance and updated exact projection;
8. audition exact routed result;
9. restart/reopen fresh service;
10. observe exact restored identities and media hashes;
11. stale/unknown-ID negative paths fail closed;
12. no console/page/request errors beyond explicitly documented expected media aborts.

### 11. Deterministic evidence and permanent gate

Add a dedicated MRAM-R3 permanent workflow without weakening existing gates.

Expected permanent workflow count after adding a dedicated R3 gate: **24**, unless a repository-native consolidation is deliberately justified and evidenced.

Evidence should bind exact source hashes and prove deterministic Browser/API payloads where appropriate, real-browser screenshots/interaction evidence, accepted revision identities, restart/reopen hashes and fail-closed paths.

### 12. Parent Issue #115 closure evaluation

After R3 validates, evaluate every required capability in parent Issue #115 against repository evidence.

Do not close #115 merely because R3 merged. Close it only if all bounded v0 requirements are directly evidenced.

If a genuine gap remains, open the smallest dependency-safe successor rung instead of broadening R3 retroactively.

### 13. Promotion

R3 promotion requires:

- implementation/evidence complete;
- dedicated MRAM-R3 gate green;
- all permanent workflows green on exact evidence-bearing head;
- independent artifact digest/manifest/hash inspection;
- durable MRAM-R3 validation record;
- all workflows green again on exact validation-record successor head;
- expected-head squash merge;
- Issue #126 completed;
- separate state-only closure evaluating Issue #115.

## MRAM-R3 non-goals / 비목표

Do not implement or claim in R3:

- sidechains;
- send-gain automation beyond existing static send edit semantics;
- mute/solo automation;
- realtime callback/device transport;
- recording/monitoring;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- resampling;
- warp/time-stretch/pitch shift;
- mastering;
- generalized commercial release readiness.

## Maximum intended R3 outcome

> **MUSICA can truthfully inspect and edit its bounded accepted routing and native mixer gain/pan automation through a real Browser/Studio Preview→Accept surface, audition the exact accepted routed result, and recover the same accepted identities and deterministic routed output after fresh restart/reopen without Browser/runtime reverse authority.**

This remains a target claim until R3 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
