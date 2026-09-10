# M0 Runtime Proof / M0 런타임 증명

## 1. Purpose / 목적

M0-R2 proves the smallest executable MUSICA loop. It is a contract and controllability proof, not a claim of production audio quality or general-purpose AI composition intelligence.

M0-R2는 실행 가능한 최소 MUSICA 루프를 증명합니다. 이는 계약과 제어 가능성의 증명이며, 상용 음질이나 범용 AI 작곡 지능을 주장하지 않습니다.

## 2. Canonical scenario / 공식 시나리오

Root intent / 루트 의도:

> Create a dark 20-second electronic instrumental that becomes more tense toward the end.
>
> 후반으로 갈수록 긴장감이 높아지는 20초짜리 어두운 전자 기악곡을 만든다.

Semantic edit / 의미 수정:

> Make only the last six seconds more urgent while keeping the melody and drums.
>
> 멜로디와 드럼은 유지하고 마지막 6초만 더 긴박하게 만든다.

The root Blueprint also HARD-locks tempo at 112 BPM.

루트 Blueprint는 템포 112 BPM도 HARD lock으로 고정합니다.

## 3. Runtime pipeline / 런타임 파이프라인

```text
Blueprint R1
   ↓ validate
Semantic Control
   ↓ deterministic resolver
Candidate Blueprint R2
   ↓ HARD lock + constraint validation
Accepted Blueprint R2
   ↓ structured diff
Blueprint → Music IR compiler
   ↓ validate
Music IR R1 / R2
   ↓
Standard MIDI File + local PCM WAV preview
   ↓
SHA-256 evidence manifest
```

## 4. M0 semantic lowering / M0 의미 변환

The runtime resolver intentionally implements only the `tension` semantic axis. The broader semantic vocabulary is schema-defined but not claimed as runtime-implemented yet.

런타임 resolver는 의도적으로 `tension` 의미 축만 구현합니다. 더 넓은 의미 어휘는 스키마에 정의되어 있지만 아직 런타임 구현으로 주장하지 않습니다.

For the canonical increase request, M0 preserves:

공식 증가 요청에서 M0는 다음을 보존합니다.

- tempo identity / 템포 정체성,
- main motif identity token / 메인 모티프 identity token,
- drum pattern identity token / 드럼 패턴 identity token.

It selects allowed mechanisms such as higher final-section bass activity, harmonic-motion intent, and texture-density intent.

대신 마지막 구간의 베이스 활동도 증가, 화성 움직임 의도 증가, 텍스처 밀도 의도 증가와 같은 허용 메커니즘을 선택합니다.

## 5. Compiler boundary / 컴파일러 경계

The M0 compiler uses explicit motif and drum events from the Blueprint, a simple chord-root bass lowering rule, and one deterministic semantic-pressure rule. It is not a complete composition engine.

M0 컴파일러는 Blueprint의 명시 모티프·드럼 이벤트, 단순 코드 루트 베이스 변환 규칙, 하나의 결정론적 semantic-pressure 규칙을 사용합니다. 완전한 작곡 엔진이 아닙니다.

## 6. Renderers / 렌더러

### MIDI

MUSICA writes a deterministic Standard MIDI File using only the Python standard library.

MUSICA는 Python 표준 라이브러리만으로 결정론적 Standard MIDI File을 기록합니다.

### WAV preview / WAV 프리뷰

MUSICA renders a deterministic mono 16-bit PCM preview through a tiny built-in synthesis path. This makes the M0 proof audible and dependency-light. It is not a production synth, sampler, mix engine, or mastering system.

MUSICA는 내장된 소형 합성 경로로 결정론적 mono 16-bit PCM 프리뷰를 렌더링합니다. 이는 M0 증명을 청취 가능하고 의존성 적게 만들기 위한 것이며, 상용 synth·sampler·mix·mastering 시스템이 아닙니다.

## 7. Reproduce locally / 로컬 재현

```bash
python -m pip install -e '.[dev]'
pytest
python -m musica.m0_demo \
  --blueprint examples/blueprints/valid/dark-electronic-20s-r1.json \
  --control examples/semantic-controls/urgent-final-section.json \
  --out artifacts/m0-demo
```

Windows PowerShell may place the command on one line or use PowerShell continuation syntax.

Windows PowerShell에서는 한 줄로 실행하거나 PowerShell 줄 연결 문법을 사용할 수 있습니다.

## 8. Evidence bundle / 근거 번들

A successful run generates:

성공 실행은 다음을 생성합니다.

- `blueprint-r1.json`
- `semantic-control.json`
- `blueprint-r2.json`
- `blueprint-diff.json`
- `music-ir-r1.json`
- `music-ir-r2.json`
- `preview-r1.mid`
- `preview-r2.mid`
- `preview-r1.wav`
- `preview-r2.wav`
- `manifest.json`

`manifest.json` binds the compiler and renderer versions to SHA-256 hashes of the generated artifacts.

`manifest.json`은 컴파일러·렌더러 버전과 생성 산출물의 SHA-256 해시를 결합합니다.

## 9. Claim boundary / 주장 경계

M0-R2 may support claims only after passing CI evidence exists. Even after validation, it does **not** prove:

M0-R2는 CI 통과 근거가 존재한 후에만 해당 주장을 지원합니다. 검증 후에도 다음을 증명하지는 않습니다.

- production-quality audio generation / 상용 수준 오디오 생성,
- arbitrary natural-language understanding / 임의 자연어의 범용 이해,
- perceptual melody identity / 지각적 멜로디 동일성,
- full DAW functionality / 완전한 DAW 기능,
- renderer-independent equivalence across external backends / 외부 백엔드 간 동일 결과 보장.
