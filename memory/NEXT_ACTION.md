# Next Action / 다음 작업

## Exact resume point / 정확한 재개점

**PLUG-R1 — TRUSTED PLUGIN STATE PREVIEW→ACCEPT & ACCEPTED OFFLINE EXECUTION v0**

Issue #159 — **OPEN**

Parent mission: Issue #155 — **Plugin Hosting & Latency Compensation Foundation v0 — OPEN**

PLUG-R0 is validated, merged and completed. The next dependency-safe step is to promote the exact R0 simulated plugin descriptor/instance/state model into accepted project authority through source-bound Preview → explicit Accept, while preserving runtime/output non-authority.

## Canonical base / 공식 기준점

- canonical main after PLUG-R0 merge:
  `d978d6fd8faa6885de2e492874ce38e992b58ef2`
- parent Issue #155 — **OPEN**
- PLUG-R0 Issue #156 — **COMPLETED**
- PLUG-R0 PR #158 — **MERGED**
- R0 implementation/evidence exact head:
  `1d3866354bc6f9d30461c4ab73a190f4ca6c473d` — **33/33 SUCCESS**
- R0 validation-record successor:
  `7a98f638306f96959d06879c3a7bb0d65f230f7b` — **33/33 SUCCESS**
- durable validation:
  `evidence/PLUG_R0_VALIDATION.md`
- dedicated artifact ID:
  `11166403201`
- artifact ZIP SHA-256:
  `5fe99e09246747ac4e8a8b2e45d4ef0e82313aa44c01f1a0e4ea88bd040bf018`
- permanent workflow count at validated R0 state: **33**

## Inherited authority / 상속 권한

R1 inherits:

~~~text
ATCM:
accepted immutable audio assets/tracks/clips
→ deterministic native mix

MRAM:
accepted routing DAG + native mixer automation
→ deterministic routed output

RTIO:
derived realtime plan/runtime only

REC:
trusted recording-finalize Preview→Accept
→ immutable accepted recording state

PLUG-R0:
stable simulated plugin descriptor/instance/state
→ detached non-canonical material
→ deterministic plugin plan
→ deterministic gain+delay processing
→ explicit latency/bypass/error semantics
~~~

R1 must reuse the R0 model exactly. It must not introduce a second plugin schema or a runtime-to-project authority path.

## Exact implementation order / 정확한 구현 순서

### 1. Re-ground accepted material and Project delta patterns

Inspect at minimum:

- `schemas/music-blueprint-v0.schema.json`;
- accepted audio/routing/automation material integration patterns;
- `src/musica/project.py` material-delta gates;
- trusted audio/routing/automation Preview→Accept implementations;
- `schemas/plugin-material-v0.schema.json`;
- `src/musica/plugin_reference.py`;
- `evidence/PLUG_R0_VALIDATION.md`.

Choose the least invasive additive accepted plugin material shape.

### 2. Split proposal vs accepted plugin material semantics cleanly

R0 material is explicitly:

> `classification = noncanonical_proposal`

Do not store that classification unchanged as accepted creative state.

Define an accepted form or versioned accepted wrapper that preserves exact descriptor/instance/state identity while making authority status unambiguous.

Legacy/no-plugin Blueprint must remain valid.

### 3. Define deterministic empty accepted plugin identity

Absence/no-plugin state must have an explicit deterministic source-binding rule.

Prefer a canonical empty material or equivalent deterministic hash so candidates can bind:

~~~text
source accepted revision
+ Blueprint SHA
+ audio SHA
+ routing SHA
+ automation SHA
+ plugin material SHA
~~~

without ambiguity between absent and empty state.

### 4. Add accepted Blueprint/plugin cross-field validation

Validate exact:

- descriptor uniqueness/order;
- instance uniqueness/order;
- plugin references;
- exact master owner identity under R1 scope;
- unique slot per owner;
- parameter ranges;
- sample-rate/channel policy;
- processor identity;
- routing existence and master identity.

Unknown/missing routing owner must fail closed.

### 5. Protect plugin material in Project Engine

Add an independent plugin-material delta gate analogous to accepted audio/routing/native-automation protection.

Required invariant:

~~~text
generic commit
+ changed accepted plugin material
→ BLOCKED

trusted plugin Accept
+ exact revalidation
→ plugin-authorized commit
~~~

A provenance marker alone must never grant permission.

### 6. Define source-bound plugin edit candidate

Use explicit stable-ID operations. Initial bounded set should cover at least:

- add instance;
- remove instance;
- set parameter/state;
- set bypass.

Descriptor handling must be explicit. If descriptor add/remove is required for the first accepted instance, freeze those operations rather than inferring descriptor authority from runtime objects.

### 7. Preview semantics

Plugin Preview must:

- bind exact source project/revision/hashes;
- validate descriptors/instances/owner/slot/state;
- apply changes to a copy only;
- produce exact material diff and changed stable IDs;
- leave accepted HEAD unchanged;
- produce a prospective accepted Blueprint/plugin-material hash;
- remain explicitly non-accepted.

### 8. Explicit Accept semantics

Accept must revalidate:

- branch HEAD equals Preview source revision;
- persisted source Blueprint hash;
- audio/routing/automation/plugin source hashes;
- exact current master routing-node identity;
- candidate Blueprint hash;
- candidate plugin material hash;
- parent revision linkage;
- no unauthorized audio/routing/automation changes.

Then advance exactly one accepted revision using the protected plugin-authorized Project Engine path.

Second Accept of the same Preview must fail closed.

### 9. Accepted plugin execution

Adapt the R0 plan builder/render path to consume accepted plugin material directly from the exact accepted revision.

Required execution proof:

~~~text
accepted routed source + accepted plugin material
→ deterministic plugin processing plan
→ deterministic reference processor
→ processed WAV
~~~

Do not require a detached Browser/runtime object to reconstruct accepted plugin state.

### 10. Controlled accepted state lifecycle

Prove at minimum:

1. no-plugin accepted baseline;
2. plugin insertion Preview — HEAD unchanged;
3. explicit Accept — exactly one revision advance;
4. accepted gain/delay state persists;
5. accepted output repeat-exact;
6. accepted gain state edit Preview/Accept changes plan/output exactly;
7. accepted bypass Preview/Accept returns byte-exact routed baseline with zero plugin effective latency;
8. accepted remove returns to documented no-plugin state;
9. stale Preview and second Accept fail closed.

### 11. Processor-error authority proof

Forced processor error is a derived execution failure.

It must not:

- mutate accepted plugin material;
- advance HEAD;
- silently disable/remove the plugin;
- write runtime state back to Blueprint.

### 12. Reopen exactness

Export/import or reopen must preserve:

- accepted descriptor identity;
- accepted instance/owner/slot/state;
- accepted plugin material SHA;
- exact derived plugin plan SHA;
- exact processed WAV SHA.

Unlike R0, R1 must prove plugin state itself is reconstructed from the project archive.

### 13. Compatibility

Prove:

- legacy/no-plugin accepted projects remain valid;
- existing routed output stays byte-identical when accepted plugin material is empty/absent;
- R0 detached helper remains explicitly non-canonical if retained;
- all prior 33 workflows remain green.

### 14. Dedicated evidence and permanent gate

Add a dedicated PLUG-R1 permanent workflow without weakening the existing **33** gates.

Expected total: **34**.

Evidence should include:

- accepted plugin material before/after;
- source-bound candidate + authority result;
- Preview proof;
- accepted revision lineage;
- deterministic plugin plan/output;
- controlled state edit;
- bypass/remove result;
- forced-error non-mutation proof;
- reopen archive;
- source/contract hash inventory;
- manifest/self-hash verification.

### 15. Promotion

PLUG-R1 promotion requires:

- implementation/evidence complete;
- dedicated PLUG-R1 gate green;
- all **34** permanent workflows green on exact evidence-bearing head;
- independent artifact/hash inspection;
- durable `evidence/PLUG_R1_VALIDATION.md`;
- validation-successor 34/34;
- expected-head squash merge;
- Issue #159 completed;
- separate state-only closure to PLUG-R2.

## PLUG-R1 non-goals / 비목표

Do not implement or claim in R1:

- real VST3/AU/CLAP binary loading;
- plugin scanning/installation;
- third-party binary state chunks;
- arbitrary plugin UI embedding;
- untrusted plugin sandboxing;
- generalized plugin parameter automation;
- sidechain/bus negotiation;
- arbitrary-graph latency compensation;
- sample-rate conversion;
- commercial third-party compatibility.

## Successor after R1

If R1 validates cleanly, exact next rung:

> **PLUG-R2 — bounded latency compensation plus explicit bypass/failure containment over accepted plugin state.**

## Maximum intended R1 outcome

> **MUSICA can accept and persist bounded simulated plugin instances/state only through source-bound Preview→Accept authority, deterministically execute the exact accepted plugin state over its accepted routed source, and reproduce accepted plugin identity plus derived plan/output after reopen while generic commit/runtime/output paths remain non-authoritative.**

This remains a target claim until R1 is implemented, evidenced, merged and state-closed.

**Repository evidence remains authoritative over conversation/model memory.**
