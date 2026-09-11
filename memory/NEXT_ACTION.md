# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**M5-R2 — FIRST HIGHER-FIDELITY LOCAL RENDERER ADAPTER v0 / M5-R2 — 첫 고음질 로컬 렌더러 어댑터 v0**

M5-R1 is validated. MUSICA now has a renderer-neutral contract, exact Music IR binding, artifact integrity checks, objective PCM WAV QA, and a deterministic reference adapter. The next bounded problem is to select and integrate the first meaningfully higher-fidelity local renderer **without weakening the M5-R1 authority boundary**.

M5-R1은 검증 완료되었습니다. MUSICA는 renderer-neutral 계약, 정확한 Music IR 바인딩, artifact 무결성 검증, 객관적 PCM WAV QA, 결정론 reference adapter를 갖췄습니다. 다음 제한 문제는 **M5-R1 권한 경계를 약화하지 않으면서** 실제로 의미 있는 음질 향상을 제공하는 첫 local renderer를 선정·통합하는 것입니다.

## First action is selection, not installation / 첫 작업은 설치가 아니라 선정

M5-R2 SHALL NOT pre-commit to FluidSynth, a SoundFont, a standalone synth, a sampler, a DAW, or a generative-audio service merely because it is familiar or easy to install.

M5-R2는 익숙하거나 설치가 쉽다는 이유만으로 FluidSynth, 특정 SoundFont, standalone synth, sampler, DAW, generative-audio service를 사전 채택하지 않습니다.

The first R2 deliverable is an evidence-backed backend selection decision.

첫 R2 산출물은 근거 기반 backend 선정 결정입니다.

## Selection criteria / 선정 기준

Candidate backends SHALL be compared on at least:

1. **Audio uplift / 음질 향상** — clearly better than the current bounded reference synth for MUSICA use cases.
2. **Music IR controllability / Music IR 제어 가능성** — deterministic or explicitly classified mapping from notes, timing, velocity, program/timbre, automation or equivalent controls.
3. **Renderer contract fit / Renderer 계약 적합성** — can be isolated behind M5-R1 Request/Capability/Result/QA contracts.
4. **Reproducibility semantics / 재현성** — byte-exact, stable-parameter, best-effort, or none must be stated truthfully and tested where possible.
5. **Windows practicality / Windows 실용성** — suitable for the user's primary Windows environment without fragile manual orchestration.
6. **Offline/local operation / 로컬 동작** — preferred for the first adapter; network dependence must be explicit if unavoidable.
7. **Licensing / 라이선스** — engine, preset, SoundFont/sample content, redistribution and commercial-use rights must be separable and documented.
8. **Install burden / 설치 부담** — avoid large or opaque toolchains where the audio uplift does not justify them.
9. **Automation surface / 자동화 인터페이스** — CLI, API, process protocol, MIDI/audio I/O or another stable adapter surface.
10. **Artifact observability / artifact 관측 가능성** — output can be hashed, QA-measured, logged and reproduced or classified accurately.
11. **Repository hygiene / 레포 위생** — no large model weights, SoundFonts or sample libraries committed to normal Git.
12. **Future DAW path / 향후 DAW 확장성** — useful stepping stone toward M5-R3 without coupling core authority to a DAW.

## Candidate classes / 후보 범주

At minimum evaluate representative options from:

- SoundFont/FluidSynth-class renderers;
- locally automatable software synths with a stable non-GUI control surface;
- sampler/instrument engines suitable for headless or scripted rendering;
- other local render paths that can consume MIDI/Music IR-derived control without taking project authority.

Candidate names are **PROPOSED candidates, not accepted dependencies**, until source/licensing/current-support evidence is collected.

후보 이름은 source·license·현재 지원 상태 근거를 확보하기 전까지 **PROPOSED 후보일 뿐 승인 dependency가 아닙니다.**

## R2 architecture target / R2 아키텍처 목표

```text
Accepted Blueprint Revision
        ↓
Canonical Music IR
        ↓ exact SHA-256
RendererRequest v0
        ↓
Renderer Registry
  ├─ musica-reference-local       [validated baseline]
  └─ <selected-hifi-local-v0>     [new R2 adapter]
        ↓
RendererResult v0
  + AudioQualityReport v0
  + backend provenance/version
  + exact artifact hashes
        ↓
Comparative evidence
```

The new backend is replaceable infrastructure. It cannot mutate Blueprint, Music IR, branches, revisions, locks, or accepted project authority.

새 backend는 교체 가능한 infrastructure이며 Blueprint, Music IR, branch, revision, lock, accepted project 권한을 변경할 수 없습니다.

## Required R2 proof / R2 필수 증명

M5-R2 SHALL prove at least:

- selected backend identity/version and source provenance;
- license/redistribution/commercial-use boundary for the engine and required sound content;
- installation/runtime requirements without committing large binary assets to Git;
- a machine-valid RendererCapability declaration;
- exact Music IR request binding;
- successful MIDI/audio rendering through the existing registry boundary;
- objective QA at an appropriate production-oriented format, preferably 44.1 kHz or 48 kHz and stereo if the backend genuinely supports it;
- renderer output remains artifact-only authority;
- tamper/path/capability negative behavior remains fail-closed;
- reproducibility classification is evidenced rather than inferred;
- comparison against `musica-reference-local` using identical canonical Music IR;
- M0→M5-R1 regression and M4-R3 real-browser regression remain green.

## Quality comparison rule / 품질 비교 규칙

R2 must distinguish three different claims:

1. **Signal validity** — objective container/signal QA already covered by M5-R1.
2. **Renderer capability uplift** — richer/stereo/higher-rate/timbre-capable output that can be objectively demonstrated.
3. **Perceptual musical quality** — requires separate comparative evaluation; R2 must not silently equate better format specifications with better perceived music.

R2는 더 높은 sample rate나 stereo라는 이유만으로 지각적 음악 품질 향상을 자동 주장해서는 안 됩니다.

If perceptual comparison is not robustly measured in R2, mark it `UNKNOWN` and leave it for M5-R4.

## Recommended development sequence / 권장 개발 순서

```text
repo/state preflight
→ candidate source + license research
→ scored backend selection matrix
→ selection decision record
→ adapter capability contract
→ isolated installation/runtime adapter
→ identical-IR baseline vs high-fidelity render
→ objective QA + provenance
→ negative/tamper/reproducibility tests
→ durable evidence
→ PR exact-head CI
→ merge
→ state-only closure
```

## M5-R2 acceptance gate / M5-R2 수용 게이트

M5-R2 may be promoted only if:

1. backend selection is evidence-backed rather than assumed;
2. licensing and sound-content provenance are documented sufficiently for the tested use;
3. the backend is reachable through the M5-R1 renderer boundary;
4. exact Music IR binding and artifact integrity remain enforced;
5. the new renderer produces valid audio and its capability uplift over the reference renderer is demonstrated;
6. reproducibility is classified and tested honestly;
7. no renderer gains canonical project authority;
8. large third-party binaries/content are kept outside normal Git;
9. M0→M5-R1 + M4-R3 regression remains green;
10. dedicated durable evidence is generated;
11. evidence-bearing exact PR head passes required CI and is merged;
12. state-only closure promotes R2.

## Non-goals / 비목표

M5-R2 does not require or claim:

- a complete DAW integration;
- VST/AU hosting inside MUSICA;
- professional mastering;
- human listener superiority evidence unless separately executed;
- proprietary foundation audio-model training;
- cloud rendering;
- replacement of the validated reference renderer;
- committing third-party SoundFonts/sample packs/model weights to the repository.

## Planned follow-on / 후속 예정

After M5-R2, the intended next bounded phase is **M5-R3 — DAW / interchange interoperability**, followed by **M5-R4 — Comparative music/audio quality evaluation**. This ordering may change only through repository evidence and an explicit decision record.

M5-R2 이후 예정된 제한 단계는 **M5-R3 — DAW / interchange interoperability**, 그 다음은 **M5-R4 — Comparative music/audio quality evaluation**입니다. 순서 변경은 레포 근거와 명시적 decision record를 통해서만 수행합니다.

## Development discipline / 개발 규율

```text
Issue
→ branch from M5-R1 closure main
→ evidence-backed backend selection
→ bounded implementation
→ tests + evidence
→ PR
→ exact-head CI
→ merge
→ state-only closure
```

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
