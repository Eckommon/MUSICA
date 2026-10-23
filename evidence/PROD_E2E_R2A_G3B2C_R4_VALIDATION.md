# G3B2C-R4 — trusted 180-second Pending Preview evidence / 승인 전 180초 미리듣기 검증

## Canonical and implementation authority / 정본
- R3 guarded merged canonical `main=f4414ffddf5a78744d86698088d18795a9f788c5`, exact 57/57 GitHub workflows and 61/61 individual checks successful.
- R4 Draft [PR #212](https://github.com/Eckommon/MUSICA/pull/212) rebase of exactly ten R4-specific files onto that accepted main, **implementation head `ccdd0ad65c94e1e3a6c3216681ef0a4ffd00e266`**. Its complete 58-workflow CI gate was running when this evidence was authored; **do not promote until exact 58/58 workflows and all 62 individual checks succeed**.
- Earlier stacked R4 implementation `c59744151b89bc3fc989a994f35235f62a55f152` completed **57/58 workflows and 61/62 checks**, with one inherited G3A standard-resolution Chromium G2B 90-second accepted-view projection timeout. Crucially, the dedicated R4 source-bound Pending Preview evidence was SUCCESS; the G3A timeout must be rerun/revalidated and is not waived.

## Independently inspected Chromium proof / 브라우저 실증 파일
- Real permanent GitHub Actions dedicated R4 run [#39968872694](https://github.com/Eckommon/MUSICA/actions/runs/39968872694) SUCCESS; uploaded original artifact ID `12508758838`.
- Independently downloaded original ZIP `MUSICA-G3B2C-R4-Chromium-pending-180s.zip`, **ZIP SHA-256 `33df36b4bc9d95103cc250e2fc49e0b7640b0871e9ad1456f8741797c8420f7e`**. Actual members: 2,167,513-byte screenshot `01-chromium-180s-pending-not-accepted.png` and `proof.json`. Opened and independently inspected the screenshot, which displays the 180s audio player with explicit **`Preview-derived native mix · NOT ACCEPTED`** and related DAW UI controls.
- `proof.json` reports Playwright Chromium-derived **180.000-second WAV metadata**, actual server-side trusted pending preview ID `preview-dd56654b9d14efc739617dfb`, original accepted parent revision `rev-audio-bd68cb08f953bd30bbd7d7dd84412e79` before/after playback, and no silent creative Accept. Discard preserves HEAD. This is an automated first-party Browser evidence test, **not** a live human pilot, full 180s real-time listening with speakers, or production musician quality evaluation.

## Candidate WAV/HTTP technical evidence / 실제 구현
- Studio native/routed long Pending Preview *creation* no longer eagerly allocates whole-song legacy Python float arrays/WAV bytes. The existing in-session, source-bound pending candidate is a read-only temporary authority bound to explicit preview ID, parent branch+HEAD, candidate Blueprint SHA and immutable source CAS SHA.
- Existing G3B2A/B fixed-window PCM renderer derives a noncanonical, SHA-bound 180s WAV; actual localhost GET `/v0/sessions/{id}/audio/stream/preview.wav?preview_id={exact_id}` supports byte-range `200/206/416`, bounded <=1MiB HTTP writes, source ID rejection and temp cleanup. Its first-party Native/Routing Browser player clearly marks pending audio not accepted. Verified 180s left/right PCM and no HEAD mutation, with explicit user Accept later yielding exact preview/accepted WAV SHA parity.
- Concurrent consecutive browser Range requests had an observable false `409` due to delayed server-finally lease clearance; the R4 implementation fixes this with early invalid-ID preflight and bounded 3-second serialisation. Wrong/stale Preview never substitutes an accepted WAV.
- Unlike R5, this R4 does not cache a pending candidate across Range requests and can redo DSP per seek. Source-bound ephemeral Preview cache is R5 Draft PR #214, not a merged feature at this milestone.

## Exact promotion gates / 승인 기준
1. R4 implementation `ccdd0ad65c94e1e3a6c3216681ef0a4ffd00e266`: **58/58 workflows, all 62 check runs SUCCESS**, no waived inherited Chromium test.
2. This evidence-bearing successor commit must independently pass the **entire 58/58 workflows and all 62 check runs**, with a renewed permanent R4 Playwright success and unchanged R3 official main.
3. After clean PR HEAD/base and diff, mark PR ready and **expected-head guarded squash merge**. R5 must rebase independently after R4 promotion and pass 59/59 + evidence successor. Keep umbrella #211/#195/#192 and G3B3 user-editing goal open.

## Explicit exclusions / 허위 완성 주장 방지
- G3B3 true user-driven two separate 180s WAV file imports → track/clip Preview and Accept → bus automation → compare and audition → full WAV download → project archive export/reopen is not yet established. Issue #215 documents that full operator test.
- No measured real audio interface latency, human pilot, 100-track scale or real third-party VST/CLAP binary plugin ABI. Neither Browser metadata display nor synthetic constant PCM is full professional DAW validation.
