# G3B3-R1A — actual Chromium edited 180s mixer Preview/Discard/Accept evidence

## Baseline and exact authority / 정본
- Real first-party G3B3-R0 two-user-WAV workflow officially promoted by [PR #216](https://github.com/Eckommon/MUSICA/pull/216), `main=4e4e8866652a7e49ca706c6e2e959bbccc96790e`, after **60/60 workflows + 64/64 individual check runs** for both implementation and evidence successor.
- Original stacked G3B3-R1A [PR #219](https://github.com/Eckommon/MUSICA/pull/219) exact head `af04d870843380cc6890dddedc953b7c35f3e8f9` passed **61/61 GitHub workflows and 65/65 check runs**. Its permanent dedicated real Chromium [run #40640688033](https://github.com/Eckommon/MUSICA/actions/runs/40640688033) SUCCESS.
- R1A-only three files were rebuilt over product-goal governance evidence head `42d387878aa5f81a3686816c36e51c0bb1270039`, exact rebased implementation `d9513632f523aa699b538b612bf77143948ccd1b`, containing **62 workflows (including governance)**. This head and this bilingual evidence successor **must each achieve all 62 workflow/check run successes before promotion**; earlier 61/61 cannot substitute. Product-goal governance PR #218 must first be merged; then R1A-only clean rebase to that canonical main and full CI rerun.

## Independent physical artifact audit / WAV 독립 파일 검사
- Actual dedicated artifact ID `12797110166`, downloaded as `MUSICA-G3B3-R1A-180s-Mixer-Preview.zip`, **ZIP SHA-256 `1f88ad22f05d477fa7872e6ab739078f9cca126d827f86282634f61b3970a2c4`**. Independent Python `zipfile`/SHA/`wave`/raw `struct` audit opened its bytes (not merely the workflow report).
- ZIP contains 4 genuine first-party Chromium screenshots (`01-180s-pending-discard.png`, `02-pending-180s-mixer-before-accept.png`, `03-accepted-180s-mixer.png`, `04-edited-180s-reopened.png`), `proof.json` and **two actual 34,560,044-byte WAV files**.
- Both edited accepted and restarted/reopened WAV files are exactly 48,000 Hz, stereo, 16-bit PCM, 8,640,000 frames = **180.000 seconds**. **Both WAV SHA-256 = `cde5433db5bfe137b9d195e132e4178fb87dddc5f181920426a7638bd8d96dbb`**. Independent first/90-second/last PCM frames all **`(2202,-901)`**.
- Original accepted two-file mix WAV SHA `6a7b3cbc3b779a5997b76b673fb6476d7c383cae9776a1f6116b30e2c8b2f6db`, PCM `(3200,-1400)`, **different** from edited pending mix and accepted outcome. Unaccepted -3dB track-A mixer Preview was Auditioned, then explicit Browser Discard kept accepted parent HEAD unchanged and stale Preview ID was denied. New -6dB track-A mixer Preview changed actual PCM at 0s/90s/end while accepted HEAD remained fixed. Only Browser **explicit Accept** advanced accepted revision to `rev-mixer-46f64c07e3cbf4a4b82f1f0fe6875ca8`, and newly accepted output WAV SHA **exactly matched the pre-Accept Preview ETag SHA**. After full Browser+Studio restart, accepted WAV SHA/PCM and revision were unchanged; browser console errors: none.
- This validates a real **user-interface-driven native mixer alternative with audibly different actual output PCM**, not the subjective claim that a human listened on speakers.

## Scope boundary and future P0 / 실제 비검증
- NOT YET: long-song **routed bus send/automation** through real first-party Browser Preview/Accept; actual **.musica archive file export → clean separate workspace import/reopen**; real song/AI-human editing quality; physical Windows audio interface latency; native VST3/CLAP binaries; app distribution and human user pilot. All remain product gap ledger C03-C10 / Issue #217.
- The exact-first-party tested file's samples are deterministic constant PCM to provide an oracle. Do not equate this with a mixed real musical performance.
- No affected accepted Project state may be mutated by Browser observations, input file hashing, Preview playback, branch HEAD races or downloaded bytes. Explicit Accept is sole creative mutation.

## Required promotion gate / 병합 관문
- Complete governance PR #218 full exact implementation+evidence CI and expected-head guarded promotion to official main first.
- Rebase only R1A four changed files on new official main, verify real first-party Browser full 180s pending audio and physical SHA proof. Full **62/62 workflow and every check run green** on both implementation and evidence successor; correct any inherited failures without disabling checks; expected-head guarded squash merge.
- Maintain compact outcome record and select next P0 sliced Issue #217: first supported 180s routed/automated mix in Browser, then actual portable .musica archive roundtrip. Update README/state and gap ledger after promotion.
