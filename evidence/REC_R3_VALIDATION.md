# REC-R3 Validation — Truthful Studio/Browser Recording & Monitoring Surface + Restart/Reopen Lifecycle v0

## Scope

Issue #152 under parent Issue #142.

REC-R3 completes the bounded Recording & Monitoring Foundation surface by projecting the already validated REC-R0 capture substrate, REC-R1 recording-finalize authority and REC-R2 monitoring runtime into a truthful Studio/Browser workflow. Browser/runtime state remains derived and non-canonical; clean capture finalization continues exclusively through the existing REC-R1 Preview → explicit Accept authority.

## Evidence-bearing implementation head

- exact implementation/evidence head: `8f238170fcf2617683adb159bd42f606c10d4e4a`
- permanent workflow count: **32**
- exact-head result: **32/32 SUCCESS**
- dedicated workflow: **REC-R3 Studio Recording & Restart Evidence**
- dedicated run: `36720989348` — **SUCCESS**
- artifact ID: `11101801176`
- artifact name: `musica-rec-r3-studio-recording-reopen-evidence`
- artifact ZIP SHA-256: `cad4ced5e9781d19f8a531a5362093bfca2546aa0f079293ce20939ece3add9c`
- artifact ZIP size: **8,214,824 bytes**

All 32 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The independently downloaded GitHub artifact matched the declared digest and byte size exactly.

The manifest contains **19 tracked evidence payloads**. All **19/19** matched their recorded SHA-256 and byte size.

The five real-browser screenshots also matched the manifest exactly:

| Screenshot | SHA-256 | Bytes |
| --- | --- | ---: |
| `01-recording-ready.png` | `6ca7697a89593624218f7b4a71f44ba14341e008713d8f149bdaa397861c900a` | 1,620,636 |
| `02-clean-capture-monitor.png` | `93c6a546ce26ec75a53b491e36b29fffc382f4391889893f71e41779ddf2aff8` | 1,693,658 |
| `03-recording-finalize-preview.png` | `02c574419e24904a2ee691d31d1f66cf73dfcfad8940e150801dbf78982de1e5` | 1,723,208 |
| `04-recording-accepted.png` | `753277ac75da844f7ffc5f9980b958b417e9175ea72883302f0ffe1fe2769de2` | 1,680,871 |
| `05-recording-reopened-reset.png` | `4efccd97202c545a40d850f88d44156b935d6a15ffb6a8a8810851019744d395` | 1,656,945 |

The artifact contract/source/test/workflow inventory was independently checked against the exact GitHub implementation head. All **17/17** files matched their recorded SHA-256 and byte size.

The persisted project workspace contains **21** content-addressed object files; all **21/21** object contents matched their SHA-256 object names.

## Browser recording projection

The initial Studio recording view binds the exact accepted project state:

- project ID: `PRJ-MRAM-R3-BROWSER`
- accepted revision:
  `rev-mram-r3-root-audio-b2abd5e4db191607-routing-4e104dd8c88177e7-auto-a1a4677d1268a35a`
- Blueprint SHA:
  `3dff898bca3e2a47905e58bc6df17c81e3f4b53105927bbbe66fc5c6a3c091ac`
- audio material SHA:
  `a605d763a91d631a4153dae1fd805cfd872e6f582d0f5b50bee5537611963de7`
- routing material SHA:
  `70e239186946a02007d5aabe19bb9359a9805f5f7b7fd707abfc22cae9f829f3`
- automation material SHA:
  `9d57f466b5f6864734e3aeea7d435f27dd4684ad5d4e6b1917309ec00090799d`

The typed projection explicitly reports:

- accepted Project state is canonical;
- Browser state is not canonical;
- recording runtime is not canonical;
- monitor state is not canonical;
- runtime cannot import assets;
- runtime cannot commit audio material;
- recording finalization authority is `REC-R1_PREVIEW_EXPLICIT_ACCEPT`.

## Clean capture + monitoring proof

A deterministic clean Studio capture/monitor run produced:

- capture frames requested/captured: **800 / 800**
- capture blocks requested/captured: **4 / 4**
- capture ERROR/SHORT_FILL/LATE counts: **0 / 0 / 0**
- capture dropout-equivalent count: **0**
- capture PCM SHA-256:
  `8bd5917d21004e7fe2143c04dfd2f20f9d546c993cd4cde41b4cb6be5b012aed`
- monitor frames written: **800**
- monitor blocks written: **4**
- monitor output xrun count: **0**
- monitor payload SHA-256:
  `8bd5917d21004e7fe2143c04dfd2f20f9d546c993cd4cde41b4cb6be5b012aed`

The run binds exact derived identities:

- capture plan SHA:
  `042f88fef149ec430340fe663f5faac2834fb187445c2918ef1b7c34e6a28306`
- capture report SHA:
  `f3b372a65c6837cccedda3d1dcf861ce2f1bb74b0dba31e489af7e9b87623d0b`
- monitor plan SHA:
  `df31760d7a32a282d0855865f5308b3cbc8e161680767bff48528b848feb559b`
- monitor report SHA:
  `783dfed34501c9118cea521c0a618648725d95a999dbf967d16102999daca158`

During capture/monitor execution, accepted HEAD and accepted asset inventory remained unchanged.

## Recording-finalize Preview authority

The Browser-generated recording finalize proposal delegates to REC-R1 and returned:

- status: **READY_FOR_PREVIEW**
- explicit Accept required: **true**
- project mutation authorized during Preview: **false**
- asset mutation authorized during Preview: **false**
- destination track: `AT-001`
- destination clip: `REC-R3-BROWSER-001`
- captured PCM SHA:
  `8bd5917d21004e7fe2143c04dfd2f20f9d546c993cd4cde41b4cb6be5b012aed`
- prospective WAV / immutable object SHA:
  `229dd2aa8e9da5596eb5e34455957e5167cc1765d59a43601e4262614dd07935`
- candidate audio material SHA:
  `40229a7d9ebd853a13659d7b164e31fdab637569646fe6db2276024e7cd8a7ce`
- candidate Blueprint SHA:
  `1ea06a8702cb0f5e6811b4f25f67f474d3c4d611a3078ee9cb0af00ccbb5f799`

Preview left accepted HEAD, asset inventory and accepted audio material unchanged.

Explicit Accept alone advanced accepted HEAD exactly once and reset the transient recording runtime.

## Accepted recording truth

After explicit Accept, track `AT-001` contains:

```text
AC-001
REC-R3-BROWSER-001
```

The accepted recording clip is bound to immutable asset:

`sha256:229dd2aa8e9da5596eb5e34455957e5167cc1765d59a43601e4262614dd07935`

The accepted revision is:

`rev-mram-r3-root-audio-b2abd5e4db191607-routing-4e104dd8c88177e7-auto-a1a4677d1268a35a-recording-5070b531001b304e`

The dedicated unit regression independently proves that routed output after recording Accept differs from the routed baseline before Accept. The evidence files named `final-routed-before.wav` and `final-routed-after.wav` refer specifically to **before vs after fresh service restart/reopen of the same accepted recording revision**, so their equality is the required lifecycle exactness proof rather than an Accept-effect comparison.

## Routed audition + self-hash verification

The final accepted routed plan includes the accepted recording clip and exact MRAM routing/native automation state.

Independent canonical-JSON self-hash recomputation matched exactly:

- routed mix plan:
  `3010933687511a3544861baea00101fe4f71cc4ed75712830f009106e3cff9c0`
- native mixer automation plan:
  `dc3e8a5cf0add17dcf4a27fe342a0fa615cc199b17bdfc8432940b9fc681e707`

Both pre-restart and post-reopen routed WAVs are exact valid deterministic PCM:

- SHA-256:
  `05d0231ea58f0ab4557922ca7bf8f4352b2f240df69288c906b8f274cea86c1e`
- bytes: **384,044**
- channels: **2**
- sample width: **2 bytes**
- sample rate: **8,000 Hz**
- frames: **96,000**
- compression: **NONE / PCM**

## Fresh restart/reopen lifecycle

The real-browser evidence stops the first Studio server, starts a fresh Studio service/server, reopens the project, and proves:

- same accepted revision;
- accepted recording clip remains present;
- exact accepted asset inventory remains present;
- transient recording runtime is reset to `null`;
- same routed plan;
- same routed WAV bytes;
- Project integrity PASS.

The accepted Browser recording projection before restart and after fresh reopen is byte-identical.

## Fail-closed proof

REC-R3 explicitly proves:

- dirty/short-filled capture is visibly **BLOCKED** from finalize;
- dirty capture reset/discard leaves accepted HEAD unchanged;
- unknown destination track is blocked;
- stale runtime handle is rejected with HTTP 404;
- previously consumed recording runtime cannot be accepted again;
- runtime state cannot import immutable assets directly;
- runtime state cannot commit accepted audio material directly;
- no Browser-only recording state is required for reopen reconstruction.

The dirty capture conflict is explicitly reported as:

```text
STALE_OR_INVALID_CAPTURE
recording finalize requires complete captured frame count
```

The unknown destination path reports `UNKNOWN_TRACK` for the exact missing track identity.

## Real-browser integrity

The evidence uses real Chromium and records:

- unexpected Browser console errors: **0**
- Browser page errors: **0**
- request failures: **0**
- unexpected HTTP errors: **0**

One HTTP 404 is deliberately expected and evidenced for stale/consumed runtime Accept after authority has advanced/reset.

## Authority boundary

```text
accepted project
→ derived Studio/Browser recording view
→ deterministic simulated capture + runtime-only monitoring
→ Browser finalize proposal
→ existing REC-R1 Preview
→ PREVIEW / accepted state unchanged
→ explicit REC-R1 Accept
→ immutable recording asset + accepted track/clip revision
→ truthful routed audition

fresh service restart
→ reopen accepted Project
→ accepted recording reconstructed from Project state
→ transient capture/monitor runtime reset
```

The following remain non-canonical:

- Browser DOM/JS state;
- recording runtime handles;
- capture runtime counters;
- monitor enabled state;
- monitor sink bytes;
- captured PCM prior to Accept;
- finalize Preview state.

## Explicit non-claims

This validation does not claim:

- host-native microphone/line input;
- host-native speaker monitoring;
- measured host-native input/monitor latency;
- zero-latency or hardware monitoring;
- take/comp workflows;
- punch-in/out;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- monitoring effects/plugins;
- sidechains;
- resampling;
- generalized commercial recording readiness.

## Validation verdict

> **VALIDATED — TRUTHFUL STUDIO/BROWSER RECORDING & MONITORING PREVIEW→ACCEPT + FRESH RESTART/REOPEN v0**

Maximum supported claim:

> **MUSICA can truthfully inspect bounded capture/monitoring runtime in Studio/Browser, finalize a clean capture through the existing REC-R1 Preview→explicit Accept authority, audition and persist the resulting accepted recording, and recover that accepted recording exactly after fresh restart/reopen while transient Browser/runtime state remains derived and non-canonical.**

Promotion remains conditional on all **32** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #152 completion and separate state-only parent #142 bounded closure evaluation.

Repository evidence remains authoritative over conversation/model memory.
