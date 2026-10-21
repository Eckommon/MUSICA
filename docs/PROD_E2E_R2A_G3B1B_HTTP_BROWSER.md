# PROD-E2E-R2A-G3B1B — Studio HTTP + Browser sliced WAV import / 브라우저 분할 WAV 가져오기

**IMPLEMENTED IN DRAFT / 초안 브랜치 구현, 검증·병합 전** · Issue #199 (parent #195 / #192). Depends on G3B1A validated streamed CAS and G3B0 bounded staging.

## Intended end-to-end resource-only chain / 의도된 구현 경로

1. A user picks WAV in Browser. ≤16MiB continues to use the previous independent direct route; >16 through 64MiB uses new staged route.
2. Browser SHA-256 is computed **incrementally via `Blob.slice()` in ≤1MiB pieces**. Per-chunk SHA-256 uses WebCrypto only on one slice; no 64MiB `file.arrayBuffer()`.
3. `POST /v0/sessions/{id}/audio/stage/start` binds declared source size, SHA, opaque token and accepted revision under a known local Studio session.
4. `POST .../stage/{token}/chunk` accepts one byte-aligned, ordered ≤1MiB chunk with exact Content-Length, media type, offset and digest. Before HTTP body read the server verifies session/token/pending-preview/current accepted HEAD.
5. `POST .../stage/{token}/finish` asks G3B0 to validate the whole private stage, then G3B1A streams into immutable CAS, descriptor and audit without creating/accepting a clip. `cancel` cleans private staging without touching the project.
6. Upload process, hash progress and a cancel control are visible in the existing native-audio Browser panel; resulting asset ID and source-out length are populated for separate **user-triggered Preview and explicit Accept**.

## Safeguards / 보안 및 권한
- No path supplied by Browser to filesystem; server-picked, project-local private stage.
- Exactly one upload per Studio session, G3B0's global two-active cap, 15-minute idle expiry and cleanup at a new server start.
- Pending Preview or changed accepted project HEAD denies begin/append/finalize. Cancel remains available even while Preview exists.
- Transfer-Encoding, bad length/type, wrong chunk order/digest/session and incomplete whole content are not accepted as audio assets.
- Legacy ≤16MiB route is retained independently. No creative HEAD mutation on resource-only import.

## Evidence needed / 필수 검증
- Draft code and focused tests are not enough: require 52/52 full GitHub Actions workflows and successful true-browser user-selected ≥3min WAV case, inspected artifacts/hash/asset/audit, HTTP cancellation and negative cases.
- Existing tests exercise backend 3min upload, corrupt/mismatched session/offset/hash and client disconnect. The separately included Node check independently compares incremental SHA for boundary lengths and sliced blobs against Node crypto.
- The numerical 3min two-track mix/export and accepted project's full-song restart/reopen remain G3B2/G3B3. **This PR must not claim that renderer is memory-safe.**
- Disk-failure crash-journal across CAS object, descriptor and audit is not yet transactional; identify/remediate orphan recovery before commercial readiness.

## Promotion / 병합 조건
PR implementation all green → independent actual Browser 3min artifact review → bilingual validation successor → 52/52 successor CI → exact-head guarded squash merge; keep #195 OPEN.
