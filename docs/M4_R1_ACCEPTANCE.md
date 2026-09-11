# M4-R1 Acceptance / Studio Application Service 수용 기준

**Status / 상태:** **VALIDATED / 검증 완료**

## Objective / 목표

M4-R1 SHALL expose validated MUSICA M0→M3 capabilities through a local-first application/session boundary without allowing UI convenience to bypass AI authority, preview/accept, lock, project-integrity, or workspace-security rules.

M4-R1은 검증된 M0→M3 기능을 local-first 애플리케이션·세션 경계로 노출하되 UI 편의성이 AI 권한, preview/accept, lock, project integrity, workspace 보안 규칙을 우회하지 못하게 해야 합니다.

## Acceptance criteria / 수용 기준

All criteria below are satisfied by exact-head PR CI and `evidence/M4_R1_VALIDATION.md`. / 아래 기준은 exact-head PR CI와 `evidence/M4_R1_VALIDATION.md`로 모두 충족되었습니다.

1. **Workspace confinement / workspace 제한** — project/cache/preview/export stay within the configured workspace; traversal/symlink escape fail closed. **PASS**
2. **Create/open / 생성·열기** — `.musica` projects can be created/reopened without Git knowledge. **PASS**
3. **Natural-language create / 자연어 생성** — create flows through M3 Director authority and M1 Blueprint generation; offline fixture is default. **PASS**
4. **Optional OpenAI / 선택적 OpenAI** — OpenAI mode is wired; missing runtime credentials fail before partial project creation. **PASS**
5. **Inspection / 검사** — branch/head, sections, six semantic values, HARD locks, branches, media and preview state are machine-readable. **PASS**
6. **Non-canonical preview / 비공식 preview** — edit previews render audible candidates without advancing the branch ref. **PASS**
7. **Explicit acceptance / 명시 승인** — only explicit acceptance commits the candidate and binds MIDI/WAV. **PASS**
8. **Discard / 폐기** — discard clears preview state/cache while preserving the exact branch head. **PASS**
9. **Preview conflict policy / preview 충돌 규칙** — branch/checkout/export operations that would make state ambiguous are blocked while preview is pending. **PASS**
10. **Branch/history / branch·이력** — branch create/checkout and accepted revision history are exposed through the application boundary. **PASS**
11. **Deterministic export / 결정론 export** — unchanged state produces byte-identical `.musica.zip`. **PASS**
12. **Media / 미디어** — accepted/preview MIDI/WAV are retrievable through service/loopback HTTP. **PASS**
13. **Local HTTP / 로컬 HTTP** — bridge is loopback-only and non-loopback bind fails closed. **PASS**
14. **Machine contracts / 기계 계약** — Studio session, preview, response and error objects use versioned JSON schemas. **PASS**
15. **Restart/open proof / 재개 증명** — a second service instance reopens the same durable project and media. **PASS**
16. **Regression / 회귀** — M0→M3 tests/evidence remain green on Python 3.11/3.12. **PASS**
17. **Canonical evidence / 공식 근거** — Python 3.12 exact-head CI generates/uploads `musica-m4-r1-studio-service`. **PASS**

## Final validation identity / 최종 검증 식별자

- implementation PR: `#24`
- exact final head: `cba73433c5e83315472c0305b20f436672d1fb0d`
- exact-head CI: `34549868112`
- final artifact: `musica-m4-r1-studio-service`, ID `10180408128`
- artifact digest: `sha256:3640aebebb156f975a9faea58026604f419aa5ecc471174f7da6cb28f1d4c81e`
- implementation merge: `4ebe2e0590b17f5e659dd48bed5b0331af7fac9b`
- durable evidence: `evidence/M4_R1_VALIDATION.md`

## Canonical authority / 공식 권한

```text
Studio client
  ↓
validated M4-R1 application service
  ↓
M3 Director / validated semantic command
  ↓
M1/M0 trusted core + HARD locks
  ↓
PREVIEW cache — not canonical
  ↓ explicit Accept only
M2 Project Engine commit
  ↓
Accepted revision + bound MIDI/WAV
```

**Preview is not an accepted revision. / Preview는 승인 리비전이 아닙니다.**

## Claim boundary / 주장 경계

M4-R1 is an **application-service boundary**, not the final polished Studio UI. It does not validate production mastering, cloud collaboration, desktop packaging, arbitrary remote HTTP serving, multi-user security, live OpenAI execution, professional DAW/VST/sampler interoperability, or browser-level E2E UX.

M4-R1은 **애플리케이션 서비스 경계**이며 최종 Studio UI가 아닙니다. 상용 마스터링, cloud collaboration, desktop packaging, 임의 원격 HTTP 제공, 다중 사용자 보안, 실제 OpenAI live 실행, 전문 DAW/VST/sampler 상호운용, browser-level E2E UX는 검증하지 않습니다.
