# Current State / 현재 상태

## Project phase / 프로젝트 단계

**CORE PRODUCT LOOP BOUNDEDLY VALIDATED → NATIVE AUDIO FOUNDATION VALIDATED → MIXER ROUTING & AUTOMATION EXPANSION IN PROGRESS**

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
→ MRAM-R2 track/routing-node gain/pan automation mapping      CURRENT
→ MRAM-R3 Browser routing/automation + reopen lifecycle
→ Issue #115 bounded closure evaluation
```

## MRAM-R0 — validated routing substrate

Issue `#118` / PR `#119` — **COMPLETED / MERGED / VALIDATED**

Canonical implementation merge/main:

> **`7e5da8b558c0c4b980f7b6e3061eca9873e65513`**

Durable validation: `evidence/MRAM_R0_VALIDATION.md`

Key promotion facts:

- pre-validation head `1d7c310ba02ef651927ad65cc58f782b1f1b34b6` — **21/21 SUCCESS**
- validation successor `50701b45fd4c2cb9f95a01c8ec9a8b7d8ccb9956` — **21/21 SUCCESS**
- artifact ZIP SHA-256 `bfe38c8d8794e98a904155ee2f31353fe585fddeef3faeeaae2b98a17224b923`

R0 established explicit bounded routing contracts, stable bus/group/return/master identities, deterministic DAG validation/lowering and fail-closed non-empty accepted routing authority.

## MRAM-R1 — validated trusted routing authority + routed mixer

Issue `#121` — **COMPLETED**

Implementation PR `#122` — **MERGED**

Canonical implementation merge/main:

> **`422f30f78b39b333dd970bf3a20e94e1ba64e7fb`**

Durable validation:

- `evidence/MRAM_R1_VALIDATION.md`
- implementation/evidence exact head:
  `91d9629b4b017a70f30bb53d273890e22cd87734` — **22/22 permanent workflows SUCCESS**
- validation-record successor exact head:
  `009db978aab242525e20db4677083201c7af645f` — **22/22 SUCCESS**
- dedicated workflow: **MRAM-R1 Routing Authority & Routed Mixer Evidence**
- dedicated pre-validation run: `35307240384` — **SUCCESS**
- artifact ID: `10532212394`
- artifact ZIP SHA-256:
  `4a59898baf16af1d7f26d14a3f31868fc573ee028d996f5c62ba5a8881be6da0`
- independently verified manifest payloads: **9/9 exact SHA-256 + byte size PASS**
- exact Git contract inventory independently checked: **20/20 file hashes PASS**
- accepted routed-mix plan self-hash independently recomputed:
  `a4a67b79a2a402b08280b7f9c39d291f7b669800be39d558e9a1bc9fed2bb74e`
- controlled-change routed-mix plan self-hash:
  `5d7aeab03126aab73ff14c38bf5018a692951c2ff656d6909dba1c9219d77e88`
- accepted routed WAV:
  `49dbffcab7ee805083bd622959be232d356f730167e52e1ee3edeb6dbddba2a4`
- controlled-change routed WAV:
  `2ab53f16ab6f73ffc70dd92bd29abc767bce3176105efbfad8a5f617b74f2630`

### Validated MRAM-R1 behavior

MRAM-R1 establishes:

- source-bound routing edit candidates;
- Preview without accepted HEAD mutation;
- explicit trusted Accept with source/head/graph/asset revalidation;
- protected Project Engine routing commit authority;
- generic commit routing bypass rejection;
- stale Preview and second-Accept rejection;
- accepted bus/group/return/master routing;
- exact track primary output routing;
- bounded post-fader sends;
- deterministic routed mix plan;
- deterministic stereo PCM16 routed WAV;
- inherited ATCM-R2 gain/pan/mute/solo/clipping semantics;
- cycle and missing-target fail-closed behavior;
- accepted routing persistence across export/import and reopen;
- repeat-exact routing/plan/WAV after reopen;
- compatibility with existing audio, note and automation edits;
- truthful Studio audition through the routed mixer rather than a flat fallback.

The controlled evidence changes only:

```text
SEND-001 gain_db: -12.0 → -3.0
```

and proves corresponding routed-plan and WAV identity changes.

### Maximum validated MRAM-R1 claim

> **MUSICA can edit bounded explicit routing through source-bound Preview/Accept authority, persist that accepted DAG as creative state, and deterministically render the exact accepted track→node→master signal flow into a byte-reproducible derived offline mix while generic commit paths, stale Previews and invalid topology remain fail-closed.**

## Exact current rung / 현재 정확한 단계

The next rung is **MRAM-R2 — native mixer automation target mapping**.

R2 must extend the already validated typed automation authority/lowering family rather than creating a separate mixer-automation state machine.

The key design problem is target identity and backward compatibility:

```text
existing project|part automation semantics
→ versioned/safely extended native mixer target identity
→ source-bound Preview/Accept remains authoritative
→ deterministic automation lowering
→ deterministic routed mixer execution
→ derived plan/WAV only
```

Initial bounded target scope should begin with stable native identities and parameters that can be specified exactly:

- audio track gain;
- audio track pan;
- routing-node gain;
- routing-node pan.

Send gain or mute automation should remain outside R2 unless exact interpolation/execution semantics are separately frozen and evidenced.

## Current important non-claims / 현재 주요 비주장

Until separately validated, do not claim:

- native mixer automation mapping beyond existing project/part automation;
- Browser routing or native mixer automation editing;
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

> **Open and implement MRAM-R2 from canonical main `422f30f78b39b333dd970bf3a20e94e1ba64e7fb`: inspect the existing automation contract/authority/lowering stack, freeze a backward-compatible stable target model for native track and routing-node gain/pan, then prove source-bound accepted automation deterministically changes the routed mix without granting runtime or rendered output reverse authority.**

See `memory/NEXT_ACTION.md` for the exact execution order.

**Repository evidence remains authoritative over conversation/model memory.**
