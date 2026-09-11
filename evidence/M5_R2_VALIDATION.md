# M5-R2 Validation Evidence / M5-R2 검증 근거

## Verdict / 판정

**TECHNICAL EVIDENCE PASS — CANONICAL PROMOTION PENDING / 기술 근거 PASS — 공식 상태 승격 대기**

The bounded M5-R2 implementation has real Windows evidence for FluidSynth 2.6.0 + externally provisioned FluidR3_GM 3.1 behind the M5-R1 renderer boundary. Canonical milestone status SHALL remain unpromoted until this evidence-bearing exact PR head passes all required CI gates, PR #40 is merged, and a state-only closure is merged.

제한된 M5-R2 구현은 M5-R1 renderer boundary 뒤에서 실제 Windows FluidSynth 2.6.0 + 외부 provision FluidR3_GM 3.1 실행 근거를 확보했습니다. 그러나 이 evidence-bearing exact PR head의 전체 CI, PR #40 merge, state-only closure가 끝나기 전까지 공식 milestone 상태는 승격하지 않습니다.

---

## 1. Scope / 범위

M5-R2 proves the first replaceable higher-capability local renderer adapter. It does **not** prove professional mastering quality or perceptual musical superiority.

M5-R2는 첫 교체 가능한 higher-capability local renderer adapter를 증명합니다. **전문 mastering 품질 또는 지각적 음악 우월성은 증명하지 않습니다.**

Validated bounded path / 검증 제한 경로:

```text
Accepted Blueprint Revision
        ↓
Canonical Music IR
        ↓ exact SHA-256
RendererRequest v0
        ↓
Renderer Registry
        ↓
musica-fluidsynth-local
        ↓
FluidSynth 2.6.0 + exact-hash-bound FluidR3_GM 3.1
        ↓
raw engine WAV
        ↓ provenance hash/duration
trim_tail_to_requested_duration_v0
        ↓
48 kHz stereo 16-bit final WAV
        ↓
AudioQualityReport + RendererResult + provenance
```

Renderer output remains artifact/evidence only. It never receives Blueprint, revision, branch, lock, or canonical Music IR mutation authority.

Renderer 출력은 artifact/evidence일 뿐이며 Blueprint, revision, branch, lock, canonical Music IR 변경 권한을 갖지 않습니다.

---

## 2. Selection evidence / 선정 근거

- implementation Issue: `#38`
- selection decision: `docs/M5_R2_BACKEND_SELECTION.md`
- selection decision ID: `M5R2-SEL-001`
- selection PR: `#39` — **MERGED**
- selection exact head: `c841ec3c3ca46f38bb6494bcb14f89ae5d630a9f`
- selection CI: `34572291199` — Python 3.11 / Python 3.12 / Chromium **SUCCESS**
- selection merge: `72afaf90bd7d28861b4adb3d9117e37ff7e12b1c`
- selected engine: **FluidSynth 2.6.0**
- selected R2 evidence content: **FluidR3_GM 3.1**, external and replaceable
- architectural selection score: **91.8 / 100**
- perceptual-quality winner claim: **NOT MADE**

The engine and sound-content licenses are separate boundaries:

- FluidSynth engine: `LGPL-2.1-or-later`
- FluidR3_GM evidence content: `MIT` as documented by the selected source/provenance record

엔진 라이선스와 SoundFont 콘텐츠 라이선스는 별도 경계로 관리됩니다.

---

## 3. Implementation evidence / 구현 근거

- implementation PR: `#40`
- validation-basis branch head: `a80be8c67c7d36515c0d93bbfc7215b4a20199e8`
- validation-basis CI run: `34575154683`
- Python 3.11: **SUCCESS**
- Python 3.12: **SUCCESS**
- Python 3.12 pytest: **100 passed in 55.35s**
- M0→M5-R1 canonical evidence generation/upload: **SUCCESS**
- M4-R3 Playwright Chromium regression: **SUCCESS**
- Windows M5-R2 real FluidSynth job: **SUCCESS**

The implementation adds:

- backward-compatible external-resource SHA-256 binding in `RendererRequest v0`;
- provenance-manifest binding in `RendererResult v0`;
- exact executable discovery/version/hash validation;
- exact SoundFont logical-ID/hash validation;
- shell-free external-process execution;
- 48 kHz stereo s16 bounded FluidSynth capability;
- workspace-derived artifact paths;
- artifact/provenance hash verification;
- deterministic excess-tail duration normalization;
- explicit no-padding underrun failure;
- unit negative coverage for version/resource/capability/path/tamper failures.

---

## 4. Exact real runtime/content provenance / 실제 runtime·content provenance

### FluidSynth

- target/observed version: `2.6.0`
- official Windows x64 archive:
  `fluidsynth-v2.6.0-win10-x64-cpp11.zip`
- provision source:
  `https://github.com/FluidSynth/fluidsynth/releases/download/v2.6.0/fluidsynth-v2.6.0-win10-x64-cpp11.zip`
- source archive SHA-256:
  `817262deacaa748edb3af6731dffe1766b00146790becfccc949a9f701e76681`
- executed binary SHA-256:
  `08c72384a47f67b0c5be9ee8c88b1f0b6afe39a8217ed2adb83a88b41c051632`

### FluidR3_GM

- logical resource ID: `FluidR3_GM-3.1`
- provision source:
  `https://deb.debian.org/debian/pool/main/f/fluid-soundfont/fluid-soundfont_3.1.orig.tar.gz`
- source archive SHA-256:
  `2621acaa1c78e4abdb24bdd163230cc577e61276936d6aa6e3180582142f0343`
- extracted `FluidR3_GM.sf2` SHA-256:
  `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`
- extracted size: `148,398,306 bytes`
- evidence content stored in normal Git: **false**
- evidence content stored in final GitHub evidence artifact: **false**

Provisioning used network access. The bounded rendering process after provisioning declares and operates as local/offline renderer execution.

Provisioning에는 network를 사용했지만 준비 완료 후 제한된 render process 자체는 local/offline 동작입니다.

---

## 5. Exact Music IR binding / 정확한 Music IR 결합

Canonical test Music IR SHA-256:

`f28fd7f9268f1ff043f90988bb33800d95fce494cd0cc68c4265a6d8e0abc83d`

Proof / 증명:

- reference and FluidSynth requests bound to the same exact Music IR: **true**
- input Music IR unchanged after all renders: **true**
- SoundFont exact SHA-256 bound in request and runtime provenance: **true**
- renderer project authority: **false**

---

## 6. Reference vs FluidSynth capability evidence / reference 대비 capability 근거

Identical canonical Music IR was rendered by both adapters.

동일 canonical Music IR을 두 adapter로 render했습니다.

| Property / 항목 | `musica-reference-local` | `musica-fluidsynth-local` |
|---|---:|---:|
| Sample rate | 48,000 Hz | **48,000 Hz** |
| Channels | 1 mono | **2 stereo** |
| Sample width | 16-bit PCM | **16-bit PCM** |
| QA | PASS | **PASS** |
| External SoundFont | no | **exact hash-bound** |
| Final requested duration | 20.0 s | **20.0 s** |

Bounded capability uplift proven / 제한 capability 향상 증명:

- stereo output: **true**
- 48 kHz final output: **true**
- external replaceable SoundFont exact-hash binding: **true**

This is a renderer-capability uplift, **not** evidence that the music is perceptually better.

이는 renderer capability 향상이며 음악이 청감상 더 우수하다는 증거가 아닙니다.

`perceptual_quality_superiority = UNKNOWN`

---

## 7. Duration failure → bounded correction / 길이 실패 → 제한 보정

### Initial strict real-render failure

Initial Windows integration run `34573629125` correctly failed the existing AudioQualityReport duration rule.

첫 Windows integration run `34573629125`는 기존 AudioQualityReport duration rule에 따라 정상적으로 실패했습니다.

Observed raw FluidSynth output:

- requested: `20.0 s`
- raw actual: `22.549333333 s`
- sample rate: `48,000 Hz`
- channels: `2`
- sample width: `16-bit PCM`
- non-zero samples: `2,008,207`
- peak normalized: approximately `0.084688864`
- hard clipping samples: `0`
- normalized DC offset: approximately `-0.000459603`

The output had valid signal/container properties; only strict duration failed because the fast renderer retained release/effect tail.

출력의 signal/container는 정상이었고 fast renderer의 release/effect tail 때문에 strict duration만 실패했습니다.

### Correction policy

MUSICA did **not** relax the duration tolerance and did **not** disable effects merely to pass the test.

MUSICA는 duration tolerance를 완화하지 않았으며 테스트 통과만을 위해 effect를 비활성화하지 않았습니다.

Instead:

1. render raw engine WAV;
2. record raw SHA-256/size/frame count/duration;
3. fail closed if raw output is shorter than requested;
4. if raw output exceeds target, trim only exact excess frames;
5. never pad/invent missing audio;
6. QA the final normalized WAV;
7. remove the unmanaged raw WAV after successful normalization while preserving its measurements in provenance.

Policy: `trim_tail_to_requested_duration_v0`

Clean validation run observed:

- raw duration: `22.549333333333333 s`
- raw frame count: `1,082,368`
- raw SHA-256:
  `66ce1b61734037a33d74840540bc85d4e894614142d8a91193507b04914be5fb`
- target frames: `960,000`
- trimmed frames: `122,368`
- final duration: **`20.0 s`**
- padding applied: **false**
- normalization identical between independent A/B runs: **true**
- unmanaged `render.engine.wav` present in clean evidence ZIP: **false**

---

## 8. Reproducibility semantics / 재현성 의미

For this exact Windows runtime/content/configuration, independent FluidSynth run A/B produced identical tracked MIDI/WAV hashes:

- MIDI SHA-256:
  `b7b5f5cbeff58888132032f13880d2bc5aad701e906c37daa077c6e8a834248f`
- final WAV SHA-256:
  `e054ad9cb7d938f50f75d222c1522e71cc7a7f163e8ea7bf3f8dceec628bcfa3`
- observed A/B byte identity: **true**

However the adapter capability remains conservatively declared:

```text
reproducibility = stable_parameters
individual RendererResult verified = false
```

Byte identity observed in one exact environment does not authorize a cross-version/cross-OS byte-exact guarantee.

한 exact environment에서의 byte identity 관측은 cross-version/cross-OS byte-exact 보장을 승인하지 않습니다.

---

## 9. Clean GitHub evidence artifact / 정리된 GitHub 근거 artifact

Validation-basis run `34575154683` produced:

- artifact name: `musica-m5-r2-fluidsynth`
- artifact ID: `10189325341`
- GitHub artifact digest:
  `sha256:c9a69d7c5f36779d2e163c37c57aad9e1597127f54529e742ea266d4a6f61847`
- independently downloaded ZIP SHA-256:
  `c9a69d7c5f36779d2e163c37c57aad9e1597127f54529e742ea266d4a6f61847`
- digest match: **true**
- ZIP entries: `22`
- unmanaged raw engine WAV entries: **0**
- manifest tracked artifacts excluding self-manifest: `21`

The final FluidSynth run-A WAV was independently opened from the downloaded artifact:

- sample rate: `48,000 Hz`
- channels: `2`
- sample width: `2 bytes / 16-bit`
- frame count: `960,000`
- duration: **`20.0 s`**
- byte size: `3,840,044`

---

## 10. Security / negative behavior / 보안·부정 경로

Unit/regression evidence covers fail-closed behavior for at least:

- Music IR hash mismatch;
- unknown renderer;
- unsupported renderer capability;
- SoundFont ID/hash mismatch;
- missing/invalid FluidSynth executable;
- exact-version mismatch;
- subprocess failure/timeout boundary;
- path traversal / caller-output-path avoidance;
- provenance tamper;
- artifact hash/size tamper;
- raw renderer underrun (no padding);
- existing corrupt/silent/clipped/duration-invalid audio QA.

Renderer output and external resources cannot promote accepted project state.

Renderer output 및 외부 resource는 accepted project state를 승격할 수 없습니다.

---

## 11. Promotion boundary / 승격 경계

Technical evidence above is **PASS** for the bounded implementation, but the canonical milestone SHALL become `VALIDATED` only after:

1. this durable evidence is present on the PR head;
2. that exact evidence-bearing head passes Python 3.11, Python 3.12, prior M0→M5-R1 evidence, M4-R3 Chromium, and Windows M5-R2 real-render gates;
3. PR #40 is merged with exact-head protection;
4. Issue #38 is closed completed;
5. a separate state-only closure updates canonical `CURRENT_STATE` / `NEXT_ACTION` and itself passes required CI before merge.

이 기술 근거는 제한 구현에 대해 PASS이지만 위 절차 완료 전 공식 milestone은 `VALIDATED`로 승격하지 않습니다.

---

## 12. Explicit non-claims / 명시적 비주장

M5-R2 does **not** validate:

- perceptual superiority over the reference renderer;
- human listener preference;
- professional mastering quality;
- every FluidSynth build, operating system or SoundFont;
- byte-exact identity across versions/platforms;
- VST/AU hosting or DAW interoperability;
- live OpenAI execution;
- bundled redistribution of FluidR3_GM inside MUSICA;
- cloud rendering.

Those claims require separate bounded evidence. Perceptual comparison remains planned for M5-R4.

위 주장은 별도 제한 근거가 필요하며 청감 비교는 M5-R4 범위로 유지합니다.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
