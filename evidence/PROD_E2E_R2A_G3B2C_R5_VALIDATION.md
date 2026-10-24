# PROD-E2E R2A G3B2C-R5 — source-bound pending WAV seek-cache validation / 승인 전 180초 반복 청취 검증

## Status and authority / 상태·정본
- Parent R4 is still DRAFT PR #212; R5 is **stacked DRAFT PR #214** with issue #213. R3 has officially merged to `main=f4414ffddf5a78744d86698088d18795a9f788c5`.
- Original implementation HEAD `808b2c0548c0a50de366ed0595c885b1a4deb1b7` passed **59/59 GitHub Actions workflows and 63/63 individual checks** including dedicated 59th cache workflow run [#39969888960](https://github.com/Eckommon/MUSICA/actions/runs/39969888960). No CI gates waived.
- The R5-only change set was **rebased onto R4's R3-main-based implementation** with five files. Rebased implementation HEAD `23a413bd6fe5b64a098495fe712459b349359fa3`. **This rebase must independently pass all 59 workflows and all 63 checks**; original head success is not sufficient. R4 must first finish its own implementation, bilingual evidence successor, and guarded main merge, after which R5 must cleanly rebase to the new canonical main and revalidate.

## Independently audited real 180s candidate WAV / 독립 산출물
- GitHub Actions dedicated artifact ID **`12510273451`**, downloaded as `MUSICA-G3B2C-R5-Pending-180s-Range-Cache-Proof.zip`. ZIP SHA-256 **`088d1cc5b698e6159a278051a26dc537389541eaf02ed9416e55526fcce2985e`**. Archive contains one real **34,560,044-byte WAV** and `proof.json`. Its stored ZIP is compressed (~34KB) because the source PCM is synthetic constant amplitude; this does not reduce the decoded WAV's full 180-second length.
- Independently parsed the PCM16 WAV with Python `wave`: **48,000Hz, stereo, 2-byte samples, 8,640,000 frames = 180.000 seconds**. SHA-256 **`857a849ef8584ad7ded2a0b0cf6881dcf536fe6f9ba0fdf263c33643eb759c81`**, byte-exact match to embedded `proof.json`.
- Decoded stereo samples at first frame, frame 1, midpoint (4,320,000), and final frame (8,639,999): **left 2005 / right -2500** on all four checks; the -6dB pending native mixer candidate differs from the approved left mix of 4000 and has not been automatically Accept'ed.
- Three actual session-bound HTTP byte Ranges: `bytes=44-47`, `bytes=17280044-17280047`, `bytes=-4`, with only **one whole-song DSP render** (`dsp_render_count=1`) for the same still-active unaccepted candidate. Accepted HEAD `rev-audio-bd68cb08f953bd30bbd7d7dd84412e79` unchanged.
- Distinct immutable source object CAS SHA values: A `8ab1c0a43ac895ef3dc1ec9b4afa4348726eb396784a878953f122bae4672165`; B `f8910ab88b00d52bb19fabb31e8d9ed10419ed0a615945e24253baa2fd32b2a8`.
- Maximum Linux CI-process RSS **195,756KiB** (about 191.17MiB) and test suite verifies under 512MiB. These are synthetic repeatability metrics, not subjective audio fidelity or realtime latency guarantees.

## Security, cleanup, and limitations / 남은 과제
- Pending candidate source/accepted-parent revision/Blueprint/mix plan/original CAS hash and cached derived output SHA are verified. Wrong/discarded Preview IDs must fail before serving cached WAV. TTL 300 seconds, maximum two 256MiB files, no lease eviction, symlink root denial and prefixed orphan startup cleanup. Corrupt cache output triggers derived WAV re-render.
- Eager deletion upon every Accept/Discard/replace without a following cache request is not yet guaranteed. Browser actual 180s Preview evidence belongs to R4; **this R5 proof does not claim a human created or exported/reopened a finished 180s piece**.
- Real use end-to-end G3B3 operator import, edit, Preview, explicit Accept, routing+automation, export, archive and reopen; physical device latency and real VST/CLAP binary plugin ABI remain open.

## Promotion gates / 병합 조건
This evidence is part of the R5 proposed successor **not an authorization to merge**. Require clean R5-only commit against **promoted R4 main**, **59/59 workflows + all check runs** on both implementation and evidence successor, inspect latest downloadable artifact SHA, mark PR ready and expected-head guarded squash. Keep parent #211/#195/#192 and G3B3 open until complete.
