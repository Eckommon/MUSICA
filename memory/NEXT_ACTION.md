# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**ISSUE #115 — MIXER ROUTING & AUTOMATION FOUNDATION v0**

The bounded Audio Track / Clip / Mixer Foundation v0 is validated end-to-end through ATCM-R4. This state-only closure authorizes closing parent Issue `#95` after the state record itself is green and merged.

The next dependency-safe commercial-workstation mission is explicit mixer routing plus supported programmable mixer automation.

Do **not** jump directly to recording, low-latency device I/O or third-party plugin hosting before the routing substrate is trustworthy.

## Canonical base / 공식 기준점

- parent Issue `#95` — bounded closure criteria **SATISFIED; close after state-only merge**
- ATCM-R0 `#97` — **COMPLETED / VALIDATED**
- ATCM-R1 `#99` — **COMPLETED / VALIDATED**
- ATCM-R2 `#102` — **COMPLETED / VALIDATED**
- ATCM-R3 `#105` — **COMPLETED / VALIDATED**
- ATCM-R4 `#111` — **COMPLETED / VALIDATED**
- ATCM-R4 PR `#114` — **MERGED**
- R4 merge/main: `e19c8ebf81b1dc37a03493458abb180adf48e9c7`
- R4 pre-validation exact head `2062c6e778b4cd7c726644550ca3917e4c102275` — **20/20 SUCCESS**
- R4 validation-record successor head `714769e2cedaa545512b8763066ef11fb9a594d1` — **20/20 SUCCESS**
- durable R4 validation: `evidence/ATCM_R4_VALIDATION.md`
- exact successor Issue `#115` — **OPEN**

## Inherited authority / 상속 권한

Issue #115 inherits a validated native-audio substrate:

```text
immutable audio asset
→ accepted track / clip state
→ Preview → explicit Accept
→ accepted per-track mixer state
→ deterministic offline mix
→ truthful Browser interaction
→ deterministic persistence / fresh reopen
```

Routing and automation must extend that substrate without creating a second source of creative authority.

## Core invariant / 핵심 불변식

```text
accepted tracks + clips + mixer state
+ accepted explicit routing graph
+ accepted supported automation
→ deterministic signal-flow plan
→ deterministic derived routed mix
≠ reverse creative authority
```

Browser state, runtime graph objects, meters and rendered audio remain derived unless explicitly accepted through the trusted authority path.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground the completed native-audio foundation

Inspect at minimum:

- `docs/COMMERCIAL_WORKSTATION_TARGET.md`;
- `evidence/ATCM_R2_VALIDATION.md`;
- `evidence/ATCM_R3_VALIDATION.md`;
- `evidence/ATCM_R4_VALIDATION.md`;
- `schemas/audio-material-v0.schema.json`;
- native mixer contracts/schemas;
- `src/musica/audio_edit.py`;
- `src/musica/audio_mixer_edit.py`;
- `src/musica/native_mixer.py`;
- Studio/Browser native-audio projection and E2E code;
- existing automation contract/runtime/lowering modules.

Do not fork accepted-state authority or duplicate the automation system.

### 2. Freeze routing topology v0 before implementation

Define a small explicit acyclic graph with stable identities.

At minimum decide and version:

- master/output sink identity;
- bus/group/return node identity and ordering;
- track output target semantics;
- send identity;
- send gain range/unit;
- one exact send tap position for v0 unless pre/post semantics are fully contracted;
- deterministic node/edge ordering;
- summing order;
- graph validation and cycle policy;
- missing target behavior;
- unsupported topology behavior.

Prefer a narrow DAG over an under-specified general graph.

### 3. Define canonical routing contract

The accepted routing representation must bind at least:

- routing version;
- stable node IDs;
- node kind;
- explicit output target;
- ordered sends;
- exact source/target IDs;
- accepted gain/pan/mute/solo where applicable;
- one master sink;
- canonical ordering rules.

Reject:

- duplicate node/send IDs;
- unknown targets;
- cycles;
- missing master;
- ambiguous multiple masters;
- invalid gains/parameters;
- routes that violate the bounded topology.

### 4. Extend Preview→Accept authority for routing edits

Routing state changes must be source-bound candidates.

At minimum support:

- add bus/group;
- set track output target;
- add/remove bounded send;
- set send gain;
- set bounded bus mixer state where contracted.

Required authority behavior:

```text
accepted source revision
→ routing candidate
→ validate graph + project binding
→ Preview; accepted HEAD unchanged
→ explicit Accept
→ revalidate source/head/graph
→ exactly one accepted revision advance
```

Stale Preview must fail closed.

### 5. Build deterministic signal-flow plan

Lower exact accepted state into an inspectable plan that records:

- source revision / Blueprint hashes;
- routing contract version;
- ordered graph nodes and edges;
- track/clip source bindings;
- resolved output targets;
- resolved send gains;
- mixer parameter values;
- automation bindings where supported;
- deterministic plan SHA-256.

### 6. Extend the deterministic offline mixer

The routed renderer must inherit existing explicit R2 numeric/output semantics unless a versioned change is necessary.

Prove at minimum:

- direct track→master;
- two or more tracks→bus→master;
- send contribution;
- deterministic summing order;
- mute/solo interactions where applicable;
- exact byte-reproducible output;
- invalid graph cannot render.

Do not introduce hidden resampling, limiter or dynamic routing.

### 7. Bind supported mixer automation

Reuse the existing typed automation authority/lowering family.

Start with a bounded parameter map, preferably:

- track gain;
- track pan;
- bus/group gain;
- bus/group pan where the node contract supports it;
- send gain only if interpolation/execution semantics can be specified exactly.

Each automatable parameter must declare:

- stable target identity;
- parameter identity;
- unit/range;
- interpolation semantics;
- time/sample lowering rule;
- fail-closed unsupported mapping behavior.

Do not guess plugin/device parameter semantics.

### 8. Browser inspection and edit surface

Expose the accepted routing graph and bounded mixer automation truthfully in Browser Studio.

Browser operations must:

- show accepted vs Preview state;
- use source-bound candidate endpoints;
- never directly mutate accepted routing;
- show exact route target/send identity;
- truthfully label accepted/preview-derived audition;
- keep meters/runtime transport derived.

### 9. Persistence / reopen

Prove accepted routing and supported automation survive deterministic export/import and fresh reopen with exact stable IDs and graph structure.

Regenerated signal-flow plan and routed WAV must match before/after reopen.

### 10. Negative matrix

At minimum fail closed on:

- routing cycle;
- unknown output target;
- unknown send target;
- duplicate IDs;
- missing/ambiguous master;
- invalid gain/pan/send values;
- stale Preview;
- unsupported automation target/parameter;
- missing/corrupt referenced audio asset;
- Browser/API direct accepted-state mutation attempt.

### 11. Dedicated evidence

Construct deterministic evidence such as:

```text
accepted native-audio project
→ Preview bus + route + send
→ accepted HEAD unchanged
→ explicit Accept
→ deterministic routed plan A + WAV A
→ independent plan B + WAV B
→ byte equality
→ Preview supported mixer automation
→ explicit Accept
→ exact documented routed-audio difference
→ fresh reopen
→ same graph/automation IDs + same derived hashes
→ invalid cycle/missing target/stale Preview fail closed
→ real Browser projection remains non-canonical
```

### 12. Permanent CI and promotion

Issue #115 must add its own dedicated permanent gate without weakening the existing **20** permanent workflows.

Promotion requires:

- implementation and deterministic evidence complete;
- all permanent workflows green on exact evidence-bearing head;
- independently inspected artifact manifest/hashes;
- durable routing/automation validation record;
- successor exact-head full rerun;
- expected-head merge;
- Issue #115 completion;
- separate state-only closure.

## Explicit non-goals / 비목표

Do not widen Issue #115 into:

- ASIO/CoreAudio/WASAPI callback engine;
- microphone/line recording;
- low-latency monitoring guarantee;
- VST3/AU/CLAP hosting;
- arbitrary plugin sidechains;
- plugin-delay compensation;
- implicit sample-rate conversion;
- warp/time-stretch/pitch shift;
- mastering-grade processing;
- cloud/multi-user authority;
- generalized commercial release qualification.

## Dependency path / 의존 경로

```text
Audio Track / Clip / Mixer Foundation v0      VALIDATED
→ Mixer Routing & Automation Foundation v0    CURRENT / Issue #115
→ real-time engine + devices
→ recording / monitoring
→ plugin hosting + latency compensation
→ deeper audio editing
→ release hardening
```

The exact later order remains evidence-driven.

## Maximum intended outcome / 최대 의도 결과

> **MUSICA can represent, edit through Preview/Accept, persist, inspect and deterministically render a bounded explicit mixer routing graph with supported programmable mixer automation, without allowing routing runtime or rendered audio to become reverse creative authority.**

This remains a target claim until Issue `#115` is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**