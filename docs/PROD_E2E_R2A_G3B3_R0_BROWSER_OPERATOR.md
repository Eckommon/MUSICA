# PROD-E2E G3B3-R0 — genuine first-party Browser 2×180s source workflow / 브라우저 3분 2트랙 제작 실증

**IMPLEMENTATION DRAFT / NOT MERGED**: G3B2C-R4 (#212) and R5 (#214)
are officially merged, latest baseline `main=d594678d4662369c648ce86ddcca09e2537887d1`.
The G3B3-only branch has been reconstructed on that exact baseline. Full 60-workflow
implementation CI, independent WAV/artifact review and bilingual evidence successor
60-workflow CI are still required before guarded merge. Parent Issue #215,
umbrella #195/#192.

## Why / 우선순위
R4/R5 separately prove accepted/pending Preview 180s WAV and source-bound Range caches. The final MUSICA goal requires more: a **real first-party Browser user-operated complete production workflow**, rather than pre-seeding an accepted track/clip structure via backend fixtures.

## Real-browser failure discovered and corrected / 실제 브라우저 발견 사항
- The first dedicated 60th workflow successfully completed **both real 34.56MB user-file imports, four explicit Preview→Accept actions, first full-length accepted WAV download and PCM verification**. It initially failed **only on the immediate download after reopening the Project** because Chromium was simultaneously requesting accepted-audio metadata: the old accepted HTTP handler rejected same-session requests after a 3-second busy grace, causing the second download to be cancelled.
- Corrected the accepted Range transport to queue **at most two same-session waiting requests for up to 120 seconds**, without holding a global streaming slot while waiting, while still enforcing one active stream/session and two concurrent global streams. Preserved fail-closed behavior for a third waiter and malicious sessions. Strengthened the preexisting accepted-WAV session-busy unit test and added a deterministic two-waiter/no-third test; this is a legitimate changed contract, **not disabled regression coverage**.
- A subsequent real Chromium CI run completed the audio output and reopen SHA steps, but surfaced **background stale accepted-WAV Range requests (HTTP 500)** when explicit Preview/Accept advanced HEAD while the Browser reloaded the same player URL. The new corrective implementation avoids unchanged-authority `src` reassignments, cancels obsolete media before Preview/Accept/Discard, and classifies render-time accepted HEAD changes as a fail-closed conflict (HTTP 409), with a targeted negative test. The permanent Chromium run must prove that there are no unexpected console errors before this can be called fixed.
- The corrected exact implementation and the full 60-workflow CI are pending. No claim of successful Project reopen/download until new permanent Browser evidence passes.

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
