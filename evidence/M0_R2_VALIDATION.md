# M0-R2 Validation Evidence / M0-R2 검증 근거

**Status / 상태:** VALIDATION EVIDENCE RECORDED / 검증 근거 기록

## 1. Scope / 범위

This record captures the repository-backed evidence for the minimal deterministic MUSICA runtime loop implemented in M0-R2.

이 문서는 M0-R2에서 구현한 최소 결정론 MUSICA 런타임 루프의 레포 기반 검증 근거를 기록합니다.

## 2. GitHub Actions evidence / GitHub Actions 근거

- Workflow / 워크플로: `MUSICA CI`
- Run ID / 실행 ID: `34505494680`
- Pull request / PR: `#4`
- Head SHA / 헤드 SHA: `b581a25647f32ec844570a666d91b05ebf0c5dd3`
- Python 3.11 job / 작업: **SUCCESS**
- Python 3.12 job / 작업: **SUCCESS**
- Canonical M0 evidence generation / 공식 M0 근거 생성: **SUCCESS**
- Artifact upload / 산출물 업로드: **SUCCESS**

## 3. Workflow artifact / 워크플로 산출물

- Artifact name / 이름: `musica-m0-demo`
- Artifact ID / ID: `10163638294`
- Archive size / 압축 크기: `941953 bytes`
- Artifact archive digest / 압축 산출물 digest: `sha256:6a72629116444924cd2ca219672cd4d0fd83107c612f57b070ef4b8dc1c2fa1d`

The artifact was separately inspected after CI completion; the following inner files were present.

CI 완료 후 산출물 자체를 별도로 검사했으며 다음 내부 파일이 존재했습니다.

| Artifact / 산출물 | Size / 크기 | SHA-256 |
| --- | ---: | --- |
| `blueprint-diff.json` | 1691 | `270c57110148955e2709cf8dd8f03d3ff46b541007b981eb2c1c004cf8eaf512` |
| `blueprint-r1.json` | 4695 | `085d44ac294631e0816b6cb3e58bc5d616b29dec408f867633506e83a2f7222b` |
| `blueprint-r2.json` | 5051 | `074b906a3a737561b35509a1b2fdc6b9339688255eefe27c4b44c6595777a25c` |
| `music-ir-r1.json` | 5887 | `b17f2c0e883dd4b24d13048d10b2d5cfe4db2b528084277acdac28cf9fd0cc17` |
| `music-ir-r2.json` | 6023 | `53efe7c2dd9445a7bd1065fe622a29180cb7dbdb3b570a59869ea5b541fa5987` |
| `preview-r1.mid` | 788 | `09805711363539af14f57a0e9db0007a6ea316f18d0baff54ad8f1d8b78a7b63` |
| `preview-r1.wav` | 882044 | `e90599109aaa75828d5c65fecbea04ad457a4910fbc0fafb0fc881b20eadc8bd` |
| `preview-r2.mid` | 808 | `a835d16c6e3c0a60f47bb93de0d85088e630161f5bd76213404ef2cfdfe818a7` |
| `preview-r2.wav` | 882044 | `63b29370f815b2de57914b406abaab2e956176e8a38cca64a35b6e4baeba4e65` |
| `semantic-control.json` | 513 | `68ec12a11dc1f9569a7caccd86c930e905c42d9d9d67d69d0c523ba36417292d` |

`preview-r1` and `preview-r2` have different MIDI and WAV hashes, proving that the accepted semantic edit changed executable/rendered output. Contract tests additionally prove that tempo, motif identity token, and drum-pattern identity token remain HARD-locked.

`preview-r1`과 `preview-r2`의 MIDI·WAV 해시는 서로 다르므로 승인된 의미 수정이 실제 실행·렌더 결과를 변경했음을 증명합니다. 계약 테스트는 동시에 템포, 모티프 identity token, 드럼 패턴 identity token의 HARD lock 보존을 증명합니다.

## 4. Runtime identity / 런타임 식별자

- Project / 프로젝트: `MUSICA-M0-DEMO-001`
- Parent revision / 부모 리비전: `rev-001`
- Candidate revision / 후보 리비전: `rev-002`
- Semantic control / 의미 제어: `SC-M0-001`
- Compiler / 컴파일러: `musica-deterministic-m0@0.0.1`
- MIDI renderer / MIDI 렌더러: `musica-smf-writer@0.0.1`
- WAV renderer / WAV 렌더러: `musica-local-preview-synth@0.0.1`
- WAV format / WAV 형식: mono, 16-bit PCM, 22050 Hz

## 5. Validated claims / 검증된 주장

M0-R2 evidence supports only the following claims.

M0-R2 근거는 다음 주장만 지원합니다.

1. A validated Blueprint can compile deterministically to validated Music IR. / 검증된 Blueprint를 결정론적으로 검증된 Music IR로 컴파일할 수 있음.
2. A bounded `tension` semantic edit can produce an explicit revision while preserving specified HARD locks. / 제한된 `tension` 의미 수정이 지정 HARD lock을 보존하며 명시적 리비전을 생성할 수 있음.
3. A structured diff can explain that revision. / 구조화 diff가 해당 리비전을 설명할 수 있음.
4. The resulting IR can be serialized to deterministic Standard MIDI File bytes. / 결과 IR을 결정론적 Standard MIDI File로 직렬화할 수 있음.
5. The resulting IR can be rendered to an audible deterministic local PCM WAV preview. / 결과 IR을 청취 가능한 결정론적 로컬 PCM WAV 프리뷰로 렌더링할 수 있음.
6. Generated evidence artifacts are reproducible at SHA-256 level under the tested path. / 테스트된 경로에서 생성 근거 산출물을 SHA-256 수준으로 재현할 수 있음.

## 6. Explicit non-claims / 명시적 비주장

This evidence does **not** prove production audio quality, general-purpose semantic music understanding, perceptual melody equivalence, full DAW functionality, external generative-audio integration, or professional mixing/mastering.

이 근거는 상용 수준 음질, 범용 의미 음악 이해, 지각적 멜로디 동일성, 완전한 DAW 기능, 외부 생성형 오디오 통합, 전문 믹싱·마스터링을 증명하지 않습니다.
