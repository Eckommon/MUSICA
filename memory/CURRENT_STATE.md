# Current State / 현재 상태

## Project phase / 프로젝트 단계

**M5-R2 — FIRST HIGHER-FIDELITY LOCAL RENDERER ADAPTER v0: VALIDATED — BOUNDED / M5-R2 — 첫 고음질 로컬 렌더러 어댑터 v0: 제한 범위 검증 완료**

M0→M5-R2 are validated within their explicitly bounded claims. MUSICA now has a replaceable real local renderer path in addition to its deterministic reference renderer: exact accepted Music IR can be rendered through FluidSynth 2.6.0 with an exact-hash-bound external FluidR3_GM 3.1 SoundFont while canonical project authority remains outside the renderer.

M0→M5-R2는 각 명시적 제한 주장 범위에서 검증 완료되었습니다. MUSICA는 결정론적 reference renderer 외에 교체 가능한 실제 local renderer 경로를 갖췄습니다. 승인된 exact Music IR을 FluidSynth 2.6.0 + exact-hash-bound 외부 FluidR3_GM 3.1 SoundFont로 렌더할 수 있으며 canonical project authority는 renderer 외부에 유지됩니다.

## Canonical core proposition / 공식 핵심 명제

> **MUSICA lets anyone create music by intent, while allowing every musical decision to become inspectable, lockable, editable, reproducible, and programmable.**
>
> **MUSICA는 누구나 의도로 음악을 만들 수 있게 하되, 모든 음악적 결정을 검사하고, 잠그고, 편집하고, 재현하고, 프로그래밍할 수 있게 하는 시스템이다.**

Product promise / 제품 약속:

> **Easy enough to direct in natural language, precise enough to edit as a professional music system.**
>
> **자연어로 지시할 만큼 쉽고, 전문 음악 시스템처럼 세밀하게 편집할 만큼 정밀해야 한다.**

## Canonical milestone ledger / 공식 마일스톤 원장

| Milestone | Status | Durable evidence / 영속 근거 |
|---|---|---|
| M0 Controllable Core | **VALIDATED** | `evidence/M0_R2_VALIDATION.md` |
| M1 Creative Core | **VALIDATED** | `evidence/M1_VALIDATION.md` |
| M2 Project & Version Engine | **VALIDATED** | `evidence/M2_VALIDATION.md` |
| M3-R1 Director authority boundary | **VALIDATED** | `evidence/M3_R1_VALIDATION.md` |
| M3-R2 OpenAI adapter contract | **VALIDATED — ADAPTER_CONTRACT_EVIDENCE** | `evidence/M3_R2_VALIDATION.md` |
| M3 AI Music Director Provider Layer | **VALIDATED — BOUNDED** | R1 + R2 evidence |
| M4-R1 Studio Application Service | **VALIDATED** | `evidence/M4_R1_VALIDATION.md` |
| M4-R2 Browser Studio UI | **VALIDATED** | `evidence/M4_R2_VALIDATION.md` |
| M4-R3 Usable MVP / real-browser E2E | **VALIDATED** | `evidence/M4_R3_VALIDATION.md` |
| M5-R1 Renderer Adapter Contract + Audio QA Baseline | **VALIDATED** | `evidence/M5_R1_VALIDATION.md` |
| M5-R2 First higher-fidelity local renderer | **VALIDATED — BOUNDED** | `evidence/M5_R2_VALIDATION.md` |
| Live OpenAI provider execution | **NOT VALIDATED** | separate `LIVE_PROVIDER_EVIDENCE` required |
| M5-R3 DAW / interchange interoperability | **NOT IMPLEMENTED** | next bounded mission |
| M5-R4 Comparative music/audio quality evaluation | **NOT IMPLEMENTED** | later phase |

## M5-R2 final evidence / M5-R2 최종 근거

### Selection / 선정

- implementation Issue: `#38` — **CLOSED / completed**
- selection PR: `#39` — **MERGED**
- selection exact head: `c841ec3c3ca46f38bb6494bcb14f89ae5d630a9f`
- selection CI: `34572291199` — Python 3.11 / 3.12 + Chromium **SUCCESS**
- selection merge: `72afaf90bd7d28861b4adb3d9117e37ff7e12b1c`
- selected engine: `FluidSynth 2.6.0`
- selected evidence content: external `FluidR3_GM 3.1`
- architectural selection score: `91.8 / 100`
- selection artifact: `docs/M5_R2_BACKEND_SELECTION.md`

### Implementation / 구현

- implementation PR: `#40` — **MERGED**
- exact evidence-bearing head: `041ce64846f5ae4998122d24c8c0f23f158fa884`
- exact-head CI: `34575439880`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- exact-head pytest: **100 passed**
- M0→M5-R1 canonical evidence chain: **SUCCESS**
- M4-R3 Playwright Chromium regression: **SUCCESS**
- Windows real FluidSynth evidence: **SUCCESS**
- final exact-head artifact: `musica-m5-r2-fluidsynth`
- artifact ID: `10189445028`
- GitHub artifact digest: `sha256:4574660bce161ef7574751a75e142a84194bd8a4832922ec22286539622b2f73`
- independently downloaded ZIP digest: **MATCH**
- implementation merge: `713c3ab854f15ee8f5e0155d05d51aae95a4987f`
- durable evidence: `evidence/M5_R2_VALIDATION.md`

## Exact M5-R2 renderer proof / 정확한 M5-R2 renderer 증명

Canonical Music IR:

- SHA-256: `f28fd7f9268f1ff043f90988bb33800d95fce494cd0cc68c4265a6d8e0abc83d`
- reference and FluidSynth requests bound to the same exact Music IR: **true**
- input Music IR unchanged after rendering: **true**
- renderer project authority: **false**

Runtime/content provenance:

- renderer ID: `musica-fluidsynth-local`
- FluidSynth observed version: `2.6.0`
- official Windows x64 source archive SHA-256: `817262deacaa748edb3af6731dffe1766b00146790becfccc949a9f701e76681`
- executed `fluidsynth.exe` SHA-256: `08c72384a47f67b0c5be9ee8c88b1f0b6afe39a8217ed2adb83a88b41c051632`
- external SoundFont logical ID: `FluidR3_GM-3.1`
- external SoundFont SHA-256: `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`
- SoundFont normal-Git inclusion: **false**
- bounded render-time network requirement: **false**

Final audio evidence:

- sample rate: **48,000 Hz**
- channels: **2 stereo**
- sample width: **16-bit PCM**
- final frame count: **960,000**
- final duration: **20.0 s**
- AudioQualityReport: **PASS**
- hard clipping samples: **0**
- independent A/B MIDI SHA-256: `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- independent A/B final WAV SHA-256: `e054ad9cb7d938f50f75d222c1522e71cc7a7f163e8ea7bf3f8dceec628bcfa3`
- byte identity observed for the exact Windows runtime/content/config: **true**
- declared reproducibility remains `stable_parameters`; individual result `verified=false`

### Duration normalization / 길이 정규화

The first real strict run correctly failed because FluidSynth produced a `22.549333333 s` release/effect tail for an explicit `20.0 s` MUSICA request. MUSICA did not weaken QA or hide the discrepancy.

첫 실제 strict run은 20초 MUSICA 요청에 FluidSynth가 `22.549333333초` release/effect tail을 생성해 정상적으로 실패했습니다. MUSICA는 QA를 완화하거나 차이를 숨기지 않았습니다.

Validated policy: `trim_tail_to_requested_duration_v0`

- raw engine SHA-256/duration/frame count recorded in provenance;
- raw output shorter than target → **FAIL CLOSED**;
- raw output longer than target → exact excess frames only are trimmed;
- padding/invented audio: **forbidden**;
- final normalized artifact is QA-measured again;
- unmanaged raw WAV is removed after successful normalization;
- final exact-head evidence ZIP contains `render.engine.wav`: **0 files**.

## Validated capability stack / 검증된 기능 스택

### Music authority core / 음악 권한 코어
- typed Intent / Blueprint / Semantic Control / Music IR contracts;
- deterministic composition/lowering paths;
- six bounded semantic axes;
- HARD-lock/constraint fail-closed validation;
- immutable accepted revisions/branches and audit chain.

### AI Director / AI 디렉터
- provider-neutral typed proposal boundary;
- explicit user intent outranks provider inference;
- providers cannot directly mutate accepted Blueprint/Project state;
- OpenAI adapter contract is validated offline, but **live OpenAI execution remains NOT VALIDATED**.

### Studio / Studio
- local-first Browser Studio with `Direct → Shape → Inspect → Code`;
- non-canonical audible Preview separated from accepted state;
- explicit Accept/Discard;
- visible HARD locks, structured diff, branch/history/export;
- real Chromium create → preview → accept → branch/history/export → Code → restart/reopen validated.

### Renderer / Renderer
- renderer-neutral Request/Capability/Result/QA boundary;
- exact Music IR + external resource hash binding;
- reference deterministic renderer retained;
- real external-process FluidSynth adapter validated on Windows CI;
- 48 kHz stereo 16-bit PCM capability proven;
- executable/content provenance and artifact hashes recorded;
- workspace confinement and tamper verification;
- renderer has no accepted-project mutation authority;
- third-party engine/content remains external to normal Git.

## Canonical authority rule / 공식 권한 규칙

```text
User
 ↓
Browser Studio / API
 ↓
M4 application service
 ↓
M3 proposal boundary or validated semantic command
 ↓
M1/M0 trusted core + HARD locks
 ↓
PREVIEW — non-canonical
 ↓ explicit user Accept only
M2 Project Engine
 ↓
Accepted Blueprint Revision
 ↓ trusted lowering
Canonical Music IR
 ↓ exact hash-bound RendererRequest
M5 Renderer Registry
 ├─ musica-reference-local
 └─ musica-fluidsynth-local
        ↓
Artifacts + QA + provenance only
```

**Browser, AI provider, preview, renderer process, SoundFont and renderer artifacts never outrank the accepted `.musica` Project Bundle or canonical Music IR derived from its accepted revision.**

**Browser, AI provider, preview, renderer process, SoundFont, renderer artifact는 승인된 `.musica` Project Bundle 또는 그 승인 revision에서 파생된 canonical Music IR보다 우선할 수 없습니다.**

## Current claim boundaries / 현재 주장 경계

The repository does **not** yet validate or imply:

- successful live OpenAI API execution;
- human-subject usability-study evidence;
- perceptual superiority of FluidSynth/FluidR3 over the reference renderer;
- professional/mastering audio quality;
- byte-exact identity across all FluidSynth versions, operating systems or SoundFonts;
- bundled redistribution of FluidR3_GM as MUSICA product content;
- VST/AU hosting;
- professional DAW automation/interchange round-trip;
- waveform/piano-roll/note-level professional editing UI;
- cloud collaboration/multi-user security;
- desktop installer/signing;
- remote HTTP serving.

특히 **48 kHz stereo capability 향상은 검증되었지만 청감상 더 좋은 음악이라는 주장은 아직 UNKNOWN**입니다. 해당 비교는 별도 M5-R4 범위입니다.

## Next phase / 다음 단계

The exact next bounded mission is **M5-R3 — DAW / Interchange Interoperability v0**.

정확한 다음 제한 mission은 **M5-R3 — DAW / Interchange Interoperability v0 / DAW·교환 상호운용성 v0**입니다.

M5-R3 shall begin with evidence-backed interchange-target selection and round-trip authority design rather than coupling MUSICA Core directly to a specific DAW.

M5-R3는 특정 DAW에 MUSICA Core를 직접 결합하지 않고, 근거 기반 interchange target 선정과 round-trip 권한 설계부터 시작합니다.

## Resume authority / 재개 권위

Before substantive work inspect in order / 실질 작업 전 순서대로 확인:

1. `governance/SOURCE_OF_TRUTH.md`
2. `docs/PRODUCT_THESIS.md`
3. normative design package/specs
4. prior milestone durable evidence
5. `docs/M5_R1_ACCEPTANCE.md`
6. `docs/M5_R2_BACKEND_SELECTION.md`
7. `docs/M5_R2_ACCEPTANCE.md`
8. `docs/M5_R2_RUNTIME.md`
9. `evidence/M5_R2_VALIDATION.md`
10. this file / 본 파일
11. `memory/NEXT_ACTION.md`
12. relevant Issue/PR/CI evidence / 관련 Issue·PR·CI 근거

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
