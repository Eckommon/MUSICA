# M3-R2 Acceptance / OpenAI Provider Adapter 수용 기준

**Status / 상태:** ACTIVE GATE / 활성 게이트

## Objective / 목표

M3-R2 SHALL connect the validated M3-R1 provider-neutral boundary to the current OpenAI Responses API contract without granting the external model authority over canonical MUSICA state.

M3-R2는 검증된 M3-R1 provider-neutral 경계를 현재 OpenAI Responses API 계약에 연결하되 외부 모델에 MUSICA 공식 상태 권한을 부여하지 않아야 합니다.

## Acceptance criteria / 수용 기준

M3-R2 is accepted only when all of the following are repository-backed and exact-head CI validated.

M3-R2는 다음 조건이 레포 근거와 exact-head CI로 모두 검증된 경우에만 수용합니다.

1. **Current API contract / 현재 API 계약** — adapter builds `POST /v1/responses` payloads and requests strict `text.format.type=json_schema` Structured Outputs.
2. **Narrow model authority / 제한된 모델 권한** — the model emits only mode-specific creative bodies. Provider metadata, seed policy, explicit user preserve/exclusion policy, exact edit time scope, protected HARD-lock targets, proposal identity, and acceptance remain MUSICA-owned.
3. **M3-R1 reuse / M3-R1 재사용** — reconstructed output MUST pass existing Director Proposal v0 authority validation before lowering.
4. **Create path / 생성 경로** — natural language → OpenAI body → Director Proposal → Music Intent → M1 Blueprint → M2 project commit.
5. **Edit path / 수정 경로** — natural language + exact revision context → OpenAI body → exact scope/protected-target reconstruction → Semantic Control → M1 resolver → HARD lock validation → explicit M2 commit.
6. **Credential boundary / 자격정보 경계** — live credentials come only from a runtime environment variable; API keys and Authorization headers MUST NOT enter repository evidence or canonical adapter exchange records.
7. **Injected transport / 주입형 transport** — normal CI MUST run without network and without secrets.
8. **Provenance / provenance** — successful exchange records provider/model/response metadata, usage, retry policy, and SHA-256 digests for exact request payload, raw response, structured body, and reconstructed Director Proposal.
9. **Failure taxonomy / 실패 분류** — auth, rate-limit, server, timeout, transport, incomplete, refusal, and invalid-output failures are distinct and fail closed.
10. **Retry boundary / 재시도 경계** — only bounded transient classes may retry; auth or invalid model output MUST NOT be silently retried into acceptance.
11. **Evidence-class honesty / 근거 분류 정직성** — injected/offline CI evidence MUST be labeled `ADAPTER_CONTRACT_EVIDENCE`; only an actually authorized network call may be labeled `LIVE_PROVIDER_EVIDENCE`.
12. **Authority attacks / 권한 공격** — arbitrary Blueprint/patch/acceptance injection and invalid section targeting MUST be rejected before canonical state mutation.
13. **Regression / 회귀** — M0, M1, M2, and M3-R1 test/evidence paths remain green on Python 3.11 and 3.12.
14. **Canonical artifact / 공식 산출물** — Python 3.12 CI generates and uploads `musica-m3-r2-openai-adapter` evidence.

## Canonical proof / 공식 증명

```text
User language
  ↓
Director Request v0
  ↓
OpenAI Responses payload
  ↓
[injected offline transport in normal CI]
  ↓
strict mode-specific creative body
  ↓
MUSICA reconstructs Director Proposal v0
  ↓
M3-R1 authority validation
  ↓
M1 trusted lowering + locks
  ↓
M2 explicit project commit
  ↓
MIDI/WAV + hashes + adapter exchange evidence
```

Negative proof MUST additionally demonstrate malformed/over-authoritative model output, refusal, incomplete response, rate-limit, and timeout fail closed.

부정 증명은 잘못되거나 과도한 권한의 모델 출력, refusal, incomplete response, rate-limit, timeout이 모두 실패 폐쇄됨을 추가로 입증해야 합니다.

## Claim boundary / 주장 경계

M3-R2 does **not** require or imply:

- a live OpenAI call in public CI,
- committed API credentials,
- identical future model output,
- universal natural-language music understanding,
- autonomous project acceptance,
- production mastering quality,
- direct DAW/plugin control.

M3-R2는 public CI의 실제 OpenAI 호출, API key 커밋, 미래 모델 출력의 동일성, 보편적 자연어 음악 이해, 자율 승인, 상용 마스터링, 직접 DAW/plugin 제어를 요구하거나 암시하지 않습니다.
