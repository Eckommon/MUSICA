# Post-Compare Successor Selection / Compare 이후 후속 미션 선정

## Status / 상태

**RATIFIED TARGET — AUDIO TRACK / CLIP / MIXER FOUNDATION v0**

This record completes the successor review required after the accepted-revision Compare closure. It selects exactly one bounded implementation mission from the current repository state and the long-term commercial-workstation objective.

- canonical review base: `f6128a8b5dcaae5f4cb4e05ad21da415b34afaa5`
- selected implementation Issue: `#95`
- predecessor: **Accepted Revision A/B Compare & Human Decision Surface v0 — VALIDATED — BOUNDED READ-ONLY DECISION SURFACE**
- long-term target: `docs/COMMERCIAL_WORKSTATION_TARGET.md`
- selected capability: **Audio Track / Clip / Mixer Foundation v0**
- milestone numbering: **no inferred `M8` or other numeric milestone**

## 1. Decision context / 결정 배경

The core thesis loop is now boundedly validated:

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
```

The next problem is therefore not another missing loop step. It is how to expand MUSICA from a bounded AI-native programmable workstation into a **general-purpose, commercially usable music production workstation** without losing its authority, reproducibility and evidence model.

Repository inspection shows strong existing coverage for:

- intent and Blueprint authority;
- semantic creation/editing;
- immutable project revisions and branches;
- exact-note editing;
- automation authority/editing/lowering;
- deterministic rendering and media artifacts;
- Browser Studio;
- DAWproject interchange and exact-note reconciliation;
- accepted-revision A/B comparison.

The repository does not yet contain a native audio asset/clip/track/multitrack mixer domain. Rendered WAVs exist as derived artifacts, but they are not a general-purpose editable audio arrangement substrate.

## 2. Serious candidate comparison / 주요 후보 비교

| Candidate | Product leverage | Prerequisite readiness | Authority / dependency risk | Sequencing judgment |
|---|---|---|---|---|
| **A. Audio Track / Clip / Mixer Foundation** | Very high for general-purpose production | High enough: project/version/render/Browser patterns already exist | Moderate and internally controllable | **SELECTED** — creates substrate required by several later DAW capabilities |
| B. Automation renderer mapping expansion | High for programmability | High | Moderate backend-semantic expansion | Deferred — useful, but does not fill the missing native audio-production substrate |
| C. `LIVE_PROVIDER_EVIDENCE` | High proof value for AI deployment | Structurally ready | External credential/network/model dependency | Deferred — proves an existing provider boundary rather than adding missing DAW substrate |
| D. Automation-aware DAW interchange | High professional interoperability value | Partial | High external-state reconciliation complexity | Deferred until native audio/mixer ownership is clearer |
| E. VST3/CLAP/AU plugin host foundation | Very high commercial workstation value | Insufficient internal signal-path substrate | High runtime/platform/third-party state risk | Deferred until track/mixer/signal-path foundation exists |
| F. Real-time device/recording engine | Very high workstation value | Partial | High OS/audio-driver/latency risk | Deferred until accepted audio track/clip semantics are established |
| G. Packaging/signing/release hardening | High distribution value | Possible | Operational rather than musical | Deferred — commercial distribution should harden a more complete production core |
| H. Human usability/perceptual study | Important for later product claims | Possible | Human-study/evaluation dependency | Deferred — not a substitute for missing production primitives |

## 3. Why Audio Track / Clip / Mixer is first / 선정 이유

A commercial music-production workstation requires a trustworthy native representation of audio placed in time and mixed through explicit track state.

Without that substrate:

- recording has no stable native destination model;
- waveform/non-destructive clip editing has no canonical object to edit;
- plugin hosting has no trustworthy track/signal-path attachment model;
- buses/routing/latency compensation lack an internal graph to extend;
- automation expansion risks targeting ad hoc renderer state rather than stable production objects;
- DAW interchange remains mostly an external adapter rather than mapping to a rich internal workstation model.

By contrast, a bounded audio-track/clip/mixer foundation can reuse the strongest existing MUSICA patterns:

```text
immutable content identity
+ typed project state
+ source-bound Preview edits
+ explicit Accept
+ deterministic derived rendering
+ Browser inspection
+ restart/reopen evidence
```

## 4. Ratified mission / 비준 미션

> **Allow an accepted MUSICA project to own immutable imported audio assets by exact identity, arrange those assets as stable non-destructive clips on audio tracks, maintain bounded track mixer state, edit that state through Preview/Accept authority, and deterministically reproduce a multitrack stereo mix.**

Implementation authority is Issue `#95`.

## 5. Native audio authority model / Native audio 권한 모델

### Accepted project state may reference

- immutable content-addressed audio assets;
- stable audio track IDs/order/names;
- stable clip IDs;
- clip → asset identity;
- timeline placement;
- source in/out region;
- bounded clip gain;
- track gain/pan/mute/solo.

### Derived execution remains non-canonical

```text
accepted audio material
→ validated asset resolution
→ deterministic mix plan
→ decoded/mixed samples
→ track or stereo render
→ Browser audition/meter/waveform projection
```

No decoded buffer, waveform cache, meter, renderer output or Browser manipulation may silently become accepted state.

## 6. v0 format boundary / v0 포맷 경계

The first implementation should prefer a narrow deterministic source format rather than pretend to support arbitrary media.

Recommended v0 import boundary:

- WAV container;
- PCM integer source encoding only for the first evidence path;
- explicitly supported sample rates/channel counts declared in the contract;
- deterministic conversion/mix behavior documented;
- unsupported codecs/formats fail closed rather than being silently transcoded.

Broader formats may follow after the internal authority and mixer model are stable.

## 7. v0 edit boundary / v0 편집 경계

Minimum trusted edits:

- import/reference an audio asset;
- add an audio track;
- add a clip referencing an exact asset;
- move a clip on the project timeline;
- trim clip source in/out non-destructively;
- change bounded clip gain;
- change track gain/pan/mute/solo.

Each mutation must be source-bound and Preview-only until explicit Accept.

Delete/reorder/duplicate operations may be included if the implementation remains bounded and evidence-friendly, but are not allowed to dilute the mandatory path above.

## 8. Mix semantics / 믹스 의미론

The implementation must specify instead of guessing:

- timeline/sample alignment policy;
- channel conversion policy within the v0 supported set;
- clip gain law;
- track gain law;
- pan law;
- mute and solo precedence;
- overlap summing behavior;
- headroom/clipping behavior;
- output sample rate/bit-depth policy;
- deterministic render-plan identity.

A mix whose semantics are not explicitly declared cannot support a reproducibility claim.

## 9. Browser scope / Browser 범위

The Browser Studio surface must be sufficient to prove this is a usable production primitive rather than a hidden data structure.

Minimum visible path:

```text
accepted project
→ audio track list
→ clip timeline representation
→ track gain/pan/mute/solo
→ source/provenance identity
→ Preview distinction
→ explicit Accept
→ accepted mix audition
```

A first-pass waveform may be a derived visualization if implemented, but waveform display itself is not required to become canonical data.

## 10. Required failure modes / 필수 실패 폐쇄

Fail closed on at least:

- missing asset;
- asset bytes whose hash no longer matches identity;
- unsupported/invalid WAV structure;
- clip source range outside source duration;
- duplicate track/clip IDs;
- invalid time/gain/pan ranges;
- stale source revision for an edit candidate;
- any edit that would bypass explicit Accept;
- any path traversal or asset reference outside the project asset boundary.

## 11. Permanent evidence requirements / 영구 검증 요구

Promotion requires:

1. machine-valid asset/material/edit/mix schemas;
2. deterministic trusted-core tests;
3. exact asset SHA/size/format provenance;
4. deterministic offline mixdown A/B byte reproduction;
5. source-bound Preview and stale-source failure proof;
6. explicit Accept advances exactly one revision;
7. reopen/restart preserves accepted audio material and reproducible mix identity;
8. real-Chromium arrangement/mixer workflow evidence;
9. fail-closed corrupt/missing media evidence;
10. permanent workflow wiring;
11. all prior permanent M0→Compare workflows green on the exact evidence head;
12. durable validation record;
13. expected-head merge and separate state-only closure.

## 12. Explicit non-goals / 명시적 비목표

Do not expand Issue `#95` into:

- microphone/line recording;
- ASIO/CoreAudio/WASAPI device engine;
- low-latency performance claims;
- plugin hosting;
- latency compensation;
- arbitrary buses/sends/sidechains;
- time-stretch/warp/pitch shifting;
- destructive waveform editing;
- comping/take lanes;
- mastering-grade DSP;
- cloud collaboration;
- commercial-release readiness itself.

These remain later workstation domains.

## 13. Deferred candidates remain valid / 보류 후보 유지

This selection does not reject:

- `LIVE_PROVIDER_EVIDENCE`;
- automation renderer expansion;
- automation-aware DAW reconciliation;
- real-time device/recording engine;
- VST3/CLAP/AU hosting;
- release hardening;
- usability/perceptual evaluation.

They must be revisited against the new native audio foundation after Issue `#95` is state-closed.

## 14. Maximum intended claim / 최대 의도 주장

> **MUSICA can own immutable imported audio assets as explicit project references, arrange them as accepted audio clips on stable audio tracks, apply bounded mixer state, edit them through Preview/Accept authority, and deterministically reproduce the resulting multitrack mix without granting rendered audio or Browser state reverse authority.**

This is a target claim only until Issue `#95` is implemented, independently evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
