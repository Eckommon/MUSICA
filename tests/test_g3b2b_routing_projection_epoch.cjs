/* G3B2B: prove older routing GET completions cannot overwrite the newer view. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const script = fs.readFileSync(
  path.join(__dirname, "../src/musica/studio_web/routing_editing.js"),
  "utf8"
);

function makeFixture() {
  const requests = [];
  const win = {
    fetch: (url) => new Promise((resolve, reject) => {
      requests.push({ url, resolve, reject });
    }),
    addEventListener: () => {},
    dispatchEvent: () => {},
  };
  const doc = {
    readyState: "loading",
    getElementById: () => ({ hidden: false, textContent: "", className: "" }),
    addEventListener: () => {},
  };
  vm.runInNewContext(script, {
    window: win, document: doc, queueMicrotask,
    CustomEvent: class { constructor(kind, details) { this.kind = kind; this.details = details; } }
  });
  const state = win.MUSICA_ROUTING.state;
  const mutations = [];
  let current = null;
  Object.defineProperty(state, "view", {
    configurable: true,
    get() { return current; },
    set(x) { mutations.push(x); current = x; },
  });
  state.root = {};
  state.sessionId = "test-session";
  return { win, state, requests, mutations };
}

function response(value, ok = true) {
  return {
    status: ok ? 200 : 409,
    ok,
    headers: { get: () => "application/json" },
    json: async () => value
  };
}

async function testOlderGetCannotOverwriteNewerRejectedProjection() {
  const t = makeFixture();
  const older = t.win.MUSICA_ROUTING.refresh(true);
  const newest = t.win.MUSICA_ROUTING.refresh(true);
  assert.equal(t.requests.length, 2);
  assert.match(t.requests[0].url, /\/mixer-routing$/);
  t.requests[1].resolve(response({ ok: false, error: { message: "latest rejected" } }, false));
  await newest;
  t.requests[0].resolve(response({
    ok: true, data: { revision_id: "stale-accepted-revision" }
  }));
  await older;
  assert.equal(t.state.view, null);
  assert.equal(t.mutations.some(x => x && x.revision_id === "stale-accepted-revision"), false,
    "the older GET was installed after a more recent routing request");
}

async function testPreviousSessionResponseCannotInstall() {
  const t = makeFixture();
  const pending = t.win.MUSICA_ROUTING.refresh(true);
  t.state.sessionId = "different-session";
  t.requests[0].resolve(response({
    ok: true, data: { revision_id: "cross-session-old-view" }
  }));
  await pending;
  assert.equal(t.mutations.length, 0);
  assert.equal(t.state.view, null);
}

(async () => {
  await testOlderGetCannotOverwriteNewerRejectedProjection();
  await testPreviousSessionResponseCannotInstall();
  process.stdout.write("G3B2B routing projection epoch: PASS 2/2\n");
})().catch(error => { process.stderr.write(String(error.stack || error)); process.exitCode = 1; });
