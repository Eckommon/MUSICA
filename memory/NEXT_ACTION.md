# MUSICA Next Action / 현재 다음 작업

**Assessment as-of 2026-10-28**. Official baseline main: `d594678d4662369c648ce86ddcca09e2537887d1`. Always re-read exact current main, PR head and GitHub Actions before writing or merging. Governing objective: **AI-supported, local-first general-purpose music-production workstation**, not a catalog of isolated green DSP tests.

## Strict cycle / 고정 개발 루프

`OBSERVE → GAP → PRIORITIZE → PLAN → EXECUTE → VALIDATE → IMPROVE → RELEASE/ROLLBACK → NEXT`

Full policy: `docs/PRODUCT_EXECUTION_LOOP.md` proposed in PR #218. Machine-readable capability ledger: `governance/product_gap_ledger.json`; human summary: `docs/PRODUCT_CAPABILITY_GAP_LEDGER.md`. A new run begins at OBSERVE and ranks unsupported user tasks, not the easiest feature to implement.

## P0 — finish existing evidence-bearing production slice

**[PR #216, G3B3-R0](https://github.com/Eckommon/MUSICA/pull/216)** implementation `75a95c51b6795ef6faa47c5b82af9c18cedb6c70`: 60/60 workflows + 64/64 check runs confirmed, actual first-party Chromium two independently selected 180s WAV imports, four explicit track/clip Accepts, supported WAV and exact SHA after Studio/Browser restart. Independent ZIP #12714651924 / SHA `2caf12319f5a255d75fed93b9e971b970232050f7748779d974b57bb1f20ba1b`. **Do NOT claim PR merged**. Check full 60/60 and all 64 checks for bilingual evidence successor `f4c9f94cb29629c4507e1e0ae5c5a23da817c2c5`. Follow up inherited G2B Chromium timeout with logs; legitimate retry only, no waived gate. Check canonical main unchanged, mark ready and expected-head squash, verify new official main. Keep parent #215 open.

## P0 — ratify loop and update state

**[PR #218](https://github.com/Eckommon/MUSICA/pull/218)** governance and ten-domain product-gap ledger, evidence grades E0–E4, permanent new workflow. Once #216 is official, rebase #218 on that exact main, refresh README and memory references including new exact canonical SHA, run full **61 workflows + all checks** on current code and bilingual governance evidence if used. Only then expected-head guarded squash. Any change after test requires new full suite.

## P0 — first next real creative-operator gap

**[Issue #217, G3B3-R1](https://github.com/Eckommon/MUSICA/issues/217)**. Build a bounded first-party Browser 180s editing slice that *uses the two accepted tracks imported via actual UI*: change a track gain/pan, listen and compare **pending** WAV vs accepted at 0s/90s/last, Discard one candidate without HEAD change, explicitly Accept another and prove final WAV SHA equals preview, then supported routed bus automation and a genuine .musica archive export/import exact SHA and route-plan preservation. Implement in small independently audited PRs, not one unenforceable mega-milestone.

**Rejected next choice:** another simulated plugin/RTIO/AI widget before the interactive edit-and-deliver journey. These are important P1 streams but do not close the present P0 gap.

## Future stages

P1: real waveform/timeline editing and undo/crash recovery, AI provider and human listening/lock study, physical Windows sound interface measurements, real plugin #177. P2: distribution/licensing/installer/signing/migration/scalability/human market testing. Never call a synthetic Chromium fixture a human beta.

## Absolute gates

- No auto-Accept of AI/Browser/audio/plugin/device state; canonical accepted HEAD is the source of truth.
- Source CAS hashes, accepted parent revision, candidate and plugin/routing plan provenance, no stale/foreign Preview playback.
- All exact-head full GitHub workflow/check runs green for implementation *and* evidence successor. Never bypass inherited red checks.
- Independent actual audio bytes (WAV rate/channels/frame count/PCM/SHA), browser screenshot+console errors, memory and persistence proof before promoting.
- Fail closed, retain Draft and log diagnosis+next action when CI is incomplete. GitHub exact refs/artifacts outrank memory and old PR comment text.
