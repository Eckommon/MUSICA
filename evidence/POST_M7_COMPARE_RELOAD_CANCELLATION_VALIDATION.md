# Post-M7 Compare browser navigation-cancellation classifier — validation / 브라우저 재열기 안정성 검증

## Root-cause record / 실제 반복 실패
As of 2026-11-12, source baseline canonical `main=4e4e8866652a7e49ca706c6e2e959bbccc96790e`. Genuine inherited Post-M7 real Chromium Compare CI failed in both unrelated Draft branches:
- Governance implementation workflow [run #43135652357](https://github.com/Eckommon/MUSICA/actions/runs/43135652357), job #130910242316.
- G3B3-R1A implementation workflow [run #43136181531](https://github.com/Eckommon/MUSICA/actions/runs/43136181531), job #130911965920.
The failures were **not** incorrect accepted revisions, WAV SHA, MIDI SHA, Browser diff, console errors or page errors. Exact exception: `Accepted revision Compare real-browser proof failed: true=[], false=[], console=[], page=[], requests=[GET .../v0/sessions/{old_session}/media/audio.wav?v=...: net::ERR_ABORTED, GET .../v0/health: net::ERR_ABORTED]`. Those old-page media/health GETs were canceled when the test intentionally invoked `page.reload(wait_until="domcontentloaded")`. A second real Chromium run on the first fix head reported only an old in-flight `/v0/health` GET cancelled at the test's deliberate final `page.close()`; that teardown path is now explicitly armed too. The inherited test already explicitly accepted cancellation of old `/revisions/.../media/audio.wav` GET when changing a media source, but the forced full reload introduced two additional benign request types.

## Narrow code correction (no gate bypass) / 수정 기준
On explicit Browser reload **or** explicit final Browser close, remember **only actual Request objects already in flight** before `page.reload` / `page.close`. An `ERR_ABORTED` is classified as a recorded expected navigation cancellation only if ALL are true:
- the GET Request identity was in the in-flight set at the exact reload/close arm point,
- the error is an actual `ERR_ABORTED`,
- URL path is exactly `/v0/health`, OR `/v0/sessions/<opaque-session>/media/audio.wav`, and
- no HTTP 4xx/5xx response occurred.

Everything else remains a hard failure: **new health requests after reload, GET history or arbitrary endpoints, POST media, non-ERR_ABORTED transport errors, and all 4xx/5xx HTTP responses**. The real Chromium test still asserts two accepted revision directions, structured diff, exact revision-bound WAV/MIDI SHA, unchanged accepted creative HEAD and deterministic re-open. No CI workflow removed, test marked xfail, skipped or given a weaker success condition.

## Executable tests
- `src/musica/post_m7_revision_compare_e2e.py` tracks per-request startup/finish/failure and arms a one-time snapshot immediately before deliberate reload.
- `tests/test_post_m7_compare_navigation_cancel.py` adds **seven focused positive+negative scenarios** covering two actual old reload cancellations, old health probe cancelled at explicit close but new health request still hard-failed, new GET health failure, preexisting unrelated/POST failure, pre-arm session audio failure, preexisting revision-source media cancellation, and hard HTTP 502.
- This documented exact implementation is proposed via [PR #221](https://github.com/Eckommon/MUSICA/pull/221), parent Issue #220. Its latest corrected implementation HEAD is `9dfed44b2bb41b01bd3d6c3bf9c8d51d41358f70`. **The entire inherited 60-workflow suite and all check runs on that exact implementation and this evidence-bearing successor are required**; no claim of full success is made until live GitHub says so. The source-specific Post-M7 real Chromium workflow must PASS independently, and optional actual artifact/screenshots/JSON remain available.

## Promotion and downstream order
1. Do not promote until implementation + evidence successor full exact-head green, independent test result audit, expected-head guarded squash; verify resulting `main`.
2. Then clean-rebase product-goal loop PR #218 (one permanent governance workflow; total normally 61), refresh exact main SHA across README and memory/JSON ledger, rerun complete 61-workflow implementation and evidence successor, guarded merge.
3. Then clean-rebase G3B3-R1A PR #219 (one permanent first-party 180s mixer Browser workflow; total normally 62), rerun full CI both heads, independent two-WAV artifact audit and guarded merge.
4. Continue P0 Issue #217 routed gain automation and actual `.musica` archive roundtrip under the nine-step product-goal execution loop.

**Limitations:** this PR corrects a test observer's classification of actual old-page canceled HTTP GETs. It does not repair a broken renderer, source hash, missing media, real audio device or plugin, nor prove human-created music. Any actual new-page failure still fails CI.
