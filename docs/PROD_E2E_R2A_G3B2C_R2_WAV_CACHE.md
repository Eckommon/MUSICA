# G3B2C-R2: reusable accepted WAV file / 승인된 오디오 재사용 캐시

**STACKED DRAFT — depends on G3B2B #204 and G3B2C-R1 #206.** Issue #207; parent #205/#201/#195/#192.

## Actual implementation / 실제 구현
- Derived, explicitly **noncanonical** WAV output is keyed by Studio session, resolved Project root, accepted branch/HEAD, trusted gain/pan/routing mix-plan SHA, PCM sample rate and **ordered immutable source CAS SHA**. Client cannot supply an arbitrary path or accepted revision.
- First HTTP request does a fixed-block 180s render and privately stages the result in the Studio workspace cache. Subsequent requests for the same accepted source fetch only byte ranges from this file; they revalidate current plan identity, source CAS content hashes and cached file SHA, never rerendering merely because of a Browser seek.
- At most **two 256MiB derived WAVs** in one Studio server; default **5-minute *idle* TTL** (lazy cleanup at next access/release), oldest idle entry eviction, active-lease eviction forbidden, per-session HTTP stream serialisation and two global concurrent streams inherited from R1.
- Startup cleans only prefixed derived WAV orphan files inside a dedicated non-symlink workspace cache directory; no real source CAS or user file deletion. All outputs remain derived and are never added to accepted Project revisions by HTTP.

## Evidence requirements / 검증 관문
- Permanent **56th GitHub workflow** with complete inherited 55 workflows, no disabled or bypassed tests.
- Real 180s two-independent-source 48kHz PCM accepted mix, 3+ distinct Range requests at start/mid/end; exact stereo PCM values and byte-range SHA; **one and only one DSP render**, unchanged accepted HEAD, bounded RSS. A downloadable **34,560,044-byte WAV + proof.json** records original CAS SHA values, WAV SHA, three range positions, render count, sample format and Linux process peak RSS for independent audit.
- Accepted short WAV 200/206/416 legacy byte parity; TTL expiry forces one new render; crash/restart orphan cleanup; cache corruption or changed source CAS fail-closed; multiple sessions/quota and proper lease release.
- CI success on exact implementation head, independent real browser/HTTP evidence, bilingual evidence successor complete CI, then expected-head guarded merge *only after* G3B2C-R1 main promotion.

## Unproven / 아직 구현되지 않은 제품 요소
- **Project Studio view and pending Preview still contain legacy whole-WAV `wav_bytes` computations**. Therefore opening a 180s project in the first-party GUI is not proven memory-bounded even though the new accepted-only HTTP Range path reuses derived audio.
- Browser user-operated 180s 2-track source import → explicit Preview/Accept → routed automation → play/seek/export/archive reopen, device latency and real plug-in binary interfaces remain unproven.
- Cache hit currently streaming-checks **source hashes and cached file hash**, which is I/O proportional to audio length but is still significantly less CPU work than rerunning PCM DSP; no performance guarantee yet for arbitrary track counts.
- No remote server authentication or commercial real-time mastering quality is asserted.
