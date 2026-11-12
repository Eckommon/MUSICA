# MUSICA Current State / 공식 현재 상태

**As-of 2026-11-12** | Canonical `main`: `4e4e8866652a7e49ca706c6e2e959bbccc96790e` (G3B3-R0 PR #216 merged); this is the baseline at assessment, **not** a promise about future main. Read live GitHub refs and exact CI on every continuation. `docs/PRODUCT_EXECUTION_LOOP.md` is proposed via PR #218 until independently green and merged.

## Objective and product-level conclusion

Goal: an AI-assisted local-first **general-purpose music workstation** where users create/import, arrange, edit precisely, audition a source-bound candidate, Discard or explicitly Accept, route/automate, preserve/reopen an actual Project archive and export a reproducible supported WAV. Keep AI/provider, Browser, plugin and device data noncanonical until trusted human Accept.

**Current judgment:** strong bounded engineering foundations, **not completed as a usable commercial DAW**. CI cannot substitute for one real edited song nor human musician evaluation. Ten domain-level gaps and evidence grades E0–E4 are recorded in `docs/PRODUCT_CAPABILITY_GAP_LEDGER.md` and `governance/product_gap_ledger.json`.

## Last verified main + active implementation

- G3B2C-R5 accepted and pending 180s 48kHz WAV Range streaming and SHA/source-bound cache, expiry + eager Preview lifecycle cleanup, **official PR #214 merged**; exact canonical main above.
- Native assets/tracks/clips, bounded mixer/routed buses and supported automation; prior ATCM/MRAM results verified in isolated engine and first-party Browser. Strict Project/Blueprint accepted HEAD and Preview→explicit Accept remain invariant.
- Simulated RTIO/REC/PLUGIN, and bounded standalone Browser/plugin control evidence, **not** real physical audio or actual third-party plugin binary support.
- **G3B3-R0 Issue #215 / PR #216 OFFICIALLY MERGED**, evidence successor `f4c9f94cb29629c4507e1e0ae5c5a23da817c2c5`, full **60/60 workflows, 64/64 checks PASS** on both implementation and evidence exact heads. Actual first-party Chromium two user-picked 180s/48k/stereo WAVs, four explicit track/clip Accept actions, accepted WAV and exact SHA after restart/reopen. Independent artifact #12714651924 includes ZIP SHA `2caf12319f5a255d75fed93b9e971b970232050f7748779d974b57bb1f20ba1b`; both WAV SHA `6a7b3cbc3b779a5997b76b673fb6476d7c383cae9776a1f6116b30e2c8b2f6db`, PCM `(3200,-1400)` at first/middle/last. This is E2 automation, not human pilot.
- **G3B3-R1A [Draft PR #219](https://github.com/Eckommon/MUSICA/pull/219)**: same 2×180s Browser project, first-party mixer Preview/Discard and explicit Accept, native WAV accepted/reopen SHA; older stacked head 61/61 workflows and 65/65 checks succeeded but must clean-rebase and revalidate after #218 main. Routing automation and .musica archive remain separate #217 work.
- **Product-goal governance Draft PR #218**: 9-stage OBSERVE→GAP→PRIORITIZE→PLAN→EXECUTE→VALIDATE→IMPROVE→RELEASE/ROLLBACK→NEXT, a maintained quantitative/qualitative capability gap ledger and a new CI gate. This is the requested fixed operating rule once safely merged, **not a completed release gate**.

## Biggest live gaps (priority)

**P0 #217:** same genuine 180s Browser two-WAV Project with meaningful **pending mixer change, audible A/B vs accepted, explicit Discard/Accept**, supported routed bus automation and actual **.musica archive export/import** with exact WAV/plan/asset SHA parity. Current #216 does **not** prove this.

**P1:** practical waveform/timeline and undo/crash recovery; actual AI provider-directed output and listening-quality/lock audit; supported Windows physical audio-interface/RTIO capture and monitoring; one legally authorized real plugin ABI (#177); reproducible scale/platform UX.

**P2:** installer/signing/version migration/license audit, human pilot and market validation. Do not claim mature commercial workflow, realistic music composition, hardware low latency or native plugin support from synthetic audio proof.

## Authority, promotion and evidence

- Live GitHub exact accepted main > actual generated implementation + evidence successor artifacts/checks > `memory/` pointers > issue narratives > chats.
- Each product cycle follows `docs/PRODUCT_EXECUTION_LOOP.md`; plan+proof controls are absolute. No disabling/flaking inherited workflows, no false SHA from unrendered audio, no client/AI auto-Accept.
- Only after both exact implementation head and bilingual evidence successor have **all inherited + new GitHub workflows and all checks SUCCESS**, independently inspect physical WAV/PNG/JSON evidence, check project/source SHA, then expected-head guarded squash merge and update the capability ledger and this state in a state-only follow-up.
