# PLUG-R3B Validation — Creator-facing Browser Bus Plugin Editor

## Scoped result

**PASS — a real Chromium Studio user can inspect accepted simulated two-bus processor state, propose insert/update/bypass/remove, audition transient noncanonical Preview separate from accepted output, and explicitly Accept/Discard while Project authority remains immutable until Accept.** The Browser test verified numeric causal audio alignment and preserved independently accepted creative delay during processor bypass.

This is **not** a general plugin ABI host, VST3/AU/CLAP support, arbitrary graph PDC, live audio-device PDC or commercial-release certification. Parent #155 remains OPEN for separate closure evaluation. Design and issue: `docs/PLUG_R3B_BROWSER_EDITOR.md`, #174.

## Exact implementation and CI evidence

- Clean independent PR #176, branch `feature/plug-r3b-browser-bus-editor-clean`, starting from K3-A validated main `12fb6891ad550ace5a4f80c961d52040e93f475a`.
- Exact implementation/evidence head: `f0160c669e5d33798e94342707b6eb6372ac0b77`.
- **41/41 GitHub Actions SUCCESS on the exact head**, including inherited R0/R1/R2/K3-A, Studio, RTIO, Recording, MRAM, M7 and full Python 3.11/3.12 MUSICA CI. Nothing suppressed or waived.
- Dedicated new `PLUG-R3B Real Browser Studio Bus Plugin Editor Evidence` run **38653093733** — SUCCESS.
- Actual GitHub Action artifact ID **11935452918**, ZIP size **1,611 bytes**. Independently downloaded and recomputed ZIP SHA-256, matching GitHub's artifact digest:
  `ab891b2c424ba3e7ad489f1d61d3f99cc45032b136e16b6233417bea185802ef`.
- Independently inspected ZIP contents and independently rehashed **2/2 manifest payload file SHA-256 and sizes**. The browser suite repeats all actions twice and proves byte-identical output tree, without treating two independent executions as one.
- Accepted two-bus WAV SHA-256: `e58882303f3a4b02065710587a1c8fd8f0d54f209d779d3da86b07a25345ceaf`. Actual WAV independently decoded: stereo PCM16, **8,000 Hz, 96,000 frames**; frames 0–8 zero; aligned frame **9** equals **(24576,24576)**.

## Trust, usability and lifecycle facts

- The Browser reads exact accepted revision/Blueprint/audio/routing/automation/R1 plugin/bus-host hashes through the Studio editor source endpoint and posts typed, bounded candidate material to the established K3-A trusted Preview authority.
- Accepted plugin instances and not-yet-accepted Preview are visually distinct. Separate accepted and Preview WAV elements use explicit source-specific URLs; default Studio transport, monitoring and Project artifact binding are not overridden.
- Stable two-bus IDs are selected in labelled controls. Algorithmic frames (0–4096 integer) and intentional creative delay have distinct inputs. Bypass and removal require Preview and explicit Accept; unsupported routing is presented as read-only with reason.
- Real Chromium exercised add to BUS-001, add to BUS-002, discard of a bypass/creative edit without HEAD advance, **explicit Accept of bypass with creative delay 5**, forged source-hash denial, remove on BUS-002, and restart/reopen of the exact accepted HEAD.
- Independent numerical oracle for the accepted bypass+creative case: frame **9** equals **(8192,8192)** while frame **14** equals **(24576,24576)**; bypass removes simulated algorithmic delay without silently removing creative delay.
- The browser test recorded **0 page errors and 0 console errors**. Dynamic Project IDs/status/provenance are rendered via textContent, not project-dependent HTML interpolation. Same-accepted-revision refresh observation is deduplicated to limit Recording/RTIO contention.
- Existing generic Studio media remains unchanged and accepted Project HEAD changes only on explicit Accept, not on Preview, Discard or an invalid source.

## Promotion after recording this validation

This validation document changes the branch HEAD. **Do not merge until the exact validation-successor head passes 41/41 GitHub Actions SUCCESS**, verify it is the same PR/no unrelated changes, then mark ready and squash merge with exact expected head. Close #174 after merge with the bounded claim and leave parent #155 open until separately evaluated. Third-party binary feasibility work is separately tracked in #177.

Repository exact commit, CI and real artifact evidence outrank conversation summaries.
