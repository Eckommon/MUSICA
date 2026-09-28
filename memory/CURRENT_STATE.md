# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → NATIVE AUDIO FOUNDATION VALIDATED → MIXER ROUTING & AUTOMATION FOUNDATION IN FINAL BROWSER/LIFECYCLE RUNG**

Long-term governing target:

> **MUSICA should grow into a general-purpose, commercially usable music production workstation while preserving its AI-native authority, inspectability, reproducibility and programmability.**

This remains a product target, not a claim that MUSICA is already a complete commercial DAW.

## Canonical baseline / 공식 기준점

### Audio Track / Clip / Mixer Foundation v0

Parent Issue `#95` — **COMPLETED — BOUNDED FOUNDATION ONLY**

Validated ATCM rungs:

- R0 Issue `#97` / PR `#98` — **COMPLETED / MERGED / VALIDATED**
- R1 Issue `#99` / PR `#101` — **COMPLETED / MERGED / VALIDATED**
- R2 Issue `#102` / PR `#104` — **COMPLETED / MERGED / VALIDATED**
- R3 Issue `#105` / PR `#107` — **COMPLETED / MERGED / VALIDATED**
- R4 Issue `#111` / PR `#114` — **COMPLETED / MERGED / VALIDATED**
- native-audio foundation state merge: `712769f2ec469083d5c08fca8006a4b6e419a4d0`

The bounded native-audio foundation has durable end-to-end evidence for immutable assets, accepted track/clip authority, deterministic multitrack mix, truthful Browser interaction and restart/reopen persistence/integrity.

## Current commercial-workstation mission

Parent Issue `#115` — **Mixer Routing & Automation Foundation v0 — OPEN**

Selected bounded rung sequence:

```text
MRAM-R0 routing contracts + deterministic graph lowering      VALIDATED
→ MRAM-R1 trusted routing Preview→Accept + routed mixer       VALIDATED
→ MRAM-R2 track/routing-node gain/pan automation mapping      VALIDATED
→ MRAM-R3 Browser routing/automation + reopen lifecycle       CURRENT
→ Issue #115 bounded closure evaluation
```

## MRAM-R0 — validated routing substrate

Issue `#118` / PR `#119` — **COMPLETED / MERGED / VALIDATED**

Canonical implementation merge/main:

> **`7e5da8b558c0c4b980f7b6e3061eca9873e65513`**

Durable validation: `evidence/MRAM_R0_VALIDATION.md`

R0 established explicit bounded routing contracts, stable bus/group/return/master identities, deterministic DAG validation/lowering and fail-closed non-empty accepted routing authority.

## MRAM-R1 — validated trusted routing authority + routed mixer

Issue `#121` — **COMPLETED**

Implementation PR `#122` — **MERGED**

Canonical implementation merge/main:

> **`422f30f78b39b333dd970bf3a20e94e1ba64e7fb`**

Durable validation: `evidence/MRAM_R1_VALIDATION.md`

Key validated behavior includes source-bound routing Preview→Accept, protected Project Engine routing authority, generic-commit bypass rejection, stale Preview rejection, accepted bus/group/return/master routing, post-fader sends, deterministic routed plan/WAV, reopen exactness and truthful Studio routed audition.

## MRAM-R2 — validated native mixer automation target mapping

Issue `#124` — **COMPLETED**

Implementation PR `#125` — **MERGED**

Canonical implementation merge/main:

> **`932b98e64f6e6d0b5464023b79973b1a5b33b65c`**

Durable validation:

- `evidence/MRAM_R2_VALIDATION.md`
- implementation/evidence exact head:
  `6fdc2a38b59886ebd41fe38d2f293363d3bbec77` — **23/23 permanent workflows SUCCESS**
- validation-record successor exact head:
  `7432b2a2c1ee3e4d6fe031ef36cbd8206ace6b11` — **23/23 SUCCESS**
- dedicated workflow: **MRAM-R2 Native Mixer Automation Evidence**
- dedicated run: `35615197638` — **SUCCESS**
- artifact ID: `10646022648`
- artifact ZIP SHA-256:
  `03b13c8a2c1bc1c84ed248b8891ae3626532723197359509273de56967f2abb0`
- artifact ZIP size: **39,017 bytes**
- manifest-declared payloads: **12/12 exact SHA-256 + byte size PASS**
- exact Git contract/source/test/workflow inventory: **14/14 SHA-256 + byte size PASS**
- nested project object store: **19/19 object hashes PASS**
- accepted native automation plan self-hash:
  `f711be1003c24ed287f1dda0178e2d1ce7e26758f1d59a874a3fdc6162912e73`
- controlled-change native automation plan self-hash:
  `734b2c9dd93b5b363b357b65703def65de38c098b88e50fe42cff84ac3b84798`
- accepted routed mix plan self-hash:
  `1b8b6468c1f7e4800ca4c63e3f9dc204119b9a3f343b29b4bacff062284b90ac`
- controlled-change routed mix plan self-hash:
  `01255b1ac5ea7b980666081ce0e1db6440ffa599321efb2ab78def4b568d2970`
- accepted routed WAV:
  `adf6c52671404161d9b456e1f580feb11ad832baed4aa86c86b916e6a38f8a33`
- controlled-change routed WAV:
  `3d75ff486f45fdd7d84c80064141faa7d016434b1d239fb832548dc04e889354`

### Validated MRAM-R2 behavior

MRAM-R2 establishes a backward-compatible additive extension of the existing M7 automation family for:

```text
audio_track / stable track_id / mixer.gain_db
audio_track / stable track_id / mixer.pan
routing_node / stable node_id / mixer.gain_db
routing_node / stable node_id / mixer.pan
```

The validated authority/execution chain is:

```text
exact accepted routed revision
→ source-bound native automation candidate
→ Preview / accepted HEAD unchanged
→ persisted source + Blueprint/automation/audio/routing hash validation
→ explicit Accept
→ protected native-automation Project Engine commit
→ accepted automation revision
→ deterministic beat→frame lowering
→ routed mixer track/node gain+pan execution
→ deterministic derived routed plan/WAV
```

Additional validated fail-closed behavior:

- generic commit cannot introduce/change native mixer automation;
- same Preview cannot be accepted twice;
- stale Preview after HEAD advance is rejected;
- forged same-revision parent objects are rejected by persisted-source binding;
- missing track/node identities are rejected;
- unsupported unit/range/parameter combinations are rejected;
- native mixer automation without accepted non-empty routing is rejected;
- generic M7 lowering remains explicitly `UNMAPPED`;
- export/import reopen reproduces automation identity, native lowering, routed plan and WAV exactly.

Controlled evidence changes exactly one canonical point:

```text
AUTO-AT001-GAIN / P1: -3.0 dB → -12.0 dB
```

and proves corresponding native-plan, routed-plan and WAV identity changes.

### Maximum validated MRAM-R2 claim

> **MUSICA can bind accepted typed automation to stable native audio-track and routing-node gain/pan targets, lower that automation deterministically into routed mixer execution, and reproduce the resulting routed plan/WAV exactly while generic commit bypass, stale or forged source state, unsupported configuration, missing targets and unrouted native automation remain fail-closed.**

## Exact current rung / 현재 정확한 단계

The current rung is:

> **Issue #126 — MRAM-R3: Browser Routing & Native Automation Surface + Reopen Lifecycle v0**

R3 must project the already validated routing + native automation authority into a real Browser/Studio surface without creating a Browser-only source of truth.

Required direction:

```text
accepted routing + native automation
→ derived Browser inspection
→ typed Browser edit proposal
→ existing routing/automation Preview engines
→ PREVIEW / HEAD unchanged
→ explicit Accept
→ existing trusted Project Engine boundary
→ exact accepted routed audition
→ process/service restart
→ reopen
→ same routing/automation identities + plan/WAV hashes
```

R3 should prefer the smallest complete truthful surface and reuse existing candidate/Preview/Accept engines.

## Current important non-claims / 현재 주요 비주장

Until separately validated, do not claim:

- Browser routing/native mixer automation editing;
- send-gain automation beyond the current static routing send control;
- mute/solo automation;
- sidechains;
- realtime ASIO/CoreAudio/WASAPI device operation;
- microphone/line recording or monitoring;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- implicit sample-rate conversion;
- warp/time-stretch/pitch shift or destructive waveform editing;
- mastering-grade processing;
- generalized commercial release readiness or production SLA;
- cloud/multi-user creative authority;
- perceptual superiority.

## Exact next phase / 다음 단계

> **Implement Issue #126 from canonical main `932b98e64f6e6d0b5464023b79973b1a5b33b65c`: re-ground the current Studio/Browser routing and automation projection paths, add the smallest truthful stable-ID inspection/edit surface that delegates to existing routing/automation Preview→Accept authority, prove exact routed audition plus restart/reopen lifecycle in real Chromium, then evaluate parent Issue #115 for bounded closure.**

See `memory/NEXT_ACTION.md` for the exact execution order.

**Repository evidence remains authoritative over conversation/model memory.**
