# MRAM-R2 Validation — Native Mixer Automation Target Mapping & Deterministic Routed Execution v0

## Scope

Issue #124 under parent Issue #115.

MRAM-R2 extends the validated M7 typed automation authority model to bounded stable native mixer targets and proves that accepted audio-track/routing-node gain and pan automation is source-bound, explicitly accepted, deterministically lowered into frame-domain execution, and actually applied by the MRAM-R1 routed offline mixer.

## Evidence-bearing implementation head

- exact implementation/evidence head: `6fdc2a38b59886ebd41fe38d2f293363d3bbec77`
- permanent workflow count: **23**
- exact-head result: **23/23 SUCCESS**
- one initial M5-R4 failure occurred before tests at external `Provision exact FluidSynth 2.6.0`; the failed job alone was rerun on the same exact head and completed SUCCESS through provisioning, tests, evidence generation and artifact upload
- dedicated workflow: **MRAM-R2 Native Mixer Automation Evidence**
- dedicated run: `35615197638` — **SUCCESS**
- artifact ID: `10646022648`
- artifact name: `musica-mram-r2-native-mixer-automation-evidence`
- artifact ZIP SHA-256: `03b13c8a2c1bc1c84ed248b8891ae3626532723197359509273de56967f2abb0`
- artifact ZIP size: **39,017 bytes**

All 23 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The GitHub artifact declared digest and byte size matched the independently downloaded ZIP exactly:

- SHA-256: `03b13c8a2c1bc1c84ed248b8891ae3626532723197359509273de56967f2abb0`
- bytes: **39,017**

The artifact contains **12 manifest-declared payload files plus `manifest.json`**. Every declared payload matched its manifest SHA-256 and size:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `accepted-automation.json` | `5d1ff7cd322a22968b77b4dce2a0ec3fd099806de52f9f44ae067148e71ffbf4` | 1,411 |
| `changed-automation.json` | `6e0434399ed6651e204451762a12ebc4fa87ea65a73c2ec5e0b28561d632ca47` | 1,412 |
| `changed-native-automation-plan.json` | `6a84e39ef843ff28042d738f4e0ff8cc7407e873ec30ad8956fc7dcddc770d55` | 3,027 |
| `changed-routed-mix.wav` | `3d75ff486f45fdd7d84c80064141faa7d016434b1d239fb832548dc04e889354` | 384,044 |
| `changed-routed-plan.json` | `3612169f211b3525e5cc1e16dbf168e805cdd47fc304b223d01aea7b46e7a372` | 6,957 |
| `contract-hashes.json` | `9e6e74a4d9c369be736f4ab647facf8152f82d4a1338daf4159d68b0713e61a5` | 2,032 |
| `generic-automation-execution.json` | `c9e479b584b57e340536ad7d3a86f0b968eeadf762f647953c6c191a68e1f137` | 3,091 |
| `native-automation-plan.json` | `9d6dac4c5c0f0ddb28cdaa35a4e1c4576701e3d09778fc0065d28cea61664c6b` | 3,003 |
| `project.musica.zip` | `4657abec608550bc903fa389f137c95d19d1ebb398de39538aae40b098a50dc9` | 42,699 |
| `proof.json` | `560c9ae9e528ebd8fa165167189719bf332638a96d09397e9160b298155edc66` | 1,745 |
| `routed-mix.wav` | `adf6c52671404161d9b456e1f580feb11ad832baed4aa86c86b916e6a38f8a33` | 384,044 |
| `routed-plan.json` | `d16f78291c2d7d86b2e94820190e08af106c83d3c00e302655d1feae98f35d67` | 6,911 |

The evidence contract inventory was independently compared with the exact GitHub implementation head. All **14/14** schema, implementation, test and workflow files matched both recorded SHA-256 and recorded byte size.

## Self-hash verification

Using MUSICA canonical JSON encoding, including the canonical trailing newline, all derived plan self-hashes independently recomputed exactly:

- accepted native automation plan:
  - declared/recomputed `f711be1003c24ed287f1dda0178e2d1ce7e26758f1d59a874a3fdc6162912e73`
- controlled-change native automation plan:
  - declared/recomputed `734b2c9dd93b5b363b357b65703def65de38c098b88e50fe42cff84ac3b84798`
- accepted routed mix plan:
  - declared/recomputed `1b8b6468c1f7e4800ca4c63e3f9dc204119b9a3f343b29b4bacff062284b90ac`
- controlled-change routed mix plan:
  - declared/recomputed `01255b1ac5ea7b980666081ce0e1db6440ffa599321efb2ab78def4b568d2970`

## Native target identity and lowering proof

The accepted material contains exactly the bounded initial native target classes required by Issue #124:

```text
audio_track / AT-001 / mixer.gain_db
audio_track / AT-001 / mixer.pan
routing_node / BUS-001 / mixer.gain_db
routing_node / BUS-001 / mixer.pan
```

The source automation remains canonical Blueprint material. The native mixer automation plan is explicitly `derived_noncanonical`.

For the evidence fixture at 8,000 Hz and fixed tempo, beat 1.0 lowers deterministically to frame **4,286**. The lowering plan freezes:

- fixed-tempo quarter-note beat source time;
- Decimal round-half-up frame quantization;
- first/last endpoint hold behavior;
- outgoing-point `hold | linear` interpolation;
- absolute automated gain/pan replacement when a native lane exists.

The older generic M7 lowering remains compatible and all four native lanes remain `backend_mapping: {"status":"UNMAPPED"}`; MRAM-R2 does not silently turn the generic lowering package into canonical backend authority.

## Controlled automation-change proof

The accepted automation and controlled-change automation differ in exactly one canonical point value:

```text
AUTO-AT001-GAIN / P1 / value: -3.0 dB → -12.0 dB
```

No other automation-material field changed.

That one accepted automation change changes all required derived identities:

- automation material:
  `5d1ff7cd...71ffbf4` → `6e043439...632ca47`
- native automation plan:
  `f711be10...2912e73` → `734b2c9d...3b84798`
- routed mix plan:
  `1b8b6468...84b90ac` → `01255b1a...8d2970`
- routed WAV:
  `adf6c526...8f8a33` → `3d75ff48...e889354`

This proves that accepted native mixer automation is not merely persisted metadata: it materially controls deterministic routed rendering.

## WAV inspection

Both independently inspected output WAVs are valid deterministic uncompressed stereo PCM:

- channels: **2**
- sample width: **2 bytes**
- sample rate: **8,000 Hz**
- frames: **96,000**
- byte size: **384,044**
- compression: **NONE / PCM**

The accepted and controlled-change WAV SHA-256 values are different exactly as required by the controlled automation edit.

## Project archive and reopen integrity

The nested `project.musica.zip` independently matched its manifest digest:

- SHA-256: `4657abec608550bc903fa389f137c95d19d1ebb398de39538aae40b098a50dc9`
- bytes: **42,699**

Independent archive inspection found:

- **19** content-addressed object files;
- all **19/19** object file contents matched their SHA-256 object names;
- one persisted `refs/heads/main.json`;
- the expected revision lineage from root → accepted audio → accepted routing → accepted native automation → controlled native automation change.

The evidence proof also confirms export/import reopen reproduces exact accepted automation material, native automation plan, routed mix plan, routed WAV and passes full Project integrity verification.

## Proven authority behavior

The evidence proves:

- native targets use stable exact audio-track/routing-node IDs;
- native scope is bounded to `audio_track | routing_node`;
- native parameters are bounded to `mixer.gain_db | mixer.pan`;
- gain uses `decibel [-60, 12]`;
- pan uses `normalized [-1, 1]`;
- native automation requires accepted non-empty routing so audition/render truthfulness is not lost to the flat mixer path;
- native Preview requires Project Engine context;
- Preview binds exact project ID, accepted revision, Blueprint SHA, automation-material SHA, audio-material SHA and routing-material SHA;
- Preview independently rechecks the persisted accepted source, so a forged object carrying the same revision ID fails closed;
- Preview does not mutate accepted HEAD;
- explicit Accept revalidates exact HEAD/source/candidate/audio/routing/target identity;
- generic project commit cannot introduce or change native mixer automation;
- the same Preview cannot be accepted twice;
- a Preview becomes stale after another accepted HEAD advance;
- missing audio-track/routing-node targets fail closed;
- unsupported unit/range/parameter combinations fail closed;
- audio-only native automation without routed execution context fails closed;
- accepted automation survives project export/import and reopen.

## Proven routed execution behavior

The frozen bounded execution order is:

```text
clip gain
→ automated/static track gain + pan
→ inherited track mute/solo semantics
→ track primary output + post-fader sends
→ node input sum
→ automated/static node gain + pan
→ static node mute
→ node primary output + node sends
→ unique master
→ inherited hard clip
→ deterministic PCM16 stereo WAV
```

When a native automation lane is absent for a parameter, the existing static mixer value remains authoritative. When a native lane is present, its accepted absolute value replaces the corresponding static gain/pan parameter for that rendered frame.

Derived lowering plans, routed plans and WAV bytes remain non-canonical and cannot reverse-promote themselves into accepted creative state.

## Compatibility

MRAM-R2 preserves the existing M7 project/part automation model instead of replacing it.

It also preserves MRAM-R1 static routed rendering semantics for revisions with no native mixer automation lanes. Existing audio, note, automation, routing and symbolic compiler gates all remained green on the exact implementation/evidence head.

## Explicit non-claims

This validation does not claim:

- send gain automation;
- mute or solo automation;
- arbitrary routing parameter automation;
- Browser routing/native-automation editing;
- sidechains;
- realtime audio device I/O or realtime callback guarantees;
- recording or monitoring;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- sample-rate conversion;
- warp/time-stretch/pitch shift;
- mastering;
- generalized commercial-release readiness.

## Validation verdict

> **VALIDATED — TRUSTED NATIVE MIXER AUTOMATION TARGET MAPPING & DETERMINISTIC ROUTED EXECUTION v0**

Maximum supported claim:

> **MUSICA can bind accepted typed automation to stable native audio-track and routing-node gain/pan targets, lower that automation deterministically into routed mixer execution, and reproduce the resulting routed plan/WAV exactly while generic commit bypass, stale or forged source state, unsupported configuration, missing targets and unrouted native automation remain fail-closed.**

Promotion remains conditional on all **23** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #124 completion and separate state-only closure pointing to MRAM-R3.

Repository evidence remains authoritative over conversation/model memory.
