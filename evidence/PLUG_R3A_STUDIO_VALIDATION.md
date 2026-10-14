# PLUG-R3-A Studio Bus Host Preview/Accept Validation

## Verdict (bounded; no browser/native claim)

**PASS — a Studio local service/HTTP Preview of an accepted-source-bound simulated two-bus plugin proposal yields noncanonical offline PCM audition, explicit Accept commits exactly one new Project revision, Discard leaves HEAD unchanged, and default Studio media is not silently overridden.**

Parent #155 remains OPEN, and Browser graphical editing is a separate unmerged successor (#174 / draft #175). This does **not** prove native third-party VST3/AU/CLAP compatibility, arbitrary graph PDC or audio-device realtime plugin hosting.

## Exact implementation and workflows

- PR #173, branch `feature/plug-r3-studio-bus-host-clean`.
- Implementation/evidence head: `75b0bf6960835a090bf206cd8e8ad1e6559505b4`.
- **40/40 GitHub Actions SUCCESS on the exact above head**. One inherited M7-R6 run failed transient Chromium installation after `packages.microsoft.com` apt endpoint became inaccessible. An unchanged rerun of only that failed job **passed the full original real-browser and deterministic artifact stages**. No test suppression or evidence gate was weakened.
- Dedicated `PLUG-R3 Studio Bus Host Preview Accept Authority Evidence` run **38607373832**: SUCCESS.
- Artifact ID **11916126876**, size **21,290 bytes**, GitHub-recorded and independently recomputed ZIP SHA-256:
  `4048080e7f5c624cdf118006f68e1c04a4baf1c549abb8351037e2838bde02e7`.
- Independently unzipped and checked **8/8 payload hash and size pairs**; permanent workflow also compares A/B generated directories byte-for-byte and checks its source-contract inventory.

## Creator authority and real PCM oracle

- Bounded two accepted tracks -> distinct buses -> one neutral master. Separate simulated algorithmic and user-intended creative delay remain source-bound under the existing K1-B schema; no native plugin latency reporting is fabricated.
- `GET /bus-plugins/editor` provides canonical accepted source IDs and hashes.
- `POST /preview/bus-plugins` validates typed source/candidate against the persisted Project HEAD and creates a transient Studio Preview with no revision advancement.
- `GET /bus-plugins/media/preview.wav` exposes only the pending typed bus-host Preview's derived PCM16 and checks the stored WAV SHA-256 and current accepted parent.
- On explicit global Studio Accept, the server re-derives the original candidate from persisted source, verifies Blueprint/material and derived WAV SHA-256, then invokes trusted `accept_bus_host_edit_preview`. Generic Project commit cannot authorize plugin material.
- An intentionally separate Preview media path ensures that the default Studio audio/MIDI does not silently point to the bus-host simulated processor preview and no derived plug-in file is bound as accepted generic media.
- Forced tampered pending Blueprint/WAV, stale/forged source, unsupported owner, pending Preview conflicts, bypass state and removal are covered by dedicated Studio service and HTTP tests. Discard does not advance HEAD; export/import/reopen restores exact accepted state and output.
- Numerically decoded actual evidence WAV: stereo PCM16, **8,000 Hz, 96,000 frames**, frame **9** equals **(24576,24576)** after causal two-path compensation. Preview and accepted/reopened WAV bytes identical. No runtime-to-canonical writeback.

## Promotion discipline

This validation file introduces a new commit. Before promotion, require **40/40 success on the exact validation-successor commit** and review its workflow identity, then perform expected-head squash merge. Do not close parent #155 or assert Browser graphical editing, native binary plugin ABI, realtime device PDC or commercial release readiness.
