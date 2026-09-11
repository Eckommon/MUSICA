# M5-R2 Runtime / M5-R2 런타임

## Status / 상태

**IMPLEMENTATION CANDIDATE — NOT YET VALIDATED / 구현 후보 — 아직 검증 완료 아님**

This document describes the bounded runtime contract for `musica-fluidsynth-local`. Actual FluidSynth + FluidR3 evidence is required before M5-R2 may be promoted.

이 문서는 `musica-fluidsynth-local`의 제한된 runtime contract를 설명합니다. 실제 FluidSynth + FluidR3 근거가 확보되기 전까지 M5-R2는 승격할 수 없습니다.

## Runtime configuration / 런타임 구성

The adapter is configured outside canonical project state using environment/runtime provisioning:

Adapter는 canonical project state 외부의 environment/runtime provisioning으로 구성합니다.

```text
MUSICA_FLUIDSYNTH_BIN                path or executable name (default: fluidsynth)
MUSICA_FLUIDSYNTH_SOUNDFONT          required external .sf2 path
MUSICA_FLUIDSYNTH_SOUNDFONT_ID       logical content id
MUSICA_FLUIDSYNTH_EXPECTED_VERSION   exact expected runtime version (default: 2.6.0)
```

The SoundFont path is intentionally **not** embedded into the canonical RendererRequest. Instead, the request binds a logical resource ID and exact SHA-256. The configured external file must match both before rendering.

SoundFont의 실제 filesystem path는 canonical RendererRequest에 넣지 않습니다. Request에는 logical resource ID와 정확한 SHA-256만 결합하며, 외부 구성 파일은 render 전에 두 값과 일치해야 합니다.

## Request binding / 요청 결합

`RendererRequest v0` remains backward compatible and gains an optional `resources` field. For the FluidSynth adapter exactly one resource is required:

```json
{
  "role": "soundfont",
  "resource_id": "FluidR3_GM-3.1",
  "sha256": "<exact 64-hex content hash>"
}
```

A path is not accepted from the request. Therefore a caller cannot redirect the adapter to an arbitrary SoundFont or output path through request data.

Request에서 path를 받지 않으므로 caller가 request data를 이용해 임의 SoundFont 또는 output path로 adapter를 우회할 수 없습니다.

## Execution boundary / 실행 경계

The adapter:

1. resolves the executable explicitly;
2. executes `--version` using an argument vector and `shell=False`;
3. requires exact target version `2.6.0` by default;
4. hashes the resolved executable;
5. validates the externally provisioned SoundFont and hashes it;
6. validates exact canonical Music IR hash;
7. lowers Music IR through the existing trusted MIDI renderer;
8. creates its own deterministic workspace output directory;
9. launches FluidSynth with an argument vector, never a shell command string;
10. requests bounded fast file rendering to WAV using 16-bit PCM and the requested supported sample rate;
11. runs the existing objective WAV QA;
12. writes a canonical `renderer-provenance.json` manifest and binds its SHA-256 into `RendererResult v0`.

Adapter는 shell interpolation을 사용하지 않으며 caller-controlled arbitrary output path를 허용하지 않습니다.

### Current bounded CLI shape / 현재 제한 CLI 형태

```text
<fluidsynth>
  -n -i -q
  -F <workspace-derived-output.wav>
  -T wav
  -O s16
  -r <44100-or-48000>
  <externally-configured-soundfont-path>
  <workspace-derived-midi-path>
```

The exact executable and SoundFont paths are runtime inputs, not repository or project authority.

## Capability declaration / capability 선언

Until real integration evidence says otherwise, the adapter exposes the intentionally narrow capability:

```text
renderer_id: musica-fluidsynth-local
classification: deterministic
outputs: midi, wav
sample_rates: 44100, 48000
channels: stereo (2)
sample_width: 16-bit PCM
external_binary: true
plugin_host: false
network: false at render time
reproducibility: stable_parameters
```

`stable_parameters` is a capability classification, not proof of byte identity. Individual `RendererResult` objects keep `verified=false`; independent repeated-render evidence owns verification.

`stable_parameters`는 capability 분류이며 byte identity 증명이 아닙니다. 개별 `RendererResult`는 `verified=false`를 유지하며 독립 반복 render 근거가 검증을 담당합니다.

## Provenance / provenance

A FluidSynth result additionally binds `renderer-provenance.json`. The manifest records:

- adapter version;
- exact engine version;
- executable SHA-256;
- SoundFont logical ID, SHA-256 and byte size;
- bounded render settings;
- `project_authority=false`.

`verify_result_artifacts()` verifies the provenance manifest path remains in the workspace and its bytes still match the bound SHA-256.

## Security and failure policy / 보안·실패 정책

Fail closed on:

- missing/unresolved executable;
- version-probe failure or exact-version mismatch;
- missing/empty SoundFont;
- request SoundFont ID/hash mismatch;
- canonical Music IR hash mismatch;
- unsupported sample rate/channel/sample width/output;
- subprocess timeout or non-zero exit;
- missing output;
- QA failure;
- artifact/provenance path traversal;
- artifact/provenance hash tamper.

The adapter receives no API for project revision/branch/lock mutation.

Adapter에는 project revision/branch/lock을 변경하는 API가 제공되지 않습니다.

## Repository hygiene / 레포 위생

Never commit the following to normal Git:

- FluidSynth release binary archives;
- `fluidsynth.exe` or platform binaries;
- FluidR3_GM or other SoundFonts;
- third-party sample packs;
- large generated WAV comparison artifacts.

CI/evidence SHALL provision third-party runtime/content externally and upload bounded evidence artifacts separately.

## Evidence boundary / 근거 경계

Current source-code/unit tests can prove adapter contract behavior using a synthetic executable and synthetic content bytes. They **cannot** prove actual FluidSynth audio behavior, actual FluidR3 provenance, Windows operation, or perceptual improvement.

현재 source/unit test는 synthetic executable/content를 통해 adapter contract만 증명할 수 있습니다. 실제 FluidSynth audio 동작, 실제 FluidR3 provenance, Windows 실행, 청감 향상은 증명하지 못합니다.

Those claims require the dedicated M5-R2 integration evidence path defined in `docs/M5_R2_ACCEPTANCE.md`.

**Repository evidence remains authoritative over conversation or model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
