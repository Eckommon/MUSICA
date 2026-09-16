# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**ISSUE #95 — AUDIO TRACK / CLIP / MIXER FOUNDATION v0**

The post-Compare successor review is complete on this planning branch. The selected bounded mission is the first native audio-production substrate for MUSICA's long-term general-purpose/commercial workstation objective.

Do **not** infer `M8` or widen this mission into recording/plugin hosting/real-time audio by default.

Implementation begins only after the planning/ratification PR containing this record is merged and the resulting canonical main is re-grounded.

## Canonical planning base / 공식 계획 기준점

- pre-selection canonical main: `f6128a8b5dcaae5f4cb4e05ad21da415b34afaa5`
- Compare Issue `#89` — **COMPLETED**
- Compare PR `#91` — **MERGED**
- Compare closure PR `#94` — **MERGED**
- selected successor Issue `#95` — **OPEN**
- long-term target: `docs/COMMERCIAL_WORKSTATION_TARGET.md`
- selection record: `docs/POST_COMPARE_SUCCESSOR_SELECTION.md`

## Selected mission / 선정 미션

Build a bounded native audio domain:

```text
WAV/PCM source bytes
→ immutable content-addressed project asset
→ accepted audio track + clip references
→ source-bound non-destructive edit candidate
→ Preview · NOT ACCEPTED
→ explicit Accept
→ accepted audio material
→ deterministic mix plan
→ deterministic stereo mixdown
→ Browser arrangement/mixer inspection + audition
```

## Authority invariant / 권한 불변식

### Allowed canonical/accepted state

- audio asset identity/reference metadata required to bind exact immutable bytes;
- stable track IDs/order/names;
- stable clip IDs;
- clip asset reference;
- timeline position;
- source in/out range;
- bounded clip gain;
- bounded track gain/pan/mute/solo;
- accepted revision/source provenance.

### Derived only

- decoded PCM buffers;
- waveform caches;
- meters;
- deterministic mix plan/execution package;
- rendered track/stereo audio;
- Browser selection/drag state;
- transport/runtime state.

Derived state has no reverse-promotion authority.

## Exact implementation order / 정확한 구현 순서

Proceed in this order unless repository evidence requires a narrower correction.

### 1. Re-ground after planning merge

Before code changes:

- verify canonical `main` and planning merge SHA;
- confirm Issue `#95` is the only selected implementation mission;
- inspect current permanent workflow count;
- inspect `music-blueprint-v0`, project/version authority, render/renderer, DAWproject, Studio and Browser patterns;
- identify the least invasive additive extension point for native audio material.

Do not assume the schema shape from conversation context.

### 2. Authority and contract design first

Define machine-valid versioned contracts before UI/runtime implementation.

At minimum evaluate/add bounded contracts equivalent to:

```text
audio-asset-v0
audio-material-v0
audio-edit-candidate-v0
audio-edit-authority-result-v0
audio-mix-plan-v0
```

Exact filenames may change for repository reasons.

The design must explicitly answer:

- whether audio material is embedded in the accepted Blueprint extension or referenced through another accepted project object;
- how immutable asset bytes are stored and addressed;
- how asset identity survives project export/reopen;
- exact supported WAV/PCM boundary;
- time unit and sample/timeline conversion policy;
- track/clip uniqueness and ordering;
- gain/pan ranges and laws;
- mute/solo precedence;
- source-bound stale-revision semantics;
- lock/constraint interaction;
- deterministic mix identity.

### 3. Immutable audio asset store

Implement a project-confined asset boundary with:

- validated WAV/PCM import;
- content SHA-256;
- byte length and source format metadata;
- content-addressed immutable storage;
- duplicate-identical content deduplication policy;
- safe filenames/paths independent of untrusted user filenames;
- no path traversal;
- integrity verification on read/use;
- missing/tampered asset fail-closed.

Importing bytes alone must not silently change an accepted creative revision unless the accepted project state is explicitly changed through authority.

### 4. Trusted audio material runtime

Implement accepted audio material with:

- ordered stable audio tracks;
- clips bound to exact assets;
- explicit project timeline position;
- exact source in/out bounds;
- bounded clip gain;
- bounded track gain/pan/mute/solo;
- duplicate-ID and invalid-range rejection.

All reads must be deterministic and integrity checked.

### 5. Source-bound edit authority

Minimum candidate operations:

- add/reference imported clip;
- add audio track;
- move clip;
- trim source in/out;
- set clip gain;
- set track gain;
- set track pan;
- set mute;
- set solo.

Required behavior:

```text
accepted source revision
→ source-bound edit candidate
→ validate asset/material/ranges/locks
→ READY_FOR_PREVIEW or BLOCKED
→ install Preview only
→ accepted HEAD unchanged
→ explicit Accept only
→ one accepted revision advance
```

Stale source and authority bypass must fail closed.

### 6. Deterministic offline mixer

Specify and implement explicitly:

- supported input channel layouts;
- source sample-rate policy;
- clip/timeline sample alignment;
- source-range slicing;
- clip gain;
- track gain;
- pan law;
- mute/solo precedence;
- overlapping clip summation;
- headroom/clipping policy;
- project output channels/sample rate/PCM encoding;
- mix-plan SHA/provenance.

For the supported evidence path, same accepted state + same immutable assets + same declared toolchain must produce byte-identical mix evidence where the implementation claims determinism.

### 7. Studio service and localhost API

Expose only bounded project-confined operations:

- audio material view;
- asset import/reference operation under explicit authority semantics;
- audio edit Preview;
- existing explicit Accept/Discard lifecycle;
- accepted/pending mix audition route;
- exact asset/mix provenance inspection.

Do not create a second acceptance system.

### 8. Browser arrangement + mixer surface

Add the minimum useful real Browser workflow:

- audio track rows;
- clip timeline representation;
- exact clip/asset provenance inspection;
- bounded move/trim/gain interaction;
- track gain/pan/mute/solo controls;
- clear ACCEPTED vs PREVIEW state;
- explicit Accept/Discard using existing authority;
- accepted/pending mix audition;
- no hidden project write from simple selection/drag audition state.

A waveform visualization may be derived if helpful but is not itself canonical and is not required for v0 acceptance.

### 9. Persistence and restart/reopen

Prove:

- accepted audio tracks/clips survive restart;
- exact asset references/hashes survive restart;
- no asset is rewritten during open/audition;
- deterministic accepted mix identity is reproduced after reopen;
- missing/corrupt media is surfaced truthfully and blocks invalid mix claims.

### 10. Deterministic test matrix

At minimum:

- valid supported WAV import;
- unsupported WAV/codec fail closed;
- duplicate identical asset policy;
- tampered asset fail closed;
- missing asset fail closed;
- path traversal rejection;
- valid track/clip material;
- duplicate IDs rejected;
- clip source overrun rejected;
- move/trim/gain/mixer Preview leaves HEAD unchanged;
- stale candidate blocked;
- explicit Accept advances once;
- mute/solo precedence exact;
- pan/gain exact within declared policy;
- overlapping clip summing exact;
- deterministic mix repeatability;
- restart/reopen identity;
- previous note/automation/Compare semantics unchanged.

### 11. Real-Chromium evidence

Prove a visible end-to-end path:

```text
open project
→ inspect/import bounded audio asset
→ create/reference audio track + clip through Preview
→ audition pending mix
→ Accept
→ move/trim or mixer change through Preview
→ Accept or Discard
→ reopen
→ verify accepted arrangement + mixer + exact mix provenance
```

Record console/page/request failures explicitly.

### 12. Permanent CI and promotion

Add one dedicated permanent evidence workflow without weakening prior gates.

Promotion requires:

- all Issue #95 contract/runtime/browser/evidence tests green;
- all existing permanent M0→Compare workflows green on the exact evidence-bearing head;
- deterministic evidence package and manifest;
- durable validation record;
- successor exact-head rerun after validation-record commit;
- expected-head squash merge;
- Issue #95 completed only after implementation/evidence merge;
- separate state-only closure.

## Explicit non-goals for this mission / 이번 미션 비목표

Do not implement by scope creep:

- microphone/line recording;
- audio-device drivers or low-latency guarantees;
- VST3/AU/CLAP hosting;
- latency compensation;
- arbitrary routing/buses/sends/sidechains;
- time-stretch/warp/pitch shifting;
- destructive editing;
- take lanes/comping;
- mastering suite;
- cloud collaboration;
- installer/signing/commercial release qualification.

These are later commercial-workstation missions.

## Deferred missions preserved / 보류 미션 유지

Still valid after Issue #95:

- `LIVE_PROVIDER_EVIDENCE`;
- automation renderer mapping expansion;
- automation-aware DAW interchange;
- real-time device/recording engine;
- third-party plugin hosting;
- deeper waveform/warp editing;
- production release hardening;
- human usability/perceptual evaluation where claims require it.

## Maximum intended outcome / 최대 의도 결과

> **MUSICA can own immutable imported audio assets as explicit project references, arrange them as accepted audio clips on stable audio tracks, apply bounded mixer state, edit them through Preview/Accept authority, and deterministically reproduce the resulting multitrack mix without granting rendered audio or Browser state reverse authority.**

This remains a target claim until Issue `#95` is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
