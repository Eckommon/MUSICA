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

**Latest merged Browser stage:** PR [#176](https://github.com/Eckommon/MUSICA/pull/176), canonical main `5ca2836639c348eaa7efb65fc2c03eb452ea9867`, exact implementation head `7ed8c8e40235716edf16349c6e360ace2bc5a333` **41/41 CI**, evidence-record successor `f572a9466fad7989d6c2feb76e32a158d6031c06` **41/41 CI**. Durable proof: `evidence/PLUG_R3B_BROWSER_VALIDATION.md`. This is a **bounded simulated plugin Browser milestone**, NOT a third-party native plugin host.

## Getting started / 로컬 실행

Python **3.11+** required. From an authorized local checkout:

```powershell
python -m pip install -e ".[dev]"
musica-studio --workspace ".\MUSICA-Workspace"
```

Opens localhost Browser Studio (default port 8765). For real-Chromium development/evidence, install the `e2e` optional dependency and Playwright Chromium separately. This is a **developer install**, not an end-user Windows installer.

## Next product mission / 다음 개발

1. **Product state alignment and bounded plugin v0 closure assessment**: `memory/CURRENT_STATE.md`, `memory/NEXT_ACTION.md`, Issue [#155](https://github.com/Eckommon/MUSICA/issues/155). Keep real third-party ABI support explicitly separate.
2. **[PROD-E2E-R0 #178](https://github.com/Eckommon/MUSICA/issues/178)**: one-song vertical-slice feature inventory, accepted arrangement/routing/automation, Preview/Accept, honest generated stereo WAV, archive/reopen reproducibility and explicit unsupported gates for missing steps. Prioritize production usability, not just isolated green unit tests.
3. **[PLUG-R4 #177](https://github.com/Eckommon/MUSICA/issues/177)**: assess official SDK and distribution rights, then prove **one real authorized third-party plugin binary** on one supported OS and format. A simulated processor is not proof of VST3, CLAP or AU compatibility.
4. Physical audio device/recording validation, deeper native editing, real AI provider/quality study, scalability, crash recovery, installer/signing/update and release readiness.

## Current nonclaims / 현재 지원이 입증되지 않은 범위

- **No verified commercial-general-purpose DAW completion**, user productivity study, or mastering-grade sound-quality verdict.
- **No native third-party VST3/CLAP/AU binary hosting, plugin scanning, sandbox security or realtime plugin PDC.**
- **No verified physical microphone/audio-interface hardware path, Windows device low-latency/dropout SLA or arbitrary routing graph compensation.**
- **No broad time-stretch/warp, sophisticated comping, universal channel/sample-rate conversion, full DAW state interchange, live OpenAI provider evidence, installer/signature/update or cloud collaboration claim.**

## Source of truth / 공식 기록

`docs/PRODUCT_THESIS.md` · `docs/COMMERCIAL_WORKSTATION_TARGET.md` · `memory/CURRENT_STATE.md` · `memory/NEXT_ACTION.md` · `evidence/` · exact GitHub PR/issue/CI artifacts.

**Exact accepted evidence and merged Git history > current state docs > Issue/PR descriptions > chat summaries.** Archived PR-specific acceptance documents keep their historical statuses; they are not today's active next action.
