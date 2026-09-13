# M6-R4 Acceptance Contract / M6-R4 수용 계약

**Milestone / 마일스톤:** `M6-R4 — Bounded Interchange Reconciliation for Representable Exact-Note Edits`  
**Governing Issue / 지배 Issue:** `#65`  
**Status / 상태:** `ACCEPTED SPECIFICATION — IMPLEMENTATION NOT YET VALIDATED`

## 1. Purpose / 목적

M6-R4 may reconcile a narrowly bounded external DAWproject note change into MUSICA's existing exact-note authority only when the change is provably derived from one exact MUSICA export lineage and can be expressed as an existing M6 primitive.

M6-R4는 하나의 정확한 MUSICA export 계보에 결박되고 기존 M6 primitive로 유일하게 표현 가능한 외부 DAWproject note 변경만 MUSICA exact-note authority로 환원할 수 있습니다.

The external artifact remains a **non-canonical carrier**. It never becomes accepted state by import alone.

## 2. Authority chain / 권한 체인

```text
Accepted exact-note Blueprint
→ deterministic Music IR
→ deterministic MUSICA DAWproject export
→ source-bound note identity map + normalized export baseline
→ optional external modification
→ safe parse / XSD validation / normalization
→ exact baseline-versus-returned comparison
→ uniquely provable one-primitive note delta
→ typed NoteEditCandidate
→ existing M6 source/lock/constraint authority
→ READY_FOR_PREVIEW or BLOCKED
→ non-canonical Preview
→ explicit Accept only
→ existing M2 revision authority
```

Forbidden:

```text
returned artifact alone → inferred MUSICA identity
DAW note index/order → stable note identity
nearest-note heuristic → identity
ambiguous mapping → guessed operation
external state → accepted Blueprint
Music IR mutation → accepted Blueprint
external artifact → lock/constraint bypass
```

## 3. Historical compatibility / 역사적 호환

M5-R3 evidence remains immutable historical truth. Its arbitrary external note-edit `UNSUPPORTED_BLOCKING` verdict was correct because canonical exact-note reverse-mapping authority did not yet exist.

M6-R4 is additive. It does not rewrite M5-R3 evidence and does not broaden M5-R3's historical claim.

## 4. REQUIRED Gate A — MUSICA-origin source lineage / MUSICA-origin 소스 계보

Reconciliation requires a source bundle created from one accepted exact-note Blueprint and the exact MUSICA DAWproject export produced from it.

The bundle SHALL bind at minimum:

- project ID;
- source accepted revision ID;
- canonical Blueprint SHA-256;
- exact timeline SHA-256;
- compiled Music IR SHA-256;
- exported DAWproject SHA-256;
- normalized export baseline SHA-256;
- reconciliation policy/version;
- source-bound note identity records.

Missing or mismatched binding is fail-closed.

## 5. REQUIRED Gate B — identity without array authority / 배열 권한 없는 identity

DAWproject 1.0 Note elements do not provide MUSICA stable note IDs. M6-R4 v0 therefore SHALL NOT use note array index/order as identity.

Initial v0 identity proof requires each source exact note to have a unique normalized lowered signature within the reconciled track. Duplicate signatures are ambiguous and SHALL be rejected rather than disambiguated by order.

No nearest-time, nearest-pitch, edit-distance or other heuristic note matching is permitted in v0.

## 6. REQUIRED Gate C — exact normalized baseline comparison / 정확한 정규화 baseline 비교

The returned artifact SHALL be compared against the exact normalized MUSICA export baseline stored/bound by the source bundle.

It is invalid to compare only against a newly compiled current IR because doing so could hide export serialization lineage changes or stale source conditions.

Normalization SHALL reuse the validated M5-R3 bounded parser/security path.

## 7. REQUIRED Gate D — single primitive representation / 단일 primitive 표현

M6-R4 v0 authorizes only one uniquely provable primitive change per reconciliation candidate.

Allowed existing M6 vocabulary:

```text
MOVE
RESIZE
REPITCH
SET_VELOCITY
DELETE
INSERT
```

For an update, exactly one normalized musical field may differ for exactly one source note. Channel/part identity changes are not a supported primitive.

DELETE requires exactly one uniquely identified source note to disappear.

INSERT requires exactly one returned note to be added while all source notes remain unchanged. The inserted MUSICA note identity must be deterministic and artifact/source-bound, and its part/section/timing must satisfy existing M6 exact-note constraints.

Any multi-note, multi-field or multiply-interpretable delta is `UNREPRESENTABLE_EDIT`/fail-closed for v0.

## 8. REQUIRED Gate E — non-note semantics unchanged / 비-note 의미 불변

M6-R4 v0 is a note reconciliation milestone, not a combined interchange editor.

The following must remain unchanged from the exact export baseline:

- transport tempo/meter;
- traceable track/part mapping;
- non-target/non-motif tracks within the bounded profile;
- unsupported external semantics that could affect authority.

A returned artifact containing note plus transport or other unsupported changes must not smuggle those changes through a note candidate.

## 9. REQUIRED Gate F — existing M6 candidate contract / 기존 M6 candidate 계약

A successfully reconciled delta SHALL become a normal `note-edit-candidate-v0` object with:

- exact source project/revision/Blueprint hash;
- actor kind `import` or equivalent;
- one typed existing M6 operation;
- `preview_only = true`;
- deterministic operation/candidate provenance.

M6-R4 SHALL NOT create a second edit engine or alternate canonical commit path.

## 10. REQUIRED Gate G — M6 authority remains final / M6 권한 최종성

After reconciliation, the candidate SHALL pass through the existing M6-R1 authority engine.

Existing outcomes remain authoritative:

- stale source → `BLOCKED / STALE_SOURCE`;
- stable-ID HARD lock conflict → `BLOCKED / HARD_LOCK_VIOLATION`;
- hard constraint/invariant conflict → blocked;
- valid candidate → `READY_FOR_PREVIEW` only.

Reconciliation success never implies acceptance.

## 11. REQUIRED Gate H — explicit Accept / 명시적 승인

A reconciled candidate is non-canonical. Accepted project state may change only through the existing Preview + explicit M2 Accept path.

The external artifact, normalized representation, identity map, reconciliation result or authority result cannot advance a branch/ref directly.

## 12. REQUIRED Gate I — fail-closed cases / 실패 폐쇄 사례

Automated evidence SHALL cover at minimum:

- missing/stale source revision binding;
- source Blueprint hash mismatch;
- exact timeline/hash mismatch;
- export artifact/baseline mismatch;
- duplicate/ambiguous source note signature;
- duplicate/ambiguous returned note signature;
- unchanged artifact presented as an edit;
- multiple note changes;
- one note with multiple primitive fields changed;
- channel/part identity change;
- tempo/meter change combined with note change;
- non-target track change;
- malformed/unsafe/XSD-invalid DAWproject through inherited M5-R3 security path;
- HARD-lock conflict after successful reconciliation.

No fail-closed case may mutate accepted state.

## 13. REQUIRED Gate J — evidence / 근거

A dedicated M6-R4 evidence package SHALL bind at minimum:

```text
source Blueprint hash
source exact-timeline hash
source Music-IR hash
source exported DAWproject hash
identity-map hash
normalized baseline hash
returned artifact hash(es)
normalized returned hash(es)
typed NoteEditCandidate(s)
M6 authority result(s)
negative ambiguity/stale/lock proof(s)
manifest with per-file SHA-256
```

Machine-readable evidence is primary. Narrative documentation alone is insufficient.

## 14. REQUIRED Gate K — regressions / 회귀

An evidence-bearing exact PR head SHALL keep green at minimum:

- M5-R3 DAWproject evidence/regressions;
- M5-R4 comparison evidence;
- M6-R1 exact-note authority evidence;
- M6-R2 Browser piano-roll evidence;
- M6-R3 real-browser exact-note evidence;
- full MUSICA Python 3.11/3.12 CI;
- M4 real-browser and M5-R2 Windows renderer jobs contained in MUSICA CI.

## 15. Non-goals / 비목표

M6-R4 v0 does **not** validate or imply:

- arbitrary DAWproject reverse mapping;
- reconciliation of non-MUSICA-origin DAWproject projects;
- compatibility with every DAW or any specific DAW unless separately smoke-tested;
- multi-note batch reconciliation;
- heuristic note correspondence;
- arbitrary polyphonic/every-part exact-note editing;
- tempo-map reconciliation;
- automation/mixer/plugin/device round-trip;
- live MIDI recording;
- waveform/destructive audio editing;
- external DAW state as canonical authority.

## 16. Promotion rule / 승격 규칙

M6-R4 may be promoted only after:

```text
implementation
→ targeted tests
→ dedicated machine evidence
→ exact-head full CI/regressions
→ artifact download + independent manifest/hash inspection
→ durable evidence/M6_R4_VALIDATION.md
→ exact evidence-bearing successor rerun
→ final artifact inspection
→ expected-head PR merge
→ Issue #65 completed
→ state-only closure
```

A missing or inferred gate is not PASS.

**Repository evidence remains authoritative over conversation/model memory. / 레포 근거는 대화·모델 기억보다 우선합니다.**
