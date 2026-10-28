# MUSICA Product-Goal Execution Loop v1.0 / 제품 목표 중심 개발 고정규약

**Authority:** this contract governs each subsequent MUSICA implementation, correction and promotion once merged. It extends, and must never relax, the exact accepted creative-state and CI evidence authority documented in `docs/PRODUCT_THESIS.md` and `docs/COMMERCIAL_WORKSTATION_TARGET.md`. A green CI is **not** commercial DAW readiness.

## North star / 목표

An **AI-assisted, local-first, general-purpose music workstation**: an ordinary user can originate or import music, arrange MIDI/audio, modify precisely, hear an unaccepted alternative, compare/Discard/explicitly Accept, mix and automate, persist and reopen without loss, deliver a supported audio/project artifact, and understand what the AI actually changed. Recording, third-party plugin hosting, physical I/O, robustness and distribution must be separately demonstrated before included in product-ready claims.

MUSICA의 성공 기준은 기능 파일 개수·테스트 개수·PR 개수가 아니라 **일반 사용자가 처음부터 끝까지 음악을 만들어 수정·청취·승인·저장·출력할 수 있는가**이다. AI 제안이나 Browser 상태가 사람의 명시적 Accept 없이 정본 창작 상태를 갱신해서는 안 된다.

## Non-negotiable single-cycle loop / 모든 개발 작업에 적용할 7단계 루프

```text
1. OBSERVE       current canonical main + exact PR/head/workflow/artifact + real user journey
2. GAP           product capability ledger, evidence strength, unsupported states
3. PRIORITIZE    biggest user-workflow blocker given safety/dependencies/effort
4. PLAN          smallest vertical, testable contract, measurable pass/fail/rollback
5. EXECUTE       implementation, UI and programmatic tests + actual audio evidence
6. VALIDATE      exact-head full CI, browser/audio SHA/PCM, negative tests, security
7. RELEASE/NEXT  guarded squash or rollback; update ledger/state; queue next gap
                    ↑_____________________________________________________|
```

Do **not** replace a failed implementation with a new feature or close a parent Issue merely because an isolated unit test passes. Each user-requested continuation re-enters at Step 1 using live GitHub, **never an old chat summary**. If no gate-compliant promotion is possible in the current session, preserve a Draft, reproducible failure details, and the next exact action; never describe unverified future work as complete.

## Product evidence grades / 증거 등급

| Grade | What is actually proven | What it is NOT |
|---|---|---|
| E0 design | typed specification, contract, architecture | functioning UI/engine |
| E1 focused | deterministic unit, bounded mock or synthetic DSP | integrated Browser use |
| E2 integrated | actual process+localhost HTTP, Browser Playwright, audio SHA, reopen | human-directed creativity or hardware |
| E3 operated | hands-on pilot with observed human task completion, time/error records and real audio | commercial reliability or universal support |
| E4 release | physical I/O/real plugin only where claimed; security/licensing, migration, performance, distribution and repeated user acceptance | open-ended compatibility |

The grade is the **minimum of the evidence needed by the claim**, not the maximum grade attained by one subfeature. A numerical 180s synthetic WAV is E2 for the transport, not E3 for music quality. Explicitly label simulated device/plugin paths as simulated. No untested assertion receives a pass.

## Product impact prioritization / 결정 순서

Choose next tasks lexicographically, with **no fabricated weighted percent-completion**:

1. **P0 safety/canonical authority blockers**: lost project data, hidden Accept, failed source hash, corruption, stale preview/audio, broken exports/reopen.
2. **P0 integrated-journey blockers**: inability to import/create, edit, audition alternative, compare, Accept, mix, automate, export and restore one supported real song.
3. **P1 usability/creative agency**: timeline/waveform/selection/undo, transparency of AI suggestions/locks, recoverability, supported editing breadth; prove in the first-party UI.
4. **P1 platform/product feasibility**: real supported hardware I/O, at least one authorized plugin binary, bounded project scale, reliable file handling, persistent offline mode.
5. **P2 commercial/distribution and validated demand**: installer/signing/updating, compliance, human pilots and market-fit evidence before declaring commercially usable.

Within the same class, pick: missing dependency first → strongest user impact → highest safety/risk reduction → smallest independently verifiable slice. Record the selection and *rejected alternative* in the gap ledger or Issue before writing code. Parallel tasks may be prepared as Drafts but cannot be promoted ahead of unmerged dependencies.

## PLAN contract (required per implementation) / 작업 설계 필수요건

- **User job**: one actual supported action sequence in the first-party Studio; named inputs and output.
- **Baseline**: exact `main` SHA and last merged capability; reproducible known defect/gap.
- **Scope**: supported project size, OS, rate, formats, routes, one explicit non-goal.
- **Authority**: accepted parent HEAD, source/preview identity, lock and CAS SHA checks; no auto-Accept; stale HEAD fails closed.
- **Proof**: positive + negative tests, at least one true audio/Browser fixture when UI/audio changes; known numerical PCM oracle, data loss/expiry cases, Linux RSS and time where meaningful.
- **Exit**: CI workflow count and every job/check green on exact implementation HEAD, inspect actual artifacts, write bilingual evidence, repeat full CI on exact evidence successor, expected-head guarded merge, verified canonical main.
- **Fallback**: fail closed, rollback or leave Draft, open Issues for unproven behaviors. No disabling an inherited CI workflow to force green.

## VALIDATE contract (non-waivable) / 정량 검증

For WAV work, inspect **actual bytes**, SHA-256, channels, rate, sample width, frame count, PCM at first/middle/last, clip/clipping status where applicable, reference/reopened byte parity, accepted HEAD invariant, trace of deliberate Preview→Accept, RAM/CPU and bounded transfer. For Browser, prove real Playwright actions with screenshots and request/console error log (not just backend state changes). For AI, include prompt/provider/model version, reproducibility limits, generated material, lock and changed-field report, a human listening/usefulness rubric, and explicit approval. For device/plugin, identify real hardware/SDK/plugin binary and measure real throughput/latency or mark **NOT TESTED**.

A workflow run from a **predecessor SHA** is not a pass for a rebased/current SHA. Rerun transient failures only with logs and exact gates unchanged. Any changed file after evidence forces a new exact-head full suite.

## RELEASE and NEXT / 정식 반영과 반복

- Only if dependencies are merged and both implementation + bilingual-evidence successor are full-green: compare changes against expected main, mark PR ready, expected-head squash, verify resulting canonical HEAD and parent Issue disposition.
- Update `docs/PRODUCT_CAPABILITY_GAP_LEDGER.md`, `governance/product_gap_ledger.json`, `memory/CURRENT_STATE.md`, `memory/NEXT_ACTION.md`, and the README current-status section **in a separate state-only PR** when needed. Never silently leave pointers months out of date.
- Each loop publishes a compact **decision record**: objective, prior evidence, selected blocker, real code paths, precise tests/failed tests, artifact SHA, unmet criteria, and next work item with trigger. Use GitHub Issue/PR comments and/or `evidence/`, not untraceable model memory.
- A new loop automatically begins with the highest blocking gap, not an arbitrary isolated subsystem. If a proposed feature changes final-product usefulness, update the ledger before promotion.

## Promotion and completion gates / 종료 판정

**Feature complete** = bounded contract + all inherited full CI on exact implementation/evidence heads + independent evidence + guarded main merge.  
**Integrated workflow complete** = real first-party UI end-to-end actions, user-selected media, source/HEAD authority, correct WAV/export, reopen parity, supported error cases, reproducible evidence.  
**Commercially ready** = integrated workflow plus critical editing breadth, real AI direction, measured physical/device & real plugin claims as applicable, human study, recovery, performance, security/compliance/licensing, supported Windows distribution. These three labels must never be conflated.

**Loop seed (2026-10-28):** [G3B3-R0 #215 / PR #216](https://github.com/Eckommon/MUSICA/pull/216) real Chromium two 180s user-chosen WAVs, explicit four Accept actions, independent export/reopen SHA; still not a full edited song. Next highest product gap: **long pending mixer + routed automation Preview→audition→Accept in the same browser-produced song, then genuine project archive round trip**. Follow after exact-head #216 evidence promotion, never beforehand.
