# MUSICA — AI-native Programmable Music Workstation / AI 기반 음악 제작 워크스테이션

> **Create music by intent while every important musical decision stays inspectable, lockable, editable, reproducible, and programmable.**  
> **누구나 의도로 음악을 만들고, 중요한 음악적 결정은 검사·잠금·편집·재현·프로그래밍할 수 있도록 한다.**

MUSICA is an **AI-native, local-first, programmable music production workstation under active development**, not a finished commercial DAW. Its long-term governing goal is a **general-purpose, commercially usable production application** that preserves the accepted creative-state authority model.

MUSICA는 **개발 중인 AI-native 로컬 우선 음악 제작 프로그램**입니다. 장기 목표는 일반적인 음악 제작을 내부에서 완결하는 **범용·상용 워크스테이션**이며, 현재 상용 완성 또는 모든 하드웨어/플러그인 호환을 주장하지 않습니다.

## Canonical authority / 공식 창작 권한

```text
Describe → Generate Blueprint → Audition → Lock → Refine → Compare → Accept
사용자·AI 제안 → typed source-bound Preview (NOT ACCEPTED)
             → explicit human Accept
             → immutable accepted Project/Blueprint revision
             → derived render / Browser / plugin / realtime state
```

The accepted Project revision—not Browser, plugin, renderer, waveform cache, AI output, microphone capture buffers, or raw WAV—remains authoritative until an explicit trusted Accept. Source hashes, constraints, locks, revisions, and deterministic evidence protect the edit boundary.

## Validated bounded foundations / 제한된 범위에서 검증한 기반

| Stage | Evidence-backed bounded scope |
|---|---|
| M0–M7 + Post-M7 | intent/Blueprint, Music Director provider contract, Browser Studio, note/semantic editing, automation, renderer, MIDI/DAWproject interchange and accepted-revision A/B comparison |
| ATCM #95 | immutable native audio assets; accepted audio tracks/clips; bounded mixer, deterministic mix and reopen |
| MRAM #115 | accepted routing/sends and supported mixer automation; Browser/Studio inspection; deterministic routed execution |
| RTIO #129 | simulated backend callback/transport/latency/dropout instrumentation and truthful Browser runtime |
| REC #142 | deterministic simulated capture/monitoring, recording finalize Preview→Accept, Browser lifecycle |
| PLUG-R0/R1 | bounded **simulated** plugin descriptors/state and accepted master processing authority |
| PLUG-R2 #162 | accepted two-bus **simulated** algorithmic latency, actual causal offline alignment, independent creative delay, bypass/error fail-closed |
| PLUG-R3 #174 | Studio + real-Chromium Browser two-bus simulated plugin add/update/bypass/remove → Preview audition → explicit Accept/Discard, exact reopen |

**Latest official merged production stage (checked 2026-10-28):** G3B2C-R5 [PR #214](https://github.com/Eckommon/MUSICA/pull/214), canonical main `d594678d4662369c648ce86ddcca09e2537887d1`. Exact R5 evidenced accepted/pending 180s WAV Range and cache. **Next: G3B3-R0 [PR #216](https://github.com/Eckommon/MUSICA/pull/216) is Draft.** Its implementation `75a95c51b6795ef6faa47c5b82af9c18cedb6c70` passed 60/60 workflows and 64/64 checks. First-party headless Chromium picked two independent 180s WAVs, explicitly accepted 2 tracks + 2 clips, downloaded 180s stereo WAV, reopened Studio and downloaded an exact-SHA-identical WAV. **Its evidence successor is not yet promoted**. These are synthetic PCM fixtures in actual Browser controls, not a hands-on human musical pilot.

**Fixed product execution loop (proposed PR #218):** `docs/PRODUCT_EXECUTION_LOOP.md`, `docs/PRODUCT_CAPABILITY_GAP_LEDGER.md`, machine-readable `governance/product_gap_ledger.json` and a CI enforcement gate; status remains Draft until exact-head full CI + guarded merge.

## Getting started / 로컬 실행

Python **3.11+** required. From an authorized local checkout:

```powershell
python -m pip install -e ".[dev]"
musica-studio --workspace ".\MUSICA-Workspace"
```

Opens localhost Browser Studio (default port 8765). For real-Chromium development/evidence, install the `e2e` optional dependency and Playwright Chromium separately. This is a **developer install**, not an end-user Windows installer.

## Next product mission / 다음 개발

1. **Finish [G3B3-R0 #215 / PR #216](https://github.com/Eckommon/MUSICA/pull/216)**: evidence successor exact full CI, inspect actual Browser two-WAV exports/restart SHA, expected-head guarded merge. No previous CI success transfers across SHA.
2. **Ratify [product-goal execution loop PR #218](https://github.com/Eckommon/MUSICA/pull/218)**: capability gap ledger, P0 safety/user-journey blockers, measurable PLAN→EXECUTE→VALIDATE→IMPROVE→RELEASE/ROLLBACK→NEXT, permanent CI and updated state documents.
3. **[G3B3-R1 #217](https://github.com/Eckommon/MUSICA/issues/217)**: in the same actual 180s two-source Browser session, pending mixer editing and audible A/B before explicit Accept; supported routed gain automation; true .musica archive export, fresh import and exact WAV/plan/source parity.
4. **Real general-purpose evidence:** waveform/undo/comping and crash recovery, live AI provider quality and lock preservation, physical Windows device monitoring/latency, one licensed third-party plugin binary [#177](https://github.com/Eckommon/MUSICA/issues/177), supported installer and human usability pilot. Simulated RTIO/plugin tests are not substitutes.

## Current nonclaims / 현재 지원이 입증되지 않은 범위

- **No verified commercial-general-purpose DAW completion**, user productivity study, or mastering-grade sound-quality verdict.
- **No native third-party VST3/CLAP/AU binary hosting, plugin scanning, sandbox security or realtime plugin PDC.**
- **No verified physical microphone/audio-interface hardware path, Windows device low-latency/dropout SLA or arbitrary routing graph compensation.**
- **No broad time-stretch/warp, sophisticated comping, universal channel/sample-rate conversion, full DAW state interchange, live OpenAI provider evidence, installer/signature/update or cloud collaboration claim.**

## Source of truth / 공식 기록

`docs/PRODUCT_THESIS.md` · `docs/COMMERCIAL_WORKSTATION_TARGET.md` · `docs/PRODUCT_EXECUTION_LOOP.md` · `docs/PRODUCT_CAPABILITY_GAP_LEDGER.md` · `memory/CURRENT_STATE.md` · `memory/NEXT_ACTION.md` · `evidence/` · exact GitHub PR/issue/CI artifacts.

**Exact accepted evidence and merged Git history > current state docs > Issue/PR descriptions > chat summaries.** Archived PR-specific acceptance documents keep their historical statuses; they are not today's active next action.
