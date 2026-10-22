# G3B2B — Accepted routed 180s / gain automation independent validation
# G3B2B — 승인된 180초 라우팅·게인 자동화 독립 검증

## Promotion provenance / 커밋 이력
- Parent G3B2 Issue [#203](https://github.com/Eckommon/MUSICA/issues/203), [#201](https://github.com/Eckommon/MUSICA/issues/201), #195/#192.
- G3B2A merged main `7fbe235289d7d7526b7b4d1c2e7453625cd2dfe1`. G3B2B isolated *four-file-only* implementation rebased HEAD **`f10229f3c76631e0f68c361c1b7d3c5448548814`**, PR [#204](https://github.com/Eckommon/MUSICA/pull/204).
- **54/54 GitHub Actions workflows SUCCESS; 58/58 individual checks SUCCESS** on that exact HEAD, including 53 inherited gates and new G3B2B permanent workflow; original pre-rebase G3B2B long automation suite also passed all 54 on `74c3354e7f9071eaeddaff8f62c59c3175fd26de`.
- The rebase did *not* reintroduce four G3B2A or original Browser-G2B regression files as duplicate changes. All inherited canonical source files remain on verified G3B2A main.

## Independent audio/WAV artifact audit / WAV 독립 검사
- Exact-rebased-head dedicated run **[#39735593832](https://github.com/Eckommon/MUSICA/actions/runs/39735593832) SUCCESS**. Downloaded artifact **`12406689948`** `musica-prod-e2e-r2a-g3b2b-routed-180s`, ZIP SHA256 **`16abd83ac6d59fb6ed6af335f173508188322d1dd583bf3782433ba9e8cf111e`**, inspected archive members, JSON proof and decoded WAV sample frames independently of the test harness.
- Immutable accepted source A/B: each **180s, 48,000Hz, stereo PCM16, 8,640,000 frames** and distinct SHA `8ab1c0a43ac895ef3dc1ec9b4afa4348726eb396784a878953f122bae4672165` and `f8910ab88b00d52bb19fabb31e8d9ed10419ed0a615945e24253baa2fd32b2a8`. Explicit acceptance creates separate tracks/clips, then approved routing creates Bus A / Bus B / Master.
- `routed-180s.wav`: **34,560,044 B**, stereo PCM16 48kHz, **SHA256 `857a849ef8584ad7ded2a0b0cf6881dcf536fe6f9ba0fdf263c33643eb759c81`**. Exact PCM at first, ramp-midpoint, 90s and last frames `(2005,-2500)`: Bus A static -6dB, Bus B unchanged. Zero clipped samples, accepted HEAD unchanged, re-imported .musica project render SHA identical across different block sizes.
- `routed-automated-180s.wav`: **34,560,044 B**, stereo PCM16 48kHz, **SHA256 `abee94a49c3150fafb35ee10dc403be3c3d78b2f640c4381f0d45d944ea7ccad`**. Real explicitly accepted Bus A gain automation **-6 → -12 dB** via 80 beats, end at frame **2,057,143**, right channel unchanged. Independent decoded samples:
  - frame 0 / -6dB: `(2005,-2500)`
  - frame 1,028,571 / about -9dB: `(1419,-2500)`
  - frame 2,057,143 / -12dB: `(1005,-2500)`
  - frame 4,320,000 and 8,639,999 / held -12dB: `(1005,-2500)`
- Short accepted routing+send+return and native track gain/bus pan automation **byte-exact match the prior legacy `render_routed_mix`** including stable plan hash. New renderer reads only bounded `wave.readframes()`, per-block floats (4096 frame default, 16384 maximum), does not assemble full 180s frame lists, outputs only noncanonical project-private temp WAV and never changes creative authority.
- G3B2B exact-run `proof.json` Linux process peak RSS **194,876 KiB** (about 190.3MiB), includes Studio/CAS/test setup, not a precise isolated DSP memory benchmark. Output WAV capped at 256MiB; source integrity and accepted HEAD verified after rendering. CPU/wall time and memory for arbitrary 100-track projects unproven.

## Scope limits / 실제 제품 완성 여부
- **Not full DAW:** 180s Browser preview/accepted audible WAV still passes through legacy in-memory Studio render paths. G3B2C R1 Draft #206 adds an opt-in accepted HTTP Range endpoint but is unmerged and not a Browser UI replacement. G3B3 full operator 180s 2-track production, export/reopen, long-pan automation, external hardware/real plugins/realtime low latency not validated.
- Preview → explicit user Accept remains the only source of canonical revision mutation. Derived output is not source media or canonical creation. Full project audit memory bounds and atomic crash recovery are not proved.

## Mandatory second gate / 필수 후속 검증
This is a durable evidence successor. Do **not** merge until exact document-bearing successor commit passes **54/54** full workflows, then reconfirm PR head/main and merge with `expected_head_sha` protected squash. Keep #201/#195/#192 and #205 OPEN.
