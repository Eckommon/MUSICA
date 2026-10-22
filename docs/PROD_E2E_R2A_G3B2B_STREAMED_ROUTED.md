# G3B2B — bounded routed 180s stereo WAV / 라우팅·오토메이션 스트리밍

**Draft on stacked development branch / 선행 G3B2A 병합 전 후속 초안**. Issue #203, parent #201/#195/#192.

## Added renderer / 신설 기능
- `render_routed_mix_streamed` compiles the exact **accepted HEAD** through the existing trusted `build_routed_mix_plan`, including routing graph, track/bus/send/master and source-bound native automation gain/pan lanes.
- For each fixed ≤16,384-frame window, read only overlapping PCM source frames, compute post-fader track sends, ordered routing node sums/process/sends, and hard-clipped stereo PCM16. Keep `value_at_frame` global frame coordinates so automation ramps do not reset at chunk boundaries.
- Preserve original `render_routed_mix` unchanged. Private, noncanonical WAV-to-file and SHA-only reporting, optional cancellation and required accepted HEAD/source CAS SHA recheck. Never Accept any creative revision or add WAV to canonical CAS.
- 256MiB derived stereo output file cap, no 3-minute float arrays. Memory scales with active tracks/routing nodes and output block size, rather than duration.

## Explicit test gates / 증거 조건
- Byte-identical 12s legacy routed mix with track send, return and master over two different window sizes, same clipping/peak and stable plan hash.
- Byte-identical short accepted native automation (track gain + bus pan ramps), relative/absolute frame boundary semantics.
- Two independently accepted 180s/48kHz/stereo PCM16 sources → two accepted group buses (Bus A -6dB, Bus B unity) → master → 180s output WAV with numerical channel oracle; source-bound .musica archive reopen and second block-size SHA parity; Linux RSS <512MiB. Additional independently accepted Bus A gain automation ramp -6dB → -12dB over 80 beats renders the entire 180s WAV, with explicit first/mid/end PCM oracle and independent JSON/WAV evidence.
- Dedicated 54th permanent workflow and downloadable 180s WAV+JSON. Full 54/54 inherited checks, independent SHA/PCM evidence + bilingual validation successor, then guarded merge; no skipped tests.

## NOT yet done / 한계
- G3B2C first-party HTTP/Browser noncanonical file audition/export and G3B3 real 180s human-flow full-song accepted mix/restart/reopen.
- Long 180s **gain automation** is covered by a dedicated accepted-bus-ramp WAV and frame-based PCM oracle; 180s pan automation still requires its own independent case.
- No live Windows/macOS hardware latency, real VST/CLAP/third-party binaries, mastering grade claim, or complete project-wide bounded integrity / crash journal.
