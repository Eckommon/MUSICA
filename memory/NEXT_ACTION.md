# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**PLUG-R0 — PLUGIN CONTRACTS & DETERMINISTIC SIMULATED PROCESSOR v0**

Issue #156 — **OPEN**

Parent mission: Issue #155 — **Plugin Hosting & Latency Compensation Foundation v0 — OPEN**

Recording & Monitoring Foundation v0 is completed. The next dependency-safe step in the commercial-workstation sequence is to establish plugin identity/state/execution/latency contracts with a deterministic simulated processor before any real VST3/AU/CLAP binary-hosting claim.

## Canonical base / 공식 기준점

- canonical main after REC-R3 implementation merge:
  ed77897bba8b50a4feaf0742961494dc44545fc6
- Recording & Monitoring parent Issue #142 — **COMPLETED**
- REC-R3 Issue #152 — **COMPLETED**
- REC-R3 PR #154 — **MERGED**
- REC-R3 implementation/evidence exact head:
  8f238170fcf2617683adb159bd42f606c10d4e4a — **32/32 SUCCESS**
- REC-R3 validation-record successor:
  14272648a8c7191270963e5d86197783ba1be1e0 — **32/32 SUCCESS**
- durable validation:
  evidence/REC_R3_VALIDATION.md
- dedicated artifact ID:
  11101801176
- artifact ZIP SHA-256:
  cad4ced5e9781d19f8a531a5362093bfca2546aa0f079293ce20939ece3add9c
- permanent workflow count: **32**

## Inherited authority / 상속 권한

PLUG-R0 inherits:

~~~text
ATCM:
immutable audio assets/tracks/clips
→ static mixer
→ deterministic native mix

MRAM:
accepted routing DAG + native mixer automation
→ deterministic routed processing

RTIO:
provenance-bound realtime plans/callback/transport/runtime
→ derived device/runtime state only

REC:
deterministic capture + runtime-only monitoring
→ trusted recording Preview/Accept
→ immutable accepted recording media
~~~

PLUG-R0 must add plugin representation and deterministic reference execution without creating a new creative authority path.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground current signal/execution boundaries

Inspect at minimum:

- src/musica/routed_mixer.py;
- src/musica/native_mixer.py;
- src/musica/native_mixer_automation.py;
- routing material/plan contracts;
- RTIO realtime execution/callback/transport plans;
- Project Engine material-delta gates;
- accepted Blueprint material schema pattern;
- deterministic evidence/self-hash helpers;
- durable MRAM/RTIO/REC validation records.

Determine the narrowest additive plugin material that preserves existing legacy/no-plugin Blueprint behavior byte-for-byte where possible.

### 2. Freeze plugin descriptor identity v0

Define a versioned descriptor with stable identity such as:

- stable plugin_id;
- format kind, initially explicit simulated/reference only;
- vendor;
- plugin name;
- semantic/version identity;
- processor capability ID/version;
- supported input/output channel layout;
- supported sample-rate policy;
- parameter descriptors;
- declared latency capability;
- deterministic processor identity.

Do not identify plugins by display name alone.

### 3. Freeze accepted plugin instance/state representation

Define stable plugin instance identity:

- instance_id;
- exact owner kind and owner ID;
- exact insertion slot/order;
- descriptor/plugin ID;
- enabled/bypass state;
- canonical parameter values/state;
- optional explicit state-version identity.

Initial owner scope should be the smallest useful exact set, preferably audio track and/or routing node insertion.

Avoid wildcard/name/index-only addressing.

### 4. Preserve accepted mutation authority boundary

PLUG-R0 should **not** yet allow accepted non-empty plugin mutation through generic commit.

Required R0 invariant:

~~~text
legacy/empty plugin material
→ accepted Project compatibility

non-empty plugin material
→ structural validation + deterministic derived execution proof
→ accepted Project mutation remains fail-closed
~~~

A later PLUG-R1 should add source-bound Preview→Accept authority.

### 5. Freeze deterministic simulated processor v0

Prefer one explicit deterministic reference processor that exercises both parameter state and latency semantics.

Recommended v0:

- stereo PCM processing;
- exact source sample-rate match;
- deterministic gain parameter;
- optional fixed-frame delay;
- exact declared latency in frames;
- no resampling;
- no hidden channel conversion;
- no stochastic/noise DSP;
- deterministic forced processing error injection.

The processor implementation must be separately identifiable/versioned.

### 6. Define derived plugin processing plan

Bind exact:

- accepted project ID/revision;
- Blueprint SHA;
- audio material SHA;
- routing material SHA;
- automation material SHA;
- plugin material SHA;
- descriptor/instance/state identity;
- insertion owner/slot/order;
- sample rate/channels/format;
- parameter values;
- bypass state;
- declared latency frames;
- processor implementation ID/version;
- deterministic plan SHA.

The plan remains derived/non-canonical.

### 7. Define exact processing order

Freeze the initial insertion point relative to existing mixer/routing semantics.

For example:

~~~text
clip/source
→ track plugin chain
→ track gain/pan/mute/solo
→ routing output + sends
→ node plugin chain
→ node gain/pan/mute
→ master
→ clipping
~~~

or another explicitly justified ordering.

Do not leave ordering implicit.

### 8. Deterministic controlled-change proof

At minimum prove:

1. baseline no-plugin path remains identical to existing routed output;
2. deterministic plugin instance plan A;
3. deterministic output A;
4. controlled gain/state change → plan/output B;
5. bypass state produces explicitly documented output;
6. fixed declared latency is exact in plan/runtime;
7. independent rerun reproduces exact plan/output hashes.

Prefer numerical checks in addition to hash differences.

### 9. Fail-closed matrix

Reject at minimum:

- unknown plugin/descriptor ID;
- duplicate instance ID;
- invalid owner/slot;
- unsupported owner kind;
- unsupported channels;
- sample-rate mismatch;
- unsupported parameter ID;
- out-of-range parameter;
- invalid bypass/state;
- malformed/non-canonical instance ordering;
- plugin material hash mismatch;
- forced processor error;
- missing/corrupt source asset;
- invalid routing graph;
- generic accepted-plugin mutation bypass.

### 10. Reopen exactness

Export/import or reopen must reproduce:

- exact plugin descriptor/instance/state identity;
- exact plugin material SHA;
- exact derived processing plan SHA;
- exact deterministic processed output SHA.

Runtime processor objects remain reconstructable derived state, not persisted creative authority.

### 11. Dedicated evidence and permanent gate

Add a dedicated PLUG-R0 workflow without weakening the existing **32** permanent gates.

Expected total: **33** permanent workflows.

Evidence should include:

- descriptor/state material;
- processing plan;
- baseline and processed output;
- controlled-change/bypass output;
- forced-error proof;
- source/contract hash inventory;
- project/reopen proof;
- exact manifest/self-hash verification.

### 12. Promotion

PLUG-R0 promotion requires:

- implementation/evidence complete;
- dedicated PLUG-R0 gate green;
- all 33 permanent workflows green on exact evidence-bearing head;
- independent artifact digest/manifest/hash inspection;
- durable PLUG-R0 validation record;
- all 33 workflows green again on the validation successor;
- expected-head squash merge;
- Issue #156 completed;
- separate state-only closure to PLUG-R1.

## PLUG-R0 non-goals / 비목표

Do not implement or claim in R0:

- real VST3/AU/CLAP binary loading;
- host plugin scanning/installation;
- arbitrary plugin UI/editor embedding;
- third-party state chunks;
- untrusted plugin sandboxing;
- generalized plugin parameter automation;
- sidechain/bus negotiation;
- arbitrary-graph latency compensation;
- sample-rate conversion;
- commercial third-party compatibility.

## Maximum intended PLUG-R0 outcome

> **MUSICA can describe stable bounded plugin instances and state, lower them into an exact deterministic simulated processing plan with explicit latency and capability constraints, and reproduce derived output exactly while accepted plugin mutation remains closed and runtime/output state remains non-canonical.**

This remains a target claim until PLUG-R0 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
