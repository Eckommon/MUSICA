# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**REC-R1 — TRUSTED CAPTURED-ASSET FINALIZE & RECORDING PREVIEW/ACCEPT AUTHORITY v0**

Issue `#146` — **OPEN**

Parent mission: Issue `#142` — **Recording & Monitoring Foundation v0 — OPEN**

REC-R0 is validated, merged and completed. The next dependency-safe step is to turn one exact completed derived capture into immutable accepted project media only through explicit source-bound recording authority.

## Canonical base / 공식 기준점

- canonical main after REC-R0 merge: `fce2797639258ec32418c13fb56bb9266f818b20`
- REC-R0 Issue `#143` — **COMPLETED**
- REC-R0 PR `#145` — **MERGED**
- implementation/evidence head `f8b0f90a852aeb8ba48f361c5ba1844ecb8325ac` — **29/29 SUCCESS**
- validation successor `a4d80c9e5ad9d4038bc26cf87dd6f4abbff0c348` — **29/29 SUCCESS**
- durable validation: `evidence/REC_R0_VALIDATION.md`
- artifact ID `11062015980`
- artifact ZIP SHA `04a9a49aee2a3d719e4de5f97b72e2d3aa9f3607456f984f6c3d3d9049f0f203`
- permanent workflow count: **29**

## Inherited authority / 상속 권한

```text
ATCM immutable assets + audio Preview/Accept
+ REC-R0 exact capture plan/report/PCM identity
→ REC-R1 trusted recording-finalize authority
```

Capture runtime remains derived. REC-R1 must not promote runtime objects or a report directly into accepted creative state.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground asset and audio-edit authority

Inspect `audio_assets.py`, `audio_contracts.py`, `audio_edit.py`, audio schemas/tests/validations, `recording_capture.py`, REC-R0 validation, and Project object-store/export-import integrity.

### 2. Freeze recording-finalize candidate v0

Bind exact project/revision and Blueprint/audio/routing/automation hashes, capture-plan SHA, capture-report SHA, PCM SHA/size/rate/channels/frame count, destination stable track ID, new stable clip ID, timeline start/source range/gain, actor/reason, and `preview_only=true`.

### 3. Deterministic captured-media representation

If the immutable asset domain requires WAV, define one deterministic PCM16 little-endian → WAV wrapping path. No resampling, gain processing, hidden padding or channel reinterpretation. Preserve raw capture SHA as provenance.

### 4. Preview without accepted mutation

```text
accepted revision R + exact capture C
→ validate source/capture/destination
→ Preview
→ accepted HEAD remains R
```

Preview must not create accepted track/clip state.

### 5. Explicit trusted Accept

Revalidate HEAD, persisted source hashes, plan/report self-hashes, exact PCM bytes, destination track/clip identity and no-resampling constraints. Only then create/reuse immutable captured asset and commit accepted audio material exactly once.

### 6. Fail-closed authority matrix

Reject generic commit/runtime promotion, second Accept, stale Preview, payload/report/plan tamper, wrong revision binding, unsupported format/rate/channels, missing track, duplicate clip ID, invalid timing/range and any configuration requiring resampling.

### 7. Cancel/discard proof

Abandoning a candidate must leave accepted HEAD/audio material unchanged and must not surface accepted recording media through a hidden path. If staged object bytes exist, explicitly distinguish object-store presence from accepted authority.

### 8. Accepted recording proof

Prove exactly one revision advance, exact immutable asset identity, target track ID, new clip ID, timing/source range/gain, and deterministic downstream native/routed plan/WAV change.

### 9. Reopen compatibility

Export/import reopen must preserve asset/track/clip identity, accepted audio material SHA and downstream plan/WAV identities.

### 10. Dedicated evidence and permanent gate

Add a REC-R1 workflow without weakening the existing 29 gates. Expected total: **30** permanent workflows.

### 11. Promotion

Implementation/evidence → 30/30 exact-head green → independent artifact inspection → durable `evidence/REC_R1_VALIDATION.md` → successor 30/30 green → expected-head squash merge → Issue #146 completed → state-only closure to REC-R2.

## Non-goals

No Browser recording UI, live monitoring, take/comp, punch recording, host-native microphone/line input, measured host-native latency, resampling, plugin hosting/PDC, sidechains or generalized commercial recording readiness.

## Maximum intended REC-R1 outcome

> **MUSICA can finalize a validated derived capture into immutable content-addressed project media and place it into stable accepted track/clip state only through a source-bound Preview→explicit Accept recording authority, while stale/tampered/bypass/discard paths remain fail-closed.**

This remains a target claim until REC-R1 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
