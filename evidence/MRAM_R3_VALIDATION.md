# MRAM-R3 Validation — Truthful Browser Routing & Native Automation Surface + Restart/Reopen v0

## Scope

Issue #126 under parent Issue #115.

MRAM-R3 projects the already validated accepted routing graph and MRAM-R2 native mixer gain/pan automation into a real Browser/Studio surface, routes Browser proposals through the existing trusted Preview→Accept authorities, auditions the exact routed candidate/accepted state, and proves fresh Studio-service restart/reopen exactness without granting Browser/runtime/media state reverse creative authority.

## Evidence-bearing implementation head

- exact implementation/evidence head: **68250b792ea8ecf773bfd92a16c8866efb4ef2b5**
- permanent workflow count: **24**
- exact-head result: **24/24 SUCCESS**
- dedicated workflow: **MRAM-R3 Browser Routing & Reopen Evidence**
- dedicated run: **36530923478 — SUCCESS**
- artifact ID: **11016528257**
- artifact name: **musica-mram-r3-browser-routing-reopen-evidence**
- artifact ZIP SHA-256: **e56c11505cf50b410b74461bdf0bc9a2fb88de31d13a04dbe4b4ad3c54d58938**
- artifact ZIP size: **7,971,169 bytes**

All 24 permanent workflows completed successfully on this exact implementation/evidence head before this durable validation record was added.

## Independent artifact inspection

The GitHub artifact-declared digest and size matched the independently downloaded ZIP exactly.

The manifest declares **17 evidence payloads**. All **17/17** matched their recorded SHA-256 and byte size.

The exact GitHub implementation inventory recorded by the artifact was independently checked against the implementation/evidence head. All **17/17** schema, service, Browser asset, test and workflow files matched their recorded SHA-256 and byte size.

The persisted Project workspace contains **27 content-addressed object files**. All **27/27** object contents independently matched the SHA-256 encoded in their object filename.

Six real-Chromium screenshots were independently parsed as valid PNG images:

| Screenshot | SHA-256 | Bytes | Dimensions |
| --- | --- | ---: | --- |
| 01-accepted-routing-automation.png | 3f5cc3d901c4fd1a7ca27d98311c12f057abd423bdef0fdb515996535a6c05ca | 1,295,800 | 1600×3619 |
| 02-routing-preview.png | e5cfb7314b8ada5649bb457ed873803a29923b71aef6149d87dbcdeb4dd37dcc | 1,435,223 | 1600×4013 |
| 03-routing-accepted.png | dbe9ee991c7cf2e26c1fd95d8d8768ec0acc4689fde5d414cc22293235436560 | 1,297,203 | 1600×3671 |
| 04-native-automation-preview.png | c6d11da234e3fcd3522328fcad4dfee1ddd7eba22e65c30b240d4367bd4ff970 | 1,478,480 | 1600×4075 |
| 05-native-automation-accepted.png | 8403bf6adf4df82bfa599a77234db118d7fb4d0bc09cc1e51d8bcb3eebf5492d | 1,328,409 | 1600×3743 |
| 06-reopened-exact.png | f76ab86187e779e2f2d9494bbb59a4dd51e5a11b8a3934337ac851fa202ed531 | 1,277,068 | 1600×3619 |

## Real-Browser authority proof

The dedicated real-Chromium evidence proves that the Browser projections bind the same exact accepted source:

- accepted revision ID;
- Blueprint SHA;
- audio-material SHA;
- routing-material SHA;
- automation-material SHA;
- stable track output IDs;
- stable routing node IDs;
- stable send IDs;
- stable native automation lane/point IDs.

The Browser routing surface is explicitly derived/non-canonical.

Browser routing proposals use existing typed routing operations and the MRAM-R1 authority engine. The evidenced controlled routing edit is exactly:

~~~text
SEND-001 gain_db: -12 dB → -2 dB
~~~

The routing Preview is source-bound, leaves accepted HEAD unchanged, exposes exact changed IDs and authority result, renders the exact routed candidate WAV, and remains non-canonical until explicit Accept.

Explicit Accept advances exactly once to the candidate revision and persists the accepted send gain.

## Native automation Browser proof

The existing automation Browser surface is reused rather than replaced by a parallel MRAM state machine.

For MRAM-R2 native mixer lanes, the Browser path binds exact audio/routing hashes and passes Project Engine context to the existing native automation authority.

The evidenced controlled native automation edit is exactly:

~~~text
AUTO-AT001-GAIN / P-R3-1: -3 dB → -12 dB
~~~

The native automation Preview leaves accepted HEAD unchanged, uses the MRAM-R2 routed native mixer audition path, does not use the legacy M7 reference-renderer UNMAPPED path as if it were native mixer authority, and remains non-canonical until explicit Accept.

Explicit Accept advances exactly once and persists the native automation point value.

## Legacy compatibility boundary

MRAM-R3 preserves the historical M7 audition inspector for its validated explicit legacy automation family.

The Browser inspector does not request that legacy audition path when automation editing is unavailable or when accepted lanes target native audio_track or routing_node mixer scopes.

Native mixer automation audition truth is instead supplied by the exact routed-mixer surface.

This boundary was regression-checked by the permanent M7-R6 and Post-M7 Accepted Revision Compare gates, both of which completed SUCCESS on the exact implementation/evidence head.

## Routed audition proof

The Browser fetched routed WAV bytes and independently compared their SHA-256 to the exact accepted/Preview routed-audition projection.

- initial accepted routed WAV SHA-256:
  **742441db0aebe4d917c7f7490682efb8d017a543c02b21e987e0eefbc0063ca8**
- final routed WAV SHA-256:
  **2eb68ddccaa8e827ebc6c0235d5740702fb7b631f91f3fcefff698ff7d9a9eee**
- final routed mix plan SHA-256:
  **a0bcb84ac8789c544bb0ce595fd5113059aa217cfe1ab76bacba953d5dcf89ea**
- final accepted revision:
  **rev-studio-382cb403161ac48f712061ab**

## Restart/reopen exactness

After stopping the first Studio service and opening the same persisted project through a fresh Studio service and fresh Browser page, evidence proves exact equality for:

- accepted revision ID;
- routing-material SHA;
- automation-material SHA;
- native automation identities;
- routed mix plan SHA;
- routed WAV SHA;
- Project integrity status.

Final/reopened routing projection hashes were byte-identical, and final/reopened automation projection hashes were byte-identical.

## Fail-closed Browser negatives

Real-Browser negative requests prove:

- unknown routing send ID does not install Preview and returns UNKNOWN_SEND;
- a stale pre-edit Browser routing source does not silently rebase and returns STALE_SOURCE;
- accepted HEAD is not mutated by blocked requests;
- Browser/runtime state has no direct Project mutation authority.

## Browser lifecycle diagnostics

The final evidence records:

- Browser console errors: **0**
- Browser page errors: **0**
- unexpected request failures: **0**
- HTTP error responses: **0**

Four net::ERR_ABORTED requests are separately classified as expected media lifecycle cancellations. Each is a GET for a superseded Studio audio WAV URL while an HTML audio element replaces its source during accepted/Preview refresh. They are not HTTP/API failures and do not alter authority or evidence state.

## Authority boundary

The validated R3 authority chain is:

~~~text
accepted Project revision
→ exact derived Browser routing/automation projection
→ typed Browser candidate
→ existing routing or automation Preview authority
→ PREVIEW · accepted HEAD unchanged
→ explicit Accept
→ existing trusted Project Engine commit boundary
→ accepted revision
→ exact routed audition
~~~

The following remain non-canonical:

~~~text
Browser DOM / JS state
pending Studio Preview
routed audition cache
native automation lowering plan
routed mix plan
rendered WAV bytes
screenshots
~~~

None can reverse-promote themselves into accepted creative state.

## Explicit non-claims

This validation does not claim sidechains, send-gain automation, mute/solo automation, realtime device callbacks, recording/monitoring, VST3/AU/CLAP hosting, plugin-delay compensation, sample-rate conversion, warp/time-stretch/pitch shift, mastering-grade processing, cloud/multi-user authority, or generalized commercial release readiness.

## Validation verdict

> **VALIDATED — TRUTHFUL BROWSER ROUTING & NATIVE AUTOMATION SURFACE + RESTART/REOPEN v0**

Maximum supported claim:

> **MUSICA can truthfully inspect and edit its bounded accepted routing and native mixer gain/pan automation through a real Browser/Studio Preview→Accept surface, audition the exact accepted routed result, and recover the same accepted identities and deterministic routed output after fresh restart/reopen while Browser/runtime/media state remains non-canonical and stale or unknown-ID proposals fail closed.**

Promotion remains conditional on all **24** permanent workflows succeeding again on the exact successor head containing this durable validation record, followed by expected-head squash merge, Issue #126 completion and a separate state-only parent Issue #115 closure evaluation.

Repository evidence remains authoritative over conversation/model memory.
