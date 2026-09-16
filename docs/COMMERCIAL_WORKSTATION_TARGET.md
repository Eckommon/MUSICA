# MUSICA Commercial Workstation Target / 상용 음악 제작 워크스테이션 목표

**Status / 상태:** LONG-TERM PRODUCT TARGET — GOVERNING, NOT A COMPLETION CLAIM

## 1. Long-term objective / 장기 목표

MUSICA has two inseparable product ambitions:

1. preserve its AI-native core proposition — music can be created by intent while every important musical decision remains inspectable, lockable, editable, reproducible and programmable;
2. grow into a **general-purpose, commercially usable music production workstation** in which a user can complete ordinary end-to-end production work without being forced to leave MUSICA for basic DAW operations.

MUSICA의 장기 목표는 AI-native 창작 제어 모델을 보존하면서, 일반적인 음악 제작 작업을 자체적으로 완결할 수 있는 **범용/상용 음악 제작 워크스테이션**으로 성장하는 것입니다.

This target does **not** mean MUSICA must clone every feature of every established DAW. Commercial/general-purpose readiness means that core production workflows are first-class, reliable, persistent, interoperable and distributable.

## 2. Relationship to the foundation non-goals / 기반 비목표와의 관계

`docs/PRODUCT_THESIS.md` and `docs/design/ARCHITECTURE_v0.1.md` correctly stated that full DAW replacement, universal plugin hosting and mastering-grade universal DSP were **foundation-stage non-goals**.

Those statements remain historically and architecturally valid: M0–M7 did not need those capabilities to validate the core thesis. They do **not** prohibit later workstation expansion.

The program therefore distinguishes:

```text
Foundation acceptance boundary
    ≠
Long-term product ceiling
```

## 3. Product identity / 제품 정체성

MUSICA should not become a conventional DAW with an AI chat box attached. Its workstation capabilities must remain integrated with the same authority model:

```text
User intent / precise edit
        ↓
typed candidate
        ↓
locks + constraints + source binding
        ↓
Preview · NOT ACCEPTED
        ↓ explicit Accept
Accepted project revision
        ↓
deterministic/declared execution
        ↓
audio, MIDI, plugin, device, interchange and export artifacts
```

AI, Browser state, meters, waveforms, plugin runtime state, rendered audio and external DAW state may inform the user, but may not silently become canonical creative authority.

## 4. General-purpose workstation capability domains / 범용 워크스테이션 기능 영역

The long-term program must eventually provide credible coverage across these domains. The list is a target map, not a promise that every item is implemented now.

### A. Native project and arrangement

- instrument/MIDI tracks;
- audio tracks;
- stable clips/regions and timeline arrangement;
- project tempo/time structure;
- non-destructive editing;
- selection, duplication, move, trim and bounded transformations;
- robust undo/version/revision semantics.

### B. Audio assets and recording

- content-addressed project audio assets;
- import/export of common production formats;
- recording, monitoring and take management;
- deterministic provenance where technically possible;
- missing/corrupt media recovery and fail-closed behavior.

### C. Mixer and signal flow

- per-track gain/pan/mute/solo;
- buses, sends, returns, groups and routing;
- automation over supported mixer/device parameters;
- metering and clipping/headroom policy;
- deterministic offline rendering and explicit real-time behavior.

### D. Instruments, effects and plugin hosting

- native/reference instruments and DSP where useful;
- third-party plugin hosting through platform-appropriate standards such as VST3, CLAP and AU where applicable;
- capability discovery instead of guessed parameter semantics;
- explicit plugin identity/version/state provenance;
- sandbox/crash containment and missing-plugin handling before commercial claims.

### E. Real-time engine

- audio-device abstraction appropriate to supported operating systems;
- transport, monitoring and low-latency scheduling;
- latency reporting/compensation;
- deterministic offline vs real-time behavior explicitly distinguished;
- performance and dropout evidence under supported workloads.

### F. Audio editing depth

- waveform inspection;
- fades/crossfades;
- clip gain and non-destructive processing;
- time-stretch/warp and pitch operations when provenance and quality policies are defined;
- comping/take workflows where supported.

### G. Composition and programmability

- semantic controls;
- exact notes/MIDI-like events;
- rich automation;
- structured transformations;
- Blueprint/IR/API/CLI surfaces;
- AI direction that resolves through the same contracts rather than bypassing them.

### H. Interoperability

- MIDI and common audio exchange;
- DAWproject and other justified interchange adapters;
- explicit loss reports and reconciliation boundaries;
- no external format becomes canonical merely because it is widely used.

### I. Product reliability and commercial distribution

- project migration/version compatibility;
- crash recovery and autosave strategy;
- large-project scalability and performance profiling;
- installer/package, signing and update strategy;
- platform support matrix;
- licensing/dependency compliance;
- release qualification and regression evidence.

### J. Collaboration — later, separate authority domain

Cloud sync, multi-user editing, permissions and conflict resolution are valuable but introduce distributed authority. They remain separate from the initial commercial-workstation path until explicitly ratified.

## 5. Commercial-readiness gates / 상용 준비 게이트

MUSICA must not claim commercial/general-purpose completion merely because individual features exist. A future release-readiness decision should require evidence across at least:

- **workflow completeness** — ordinary production can be completed without missing basic internal primitives;
- **correctness** — project state, media references, timing and signal flow are trustworthy;
- **real-time reliability** — where real-time capability is claimed;
- **persistence/recovery** — reopen, migration, autosave/recovery and missing-asset behavior;
- **performance/scalability** — bounded supported project sizes and latency/load targets;
- **interoperability** — imports/exports disclose loss instead of inventing fidelity;
- **plugin/device robustness** — only when those capabilities are claimed;
- **distribution/security/compliance** — installer/signing/dependencies/licenses/update path;
- **UX evidence** — when usability or workflow-efficiency claims are made.

## 6. Sequencing principle / 개발 순서 원칙

The expansion order must follow dependency structure rather than feature popularity.

Preferred architectural dependency chain:

```text
native audio asset
→ audio clip
→ audio track
→ mixer/signal path
→ deterministic offline mix
→ richer routing/automation
→ real-time engine + devices
→ recording/monitoring
→ plugin hosting + latency compensation
→ deeper audio editing
→ release hardening
```

This is a dependency guide, not a fixed milestone schedule. Repository evidence may change the exact order.

## 7. First selected expansion / 첫 확장

The post-Compare successor review selects:

> **Issue #95 — Audio Track / Clip / Mixer Foundation v0**

Reason: the repository already validates intent, note editing, automation, rendering, versioning, Browser Studio, interchange and Compare, but lacks a native audio-track/clip/multitrack-mixer substrate. That substrate is a prerequisite for many later general-purpose DAW capabilities.

The first foundation is deliberately bounded. It does not yet claim microphone recording, a low-latency device engine, plugin hosting, arbitrary buses/sends, warp/time-stretch, destructive editing or commercial release readiness.

## 8. Governing invariant / 지배 불변식

Commercial expansion must not destroy MUSICA's differentiator.

> **More DAW capability must increase production power without creating hidden, non-reproducible or reverse-authoritative musical state.**

A feature that cannot yet satisfy this invariant must remain unsupported, derived, experimental or explicitly lossy until its authority and evidence contract is ready.

**Repository evidence remains authoritative over conversation/model memory.**
