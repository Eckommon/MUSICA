# PROD-E2E-R1B-G0 — Guided One-Song Browser Journey / 한 곡 제작 안내

**Status / 상태: DRAFT (implementation and CI unvalidated).** Parent issues #183 → #181 → #178.

## User operation / 사용자 흐름

In MUSICA local Browser Studio, create or open a song project and select **Inspect → One-song production guide**. The guide links to *existing* trusted first-party Studio controls rather than hiding source/Preview/Accept transitions.

1. Create/open a local accepted project. / 승인된 로컬 프로젝트 생성·열기.
2. Import an integer-PCM mono/stereo WAV resource with the existing 16 MiB bounded importer. Import itself never edits accepted music state. / 가져오기는 자산 저장만 수행.
3. Navigate to native **Add Track** → Preview → explicitly **Accept**. Navigate to **Add Clip**, use resource ID → Preview → explicitly **Accept**. / 트랙과 클립을 따로 승인.
4. Use native mixer manually; routing and automation are optional and availability/topology-gated. No automatic routing, fabrication of lanes or auto-Accept. / 믹싱·라우팅·자동화는 지원 범위 내에서 직접 작업.
5. The guide shows progress **from accepted audio source projection**, not from file picker presence. It identifies the SHA-256 and sample rate of the accepted-derived noncanonical mix, blocks download while a known Preview is pending and checks fresh accepted HEAD / Preview on the server when clicked. **Download accepted WAV** is distinct from **Export .musica**.
6. Reopen project and confirm accepted revision and derived WAV hash / bytes.

## Explicit limits / 제한

G0 is a **navigation and guarded delivery bridge**, not a complete musical arrangement editing implementation. Routing/automation are *optional*, and the guide does not claim they were exercised just because buttons are visible. Real Chromium automated file chooser/click testing is not real-human usability proof; no full-length professionally mastered song, 48kHz physical hardware callback, microphone, or real VST3/CLAP/AU binary is proven.

## Promotion criteria / 병합 전 필수 검증

1. Real Playwright Chromium evidence including source head invariance on Import/Preview, two explicit Accepts, blocked pending download, WAV file downloaded with nonzero samples and exact SHA, exported .musica and restart/reopen byte equality.
2. New 44th permanent workflow and all inherited workflows success on the same exact implementation SHA; independently inspect CI artifacts (ZIP SHA, manifest if provided, numerical WAV and screenshots).
3. Bilingual durable validation file committed after first results; all 44 workflows successful **again** on exact validation-successor SHA; only then mark ready and expected-head squash merge.
4. Do not close parent #181 or #178: later R1B must demonstrate integrated arrangement/routing/automation and longer multi-track creation. / 상위 목표는 유지.
