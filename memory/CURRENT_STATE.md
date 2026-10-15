# MUSICA Current State / 공식 현재 상태

**Last state refresh / 상태 기준:** 2026-10-15, post-PLUG-R3B expected-head squash merge. **Canonical GitHub `main`: `5ca2836639c348eaa7efb65fc2c03eb452ea9867`.** This is the new truth after PR #176. If `origin/main` later advances, inspect the new exact HEAD/CI and update these pointers before acting.

## Product phase / 제품 단계

**AI-native core creative control VALIDATED — bounded; native audio, mixer routing, simulated realtime and recording foundations VALIDATED — bounded; simulated plugin two-bus causal offline PDC and Studio/Browser plugin edit loop VALIDATED — bounded; one-song integrated production, real third-party plugin binaries, physical-device support and commercial-release readiness NOT YET VALIDATED.**

장기 목표: 사용자의 자연어 의도에서 실제 편곡·녹음·믹싱·수정·저장·출력까지 MUSICA 내부에서 완결하는 범용 음악 제작 프로그램. 단, 모든 생성·실행·Browser·미터·플러그인 런타임 상태는 승인된 Music Blueprint/Project revision을 역으로 수정할 수 없습니다.

## Completed project foundations / 완료한 제한적 기반

| Track | Issue | Evidence |
|---|---|---|
| M0–M7 + revision Compare | #89 | accepted creation/edit/automation/compare; `evidence/POST_M7_REVISION_COMPARE_VALIDATION.md` |
| ATCM audio assets/tracks/clips/mixer | #95 CLOSED | `evidence/ATCM_R4_VALIDATION.md` |
| MRAM routing + native mixer automation | #115 CLOSED | `evidence/MRAM_R3_VALIDATION.md` |
| RTIO simulated realtime callback/runtime | #129 CLOSED | `evidence/RTIO_R3_VALIDATION.md` |
| REC simulated capture/monitoring + trusted finalize | #142 CLOSED | `evidence/REC_R3_VALIDATION.md` |
| PLUG-R0 simulated processor contract | #156 CLOSED; PR #158 MERGED | `evidence/PLUG_R0_VALIDATION.md` |
| PLUG-R1 accepted master plugin state | #159 CLOSED; PR #161 MERGED | `evidence/PLUG_R1_VALIDATION.md` |
| PLUG-R2 offline two-path causal PDC | #162 CLOSED, #166 CLOSED; PRs #165/#167/#168/#169 MERGED | `evidence/PLUG_R2B_K1B_VALIDATION.md` |
| PLUG-R2B K2 Studio accepted opt-in offline WAV | PR #171 MERGED | `evidence/PLUG_R2B_K2_VALIDATION.md` |
| PLUG-R3A Studio Preview→Accept | PR #173 MERGED | `evidence/PLUG_R3A_STUDIO_VALIDATION.md` |
| PLUG-R3B real Browser editing | #174 CLOSED; PR #176 MERGED | `evidence/PLUG_R3B_BROWSER_VALIDATION.md` |

Last verified PLUG-R3B implementation head `7ed8c8e40235716edf16349c6e360ace2bc5a333`: **41/41 SUCCESS**. Evidence/validation successor `f572a9466fad7989d6c2feb76e32a158d6031c06`: **41/41 SUCCESS**, expected-head squash merge `5ca2836639c348eaa7efb65fc2c03eb452ea9867`. Dedicated corrected-head Chromium run `38654626234`, artifact `11936550747`, independently verified ZIP SHA-256 `8f9f14da6211c6975355c54848a657a4d7011f228e472e696cf92f0e2d685570`; two-bus alignment frame 9 stereo PCM16 `(24576,24576)`, bypass with 5 creative frames preserved.

## Live program gaps / 진행 중인 진짜 제품 격차

- **#155 Plugin Hosting & Latency Compensation Foundation v0:** parent OPEN pending **evidence-backed scoped closure evaluation** of its 17 minimum requirements. All current plugin success is simulated/offline only; no actual plugin binary or realtime PDC. Parent v0 closure must NOT be misread as a real plugin ecosystem.
- **#177 PLUG-R4:** real authorized plugin ABI feasibility, licensed SDK selection and actual binary execution proof OPEN. One format and one supported OS first.
- **#178 PROD-E2E-R0:** a real one-song end-to-end production vertical slice OPEN; integrate accepted arrangement, routed audio, automation, simulated plugin, human Preview/Accept, A/B compare, WAV deliverable and export/reopen. Report any unsupported step transparently.
- Windows physical device/recording, general routing and plugin graphs, audible end-to-end real production, real provider generation quality, deep waveform/comping/warp, long-session robustness, migration/installer/security/licensing, product UX and commercial acceptance **remain unproven**.

## Authority and promotion / 권한·검증 규칙

```text
accepted exact Project revision
→ typed source-bound candidate + constraints + locks
→ Preview (NOT ACCEPTED)
→ explicit Accept only
→ new immutable canonical revision
→ deterministic/declared derived media and Browser projections
```

- No rendered or recorded samples may silently become canonical. No browser/plugin/device callback commits creative state.
- For changes with new contracts: implementation+numerical evidence, exact-head all green, independent artifact/hash/PCM, durable validation, full CI on successor, **expected-head squash merge**.
- Do not conflate deterministic simulated backend with physical I/O; do not treat synthetic plugin delay as real plugin-reported latency.
- If CI/browser fails, investigate or rerun genuinely transient environment failure, never waive a required gate.
- Product success requires both feature-specific correctness and at least one truthful integrated production workflow; green CI alone is not a product-completion verdict.

**Exact next action is `memory/NEXT_ACTION.md`. Repository evidence outranks chat and outdated historical milestone documents.**
