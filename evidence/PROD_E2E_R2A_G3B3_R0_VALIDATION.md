# G3B3-R0 — real Chromium two-source 180s Studio production evidence / 브라우저 3분 2트랙 실증

## Promotion candidate / 승격 대상

- Official baseline `main`: `d594678d4662369c648ce86ddcca09e2537887d1` (G3B2C-R5 merged).
- Draft [PR #216](https://github.com/Eckommon/MUSICA/pull/216) exact implementation HEAD: `75a95c51b6795ef6faa47c5b82af9c18cedb6c70`, G3B3-R0-only six-file change set. **60/60 distinct GitHub Actions workflow runs SUCCESS and 64/64 check runs SUCCESS** on the same implementation HEAD; dedicated 60th [run #40461005973](https://github.com/Eckommon/MUSICA/actions/runs/40461005973) SUCCESS. No inherited gate was skipped or suppressed.
- This bilingual document is an **evidence successor, not an automatic merge approval**. Its exact commit must independently rerun and PASS 60/60 workflows and all 64 check runs before expected-head guarded squash. If canonical main changes, rebase & rerun.

## Independently audited real Chromium artifact / 독립 파일 검증

- Dedicated GitHub Actions artifact ID `12714651924`, independently downloaded as `MUSICA-G3B3-R0-verified-2x180s.zip` with ZIP SHA-256 **`2caf12319f5a255d75fed93b9e971b970232050f7748779d974b57bb1f20ba1b`**.
- ZIP includes `01-two-180s-accepted-tracks.png`, `02-accepted-user-download.png`, `03-180s-project-reopened.png`, `browser-accepted-180s.wav`, `browser-reopened-180s.wav`, and `proof.json`.
- Independently decoded **both** WAVs using Python `wave`: each is precisely 34,560,044 bytes, 48,000 Hz, 2-channel stereo, 16-bit PCM, 8,640,000 frames / **180.000 seconds**. Each has SHA-256 **`6a7b3cbc3b779a5997b76b673fb6476d7c383cae9776a1f6116b30e2c8b2f6db`**. First, second, 90-second midpoint, and last stereo PCM samples each equal `(3200, -1400)`. Identical SHA establishes deterministic output **after closing/restarting actual Studio and Chromium and reopening the same Project via first-party UI**.
- Browser file-picker imported **two distinct 180s 48kHz WAVs** with content-addressed original hashes: A `ed8574e1153f75d8319bc7eeb1f44d71cd7a7737723a9abecd60fb85b7545afd`, B `860a459191af8b84bbfb5b6ea2aa2851545111caeb0c9253db62755c7565671d`. Original sample frames A `(2000,-1000)`, B `(1200,-400)`; accepted sum `(3200,-1400)`.
- `proof.json` records **four separate visible track/clip Preview→explicit Accept actions**, accepted HEAD transitions only on each actual Accept, resource-only import never advances HEAD, exactly two tracks with one independent clip each, no Browser console errors, SHA-preserving reopen, and generated screenshots. These are synthetic numerical audio fixtures controlled through real first-party Browser UI; they do not establish human musical creativity or sound quality.

## Corrected product failure / 수정된 통합 오류

The initial Browser session revealed competing metadata/Download Range requests and an accepted-parent HEAD swap causing cancellation or HTTP 500. The implementation now (a) does not redundantly set identical media URL during each UI refresh; (b) cancels obsolete media before Preview/Accept/Discard; (c) queues at most two same-session accepted WAV HTTP requests without overlapping active streams or consuming global slots while waiting; and (d) turns only known stale accepted-render HEAD conflicts into explicit fail-closed conflict responses. Unrelated integrity failures are **not** suppressed. Focused accepted WAV HTTP/cache tests **27 passed** earlier; full inherited+new CI at the implementation HEAD confirms the integrated contract.

## Product readiness limits / 과장 금지

This milestone proves **only** a first-party automated Browser flow: separate 2×180s resource imports → 2 track & 2 clip Preview→explicit Accept → 180s accepted WAV download → Studio restart/open → byte-for-byte identical second WAV. It does **not** validate:
- A new *pending 180s mixer edit* audibly compared with accepted mix and accepted afterward in the same full Browser session;
- 180s routed buses + gain/pan automation combined with plugin operations, audio archiving (.musica) and independent import/reopen;
- A real composed musical arrangement, 100-track editing, waveform ergonomics, hands-on human pilot, physical microphone/audio interface/low-latency reliability, real third-party VST3/CLAP binaries, actual live AI-provider creativity quality, or signed Windows distribution.

## Mandatory promotion rule / 병합 관문

1. Recheck exact HEAD/branch/base and that both 60/60 workflows and all 64 checks on this **documentation-bearing successor** succeed.
2. Confirm no changed accepted Project authority or implicit Accept, no stale client audio resumes, screenshot and ZIP audit remain available, no inherited workflow waived.
3. Only then mark #216 ready and **expected-head guarded squash merge**. Keep Issue #215, parent #195/#192 open for wider production. Apply `docs/PRODUCT_EXECUTION_LOOP.md` and `docs/PRODUCT_CAPABILITY_GAP_LEDGER.md` once governance PR has been independently promoted.
