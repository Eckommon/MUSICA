# MUSICA Product Capability & Evidence Gap Ledger v1.0 / 제품 목표 격차 장부

**As-of:** 2026-10-28. Canonical `main` examined: `d594678d4662369c648ce86ddcca09e2537887d1`. Machine-verifiable counterpart: `governance/product_gap_ledger.json`. **Not a percentage-completion claim.** Refresh this document after each guarded promotion and on every new product-goal loop, with the actual HEAD.

## Current goal assessment / 목표 달성 평가

**Engineering execution: effective but disproportionately foundation-heavy.** Verified accepted Blueprint authority, native audio, routing, deterministic 180-second WAV streaming/Preview/cache, Browser audio staging, offline simulated plugins, simulated runtime/capture and repeated regression CI show meaningful implementation. Latest G3B3-R0 PR #216 implementation at `75a95c51b6795ef6faa47c5b82af9c18cedb6c70` achieved **60/60 workflows and 64/64 checks**; artifact #12714651924 independently confirmed real Chromium 2×180s user-selected WAVs, 4 visible Accept operations, exact PCM16 stereo 180s audio and **byte-exact WAV SHA after restart/reopen**. This is bounded E2 evidence; at the time of this ledger, the evidence-bearing successor PR #216 remains unmerged.

**Product outcome: not yet attained.** The exercised project consists of synthetic PCM fixtures, not a user-created musical arrangement with audible full-song editing, routed automation, save/archive recovery, AI creative guidance and hands-on user validation. A technical feature counted as green cannot stand in for unsupported user tasks. The existing README, `memory/CURRENT_STATE.md`, and `memory/NEXT_ACTION.md` contain historical PLUG-R3B/41-workflow status and must be corrected, independently promoted as state-only documentation.

## Evidence-backed capability map / 증거별 진척

| Gap ID | User-facing capability | Evidence | Current boundary | Next |
|---|---|---|---|---|
| C01 | Inspectable canonical authority, locks, Preview/Accept | E2 bounded | Complete integration adversarial audit not yet | #215 |
| C02 | Real Chromium 2×180s WAV import, 2 tracks/clips, Download/reopen | E2 **PR #216 implementation** | Need evidence successor and guarded merge; music not real composition | #215 |
| C03 | Pending 180s mixer edit → A/B audible compare → explicit Accept | E1 isolated engine | Not one demonstrated first-party Browser workflow | **#217 P0** |
| C04 | Routed bus and automation on the same 180s song | E1 bounded tests | No end-to-end operator acceptance | **#217 P0** |
| C05 | Real song archive export → fresh import and exact reopen | E1 / partial | Studio workspace restart proven; **archive roundtrip not** | **#217 P0** |
| C06 | Waveform trim/fade, undo, crash recovery, ergonomic UI | E1 partial | Not robust general-purpose editing | #178 |
| C07 | Live AI-directed changes, audible quality, locks | E1 contract | No real provider + human listening quality evidence | #178 |
| C08 | Real Windows audio interface, low-latency recording | E1 simulated | Physical I/O entirely unverified | #129 |
| C09 | Authorized native plugin binary host | E1 simulated | Simulated PDC is not VST3/CLAP | #177 |
| C10 | End-user Windows distribution, scale, user-market validation | E0 | Developer install only, no signed release or human pilot | #178 |

Evidence grade defined in `docs/PRODUCT_EXECUTION_LOOP.md`. E1 or E2 for a scoped property is **not** the general-purpose DAW E3/E4 declaration. Do not attach invented overall percentages, labor-hours, CI pass rates averaged across unrelated branches, or commercial readiness tags to this table.

## Immediate decision / 다음 작업 선정

- **First finish #216**: exact documentation-bearing successor full **60/60 workflows and all 64 jobs**, independent artifact proof, expected-head guarded squash. This converts the true 2×180s native first-party Browser journey from Draft to main-backed support.
- **Next P0 Issue #217**: in that **same 180-second two-WAV Studio project**, introduce a real pending mixer change, audition and compare with accepted audio without changing HEAD, Discard one candidate, explicitly Accept another, then route/automate supported buses and persist an actual project archive through fresh import/reopen. Verify WAV SHA/PCM, routing/automation plan hash, source identity, actual Chromium actions, no console errors, RSS and meaningful duration.
- **Rejected alternative at this gate:** implementing another isolated simulated plugin/RTIO feature or AI UI widget would expand test count but does not address the fact a user still cannot prove a complete edit-and-deliver creative loop. Real plugin, hardware and AI quality remain important P1 streams, not substitutes for P0 workflow completeness.

## Fail-closed success milestones / 실제 종료 조건

1. **Feature pass:** exact source/authority contract, 100% of inherited and newly required GitHub workflows/check runs green on implementation and independent evidence successor, exact-head guarded merge.
2. **Workflow pass:** first-party human-like Browser operation with user-provided files and a meaningful edit before Accept, whole-song audition/comparison, routing/automation, export, **archive** restore, deterministic SHA/PCM and no silent Accept.
3. **Human pilot pass:** actual musicians successfully perform defined tasks with observable outcomes, no unsupported-action ambiguity, qualitative listening notes, task completion/time/errors; distinct from Playwright.
4. **Commercial gate:** supported real hardware/plugin where claimed, security/migration/recovery/long-session load, Windows installer/signature/licensing/accessibility, repeated human pilot. None of these four gates may be inferred from a single synthetic WAV run.

## Loop operating record / 실행 결과 기록

Every cycle: **OBSERVE → GAP → PRIORITIZE → PLAN → EXECUTE → VALIDATE → RELEASE or ROLLBACK → NEXT**. Log exact main/PR SHA, rejected alternative, test scope and failure diagnosis, downloaded artifact ZIP SHA and contents, promotion outcome and next dependency. Rerun full CI on **any** successor change. Update this ledger and the machine ledger after promoting any meaningful milestone; unresolved claims remain OPEN and explicitly **NOT VERIFIED**.
