# PLUG-R2B K1-B Validation — Accepted Simulated Bus Processor & Offline Causal PDC

## Scoped verdict

**PASS — exact accepted Project bus-processor state through trusted Preview -> explicit Accept produces real, sample-numerically demonstrated, causal two-path offline compensation. NOT real third-party plugin hosting, realtime PDC, or Studio integration.**

Parent Issue #155, R2 Issue #162 and K1 Issue #166 remain OPEN until separately validated wider integration. Predecessor K1-A merged main `58c7c6ebe8be6f990ecd21125293c61c815939d1`.

## Evidence-bearing implementation

- PR #169, `feature/plug-r2b-k1b-accepted-host-clean`
- exact implementation/evidence head `13dfd60e8cc09cd7e05a35f803c41931e39ad01b`: **38/38 GitHub Actions SUCCESS**
- dedicated workflow `PLUG-R2B K1-B Accepted Simulated Bus Host & Offline PDC Evidence`, run **38587048650**, SUCCESS
- uploaded artifact ID **11905669725**, size **38,705 bytes**
- GitHub artifact SHA-256 and independently recomputed ZIP SHA-256:
  `a83a1922b336a0d3e5a9518af67fb3d633c164607aabf69c370334dd1f70831f`
- independently opened the ZIP: 10/10 manifest artifact file size/SHA-256 checks passed; dedicated CI also verifies 14/14 checked-out source-contract inventory hashes, two repeated evidence outputs and inherited R1/R2/MRAM authority.

## Independently decoded WAV and durable authority proof

- Accepted Project Audio + Routing Preview->Accept then separately trusted K1-B bus-host Preview->Accept; rejected generic Project bypass; immutable accepted material and source hashes.
- WAV: **8,000 Hz, stereo PCM16, 96,000 frames**.
- Accepted explicitly simulated processing delays: BUS-001 **3 frames** and BUS-002 **9 frames**; planner offsets **+6 / +0**.
- Compensated WAV: frame **3** equals **(0,0)**; frame **9** equals **(24576,24576)**; the formerly faster path is delayed rather than the slower path advanced.
- Creative delay **5 frames** on BUS-001: at frame **9** only BUS-002 contributes **(8192,8192)**; at frame **14** both contribute **(24576,24576)**. Creative intent is not compensated away.
- Bypass: recomputed algorithmic latency/offset while retaining independent creative delay; frame **9** **(8192,8192)**, frame **14** **(24576,24576)**.
- Removed / empty accepted bus processors: byte-exact legacy routed WAV (frame **3** **(24576,24576)**); no silent intermediate quantization.
- Forced processor error aborts derived rendering; accepted Project HEAD unchanged. Reopened archive reproduces exact accepted plan/WAV.
- Hash-consistent forged source plan and tampered accepted source/owner/processor inputs fail closed. Existing R1 master chain is never silently omitted by the K1-B rendering entrypoint.

## Strict limits and next work

K1-B is constrained to exactly two accepted tracks -> distinct accepted buses -> one neutral master, stereo PCM16 and a bounded **simulated** processor. It does NOT host arbitrary VST3/AU/CLAP binaries, infer native algorithmic latency from creative `delay_frames`, integrate compensated execution into Studio/browser or audio-device callback, support arbitrary graph PDC or guarantee commercial-grade performance.

The exact implementation head is validated. This record itself changes the PR head: require **38/38 SUCCESS on this durable-validation successor head before expected-head squash merge**. Then leave #166/#162/#155 OPEN and pursue truthful Studio inspect/Preview->Accept/render selection for the bounded accepted bus-host state as a separate rung.

Repository evidence and exact commit checks take precedence over summaries or model recollection.
