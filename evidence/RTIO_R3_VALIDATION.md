# RTIO-R3 Validation — Studio/Browser Runtime Inspection + Restart/Reopen Lifecycle v0

## Scope

Issue #139 under parent Issue #129.

RTIO-R3 projects the already validated RTIO-R0/R1/R2 realtime execution truth into Studio/Browser inspection, exposes bounded runtime-only transport commands, and proves fresh service restart + project reopen lifecycle exactness while Browser/runtime state remains derived and non-canonical.

## Evidence-bearing implementation head

- exact implementation/evidence head: `1b1e4031bfc6df727afaaf7e5fc432e6379b5a32`
- permanent workflow count: **28**
- exact-head result: **28/28 SUCCESS**
- dedicated workflow: **RTIO-R3 Studio Runtime & Restart Evidence**
- dedicated run: `36624838108` — **SUCCESS**
- artifact ID: `11060346157`
- artifact name: `musica-rtio-r3-studio-runtime-reopen-evidence`
- artifact ZIP SHA-256: `26c5f34f9d95ab874895ba2ac68ff67e84d46054b477c950ce096c7a5225b7d1`
- artifact ZIP size: **6,087,068 bytes**

All 28 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The GitHub artifact-declared digest and byte size matched the independently downloaded ZIP exactly.

The top-level evidence manifest declares **17 payload artifacts**. All **17/17** independently matched both declared SHA-256 and byte size.

Selected payloads:

| Payload | SHA-256 | Bytes |
| --- | --- | ---: |
| `01-runtime-open-stopped.png` | `f1e246cc2445a3dd1ac5d36ccef92cf58f3f183eef1dfa63a27e7b627a6259a4` | 1,551,431 |
| `02-runtime-seek-exact-frame.png` | `f070a91d4a842dcbd00431de747e133ff1b3275e66b2a45bc1a8b7c51467f4ff` | 1,551,659 |
| `03-stale-runtime-blocked.png` | `458df864978927016062a84dad1ee8c736fea55a69ac8185091b1ec9dc745456` | 1,549,063 |
| `04-runtime-reopened-reset.png` | `e9b05def9ff055f39ba7ac8305f8a79b7cffdc8151b93c1b403a16142c1c515f` | 1,529,240 |
| `final-realtime-plan.json` | `c1fda5fd62518a525b8ca8649cb4abf650fa55c3b5c97a31a2f86ea906e5c3f6` | 1,532 |
| `proof.json` | `a761d3edaa1824f79e880277b41ac96ff163183b6a5b3b89ca372769907c52c6` | 1,790 |
| `runtime-open-view.json` | `76944248882b4cb6a30ab99754026b2751103a3ef534206358966339c34d60ed` | 2,048 |
| `runtime-command-view.json` | `8a6c1c7df1ec64431aa2610a1af59767d7ff8a6952caf697834a213825da76fb` | 2,056 |
| `restart-runtime-view.json` | `db5a2251ffcf5c92d31f9e5864ea4895466b57ae8eeed47c2796a4a6a27e9663` | 1,997 |
| `scenario-before-report.json` | `d5fa2883bd7ea898e98b53e23d2fea6914b6c42ab25acf466f52072236141368` | 1,329 |
| `scenario-after-report.json` | `d5fa2883bd7ea898e98b53e23d2fea6914b6c42ab25acf466f52072236141368` | 1,329 |
| `scenario-before-sink.pcm` | `2aeddec6b6fa724065dcd60280925ebab7a871f866ac35fc673e1bc4869e5135` | 195,072 |
| `scenario-after-sink.pcm` | `2aeddec6b6fa724065dcd60280925ebab7a871f866ac35fc673e1bc4869e5135` | 195,072 |

The four real-browser screenshots independently decode as valid RGB PNG images at approximately 1600×4260–4320 pixels.

The evidence contract/source/test/workflow inventory was independently compared with exact GitHub head `1b1e4031...`. All **14/14** files matched both recorded SHA-256 and byte size.

The persisted workspace contains **21** content-addressed object files. All **21/21** independently matched the SHA-256 encoded in their object filename.

## Realtime-plan self-hash verification

Using MUSICA canonical JSON bytes, including the canonical trailing newline, the final reopened realtime execution plan independently recomputed exactly:

- declared:
  `99f9efca493ed4fd6cd1f4c8681ac20ae2d2b60ad0ee6c51012f8b29a1e1af12`
- recomputed:
  `99f9efca493ed4fd6cd1f4c8681ac20ae2d2b60ad0ee6c51012f8b29a1e1af12`

The final plan remains explicitly:

```text
classification = derived_noncanonical
backend        = musica-simulated-output-v0
sample rate    = 8,000 Hz
channels       = 2
duration       = 96,000 frames
block size     = 256 frames
wall-clock authority = none_simulated
runtime_state_is_canonical = false
```

## Studio/Browser runtime projection

The validated runtime projection binds exact:

- Studio session ID;
- project ID;
- accepted revision ID;
- realtime execution plan SHA;
- Blueprint SHA;
- audio material SHA;
- routing material SHA;
- automation material SHA;
- routed mix plan SHA;
- routed WAV SHA;
- backend identity/capability;
- sample rate, duration, channels and block size;
- exact-frame transport state/playhead;
- callback/runtime metrics;
- latency provenance;
- authority flags.

The projection explicitly states:

```text
accepted_project_state_is_canonical = true
browser_state_is_canonical          = false
runtime_state_is_canonical          = false
project_mutation_authorized         = false
runtime_commands_mutate_project     = false
position_authority                  = exact_frame_cursor_not_wall_clock
```

The Browser therefore inspects server-side runtime truth rather than reconstructing authority from DOM labels or wall-clock time.

## Bounded runtime command proof

The Studio Browser surface delegates bounded runtime commands to the existing RTIO-R2 exact-frame transport.

The evidence executes:

```text
PLAY
→ one 256-frame callback step
→ STOP
→ SEEK exact frame 48,000
```

The resulting Browser/server runtime projection shows:

- state: `STOPPED`;
- playhead frame: **48,000**;
- callbacks requested: **1**;
- frames requested/delivered: **256 / 256**;
- play count: **1**;
- stop count: **1**;
- seek count: **1**;
- transport discontinuity count: **1**;
- error/short-fill/late/xrun-equivalent counts: **0**.

The accepted Project HEAD remains unchanged throughout this runtime lifecycle.

## Stale and unknown runtime fail-closed proof

The evidence directly proves:

- an unknown runtime handle returns the expected not-found failure;
- after accepted Project HEAD advances, an old runtime bound to the prior accepted revision becomes stale and fails closed;
- runtime/source validation is based on exact accepted revision and plan identity, not Browser-local state.

The real-browser evidence recorded only the two expected HTTP errors for these negative tests and **0 unexpected HTTP errors**.

## Fresh restart/reopen exactness

The critical R3 lifecycle proof performs a fresh Studio service restart and project reopen.

Before restart, the deterministic scenario reaches:

```text
final state                      = END_OF_STREAM
final playhead                   = 96,000
callbacks requested              = 191
frames requested/delivered       = 48,768 / 48,768
play count                       = 2
stop count                       = 1
seek count                       = 1
transport discontinuity count    = 1
error / short / late / xrun      = 0 / 0 / 0 / 0
sink frames                      = 48,768
sink bytes                       = 195,072
sink SHA-256                     = 2aeddec6...9e5135
```

After a fresh service restart and reopening the same persisted project, replaying the same bounded transport scenario reproduces exactly:

- accepted revision;
- realtime execution plan identity;
- source binding;
- transport events;
- callback transactions;
- transport report;
- sink bytes and sink SHA-256.

The before/after transport reports are byte-identical and share SHA-256:

> `d5fa2883bd7ea898e98b53e23d2fea6914b6c42ab25acf466f52072236141368`

The before/after sink payloads are byte-identical and share SHA-256:

> `2aeddec6b6fa724065dcd60280925ebab7a871f866ac35fc673e1bc4869e5135`

This proves deterministic realtime-runtime regeneration from accepted state rather than persistence of runtime state itself.

## Runtime state is intentionally not persisted

After restart/reopen, the new runtime view resets:

```text
transport state   = STOPPED
playhead frame    = 0
callbacks         = 0
frames delivered  = 0
play/stop/seek    = 0 / 0 / 0
runtime_id        = new runtime identity
```

while accepted revision and final realtime plan/source identity are reconstructed exactly.

Therefore:

- playhead is not creative project state;
- runtime metrics are not creative project state;
- Browser state is not creative project state;
- a fresh runtime is regenerated from accepted Project authority.

## Real-browser truthfulness

The dedicated evidence uses real Chromium and proves:

- exact frame 0 visible on runtime open;
- exact seek frame 48,000 visible after command sequence;
- stale runtime visibly blocked after accepted HEAD advance;
- reopened runtime visibly reset while bound to the reopened accepted state;
- configured latency provenance is truthfully labeled;
- Browser project mutation authority is false;
- Browser console errors: **0**;
- Browser page errors: **0**;
- unexpected request failures: **0**;
- unexpected HTTP errors: **0**.

Expected media aborts caused by normal Browser media reload behavior are explicitly recorded separately and are not treated as runtime failures.

## Latency and device-boundary truthfulness

The validated Browser/runtime payload reports:

```text
configured_block_size_frames       = 256
nominal_output_latency_frames      = 0
nominal_source                     = simulated_backend_capability
host_observed_latency_available    = false
wall_clock_guarantee_claimed       = false
```

This is simulated-backend configuration provenance only.

RTIO-R3 does **not** claim measured host-native ASIO/CoreAudio/WASAPI latency, wall-clock scheduling guarantees, physical device delivery, or commercial low-latency readiness.

## Authority boundary

The validated authority chain is:

```text
accepted Project revision
→ deterministic routed source
→ deterministic realtime execution plan
→ derived Studio runtime
→ derived Browser projection
→ bounded runtime-only commands
→ exact-frame transport/callback execution
```

No reverse arrow exists from Browser DOM state, runtime playhead, runtime metrics, sink bytes, transport reports or device-like state into accepted Project creative authority.

## Explicit non-claims

This validation does not claim:

- host-native ASIO/CoreAudio/WASAPI output;
- host-observed latency guarantees;
- wall-clock realtime guarantees;
- microphone/line input;
- recording or monitoring;
- take/comp workflows;
- VST3/AU/CLAP hosting;
- plugin-delay compensation;
- sample-rate conversion;
- Browser-originated Project mutation authority;
- sidechains;
- mastering;
- generalized commercial realtime readiness.

## Validation verdict

> **VALIDATED — STUDIO/BROWSER REALTIME RUNTIME INSPECTION + RESTART/REOPEN LIFECYCLE v0**

Maximum supported claim:

> **MUSICA can truthfully expose its provenance-bound realtime/transport runtime in Studio/Browser and recover the same accepted source binding and deterministic runtime behavior after a fresh restart/reopen while runtime and Browser state remain derived and non-canonical.**

Promotion remains conditional on all **28** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #139 completion and separate parent Issue #129 bounded closure evaluation.

Repository evidence remains authoritative over conversation/model memory.
