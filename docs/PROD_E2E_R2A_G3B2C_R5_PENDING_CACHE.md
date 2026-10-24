# G3B2C-R5 — source-bound pending WAV reuse / 승인 전 Preview 반복 재생 캐시

**STACKED DRAFT** — Issue #213. Parent #211/#209/#207/#205/#201/#195/#192. Depends on official guarded completion of G3B2C-R3 and R4. This R5 branch currently contains unmerged ancestors; it may not merge before them.

## Intended behavior / 동작
- Cached **unaccepted** candidate WAV is keyed by in-process trusted pending object identity + Studio session, canonical Project root, branch, exact accepted parent HEAD, preview ID, candidate revision ID, Blueprint SHA-256, routed/native mix-plan hash, source CAS SHA-256 and mix sample rate.
- The first Preview WAV byte-Range request derives a 180s WAV via G3B2A/B fixed-window render and promotes only that **noncanonical** derived file to a *separate* pending cache root. Subsequent byte Ranges for the identical pending candidate retrieve slices without recomputing any DSP; they recompute trusted plan identity and re-hash source CAS and output WAV on cache hit.
- Changed/Discarded/Accepted Preview must never be served under its old URL. The server checks the active pending Preview token and accepted parent HEAD before each request and while writing each <=1MiB chunk. A new candidate invalidates old cached identity, without ever accepting an edit. The StudioService **Preview cleanup lifecycle now eagerly deletes idle cached candidates on Accept, Discard, replacement and session close**, while leased in-flight outputs are only deleted after transfer release.
- At most two cached WAV files, each <=256MiB, 5-minute idle TTL, oldest idle eviction, no eviction of leased in-flight output, dedicated non-symlink cache root, prefix-limited crash-orphan cleanup on server restart. Transport continues one active session/two global concurrent streams, correct 200/206/416, Content-Length, Content-Range and SHA-derived ETag from R4.

## Required test evidence / 증거 기준
- Permanent **59th workflow**: two independent already accepted 180s/48k/stereo/PCM16 source WAVs + a pending native gain -6dB candidate. Three distinct first/middle/end Range requests must give exact `(2005,-2500)` frame samples, **one DSP render**, expected output SHA and 8,640,000 frames, no creative HEAD advancement. Check invalid Preview token, Discard invalidation, TTL second render, filesystem symlink denial, Linux process RSS <512MiB.
- Upload the actual full-length noncanonical WAV and `proof.json` for independent SHA/PCM/RSS audit. Whole 59/59 inherited+new workflow suite on exact implementation head and evidence successor must pass before guarded promotion.

## Explicit limitations / 아직 미완료
- The service now eagerly invalidates cached output when a Preview is Accepted, Discarded, replaced or the Studio session closes. An actively leased WAV is removed **after** that transfer's exit, avoiding premature deletion; orphan restart cleanup remains in place. Parallel browser-cache ownership is scoped to one StudioService.
- Browser metadata/playback in the first-party Studio is tested by predecessor R4; **this R5 test itself does not establish actual 180-second human-operated editing or low-latency audio device**.
- Full G3B3 operator source upload→Preview→Accept→routing automation→WAV export→archive reopen, 100-track load, real VST/CLAP plugin binaries and hardware monitoring remain unproven. Do not claim fully usable professional DAW.
