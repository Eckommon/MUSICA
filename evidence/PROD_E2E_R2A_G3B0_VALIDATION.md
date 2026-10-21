# PROD-E2E-R2A-G3B0 validation / 사설 분할 WAV 임시 수신 검증

## Exact implementation and upstream / 구현 근거
- PR #197 (issue #195; parent #192). Source main: `7c74296fa63319c7d301d22c1589b5a53b091502` (G3A verified 49/49 on implementation and evidence successor).
- Exact implementation head: **`d2d7c73c161e30586153abed04f57c499958f5d0`**.
- All **50/50 permanent GitHub Actions workflows SUCCESS** at this exact head, including `PROD-E2E R2A G3B0 Bounded Private WAV Staging` and all 49 inherited workflow gates. No skipped or relaxed regression gates.

## What is genuinely implemented / 구현·검증 범위
- `BoundedWavStaging` stores upload bytes in private host-created temporary files; it does not accept user paths, does not touch project creative HEAD, and does not create an audio asset/clip.
- Explicit session identity, cryptographically random opaque transfer token, **64MiB per-source declared cap**, **1MiB per chunk**, **at most two active transfers**, strict monotonically increasing offsets, per-chunk SHA256 and streamed whole-object SHA256 before revealing verified temporary path.
- Cancel and application-close cleanup remove temp files. Malformed session, wrong session, bad digest, replay/offset mismatch, oversized block, oversized declared file, truncated upload and total SHA mismatch fail closed. Focused Python unit tests and inherited Studio/browser CI all pass.
- A verified temporary file is **NOT canonical CAS content**. No audio-asset descriptor/audit, HTTP route or Browser File.slice integration exists in this increment. No real 3-minute rendering or full-length music file has been proven.

## Security/technical limitations / 제품화 전 필수 보강
- Before exposing this primitive through HTTP, implement session existence, pending-preview checks **at every action**, finite expiry, transfer accounting/cleanup, Content-Length and media type checks and a safe no-user-path streaming finalize into immutable CAS with WAV integrity validation.
- Existing legacy direct `import-wav` stays 16MiB and trusted. No hidden bypass.
- No 3-minute dual-track, low-latency device, external VST/CLAP binary, actual human usability or AI composition claim is implied.

## Promotion gate / 병합 규칙
The commit containing this bilingual validation is the **evidence successor**. It MUST itself achieve **50/50 GitHub workflows SUCCESS** at exact HEAD before marking PR #197 ready and performing expected-head guarded squash merge. Keep #195 OPEN for G3B-1 HTTP/CAS and G3B-2/3 long-session proof.
