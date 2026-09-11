# M5-R2 Runtime / M5-R2 런타임

## Status / 상태

**IMPLEMENTATION CANDIDATE — FINAL VALIDATION PENDING / 구현 후보 — 최종 검증 대기**

This document defines the bounded runtime contract for `musica-fluidsynth-local`. Real FluidSynth 2.6.0 + externally provisioned FluidR3_GM 3.1 execution has been observed on the implementation branch, but M5-R2 remains unpromoted until durable evidence, evidence-bearing exact-head CI, merge, and state-only closure are complete.

이 문서는 `musica-fluidsynth-local`의 제한된 runtime contract를 정의합니다. 구현 branch에서 실제 FluidSynth 2.6.0 + 외부 provision된 FluidR3_GM 3.1 실행은 관측되었지만, durable evidence·evidence-bearing exact-head CI·merge·state-only closure가 끝나기 전까지 M5-R2는 승격하지 않습니다.

## Runtime configuration / 런타임 구성

The adapter is configured outside canonical project state using runtime provisioning:

```text
MUSICA_FLUIDSYNTH_BIN                path or executable name (default: fluidsynth)
MUSICA_FLUIDSYNTH_SOUNDFONT          required external .sf2 path
MUSICA_FLUIDSYNTH_SOUNDFONT_ID       logical content id
MUSICA_FLUIDSYNTH_EXPECTED_VERSION   exact expected runtime version (default: 2.6.0)
```

The SoundFont filesystem path is intentionally **not** embedded into canonical `RendererRequest v0`. The request binds only a logical resource ID and exact SHA-256; the externally configured file must match both before rendering.

SoundFont의 실제 filesystem path는 canonical `RendererRequest v0`에 넣지 않습니다. Request에는 logical resource ID와 정확한 SHA-256만 결합하며 외부 구성 파일은 render 전에 두 값과 일치해야 합니다.

Provisioning may require network access, but the bounded render operation itself declares `network=false` and does not require network access after executable/content provisioning.

Provisioning 단계는 network를 사용할 수 있지만 executable/content 준비 이후의 제한된 render 동작 자체는 `network=false`이며 network를 요구하지 않습니다.

## Request binding / 요청 결합

For the FluidSynth adapter exactly one external SoundFont resource is required:

```json
{
  "role": "soundfont",
  "resource_id": "FluidR3_GM-3.1",
  "sha256": "<exact 64-hex content hash>"
}
```

A path is not accepted from the request. Therefore caller request data cannot redirect the adapter to arbitrary SoundFont or output paths.

## Execution boundary / 실행 경계

The adapter SHALL:

1. resolve the executable explicitly;
2. probe `--version` with an argument vector and `shell=False`;
3. require exact target version `2.6.0` by default;
4. hash the resolved executable;
5. hash and validate the externally provisioned SoundFont;
6. validate exact canonical Music IR SHA-256;
7. lower Music IR through the existing trusted MIDI renderer;
8. derive output paths only below the caller-provided workspace;
9. launch FluidSynth with an argument vector, never shell interpolation;
10. request fast file rendering to WAV as 48 kHz stereo 16-bit PCM;
11. normalize only excess renderer tail to the explicit MUSICA duration contract;
12. run objective WAV QA on the normalized final artifact;
13. write canonical `renderer-provenance.json` and bind its SHA-256 into `RendererResult v0`;
14. remove the unmanaged raw-engine WAV after successful normalization while retaining its hash/duration provenance.

The adapter receives no API for project revision, branch, lock, Blueprint, or canonical Music IR mutation.

Adapter에는 project revision, branch, lock, Blueprint 또는 canonical Music IR을 변경하는 API가 제공되지 않습니다.

### Current bounded CLI shape / 현재 제한 CLI 형태

```text
<fluidsynth>
  -n -i -q
  -F <workspace-derived-raw-output.wav>
  -T wav
  -O s16
  -r 48000
  <externally-configured-soundfont-path>
  <workspace-derived-midi-path>
```

The executable path, SoundFont path and raw renderer file are runtime infrastructure, not project authority.

## Duration normalization / 길이 정규화

FluidSynth fast rendering may retain instrument release/effect tail beyond the requested MUSICA project duration. M5-R2 does **not** relax duration QA and does **not** disable renderer effects merely to force a shorter file.

FluidSynth fast rendering은 요청된 MUSICA project 길이 이후의 instrument release/effect tail을 포함할 수 있습니다. M5-R2는 이를 이유로 duration QA를 완화하지 않으며 파일 길이를 맞추기 위해 renderer effect를 임의로 비활성화하지 않습니다.

The bounded policy is:

```text
FluidSynth raw WAV
      ↓
record raw SHA-256 / bytes / frame count / duration
      ↓
if raw < requested duration → FAIL CLOSED
if raw ≥ requested duration → trim exact excess frames only
      ↓
final WAV at exact requested frame count
      ↓
objective AudioQualityReport
      ↓
remove unmanaged raw WAV after success
```

Policy identifier: `trim_tail_to_requested_duration_v0`.

Padding is forbidden in R2. MUSICA SHALL NOT invent missing audio when the renderer underruns the requested duration.

R2에서 padding은 금지됩니다. Renderer 출력이 요청 길이보다 짧을 경우 MUSICA는 누락 audio를 생성해 채우지 않고 fail-closed 합니다.

The provenance manifest records whether normalization occurred, raw SHA-256, raw byte size, raw frame count/duration, target frame count/duration, trimmed frame count and `padding_applied=false`.

## Capability declaration / capability 선언

The intentionally narrow R2 capability is:

```text
renderer_id: musica-fluidsynth-local
classification: deterministic
outputs: midi, wav
sample_rates: 48000 only
channels: stereo (2)
sample_width: 16-bit PCM
external_binary: true
plugin_host: false
network: false at render time
reproducibility: stable_parameters
```

Only 48 kHz is declared because that is the R2 evidence target. Other FluidSynth-supported formats are not silently promoted into MUSICA capability.

R2 evidence target이 48 kHz이므로 해당 범위만 선언합니다. FluidSynth 자체가 지원할 수 있는 다른 format을 MUSICA capability로 자동 승격하지 않습니다.

`stable_parameters` is a capability classification, not proof of byte identity. Individual `RendererResult` objects keep `verified=false`; independent repeated-render evidence owns any observed byte-identity claim.

`stable_parameters`는 capability 분류이며 byte identity 증명이 아닙니다. 개별 `RendererResult`는 `verified=false`를 유지하며 독립 반복 render 근거가 실제 동일성 관측을 담당합니다.

## Provenance / provenance

A FluidSynth result binds `renderer-provenance.json`. It records at least:

- adapter version;
- exact engine version and executable SHA-256;
- SoundFont logical ID, SHA-256 and byte size;
- bounded render settings;
- duration-normalization policy and raw-engine measurements;
- `network_required=false` for render execution;
- `project_authority=false`.

`verify_result_artifacts()` verifies the provenance path remains inside the workspace and that its bytes match the SHA-256 bound into `RendererResult v0`.

## Security and failure policy / 보안·실패 정책

Fail closed on:

- missing/unresolved executable;
- version-probe failure or exact-version mismatch;
- missing/empty SoundFont;
- SoundFont ID/hash mismatch;
- canonical Music IR hash mismatch;
- unsupported sample rate/channel/sample width/output;
- subprocess timeout or non-zero exit;
- missing/corrupt output;
- raw output shorter than requested duration;
- final AudioQualityReport failure;
- raw-intermediate cleanup failure;
- artifact/provenance path traversal;
- artifact/provenance hash tamper.

## Repository hygiene / 레포 위생

Never commit the following to normal Git:

- FluidSynth binary archives or platform executables;
- FluidR3_GM or other SoundFonts;
- third-party sample packs;
- large generated comparison WAVs;
- raw engine intermediate WAVs.

CI/evidence provisions third-party runtime/content outside the repository, records exact provenance/hashes, and uploads only bounded evidence artifacts.

## Evidence boundary / 근거 경계

Synthetic unit tests prove adapter contract behavior. Dedicated Windows integration evidence is required to prove actual FluidSynth 2.6.0 execution, exact external SoundFont binding, 48 kHz stereo output, normalization behavior and runtime practicality.

Synthetic unit test는 adapter contract 동작을 증명합니다. 실제 FluidSynth 2.6.0 실행, 정확한 외부 SoundFont binding, 48 kHz stereo 출력, normalization 동작과 Windows runtime 실용성은 별도 Windows integration evidence가 증명해야 합니다.

Neither higher sample format nor a richer SoundFont automatically proves perceptual musical superiority. Perceptual superiority remains `UNKNOWN` until a separate comparative evaluation such as M5-R4.

높은 format spec 또는 풍부한 SoundFont 자체는 지각적 음악 품질 우월성을 자동 증명하지 않습니다. 청감 우월성은 M5-R4 같은 별도 비교 평가 전까지 `UNKNOWN`입니다.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
