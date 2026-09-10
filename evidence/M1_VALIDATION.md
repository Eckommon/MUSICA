# M1 Creative Core Validation Evidence / M1 Creative Core 검증 근거

**Evidence status / 근거 상태:** PASS — PRE-MERGE VALIDATION / 통과 — 병합 전 검증

## Source / 출처

- Pull Request / PR: `#8`
- Validated head: `a2e027f9153043492bd1f26fef75ff6484291067`
- GitHub Actions workflow: `MUSICA CI`
- Workflow run: **34508344675**
- Python 3.11 test job: **SUCCESS**
- Python 3.12 test job: **SUCCESS**
- M0 regression evidence generation: **SUCCESS**
- M1 evidence generation: **SUCCESS**
- M1 evidence upload: **SUCCESS**

## M1 artifact / M1 산출 근거

- Artifact name: `musica-m1-creative-core`
- Artifact ID: **10164774426**
- Archive size: **2,397,001 bytes**
- GitHub artifact digest: `sha256:006d52ca21e91690b0be2322104c5e2fdd2a59f9bd5ec3c5880b79e940126c92`
- Manifest evidence scope: `M1-Creative-Core-v0`
- Manifest-bound internal artifacts: **51 files**

## Canonical profile evidence / 공식 프로필 근거

| Profile / 프로필 | Seed | Tempo | Tonality / 조성 | MIDI SHA-256 | WAV SHA-256 |
|---|---:|---:|---|---|---|
| `dark_electronic` | 101 | 112 BPM | D minor | `4a621d7a2dc9163700a4747d33ea5f5e4b7d016d15af25018cb893fd87224bb2` | `85e0459f2340027b7d2956737962d8f4b096cf40d078799e81f30d99ac76d70c` |
| `warm_ambient` | 202 | 84 BPM | G major | `0c8fec4263088e6268acccacdffeb5c27b3322d5ea27cb706c0ed7c3dd9ce316` | `97ea2e5dc7d479323330f2d7ba29d1a075229394e0920e7d9d523ebc091a9e62` |
| `kinetic_minimal` | 303 | 124 BPM | A minor | `776084c499d2efc707764d8e1e3f938866e167ef9840de594fef11a1cb04e3e7` | `bfa4a2c4c0e20223f4e2b4235b95b747ee6fbf1bf3d617d3e81f19ceb4233e84` |

The three canonical MIDI hashes and three canonical WAV hashes are pairwise distinct.

세 공식 MIDI 해시와 WAV 해시는 각각 상호 구분됩니다.

## Six-axis semantic executable evidence / 6축 semantic 실행 근거

All six supported axes produced a distinct executable MIDI result from the same locked canonical parent:

6개 지원 축 모두 동일한 잠금 parent에서 서로 구분되는 실행 MIDI 결과를 생성했습니다.

- `energy`: `52da947bc0683d7c88f72b5ad6991caf93be7435b62bde618ccc5ec16675c1de`
- `tension`: `744eedd8b4b75739aedcfe0b377bd66098eec100b4e18051f705d2e3f4d15390`
- `density`: `653812b64044ce1320d39014befa313e16f0fef36029f9e0132e1bf148b20e76`
- `motion`: `ee5452aa1010ccff3f14bca4076b7f545fe4cb409fd39bf4ebbc61cce7d17f32`
- `brightness`: `6122a0bedd571119056b752cecedc7a65e7a2c0b601e86c386a14e66d576730e`
- `warmth`: `3ab7e7e6009843e99b49f4498f5a600776c6346e23d93e10ce29647df88e74f7`

Automated tests additionally prove that each axis changes the local WAV output while preserving HARD tempo, melody-identity token, and rhythm-identity token locks.

자동 테스트는 각 축이 로컬 WAV 결과도 변경하면서 HARD tempo·melody identity token·rhythm identity token 잠금을 보존함을 추가로 검증합니다.

## Acceptance interpretation / 수용 해석

The evidence satisfies the executable requirements in `docs/M1_ACCEPTANCE.md` for the bounded M1 Creative Core implementation. Final `M1 = VALIDATED` status is not written here until the implementation is merged to `main` and canonical state is atomically advanced.

이 근거는 제한형 M1 Creative Core 구현에 대한 `docs/M1_ACCEPTANCE.md` 실행 요구를 충족합니다. 최종 `M1 = VALIDATED` 상태는 구현이 `main`에 병합되고 공식 상태가 원자적으로 승격되기 전까지 본 문서에서 선언하지 않습니다.

## Claim boundary / 주장 경계

This evidence does not establish arbitrary natural-language understanding, universal genre/emotion intelligence, production audio quality, perceptual melody identity, or complete DAW functionality.

본 근거는 임의 자연어 이해, 보편 장르·감정 지능, 상용 음질, 지각적 멜로디 동일성, 완전한 DAW 기능을 증명하지 않습니다.
