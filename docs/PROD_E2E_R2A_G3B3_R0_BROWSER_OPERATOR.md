# PROD-E2E G3B3-R0 — genuine first-party Browser 2×180s source workflow / 브라우저 3분 2트랙 제작 실증

**STACKED DRAFT**: requires G3B2C-R4 (#212) and G3B2C-R5 (#214) to merge first, then G3B3 clean rebase and exact full CI. Parent Issue #215, umbrella #195/#192.

## Why / 우선순위
R4/R5 separately prove accepted/pending Preview 180s WAV and source-bound Range caches. The final MUSICA goal requires more: a **real first-party Browser user-operated complete production workflow**, rather than pre-seeding an accepted track/clip structure via backend fixtures.

## Actual work in this first G3B3 slice / 구현
- Python creates two **independent, deterministic 180s 48kHz stereo PCM16 WAV files** on disk by bounded 1MiB writes. Each is exactly **34,560,044 bytes**, with different fixed stereo samples: A `(2000,-1000)`, B `(1200,-400)`. No RAM-heavy Playwright audio Buffer serialization: actual Browser `<input type=file>` chooses each file by path, exercising the >16MiB G3B1B staged 1MiB HTTPS-ish localhost transport with SHA validation. No automatic creative Accept upon asset import.
- Launch real Chromium and create a **fresh project of duration 180 seconds using the Studio UI**. In the existing native audio inspector, use the real **Preview add track** button and explicitly click **Accept**, twice, with source-bound revision checks; use **Preview add clip**/Accept twice, one independent source asset per track. Track and clip IDs and accepted HEAD transitions are saved in proof.json.
- No backend-injected accepted tracks/clips. Read back two source CAS hashes and exact track→clip→asset bindings through first-party Studio; Preview must not advance accepted HEAD.
- Real Browser `HTMLAudioElement` obtains **180.0s metadata** from accepted session-scoped WAV Range URL. User clicks visible **Download accepted WAV (bounded stream)**, receives a true 34,560,044B WAV, and code independently verifies 48kHz stereo PCM16/8,640,000 frames, L+R at 0/90/179.999s exactly `(3200,-1400)`, and SHA. No creative HEAD change on download.
- Close Studio and Chromium; start fresh Studio server and Chromium; reopen the same project by name through first-party Open UI; download reopened accepted WAV and verify byte-exact SHA to the first output. Capture screenshots and operator HEAD event transitions, output proof.json and two full WAVs for independent audit.
- 60th permanent dedicated CI workflow; existing 59 GitHub workflow suite remains enabled. Require evidence successor with full 60/60 before guarded merge.

## Explicit limitations / 미완료
- This first G3B3-R0 slice is **native two-track/clip resource import, explicit Accept, playback metadata, output and reopen**. It does **not** yet validate a newly edited *pending* 180s mixer candidate via Browser before Accept, bus routing and gain automation preview/accept, project archive (.musica) reimport and playback, or real human use. Those are next G3B3 increments and remain tracked in #215.
- Synthetic PCM tones are a numerical oracle, **not music quality**, real microphone or device latency, third-party VST/CLAP binary ABI, professional mastering or successful human beta.
- This PR is stacked on R5. The exact implementation head must pass 60/60 workflows; independent downloaded full WAV+proof.sha review; bilingual evidence successor another 60/60; only then guarded expected-head squash after R5 official merge.
