# M5-R2 Backend Selection / M5-R2 백엔드 선정

**Decision ID / 결정 ID:** `M5R2-SEL-001`  
**Evidence date / 근거 기준일:** 2026-09-11  
**Status / 상태:** `ACCEPTED_FOR_IMPLEMENTATION — NOT YET VALIDATED` / `구현 대상으로 승인 — 아직 검증 완료 아님`

## 1. Decision / 결정

MUSICA SHALL implement **FluidSynth 2.6.0** as the first higher-fidelity local renderer target behind the validated M5-R1 renderer boundary.

MUSICA는 검증된 M5-R1 renderer boundary 뒤의 첫 고음질 local renderer 구현 대상으로 **FluidSynth 2.6.0**을 채택합니다.

For the R2 evidence profile, the preferred reference sound content is **FluidR3_GM 3.1**, provisioned outside normal Git and treated as replaceable renderer content rather than canonical musical authority.

R2 근거 프로파일의 우선 기준 음원은 **FluidR3_GM 3.1**이며, normal Git 외부에서 provision하고 renderer의 교체 가능한 content로만 취급합니다. 이 SoundFont는 canonical musical authority가 아닙니다.

This decision selects an **implementation target**, not a perceptual-quality winner. Perceptual superiority remains `UNKNOWN` until separately measured.

이 결정은 **구현 대상**을 선정하는 것이며 지각적 음질 우승자를 선언하는 것이 아닙니다. 별도 측정 전까지 perceptual superiority는 `UNKNOWN`입니다.

---

## 2. Selection gate / 선정 게이트

Candidates were scored 1–5 against the twelve criteria defined in `memory/NEXT_ACTION.md`. Weighted score is:

후보는 `memory/NEXT_ACTION.md`의 12개 기준에 대해 1–5점으로 평가했습니다. 가중 점수 계산식은 다음과 같습니다.

```text
weighted score = Σ(weight × candidate_score / 5)
maximum = 100
selection threshold = 80
```

A candidate also fails selection if it requires renderer output to become project authority, cannot be isolated behind the M5-R1 contract, or has an unresolved license boundary for the tested use.

후보가 renderer output에 project authority를 요구하거나 M5-R1 contract 뒤에 격리할 수 없거나 테스트 사용에 필요한 라이선스 경계가 해소되지 않으면 총점과 무관하게 탈락합니다.

### Weights / 가중치

| Criterion / 기준 | Weight |
|---|---:|
| Audio uplift / 음질·음색 capability 향상 | 15 |
| Music IR controllability / Music IR 제어 | 15 |
| Renderer contract fit / renderer 계약 적합성 | 10 |
| Reproducibility semantics / 재현성 | 10 |
| Windows practicality / Windows 실용성 | 10 |
| Offline/local operation / 로컬 동작 | 5 |
| Licensing / 라이선스 | 10 |
| Install burden / 설치 부담 | 5 |
| Automation surface / 자동화 인터페이스 | 10 |
| Artifact observability / artifact 관측성 | 5 |
| Repository hygiene / 레포 위생 | 2 |
| Future DAW path / 향후 DAW 확장성 | 3 |
| **Total** | **100** |

---

## 3. Candidate matrix / 후보 비교표

| Candidate / 후보 | Audio | IR control | Contract | Repro | Windows | Offline | License | Install | Automation | Observe | Hygiene | DAW | Weighted /100 | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **FluidSynth 2.6.0** | 4 | 5 | 5 | 4 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 3 | **91.8** | **SELECT** |
| sfizz 1.2.3 | 4 | 4 | 4 | 4 | 3 | 5 | 5 | 2 | 3 | 4 | 3 | 4 | **76.6** | HOLD |
| Surge XT 1.3.4 | 5 | 3 | 4 | 3 | 4 | 5 | 3 | 2 | 4 | 4 | 4 | 5 | **75.6** | HOLD |

Scores are architectural selection scores, not perceptual listening scores.

점수는 아키텍처·통합 선정 점수이며 청감 품질 점수가 아닙니다.

---

## 4. Evidence by candidate / 후보별 근거

### 4.1 FluidSynth 2.6.0 — SELECT

**Current support / 현재 지원**

- Official FluidSynth news and download pages list **2.6.0**, released **2026-08-11**, as the latest release at this decision date.
- Official downloads provide Windows binary releases; the FluidSynth wiki also documents Windows installation via Chocolatey.

**Automation and contract fit / 자동화 및 계약 적합성**

- FluidSynth exposes a command-line program and a reusable C API.
- The official user manual accepts SoundFont + Standard MIDI files directly and provides `--fast-render` for non-realtime file rendering.
- The file-renderer API explicitly exists for rendering MIDI to audio as fast as possible.
- Output file type/format and sample rate are explicit settings; the audio rendering API is stereo-capable.
- Standard MIDI program/bank mapping makes the path from MUSICA Music IR → MIDI → instrument program explicit and inspectable.

**License / 라이선스**

- FluidSynth source is **LGPL-2.1-or-later** according to the project source and repository documentation.
- Engine license and SoundFont content license remain separate. MUSICA SHALL record both independently.

**Why not 5/5 on audio or reproducibility? / audio·repro가 5점이 아닌 이유**

- Perceived quality depends materially on the selected SoundFont, instrument mapping and render settings.
- Byte-exact output across different FluidSynth builds, operating systems, libsndfile builds or floating-point paths is not assumed. R2 must measure the exact tested configuration.

### 4.2 sfizz 1.2.3 — HOLD

**Strengths / 강점**

- sfizz is an SFZ parser/synth C++ library and is licensed under **BSD-2-Clause**.
- Its library configuration exposes a default sample rate of 48 kHz and supports much higher rates.
- It is suitable for high-quality sample-based instruments and has plugin/library integration paths.

**Why HOLD / 보류 이유**

- The current project organization centers the core library and plugins; a turnkey Windows headless/offline renderer path is less direct than FluidSynth's CLI/file renderer.
- Useful output requires separately sourced SFZ instrument/sample libraries, creating additional content-provenance and installation burden.
- It is a strong future sampler adapter candidate after the first R2 path proves the renderer contract with lower integration risk.

### 4.3 Surge XT 1.3.4 — HOLD

**Strengths / 강점**

- Stable version **1.3.4** is available for Windows as standalone, CLAP and VST3.
- Since 1.3.0 Surge XT includes a pure command-line/headless mode; 1.3.4 expanded CLI and Python handling.
- OSC, MIDI Program Change, Python bindings and rich synthesis/effects make it a strong future expressive-synth and DAW-path candidate.
- The project FAQ explicitly permits commercial use of music/output created with Surge XT.

**Why HOLD / 보류 이유**

- Generic Music IR instrument roles do not map as directly to a standardized GM bank as FluidSynth; MUSICA would first need a governed patch/preset mapping layer.
- The distribution/build footprint is substantially heavier than FluidSynth and plugin/standalone integration introduces more moving parts.
- Surge XT itself is GPL-3.0-or-later; output rights are permissive, but binary redistribution obligations are materially heavier than the first adapter needs.
- Its DAW/plugin strength is valuable for later M5-R3 rather than necessary for the first R2 proof.

---

## 5. Sound-content decision / 음원 콘텐츠 결정

### Preferred R2 evidence content: FluidR3_GM 3.1

FluidR3_GM is selected as the **preferred R2 evidence SoundFont**, not as an immutable MUSICA dependency.

FluidR3_GM은 **R2 근거용 우선 SoundFont**이며 불변 MUSICA dependency가 아닙니다.

Reasons / 이유:

1. FluidSynth's own getting-started documentation names FluidR3_GM/GS as compatible SoundFonts.
2. Debian/Ubuntu continue to package `fluid-soundfont-gm` / `fluid-soundfont-gs` as version 3.1-family source packages.
3. The original FluidR3 README states that Frank Wen released Fluid under the **MIT license**.
4. It provides a broad General MIDI mapping suitable for comparing identical MUSICA MIDI output across the baseline and new backend.
5. The asset is large (~148 MB class) and SHALL NOT be committed to normal Git.

### GeneralUser GS 2.0.3 — reserve, not default evidence content

GeneralUser GS 2.0.3 is explicitly compatible with current FluidSynth and is much smaller (~30.7 MB class), with 261 presets and 13 drum kits. Its license allows private/commercial music creation and software-project use. However, the author's license text also records uncertainty about the historical origin of some contained samples. Therefore:

GeneralUser GS 2.0.3은 current FluidSynth와 호환되고 크기가 작아 유용하지만, 제작자 라이선스 문서에 일부 historical sample origin의 불확실성이 명시되어 있으므로:

- it MAY be evaluated later as optional user-provisioned content;
- it SHALL NOT be the canonical R2 bundled/default distribution asset;
- MUSICA SHALL NOT infer clean redistribution provenance merely from permissive output-use language.

---

## 6. R2 implementation profile / R2 구현 프로파일

The implementation branch SHALL target the following bounded profile:

구현 branch는 다음 제한 profile을 목표로 합니다.

```text
renderer_id: musica-fluidsynth-local
engine_target: FluidSynth 2.6.0
engine_classification: local / offline / SoundFont synth
input_authority: exact hash-bound canonical Music IR lowered to MIDI
sound_content: external path, separately hashed and licensed
preferred evidence soundfont: FluidR3_GM 3.1
output target: WAV
preferred validation format: 48 kHz, stereo
project authority: false
network required at render time: false
large third-party asset in Git: forbidden
perceptual superiority claim: UNKNOWN until separately evaluated
```

Exact bit depth/file-format support SHALL be discovered from the installed build and declared truthfully in `RendererCapability`; it must not be assumed from documentation alone.

정확한 bit depth/file-format 지원은 설치된 build에서 실제 탐지해 `RendererCapability`에 기록하며 문서만으로 추정하지 않습니다.

---

## 7. Reproducibility classification / 재현성 분류

Before implementation evidence exists, FluidSynth R2 reproducibility status is:

구현 근거 확보 전 FluidSynth R2 재현성 상태는 다음과 같습니다.

```text
same exact binary + exact SoundFont + exact MIDI + exact settings:
  EXPECTED_STABLE — NOT YET VERIFIED

cross-version / cross-OS byte identity:
  UNKNOWN — MUST NOT BE CLAIMED
```

R2 evidence SHALL run at least two independent renders and compare exact artifact hashes. `RendererResult` itself may report a capability claim, but cross-run evidence owns verification, consistent with M5-R1 semantics.

---

## 8. Failure conditions / 실패 조건

Selection SHALL be reopened or changed to `NO_SELECTION` if implementation discovers any of the following:

다음이 발견되면 선정을 재검토하거나 `NO_SELECTION`으로 전환합니다.

- exact tested FluidSynth version cannot be provisioned reproducibly;
- required SoundFont license/provenance cannot be documented for the test use;
- adapter requires canonical Blueprint/Music IR mutation;
- renderer cannot stay inside workspace/artifact constraints;
- output capability is not materially above the current reference path;
- Windows operation is materially more fragile than current evidence indicates;
- reproducibility or artifact provenance cannot be classified truthfully.

---

## 9. Next exact action / 다음 정확한 작업

After this selection record is accepted and merged:

이 선정 기록이 승인·병합되면:

```text
create implementation branch from selection-merge main
→ add M5-R2 acceptance/runtime contract
→ add FluidSynth runtime discovery + capability declaration
→ keep SoundFont as external provisioned asset
→ lower identical canonical Music IR to MIDI
→ render through musica-reference-local and musica-fluidsynth-local
→ 48 kHz stereo objective QA where actual build supports it
→ hash/provenance/reproducibility comparison
→ Windows practicality smoke evidence
→ negative/tamper/regression tests
→ durable evidence
→ exact-head PR CI
→ merge
→ state-only closure
```

No perceptual-quality superiority claim is authorized by this selection document.

이 선정 문서는 지각적 음질 우월성 주장을 승인하지 않습니다.

---

## 10. Evidence sources / 근거 출처

Primary/project sources consulted on 2026-09-11:

### FluidSynth
- https://www.fluidsynth.org/download/
- https://www.fluidsynth.org/news/2026/08/11/released-fluidsynth-2-6-0/
- https://www.fluidsynth.org/documentation/
- https://www.fluidsynth.org/wiki/UserManual/
- https://www.fluidsynth.org/api/FileRenderer.html
- https://www.fluidsynth.org/api/group__audio__rendering.html
- https://github.com/FluidSynth/fluidsynth

### FluidR3_GM
- https://www.fluidsynth.org/wiki/GettingStarted/
- https://sources.debian.org/src/fluid-soundfont/3.1-5.2/README
- https://packages.debian.org/stable/source/sound/fluid-soundfont

### sfizz
- https://github.com/sfztools/sfizz
- https://github.com/sfztools/sfizz/blob/develop/LICENSE
- https://github.com/sfztools/sfizz/releases

### Surge XT
- https://surge-synthesizer.github.io/downloads/
- https://surge-synthesizer.github.io/changelog/
- https://surge-synthesizer.github.io/manual-xt/
- https://surge-synthesizer.github.io/faq/
- https://github.com/surge-synthesizer/surge

### GeneralUser GS
- https://schristiancollins.com/generaluser.php
- https://github.com/mrbumpy409/GeneralUser-GS

**Repository evidence remains authoritative over conversational memory or model inference. / 레포 근거는 대화·모델 추론보다 우선합니다.**
