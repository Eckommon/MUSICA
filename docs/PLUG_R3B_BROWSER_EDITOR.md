# PLUG-R3-B — Browser Studio Simulated Bus Processor Editor

Status: **DRAFT IMPLEMENTATION / NO PROMOTION CLAIM**. Issue #174 under parent #155; depends on approved and merged PLUG-R3-A Studio trusted editing API (draft #173). Current branch is stacked for development and must be reconstructed on exact canonical main after R3-A squash merge.

## Creator experience

An accessible, responsive **Inspect** panel shows immutable accepted bus processor instances separately from the **NOT ACCEPTED** Preview. The panel uses exact accepted Project revision and SHA-256 metadata from `GET /bus-plugins/editor` and `GET /bus-plugins`. The user can select stable bus owner, propose a simulated processor insertion/change, adjust explicit nonnegative integer processing latency and **independent creative delay**, toggle bypass, or propose removal.

Each proposal is a server-validated typed, source-bound candidate; the browser does not mutate Project state. The *separate* preview WAV has its own HTML audio player. The accepted offline WAV has a different player/URL with content hash cache-busting. Clear standalone Accept and Discard invoke existing Studio authority and then invalidate/reload the view. A pending Preview of a different kind disables new plugin proposals. Stale/forged/unsupported candidates fail closed.

No untrusted source metadata is interpolated into HTML strings; dynamic names, IDs, hashes, status text appear through `textContent` or safe element construction. Keyboard focus and native field labels are provided, with responsive styling and status announcement. Preview status is visibly distinguished from accepted state.

## Boundaries

This is a narrow Browser panel for exactly two accepted distinct buses -> neutral master, one bounded **simulated** processor per bus. It does not implement a native third-party plugin format, inspect a plugin binary, report real plugin CPU load/latency, run realtime device PDC, alter the default Studio transport, or support arbitrary graph PDC.

## Required proof before promotion

Real Chromium must exercise actual UI add, change, bypass, remove, separate Preview and accepted audition, explicit Accept and Discard, stale source denial, HEAD protection, reopened Project source identity and numerically decoded true compensated PCM at exact frame indices. Negative tests must verify the user cannot accidentally upgrade Preview into accepted state. UI/JS/CSS and HTTP source-hash trust must be included in permanent evidence. Inherited 40 workflows must remain fully enabled.

Promotion: exact implementation head **41/41 SUCCESS**, independent artifact/PCM inspection, durable validation doc, validation successor **41/41 SUCCESS**, expected-head squash merge. Until then remain Draft and keep Issue #174 OPEN.
