# PLUG-R2B K2 Validation — Truthful Studio Accepted Bus Host Inspection & Opt-in WAV

## Exact bounded verdict

**PASS — exact accepted Project bus-host state is surfaced in the Studio session and rendered through a separately requested offline WAV endpoint; default Studio media/realtime callbacks remain unchanged.** This is NOT native VST3/AU/CLAP hosting, browser graphical editing, or realtime PDC.

Parent #155 and R2 #162 remain OPEN pending their own scoped disposition and Studio/editor lifecycle evidence. K1-B prerequisite PR #169 merged canonical main `6c18b95e6c38d960b4623bc40323827b6b05e491`.

## Evidence and immutable implementation identity

- PR #171, branch `feature/plug-r2b-k2-studio-audition-clean`
- exact implementation/evidence head `78fa0485f607054201561055f7d044b81d590f31`: **39/39 GitHub Actions SUCCESS**.
- dedicated `PLUG-R2B K2 Studio Accepted Bus Host Inspection & Offline Audition Evidence` run **38594364595**, SUCCESS.
- artifact ID **11908558696**, ZIP size **4,324 bytes**, GitHub-recorded and independently recomputed ZIP SHA-256:
  `c4ed214d4e61ca2646c3a87841cddb6b54aab813cec4c993a194663564bc52be`.
- independently opened actual ZIP, verified 5/5 manifest payload member SHA-256 and bytes; dedicated workflow independently checks its 7 source-contract inventory entries and identical A/B generated evidence directories.

## Numeric PCM + Studio authority oracle

- True accepted-source session; explicit read-only `GET /v0/sessions/{id}/bus-plugins` returns revision/project, exact accepted host-material/source hashes, accepted instances, honest availability/scope.
- Separate `GET /v0/sessions/{id}/bus-plugins/media/accepted.wav` renders using accepted Project engine and K1-B simulated bus-host material, never injecting browser WAV/config and never writing Project HEAD.
- WAV is stereo PCM16 at **8,000 Hz**, **96,000 frames**; accepted opt-in output frames **0–8** are zero and frame **9** is **(24576,24576)**.
- Existing legacy WAV frame **3** is **(24576,24576)** and separate; opt-in audition did not replace default Studio media.
- The independently recomputed accepted opt-in WAV SHA matches the Studio view's `offline_audition.wav_sha256`; plan hash matches accepted source.
- Unsupported legacy/empty-routing project returns inspectable accepted metadata and `offline_audition.available=false`, not a false audition claim; invalid Studio session produces 404.
- `native_vst3_clap_au_host=false`, `realtime_pdc=false`, `default_studio_media_overridden=false`; GUI editing, live runtime PDC, plugin binaries remain unproven.

## Promotion gate

This durable validation document changes the PR HEAD. **Only merge after successor exact-head 39/39 SUCCESS** and source/workflow inspection, via expected-head squash. Keep parent scope honest. Next rung: source-bound Studio bus-plugin Preview->explicit Accept and Browser editing, supported topology only; no unvalidated realtime/native plugin claims.
