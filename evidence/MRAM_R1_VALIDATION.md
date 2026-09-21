# MRAM-R1 Validation — Trusted Routing Preview→Accept & Deterministic Routed Offline Mixer v0

## Scope

Issue #121 under parent Issue #115.

MRAM-R1 opens a bounded trusted accepted-routing authority path through source-bound Preview → explicit Accept, then makes the deterministic native offline mixer execute the exact accepted routing DAG while keeping routed plans and rendered WAV files derived/non-canonical.

## Evidence-bearing implementation head

- exact head: `91d9629b4b017a70f30bb53d273890e22cd87734`
- permanent workflow count: **22**
- exact-head result: **22/22 SUCCESS**
- dedicated workflow: **MRAM-R1 Routing Authority & Routed Mixer Evidence**
- dedicated run: `35307240384` — **SUCCESS**
- artifact ID: `10532212394`
- artifact name: `musica-mram-r1-routing-authority-mixer-evidence`
- artifact ZIP SHA-256: `4a59898baf16af1d7f26d14a3f31868fc573ee028d996f5c62ba5a8881be6da0`
- artifact ZIP size: **23,467 bytes**

All 22 permanent workflows completed successfully on this exact head before this durable validation record was added.

## Independent artifact inspection

The downloaded artifact ZIP digest matched the GitHub artifact digest exactly.

Manifest payload verification passed for all **9/9** declared payload files:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `accepted-routing.json` | `ed584991d3bd36d86ad298e7f6088b79ddb61316f5da5ec0da202bafbf5f20db` | 773 |
| `changed-routed-mix.wav` | `2ab53f16ab6f73ffc70dd92bd29abc767bce3176105efbfad8a5f617b74f2630` | 384,044 |
| `changed-routed-plan.json` | `56f77f037f447638611152abc5c502d7face8975d81cb23e9d7f7e023d791470` | 3,658 |
| `changed-routing.json` | `8a8bedb26a65c2d03234ad94698221904fb37c7808d859619bfaddd3cfddb82d` | 772 |
| `contract-hashes.json` | `64a3cfc97eb7b067552f66af846d64e57bf19b875d8011dcfb7bea263d805bca` | 2,783 |
| `project.musica.zip` | `e855c524f0714bafe36c0b43135c00e4fbd210d4b547a189a2bb7ca3f2ae0ac1` | 32,565 |
| `proof.json` | `408a2b97884639055196723e4dcfc44fc8c4eced434ea5695bf87769563f351b` | 1,289 |
| `routed-mix.wav` | `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4` | 384,044 |
| `routed-plan.json` | `67e7569cb1f345d812295519b7261ed0715d88c5b967dd595f2700f090049eb0` | 3,634 |

The evidence contract hash inventory was independently checked against the exact GitHub implementation head. All **20/20** listed schema, implementation, test and workflow files matched their recorded SHA-256 and byte sizes.

The routed-mix plan self-hashes were independently recomputed using MUSICA canonical JSON bytes, including the canonical trailing newline:

- accepted routing plan declared/recomputed:
  `a4a67b79a2a402b08280b7f9c39d291f7b669800be39d558e9a1bc9fed2bb74e`
- controlled-change plan declared/recomputed:
  `5d7aeab03126aab73ff14c38bf5018a692951c2ff656d6909dba1c9219d77e88`

The two evidence WAVs were independently parsed as valid deterministic stereo PCM16 WAV:

- channels: **2**
- sample width: **2 bytes**
- sample rate: **8,000 Hz**
- frames: **96,000**
- byte size: **384,044** each

Their SHA-256 values differ exactly as required by the controlled routing change.

The nested `project.musica.zip` was independently unpacked. Its content-addressed object files matched their SHA-256 object names, and the persisted revision lineage/references were present for reopen inspection.

## Controlled routing-change proof

The accepted routing material and controlled changed routing material differ in exactly one routing parameter:

```text
SEND-001 gain_db: -12.0 → -3.0
```

That single accepted routing change changes the derived identities:

- routing material:
  `ed584991...f5f20db` → `8a8bedb2...ddb82d`
- routing plan:
  `c3bd6ce5...d2e943` → `5482b67b...4ea7b`
- routed mix plan:
  `a4a67b79...2bb74e` → `5d7aeab0...77e88`
- routed WAV:
  `49dbffca...ba2a4` → `2ab53f16...f2630`

This demonstrates that routing is not merely persisted metadata: the accepted post-fader send state materially controls the deterministic routed render.

## Proven bounded authority behavior

The evidence proves:

- routing edit candidates bind exact project ID, source revision, source Blueprint SHA and source routing-material SHA;
- candidate application occurs on a copy for Preview;
- Preview leaves accepted HEAD unchanged;
- explicit trusted Accept revalidates source/head/graph/assets;
- accepted routing advances exactly once;
- a second Accept of the same stale Preview fails closed;
- a stale Preview after another HEAD advance fails closed;
- generic project commit cannot introduce or change non-empty routing;
- cycle candidates fail closed;
- missing-target candidates fail closed;
- accepted routing persists through export/import and reopen;
- reopen reproduces exact accepted routing, routed plan and routed WAV;
- accepted routing remains compatible with existing audio, note and automation edit paths;
- the symbolic compiler preserves existing IR behavior and does not gain routing mutation authority.

## Proven routed mixer behavior

The routed native offline mixer proves:

- exact accepted revision/audio/routing binding;
- exact track primary output routing;
- bus/group/return/master topology;
- exactly one master sink;
- explicit post-fader sends;
- inherited ATCM-R2 track gain/pan/mute/solo semantics;
- deterministic node input summing and static node gain/pan/mute;
- deterministic node primary output and send propagation;
- inherited hard clipping before PCM16 conversion;
- deterministic stereo PCM16 WAV output;
- repeat-exact routed plan;
- repeat-exact routed WAV;
- controlled send-gain change alters both routed plan and WAV;
- derived plan/runtime/rendered audio do not gain reverse canonical authority.

The frozen bounded execution order is:

```text
clip gain
→ track gain/pan/mute/solo using inherited R2 rules
→ track primary output + post-fader sends
→ node input sum
→ node static gain/pan/mute
→ node primary output + node sends
→ unique master
→ inherited hard clip
→ deterministic PCM16 stereo WAV
```

## Studio truthfulness

The implementation also closes the previously misleading audition boundary: Studio audition now uses the routed mixer for accepted non-empty routing rather than silently falling back to the flat native mix.

This does not make the Studio/browser runtime canonical. It only ensures that an audition of accepted routed state truthfully reflects that state.

## Authority boundary

MRAM-R1 grants only a narrow trusted routing acceptance path.

```text
exact accepted revision
→ source-bound routing candidate
→ Preview without mutation
→ explicit trusted Accept
→ protected routing-authorized Project Engine commit
→ accepted routing revision
→ deterministic derived routed plan/WAV
```

The following remain non-authoritative:

```text
generic commit
routing runtime object
routed plan
rendered WAV
Browser/Studio state
```

They cannot reverse-author accepted creative routing state.

## Explicit non-claims

This validation does not claim:

- mixer automation mapped to routing/native mixer parameters;
- Browser routing editing;
- generalized sidechains;
- realtime audio device callbacks/transport;
- recording/monitoring;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- sample-rate conversion;
- warp/time-stretch/pitch shift;
- mastering;
- generalized commercial release readiness.

## Validation verdict

> **VALIDATED — TRUSTED ROUTING PREVIEW→ACCEPT & DETERMINISTIC ROUTED OFFLINE MIXER v0**

Maximum supported claim:

> **MUSICA can edit bounded explicit routing through source-bound Preview/Accept authority, persist that accepted DAG as creative state, and deterministically render the exact accepted track→node→master signal flow into a byte-reproducible derived offline mix while generic commit paths, stale Previews and invalid topology remain fail-closed.**

Promotion remains conditional on all **22** permanent workflows succeeding again on the exact successor head containing this durable record, followed by expected-head squash merge, Issue #121 completion and separate state-only closure pointing to MRAM-R2.

Repository evidence remains authoritative over conversation/model memory.
