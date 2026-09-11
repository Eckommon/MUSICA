# M5-R2 Acceptance / M5-R2 수용 계약

## Mission / 미션

M5-R2 selects and integrates the first evidence-backed higher-fidelity local renderer behind the validated M5-R1 boundary. The selected implementation target is **FluidSynth 2.6.0**, with **FluidR3_GM 3.1** as the preferred externally provisioned evidence SoundFont, subject to the selection record and the fail/reopen conditions in `docs/M5_R2_BACKEND_SELECTION.md`.

M5-R2는 검증된 M5-R1 boundary 뒤에 첫 근거 기반 고음질 local renderer를 선정·통합합니다. 선정된 구현 대상은 **FluidSynth 2.6.0**이며, **FluidR3_GM 3.1**을 외부 provision 방식의 우선 evidence SoundFont로 사용합니다. 단, `docs/M5_R2_BACKEND_SELECTION.md`의 선정 근거와 fail/reopen 조건을 충족해야 합니다.

**Selection is not validation. / 선정은 검증 완료를 의미하지 않습니다.**

The milestone remains `NOT VALIDATED` until every required R2 proof below is backed by repository tests and durable evidence.

아래 R2 필수 증명이 repository test와 durable evidence로 확인되기 전까지 milestone은 `NOT VALIDATED`입니다.

---

## Authority model / 권한 모델

```text
Accepted Blueprint Revision
  ↓ trusted lowering
Canonical Music IR
  ↓ exact SHA-256 binding
RendererRequest v0
  ↓ registry + capability validation
Renderer Adapter
  ├─ musica-reference-local        [M5-R1 baseline]
  └─ musica-fluidsynth-local       [M5-R2 candidate]
       ↓ external engine + external SoundFont
Renderer artifacts
  ↓ objective QA + exact hashes + provenance
RendererResult v0
```

The FluidSynth executable, SoundFont, renderer configuration, MIDI and generated audio are renderer infrastructure/artifacts. None of them may replace or mutate accepted Blueprint, canonical Music IR, revisions, branches, locks, or project authority.

FluidSynth executable, SoundFont, renderer configuration, MIDI 및 생성 audio는 renderer infrastructure/artifact일 뿐입니다. 이들은 승인 Blueprint, canonical Music IR, revision, branch, lock, project authority를 대체하거나 변경할 수 없습니다.

---

## Selected implementation profile / 선정 구현 프로파일

```text
renderer_id: musica-fluidsynth-local
engine_target: FluidSynth 2.6.0
sound_content_profile: externally provisioned SoundFont
preferred evidence soundfont: FluidR3_GM 3.1
render_time_network_required: false
normal_git_third_party_binary: forbidden
normal_git_soundfont_or_sample_pack: forbidden
preferred evidence audio: 48 kHz stereo WAV if the exact tested build proves support
perceptual superiority: UNKNOWN unless separately evaluated
```

The adapter SHALL discover and record the actual executable version and supported render settings. It SHALL fail closed on unsupported or materially different runtime assumptions rather than silently claiming the selected profile.

Adapter는 실제 executable version과 지원 render setting을 탐지·기록해야 합니다. 지원되지 않거나 materially different한 runtime을 발견하면 선정 profile을 암묵적으로 주장하지 않고 fail closed 해야 합니다.

---

## Required proof / 필수 증명

M5-R2 is acceptable only when repository tests/evidence prove all of the following:

1. **Selection provenance / 선정 근거** — `docs/M5_R2_BACKEND_SELECTION.md` records compared candidates, scoring, sources, assumptions and `UNKNOWN`s.
2. **Exact engine identity / 엔진 식별** — the evidence runtime records the exact FluidSynth version/binary identity used; target version is 2.6.0 unless an explicit repository decision revises it before validation.
3. **Separate sound-content provenance / 음원 별도 provenance** — the exact SoundFont path is external to normal Git and its SHA-256, identity/version where available, source and license boundary are recorded separately from the engine.
4. **Machine-valid capability / 기계 검증 가능한 capability** — `musica-fluidsynth-local` declares a valid `RendererCapability v0` reflecting only capabilities actually exercised or discovered.
5. **Exact Music IR binding / 정확한 Music IR 결합** — the request is bound to the exact canonical Music IR SHA-256 before lowering/render execution.
6. **Bounded lowering / 제한된 lowering** — FluidSynth consumes MIDI/control artifacts derived from the exact Music IR; the renderer may not rewrite canonical musical state.
7. **Isolated process execution / 격리 실행** — external process invocation uses explicit argument vectors without shell interpolation, bounded timeout/error capture, and no caller-controlled arbitrary output path outside the workspace.
8. **Successful local render / 로컬 렌더 성공** — identical canonical Music IR is rendered through both `musica-reference-local` and `musica-fluidsynth-local` in the R2 evidence path.
9. **Capability uplift / capability 향상** — the FluidSynth path objectively demonstrates at least one material renderer capability above the M5-R1 reference baseline; preferred proof is a valid 48 kHz stereo WAV and externally identified sample-based instrument content if the exact runtime supports them.
10. **Objective audio QA / 객관적 QA** — the generated WAV passes `AudioQualityReport v0` checks for valid container, non-empty signal, expected duration tolerance and no hard digital clipping under the defined policy.
11. **Artifact integrity / artifact 무결성** — MIDI/audio/SoundFont-relevant provenance records include exact hashes/sizes where applicable, and tampering is detectable.
12. **Reproducibility classification / 재현성 분류** — at least two independent identical requests are compared. Byte-exact reproducibility may be marked verified only when exact artifact hashes prove it. Otherwise the result must use a weaker truthful classification.
13. **Workspace confinement / workspace 제한** — traversal, undeclared output, missing runtime, missing SoundFont, invalid SoundFont and capability mismatch cases fail closed.
14. **Project authority remains false / project 권한 없음** — rendering leaves canonical Music IR byte-equivalent and cannot advance or replace accepted project state.
15. **Repository hygiene / 레포 위생** — no FluidSynth binary, SoundFont, sample library or large generated audio is committed to normal Git.
16. **Regression / 회귀 방지** — M0→M5-R1 tests/evidence and M4-R3 real-browser E2E remain green.
17. **Durable R2 evidence / 영속 근거** — an evidence document plus CI artifact records exact request, renderer/runtime provenance, content hash/provenance, outputs, QA, reproducibility and comparison results.
18. **Exact-head integration gate / exact-head 통합 gate** — the evidence-bearing implementation PR exact head passes required CI and is merged before state promotion.
19. **State-only closure / 상태 종결** — a separate state-only closure promotes M5-R2 only after the merged evidence is rechecked from main.

---

## Capability uplift vs perceptual quality / capability 향상과 지각 품질 구분

R2 SHALL keep the following claims separate:

R2는 아래 세 주장을 반드시 분리합니다.

1. **Signal validity / 신호 유효성** — container/signal/duration/clipping QA.
2. **Renderer capability uplift / renderer capability 향상** — for example higher sample rate, stereo output, broader instrument mapping or sample-based timbre path, when objectively evidenced.
3. **Perceptual musical quality / 지각적 음악 품질** — human/model listening preference or professional quality.

A better format or richer renderer does **not** automatically prove perceptual superiority. Unless a separate evaluation protocol is executed, R2 SHALL report perceptual superiority as `UNKNOWN` and defer the claim to M5-R4.

더 높은 sample rate, stereo 또는 풍부한 renderer capability는 지각적 우월성을 자동 증명하지 않습니다. 별도 평가 protocol이 없다면 R2의 perceptual superiority는 `UNKNOWN`이며 M5-R4로 이관합니다.

---

## Licensing and redistribution boundary / 라이선스·재배포 경계

Engine and sound content SHALL be treated as separate third-party dependencies.

엔진과 음원 콘텐츠는 별도의 third-party dependency로 취급합니다.

- FluidSynth engine target: LGPL-2.1-or-later project license, to be recorded with exact runtime provenance.
- Preferred evidence SoundFont: FluidR3_GM 3.1, externally provisioned; its documented MIT provenance must be recorded for the exact source used.
- MUSICA SHALL NOT infer that an engine license grants rights to a SoundFont, or vice versa.
- R2 validation does not by itself authorize bundling either third-party binary/content in a future product installer. Redistribution packaging is a separate release/legal decision.

MUSICA는 engine license가 SoundFont 권리를 자동 부여한다고 추정해서는 안 되며 그 반대도 마찬가지입니다. R2 validation은 향후 installer에 third-party binary/content를 bundle하는 권한을 자동 승인하지 않습니다.

---

## Required negative tests / 필수 부정 테스트

At minimum, fail closed or produce an explicit non-success result for:

최소 다음 경우 fail closed 또는 명시적 non-success 결과를 내야 합니다.

- FluidSynth executable absent;
- wrong/unsupported runtime version when exact-version evidence mode is requested;
- SoundFont absent;
- SoundFont outside permitted/provisioned input policy;
- expected SoundFont hash mismatch/tamper;
- invalid or unreadable SoundFont path;
- canonical Music IR hash mismatch;
- unknown renderer ID;
- capability/output mismatch;
- output path traversal attempt;
- shell/argument injection attempt;
- renderer timeout or non-zero exit;
- missing output artifact;
- artifact hash mismatch/tamper;
- corrupt, empty/silent, clipped or duration-invalid WAV under the existing QA policy;
- false reproducibility verification claim;
- any attempt to treat renderer output as canonical project state.

---

## CI/evidence policy / CI·근거 정책

Unit/regression tests SHALL NOT require a large SoundFont to be committed into the repository.

Unit/regression test는 large SoundFont를 repository에 commit하도록 요구해서는 안 됩니다.

The R2 integration evidence job SHOULD provision the exact external dependencies at runtime, record source/version/hash, render the evidence case, upload bounded artifacts, and keep the repository free of the third-party binary/content.

R2 integration evidence job은 실행 시점에 외부 dependency를 provision하고 source/version/hash를 기록한 뒤 evidence case를 render하여 제한된 artifact만 업로드하는 방식을 우선합니다.

Windows practicality is part of the selection/validation claim. If the primary evidence render runs on another CI OS, R2 SHALL still provide a bounded Windows runtime/discovery smoke check or explicitly downgrade the Windows claim to `NOT VALIDATED`.

Windows 실용성은 선정·검증 주장에 포함됩니다. 주 evidence render가 다른 CI OS에서 실행된다면 Windows runtime/discovery smoke evidence를 별도 제공하거나 Windows claim을 `NOT VALIDATED`로 낮춰야 합니다.

---

## Reopen / NO_SELECTION rule / 재선정 규칙

The `M5R2-SEL-001` choice SHALL be reopened before validation if implementation evidence shows any disqualifier defined in `docs/M5_R2_BACKEND_SELECTION.md`, including unresolved content licensing/provenance, inability to preserve the M5-R1 authority boundary, materially fragile Windows operation, or no meaningful capability uplift over the reference renderer.

구현 근거에서 content license/provenance 미해소, M5-R1 권한 경계 유지 실패, Windows 운용의 중대한 취약성, reference renderer 대비 의미 있는 capability 향상 부재가 드러나면 `M5R2-SEL-001`은 validation 전에 재검토합니다.

`NO_SELECTION` is an acceptable evidence-based outcome; forcing a backend through the gate is not.

`NO_SELECTION`은 허용되는 근거 기반 결론이며, backend를 억지로 gate 통과시키는 것은 허용되지 않습니다.

---

## Non-goals / 비목표

M5-R2 does not require or validate:

- professional mastering quality;
- human-listener superiority;
- VST/AU hosting inside MUSICA;
- a complete DAW integration;
- proprietary foundation audio-model training;
- cloud rendering;
- live OpenAI provider execution;
- waveform/piano-roll professional editing;
- bundling third-party engine/content into a commercial installer;
- replacement or removal of the validated `musica-reference-local` renderer.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
