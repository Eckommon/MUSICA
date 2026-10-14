# PLUG-R3-A — Studio Trusted Bus Processor Preview and Explicit Accept

**Status: implementation candidate; not validated.** Parent #155 remains OPEN. K2 Studio accepted/offline-audition integration is the prerequisite and MUST be promoted independently before this feature. This rung is **Studio service + HTTP**, NOT Browser graphical editor nor realtime plugin host.

## Bounded creator-facing authority

- `GET /v0/sessions/{session_id}/bus-plugins/editor`: reads exact accepted revision, branch, source-bound candidate hash tuple and supported stable two-track/two-bus topology. Returned accepted plugin material remains canonical; a pending Preview is not.
- `POST /v0/sessions/{session_id}/preview/bus-plugins`: requires a complete typed `bus-host-edit-candidate-v0` with source project/revision/Blueprint/audio/routing/automation/R1/plugin/accepted-host hashes, explicit proposed material and actor/reason. Validates through existing `build_bus_host_edit_preview` against persisted HEAD. No generic plugin commit authority or arbitrary field/processor injection.
- Preview WAV is derived from **candidate-only** via a Project proxy reading all underlying immutable assets and a bounded simulated offline renderer. Cached noncanonically by Studio. It is **never bound to accepted Project artifacts** and is never substituted for legacy `/media/audio.wav`.
- `GET /v0/sessions/{session_id}/bus-plugins/media/preview.wav`: only while this exact Preview is pending and HEAD unchanged. Verify cached bytes against installed SHA; fail closed on stale source/tamper.
- `POST /v0/sessions/{session_id}/preview/accept` uses the existing global Studio explicit Accept action, but newly dispatches `bus_host_edit` through *full re-derivation* from the persisted parent and original source candidate; compare candidate Blueprint hash, material hash and preview WAV hash, then use `accept_bus_host_edit_preview`. Exactly one accepted revision may advance. No direct generic commit.
- `POST /v0/sessions/{session_id}/preview/discard`: unchanged global discard, removes transient preview cache, no Project revision advance.
- A pending Preview of any type blocks another; unknown owner, wrong plugin processor, no-op, fake source hash, duplicate instance/slot, bypass changes without approval, stale branch HEAD, corrupted cached WAV or recomputed mismatch fail closed.

## Scope and nonclaims

Supported only for two distinct accepted tracks routed to distinct buses converging on one neutral master; at most one bounded simulated processor per bus. Algorithmic latency is **user-accepted explicit simulation metadata**, NOT a real VST3/CLAP/AU-reported delay; creative signal delay remains a separate approved field.

This rung does not include Browser graphical editing controls, arbitrary routing DAG, realtime device PDC, native third-party binary discovery/hosting, GUI plugin editor or commercial-release readiness. These must be separately implemented and empirically verified.

## Promotion gate

Permanent **40th** workflow: new Studio service and HTTP integration tests, inherited K2/K1-B/K1-A/R1 authority, 2x deterministic evidence, manifest hashes and independently decoded PCM oracle. 40/40 exact-head CI → independently inspect evidence ZIP/accepted source/PCM → durable validation → successor 40/40 CI → expected-head squash merge. K2 must be canonical main first.
