# MUSICA Current State / 공식 현재 상태

**As-of 2026-10-28** | Canonical `main`: `d594678d4662369c648ce86ddcca09e2537887d1` (G3B2C-R5 PR #214 merged); this is the baseline at assessment, **not** a promise about future main. Read live GitHub refs and exact CI on every continuation. `docs/PRODUCT_EXECUTION_LOOP.md` is proposed via PR #218 until independently green and merged.

## Objective and product-level conclusion

Goal: an AI-assisted local-first **general-purpose music workstation** where users create/import, arrange, edit precisely, audition a source-bound candidate, Discard or explicitly Accept, route/automate, preserve/reopen an actual Project archive and export a reproducible supported WAV. Keep AI/provider, Browser, plugin and device data noncanonical until trusted human Accept.

**Current judgment:** strong bounded engineering foundations, **not completed as a usable commercial DAW**. CI cannot substitute for one real edited song nor human musician evaluation. Ten domain-level gaps and evidence grades E0–E4 are recorded in `docs/PRODUCT_CAPABILITY_GAP_LEDGER.md` and `governance/product_gap_ledger.json`.

## Last verified main + active implementation

- G3B2C-R5 accepted and pending 180s 48kHz WAV Range streaming and SHA/source-bound cache, expiry + eager Preview lifecycle cleanup, **official PR #214 merged**; exact canonical main above.
- Native assets/tracks/clips, bounded mixer/routed buses and supported automation; prior ATCM/MRAM results verified in isolated engine and first-party Browser. Strict Project/Blueprint accepted HEAD and Preview→explicit Accept remain invariant.
- Simulated RTIO/REC/PLUGIN, and bounded standalone Browser/plugin control evidence, **not** real physical audio or actual third-party plugin binary support.
- **G3B3-R0 Issue #215 / Draft PR #216**, implementation exact head `75a95c51b6795ef6faa47c5b82af9c18cedb6c70`: **60/60 workflows and 64/64 checks SUCCESS**. Actual first-party Chromium new 180s Project: 2 independently user-file-picked 34,560,044B 48kHz stereo WAVs; imported as resource only, 2 track Preview→Accept, 2 clip Preview→Accept (4 visible human-style Accept clicks); 180s WAV output, studio restart/reopen and byte-exact second WAV. Independent GitHub artifact #12714651924 ZIP SHA `2caf12319f5a255d75fed93b9e971b970232050f7748779d974b57bb1f20ba1b`; both WAV SHA `6a7b3cbc3b779a5997b76b673fb6476d7c383cae9776a1f6116b30e2c8b2f6db`, PCM `(3200,-1400)` at start/middle/end. **Evidence successor `f4c9f94cb29629c4507e1e0ae5c5a23da817c2c5` requires full exact-head CI before guarded merge**. One inherited G2B Chromium view test timed out in the successor suite and was legitimately rerun; no waiver.
- **Product-goal governance Draft PR #218**: 9-stage OBSERVE→GAP→PRIORITIZE→PLAN→EXECUTE→VALIDATE→IMPROVE→RELEASE/ROLLBACK→NEXT, a maintained quantitative/qualitative capability gap ledger and a new CI gate. This is the requested fixed operating rule once safely merged, **not a completed release gate**.

## Biggest live gaps (priority)

**P0 #217:** same genuine 180s Browser two-WAV Project with meaningful **pending mixer change, audible A/B vs accepted, explicit Discard/Accept**, supported routed bus automation and actual **.musica archive export/import** with exact WAV/plan/asset SHA parity. Current #216 does **not** prove this.

**P1:** practical waveform/timeline and undo/crash recovery; actual AI provider-directed output and listening-quality/lock audit; supported Windows physical audio-interface/RTIO capture and monitoring; one legally authorized real plugin ABI (#177); reproducible scale/platform UX.

**P2:** installer/signing/version migration/license audit, human pilot and market validation. Do not claim mature commercial workflow, realistic music composition, hardware low latency or native plugin support from synthetic audio proof.

## Authority, promotion and evidence

- Live GitHub exact accepted main > actual generated implementation + evidence successor artifacts/checks > `memory/` pointers > issue narratives > chats.
- Each product cycle follows `docs/PRODUCT_EXECUTION_LOOP.md`; plan+proof controls are absolute. No disabling/flaking inherited workflows, no false SHA from unrendered audio, no client/AI auto-Accept.
- Only after both exact implementation head and bilingual evidence successor have **all inherited + new GitHub workflows and all checks SUCCESS**, independently inspect physical WAV/PNG/JSON evidence, check project/source SHA, then expected-head guarded squash merge and update the capability ledger and this state in a state-only follow-up.
