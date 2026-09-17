# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**MRAM-R1 — TRUSTED ROUTING PREVIEW→ACCEPT + DETERMINISTIC ROUTED OFFLINE MIXER**

Parent mission: Issue `#115` — **Mixer Routing & Automation Foundation v0 — OPEN**

MRAM-R0 Issue `#118` is validated, merged and completed. The next dependency-safe step is to open accepted routing authority through the same fail-closed source-bound Preview→explicit Accept model already proven elsewhere, then make the deterministic native mixer consume that accepted routing graph.

Do **not** introduce mixer automation, Browser routing UI, recording, low-latency device I/O or plugin hosting in R1.

## Canonical base / 공식 기준점

- canonical main after MRAM-R0 implementation merge:
  `7e5da8b558c0c4b980f7b6e3061eca9873e65513`
- parent Issue `#115` — **OPEN**
- MRAM-R0 Issue `#118` — **COMPLETED**
- MRAM-R0 PR `#119` — **MERGED**
- R0 pre-validation exact head:
  `1d7c310ba02ef651927ad65cc58f782b1f1b34b6` — **21/21 SUCCESS**
- R0 validation-record successor:
  `50701b45fd4c2cb9f95a01c8ec9a8b7d8ccb9956` — **21/21 SUCCESS**
- durable validation: `evidence/MRAM_R0_VALIDATION.md`
- dedicated artifact ZIP SHA:
  `bfe38c8d8794e98a904155ee2f31353fe585fddeef3faeeaae2b98a17224b923`
- routing plan self-hash from R0 evidence:
  `4d756500bb806be98b25f3c7f2e21cb3b08b36ea652795002a89edcdedbe46e8`

Permanent workflow count at the R0 validated state: **21**.

## Inherited authority / 상속 권한

R1 inherits:

```text
ATCM:
immutable audio assets
→ accepted audio tracks/clips
→ accepted static per-track mixer
→ deterministic flat native mix
→ Browser truth
→ restart/reopen

MRAM-R0:
explicit bounded routing graph contract
→ DAG/cycle/target validation
→ deterministic derived signal-flow plan
→ non-empty accepted routing still fail-closed
```

R1 opens only the missing trusted accepted-routing boundary and routed deterministic mixer execution.

## Exact implementation order / 정확한 구현 순서

### 1. Inspect the actual protected native-audio authority path

Before writing routing acceptance code, inspect:

- `src/musica/project.py`;
- `src/musica/audio_edit.py`;
- `src/musica/audio_mixer_edit.py`;
- `src/musica/audio_contracts.py`;
- `src/musica/routing_contracts.py`;
- `src/musica/native_mixer.py`;
- R1/R2 native-audio authority tests;
- `evidence/MRAM_R0_VALIDATION.md`.

Identify the exact internal mechanism by which generic project commit is prevented from mutating native-audio accepted state and how the trusted audio accept path receives narrow authorization.

Do **not** authorize routing merely by adding a provenance string.

### 2. Freeze routing edit candidate v0

Add a source-bound candidate contract containing at least:

- candidate ID/version;
- exact project ID;
- exact source revision ID;
- source Blueprint SHA;
- source routing-material SHA;
- actor/reason;
- ordered operation list;
- `preview_only: true`.

Recommended minimum operations:

- `ADD_NODE` for bus/group/return;
- `REMOVE_NODE`;
- `SET_NODE_OUTPUT`;
- `SET_TRACK_OUTPUT`;
- `ADD_SEND`;
- `REMOVE_SEND`;
- `SET_SEND_GAIN`;
- static `SET_NODE_GAIN`, `SET_NODE_PAN`, `SET_NODE_MUTE` if those operations remain fully bounded.

Do not add automation points in this contract.

### 3. Build routing Preview

The Preview builder must:

1. validate the candidate schema;
2. load the exact source accepted revision;
3. re-check project ID / source revision / source Blueprint SHA / routing-material SHA;
4. apply operations only to a copy;
5. validate exact current audio track identities;
6. validate resulting routing material/DAG;
7. validate missing/corrupt asset/project constraints as needed;
8. construct a candidate Blueprint;
9. keep accepted HEAD unchanged;
10. return machine-readable changed node/send/track-route IDs and hashes.

Blocked candidates must not produce accepted state.

### 4. Add a trusted Project Engine routing commit boundary

Generic `project.commit_revision(...)` must continue failing on a non-empty routing change.

Implement a narrow internal path callable only by the trusted routing acceptance function.

The trusted path must:

- revalidate current HEAD equals Preview source;
- revalidate source Blueprint/routing hashes;
- revalidate the candidate graph against current accepted audio track IDs;
- revalidate project integrity/assets;
- reject stale Preview;
- advance exactly once;
- write normal durable revision/audit state;
- not grant future Browser/runtime callers generic routing authority.

### 5. Explicit Accept / discard behavior

Required:

```text
Preview
→ accepted HEAD unchanged
→ discard: no mutation

Preview
→ explicit trusted Accept
→ exact source revalidation
→ exactly one accepted revision advance
```

A second Accept of the same stale Preview must fail closed.

### 6. Extend deterministic native mixer for accepted routing

Do not replace R2 numeric semantics.

Build a routed plan that binds:

- accepted project/revision/Blueprint;
- accepted audio material;
- accepted routing material;
- exact immutable audio assets;
- R0 deterministic routing-plan hash;
- ordered track sources;
- node topology;
- node static mixer values;
- post-fader sends;
- exact summing/application order;
- master sink;
- output format/policy.

Recommended bounded execution order:

```text
clip gain
→ track gain/pan/mute/solo using inherited R2 rules
→ track primary output + post-fader sends
→ node input sum
→ node static gain/pan/mute
→ node primary output
→ unique master
→ inherited hard clip → PCM16 stereo WAV
```

Freeze any subtle send/pan semantics explicitly in the plan before claiming routed render support.

### 7. Fail-closed routed execution

Reject at least:

- routing cycle;
- unknown node;
- unknown track route;
- duplicate identity;
- missing/ambiguous master;
- unsupported node/send state;
- missing/corrupt audio asset;
- source sample-rate mismatch under existing no-resampling v0 policy;
- invalid source/head binding;
- stale Preview;
- direct generic commit bypass.

### 8. Deterministic evidence

Evidence should prove:

```text
accepted flat native-audio source
→ routing candidate
→ Preview
→ HEAD unchanged
→ deterministic preview graph identity
→ explicit Accept
→ exactly one HEAD advance
→ accepted routing graph exact
→ routed plan A + WAV A
→ independent routed plan B + WAV B
→ exact plan/WAV equality
→ controlled routing change causes exact documented output change
→ reopen project
→ same accepted routing + plan/WAV hashes
→ stale Preview / cycle / missing target / generic commit bypass fail closed
```

Rendered WAV remains derived/non-canonical.

### 9. Permanent gate

Add a dedicated MRAM-R1 permanent workflow without weakening the existing **21** gates.

Expected total after R1: **22**.

### 10. Promotion

R1 promotion requires:

- implementation/evidence complete;
- dedicated MRAM-R1 gate green;
- all 22 permanent workflows green on exact evidence-bearing head;
- independent artifact digest/manifest/hash inspection;
- durable `evidence/MRAM_R1_VALIDATION.md`;
- all 22 workflows green again on exact validation-record successor head;
- expected-head squash merge;
- R1 Issue completed;
- separate state-only closure that points to MRAM-R2.

## MRAM-R1 non-goals / 비목표

Do not implement or claim in R1:

- automation lanes mapped to audio tracks/buses/sends;
- Browser routing editing;
- sidechains;
- realtime callbacks or device transport;
- recording/monitoring;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- resampling;
- warp/time-stretch/pitch shift;
- mastering;
- generalized commercial release readiness.

## Successor after R1

If R1 validates cleanly, exact next rung:

> **MRAM-R2 — extend the existing typed automation authority/lowering model to supported native mixer targets, starting with track and routing-node gain/pan under explicit stable target identity, units/ranges and interpolation/lowering semantics.**

Do not retrofit automation scope casually. The current automation model is `project|part`; MRAM-R2 must version or safely extend target semantics with backward-compatible evidence.

## Maximum intended R1 outcome

> **MUSICA can edit bounded explicit routing through source-bound Preview/Accept authority, persist that accepted DAG as creative state, and deterministically render the exact accepted track→node→master signal flow into a byte-reproducible derived offline mix while generic commit paths, stale Previews and invalid topology remain fail-closed.**

This remains a target claim until R1 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
