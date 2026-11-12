# MUSICA product-goal closed-loop v1.0 — implementation and evidence / 목표 중심 개발 규약 검증

## Objective & authority / 목적과 근거
- Product: AI-assisted local-first **general-purpose music workstation**, while preserving canonical accepted Blueprint/Project, trusted CAS inputs, explicit Preview→Accept and bounded derivatives.
- Assessment canonical baseline: `main=4e4e8866652a7e49ca706c6e2e959bbccc96790e`, officially merged G3B3-R0 PR #216. Its exact implementation and bilingual evidence successor each achieved **60/60 GitHub workflows, 64/64 checks** and independent genuine headless Chromium 2×180s Browser WAV import/explicit Accept/export/restart SHA parity. Not a human musical pilot.
- Product-goal execution-loop [Draft PR #218](https://github.com/Eckommon/MUSICA/pull/218) exact main-based 8-file implementation HEAD `221c6937a3f2a21338de3b037a018183cdf5418c`. New permanent **61st** workflow `MUSICA Product-Goal Closed-Loop Governance`, run [#43135652012](https://github.com/Eckommon/MUSICA/actions/runs/43135652012), SUCCESS. Its actual Python3.12 validation output was:
  ```json
  {"capability_domains":10,"commercial_release_ready":false,"next_selected_issue":217,"schema_version":"1.0","unverified_or_partial":8}
  ```
  The job also verified exact README/CURRENT_STATE/NEXT_ACTION baseline consistency, mandated OBSERVE→GAP→PRIORITIZE→PLAN→EXECUTE→VALIDATE→IMPROVE→RELEASE/ROLLBACK→NEXT contract, explicit authority, no invented release readiness, and the next P0 Issue #217.
- The complete inherited + new **61-workflow and all check-run gates on this implementation HEAD are required and may still be pending when this evidence is authored**. A successful new single governance workflow is *not* permission to merge.
- This bilingual evidence-bearing successor commit must **independently** pass entire 61/61 and every check-run success (61 workflows + four MUSICA CI matrix checks = typically 65 checks), then exact PR SHA/main/base verification and guarded squash. Rebase if main has moved. No predecessor SHA success transferred.

## Readiness gap and selected next / 제품 격차 판정
- First-party Browser 2x180s audio-resource import, four explicit track/clip Accepts, WAV output and Studio restart/reopen are **E2 bounded main-backed**, not professional musician production or commercial readiness.
- Most important remaining user-controlled P0 gap is actual **3-minute edited song in one Browser session**: [Issue #217](https://github.com/Eckommon/MUSICA/issues/217) / Draft [PR #219](https://github.com/Eckommon/MUSICA/pull/219) for native mixer pending Preview A/B and explicit Discard/Accept, then routed bus automation and real `.musica` project archive import/reopen fidelity. Distinguish R1A native mixer from later routing/archive features.
- 10 capability domains are inspectable in `docs/PRODUCT_CAPABILITY_GAP_LEDGER.md` and `governance/product_gap_ledger.json` (8 not fully bounded-verified, 2 bounded-verified). No fake project percentage.
- Real user-generated musical content, human listening/qualitative AI usefulness and lock audit, Windows low-latency audio interface, third-party real plugin binary, waveform UX, crash recovery and signed distribution are **NOT VERIFIED**.

## Non-waivable promotion / 통제
- Every product implementation must record accepted source hashes/HEAD, positive and negative tests, real artifact SHA/PCM where relevant, exact full CI on implementation and evidence successor, guarded promotion and next-gap update.
- If any workflow is pending or failed, leave Draft. A rerun must have an investigated transient cause; do not skip inherited tests or autocorrect accepted creative state.
- After main merge, carry the nine-stage loop forward through Issue #217 and refresh state documents again against the new exact main in a separate checked state-only change.
